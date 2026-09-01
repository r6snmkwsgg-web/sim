/*
 * propsim.js -- browser/node port of the challenge engine.
 *
 * A faithful transliteration of propsim/engine.py: same intrabar marking, same
 * net-liquidation equity, same closed-form liquidation at the limit.  It exists
 * so the simulation can run where the reader is, instead of being a screenshot
 * of a run they have to take on trust.  web/verify.js re-runs the Python
 * suite's invariants against this port.
 *
 * Times are milliseconds (Python uses nanoseconds); nothing else differs.
 */

const MS_HOUR = 3600000;
const MS_DAY = 86400000;
const EPS = 1e-9;

/* ---------------------------------------------------------------- RNG --- */

// mulberry32: small, fast, seedable, and good enough for Monte Carlo.
export function rng(seed) {
  let a = (seed >>> 0) || 1;
  const r = () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  let spare = null;
  r.gauss = () => {
    if (spare !== null) { const s = spare; spare = null; return s; }
    let u = 0, v = 0, s = 0;
    do { u = r() * 2 - 1; v = r() * 2 - 1; s = u * u + v * v; }
    while (s >= 1 || s === 0);
    const f = Math.sqrt(-2 * Math.log(s) / s);
    spare = v * f;
    return u * f;
  };
  return r;
}

/* -------------------------------------------------------- instruments --- */

export const INSTRUMENTS = {
  EURUSD: { symbol: 'EURUSD', pointValue: 100000, minSize: 0.01, sizeStep: 0.01,
            leverage: 30, marginPerUnit: null, unit: 'lot' },
  XAUUSD: { symbol: 'XAUUSD', pointValue: 100, minSize: 0.01, sizeStep: 0.01,
            leverage: 20, marginPerUnit: null, unit: 'lot' },
  MNQ:    { symbol: 'MNQ', pointValue: 2, minSize: 1, sizeStep: 1,
            leverage: 20, marginPerUnit: 2400, unit: 'contract' },
};

export const DEFAULT_COSTS = {
  EURUSD: { spread: 0.00008, commissionPerSide: 2.5, slippage: 0 },
  XAUUSD: { spread: 0.30, commissionPerSide: 2.5, slippage: 0 },
  MNQ:    { spread: 0.25, commissionPerSide: 2.5, slippage: 0 },
};

export const ZERO_COSTS = { spread: 0, commissionPerSide: 0, slippage: 0,
                            useMeasuredSpread: false };

export function defaultConfig(over = {}) {
  return Object.assign({
    startingBalance: 20000,
    profitTarget: 1500,
    maxDrawdown: 300,
    durationHours: 24,
    maxExposurePct: 0.75,
    entryFee: 500,
    payout: 5000,
    drawdownMode: 'trailing_equity',   // static | trailing_equity | trailing_balance
    intrabarOrder: 'adverse_first',    // adverse_first | favorable_first | random
    exposureBasis: 'margin',           // margin | notional
    targetOnEquity: true,
  }, over);
}

export const breakevenRate = (c) => c.entryFee / c.payout;
export const expectedValue = (c, p) => p * c.payout - c.entryFee;

/* -------------------------------------------------------------- costs --- */

const _hsCache = new WeakMap();

export function halfSpreadSeries(bars, cm) {
  const key = `${cm.spread}|${cm.slippage || 0}|${cm.spreadMultiplier ?? 1}|` +
              `${cm.useMeasuredSpread !== false}`;
  let perBars = _hsCache.get(bars);
  if (!perBars) { perBars = new Map(); _hsCache.set(bars, perBars); }
  const hit = perBars.get(key);
  if (hit) return hit;

  const n = bars.close.length;
  const out = new Float64Array(n);
  const mult = cm.spreadMultiplier === undefined ? 1 : cm.spreadMultiplier;
  const slip = cm.slippage || 0;
  const useMeasured = cm.useMeasuredSpread !== false && bars.spread;
  for (let i = 0; i < n; i++) {
    out[i] = useMeasured ? bars.spread[i] * 0.5 * mult + slip
                         : 0.5 * cm.spread * mult + slip;
  }
  perBars.set(key, out);
  return out;
}

/* ---------------------------------------------------- synthetic market --- */

