import assert from 'node:assert';
import { test } from 'node:test';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { M2 } from '../core/params.js';
import { Sim } from '../engine/engine.js';
import { replay, stateHash } from '../engine/replay.js';
import type { SimConfig } from '../core/types.js';

/**
 * Milestone-2 invariants.
 *
 * The perceptual asymmetry (SPEC-M2 §4.1) is asserted structurally here —
 * per the spec's instruction that it live in tests, not in a config value
 * someone can flip. The forbidden-vocabulary scan covers the mechanic
 * layer only; measurement code may name what it measures.
 */

const cfgBase: SimConfig = {
  seed: 5, stream: 3, ticks: 1000,
  ablateSocial: false, m2: true,
};

let shared: Sim | undefined;
function sharedRun(): Sim {
  if (!shared) {
    shared = new Sim({ ...cfgBase });
    shared.run();
  }
  return shared;
}

test('M2 forbidden vocabulary absent from the mechanic layer', () => {
  const FORBIDDEN = new RegExp(
    '\\b(word|meaning|translate|dictionary|vocabulary|grammar|semantics|' +
    'language|dialect|token_meaning|global_lexicon|shared_lexicon|' +
    'referent_table)\\b', 'i');
  const roots = ['src/agents', 'src/world', 'src/core'];
  const files: string[] = ['src/engine/engine.ts', 'src/engine/replay.ts',
                           'src/engine/ledger.ts'];
  for (const root of roots) {
    for (const f of readdirSync(root)) {
      const p = join(root, f);
      if (statSync(p).isFile() && p.endsWith('.ts')) files.push(p);
    }
  }
  for (const f of files) {
    const lines = readFileSync(f, 'utf8').split('\n');
    lines.forEach((line, i) => {
      assert.ok(!FORBIDDEN.test(line),
        `forbidden vocabulary in ${f}:${i + 1}: ${line.trim()}`);
    });
  }
});

test('M2 perceptual asymmetry is structural (§4.1 confound 1)', () => {
  // signals must carry beyond sight, or "communication" is shared percept
  assert.ok(M2.VISION < M2.SIGNAL_RADIUS,
    `vision ${M2.VISION} must be < signal radius ${M2.SIGNAL_RADIUS}`);
  // and the run must actually produce hear events where the hearer stood
  // beyond vision of the emission origin and saw no rich node itself
  const sim = sharedRun();
  let asymmetric = 0;
  for (const em of sim.emissions) {
    if (em.mode !== 1) continue;
    const frame = sim.frames[Math.min(em.t, sim.frames.length - 1)];
    for (const [hearer, couldSee] of em.hearers) {
      if (couldSee) continue;
      const row = frame.agents.find(r => r[0] === hearer);
      if (!row) continue;
      const d = Math.max(Math.abs(row[1] - em.x), Math.abs(row[2] - em.y));
      if (d > M2.VISION) asymmetric++;
    }
  }
  assert.ok(asymmetric > 0,
    'no asymmetric hear events — the information channel is dead');
});

test('M2 isolation invariant: no crossings before contact', () => {
  const sim = sharedRun();
  const mid = (M2.BARRIER_X0 + M2.BARRIER_X1) / 2;
  for (const f of sim.frames) {
    if (f.tick >= M2.CONTACT_TICK) break;
    for (const [id, x] of f.agents) {
      const bornWest = id < 2 * M2.AGENTS_PER_SIDE
        ? id < M2.AGENTS_PER_SIDE
        : (sim.births.find(b => b[1] === id)?.[5] ?? 0) < mid;
      assert.strictEqual(bornWest, x < mid,
        `agent ${id} on the wrong side at tick ${f.tick}`);
    }
  }
});

test('M2 birth payloads carry traits only — no lexical inheritance (§2.3)', () => {
  const sim = sharedRun();
  const births = sim.ledger.entries.filter(e => e.type === 'agent.birth');
  assert.ok(births.length > 0, 'no births in the probe run');
  for (const e of births) {
    assert.deepStrictEqual(Object.keys(e.data as object).sort(),
      ['a', 'b', 'c', 'dE', 'e', 'gen', 'traits', 'x', 'y']);
  }
});

test('M2 ledger replay reconstructs the full state', () => {
  const sim = sharedRun();
  const rep = replay(cfgBase.seed, sim.ledger.entries,
                     2 * M2.AGENTS_PER_SIDE, true, true);
  assert.strictEqual(stateHash(rep.world, rep.agents),
                     stateHash(sim.world, sim.agents));
});

test('M2 determinism: same seed and stream, same state', () => {
  const cfg: SimConfig = { ...cfgBase, ticks: 600, lean: true };
  const s1 = new Sim(cfg); s1.run();
  const s2 = new Sim(cfg); s2.run();
  assert.strictEqual(stateHash(s1.world, s1.agents),
                     stateHash(s2.world, s2.agents));
});
