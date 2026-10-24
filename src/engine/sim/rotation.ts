import type { Player } from "../types";

const STARTER_MIN = [33, 32, 31, 30, 29];
const BENCH_MIN = [17, 13, 9, 5, 1];

function lineupPenalty(ps: Player[]): number {
  const guards = ps.filter((p) => p.pos === "PG" || p.pos === "SG").length;
  const bigs = ps.filter((p) => p.pos === "PF" || p.pos === "C").length;
  const pgs = ps.filter((p) => p.pos === "PG").length;
  let pen = 0;
  if (guards === 0) pen += 18;
  else if (guards === 1) pen += 3;
  if (guards > 3) pen += 6;
  if (bigs === 0) pen += 12;
  if (bigs > 3) pen += 8;
  if (pgs === 0) pen += 2;
  return pen;
}

/** Best starting five from the available players (brute force over the top 9). */
export function bestStarters(avail: Player[]): Player[] {
  const top = avail.slice().sort((a, b) => b.ovr - a.ovr).slice(0, 9);
  if (top.length <= 5) return top;
  let best: Player[] = top.slice(0, 5);
  let bestScore = -Infinity;
  const n = top.length;
  for (let a = 0; a < n; a++)
    for (let b = a + 1; b < n; b++)
      for (let c = b + 1; c < n; c++)
        for (let d = c + 1; d < n; d++)
          for (let e = d + 1; e < n; e++) {
            const ps = [top[a], top[b], top[c], top[d], top[e]];
            const s = ps.reduce((x, p) => x + p.ovr, 0) - lineupPenalty(ps);
            if (s > bestScore) {
              bestScore = s;
              best = ps;
            }
          }
  return best;
}

export function autoRotation(avail: Player[], depth = 9): { starters: number[]; minutes: Record<number, number> } {
  const starters = bestStarters(avail);
  const sIds = new Set(starters.map((p) => p.id));
  const st = starters.slice().sort((a, b) => b.ovr - a.ovr);
  const bench = avail.filter((p) => !sIds.has(p.id)).sort((a, b) => b.ovr - a.ovr);
  const minutes: Record<number, number> = {};
  st.forEach((p, i) => (minutes[p.id] = STARTER_MIN[i]));
  const benchSlots = Math.max(0, Math.min(depth - 5, bench.length));
  let leftover = 0;
  bench.forEach((p, i) => {
    if (i < benchSlots) minutes[p.id] = BENCH_MIN[i];
    else {
      minutes[p.id] = 0;
      if (i < BENCH_MIN.length) leftover += BENCH_MIN[i];
    }
  });
  // redistribute minutes from unused bench slots to the starters
  for (let i = 0; leftover > 0; i = (i + 1) % Math.max(1, st.length)) {
    if (!st.length) break;
    const p = st[i];
    if (minutes[p.id] < 37) {
      minutes[p.id]++;
      leftover--;
    } else if (st.every((q) => minutes[q.id] >= 37)) break;
  }
  return { starters: starters.map((p) => p.id), minutes };
}

/** Resolve a team's saved rotation against who is actually available. */
export function resolveRotation(
  avail: Player[],
  rot: { auto: boolean; starters: number[]; minutes: Record<number, number> },
): { starters: number[]; minutes: Record<number, number> } {
  if (rot.auto) return autoRotation(avail);
  const ids = new Set(avail.map((p) => p.id));
  const starters = rot.starters.filter((id) => ids.has(id));
  const minutes: Record<number, number> = {};
  let total = 0;
  for (const p of avail) {
    const m = rot.minutes[p.id] ?? 0;
    minutes[p.id] = m;
    total += m;
  }
  if (starters.length < 5) {
    const fill = bestStarters(avail.filter((p) => !starters.includes(p.id)));
    for (const p of fill) {
      if (starters.length >= 5) break;
      starters.push(p.id);
    }
  }
  // missing minutes (injury to a rotation player): give them to available players by OVR
  if (total < 200) {
    const order = avail.slice().sort((a, b) => b.ovr - a.ovr);
    let need = 200 - total;
    let guard = 0;
    while (need > 0 && guard++ < 400) {
      for (const p of order) {
        if (need <= 0) break;
        if (minutes[p.id] < 36) {
          minutes[p.id]++;
          need--;
        }
      }
    }
  }
  return { starters, minutes };
}
