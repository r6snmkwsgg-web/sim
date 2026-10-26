// A recruit's high school career in full: every season's line and his senior-year game log.
// Everything is derived from his ratings and a per-player seed, so nothing is stored and older
// saves get the same numbers. The senior season plays out alongside the college season.

import type { League, Player } from "./types";
import { REG_DAYS } from "./core";
import { clamp, distanceMiles, hashNormal } from "./rng";
import { hsLine, hsSituation, hsSkill, scaledPts } from "./recruiting";
import { CITIES } from "./data/cities";

/** Per-game averages for one high school season. */
export interface HsSeason {
  year: "Freshman" | "Sophomore" | "Junior" | "Senior";
  live: boolean;
  g: number;
  gs: number;
  min: number;
  pts: number;
  fgm: number;
  fga: number;
  tpm: number;
  tpa: number;
  ftm: number;
  fta: number;
  orb: number;
  reb: number;
  ast: number;
  stl: number;
  blk: number;
  tov: number;
  pf: number;
}

export interface HsGame {
  day: number;
  opp: string;
  home: boolean;
  won: boolean;
  us: number;
  them: number;
  started: boolean;
  min: number;
  pts: number;
  fgm: number;
  fga: number;
  tpm: number;
  tpa: number;
  ftm: number;
  fta: number;
  orb: number;
  reb: number;
  ast: number;
  stl: number;
  blk: number;
  tov: number;
  pf: number;
}

type Counting = Omit<HsSeason, "year" | "live" | "g" | "gs">;

