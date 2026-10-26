// The season state machine: day simulation and phase transitions.

import { checkGoals } from "./goals";
import type { League } from "./types";
import { CT_START, SELECTION_DAY, REG_DAYS, addNews, roster, userTeam } from "./core";
import { playGame } from "./play";
import { computePower, makePoll } from "./rankings";
import {
  confTourneysDone, createBracketGames, createConfTourneys, finalizeStandings, nationalDone, recordBracketResult, runSelection,
} from "./postseason";
import { aiRecruitWeek, RATINGS_WEEK, recruitDecisions, releaseRatings, resetUserPoints, signCommits } from "./recruiting";
import { weeklyDevelopment } from "./development";
import { closePortal, departures, endSeason, openPortal, rollover, signingDay } from "./offseason";
import { finishCarousel, startCarousel } from "./coaches";

export const PORTAL_ROUNDS = 4;
export const EARLY_SIGNING_WEEK = 3;

/** Weekly processing: recruiting, development, polls. */
export function weekTick(L: League, poll: boolean) {
  aiRecruitWeek(L, "hs");
  recruitDecisions(L, "hs");
  L.week++;
  resetUserPoints(L);
  if (L.phase === "regular" && L.week === RATINGS_WEEK) releaseRatings(L);
  if (L.week === EARLY_SIGNING_WEEK) signCommits(L, "Early signing period");
  if (L.phase === "regular" || L.phase === "confTourney") weeklyDevelopment(L);
  computePower(L);
  if (poll) makePoll(L, `Week ${L.polls.length}`);
}

export function isDayPhase(L: League): boolean {
  return L.phase === "regular" || L.phase === "confTourney" || L.phase === "ncaa";
}

/** The days a new recruiting week starts: points reset, AI programs move, recruits decide. */
function weekStartsToday(L: League): boolean {
  if (L.phase === "regular") return L.day > 0 && L.day % 7 === 0;
  if (L.phase === "confTourney") return L.day === CT_START;
  if (L.phase === "ncaa") return L.day === 140 || L.day === 147;
  return false;
}

/** Start the week as soon as its first day arrives, so the user lands on Monday with fresh points. Runs once per day. */
function startWeekIfDue(L: League) {
  const key = `${L.season}:${L.day}`;
  if (!weekStartsToday(L) || L.weekStarted === key) return;
  L.weekStarted = key;
  weekTick(L, L.phase !== "ncaa");
}

/** Simulate one day. Returns whether the user's team played. */
export function simDay(L: League): { userPlayed: boolean } {
  // saves from before the week started at the end of the previous day still start it here
  startWeekIfDue(L);
  const out = simDayInner(L);
  startWeekIfDue(L);
  checkGoals(L);
  return out;
}

function simDayInner(L: League): { userPlayed: boolean } {
  let userPlayed = false;
  const play = (games: { home: number; away: number }[]) => {
    for (const g of games) if (g.home === L.userTid || g.away === L.userTid) userPlayed = true;
  };
  if (L.phase === "regular") {
    createBracketGames(L, L.day);
    const games = L.games.filter((g) => g.day === L.day && !g.played);
    for (const g of games) {
      playGame(L, g);
      if (g.tourney) recordBracketResult(L, g);
    }
    play(games);
    L.day++;
    // early-season events: tomorrow's games go on the schedule as soon as today's results are in
    if (L.day < REG_DAYS) createBracketGames(L, L.day);
    if (L.day >= REG_DAYS) {
      computePower(L);
      finalizeStandings(L);
      L.phase = "confTourney";
      L.day = CT_START;
      createConfTourneys(L);
      addNews(L, "league", "Conference tournament week has arrived.", { user: false });
    }
  } else if (L.phase === "confTourney") {
    const games = createBracketGames(L, L.day);
    for (const g of games) {
      playGame(L, g);
      recordBracketResult(L, g);
    }
    play(games);
    L.day++;
    if (confTourneysDone(L) || L.day > SELECTION_DAY) {
      computePower(L);
      makePoll(L, `Week ${L.polls.length}`);
      L.phase = "selection";
      L.day = SELECTION_DAY;
      runSelection(L);
    }
  } else if (L.phase === "ncaa") {
    const games = createBracketGames(L, L.day);
    for (const g of games) {
      playGame(L, g);
      recordBracketResult(L, g);
    }
    play(games);
    L.day++;
    if (nationalDone(L) || L.day > 160) {
      L.phase = "seasonEnd";
      endSeason(L);
    }
  }
  return { userPlayed };
}

export function portalTick(L: League) {
  aiRecruitWeek(L, "both");
  recruitDecisions(L, "both");
  L.week++;
  L.portalRound++;
  resetUserPoints(L);
}

/** Validation before leaving a phase. Returns an error message for the user, or null. */
export function advanceBlocker(L: League): string | null {
  if (L.phase === "preseason") {
    const r = roster(L, L.userTid);
    const avail = r.filter((p) => !p.redshirt);
    if (avail.length < 8) return "You need at least 8 non-redshirt players to start the season.";
  }
  if (L.phase === "carousel" && L.fired && L.jobOffers.length === 0) return null;
  return null;
}

/** Move to the next phase (for phases that are not simulated day by day). */
export function advancePhase(L: League) {
  advancePhaseInner(L);
  checkGoals(L);
}

function advancePhaseInner(L: League) {
  switch (L.phase) {
    case "preseason": {
      // the fall recruiting week ends: the AI programs make their moves and recruits weigh theirs, then the season (and the high school season) tips off
      aiRecruitWeek(L, "hs");
      recruitDecisions(L, "hs");
      L.week = 1;
      resetUserPoints(L);
      L.phase = "regular";
      L.day = 0;
      addNews(L, "team", `The regular season tips off for ${userTeam(L).name}.`, { tid: L.userTid, user: true });
      break;
    }
    case "selection":
      L.phase = "ncaa";
      L.day = 134;
      break;
    case "seasonEnd":
      L.phase = "carousel";
      startCarousel(L);
      break;
    case "carousel":
      finishCarousel(L);
      L.phase = "draft";
      departures(L);
      break;
    case "draft":
      L.phase = "portal";
      openPortal(L);
      break;
    case "portal":
      portalTick(L);
      if (L.portalRound > PORTAL_ROUNDS) {
        closePortal(L);
        L.phase = "signing";
        signingDay(L);
      }
      break;
    case "signing":
      rollover(L);
      break;
    default:
      // day phases: simulate until the phase changes
      {
        const start = L.phase;
        let guard = 0;
        while (L.phase === start && guard++ < 400) simDay(L);
      }
  }
}
