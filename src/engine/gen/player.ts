import type { Player, Pos, Race, RatingKey, Ratings } from "../types";
import { RATING_KEYS } from "../types";
import { Rng, clamp } from "../rng";
import { calcOvr } from "../ratings";
import {
  FIRST_ASIAN, FIRST_BLACK, FIRST_COMMON, FIRST_HISPANIC, INTERNATIONAL,
  LAST_ASIAN, LAST_COMMON, LAST_HISPANIC,
} from "../data/names";
import { CITIES } from "../data/cities";

type Profile = Partial<Record<RatingKey, number>>;

export const ARCHETYPES: Record<Pos, { name: string; p: Profile }[]> = {
  PG: [
    { name: "Floor General", p: { hnd: 12, pas: 15, iq: 10, ins: -5, perD: 2, stl: 5, ath: 3, reb: -15, blk: -20, intD: -18, str: -12, ft: 5, end: 5 } },
    { name: "Scoring Guard", p: { three: 10, mid: 8, hnd: 10, pas: 3, iq: 2, ath: 5, ft: 8, reb: -14, blk: -20, intD: -18, str: -10, stl: 3 } },
    { name: "Slashing Guard", p: { ath: 14, ins: 8, hnd: 10, three: -6, pas: 2, perD: 3, stl: 5, reb: -10, blk: -15, intD: -14, str: -6, ft: -2 } },
    { name: "Defensive Pest", p: { perD: 15, stl: 14, ath: 8, hnd: 6, pas: 6, three: -4, mid: -4, reb: -12, blk: -16, intD: -14, str: -8, end: 6 } },
  ],
  SG: [
    { name: "Sharpshooter", p: { three: 16, mid: 8, ft: 10, hnd: 2, pas: -2, ins: -6, perD: -2, reb: -10, blk: -16, intD: -14, str: -8, iq: 4 } },
    { name: "3-and-D Guard", p: { three: 10, perD: 12, stl: 6, ath: 6, hnd: -2, pas: -4, mid: -2, ins: -4, reb: -6, blk: -10, intD: -8, str: -4, iq: 3 } },
    { name: "Slasher", p: { ath: 14, ins: 10, hnd: 6, mid: 2, three: -6, ft: -2, perD: 2, stl: 3, reb: -6, blk: -12, intD: -12, str: -2 } },
    { name: "Combo Guard", p: { hnd: 8, pas: 8, mid: 6, three: 4, iq: 4, reb: -10, blk: -16, intD: -14, str: -8 } },
  ],
  SF: [
    { name: "Wing Scorer", p: { mid: 10, three: 6, ins: 6, hnd: 4, ath: 6, ft: 4, reb: -2, blk: -8, intD: -6, perD: -2 } },
    { name: "3-and-D Wing", p: { three: 10, perD: 12, ath: 6, stl: 4, blk: -4, intD: -2, hnd: -4, pas: -4, ins: -2 } },
    { name: "Point Forward", p: { pas: 12, hnd: 8, iq: 10, reb: 2, ins: 2, blk: -6, intD: -4 } },
    { name: "Athletic Wing", p: { ath: 15, ins: 8, perD: 6, reb: 4, three: -6, mid: -2, pas: -4, iq: -4 } },
  ],
  PF: [
    { name: "Stretch Four", p: { three: 8, mid: 8, reb: 4, str: 2, hnd: -6, pas: -4, perD: -4, stl: -6 } },
    { name: "Power Forward", p: { ins: 10, reb: 12, str: 12, intD: 8, blk: 4, three: -18, mid: -4, hnd: -12, pas: -6, ath: 2, perD: -8, stl: -8, ft: -6 } },
    { name: "Athletic Forward", p: { ath: 14, ins: 8, reb: 6, blk: 8, perD: 2, three: -10, mid: -4, hnd: -6, pas: -6, intD: 2, stl: -2 } },
    { name: "Glue Guy", p: { iq: 12, reb: 8, intD: 6, perD: 4, pas: 4, ins: 0, three: -6, ath: -2, hnd: -4 } },
  ],
  C: [
    { name: "Rim Protector", p: { blk: 18, intD: 14, reb: 12, str: 8, ins: 2, three: -26, mid: -12, hnd: -18, pas: -10, ath: 2, perD: -10, stl: -10, ft: -12 } },
    { name: "Post Scorer", p: { ins: 16, str: 12, reb: 8, intD: 4, blk: 2, three: -22, hnd: -14, pas: -4, ath: -4, perD: -12, stl: -10, ft: -6 } },
    { name: "Stretch Five", p: { three: 4, mid: 10, ins: 4, reb: 8, intD: 2, blk: 4, str: 4, hnd: -12, pas: -2, ath: -6, perD: -10, stl: -10, ft: 2 } },
    { name: "Mobile Big", p: { ath: 10, ins: 8, reb: 10, blk: 10, intD: 8, perD: -4, three: -16, mid: -6, hnd: -10, pas: -4, stl: -6, ft: -8 } },
  ],
};

