// Shared league helpers: indexes, roster caches, persistence sink, news, calendar.

import type { BoxScore, Coach, Conference, League, NewsItem, NewsKind, Player, SeasonArchive, Team } from "./types";
import { Rng } from "./rng";

// ---------------- persistence sink ----------------
// The engine never reads IndexedDB. Data that leaves memory (box scores,
// players who are done with college, finished seasons) is pushed here and
// the UI layer flushes it to the database.
export interface Sink {
  box(lid: string, b: BoxScore): void;
  archivePlayer(lid: string, p: Player): void;
  archiveSeason(lid: string, a: SeasonArchive): void;
}

const memorySink: Sink & { boxes: BoxScore[]; players: Player[]; seasons: SeasonArchive[] } = {
  boxes: [],
  players: [],
  seasons: [],
  box(_l, b) {
    if (this.boxes.length > 2000) this.boxes.shift();
    this.boxes.push(b);
  },
  archivePlayer(_l, p) {
    this.players.push(p);
  },
  archiveSeason(_l, a) {
    this.seasons.push(a);
  },
};
let sink: Sink = memorySink;
export function setSink(s: Sink) {
  sink = s;
}
export function getSink(): Sink {
  return sink;
}
export function getMemorySink() {
  return memorySink;
}

// ---------------- RNG bound to league state ----------------
const rngs = new WeakMap<League, Rng>();
export function rngOf(L: League): Rng {
  let r = rngs.get(L);
  if (!r) {
    r = new Rng(L.rng);
    rngs.set(L, r);
  }
  return r;
}
/** Write the RNG state back into the league before saving. */
export function syncRng(L: League) {
  const r = rngs.get(L);
  if (r) L.rng = r.s;
}

// ---------------- indexes ----------------
interface Idx {
  players: Map<number, Player>;
  teams: Map<number, Team>;
  coaches: Map<number, Coach>;
  rosters: Map<number, Player[]> | null;
}
const rosterVersions = new WeakMap<League, number>();
/** Incremented whenever any roster changes; caches key off it. */
export function rosterVersion(L: League): number {
  return rosterVersions.get(L) ?? 0;
}
function bumpRosters(L: League) {
  rosterVersions.set(L, (rosterVersions.get(L) ?? 0) + 1);
}
const idxs = new WeakMap<League, Idx>();

function idx(L: League): Idx {
  let i = idxs.get(L);
  if (!i) {
    i = {
      players: new Map(L.players.map((p) => [p.id, p])),
      teams: new Map(L.teams.map((t) => [t.id, t])),
      coaches: new Map(L.coaches.map((c) => [c.id, c])),
      rosters: null,
    };
    idxs.set(L, i);
  }
  return i;
}

export function reindex(L: League) {
  idxs.delete(L);
}

export function player(L: League, pid: number): Player | undefined {
  return idx(L).players.get(pid);
}
export function team(L: League, tid: number): Team {
  const t = idx(L).teams.get(tid);
  if (!t) throw new Error(`no team ${tid}`);
  return t;
}
export function teamMaybe(L: League, tid: number | null | undefined): Team | undefined {
  if (tid === null || tid === undefined) return undefined;
  return idx(L).teams.get(tid);
}
export function conference(L: League, cid: number): Conference {
  return L.conferences[cid];
}
export function conferenceOf(L: League, tid: number): Conference {
  return L.conferences[team(L, tid).cid];
}
export function coach(L: League, cid: number): Coach | undefined {
  return idx(L).coaches.get(cid);
}
export function coachOf(L: League, tid: number): Coach | undefined {
  return coach(L, team(L, tid).coachId);
}
export function userTeam(L: League): Team {
  return team(L, L.userTid);
}

export function addPlayer(L: League, p: Player) {
  L.players.push(p);
  const i = idx(L);
  i.players.set(p.id, p);
  i.rosters = null;
  bumpRosters(L);
}
export function addCoach(L: League, c: Coach) {
  L.coaches.push(c);
  idx(L).coaches.set(c.id, c);
}

