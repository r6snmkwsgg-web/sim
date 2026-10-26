// Big moments: after each sim, compare the league with how it was before and
// turn the best changes (upsets, buzzer-beaters, rank jumps, titles, big
// commitments, finished goals) into full-screen celebrations.

import { useSyncExternalStore } from "react";
import type { League, Player } from "../engine/types";
import { playerName, team } from "../engine/core";
import { currentRank } from "../engine/rankings";
import { curSeason } from "../engine/play";
import { classRankings, classUnrated, ratingsHidden } from "../engine/recruiting";

export interface Moment {
  priority: number;
  kicker: string;
  title: string;
  sub?: string;
  /** team whose colors fill the card */
  tid: number;
  logos?: number[];
  pid?: number;
  link?: { to: string; label: string };
  celebrate?: boolean;
  sad?: boolean;
}

interface Snap {
  season: number;
  phase: League["phase"];
  played: Set<number>;
  rank: number | null;
  streak: number;
  confChamp: boolean;
  confTourney: string | null;
  post: string | null;
  event: string | null;
  unrated: boolean;
  recruits: Map<number, number | null>;
  goals: Set<string>;
  offers: number;
}

function userGames(L: League) {
  return L.games.filter((g) => g.played && (g.home === L.userTid || g.away === L.userTid));
}

/** Recruits the user is chasing or has landed. */
function watched(L: League): Player[] {
  return L.players.filter((p) => {
    const r = p.recruit;
    if (!r || (p.status !== "recruit" && p.status !== "portal")) return false;
    return r.committedTo === L.userTid || r.offers.includes(L.userTid) || L.board.includes(p.id) || (r.interest[L.userTid] ?? 0) > 3;
  });
}

export function snapshot(L: League): Snap {
  const s = curSeason(team(L, L.userTid));
  return {
    season: L.season,
    phase: L.phase,
    played: new Set(userGames(L).map((g) => g.id)),
    rank: currentRank(L, L.userTid),
    streak: s.streak,
    confChamp: s.confChamp,
    confTourney: s.confTourney,
    post: s.post ? `${s.post.event}:${s.post.result}` : null,
    event: s.event ? `${s.event.key}:${s.event.place}` : null,
    unrated: classUnrated(L),
    recruits: new Map(watched(L).map((p) => [p.id, p.recruit!.committedTo])),
    goals: new Set((L.goals?.season === L.season ? L.goals.list : []).filter((g) => g.done).map((g) => g.id)),
    offers: L.jobOffers.length,
  };
}

const stars = (n: number) => "★".repeat(n);

/** Schools other than the winner that wanted him most. */
function beat(p: Player, winner: number): number[] {
  return Object.entries(p.recruit!.interest)
    .filter(([k]) => Number(k) !== winner)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 2)
    .map(([k]) => Number(k));
}