const HEIGHT: Record<Pos, [number, number]> = {
  PG: [73.5, 1.9],
  SG: [76, 1.7],
  SF: [78.3, 1.5],
  PF: [80.3, 1.4],
  C: [82.6, 1.6],
};

export function randomPos(rng: Rng): Pos {
  return rng.pick(["PG", "SG", "SF", "PF", "C"] as Pos[]);
}

export function randomRace(rng: Rng): Race {
  const x = rng.next();
  if (x < 0.56) return "black";
  if (x < 0.9) return "white";
  if (x < 0.96) return "brown";
  return "asian";
}

export function randomName(rng: Rng, race: Race): { first: string; last: string } {
  let first: string;
  let last: string;
  if (race === "black") {
    first = rng.chance(0.55) ? rng.pick(FIRST_BLACK) : rng.pick(FIRST_COMMON);
    last = rng.pick(LAST_COMMON);
  } else if (race === "brown") {
    first = rng.chance(0.6) ? rng.pick(FIRST_HISPANIC) : rng.pick(FIRST_COMMON);
    last = rng.chance(0.85) ? rng.pick(LAST_HISPANIC) : rng.pick(LAST_COMMON);
  } else if (race === "asian") {
    first = rng.chance(0.5) ? rng.pick(FIRST_ASIAN) : rng.pick(FIRST_COMMON);
    last = rng.chance(0.85) ? rng.pick(LAST_ASIAN) : rng.pick(LAST_COMMON);
  } else {
    first = rng.pick(FIRST_COMMON);
    last = rng.pick(LAST_COMMON);
  }
  return { first, last };
}

let cityTotal = 0;
for (const c of CITIES) cityTotal += c.w;

export function randomHometown(rng: Rng): { city: string; state: string; lat: number; lon: number; intl?: (typeof INTERNATIONAL)[number] } {
  if (rng.chance(0.05)) {
    const pool = rng.pick(INTERNATIONAL);
    return { city: pool.city, state: pool.country, lat: pool.lat, lon: pool.lon, intl: pool };
  }
  let r = rng.next() * cityTotal;
  for (const c of CITIES) {
    r -= c.w;
    if (r < 0) return { city: c.city, state: c.state, lat: c.lat, lon: c.lon };
  }
  const c = CITIES[0];
  return { city: c.city, state: c.state, lat: c.lat, lon: c.lon };
}