/** Remove players from memory (after archiving them). */
export function removePlayers(L: League, ids: Set<number>) {
  if (!ids.size) return;
  L.players = L.players.filter((p) => !ids.has(p.id));
  const i = idx(L);
  for (const id of ids) i.players.delete(id);
  i.rosters = null;
  bumpRosters(L);
}

export function rostersDirty(L: League) {
  idx(L).rosters = null;
  bumpRosters(L);
}

/** Active players on each team's roster (including redshirts and injured). */
export function rosters(L: League): Map<number, Player[]> {
  const i = idx(L);
  if (!i.rosters) {
    const m = new Map<number, Player[]>();
    for (const t of L.teams) m.set(t.id, []);
    for (const p of L.players) {
      if (p.status === "active" && p.tid !== null) m.get(p.tid)?.push(p);
    }
    i.rosters = m;
  }
  return i.rosters;
}
export function roster(L: League, tid: number): Player[] {
  return rosters(L).get(tid) ?? [];
}

export function nextPid(L: League): number {
  return L.nextPid++;
}

// ---------------- calendar ----------------
export const REG_DAYS = 126; // regular season days 0..125
export const CT_START = 126; // conference tournaments
export const SELECTION_DAY = 132;

/** First game day of a season: the first Monday on/after Nov 2. */
export function seasonStart(season: number): Date {
  const d = new Date(Date.UTC(season, 10, 2));
  while (d.getUTCDay() !== 1) d.setUTCDate(d.getUTCDate() + 1);
  return d;
}
export function dayDate(season: number, day: number): Date {
  const d = seasonStart(season);
  d.setUTCDate(d.getUTCDate() + day);
  return d;
}
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
export function dayLabel(season: number, day: number): string {
  const d = dayDate(season, day);
  return `${MONTHS[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
}
export function shortDayLabel(season: number, day: number): string {
  const d = dayDate(season, day);
  return `${MONTHS[d.getUTCMonth()]} ${d.getUTCDate()}`;
}
export function seasonLabel(season: number): string {
  return `${season}-${String((season + 1) % 100).padStart(2, "0")}`;
}

export const PHASE_LABEL: Record<League["phase"], string> = {
  preseason: "Preseason",
  regular: "Regular Season",
  confTourney: "Conference Tournaments",
  selection: "Selection Sunday",
  ncaa: "Postseason",
  seasonEnd: "Season Review",
  carousel: "Coaching Carousel",
  draft: "Draft & Departures",
  portal: "Transfer Portal",
  signing: "Signing Day",
};

export function currentDateLabel(L: League): string {
  switch (L.phase) {
    case "preseason":
      return `Preseason ${seasonLabel(L.season)}`;
    case "regular":
    case "confTourney":
    case "selection":
    case "ncaa":
      return dayLabel(L.season, L.day);
    case "seasonEnd":
      return `April ${L.season + 1}`;
    case "carousel":
      return `April ${L.season + 1}`;
    case "draft":
      return `June ${L.season + 1}`;
    case "portal":
      return `Portal window ${L.portalRound}/4 · ${L.season + 1}`;
    case "signing":
      return `May ${L.season + 1}`;
  }
}

// ---------------- news ----------------
export function addNews(
  L: League,
  kind: NewsKind,
  text: string,
  o: { tid?: number; pid?: number; gid?: number; user?: boolean } = {},
): NewsItem {
  const item: NewsItem = {
    id: L.nextNid++,
    season: L.season,
    day: L.day,
    dateLabel: currentDateLabel(L),
    kind,
    text,
    tid: o.tid,
    pid: o.pid,
    gid: o.gid,
    read: false,
    user: o.user ?? (o.tid === L.userTid),
  };
  L.news.unshift(item);
  if (L.news.length > 600) {
    // keep all user news for a while; prune old league news first
    const keep = L.news.filter((n, i) => i < 400 || (n.user && n.season >= L.season - 1));
    L.news = keep.slice(0, 600);
  }
  return item;
}

export function playerName(p: { first: string; last: string }): string {
  return `${p.first} ${p.last}`;
}
