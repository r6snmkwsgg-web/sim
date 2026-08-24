import { P } from '../core/params.js';
import { runSim } from './run.js';

/**
 * §4.2 criterion 3 — reproducible-in-kind. Re-run the same seed under many
 * RNG streams (same world, different luck), plus the ablated control for
 * each. The phenomenon counts only if it recurs at above-chance rate, and
 * only when social memory is on.
 */
const argv = process.argv.slice(2);
const seed = argv.includes('--seed') ? Number(argv[argv.indexOf('--seed') + 1]) : 11;
const nStreams = argv.includes('--streams')
  ? Number(argv[argv.indexOf('--streams') + 1]) : 12;

interface Row {
  stream: number; contingency: number; withholding: number; corr: number;
  dyads: number; gives: number; alive: number;
  aContingency: number; aCorr: number; aGives: number;
}

const rows: Row[] = [];
console.log(`sweep: seed ${seed}, ${nStreams} streams, main + ablated control\n`);
for (let s = 1; s <= nStreams; s++) {
  const main = runSim({ seed, stream: s, ticks: P.TICKS, ablateSocial: false });
  const abl = runSim({ seed, stream: s, ticks: P.TICKS, ablateSocial: true });
  rows.push({
    stream: s,
    contingency: main.report.contingency,
    withholding: main.report.withholding,
    corr: main.report.rateCorrelation,
    dyads: main.report.reciprocalDyads,
    gives: main.report.totalGives,
    alive: main.report.aliveFinal,
    aContingency: abl.report.contingency,
    aCorr: abl.report.rateCorrelation,
    aGives: abl.report.totalGives,
  });
  const r = rows[rows.length - 1];
  console.log(`stream ${String(s).padStart(2)}  ` +
    `contingency ${f(r.contingency)}×  withhold ${f(r.withholding)}×  ` +
    `corr ${f(r.corr)}  dyads ${String(r.dyads).padStart(2)}  ` +
    `gives ${String(r.gives).padStart(4)}  alive ${String(r.alive).padStart(2)}` +
    `   | ablated: contingency ${f(r.aContingency)}×  corr ${f(r.aCorr)}`);
}

const ok = rows.filter(r => r.contingency >= 1.5 && r.dyads >= 2 &&
                            r.corr >= 0.3).length;
const aOk = rows.filter(r => Number.isFinite(r.aContingency) &&
                             r.aContingency >= 1.5 && r.aCorr >= 0.3).length;
const med = (xs: number[]) => {
  const v = xs.filter(Number.isFinite).sort((a, b) => a - b);
  return v.length ? v[Math.floor(v.length / 2)] : NaN;
};
console.log(`\nreciprocity present (contingency ≥ 1.5×, ≥2 dyads): ` +
  `${ok}/${nStreams} streams  (median contingency ${f(med(rows.map(r => r.contingency)))}×)`);
console.log(`ablated control reaching the same bar:               ` +
  `${aOk}/${nStreams} streams  (median ${f(med(rows.map(r => r.aContingency)))}×)`);

function f(v: number): string {
  return Number.isFinite(v) ? v.toFixed(2).padStart(5) : '    —';
}
