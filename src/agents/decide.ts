import { P } from '../core/params.js';
import type { RNG } from '../core/rng.js';
import type {
  Action, AgentState, Cache, Episode, Kind, Percept,
} from '../core/types.js';
import { carriedTotal, energyValue } from './agent.js';
import { retrieve, socialOf, type Retrieved } from './memory.js';

/**
 * The T1 utility decision loop (§3.4):
 *
 *   percept → memory retrieval → drive weighting → candidate generation
 *   → scoring → exploration noise → action
 *
 * Deterministic given state + seed. No language model anywhere near this.
 *
 * There is deliberately no candidate that transfers goods in both directions,
 * and no term that tracks a running balance between two agents. `give` is scored
 * from empathy × perceived need plus the agent's *learned* record of the
 * target (trust, familiarity). If stable mutual giving appears, it can only
 * have come from those learned records — which is exactly what the ablation
 * control switches off.
 */

export interface Candidate {
  action: Action;
  intent: string;
  score: number;
  /** episodes cited by this candidate (for the causal ledger) */
  cites: Episode[];
}

export interface Decision {
  action: Action;
  intent: string;
  noisyScore: number;
  rawScore: number;
  top: { intent: string; score: number }[];
  driveWeights: Record<string, number>;
  cites: Episode[];
}

const NUTRITION = P.RESOURCES.map(r => r.nutrition);
const E_NORM = 25;                       // energy units per 1.0 of utility

function stepToward(ax: number, ay: number, tx: number, ty: number): { dx: number; dy: number } {
  return { dx: Math.sign(tx - ax), dy: Math.sign(ty - ay) };
}
function cheb(ax: number, ay: number, bx: number, by: number): number {
  return Math.max(Math.abs(ax - bx), Math.abs(ay - by));
}

