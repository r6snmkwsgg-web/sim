// Multi-season stability check: sims full seasons with every system running.
//   npx tsx scripts/seasons.ts [seasons] [seed]

import { createLeague } from "../src/engine/league";
import { advancePhase, isDayPhase, simDay } from "../src/engine/advance";
import { roster, team, getMemorySink } from "../src/engine/core";
import { mean, sd } from "../src/engine/rng";
import { rosterStrength } from "../src/engine/rankings";
import type { League } from "../src/engine/types";

import { setTuning } from "../src/engine/sim/game";
// TUNE="formSd,scoreEffect,skillScale" to try engine settings
if (process.env.TUNE) {
  const [f, se, sk] = process.env.TUNE.split(",").map(Number);
  setTuning(f, se, sk);
}
const SEASONS = Number(process.argv[2] ?? 3);
const SEED = Number(process.argv[3] ?? 7);

const t0 = Date.now();
const L: League = createLeague({ name: "Test", teamSlug: "kentucky", coachFirst: "Test", coachLast: "Coach", seed: SEED });
console.log(`create: ${Date.now() - t0}ms, teams ${L.teams.length}, players ${L.players.length}, games ${L.games.length}`);

const seedWins: Record<string, [number, number]> = {};
const seedExp: Record<string, number[]> = {};
// normal CDF (Abramowitz-Stegun)
function phi(z: number): number {
  const t = 1 / (1 + 0.2316419 * Math.abs(z));
  const d = 0.3989423 * Math.exp((-z * z) / 2);
  const p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return z > 0 ? 1 - p : p;
}

function report() {
  const strengths = L.teams.map((t) => rosterStrength(L, t.id));
  const sizes = L.teams.map((t) => roster(L, t.id).length);
  const byYear: Record<number, number[]> = {};
  for (const p of L.players) if (p.status === "active") (byYear[p.eligUsed + 1] ??= []).push(p.ovr);
  const prest = L.teams.map((t) => t.prestige);
  console.log(
    `  strength mean ${mean(strengths).toFixed(1)} sd ${sd(strengths).toFixed(1)} max ${Math.max(...strengths).toFixed(1)} min ${Math.min(...strengths).toFixed(1)} | roster size ${Math.min(...sizes)}-${Math.max(...sizes)} avg ${mean(sizes).toFixed(1)} | prestige mean ${mean(prest).toFixed(1)} sd ${sd(prest).toFixed(1)}`,
  );
  console.log(`  ovr by elig year: ${Object.entries(byYear).map(([y, a]) => `${y}:${mean(a).toFixed(1)}(${a.length})`).join(" ")}`);
  const bands = [0, 20, 35, 50, 65, 80, 101];
  const parts: string[] = [];
  for (let i = 0; i < bands.length - 1; i++) {
    const ts = L.teams.filter((t) => t.prestige >= bands[i] && t.prestige < bands[i + 1]);
    if (ts.length) parts.push(`${bands[i]}-${bands[i + 1]}:${mean(ts.map((t) => rosterStrength(L, t.id))).toFixed(1)}(${ts.length})`);
  }
  console.log(`  strength by prestige band: ${parts.join(" ")}`);
  const csz = L.conferences.map((c) => L.teams.filter((t) => t.cid === c.id).length);
  const coachSk = L.coaches.filter((c) => c.tid !== null).map((c) => (c.recruiting + c.development + c.tactics) / 3);
  console.log(`  conf sizes ${Math.min(...csz)}-${Math.max(...csz)}; coach skill mean ${mean(coachSk).toFixed(1)}; prestige>=90: ${L.teams.filter((t) => t.prestige >= 90).length}, >=80: ${L.teams.filter((t) => t.prestige >= 80).length}`);
  const pp = L.players.filter((p) => p.status === "active").map((p) => p.ovr).sort((a, b) => b - a);
  console.log(`  top player ovrs: ${pp.slice(0, 8).join(",")}; #100: ${pp[99]}; #500: ${pp[499]}`);
}

