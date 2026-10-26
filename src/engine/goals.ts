// Season goals: three goals sized to your program, plus a stretch goal, each
// with a reward you get the moment you hit it.

import type { Goal, League } from "./types";
import { addNews, coach, conference, team } from "./core";
import { curSeason } from "./play";
import { clamp } from "./rng";
import { commitsFor, ratingsHidden } from "./recruiting";

const DEEP_RUNS = ["Sweet 16", "Elite Eight", "Final Four", "Championship", "Runner-up", "Champion"];

function reward(kind: Goal["reward"]["kind"], amount: number): Goal["reward"] {
  const text = kind === "points" ? `+${amount} coaching points every week` : kind === "prestige" ? `+${amount} program prestige` : `+${amount} job security`;
  return { kind, amount, text };
}

/** Make this season's goals if they don't exist yet. */
export function ensureGoals(L: League) {
  if (L.goals?.season === L.season) return;
  const t = team(L, L.userTid);
  const pr = t.prestige;
  const confName = conference(L, t.cid).short;
  const confSize = L.teams.filter((x) => x.cid === t.cid).length;
  const list: Goal[] = [];
  // wins: a little above what the athletic director expects
  const wins = pr >= 88 ? 27 : pr >= 78 ? 24 : pr >= 66 ? 21 : pr >= 52 ? 18 : pr >= 38 ? 15 : 12;
  list.push({ id: "wins", kind: "wins", text: `Win ${wins} games`, target: wins, reward: reward("prestige", 2), done: false });
  // the conference race
  if (pr >= 70) list.push({ id: "conf", kind: "confchamp", text: `Win the ${confName} regular season`, target: 1, reward: reward("security", 12), done: false });
  else {
    const k = pr >= 45 ? 3 : Math.ceil(confSize / 2);
    list.push({ id: "conf", kind: "conf", text: `Finish top ${k} in the ${confName}`, target: k, reward: reward("security", 12), done: false });
  }
  // recruiting
  const stars = pr >= 70 ? 4 : pr >= 40 ? 3 : 2;
  list.push({ id: "recruit", kind: "recruit", text: `Land a ${stars}-star recruit`, target: stars, reward: reward("points", 8), done: false });
  // the stretch goal
  if (pr >= 78) list.push({ id: "stretch", kind: "final4", text: "Reach the Final Four", target: 1, stretch: true, reward: reward("prestige", 4), done: false });
  else if (pr >= 60) list.push({ id: "stretch", kind: "sweet16", text: "Reach the Sweet 16", target: 1, stretch: true, reward: reward("prestige", 4), done: false });
  else if (pr >= 40) list.push({ id: "stretch", kind: "ncaa", text: "Make the NCAA Tournament", target: 1, stretch: true, reward: reward("prestige", 4), done: false });
  else list.push({ id: "stretch", kind: "ranked", text: "Beat a ranked team", target: 1, stretch: true, reward: reward("prestige", 3), done: false });
  L.goals = { season: L.season, list };
  // last season's bonus points are gone
  const old = L.pointsBonus ?? 0;
  if (old) {
    L.recruitPtsMax = Math.max(0, L.recruitPtsMax - old);
    L.recruitPts = Math.min(L.recruitPts, L.recruitPtsMax);
  }
  L.pointsBonus = 0;
}

/** Progress toward a goal as [current, target]. */
export function goalProgress(L: League, g: Goal): [number, number] {
  const t = team(L, L.userTid);
  const s = curSeason(t);
  switch (g.kind) {
    case "wins":
      return [Math.min(s.w, g.target), g.target];
    case "conf":
      return [s.confRank !== null && s.confRank <= g.target ? 1 : 0, 1];
    case "confchamp":
      return [s.confChamp ? 1 : 0, 1];
    case "recruit":
      // an unrated commit counts once the rankings come out
      return [commitsFor(L, t.id).some((p) => p.recruit?.kind === "hs" && !ratingsHidden(L, p) && p.recruit.stars >= g.target) ? 1 : 0, 1];
    case "ranked":
      return [Math.min(1, s.rankedWins ?? 0), 1];
    case "ncaa":
      return [s.post?.event === "ncaa" ? 1 : 0, 1];
    case "sweet16":
      return [s.post?.event === "ncaa" && DEEP_RUNS.includes(s.post.result) ? 1 : 0, 1];
    case "final4":
      return [s.post?.event === "ncaa" && ["Final Four", "Championship", "Runner-up", "Champion"].includes(s.post.result) ? 1 : 0, 1];
  }
}

/** Mark finished goals, pay their rewards, and note missed ones at season's end. Returns goals just completed. */
export function checkGoals(L: League): Goal[] {
  ensureGoals(L);
  const done: Goal[] = [];
  const t = team(L, L.userTid);
  for (const g of L.goals!.list) {
    if (g.done || g.failed) continue;
    const [cur, max] = goalProgress(L, g);
    if (cur >= max) {
      g.done = true;
      done.push(g);
      L.goalsDone = (L.goalsDone ?? 0) + 1;
      if (g.reward.kind === "prestige") t.prestige = Math.round(clamp(t.prestige + g.reward.amount, 1, 99) * 10) / 10;
      else if (g.reward.kind === "security") {
        const c = coach(L, L.userCid);
        if (c) c.security = Math.min(100, c.security + g.reward.amount);
      } else {
        L.pointsBonus = (L.pointsBonus ?? 0) + g.reward.amount;
        L.recruitPtsMax += g.reward.amount;
        L.recruitPts += g.reward.amount;
      }
      addNews(L, "milestone", `Goal complete: ${g.text}. Reward: ${g.reward.text}.`, { tid: t.id, user: true });
    }
  }
  // goals that can no longer happen
  const over = ["seasonEnd", "carousel", "draft", "portal", "signing"].includes(L.phase);
  for (const g of L.goals!.list) {
    if (g.done || g.failed) continue;
    if (g.kind === "conf" || g.kind === "confchamp") g.failed = L.phase !== "preseason" && L.phase !== "regular";
    else if (g.kind === "recruit") g.failed = L.phase === "signing"; // recruiting runs through signing day
    else g.failed = over;
  }
  return done;
}
