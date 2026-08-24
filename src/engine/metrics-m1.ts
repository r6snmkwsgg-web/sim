import { M1, P } from '../core/params.js';
import { RNG } from '../core/rng.js';
import type { Frame, SimEvent } from './engine.js';

/**
 * PREREGISTERED MEASUREMENT — SPEC-M1 §5.
 *
 * This file was written, in full, before the first M1 simulation output was
 * examined (only compile checks were run). The definitions and thresholds
 * below are fixed; changing them after looking at results voids the
 * milestone. Tuning knobs live in params.ts and are explicitly §8 territory;
 * nothing in this file is.
 *
 * Definitions (§5.1):
 *  - generation: lineage depth from the founder cohort (founders = 0).
 *  - holder (token dimension): an agent with ≥2 emissions in the trailing
 *    700 ticks; its option is the modal token of those emissions
 *    (tie-break: higher count, then lower token id).
 *  - holder (gather-site dimension): an agent with ≥5 pith gathers in the
 *    trailing 400 ticks; its option is the modal site (nearest site centre).
 *  - practice: an option held by ≥60% of holders, with holders ≥25% of the
 *    living population, for ≥500 consecutive ticks (sampled every 25).
 *  - origin: the first agent to produce a run of consecutive same-option
 *    acts (3 emissions / 5 pith gathers) at a moment when the option's share
 *    of all such acts in the trailing window is <45%.
 *  - survival (strict, §5.1): at some tick the practice is active, the
 *    origin agent is dead, and every living agent's generation is ≥ origin's
 *    generation + 3. A median-generation variant is reported as secondary.
 *  - transmission contingency (§5.3): among agents born in the run, the rate
 *    of adopting option X when exposed to X before their own first choice,
 *    versus when not exposed. Exposure is counted per perceivable act-tick
 *    (an emission within signal radius / a gather within vision of where the
 *    agent stood at that tick) — opportunity-normalized per amendment A1.
 *  - permutation control (§5.5): option labels are shuffled across the run's
 *    acts (who/when/where held constant); contingency recomputed 200×.
 *  - drift null (§5.2): a neutral copying model — N slots, K options, each
 *    slot replaced with probability 1/L per tick by copying a uniformly
 *    random living slot — run 500× and scored with the same practice
 *    threshold. The result must beat this, not zero.
 */

export interface M1RunData {
  ticks: number;
  frames: Frame[];
  gathers: number[][];        // [tick, agent, x, y, kind]
  births: number[][];         // [tick, child, gen, parentA, parentB]
  events: SimEvent[];         // signals carry o = token; deaths
  founders: number;
  siteCenters: [number, number][];
}

export interface PracticeSpan {
  option: number;
  start: number;              // first tick of the qualifying span
  end: number;                // last tick observed at threshold
  originAgent: number;
  originTick: number;
  originGen: number;
  originDeadBy: number;       // tick of origin's death, -1 alive at run end
  survivedStrict: boolean;    // all living ≥ origin.gen+3 while active
  survivedMedian: boolean;    // median living gen ≥ origin.gen+3 while active
}

export interface DimensionReport {
  dimension: 'token' | 'site';
  options: number;
  practices: PracticeSpan[];
  anySurvivedStrict: boolean;
  anySurvivedMedian: boolean;
  contingency: number;        // adopt-rate ratio exposed vs unexposed
  adoptExposed: [number, number];    // [adoptions, cells]
  adoptUnexposed: [number, number];
  permutationMean: number;    // mean contingency under label permutation
  permutationZ: number;
  holdersFinal: number;
  shareSeries: { tick: number; share: number[] }[];  // option shares over time
}

export interface M1Report {
  token: DimensionReport;
  site: DimensionReport;
  demography: {
    aliveFinal: number; born: number; died: number;
    meanLifespan: number; maxGen: number; minLivingGen: number;
    medianLivingGen: number;
  };
  drift: { token: number; site: number; reps: number };
}

const SAMPLE = 25;
const PRACTICE_SHARE = 0.6;
const PRACTICE_TICKS = 500;
const HOLDER_MIN = 0.25;
const TOKEN_WINDOW = 700;
const TOKEN_MIN_EMITS = 2;
const SITE_WINDOW = 400;
const SITE_MIN_GATHERS = 5;
const ORIGIN_RUN_TOKEN = 3;
const ORIGIN_RUN_SITE = 5;
const ORIGIN_MAX_SHARE = 0.45;

interface Act { tick: number; agent: number; option: number; x: number; y: number }