function shapeRatings(rng: Rng, pos: Pos, level: number, profile: Profile): Ratings {
  const r = {} as Ratings;
  for (const k of RATING_KEYS) {
    r[k] = level + (profile[k] ?? 0) + rng.normal(0, 6);
  }
  // one standout trait for flavor
  const spike = rng.pick(RATING_KEYS);
  r[spike] += rng.uniform(4, 10);
  r.end = level + 4 + rng.normal(0, 8);
  // bigs shouldn't be great ball handlers; guards shouldn't be dominant shot blockers
  if (pos === "C" || pos === "PF") r.hnd = Math.min(r.hnd, level + 8);
  if (pos === "PG" || pos === "SG") r.blk = Math.min(r.blk, level - 2);
  for (const k of RATING_KEYS) r[k] = clamp(Math.round(r[k]), 1, 99);
  return r;
}

/** Shift ratings so the overall lands on the target. */
export function fitToOvr(r: Ratings, pos: Pos, hgt: number, target: number): void {
  for (let pass = 0; pass < 4; pass++) {
    const cur = calcOvr(r, pos, hgt);
    const diff = target - cur;
    if (Math.abs(diff) < 0.5) return;
    for (const k of RATING_KEYS) {
      if (k === "end") continue;
      r[k] = clamp(Math.round(r[k] + diff), 1, 99);
    }
  }
}

export interface GenOptions {
  id: number;
  ovr: number;
  pot: number;
  year: number; // 0 = HS recruit
  pos?: Pos;
}

export function generatePlayer(rng: Rng, o: GenOptions): Player {
  const pos = o.pos ?? randomPos(rng);
  const home = randomHometown(rng);
  let race: Race;
  let first: string;
  let last: string;
  if (home.intl) {
    race = rng.pick(home.intl.race);
    first = rng.pick(home.intl.first);
    last = rng.pick(home.intl.last);
  } else {
    race = randomRace(rng);
    ({ first, last } = randomName(rng, race));
  }
  const [hm, hs] = HEIGHT[pos];
  // better players skew slightly taller within position
  const hgt = clamp(Math.round(rng.normal(hm + (o.pot - 55) * 0.03, hs)), 66, 88);
  const wgt = Math.round(clamp(185 + (hgt - 74) * 7.5 + rng.normal(0, 13) + (pos === "C" ? 10 : 0), 150, 300));
  const wing = Math.round(hgt + rng.normal(3.5, 2));
  const arche = rng.pick(ARCHETYPES[pos]);
  const r = shapeRatings(rng, pos, o.ovr, arche.p);
  fitToOvr(r, pos, hgt, o.ovr);
  const ovr = calcOvr(r, pos, hgt);
  const pot = Math.max(ovr, Math.round(o.pot));
  return {
    id: o.id,
    first,
    last,
    pos,
    archetype: arche.name,
    hgt,
    wgt,
    wing,
    city: home.city,
    state: home.state,
    lat: home.lat,
    lon: home.lon,
    faceSeed: rng.seed32(),
    race,
    r,
    ovr,
    pot,
    potErr: Math.round(rng.normal(0, 3)),
    workEthic: clamp(Math.round(rng.normal(55, 18)), 5, 99),
    loyalty: clamp(Math.round(rng.normal(55, 20)), 5, 99),
    tid: null,
    status: o.year === 0 ? "recruit" : "active",
    year: o.year,
    eligUsed: Math.max(0, o.year - 1),
    redshirt: false,
    usedRedshirt: false,
    jersey: 0,
    tend: { three: 5, mid: 5, inside: 5, drive: 5 },
    injury: null,
    stats: [],
    hist: [],
    awards: [],
    transfers: [],
    recruit: null,
    nilDeal: 0,
    morale: 70,
    gameHigh: { pts: 0, reb: 0, ast: 0 },
  };
}

/** Pick an unused jersey number for a roster. */
export function assignJersey(rng: Rng, used: Set<number>): number {
  const pool = [0, 1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 20, 21, 22, 23, 24, 25, 30, 31, 32, 33, 34, 35, 40, 41, 42, 43, 44, 45, 50, 51, 52, 55];
  const free = pool.filter((n) => !used.has(n));
  const n = free.length ? rng.pick(free) : rng.int(0, 99);
  used.add(n);
  return n;
}