function seeded(seed: number) {
  let h = seed >>> 0 || 1;
  return () => {
    h = (h + 0x6d2b79f5) | 0;
    let t = Math.imul(h ^ (h >>> 15), 1 | h);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function gauss(r: () => number): number {
  return Math.sqrt(-2 * Math.log(r() + 1e-9)) * Math.cos(2 * Math.PI * r());
}

function binomial(r: () => number, n: number, p: number): number {
  let k = 0;
  for (let i = 0; i < n; i++) if (r() < p) k++;
  return k;
}

function poisson(r: () => number, lambda: number): number {
  if (lambda <= 0) return 0;
  const l = Math.exp(-lambda);
  let k = 0;
  let prod = r();
  while (prod > l && k < 60) {
    k++;
    prod *= r();
  }
  return k;
}

const one = (x: number) => Math.round(x * 10) / 10;

/** His shooting as a player: percentages and shot diet from his ratings, with his own quirks. */
function shooting(p: Player) {
  const R = p.r;
  const r = seeded(p.faceSeed ^ 0x51ed270b);
  const big = p.pos === "PF" || p.pos === "C";
  const p3 = clamp(0.3 + (R.three - 40) * 0.0042 + gauss(r) * 0.02, 0.18, 0.5);
  const p2 = clamp(0.46 + ((R.ins + R.mid) / 2 - 40) * 0.0035 + (big ? 0.04 : 0) + gauss(r) * 0.02, 0.37, 0.68);
  const pft = clamp(0.69 + (R.ft - 45) * 0.005 + gauss(r) * 0.03, 0.48, 0.93);
  // share of his shots from three, and free throws per shot
  const tr = clamp(0.14 + (R.three - 35) * 0.008 + (big ? -0.1 : 0.05), 0, 0.65);
  const ftr = clamp(0.28 + (R.ath - 50) * 0.003 + (R.ins - 50) * 0.003 + (big ? 0.06 : 0), 0.12, 0.6);
  return { p2, p3, pft, tr, ftr, r };
}

/** How he plays in high school: his shooting, with volume from his senior-year line. */
function profile(p: Player) {
  const line = hsLine(p)!;
  const R = p.r;
  const { p2: p2Skill, p3: p3Skill, pft, tr, ftr, r } = shooting(p);
  const big = p.pos === "PF" || p.pos === "C";
  const guard = p.pos === "PG" || p.pos === "SG";
  // a weak league makes for easy buckets (and a loaded prep schedule for hard ones); free throws are the same anywhere
  const sit = hsSituation(p);
  const p2 = clamp(p2Skill + 0.025 * sit, 0.35, 0.72);
  const p3 = clamp(p3Skill + 0.012 * sit, 0.16, 0.52);
  const fga = line.pts / ((1 - tr) * 2 * p2 + tr * 3 * p3 + ftr * pft);
  return {
    line,
    p2,
    p3,
    pft,
    tr,
    ftr,
    fga,
    orbShare: big ? 0.36 : guard ? 0.18 : 0.26,
    tov: clamp(0.8 + line.pts * 0.05 + (55 - R.hnd) * 0.04 + (p.pos === "PG" ? 0.4 : 0) + gauss(r) * 0.25, 0.3, 6),
    pf: clamp(1.6 + (big ? 0.8 : 0.2) + (50 - R.perD) * 0.01 + gauss(r) * 0.3, 0.6, 4),
    min: clamp(19 + line.pts * 0.32 + gauss(r) * 1.5, 12, 31),
  };
}

const PREFIXES = ["Lincoln", "Jefferson", "Roosevelt", "Kennedy", "Washington", "Franklin", "St. Joseph", "Bishop Moore", "Oak Ridge", "Riverside", "Lakeview", "Hillcrest", "Heritage", "Mountain View", "Central Catholic", "Northside", "Eastside", "Westview"];
const SIDES = ["Central", "North", "South", "East", "West", "Catholic", "Prep", "Christian"];

/** Opponents: schools from nearby towns, or the classic names every state has. */
function opponents(p: Player, r: () => number, n: number): string[] {
  const near = CITIES.filter((c) => c.city !== p.city && distanceMiles(p.lat, p.lon, c.lat, c.lon) < 220).map((c) => c.city);
  const out: string[] = [];
  for (let i = 0; i < n; i++) {
    out.push(near.length && r() < 0.6 ? `${near[Math.floor(r() * near.length)]} ${SIDES[Math.floor(r() * SIDES.length)]}` : `${PREFIXES[Math.floor(r() * PREFIXES.length)]} High`);
  }
  return out;
}

/** Days the senior season's games fall on: spread over the college regular season. */
function seniorDays(p: Player): number[] {
  const full = 26 + (p.faceSeed % 5);
  return Array.from({ length: full }, (_, i) => Math.min(REG_DAYS - 1, Math.floor(((i + 0.5) * REG_DAYS) / full)));
}

/** His senior-year games played so far (all of them once the college regular season is over). */
export function hsGameLog(L: League, p: Player): HsGame[] {
  const r0 = p.recruit;
  if (!r0 || r0.kind !== "hs" || !r0.hs || L.season + 1 !== r0.classSeason) return [];
  const days = seniorDays(p);
  const played = L.phase === "preseason" ? 0 : L.phase === "regular" ? days.filter((d) => d < L.day).length : days.length;
  const pr = profile(p);
  const rs = seeded((p.faceSeed ^ 0x2f6b) + p.id * 7919);
  const opps = opponents(p, rs, days.length);
  const winP = clamp(0.45 + (p.ovr - 40) * 0.012, 0.3, 0.9);
  const out: HsGame[] = [];
  for (let i = 0; i < played; i++) {
    const r = seeded(p.faceSeed * 31 + i * 7919 + 17);
    const min = Math.round(clamp(pr.min * (0.9 + r() * 0.2), 8, 32));
    const mf = min / pr.min;
    const fga = Math.max(0, Math.round(pr.fga * mf * (0.82 + r() * 0.36)));
    const tpa = binomial(r, fga, pr.tr);
    const tpm = binomial(r, tpa, pr.p3);
    const fgm = tpm + binomial(r, fga - tpa, pr.p2);
    const fta = Math.max(0, Math.round(fga * pr.ftr * (0.5 + r())));
    const ftm = binomial(r, fta, pr.pft);
    const pts = 2 * (fgm - tpm) + 3 * tpm + ftm;
    const reb = poisson(r, pr.line.reb * mf);
    const won = r() < winP;
    const us = Math.round(Math.max(pts + 20, 50 + r() * 28));
    const margin = 1 + Math.floor(r() * 22);
    out.push({
      day: days[i],
      opp: opps[i],
      home: r() < 0.5,
      won,
      us,
      them: Math.max(25, won ? us - margin : us + margin),
      started: true,
      min,
      pts,
      fgm,
      fga,
      tpm,
      tpa,
      ftm,
      fta,
      orb: binomial(r, reb, pr.orbShare),
      reb,
      ast: poisson(r, pr.line.ast * mf),
      stl: poisson(r, pr.line.stl * mf),
      blk: poisson(r, pr.line.blk * mf),
      tov: poisson(r, pr.tov * mf),
      pf: Math.min(5, poisson(r, pr.pf * mf)),
    });
  }
  return out;
}

const COUNTING: (keyof Counting)[] = ["min", "pts", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "orb", "reb", "ast", "stl", "blk", "tov", "pf"];

/** Every high school season as per-game averages; the senior one comes from his game log so far. */
export function hsSeasons(L: League, p: Player): HsSeason[] {
  const r0 = p.recruit;
  const line = hsLine(p);
  if (!r0 || r0.kind !== "hs" || !line) return [];
  const pr = profile(p);
  const r = seeded(p.faceSeed ^ 0x9e3779b9);
  const early = (year: HsSeason["year"], f: number): HsSeason => {
    const g = 22 + Math.floor(r() * 8);
    const j = () => 0.9 + r() * 0.2;
    // younger: fewer minutes, a smaller role and a little less accurate
    const p2 = pr.p2 - (1 - f) * 0.06;
    const p3 = pr.p3 - (1 - f) * 0.05;
    const pft = pr.pft - (1 - f) * 0.06;
    const pts = line.pts * f * j();
    const fga = pts / ((1 - pr.tr) * 2 * p2 + pr.tr * 3 * p3 + pr.ftr * pft);
    const reb = line.reb * f * j();
    return {
      year,
      live: false,
      g,
      gs: Math.round(g * clamp(f * 1.25 - 0.2, 0.1, 1)),
      min: one(pr.min * Math.pow(f, 0.6)),
      pts: one(pts),
      fgm: one(fga * (1 - pr.tr) * p2 + fga * pr.tr * p3),
      fga: one(fga),
      tpm: one(fga * pr.tr * p3),
      tpa: one(fga * pr.tr),
      ftm: one(fga * pr.ftr * pft),
      fta: one(fga * pr.ftr),
      orb: one(reb * pr.orbShare),
      reb: one(reb),
      ast: one(line.ast * f * j()),
      stl: one(line.stl * f * j()),
      blk: one(line.blk * f * j()),
      tov: one(pr.tov * Math.pow(f, 0.8)),
      pf: one(pr.pf * Math.pow(f, 0.5)),
    };
  };
  const out = [early("Freshman", 0.45), early("Sophomore", 0.66), early("Junior", 0.86)];
  if (L.season + 1 === r0.classSeason) {
    const games = hsGameLog(L, p);
    const g = games.length;
    const avg = Object.fromEntries(COUNTING.map((k) => [k, g ? one(games.reduce((a, x) => a + x[k], 0) / g) : 0])) as Counting;
    out.push({ year: "Senior", live: L.phase === "preseason" || L.phase === "regular", g, gs: games.filter((x) => x.started).length, ...avg });
  }
  return out;
}

// the board sorts the whole class by these, so each player's current line is kept for the day
const nowCache = new Map<number, { key: string; s: HsSeason | null }>();

/** Games into his senior year before it stands for him: a hot first week shouldn't top the board. */
export const HS_MIN_GAMES = 6;

/** The season he's playing (or last played): his senior year once he's a few games in, his junior year before. */
export function hsNow(L: League, p: Player): HsSeason | null {
  const key = `${L.id}:${L.season}:${L.phase}:${L.day}`;
  const c = nowCache.get(p.id);
  if (c && c.key === key) return c.s;
  const ss = hsSeasons(L, p);
  const s = [...ss].reverse().find((x) => x.g >= (x.live ? HS_MIN_GAMES : 1)) ?? null;
  nowCache.set(p.id, { key, s });
  return s;
}

// ---------------- summer circuit ----------------
// Grassroots ball the summers before his junior (16U) and senior (17U) years. The best prospects play on
// the national circuit, against each other on stacked teams: fewer shots, real defense, so the numbers are
// lower but honest. Regional circuits are softer. Fewer games than a high school season, so percentages
// bounce around more. Lots of kids never play on a circuit at all. Prospects from overseas play for their
// country's youth national team instead: strong competition, only a handful of games.

export type Circuit = "National" | "Regional" | "International";

export interface SummerSeason extends Omit<HsSeason, "year" | "live"> {
  label: "16U" | "17U";
  circuit: Circuit;
  team: string;
}

const SUMMER_NICKS = ["Elite", "Express", "All-Stars", "Select", "Legends", "Warriors", "Lightning", "Hoops", "Rise", "Prime", "Titans", "Stars"];

/** The circuit he played on that summer, or null if he didn't play on one. */
function isOverseas(p: Player): boolean {
  // US hometowns carry a two-letter state, international ones the country
  return p.state.length > 2;
}

export function summerCircuit(p: Player, label: "16U" | "17U" = "17U"): Circuit | null {
  const r = p.recruit;
  if (!r || r.kind !== "hs") return null;
  // mostly the best prospects, but some get overlooked and some get in on a name; a kid can move up a level between summers
  const z = hashNormal(p.faceSeed ^ 0x3c6ef372);
  const zz = label === "16U" ? 0.8 * z + 0.6 * hashNormal(p.faceSeed ^ 0x1f83d9ab) : z;
  const x = r.rank * Math.exp(0.55 * zz) * (label === "16U" ? 1.15 : 1);
  if (isOverseas(p)) return x <= 700 ? "International" : null;
  return x <= 330 ? "National" : x <= 1100 ? "Regional" : null;
}

/** His summer seasons, per game (none for transfers or kids who never played on a circuit). */
export function summerSeasons(p: Player): SummerSeason[] {
  const r0 = p.recruit;
  const line = hsLine(p);
  if (!r0 || r0.kind !== "hs" || !line) return [];
  const sk = hsSkill(p);
  const sh = shooting(p);
  const big = p.pos === "PF" || p.pos === "C";
  const club = `${p.city} ${SUMMER_NICKS[p.faceSeed % SUMMER_NICKS.length]}`;
  const out: SummerSeason[] = [];
  for (const [label, f, salt] of [["16U", 0.88, 16], ["17U", 1, 17]] as const) {
    const circuit = summerCircuit(p, label);
    if (!circuit) continue;
    // the national circuit and youth national teams are the top competition
    const nat = circuit !== "Regional";
    const r = seeded(p.faceSeed * 131 + salt * 7919);
    // his role on that team: some stars share the ball, some kids get the keys
    const role = hashNormal(p.faceSeed ^ (0x5f3759df + salt));
    const g = circuit === "International" ? 6 + Math.floor(r() * 3) : (nat ? 14 : 10) + Math.floor(r() * 6);
    const ptsPg = scaledPts(sk.pts * f * Math.exp(0.15 * role), 26) * (nat ? 0.7 : 0.8);
    const p2 = clamp(sh.p2 + (nat ? -0.035 : 0.01) - (1 - f) * 0.04, 0.3, 0.7);
    const p3 = clamp(sh.p3 + (nat ? -0.02 : 0.005) - (1 - f) * 0.03, 0.14, 0.5);
    const pft = clamp(sh.pft - (1 - f) * 0.03, 0.45, 0.93);
    const fga = Math.round((ptsPg / ((1 - sh.tr) * 2 * p2 + sh.tr * 3 * p3 + sh.ftr * pft)) * g * (0.92 + r() * 0.16));
    const tpa = binomial(r, fga, sh.tr);
    const tpm = binomial(r, tpa, p3);
    const fgm = tpm + binomial(r, fga - tpa, p2);
    const fta = Math.round(fga * sh.ftr * (0.85 + r() * 0.3));
    const ftm = binomial(r, fta, pft);
    const level = (nat ? 0.72 : 0.88) * f * Math.exp(0.1 * role);
    const reb = poisson(r, sk.reb * level * g);
    const per = (n: number) => one(n / g);
    out.push({
      label,
      circuit,
      team: circuit === "International" ? `${p.state} ${label === "16U" ? "U16" : "U17"}` : club,
      g,
      gs: Math.round(g * clamp(0.45 + 0.25 * role + (ptsPg - 12) * 0.04, 0.05, 1)),
      min: one(clamp((nat ? 14 : 17) + ptsPg * 0.42 + role * 1.5, 8, 32)),
      pts: per(2 * (fgm - tpm) + 3 * tpm + ftm),
      fgm: per(fgm),
      fga: per(fga),
      tpm: per(tpm),
      tpa: per(tpa),
      ftm: per(ftm),
      fta: per(fta),
      orb: per(binomial(r, reb, big ? 0.36 : 0.22)),
      reb: per(reb),
      ast: per(poisson(r, sk.ast * level * g)),
      stl: per(poisson(r, line.stl * level * g)),
      blk: per(poisson(r, line.blk * level * g)),
      tov: per(poisson(r, (0.6 + ptsPg * 0.08 + (55 - p.r.hnd) * 0.03) * g)),
      pf: per(poisson(r, (1.8 + (big ? 0.6 : 0)) * g)),
    });
  }
  return out;
}

// the board sorts the whole class by these
const summerCache = new Map<number, { key: string; s: SummerSeason | null }>();

/** His most recent summer (17U), or null if he didn't play on a circuit. */
export function summerNow(p: Player): SummerSeason | null {
  const key = `${p.ovr}:${p.recruit?.rank}:${p.faceSeed}`;
  const c = summerCache.get(p.id);
  if (c && c.key === key) return c.s;
  const s = summerSeasons(p).find((x) => x.label === "17U") ?? null;
  summerCache.set(p.id, { key, s });
  return s;
}