export function decide(a: AgentState, pc: Percept, ownCaches: Cache[],
                       rng: RNG): Decision {
  const T = a.traits;
  const tick = pc.tick;
  const hunger = 1 - a.energy / P.ENERGY_MAX;
  const carriedVal = energyValue(a.carried);
  const cachedVal = ownCaches.reduce((s, c) => s + energyValue(c.q), 0);
  const wealth = carriedVal + cachedVal;

  // ---- drive weighting (traits × situation; §3.2 drives are satiable) -----
  // survival: urgency from hunger.
  const uSurv = Math.pow(Math.max(0, hunger), 1.35);
  // safety: urgency from remembered recent harm.
  const threats = retrieve(a, tick,
    ep => (ep.type === 'attack-in' || ep.type === 'theft-in') ? 1 : 0, 4);
  const uSafe = Math.min(1, threats.reduce(
    (s, r) => s + 0.55 * Math.exp(-(tick - r.ep.tick) / 140), 0));
  // belonging: urgency grows with time since any positive social contact.
  let lastSocial = a.bornTick;
  for (const ep of a.episodic) {
    if ((ep.type === 'gift-in' || ep.type === 'gift-out' ||
         ep.type === 'signal-heard') && ep.tick > lastSocial) lastSocial = ep.tick;
  }
  const uBel = Math.min(1, (tick - lastSocial) * P.BELONGING_DECAY);
  // status: urgency from low relative stored wealth.
  const uStat = 1 - wealth / (wealth + P.STATUS_HALF_WEALTH);

  const w = {
    survival: P.DRIVE_BASE.survival * (0.25 + 2.9 * uSurv),
    safety: P.DRIVE_BASE.safety * uSafe * (1.4 - 0.8 * T.riskTolerance),
    belonging: P.DRIVE_BASE.belonging * (0.35 + 0.65 * uBel) * (0.5 + T.sociability),
    status: P.DRIVE_BASE.status * uStat * (0.3 + 1.4 * T.statusSensitivity),
  };

  const cands: Candidate[] = [];
  const push = (action: Action, intent: string, score: number, cites: Episode[] = []) =>
    cands.push({ action, intent, score, cites });

  // ---- eat ---------------------------------------------------------------
  if (a.energy < 92) {
    for (const k of [0, 1, 2] as Kind[]) {
      if (a.carried[k] >= 0.5) {
        const amt = Math.min(P.EAT_AMOUNT, a.carried[k]);
        push({ t: 'eat', kind: k }, `eat:${k}`,
          w.survival * (NUTRITION[k] * amt / E_NORM));
      }
    }
  }

  // ---- gather here (node or spill in this cell) ---------------------------
  const room = P.CARRY_MAX - carriedTotal(a);
  const hereNode = pc.nodes.find(n => n.x === a.x && n.y === a.y && n.q > 0.25);
  const hereSpill = pc.spills.find(s => s.x === a.x && s.y === a.y && s.q > 0.25);
  if (room > 0.5) {
    const g = hereSpill ?? (hereNode && hereNode.open ? hereNode : undefined);
    if (g) {
      const k = 'k' in g ? g.k : 0;
      const rate = Math.min(P.RESOURCES[k].gatherRate, g.q, room);
      push({ t: 'gather' }, `gather:${k}`,
        (0.6 * w.survival + 0.45 * w.status) * (NUTRITION[k] * rate / E_NORM)
        * (0.35 + 0.65 * Math.min(1, hunger * 2 + uStat)));
    } else if (hereNode && !hereNode.open) {
      // standing on a sealed seasonal node — remembered as such, not acted on
    }
  }

  // ---- move toward the best known food -----------------------------------
  const discount = 0.85 + 0.11 * T.patience;
  let bestMove: { score: number; x: number; y: number; k: Kind; cites: Episode[] } | null = null;
  const considerSite = (x: number, y: number, k: Kind, q: number,
                        open: boolean, cites: Episode[]) => {
    if (!open || q < 1) return;
    const d = cheb(a.x, a.y, x, y);
    if (d === 0) return;
    const rate = Math.min(P.RESOURCES[k].gatherRate, q, Math.max(room, 0));
    const s = (0.6 * w.survival + 0.4 * w.status)
      * (NUTRITION[k] * rate / E_NORM) * Math.pow(discount, d);
    if (!bestMove || s > bestMove.score) bestMove = { score: s, x, y, k, cites };
  };
  for (const n of pc.nodes) considerSite(n.x, n.y, n.k, n.q, n.open, []);
  for (const s of pc.spills) considerSite(s.x, s.y, s.k, s.q, true, []);
  if (room > 0.5) {
    // remembered nodes beyond vision (episodic memory doing real work)
    const remembered = retrieve(a, tick, ep =>
      ep.type === 'node-seen' && cheb(a.x, a.y, ep.x, ep.y) > P.VISION ? 1 : 0, 4);
    for (const r of remembered) {
      const k = r.ep.k as Kind;
      const open = !P.RESOURCES[k].seasonal || pc.atmos > 0.6; // inference from sky
      considerSite(r.ep.x, r.ep.y, k, r.ep.amount, open, [r.ep]);
    }
  }
  if (bestMove !== null) {
    const bm = bestMove as { score: number; x: number; y: number; k: Kind; cites: Episode[] };
    push({ t: 'move', ...stepToward(a.x, a.y, bm.x, bm.y) },
      `to-food:${bm.k}`, bm.score, bm.cites);
  }

  // ---- store / go home to store ------------------------------------------
  const storable = [0, 2] as Kind[];
  const atHome = a.x === a.homeX && a.y === a.homeY;
  for (const k of storable) {
    const amt = a.carried[k] - 2.5;
    if (amt < 1) continue;
    const H = 150 * (0.5 + T.patience);
    const keep = Math.exp(-P.RESOURCES[k].cacheDecay * H)
               - Math.exp(-P.RESOURCES[k].carryDecay * H);
    const s = (0.3 * w.survival + 0.85 * w.status) * (NUTRITION[k] * amt * keep / E_NORM);
    if (atHome) push({ t: 'store', kind: k }, `store:${k}`, s);
    else {
      const d = cheb(a.x, a.y, a.homeX, a.homeY);
      push({ t: 'move', ...stepToward(a.x, a.y, a.homeX, a.homeY) },
        `to-home-store:${k}`, s * Math.pow(discount, d) * 0.92);
    }
  }

  // ---- withdraw from own cache (or head home to do so) --------------------
  for (const c of ownCaches) {
    const k = ([0, 2, 1] as Kind[]).find(kk => c.q[kk] > 0.5);
    if (k === undefined || hunger < 0.25) continue;
    const amt = Math.min(P.TAKE_AMOUNT, c.q[k], Math.max(room, 0));
    if (amt < 0.5) continue;
    const s = w.survival * (NUTRITION[k] * amt / E_NORM) * 0.95;
    const d = cheb(a.x, a.y, c.x, c.y);
    if (d === 0) push({ t: 'takeCache', owner: a.id, kind: k }, `withdraw:${k}`, s);
    else push({ t: 'move', ...stepToward(a.x, a.y, c.x, c.y) },
      `to-cache`, s * Math.pow(discount, d));
  }

  // ---- give (adjacent, visibly needy or socially bound) -------------------
  for (const b of pc.agents) {
    if (cheb(a.x, a.y, b.x, b.y) > 1) continue;
    const rec = socialOf(a, b.id);
    const need = [1.0, 0.42, 0.1][b.band];
    for (const k of [0, 2, 1] as Kind[]) {
      if (a.carried[k] < 1) continue;
      const amt = Math.min(a.carried[k] * P.GIVE_FRACTION, P.GIVE_MAX);
      // negative trust cuts deeper than positive trust lifts: a grudge
      // suppresses even empathy-driven giving
      const trustTerm = rec.trust >= 0
        ? P.GIVE_W_TRUST * rec.trust
        : P.GIVE_W_TRUST * 2.2 * rec.trust;
      const warmth =
        P.GIVE_W_NEED * T.empathy * need * (rec.trust < -0.12 ? 0.35 : 1) +
        trustTerm +
        P.GIVE_W_FAM * rec.familiarity;
      const value = w.belonging * warmth * (NUTRITION[k] * amt / E_NORM);
      const scarcity = Math.max(0, 1 - carriedVal / 40);
      const cost = w.survival * P.GIVE_COST_W * (0.25 + 1.3 * hunger + scarcity)
        * (NUTRITION[k] * amt / E_NORM) / 2.6;
      push({ t: 'give', target: b.id, kind: k }, `give:${b.id}`, value - cost);
      break;                                    // offer the best storable kind only
    }
  }

  // ---- take (mug an adjacent carrier) ------------------------------------
  for (const b of pc.agents) {
    if (cheb(a.x, a.y, b.x, b.y) > 1 || b.load === 0) continue;
    const rec = socialOf(a, b.id);
    const witnesses = pc.agents.filter(o => o.id !== b.id).length;
    const gain = w.survival * (0.25 + 1.4 * hunger) * (7 * P.TAKE_AMOUNT / E_NORM)
      + 0.55 * T.aggression + 0.3 * (1 - T.empathy);
    const inhibit = P.TAKE_TRUST_W * Math.max(0, rec.trust + 0.3 * rec.familiarity)
      + P.TAKE_RISK_W * (1 - T.riskTolerance) * 0.8
      + T.conformity * 0.7 * Math.min(3, witnesses);
    push({ t: 'take', target: b.id, kind: 0 }, `take:${b.id}`, gain - inhibit);
  }

  // ---- loot a cache in this cell -----------------------------------------
  for (const c of pc.caches) {
    if (c.owner === a.id || c.x !== a.x || c.y !== a.y) continue;
    const k = ([0, 2, 1] as Kind[]).find(kk => c.q[kk] > 0.5);
    if (k === undefined) continue;
    const rec = socialOf(a, c.owner);
    const amt = Math.min(P.TAKE_AMOUNT, c.q[k], Math.max(room, 0));
    const witnesses = pc.agents.length;
    const gain = w.survival * (0.3 + 1.3 * hunger) * (NUTRITION[k] * amt / E_NORM)
      + 0.35 * T.aggression;
    const inhibit = P.TAKE_TRUST_W * Math.max(0, rec.trust + 0.3 * rec.familiarity)
      + T.conformity * 0.9 * Math.min(3, witnesses)
      + P.TAKE_RISK_W * (1 - T.riskTolerance) * 0.35;
    push({ t: 'takeCache', owner: c.owner, kind: k }, `loot:${c.owner}`, gain - inhibit);
  }

  // ---- attack ------------------------------------------------------------
  for (const b of pc.agents) {
    if (cheb(a.x, a.y, b.x, b.y) > 1) continue;
    const rec = socialOf(a, b.id);
    const desperate = hunger > 0.8 && b.load > 0 && rec.trust <= 0;
    if (T.aggression < P.ATTACK_THRESHOLD && !desperate) continue;
    const witnesses = pc.agents.filter(o => o.id !== b.id).length;
    const gain = w.survival * (0.2 + 1.3 * hunger) * (7 * 2.5 * P.ATTACK_SPOIL / E_NORM)
      + 0.7 * T.aggression + 0.25 * w.status;
    const inhibit = P.TAKE_TRUST_W * 1.2 * Math.max(0, rec.trust)
      + P.TAKE_RISK_W * 1.4 * (1 - T.riskTolerance)
      + T.conformity * 1.1 * Math.min(3, witnesses)
      + T.empathy * 1.0;
    push({ t: 'attack', target: b.id }, `attack:${b.id}`, gain - inhibit);
  }

  // ---- respond to signals -------------------------------------------------
  for (const s of pc.signals) {
    if (s.from === a.id) continue;
    const rec = socialOf(a, s.from);
    const d = cheb(a.x, a.y, s.x, s.y);
    if (d === 0) continue;
    if (s.mode === 0 && carriedVal > 12) {
      // distress: come and (probably) give
      const sc = w.belonging * P.RESPOND_W *
        (0.5 * T.empathy + 0.75 * Math.max(0, rec.trust) + 0.2 * rec.familiarity)
        - 0.02 * d;
      push({ t: 'move', ...stepToward(a.x, a.y, s.x, s.y) }, `respond:${s.from}`, sc);
    } else if (s.mode === 1 && room > 2) {
      // abundance ping: food over there
      const sc = w.survival * 0.5 * hunger + 0.3 * T.curiosity - 0.02 * d;
      push({ t: 'move', ...stepToward(a.x, a.y, s.x, s.y) }, `heed:${s.from}`, sc);
    }
  }

  // ---- emit signals -------------------------------------------------------
  if (a.energy < P.DISTRESS_ENERGY && carriedVal < 8) {
    push({ t: 'signal', mode: 0 }, 'signal-distress',
      w.survival * 1.15 * (0.3 + 0.7 * T.sociability));
  }
  if (hereNode && hereNode.open && hereNode.q > 0.55 * P.RESOURCES[hereNode.k].cap
      && (room < 3 || hunger < 0.25)) {
    push({ t: 'signal', mode: 1 }, 'signal-abundance',
      w.belonging * (0.55 * T.sociability + 0.3 * T.empathy));
  }

  // ---- follow / keep company ---------------------------------------------
  let bestF: { id: number; s: number; x: number; y: number } | null = null;
  for (const b of pc.agents) {
    const rec = socialOf(a, b.id);
    const s = w.belonging * P.FOLLOW_W *
      (0.45 * rec.familiarity + 0.65 * Math.max(0, rec.trust) + 0.25 * T.sociability);
    if (!bestF || s > bestF.s) bestF = { id: b.id, s, x: b.x, y: b.y };
  }
  if (bestF && bestF.s > 0.05) {
    const d = cheb(a.x, a.y, bestF.x, bestF.y);
    if (d > 1) push({ t: 'follow', target: bestF.id }, `follow:${bestF.id}`, bestF.s);
  }

  // ---- explore ------------------------------------------------------------
  const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]];
  const [ex, ey] = dirs[rng.int(8)];
  push({ t: 'move', dx: ex, dy: ey }, 'explore',
    P.EXPLORE_W * (0.3 + 0.7 * T.curiosity) * (0.5 + 0.8 * hunger));

  // flee when threatened: move away from the nearest remembered aggressor
  if (uSafe > 0.3 && threats.length > 0) {
    const t0 = threats[0].ep;
    const foe = pc.agents.find(b => b.id === t0.who);
    if (foe) {
      push({ t: 'move', dx: -Math.sign(foe.x - a.x) || 1, dy: -Math.sign(foe.y - a.y) },
        `flee:${foe.id}`, w.safety * 1.5, [t0]);
    }
  }

  push({ t: 'rest' }, 'rest', 0.12);

  // ---- exploration noise, then argmax (§3.4: perturb, never replace) ------
  let best: Candidate = cands[0];
  let bestNoisy = -Infinity;
  const top: { intent: string; score: number }[] = [];
  for (const c of cands) {
    const noisy = c.score + P.NOISE_TEMP * rng.gumbel();
    top.push({ intent: c.intent, score: Math.round(c.score * 1000) / 1000 });
    if (noisy > bestNoisy) { bestNoisy = noisy; best = c; }
  }
  top.sort((p, q) => q.score - p.score);

  return {
    action: best.action,
    intent: best.intent,
    noisyScore: bestNoisy,
    rawScore: best.score,
    top: top.slice(0, 3),
    driveWeights: {
      survival: r3(w.survival), safety: r3(w.safety),
      belonging: r3(w.belonging), status: r3(w.status),
    },
    cites: best.cites,
  };
}

function r3(v: number): number { return Math.round(v * 1000) / 1000; }
