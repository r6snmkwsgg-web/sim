import type { DraftPick, League, Player, SeasonArchive, SeasonSummary } from "./types";
import { clamp } from "./rng";
import {
  addNews, addPlayer, coach, getSink, nextPid, playerName, removePlayers, roster, rngOf, rostersDirty, team, userTeam,
} from "./core";
import { curSeason } from "./play";
import { computePower, makePoll } from "./rankings";
import { computeAwards } from "./awards";
import { recordCareer, recordSeason } from "./records";
import { confStandings } from "./postseason";
import { classRankings, commitsFor, dirtyRec, draftStock, finalSigning, staffPoints, generateRecruitClass, invalidateFit, NIL_VALUE, rankAndStar, recruitValue } from "./recruiting";
import { updatePrograms, nilBudgetFor } from "./coaches";
import { offseasonDevelopment } from "./development";
import { generatePlayer, assignJersey } from "./gen/player";
import { talentLevel } from "./gen/roster";
import { generateSchedule } from "./schedule";
import { chooseStrategy, aiRedshirts } from "./ai";
import { emptyTeamSeason } from "./stats";

export const NBA_TEAMS = [
  "Atlanta", "Boston", "Brooklyn", "Charlotte", "Chicago", "Cleveland", "Dallas", "Denver", "Detroit", "Golden State",
  "Houston", "Indiana", "LA Clippers", "LA Lakers", "Memphis", "Miami", "Milwaukee", "Minnesota", "New Orleans", "New York",
  "Oklahoma City", "Orlando", "Philadelphia", "Phoenix", "Portland", "Sacramento", "San Antonio", "Toronto", "Utah", "Washington",
];

/** Move a player out of memory into the archive (career records first). */
export function archivePlayer(L: League, p: Player) {
  p.leftSeason = L.season;
  recordCareer(L, p);
  getSink().archivePlayer(L.id, structuredClone(p));
}

// ---------------- season end ----------------
export function endSeason(L: League) {
  computePower(L);
  makePoll(L, "Final", true);
  // class rankings before awards/prestige
  const cr = classRankings(L, "hs");
  const crMap = new Map(cr.map((x) => [x.tid, x]));
  for (const t of L.teams) {
    const s = curSeason(t);
    s.power = L.power[t.id]?.power ?? 0;
    const c = crMap.get(t.id);
    s.recruitPts = c?.pts ?? 0;
    s.recruitRank = c && c.n > 0 ? c.rank : null;
  }
  const aw = computeAwards(L);
  L.awards.push(aw);
  recordSeason(L);
  // snapshot rosters and ratings
  for (const t of L.teams) curSeason(t).roster = roster(L, t.id).map((p) => p.id);
  updatePrograms(L);
  // summary
  const ncaa = L.brackets.find((b) => b.key === "ncaa");
  const ff: number[] = [];
  if (ncaa) for (const g of ncaa.games) if (g.round === 4) for (const x of [g.a, g.b]) if (x !== null) ff.push(x);
  const us = curSeason(userTeam(L));
  const sum: SeasonSummary = {
    season: L.season,
    champion: ncaa?.champion ?? null,
    runnerUp: ncaa?.runnerUp ?? null,
    finalFour: ff,
    mop: aw.national.find((a) => a.name === "Final Four Most Outstanding Player") ?? null,
    poy: aw.national.find((a) => a.name === "Player of the Year") ?? null,
    nitChamp: L.brackets.find((b) => b.key === "nit")?.champion ?? null,
    cbiChamp: L.brackets.find((b) => b.key === "cbi")?.champion ?? null,
    userTid: L.userTid,
    userResult: us.post ? (us.post.event === "ncaa" ? `NCAA: ${us.post.result} (${us.post.seed} seed)` : `${us.post.event.toUpperCase()}: ${us.post.result}`) : "No postseason",
    apTop: L.polls[L.polls.length - 1]?.ranks[0]?.tid ?? null,
  };
  L.history.push(sum);
  if (sum.champion === L.userTid) L.achievements.push({ season: L.season, name: `National Champions (${userTeam(L).name})` });
  else if (ff.includes(L.userTid)) L.achievements.push({ season: L.season, name: `Final Four (${userTeam(L).name})` });
  // archive the season
  const archive: SeasonArchive = {
    season: L.season,
    games: L.games.map((g) => ({ ...g })),
    brackets: structuredClone(L.brackets),
    polls: structuredClone(L.polls),
    power: L.teams.map((t) => ({ tid: t.id, ...(L.power[t.id] ?? { power: 0, off: 0, def: 0, sos: 0 }) })),
    recruitClasses: cr.filter((x) => x.n > 0).map((x) => ({ tid: x.tid, pts: x.pts, rank: x.rank, pids: commitsFor(L, x.tid).filter((p) => p.recruit?.kind === "hs").map((p) => p.id) })),
    draft: [],
    transfers: [],
    standings: L.conferences.map((c) => ({ cid: c.id, order: confStandings(L, c.id) })),
  };
  getSink().archiveSeason(L.id, archive);
  addNews(L, "league", `The ${L.season}-${String((L.season + 1) % 100).padStart(2, "0")} season is complete.`, { user: false });
}

