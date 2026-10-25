import type { Coach } from "../types";
import { Rng, clamp } from "../rng";
import { randomName, randomRace } from "./player";

export function generateCoach(rng: Rng, id: number, tid: number | null, prestige: number, season: number): Coach {
  const race = rng.chance(0.62) ? "white" : randomRace(rng);
  const { first, last } = randomName(rng, race);
  // recruiting pull tracks the size of the job; teaching and game planning are found at every level
  const r = (base: number) => Math.round(clamp(base + rng.normal(0, 11), 15, 99));
  const recruitBase = 30 + prestige * 0.5;
  const craftBase = 40 + prestige * 0.25;
  return {
    id,
    first,
    last,
    tid,
    user: false,
    age: rng.int(36, 66),
    recruiting: r(recruitBase),
    development: r(craftBase),
    tactics: r(craftBase),
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
