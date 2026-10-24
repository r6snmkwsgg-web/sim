// Calibration harness for the game sim: sims many games between generated
// teams and reports league-wide rates against real D1 averages.
//   npm run calibrate -- [games]

import { Rng, mean, sd } from "../src/engine/rng";
import { generateInitialRoster, talentLevel } from "../src/engine/gen/roster";
import { autoRotation } from "../src/engine/sim/rotation";
import { simGame, type SimTeam } from "../src/engine/sim/game";
import type { Player, Strategy } from "../src/engine/types";

const N_TEAMS = 80;
const GAMES = Number(process.argv[2] ?? 4000);
const rng = new Rng(12345);
let pid = 1;

interface T {
  tid: number;
  prestige: number;
  players: Player[];
  strength: number;
}

const teams: T[] = [];
for (let i = 0; i < N_TEAMS; i++) {
  const prestige = 8 + (90 * i) / (N_TEAMS - 1);
  const players = generateInitialRoster(rng, i, prestige, () => pid++, 14);
  const top8 = players.map((p) => p.ovr).sort((a, b) => b - a).slice(0, 8);
  teams.push({ tid: i, prestige, players, strength: mean(top8) });
}

const strat: Strategy = { tempo: 3, offense: "balanced", defense: "man", rebounding: "balanced" };
function simTeam(t: T): SimTeam {
  const rot = autoRotation(t.players);
  return { tid: t.tid, name: `T${t.tid}`, players: t.players, starters: rot.starters, minutes: rot.minutes, strategy: strat, tactics: 50 };
}

const agg = { poss: 0, pts: 0, fgm: 0, fga: 0, tpm: 0, tpa: 0, ftm: 0, fta: 0, orb: 0, drb: 0, ast: 0, stl: 0, blk: 0, tov: 0, pf: 0, games: 0 };
const margins: { diff: number; margin: number; homeWin: boolean }[] = [];
const playerPts = new Map<number, { pts: number; g: number; min: number }>();
let homeWins = 0;
const homeMargins: number[] = [];
const neutralMargins: number[] = [];
let ots = 0;
const t0 = Date.now();
for (let g = 0; g < GAMES; g++) {
  const a = teams[rng.int(0, N_TEAMS - 1)];
  let b = teams[rng.int(0, N_TEAMS - 1)];
  while (b === a) b = teams[rng.int(0, N_TEAMS - 1)];
  const neutral = g % 2 === 0;
  const res = simGame(simTeam(a), simTeam(b), rng, { neutral, homeAdv: 3.5, pbp: false, injuries: false });
  agg.games++;
  agg.poss += res.poss;
  if (res.ot) ots++;
  for (const side of [res.home, res.away]) {
    agg.pts += side.pts;
    for (const l of side.lines) {
      agg.fgm += l.fgm; agg.fga += l.fga; agg.tpm += l.tpm; agg.tpa += l.tpa; agg.ftm += l.ftm; agg.fta += l.fta;
      agg.orb += l.orb; agg.drb += l.drb; agg.ast += l.ast; agg.stl += l.stl; agg.blk += l.blk; agg.tov += l.tov; agg.pf += l.pf;
      const e = playerPts.get(l.pid) ?? { pts: 0, g: 0, min: 0 };
      e.pts += l.pts; e.g++; e.min += l.min;
      playerPts.set(l.pid, e);
    }
  }
  if (!neutral) {
    if (res.home.pts > res.away.pts) homeWins++;
    homeMargins.push(res.home.pts - res.away.pts);
  } else neutralMargins.push(res.home.pts - res.away.pts);
  margins.push({ diff: a.strength - b.strength, margin: res.home.pts - res.away.pts, homeWin: res.home.pts > res.away.pts });
}
const ms = (Date.now() - t0) / GAMES;
const tg = agg.games * 2;
const pct = (x: number) => (100 * x).toFixed(1) + "%";
const fga2 = agg.fga - agg.tpa;
const fgm2 = agg.fgm - agg.tpm;
console.log(`sim speed: ${ms.toFixed(3)} ms/game`);
console.log(`poss/40       ${(agg.poss / agg.games).toFixed(1)}   (D1 ~67.5)`);
console.log(`PPG           ${(agg.pts / tg).toFixed(1)}   (D1 ~72)`);
console.log(`pts/100       ${((100 * agg.pts) / (agg.poss * 2)).toFixed(1)}  (D1 ~106)`);
console.log(`FG%           ${pct(agg.fgm / agg.fga)}  (D1 ~44%)`);
console.log(`eFG%          ${pct((agg.fgm + 0.5 * agg.tpm) / agg.fga)}  (D1 ~50.5%)`);
console.log(`2P%           ${pct(fgm2 / fga2)}  (D1 ~51.5%)`);
console.log(`3P%           ${pct(agg.tpm / agg.tpa)}  (D1 ~34%)`);
console.log(`3PA rate      ${pct(agg.tpa / agg.fga)}  (D1 ~39%)`);
console.log(`FT%           ${pct(agg.ftm / agg.fta)}  (D1 ~71.5%)`);
console.log(`FTA/FGA       ${(agg.fta / agg.fga).toFixed(3)} (D1 ~0.32)`);
console.log(`TO%           ${pct(agg.tov / (agg.poss * 2))}  (D1 ~17%)`);
console.log(`ORB%          ${pct(agg.orb / (agg.orb + agg.drb - 0) )} of all reb; vs D1 ORB% ~29% of available`);
console.log(`STL%          ${pct(agg.stl / (agg.poss * 2))}  (D1 ~9%)`);
console.log(`BLK% of 2PA   ${pct(agg.blk / fga2)}  (D1 ~9%)`);
console.log(`AST/FGM       ${pct(agg.ast / agg.fgm)}  (D1 ~52%)`);
console.log(`FGA/team      ${(agg.fga / tg).toFixed(1)}  (D1 ~58)`);
console.log(`PF/team       ${(agg.pf / tg).toFixed(1)}  (D1 ~17)`);
console.log(`REB/team      ${((agg.orb + agg.drb) / tg).toFixed(1)}  (D1 ~35)`);
console.log(`home win%     ${pct(homeWins / (GAMES / 2))}  (D1 ~62-65% overall, inflated by scheduling)`);
console.log(`home margin   ${(mean(homeMargins) - mean(neutralMargins)).toFixed(2)} pts (target ~3.2)`);
console.log(`OT rate       ${pct(ots / GAMES)}  (D1 ~6%)`);