// ---------------- departures: eligibility, graduation, draft ----------------
export const draftValue = draftStock;

export function departures(L: League) {
  const rng = rngOf(L);
  const leaving = new Set<number>();
  const graduating: Player[] = [];
  const underclass: Player[] = [];
  for (const p of L.players) {
    if (p.status !== "active") continue;
    if (p.redshirt) {
      p.usedRedshirt = true;
      p.redshirt = false;
    } else {
      p.eligUsed++;
    }
    if (p.eligUsed >= 4 || p.year >= 5) graduating.push(p);
    else underclass.push(p);
  }
  // draft board
  const board = [...graduating, ...underclass]
    .filter((p) => p.ovr >= 55)
    .map((p) => ({ p, v: draftValue(p) + rng.normal(0, 2) }))
    .sort((a, b) => b.v - a.v);
  const declared = new Set<number>();
  board.forEach(({ p }, i) => {
    if (graduating.includes(p)) return;
    const proj = i + 1;
    let prob = proj <= 10 ? 0.97 : proj <= 20 ? 0.85 : proj <= 30 ? 0.62 : proj <= 45 ? 0.3 : 0;
    prob *= 1 - 0.25 * (p.loyalty / 100);
    if (p.nilDeal > NIL_VALUE[4]) prob *= 0.8;
    if (rng.chance(prob)) declared.add(p.id);
  });
  const pool = board.filter(({ p }) => graduating.includes(p) || declared.has(p.id)).slice(0, 58);
  const order = rng.shuffle(NBA_TEAMS.slice());
  const picks: DraftPick[] = [];
  pool.forEach(({ p }, i) => {
    const round = i < 29 ? 1 : 2;
    const pick = i + 1;
    const nbaTeam = order[i % 30];
    p.draft = { season: L.season + 1, round, pick, team: nbaTeam };
    p.status = "drafted";
    picks.push({ season: L.season + 1, round, pick, pid: p.id, name: playerName(p), tid: p.tid ?? -1, pos: p.pos, year: p.year, ovr: p.ovr, nbaTeam });
    leaving.add(p.id);
    if (p.tid === L.userTid) addNews(L, "draft", `${playerName(p)} was selected No. ${pick} overall by ${nbaTeam} in the NBA Draft!`, { tid: p.tid, pid: p.id, user: true });
  });
  if (picks[0]) addNews(L, "draft", `${picks[0].name} (${team(L, picks[0].tid).name}) goes No. 1 overall to ${picks[0].nbaTeam}.`, { tid: picks[0].tid, pid: picks[0].pid, user: picks[0].tid === L.userTid });
  L.draftHistory.push(...picks);
  for (const p of graduating) {
    if (leaving.has(p.id)) continue;
    p.status = "graduated";
    leaving.add(p.id);
  }
  for (const id of declared) {
    const p = L.players.find((x) => x.id === id)!;
    if (leaving.has(p.id)) continue;
    p.status = "left";
    p.retiredReason = "Declared for the draft (undrafted)";
    leaving.add(p.id);
    if (p.tid === L.userTid) addNews(L, "draft", `${playerName(p)} went undrafted after declaring early and is turning pro overseas.`, { tid: p.tid, pid: p.id, user: true });
  }
  const userLeaving = L.players.filter((p) => leaving.has(p.id) && p.tid === L.userTid && p.status === "graduated");
  if (userLeaving.length) addNews(L, "team", `Graduating from ${userTeam(L).name}: ${userLeaving.map(playerName).join(", ")}.`, { tid: L.userTid, user: true });
  for (const p of L.players) if (leaving.has(p.id)) archivePlayer(L, p);
  removePlayers(L, leaving);
  invalidateFit(L);
}

