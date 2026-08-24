import { M2 } from '../core/params.js';
import { RNG } from '../core/rng.js';
import type { Frame, SimEvent } from './engine.js';

/**
 * PREREGISTERED MEASUREMENT — SPEC-M2 §5.
 *
 * Written in full before the first M2 simulation output was examined (only
 * compile checks were run). Definitions and thresholds are fixed; changing
 * them after looking at results voids the milestone. The §5.4 permutation
 * control is run FIRST in the report, per §5.4's own instruction.
 *
 * Definitions:
 *  - population: an agent's birth side of the barrier (west = 0, east = 1).
 *    Founders by spawn side; children by birth x. Migration after contact
 *    does not change an agent's population.
 *  - qualified (agent, class k, time t): the agent's strongest association
 *    for k has confidence ≥ 0.3 at the snapshot nearest t.
 *  - coherence (§5.1): for population p and class k — ≥10 qualified agents
 *    and ≥50% of them sharing one top token, sustained across ≥5 consecutive
 *    snapshots (1,000 ticks). Reported against a neutral-copying drift null.
 *  - communicative success (§5.2): a hear event is (emission of mode 1 with
 *    token T, hearer B alive, B could NOT see any rich open node at that
 *    tick — the §2.1 asymmetry, enforced per event). Success: B gathers
 *    within HEED_RADIUS of the emission origin within HEED_WINDOW ticks.
 *    Baseline: for each hear event, up to 3 deterministic control ticks for
 *    the same agent at matched distance (±2) from the same origin with no
 *    mode-1 emission audible in the trailing window; same success test.
 *  - kind alignment + permutation (§5.4): over successful hear events, the
 *    share where the kind B actually found equals the hearer-side
 *    population's production mapping for T (the class most often produced
 *    with T by that side in the trailing 1,500 ticks). Control: hold that
 *    mapping and all behavior fixed, permute tokens across the same side's
 *    mode-1 emissions, 200 reps. Tokens are differentiated only if the
 *    observed alignment sits ≥3 SD above the permuted distribution.
 *  - divergence (§5.3): at the last pre-contact snapshot, for classes
 *    coherent in BOTH populations: divergent if the modal tokens differ.
 *  - fidelity (§5.5): birth cohorts of 1,000 ticks; a cohort's mapping per
 *    class is the modal top-token among its qualified members at the
 *    snapshot nearest (cohort end + 250; amended, see below). fidelity(g) =
 *    share of classes (with ≥5 qualified members and ≥50% agreement in
 *    cohort g−1) whose modal token is unchanged in cohort g.
 *  - borrowing (§5.6): for each divergent class, the share (within a
 *    population's qualified members) holding the OTHER population's
 *    pre-contact modal token. Borrowed: that share rises ≥0.20 above its
 *    pre-contact level and holds for ≥2 consecutive snapshots. Adopters'
 *    mean final trust toward other-side agents is compared with
 *    non-adopters' (the M0 social layer check).
 *
 * POST-HOC AMENDMENTS (disclosed — measurement-code defects, not threshold
 * changes; each made the metric undefined or attributed behavior to the
 * wrong cause, and none was altered in response to a finite observed value):
 *  - a1 (§5.5): measure tick was cohort end + 1,200, but mean lifespan is
 *    ~390 ticks, so every cohort member was dead and absent from the
 *    snapshot at measurement — the metric returned NaN by construction in
 *    every run ever executed. Amended to cohort end + 250. No finite
 *    fidelity value was ever observed under the old offset.
 *  - a2 (§5.6): the borrowed-share scan had no minimum-denominator guard; a
 *    snapshot with 1–2 qualified members could read share 1.0 and trigger
 *    "borrowed" with zero final adopters (observed as an internally
 *    inconsistent report line). Snapshots with <10 qualified members (the
 *    §5.1 floor) now carry no information and are skipped.
 *  - a3 (§5.2): control ticks excluded audible calls only in the trailing
 *    window [t−50, t], but success is scored in the forward window
 *    (t, t+50] — a call landing inside the scored window could drive the
 *    control gather, contaminating the baseline with call-driven behavior.
 *    The exclusion now covers [t−50, t+50].
 *  - a4 (§5.1): the beats-drift gate compared the fraction of coherent
 *    cells (≤1 by definition) against driftRate + 0.2; at the qualified
 *    population sizes this world produces (~30), single-pool neutral drift
 *    concentrates with probability ~0.94, putting the bar at ~1.14 — no
 *    observation could ever pass, and every §6 verdict would read "fail"
 *    regardless of the data. Amended to the discriminating prediction of
 *    the same null: a single neutral pool can concentrate, but every agent
 *    holds ONE pool token, so two classes can never be simultaneously
 *    coherent on DIFFERENT tokens within one population. Beats-drift now
 *    requires exactly that pattern (≥2 classes, same population, coherent
 *    streaks overlapping at one snapshot, distinct modal tokens). The
 *    single-pool concentration probability is still reported as context.
 */

