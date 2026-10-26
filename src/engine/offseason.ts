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
import { classRankings, commitsFor, dirtyRec, draftStock, finalSigning, resetUserPoints, generateRecruitClass, invalidateFit, NIL_VALUE, rankAndStar, recruitValue } from "./recruiting";
import { updatePrograms, nilBudgetFor } from "./coaches";
import { offseasonDevelopment } from "./development";
import { generatePlayer, assignJersey } from "./gen/player";
import { talentLevel } from "./gen/roster";
import { generateSchedule } from "./schedule";
import { hsNow } from "./hsStats";
import { chooseStrategy, aiRedshirts } from "./ai";
import { emptyLine, emptyTeamSeason } from "./stats";
import { applyRealignment } from "./realignment";
import { INTL } from "./data/international";

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
  // snapshot rosters; redshirt seasons get an explicit (empty) stat line
  for (const t of L.teams) {
    const ps = roster(L, t.id);
    curSeason(t).roster = ps.map((p) => p.id);
    for (const p of ps) {
      if (p.redshirt && !p.stats.some((x) => x.season === L.season && x.tid === t.id)) {
        p.stats.push({ ...emptyLine(), season: L.season, tid: t.id, year: p.eligUsed + 1, rs: true });
      }
    }
  }
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
  userMilestones(L);
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
  // international and pro-path prospects take about 20 of the 58 picks, mostly in the second round
  const DRAFT_PICKS = 58;
  const intlSlots = new Set<number>();
  const firstRound = rng.int(4, 7);
  while (intlSlots.size < firstRound) {
    // later first-round picks are more likely to go abroad
    const w = Array.from({ length: 30 }, (_, i) => 3 + i);
    intlSlots.add(1 + rng.weighted(w));
  }
  const secondRound = rng.int(12, 17);
  while (intlSlots.size < firstRound + secondRound) intlSlots.add(rng.int(31, DRAFT_PICKS));
  const collegeSlots = DRAFT_PICKS - intlSlots.size;
  const declared = new Set<number>();
  board.forEach(({ p }, i) => {
    if (graduating.includes(p)) return;
    const proj = i + 1;
    let prob = proj <= 8 ? 0.97 : proj <= 16 ? 0.85 : proj <= 24 ? 0.6 : proj <= 36 ? 0.28 : 0;
    prob *= 1 - 0.25 * (p.loyalty / 100);
    if (p.nilDeal > NIL_VALUE[4]) prob *= 0.8;
    if (rng.chance(prob)) declared.add(p.id);
  });
  const pool = board.filter(({ p }) => graduating.includes(p) || declared.has(p.id)).slice(0, collegeSlots);
  const order = rng.shuffle(NBA_TEAMS.slice());
  const picks: DraftPick[] = [];
  let ci = 0;
  for (let pick = 1; pick <= DRAFT_PICKS; pick++) {
    const round = pick <= 30 ? 1 : 2;
    const nbaTeam = order[(pick - 1) % 30];
    if (intlSlots.has(pick) || ci >= pool.length) {
      const src = INTL[rng.weighted(INTL.map((x) => x.weight))];
      const name = `${rng.pick(src.first)} ${rng.pick(src.last)}`;
      const pos = rng.pick(["PG", "SG", "SF", "PF", "C"] as const);
      picks.push({ season: L.season + 1, round, pick, pid: -((L.season + 1) * 100 + pick), name, tid: -1, pos, year: 0, ovr: 0, nbaTeam, from: `${rng.pick(src.clubs)} (${src.country})` });
      continue;
    }
    const { p } = pool[ci++];
    p.draft = { season: L.season + 1, round, pick, team: nbaTeam };
    p.status = "drafted";
    picks.push({ season: L.season + 1, round, pick, pid: p.id, name: playerName(p), tid: p.tid ?? -1, pos: p.pos, year: p.year, ovr: p.ovr, nbaTeam });
    leaving.add(p.id);
    if (p.tid === L.userTid) addNews(L, "draft", `${playerName(p)} was selected No. ${pick} overall by ${nbaTeam} in the NBA Draft!`, { tid: p.tid, pid: p.id, user: true });
  }
  if (picks[0]) {
    const p0 = picks[0];
    const from = p0.tid >= 0 ? team(L, p0.tid).name : p0.from;
    addNews(L, "draft", `${p0.name} (${from}) goes No. 1 overall to ${p0.nbaTeam}.`, p0.tid >= 0 ? { tid: p0.tid, pid: p0.pid, user: p0.tid === L.userTid } : { user: false });
  }
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
/**
 * Chance a player enters the transfer portal this spring. Modern college
 * basketball sees about half of all players with eligibility left enter:
 * bench players chasing minutes, mid-major standouts moving up for NIL
 * money, players following (or fleeing) a coaching change, grad transfers,
 * and plain fresh starts. Each reason is its own chance; they combine.
 */
