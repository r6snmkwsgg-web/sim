import type { LedgerEntry } from '../core/types.js';

/** Human-readable one-liner for a ledger entry (trace CLI + viewer export). */
export function describe(e: LedgerEntry): string {
  const d = e.data as any;
  switch (e.type) {
    case 'decision': {
      const top = (d.top as { intent: string; score: number }[] | undefined)
        ?.map(t => `${t.intent}=${t.score}`).join(' ');
      return `agent ${e.subject} decided ${d.intent} (score ${d.score}; ` +
             `drives s=${d.w?.survival} f=${d.w?.safety} b=${d.w?.belonging} ` +
             `st=${d.w?.status}${top ? `; top: ${top}` : ''})`;
    }
    case 'act.move': return `agent ${d.a} moved to (${d.x},${d.y}) [${d.intent}]`;
    case 'act.follow': return `agent ${d.a} followed agent ${d.b} to (${d.x},${d.y})`;
    case 'act.gather': return d.src === 'n'
      ? `agent ${d.a} gathered ${f(d.g)} of r${d.k} from node ${d.n}`
      : `agent ${d.a} scavenged ${f(d.g)} of r${d.k} from a spill`;
    case 'act.gather-fail': return d.reason === 'sealed'
      ? `agent ${d.a} tried to gather node ${d.n} — sealed by the atmosphere`
      : `agent ${d.a} found nothing to gather`;
    case 'act.eat': return `agent ${d.a} ate ${f(d.amt)} of r${d.k} (+${f(d.dE)} energy)`;
    case 'act.store': return `agent ${d.a} cached ${f(d.amt)} of r${d.k} at (${d.x},${d.y})`;
    case 'act.give': return `agent ${d.a} GAVE ${f(d.amt)} of r${d.k} to agent ${d.b}`;
    case 'act.take': return `agent ${d.a} TOOK ${f(d.amt)} of r${d.k} from agent ${d.b}`;
    case 'act.withdraw': return `agent ${d.a} withdrew ${f(d.amt)} of r${d.k} from own cache`;
    case 'act.loot': return `agent ${d.a} LOOTED ${f(d.amt)} of r${d.k} from agent ${d.o}'s cache`;
    case 'act.attack': return `agent ${d.a} ATTACKED agent ${d.b} (dmg ${f(d.dmg)})`;
    case 'act.signal': return `agent ${d.a} signalled ${d.mode === 0 ? 'distress' : 'abundance'} at (${d.x},${d.y})`;
    case 'act.rest': return `agent ${d.a} rested`;
    case 'agent.death': return `agent ${d.a} died of ${d.cause} at (${d.x},${d.y})`;
    case 'mem.ep': {
      const ep = d.ep;
      return `agent ${d.a} remembers: ${ep.type}` +
        (ep.who >= 0 ? ` (agent ${ep.who}` +
          (ep.amount ? `, ${f(ep.amount)}${ep.k >= 0 ? ` of r${ep.k}` : ''}` : '') + ')' : '');
    }
    case 'mem.trust':
      return `agent ${d.a}'s trust in agent ${d.b} → ${f(d.tr)} ` +
             `(familiarity ${f(d.fa)}, debt ${f(d.de)})`;
    case 'world.regen': return `resource regrowth`;
    case 'world.decay': return `goods decayed`;
    case 'world.metab': return `metabolism`;
    case 'mem.drift': return `familiarity drift (co-presence)`;
    default: return e.type;
  }
}

function f(v: number): string {
  return typeof v === 'number' ? (Math.round(v * 100) / 100).toString() : String(v);
}
