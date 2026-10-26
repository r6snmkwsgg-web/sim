import type { BoxScore, Game, League, PbpEvent, Player, Team, TeamSeason } from "./types";
import { addNews, coachOf, getSink, playerName, roster, rngOf, team } from "./core";
import { simGame, type SimTeam } from "./sim/game";
import { resolveRotation } from "./sim/rotation";
import { addBox, seasonLine } from "./stats";
import { recordGameLine } from "./records";
import { currentRank } from "./rankings";

export function curSeason(t: Team): TeamSeason {
  return t.seasons[t.seasons.length - 1];
}

export function availablePlayers(L: League, tid: number): Player[] {
  const all = roster(L, tid);
  let avail = all.filter((p) => !p.redshirt && !p.injury);
  if (avail.length < 5) {
    // emergency: pull in the least-injured / redshirting players
    const extra = all
      .filter((p) => !avail.includes(p))
      .sort((a, b) => (a.injury?.games ?? 0) - (b.injury?.games ?? 0));
    avail = avail.concat(extra.slice(0, 5 - avail.length));
  }
  return avail;
}

const rotCache = new Map<string, { starters: number[]; minutes: Record<number, number> }>();

export function buildSimTeam(L: League, t: Team): SimTeam {
  const avail = availablePlayers(L, t.id);
  let rot;
  if (t.id === L.userTid && !t.rotation.auto) rot = resolveRotation(avail, t.rotation, roster(L, t.id));
  else {
    const key = `${t.id}:${avail.map((p) => p.id * 100 + p.ovr).join(",")}`;
    rot = rotCache.get(key);
    if (!rot) {
      rot = resolveRotation(avail, { auto: true, starters: [], minutes: {} });
      if (rotCache.size > 4000) rotCache.clear();
      rotCache.set(key, rot);
    }
  }
  return {
    tid: t.id,
    name: t.name,
    players: avail,
    starters: rot.starters,
    minutes: rot.minutes,
    strategy: t.strategy,
    tactics: coachOf(L, t.id)?.tactics ?? 50,
  };
}

const INJURIES: [number, number, number, string[]][] = [
  [0.5, 1, 2, ["Ankle sprain", "Back spasms", "Illness", "Bruised knee", "Jammed finger"]],
  [0.82, 3, 6, ["Sprained ankle", "Hamstring strain", "Concussion", "Hip pointer", "Groin strain"]],
  [0.95, 7, 14, ["Broken finger", "MCL sprain", "Stress reaction", "High ankle sprain", "Broken nose"]],
  [1, 15, 40, ["Torn meniscus", "Broken foot", "Torn ACL", "Fractured wrist", "Achilles strain"]],
];

export function injurePlayer(L: League, p: Player) {
  const rng = rngOf(L);
  const x = rng.next();
  for (const [cut, lo, hi, names] of INJURIES) {
    if (x <= cut) {
      const name = rng.pick(names);
      const games = name === "Torn ACL" ? rng.int(30, 45) : rng.int(lo, hi);
      p.injury = { name, games };
      if (p.tid === L.userTid) addNews(L, "injury", `${playerName(p)} (${name}) is expected to miss ${games} game${games > 1 ? "s" : ""}.`, { tid: p.tid ?? undefined, pid: p.id, user: true });
      return;
    }
  }
}

function applyTeamResult(L: League, g: Game, tid: number, pf: number, pa: number) {
  const t = team(L, tid);
  const s = curSeason(t);
  const won = pf > pa;
  const home = !g.neutral && g.home === tid;
  const away = !g.neutral && g.away === tid;
  if (won) {
    s.w++;
    s.streak = s.streak > 0 ? s.streak + 1 : 1;
  } else {
    s.l++;
    s.streak = s.streak < 0 ? s.streak - 1 : -1;
  }
  if (g.type === "conf") won ? s.cw++ : s.cl++;
  if (home) won ? s.hw++ : s.hl++;
  else if (away) won ? s.aw++ : s.al++;
  else won ? s.nw++ : s.nl++;
  s.pf += pf;
  s.pa += pa;
}

