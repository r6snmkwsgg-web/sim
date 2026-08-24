import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { M1, P } from '../core/params.js';
import type { SimConfig } from '../core/types.js';
import { Sim } from '../engine/engine.js';
import { analyzeM1, type M1Report } from '../engine/metrics-m1.js';
import { replay, stateHash } from '../engine/replay.js';
import { m1NodeSpec } from '../world/world.js';

/**
 * Run one Milestone-1 condition and print the preregistered report.
 *
 * Usage: node dist/cli/m1.js [--seed N] [--stream N] [--ticks N]
 *          [--ablate-observation | --ablate-inheritance | --scramble]
 *          [--lean] [--no-replay] [--demography-only]
 */
const argv = process.argv.slice(2);
const get = (flag: string, dflt: number) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? Number(argv[i + 1]) : dflt;
};
const cfg: SimConfig = {
  seed: get('--seed', 11),
  stream: get('--stream', 1),
  ticks: get('--ticks', M1.TICKS),
  ablateSocial: false,
  m1: true,
  ablateObservation: argv.includes('--ablate-observation'),
  ablateInheritance: argv.includes('--ablate-inheritance'),
  scrambleChildren: argv.includes('--scramble'),
  lean: argv.includes('--lean'),
};

const t0 = performance.now();
const sim = new Sim(cfg);
sim.run();
const wall = (performance.now() - t0) / 1000;

const condition = cfg.ablateObservation ? 'ABLATION A (no observation)'
  : cfg.ablateInheritance ? 'ABLATION B (random child traits)'
  : cfg.scrambleChildren ? 'ABLATION C (spatial scramble)'
  : 'MAIN';

console.log(`── M1 ${condition} ─ seed ${cfg.seed} stream ${cfg.stream} ` +
  `─ ${cfg.ticks} ticks in ${wall.toFixed(1)}s ` +
  `(${sim.ledger.keep ? sim.ledger.entries.length + ' ledger entries' : 'lean'})`);

// §2 neutrality verification: the three pith sites must be numerically
// identical in count, cap, and regen before any result means anything.
const sites = sim.world.siteCenters!;
const perSite = sites.map(() => ({ n: 0 }));
for (const nd of sim.world.nodes) {
  if (nd.k !== 1) continue;
  let best = 0, bd = Infinity;
  sites.forEach(([sx, sy], i) => {
    const d = (sx - nd.x) ** 2 + (sy - nd.y) ** 2;
    if (d < bd) { bd = d; best = i; }
  });
  perSite[best].n++;
}
const spec = m1NodeSpec(1);
console.log(`pith sites: nodes ${perSite.map(s => s.n).join('/')}  ` +
  `cap ${spec.cap} regen ${spec.regen} each — ` +
  (perSite.every(s => s.n === M1.PITH_PER_SITE)
    ? 'yield-identical ✓' : 'NOT IDENTICAL — result void'));

// demography (tuning-relevant; §8 territory)
const popAt = (t: number) =>
  sim.frames[Math.min(t, sim.frames.length - 1)].agents.length;
console.log(`population: ${[0, 0.25, 0.5, 0.75, 1].map(f =>
  `t${Math.round(f * (cfg.ticks - 1))}=${popAt(Math.round(f * (cfg.ticks - 1)))}`)
  .join('  ')}`);
const deathsBy = { age: 0, starvation: 0, violence: 0 };
for (const e of sim.ledger.keep ? sim.ledger.entries : []) {
  if (e.type === 'agent.death') {
    deathsBy[(e.data as any).cause as keyof typeof deathsBy]++;
  }
}
if (sim.ledger.keep) {
  console.log(`deaths: age ${deathsBy.age}, starvation ${deathsBy.starvation}, ` +
    `violence ${deathsBy.violence}   births ${sim.births.length}`);
}

if (argv.includes('--demography-only')) process.exit(0);

const report: M1Report = analyzeM1({
  ticks: cfg.ticks, frames: sim.frames, gathers: sim.gathers,
  births: sim.births, events: sim.events,
  founders: cfg.agents ?? M1.AGENTS_START,
  siteCenters: sites,
});

printDimension(report, 'token');
printDimension(report, 'site');
const d = report.demography;
console.log(`demography: alive ${d.aliveFinal}, born ${d.born}, died ${d.died}, ` +
  `mean lifespan ${d.meanLifespan}, max gen ${d.maxGen}, ` +
  `living gen min/median ${d.minLivingGen}/${d.medianLivingGen}`);
