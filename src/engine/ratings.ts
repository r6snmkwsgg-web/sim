import type { Player, Pos, RatingKey, Ratings } from "./types";
import { RATING_KEYS } from "./types";

// Weights for overall rating by position (each row sums to 1).
export const OVR_WEIGHTS: Record<Pos, Partial<Record<RatingKey, number>>> = {
  PG: { hnd: 0.16, pas: 0.16, three: 0.12, mid: 0.07, ins: 0.06, iq: 0.12, perD: 0.1, stl: 0.05, ath: 0.1, ft: 0.03, reb: 0.02, str: 0.01 },
  SG: { three: 0.17, mid: 0.1, ins: 0.08, hnd: 0.1, pas: 0.07, iq: 0.09, perD: 0.12, stl: 0.05, ath: 0.11, ft: 0.04, reb: 0.04, str: 0.03 },
  SF: { three: 0.11, mid: 0.09, ins: 0.11, hnd: 0.07, pas: 0.06, iq: 0.09, perD: 0.11, intD: 0.05, reb: 0.08, ath: 0.11, str: 0.05, stl: 0.03, blk: 0.02, ft: 0.02 },
  PF: { ins: 0.15, mid: 0.07, three: 0.05, reb: 0.15, intD: 0.13, blk: 0.07, str: 0.1, ath: 0.09, iq: 0.08, perD: 0.05, pas: 0.03, hnd: 0.02, ft: 0.01 },
  C: { ins: 0.17, reb: 0.17, intD: 0.16, blk: 0.12, str: 0.11, ath: 0.07, iq: 0.07, mid: 0.03, pas: 0.03, ft: 0.02, hnd: 0.01, three: 0.04 },
};

export const POS_HEIGHT: Record<Pos, number> = { PG: 74, SG: 76, SF: 78, PF: 80, C: 82 };

export function calcOvr(r: Ratings, pos: Pos, hgt: number): number {
  const w = OVR_WEIGHTS[pos];
  let s = 0;
  let tw = 0;
  for (const k of RATING_KEYS) {
    const wk = w[k];
    if (wk) {
      s += wk * r[k];
      tw += wk;
    }
  }
  const base = s / tw;
  return Math.round(Math.max(1, Math.min(99, base + (hgt - POS_HEIGHT[pos]) * 0.8)));
}

/** Overall if the player were slotted at another position (used for lineup decisions). */
export function ovrAt(p: Player, pos: Pos): number {
  return calcOvr(p.r, pos, p.hgt);
}

export function updateOvr(p: Player): void {
  p.ovr = calcOvr(p.r, p.pos, p.hgt);
}

// Letter grades against D1 players: C is the typical player, B a good starter, A an All-American.
// (About 2% of D1 players grade out as an A overall, about a quarter B, half C.)
const GRADES: [number, string][] = [
  [75, "A+"], [70, "A"], [66, "A-"], [62, "B+"], [58, "B"], [54, "B-"],
  [50, "C+"], [46, "C"], [42, "C-"], [38, "D+"], [34, "D"], [30, "D-"],
];

export function grade(x: number): string {
  for (const [t, g] of GRADES) if (x >= t) return g;
  return "F";
}

export function gradeClass(x: number): string {
  if (x >= 66) return "g-a";
  if (x >= 54) return "g-b";
  if (x >= 42) return "g-c";
  if (x >= 30) return "g-d";
  return "g-f";
}

export const RATING_LABELS: Record<RatingKey, string> = {
  ins: "Inside",
  mid: "Mid-Range",
  three: "Three",
  ft: "Free Throw",
  hnd: "Handling",
  pas: "Passing",
  iq: "Basketball IQ",
  perD: "Perimeter D",
  intD: "Interior D",
  stl: "Steals",
  blk: "Blocks",
  reb: "Rebounding",
  ath: "Athleticism",
  str: "Strength",
  end: "Endurance",
};

export const RATING_SHORT: Record<RatingKey, string> = {
  ins: "INS", mid: "MID", three: "3PT", ft: "FT", hnd: "HND", pas: "PAS", iq: "IQ",
  perD: "PER", intD: "INT", stl: "STL", blk: "BLK", reb: "REB", ath: "ATH", str: "STR", end: "END",
};

export function heightStr(inches: number): string {
  return `${Math.floor(inches / 12)}'${Math.round(inches % 12)}"`;
}

export const CLASS_LABELS = ["HS", "FR", "SO", "JR", "SR", "GR"];

export function classLabel(p: { year: number; usedRedshirt: boolean; redshirt: boolean; eligUsed?: number }): string {
  // Display by eligibility year: a redshirt freshman is in year 2 with 0 or 1 seasons used.
  const elig = p.eligUsed ?? p.year - 1;
  const idx = Math.min(5, Math.max(0, p.year === 0 ? 0 : elig + 1));
  const base = CLASS_LABELS[idx] ?? "GR";
  if (p.redshirt) return `${base} (RS)`;
  if (p.usedRedshirt && p.year > 1) return `RS ${base}`;
  return base;
}

/** Classify prestige into a named tier. */
export function prestigeTier(p: number): string {
  if (p >= 90) return "Blue Blood";
  if (p >= 80) return "Elite";
  if (p >= 70) return "Power Program";
  if (p >= 58) return "Solid";
  if (p >= 45) return "Mid-Major";
  if (p >= 30) return "Low-Major";
  return "Rebuild";
}

export function prestigeStars(p: number): number {
  // 0.5 .. 5 stars
  return Math.max(0.5, Math.min(5, Math.round((p / 20) * 2) / 2));
}