const SYNTH = {
  EURUSD: { p0: 1.0850, vol: 0.07, spread: 0.00008 },
  XAUUSD: { p0: 2350.0, vol: 0.16, spread: 0.30 },
  MNQ:    { p0: 18500.0, vol: 0.22, spread: 0.25 },
};

const SESSION_VOL = [
  0.55, 0.50, 0.50, 0.55, 0.65, 0.75, 0.85, 1.00,
  1.20, 1.25, 1.15, 1.05, 1.10, 1.45, 1.55, 1.40,
  1.20, 1.05, 0.90, 0.80, 0.70, 0.60, 0.55, 0.55,
];

const marketOpen = (d) => {
  const wd = d.getUTCDay();               // 0 Sun .. 6 Sat
  if (wd === 6) return false;
  if (wd === 0) return d.getUTCHours() >= 21;
  if (wd === 5) return d.getUTCHours() < 21;
  return true;
};

/**
 * Driftless path with volatility clustering, jumps and session structure.
 * Bars are aggregated from simulated sub-bar steps -- the extremes are what
 * the drawdown rule reads, so they must come from a path, never be decorated
 * onto a close.
 */
export function generateSynthetic(symbol, days, seed, barSeconds = 60,
                                  substeps = 10, jumpsPerDay = 2) {
  const p = SYNTH[symbol];
  const r = rng(seed * 2654435761 + 17);
  const t0 = Date.UTC(2024, 0, 1);
  const nBars = Math.floor((days * 86400) / barSeconds);
  const secondsPerYear = 252 * 24 * 3600;
  const dtSub = (barSeconds / substeps) / secondsPerYear;
  const sigmaBase = p.vol * Math.sqrt(dtSub);
  const rho = 0.97, sigmaV = 0.30;
  const jumpP = jumpsPerDay / (86400 / barSeconds);

  const ts = [], open = [], high = [], low = [], close = [], spread = [];
  let logVol = 0, price = p.p0;

  for (let k = 0; k < nBars; k++) {
    const when = new Date(t0 + k * barSeconds * 1000);
    if (!marketOpen(when)) continue;
    logVol = rho * logVol + Math.sqrt(1 - rho * rho) * sigmaV * r.gauss();
    const session = SESSION_VOL[when.getUTCHours()];
    const sigma = sigmaBase * session * Math.exp(logVol);

    const o = price;
    let h = price, l = price;
    for (let s = 0; s < substeps; s++) {
      price *= Math.exp(-0.5 * sigma * sigma + sigma * r.gauss());
      if (price > h) h = price; else if (price < l) l = price;
    }
    if (r() < jumpP) {
      price *= Math.exp(r.gauss() * sigma * Math.sqrt(substeps) * 6);
      if (price > h) h = price; else if (price < l) l = price;
    }
    let widen = 0.35 + 0.75 / session;
    const hour = when.getUTCHours();
    if (hour === 21 || hour === 22) widen *= 2.5;

    ts.push(when.getTime());
    open.push(o); high.push(h); low.push(l); close.push(price);
    spread.push(p.spread * widen);
  }
  return {
    symbol, timeframe: `${barSeconds}s`, source: `synthetic(seed=${seed})`,
    ts: Float64Array.from(ts), open: Float64Array.from(open),
    high: Float64Array.from(high), low: Float64Array.from(low),
    close: Float64Array.from(close), spread: Float64Array.from(spread),
  };
}

/* ------------------------------------------------------------- sizing --- */

function resolveSize(order, inst, price, equity) {
  const denom = price * inst.pointValue;
  if (denom <= 0) return 0;
  switch (order.sizing) {
    case 'units': return order.size;
    case 'notional': return order.size / denom;
    case 'account_pct': return Math.max(0, equity) * order.size / denom;
    case 'margin_pct': {
      const budget = Math.max(0, equity) * order.size;
      return inst.marginPerUnit !== null && inst.marginPerUnit !== undefined
        ? budget / inst.marginPerUnit
        : budget * inst.leverage / denom;
    }
    default: throw new Error(`unknown sizing ${order.sizing}`);
  }
}

function capExposure(size, inst, price, equity, maxPct, marginBasis) {
  if (size <= 0 || equity <= 0) return 0;
  const cap = maxPct * equity;
  const notional = Math.abs(size) * price * inst.pointValue;
  const used = marginBasis
    ? (inst.marginPerUnit != null ? Math.abs(size) * inst.marginPerUnit
                                  : notional / inst.leverage)
    : notional;
  return used <= cap || used <= 0 ? size : size * (cap / used);
}

