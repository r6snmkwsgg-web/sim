import type { League, Poll } from "./types";
import { mean, clamp } from "./rng";
import { roster, team } from "./core";

/** Roster-based strength: average of the top 8 healthy, non-redshirt overalls. */
export function rosterStrength(L: League, tid: number): number {
  const ps = roster(L, tid)
    .filter((p) => !p.redshirt)
    .map((p) => p.ovr * (p.injury && p.injury.games > 10 ? 0.5 : 1))
    .sort((a, b) => b - a)
    .slice(0, 8);
  return ps.length ? mean(ps) : 30;
}

const PTS_PER_OVR = 1.25;

export function priorPower(L: League): Map<number, number> {
  const s = new Map<number, number>();
  for (const t of L.teams) s.set(t.id, rosterStrength(L, t.id));
  const avg = mean([...s.values()]);
  const out = new Map<number, number>();
  for (const [tid, v] of s) out.set(tid, (v - avg) * PTS_PER_OVR);
  return out;
}

/** Opponent-adjusted margin rating, offense/defense, and strength of schedule. */
export function computePower(L: League) {
  const prior = priorPower(L);
  const games = L.games.filter((g) => g.played);
  const byTeam = new Map<number, { opp: number; m: number; pf: number; pa: number; loc: number }[]>();
  for (const t of L.teams) byTeam.set(t.id, []);
  let totalPts = 0;
  for (const g of games) {
    const loc = g.neutral ? 0 : 1;
    byTeam.get(g.home)?.push({ opp: g.away, m: g.hs - g.as, pf: g.hs, pa: g.as, loc });
    byTeam.get(g.away)?.push({ opp: g.home, m: g.as - g.hs, pf: g.as, pa: g.hs, loc: -loc });
    totalPts += g.hs + g.as;
  }
  const avgPts = games.length ? totalPts / (games.length * 2) : 70;
  const HCA = L.settings.homeCourt * 0.9;
  const K = 3;
  let r = new Map(prior);
  const O = new Map<number, number>();
  const D = new Map<number, number>();
  for (const t of L.teams) {
    O.set(t.id, (prior.get(t.id) ?? 0) / 2);
    D.set(t.id, -(prior.get(t.id) ?? 0) / 2);
  }
  for (let it = 0; it < 25; it++) {
    const nr = new Map<number, number>();
    const nO = new Map<number, number>();
    const nD = new Map<number, number>();
    for (const t of L.teams) {
      const gl = byTeam.get(t.id)!;
      let s = 0;
      let so = 0;
      let sd = 0;
      for (const x of gl) {
        const adj = x.loc * HCA;
        s += clamp(x.m - adj, -25, 25) + (r.get(x.opp) ?? 0);
        so += x.pf - adj / 2 - avgPts - (D.get(x.opp) ?? 0);
        sd += x.pa + adj / 2 - avgPts - (O.get(x.opp) ?? 0);
      }
      const pr = prior.get(t.id) ?? 0;
      nr.set(t.id, (s + K * pr) / (gl.length + K));
      nO.set(t.id, (so + K * (pr / 2)) / (gl.length + K));
      nD.set(t.id, (sd + K * (-pr / 2)) / (gl.length + K));
    }
    const mr = mean([...nr.values()]);
    for (const [k, v] of nr) nr.set(k, v - mr);
    r = nr;
    for (const [k, v] of nO) O.set(k, v);
    for (const [k, v] of nD) D.set(k, v);
  }
  L.power = {};
  for (const t of L.teams) {
    const gl = byTeam.get(t.id)!;
    const sos = gl.length ? mean(gl.map((x) => r.get(x.opp) ?? 0)) : 0;
    L.power[t.id] = {
      power: Math.round((r.get(t.id) ?? 0) * 10) / 10,
      off: Math.round(((O.get(t.id) ?? 0) + avgPts) * 10) / 10,
      def: Math.round(((D.get(t.id) ?? 0) + avgPts) * 10) / 10,
      sos: Math.round(sos * 10) / 10,
    };
  }
}

