import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Sim } from '../engine/engine.js';
import { stateHash } from '../engine/replay.js';

/**
 * Predictable rules, unpredictable consequences (§3.4): every run must be a
 * pure function of (seed, stream). No wall clock, no Math.random.
 */

test('same seed + same stream → identical world, bit for bit', () => {
  const a = new Sim({ seed: 7, stream: 3, ticks: 400, ablateSocial: false });
  const b = new Sim({ seed: 7, stream: 3, ticks: 400, ablateSocial: false });
  a.run(); b.run();
  assert.equal(stateHash(a.world, a.agents), stateHash(b.world, b.agents));
  assert.equal(a.ledger.entries.length, b.ledger.entries.length);
  assert.deepEqual(a.events, b.events);
});

test('same seed + different stream → same map, different history', () => {
  const a = new Sim({ seed: 7, stream: 1, ticks: 400, ablateSocial: false });
  const b = new Sim({ seed: 7, stream: 2, ticks: 400, ablateSocial: false });
  // identical worldgen…
  assert.deepEqual(a.world.nodes, b.world.nodes);
  assert.deepEqual(a.agents.map(x => x.traits), b.agents.map(x => x.traits));
  a.run(); b.run();
  // …divergent trajectories
  assert.notEqual(stateHash(a.world, a.agents), stateHash(b.world, b.agents));
});