const roundSize = (inst, size) =>
  inst.sizeStep > 0 ? Math.max(0, Math.floor(size / inst.sizeStep + 1e-9) * inst.sizeStep)
                    : size;

function resolveLevels(order, entryMid, d, size, pv) {
  let tp = order.tpPrice ?? null, sl = order.slPrice ?? null;
  const unit = pv * size;
  if (tp === null && order.tpDollars != null && unit > 0) tp = entryMid + d * (order.tpDollars / unit);
  if (sl === null && order.slDollars != null && unit > 0) sl = entryMid - d * (order.slDollars / unit);
  if (tp === null && order.tpPct != null) tp = entryMid * (1 + d * order.tpPct);
  if (sl === null && order.slPct != null) sl = entryMid * (1 - d * order.slPct);
  return [tp, sl];
}

const solveMidForEquity = (targetEq, balance, d, entryFill, hs, unit, pending) =>
  unit === 0 ? entryFill
             : d * hs + entryFill + d * (targetEq + pending - balance) / unit;

const clampBetween = (x, a, b) => {
  const lo = Math.min(a, b), hi = Math.max(a, b);
  return x < lo ? lo : (x > hi ? hi : x);
};

/* ------------------------------------------------------------- engine --- */

export function runChallenge(bars, strategy, inst, cm, cfg, r, startIndex,
                             halfSpread, collectCurve = false) {
  const { ts, high: hi, low: lo, close: cl } = bars;
  const n = ts.length;
  const hsArr = halfSpread || halfSpreadSeries(bars, cm);

  const startTs = ts[startIndex];
  const deadline = startTs + cfg.durationHours * MS_HOUR;
  const targetEquity = cfg.startingBalance + cfg.profitTarget;
  const pv = inst.pointValue;
  const commSide = cm.commissionPerSide;
  const ddLimit = cfg.maxDrawdown;
  const trailingEq = cfg.drawdownMode === 'trailing_equity';
  const trailingBal = cfg.drawdownMode === 'trailing_balance';
  const marginBasis = cfg.exposureBasis === 'margin';
  const targetOnEquity = cfg.targetOnEquity !== false;

  let balance = cfg.startingBalance;
  let equity = balance, peakEquity = balance, peakBalance = balance;
  let minEquity = balance, maxDD = 0;
  let floor = balance - ddLimit;

  let pos = null;
  const trades = [];
  let commissionPaid = 0, spreadPaid = 0, ordersRejected = 0, barsInMarket = 0;
  let outcome = null, breachTs = null, breachEquity = null;
  const curveTs = [], curveEq = [], curveFloor = [], curveFloorPx = [];

  /* The number a trader actually wants on the chart: the price at which the
     account dies right now.  Under a trailing rule it ratchets up behind every
     new equity high and never comes back down, which is the whole argument
     made visible. */
  const pushCurve = (t, eq) => {
    curveTs.push(t); curveEq.push(eq); curveFloor.push(floor);
    if (pos === null) { curveFloorPx.push(NaN); return; }
    const unit = pv * pos.size;
    curveFloorPx.push(solveMidForEquity(floor, balance, pos.direction,
      pos.entryFill, hsArr[Math.min(i, n - 1)], unit, commSide * pos.size));
  };

  const ctx = {
    bars, inst, cfg, rng: r, i: startIndex, startIndex, deadline,
    ts, high: hi, low: lo, close: cl, open: bars.open,
    balance, equity, position: null, nTrades: 0, state: {},
  };
  if (strategy.onStart) strategy.onStart(ctx);

  function closePosition(exitMid, exitTs, exitIndex, hs, reason) {
    const p = pos, d = p.direction;
    const exitFill = exitMid - d * hs;
    const gross = d * (exitMid - p.entryMid) * pv * p.size;
    const spreadCost = (p.entryHalfSpread + hs) * pv * p.size;
    const commission = 2 * commSide * p.size;
    const net = d * (exitFill - p.entryFill) * pv * p.size - commSide * p.size;
    balance += net;
    commissionPaid += commSide * p.size;
    spreadPaid += spreadCost;
    trades.push({
      direction: d, size: p.size, entryTs: p.entryTs, exitTs,
      entryIndex: p.entryIndex, exitIndex, entryMid: p.entryMid, exitMid,
      grossPnl: gross, spreadCost, commission,
      netPnl: gross - spreadCost - commission, reason,
    });
    pos = null;
    if (balance > peakBalance) {
      peakBalance = balance;
      if (trailingBal) floor = peakBalance - ddLimit;
    }
  }

  let i = startIndex, lastIndex = startIndex, barsInWindow = 0;

  while (i < n && ts[i] < deadline) {
    lastIndex = i;
    barsInWindow++;
    const hs = hsArr[i];

    if (pos !== null) {
      barsInMarket++;
      const d = pos.direction, entryFill = pos.entryFill, size = pos.size;
      const pendingExitComm = commSide * size;
      const unit = pv * size;

      let adverseMid, favorableMid, stopHit, tpHit;
      if (d > 0) {
        adverseMid = lo[i];
        stopHit = pos.sl !== null && adverseMid <= pos.sl;
        if (stopHit) adverseMid = pos.sl;
        favorableMid = hi[i];
        tpHit = pos.tp !== null && favorableMid >= pos.tp;
        if (tpHit) favorableMid = pos.tp;
      } else {
        adverseMid = hi[i];
        stopHit = pos.sl !== null && adverseMid >= pos.sl;
        if (stopHit) adverseMid = pos.sl;
        favorableMid = lo[i];
        tpHit = pos.tp !== null && favorableMid <= pos.tp;
        if (tpHit) favorableMid = pos.tp;
      }

      const adverseFirst = cfg.intrabarOrder === 'adverse_first' ? true
        : cfg.intrabarOrder === 'favorable_first' ? false : r() < 0.5;
      const marks = adverseFirst
        ? [[adverseMid, stopHit, 'stop_loss'], [favorableMid, tpHit, 'take_profit'], [cl[i], false, 'mark']]
        : [[favorableMid, tpHit, 'take_profit'], [adverseMid, stopHit, 'stop_loss'], [cl[i], false, 'mark']];

      for (let m = 0; m < 3; m++) {
        const mid = marks[m][0], hit = marks[m][1], reason = marks[m][2];
        const eq = balance + d * ((mid - d * hs) - entryFill) * unit - pendingExitComm;

        if (eq > peakEquity) {
          peakEquity = eq;
          if (trailingEq) floor = peakEquity - ddLimit;
        }

        if (eq <= floor + EPS) {
          breachEquity = eq;
          const exitMid = clampBetween(
            solveMidForEquity(floor, balance, d, entryFill, hs, unit, pendingExitComm),
            mid, pos.lastSafeMid);
          closePosition(exitMid, ts[i], i, hs, 'drawdown_breach');
          outcome = 'FAIL_DRAWDOWN';
          breachTs = ts[i];
          equity = balance;
          if (equity < minEquity) minEquity = equity;
          if (peakEquity - equity > maxDD) maxDD = peakEquity - equity;
          break;
        }

        if (eq < minEquity) minEquity = eq;
        if (peakEquity - eq > maxDD) maxDD = peakEquity - eq;

        if (targetOnEquity && eq >= targetEquity - EPS) {
          const exitMid = clampBetween(
            solveMidForEquity(targetEquity, balance, d, entryFill, hs, unit, pendingExitComm),
            pos.lastSafeMid, mid);
          closePosition(exitMid, ts[i], i, hs, 'profit_target');
          outcome = 'PASS';
          equity = balance;
          break;
        }

        pos.lastSafeMid = mid;
        equity = eq;

        if (hit) {
          closePosition(mid, ts[i], i, hs, reason);
          equity = balance;
          if (!targetOnEquity && balance >= targetEquity - EPS) outcome = 'PASS';
          break;
        }
      }

      if (outcome !== null) {
        if (collectCurve) pushCurve(ts[i], equity);
        break;
      }
    } else {
      equity = balance;
      if (equity <= floor + EPS) {
        outcome = 'FAIL_DRAWDOWN';
        breachTs = ts[i];
        breachEquity = equity;
        if (collectCurve) pushCurve(ts[i], equity);
        break;
      }
    }

    ctx.i = i; ctx.balance = balance; ctx.equity = equity;
    ctx.position = pos; ctx.nTrades = trades.length;
    const signal = strategy.onBar(ctx);

    if (signal) {
      if (signal === 'CLOSE') {
        if (pos !== null) {
          closePosition(cl[i], ts[i], i, hs, 'strategy_close');
          equity = balance;
          if (!targetOnEquity && balance >= targetEquity - EPS) outcome = 'PASS';
        }
      } else if (pos !== null) {
        ordersRejected++;
      } else {
        const mid = cl[i];
        let size = resolveSize(signal, inst, mid, equity);
        size = capExposure(size, inst, mid, equity, cfg.maxExposurePct, marginBasis);
        size = roundSize(inst, size);
        if (size < inst.minSize - 1e-12 || size <= 0) {
          ordersRejected++;
        } else {
          const d = signal.direction;
          const entryFill = mid + d * hs;
          const [tp, sl] = resolveLevels(signal, mid, d, size, pv);
          balance -= commSide * size;
          commissionPaid += commSide * size;
          pos = { direction: d, size, entryMid: mid, entryFill,
                  entryHalfSpread: hs, entryTs: ts[i], entryIndex: i,
                  tp, sl, lastSafeMid: mid };
          const eq = balance - 2 * hs * pv * size - commSide * size;
          equity = eq;
          if (eq <= floor + EPS) {
            breachEquity = eq;
            closePosition(mid, ts[i], i, hs, 'drawdown_breach');
            outcome = 'FAIL_DRAWDOWN';
            breachTs = ts[i];
            equity = balance;
          }
          if (equity < minEquity) minEquity = equity;
          if (peakEquity - equity > maxDD) maxDD = peakEquity - equity;
        }
      }
    }

    if (collectCurve) pushCurve(ts[i], equity);
    if (outcome !== null) break;
    i++;
  }

  const truncated = outcome === null && i >= n && (n === 0 || ts[n - 1] < deadline);

  if (outcome === null) {
    if (pos !== null) {
      closePosition(cl[lastIndex], ts[lastIndex], lastIndex, hsArr[lastIndex],
                    truncated ? 'end_of_data' : 'timeout');
      equity = balance;
      if (collectCurve && curveEq.length) curveEq[curveEq.length - 1] = equity;
    }
    outcome = balance >= targetEquity - EPS ? 'PASS' : 'FAIL_TIMEOUT';
  }
  if (equity < minEquity) minEquity = equity;

  return {
    outcome, startTs, endTs: n ? ts[lastIndex] : startTs, barsInWindow,
    finalBalance: balance, finalEquity: equity, peakEquity, minEquity,
    maxDrawdownReached: maxDD, commissionPaid, spreadPaid,
    totalCosts: commissionPaid + spreadPaid, trades,
    curveTs, curveEq, curveFloor, curveFloorPx, breachTs, breachEquity, truncated,
    ordersRejected, barsInMarket,
  };
}

