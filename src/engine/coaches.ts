import type { Coach, League, Team } from "./types";
import { clamp } from "./rng";
import { addCoach, addNews, coach, conference, reindex, rngOf, team, userTeam } from "./core";
import { generateCoach } from "./gen/coach";
import { curSeason } from "./play";
import { winPct } from "./stats";
import { prestigeTier } from "./ratings";

const POST_SCORE: Record<string, number> = {
  Champion: 35,
  "Runner-up": 28,
  "Final Four": 22,
  "Elite Eight": 16,
  "Sweet 16": 11,
  "Round of 32": 7,
  "Round of 64": 4,
  "First Four": 2,
};
const TIER_CAP = [100, 100, 90, 78, 68];

export function seasonScore(L: League, t: Team): number {
  const s = curSeason(t);
  // strength of the team (opponent-adjusted) matters more than raw record
  const power = L.power[t.id]?.power ?? 0;
  let score = clamp(43 + 2.0 * power, 2, 96) + 10 * (winPct(s.w, s.l) - 0.5);
  if (s.post?.event === "ncaa") score += POST_SCORE[s.post.result] ?? 3;
  else if (s.post?.event === "nit") score += s.post.result === "Champion" ? 4 : 1;
  else if (s.post?.event === "cbi") score += 0.5;
  if (s.confChamp) score += 3;
  if (s.confTourney === "Champion") score += 2;
  if (s.apFinal !== null) score += s.apFinal <= 5 ? 6 : s.apFinal <= 10 ? 4 : 2;
  if (s.recruitRank !== null) score += s.recruitRank <= 5 ? 5 : s.recruitRank <= 10 ? 3 : s.recruitRank <= 25 ? 1.5 : 0;
  return clamp(score, 0, 100);
}

export function nilBudgetFor(L: League, t: Team): number {
  const tier = conference(L, t.cid).tier;
  const mult = [0, 1, 0.45, 0.2, 0.08][tier] ?? 0.08;
  return Math.round(6000 * mult * Math.pow(t.prestige / 100, 1.5) + 50);
}

export function updatePrograms(L: League) {
  const rng = rngOf(L);
  for (const t of L.teams) {
    const s = curSeason(t);
    const score = seasonScore(L, t);
    const old = t.prestige;
    const delta = score - old;
    let rate = delta > 0 ? 0.13 : 0.1;
    if (delta < 0 && old > 85) rate *= 0.7;
    let np = old + rate * delta;
    const cap = TIER_CAP[conference(L, t.cid).tier] ?? 68;
    if (np > cap && np > old) np = Math.max(old, cap + (np - cap) * 0.35);
    t.prestige = Math.round(clamp(np, 1, 99) * 10) / 10;
    s.prestige = t.prestige;
    t.facilities = Math.round(clamp(t.facilities + 0.08 * (t.prestige - t.facilities) + rng.normal(0, 1), 5, 99));
    t.nilBudget = nilBudgetFor(L, t);
    if (t.id === L.userTid) {
      const before = prestigeTier(old);
      const after = prestigeTier(t.prestige);
      if (before !== after) {
        addNews(L, "milestone", `${t.name}'s program prestige is now "${after}" (was "${before}").`, { tid: t.id, user: true });
        if (after === "Blue Blood" && !L.achievements.some((a) => a.name === `Blue Blood: ${t.name}`)) {
          L.achievements.push({ season: L.season, name: `Blue Blood: ${t.name}` });
        }
      }
    }
    // coach reputation & security
    const c = coach(L, t.coachId);
    if (c) {
      c.rep = Math.round(clamp(c.rep + 0.2 * (score - c.rep) + (score - old) * 0.05, 1, 99) * 10) / 10;
      const yearsIn = L.season - c.hired + 1;
      let sec = c.security + (score - old) * 0.9 + 3;
      if (yearsIn <= 2) sec = Math.max(sec, 35);
      c.security = Math.round(clamp(sec, 0, 100));
      c.seasons.push({
        season: L.season,
        tid: t.id,
        w: s.w,
        l: s.l,
        cw: s.cw,
        cl: s.cl,
        result: s.post ? (s.post.event === "ncaa" ? `NCAA ${s.post.result}` : `${s.post.event.toUpperCase()} ${s.post.result}`) : s.confRank ? `${s.confRank}${ord(s.confRank)} in conf.` : "",
      });
    }
  }
}

function ord(n: number): string {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return s[(v - 20) % 10] || s[v] || s[0];
}

// ---------------- carousel ----------------
export interface Vacancy {
  tid: number;
}

