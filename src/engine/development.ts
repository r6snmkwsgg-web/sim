import type { League, Player, PracticeFocus, RatingKey, Team } from "./types";
import { RATING_KEYS } from "./types";
import { Rng, clamp } from "./rng";
import { OVR_WEIGHTS, updateOvr } from "./ratings";
import { coachOf, roster, rngOf } from "./core";
import { injurePlayer } from "./play";

export const FOCUS_KEYS: Record<PracticeFocus, RatingKey[]> = {
  balanced: [],
  shooting: ["three", "mid", "ft"],
  inside: ["ins", "str", "reb"],
  playmaking: ["hnd", "pas", "iq"],
  defense: ["perD", "intD", "stl", "blk"],
  rebounding: ["reb", "str", "blk"],
  conditioning: ["end", "ath"],
};

export const FOCUS_LABELS: Record<PracticeFocus, string> = {
  balanced: "Balanced",
  shooting: "Shooting",
  inside: "Inside Scoring",
  playmaking: "Playmaking",
  defense: "Defense",
  rebounding: "Rebounding",
  conditioning: "Conditioning",
};

/** Raise (or lower) a player's ratings so his overall moves by about `gain`. */
export function growPlayer(rng: Rng, p: Player, gain: number, teamFocus: PracticeFocus, indFocus: PracticeFocus | undefined) {
  if (Math.abs(gain) < 1e-6) return;
  const ow = OVR_WEIGHTS[p.pos];
  const tf = new Set(FOCUS_KEYS[teamFocus]);
  const inf = new Set(indFocus ? FOCUS_KEYS[indFocus] : []);
  const w: Partial<Record<RatingKey, number>> = {};
  let effect = 0;
  let total = 0;
  for (const k of RATING_KEYS) {
    let x = (ow[k] ?? 0) + 0.03;
    if (tf.has(k)) x *= 1.8;
    if (inf.has(k)) x *= 2.2;
    if (k === "ath" && teamFocus !== "conditioning") x *= 0.55;
    if (k === "end" && teamFocus === "conditioning") x += 0.08;
    x *= rng.uniform(0.5, 1.5);
    w[k] = x;
    total += x;
  }
  for (const k of RATING_KEYS) {
    w[k] = w[k]! / total;
    effect += (ow[k] ?? 0) * w[k]!;
  }
  if (effect <= 0) return;
  const c = gain / effect;
  for (const k of RATING_KEYS) {
    p.r[k] = clamp(Math.round((p.r[k] + c * w[k]!) * 100) / 100, 1, 99);
  }
  updateOvr(p);
  if (p.pot < p.ovr) p.pot = p.ovr;
}

function minutesPerGame(p: Player, season: number, tid: number | null): number {
  const s = p.stats.find((x) => x.season === season && x.tid === tid);
  return s && s.g ? s.min / s.g : 0;
}

const INTENSITY = [0, 0.75, 1, 1.3];

/** In-season weekly development driven by practice plans. */
export function weeklyDevelopment(L: League) {
  const rng = rngOf(L);
  for (const t of L.teams) {
    const plan = t.practice;
    const ch = coachOf(L, t.id);
    const dev = 0.6 + 0.8 * ((ch?.development ?? 50) / 100);
    const intensity = INTENSITY[plan.intensity];
    for (const p of roster(L, t.id)) {
      if (p.injury) continue;
      const gap = p.pot - p.ovr;
      const mpg = minutesPerGame(p, L.season, t.id);
      const mins = 1 + 0.25 * Math.min(1, mpg / 30);
      const we = 0.7 + 0.6 * (p.workEthic / 100);
      let gain = Math.max(0, gap) * 0.0065 * intensity * dev * we * mins * rng.uniform(0.4, 1.6);
      if (gap <= 0) gain = rng.normal(0, 0.06);
      growPlayer(rng, p, gain, plan.focus, plan.individual[p.id]);
      if (plan.intensity === 3 && L.settings.injuries && rng.chance(0.004)) injurePlayer(L, p);
    }
  }
}

const YEAR_RATE = [0, 0.36, 0.32, 0.3, 0.28, 0.25, 0.2];

/** Offseason development; `p.year` is the season just completed. */
export function offseasonDevelopment(L: League, p: Player, t: Team | undefined) {
  const rng = rngOf(L);
  const ch = t ? coachOf(L, t.id) : undefined;
  const dev = 0.6 + 0.8 * ((ch?.development ?? 50) / 100);
  const we = 0.7 + 0.6 * (p.workEthic / 100);
  const gap = Math.max(0, p.pot - p.ovr);
  const rate = YEAR_RATE[Math.min(6, Math.max(1, p.year))];
  // potential drifts: late bloomers and busts
  p.pot = Math.round(clamp(p.pot + rng.normal(0, 2.2), 20, 99));
  const gain = gap * rate * we * dev + rng.normal(0, 1.8);
  growPlayer(rng, p, gain, t?.practice.focus ?? "balanced", t?.practice.individual[p.id]);
  if (p.pot < p.ovr) p.pot = p.ovr;
}
