import { M1, M2, P, type TraitName } from '../core/params.js';
import { RNG } from '../core/rng.js';
import type {
  Action, AgentState, Cache, Episode, EpisodeType, Kind, Percept, SimConfig,
  WorldState,
} from '../core/types.js';
import { blankAgent, carriedTotal, clamp01, createAgents,
         energyValue } from '../agents/agent.js';
import { decide, type M1Opts } from '../agents/decide.js';
import { clampTrust, lexBump, lexTopToken, socialMut,
         writeEpisode } from '../agents/memory.js';
import { generateWorld, atmosphere, nodeOpen, m1NodeSpec, m2NodeSpec,
         m2Blocked, m2CrossBlocked } from '../world/world.js';
import { Ledger } from './ledger.js';

/**
 * The simulation engine. One rule above all others: no state changes outside
 * a ledger entry (§4.1). Every mutation site here appends an entry whose
 * payload is sufficient to replay it; src/engine/replay.ts proves that by
 * reconstruction.
 */

export interface SimEvent {
  tick: number;
  type: 'give' | 'take' | 'loot' | 'attack' | 'signal' | 'death';
  a: number;              // actor
  b: number;              // other party (-1)
  k: number;              // resource kind (-1)
  amt: number;
  ledger: number;         // resolution entry id
  /** for loot: whether the owner saw it happen (unwitnessed theft is a
   *  defection the victim cannot retaliate against — by design) */
  w?: boolean;
  /** for M1 signals: the arbitrary token emitted */
  o?: number;
}

export interface Frame {
  tick: number;
  /** per live agent: [id, x, y, energy, carriedValue] */
  agents: number[][];
}

export class Sim {
  cfg: SimConfig;
  world: WorldState;
  agents: AgentState[];
  ledger: Ledger;
  events: SimEvent[] = [];
  frames: Frame[] = [];
  nodeSnaps: { tick: number; q: number[] }[] = [];
  cacheSnaps: { tick: number; c: number[][] }[] = [];
  /** M1: [tick, agent, x, y, kind] for every successful gather */
  gathers: number[][] = [];
  /** M1: [tick, child, gen, parentA, parentB, x] */
  births: number[][] = [];
  /** M2: emission log for the measurement layer (never agent-visible) */
  emissions: { t: number; a: number; mode: number; tok: number; x: number;
               y: number; ref: number; hearers: [number, number][] }[] = [];
  /** M2: per-agent strongest association snapshots, every 250 ticks */
  lexSnaps: { tick: number; rows: number[][] }[] = [];

  private orderRng: RNG;
  private noiseRng: RNG;
  private mortalityRng: RNG;
  private reproRng: RNG;
  private scatterRng: RNG;
  private lastHarm = new Map<number, number>();          // agent → ledger id
  private nodeSeen = new Map<number, Map<number, number>>(); // agent → node → tick
  private lastWatch = new Map<number, number>();  // watcher*1e4+actor → tick
  private agedToDie = new Set<number>();
  /** effective radii for this run (M2 shrinks sight; calls carry farther) */
  private vision: number = P.VISION;
  private sigR: number = P.SIGNAL_RADIUS;
  /** M2: outstanding acted-on tips awaiting an outcome */
  private tips: { b: number; emitter: number; tok: number; x: number;
                  y: number; kHat: number; deadline: number;
                  arrived: boolean }[] = [];

  constructor(cfg: SimConfig) {
    this.cfg = cfg;
    if (cfg.m2) cfg.m1 = true;             // M2 builds on the M1 systems
    this.ledger = new Ledger(!cfg.lean);
    this.world = generateWorld(cfg.seed, !!cfg.m1, !!cfg.m2);
    this.agents = createAgents(cfg.seed,
      cfg.agents ?? (cfg.m2 ? 2 * M2.AGENTS_PER_SIDE
                   : cfg.m1 ? M1.AGENTS_START : P.N_AGENTS),
      !!cfg.m1, !!cfg.m2);
    if (cfg.m2) {
      // ablation B removes the §2.1 asymmetry entirely: sight reaches as
      // far as any signal, so nothing a call carries is ever private
      this.vision = cfg.fullObservability ? M2.SIGNAL_RADIUS : M2.VISION;
      this.sigR = M2.SIGNAL_RADIUS;
    }
    this.orderRng = new RNG(cfg.seed, `order:${cfg.stream}`);
    this.noiseRng = new RNG(cfg.seed, `noise:${cfg.stream}`);
    this.mortalityRng = new RNG(cfg.seed, `mortality:${cfg.stream}`);
    this.reproRng = new RNG(cfg.seed, `repro:${cfg.stream}`);
    this.scatterRng = new RNG(cfg.seed, `scatter:${cfg.stream}`);
    for (const a of this.agents) this.nodeSeen.set(a.id, new Map());
  }

  run(): void {
    for (let t = 0; t < this.cfg.ticks; t++) this.step();
  }

  // -------------------------------------------------------------------------

  step(): void {
    const t = this.world.tick;
    this.worldRegen(t);
    this.worldDecay(t);
    this.worldMetabolism(t);
    if (!this.cfg.ablateSocial) this.memDrift(t);
    this.world.signals = this.world.signals.filter(s => t - s.tick <= P.SIGNAL_TTL);
    if (this.cfg.m1) {
      if (this.cfg.scrambleChildren) this.scramble(t);
      this.mortality(t);
    }
    if (this.cfg.m2 && this.reproRng.next() < M2.BLOOM_CHANCE) {
      // a transient windfall — the §2.1 information asymmetry stays alive
      const n = this.world.nodes[this.reproRng.int(this.world.nodes.length)];
      const target = m2NodeSpec(n.k).cap * M2.BLOOM_MULT;
      if (n.q < target) {
        const dq = target - n.q;
        n.q += dq;
        this.ledger.append(t, 'stochastic', 'world.bloom', -1, { n: n.id, dq });
      }
    }

    const order = this.orderRng.shuffle(
      this.agents.filter(a => a.alive).map(a => a.id));
    for (const id of order) {
      const a = this.agents[id];
      if (!a.alive) continue;
      this.agentTurn(a, t);
    }
    this.deaths(t);
    if (this.cfg.m1) this.reproduction(t);
    if (this.cfg.m2) {
      this.tipExpiry(t);
      if (t % 250 === 0) this.snapLex(t);
    }
    this.record(t);
    this.world.tick = t + 1;
  }

