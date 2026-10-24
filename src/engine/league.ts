import type { Conference, League, Settings, Team } from "./types";
import { clamp } from "./rng";
import { addCoach, addNews, addPlayer, reindex, roster, rngOf } from "./core";
import confData from "./data/conferences.json";
import teamData from "./data/teams.json";
import { generateInitialRoster, talentLevel } from "./gen/roster";
import { generateCoach } from "./gen/coach";
import { generateSchedule } from "./schedule";
import { generateRecruitClass, BASE_POINTS, staffPoints } from "./recruiting";
import { computePower, makePoll } from "./rankings";
import { chooseStrategy, aiRedshirts } from "./ai";
import { emptyTeamSeason } from "./stats";
import { emptyRecordBook } from "./records";
import { nilBudgetFor } from "./coaches";
import { DATA_VERSION } from "./migrate";

export const DEFAULT_SETTINGS: Settings = {
  nil: true,
  portal: true,
  bracketSize: 68,
  rosterMax: 15,
  canBeFired: true,
  recruitingDifficulty: 2,
  injuries: true,
  keepAllBoxScores: true,
  homeCourt: 3.5,
  autoRecruit: false,
};

export interface TeamInfo {
  slug: string;
  name: string;
  mascot: string;
  abbrev: string;
  short: string;
  conf: string;
  colors: [string, string];
  prestige: number;
  city: string;
  state: string;
}

export function teamCatalog(): { teams: TeamInfo[]; conferences: { slug: string; name: string; short: string; tier: number }[] } {
  return {
    teams: (teamData as unknown as (TeamInfo & { id: string })[]).map((t) => ({ ...t, slug: t.id })),
    conferences: (confData as { id: string; name: string; short: string; tier: number }[]).map((c) => ({ slug: c.id, name: c.name, short: c.short, tier: c.tier })),
  };
}

export interface NewLeagueOptions {
  name: string;
  teamSlug: string;
  coachFirst: string;
  coachLast: string;
  settings?: Partial<Settings>;
  seed?: number;
  startSeason?: number;
}

function uid(): string {
  return Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
}