export interface EmissionLog {
  t: number; a: number; mode: number; tok: number; x: number; y: number;
  /** engine-derived richest visible kind for mode-1 emissions, else -1 */
  ref: number;
  /** [hearerId, couldSeeRichNode(0|1)] */
  hearers: [number, number][];
}

export interface LexSnap {
  tick: number;
  /** per living agent: [id, top0, conf0, top1, conf1, top2, conf2]
   *  (top = strongest token per class, -1 if none) */
  rows: number[][];
}

export interface M2RunData {
  ticks: number;
  contactTick: number;
  frames: Frame[];
  gathers: number[][];        // [tick, agent, x, y, kind]
  births: number[][];         // [tick, child, gen, pa, pb, x]
  events: SimEvent[];
  emissions: EmissionLog[];
  lexSnaps: LexSnap[];
  foundersPerSide: number;
}

const QUAL_CONF = 0.3;
const COHER_MIN_AGENTS = 10;
const COHER_SHARE = 0.5;
const COHER_SNAPS = 5;         // consecutive snapshots (snap spacing 250)
const SNAP_SPACING = 250;
const PROD_WINDOW = 1500;
const BORROW_RISE = 0.20;
const COHORT_TICKS = 1000;
const PERM_REPS = 200;
const CONTROLS_PER_EVENT = 3;

export interface CoherenceCell {
  pop: number; k: number;
  achieved: boolean; start: number;   // first tick of qualifying stretch
  finalAgreement: number; finalQualified: number; modal: number;
}

export interface M2Report {
  permutation: {                       // §5.4 — reported first
    alignmentObserved: number;
    permutedMean: number; permutedSd: number; z: number;
    successEvents: number;
    differentiated: boolean;
  };
  coherence: CoherenceCell[];          // §5.1, 2 pops × 3 classes
  drift: { pop: number; rate: number }[];
  coherenceBeatsDrift: boolean;
  success: {                           // §5.2
    rateSignal: number; rateBaseline: number; contingency: number;
    hearEvents: number; controls: number;
  };
  divergence: {                        // §5.3
    divergentClasses: { k: number; west: number; east: number }[];
    coherentBoth: number[];
    series: { tick: number; jsd: number[] }[];
  };
  fidelity: { pop: number; series: { cohort: number; value: number }[] }[];
  borrowing: {                         // §5.6
    k: number; adoptingPop: number; peakShare: number; preShare: number;
    latency: number;
    adopterTrust: number; nonAdopterTrust: number; adopters: number;
  }[];
  demography: { west: number; east: number; born: number; died: number;
                maxGen: number };
  verdict: 'full' | 'partial-signaling' | 'partial-coordination' | 'fail';
}

