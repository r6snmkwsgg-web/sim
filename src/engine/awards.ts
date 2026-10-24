import type { AwardEntry, League, Player, PlayerSeasonStats, SeasonAwards } from "./types";
import { addNews, coach, playerName, team } from "./core";
import { curSeason } from "./play";
import { fmt1, gameScore, winPct } from "./stats";

interface Cand {
  p: Player;
  s: PlayerSeasonStats;
  tid: number;
  cid: number;
  val: number;
  def: number;
}

function line(s: PlayerSeasonStats, kind: "off" | "def" = "off"): string {
  const g = s.g || 1;
  if (kind === "def") return `SPG ${fmt1(s.stl / g)}, BPG ${fmt1(s.blk / g)}, RPG ${fmt1((s.orb + s.drb) / g)}`;
  return `PPG ${fmt1(s.pts / g)}, RPG ${fmt1((s.orb + s.drb) / g)}, APG ${fmt1(s.ast / g)}`;
}

function entry(name: string, c: Cand, kind: "off" | "def" = "off"): AwardEntry {
  return { name, pid: c.p.id, tid: c.tid, playerName: playerName(c.p), line: line(c.s, kind) };
}

export function computeAwards(L: League): SeasonAwards {
  const cands: Cand[] = [];
  for (const p of L.players) {
    if (p.status !== "active") continue;
    for (const s of p.stats) {
      if (s.season !== L.season || s.g < Math.max(8, 0)) continue;
      const t = team(L, s.tid);
      const ts = curSeason(t);
      const minPg = s.min / s.g;
      if (minPg < 12) continue;
      const gs = gameScore(s) / s.g;
      const wp = winPct(ts.w, ts.l);
      const gamesFactor = Math.min(1, s.g / 25);
      const val = gs * (0.8 + 0.4 * wp) * gamesFactor + (L.power[t.id]?.power ?? 0) * 0.05;
      const def = ((1.3 * s.stl + 1.1 * s.blk + 0.25 * s.drb) / s.g + 0.03 * (p.r.perD + p.r.intD) + 0.04 * (L.power[t.id]?.power ?? 0)) * gamesFactor;
      cands.push({ p, s, tid: t.id, cid: t.cid, val, def });
    }
  }
  cands.sort((a, b) => b.val - a.val);
  const national: AwardEntry[] = [];
  const award = (name: string, c: Cand | undefined, kind: "off" | "def" = "off") => {
    if (!c) return;
    national.push(entry(name, c, kind));
    c.p.awards.push({ season: L.season, name });
  };
  award("Player of the Year", cands[0]);
  award("Defensive Player of the Year", cands.slice().sort((a, b) => b.def - a.def)[0], "def");
  award("Freshman of the Year", cands.find((c) => c.s.year === 1 && !c.s.rs));
  award("Sixth Man of the Year", cands.find((c) => c.s.gs <= c.s.g * 0.35 && c.s.g >= 20));
  const improved = cands
    .map((c) => {
      const prev = c.p.hist.find((h) => h.season === L.season - 1);
      return { c, d: prev ? c.p.ovr - prev.ovr : 0 };
    })
    .filter((x) => x.d > 0)
    .sort((a, b) => b.d - a.d || b.c.val - a.c.val)[0];
  if (improved) award("Most Improved Player", improved.c);

  // coach of the year: wins above preseason expectation
  let bestCoach: { tid: number; score: number } | null = null;
  for (const t of L.teams) {
    const s = curSeason(t);
    const exp = 0.5 + (s.apPre ? (26 - s.apPre) * 0.012 : 0) + (t.prestige - 50) * 0.004;
    const post = s.post?.event === "ncaa" ? { Champion: 0.25, "Runner-up": 0.18, "Final Four": 0.13, "Elite Eight": 0.08, "Sweet 16": 0.05 }[s.post.result] ?? 0.02 : 0;
    const score = winPct(s.w, s.l) - exp + post + (s.w + s.l > 0 ? 0 : -1);
    if (!bestCoach || score > bestCoach.score) bestCoach = { tid: t.id, score };
  }
  if (bestCoach) {
    const t = team(L, bestCoach.tid);
    const c = coach(L, t.coachId);
    const s = curSeason(t);
    if (c) {
      national.push({ name: "Coach of the Year", cid: c.id, tid: t.id, playerName: `${c.first} ${c.last}`, line: `${s.w}-${s.l}${s.post?.event === "ncaa" ? `, ${s.post.result}` : ""}` });
      c.awards.push({ season: L.season, name: "Coach of the Year" });
    }
  }

  // All-America
  const allAmerica: AwardEntry[][] = [];
  for (let k = 0; k < 3; k++) {
    const name = ["First Team All-America", "Second Team All-America", "Third Team All-America"][k];
    const grp = cands.slice(k * 5, k * 5 + 5);
    allAmerica.push(grp.map((c) => entry(name, c)));
    for (const c of grp) c.p.awards.push({ season: L.season, name });
  }

  // conferences
  const conf: SeasonAwards["conf"] = {};
  for (const cf of L.conferences) {
    const cc = cands.filter((c) => c.cid === cf.id);
    if (!cc.length) continue;
    const awards: AwardEntry[] = [];
    const give = (name: string, c: Cand | undefined, kind: "off" | "def" = "off") => {
      if (!c) return;
      const e = entry(`${cf.short} ${name}`, c, kind);
      e.confId = cf.id;
      awards.push(e);
      c.p.awards.push({ season: L.season, name: `${cf.short} ${name}` });
    };
    give("Player of the Year", cc[0]);
    give("Defensive Player of the Year", cc.slice().sort((a, b) => b.def - a.def)[0], "def");
    give("Freshman of the Year", cc.find((c) => c.s.year === 1 && !c.s.rs));
    const teams: AwardEntry[][] = [];
    for (let k = 0; k < 2; k++) {
      const name = k === 0 ? `All-${cf.short} First Team` : `All-${cf.short} Second Team`;
      const grp = cc.slice(k * 5, k * 5 + 5);
      teams.push(grp.map((c) => ({ ...entry(name, c), confId: cf.id })));
      for (const c of grp) c.p.awards.push({ season: L.season, name });
    }
    // conference coach of the year: best conference record relative to prestige
    const members = L.teams.filter((t) => t.cid === cf.id);
    const best = members
      .map((t) => {
        const s = curSeason(t);
        return { t, score: winPct(s.cw, s.cl) - t.prestige / 200 + (s.confRank === 1 ? 0.1 : 0) };
      })
      .sort((a, b) => b.score - a.score)[0];
    if (best) {
      const ch = coach(L, best.t.coachId);
      const s = curSeason(best.t);
      if (ch) {
        awards.push({ name: `${cf.short} Coach of the Year`, cid: ch.id, tid: best.t.id, playerName: `${ch.first} ${ch.last}`, line: `${s.cw}-${s.cl} in conference`, confId: cf.id });
        ch.awards.push({ season: L.season, name: `${cf.short} Coach of the Year` });
      }
    }
    conf[cf.id] = { awards, teams };
  }

  // Final Four MOP: best player on the champion
  const ncaa = L.brackets.find((b) => b.key === "ncaa");
  if (ncaa?.champion != null) {
    const mop = cands.find((c) => c.tid === ncaa.champion);
    if (mop) {
      national.push(entry("Final Four Most Outstanding Player", mop));
      mop.p.awards.push({ season: L.season, name: "Final Four Most Outstanding Player" });
    }
  }

  const sa: SeasonAwards = { season: L.season, national, allAmerica, conf };
  // user news
  for (const a of [...national, ...allAmerica.flat()]) {
    if (a.tid === L.userTid) addNews(L, "award", `${a.playerName} wins ${a.name}!`, { tid: a.tid, pid: a.pid, user: true });
  }
  const poy = national.find((a) => a.name === "Player of the Year");
  if (poy) addNews(L, "award", `${poy.playerName} (${team(L, poy.tid).name}) is the national Player of the Year.`, { tid: poy.tid, pid: poy.pid, user: poy.tid === L.userTid });
  return sa;
}
