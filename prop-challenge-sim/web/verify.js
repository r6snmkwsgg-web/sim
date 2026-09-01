/*
 * verify.js -- checks the JavaScript port against the Python engine.
 *
 * The browser build is only worth shipping if it computes the same thing the
 * tested Python engine does.  These are the same invariants, transliterated:
 * the dip-and-recover case, exact liquidation at the floor, the cost
 * arithmetic, and the gambler's-ruin identity.  Run with `node web/verify.js`.
 */

import {
  DEFAULT_COSTS, INSTRUMENTS, STRATEGIES, ZERO_COSTS, defaultConfig,
  generateSynthetic, runChallenge, runMonteCarlo, rng,
} from './propsim.js';

let pass = 0;
const fails = [];
const ok = (name, cond, detail = '') => {
  if (cond) { pass++; process.stdout.write('.'); }
  else { fails.push(`${name}: ${detail}`); process.stdout.write('F'); }
};
const near = (a, b, tol) => Math.abs(a - b) <= tol;

const TEST_INST = { symbol: 'TEST', pointValue: 1, minSize: 1, sizeStep: 1,
                    leverage: 1, marginPerUnit: null };

function makeBars(rows) {
  const t0 = Date.UTC(2024, 0, 2);
  return {
    symbol: 'TEST', timeframe: '1m', source: 'literal',
    ts: Float64Array.from(rows.map((_, i) => t0 + i * 60000)),
    open: Float64Array.from(rows.map(r => r[0])),
    high: Float64Array.from(rows.map(r => r[1])),
    low: Float64Array.from(rows.map(r => r[2])),
    close: Float64Array.from(rows.map(r => r[3])),
    spread: null,
  };
}

const scripted = (actions) => ({
  onStart() {}, onBar(ctx) { return actions[ctx.i - ctx.startIndex] ?? null; },
});
const longUnits = (n, extra = {}) =>
  Object.assign({ direction: 1, sizing: 'units', size: n }, extra);

const STATIC = defaultConfig({ drawdownMode: 'static' });

/* -- the headline case ---------------------------------------------------- */

{
  const bars = makeBars([
    [100, 100, 100, 100],
    [100, 101, 96, 101],     // $400 underwater intrabar, closes $100 up
    [101, 121, 101, 120],    // would have cleared the +$1,500 target
  ]);
  const r = runChallenge(bars, scripted({ 0: longUnits(100) }), TEST_INST,
                         ZERO_COSTS, STATIC, rng(7), 0, null, false);
  ok('dip-and-recover is a FAIL', r.outcome === 'FAIL_DRAWDOWN', r.outcome);
  ok('liquidates at the floor', near(r.finalBalance, 19700, 1e-6), r.finalBalance);
  ok('liquidation price', near(r.trades[0].exitMid, 97, 1e-9), r.trades[0].exitMid);
  ok('raw mark kept for diagnosis', near(r.breachEquity, 19600, 1e-6), r.breachEquity);
  // and the counterfactual the Python test also asserts
  const closeOnly = [101, 120].map(c => 20000 + (c - 100) * 100);
  ok('no close ever breaches', Math.min(...closeOnly) > 19700);
  ok('close-only engine would PASS', Math.max(...closeOnly) >= 21500);
}

/* -- short side, boundary, stop truncation -------------------------------- */

