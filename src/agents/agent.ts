import { M1, M2, P, type TraitName } from '../core/params.js';
import { RNG } from '../core/rng.js';
import type { AgentState } from '../core/types.js';

/**
 * Agent state (§3.2): a database row plus a memory store, never a
 * conversation history. Milestone 0 runs everything at tier T1 — the
 * hand-written utility function in decide.ts. Zero LLM calls.
 */

export function createAgents(seed: number, n: number = P.N_AGENTS,
                             m1 = false, m2 = false): AgentState[] {
  const rng = new RNG(seed, 'agents');
  const agents: AgentState[] = [];
  for (let id = 0; id < n; id++) {
    const traits = {} as Record<TraitName, number>;
    for (const t of P.TRAITS) {
      traits[t] = clamp01(rng.normal(P.TRAIT_MEAN, P.TRAIT_SD));
    }
    let x = 6 + rng.int(P.WORLD - 12);
    const y = 6 + rng.int(P.WORLD - 12);
    if (m2) {
      // two founder populations, one per side of the barrier (SPEC-M2 §2.4)
      const west = id < n / 2;
      x = west ? 4 + rng.int(M2.BARRIER_X0 - 8)
               : M2.BARRIER_X1 + 4 + rng.int(P.WORLD - M2.BARRIER_X1 - 9);
    }
    // founders start age-staggered so mortality doesn't arrive as one wave
    const bornTick = m1 || m2 ? -rng.int(M1.FOUNDER_AGE_MAX) : 0;
    agents.push(blankAgent(id, x, y, traits, bornTick, 0, [-1, -1],
                           P.START_ENERGY));
  }
  return agents;
}

/** shared by founder creation, birth resolution, and ledger replay */
export function blankAgent(id: number, x: number, y: number,
                           traits: Record<TraitName, number>, bornTick: number,
                           gen: number, parents: [number, number],
                           energy: number): AgentState {
  return {
    id,
    alive: true,
    x, y,
    energy,
    health: P.HEALTH_MAX,
    carried: [0, 0, 0],
    traits,
    followTarget: -1,
    homeX: x, homeY: y,
    episodic: [],
    epHead: 0,
    social: new Map(),
    bornTick,
    diedTick: -1,
    gen,
    parents,
    lastRepro: -1,
  };
}

export function clamp01(v: number): number {
  return v < 0 ? 0 : v > 1 ? 1 : v;
}

export function carriedTotal(a: AgentState): number {
  return a.carried[0] + a.carried[1] + a.carried[2];
}

/** value of goods in energy units — used for wealth metrics and need estimates */
export function energyValue(q: [number, number, number]): number {
  return q[0] * P.RESOURCES[0].nutrition +
         q[1] * P.RESOURCES[1].nutrition +
         q[2] * P.RESOURCES[2].nutrition;
}
