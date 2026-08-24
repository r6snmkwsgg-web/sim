import { createHash } from 'node:crypto';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { P } from '../core/params.js';
import { Sim } from '../engine/engine.js';
import { analyze, windowedReciprocity, type ReciprocityReport,
         type WindowedReport } from '../engine/metrics.js';

/**
 * The six-test verification protocol. Runs in order; stops at the first
 * failure, because each test makes the next meaningless if it fails.
 *
 *   1  no paired-transfer mechanic in the world/agent layer (source scan)
 *   2  determinism: same seed twice → identical ledger hash
 *   3  the memory→decision edge is live: per-give social values, logged
 *   4  windowed pair correlation rises above zero and holds; punishment
 *      drops the victim's giving to the transgressor
 *   5  the null model: social memory ablated → the correlation collapses
 *   6  ten RNG streams: the pattern shows in most of them
 *
 * Usage: node dist/cli/verify.js [--seed N]
 */

const argv = process.argv.slice(2);
const seed = argv.includes('--seed')
  ? Number(argv[argv.indexOf('--seed') + 1]) : 11;
const TICKS = P.TICKS;

let failed = false;
function verdict(n: number, name: string, ok: boolean, detail: string): void {
  console.log(`\n${ok ? 'PASS' : 'FAIL'}  Test ${n} — ${name}`);
  if (detail) console.log(detail.split('\n').map(l => '      ' + l).join('\n'));
  if (!ok) {
    console.log(`\nSTOPPED at Test ${n}: each later test would be meaningless.`);
    failed = true;
  }
}

function header(n: number, name: string): void {
  console.log(`\n━━ Test ${n} — ${name} ${'━'.repeat(Math.max(1, 50 - name.length))}`);
}

// ---------------------------------------------------------------------------
function main(): void {
  test1();
  if (failed) return exit();
  const canonical = test2();
  if (failed || !canonical) return exit();
  test3(canonical);
  if (failed) return exit();
  const mainReport = test4(canonical);
  if (failed) return exit();
  test5(mainReport);
  if (failed) return exit();
  test6();
  exit();
}
function exit(): void {
  process.exitCode = failed ? 1 : 0;
  if (!failed) console.log('\nAll six tests passed.');
}

// ---- Test 1: no paired-transfer mechanic ----------------------------------
// M0 vocabulary plus the M1 §4 list — the mechanic layer may not name the
// phenomena it is supposed to produce.
const FORBIDDEN = /\b(trade|exchange|barter|swap|reciproc\w*|fair|reputation|debt|owe[sd]?|tradition|culture|custom|ritual|norm|practice|teach|imitate|copy_behavior|meme|conform_to_group|inherit_behavior|lineage_preference)\b/i;

function scan(files: string[]): string[] {
  const hits: string[] = [];
  for (const f of files) {
    const lines = readFileSync(f, 'utf8').split('\n');
    lines.forEach((line, i) => {
      const m = line.match(FORBIDDEN);
      if (m) hits.push(`${f}:${i + 1}  [${m[1]}]  ${line.trim().slice(0, 70)}`);
    });
  }
  return hits;
}

