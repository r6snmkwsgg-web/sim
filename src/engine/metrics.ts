import type { Frame, SimEvent } from './engine.js';

/**
 * Instrumentation (§4.3), Milestone-0 subset — the numbers that decide
 * whether the target phenomenon (§5: reciprocal exchange without a trade
 * mechanic) actually happened.
 *
 * Everything here is computed from the recording (frames + events) alone,
 * never from simulation internals, so the same code can score a live run,
 * a replayed run, or a recording loaded from disk.
 *
 * The core measurement is opportunity-normalized giving:
 *   an "opportunity" is a tick where A stands adjacent to B while carrying
 *   enough to give. Each opportunity is classified by what A *knows* about B:
 *     prior-giver — B has given to A, more recently than any known harm
 *     hostile     — B has taken from / attacked A (knowingly), more recently
 *     neutral     — no history either way
 *   The reciprocity contingency is rate(prior-giver) / rate(neutral).
 *   The withholding ratio is rate(hostile) / rate(neutral).
 *
 * If giving were driven only by the utility function's empathy × need term,
 * these ratios sit near 1 — which is exactly what the ablated control shows.
 */

export interface ReciprocityReport {
  opportunities: Record<Class, number>;
  gives: Record<Class, number>;
  rates: Record<Class, number>;
  contingency: number;        // rate(prior-giver) / rate(neutral)
  withholding: number;        // rate(hostile) / rate(neutral)
  reciprocalDyads: number;    // pairs with ≥2 gifts in each direction
  /**
   * Pearson correlation between the opportunity-normalized give *rates*
   * A→B and B→A across pairs. Normalizing by opportunity cancels the
   * co-location confound (pairs that spend time together both give more);
   * what remains positive only if giving is *directed back* at givers.
   */
  rateCorrelation: number;
  totalGives: number;
  totalDefections: number;    // takes + attacks + loots
  coopRatio: number;
  giniFinal: number;
  aliveFinal: number;
  giftMatrix: number[][];     // value given A→B (energy units, rounded)
  series: { tick: number; gives: number; defections: number; gini: number }[];
}

type Class = 'priorGiver' | 'hostile' | 'neutral';

const GIVE_ABLE = 10;         // carried energy value at which giving is possible