// ---------------- transfer portal ----------------
export function transferRisk(L: League, p: Player): number {
  if (p.tid === null || p.status !== "active") return 0;
  const t = team(L, p.tid);
  const mates = roster(L, p.tid).slice().sort((a, b) => b.ovr - a.ovr);
  const rank = mates.indexOf(p) + 1;
  const s = p.stats.find((x) => x.season === L.season && x.tid === p.tid);
  const mpg = s && s.g ? s.min / s.g : 0;
  const expected = rank <= 5 ? 26 : rank <= 8 ? 15 : rank <= 10 ? 7 : 2;
  const dis = Math.max(0, expected - mpg - 4) / 20;
  let pr = 0.03 + 0.3 * Math.min(1, dis);
  const lvl = talentLevel(t.prestige);
  if (p.ovr > lvl + 6 && t.prestige < 70) pr += 0.12 * Math.min(2, (p.ovr - lvl - 6) / 6);
  const c = coach(L, t.coachId);
  if (c && c.hired === L.season + 1) pr += 0.12;
  if (p.eligUsed === 3 && mpg < 15) pr += 0.08;
  // buried well below the program's level: look for minutes elsewhere
  if (rank > 9 && p.ovr < lvl - 10 && mpg < 6 && p.eligUsed < 3) pr += 0.3;
  pr *= 1.35 - p.loyalty / 100;
  pr *= 1 - 0.5 * Math.min(1, p.nilDeal / NIL_VALUE[3]);
  const ts = curSeason(t);
  if (ts.w + ts.l > 0 && ts.w / (ts.w + ts.l) > 0.65) pr *= 0.85;
  return clamp(pr, 0, 0.85);
}

export function openPortal(L: League) {
  const rng = rngOf(L);
  L.portalRound = 1;
  L.transfers = [];
  const entering: Player[] = [];
  for (const p of L.players) {
    if (p.status !== "active" || p.tid === null) continue;
    if (!L.settings.portal) continue;
    if (rng.chance(transferRisk(L, p))) entering.push(p);
  }
  const fromTid = new Map<number, number>();
  for (const p of entering) {
    const from = p.tid!;
    fromTid.set(p.id, from);
    p.status = "portal";
    p.tid = null;
    L.transfers.push({ season: L.season + 1, pid: p.id, name: playerName(p), from, to: null, ovr: p.ovr, stars: 0 });
  }
  rankAndStar(L, entering, "portal", L.season + 1);
  for (const p of entering) {
    const r = p.recruit!;
    const from = fromTid.get(p.id)!;
    r.fromTid = from;
    // former school keeps a relationship
    r.interest[from] = 8 * (p.loyalty / 100);
    const mv = L.transfers.find((m) => m.pid === p.id);
    if (mv) mv.stars = r.stars;
    if (from === L.userTid) addNews(L, "portal", `${playerName(p)} (${p.pos}, ${r.stars}★) has entered the transfer portal.`, { tid: from, pid: p.id, user: true });
  }
  const top = entering.filter((p) => p.recruit!.stars === 5).slice(0, 3);
  if (entering.length) addNews(L, "portal", `The transfer portal is open: ${entering.length} players have entered${top.length ? `, headlined by ${top.map(playerName).join(", ")}` : ""}.`, { user: false });
  rostersDirty(L);
  dirtyRec(L);
  invalidateFit(L);
  L.recruitPtsMax = staffPoints(L, userTeam(L));
  L.recruitPts = L.recruitPtsMax;
}