{
  const bars = makeBars([[100,100,100,100],[100,104,100,99],[99,99,80,80]]);
  const r = runChallenge(bars, scripted({ 0: { direction: -1, sizing: 'units', size: 100 } }),
                         TEST_INST, ZERO_COSTS, STATIC, rng(7), 0, null, false);
  ok('short breaches on the high', r.outcome === 'FAIL_DRAWDOWN', r.outcome);
  ok('short liquidation price', near(r.trades[0].exitMid, 103, 1e-9), r.trades[0].exitMid);
}
{
  const at = makeBars([[100,100,100,100],[100,100,97,100],[100,100,100,100]]);
  const inside = makeBars([[100,100,100,100],[100,100,97.01,100],[100,100,100,100]]);
  const a = runChallenge(at, scripted({ 0: longUnits(100) }), TEST_INST, ZERO_COSTS, STATIC, rng(1), 0, null, false);
  const b = runChallenge(inside, scripted({ 0: longUnits(100) }), TEST_INST, ZERO_COSTS, STATIC, rng(1), 0, null, false);
  ok('exactly at the limit breaches', a.outcome === 'FAIL_DRAWDOWN', a.outcome);
  ok('one dollar inside survives', b.outcome !== 'FAIL_DRAWDOWN', b.outcome);
}
{
  const bars = makeBars([[100,100,100,100],[100,100,90,95],[95,95,95,95]]);
  const r = runChallenge(bars, scripted({ 0: longUnits(100, { slPrice: 99.5 }) }),
                         TEST_INST, ZERO_COSTS, STATIC, rng(1), 0, null, false);
  ok('stop truncates the excursion', r.outcome !== 'FAIL_DRAWDOWN', r.outcome);
  ok('stopped out at the stop', near(r.finalBalance, 19950, 1e-6), r.finalBalance);
}

/* -- target, costs, exposure cap ------------------------------------------ */

{
  const bars = makeBars([[100,100,100,100],[100,116,100,115],[115,115,115,115]]);
  const r = runChallenge(bars, scripted({ 0: longUnits(100) }), TEST_INST,
                         ZERO_COSTS, STATIC, rng(1), 0, null, false);
  ok('passes on the target', r.outcome === 'PASS', r.outcome);
  ok('closes exactly on target', near(r.finalBalance, 21500, 1e-6), r.finalBalance);
}
{
  const bars = makeBars(Array(3).fill([100,100,100,100]));
  const cm = { spread: 0.10, commissionPerSide: 2.5, slippage: 0, useMeasuredSpread: false };
  const r = runChallenge(bars, scripted({ 0: longUnits(10), 1: 'CLOSE' }), TEST_INST,
                         cm, STATIC, rng(1), 0, null, false);
  ok('spread charged both sides', near(r.spreadPaid, 1.0, 1e-9), r.spreadPaid);
  ok('commission is $5 round turn', near(r.commissionPaid, 50, 1e-9), r.commissionPaid);
  ok('flat round trip loses exactly costs', near(r.finalBalance, 19949, 1e-6), r.finalBalance);
}
{
  const bars = makeBars(Array(3).fill([100,100,100,100]));
  const r = runChallenge(bars, scripted({ 0: longUnits(1000), 1: 'CLOSE' }), TEST_INST,
                         ZERO_COSTS, defaultConfig({ drawdownMode: 'static', exposureBasis: 'notional' }),
                         rng(1), 0, null, false);
  ok('exposure cap scales size down', near(r.trades[0].size, 150, 1e-9), r.trades[0].size);
}

/* -- limit entries --------------------------------------------------------- */

{
  const bars = makeBars([[100,100,100,100],[100,102,98,101],[101,101,101,101]]);
  const hit = runChallenge(bars, scripted({ 1: longUnits(100, { fillPrice: 99 }), 2: 'CLOSE' }),
                           TEST_INST, ZERO_COSTS, STATIC, rng(1), 0, null, false);
  ok('limit fills at its level', near(hit.trades[0].entryMid, 99, 1e-9), hit.trades[0]?.entryMid);
  ok('limit P&L', near(hit.finalBalance, 20200, 1e-6), hit.finalBalance);

  const miss = makeBars([[100,100,100,100],[100,100.5,99.8,100.2],[100.2,100.2,100.2,100.2]]);
  const r2 = runChallenge(miss, scripted({ 1: longUnits(100, { fillPrice: 99 }) }),
                          TEST_INST, ZERO_COSTS, STATIC, rng(1), 0, null, false);
  ok('unreached limit is rejected', r2.trades.length === 0 && r2.ordersRejected === 1,
     `trades ${r2.trades.length} rejected ${r2.ordersRejected}`);
}

