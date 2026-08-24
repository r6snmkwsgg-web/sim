import { P } from '../core/params.js';
import type {
  AgentState, Cache, Episode, Kind, LedgerEntry, WorldState,
} from '../core/types.js';
import { createAgents } from '../agents/agent.js';
import { socialMut, writeEpisode } from '../agents/memory.js';
import { generateWorld } from '../world/world.js';
import { applyMemDrift } from './engine.js';

/**
 * Ledger replay (§4.1's teeth).
 *
 * Reconstructs the entire final state — agents, memory, social records,
 * nodes, caches, spills, signals — from the initial seed plus the ledger
 * entries alone. If any code path mutated state without writing a
 * sufficient entry, the replayed hash diverges and the test fails.
 */

export interface Replica {
  world: WorldState;
  agents: AgentState[];
}

export function replay(seed: number, entries: LedgerEntry[]): Replica {
  const world = generateWorld(seed);
  const agents = createAgents(seed);
  let curTick = -1;

  const cacheAt = (owner: number, x: number, y: number): Cache => {
    let c = world.caches.find(cc => cc.owner === owner && cc.x === x && cc.y === y);
    if (!c) { c = { owner, x, y, q: [0, 0, 0] }; world.caches.push(c); }
    return c;
  };
  const spillAt = (x: number, y: number) => {
    let s = world.spills.find(ss => ss.x === x && ss.y === y);
    if (!s) { s = { x, y, q: [0, 0, 0] as [number, number, number] }; world.spills.push(s); }
    return s;
  };

  for (const e of entries) {
    const d = e.data as any;
    switch (e.type) {
      case 'world.regen': {
        if (e.tick !== curTick) {   // start of a tick: apply the signal-expiry rule
          curTick = e.tick;
          world.signals = world.signals.filter(s => e.tick - s.tick <= P.SIGNAL_TTL);
        }
        for (const [nid, dq] of d.d as [number, number][]) world.nodes[nid].q += dq;
        break;
      }
      case 'world.decay': {
        for (const [aid, k, dq] of d.c as [number, number, number][]) {
          agents[aid].carried[k] += dq;
        }
        for (const [o, x, y, k, dq] of d.s as [number, number, number, number, number][]) {
          cacheAt(o, x, y).q[k] += dq;
        }
        for (const [x, y, k, dq] of d.p as [number, number, number, number][]) {
          spillAt(x, y).q[k] += dq;
        }
        world.spills = world.spills.filter(sp => sp.q[0] + sp.q[1] + sp.q[2] >= 0.02);
        break;
      }
      case 'world.metab': {
        for (const [aid, dE, dH] of d.d as [number, number, number][]) {
          agents[aid].energy += dE;
          agents[aid].health += dH;
        }
        break;
      }
      case 'mem.drift':
        applyMemDrift(agents);
        break;

      case 'act.move': case 'act.follow': {
        const a = agents[d.a];
        a.x = d.x; a.y = d.y; a.energy += d.dE;
        if (e.type === 'act.follow') a.followTarget = d.b;
        break;
      }
      case 'act.gather': {
        const a = agents[d.a];
        if (d.src === 'n') world.nodes[d.n].q -= d.g;
        else spillAt(d.x, d.y).q[d.k as Kind] -= d.g;
        a.carried[d.k as Kind] += d.g;
        break;
      }
      case 'act.eat': {
        const a = agents[d.a];
        a.carried[d.k as Kind] -= d.amt;
        a.energy += d.dE;
        break;
      }
      case 'act.store': {
        agents[d.a].carried[d.k as Kind] -= d.amt;
        cacheAt(d.a, d.x, d.y).q[d.k as Kind] += d.amt;
        break;
      }
      case 'act.give': {
        agents[d.a].carried[d.k as Kind] -= d.amt;
        agents[d.b].carried[d.k as Kind] += d.amt;
        break;
      }
      case 'act.take': {
        agents[d.b].carried[d.k as Kind] -= d.amt;
        agents[d.a].carried[d.k as Kind] += d.amt;
        break;
      }
      case 'act.withdraw': case 'act.loot': {
        cacheAt(d.o, d.x, d.y).q[d.k as Kind] -= d.amt;
        agents[d.a].carried[d.k as Kind] += d.amt;
        break;
      }
      case 'act.attack': {
        const a = agents[d.a], b = agents[d.b];
        b.health -= d.dmg;
        for (let k = 0; k < 3; k++) {
          b.carried[k] -= d.spoil[k];
          a.carried[k] += d.spoil[k];
        }
        break;
      }
      case 'act.signal': {
        const a = agents[d.a];
        a.energy += d.dE;
        world.signals.push({ from: d.a, x: d.x, y: d.y, mode: d.mode, tick: e.tick });
        break;
      }
      case 'agent.death': {
        const a = agents[d.a];
        a.alive = false; a.diedTick = e.tick; a.followTarget = -1;
        a.carried = [0, 0, 0];
        if (d.drop[0] + d.drop[1] + d.drop[2] > 0.02) {
          const sp = spillAt(d.x, d.y);
          for (let k = 0; k < 3; k++) sp.q[k] += d.drop[k];
        }
        break;
      }
      case 'mem.ep':
        writeEpisode(agents[d.a], d.ep as Episode);
        break;
      case 'mem.trust': {
        const rec = socialMut(agents[d.a], d.b);
        rec.trust = d.tr; rec.familiarity = d.fa; rec.debt = d.de;
        rec.lastTick = d.lt; rec.lastLedger = e.id;
        break;
      }
      // no state mutation:
      case 'decision': case 'act.rest': case 'act.gather-fail':
        break;
      default:
        throw new Error(`replay: unknown ledger entry type '${e.type}'`);
    }
  }
  world.tick = curTick + 1;
  return { world, agents };
}

/** Deterministic hash of the full simulation state (fnv1a over stable JSON). */
export function stateHash(world: WorldState, agents: AgentState[]): string {
  const parts: string[] = [];
  for (const a of agents) {
    const social = [...a.social.entries()].sort((p, q) => p[0] - q[0]);
    parts.push(JSON.stringify({
      id: a.id, alive: a.alive, x: a.x, y: a.y,
      e: a.energy, h: a.health, c: a.carried,
      f: a.followTarget, hx: a.homeX, hy: a.homeY,
      died: a.diedTick, eph: a.epHead,
      epi: a.episodic,
      soc: social,
    }));
  }
  parts.push(JSON.stringify(world.nodes.map(n => n.q)));
  parts.push(JSON.stringify(
    [...world.caches].sort((p, q) => p.owner - q.owner || p.x - q.x || p.y - q.y)));
  parts.push(JSON.stringify(
    [...world.spills].sort((p, q) => p.x - q.x || p.y - q.y)));
  parts.push(JSON.stringify(world.signals));
  let h1 = 0x811c9dc5, h2 = 0x01234567;
  for (const s of parts) {
    for (let i = 0; i < s.length; i++) {
      h1 = Math.imul(h1 ^ s.charCodeAt(i), 0x01000193) >>> 0;
      h2 = (Math.imul(h2 ^ s.charCodeAt(i), 0x5bd1e995) + (h2 >>> 13)) >>> 0;
    }
  }
  return h1.toString(16).padStart(8, '0') + h2.toString(16).padStart(8, '0');
}