console.log(`drift null (neutral copying, ${report.drift.reps} reps): ` +
  `token ${(report.drift.token * 100).toFixed(1)}%  ` +
  `site ${(report.drift.site * 100).toFixed(1)}%`);

function printDimension(r: M1Report, dim: 'token' | 'site'): void {
  const x = r[dim];
  console.log(`\n[${dim}] ${x.options} options, ${x.holdersFinal} holders at end`);
  if (x.practices.length === 0) {
    console.log('  no practice reached threshold');
  }
  for (const p of x.practices) {
    console.log(`  option ${p.option}: threshold ${p.start}–${p.end} ` +
      `(${p.end - p.start} ticks)  origin #${p.originAgent} ` +
      `(gen ${p.originGen}, t=${p.originTick}, ` +
      `${p.originDeadBy >= 0 ? `died t=${p.originDeadBy}` : 'alive at end'})  ` +
      `3-gen survival: strict ${p.survivedStrict ? 'YES' : 'no'} / ` +
      `median ${p.survivedMedian ? 'YES' : 'no'}`);
  }
  console.log(`  transmission contingency ${x.contingency}× ` +
    `(exposed ${x.adoptExposed[0]}/${x.adoptExposed[1]}, ` +
    `unexposed ${x.adoptUnexposed[0]}/${x.adoptUnexposed[1]})  ` +
    `permutation mean ${x.permutationMean}× (z ${x.permutationZ})`);
}

// optional recording for the existing L3 viewer (drag & drop it in)
const outIdx = argv.indexOf('--out');
if (outIdx >= 0) {
  const dir = argv[outIdx + 1];
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'recording.json'), JSON.stringify({
    meta: {
      project: 'OpenCivilization M1', seed: cfg.seed, stream: cfg.stream,
      ticks: cfg.ticks, ablateSocial: false,
      wallMs: Math.round(wall * 1000),
      ledgerEntries: sim.ledger.keep ? sim.ledger.entries.length : 0,
      finalHash: '',
    },
    world: {
      size: P.WORLD, atmosPeriod: P.ATMOS_PERIOD, atmosOpen: P.ATMOS_OPEN,
      elevation: Array.from(sim.world.elevation, v => Math.round(v * 255)),
      nodes: sim.world.nodes.map(n => ({ id: n.id, x: n.x, y: n.y, k: n.k })),
      caps: [m1NodeSpec(0).cap, m1NodeSpec(1).cap, m1NodeSpec(2).cap],
    },
    agents: sim.agents.map(a => ({
      id: a.id, traits: a.traits, home: [a.homeX, a.homeY], died: a.diedTick,
      social: [...a.social.entries()]
        .filter(([, r]) => Math.abs(r.trust) > 0.05 || r.familiarity > 0.1)
        .map(([b, r]) => [b, Math.round(r.trust * 100) / 100,
                          Math.round(r.familiarity * 100) / 100]),
    })),
    frames: sim.frames,
    nodeSnaps: sim.nodeSnaps,
    cacheSnaps: sim.cacheSnaps,
    events: sim.events.filter(e => e.type !== 'signal' || e.tick % 3 === 0),
    report: {
      totalGives: sim.events.filter(e => e.type === 'give').length,
      totalDefections: sim.events.filter(e =>
        e.type === 'take' || e.type === 'attack' || e.type === 'loot').length,
      rates: { priorGiver: NaN, neutral: NaN, hostile: NaN },
      contingency: NaN, withholding: NaN, rateCorrelation: NaN,
      permutationZ: NaN, reciprocalDyads: NaN, giniFinal: NaN,
      aliveFinal: report.demography.aliveFinal,
      m1: {
        tokenPractices: report.token.practices,
        tokenContingency: report.token.contingency,
        maxGen: report.demography.maxGen,
      },
    },
  }));
  console.log(`recording written to ${dir}/ (drag recording.json into the viewer)`);
}

// ledger completeness still holds at M1 scale (full runs only)
if (sim.ledger.keep && !argv.includes('--no-replay')) {
  const rep = replay(cfg.seed, sim.ledger.entries,
    cfg.agents ?? M1.AGENTS_START, true);
  const live = stateHash(sim.world, sim.agents);
  const replayed = stateHash(rep.world, rep.agents);
  console.log(live === replayed
    ? `ledger replay verified (state hash ${live})`
    : `LEDGER INCOMPLETE: ${replayed} != ${live}`);
  if (live !== replayed) process.exit(1);
}
