// The record book: league-wide and program records for games, seasons and careers.

import type { BoxLine, Game, League, Player, RecordBook, RecordEntry, StatLine } from "./types";
import { careerLine } from "./stats";

export const GAME_STATS: { key: string; label: string; get: (l: BoxLine) => number }[] = [
  { key: "pts", label: "Points", get: (l) => l.pts },
  { key: "reb", label: "Rebounds", get: (l) => l.orb + l.drb },
  { key: "ast", label: "Assists", get: (l) => l.ast },
  { key: "stl", label: "Steals", get: (l) => l.stl },
  { key: "blk", label: "Blocks", get: (l) => l.blk },
  { key: "tpm", label: "3-Pointers Made", get: (l) => l.tpm },
];

export const TOTAL_STATS: { key: string; label: string; get: (s: StatLine) => number; avg?: boolean; minG?: number }[] = [
  { key: "pts", label: "Points", get: (s) => s.pts },
  { key: "reb", label: "Rebounds", get: (s) => s.orb + s.drb },
  { key: "ast", label: "Assists", get: (s) => s.ast },
  { key: "stl", label: "Steals", get: (s) => s.stl },
  { key: "blk", label: "Blocks", get: (s) => s.blk },
  { key: "tpm", label: "3-Pointers Made", get: (s) => s.tpm },
  { key: "ppg", label: "Points Per Game", get: (s) => (s.g ? s.pts / s.g : 0), avg: true, minG: 20 },
  { key: "rpg", label: "Rebounds Per Game", get: (s) => (s.g ? (s.orb + s.drb) / s.g : 0), avg: true, minG: 20 },
  { key: "apg", label: "Assists Per Game", get: (s) => (s.g ? s.ast / s.g : 0), avg: true, minG: 20 },
];

export const CAREER_EXTRA = [{ key: "g", label: "Games Played", get: (s: StatLine) => s.g }];

export const TEAM_SEASON_STATS = [
  { key: "w", label: "Wins" },
  { key: "wpct", label: "Win Percentage" },
  { key: "ppg", label: "Points Per Game" },
  { key: "margin", label: "Scoring Margin" },
];

export function emptyRecordBook(): RecordBook {
  return { game: {}, season: {}, career: {}, teamSeason: {}, program: {}, programSeason: {} };
}

export function insertRecord(list: RecordEntry[], e: RecordEntry, max: number): boolean {
  if (list.length >= max && e.value <= list[list.length - 1].value) return false;
  // replace an existing entry for the same player+season (career/program updates)
  const i = list.findIndex((x) => x.pid === e.pid && x.season === e.season && x.tid === e.tid && x.gid === e.gid);
  if (i >= 0) {
    if (list[i].value >= e.value) return false;
    list.splice(i, 1);
  }
  let pos = list.length;
  while (pos > 0 && list[pos - 1].value < e.value) pos--;
  list.splice(pos, 0, e);
  if (list.length > max) list.length = max;
  return pos < max;
}

function listFor(o: Record<string, RecordEntry[]>, key: string): RecordEntry[] {
  return (o[key] ??= []);
}

export function recordGameLine(L: League, g: Game, tid: number, opp: number, line: BoxLine) {
  const R = L.records;
  for (const st of GAME_STATS) {
    const v = st.get(line);
    if (v <= 0) continue;
    const list = listFor(R.game, st.key);
    if (list.length >= 25 && v <= list[list.length - 1].value) continue;
    insertRecord(list, { pid: line.pid, name: line.name, tid, season: g.season, value: v, gid: g.id, opp }, 25);
  }
}

/** Season-end: single-season records (league and program) and team season records. */
export function recordSeason(L: League) {
  const R = L.records;
  for (const p of L.players) {
    for (const s of p.stats) {
      if (s.season !== L.season || s.g === 0) continue;
      const name = `${p.first} ${p.last}`;
      const prog = (R.programSeason[s.tid] ??= {});
      for (const st of TOTAL_STATS) {
        if (st.minG && s.g < st.minG) continue;
        const v = Math.round(st.get(s) * 10) / 10;
        if (v <= 0) continue;
        const e = { pid: p.id, name, tid: s.tid, season: s.season, value: v };
        insertRecord(listFor(R.season, st.key), e, 25);
        insertRecord(listFor(prog, st.key), e, 10);
      }
    }
  }
  for (const t of L.teams) {
    const s = t.seasons[t.seasons.length - 1];
    if (!s || s.season !== L.season) continue;
    const g = s.w + s.l;
    if (!g) continue;
    const vals: Record<string, number> = {
      w: s.w,
      wpct: Math.round((s.w / g) * 1000) / 1000,
      ppg: Math.round((s.pf / g) * 10) / 10,
      margin: Math.round(((s.pf - s.pa) / g) * 10) / 10,
    };
    for (const k of Object.keys(vals)) {
      insertRecord(listFor(R.teamSeason, k), { pid: -1, name: t.name, tid: t.id, season: s.season, value: vals[k] }, 25);
    }
  }
}

/** When a player leaves college: career records (league and per program). */
export function recordCareer(L: League, p: Player) {
  if (!p.stats.length) return;
  const R = L.records;
  const name = `${p.first} ${p.last}`;
  const lastTid = p.stats[p.stats.length - 1].tid;
  const all = careerLine(p);
  const lastSeason = p.stats[p.stats.length - 1].season;
  for (const st of [...TOTAL_STATS, ...CAREER_EXTRA]) {
    if ("avg" in st && st.avg && all.g < 60) continue;
    const v = Math.round(st.get(all) * 10) / 10;
    if (v <= 0) continue;
    insertRecord(listFor(R.career, st.key), { pid: p.id, name, tid: lastTid, season: lastSeason, value: v }, 25);
  }
  const tids = new Set(p.stats.map((s) => s.tid));
  for (const tid of tids) {
    const line = careerLine(p, tid);
    const prog = (R.program[tid] ??= {});
    for (const st of [...TOTAL_STATS, ...CAREER_EXTRA]) {
      if ("avg" in st && st.avg && line.g < 50) continue;
      const v = Math.round(st.get(line) * 10) / 10;
      if (v <= 0) continue;
      insertRecord(listFor(prog, st.key), { pid: p.id, name, tid, season: lastSeason, value: v }, 10);
    }
  }
}
