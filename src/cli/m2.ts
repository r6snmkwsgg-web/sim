import { readFileSync, writeFileSync } from 'node:fs';
import { M2 } from '../core/params.js';
import type { SimConfig } from '../core/types.js';
import { Sim } from '../engine/engine.js';
import { analyzeM2, type M2RunData } from '../engine/metrics-m2.js';
import { replay, stateHash } from '../engine/replay.js';

/**
 * Run one Milestone-2 condition and print the preregistered report,
 * §5.4 permutation control first (per its own instruction).
 *
 * Usage: node dist/cli/m2.js [--seed N] [--stream N] [--ticks N]
 *          [--ablate-reinforce | --full-observability | --ablate-observation]
 *          [--lean] [--no-replay] [--demography-only]
 *          [--dump FILE]   save run data + trust for offline measurement
 *          [--from FILE]   skip the sim; analyze a dumped run
 */
const argv = process.argv.slice(2);
const get = (flag: string, dflt: number) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? Number(argv[i + 1]) : dflt;
};
const getS = (flag: string): string | undefined => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : undefined;
};
const cfg: SimConfig = {
  seed: get('--seed', 11),
  stream: get('--stream', 1),
  ticks: get('--ticks', M2.TICKS),
  ablateSocial: false,
  m2: true,
  ablateReinforce: argv.includes('--ablate-reinforce'),
  fullObservability: argv.includes('--full-observability'),
  ablateObservation: argv.includes('--ablate-observation'),
  lean: argv.includes('--lean'),
};
const condition = cfg.ablateReinforce ? 'ABLATION A (no reinforcement)'
  : cfg.fullObservability ? 'ABLATION B (full observability)'
  : cfg.ablateObservation ? 'ABLATION C (no social learning)'
  : 'MAIN';

const fromFile = getS('--from');
let run: M2RunData;
let finalTrust: number[][];
let sim: Sim | undefined;
if (fromFile) {
  const saved = JSON.parse(readFileSync(fromFile, 'utf8'));
  run = saved.run; finalTrust = saved.finalTrust;
  cfg.ticks = run.ticks;
  console.log(`── M2 ${condition} ─ loaded from ${fromFile}`);
} else {
  const t0 = performance.now();
  sim = new Sim(cfg);
  sim.run();
  const wall = (performance.now() - t0) / 1000;
  console.log(`── M2 ${condition} ─ seed ${cfg.seed} stream ${cfg.stream} ` +
    `─ ${cfg.ticks} ticks in ${wall.toFixed(1)}s ` +
    `(${sim.ledger.keep ? sim.ledger.entries.length + ' ledger entries' : 'lean'})`);
  run = {
    ticks: cfg.ticks, contactTick: Math.min(M2.CONTACT_TICK, cfg.ticks),
    frames: sim.frames, gathers: sim.gathers, births: sim.births,
    events: sim.events, emissions: sim.emissions, lexSnaps: sim.lexSnaps,
    foundersPerSide: M2.AGENTS_PER_SIDE,
  };
  finalTrust = [];
  for (const a of sim.agents) {
    for (const [b, r] of a.social) {
      if (Math.abs(r.trust) > 0.05) finalTrust.push([a.id, b, r.trust]);
    }
  }
  const dumpFile = getS('--dump');
  if (dumpFile) {
    writeFileSync(dumpFile, JSON.stringify({ run, finalTrust }));
    console.log(`run data dumped to ${dumpFile}`);
  }
}

// isolation invariant: nobody crosses before contact
const mid = (M2.BARRIER_X0 + M2.BARRIER_X1) / 2;
let crossings = 0;
for (const f of run.frames) {
  if (f.tick >= Math.min(M2.CONTACT_TICK, cfg.ticks)) break;
  for (const [id, x] of f.agents) {
    const westFounder = id < M2.AGENTS_PER_SIDE;
    const bornWest = id < 2 * M2.AGENTS_PER_SIDE
      ? westFounder
      : (run.births.find(b => b[1] === id)?.[5] ?? 0) < mid;
    if (bornWest !== x < mid) crossings++;
  }
}
console.log(`isolation: ${crossings === 0 ? 'intact ✓' :
  `VIOLATED (${crossings} agent-ticks across the divide pre-contact)`}`);

