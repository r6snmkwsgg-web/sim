import type { Game, League, Team } from "./types";
import { Rng } from "./rng";
import { rngOf } from "./core";

const CONF_START = 49;
const CONF_END = 124;
const NC_SLOTS = [0, 3, 7, 10, 14, 17, 21, 24, 28, 31, 35, 38, 42, 45];
// Thanksgiving-week tournaments, played on neutral floors
const MTE_SLOTS = new Set([17, 21, 24]);
// early December challenge series and the holiday showcases: programs schedule their peers
const MARQUEE_SLOTS = new Set([28, 38]);
const MTE_NAMES = [
  "Maui Invitational", "Battle 4 Atlantis", "Players Era Festival", "Las Vegas Invitational", "Charleston Classic",
  "Legends Classic", "Empire Classic", "Fort Myers Tip-Off", "Arizona Tip-Off", "Baha Mar Championship", "ESPN Events Invitational",
];
const SMALL_MTE_NAMES = [
  "Cancun Challenge", "Paradise Jam", "Cayman Islands Classic", "Jamaica Classic", "Myrtle Beach Invitational",
  "Gulf Coast Showcase", "Hall of Fame Tip-Off", "Sunshine Slam", "Emerald Coast Classic", "Diamond Head Classic",
];
const SHOWCASE_NAMES = ["Champions Classic", "CBS Sports Classic", "Jimmy V Classic", "Holiday Hoopsgiving", "Hall of Fame Series", "Basketball Hall of Fame Showcase"];

type Pair = [number, number];

/** Circle-method round robin. Returns rounds of pairs (indices). */
function roundRobin(n: number): Pair[][] {
  const ids = Array.from({ length: n % 2 === 0 ? n : n + 1 }, (_, i) => i);
  const m = ids.length;
  const rounds: Pair[][] = [];
  for (let r = 0; r < m - 1; r++) {
    const round: Pair[] = [];
    for (let i = 0; i < m / 2; i++) {
      const a = ids[i];
      const b = ids[m - 1 - i];
      if (a < n && b < n) round.push(r % 2 === 0 ? [a, b] : [b, a]);
    }
    rounds.push(round);
    // rotate all but the first
    ids.splice(1, 0, ids.pop()!);
  }
  return rounds;
}

/** Greedy edge coloring of a pair list into rounds (each team once per round). */
function colorRounds(pairs: Pair[], rng: Rng): Pair[][] {
  const rounds: { pairs: Pair[]; used: Set<number> }[] = [];
  const order = rng.shuffle(pairs.slice());
  for (const p of order) {
    let placed = false;
    for (const r of rounds) {
      if (!r.used.has(p[0]) && !r.used.has(p[1])) {
        r.pairs.push(p);
        r.used.add(p[0]);
        r.used.add(p[1]);
        placed = true;
        break;
      }
    }
    if (!placed) rounds.push({ pairs: [p], used: new Set(p) });
  }
  return rounds.map((r) => r.pairs);
}

function conferenceRounds(n: number, games: number, rng: Rng): Pair[][] {
  const g = Math.min(games, 2 * (n - 1));
  const rr = roundRobin(n);
  if (g >= 2 * (n - 1)) {
    // full double round robin, second half mirrored
    const second = rr.map((round) => round.map(([a, b]) => [b, a] as Pair));
    return [...rr, ...second];
  }
  if (g >= n - 1) {
    let k = g - (n - 1);
    if ((n * k) % 2 === 1) k -= 1;
    const extras: Pair[] = [];
    // k-regular circulant graph for rematches
    for (let d = 1; d <= Math.floor(k / 2); d++) {
      for (let i = 0; i < n; i++) extras.push([i, (i + d) % n]);
    }
    if (k % 2 === 1) for (let i = 0; i < n / 2; i++) extras.push([i, i + n / 2]);
    const extraRounds = colorRounds(extras, rng);
    // interleave extra rounds into the second half of the conference season
    const out: Pair[][] = rr.slice();
    for (const er of extraRounds) {
      const pos = rng.int(Math.floor(out.length / 2), out.length);
      out.splice(pos, 0, er);
    }
    return out;
  }
  // fewer games than opponents: G-regular subset
  const pairs: Pair[] = [];
  let k = g;
  if ((n * k) % 2 === 1) k -= 1;
  for (let d = 1; d <= Math.floor(k / 2); d++) for (let i = 0; i < n; i++) pairs.push([i, (i + d) % n]);
  if (k % 2 === 1) for (let i = 0; i < n / 2; i++) pairs.push([i, i + n / 2]);
  return colorRounds(pairs, rng);
}