/* -- trailing vs static ---------------------------------------------------- */

{
  const bars = makeBars([[100,100,100,100],[100,105,100,105],[105,105,101.5,105],[105,105,105,105]]);
  const s = runChallenge(bars, scripted({ 0: longUnits(100) }), TEST_INST, ZERO_COSTS,
                         defaultConfig({ drawdownMode: 'static' }), rng(1), 0, null, false);
  const t = runChallenge(bars, scripted({ 0: longUnits(100) }), TEST_INST, ZERO_COSTS,
                         defaultConfig({ drawdownMode: 'trailing_equity' }), rng(1), 0, null, false);
  ok('static survives the giveback', s.outcome !== 'FAIL_DRAWDOWN', s.outcome);
  ok('trailing does not', t.outcome === 'FAIL_DRAWDOWN', t.outcome);
  ok('trailing dies at peak-300', near(t.finalBalance, 20200, 1e-6), t.finalBalance);
}

/* -- gambler's ruin, end to end -------------------------------------------- */

process.stdout.write('\n  gambler\'s ruin: ');
{
  const bars = generateSynthetic('EURUSD', 90, 13);
  for (const [target, dd] of [[450, 150], [300, 300], [150, 450]]) {
    const cfg = defaultConfig({ profitTarget: target, maxDrawdown: dd,
                                drawdownMode: 'static', intrabarOrder: 'random' });
    const s = runMonteCarlo(bars, 'buy_and_hold', { size: 0.6 },
                            INSTRUMENTS.EURUSD, ZERO_COSTS, cfg, 1200, 77);
    const expected = dd / (target + dd);
    process.stdout.write(`${(s.passRate * 100).toFixed(1)}%/${(expected * 100).toFixed(0)}% `);
    ok(`ruin ${target}/${dd}`, Math.abs(s.passRate - expected) < 0.04,
       `got ${(s.passRate * 100).toFixed(2)}%, expected ${(expected * 100).toFixed(2)}%`);
  }
}

/* -- headline table shape --------------------------------------------------- */

process.stdout.write('\n\n  strategy        rulebook           pass   DD fail  timeout       EV\n');
{
  const bars = generateSynthetic('EURUSD', 180, 0);
  const inst = INSTRUMENTS.EURUSD;
  const cm = Object.assign({}, DEFAULT_COSTS.EURUSD);
  const rows = [
    ['buy and hold', 'buy_and_hold', { size: 0.45 }],
    ['fixed tp/sl', 'fixed_tp_sl', { size: 0.45, tpDollars: 900, slDollars: 150, entriesPerDay: 8 }],
    ['momentum', 'momentum', { size: 0.45, tpDollars: 900, slDollars: 150, lookback: 30 }],
  ];
  for (const [label, name, params] of rows) {
    for (const mode of ['trailing_equity', 'static']) {
      const cfg = defaultConfig({ drawdownMode: mode });
      const s = runMonteCarlo(bars, name, params, inst, cm, cfg, 4000, 2024);
      console.log(`  ${label.padEnd(15)} ${mode.padEnd(17)} ${(s.passRate * 100).toFixed(2).padStart(6)}%` +
                  ` ${(s.nDD / s.n * 100).toFixed(1).padStart(7)}% ${(s.nTO / s.n * 100).toFixed(1).padStart(7)}%` +
                  ` ${('$' + s.ev.toFixed(0)).padStart(8)}`);
      if (name === 'buy_and_hold' && mode === 'trailing_equity')
        ok('trailing kills buy-and-hold', s.passRate < 0.03, `${(s.passRate * 100).toFixed(2)}%`);
      if (name === 'buy_and_hold' && mode === 'static')
        ok('static buy-and-hold near breakeven', s.passRate > 0.05 && s.passRate < 0.18,
           `${(s.passRate * 100).toFixed(2)}%`);
    }
  }
}

console.log(`\n${pass} passed, ${fails.length} failed`);
for (const f of fails) console.log('  FAIL ' + f);
process.exit(fails.length ? 1 : 0);