  /** M2 measurement snapshot: each agent's strongest association per kind */
  private snapLex(t: number): void {
    const rows: number[][] = [];
    for (const a of this.agents) {
      if (!a.alive) continue;
      const row = [a.id];
      for (let k = 0; k < M2.REFS; k++) {
        const [tok, conf] = lexTopToken(a, k);
        row.push(tok, Math.round(conf * 100) / 100);
      }
      rows.push(row);
    }
    this.lexSnaps.push({ tick: t, rows });
  }

  // ---- M1 world rules (SPEC-M1 §3.1–3.2) -----------------------------------

  /** age-based hazard (§3.1); the draw is a stochastic event in the ledger */
  private mortality(t: number): void {
    for (const a of this.agents) {
      if (!a.alive) continue;
      const age = t - a.bornTick;
      const h = M1.HAZARD_BASE +
        (age > M1.HAZARD_AGE ? (age - M1.HAZARD_AGE) * M1.HAZARD_SLOPE : 0);
      if (this.mortalityRng.next() < h) this.agedToDie.add(a.id);
    }
  }

  /**
   * Ablation C (SPEC-M1 §5.4): children relocate to a random site at
   * independence — a uniformly chosen gather site, not their parents' —
   * severing the birth-locale correlation while leaving a livable start.
   */
  private scramble(t: number): void {
    const sites = this.world.siteCenters!;
    for (const a of this.agents) {
      if (!a.alive || t - a.bornTick !== M1.DEP_AGE || a.gen === 0) continue;
      const [sx, sy] = sites[this.scatterRng.int(sites.length)];
      const x = clampW(Math.round(sx + this.scatterRng.normal(0, 5)));
      const y = clampW(Math.round(sy + this.scatterRng.normal(0, 5)));
      a.x = x; a.y = y; a.homeX = x; a.homeY = y;
      this.ledger.append(t, 'stochastic', 'agent.scatter', a.id,
        { a: a.id, x, y });
    }
  }