export function transferRisk(L: League, p: Player): number {
  if (p.tid === null || p.status !== "active") return 0;
  const t = team(L, p.tid);
  const mates = roster(L, p.tid).slice().sort((a, b) => b.ovr - a.ovr);
  const rank = mates.indexOf(p) + 1;
  const s = p.stats.find((x) => x.season === L.season && x.tid === p.tid);
  const mpg = s && s.g ? s.min / s.g : 0;
  const played = !!s && s.g >= 6;
  const lvl = talentLevel(t.prestige);
  const reasons: number[] = [];
  // a fresh start: fit, family, school, or just the modern market
  reasons.push(0.36);
  // playing time against where he sits on the depth chart
  const expected = rank <= 5 ? 26 : rank <= 8 ? 16 : rank <= 10 ? 9 : 4;
  if (played) reasons.push(0.7 * Math.min(1, Math.max(0, expected - mpg - 3) / 14));
  // buried: deep bench guys who barely play look for a real role
  if (rank > 8 && mpg < 10) reasons.push(rank > 11 ? 0.65 : 0.5);
  // moving up: a player better than his program's level gets courted (NIL)
  if (p.ovr > lvl + 6 && t.prestige < 78) reasons.push(Math.min(0.55, 0.18 + 0.06 * (p.ovr - lvl - 6)));
  // a new head coach
  const c = coach(L, t.coachId);
  if (c && c.hired === L.season + 1) reasons.push(0.3);
  // one year left and not a starter: graduate transfer
  if (p.eligUsed === 3 && rank > 5) reasons.push(0.2);
  let pr = 1 - reasons.reduce((a, r) => a * (1 - r), 1);
  pr *= 1.3 - p.loyalty / 100;
  pr *= 1 - 0.45 * Math.min(1, p.nilDeal / NIL_VALUE[3]);
  // winning keeps a locker room together; losing empties it
  const ts = curSeason(t);
  const wp = ts.w + ts.l > 0 ? ts.w / (ts.w + ts.l) : 0.5;
  if (wp > 0.7) pr *= 0.72;
  else if (wp > 0.6) pr *= 0.86;
  else if (wp < 0.4) pr *= 1.15;
  if (ts.post?.event === "ncaa") pr *= 0.88;
  // portal intensity setting (1 = modern era)
  pr *= L.settings.portalRate ?? 1;
  return clamp(pr, 0, 0.92);
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
    // what a transfer is looking for depends on why he left
    const ft = team(L, from);
    const st = p.stats.find((x) => x.season === L.season && x.tid === from);
    const mpg = st && st.g ? st.min / st.g : 0;
    if (p.ovr > talentLevel(ft.prestige) + 6) {
      r.prefs.prestige = Math.max(r.prefs.prestige, 4);
      r.prefs.nil = 5;
      r.prefs.contender = Math.max(r.prefs.contender, 4);
    } else if (mpg < 18) {
      r.prefs.pt = 5;
      r.prefs.prestige = Math.min(r.prefs.prestige, 3);
    }
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
  resetUserPoints(L);
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
    // most players who enter don't go back, but some withdraw and return
    else if (spots(from) > 0 && rng.chance(0.18)) dest = from;
    else {
      const needy = L.teams.filter((t) => (t.id !== L.userTid || L.settings.autoRecruit) && spots(t.id) > 0);
      // about a third of real entrants never land at another Division I school
      if (needy.length && rng.chance(0.62)) {
        // late signings land where they'd start, a little above the program's typical player
        const want = p.ovr - 3;
        const fitting = needy.sort((a, b) => Math.abs(talentLevel(a.prestige) - want) - Math.abs(talentLevel(b.prestige) - want)).slice(0, 10);
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
  (L.transferLog ??= []).push(...L.transfers);
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
  // the senior season each signee just finished (it can only be worked out before the year turns over)
  const senior = new Map(L.players.filter((p) => p.recruit?.kind === "hs" && p.recruit.stage === "signed").map((p) => [p.id, hsNow(L, p)]));
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
    // remember the senior season he actually had, as shown while he was being recruited
    const sr = senior.get(p.id);
    p.recruitedBy = { tid, season: L.season, stars: r.stars, rank: r.rank, kind: "hs", hs: sr ? { pts: sr.pts, reb: sr.reb, ast: sr.ast } : r.hs };
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
  applyRealignment(L);
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
      if (t.rotation.order) t.rotation.order = t.rotation.order.filter((id) => ids.has(id));
      for (const k of Object.keys(t.rotation.minutes)) if (!ids.has(Number(k))) delete t.rotation.minutes[Number(k)];
      if (t.rotation.starters.length < 5) t.rotation.auto = true;
      for (const p of roster(L, t.id)) p.redshirt = false;
    }
    t.practice.individual = Object.fromEntries(Object.entries(t.practice.individual).filter(([k]) => roster(L, t.id).some((p) => p.id === Number(k))));
  }
  L.games = generateSchedule(L);
  generateRecruitClass(L);
  L.board = [];
  resetUserPoints(L);
  computePower(L);
  makePoll(L, "Preseason");
  const ut = userTeam(L);
  const r = L.polls[0].ranks.find((x) => x.tid === ut.id);
  addNews(L, "league", `The ${L.season}-${String((L.season + 1) % 100).padStart(2, "0")} season is here. ${ut.name} is ${r ? `ranked No. ${r.rank} in the preseason poll` : "unranked in the preseason poll"}.`, { tid: ut.id, user: true });
}

