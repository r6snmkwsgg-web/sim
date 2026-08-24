import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Sim } from '../engine/engine.js';

/**
 * The veil (§2.2): agents receive structured percepts — ids, quantities,
 * coordinates — never a word for a thing they have not named. Resource
 * kinds are integers; the display names (thren, pith, osk) exist only in
 * the viewer and the docs. If someone leaks a human-language label into the
 * percept schema, this test is the tripwire.
 */

const ALLOWED_KEYS = new Set([
  'tick', 'self', 'x', 'y', 'energy', 'health', 'carried', 'cached', 'atmos',
  'nodes', 'k', 'q', 'open', 'agents', 'id', 'band', 'load', 'signals',
  'from', 'mode', 'age', 'caches', 'owner', 'spills',
]);
const FORBIDDEN = /thren|pith|osk|salt|wood|iron|grain|food|berry|stone|gold|winter|summer|season|north|south|east|west/i;

test('percepts contain only schema keys and no human-language names', () => {
  const sim = new Sim({ seed: 11, stream: 1, ticks: 300, ablateSocial: false });
  sim.run();
  let checked = 0;
  for (const a of sim.agents) {
    if (!a.alive) continue;
    const pc = sim.percept(a, sim.world.tick);
    const json = JSON.stringify(pc);
    assert.ok(!FORBIDDEN.test(json),
      `percept for agent ${a.id} leaks a human-language name: ${json.slice(0, 200)}`);
    walk(pc, (key) => {
      assert.ok(ALLOWED_KEYS.has(key),
        `percept for agent ${a.id} has unexpected key '${key}'`);
    });
    checked++;
  }
  assert.ok(checked > 0, 'no living agents to check');
});

function walk(v: unknown, onKey: (k: string) => void): void {
  if (Array.isArray(v)) { for (const x of v) walk(x, onKey); return; }
  if (v && typeof v === 'object') {
    for (const [k, x] of Object.entries(v)) { onKey(k); walk(x, onKey); }
  }
}