  /** §3.2 — dumb pairing: adjacent, both surplus and mature, coin flip */
  private reproduction(t: number): void {
    const aliveCount = this.agents.reduce((s, a) => s + (a.alive ? 1 : 0), 0);
    if (aliveCount >= (this.cfg.m2 ? M2.POP_CAP : M1.POP_CAP)) return;
    const eligible = (a: AgentState) =>
      a.alive && t - a.bornTick >= M1.MATURITY &&
      a.energy >= M1.REPRO_ENERGY &&
      (t - a.lastRepro >= M1.REPRO_COOLDOWN || a.lastRepro < 0) &&
      energyValue(a.carried) + this.cachedValue(a.id) >= M1.REPRO_WEALTH;
    const taken = new Set<number>();
    const n = this.agents.length;         // children born this tick don't pair
    for (let i = 0; i < n; i++) {
      const a = this.agents[i];
      if (taken.has(a.id) || !eligible(a)) continue;
      for (let j = i + 1; j < n; j++) {
        const b = this.agents[j];
        if (taken.has(b.id) || !eligible(b)) continue;
        if (Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y)) > 1) continue;
        if (this.reproRng.next() >= M1.REPRO_CHANCE) continue;
        this.birth(a, b, t);
        taken.add(a.id); taken.add(b.id);
        break;
      }
    }
  }

  private birth(a: AgentState, b: AgentState, t: number): void {
    const traits = {} as Record<TraitName, number>;
    for (const tr of P.TRAITS) {
      // §3.2: traits only — midparent + mutation. Ablation B: random draw.
      traits[tr] = this.cfg.ablateInheritance
        ? clamp01(this.reproRng.normal(P.TRAIT_MEAN, P.TRAIT_SD))
        : clamp01(M1.HERITABILITY * (a.traits[tr] + b.traits[tr]) / 2 +
                  (1 - M1.HERITABILITY) * this.reproRng.normal(P.TRAIT_MEAN, P.TRAIT_SD) +
                  this.reproRng.normal(0, M1.MUTATION_SD));
    }
    const child = blankAgent(this.agents.length, a.x, a.y, traits, t,
      Math.max(a.gen, b.gen) + 1, [a.id, b.id], M1.CHILD_ENERGY);
    this.agents.push(child);
    this.nodeSeen.set(child.id, new Map());
    const dE = -M1.REPRO_COST;
    a.energy += dE; b.energy += dE;
    a.lastRepro = t; b.lastRepro = t;
    const eid = this.ledger.append(t, 'stochastic', 'agent.birth', child.id, {
      c: child.id, a: a.id, b: b.id, x: child.x, y: child.y,
      gen: child.gen, traits, e: M1.CHILD_ENERGY, dE,
    });
    this.births.push([t, child.id, child.gen, a.id, b.id, child.x]);
    // newborns know their parents and parents know their newborn — kinship
    // is biology, not inherited behavior (§3.2: traits only means the child
    // copies no memories; these are fresh records everyone writes at birth)
    this.social(a, child.id, M1.KIN_TRUST, M1.KIN_FAM, t, eid);
    this.social(b, child.id, M1.KIN_TRUST, M1.KIN_FAM, t, eid);
    this.social(child, a.id, M1.KIN_TRUST, M1.KIN_FAM, t, eid);
    this.social(child, b.id, M1.KIN_TRUST, M1.KIN_FAM, t, eid);
  }

  private cachedValue(id: number): number {
    let v = 0;
    for (const c of this.world.caches) {
      if (c.owner === id) v += energyValue(c.q);
    }
    return v;
  }

  // ---- world rules ---------------------------------------------------------

  private worldRegen(t: number): void {
    const d: [number, number][] = [];
    for (const n of this.world.nodes) {
      const spec = this.cfg.m2 ? m2NodeSpec(n.k)
        : this.cfg.m1 ? m1NodeSpec(n.k) : P.RESOURCES[n.k];
      if (n.q < spec.cap) {
        const dq = Math.min(spec.regen, spec.cap - n.q);
        n.q += dq;
        d.push([n.id, dq]);
      }
    }
    this.ledger.append(t, 'world', 'world.regen', -1, { d });
  }

  private worldDecay(t: number): void {
    const c: [number, number, number][] = [];   // agent, kind, dq
    const s: [number, number, number, number, number][] = []; // owner,x,y,kind,dq
    const p: [number, number, number, number][] = [];         // x,y,kind,dq
    for (const a of this.agents) {
      if (!a.alive) continue;
      for (let k = 0; k < 3; k++) {
        if (a.carried[k] > 1e-6) {
          const dq = -a.carried[k] * P.RESOURCES[k].carryDecay;
          a.carried[k] += dq;
          c.push([a.id, k, dq]);
        }
      }
    }
    for (const cache of this.world.caches) {
      for (let k = 0; k < 3; k++) {
        if (cache.q[k] > 1e-6) {
          const dq = -cache.q[k] * P.RESOURCES[k].cacheDecay;
          cache.q[k] += dq;
          s.push([cache.owner, cache.x, cache.y, k, dq]);
        }
      }
    }
    for (const sp of this.world.spills) {
      for (let k = 0; k < 3; k++) {
        if (sp.q[k] > 1e-6) {
          const dq = -sp.q[k] * P.SPILL_DECAY;
          sp.q[k] += dq;
          p.push([sp.x, sp.y, k, dq]);
        }
      }
    }
    this.world.spills = this.world.spills.filter(
      sp => sp.q[0] + sp.q[1] + sp.q[2] >= 0.02);
    this.ledger.append(t, 'world', 'world.decay', -1, { c, s, p });
  }

  private worldMetabolism(t: number): void {
    const d: [number, number, number][] = [];   // agent, dEnergy, dHealth
    const id = this.ledger.entries.length;      // this entry's id, for lastHarm
    for (const a of this.agents) {
      if (!a.alive) continue;
      const drain = this.cfg.m1 && t - a.bornTick < M1.DEP_AGE
        ? P.BASE_DRAIN * M1.DEP_DRAIN : P.BASE_DRAIN;
      let dE = -Math.min(drain, a.energy);
      let dH = 0;
      if (a.energy + dE <= 0.01) {
        dH -= P.STARVE_DAMAGE;
        this.lastHarm.set(a.id, id);
      } else if (a.energy > 55 && a.health < P.HEALTH_MAX) {
        dH = Math.min(P.HEALTH_REGEN, P.HEALTH_MAX - a.health);
      }
      a.energy += dE;
      a.health += dH;
      d.push([a.id, dE, dH]);
    }
    this.ledger.append(t, 'world', 'world.metab', -1, { d });
  }

  /** ambient social cognition: co-presence breeds familiarity; trust fades */
  private memDrift(t: number): void {
    // rule-based batch (payload derivable from state; replay recomputes)
    this.ledger.append(t, 'world', 'mem.drift', -1, {});
    applyMemDrift(this.agents);
  }

  // ---- one agent's turn ----------------------------------------------------

  private agentTurn(a: AgentState, t: number): void {
    const pc = this.percept(a, t);
    this.noteNodes(a, pc, t);
    const ownCaches = this.world.caches.filter(c => c.owner === a.id);
    const m1opts: M1Opts | undefined = this.cfg.m1
      ? { age: t - a.bornTick,
          ...(this.cfg.ablateTokenBias ? { tokenBiasOff: true } : {}),
          ...(this.cfg.m2 ? { m2: true, vision: this.vision } : {}) }
      : undefined;
    const dec = decide(a, pc, ownCaches, this.noiseRng, m1opts);

    // M2: acting on a tip opens an outcome window (§2.2 — both parties will
    // update on how it turns out, and on nothing else)
    if (this.cfg.m2 && dec.intent.startsWith('heed2:')) {
      const [, em, tok, sx, sy, kHat] = dec.intent.split(':').map(Number);
      const existing = this.tips.findIndex(p => p.b === a.id);
      const tip = { b: a.id, emitter: em, tok, x: sx, y: sy, kHat,
                    deadline: t + M2.HEED_WINDOW, arrived: false };
      if (existing >= 0) this.tips[existing] = tip;
      else this.tips.push(tip);
    }

    const causes: number[] = [];
    for (const ep of dec.cites) if (ep.ledger >= 0) causes.push(ep.ledger);
    const target = actionTarget(dec.action);
    // snapshot of the social memory actually read while scoring this action —
    // the live memory→decision edge, inspectable per decision (§9 thought log)
    let soc: { b: number; tr: number; fa: number } | undefined;
    if (target >= 0) {
      const rec = a.social.get(target);
      if (rec && rec.lastLedger >= 0) causes.push(rec.lastLedger);
      soc = { b: target,
              tr: Math.round((rec?.trust ?? 0) * 1000) / 1000,
              fa: Math.round((rec?.familiarity ?? 0) * 1000) / 1000 };
    }
    const decId = this.ledger.append(t, 'agent', 'decision', a.id, {
      act: dec.action, intent: dec.intent,
      score: Math.round(dec.rawScore * 1000) / 1000,
      top: dec.top, w: dec.driveWeights,
      ...(soc ? { soc } : {}),
    }, causes);

    this.resolve(a, dec.action, dec.intent, decId, t);
  }

  private resolve(a: AgentState, act: Action, intent: string,
                  decId: number, t: number): void {
    switch (act.t) {
      case 'rest':
        this.ledger.append(t, 'agent', 'act.rest', a.id, { a: a.id }, [decId]);
        break;

      case 'move': case 'follow': {
        const dx = act.t === 'follow'
          ? Math.sign(this.agents[act.target].x - a.x) : act.dx;
        const dy = act.t === 'follow'
          ? Math.sign(this.agents[act.target].y - a.y) : act.dy;
        let nx = clampW(a.x + dx), ny = clampW(a.y + dy);
        if (this.cfg.m2 && m2Blocked(nx, ny, t)) {
          // the divide is a world rule: blocked steps slide along it
          if (!m2Blocked(clampW(a.x + dx), a.y, t)) {
            nx = clampW(a.x + dx); ny = a.y;
          } else if (!m2Blocked(a.x, clampW(a.y + dy), t)) {
            nx = a.x; ny = clampW(a.y + dy);
          } else {
            nx = a.x; ny = a.y;
          }
        }
        const dE = -Math.min(P.MOVE_DRAIN, a.energy);
        a.x = nx; a.y = ny; a.energy += dE;
        if (act.t === 'follow') a.followTarget = act.target;
        this.ledger.append(t, 'agent',
          act.t === 'follow' ? 'act.follow' : 'act.move', a.id,
          { a: a.id, x: nx, y: ny, dE, b: act.t === 'follow' ? act.target : -1,
            intent }, [decId]);
        break;
      }

      case 'gather': {
        const room = P.CARRY_MAX - carriedTotal(a);
        const sp = this.world.spills.find(s => s.x === a.x && s.y === a.y);
        if (sp) {
          const k = ([0, 2, 1] as Kind[]).find(kk => sp.q[kk] > 0.25);
          if (k !== undefined) {
            const g = Math.min(P.RESOURCES[k].gatherRate * 1.5, sp.q[k], room);
            sp.q[k] -= g; a.carried[k] += g;
            this.ledger.append(t, 'agent', 'act.gather', a.id,
              { a: a.id, src: 's', x: a.x, y: a.y, k, g }, [decId]);
            break;
          }
        }
        const n = this.world.nodes.find(
          nn => nn.x === a.x && nn.y === a.y && nn.q > 0.25);
        if (!n) {
          this.ledger.append(t, 'agent', 'act.gather-fail', a.id,
            { a: a.id, reason: 'empty' }, [decId]);
        } else if (!nodeOpen(n.k, t)) {
          const eid = this.ledger.append(t, 'agent', 'act.gather-fail', a.id,
            { a: a.id, n: n.id, reason: 'sealed' }, [decId]);
          this.episode(a, t, 'gather-sealed', -1, n.x, n.y, n.k, 0, 0.45, eid);
        } else {
          const g = Math.min(P.RESOURCES[n.k].gatherRate, n.q, room);
          n.q -= g; a.carried[n.k] += g;
          const eid = this.ledger.append(t, 'agent', 'act.gather', a.id,
            { a: a.id, src: 'n', n: n.id, k: n.k, g }, [decId]);
          if (this.cfg.m1) {
            this.gathers.push([t, a.id, n.x, n.y, n.k]);
            this.watched(a, t, n.x, n.y, n.k, g, eid);
          }
          if (this.cfg.m2) this.tipOutcome(a, n.k, t, eid);
        }
        break;
      }

      case 'eat': {
        const amt = Math.min(P.EAT_AMOUNT, a.carried[act.kind]);
        const dE = Math.min(amt * P.RESOURCES[act.kind].nutrition,
                            P.ENERGY_MAX - a.energy);
        a.carried[act.kind] -= amt; a.energy += dE;
        const eid = this.ledger.append(t, 'agent', 'act.eat', a.id,
          { a: a.id, k: act.kind, amt, dE }, [decId]);
        if (a.energy < 20) {
          this.episode(a, t, 'starving', -1, a.x, a.y, -1, 0, 0.8, eid);
        }
        break;
      }

      case 'store': {
        const amt = Math.max(0, a.carried[act.kind] - 2.5);
        if (amt <= 0) {
          this.ledger.append(t, 'agent', 'act.rest', a.id, { a: a.id }, [decId]);
          break;
        }
        a.carried[act.kind] -= amt;
        const cache = this.cacheAt(a.id, a.x, a.y, true)!;
        cache.q[act.kind] += amt;
        this.ledger.append(t, 'agent', 'act.store', a.id,
          { a: a.id, k: act.kind, amt, x: a.x, y: a.y }, [decId]);
        break;
      }

      case 'give': {
        const b = this.agents[act.target];
        if (!b.alive || chebA(a, b) > 1) {
          this.ledger.append(t, 'agent', 'act.rest', a.id, { a: a.id }, [decId]);
          break;
        }
        const room = P.CARRY_MAX - carriedTotal(b);
        const amt = Math.min(a.carried[act.kind] * P.GIVE_FRACTION, P.GIVE_MAX,
                             Math.max(room, 0));
        if (amt < 0.25) {
          this.ledger.append(t, 'agent', 'act.rest', a.id, { a: a.id }, [decId]);
          break;
        }
        a.carried[act.kind] -= amt; b.carried[act.kind] += amt;
        const eid = this.ledger.append(t, 'agent', 'act.give', a.id,
          { a: a.id, b: b.id, k: act.kind, amt }, [decId]);
        this.events.push({ tick: t, type: 'give', a: a.id, b: b.id,
                           k: act.kind, amt, ledger: eid });
        const value = amt * P.RESOURCES[act.kind].nutrition;
        this.episode(a, t, 'gift-out', b.id, a.x, a.y, act.kind, amt, 0.55, eid);
        this.episode(b, t, 'gift-in', a.id, b.x, b.y, act.kind, amt,
                     Math.min(1, 0.6 + value / 30), eid);
        // the receiver learns the giver can be counted on; the giver warms too
        this.social(b, a.id, P.TRUST_GIFT * Math.min(1.6, value / 9),
                    P.FAMILIARITY_STEP * 3, t, eid);
        this.social(a, b.id, P.TRUST_GIFT_GIVER, P.FAMILIARITY_STEP * 3, t, eid);
        break;
      }

      case 'take': {
        const b = this.agents[act.target];
        if (!b.alive || chebA(a, b) > 1) {
          this.ledger.append(t, 'agent', 'act.rest', a.id, { a: a.id }, [decId]);
          break;
        }
        let k = 0 as Kind, bestVal = -1;
        for (const kk of [0, 1, 2] as Kind[]) {
          const v = b.carried[kk] * P.RESOURCES[kk].nutrition;
          if (v > bestVal) { bestVal = v; k = kk; }
        }
        const room = P.CARRY_MAX - carriedTotal(a);
        const amt = Math.min(P.TAKE_AMOUNT, b.carried[k], Math.max(room, 0));
        if (amt < 0.2) {
          this.ledger.append(t, 'agent', 'act.rest', a.id, { a: a.id }, [decId]);
          break;
        }
        b.carried[k] -= amt; a.carried[k] += amt;
        const eid = this.ledger.append(t, 'agent', 'act.take', a.id,
          { a: a.id, b: b.id, k, amt }, [decId]);
        this.events.push({ tick: t, type: 'take', a: a.id, b: b.id, k, amt,
                           ledger: eid });
        const value = amt * P.RESOURCES[k].nutrition;
        this.episode(b, t, 'theft-in', a.id, b.x, b.y, k, amt, 0.9, eid);
        this.social(b, a.id, P.TRUST_THEFT * Math.min(1.5, 0.5 + value / 14),
                    P.FAMILIARITY_STEP * 2, t, eid);
        this.witness(a, b, t, 'theft-seen', eid, P.TRUST_THEFT * 0.45);
        break;
      }

      case 'takeCache': {
        const cache = this.cacheAt(act.owner, a.x, a.y, false);
        if (!cache || cache.q[act.kind] < 0.2) {
          this.ledger.append(t, 'agent', 'act.rest', a.id, { a: a.id }, [decId]);
          break;
        }
        const room = P.CARRY_MAX - carriedTotal(a);
        const amt = Math.min(P.TAKE_AMOUNT, cache.q[act.kind], Math.max(room, 0));
        cache.q[act.kind] -= amt; a.carried[act.kind] += amt;
        const own = act.owner === a.id;
        const eid = this.ledger.append(t, 'agent',
          own ? 'act.withdraw' : 'act.loot', a.id,
          { a: a.id, o: act.owner, k: act.kind, amt, x: a.x, y: a.y }, [decId]);
        if (!own) {
          const owner = this.agents[act.owner];
          const seen = owner.alive && chebA(owner, a) <= this.vision && !(this.cfg.m2 && m2CrossBlocked(owner.x, a.x, t));
          this.events.push({ tick: t, type: 'loot', a: a.id, b: act.owner,
                             k: act.kind, amt, ledger: eid, w: seen });
          // the owner only learns of it if they can see it happen (§3.3:
          // imperfect information is what makes defection viable)
          if (seen) {
            this.episode(owner, t, 'theft-in', a.id, a.x, a.y, act.kind, amt,
                         0.9, eid);
            this.social(owner, a.id, P.TRUST_THEFT, P.FAMILIARITY_STEP * 2,
                        t, eid);
          }
          this.witness(a, owner, t, 'theft-seen', eid, P.TRUST_THEFT * 0.45);
        }
        break;
      }

      case 'attack': {
        const b = this.agents[act.target];
        if (!b.alive || chebA(a, b) > 1) {
          this.ledger.append(t, 'agent', 'act.rest', a.id, { a: a.id }, [decId]);
          break;
        }
        const dmg = P.ATTACK_DAMAGE * (0.7 + 0.6 * a.traits.aggression);
        b.health -= dmg;
        const spoil: [number, number, number] = [0, 0, 0];
        const room = P.CARRY_MAX - carriedTotal(a);
        let taken = 0;
        for (const k of [0, 2, 1] as Kind[]) {
          const amt = Math.min(b.carried[k] * P.ATTACK_SPOIL,
                               Math.max(room - taken, 0));
          spoil[k] = amt; taken += amt;
          b.carried[k] -= amt; a.carried[k] += amt;
        }
        const eid = this.ledger.append(t, 'agent', 'act.attack', a.id,
          { a: a.id, b: b.id, dmg, spoil }, [decId]);
        this.lastHarm.set(b.id, eid);
        this.events.push({ tick: t, type: 'attack', a: a.id, b: b.id, k: -1,
                           amt: dmg, ledger: eid });
        this.episode(b, t, 'attack-in', a.id, b.x, b.y, -1, dmg, 1.0, eid);
        this.episode(a, t, 'attack-out', b.id, a.x, a.y, -1, dmg, 0.5, eid);
        this.social(b, a.id, P.TRUST_ATTACK, P.FAMILIARITY_STEP * 2, t, eid);
        this.witness(a, b, t, 'attack-seen', eid, P.TRUST_ATTACK * 0.4);
        break;
      }

      case 'signal': {
        const dE = -Math.min(this.cfg.m1 ? M1.SIGNAL_COST : P.SIGNAL_COST,
                             a.energy);
        a.energy += dE;
        const token = this.cfg.m1 ? (act.token ?? -1) : -1;
        const eid = this.ledger.append(t, 'agent', 'act.signal', a.id,
          { a: a.id, mode: act.mode, x: a.x, y: a.y, dE,
            ...(token >= 0 ? { token } : {}) }, [decId]);
        this.world.signals.push({ from: a.id, x: a.x, y: a.y,
                                  mode: act.mode, tick: t,
                                  ...(token >= 0 ? { token } : {}) });
        this.events.push({ tick: t, type: 'signal', a: a.id, b: -1,
                           k: act.mode, amt: 0, ledger: eid,
                           ...(token >= 0 ? { o: token } : {}) });
        if (this.cfg.m1) {
          // the emitter remembers its own call: suppresses repeat distress,
          // satisfies its own company-seeking, carries no imitation weight
          this.episode(a, t, 'signaled', -1, a.x, a.y, token, act.mode,
                       0.2, eid);
        }
        // M2: what was the caller looking at? (measurement-side only —
        // derived from the same rule the caller's decision used; never
        // transmitted to any hearer)
        let ref = -1;
        if (this.cfg.m2 && act.mode === 1) {
          let bestV = 0;
          for (const n of this.world.nodes) {
            if (cheb(a.x, a.y, n.x, n.y) > this.vision) continue;
            if (!nodeOpen(n.k, t) || n.q <= M2.ABUND_Q * m2NodeSpec(n.k).cap) continue;
            const v = P.RESOURCES[n.k].nutrition * n.q;
            if (v > bestV) { bestV = v; ref = n.k; }
          }
        }
        const hearerLog: [number, number][] = [];
        for (const o of this.agents) {
          if (o.id === a.id || !o.alive) continue;
          if (chebA(o, a) > this.sigR) continue;
          if (this.cfg.m2 && m2CrossBlocked(o.x, a.x, t)) continue;
          // the heard mark (k = token) is the veil-level percept; its
          // weight exists only when the observation channel is on
          let w: number | undefined;
          if (this.cfg.m1 && !this.cfg.ablateObservation && token >= 0) {
            const rec = o.social.get(a.id);
            w = Math.min(1.25, 0.4 + 0.6 * Math.max(0, rec?.trust ?? 0) +
                               0.25 * (rec?.familiarity ?? 0));
          }
          this.episode(o, t, 'signal-heard', a.id, a.x, a.y, token, act.mode,
                       act.mode === 0 ? 0.75 : 0.5, eid, w);
          if (this.cfg.m2 && act.mode === 1) {
            // could the hearer see a rich open node itself? (asymmetry flag
            // for the measurement, and the grounding condition below)
            let seesK = -1, seesV = 0;
            for (const n of this.world.nodes) {
              if (cheb(o.x, o.y, n.x, n.y) > this.vision) continue;
              if (this.cfg.m2 && m2CrossBlocked(o.x, n.x, t)) continue;
              if (!nodeOpen(n.k, t) || n.q <= M2.ABUND_Q * m2NodeSpec(n.k).cap) continue;
              const v = P.RESOURCES[n.k].nutrition * n.q;
              if (v > seesV) { seesV = v; seesK = n.k; }
            }
            hearerLog.push([o.id, seesK >= 0 ? 1 : 0]);
            // hear-while-seeing acquisition (§2.3): the child-at-the-elbow
            // path. Off under ablation A (no confidence updates) and under
            // ablation C (no social learning).
            if (token >= 0 && seesK >= 0 && !this.cfg.ablateReinforce &&
                !this.cfg.ablateObservation) {
              const rec = o.social.get(a.id);
              const cw = Math.min(1.25, 0.4 + 0.6 * Math.max(0, rec?.trust ?? 0) +
                                        0.25 * (rec?.familiarity ?? 0));
              const dCo = M2.LEX_DELTA_CO * cw;
              const lCo = M2.LEX_LAT * dCo / M2.LEX_DELTA_FOUND;
              const post = lexBump(o, token, seesK, dCo, lCo);
              this.ledger.append(t, 'agent', 'mem.lex', o.id,
                { a: o.id, tk: token, k: seesK,
                  d: dCo, l: lCo, c: r3(post) }, [eid]);
            }
          }
        }
        if (this.cfg.m2 && act.mode === 1) {
          this.emissions.push({ t, a: a.id, mode: act.mode, tok: token,
                                x: a.x, y: a.y, ref, hearers: hearerLog });
        }
        break;
      }
    }
  }

  // ---- deaths --------------------------------------------------------------

  private deaths(t: number): void {
    for (const a of this.agents) {
      if (!a.alive || (a.health > 0 && !this.agedToDie.has(a.id))) continue;
      a.alive = false;
      a.diedTick = t;
      a.followTarget = -1;
      const drop: [number, number, number] = [...a.carried];
      a.carried = [0, 0, 0];
      if (drop[0] + drop[1] + drop[2] > 0.02) {
        const sp = this.spillAt(a.x, a.y, true)!;
        for (let k = 0; k < 3; k++) sp.q[k] += drop[k];
      }
      const aged = a.health > 0 && this.agedToDie.has(a.id);
      const causeId = aged ? undefined : this.lastHarm.get(a.id);
      const cause = aged ? 'age' : a.energy <= 0.01 ? 'starvation' : 'violence';
      const eid = this.ledger.append(t, aged ? 'stochastic' : 'world',
        'agent.death', a.id, { a: a.id, cause, x: a.x, y: a.y, drop },
        causeId !== undefined ? [causeId] : []);
      this.events.push({ tick: t, type: 'death', a: a.id, b: -1, k: -1,
                         amt: 0, ledger: eid });
    }
    this.agedToDie.clear();
  }

  // ---- perception (§2.2: the veil — structured, schema-only) ---------------

  percept(a: AgentState, t: number): Percept {
    const R = this.vision;
    // the M2 divide blocks perception while closed — no sight, no sound,
    // no knowledge crosses it (§2.4 isolation is structural, not advisory)
    const sees = (x: number) =>
      !this.cfg.m2 || !m2CrossBlocked(a.x, x, t);
    const nodes = this.world.nodes
      .filter(n => cheb(a.x, a.y, n.x, n.y) <= R && n.q > 0.1 && sees(n.x))
      .map(n => ({ x: n.x, y: n.y, k: n.k, q: round2(n.q),
                   open: nodeOpen(n.k, t) }));
    const agents = this.agents
      .filter(b => b.alive && b.id !== a.id &&
                   cheb(a.x, a.y, b.x, b.y) <= R && sees(b.x))
      .map(b => ({
        id: b.id, x: b.x, y: b.y,
        band: b.energy < 25 ? 0 : b.energy < 60 ? 1 : 2,
        load: carriedTotal(b) < 2 ? 0 : carriedTotal(b) < 10 ? 1 : 2,
      }));
    const signals = this.world.signals
      .filter(s => cheb(a.x, a.y, s.x, s.y) <= this.sigR && sees(s.x))
      .map(s => ({ from: s.from, x: s.x, y: s.y, mode: s.mode,
                   age: t - s.tick, tok: s.token ?? -1 }));
    const caches = this.world.caches
      .filter(c => cheb(a.x, a.y, c.x, c.y) <= R &&
                   c.q[0] + c.q[1] + c.q[2] > 0.3 && sees(c.x))
      .map(c => ({ owner: c.owner, x: c.x, y: c.y,
                   q: c.q.map(round2) as [number, number, number] }));
    const spills = [] as { x: number; y: number; k: Kind; q: number }[];
    for (const sp of this.world.spills) {
      if (cheb(a.x, a.y, sp.x, sp.y) > R || !sees(sp.x)) continue;
      for (const k of [0, 1, 2] as Kind[]) {
        if (sp.q[k] > 0.25) spills.push({ x: sp.x, y: sp.y, k, q: round2(sp.q[k]) });
      }
    }
    return {
      tick: t,
      self: { x: a.x, y: a.y, energy: round2(a.energy), health: round2(a.health),
              carried: a.carried.map(round2) as [number, number, number],
              cached: [0, 0, 0] },
      atmos: round2(atmosphere(t)),
      nodes, agents, signals, caches, spills,
    };
  }

  /** commit notable node sightings to episodic memory (throttled) */
  private noteNodes(a: AgentState, pc: Percept, t: number): void {
    const seen = this.nodeSeen.get(a.id)!;
    for (const n of pc.nodes) {
      const cap = this.cfg.m1 ? m1NodeSpec(n.k).cap : P.RESOURCES[n.k].cap;
      if (n.q < 0.3 * cap) continue;
      const node = this.world.nodes.find(nn => nn.x === n.x && nn.y === n.y &&
                                               nn.k === n.k)!;
      const last = seen.get(node.id);
      if (last !== undefined && t - last < 150) continue;
      seen.set(node.id, t);
      const eid = this.ledger.append(t, 'agent', 'mem.ep', a.id, {
        a: a.id, ep: null,   // filled below (episode carries its own entry id)
      });
      const ep: Episode = { tick: t, type: 'node-seen', who: -1, x: n.x, y: n.y,
                            k: n.k, amount: n.q, salience: 0.4, ledger: eid };
      const entry = this.ledger.get(eid);
      if (entry) entry.data.ep = ep;
      writeEpisode(a, ep);
    }
  }

  // ---- memory + social plumbing (every write is a ledger entry) ------------

  private episode(a: AgentState, t: number, type: EpisodeType, who: number,
                  x: number, y: number, k: number, amount: number,
                  salience: number, cause: number, w?: number): void {
    if (!a.alive) return;
    const eid = this.ledger.append(t, 'agent', 'mem.ep', a.id, { a: a.id, ep: null },
                                   [cause]);
    const ep: Episode = { tick: t, type, who, x, y, k, amount, salience,
                          ledger: eid, ...(w !== undefined ? { w } : {}) };
    const entry = this.ledger.get(eid);
    if (entry) entry.data.ep = ep;
    writeEpisode(a, ep);
  }

  /** update owner's social record of `other`; frozen under ablation (§5) */
  private social(owner: AgentState, other: number, dTrust: number, dFam: number,
                 t: number, cause: number): void {
    if (this.cfg.ablateSocial || !owner.alive) return;
    const rec = socialMut(owner, other);
    const causes = rec.lastLedger >= 0 ? [cause, rec.lastLedger] : [cause];
    rec.trust = clampTrust(rec.trust + dTrust);
    rec.familiarity = Math.min(1, rec.familiarity + dFam);
    rec.lastTick = t;
    rec.lastLedger = this.ledger.append(t, 'agent', 'mem.trust', owner.id, {
      a: owner.id, b: other,
      tr: rec.trust, fa: rec.familiarity, lt: t,
    }, causes);
  }

  /**
   * M2 (§2.2): the world resolves a tip. The hearer, having gathered near
   * the called site, associates the mark with WHAT IT FOUND — its own
   * percept, not a label. The emitter, if it can see the hearer succeed,
   * reinforces its own association. A good tip warms trust; nothing tells
   * either party what the mark "really" refers to.
   */
  private tipOutcome(b: AgentState, kFound: number, t: number,
                     gatherEid: number): void {
    const i = this.tips.findIndex(p => p.b === b.id && t <= p.deadline &&
      cheb(b.x, b.y, p.x, p.y) <= M2.HEED_RADIUS);
    if (i < 0) return;
    const tip = this.tips[i];
    this.tips.splice(i, 1);
    if (this.cfg.ablateReinforce) return;
    const post = lexBump(b, tip.tok, kFound, M2.LEX_DELTA_FOUND, M2.LEX_LAT);
    this.ledger.append(t, 'agent', 'mem.lex', b.id,
      { a: b.id, tk: tip.tok, k: kFound, d: M2.LEX_DELTA_FOUND,
        l: M2.LEX_LAT, c: r3(post) },
      [gatherEid]);
    this.social(b, tip.emitter, M2.TRUST_TIP_GOOD, P.FAMILIARITY_STEP, t,
                gatherEid);
    const em = this.agents[tip.emitter];
    if (em?.alive && chebA(em, b) <= this.vision &&
        !(this.cfg.m2 && m2CrossBlocked(em.x, b.x, t))) {
      const lEmit = M2.LEX_LAT * M2.LEX_DELTA_EMIT / M2.LEX_DELTA_FOUND;
      const postE = lexBump(em, tip.tok, kFound, M2.LEX_DELTA_EMIT, lEmit);
      this.ledger.append(t, 'agent', 'mem.lex', em.id,
        { a: em.id, tk: tip.tok, k: kFound, d: M2.LEX_DELTA_EMIT,
          l: lEmit, c: r3(postE) }, [gatherEid]);
    }
  }

  /** expire acted-on tips: an arrival that found nothing weakens the mark */
  private tipExpiry(t: number): void {
    for (let i = this.tips.length - 1; i >= 0; i--) {
      const tip = this.tips[i];
      const b = this.agents[tip.b];
      if (!b.alive) { this.tips.splice(i, 1); continue; }
      if (cheb(b.x, b.y, tip.x, tip.y) <= M2.HEED_RADIUS) tip.arrived = true;
      if (t <= tip.deadline) continue;
      this.tips.splice(i, 1);
      if (!tip.arrived || this.cfg.ablateReinforce) continue;
      const post = lexBump(b, tip.tok, tip.kHat, -M2.LEX_DELTA_FAIL);
      const eid = this.ledger.append(t, 'agent', 'mem.lex', b.id,
        { a: b.id, tk: tip.tok, k: tip.kHat, d: -M2.LEX_DELTA_FAIL,
          c: r3(post) });
      this.social(b, tip.emitter, M2.TRUST_TIP_BAD, 0, t, eid);
    }
  }

  /**
   * The observation channel (SPEC-M1 §3.3): anyone who can see the actor
   * gather records a low-salience watch entry — action, place, actor, tick —
   * whose weight is the watcher's regard for the actor at that moment. It is
   * a percept written to memory, nothing more; the bounded bias it feeds is
   * applied in the watcher's own scoring. Throttled per (watcher, actor) so
   * standing beside someone doesn't flood the ledger.
   */
  private watched(actor: AgentState, t: number, x: number, y: number,
                  k: number, amount: number, eventId: number): void {
    if (this.cfg.ablateObservation) return;
    for (const o of this.agents) {
      if (!o.alive || o.id === actor.id) continue;
      if (cheb(o.x, o.y, actor.x, actor.y) > this.vision || (this.cfg.m2 && m2CrossBlocked(o.x, actor.x, t))) continue;
      const key = o.id * 10000 + actor.id;
      const last = this.lastWatch.get(key);
      if (last !== undefined && t - last < M1.OBS_THROTTLE) continue;
      this.lastWatch.set(key, t);
      const rec = o.social.get(actor.id);
      const w = Math.min(1.25, 0.4 + 0.6 * Math.max(0, rec?.trust ?? 0) +
                               0.25 * (rec?.familiarity ?? 0));
      this.episode(o, t, 'saw-gather', actor.id, x, y, k, amount,
                   M1.OBS_SALIENCE, eventId, w);
    }
  }

  /** bystanders who can see a transgression remember it too */
  private witness(actor: AgentState, victim: AgentState, t: number,
                  type: EpisodeType, eventId: number, dTrust: number): void {
    for (const o of this.agents) {
      if (!o.alive || o.id === actor.id || o.id === victim.id) continue;
      if (cheb(o.x, o.y, actor.x, actor.y) > this.vision || (this.cfg.m2 && m2CrossBlocked(o.x, actor.x, t))) continue;
      this.episode(o, t, type, actor.id, actor.x, actor.y, -1, 0, 0.6, eventId);
      this.social(o, actor.id, dTrust, P.FAMILIARITY_STEP, t, eventId);
    }
  }

  // ---- helpers -------------------------------------------------------------

  private cacheAt(owner: number, x: number, y: number, create: boolean): Cache | null {
    let c = this.world.caches.find(cc => cc.owner === owner && cc.x === x &&
                                         cc.y === y) ?? null;
    if (!c && create) {
      c = { owner, x, y, q: [0, 0, 0] };
      this.world.caches.push(c);
    }
    return c;
  }

  private spillAt(x: number, y: number, create: boolean) {
    let s = this.world.spills.find(ss => ss.x === x && ss.y === y) ?? null;
    if (!s && create) {
      s = { x, y, q: [0, 0, 0] as [number, number, number] };
      this.world.spills.push(s);
    }
    return s;
  }

  private record(t: number): void {
    this.frames.push({
      tick: t,
      agents: this.agents.filter(a => a.alive).map(a =>
        [a.id, a.x, a.y, Math.round(a.energy),
         Math.round(energyValue(a.carried))]),
    });
    if (t % 5 === 0) {
      this.nodeSnaps.push({ tick: t,
        q: this.world.nodes.map(n => Math.round(n.q * 10) / 10) });
      this.cacheSnaps.push({ tick: t,
        c: this.world.caches.map(cc =>
          [cc.owner, cc.x, cc.y, Math.round(energyValue(cc.q))]) });
    }
  }
}