/* --------------------------------------------------------- strategies --- */

export const STRATEGIES = {
  buy_and_hold: (p) => {
    let done = false;
    return {
      label: 'Buy and hold',
      onStart() { done = false; },
      onBar(ctx) {
        if (done || ctx.position) return null;
        done = true;
        return { direction: p.direction ?? 1, sizing: 'margin_pct', size: p.size,
                 tpPct: p.tpPct ?? null, slPct: p.slPct ?? null,
                 tpDollars: p.tpDollars ?? null, slDollars: p.slDollars ?? null };
      },
    };
  },
  fixed_tp_sl: (p) => {
    let pEntry = 0;
    return {
      label: 'Fixed TP/SL',
      onStart(ctx) {
        const stepMs = ctx.ts.length > 1 ? (ctx.ts[1] - ctx.ts[0]) : 60000;
        pEntry = Math.min(1, (p.entriesPerDay ?? 8) / (MS_DAY / stepMs));
      },
      onBar(ctx) {
        if (ctx.position) return null;
        if (ctx.rng() >= pEntry) return null;
        const d = p.direction ?? (ctx.rng() < 0.5 ? 1 : -1);
        return { direction: d, sizing: 'margin_pct', size: p.size,
                 tpPct: p.tpPct ?? null, slPct: p.slPct ?? null,
                 tpDollars: p.tpDollars ?? null, slDollars: p.slDollars ?? null };
      },
    };
  },
  momentum: (p) => {
    let readyAt = 0, seenTrades = 0;
    const lookback = p.lookback ?? 30, cooldown = p.cooldown ?? 5;
    return {
      label: 'Momentum breakout',
      onStart(ctx) { readyAt = ctx.startIndex + lookback; seenTrades = 0; },
      onBar(ctx) {
        if (ctx.nTrades > seenTrades) {
          seenTrades = ctx.nTrades;
          readyAt = Math.max(readyAt, ctx.i + cooldown);
        }
        if (ctx.position) return null;
        const i = ctx.i;
        if (i < readyAt || i < lookback) return null;
        let hh = -Infinity, ll = Infinity;
        for (let k = i - lookback; k < i; k++) {
          if (ctx.high[k] > hh) hh = ctx.high[k];
          if (ctx.low[k] < ll) ll = ctx.low[k];
        }
        const price = ctx.close[i];
        let d = 0;
        if (price > hh) d = 1; else if (price < ll) d = -1;
        if (d === 0) return null;
        return { direction: d, sizing: 'margin_pct', size: p.size,
                 tpPct: p.tpPct ?? null, slPct: p.slPct ?? null,
                 tpDollars: p.tpDollars ?? null, slDollars: p.slDollars ?? null };
      },
    };
  },
};