export function analyze(frames: Frame[], events: SimEvent[],
                         nAgents: number): ReciprocityReport {
  // per ordered pair, what A knows about B: gifts received, harms suffered
  const giftsFrom = new Map<number, number>();
  const harmsFrom = new Map<number, number>();
  const key = (a: number, b: number) => a * 1000 + b;

  // index events by tick for the sweep
  const evByTick = new Map<number, SimEvent[]>();
  for (const e of events) {
    let l = evByTick.get(e.tick);
    if (!l) evByTick.set(e.tick, l = []);
    l.push(e);
  }

  const opportunities: Record<Class, number> = { priorGiver: 0, hostile: 0, neutral: 0 };
  const gives: Record<Class, number> = { priorGiver: 0, hostile: 0, neutral: 0 };
  const pairOpp = new Map<number, number>();     // ordered-pair opportunities
  const pairGive = new Map<number, number>();    // ordered-pair gives
  const giftMatrix: number[][] =
    Array.from({ length: nAgents }, () => new Array(nAgents).fill(0));
  const giftCount: number[][] =
    Array.from({ length: nAgents }, () => new Array(nAgents).fill(0));

  const classify = (a: number, b: number): Class => {
    // A's net standing with B: gifts count for, known harms count against
    // (weighted — one theft outweighs one gift, mirroring trust asymmetry)
    const g = giftsFrom.get(key(a, b)) ?? 0;
    const h = harmsFrom.get(key(a, b)) ?? 0;
    const net = g - 1.5 * h;
    if (g >= 1 && net > 0) return 'priorGiver';
    if (h >= 1) return 'hostile';
    return 'neutral';
  };

  let cumGives = 0, cumDef = 0;
  const series: ReciprocityReport['series'] = [];

  for (const f of frames) {
    // 1. count opportunities under the knowledge state *entering* this tick
    const givesNow = new Set<number>();
    for (const e of evByTick.get(f.tick) ?? []) {
      if (e.type === 'give') givesNow.add(key(e.a, e.b));
    }
    for (const [idA, xA, yA, , loadA] of f.agents) {
      if (loadA < GIVE_ABLE) continue;
      for (const [idB, xB, yB] of f.agents) {
        if (idB === idA) continue;
        if (Math.max(Math.abs(xA - xB), Math.abs(yA - yB)) > 1) continue;
        const cls = classify(idA, idB);
        opportunities[cls]++;
        const pk = key(idA, idB);
        pairOpp.set(pk, (pairOpp.get(pk) ?? 0) + 1);
        if (givesNow.has(pk)) {
          gives[cls]++;
          pairGive.set(pk, (pairGive.get(pk) ?? 0) + 1);
        }
      }
    }
    // 2. then fold this tick's events into the knowledge state
    for (const e of evByTick.get(f.tick) ?? []) {
      if (e.type === 'give') {
        const k = key(e.b, e.a);                        // receiver remembers giver
        giftsFrom.set(k, (giftsFrom.get(k) ?? 0) + 1);
        giftMatrix[e.a][e.b] += e.amt;
        giftCount[e.a][e.b]++;
        cumGives++;
      } else if (e.type === 'take' || e.type === 'attack' ||
                 (e.type === 'loot' && e.w)) {
        const k = key(e.b, e.a);                        // victim remembers harm
        harmsFrom.set(k, (harmsFrom.get(k) ?? 0) + 1);
        cumDef++;
      } else if (e.type === 'loot') {
        cumDef++;                                       // unwitnessed: still a defection
      }
    }
    if (f.tick % 25 === 0) {
      series.push({ tick: f.tick, gives: cumGives, defections: cumDef,
                    gini: gini(f.agents.map(r => r[4])) });
    }
  }

  const rate = (c: Class) =>
    opportunities[c] > 0 ? gives[c] / opportunities[c] : 0;
  const rates: Record<Class, number> = {
    priorGiver: rate('priorGiver'), hostile: rate('hostile'), neutral: rate('neutral'),
  };
  const safe = (num: number, den: number) => (den > 1e-9 ? num / den : NaN);

  let reciprocalDyads = 0;
  for (let a = 0; a < nAgents; a++) {
    for (let b = a + 1; b < nAgents; b++) {
      if (giftCount[a][b] >= 2 && giftCount[b][a] >= 2) reciprocalDyads++;
    }
  }

  // pairwise rate correlation (see the field's doc comment)
  const xs: number[] = [], ys: number[] = [];
  const MIN_OPP = 25;
  for (let a = 0; a < nAgents; a++) {
    for (let b = a + 1; b < nAgents; b++) {
      const oAB = pairOpp.get(key(a, b)) ?? 0;
      const oBA = pairOpp.get(key(b, a)) ?? 0;
      if (oAB < MIN_OPP || oBA < MIN_OPP) continue;
      xs.push((pairGive.get(key(a, b)) ?? 0) / oAB);
      ys.push((pairGive.get(key(b, a)) ?? 0) / oBA);
    }
  }
  const rateCorrelation = pearson(xs, ys);

  const last = frames[frames.length - 1];
  return {
    opportunities, gives, rates,
    contingency: safe(rates.priorGiver, rates.neutral),
    withholding: safe(rates.hostile, rates.neutral),
    reciprocalDyads,
    rateCorrelation,
    totalGives: cumGives,
    totalDefections: cumDef,
    coopRatio: safe(cumGives, cumDef),
    giniFinal: gini(last.agents.map(r => r[4])),
    aliveFinal: last.agents.length,
    giftMatrix: giftMatrix.map(row => row.map(v => Math.round(v * 10) / 10)),
    series,
  };
}

function pearson(xs: number[], ys: number[]): number {
  const n = xs.length;
  if (n < 4) return NaN;
  const mx = xs.reduce((s, v) => s + v, 0) / n;
  const my = ys.reduce((s, v) => s + v, 0) / n;
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) {
    sxy += (xs[i] - mx) * (ys[i] - my);
    sxx += (xs[i] - mx) ** 2;
    syy += (ys[i] - my) ** 2;
  }
  if (sxx < 1e-12 || syy < 1e-12) return NaN;
  return Math.round((sxy / Math.sqrt(sxx * syy)) * 1000) / 1000;
}

export function gini(values: number[]): number {
  const v = values.filter(x => x >= 0).sort((a, b) => a - b);
  const n = v.length;
  if (n === 0) return 0;
  const sum = v.reduce((s, x) => s + x, 0);
  if (sum <= 0) return 0;
  let cum = 0;
  for (let i = 0; i < n; i++) cum += (2 * (i + 1) - n - 1) * v[i];
  return Math.round((cum / (n * sum)) * 1000) / 1000;
}