export function playGame(L: League, g: Game) {
  const rng = rngOf(L);
  const home = team(L, g.home);
  const away = team(L, g.away);
  const hs = buildSimTeam(L, home);
  const as = buildSimTeam(L, away);
  const isUser = g.home === L.userTid || g.away === L.userTid;
  const bigGame = g.type === "ncaa" && (g.tourney?.round ?? 0) >= 3;
  // the user's game prep applies to this game if it was for this opponent; either way it's used up
  if (isUser && L.prep) {
    const opp = g.home === L.userTid ? g.away : g.home;
    if (L.prep.opp === opp && L.prep.level > 0) {
      (g.home === L.userTid ? hs : as).prep = L.prep.level;
      g.prep = L.prep.level;
    }
    L.prep = undefined;
  }
  const res = simGame(hs, as, rng, {
    neutral: g.neutral,
    homeAdv: L.settings.homeCourt,
    pbp: isUser || bigGame,
    injuries: L.settings.injuries,
  });
  g.played = true;
  g.hs = res.home.pts;
  g.as = res.away.pts;
  g.ot = res.ot;
  g.hasBox = isUser || L.settings.keepAllBoxScores || g.type !== "nc" && g.type !== "conf";
  g.hasPbp = isUser || bigGame;

  // player stats
  const sides = [
    { t: home, lines: res.home.lines, opp: away },
    { t: away, lines: res.away.lines, opp: home },
  ];
  const byId = new Map<number, Player>();
  for (const p of hs.players) byId.set(p.id, p);
  for (const p of as.players) byId.set(p.id, p);
  for (const side of sides) {
    for (const line of side.lines) {
      const p = byId.get(line.pid);
      if (!p) continue;
      if (line.min <= 0 && !line.starter) continue;
      const s = seasonLine(p, L.season, side.t.id);
      addBox(s, line);
      const reb = line.orb + line.drb;
      if (line.pts > p.gameHigh.pts) p.gameHigh.pts = line.pts;
      if (reb > p.gameHigh.reb) p.gameHigh.reb = reb;
      if (line.ast > p.gameHigh.ast) p.gameHigh.ast = line.ast;
      recordGameLine(L, g, side.t.id, side.opp.id, line);
    }
  }
  applyTeamResult(L, g, home.id, res.home.pts, res.away.pts);
  applyTeamResult(L, g, away.id, res.away.pts, res.home.pts);

  // injuries: decrement existing, then apply new
  for (const t of [home, away]) {
    for (const p of roster(L, t.id)) {
      if (p.injury) {
        p.injury.games--;
        if (p.injury.games <= 0) {
          if (p.tid === L.userTid) addNews(L, "injury", `${playerName(p)} has returned from injury.`, { tid: p.tid, pid: p.id, user: true });
          p.injury = null;
        }
      }
    }
  }
  for (const inj of res.injuries) {
    const p = byId.get(inj.pid);
    if (p && !p.injury) injurePlayer(L, p);
  }

  // box score
  if (g.hasBox) {
    const box: BoxScore = {
      gid: g.id,
      season: g.season,
      day: g.day,
      home: { tid: home.id, pts: res.home.pts, halves: res.home.halves, lines: res.home.lines },
      away: { tid: away.id, pts: res.away.pts, halves: res.away.halves, lines: res.away.lines },
      ot: res.ot,
      neutral: g.neutral,
      type: g.type,
      poss: res.poss,
      pbp: g.hasPbp ? res.pbp : undefined,
    };
    getSink().box(L.id, box);
  }

  // news
  if (isUser) {
    const userHome = g.home === L.userTid;
    const us = userHome ? res.home.pts : res.away.pts;
    const them = userHome ? res.away.pts : res.home.pts;
    const opp = userHome ? away : home;
    const lines = userHome ? res.home.lines : res.away.lines;
    const top = lines.slice().sort((a, b) => b.pts - a.pts)[0];
    const loc = g.neutral ? "vs" : userHome ? "vs" : "at";
    const oppRank = currentRank(L, opp.id);
    g.oppRank = oppRank;
    g.oppEdge = (L.power[opp.id]?.power ?? 0) - (L.power[L.userTid]?.power ?? 0);
    if (us > them && oppRank) {
      const cs = curSeason(team(L, L.userTid));
      cs.rankedWins = (cs.rankedWins ?? 0) + 1;
    }
    const c = clutchShot(res.pbp, res.home.pts > res.away.pts ? 0 : 1);
    if (c) {
      const line = [...res.home.lines, ...res.away.lines].find((x) => x.pid === c.pid);
      if (line) g.clutch = { ...c, name: line.name };
    }
    addNews(
      L,
      "game",
      `${us > them ? "W" : "L"} ${us}-${them}${g.ot ? ` (${g.ot > 1 ? g.ot : ""}OT)` : ""} ${loc} ${oppRank ? `#${oppRank} ` : ""}${opp.name}. ${top ? `${top.name} led with ${top.pts} pts.` : ""}`,
      { tid: L.userTid, gid: g.id, user: true },
    );
  } else {
    // notable upsets
    const hr = currentRank(L, home.id);
    const ar = currentRank(L, away.id);
    const loserRank = res.home.pts > res.away.pts ? ar : hr;
    const winnerRank = res.home.pts > res.away.pts ? hr : ar;
    if (loserRank && loserRank <= 5 && (!winnerRank || winnerRank > 20) && g.type !== "ncaa") {
      const w = res.home.pts > res.away.pts ? home : away;
      const l = res.home.pts > res.away.pts ? away : home;
      addNews(L, "league", `Upset! ${w.name} knocks off #${loserRank} ${l.name}, ${Math.max(g.hs, g.as)}-${Math.min(g.hs, g.as)}.`, { tid: w.id, gid: g.id, user: false });
    }
  }
}

/** The go-ahead score of a game decided in the final seconds, if there was one. */
function clutchShot(pbp: PbpEvent[], winner: 0 | 1): { pid: number; side: 0 | 1; secs: number } | null {
  if (!pbp.length) return null;
  const lastPer = pbp[pbp.length - 1].per;
  const end = lastPer <= 2 ? lastPer * 1200 : 2400 + (lastPer - 2) * 300;
  let prevLead = 0;
  let pick: PbpEvent | null = null;
  for (const e of pbp) {
    const lead = winner === 0 ? e.hs - e.as : e.as - e.hs;
    if (lead > 0 && prevLead <= 0 && (e.k === "fg" || e.k === "ft") && e.m) pick = e;
    prevLead = lead;
  }
  if (!pick || pick.per !== lastPer || pick.p === undefined) return null;
  const secs = end - pick.t;
  return secs <= 5 ? { pid: pick.p, side: winner, secs: Math.max(0, secs) } : null;
}