/** shared with replay: the ambient familiarity/trust-fade rule */
export function applyMemDrift(agents: AgentState[]): void {
  for (const a of agents) {
    if (!a.alive) continue;
    for (const b of agents) {
      if (b.id === a.id || !b.alive) continue;
      if (cheb(a.x, a.y, b.x, b.y) <= 1) {
        const rec = socialMut(a, b.id);
        rec.familiarity = Math.min(1, rec.familiarity + P.FAMILIARITY_STEP * 0.25);
      }
    }
    for (const rec of a.social.values()) {
      rec.trust *= 1 - P.TRUST_DECAY;
    }
  }
}

function cheb(ax: number, ay: number, bx: number, by: number): number {
  return Math.max(Math.abs(ax - bx), Math.abs(ay - by));
}
function chebA(a: { x: number; y: number }, b: { x: number; y: number }): number {
  return cheb(a.x, a.y, b.x, b.y);
}
function clampW(v: number): number {
  return v < 0 ? 0 : v >= P.WORLD ? P.WORLD - 1 : v;
}
function round2(v: number): number { return Math.round(v * 100) / 100; }
function r3(v: number): number { return Math.round(v * 1000) / 1000; }
function actionTarget(a: Action): number {
  switch (a.t) {
    case 'give': case 'take': case 'follow': case 'attack': return a.target;
    case 'takeCache': return a.owner;
    default: return -1;
  }
}
