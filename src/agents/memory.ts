import { M1, P } from '../core/params.js';
import type { AgentState, Episode, EpisodeType, SocialRecord } from '../core/types.js';

/**
 * Memory (§3.3). Milestone 0 carries two of the five stores:
 *
 *  - episodic: a bounded ring buffer per agent. Bounded means lossy, and
 *    lossy is load-bearing: perfect recall would destroy the
 *    imperfect-information dynamics the milestone is testing.
 *  - social: per-relationship trust / familiarity. Asymmetric —
 *    A's record of B is not B's record of A — and built only from events
 *    the owner directly experienced or witnessed.
 *
 * Retrieval is scored, not exhaustive: salience × recency × relevance.
 */

export function writeEpisode(a: AgentState, ep: Episode): void {
  if (a.episodic.length < P.EPISODIC_CAP) {
    a.episodic.push(ep);
  } else {
    a.episodic[a.epHead] = ep;             // overwrite the oldest slot
  }
  a.epHead = (a.epHead + 1) % P.EPISODIC_CAP;

  // M1 observation channel (SPEC-M1 §3.3): watch entries accumulate into
  // decayed per-agent summaries that the decision loop reads as a bounded
  // bias. These are derived views over the ledgered episodic record — the
  // replay rebuilds them through this same function — and carry weight only
  // when the entry was written with one (`w` is absent under ablation A).
  if (ep.w === undefined) return;
  decayObs(a, ep.tick);
  if (ep.type === 'signal-heard' && ep.k >= 0) {
    if (!a.tokenObs) a.tokenObs = new Float64Array(M1.TOKENS);
    a.tokenObs[ep.k] += ep.w;
  } else if (ep.type === 'saw-gather') {
    if (!a.obsGrid) a.obsGrid = new Float64Array(M1.OBS_GRID * M1.OBS_GRID);
    const g = M1.OBS_GRID, cell = Math.floor(P.WORLD / g);
    const gx = Math.min(g - 1, Math.floor(ep.x / cell));
    const gy = Math.min(g - 1, Math.floor(ep.y / cell));
    a.obsGrid[gy * g + gx] += ep.w;
  }
}

/** bring the observation accumulators forward to `tick`, applying decay */
export function decayObs(a: AgentState, tick: number): void {
  const last = a.obsTick ?? tick;
  if (tick > last) {
    const f = Math.exp(-(tick - last) / M1.OBS_TAU);
    if (a.tokenObs) for (let i = 0; i < a.tokenObs.length; i++) a.tokenObs[i] *= f;
    if (a.obsGrid) for (let i = 0; i < a.obsGrid.length; i++) a.obsGrid[i] *= f;
  }
  a.obsTick = Math.max(last, tick);
}

/** decayed observed-gather weight around a map position (0 when unwatched) */
export function gatherObsAt(a: AgentState, x: number, y: number,
                            tick: number): number {
  if (!a.obsGrid) return 0;
  const f = Math.exp(-Math.max(0, tick - (a.obsTick ?? tick)) / M1.OBS_TAU);
  const g = M1.OBS_GRID, cell = Math.floor(P.WORLD / g);
  const gx = Math.min(g - 1, Math.floor(x / cell));
  const gy = Math.min(g - 1, Math.floor(y / cell));
  return a.obsGrid[gy * g + gx] * f;
}

export interface Retrieved {
  ep: Episode;
  score: number;
}

/**
 * Top-k episodes for a query. `relevance` maps an episode to 0..1; the
 * final score is salience × exp(-age/τ) × relevance.
 */
export function retrieve(a: AgentState, tick: number,
                         relevance: (ep: Episode) => number,
                         k: number = P.RETRIEVE_K): Retrieved[] {
  const scored: Retrieved[] = [];
  for (const ep of a.episodic) {
    const rel = relevance(ep);
    if (rel <= 0) continue;
    const score = ep.salience * Math.exp(-(tick - ep.tick) / P.RECENCY_TAU) * rel;
    if (score > 1e-4) scored.push({ ep, score });
  }
  scored.sort((p, q) => q.score - p.score);
  return scored.slice(0, k);
}

/** Convenience relevance filter by episode type(s). */
export function byType(...types: EpisodeType[]): (ep: Episode) => number {
  const set = new Set<string>(types);
  return ep => (set.has(ep.type) ? 1 : 0);
}

const NEUTRAL: SocialRecord = { trust: 0, familiarity: 0, lastTick: -1, lastLedger: -1 };

/** Read-only view of A's model of `other` (neutral default for strangers). */
export function socialOf(a: AgentState, other: number): SocialRecord {
  return a.social.get(other) ?? NEUTRAL;
}

export function socialMut(a: AgentState, other: number): SocialRecord {
  let r = a.social.get(other);
  if (!r) {
    r = { trust: 0, familiarity: 0, lastTick: -1, lastLedger: -1 };
    a.social.set(other, r);
  }
  return r;
}

export function clampTrust(v: number): number {
  return v < -1 ? -1 : v > 1 ? 1 : v;
}
