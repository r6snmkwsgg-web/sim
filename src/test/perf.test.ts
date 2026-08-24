import { test } from 'node:test';
import assert from 'node:assert/strict';
import { P } from '../core/params.js';
import { Sim } from '../engine/engine.js';

/** §5: 2,000 ticks, 20 agents, full causal ledger — under 30 seconds. */

test('the vertical slice runs 2,000 ticks in under 30 seconds', () => {
  const t0 = performance.now();
  const sim = new Sim({ seed: 11, stream: 1, ticks: P.TICKS, ablateSocial: false });
  sim.run();
  const wall = performance.now() - t0;
  assert.ok(wall < 30_000, `took ${Math.round(wall)}ms`);
  assert.equal(sim.world.tick, P.TICKS);
  assert.ok(sim.ledger.entries.length > P.TICKS * 3,
    'ledger suspiciously sparse — attribution is probably missing');
});