// strength difference vs result
const buckets = [0, 3, 6, 9, 12, 16, 20, 30];
for (let i = 0; i < buckets.length - 1; i++) {
  const set = margins.filter((m) => Math.abs(m.diff) >= buckets[i] && Math.abs(m.diff) < buckets[i + 1]);
  if (!set.length) continue;
  const favWin = set.filter((m) => (m.diff > 0 ? m.margin > 0 : m.margin < 0)).length / set.length;
  const favMargin = mean(set.map((m) => (m.diff > 0 ? m.margin : -m.margin)));
  console.log(`strength gap ${buckets[i]}-${buckets[i + 1]}: n=${set.length} fav win ${pct(favWin)} avg margin ${favMargin.toFixed(1)} sd ${sd(set.map((m) => (m.diff > 0 ? m.margin : -m.margin))).toFixed(1)}`);
}
const ppg = [...playerPts.values()].filter((e) => e.g >= 20).map((e) => e.pts / e.g).sort((a, b) => b - a);
console.log(`top scorer PPG ${ppg.slice(0, 5).map((x) => x.toFixed(1)).join(", ")}  (D1 leaders ~23-27)`);
const mpg = [...playerPts.values()].filter((e) => e.g >= 20).map((e) => e.min / e.g).sort((a, b) => b - a);
console.log(`top MPG ${mpg.slice(0, 5).map((x) => x.toFixed(1)).join(", ")}; players >=30mpg: ${mpg.filter((m) => m >= 30).length}/${N_TEAMS}`);
console.log(`team strength range: ${teams[0].strength.toFixed(1)} .. ${teams[N_TEAMS - 1].strength.toFixed(1)}; level(50)=${talentLevel(50).toFixed(1)}`);