export function powerRanks(L: League): Map<number, number> {
  const sorted = L.teams.slice().sort((a, b) => (L.power[b.id]?.power ?? 0) - (L.power[a.id]?.power ?? 0));
  return new Map(sorted.map((t, i) => [t.id, i + 1]));
}

export function currentPoll(L: League): Poll | undefined {
  return L.polls[L.polls.length - 1];
}

const rankCache = new WeakMap<Poll, Map<number, number>>();
export function currentRank(L: League, tid: number): number | null {
  const poll = currentPoll(L);
  if (!poll) return null;
  let m = rankCache.get(poll);
  if (!m) {
    m = new Map(poll.ranks.map((r) => [r.tid, r.rank]));
    rankCache.set(poll, m);
  }
  return m.get(tid) ?? null;
}

export function makePoll(L: League, label: string, final = false) {
  const prev = currentPoll(L);
  const prevRank = new Map<number, number>(prev ? prev.ranks.map((r) => [r.tid, r.rank]) : []);
  const scores = L.teams.map((t) => {
    const s = t.seasons[t.seasons.length - 1];
    const g = s.w + s.l;
    const pw = L.power[t.id]?.power ?? 0;
    let score = pw + 1.15 * (s.w - s.l) * (g / (g + 6)) + 0.05 * (t.prestige - 50);
    if (g === 0) score = pw + 0.07 * (t.prestige - 50);
    const pr = prevRank.get(t.id);
    if (pr && !final) score += (26 - pr) * 0.22;
    if (final && s.post?.event === "ncaa") {
      // final poll rewards tournament runs
      const bonus: Record<string, number> = { Champion: 14, "Runner-up": 10, "Final Four": 7, "Elite Eight": 4, "Sweet 16": 2 };
      score += bonus[s.post.result] ?? 0;
    }
    return { t, s, score };
  });
  scores.sort((a, b) => b.score - a.score);
  const top = scores.slice(0, 25);
  const poll: Poll = {
    week: L.week,
    label,
    ranks: top.map((x, i) => ({
      tid: x.t.id,
      rank: i + 1,
      prev: prevRank.get(x.t.id) ?? null,
      w: x.s.w,
      l: x.s.l,
      pts: Math.round(1575 - i * 60 + (x.score - top[Math.min(i + 1, top.length - 1)].score) * 3),
    })),
  };
  L.polls.push(poll);
  for (const r of poll.ranks) {
    const s = team(L, r.tid).seasons[team(L, r.tid).seasons.length - 1];
    if (L.polls.length === 1 || label === "Preseason") s.apPre = r.rank;
    if (s.apBest === null || r.rank < s.apBest) s.apBest = r.rank;
    if (final) s.apFinal = r.rank;
  }
}

/** Selection committee score: predictive power plus resume. */
export function selectionScores(L: League): Map<number, number> {
  const pr = powerRanks(L);
  const out = new Map<number, number>();
  const wins = new Map<number, { q1: number; bad: number }>();
  for (const t of L.teams) wins.set(t.id, { q1: 0, bad: 0 });
  for (const g of L.games) {
    if (!g.played || g.type === "ncaa" || g.type === "nit" || g.type === "cbi") continue;
    const homeWon = g.hs > g.as;
    const w = homeWon ? g.home : g.away;
    const l = homeWon ? g.away : g.home;
    const wLoc = g.neutral ? 0 : homeWon ? 1 : -1; // winner location
    const lRank = pr.get(l) ?? 200;
    const wRank = pr.get(w) ?? 200;
    const q1cut = wLoc === 1 ? 30 : wLoc === 0 ? 50 : 75;
    if (lRank <= q1cut) wins.get(w)!.q1++;
    const badCut = wLoc === 1 ? 160 : 200; // loser at home vs bad team is worse
    if (wRank > badCut) wins.get(l)!.bad++;
  }
  for (const t of L.teams) {
    const s = t.seasons[t.seasons.length - 1];
    const q = wins.get(t.id)!;
    const pw = L.power[t.id]?.power ?? 0;
    // like the real committee: Quad 1 wins count most, so mid-majors with few chances get seeded lower
    out.set(t.id, pw + 0.38 * (s.w - s.l) + 1.3 * q.q1 - 1.6 * q.bad);
  }
  return out;
}