function test1(): void {
  header(1, 'no paired-transfer mechanic');
  const dir = (d: string) => readdirSync(d).filter(f => f.endsWith('.ts'))
    .map(f => join(d, f));
  // the mechanic layer: everything that defines the world and the agents.
  // metrics/tests/docs are the measurement layer — they name what they
  // measure, and the protocol's own Tests 4-6 live there.
  const mechanic = [
    ...dir('src/agents'), ...dir('src/world'), ...dir('src/core'),
    'src/engine/engine.ts', 'src/engine/replay.ts', 'src/engine/ledger.ts',
  ];
  const hits = scan(mechanic);
  const measurementHits = scan(['src/engine/metrics.ts']).length;
  // and the action schema itself: transfers are give and take, nothing else
  const actionSrc = readFileSync('src/core/types.ts', 'utf8');
  const transferActions = [...actionSrc.matchAll(/\{ t: '(\w+)'/g)]
    .map(m => m[1]);
  const allowed = new Set(['move', 'gather', 'eat', 'store', 'give', 'take',
                           'takeCache', 'follow', 'attack', 'signal', 'rest']);
  const rogue = transferActions.filter(a => !allowed.has(a));
  const ok = hits.length === 0 && rogue.length === 0;
  verdict(1, 'mechanic layer contains no trading vocabulary or action', ok,
    `actions in the schema: ${transferActions.join(' ')}\n` +
    (rogue.length ? `ROGUE ACTIONS: ${rogue.join(' ')}\n` : '') +
    (hits.length ? hits.join('\n') :
      `0 hits across ${mechanic.length} mechanic files`) +
    `\n(measurement layer src/engine/metrics.ts mentions the words ` +
    `${measurementHits}× — it names what it measures, and Tests 4-6 run there)`);
}

// ---- Test 2: determinism ---------------------------------------------------
function test2(): Sim | null {
  header(2, 'determinism (ledger hash, same seed twice)');
  const run = () => {
    const sim = new Sim({ seed, stream: 1, ticks: TICKS, ablateSocial: false });
    sim.run();
    return sim;
  };
  const s1 = run(), s2 = run();
  const h1 = createHash('sha256').update(s1.ledger.toJSONL()).digest('hex');
  const h2 = createHash('sha256').update(s2.ledger.toJSONL()).digest('hex');
  const ok = h1 === h2;
  verdict(2, 'identical ledgers', ok,
    `run A sha256 ${h1.slice(0, 32)}…\nrun B sha256 ${h2.slice(0, 32)}…` +
    (ok ? `\n${s1.ledger.entries.length} entries, byte-identical` : ''));
  return ok ? s1 : null;
}

// ---- Test 3: the memory→decision edge is live ------------------------------
function test3(sim: Sim): void {
  header(3, 'memory→decision edge (one agent, every give, values at decision time)');
  // the most prolific giver
  const givesBy = new Map<number, number>();
  for (const e of sim.events) {
    if (e.type === 'give') givesBy.set(e.a, (givesBy.get(e.a) ?? 0) + 1);
  }
  const probe = [...givesBy.entries()].sort((p, q) => q[1] - p[1])[0]?.[0];
  if (probe === undefined) {
    verdict(3, 'no gives occurred at all', false, '');
    return;
  }
  // every give decision by the probe, with the social values read at scoring
  const rows: { tick: number; b: number; tr: number; fa: number }[] = [];
  for (const e of sim.ledger.entries) {
    if (e.type !== 'decision' || e.subject !== probe) continue;
    const d = e.data as any;
    if (d.act?.t !== 'give' || !d.soc) continue;
    rows.push({ tick: e.tick, b: d.soc.b, tr: d.soc.tr, fa: d.soc.fa });
  }
  const lines = [`probe: agent ${probe} (${givesBy.get(probe)} gives)`,
    `tick   → target   trust@decision   familiarity@decision`];
  const shown = rows.length <= 30
    ? rows
    : [...rows.slice(0, 15), null, ...rows.slice(-15)];
  for (const r of shown) {
    lines.push(r === null
      ? `  … ${rows.length - 30} more …`
      : `${String(r.tick).padStart(5)}  → #${String(r.b).padEnd(6)} ` +
        `${String(r.tr.toFixed(3)).padStart(8)}         ${r.fa.toFixed(3)}`);
  }
  // criteria: non-zero values exist, and per-target values change over time
  const nonZero = rows.filter(r => r.tr !== 0).length;
  let changing = 0;
  const byTarget = new Map<number, number[]>();
  for (const r of rows) {
    let l = byTarget.get(r.b);
    if (!l) byTarget.set(r.b, l = []);
    l.push(r.tr);
  }
  for (const [b, trs] of byTarget) {
    if (trs.length >= 2 && new Set(trs.map(v => v.toFixed(3))).size > 1) {
      changing++;
      lines.push(`trust trajectory toward #${b}: ` +
        trs.slice(0, 8).map(v => v.toFixed(2)).join(' → ') +
        (trs.length > 8 ? ' → …' : ''));
    }
    if (changing >= 3) break;
  }
  lines.push(`gives with non-zero trust at decision time: ${nonZero}/${rows.length}`);
  lines.push(`targets whose retrieved values changed across gives: ${changing}`);
  lines.push(`(zeros are first-contact gives — the empathy bootstrap; they must`);
  lines.push(` exist too, or nothing could ever start a relationship)`);
  const ok = nonZero > 0 && changing > 0;
  verdict(3, 'retrieved values are non-zero and move after interactions', ok,
    lines.join('\n'));
}

// ---- Test 4: the main measurement ------------------------------------------
function reportLines(r: WindowedReport): string {
  const fmt = (v: number) => (Number.isFinite(v) ? v.toFixed(3) : '  n/a');
  const series = r.corrSeries
    .map((v, i) => `w${i} [${i * r.windowSize}–${(i + 1) * r.windowSize})  ` +
      `counts r=${fmt(v)}` +
      (r.rateSeries ? `   rate r=${fmt(r.rateSeries[i])}` : ''))
    .join('\n');
  const p = r.punishment;
  let out = `${series}\nlate-half mean: counts r = ${r.lateMean}` +
    (r.rateLateMean !== undefined ? `, opportunity-normalized r = ${r.rateLateMean}` : '') +
    `  (${r.pairsUsed} active pairs)\n` +
    `punishment: around ${p.events} known harms, victim→transgressor gifts ` +
    `${p.giftsBefore} in the ${r.windowSize} ticks before vs ${p.giftsAfter} after`;
  if (r.punishmentRate) {
    const pr = r.punishmentRate;
    out += `\n            per adjacent tick: ${fmt(pr.beforeRate)} before vs ` +
      `${fmt(pr.afterRate)} after (${pr.oppBefore}/${pr.oppAfter} opportunities)`;
  }
  return out;
}

// Per SPEC amendment A1, Tests 4–6 gate on opportunity-normalized rates.
// Gate values are regression bounds pinned (with margin) to the committed
// canonical run, not preregistered statistics — the preregistered claim is
// the main/ablated separation itself.
function test4(sim: Sim): { w: WindowedReport; a: ReciprocityReport } {
  header(4, 'windowed pair correlation + punishment (main run, normalized per A1)');
  const w = windowedReciprocity(sim.events, TICKS, 200, sim.frames);
  const a = analyze(sim.frames, sim.events, sim.agents.length);
  const lastThree = (w.rateSeries ?? []).slice(-3).filter(Number.isFinite);
  const holds = w.rateLateMean !== undefined && Number.isFinite(w.rateLateMean) &&
    w.rateLateMean >= 0.2 && lastThree.length > 0 && lastThree.every(v => v > 0);
  const punishes = a.withholding < 1.05;   // transgressors do no better than strangers
  const strong = a.contingency >= 1.8 && a.permutationZ >= 4;
  verdict(4, 'normalized correlation rises and holds; transgressors are not favored',
    holds && punishes && strong, reportLines(w) +
    `\nfull-run (opportunity-normalized): contingency ${a.contingency.toFixed(2)}×, ` +
    `withholding ${a.withholding.toFixed(2)}×, rate correlation ` +
    `${a.rateCorrelation.toFixed(2)}, permutation z ${a.permutationZ.toFixed(2)}` +
    (holds ? '' : '\nrate correlation did not rise and hold') +
    (punishes ? '' : '\npunishment check FAILED: transgressors favored') +
    (strong ? '' : '\ncontingency/permutation gate FAILED'));
  return { w, a };
}

// ---- Test 5: the null model ------------------------------------------------
function test5(main: { w: WindowedReport; a: ReciprocityReport }): void {
  header(5, 'null model (same seed, social memory ablated) + permutation control');
  const sim = new Sim({ seed, stream: 1, ticks: TICKS, ablateSocial: true });
  sim.run();
  const w = windowedReciprocity(sim.events, TICKS, 200, sim.frames);
  const a = analyze(sim.frames, sim.events, sim.agents.length);
  const mR = main.w.rateLateMean ?? NaN, aR = w.rateLateMean ?? NaN;
  const collapsed = !Number.isFinite(aR) || aR < 0.15 || aR < mR / 2;
  const flat = !Number.isFinite(a.contingency) || a.contingency <= 1.5;
  const zGone = !Number.isFinite(a.permutationZ) || a.permutationZ <= 3;
  verdict(5, 'normalized correlation, contingency, and permutation z all collapse',
    collapsed && flat && zGone, reportLines(w) +
    `\nnormalized late-half r: main ${mR} vs ablated ${aR}` +
    `\ncontingency: main ${main.a.contingency.toFixed(2)}× vs ablated ` +
    `${a.contingency.toFixed(2)}×   permutation z: main ` +
    `${main.a.permutationZ.toFixed(2)} vs ablated ${a.permutationZ.toFixed(2)}` +
    (collapsed && flat && zGone ? '' :
      '\nRESULT VOID: the pattern comes from the utility shape, not history'));
}

// ---- Test 6: not a fluke ---------------------------------------------------
function test6(): void {
  header(6, 'ten RNG streams, same seed (normalized statistics)');
  let passing = 0;
  const lines: string[] = [];
  for (let s = 1; s <= 10; s++) {
    const sim = new Sim({ seed, stream: s, ticks: TICKS, ablateSocial: false });
    sim.run();
    const w = windowedReciprocity(sim.events, TICKS, 200, sim.frames);
    const a = analyze(sim.frames, sim.events, sim.agents.length);
    const ok = a.contingency >= 1.5 && a.rateCorrelation >= 0.3;
    if (ok) passing++;
    lines.push(`stream ${String(s).padStart(2)}: contingency ` +
      `${a.contingency.toFixed(2)}×  rate corr ${a.rateCorrelation.toFixed(2)}  ` +
      `windowed late r ${Number.isFinite(w.rateLateMean ?? NaN)
        ? (w.rateLateMean as number).toFixed(3) : '  n/a'}  z ` +
      `${a.permutationZ.toFixed(1)}  ` + (ok ? 'shows' : 'ABSENT'));
  }
  verdict(6, 'the pattern shows in most streams', passing >= 7,
    lines.join('\n') + `\n${passing}/10 streams show it`);
}

main();