export interface M1AnalyzeOpts {
  permutation?: boolean;      // §5.5 control (main runs; expensive)
  drift?: boolean;            // §5.2 null (main runs; expensive)
}

export function analyzeM1(run: M1RunData, opts: M1AnalyzeOpts = {}): M1Report {
  const gen = new Map<number, number>();
  for (let i = 0; i < run.founders; i++) gen.set(i, 0);
  for (const [, child, g] of run.births) gen.set(child, g);
  const deadAt = new Map<number, number>();
  for (const e of run.events) {
    if (e.type === 'death') deadAt.set(e.a, e.tick);
  }

  const emissions: Act[] = run.events
    .filter(e => e.type === 'signal' && e.o !== undefined && e.o >= 0)
    .map(e => {
      const row = frameRow(run.frames, e.tick, e.a);
      return { tick: e.tick, agent: e.a, option: e.o!, x: row?.[1] ?? -99,
               y: row?.[2] ?? -99 };
    });
  const siteOf = (x: number, y: number) => {
    let best = 0, bd = Infinity;
    run.siteCenters.forEach(([sx, sy], i) => {
      const d = (sx - x) ** 2 + (sy - y) ** 2;
      if (d < bd) { bd = d; best = i; }
    });
    return best;
  };
  const pithGathers: Act[] = run.gathers
    .filter(g => g[4] === 1)
    .map(g => ({ tick: g[0], agent: g[1], option: siteOf(g[2], g[3]),
                 x: g[2], y: g[3] }));

  const doPerm = opts.permutation !== false;
  const token = dimensionReport('token', M1.TOKENS, emissions, run, gen,
    deadAt, TOKEN_WINDOW, TOKEN_MIN_EMITS, ORIGIN_RUN_TOKEN, P.SIGNAL_RADIUS,
    doPerm);
  const site = dimensionReport('site', run.siteCenters.length, pithGathers,
    run, gen, deadAt, SITE_WINDOW, SITE_MIN_GATHERS, ORIGIN_RUN_SITE, P.VISION,
    doPerm);

  // demography
  const lifespans: number[] = [];
  const bornTickOf = new Map<number, number>(run.births.map(b => [b[1], b[0]]));
  for (const [id, d] of deadAt) lifespans.push(d - (bornTickOf.get(id) ?? 0));
  const lastFrame = run.frames[run.frames.length - 1];
  const livingGens = lastFrame.agents.map(r => gen.get(r[0]) ?? 0)
    .sort((a, b) => a - b);
  const demography = {
    aliveFinal: lastFrame.agents.length,
    born: run.births.length,
    died: deadAt.size,
    meanLifespan: lifespans.length
      ? Math.round(lifespans.reduce((s, v) => s + v, 0) / lifespans.length) : NaN,
    maxGen: Math.max(0, ...[...gen.values()]),
    minLivingGen: livingGens[0] ?? 0,
    medianLivingGen: livingGens[Math.floor(livingGens.length / 2)] ?? 0,
  };

  const meanAlive = Math.round(run.frames.reduce(
    (s, f) => s + f.agents.length, 0) / run.frames.length);
  const L = Number.isFinite(demography.meanLifespan)
    ? Math.max(50, demography.meanLifespan) : 400;
  const drift = opts.drift !== false ? {
    token: driftNull(M1.TOKENS, meanAlive, L, run.ticks, 500),
    site: driftNull(run.siteCenters.length, meanAlive, L, run.ticks, 500),
    reps: 500,
  } : { token: NaN, site: NaN, reps: 0 };

  return { token, site, demography, drift };
}

// ---------------------------------------------------------------------------

function frameRow(frames: Frame[], tick: number, agent: number) {
  const f = frames[Math.min(tick, frames.length - 1)];
  return f?.agents.find(r => r[0] === agent);
}