export function analyzeM2(run: M2RunData,
                          finalTrust: number[][]): M2Report {
  const side = sideMap(run);
  const snaps = run.lexSnaps;
  const K = M2.REFS;

  // ---- §5.4 first: permutation over kind alignment ------------------------
  const hearEvents = collectHearEvents(run);
  const successes = hearEvents.filter(h => h.foundKind >= 0);
  const prodRef = productionMapping(run, side);
  const alignOf = (tokAt: (i: number) => number) => {
    let hit = 0, n = 0;
    for (let i = 0; i < successes.length; i++) {
      const h = successes[i];
      const m = prodRef(h.tick, side.get(h.hearer) ?? 0, tokAt(i));
      if (m < 0) continue;
      n++;
      if (m === h.foundKind) hit++;
    }
    return n > 0 ? hit / n : NaN;
  };
  const alignmentObserved = alignOf(i => successes[i].tok);
  const rng = new RNG(49979687, 'm2perm');
  const permVals: number[] = [];
  // permute tokens across the same side's mode-1 emissions
  const bySide: number[][] = [[], []];
  successes.forEach((h, i) => bySide[side.get(h.hearer) ?? 0].push(i));
  const sideTokens = bySide.map(list => list.map(i => successes[i].tok));
  for (let rep = 0; rep < PERM_REPS; rep++) {
    const shuffled = sideTokens.map(l => rng.shuffle([...l]));
    const at = new Map<number, number>();
    bySide.forEach((list, s) => list.forEach((i, j) => at.set(i, shuffled[s][j])));
    const v = alignOf(i => at.get(i)!);
    if (Number.isFinite(v)) permVals.push(v);
  }
  const pMean = mean(permVals), pSd = sd(permVals, pMean);
  const z = pSd > 1e-9 ? (alignmentObserved - pMean) / pSd : NaN;
  const differentiated = Number.isFinite(z) && z >= 3;

  // ---- §5.1 coherence ------------------------------------------------------
  const coherence: CoherenceCell[] = [];
  for (let pop = 0; pop < 2; pop++) {
    for (let k = 0; k < K; k++) {
      let streak = 0, start = -1, achieved = false, achievedAt = -1;
      let lastAgreement = 0, lastQualified = 0, lastModal = -1;
      for (const snap of snaps) {
        const { agreement, qualified, modal } = agreementAt(snap, pop, k, side);
        lastAgreement = agreement; lastQualified = qualified; lastModal = modal;
        if (qualified >= COHER_MIN_AGENTS && agreement >= COHER_SHARE) {
          if (streak === 0) start = snap.tick;
          streak++;
          if (streak >= COHER_SNAPS && !achieved) { achieved = true; achievedAt = start; }
        } else streak = 0;
      }
      coherence.push({ pop, k, achieved, start: achieved ? achievedAt : -1,
        finalAgreement: r2(lastAgreement), finalQualified: lastQualified,
        modal: lastModal });
    }
  }

  // ---- drift null ----------------------------------------------------------
  const meanQualified = [0, 1].map(pop => {
    const vals = snaps.map(s => {
      let q = 0;
      for (let k = 0; k < K; k++) q += agreementAt(s, pop, k, side).qualified;
      return q / K;
    });
    return Math.max(4, Math.round(mean(vals)));
  });
  const meanLifespan = lifespan(run);
  const drift = [0, 1].map(pop => ({
    pop,
    rate: coherenceDrift(meanQualified[pop], meanLifespan, run.contactTick),
  }));
  // amendment a4: single-pool drift concentrates, but cannot hold two
  // classes simultaneously coherent on DIFFERENT tokens in one population
  let coherenceBeatsDrift = false;
  for (let pop = 0; pop < 2 && !coherenceBeatsDrift; pop++) {
    const streak = new Array(K).fill(0);
    const curModal = new Array(K).fill(-1);
    for (const snap of snaps) {
      const now: number[] = [];
      for (let k = 0; k < K; k++) {
        const { agreement, qualified, modal } = agreementAt(snap, pop, k, side);
        if (qualified >= COHER_MIN_AGENTS && agreement >= COHER_SHARE) {
          streak[k]++; curModal[k] = modal;
        } else streak[k] = 0;
        if (streak[k] >= COHER_SNAPS) now.push(curModal[k]);
      }
      if (now.length >= 2 && new Set(now).size >= 2) {
        coherenceBeatsDrift = true;
        break;
      }
    }
  }

  // ---- §5.2 communicative success -----------------------------------------
  const successRate = successes.length / Math.max(1, hearEvents.length);
  const { baseRate, controls } = baseline(run, hearEvents);
  const success = {
    rateSignal: r3(successRate), rateBaseline: r3(baseRate),
    contingency: baseRate > 1e-9 ? r2(successRate / baseRate) : NaN,
    hearEvents: hearEvents.length, controls,
  };

  // ---- §5.3 divergence -----------------------------------------------------
  const preContactSnap = lastSnapBefore(snaps, run.contactTick);
  const coherentBoth: number[] = [];
  const divergentClasses: { k: number; west: number; east: number }[] = [];
  for (let k = 0; k < K; k++) {
    const w = coherence.find(c => c.pop === 0 && c.k === k)!;
    const e = coherence.find(c => c.pop === 1 && c.k === k)!;
    // both achieved coherence before contact
    if (w.achieved && e.achieved && w.start < run.contactTick &&
        e.start < run.contactTick) {
      coherentBoth.push(k);
      const mw = agreementAt(preContactSnap, 0, k, side).modal;
      const me = agreementAt(preContactSnap, 1, k, side).modal;
      if (mw >= 0 && me >= 0 && mw !== me) {
        divergentClasses.push({ k, west: mw, east: me });
      }
    }
  }
  const series = snaps.filter((_, i) => i % 2 === 0).map(s => ({
    tick: s.tick,
    jsd: Array.from({ length: K }, (_, k) => r3(jsdAt(s, k, side))),
  }));

  // ---- §5.5 fidelity -------------------------------------------------------
  const fidelity = [0, 1].map(pop => ({
    pop, series: fidelitySeries(run, snaps, pop, side),
  }));

  // ---- §5.6 borrowing ------------------------------------------------------
  const borrowing: M2Report['borrowing'] = [];
  const trustToOther = otherSideTrust(finalTrust, side);
  for (const dv of divergentClasses) {
    for (const pop of [0, 1]) {
      const foreign = pop === 0 ? dv.east : dv.west;
      const pre = shareOfToken(preContactSnap, pop, dv.k, foreign, side);
      if (!Number.isFinite(pre)) continue;
      let peak = pre, latency = -1, hold = 0, borrowed = false;
      for (const s of snaps) {
        if (s.tick < run.contactTick) continue;
        const sh = shareOfToken(s, pop, dv.k, foreign, side);
        if (!Number.isFinite(sh)) continue;   // a2: no-information snapshot
        peak = Math.max(peak, sh);
        if (sh >= pre + BORROW_RISE) {
          hold++;
          if (hold >= 2 && latency < 0) { latency = s.tick - run.contactTick; borrowed = true; }
        } else hold = 0;
      }
      if (!borrowed) continue;
      // adopters: this pop's agents whose final top token for k is foreign
      const last = snaps[snaps.length - 1];
      const adopters: number[] = [], others: number[] = [];
      for (const row of last.rows) {
        if ((side.get(row[0]) ?? -1) !== pop) continue;
        if (row[2 * dv.k + 2] < QUAL_CONF) continue;
        (row[2 * dv.k + 1] === foreign ? adopters : others).push(row[0]);
      }
      const tr = (ids: number[]) =>
        r2(mean(ids.map(id => trustToOther.get(id) ?? 0)));
      borrowing.push({
        k: dv.k, adoptingPop: pop, peakShare: r2(peak), preShare: r2(pre),
        latency, adopterTrust: tr(adopters), nonAdopterTrust: tr(others),
        adopters: adopters.length,
      });
    }
  }

  // ---- demography + verdict ------------------------------------------------
  const lastFrame = run.frames[run.frames.length - 1];
  const west = lastFrame.agents.filter(r => (side.get(r[0]) ?? 0) === 0).length;
  const demography = {
    west, east: lastFrame.agents.length - west,
    born: run.births.length,
    died: run.events.filter(e => e.type === 'death').length,
    maxGen: Math.max(0, ...run.births.map(b => b[2])),
  };

  // fidelity stable = last three defined cohorts within each pop average ≥0.5
  const fidelityStable = fidelity.every(f => {
    const tail = f.series.filter(p => Number.isFinite(p.value)).slice(-3);
    return tail.length >= 3 && mean(tail.map(p => p.value)) >= 0.5;
  });
  let verdict: M2Report['verdict'];
  if (!coherenceBeatsDrift) verdict = 'fail';
  else if (!differentiated) verdict = 'partial-coordination';
  else if (fidelityStable && divergentClasses.length > 0 && borrowing.length > 0) {
    verdict = 'full';
  } else verdict = 'partial-signaling';

  return {
    permutation: {
      alignmentObserved: r3(alignmentObserved), permutedMean: r3(pMean),
      permutedSd: r3(pSd), z: r2(z), successEvents: successes.length,
      differentiated,
    },
    coherence, drift: drift.map(d => ({ pop: d.pop, rate: r3(d.rate) })),
    coherenceBeatsDrift, success,
    divergence: { divergentClasses, coherentBoth, series },
    fidelity, borrowing, demography, verdict,
  };
}

