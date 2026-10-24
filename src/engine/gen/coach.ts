import type { Coach } from "../types";
import { Rng, clamp } from "../rng";
import { randomName, randomRace } from "./player";

export function generateCoach(rng: Rng, id: number, tid: number | null, prestige: number, season: number): Coach {
  const race = rng.chance(0.62) ? "white" : randomRace(rng);
  const { first, last } = randomName(rng, race);
  const base = 30 + prestige * 0.5;
  const r = () => Math.round(clamp(base + rng.normal(0, 11), 15, 99));
  return {
    id,
    first,
    last,
    tid,
    user: false,
    age: rng.int(36, 66),
    recruiting: r(),
    development: r(),
    tactics: r(),
    rep: Math.round(clamp(prestige + rng.normal(0, 10), 5, 99)),
    faceSeed: rng.seed32(),
    race,
    hired: season - rng.int(0, 9),
    seasons: [],
    security: 60,
    retired: false,
    awards: [],
  };
}
