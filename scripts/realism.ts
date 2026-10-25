// Realism report: sims full seasons (offseason included) and compares the
// league to real Division I men's basketball.
//   npx tsx scripts/realism.ts [seasons] [seed]

import { createLeague } from "../src/engine/league";
import { advancePhase, isDayPhase, simDay } from "../src/engine/advance";
import { mean, sd } from "../src/engine/rng";
import type { League } from "../src/engine/types";
import { setTuning } from "../src/engine/sim/game";
// TUNE="formSd,scoreEffect,skillScale" to try engine settings
if (process.env.TUNE) {
  const [f, se, sk] = process.env.TUNE.split(",").map(Number);
  setTuning(f, se, sk);
}

const SEASONS = Number(process.argv[2] ?? 4);
const SEED = Number(process.argv[3] ?? 11);
const L: League = createLeague({ name: "Realism", teamSlug: "drake", coachFirst: "A", coachLast: "B", seed: SEED });

type Row = { key: string; label: string; real: string; lo: number; hi: number; fmt?: (x: number) => string };
// targets: real D1 men's basketball, recent seasons
const ROWS: Row[] = [
  { key: "ppg", label: "Points per team-game", real: "72-74", lo: 71, hi: 75 },
  { key: "poss", label: "Possessions per game", real: "~67.5", lo: 66, hi: 69.5 },
  { key: "fg", label: "FG%", real: "~44.5%", lo: 43.5, hi: 45.5 },
  { key: "tp", label: "3P%", real: "~34%", lo: 33, hi: 35 },
  { key: "tpr", label: "3PA share of FGA", real: "~39%", lo: 37, hi: 41 },
  { key: "ft", label: "FT%", real: "~71.5%", lo: 70, hi: 73 },
  { key: "fta", label: "FTA per FGA", real: "~0.32", lo: 0.29, hi: 0.35, fmt: (x) => x.toFixed(3) },
  { key: "tov", label: "Turnover rate", real: "~17%", lo: 16, hi: 18 },
  { key: "homeConf", label: "Home win% (conference games)", real: "~61%", lo: 58, hi: 64 },
  { key: "homeEdge", label: "Home edge (pts, vs power)", real: "~3.0-3.5", lo: 2.7, hi: 3.8 },
  { key: "ot", label: "Overtime rate", real: "~5.4%", lo: 4.6, hi: 6.5 },
  { key: "noise", label: "Game margin noise (sd)", real: "~11", lo: 10, hi: 12 },
  { key: "ppg1", label: "Scoring leader (ppg)", real: "25-28", lo: 24.5, hi: 29 },
  { key: "ppg10", label: "10th in scoring (ppg)", real: "~22", lo: 20.5, hi: 23.5 },
  { key: "rpg1", label: "Rebounding leader (rpg)", real: "12-13", lo: 11.3, hi: 14 },
  { key: "rpg10", label: "10th in rebounding", real: "~10", lo: 9.2, hi: 10.8 },
  { key: "apg1", label: "Assists leader (apg)", real: "7.5-9.5", lo: 7.2, hi: 9.8 },
  { key: "apg10", label: "10th in assists", real: "~6.2", lo: 5.6, hi: 6.8 },
  { key: "bpg1", label: "Blocks leader (bpg)", real: "3.5-4", lo: 3.2, hi: 4.3 },
  { key: "spg1", label: "Steals leader (spg)", real: "2.6-3", lo: 2.4, hi: 3.2 },
  { key: "best", label: "Best record (wins)", real: "33-36", lo: 32, hi: 37 },
  { key: "w30", label: "30-win teams", real: "6-10", lo: 5, hi: 11 },
  { key: "unbeat", label: "Unbeaten regular seasons", real: "~0.1/yr", lo: 0, hi: 0.5 },
  { key: "champ1x", label: "Champion is a 1 seed (exp.)", real: "~65%", lo: 50, hi: 75 },
  { key: "ff1x", label: "Final Four spots for 1 seeds (exp.)", real: "~40%", lo: 32, hi: 48 },
  { key: "up12", label: "12 seeds beat 5 seeds (exp.)", real: "~35%", lo: 28, hi: 40 },
  { key: "up13", label: "13 seeds beat 4 seeds (exp.)", real: "~21%", lo: 16, hi: 26 },
  { key: "up14", label: "14 seeds beat 3 seeds (exp.)", real: "~15%", lo: 10, hi: 19 },
  { key: "up15", label: "15 seeds beat 2 seeds (exp.)", real: "~7%", lo: 4, hi: 10 },
  { key: "up16", label: "16 seeds beat 1 seeds (exp.)", real: "~1.3%", lo: 0.3, hi: 3 },
  { key: "coach", label: "Head coaching changes", real: "50-60", lo: 42, hi: 68 },
  { key: "portal", label: "Transfer portal entrants", real: "2,000-2,300", lo: 1700, hi: 2600, fmt: (x) => Math.round(x).toString() },
  { key: "portalPct", label: "Portal entrants % of players", real: "~40%", lo: 32, hi: 46 },
  { key: "transfers", label: "Transfers landing at D1 schools", real: "~1,300-1,500", lo: 1100, hi: 1700, fmt: (x) => Math.round(x).toString() },
  { key: "draftCol", label: "College players drafted", real: "~36 of 59", lo: 30, hi: 42 },
  { key: "draftFr", label: "Freshmen drafted", real: "~10-15", lo: 8, hi: 17 },
];