// ---------------------------------------------------------------------------

interface HearEvent {
  tick: number; hearer: number; emitter: number; tok: number;
  x: number; y: number; dist: number;
  foundKind: number;           // -1 if no success
}

function sideMap(run: M2RunData): Map<number, number> {
  const side = new Map<number, number>();
  for (let i = 0; i < 2 * run.foundersPerSide; i++) {
    side.set(i, i < run.foundersPerSide ? 0 : 1);
  }
  const mid = (M2.BARRIER_X0 + M2.BARRIER_X1) / 2;
  for (const [, child, , , , x] of run.births) {
    side.set(child, x < mid ? 0 : 1);
  }
  return side;
}

function collectHearEvents(run: M2RunData): HearEvent[] {
  // gathers indexed per agent for the success lookup
  const gByAgent = new Map<number, number[][]>();
  for (const g of run.gathers) {
    let l = gByAgent.get(g[1]);
    if (!l) gByAgent.set(g[1], l = []);
    l.push(g);
  }
  const frameOf = (t: number) =>
    run.frames[Math.min(run.frames.length - 1, t)];
  const out: HearEvent[] = [];
  for (const em of run.emissions) {
    if (em.mode !== 1 || em.tok < 0) continue;
    for (const [hearer, couldSee] of em.hearers) {
      if (couldSee) continue;                     // §2.1 asymmetry, per event
      if (hearer === em.a) continue;
      const row = frameOf(em.t).agents.find(r => r[0] === hearer);
      if (!row) continue;
      const dist = Math.max(Math.abs(row[1] - em.x), Math.abs(row[2] - em.y));
      let foundKind = -1;
      for (const g of gByAgent.get(hearer) ?? []) {
        if (g[0] <= em.t || g[0] > em.t + M2.HEED_WINDOW) continue;
        if (Math.max(Math.abs(g[2] - em.x), Math.abs(g[3] - em.y)) > M2.HEED_RADIUS) continue;
        foundKind = g[4];
        break;
      }
      out.push({ tick: em.t, hearer, emitter: em.a, tok: em.tok,
                 x: em.x, y: em.y, dist, foundKind });
    }
  }
  return out;
}