function dimensionReport(dimension: 'token' | 'site', K: number, acts: Act[],
                         run: M1RunData, gen: Map<number, number>,
                         deadAt: Map<number, number>, windowT: number,
                         minActs: number, originRun: number,
                         percRadius: number, doPerm = true): DimensionReport {
  // per-agent chronological act lists
  const byAgent = new Map<number, Act[]>();
  for (const a of acts) {
    let l = byAgent.get(a.agent);
    if (!l) byAgent.set(a.agent, l = []);
    l.push(a);
  }

  // ---- practice spans -----------------------------------------------------
  const shareSeries: { tick: number; share: number[] }[] = [];
  const atThreshold: number[][] = [];         // per sample: options at threshold
  for (let t = 0; t < run.ticks; t += SAMPLE) {
    const f = run.frames[Math.min(t, run.frames.length - 1)];
    const living = new Set(f.agents.map(r => r[0]));
    const counts = new Array(K).fill(0);
    let holders = 0;
    for (const id of living) {
      const l = byAgent.get(id);
      if (!l) continue;
      const recent = l.filter(a => a.tick > t - windowT && a.tick <= t);
      if (recent.length < minActs) continue;
      holders++;
      counts[modal(recent.map(a => a.option), K)]++;
    }
    const share = counts.map(c => holders ? c / holders : 0);
    shareSeries.push({ tick: t, share: share.map(v => Math.round(v * 1000) / 1000) });
    const qualified = holders >= HOLDER_MIN * living.size && holders > 0;
    atThreshold.push(share
      .map((s, o) => (qualified && s >= PRACTICE_SHARE ? o : -1))
      .filter(o => o >= 0));
  }

  // consecutive spans per option
  const spans: { option: number; start: number; end: number }[] = [];
  for (let o = 0; o < K; o++) {
    let start = -1;
    for (let i = 0; i <= atThreshold.length; i++) {
      const hit = i < atThreshold.length && atThreshold[i].includes(o);
      if (hit && start < 0) start = i * SAMPLE;
      if (!hit && start >= 0) {
        const end = (i - 1) * SAMPLE;
        if (end - start >= PRACTICE_TICKS) spans.push({ option: o, start, end });
        start = -1;
      }
    }
  }

  // ---- origins ------------------------------------------------------------
  const origin = new Map<number, { agent: number; tick: number }>();
  const sortedActs = [...acts].sort((p, q) => p.tick - q.tick);
  const runsByAgent = new Map<number, { option: number; n: number }>();
  for (let i = 0; i < sortedActs.length; i++) {
    const a = sortedActs[i];
    const r = runsByAgent.get(a.agent);
    const n = r && r.option === a.option ? r.n + 1 : 1;
    runsByAgent.set(a.agent, { option: a.option, n });
    if (n >= originRun && !origin.has(a.option)) {
      // population share of this option in the trailing window
      let tot = 0, same = 0;
      for (let j = i; j >= 0 && sortedActs[j].tick > a.tick - windowT; j--) {
        tot++;
        if (sortedActs[j].option === a.option) same++;
      }
      if (tot === 0 || same / tot < ORIGIN_MAX_SHARE) {
        origin.set(a.option, { agent: a.agent, tick: a.tick });
      }
    }
  }

  // ---- survival -----------------------------------------------------------
  const practices: PracticeSpan[] = spans.map(sp => {
    const or = origin.get(sp.option);
    const originAgent = or?.agent ?? -1;
    const originGen = or ? gen.get(or.agent) ?? 0 : -1;
    const originDeadBy = or ? deadAt.get(or.agent) ?? -1 : -1;
    let survivedStrict = false, survivedMedian = false;
    if (or && originDeadBy >= 0) {
      for (let t = Math.max(sp.start, originDeadBy); t <= sp.end; t += SAMPLE) {
        const f = run.frames[Math.min(t, run.frames.length - 1)];
        const gens = f.agents.map(r => gen.get(r[0]) ?? 0).sort((a, b) => a - b);
        if (gens.length === 0) break;
        if (gens[0] >= originGen + 3) survivedStrict = true;
        if (gens[Math.floor(gens.length / 2)] >= originGen + 3) survivedMedian = true;
        if (survivedStrict) break;
      }
    }
    return { option: sp.option, start: sp.start, end: sp.end, originAgent,
             originTick: or?.tick ?? -1, originGen, originDeadBy,
             survivedStrict, survivedMedian };
  });

  // ---- transmission contingency (§5.3) ------------------------------------
  const bornIds = new Set(run.births.map(b => b[1]));
  const adoption = new Map<number, { tick: number; option: number }>();
  for (const [id, l] of byAgent) {
    if (!bornIds.has(id) || l.length < minActs) continue;
    const firstActs = l.slice(0, minActs);
    adoption.set(id, { tick: firstActs[firstActs.length - 1].tick,
                       option: modal(firstActs.map(a => a.option), K) });
  }
  // exposure: perceivable acts by *others* before the agent's adoption tick
  const exposure = new Map<number, Float64Array>();
  for (const id of adoption.keys()) exposure.set(id, new Float64Array(K));
  for (const a of acts) {
    const f = run.frames[Math.min(a.tick, run.frames.length - 1)];
    for (const row of f.agents) {
      const id = row[0];
      if (id === a.agent) continue;
      const ad = adoption.get(id);
      if (!ad || a.tick >= ad.tick) continue;
      if (Math.max(Math.abs(row[1] - a.x), Math.abs(row[2] - a.y)) > percRadius) continue;
      exposure.get(id)![a.option]++;
    }
  }
  const contingencyOf = (adopt: Map<number, { option: number }>,
                         exp: Map<number, Float64Array>) => {
    let aE = 0, nE = 0, aU = 0, nU = 0;
    for (const [id, ad] of adopt) {
      const ex = exp.get(id)!;
      for (let o = 0; o < K; o++) {
        if (ex[o] > 0) { nE++; if (ad.option === o) aE++; }
        else { nU++; if (ad.option === o) aU++; }
      }
    }
    const rE = nE ? aE / nE : NaN, rU = nU ? aU / nU : NaN;
    return { ratio: rU > 0 ? rE / rU : NaN, aE, nE, aU, nU };
  };
  const obs = contingencyOf(adoption, exposure);

  // ---- permutation control (§5.5) -----------------------------------------
  const rng = new RNG(15485863, `perm:${dimension}`);
  const labels = acts.map(a => a.option);
  const permRatios: number[] = [];
  for (let rep = 0; rep < (doPerm ? 200 : 0); rep++) {
    const shuffled = rng.shuffle([...labels]);
    const permExp = new Map<number, Float64Array>();
    for (const id of adoption.keys()) permExp.set(id, new Float64Array(K));
    for (let i = 0; i < acts.length; i++) {
      const a = acts[i], o = shuffled[i];
      const f = run.frames[Math.min(a.tick, run.frames.length - 1)];
      for (const row of f.agents) {
        const id = row[0];
        if (id === a.agent) continue;
        const ad = adoption.get(id);
        if (!ad || a.tick >= ad.tick) continue;
        if (Math.max(Math.abs(row[1] - a.x), Math.abs(row[2] - a.y)) > percRadius) continue;
        permExp.get(id)![o]++;
      }
    }
    const r = contingencyOf(adoption, permExp).ratio;
    if (Number.isFinite(r)) permRatios.push(r);
  }
  const pMean = permRatios.length
    ? permRatios.reduce((s, v) => s + v, 0) / permRatios.length : NaN;
  const pSd = permRatios.length > 1
    ? Math.sqrt(permRatios.reduce((s, v) => s + (v - pMean) ** 2, 0) /
                (permRatios.length - 1)) : NaN;

  const lastSample = shareSeries[shareSeries.length - 1];
  return {
    dimension, options: K, practices,
    anySurvivedStrict: practices.some(p => p.survivedStrict),
    anySurvivedMedian: practices.some(p => p.survivedMedian),
    contingency: Math.round(obs.ratio * 100) / 100,
    adoptExposed: [obs.aE, obs.nE],
    adoptUnexposed: [obs.aU, obs.nU],
    permutationMean: Math.round(pMean * 100) / 100,
    permutationZ: pSd > 1e-9
      ? Math.round(((obs.ratio - pMean) / pSd) * 100) / 100 : NaN,
    holdersFinal: [...byAgent.keys()].filter(id =>
      run.frames[run.frames.length - 1].agents.some(r => r[0] === id)).length,
    shareSeries: shareSeries.filter((_, i) => i % 4 === 0),
  };
}

