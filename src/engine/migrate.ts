// Bring older saves up to the current data model. Every field added after the
// first release gets a default here, so leagues never break across updates.

import type { League } from "./types";

export const DATA_VERSION = 2;

export function migrate(L: League): League {
  L.transferLog ??= [];
  L.realign ??= [];
  L.vacancies ??= [];
  L.achievements ??= [];
  L.board ??= [];
  L.settings.autoRecruit ??= false;
  for (const t of L.teams) {
    for (const s of t.seasons) s.prestigeStart ??= s.prestige;
  }
  L.version = Math.max(L.version ?? 1, DATA_VERSION);
  return L;
}