/**
 * Side production mapping: class most often produced with T over the
 * trailing window (bucketed to 250-tick granularity for tractability —
 * same definition, coarser edges). Precomputed prefix sums; O(1) lookups,
 * which the 200-rep permutation needs.
 */
function productionMapping(run: M2RunData, side: Map<number, number>) {
  const B = 250;
  const nB = Math.ceil(run.ticks / B) + 1;
  // prefix[pop][tok][bucket+1][ref] = counts in buckets 0..bucket
  const prefix = Array.from({ length: 2 }, () =>
    Array.from({ length: 8 }, () =>
      Array.from({ length: nB + 1 }, () => new Int32Array(M2.REFS))));
  for (const e of run.emissions) {
    if (e.mode !== 1 || e.tok < 0 || e.ref < 0) continue;
    const s = side.get(e.a) ?? -1;
    if (s < 0) continue;
    prefix[s][e.tok][Math.floor(e.t / B) + 1][e.ref]++;
  }
  for (let s = 0; s < 2; s++) {
    for (let tk = 0; tk < 8; tk++) {
      for (let b = 1; b <= nB; b++) {
        for (let k = 0; k < M2.REFS; k++) {
          prefix[s][tk][b][k] += prefix[s][tk][b - 1][k];
        }
      }
    }
  }
  return (tick: number, pop: number, tok: number): number => {
    const hi = Math.min(nB, Math.floor(tick / B) + 1);
    const lo = Math.max(0, Math.floor((tick - PROD_WINDOW) / B));
    const p = prefix[pop][tok];
    let tot = 0, best = 0, bestC = -1;
    for (let k = 0; k < M2.REFS; k++) {
      const c = p[hi][k] - p[lo][k];
      tot += c;
      if (c > bestC) { bestC = c; best = k; }
    }
    return tot < 3 ? -1 : best;
  };
}

