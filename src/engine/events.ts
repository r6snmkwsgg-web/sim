// Early-season events: the Thanksgiving-week tournaments (Maui, Battle 4 Atlantis and the rest).
// Eight-team events take three days with consolation games, so every team plays three times;
// four-team events take two. All of it counts as nonconference games on neutral floors.

import type { Bracket, BracketGame, League, Team } from "./types";
import { seasonStart } from "./core";
import type { Rng } from "./rng";
import { seedOrder } from "./postseason";

// roughly strongest fields first, like the real ones
const BIG_EVENTS = [
  "Maui Invitational", "Battle 4 Atlantis", "Players Era Festival", "Las Vegas Invitational", "ESPN Events Invitational",
  "Baha Mar Championship", "Empire Classic", "Legends Classic", "Charleston Classic", "Arizona Tip-Off", "Fort Myers Tip-Off",
];
const SMALL_EVENTS = [
  "Cancun Challenge", "Paradise Jam", "Cayman Islands Classic", "Jamaica Classic", "Myrtle Beach Invitational",
  "Gulf Coast Showcase", "Hall of Fame Tip-Off", "Sunshine Slam", "Emerald Coast Classic", "Diamond Head Classic",
];

/** Days from opening night to Thanksgiving: always a Thursday, 17 or 24 days in. */
export function thanksgivingDay(season: number): number {
  const d = new Date(Date.UTC(season, 10, 1));
  while (d.getUTCDay() !== 4) d.setUTCDate(d.getUTCDate() + 1);
  d.setUTCDate(d.getUTCDate() + 21);
  return Math.round((d.getTime() - seasonStart(season).getTime()) / 86400000);
}

function slot(round: number, s: number, extra: Partial<BracketGame> = {}): BracketGame {
  return { slot: s, round, a: null, b: null, sa: null, sb: null, gid: null, winner: null, ...extra };
}

/** Quarterfinal losers play consolation games; everyone finishes with a place from 1 to 8. */
function eightTeam(key: string, name: string, seeds: number[], days: number[]): Bracket {
  const order = seedOrder(8);
  const games: BracketGame[] = [];
  for (let j = 0; j < 4; j++) {
    const s1 = order[2 * j];
    const s2 = order[2 * j + 1];
    games.push(slot(0, j, { a: seeds[s1 - 1], sa: s1, b: seeds[s2 - 1], sb: s2, lose: { round: 1, slot: 10 + (j >> 1), side: (j & 1) as 0 | 1 } }));
  }
  games.push(slot(1, 0, { lose: { round: 2, slot: 10, side: 0 } }));
  games.push(slot(1, 1, { lose: { round: 2, slot: 10, side: 1 } }));
  games.push(slot(1, 10, { label: "Consolation semifinal", win: { round: 2, slot: 11, side: 0 }, lose: { round: 2, slot: 12, side: 0 } }));
  games.push(slot(1, 11, { label: "Consolation semifinal", win: { round: 2, slot: 11, side: 1 }, lose: { round: 2, slot: 12, side: 1 } }));
  games.push(slot(2, 0, { place: 1 }));
  games.push(slot(2, 10, { place: 3, label: "Third place" }));
  games.push(slot(2, 11, { place: 5, label: "Fifth place" }));
  games.push(slot(2, 12, { place: 7, label: "Seventh place" }));
  return { key, name, rounds: ["Quarterfinals", "Semifinals", "Championship"], games, champion: null, runnerUp: null, neutral: true, days };
}

function fourTeam(key: string, name: string, seeds: number[], days: number[]): Bracket {
  const games: BracketGame[] = [
    slot(0, 0, { a: seeds[0], sa: 1, b: seeds[3], sb: 4, lose: { round: 1, slot: 10, side: 0 } }),
    slot(0, 1, { a: seeds[1], sa: 2, b: seeds[2], sb: 3, lose: { round: 1, slot: 10, side: 1 } }),
    slot(1, 0, { place: 1 }),
    slot(1, 10, { place: 3, label: "Third place" }),
  ];
  return { key, name, rounds: ["Semifinals", "Championship"], games, champion: null, runnerUp: null, neutral: true, days };
}

/**
 * Invite the fields and set the dates. Events fill in tiers, so programs meet their peers (Maui is
 * full of power programs, the Cancun Challenge isn't), with no two teams from one conference in the
 * same event. The user's program always gets an invitation.
 */
export function createEvents(L: League, rng: Rng): Bracket[] {
  const T = thanksgivingDay(L.season);
  const ranked = L.teams
    .map((t) => ({ t, s: t.prestige + rng.normal(0, 9) }))
    .sort((a, b) => b.s - a.s)
    .map((x) => x.t);
  const used = new Set<number>();
  const fill = (count: number, size: number, pool: Team[]): Team[][] => {
    const fields: Team[][] = [];
    for (let i = 0; i < count; i++) {
      const f: Team[] = [];
      for (const t of pool) {
        if (f.length === size) break;
        if (used.has(t.id) || f.some((x) => x.cid === t.cid)) continue;
        used.add(t.id);
        f.push(t);
      }
      if (f.length === size) fields.push(f);
    }
    return fields;
  };
  const big = fill(BIG_EVENTS.length, 8, ranked.slice(0, 150));
  // the smaller events draw mid- and low-majors from all over
  const rest = ranked
    .slice(95)
    .map((t) => ({ t, s: t.prestige + rng.normal(0, 18) }))
    .sort((a, b) => b.s - a.s)
    .map((x) => x.t);
  const small = fill(SMALL_EVENTS.length, 4, rest);
  const user = L.teams.find((t) => t.id === L.userTid)!;
  if (!used.has(user.id)) {
    // take the spot of the closest-level program in a field without a conference rival
    let best: { f: Team[]; i: number } | null = null;
    let bestD = Infinity;
    for (const f of [...big, ...small]) {
      for (let i = 0; i < f.length; i++) {
        if (f.some((x, j) => j !== i && x.cid === user.cid)) continue;
        const d = Math.abs(f[i].prestige - user.prestige);
        if (d < bestD) {
          bestD = d;
          best = { f, i };
        }
      }
    }
    if (best) best.f[best.i] = user;
  }
  const seeds = (f: Team[]) => f.slice().sort((a, b) => b.prestige - a.prestige).map((t) => t.id);
  // the strongest fields go to the biggest names, give or take a spot
  const nearly = (names: string[]) => names.map((n, i) => ({ n, k: i + rng.uniform(-1.5, 1.5) })).sort((a, b) => a.k - b.k).map((x) => x.n);
  const bigNames = nearly(BIG_EVENTS);
  const smallNames = rng.shuffle(SMALL_EVENTS.slice());
  const out: Bracket[] = [];
  big.forEach((f, i) => out.push(eightTeam(`mte:${out.length}`, bigNames[i], seeds(f), i % 2 === 0 ? [T - 3, T - 2, T - 1] : [T, T + 1, T + 2])));
  small.forEach((f, i) => out.push(fourTeam(`mte:${out.length}`, smallNames[i], seeds(f), i % 2 === 0 ? [T - 2, T - 1] : [T + 1, T + 2])));
  return out;
}

/** Each team's event days, and how many games it plays there. */
export function eventCommitments(events: Bracket[]): Map<number, { days: number[]; games: number }> {
  const out = new Map<number, { days: number[]; games: number }>();
  for (const br of events) {
    for (const g of br.games) {
      if (g.round !== 0) continue;
      for (const tid of [g.a, g.b]) if (tid !== null) out.set(tid, { days: br.days, games: br.days.length });
    }
  }
  return out;
}
