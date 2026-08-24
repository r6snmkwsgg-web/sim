import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Sim } from '../engine/engine.js';
import { replay, stateHash } from '../engine/replay.js';

/**
 * §4.1's guarantee — "no exceptions, no unattributed mutations" — enforced
 * by reconstruction: replaying the ledger from the initial seed must
 * reproduce the final state exactly, memory stores and social records
 * included. Any mutation that bypasses the ledger breaks this.
 */

for (const ablate of [false, true]) {
  test(`ledger replay reproduces the full state (ablateSocial=${ablate})`, () => {
    const sim = new Sim({ seed: 23, stream: 5, ticks: 800, ablateSocial: ablate });
    sim.run();
    const rep = replay(23, sim.ledger.entries);
    assert.equal(stateHash(rep.world, rep.agents),
                 stateHash(sim.world, sim.agents));
  });
}

test('every ledger entry carries a cause attribution', () => {
  const sim = new Sim({ seed: 23, stream: 5, ticks: 300, ablateSocial: false });
  sim.run();
  const kinds = new Set(['world', 'agent', 'stochastic', 'player']);
  for (const e of sim.ledger.entries) {
    assert.ok(kinds.has(e.kind), `entry ${e.id} has kind '${e.kind}'`);
    for (const c of e.causes) {
      assert.ok(c >= 0 && c < e.id,
        `entry ${e.id} cites cause ${c}, which is not an earlier entry`);
    }
  }
});