function baseline(run: M2RunData, hearEvents: HearEvent[]) {
  // audibility index: for control ticks we need "no mode-1 emission audible
  // in the trailing window" — bucket emissions by tick for a fast check
  const emByTick = new Map<number, EmissionLog[]>();
  for (const e of run.emissions) {
    if (e.mode !== 1) continue;
    let l = emByTick.get(e.t);
    if (!l) emByTick.set(e.t, l = []);
    l.push(e);
  }
  const audible = (id: number, x: number, y: number, t: number): boolean => {
    // amendment a3: cover the scored forward window too, not just trailing
    for (let dt = -M2.HEED_WINDOW; dt <= M2.HEED_WINDOW; dt++) {
      for (const e of emByTick.get(t - dt) ?? []) {
        if (Math.max(Math.abs(e.x - x), Math.abs(e.y - y)) <= M2.SIGNAL_RADIUS) {
          return true;
        }
      }
    }
    return false;
  };
  const gByAgent = new Map<number, number[][]>();
  for (const g of run.gathers) {
    let l = gByAgent.get(g[1]);
    if (!l) gByAgent.set(g[1], l = []);
    l.push(g);
  }
  const rng = new RNG(86028157, 'm2base');
  let hits = 0, n = 0;
  for (const h of hearEvents) {
    let tried = 0, found = 0;
    while (tried < 24 && found < CONTROLS_PER_EVENT) {
      tried++;
      const t = 100 + rng.int(run.ticks - 200);
      const row = run.frames[Math.min(run.frames.length - 1, t)]
        .agents.find(r => r[0] === h.hearer);
      if (!row) continue;
      const d = Math.max(Math.abs(row[1] - h.x), Math.abs(row[2] - h.y));
      if (Math.abs(d - h.dist) > 2) continue;
      if (audible(h.hearer, row[1], row[2], t)) continue;
      found++; n++;
      for (const g of gByAgent.get(h.hearer) ?? []) {
        if (g[0] <= t || g[0] > t + M2.HEED_WINDOW) continue;
        if (Math.max(Math.abs(g[2] - h.x), Math.abs(g[3] - h.y)) > M2.HEED_RADIUS) continue;
        hits++;
        break;
      }
    }
  }
  return { baseRate: n > 0 ? hits / n : NaN, controls: n };
}

function agreementAt(snap: LexSnap, pop: number, k: number,
                     side: Map<number, number>) {
  const counts = new Map<number, number>();
  let qualified = 0;
  for (const row of snap.rows) {
    if ((side.get(row[0]) ?? -1) !== pop) continue;
    const top = row[2 * k + 1], conf = row[2 * k + 2];
    if (top < 0 || conf < QUAL_CONF) continue;
    qualified++;
    counts.set(top, (counts.get(top) ?? 0) + 1);
  }
  let modal = -1, best = 0;
  for (const [tok, c] of counts) if (c > best) { best = c; modal = tok; }
  return { agreement: qualified ? best / qualified : 0, qualified, modal };
}

function shareOfToken(snap: LexSnap, pop: number, k: number, tok: number,
                      side: Map<number, number>): number {
  let qualified = 0, hits = 0;
  for (const row of snap.rows) {
    if ((side.get(row[0]) ?? -1) !== pop) continue;
    if (row[2 * k + 1] < 0 || row[2 * k + 2] < QUAL_CONF) continue;
    qualified++;
    if (row[2 * k + 1] === tok) hits++;
  }
  // amendment a2: below the §5.1 floor the share carries no information
  return qualified >= COHER_MIN_AGENTS ? hits / qualified : NaN;
}

function jsdAt(snap: LexSnap, k: number, side: Map<number, number>): number {
  const dist = (pop: number) => {
    const d = new Array(8).fill(0);
    let n = 0;
    for (const row of snap.rows) {
      if ((side.get(row[0]) ?? -1) !== pop) continue;
      if (row[2 * k + 1] < 0 || row[2 * k + 2] < QUAL_CONF) continue;
      d[row[2 * k + 1]]++; n++;
    }
    return n ? d.map(v => v / n) : null;
  };
  const p = dist(0), q = dist(1);
  if (!p || !q) return NaN;
  const m = p.map((v, i) => (v + q[i]) / 2);
  const kl = (a: number[], b: number[]) =>
    a.reduce((s, v, i) => (v > 0 && b[i] > 0 ? s + v * Math.log2(v / b[i]) : s), 0);
  return (kl(p, m) + kl(q, m)) / 2;
}