/** Career milestones for the user's coach (each awarded once). */
function userMilestones(L: League) {
  const uc = coach(L, L.userCid);
  if (!uc) return;
  const ut = userTeam(L);
  const s = curSeason(ut);
  const have = new Set(L.achievements.map((a) => a.name.replace(/ \(.*\)$/, "")));
  const award = (name: string) => {
    if (have.has(name)) return;
    have.add(name);
    L.achievements.push({ season: L.season, name: `${name} (${ut.name})` });
    addNews(L, "milestone", `Milestone: ${name}!`, { tid: ut.id, user: true });
  };
  if (s.post?.event === "ncaa") award("First NCAA Tournament bid");
  if (s.post?.event === "ncaa" && ["Champion", "Runner-up", "Final Four", "Elite Eight", "Sweet 16"].includes(s.post.result)) award("First Sweet 16");
  if (s.confChamp) award("First conference regular-season title");
  if (s.confTourney === "Champion") award("First conference tournament title");
  if (s.apBest === 1) award("Ranked No. 1 in the country");
  if (s.recruitRank === 1) award("No. 1 recruiting class");
  if (s.w >= 30) award("30-win season");
  if (uc.awards.some((a) => a.name === "Coach of the Year" && a.season === L.season)) award("National Coach of the Year");
  const wins = uc.seasons.reduce((a, x) => a + x.w, 0);
  for (const m of [100, 250, 500, 750]) if (wins >= m) award(`${m} career wins`);
}