export function createLeague(o: NewLeagueOptions): League {
  const seed = o.seed ?? Math.floor(Math.random() * 2 ** 31);
  const season = o.startSeason ?? 2026;
  const settings: Settings = { ...DEFAULT_SETTINGS, ...(o.settings ?? {}) };
  const conferences: Conference[] = (confData as { id: string; name: string; short: string; tier: number; confGames: number; tourneyTeams: number }[]).map((c, i) => ({
    id: i,
    slug: c.id,
    name: c.name,
    short: c.short,
    tier: c.tier,
    confGames: c.confGames,
    tourneyTeams: c.tourneyTeams,
  }));
  const confBySlug = new Map(conferences.map((c) => [c.slug, c]));
  const L: League = {
    id: uid(),
    name: o.name,
    version: DATA_VERSION,
    created: Date.now(),
    updated: Date.now(),
    seed,
    rng: seed,
    settings,
    startSeason: season,
    season,
    phase: "preseason",
    day: 0,
    week: 0,
    portalRound: 0,
    userTid: 0,
    userCid: 0,
    teams: [],
    conferences,
    players: [],
    coaches: [],
    nextPid: 1,
    nextGid: 1,
    nextNid: 1,
    nextCoachId: 1,
    games: [],
    brackets: [],
    polls: [],
    power: {},
    news: [],
    history: [],
    awards: [],
    records: emptyRecordBook(),
    draftHistory: [],
    transfers: [],
    transferLog: [],
    jobOffers: [],
    vacancies: [],
    realign: [],
    fired: false,
    recruitPts: BASE_POINTS,
    recruitPtsMax: BASE_POINTS,
    board: [],
    achievements: [],
    stopReason: null,
  };
  const rng = rngOf(L);
  const raw = teamData as unknown as { id: string; name: string; mascot: string; abbrev: string; short: string; conf: string; city: string; state: string; lat: number; lon: number; colors: [string, string]; prestige: number }[];
  raw.forEach((d, i) => {
    const c = confBySlug.get(d.conf);
    if (!c) throw new Error(`unknown conference ${d.conf}`);
    const t: Team = {
      id: i,
      slug: d.id,
      name: d.name,
      mascot: d.mascot,
      abbrev: d.abbrev,
      short: d.short,
      cid: c.id,
      city: d.city,
      state: d.state,
      lat: d.lat,
      lon: d.lon,
      colors: d.colors,
      prestige: d.prestige,
      facilities: Math.round(clamp(d.prestige + rng.normal(0, 9), 5, 99)),
      nilBudget: 0,
      coachId: -1,
      strategy: { tempo: 3, offense: "balanced", defense: "man", rebounding: "balanced" },
      rotation: { auto: true, starters: [], minutes: {} },
      practice: { focus: "balanced", intensity: 2, individual: {} },
      seasons: [],
      officialVisitsUsed: 0,
      recruitPoints: 0,
    };
    L.teams.push(t);
  });
  reindex(L);
  for (const t of L.teams) t.nilBudget = nilBudgetFor(L, t);
  const user = L.teams.find((t) => t.slug === o.teamSlug) ?? L.teams[0];
  L.userTid = user.id;

  // coaches
  for (const t of L.teams) {
    const c = generateCoach(rng, L.nextCoachId++, t.id, t.prestige, season);
    if (t.id === user.id) {
      c.first = o.coachFirst || "Coach";
      c.last = o.coachLast || "You";
      c.user = true;
      c.age = 38;
      c.recruiting = 60;
      c.development = 60;
      c.tactics = 60;
      c.rep = Math.round(clamp(t.prestige * 0.6 + 20, 25, 75));
      c.hired = season;
      c.security = 70;
      L.userCid = c.id;
    }
    t.coachId = c.id;
    addCoach(L, c);
  }

  // rosters
  for (const t of L.teams) {
    const size = clamp(13 + rng.int(0, 2), 10, settings.rosterMax);
    const ps = generateInitialRoster(rng, t.id, t.prestige, () => L.nextPid++, size);
    for (const p of ps) {
      p.hist.push({ season, ovr: p.ovr, pot: p.pot, r: { ...p.r } });
      // plausible recruiting pedigree for the generated starting rosters
      const walkOn = p.ovr < talentLevel(t.prestige) - 9;
      const stars = walkOn ? 0 : p.pot >= 82 ? 5 : p.pot >= 71 ? 4 : p.pot >= 60 ? 3 : p.pot >= 50 ? 2 : 1;
      p.recruitedBy = { tid: t.id, season: season - p.year + 1, stars, rank: 0, kind: "hs" };
      addPlayer(L, p);
    }
    t.seasons.push(emptyTeamSeason(season, t.coachId, t.prestige));
  }
  for (const t of L.teams) {
    if (t.id === user.id) continue; // the user starts from neutral tactics
    t.strategy = chooseStrategy(L, t, roster(L, t.id));
    aiRedshirts(L, t);
  }
  L.games = generateSchedule(L);
  generateRecruitClass(L);
  computePower(L);
  makePoll(L, "Preseason");
  L.recruitPtsMax = staffPoints(L, user);
  L.recruitPts = L.recruitPtsMax;
  const rank = L.polls[0]?.ranks.find((r) => r.tid === user.id)?.rank;
  const welcome = rank ? `Expectations are high: the ${user.mascot} open the season ranked No. ${rank}.` : "Nobody expects much yet. Time to change that.";
  addNews(L, "job", `Welcome to ${user.name}, Coach ${o.coachLast || "You"}. ${welcome}`, { tid: user.id, user: true });
  addNews(L, "recruit", `The class of ${season + 1} is on the board: ${L.players.filter((p) => p.status === "recruit").length} prospects. You have ${L.recruitPtsMax} recruiting points per week.`, { tid: user.id, user: true });
  return L;
}
