import { P } from '../core/params.js';
import { RNG } from '../core/rng.js';
import type {
  Action, AgentState, Cache, Episode, EpisodeType, Kind, Percept, SimConfig,
  WorldState,
} from '../core/types.js';
import { carriedTotal, createAgents, energyValue } from '../agents/agent.js';
import { decide } from '../agents/decide.js';
import { clampTrust, socialMut, writeEpisode } from '../agents/memory.js';
import { generateWorld, atmosphere, nodeOpen } from '../world/world.js';
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
  ledger = new Ledger();
  events: SimEvent[] = [];
  frames: Frame[] = [];
  nodeSnaps: { tick: number; q: number[] }[] = [];
  cacheSnaps: { tick: number; c: number[][] }[] = [];

  private orderRng: RNG;
  private noiseRng: RNG;
  private lastHarm = new Map<number, number>();          // agent → ledger id
  private nodeSeen = new Map<number, Map<number, number>>(); // agent → node → tick

  constructor(cfg: SimConfig) {
    this.cfg = cfg;
    this.world = generateWorld(cfg.seed);
    this.agents = createAgents(cfg.seed);
    this.orderRng = new RNG(cfg.seed, `order:${cfg.stream}`);
    this.noiseRng = new RNG(cfg.seed, `noise:${cfg.stream}`);
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

    const order = this.orderRng.shuffle(
      this.agents.filter(a => a.alive).map(a => a.id));
    for (const id of order) {
      const a = this.agents[id];
      if (!a.alive) continue;
      this.agentTurn(a, t);
    }
    this.deaths(t);
    this.record(t);
    this.world.tick = t + 1;
  }

  // ---- world rules ---------------------------------------------------------

  private worldRegen(t: number): void {
    const d: [number, number][] = [];
    for (const n of this.world.nodes) {
      const spec = P.RESOURCES[n.k];
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
      let dE = -Math.min(P.BASE_DRAIN, a.energy);
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
    const dec = decide(a, pc, ownCaches, this.noiseRng);

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
        const nx = clampW(a.x + dx), ny = clampW(a.y + dy);
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
          this.ledger.append(t, 'agent', 'act.gather', a.id,
            { a: a.id, src: 'n', n: n.id, k: n.k, g }, [decId]);
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
          const seen = owner.alive && chebA(owner, a) <= P.VISION;
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
        const dE = -Math.min(P.SIGNAL_COST, a.energy);
        a.energy += dE;
        const eid = this.ledger.append(t, 'agent', 'act.signal', a.id,
          { a: a.id, mode: act.mode, x: a.x, y: a.y, dE }, [decId]);
        this.world.signals.push({ from: a.id, x: a.x, y: a.y,
                                  mode: act.mode, tick: t });
        this.events.push({ tick: t, type: 'signal', a: a.id, b: -1,
                           k: act.mode, amt: 0, ledger: eid });
        for (const o of this.agents) {
          if (o.id === a.id || !o.alive) continue;
          if (chebA(o, a) <= P.SIGNAL_RADIUS) {
            this.episode(o, t, 'signal-heard', a.id, a.x, a.y, -1, act.mode,
                         act.mode === 0 ? 0.75 : 0.5, eid);
          }
        }
        break;
      }
    }
  }

  // ---- deaths --------------------------------------------------------------

  private deaths(t: number): void {
    for (const a of this.agents) {
      if (!a.alive || a.health > 0) continue;
      a.alive = false;
      a.diedTick = t;
      a.followTarget = -1;
      const drop: [number, number, number] = [...a.carried];
      a.carried = [0, 0, 0];
      if (drop[0] + drop[1] + drop[2] > 0.02) {
        const sp = this.spillAt(a.x, a.y, true)!;
        for (let k = 0; k < 3; k++) sp.q[k] += drop[k];
      }
      const causeId = this.lastHarm.get(a.id);
      const cause = a.energy <= 0.01 ? 'starvation' : 'violence';
      const eid = this.ledger.append(t, 'world', 'agent.death', a.id,
        { a: a.id, cause, x: a.x, y: a.y, drop },
        causeId !== undefined ? [causeId] : []);
      this.events.push({ tick: t, type: 'death', a: a.id, b: -1, k: -1,
                         amt: 0, ledger: eid });
    }
  }

  // ---- perception (§2.2: the veil — structured, schema-only) ---------------

  percept(a: AgentState, t: number): Percept {
    const R = P.VISION;
    const nodes = this.world.nodes
      .filter(n => cheb(a.x, a.y, n.x, n.y) <= R && n.q > 0.1)
      .map(n => ({ x: n.x, y: n.y, k: n.k, q: round2(n.q),
                   open: nodeOpen(n.k, t) }));
    const agents = this.agents
      .filter(b => b.alive && b.id !== a.id && cheb(a.x, a.y, b.x, b.y) <= R)
      .map(b => ({
        id: b.id, x: b.x, y: b.y,
        band: b.energy < 25 ? 0 : b.energy < 60 ? 1 : 2,
        load: carriedTotal(b) < 2 ? 0 : carriedTotal(b) < 10 ? 1 : 2,
      }));
    const signals = this.world.signals
      .filter(s => cheb(a.x, a.y, s.x, s.y) <= P.SIGNAL_RADIUS)
      .map(s => ({ from: s.from, x: s.x, y: s.y, mode: s.mode,
                   age: t - s.tick }));
    const caches = this.world.caches
      .filter(c => cheb(a.x, a.y, c.x, c.y) <= R &&
                   c.q[0] + c.q[1] + c.q[2] > 0.3)
      .map(c => ({ owner: c.owner, x: c.x, y: c.y,
                   q: c.q.map(round2) as [number, number, number] }));
    const spills = [] as { x: number; y: number; k: Kind; q: number }[];
    for (const sp of this.world.spills) {
      if (cheb(a.x, a.y, sp.x, sp.y) > R) continue;
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
      if (n.q < 0.3 * P.RESOURCES[n.k].cap) continue;
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
      this.ledger.entries[eid].data.ep = ep;
      writeEpisode(a, ep);
    }
  }

  // ---- memory + social plumbing (every write is a ledger entry) ------------

  private episode(a: AgentState, t: number, type: EpisodeType, who: number,
                  x: number, y: number, k: number, amount: number,
                  salience: number, cause: number): void {
    if (!a.alive) return;
    const eid = this.ledger.append(t, 'agent', 'mem.ep', a.id, { a: a.id, ep: null },
                                   [cause]);
    const ep: Episode = { tick: t, type, who, x, y, k, amount, salience,
                          ledger: eid };
    this.ledger.entries[eid].data.ep = ep;
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

  /** bystanders who can see a transgression remember it too */
  private witness(actor: AgentState, victim: AgentState, t: number,
                  type: EpisodeType, eventId: number, dTrust: number): void {
    for (const o of this.agents) {
      if (!o.alive || o.id === actor.id || o.id === victim.id) continue;
      if (cheb(o.x, o.y, actor.x, actor.y) > P.VISION) continue;
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
function actionTarget(a: Action): number {
  switch (a.t) {
    case 'give': case 'take': case 'follow': case 'attack': return a.target;
    case 'takeCache': return a.owner;
    default: return -1;
  }
}
