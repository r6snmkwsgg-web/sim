import { test } from 'node:test';
import assert from 'node:assert/strict';
import { P } from '../core/params.js';
import { Sim } from '../engine/engine.js';
import { analyze } from '../engine/metrics.js';

/**
 * The Milestone-0 target phenomenon (§5): reciprocal exchange without a
 * trade mechanic — held to the §4.2 criteria.
 *
 *  1. Unscripted   — there is no trade() action; grep the codebase.
 *  2. Traceable    — checked structurally here: a gift's causal chain must
 *                    pass through social memory into an earlier counter-gift.
 *  3. Reproducible — the multi-stream sweep (npm run sweep); spot-checked
 *                    here on a second stream.
 *  4. Non-retrievable — n/a at M0 (no pretrained model to retrieve from);
 *                    the ablated control plays the analogous role: an agent
 *                    without social memory does not produce the pattern.
 */

const CANON = { seed: 11, stream: 1, ticks: P.TICKS };

function run(ablate: boolean, stream = CANON.stream) {
  const sim = new Sim({ ...CANON, stream, ablateSocial: ablate });
  sim.run();
  return { sim, report: analyze(sim.frames, sim.events, P.N_AGENTS) };
}

test('reciprocal exchange emerges on the canonical seed', () => {
  const { report } = run(false);
  assert.ok(report.totalGives >= 200, `only ${report.totalGives} gives`);
  assert.ok(report.contingency >= 2.0,
    `contingency ${report.contingency} — giving is not conditioned on prior givers`);
  assert.ok(report.rateCorrelation >= 0.5,
    `rate correlation ${report.rateCorrelation} — no pairwise reciprocity`);
  assert.ok(report.reciprocalDyads >= 10,
    `only ${report.reciprocalDyads} reciprocal dyads`);
  assert.ok(report.withholding < 1.0,
    `withholding ${report.withholding} — transgressors are not being refused`);
});

test('…and again on an independent noise stream (reproducible-in-kind)', () => {
  const { report } = run(false, 9);
  assert.ok(report.contingency >= 1.5, `contingency ${report.contingency}`);
  assert.ok(report.rateCorrelation >= 0.4,
    `rate correlation ${report.rateCorrelation}`);
});

test('freezing social memory destroys the pattern (the §5 control)', () => {
  const { report } = run(true);
  // same utility function, same world, same noise stream — only the memory
  // writes differ. If the contingency survives this, it was baked into the
  // utility shape and the emergence claim is void.
  assert.ok(!Number.isFinite(report.contingency) || report.contingency <= 1.5,
    `ablated contingency ${report.contingency} — reciprocity did NOT come from social memory`);
  assert.ok(!Number.isFinite(report.rateCorrelation) || report.rateCorrelation <= 0.35,
    `ablated rate correlation ${report.rateCorrelation}`);
});

test('a gift is causally traceable to an earlier counter-gift (§4.2.2)', () => {
  const { sim } = run(false);
  const gives = sim.events.filter(e => e.type === 'give');
  // find a gift whose ancestry passes: decision → mem.trust → earlier act.give
  // where that earlier gift ran in the opposite direction
  let traced = 0;
  for (const g of gives.slice(-200)) {
    const give = sim.ledger.get(g.ledger)!;
    const decision = give.causes.map(c => sim.ledger.get(c)!)
      .find(e => e?.type === 'decision');
    if (!decision) continue;
    const trust = decision.causes.map(c => sim.ledger.get(c)!)
      .find(e => e?.type === 'mem.trust');
    if (!trust) continue;
    // walk the trust-update chain looking for a counter-gift
    const stack = [...trust.causes];
    const seen = new Set<number>();
    while (stack.length) {
      const id = stack.pop()!;
      if (seen.has(id)) continue;
      seen.add(id);
      const e = sim.ledger.get(id);
      if (!e) continue;
      if (e.type === 'act.give' &&
          (e.data as any).a === g.b && (e.data as any).b === g.a) {
        traced++;
        break;
      }
      if (e.type === 'mem.trust' || e.type === 'act.give' || e.type === 'mem.ep') {
        stack.push(...e.causes);
      }
    }
    if (traced > 0) break;
  }
  assert.ok(traced > 0,
    'no gift could be traced through social memory to a counter-gift');
});