const popAt = (t: number) => {
  const f = run.frames[Math.min(t, run.frames.length - 1)];
  const w = f.agents.filter(r => r[1] < mid).length;
  return `${w}+${f.agents.length - w}`;
};
console.log(`population (west+east): ` +
  [0, 0.25, 0.5, 0.75, 1].map(fr =>
    `t${Math.round(fr * (cfg.ticks - 1))}=${popAt(Math.round(fr * (cfg.ticks - 1)))}`)
    .join('  '));
console.log(`emissions (mode 1): ${run.emissions.length}   ` +
  `births ${run.births.length}`);

if (!argv.includes('--demography-only')) {
  const rep = analyzeM2(run, finalTrust);

  const p = rep.permutation;
  console.log(`\n[§5.4 PERMUTATION — the decisive test, run first]`);
  console.log(`  kind alignment observed ${p.alignmentObserved} vs permuted ` +
    `${p.permutedMean}±${p.permutedSd} (z ${p.z}) over ${p.successEvents} ` +
    `successful acted-on calls → tokens ${p.differentiated
      ? 'DIFFERENTIATED' : 'NOT differentiated (alarm bells)'}`);

  console.log(`\n[§5.1 coherence] (drift null: ` +
    rep.drift.map(d => `pop${d.pop} ${(d.rate * 100).toFixed(0)}%`).join(', ') + ')');
  for (const c of rep.coherence) {
    console.log(`  pop${c.pop} kind${c.k}: ${c.achieved
      ? `COHERENT from t${c.start}` : 'not coherent'}  ` +
      `final agreement ${c.finalAgreement} (${c.finalQualified} qualified, ` +
      `modal token ${c.modal})`);
  }
  console.log(`  beats drift: ${rep.coherenceBeatsDrift ? 'YES' : 'no'}`);

  const s = rep.success;
  console.log(`\n[§5.2 communicative success] with-call ${s.rateSignal} vs ` +
    `baseline ${s.rateBaseline} → contingency ${s.contingency}× ` +
    `(${s.hearEvents} asymmetric hear events, ${s.controls} controls)`);

  console.log(`\n[§5.3 divergence] classes coherent in both: ` +
    `[${rep.divergence.coherentBoth.join(',')}]  divergent: ` +
    (rep.divergence.divergentClasses.length
      ? rep.divergence.divergentClasses.map(d =>
          `kind${d.k} (west tok${d.west} vs east tok${d.east})`).join('; ')
      : 'none'));

  console.log(`\n[§5.5 fidelity]`);
  for (const f of rep.fidelity) {
    console.log(`  pop${f.pop}: ` + f.series.map(pt =>
      `${pt.cohort}:${Number.isFinite(pt.value) ? pt.value : '—'}`).join(' '));
  }

  console.log(`\n[§5.6 borrowing]` + (rep.borrowing.length === 0 ? ' none' : ''));
  for (const b of rep.borrowing) {
    console.log(`  kind${b.k}: pop${b.adoptingPop} adopted the other side's ` +
      `token — share ${b.preShare}→${b.peakShare}, latency ${b.latency}t, ` +
      `adopters(${b.adopters}) trust-to-other-side ${b.adopterTrust} vs ` +
      `non-adopters ${b.nonAdopterTrust}`);
  }
  const d = rep.demography;
  console.log(`\ndemography: west ${d.west} east ${d.east}, born ${d.born}, ` +
    `died ${d.died}, max gen ${d.maxGen}`);
  console.log(`\nVERDICT (§6): ${rep.verdict.toUpperCase()}`);
}

if (sim && sim.ledger.keep && !argv.includes('--no-replay')) {
  const rep2 = replay(cfg.seed, sim.ledger.entries,
    cfg.agents ?? 2 * M2.AGENTS_PER_SIDE, true, true);
  const live = stateHash(sim.world, sim.agents);
  const replayed = stateHash(rep2.world, rep2.agents);
  console.log(live === replayed
    ? `ledger replay verified (state hash ${live})`
    : `LEDGER INCOMPLETE: ${replayed} != ${live}`);
  if (live !== replayed) process.exit(1);
}