/* -------------------------------------------------------- monte carlo --- */

export function validStartRange(bars, cfg) {
  const horizon = cfg.durationHours * MS_HOUR;
  const cutoff = bars.ts[bars.ts.length - 1] - horizon;
  let lo = 0, hi = bars.ts.length - 1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (bars.ts[mid] <= cutoff) lo = mid; else hi = mid - 1;
  }
  return lo;
}

export function independentWindows(bars, cfg) {
  if (bars.ts.length < 2) return 0;
  const span = bars.ts[bars.ts.length - 1] - bars.ts[0];
  return Math.max(0, Math.floor(span / (cfg.durationHours * MS_HOUR)));
}

function barsInWindowAt(bars, start, horizon) {
  const deadline = bars.ts[start] + horizon;
  let lo = start, hi = bars.ts.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (bars.ts[mid] < deadline) lo = mid + 1; else hi = mid;
  }
  return lo - start;
}

export function sampleStarts(bars, cfg, n, seed, minBars = 240) {
  const r = rng(seed);
  const horizon = cfg.durationHours * MS_HOUR;
  const top = validStartRange(bars, cfg);
  if (top <= 0) throw new Error('dataset too short for one window');
  const starts = [];
  let rejected = 0, budget = n * 20;
  while (starts.length < n && budget-- > 0) {
    const i = Math.floor(r() * (top + 1));
    if (barsInWindowAt(bars, i, horizon) < minBars) { rejected++; continue; }
    starts.push(i);
  }
  return { starts, rejected };
}

