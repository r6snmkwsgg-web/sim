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

// ---------------------------------------------------------------------------
// Windowed pair correlation — the protocol's Test 4/5/6 measurement.
//
// For each ordered pair, count gifts per fixed window. Per window, correlate
// gifts A→B against gifts B→A across pairs (each unordered pair enters in
// both orientations, making the statistic symmetric). Mutual giving means the
// correlation rises above zero once histories accumulate, and holds.
// Punishment: around each known harm (take, attack, witnessed loot), compare
// the victim's gifts to the transgressor in the window before vs. after.
// ---------------------------------------------------------------------------

export interface WindowedReport {
  windowSize: number;
  corrSeries: number[];          // one r per window (NaN where undefined)
  lateMean: number;              // mean r over the last half of the run
  pairsUsed: number;
  punishment: { events: number; giftsBefore: number; giftsAfter: number };
  /**
   * Diagnostic variant: the same correlation computed on opportunity-
   * normalized rates (gifts per tick spent adjacent) instead of raw counts.
   * Raw counts are confounded by co-location — a pair that spends a window
   * side by side gives more in both directions whether or not anyone
   * remembers anything. Rates cancel that. Only present when frames are
   * supplied.
   */
  rateSeries?: number[];
  rateLateMean?: number;
  punishmentRate?: { beforeRate: number; afterRate: number;
                     oppBefore: number; oppAfter: number };
}

export function windowedReciprocity(events: SimEvent[], ticks: number,
                                    windowSize = 200,
                                    frames?: Frame[]): WindowedReport {
  const W = Math.floor(ticks / windowSize);
  const key = (a: number, b: number) => a * 1000 + b;
  const counts = new Map<number, Int32Array>();
  const pairTotal = new Map<number, number>();   // unordered activity
  const ukey = (a: number, b: number) => key(Math.min(a, b), Math.max(a, b));

  for (const e of events) {
    if (e.type !== 'give') continue;
    const w = Math.min(W - 1, Math.floor(e.tick / windowSize));
    let row = counts.get(key(e.a, e.b));
    if (!row) counts.set(key(e.a, e.b), row = new Int32Array(W));
    row[w]++;
    pairTotal.set(ukey(e.a, e.b), (pairTotal.get(ukey(e.a, e.b)) ?? 0) + 1);
  }

  const pairs: [number, number][] = [];
  for (const [uk, total] of pairTotal) {
    if (total >= 3) pairs.push([Math.floor(uk / 1000), uk % 1000]);
  }

  const corrSeries: number[] = [];
  for (let w = 0; w < W; w++) {
    const xs: number[] = [], ys: number[] = [];
    for (const [a, b] of pairs) {
      const ab = counts.get(key(a, b))?.[w] ?? 0;
      const ba = counts.get(key(b, a))?.[w] ?? 0;
      xs.push(ab, ba);
      ys.push(ba, ab);
    }
    corrSeries.push(xs.length >= 12 ? pearson(xs, ys) : NaN);
  }
  const late = corrSeries.slice(Math.floor(W / 2)).filter(Number.isFinite);
  const lateMean = late.length
    ? Math.round(late.reduce((s, v) => s + v, 0) / late.length * 1000) / 1000
    : NaN;

  let pEvents = 0, giftsBefore = 0, giftsAfter = 0;
  for (const e of events) {
    const harm = e.type === 'take' || e.type === 'attack' ||
                 (e.type === 'loot' && e.w);
    if (!harm) continue;
    if (e.tick < windowSize || e.tick > ticks - windowSize) continue;
    pEvents++;
    for (const g of events) {
      if (g.type !== 'give' || g.a !== e.b || g.b !== e.a) continue;
      if (g.tick >= e.tick - windowSize && g.tick < e.tick) giftsBefore++;
      else if (g.tick >= e.tick && g.tick < e.tick + windowSize) giftsAfter++;
    }
  }

  const report: WindowedReport = {
    windowSize, corrSeries, lateMean, pairsUsed: pairs.length,
    punishment: { events: pEvents, giftsBefore, giftsAfter },
  };

  if (frames) {
    // adjacency ticks per ordered pair per window (giver able to give)
    const opp = new Map<number, Int32Array>();
    for (const f of frames) {
      const w = Math.min(W - 1, Math.floor(f.tick / windowSize));
      for (const [idA, xA, yA, , loadA] of f.agents) {
        if (loadA < GIVE_ABLE) continue;
        for (const [idB, xB, yB] of f.agents) {
          if (idB === idA) continue;
          if (Math.max(Math.abs(xA - xB), Math.abs(yA - yB)) > 1) continue;
          let row = opp.get(key(idA, idB));
          if (!row) opp.set(key(idA, idB), row = new Int32Array(W));
          row[w]++;
        }
      }
    }
    const rateSeries: number[] = [];
    for (let w = 0; w < W; w++) {
      const xs: number[] = [], ys: number[] = [];
      for (const [a, b] of pairs) {
        const oAB = opp.get(key(a, b))?.[w] ?? 0;
        const oBA = opp.get(key(b, a))?.[w] ?? 0;
        if (oAB < 15 || oBA < 15) continue;
        const rAB = (counts.get(key(a, b))?.[w] ?? 0) / oAB;
        const rBA = (counts.get(key(b, a))?.[w] ?? 0) / oBA;
        xs.push(rAB, rBA);
        ys.push(rBA, rAB);
      }
      rateSeries.push(xs.length >= 12 ? pearson(xs, ys) : NaN);
    }
    const rlate = rateSeries.slice(Math.floor(W / 2)).filter(Number.isFinite);
    report.rateSeries = rateSeries;
    report.rateLateMean = rlate.length
      ? Math.round(rlate.reduce((s, v) => s + v, 0) / rlate.length * 1000) / 1000
      : NaN;

    // punishment, opportunity-normalized: victim→transgressor give rate
    let oppBefore = 0, oppAfter = 0;
    for (const e of events) {
      const harm = e.type === 'take' || e.type === 'attack' ||
                   (e.type === 'loot' && e.w);
      if (!harm) continue;
      if (e.tick < windowSize || e.tick > ticks - windowSize) continue;
      for (const f of frames) {
        if (f.tick < e.tick - windowSize || f.tick >= e.tick + windowSize) continue;
        const va = f.agents.find(r => r[0] === e.b);
        const ta = f.agents.find(r => r[0] === e.a);
        if (!va || !ta || va[4] < GIVE_ABLE) continue;
        if (Math.max(Math.abs(va[1] - ta[1]), Math.abs(va[2] - ta[2])) > 1) continue;
        if (f.tick < e.tick) oppBefore++; else oppAfter++;
      }
    }
    report.punishmentRate = {
      beforeRate: oppBefore ? Math.round(giftsBefore / oppBefore * 1e4) / 1e4 : NaN,
      afterRate: oppAfter ? Math.round(giftsAfter / oppAfter * 1e4) / 1e4 : NaN,
      oppBefore, oppAfter,
    };
  }
  return report;
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