/** Beginning of the carousel: firings, retirements, user's evaluation & offers. */
export function startCarousel(L: League) {
  const rng = rngOf(L);
  L.jobOffers = [];
  L.fired = false;
  const vacancies: number[] = [];
  for (const t of L.teams) {
    const c = coach(L, t.coachId);
    if (!c || c.user) continue;
    c.age++;
    const fire = c.security < 12 && L.season - c.hired >= 2 && rng.chance(0.7);
    const retire = (c.age >= 68 && rng.chance(0.35)) || c.age >= 73;
    if (fire || retire) {
      c.tid = null;
      if (retire) c.retired = true;
      vacancies.push(t.id);
      t.coachId = -1;
      if (fire) addNews(L, "job", `${t.name} has fired head coach ${c.first} ${c.last}.`, { tid: t.id, user: false });
      else addNews(L, "job", `${t.name} head coach ${c.first} ${c.last} has retired.`, { tid: t.id, user: false });
    }
  }
  const uc = coach(L, L.userCid)!;
  uc.age++;
  const ut = userTeam(L);
  if (L.settings.canBeFired && uc.security <= 10 && L.season - uc.hired >= 2) {
    L.fired = true;
    addNews(L, "job", `You have been fired as head coach of ${ut.name}. Pick a new job from the offers available.`, { tid: ut.id, user: true });
  }
  // offers for the user
  const open = vacancies.map((tid) => team(L, tid)).sort((a, b) => b.prestige - a.prestige);
  let offers: Team[];
  if (L.fired) {
    offers = open.filter((t) => t.prestige <= uc.rep + 5).slice(0, 4);
    if (offers.length < 2) {
      // create openings at low-prestige schools
      const low = L.teams
        .filter((t) => t.id !== ut.id && !vacancies.includes(t.id) && t.prestige < 35)
        .sort(() => rng.next() - 0.5)
        .slice(0, 3 - offers.length);
      for (const t of low) {
        const c = coach(L, t.coachId);
        if (c) c.tid = null;
        t.coachId = -1;
        vacancies.push(t.id);
        offers.push(t);
      }
    }
  } else {
    offers = open.filter((t) => t.prestige >= ut.prestige + 4 && uc.rep >= t.prestige - 14).slice(0, 3);
  }
  for (const t of offers) {
    L.jobOffers.push({ tid: t.id, season: L.season, reason: L.fired ? "Opening" : `${prestigeTier(t.prestige)} program` });
  }
  if (!L.fired && L.jobOffers.length) {
    addNews(L, "job", `You have ${L.jobOffers.length} job offer${L.jobOffers.length > 1 ? "s" : ""}: ${L.jobOffers.map((o) => team(L, o.tid).name).join(", ")}.`, { tid: ut.id, user: true });
  }
  L.vacancies = vacancies;
}

export function acceptJob(L: League, tid: number): boolean {
  const offer = L.jobOffers.find((o) => o.tid === tid);
  if (!offer) return false;
  const uc = coach(L, L.userCid)!;
  const old = userTeam(L);
  const nt = team(L, tid);
  // old team becomes a vacancy
  old.coachId = -1;
  if (!L.vacancies.includes(old.id)) L.vacancies.push(old.id);
  L.vacancies = L.vacancies.filter((x) => x !== tid);
  const prevCoach = nt.coachId >= 0 ? coach(L, nt.coachId) : undefined;
  if (prevCoach) prevCoach.tid = null;
  nt.coachId = uc.id;
  uc.tid = nt.id;
  uc.hired = L.season + 1;
  uc.security = 60;
  L.userTid = nt.id;
  L.jobOffers = [];
  L.fired = false;
  L.board = [];
  nt.rotation = { auto: true, starters: [], minutes: {} };
  addNews(L, "job", `You have accepted the head coaching job at ${nt.name}!`, { tid: nt.id, user: true });
  return true;
}

/** End of the carousel: AI fills every vacancy (chains included). */
export function finishCarousel(L: League) {
  const rng = rngOf(L);
  if (L.fired && L.jobOffers.length) {
    // the user must have a job: take the best offer
    acceptJob(L, L.jobOffers[0].tid);
  }
  L.jobOffers = [];
  const queue = L.vacancies.slice();
  let guard = 0;
  while (queue.length && guard++ < 400) {
    queue.sort((a, b) => team(L, b).prestige - team(L, a).prestige);
    const tid = queue.shift()!;
    const t = team(L, tid);
    if (t.coachId >= 0) continue;
    // poach a successful coach from a smaller program
    const pool = L.coaches.filter(
      (c) => !c.user && c.tid !== null && !c.retired && c.age < 64 && team(L, c.tid).prestige <= t.prestige - 8 && c.rep >= t.prestige - 12,
    );
    let hire: Coach | undefined;
    if (pool.length && rng.chance(0.65)) {
      hire = pool.sort((a, b) => b.rep - a.rep)[Math.min(pool.length - 1, rng.int(0, 2))];
      const from = team(L, hire.tid!);
      from.coachId = -1;
      queue.push(from.id);
      addNews(L, "job", `${t.name} hires ${hire.first} ${hire.last} away from ${from.name}.`, { tid: t.id, user: from.id === L.userTid });
    } else {
      hire = generateCoach(rng, L.nextCoachId++, t.id, t.prestige * 0.75, L.season + 1);
      hire.age = rng.int(34, 52);
      hire.rep = Math.round(clamp(t.prestige * 0.7 + rng.normal(0, 8), 5, 90));
      addCoach(L, hire);
      addNews(L, "job", `${t.name} names ${hire.first} ${hire.last} head coach.`, { tid: t.id, user: false });
    }
    hire.tid = t.id;
    hire.hired = L.season + 1;
    hire.security = 60;
    t.coachId = hire.id;
  }
  L.vacancies = [];
  // drop retired/unemployed AI coaches from memory if they never coached a season
  L.coaches = L.coaches.filter((c) => c.user || c.tid !== null || c.seasons.length > 0);
  reindex(L);
}
