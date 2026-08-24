import type { CauseKind, LedgerEntry } from '../core/types.js';

/**
 * The causal ledger (§4.1).
 *
 * Every state change in the simulation is appended here, attributed to exactly
 * one CauseKind, carrying a payload sufficient to replay the mutation and the
 * ids of the entries that caused it. The replay test (src/test/replay) holds
 * this honest: reconstructing the final world from the ledger alone must
 * reproduce the live simulation bit-for-bit. No unattributed mutations.
 */
export class Ledger {
  entries: LedgerEntry[] = [];

  append(tick: number, kind: CauseKind, type: string, subject: number,
         data: Record<string, unknown>, causes: number[] = []): number {
    const id = this.entries.length;
    this.entries.push({ id, tick, kind, type, subject, data, causes });
    return id;
  }

  get(id: number): LedgerEntry | undefined {
    return this.entries[id];
  }

  /**
   * Expand an event backward into its tree of causes (§4.1).
   * Depth-limited; shared ancestors are visited once and referenced after.
   */
  trace(id: number, maxDepth = 8): TraceNode | null {
    const root = this.entries[id];
    if (!root) return null;
    const seen = new Set<number>();
    const build = (e: LedgerEntry, depth: number): TraceNode => {
      const node: TraceNode = { entry: e, children: [], truncated: false, ref: false };
      if (seen.has(e.id)) { node.ref = true; return node; }
      seen.add(e.id);
      if (depth >= maxDepth) { node.truncated = e.causes.length > 0; return node; }
      for (const cid of e.causes) {
        const c = this.entries[cid];
        if (c) node.children.push(build(c, depth + 1));
      }
      return node;
    };
    return build(root, 0);
  }

  /** Pretty-print a trace tree in the style of the §4.1 example. */
  format(node: TraceNode, describe: (e: LedgerEntry) => string): string {
    const lines: string[] = [];
    const walk = (n: TraceNode, prefix: string, isLast: boolean, isRoot: boolean) => {
      const tag = `[${n.entry.kind}]`;
      const head = isRoot ? '' : prefix + (isLast ? '└ ' : '├ ');
      const suffix = n.ref ? '  (see above)' : n.truncated ? '  …' : '';
      lines.push(`${head}${describe(n.entry)}  t=${n.entry.tick}  ${tag}${suffix}`);
      if (n.ref) return;
      const childPrefix = isRoot ? '' : prefix + (isLast ? '  ' : '│ ');
      n.children.forEach((c, i) =>
        walk(c, childPrefix, i === n.children.length - 1, false));
    };
    walk(node, '', true, true);
    return lines.join('\n');
  }

  toJSONL(): string {
    const out: string[] = new Array(this.entries.length);
    for (let i = 0; i < this.entries.length; i++) {
      out[i] = JSON.stringify(this.entries[i]);
    }
    return out.join('\n') + '\n';
  }
}

export interface TraceNode {
  entry: LedgerEntry;
  children: TraceNode[];
  truncated: boolean;
  ref: boolean;
}
