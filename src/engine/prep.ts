// Game prep: spend the week's coaching points (the same pool recruiting uses)
// scouting your next opponent. Your players know their sets and tendencies,
// which shows up as slightly better shots on offense and contested looks on
// defense. It costs recruiting, so it's a real tradeoff.

import type { League } from "./types";
import { team } from "./core";

export interface PrepLevel {
  level: number;
  name: string;
  cost: number;
  /** about how many points a game it's worth */
  edge: number;
  desc: string;
}

export const PREP_LEVELS: PrepLevel[] = [
  { level: 0, name: "No prep", cost: 0, edge: 0, desc: "Play your game and see what happens." },
  { level: 1, name: "Film study", cost: 6, edge: 1, desc: "The staff cuts up their last few games. Your guys know who the shooters are." },
  { level: 2, name: "Scouting report", cost: 14, edge: 2, desc: "A full report on their sets and tendencies, walked through in practice." },
  { level: 3, name: "Full game plan", cost: 24, edge: 2.5, desc: "Advance scouting, a tailored game plan and a walkthrough of every set. Worth it for the big ones." },
];

/** Added to your shooting and taken off theirs, by prep level (calibrated to the edges above). */
export const PREP_SHOT = [0, 0.006, 0.0115, 0.0145];

/** The user's next opponent: the next scheduled game, or a pending bracket game. */
export function nextOpponent(L: League): number | null {
  for (const g of L.games) {
    if (g.played) continue;
    if (g.home === L.userTid) return g.away;
    if (g.away === L.userTid) return g.home;
  }
  for (const br of L.brackets) {
    if (br.champion !== null) continue;
    const bg = br.games.find((x) => x.winner === null && (x.a === L.userTid || x.b === L.userTid));
    if (bg) return bg.a === L.userTid ? bg.b : bg.a;
  }
  return null;
}

/** The prep level already bought for the next game. */
export function currentPrep(L: League): number {
  const opp = nextOpponent(L);
  return L.prep && opp !== null && L.prep.opp === opp ? L.prep.level : 0;
}

/** Buy (or change) prep for the next game. Points spent this week come back if you lower it. */
export function setPrep(L: League, level: number): { ok: boolean; msg?: string } {
  const opp = nextOpponent(L);
  if (opp === null) return { ok: false, msg: "No opponent yet" };
  const want = PREP_LEVELS[level];
  if (!want) return { ok: false, msg: "Unknown level" };
  const cur = L.prep && L.prep.opp === opp ? L.prep : null;
  const paid = cur?.paid ?? 0;
  const weekPaid = cur && cur.week === L.week ? cur.weekPaid : 0;
  const extra = want.cost - paid;
  if (extra > L.recruitPts) return { ok: false, msg: `Needs ${extra} points; you have ${L.recruitPts} left this week` };
  if (extra >= 0) {
    L.recruitPts -= extra;
    L.prep = { opp, level, paid: want.cost, week: L.week, weekPaid: weekPaid + extra };
  } else {
    // lowering: only this week's spending is refundable
    const refund = Math.min(-extra, weekPaid);
    L.recruitPts += refund;
    const left = paid - refund;
    L.prep = level === 0 && left === 0 ? undefined : { opp, level, paid: left, week: L.week, weekPaid: weekPaid - refund };
  }
  return { ok: true };
}

/** Line for the next game in points (positive = the user is favored), with and without prep. */
export function projectedLine(L: League, opp: number, home: boolean | null, prep: number): number {
  const us = L.power[L.userTid]?.power ?? 0;
  const them = L.power[opp]?.power ?? 0;
  const court = home === null ? 0 : home ? L.settings.homeCourt : -L.settings.homeCourt;
  return us - them + court + (PREP_LEVELS[prep]?.edge ?? 0);
}

export function prepSummary(L: League): string {
  const lvl = currentPrep(L);
  const opp = nextOpponent(L);
  if (opp === null) return "";
  return lvl ? `${PREP_LEVELS[lvl].name} for ${team(L, opp).name}` : `No prep yet for ${team(L, opp).name}`;
}