export function closePortal(L: League) {
  const rng = rngOf(L);
  const spots = (tid: number) => L.settings.rosterMax - roster(L, tid).length - commitsFor(L, tid).filter((q) => q.recruit?.kind === "hs").length;
  const portal = L.players.filter((p) => p.status === "portal");
  // committed players join; others return home or find a spot
  portal.sort((a, b) => recruitValue(b) - recruitValue(a));
  for (const p of portal) {
    const r = p.recruit!;
    const from = r.fromTid!;
    let dest: number | null = null;
    if (r.committedTo !== null && (r.stage === "committed" || r.stage === "signed")) dest = r.committedTo;
    else if (spots(from) > 0 && rng.chance(0.6)) dest = from;
    else {
      const needy = L.teams.filter((t) => t.id !== L.userTid && spots(t.id) > 0);
      if (needy.length) {
        const fitting = needy.sort((a, b) => Math.abs(talentLevel(a.prestige) - p.ovr) - Math.abs(talentLevel(b.prestige) - p.ovr)).slice(0, 10);
        dest = rng.pick(fitting).id;
      }
    }
    const mv = L.transfers.find((m) => m.pid === p.id);
    if (dest === null) {
      p.status = "left";
      p.retiredReason = "Left college after entering the portal";
      if (mv) mv.to = null;
      archivePlayer(L, p);
      continue;
    }
    p.status = "active";
    p.tid = dest;
    p.nilDeal = r.nil[dest] ?? 0;
    if (dest !== from) {
      p.transfers.push({ season: L.season + 1, from, to: dest });
      p.recruitedBy = { tid: dest, season: L.season + 1, stars: r.stars, rank: r.rank, kind: "portal" };
      if (dest === L.userTid) addNews(L, "portal", `Transfer ${playerName(p)} (${p.pos}, from ${team(L, from).name}) joins ${team(L, dest).name}.`, { tid: dest, pid: p.id, user: true });
      else if (from === L.userTid) addNews(L, "portal", `${playerName(p)} transfers from ${team(L, from).name} to ${team(L, dest).name}.`, { tid: from, pid: p.id, user: true });
    } else if (from === L.userTid) {
      addNews(L, "portal", `${playerName(p)} withdrew from the portal and is returning to ${team(L, from).name}.`, { tid: from, pid: p.id, user: true });
    }
    if (mv) mv.to = dest === from ? null : dest;
    p.recruit = null;
    const used = new Set(roster(L, dest).map((q) => q.jersey));
    if (used.has(p.jersey)) p.jersey = assignJersey(rng, used);
    rostersDirty(L);
  }
  removePlayers(L, new Set(L.players.filter((p) => p.status === "left").map((p) => p.id)));
  L.transfers = L.transfers.filter((m) => m.to !== null);
  dirtyRec(L);
  invalidateFit(L);
}

// ---------------- signing day ----------------
export function signingDay(L: League) {
  finalSigning(L);
  invalidateFit(L);
}

/** Before the new season: enforce roster limits and fill with walk-ons. */
export function finalizeRosters(L: League) {
  const rng = rngOf(L);
  for (const t of L.teams) {
    const incoming = commitsFor(L, t.id).filter((p) => p.recruit?.kind === "hs" && p.recruit.stage === "signed");
    const current = roster(L, t.id);
    let over = current.length + incoming.length - L.settings.rosterMax;
    if (over > 0) {
      // release the lowest-rated players without scholarships first
      const cut = current.slice().sort((a, b) => a.ovr + a.pot * 0.3 - (b.ovr + b.pot * 0.3)).slice(0, over);
      for (const p of cut) {
        p.status = "left";
        p.retiredReason = `Released by ${t.name}`;
        if (t.id === L.userTid) addNews(L, "team", `${playerName(p)} was released to meet the roster limit.`, { tid: t.id, pid: p.id, user: true });
        archivePlayer(L, p);
      }
      removePlayers(L, new Set(cut.map((p) => p.id)));
      over = 0;
    }
    const total = roster(L, t.id).length + incoming.length;
    const minSize = Math.min(L.settings.rosterMax, 13);
    if (total < minSize) {
      const used = new Set(roster(L, t.id).map((p) => p.jersey));
      for (let i = total; i < minSize; i++) {
        const lvl = talentLevel(t.prestige) - 14;
        const ovr = Math.round(clamp(lvl + rng.normal(0, 4), 18, 60));
        const p = generatePlayer(rng, { id: nextPid(L), ovr, pot: ovr + rng.int(3, 12), year: 1 });
        p.tid = t.id;
        p.status = "active";
        p.year = 0; // becomes 1 at rollover
        p.eligUsed = 0;
        p.archetype = `Walk-on ${p.archetype}`;
        p.jersey = assignJersey(rng, used);
        p.recruitedBy = { tid: t.id, season: L.season + 1, stars: 0, rank: 0, kind: "hs" };
        addPlayer(L, p);
        if (t.id === L.userTid) addNews(L, "team", `Walk-on ${playerName(p)} (${p.pos}) joins ${t.name}.`, { tid: t.id, pid: p.id, user: true });
      }
    }
  }
  rostersDirty(L);
}

