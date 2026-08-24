import { Sim } from '../engine/engine.js';
import { describe } from './describe.js';
import { parseArgs } from './run.js';

/**
 * Causal trace CLI (§4.1): re-run a seed deterministically, pick an event,
 * and expand it backward into the tree of causes that produced it.
 *
 * Usage:
 *   node dist/cli/trace.js [--seed N] [--stream N] [--event <ledger id>]
 *   node dist/cli/trace.js --last-give        # trace the final gift of the run
 *   node dist/cli/trace.js --gives 5          # trace the last 5 gifts
 */
const argv = process.argv.slice(2);
const cfg = parseArgs(argv);
const sim = new Sim(cfg);
sim.run();

const ids: number[] = [];
const evIdx = argv.indexOf('--event');
if (evIdx >= 0) {
  ids.push(Number(argv[evIdx + 1]));
} else {
  const n = argv.includes('--gives') ? Number(argv[argv.indexOf('--gives') + 1]) : 1;
  const gives = sim.events.filter(e => e.type === 'give');
  for (const e of gives.slice(-n)) ids.push(e.ledger);
  if (ids.length === 0) {
    console.log('no gifts occurred in this run');
    process.exit(0);
  }
}

for (const id of ids) {
  const tree = sim.ledger.trace(id, 9);
  if (!tree) { console.error(`no ledger entry ${id}`); continue; }
  console.log('\nWHY DID THIS HAPPEN?\n');
  console.log(sim.ledger.format(tree, describe));
}
console.log(`\n(${sim.ledger.entries.length} ledger entries; ` +
  `every line above is attributed to world rule, agent decision, ` +
  `stochastic event, or player intervention — §4.1)`);