report();
for (let s = 0; s < SEASONS; s++) {
  const ts = Date.now();
  advancePhase(L); // preseason -> regular
  const commitLog: string[] = [];
  let lastWeek = -1;
  while (isDayPhase(L) || L.phase === "selection") {
    if (L.phase === "selection") advancePhase(L);
    else simDay(L);
    if (L.week !== lastWeek && L.week % 4 === 0) {
      lastWeek = L.week;
      const c = L.players.filter((p) => p.recruit?.kind === "hs" && p.recruit.committedTo !== null).length;
      commitLog.push(`w${L.week}:${c}`);
    }
  }
  console.log(`  commits by week: ${commitLog.join(" ")}`);
  const tSeason = Date.now() - ts;
  // upset tracking
  const ncaa = L.brackets.find((b) => b.key === "ncaa")!;
  for (const g of ncaa.games) {
    if (g.round !== 0 || g.winner === null || g.sa === null || g.sb === null) continue;
    const hi = Math.min(g.sa, g.sb);
    const lo = Math.max(g.sa, g.sb);
    const key = `${hi}v${lo}`;
    const e = (seedWins[key] ??= [0, 0]);
    const hiTeam = g.sa < g.sb ? g.a : g.b;
    if (g.winner === hiTeam) e[0]++;
    e[1]++;
  }
  // expected upset chance from each matchup's power gap and this season's game-level noise
  {
    const xs: number[] = [];
    const ys: number[] = [];
    for (const g of L.games) {
      if (!g.played) continue;
      xs.push((L.power[g.home]?.power ?? 0) - (L.power[g.away]?.power ?? 0) + (g.neutral ? 0 : L.settings.homeCourt));
      ys.push(g.hs - g.as);
    }
    const mx = mean(xs), my = mean(ys);
    let c = 0, v = 0;
    for (let i = 0; i < xs.length; i++) { c += (xs[i] - mx) * (ys[i] - my); v += (xs[i] - mx) ** 2; }
    const slope = c / v;
    const resid = sd(ys.map((y, i) => y - (my + slope * (xs[i] - mx))));
    for (const g of ncaa.games) {
      if (g.round !== 0 || g.a === null || g.b === null || g.sa === null || g.sb === null) continue;
      const [hi, lo] = g.sa < g.sb ? [g.a, g.b] : [g.b, g.a];
      const gap = (L.power[hi]?.power ?? 0) - (L.power[lo]?.power ?? 0);
      (seedExp[`${Math.min(g.sa, g.sb)}v${Math.max(g.sa, g.sb)}`] ??= []).push(phi((-gap * slope) / resid));
    }
    console.log(`  power->margin slope ${slope.toFixed(2)}, game noise sd ${resid.toFixed(1)}`);
  }
  const seedPow: Record<number, number[]> = {};
  for (const g of ncaa.games) {
    if (g.round !== 0) continue;
    for (const [tid, sd0] of [[g.a, g.sa], [g.b, g.sb]] as const) if (tid !== null && sd0 !== null) (seedPow[sd0] ??= []).push(L.power[tid]?.power ?? 0);
  }
  console.log(`  avg power by seed: ${Object.entries(seedPow).map(([k, v]) => `${k}:${mean(v).toFixed(0)}`).join(" ")}`);
  const h = L.history[L.history.length - 1];
  const champ = team(L, h.champion!);
  const games = L.games.filter((g) => g.played).length;
  // game-level realism: home edge (vs power gap), overtime rate, scoring leaders
  const played = L.games.filter((g) => g.played);
  const resid = played.filter((g) => !g.neutral).map((g) => g.hs - g.as - ((L.power[g.home]?.power ?? 0) - (L.power[g.away]?.power ?? 0)));
  const ots = played.filter((g) => g.ot).length;
  console.log(`  home edge after power gap ${mean(resid).toFixed(2)} pts; OT rate ${((100 * ots) / played.length).toFixed(1)}%; home win ${((100 * played.filter((g) => !g.neutral && g.hs > g.as).length) / Math.max(1, played.filter((g) => !g.neutral).length)).toFixed(1)}%`);
  const ppg = L.players
    .map((p) => p.stats.find((x) => x.season === L.season))
    .filter((x): x is NonNullable<typeof x> => !!x && x.g >= 20)
    .map((x) => x.pts / x.g)
    .sort((a, b) => b - a);
  console.log(`  scoring leaders ${ppg.slice(0, 6).map((v) => v.toFixed(1)).join(", ")}; #25 ${ppg[24]?.toFixed(1)}; #100 ${ppg[99]?.toFixed(1)}`);
  console.log(`\nSeason ${L.season}: ${games} games in ${tSeason}ms. Champion ${champ.name} (prestige ${champ.prestige.toFixed(0)}), runner-up ${team(L, h.runnerUp!).name}. Final Four: ${h.finalFour.map((t) => team(L, t).name).join(", ")}`);
  console.log(`  POY ${h.poy?.playerName} (${h.poy ? team(L, h.poy.tid).name : ""}) ${h.poy?.line}. User: ${h.userResult}`);
  const recs = L.players.filter((p) => p.recruit?.kind === "hs");
  const signed = recs.filter((p) => p.recruit!.stage === "signed" || p.recruit!.stage === "committed").length;
  console.log(`  HS recruits: ${recs.length}, committed/signed by season end: ${signed}`);
  const fives = recs.filter((p) => p.recruit!.stars === 5 && p.recruit!.committedTo !== null);
  console.log(`  5-star destinations prestige: ${fives.map((p) => team(L, p.recruit!.committedTo!).prestige.toFixed(0)).join(",")}`);
  const t1 = Date.now();
  advancePhase(L); // seasonEnd -> carousel
  advancePhase(L); // carousel -> draft
  console.log(`  draft picks this year: ${L.draftHistory.filter((d) => d.season === L.season + 1).length}`);
  advancePhase(L); // draft -> portal
  const portalN = L.players.filter((p) => p.status === "portal").length;
  while (L.phase === "portal") advancePhase(L);
  console.log(`  portal entrants ${portalN}, transfers completed ${L.transfers.length}`);
  const recs2 = L.players.filter((p) => p.recruit?.kind === "hs");
  console.log(`  after signing day: signed ${recs2.filter((p) => p.recruit!.stage === "signed").length}, unsigned ${recs2.filter((p) => p.recruit!.stage === "unsigned").length}`);
  const moves = (L.realign ?? []).map((r) => `${team(L, r.tid).name}->${L.conferences[r.toCid].short}`);
  if (moves.length) console.log(`  realignment: ${moves.join(", ")}`);
  advancePhase(L); // signing -> preseason (rollover)
  console.log(`  offseason ${Date.now() - t1}ms; players in memory ${L.players.length}; archived players ${getMemorySink().players.length}`);
  report();
}
console.log("\nNCAA first-round favorite win rates:");
for (const [k, [w, n]] of Object.entries(seedWins).sort((a, b) => Number(a[0].split("v")[0]) - Number(b[0].split("v")[0]))) {
  console.log(`  ${k}: ${w}/${n} (${((100 * w) / n).toFixed(0)}%), expected upset rate ${(100 * mean(seedExp[k] ?? [0])).toFixed(0)}%`);
}
console.log(`total ${(Date.now() - t0) / 1000}s`);
