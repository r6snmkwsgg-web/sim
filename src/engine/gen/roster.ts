import type { Player, Pos } from "../types";
import { Rng, clamp } from "../rng";
import { generatePlayer, assignJersey } from "./player";

/** Typical overall of a team's core players for a given prestige. */
export function talentLevel(prestige: number): number {
  return 38 + 0.26 * prestige;
}

const CLASS_BONUS = [0, -4.5, -1.5, 1.5, 3.5, 4.5];
const GROWTH_LEFT = [0, 13, 9, 5, 2, 0];

const POS_TEMPLATE: Pos[] = ["PG", "PG", "SG", "SG", "SG", "SF", "SF", "SF", "PF", "PF", "PF", "C", "C"];

export function randomClassYear(rng: Rng): number {
  const x = rng.next();
  if (x < 0.29) return 1;
  if (x < 0.55) return 2;
  if (x < 0.78) return 3;
  if (x < 0.97) return 4;
  return 5;
}

/** Potential for a player of a given current overall and class. */
export function potFor(rng: Rng, ovr: number, year: number): number {
  return Math.round(ovr + Math.max(0, GROWTH_LEFT[Math.min(5, year)] + rng.normal(0, 4)));
}

export function generateInitialRoster(
  rng: Rng,
  tid: number,
  prestige: number,
  nextId: () => number,
  size: number,
): Player[] {
  const level = talentLevel(prestige) + rng.normal(0, 2.5);
  const positions = POS_TEMPLATE.slice();
  while (positions.length < size) positions.push(rng.pick(["PG", "SG", "SF", "PF", "C"] as Pos[]));
  rng.shuffle(positions);
  const used = new Set<number>();
  const players: Player[] = [];
  for (let i = 0; i < size; i++) {
    const walkOn = i >= size - 2;
    const year = randomClassYear(rng);
    let ovr = level + CLASS_BONUS[year] + rng.normal(0, 6);
    if (walkOn) ovr = level - 13 + rng.normal(0, 4);
    ovr = Math.round(clamp(ovr, 22, 82));
    const pot = potFor(rng, ovr, year);
    const p = generatePlayer(rng, { id: nextId(), ovr, pot, year, pos: positions[i] });
    p.tid = tid;
    p.status = "active";
    p.eligUsed = year - 1;
    if (year === 5) {
      p.usedRedshirt = true;
      p.eligUsed = 3;
    } else if (year >= 2 && rng.chance(0.12)) {
      p.usedRedshirt = true;
      p.eligUsed = year - 2;
    }
    p.jersey = assignJersey(rng, used);
    players.push(p);
  }
  return players;
}
