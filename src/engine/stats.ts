import type { BoxLine, Player, PlayerSeasonStats, StatLine, TeamSeason } from "./types";
import { STAT_KEYS } from "./types";

export function emptyLine(): StatLine {
  return { g: 0, gs: 0, min: 0, pts: 0, fgm: 0, fga: 0, tpm: 0, tpa: 0, ftm: 0, fta: 0, orb: 0, drb: 0, ast: 0, stl: 0, blk: 0, tov: 0, pf: 0 };
}

export function seasonLine(p: Player, season: number, tid: number): PlayerSeasonStats {
  for (let i = p.stats.length - 1; i >= 0; i--) {
    const s = p.stats[i];
    if (s.season === season && s.tid === tid) return s;
    if (s.season < season) break;
  }
  const s: PlayerSeasonStats = { ...emptyLine(), season, tid, year: p.eligUsed + 1, rs: p.redshirt };
  p.stats.push(s);
  return s;
}

export function addBox(s: StatLine, b: BoxLine) {
  s.g++;
  if (b.starter) s.gs++;
  s.min += b.min;
  s.pts += b.pts;
  s.fgm += b.fgm;
  s.fga += b.fga;
  s.tpm += b.tpm;
  s.tpa += b.tpa;
  s.ftm += b.ftm;
  s.fta += b.fta;
  s.orb += b.orb;
  s.drb += b.drb;
  s.ast += b.ast;
  s.stl += b.stl;
  s.blk += b.blk;
  s.tov += b.tov;
  s.pf += b.pf;
}

export function sumLines(lines: StatLine[]): StatLine {
  const t = emptyLine();
  for (const l of lines) for (const k of STAT_KEYS) t[k] += l[k];
  return t;
}

export function careerLine(p: Player, tid?: number): StatLine {
  return sumLines(p.stats.filter((s) => tid === undefined || s.tid === tid));
}

export const per = (x: number, g: number) => (g > 0 ? x / g : 0);
export const pctOf = (m: number, a: number) => (a > 0 ? m / a : 0);
export const reb = (s: StatLine) => s.orb + s.drb;

export function fmt1(x: number): string {
  return (Math.round(x * 10) / 10).toFixed(1);
}
export function fmtPct(m: number, a: number): string {
  if (!a) return "-";
  const v = m / a;
  return v >= 1 ? "1.000" : v.toFixed(3).replace(/^0/, "");
}

/** Hollinger game score style value per game. */
export function gameScore(s: StatLine): number {
  return s.pts + 0.4 * s.fgm - 0.7 * s.fga - 0.4 * (s.fta - s.ftm) + 0.7 * s.orb + 0.3 * s.drb + s.stl + 0.7 * s.ast + 0.7 * s.blk - 0.4 * s.pf - s.tov;
}

export function emptyTeamSeason(season: number, coachId: number, prestige: number): TeamSeason {
  return {
    season,
    coachId,
    w: 0, l: 0, cw: 0, cl: 0, hw: 0, hl: 0, aw: 0, al: 0, nw: 0, nl: 0, pf: 0, pa: 0,
    streak: 0,
    confRank: null,
    confChamp: false,
    confTourney: null,
    post: null,
    apPre: null,
    apFinal: null,
    apBest: null,
    power: 0,
    prestige,
    recruitRank: null,
    recruitPts: 0,
    roster: [],
  };
}

export function winPct(w: number, l: number): number {
  return w + l > 0 ? w / (w + l) : 0;
}

export function recordStr(w: number, l: number): string {
  return `${w}-${l}`;
}