function fidelitySeries(run: M2RunData, snaps: LexSnap[], pop: number,
                        side: Map<number, number>) {
  const bornTick = new Map<number, number>(run.births.map(b => [b[1], b[0]]));
  const cohortOf = (id: number) => {
    const bt = bornTick.get(id);
    return bt === undefined ? 0 : 1 + Math.floor(bt / COHORT_TICKS);
  };
  const nCohorts = 1 + Math.ceil(run.ticks / COHORT_TICKS);
  // cohort mapping per class, measured when the cohort is mature
  const mapping: (number | null)[][] = [];
  for (let g = 0; g < nCohorts; g++) {
    // amendment a1: end + 250, so members can still be alive at measurement
    const measureTick = Math.min(run.ticks - 1, g * COHORT_TICKS + 250);
    const snap = lastSnapBefore(snaps, measureTick + 1);
    const perClass: (number | null)[] = [];
    for (let k = 0; k < M2.REFS; k++) {
      const counts = new Map<number, number>();
      let q = 0;
      for (const row of snap.rows) {
        if ((side.get(row[0]) ?? -1) !== pop || cohortOf(row[0]) !== g) continue;
        if (row[2 * k + 1] < 0 || row[2 * k + 2] < QUAL_CONF) continue;
        q++;
        counts.set(row[2 * k + 1], (counts.get(row[2 * k + 1]) ?? 0) + 1);
      }
      let modal = -1, best = 0;
      for (const [tok, c] of counts) if (c > best) { best = c; modal = tok; }
      perClass.push(q >= 5 && best / q >= COHER_SHARE ? modal : null);
    }
    mapping.push(perClass);
  }
  const series: { cohort: number; value: number }[] = [];
  for (let g = 1; g < nCohorts; g++) {
    let denom = 0, kept = 0;
    for (let k = 0; k < M2.REFS; k++) {
      if (mapping[g - 1][k] === null) continue;
      denom++;
      if (mapping[g][k] === mapping[g - 1][k]) kept++;
    }
    series.push({ cohort: g, value: denom ? r2(kept / denom) : NaN });
  }
  return series;
}

/** neutral copying null for §5.1: P(one token ≥50% sustained 1000t) */
function coherenceDrift(N: number, L: number, horizon: number): number {
  const rng = new RNG(67867967, `m2drift:${N}`);
  const reps = 300;
  let hits = 0;
  for (let r = 0; r < reps; r++) {
    const slots = new Int32Array(N);
    for (let i = 0; i < N; i++) slots[i] = rng.int(8);
    const counts = new Array(8).fill(0);
    for (const s of slots) counts[s]++;
    let streak = 0, hit = false;
    const pRepl = 1 / Math.max(50, L);
    for (let t = 0; t < horizon && !hit; t++) {
      for (let i = 0; i < N; i++) {
        if (rng.next() < pRepl) {
          counts[slots[i]]--;
          slots[i] = slots[rng.int(N)];
          counts[slots[i]]++;
        }
      }
      streak = Math.max(...counts) >= COHER_SHARE * N ? streak + 1 : 0;
      if (streak >= COHER_SNAPS * SNAP_SPACING) hit = true;
    }
    if (hit) hits++;
  }
  return hits / reps;
}

function otherSideTrust(finalTrust: number[][],
                        side: Map<number, number>): Map<number, number> {
  const acc = new Map<number, { s: number; n: number }>();
  for (const [a, b, tr] of finalTrust) {
    if ((side.get(a) ?? -1) === (side.get(b) ?? -1)) continue;
    let e = acc.get(a);
    if (!e) acc.set(a, e = { s: 0, n: 0 });
    e.s += tr; e.n++;
  }
  return new Map([...acc].map(([id, e]) => [id, e.s / e.n]));
}

function lifespan(run: M2RunData): number {
  const bornTick = new Map<number, number>(run.births.map(b => [b[1], b[0]]));
  const ls: number[] = [];
  for (const e of run.events) {
    if (e.type === 'death') ls.push(e.tick - (bornTick.get(e.a) ?? 0));
  }
  return ls.length ? mean(ls) : 400;
}

function lastSnapBefore(snaps: LexSnap[], tick: number): LexSnap {
  let out = snaps[0];
  for (const s of snaps) if (s.tick < tick) out = s;
  return out;
}

function mean(xs: number[]): number {
  return xs.length ? xs.reduce((s, v) => s + v, 0) / xs.length : NaN;
}
function sd(xs: number[], m: number): number {
  return xs.length > 1
    ? Math.sqrt(xs.reduce((s, v) => s + (v - m) ** 2, 0) / (xs.length - 1)) : NaN;
}
function r2(v: number): number { return Math.round(v * 100) / 100; }
function r3(v: number): number { return Math.round(v * 1000) / 1000; }