export const Z95 = 1.959963984540054;

export function wilson(passes, n) {
  if (!n) return [0, 0];
  const p = passes / n, z = Z95;
  const denom = 1 + z * z / n;
  const centre = (p + z * z / (2 * n)) / denom;
  const half = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom;
  return [Math.max(0, centre - half), Math.min(1, centre + half)];
}

/**
 * Bootstrap over start-days: overlapping windows are not independent draws.
 * `samples = 0` skips it and falls back to Wilson -- worth doing for a sweep
 * cell whose interval is never displayed, since the bootstrap costs far more
 * than the simulation it summarises.
 */
export function clusterInterval(attempts, samples = 800, seed = 99) {
  if (!attempts.length) return [0, 0];
  if (!samples) return wilson(attempts.filter(a => a.outcome === 'PASS').length,
                              attempts.length);
  const byDay = new Map();
  for (const a of attempts) {
    const key = Math.floor(a.startTs / MS_DAY);
    if (!byDay.has(key)) byDay.set(key, []);
    byDay.get(key).push(a.outcome === 'PASS' ? 1 : 0);
  }
  const days = [...byDay.values()];
  if (days.length < 2) return wilson(attempts.filter(a => a.outcome === 'PASS').length,
                                     attempts.length);
  const r = rng(seed), k = days.length, rates = [];
  for (let b = 0; b < samples; b++) {
    let hits = 0, total = 0;
    for (let j = 0; j < k; j++) {
      const block = days[(r() * k) | 0];
      for (const v of block) { hits += v; total++; }
    }
    rates.push(total ? hits / total : 0);
  }
  rates.sort((a, b) => a - b);
  return [rates[Math.max(0, ((0.025 * rates.length) | 0) - 1)],
          rates[Math.min(rates.length - 1, (0.975 * rates.length) | 0)]];
}

