// Derived data shared by several pages.

import type { Game, League, Player, PlayerSeasonStats } from "../engine/types";
import { roster, team } from "../engine/core";
import { curSeason } from "../engine/play";
import { powerRanks } from "../engine/rankings";
import { confStandings } from "../engine/postseason";
import { winPct } from "../engine/stats";

export function teamGames(L: League, tid: number): Game[] {
  return L.games.filter((g) => g.home === tid || g.away === tid).sort((a, b) => a.day - b.day || a.id - b.id);
}

export function nextGame(L: League, tid: number): Game | undefined {
  return teamGames(L, tid).find((g) => !g.played);
}

export function lastGames(L: League, tid: number, n: number): Game[] {
  return teamGames(L, tid)
    .filter((g) => g.played)
    .slice(-n)
    .reverse();
}

export function gameView(g: Game, tid: number) {
  const home = g.home === tid;
  const us = home ? g.hs : g.as;
  const them = home ? g.as : g.hs;
  const opp = home ? g.away : g.home;
  const loc = g.neutral ? "N" : home ? "H" : "A";
  return { home, us, them, opp, loc, won: us > them, played: g.played };
}

export function seasonStatsOf(p: Player, season: number, tid?: number): PlayerSeasonStats | undefined {
  return p.stats.find((s) => s.season === season && (tid === undefined || s.tid === tid));
}

export function teamLeaders(L: League, tid: number, season = L.season) {
  const ps = roster(L, tid)
    .map((p) => ({ p, s: seasonStatsOf(p, season, tid) }))
    .filter((x): x is { p: Player; s: PlayerSeasonStats } => !!x.s && x.s.g > 0);
  const best = (f: (s: PlayerSeasonStats) => number) => ps.slice().sort((a, b) => f(b.s) / b.s.g - f(a.s) / a.s.g)[0];
  return {
    pts: best((s) => s.pts),
    reb: best((s) => s.orb + s.drb),
    ast: best((s) => s.ast),
    stl: best((s) => s.stl),
    blk: best((s) => s.blk),
  };
}

export function standingsRows(L: League, cid: number) {
  const order = confStandings(L, cid);
  const pr = powerRanks(L);
  return order.map((tid, i) => {
    const t = team(L, tid);
    const s = curSeason(t);
    return { t, s, pos: i + 1, power: pr.get(tid) ?? 0, cpct: winPct(s.cw, s.cl) };
  });
}

export function streakStr(n: number): string {
  if (!n) return "-";
  return n > 0 ? `W${n}` : `L${-n}`;
}

export const KIND_COLORS: Record<string, string> = {
  game: "#3b82f6",
  recruit: "#16a34a",
  injury: "#dc2626",
  award: "#d4a514",
  poll: "#8b5cf6",
  job: "#f97316",
  portal: "#0ea5e9",
  draft: "#6366f1",
  league: "#64748b",
  milestone: "#eab308",
  team: "#0d9488",
};