export function momentsSince(L: League, b: Snap): Moment[] {
  const out: Moment[] = [];
  if (b.season !== L.season) return out;
  const me = L.userTid;
  const ut = team(L, me);
  const s = curSeason(ut);
  const base = `/l/${L.id}`;

  // games
  for (const g of userGames(L)) {
    if (b.played.has(g.id)) continue;
    const home = g.home === me;
    const us = home ? g.hs : g.as;
    const them = home ? g.as : g.hs;
    const opp = team(L, home ? g.away : g.home);
    const won = us > them;
    const score = `${us}-${them}${g.ot ? ` (${g.ot > 1 ? g.ot : ""}OT)` : ""}`;
    const box = { to: `${base}/game/${g.id}`, label: "Box score" };
    const mySide = home ? 0 : 1;
    if (g.clutch && g.clutch.side === mySide) {
      out.push({ priority: 92, kicker: "Buzzer beater!", title: `${g.clutch.name} wins it`, sub: `With ${g.clutch.secs <= 1 ? "no time" : `${Math.round(g.clutch.secs)} seconds`} left: ${ut.short} ${score} over ${opp.name}`, tid: me, logos: [me, opp.id], pid: g.clutch.pid, link: box, celebrate: true });
      continue;
    }
    if (g.clutch && !won) {
      out.push({ priority: 58, kicker: "Heartbreaker", title: `${g.clutch.name} beats you at the horn`, sub: `${opp.name} ${them}-${us}`, tid: opp.id, logos: [opp.id, me], link: box, sad: true });
      continue;
    }
    const big = (g.oppEdge ?? 0) >= 5 || (g.oppRank !== undefined && g.oppRank !== null && g.oppRank <= 10);
    if (won && big) {
      const r = g.oppRank ? `#${g.oppRank} ` : "";
      out.push({ priority: g.oppRank && g.oppRank <= 5 ? 88 : 80, kicker: "Upset!", title: `You knocked off ${r}${opp.name}`, sub: `${ut.short} ${score}`, tid: me, logos: [me, opp.id], link: box, celebrate: true });
    } else if (won && g.oppRank) {
      out.push({ priority: 66, kicker: "Ranked win", title: `${ut.short} beats #${g.oppRank} ${opp.name}`, sub: score, tid: me, logos: [me, opp.id], link: box, celebrate: true });
    }
  }

  // the polls
  const rank = currentRank(L, me);
  if (rank !== null && rank !== b.rank) {
    if (rank === 1) out.push({ priority: 96, kicker: "No. 1 in the country", title: `${ut.name} is the top team in America`, sub: "The AP poll is out.", tid: me, logos: [me], link: { to: `${base}/rankings`, label: "Rankings" }, celebrate: true });
    else if (b.rank === null) out.push({ priority: 72, kicker: "You're ranked", title: `#${rank} ${ut.name}`, sub: "Into the AP Top 25.", tid: me, logos: [me], link: { to: `${base}/rankings`, label: "Rankings" }, celebrate: true });
    else if (rank <= 10 && b.rank > 10) out.push({ priority: 74, kicker: "Top 10", title: `Up to #${rank}`, sub: `From #${b.rank} last week.`, tid: me, logos: [me], link: { to: `${base}/rankings`, label: "Rankings" }, celebrate: true });
    else if (b.rank - rank >= 6) out.push({ priority: 50, kicker: "Climbing", title: `Up to #${rank}`, sub: `From #${b.rank} last week.`, tid: me, logos: [me], link: { to: `${base}/rankings`, label: "Rankings" } });
  }
  for (const n of [5, 10, 15, 20, 25, 30]) {
    if (s.streak >= n && b.streak < n) out.push({ priority: 52 + n, kicker: "On fire", title: `${n} straight wins`, sub: `${ut.name} is ${s.w}-${s.l}.`, tid: me, logos: [me], celebrate: n >= 10 });
  }

  // titles and March
  if (s.confChamp && !b.confChamp)
    out.push({ priority: 78, kicker: "Conference champions", title: `${ut.name} wins the regular season`, sub: `${s.cw}-${s.cl} in conference play.`, tid: me, logos: [me], link: { to: `${base}/standings`, label: "Standings" }, celebrate: true });
  if (s.event?.place === 1 && b.event !== `${s.event.key}:1`)
    out.push({ priority: 74, kicker: "Early-season title", title: `${s.event.name} champions`, sub: `${ut.name} won all ${s.event.of === 8 ? "three" : "two"} games.`, tid: me, logos: [me], link: { to: `${base}/events`, label: "Bracket" }, celebrate: true });
  if (s.confTourney === "Champion" && b.confTourney !== "Champion")
    out.push({ priority: 86, kicker: "Cut down the nets", title: `${L.conferences[ut.cid].short} tournament champions`, sub: "Automatic bid to the NCAA Tournament.", tid: me, logos: [me], link: { to: `${base}/conf-tourneys`, label: "Bracket" }, celebrate: true });
  const post = s.post ? `${s.post.event}:${s.post.result}` : null;
  if (s.post && post !== b.post) {
    const p = s.post;
    if (b.post === null) {
      if (p.event === "ncaa") out.push({ priority: 89, kicker: "Selection Sunday", title: "You're dancing!", sub: `${ut.name} is a ${p.seed} seed in the NCAA Tournament.`, tid: me, logos: [me], link: { to: `${base}/tournaments`, label: "See the bracket" }, celebrate: true });
      else out.push({ priority: 40, kicker: "Selection Sunday", title: `${p.event.toUpperCase()} bid`, sub: `A ${p.seed} seed in the ${p.event.toUpperCase()}.`, tid: me, logos: [me], link: { to: `${base}/nit`, label: "Bracket" } });
    } else if (p.event === "ncaa") {
      const step: Record<string, [number, string, string]> = {
        "Round of 32": [62, "Survive and advance", "On to the Round of 32"],
        "Sweet 16": [72, "Sweet 16", "Into the second weekend"],
        "Elite Eight": [80, "Elite Eight", "One win from the Final Four"],
        "Final Four": [93, "Final Four", `${ut.name} is going to the Final Four`],
        Championship: [95, "Title game", "Playing for a national championship"],
        Champion: [100, "National champions", `${ut.name} wins it all`],
      };
      const st = step[p.result];
      if (st) out.push({ priority: st[0], kicker: st[1], title: st[2], sub: `${ut.name} · ${p.seed} seed`, tid: me, logos: [me], link: { to: `${base}/tournaments`, label: "Bracket" }, celebrate: true });
    }
  }

  // recruiting drama
  const byId = new Map(L.players.map((x) => [x.id, x]));
  for (const [pid, wasTid] of b.recruits) {
    const p = byId.get(pid);
    if (!p?.recruit) continue;
    const r = p.recruit;
    const was = wasTid ?? null;
    const now = r.committedTo;
    if (now === was) continue;
    const name = playerName(p);
    const link = { to: `${base}/player/${p.id}`, label: "His page" };
    // before the rankings come out nobody knows how many stars he is
    const unrated = ratingsHidden(L, p);
    const st = unrated ? 3 : r.stars;
    const starTxt = unrated ? "" : `${stars(r.stars)} `;
    if (now === me) {
      const over = beat(p, me);
      out.push({
        priority: 60 + st * 6,
        kicker: was !== null ? "Flipped!" : "Committed!",
        title: `${starTxt}${name} picks ${ut.short}`,
        sub: `${r.kind === "portal" ? "Transfer" : `${p.pos} from ${p.city}, ${p.state}`}${over.length ? `. He chose you over ${over.map((t) => team(L, t).name).join(" and ")}.` : "."}`,
        tid: me,
        logos: [me, ...over],
        pid: p.id,
        link,
        celebrate: true,
      });
    } else if (was === me) {
      out.push({ priority: 70, kicker: "Decommitment", title: `${name} backs off his pledge`, sub: now !== null ? `He's flipped to ${team(L, now).name}.` : "He's back on the market. Win him back.", tid: now ?? me, logos: now !== null ? [now, me] : [me], pid: p.id, link, sad: true });
    } else if (now !== null && was === null && (r.offers.includes(me) || (!unrated && r.stars >= 3))) {
      out.push({ priority: 34 + st * 4, kicker: "Lost one", title: `${team(L, now).name} lands ${starTxt}${name}`, sub: "A recruit you were after went elsewhere.", tid: now, logos: [now, me], pid: p.id, link, sad: true });
    }
  }
  // the rankings come out: did one of your early targets turn out to be a gem?
  if (b.unrated && !classUnrated(L) && L.season === b.season) {
    const mine = watched(L)
      .filter((p) => p.recruit!.kind === "hs")
      .sort((a, b2) => a.recruit!.rank - b2.recruit!.rank);
    const top = mine[0];
    if (top) {
      const r = top.recruit!;
      out.push({
        priority: 58 + r.stars * 5,
        kicker: "Rankings are out",
        title: `${playerName(top)} is a ${stars(r.stars)}`,
        sub: `No. ${r.rank} in the class.${r.early?.includes(me) ? " You got in early, so he still takes you seriously." : ""}`,
        tid: me,
        logos: [me],
        pid: top.id,
        link: { to: `${base}/player/${top.id}`, label: "His page" },
        celebrate: r.stars >= 4,
      });
    } else out.push({ priority: 30, kicker: "Rankings are out", title: "The new class is ranked", sub: "Stars and national rankings are on the board now.", tid: me, logos: [me], link: { to: `${base}/recruiting`, label: "Recruiting board" } });
  }
  if (L.phase === "signing" && b.phase !== "signing") {
    const cr = classRankings(L).find((x) => x.tid === me);
    out.push({ priority: 76, kicker: "Signing Day", title: cr && cr.n ? `${cr.n} signee${cr.n === 1 ? "" : "s"}: the #${cr.rank} class` : "Signing Day is over", sub: "Your next class is locked in.", tid: me, logos: [me], link: { to: `${base}/classes`, label: "Class rankings" }, celebrate: !!cr && cr.n > 0 });
  }

  // goals and jobs
  for (const g of L.goals?.season === L.season ? L.goals.list : []) {
    if (g.done && !b.goals.has(g.id)) out.push({ priority: 68, kicker: g.stretch ? "Stretch goal complete" : "Goal complete", title: g.text, sub: `Reward: ${g.reward.text}.`, tid: me, logos: [me], link: { to: base, label: "Your goals" }, celebrate: true });
  }
  if (L.jobOffers.length > b.offers) {
    const o = L.jobOffers[L.jobOffers.length - 1];
    out.push({ priority: 64, kicker: "Job offer", title: `${team(L, o.tid).name} wants you`, sub: "Decide on the Coach & Jobs page.", tid: o.tid, logos: [o.tid], link: { to: `${base}/coach`, label: "Coach & Jobs" } });
  }
  return out;
}

// ---------------- the queue the overlay shows ----------------
const MAX_PER_SIM = 4;
let queue: Moment[] = [];
let more = 0;
const listeners = new Set<() => void>();
function emit() {
  for (const l of listeners) l();
}

export function pushMoments(ms: Moment[]) {
  if (!ms.length) return;
  const top = ms.slice().sort((a, b) => b.priority - a.priority);
  queue = [...queue, ...top.slice(0, MAX_PER_SIM)];
  more += Math.max(0, top.length - MAX_PER_SIM);
  emit();
}

export function popMoment() {
  queue = queue.slice(1);
  if (!queue.length) more = 0;
  emit();
}

export function clearMoments() {
  queue = [];
  more = 0;
  emit();
}

let snapVersion = 0;
function bump() {
  snapVersion++;
}
listeners.add(bump);

export function useMoments(): { queue: Moment[]; more: number } {
  useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => snapVersion,
  );
  return { queue, more };
}