/**
 * Run `n` attempts.  `onChunk` makes it cooperative: the browser calls this in
 * animation frames so a 10,000-attempt run never freezes the page.
 */
export function runMonteCarlo(bars, strategyName, params, inst, cm, cfg, n, seed,
                              minBars = 240) {
  const { starts, rejected } = sampleStarts(bars, cfg, n, seed, minBars);
  const hs = halfSpreadSeries(bars, cm);
  const strategy = STRATEGIES[strategyName](params);
  const attempts = [];
  for (let k = 0; k < starts.length; k++) {
    const res = runChallenge(bars, strategy, inst, cm, cfg,
                             rng(seed * 1000003 + k), starts[k], hs, false);
    attempts.push({ outcome: res.outcome, startTs: res.startTs,
                    maxDrawdown: res.maxDrawdownReached,
                    totalCosts: res.totalCosts, nTrades: res.trades.length });
  }
  return summarise(attempts, cfg, rejected, independentWindows(bars, cfg));
}

export function summarise(attempts, cfg, rejected = 0, indepWindows = 0,
                          bootstrapSamples = 800) {
  const n = attempts.length;
  let nPass = 0, nDD = 0, nTO = 0, costs = 0, trades = 0;
  const dds = [];
  for (const a of attempts) {
    if (a.outcome === 'PASS') nPass++;
    else if (a.outcome === 'FAIL_DRAWDOWN') nDD++;
    else nTO++;
    costs += a.totalCosts; trades += a.nTrades; dds.push(a.maxDrawdown);
  }
  dds.sort((a, b) => a - b);
  const passRate = n ? nPass / n : 0;
  const [cl, ch] = clusterInterval(attempts, bootstrapSamples);
  return {
    n, nPass, nDD, nTO, passRate, rejected, indepWindows,
    wilson: wilson(nPass, n),
    cluster: [cl, ch],
    breakeven: breakevenRate(cfg),
    ev: expectedValue(cfg, passRate),
    evLow: expectedValue(cfg, cl), evHigh: expectedValue(cfg, ch),
    medianDD: n ? dds[n >> 1] : 0,
    meanCosts: n ? costs / n : 0,
    meanTrades: n ? trades / n : 0,
    attempts,
  };
}


/* ------------------------------------------------------- packed bars --- */

/**
 * Decode the base64 varint blob produced by web/pack_bars.py.
 * Deltas are zigzag varints in integer points; see that script for the layout.
 */
export function decodePackedBars(blob, symbol = 'EURUSD') {
  const bin = atob(blob.b64);
  const n = blob.n, scale = blob.scale;
  const ts = new Float64Array(n), open = new Float64Array(n);
  const high = new Float64Array(n), low = new Float64Array(n);
  const close = new Float64Array(n);

  let p = 0;
  const readVarint = () => {
    let shift = 0, result = 0, b;
    do {
      b = bin.charCodeAt(p++);
      result += (b & 0x7F) * Math.pow(2, shift);  // += not |=: stay off 32-bit truncation
      shift += 7;
    } while (b & 0x80);
    return (result >>> 1) ^ -(result & 1);          // un-zigzag
  };

  let minute = blob.t0, prevClose = 0;
  for (let k = 0; k < n; k++) {
    const dt = readVarint();
    const dOpen = readVarint();
    const dHigh = readVarint();
    const dLow = readVarint();
    const dClose = readVarint();
    minute += dt;
    const o = (k === 0 ? dOpen : prevClose + dOpen);
    const h = o + dHigh, l = o + dLow, c = o + dClose;
    ts[k] = minute * 60000;
    open[k] = o / scale; high[k] = h / scale;
    low[k] = l / scale; close[k] = c / scale;
    prevClose = c;
  }
  return { symbol, timeframe: '1m', source: 'HistData.com EURUSD M1',
           ts, open, high, low, close, spread: null };
}
