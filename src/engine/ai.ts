// AI coaching decisions: strategy selection, redshirts, roster trimming.

import type { League, Player, Strategy, Team, Tempo } from "./types";
import { mean } from "./rng";
import { roster, rngOf } from "./core";

export function chooseStrategy(L: League, t: Team, players: Player[]): Strategy {
  const rng = rngOf(L);
  const top = players.slice().sort((a, b) => b.ovr - a.ovr).slice(0, 8);
  if (!top.length) return { tempo: 3, offense: "balanced", defense: "man", rebounding: "balanced" };
  const three = mean(top.map((p) => p.r.three));
  const inside = mean(top.map((p) => (p.r.ins + p.r.str) / 2));
  const ath = mean(top.map((p) => p.r.ath));
  const end = mean(top.map((p) => p.r.end));
  const perD = mean(top.map((p) => p.r.perD));
  const intD = mean(top.map((p) => p.r.intD));
  const reb = mean(top.map((p) => p.r.reb));
  const offense = three - inside > 5 ? "perimeter" : inside - three > 6 ? "inside" : "balanced";
  let defense: Strategy["defense"] = "man";
  if (ath > 58 && end > 58 && rng.chance(0.5)) defense = "press";
  else if (intD - perD > 6 || rng.chance(0.12)) defense = "zone";
  let tempo: Tempo = 3;
  const x = ath - 52 + rng.normal(0, 5);
  if (x > 8) tempo = 5;
  else if (x > 3) tempo = 4;
  else if (x < -8) tempo = 1;
  else if (x < -3) tempo = 2;
  const rebounding = reb > 58 ? "crash" : reb < 45 && rng.chance(0.5) ? "getback" : "balanced";
  return { tempo, offense, defense, rebounding };
}

/** AI redshirt decisions in the preseason. */
export function aiRedshirts(L: League, t: Team) {
  const rng = rngOf(L);
  const ps = roster(L, t.id).slice().sort((a, b) => b.ovr - a.ovr);
  ps.forEach((p, i) => {
    p.redshirt = false;
    if (i >= 10 && !p.usedRedshirt && p.eligUsed === 0 && p.year <= 2 && rng.chance(0.55)) p.redshirt = true;
  });
}
