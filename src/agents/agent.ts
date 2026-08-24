import { P, type TraitName } from '../core/params.js';
import { RNG } from '../core/rng.js';
import type { AgentState } from '../core/types.js';

/**
 * Agent state (§3.2): a database row plus a memory store, never a
 * conversation history. Milestone 0 runs everything at tier T1 — the
 * hand-written utility function in decide.ts. Zero LLM calls.
 */

export function createAgents(seed: number): AgentState[] {
  const rng = new RNG(seed, 'agents');
  const agents: AgentState[] = [];
  for (let id = 0; id < P.N_AGENTS; id++) {
    const traits = {} as Record<TraitName, number>;
    for (const t of P.TRAITS) {
      traits[t] = clamp01(rng.normal(P.TRAIT_MEAN, P.TRAIT_SD));
    }
    const x = 6 + rng.int(P.WORLD - 12);
    const y = 6 + rng.int(P.WORLD - 12);
    agents.push({
      id,
      alive: true,
      x, y,
      energy: P.START_ENERGY,
      health: P.HEALTH_MAX,
      carried: [0, 0, 0],
      traits,
      followTarget: -1,
      homeX: x, homeY: y,
      episodic: [],
      epHead: 0,
      social: new Map(),
      bornTick: 0,
      diedTick: -1,
    });
  }
  return agents;
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