export function generateSchedule(L: League): Game[] {
  const rng = rngOf(L);
  const games: Game[] = [];
  const confCount = new Map<number, number>();
  const homeCount = new Map<number, number>();
  for (const t of L.teams) {
    confCount.set(t.id, 0);
    homeCount.set(t.id, 0);
  }
  const mk = (home: number, away: number, day: number, type: Game["type"], neutral = false, event?: string): Game => ({
    id: L.nextGid++,
    season: L.season,
    day,
    home,
    away,
    neutral,
    type,
    played: false,
    hs: 0,
    as: 0,
    ot: 0,
    event,
  });

  // --- conference games ---
  for (const c of L.conferences) {
    const members = rng.shuffle(L.teams.filter((t) => t.cid === c.id).map((t) => t.id));
    const n = members.length;
    if (n < 2) continue;
    const rounds = conferenceRounds(n, c.confGames, rng);
    const R = rounds.length;
    const span = CONF_END - CONF_START;
    // track pair meetings to alternate home/away for rematches
    const met = new Map<string, number>();
    rounds.forEach((round, ri) => {
      const day = Math.round(CONF_START + (R === 1 ? span : (span * ri) / (R - 1)));
      for (const [ia, ib] of round) {
        let a = members[ia];
        let b = members[ib];
        const key = a < b ? `${a}-${b}` : `${b}-${a}`;
        const prevHome = met.get(key);
        if (prevHome !== undefined) {
          // rematch: the other team hosts
          if (prevHome === a) [a, b] = [b, a];
        } else if ((homeCount.get(a) ?? 0) > (homeCount.get(b) ?? 0) + 1) {
          [a, b] = [b, a];
        }
        met.set(key, a);
        homeCount.set(a, (homeCount.get(a) ?? 0) + 1);
        confCount.set(a, (confCount.get(a) ?? 0) + 1);
        confCount.set(b, (confCount.get(b) ?? 0) + 1);
        games.push(mk(a, b, day, "conf"));
      }
    });
  }

  // --- non-conference games ---
  const need = new Map<number, number>();
  for (const t of L.teams) {
    const target = rng.int(30, 32);
    need.set(t.id, Math.max(8, Math.min(NC_SLOTS.length, target - (confCount.get(t.id) ?? 0))));
  }
  const played = new Set<string>();
  const byId = new Map(L.teams.map((t) => [t.id, t]));
  const mteNames = rng.shuffle(MTE_NAMES.slice());
  const smallNames = rng.shuffle(SMALL_MTE_NAMES.slice());
  const showNames = rng.shuffle(SHOWCASE_NAMES.slice());
  let mteIdx = 0;
  let smallIdx = 0;
  let showIdx = 0;
  NC_SLOTS.forEach((day, si) => {
    const slotsLeft = NC_SLOTS.length - si;
    const avail = L.teams
      .filter((t) => (need.get(t.id) ?? 0) > 0)
      .map((t) => ({ t, urg: (need.get(t.id) ?? 0) / slotsLeft + rng.next() * 0.3 }))
      .filter((x) => x.urg >= 0.99 || rng.next() < x.urg)
      .sort((a, b) => b.urg - a.urg)
      .map((x) => x.t);
    const busy = new Set<number>();
    for (const a of avail) {
      if (busy.has(a.id)) continue;
      // find an opponent: different conference, not yet played, also available
      const peerSlot = MTE_SLOTS.has(day) || (MARQUEE_SLOTS.has(day) && a.prestige >= 50);
      let best: Team | null = null;
      let bestScore = -Infinity;
      for (let tries = 0; tries < 18; tries++) {
        const b = avail[rng.int(0, avail.length - 1)];
        if (b.id === a.id || busy.has(b.id) || b.cid === a.cid) continue;
        const key = a.id < b.id ? `${a.id}-${b.id}` : `${b.id}-${a.id}`;
        if (played.has(key)) continue;
        let score = rng.next() + (need.get(b.id) ?? 0) / slotsLeft;
        // tournaments and marquee dates bring programs of a similar level together
        if (peerSlot) score += 1.6 * (1 - Math.min(1, Math.abs(a.prestige - b.prestige) / 30));
        if (score > bestScore) {
          bestScore = score;
          best = b;
        }
      }
      if (!best) continue;
      const b = best;
      busy.add(a.id);
      busy.add(b.id);
      played.add(a.id < b.id ? `${a.id}-${b.id}` : `${b.id}-${a.id}`);
      need.set(a.id, (need.get(a.id) ?? 0) - 1);
      need.set(b.id, (need.get(b.id) ?? 0) - 1);
      const ta = byId.get(a.id)!;
      const tb = byId.get(b.id)!;
      const bothStrong = ta.prestige >= 55 && tb.prestige >= 55;
      if (MTE_SLOTS.has(day) && rng.chance(bothStrong ? 0.95 : 0.6)) {
        const big = Math.max(ta.prestige, tb.prestige) >= 50;
        const ev = big ? mteNames[mteIdx++ % mteNames.length] : smallNames[smallIdx++ % smallNames.length];
        games.push(mk(a.id, b.id, day, "nc", true, ev));
        continue;
      }
      if (day === 38 && bothStrong && rng.chance(0.5)) {
        games.push(mk(a.id, b.id, day, "nc", true, showNames[showIdx++ % showNames.length]));
        continue;
      }
      const pHome = Math.max(0.15, Math.min(0.88, 0.5 + (ta.prestige - tb.prestige) / 110));
      if (rng.next() < pHome) games.push(mk(a.id, b.id, day, "nc"));
      else games.push(mk(b.id, a.id, day, "nc"));
    }
  });
  games.sort((x, y) => x.day - y.day || x.id - y.id);
  return games;
}
