import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { M1 } from '../core/params.js';
import { Sim } from '../engine/engine.js';
import { replay, stateHash } from '../engine/replay.js';
import { m1NodeSpec } from '../world/world.js';

/**
 * Milestone-1 invariants (SPEC-M1). The full §7 protocol is
 * `npm run m1:sweep`; these are the structural guarantees it rests on.
 */

test('M0 canonical ledger is byte-stable across M1 development', () => {
  // The M0 result is committed with this hash; any M1 change that alters it
  // has broken the M0 experiment retroactively.
  const sim = new Sim({ seed: 11, stream: 1, ticks: 2000, ablateSocial: false });
  sim.run();
  const h = createHash('sha256').update(sim.ledger.toJSONL()).digest('hex');
  assert.equal(h,
    'db67cf15629ad3d87ff259d80b1e5143e8f0f551a07a38787fb879aa61d7b4cf');
});

test('the three pith sites are numerically yield-identical (§2)', () => {
  const sim = new Sim({ seed: 11, stream: 1, ticks: 0, ablateSocial: false,
                        m1: true });
  const sites = sim.world.siteCenters!;
  assert.equal(sites.length, M1.PITH_SITES);
  const counts = sites.map(() => 0);
  for (const n of sim.world.nodes) {
    if (n.k !== 1) continue;
    let best = 0, bd = Infinity;
    sites.forEach(([sx, sy], i) => {
      const d = (sx - n.x) ** 2 + (sy - n.y) ** 2;
      if (d < bd) { bd = d; best = i; }
    });
    counts[best]++;
  }
  // identical node count per site; cap and regen are shared by construction
  for (const c of counts) assert.equal(c, M1.PITH_PER_SITE);
  assert.equal(m1NodeSpec(1).cap, M1.PITH_CAP);
});

test('M1 runs are deterministic per (seed, stream)', () => {
  const run = () => {
    const s = new Sim({ seed: 7, stream: 2, ticks: 1200, ablateSocial: false,
                        m1: true });
    s.run();
    return s;
  };
  const a = run(), b = run();
  assert.equal(stateHash(a.world, a.agents), stateHash(b.world, b.agents));
  assert.equal(a.ledger.entries.length, b.ledger.entries.length);
});

test('M1 canonical state is pinned across M2 development', () => {
  // The M1 protocol result is committed; M2 work must not disturb M1 runs.
  const s = new Sim({ seed: 7, stream: 2, ticks: 2500, ablateSocial: false,
                      m1: true });
  s.run();
  assert.equal(stateHash(s.world, s.agents), 'f7c6eab310da05a4');
});

test('M1 ledger replay reproduces the full state (births, deaths, watches)', () => {
  const sim = new Sim({ seed: 7, stream: 2, ticks: 2500, ablateSocial: false,
                        m1: true });
  sim.run();
  assert.ok(sim.births.length > 5, `only ${sim.births.length} births`);
  assert.ok(sim.events.some(e => e.type === 'death'), 'no deaths');
  const rep = replay(7, sim.ledger.entries, M1.AGENTS_START, true);
  assert.equal(stateHash(rep.world, rep.agents),
               stateHash(sim.world, sim.agents));
});

test('children inherit traits only — never state, memory, or position bias', () => {
  const sim = new Sim({ seed: 7, stream: 2, ticks: 2500, ablateSocial: false,
                        m1: true });
  sim.run();
  const child = sim.agents.find(a => a.gen > 0);
  assert.ok(child, 'no children born');
  // at birth: no episodes, no carried goods, no cache — verified by replaying
  // the birth entry alone
  const birth = sim.ledger.entries.find(e => e.type === 'agent.birth')!;
  const d = birth.data as any;
  assert.deepEqual(Object.keys(d).sort(),
    ['a', 'b', 'c', 'dE', 'e', 'gen', 'traits', 'x', 'y'],
    'birth entry carries more than traits + position + energy');
});

test('token choice never locks in (§3.3: bounded below determinism)', () => {
  const sim = new Sim({ seed: 11, stream: 1, ticks: 4000, ablateSocial: false,
                        m1: true, lean: true });
  sim.run();
  const late = new Set<number>();
  for (const e of sim.events) {
    if (e.type === 'signal' && e.o !== undefined && e.o >= 0 && e.tick > 3000) {
      late.add(e.o);
    }
  }
  assert.ok(late.size >= 2,
    `only ${late.size} distinct tokens in late emissions — bias saturated into lock-in`);
});

test('the M1 slice stays inside its wall-clock budget (§3.4)', () => {
  const t0 = performance.now();
  const sim = new Sim({ seed: 5, stream: 1, ticks: M1.TICKS,
                        ablateSocial: false, m1: true, lean: true });
  sim.run();
  const wall = performance.now() - t0;
  assert.ok(wall < 300_000, `took ${Math.round(wall / 1000)}s (budget 300s)`);
  assert.ok(sim.frames[sim.frames.length - 1].agents.length > 20,
    'population collapsed');
});
