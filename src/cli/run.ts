import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { P } from '../core/params.js';
import type { SimConfig } from '../core/types.js';
import { Sim } from '../engine/engine.js';
import { analyze } from '../engine/metrics.js';
import { replay, stateHash } from '../engine/replay.js';
import { describe } from './describe.js';

/**
 * Run one Milestone-0 world and write its record:
 *
 *   runs/<out>/recording.json  — frames, events, metrics (feeds the L3 viewer)
 *   runs/<out>/ledger.jsonl    — the full causal ledger (§4.1)
 *   runs/<out>/traceable.json  — causal closure of every social event, with
 *                                human-readable descriptions (viewer trace mode)
 *
 * Usage: node dist/cli/run.js [--seed N] [--stream N] [--ticks N]
 *                             [--ablate-social] [--out runs/name] [--quiet]
 */

export function parseArgs(argv: string[]): SimConfig & { out: string; quiet: boolean } {
  const get = (flag: string, dflt: number) => {
    const i = argv.indexOf(flag);
    return i >= 0 ? Number(argv[i + 1]) : dflt;
  };
  return {
    seed: get('--seed', 11),
    stream: get('--stream', 1),
    ticks: get('--ticks', P.TICKS),
    ablateSocial: argv.includes('--ablate-social'),
    out: (() => { const i = argv.indexOf('--out'); return i >= 0 ? argv[i + 1] : ''; })(),
    quiet: argv.includes('--quiet'),
  };
}

export function runSim(cfg: SimConfig) {
  const t0 = performance.now();
  const sim = new Sim(cfg);
  sim.run();
  const wallMs = performance.now() - t0;
  const report = analyze(sim.frames, sim.events, P.N_AGENTS);
  return { sim, report, wallMs };
}

export function buildRecording(sim: Sim, report: ReturnType<typeof analyze>,
                               wallMs: number) {
  return {
    meta: {
      project: 'OpenCivilization M0', seed: sim.cfg.seed, stream: sim.cfg.stream,
      ticks: sim.cfg.ticks, ablateSocial: sim.cfg.ablateSocial,
      wallMs: Math.round(wallMs), ledgerEntries: sim.ledger.entries.length,
      finalHash: stateHash(sim.world, sim.agents),
    },
    world: {
      size: P.WORLD,
      atmosPeriod: P.ATMOS_PERIOD, atmosOpen: P.ATMOS_OPEN,
      elevation: Array.from(sim.world.elevation, v => Math.round(v * 255)),
      nodes: sim.world.nodes.map(n => ({ id: n.id, x: n.x, y: n.y, k: n.k })),
      caps: P.RESOURCES.map(r => r.cap),
    },
    agents: sim.agents.map(a => ({
      id: a.id, traits: a.traits, home: [a.homeX, a.homeY],
      died: a.diedTick,
      social: [...a.social.entries()]
        .filter(([, r]) => Math.abs(r.trust) > 0.02 || r.familiarity > 0.05)
        .map(([b, r]) => [b, Math.round(r.trust * 100) / 100,
                          Math.round(r.familiarity * 100) / 100,
                          Math.round(r.debt * 10) / 10]),
    })),
    frames: sim.frames,
    nodeSnaps: sim.nodeSnaps,
    cacheSnaps: sim.cacheSnaps,
    events: sim.events,
    report,
  };
}

/** ledger entries reachable from social events, with descriptions (viewer) */
export function buildTraceable(sim: Sim) {
  const roots = sim.events
    .filter(e => e.type === 'give' || e.type === 'take' || e.type === 'attack' ||
                 e.type === 'loot' || e.type === 'death')
    .map(e => e.ledger);
  const keep = new Set<number>();
  const stack = [...roots];
  while (stack.length) {
    const id = stack.pop()!;
    if (keep.has(id)) continue;
    keep.add(id);
    const e = sim.ledger.get(id);
    if (e) for (const c of e.causes) stack.push(c);
  }
  const entries = [...keep].sort((a, b) => a - b).map(id => {
    const e = sim.ledger.get(id)!;
    return { id: e.id, tick: e.tick, kind: e.kind, type: e.type,
             subject: e.subject, causes: e.causes, desc: describe(e) };
  });
  return { roots, entries };
}

export function summarize(report: ReturnType<typeof analyze>,
                          cfg: SimConfig, wallMs: number,
                          ledgerEntries: number): string {
  const r = report;
  const pct = (v: number) => (v * 100).toFixed(2) + '%';
  const lines = [
    `── OpenCivilization M0 ─ seed ${cfg.seed} stream ${cfg.stream}` +
      (cfg.ablateSocial ? ' [SOCIAL MEMORY ABLATED]' : '') + ' ' + '─'.repeat(10),
    `ticks ${cfg.ticks}  wall ${(wallMs / 1000).toFixed(2)}s  ` +
      `ledger ${ledgerEntries} entries  alive ${r.aliveFinal}/${P.N_AGENTS}`,
    `gives ${r.totalGives}  defections ${r.totalDefections} ` +
      `(coop ratio ${fmt(r.coopRatio)})  gini ${r.giniFinal}`,
    `give rate | toward prior givers: ${pct(r.rates.priorGiver)}` +
      ` (${r.gives.priorGiver}/${r.opportunities.priorGiver})`,
    `          | toward strangers:    ${pct(r.rates.neutral)}` +
      ` (${r.gives.neutral}/${r.opportunities.neutral})`,
    `          | toward transgressors:${pct(r.rates.hostile)}` +
      ` (${r.gives.hostile}/${r.opportunities.hostile})`,
    `reciprocity contingency ${fmt(r.contingency)}×   ` +
      `withholding ${fmt(r.withholding)}×   reciprocal dyads ${r.reciprocalDyads}` +
      `   rate correlation ${fmt(r.rateCorrelation)}`,
  ];
  return lines.join('\n');
}

function fmt(v: number): string {
  return Number.isFinite(v) ? v.toFixed(2) : '—';
}

// ---- main -----------------------------------------------------------------
const isMain = process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  const cfg = parseArgs(process.argv.slice(2));
  const { sim, report, wallMs } = runSim(cfg);
  console.log(summarize(report, cfg, wallMs, sim.ledger.entries.length));

  if (cfg.out) {
    mkdirSync(cfg.out, { recursive: true });
    writeFileSync(join(cfg.out, 'recording.json'),
      JSON.stringify(buildRecording(sim, report, wallMs)));
    writeFileSync(join(cfg.out, 'ledger.jsonl'), sim.ledger.toJSONL());
    writeFileSync(join(cfg.out, 'traceable.json'),
      JSON.stringify(buildTraceable(sim)));
    writeFileSync(join(cfg.out, 'metrics.json'), JSON.stringify(report, null, 2));
    console.log(`written to ${cfg.out}/`);
  }

  // ledger integrity: replay must reproduce the final state bit-for-bit
  const rep = replay(cfg.seed, sim.ledger.entries);
  const live = stateHash(sim.world, sim.agents);
  const replayed = stateHash(rep.world, rep.agents);
  if (live !== replayed) {
    console.error(`LEDGER INCOMPLETE: replay hash ${replayed} != live ${live}`);
    process.exit(1);
  }
  console.log(`ledger replay verified (state hash ${live})`);
}