let spare: number | null = null;
function gauss(): number {
  if (spare !== null) {
    const v = spare;
    spare = null;
    return v;
  }
  let u = 0, v = 0;
  while (u === 0) u = Math.random();
  v = Math.random();
  const r = Math.sqrt(-2 * Math.log(u));
  spare = r * Math.sin(2 * Math.PI * v);
  return r * Math.cos(2 * Math.PI * v);
}

function phi(z: number): number {
  const t = 1 / (1 + 0.2316419 * Math.abs(z));
  const d = 0.3989423 * Math.exp((-z * z) / 2);
  const p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return z > 0 ? 1 - p : p;
}

const acc: Record<string, number[]> = {};
const put = (k: string, v: number) => (acc[k] ??= []).push(v);
const minutesByClass: Record<string, number> = {};

for (let s = 0; s < SEASONS; s++) {
  // ---------- the season ----------
  while (L.phase !== "seasonEnd") {
    if (isDayPhase(L)) simDay(L);
    else advancePhase(L);
  }
  const season = L.season;
  const played = L.games.filter((g) => g.played);
  // box totals from every player's season line
  const t = { pts: 0, fgm: 0, fga: 0, tpm: 0, tpa: 0, ftm: 0, fta: 0, orb: 0, drb: 0, tov: 0 };
  const lines: { pts: number; reb: number; ast: number; blk: number; stl: number; g: number }[] = [];
  for (const p of L.players) {
    for (const st of p.stats) {
      if (st.season !== season || !st.g) continue;
      for (const k of Object.keys(t) as (keyof typeof t)[]) t[k] += st[k];
      lines.push({ pts: st.pts, reb: st.orb + st.drb, ast: st.ast, blk: st.blk, stl: st.stl, g: st.g });
      const cls = st.rs ? "RS" : ["", "FR", "SO", "JR", "SR", "GR"][Math.min(5, st.year)] ?? "?";
      minutesByClass[cls] = (minutesByClass[cls] ?? 0) + st.min;
    }
  }
  const teamGames = played.length * 2;
  const poss = (t.fga - t.orb + t.tov + 0.475 * t.fta) / teamGames;
  put("ppg", t.pts / teamGames);
  put("poss", poss);
  put("fg", (100 * t.fgm) / t.fga);
  put("tp", (100 * t.tpm) / t.tpa);
  put("tpr", (100 * t.tpa) / t.fga);
  put("ft", (100 * t.ftm) / t.fta);
  put("fta", t.fta / t.fga);
  put("tov", (100 * t.tov) / (poss * teamGames));
  const conf = played.filter((g) => g.type === "conf" && !g.neutral);
  put("homeConf", (100 * conf.filter((g) => g.hs > g.as).length) / conf.length);
  put("ot", (100 * played.filter((g) => g.ot).length) / played.length);
  {
    const xs: number[] = [];
    const ys: number[] = [];
    const resid: number[] = [];
    for (const g of played) {
      xs.push((L.power[g.home]?.power ?? 0) - (L.power[g.away]?.power ?? 0) + (g.neutral ? 0 : L.settings.homeCourt));
      ys.push(g.hs - g.as);
    }
    const mx = mean(xs), my = mean(ys);
    let c = 0, v = 0;
    for (let i = 0; i < xs.length; i++) {
      c += (xs[i] - mx) * (ys[i] - my);
      v += (xs[i] - mx) ** 2;
    }
    const slope = c / v;
    for (let i = 0; i < xs.length; i++) resid.push(ys[i] - (my + slope * (xs[i] - mx)));
    put("noise", sd(resid));
    const home = played.filter((g) => !g.neutral).map((g) => g.hs - g.as - ((L.power[g.home]?.power ?? 0) - (L.power[g.away]?.power ?? 0)));
    put("homeEdge", mean(home));
    // expected first-round upsets from power gaps
    const ncaa = L.brackets.find((b) => b.key === "ncaa")!;
    const sdn = sd(resid);
    for (const g of ncaa.games) {
      if (g.round !== 0 || g.a === null || g.b === null || g.sa === null || g.sb === null) continue;
      const hi = Math.min(g.sa, g.sb);
      const lo = Math.max(g.sa, g.sb);
      if (lo - hi < 7) continue;
      const [ht, lt] = g.sa < g.sb ? [g.a, g.b] : [g.b, g.a];
      const gap = (L.power[ht]?.power ?? 0) - (L.power[lt]?.power ?? 0);
      put(`up${lo}`, 100 * phi((-gap * slope) / sdn));
    }
    // Monte Carlo: replay this bracket many times from power ratings and game noise
    {
      const r0 = ncaa.games.filter((g) => g.round === 0).sort((a, b) => a.slot - b.slot);
      let champ1 = 0, ff1 = 0;
      const N = 2000;
      const seedOfT = new Map<number, number>();
      for (const g of ncaa.games) {
        if (g.a !== null && g.sa !== null) seedOfT.set(g.a, g.sa);
        if (g.b !== null && g.sb !== null) seedOfT.set(g.b, g.sb);
      }
      for (let it = 0; it < N; it++) {
        let alive = r0.map((g) => [g.a!, g.b!]).flat();
        let round = 0;
        while (alive.length > 1) {
          const next: number[] = [];
          for (let k = 0; k < alive.length; k += 2) {
            const a = alive[k], b = alive[k + 1];
            const m = slope * ((L.power[a]?.power ?? 0) - (L.power[b]?.power ?? 0)) + sdn * gauss();
            next.push(m > 0 ? a : b);
          }
          alive = next;
          round++;
          if (alive.length === 4) ff1 += alive.filter((x) => seedOfT.get(x) === 1).length / 4;
        }
        if (seedOfT.get(alive[0]) === 1) champ1++;
      }
      put("champ1x", (100 * champ1) / N);
      put("ff1x", (100 * ff1) / N);
    }
    // champion and Final Four seeds
    const seedOf = new Map<number, number>();
    for (const g of ncaa.games) {
      if (g.a !== null && g.sa !== null) seedOf.set(g.a, g.sa);
      if (g.b !== null && g.sb !== null) seedOf.set(g.b, g.sb);
    }
    const h = L.history[L.history.length - 1];
    put("champ1", h.champion !== null && seedOf.get(h.champion) === 1 ? 100 : 0);
    put("ff1", (100 * h.finalFour.filter((x) => seedOf.get(x) === 1).length) / 4);
  }
  // power by national rank and where each seed line ranks
  {
    const pw = L.teams.map((tm) => L.power[tm.id]?.power ?? 0).sort((a, b) => b - a);
    for (const r of [1, 5, 10, 25, 50, 75, 100, 150, 200, 300]) put(`pw${r}`, pw[r - 1]);
    const rankOf = new Map(L.teams.map((tm) => [tm.id, 0]));
    L.teams
      .slice()
      .sort((a, b) => (L.power[b.id]?.power ?? 0) - (L.power[a.id]?.power ?? 0))
      .forEach((tm, i) => rankOf.set(tm.id, i + 1));
    const ncaa = L.brackets.find((b) => b.key === "ncaa")!;
    for (const g of ncaa.games) {
      if (g.round !== 0) continue;
      if (g.a !== null && g.sa !== null) put(`seed${g.sa}`, rankOf.get(g.a)!);
      if (g.b !== null && g.sb !== null) put(`seed${g.sb}`, rankOf.get(g.b)!);
    }
  }
  const lead = (f: (l: (typeof lines)[number]) => number) => {
    const v = lines.filter((l) => l.g >= 20).map((l) => f(l) / l.g).sort((a, b) => b - a);
    return [v[0], v[9]];
  };
  const [p1, p10] = lead((l) => l.pts);
  const [r1, r10] = lead((l) => l.reb);
  const [a1, a10] = lead((l) => l.ast);
  put("ppg1", p1);
  put("ppg10", p10);
  put("rpg1", r1);
  put("rpg10", r10);
  put("apg1", a1);
  put("apg10", a10);
  put("bpg1", lead((l) => l.blk)[0]);
  put("spg1", lead((l) => l.stl)[0]);
  const recs = L.teams.map((tm) => tm.seasons[tm.seasons.length - 1]);
  put("best", Math.max(...recs.map((r) => r.w)));
  put("w30", recs.filter((r) => r.w >= 30).length);
  // unbeaten through the regular season: no losses in non-postseason games
  const regLoss = new Map<number, number>();
  for (const g of played) {
    if (g.type !== "nc" && g.type !== "conf") continue;
    const loser = g.hs > g.as ? g.away : g.home;
    regLoss.set(loser, (regLoss.get(loser) ?? 0) + 1);
  }
  put("unbeat", L.teams.filter((tm) => !regLoss.get(tm.id)).length);

  // ---------- the offseason ----------
  const rostered = L.players.filter((p) => p.status === "active" && p.tid !== null).length;
  const coachBefore = new Map(L.teams.map((tm) => [tm.id, tm.coachId]));
  advancePhase(L); // seasonEnd -> carousel
  advancePhase(L); // carousel -> draft
  put("coach", L.teams.filter((tm) => tm.coachId !== coachBefore.get(tm.id)).length);
  const picks = L.draftHistory.filter((d) => d.season === season + 1);
  put("draftCol", picks.filter((d) => d.tid >= 0).length);
  put("draftFr", picks.filter((d) => d.tid >= 0 && d.year <= 1).length);
  for (const y of [1, 2, 3, 4, 5]) put(`draftY${y}`, picks.filter((d) => d.tid >= 0 && d.year === y).length);
  // coach security spread before the carousel (diagnostic)
  for (const c of L.coaches) if (!c.user && c.tid !== null) put("sec", c.security);
  const transfersBefore = L.transferLog?.length ?? 0;
  advancePhase(L); // draft -> portal
  const entrants = L.players.filter((p) => p.status === "portal").length;
  put("portal", entrants);
  // share of everyone who was on a roster this season, as the real figure counts it
  put("portalPct", (100 * entrants) / Math.max(1, rostered));
  while ((L.phase as string) === "portal") advancePhase(L);
  const moves = (L.transferLog ?? []).slice(transfersBefore).filter((m) => m.season === season + 1 || m.season === season);
  put("transfers", moves.filter((m) => m.to !== null && m.to !== m.from).length);
  advancePhase(L); // signing -> new season
  for (const tm of L.teams) put("rosterSize", L.players.filter((p) => p.tid === tm.id && p.status === "active").length);
  process.stdout.write(`season ${season} done\n`);
}