function modal(options: number[], K: number): number {
  const counts = new Array(K).fill(0);
  for (const o of options) counts[o]++;
  let best = 0;
  for (let o = 1; o < K; o++) if (counts[o] > counts[best]) best = o;
  return best;
}

/** §5.2 drift null: neutral copying, no bias — the bar to beat */
export function driftNull(K: number, N: number, L: number, ticks: number,
                          reps: number): number {
  const rng = new RNG(32452843, `drift:${K}:${N}`);
  let hits = 0;
  for (let r = 0; r < reps; r++) {
    const slots = new Int32Array(N);
    for (let i = 0; i < N; i++) slots[i] = rng.int(K);
    const counts = new Array(K).fill(0);
    for (const s of slots) counts[s]++;
    let run = 0, hit = false;
    const pRepl = 1 / L;
    for (let t = 0; t < ticks && !hit; t++) {
      for (let i = 0; i < N; i++) {
        if (rng.next() < pRepl) {
          counts[slots[i]]--;
          slots[i] = slots[rng.int(N)];
          counts[slots[i]]++;
        }
      }
      const top = Math.max(...counts);
      run = top >= PRACTICE_SHARE * N ? run + 1 : 0;
      if (run >= PRACTICE_TICKS) hit = true;
    }
    if (hit) hits++;
  }
  return Math.round((hits / reps) * 1000) / 1000;
}