// ---------------- new season ----------------
export function rollover(L: League) {
  const rng = rngOf(L);
  finalizeRosters(L);
  L.season++;
  L.phase = "preseason";
  L.day = 0;
  L.week = 0;
  L.portalRound = 0;
  L.polls = [];
  L.brackets = [];
  L.transfers = [];
  // returning players develop and age
  for (const p of L.players) {
    if (p.status !== "active" || p.tid === null) continue;
    const t = team(L, p.tid);
    if (p.year >= 1) offseasonDevelopment(L, p, t);
    p.year++;
    if (p.injury) {
      p.injury.games -= 25;
      if (p.injury.games <= 0) p.injury = null;
    }
    p.morale = 70;
  }
  // signed recruits enroll
  const enroll: Player[] = [];
  for (const p of L.players) {
    const r = p.recruit;
    if (!r || r.kind !== "hs") continue;
    if (r.stage === "signed" && r.committedTo !== null) enroll.push(p);
  }
  for (const p of enroll) {
    const r = p.recruit!;
    const tid = r.committedTo!;
    p.status = "active";
    p.tid = tid;
    p.year = 1;
    p.eligUsed = 0;
    p.nilDeal = r.nil[tid] ?? 0;
    p.recruitedBy = { tid, season: L.season, stars: r.stars, rank: r.rank, kind: "hs" };
    p.recruit = null;
    const used = new Set(roster(L, tid).map((q) => q.jersey));
    p.jersey = assignJersey(rng, used);
  }
  // drop unsigned recruits entirely (they never played college ball)
  removePlayers(L, new Set(L.players.filter((p) => p.status === "unsigned" || (p.status === "recruit" && p.recruit?.stage !== "signed")).map((p) => p.id)));
  rostersDirty(L);
  dirtyRec(L);
  invalidateFit(L);
  // ratings snapshot for the new season
  for (const p of L.players) {
    if (p.status === "active") p.hist.push({ season: L.season, ovr: p.ovr, pot: p.pot, r: { ...p.r } });
  }
  // teams
  for (const t of L.teams) {
    t.seasons.push(emptyTeamSeason(L.season, t.coachId, t.prestige));
    t.officialVisitsUsed = 0;
    t.nilBudget = nilBudgetFor(L, t);
    if (t.id !== L.userTid) {
      t.strategy = chooseStrategy(L, t, roster(L, t.id));
      aiRedshirts(L, t);
    } else {
      // keep the user's rotation valid
      const ids = new Set(roster(L, t.id).map((p) => p.id));
      t.rotation.starters = t.rotation.starters.filter((id) => ids.has(id));
      for (const k of Object.keys(t.rotation.minutes)) if (!ids.has(Number(k))) delete t.rotation.minutes[Number(k)];
      if (t.rotation.starters.length < 5) t.rotation.auto = true;
      for (const p of roster(L, t.id)) p.redshirt = false;
    }
    t.practice.individual = Object.fromEntries(Object.entries(t.practice.individual).filter(([k]) => roster(L, t.id).some((p) => p.id === Number(k))));
  }
  L.games = generateSchedule(L);
  generateRecruitClass(L);
  L.board = [];
  L.recruitPtsMax = staffPoints(L, userTeam(L));
  L.recruitPts = L.recruitPtsMax;
  computePower(L);
  makePoll(L, "Preseason");
  const ut = userTeam(L);
  const r = L.polls[0].ranks.find((x) => x.tid === ut.id);
  addNews(L, "league", `The ${L.season}-${String((L.season + 1) % 100).padStart(2, "0")} season is here. ${ut.name} is ${r ? `ranked No. ${r.rank} in the preseason poll` : "unranked in the preseason poll"}.`, { tid: ut.id, user: true });
}