console.log(`\nRealism report: ${SEASONS} seasons, seed ${SEED}\n`);
console.log(`${"metric".padEnd(36)} ${"sim".padStart(9)}   ${"real".padEnd(14)} status`);
let ok = 0;
for (const r of ROWS) {
  const v = acc[r.key];
  if (!v?.length) {
    console.log(`${r.label.padEnd(36)} ${"-".padStart(9)}   ${r.real.padEnd(14)} n/a`);
    continue;
  }
  const m = mean(v);
  const good = m >= r.lo && m <= r.hi;
  if (good) ok++;
  const f = r.fmt ? r.fmt(m) : m.toFixed(1);
  console.log(`${r.label.padEnd(36)} ${f.padStart(9)}   ${r.real.padEnd(14)} ${good ? "ok" : m < r.lo ? "LOW" : "HIGH"}`);
}
console.log(`\n${ok}/${ROWS.length} within range`);
// real: KenPom AdjEM by rank (recent seasons) converted to points per game at ~68 possessions
const REAL_PW: Record<number, number> = { 1: 25, 5: 20, 10: 17.5, 25: 13.5, 50: 9.5, 75: 6.8, 100: 4.1, 150: 0.5, 200: -2.2, 300: -8 };
console.log(`\npower by rank (sim / real): ${Object.keys(REAL_PW).map((r) => `#${r} ${mean(acc[`pw${r}`] ?? [0]).toFixed(1)}/${REAL_PW[Number(r)]}`).join("  ")}`);
// real: typical KenPom rank by seed line
const REAL_SEED: Record<number, string> = { 1: "2", 2: "7", 3: "11", 4: "15", 5: "20", 6: "25", 7: "29", 8: "33", 9: "37", 10: "42", 11: "45", 12: "60", 13: "90", 14: "115", 15: "160", 16: "230" };
console.log(`seed ranks (sim / real): ${Object.keys(REAL_SEED).map((sd) => `${sd}:${mean(acc[`seed${sd}`] ?? [0]).toFixed(0)}/${REAL_SEED[Number(sd)]}`).join(" ")}`);
const totMin = Object.values(minutesByClass).reduce((a, b) => a + b, 0);
console.log(`drafted by class: ${[1, 2, 3, 4, 5].map((y) => `${["", "FR", "SO", "JR", "SR", "5th"][y]} ${mean(acc[`draftY${y}`] ?? [0]).toFixed(1)}`).join(", ")}; coach security mean ${mean(acc.sec ?? [0]).toFixed(0)}, <25: ${(100 * (acc.sec ?? []).filter((x) => x < 25).length / Math.max(1, (acc.sec ?? []).length)).toFixed(0)}%`);
console.log(`roster size at tip-off: avg ${mean(acc.rosterSize ?? [0]).toFixed(1)}, under 12: ${(100 * (acc.rosterSize ?? []).filter((x) => x < 12).length / Math.max(1, (acc.rosterSize ?? []).length)).toFixed(1)}%`);
console.log(`minutes by class: ${Object.entries(minutesByClass).sort().map(([k, v]) => `${k} ${((100 * v) / totMin).toFixed(0)}%`).join(", ")}`);
