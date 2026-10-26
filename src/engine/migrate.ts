// Bring older saves up to the current data model. Every field added after the
// first release gets a default here, so leagues never break across updates.

import type { League } from "./types";
import confData from "./data/conferences.json";
import { userTeam } from "./core";
import { staffPoints } from "./recruiting";

export const DATA_VERSION = 3;

export function migrate(L: League): League {
  L.transferLog ??= [];
  L.realign ??= [];
  L.vacancies ??= [];
  L.achievements ??= [];
  L.board ??= [];
  L.settings.autoRecruit ??= false;
  L.settings.portalRate ??= 1;
  const campus = new Map((confData as { id: string; campusRounds?: number }[]).map((c) => [c.id, c.campusRounds ?? 0]));
  for (const c of L.conferences) c.campusRounds ??= campus.get(c.slug) ?? 0;
  for (const t of L.teams) {
    for (const s of t.seasons) s.prestigeStart ??= s.prestige;
    t.boosters ??= boostersFor(t.slug);
  }
  if ((L.version ?? 1) < 3) {
    // weekly points doubled (about 85-115): top up this week's points, keeping what was already spent
    const spent = Math.max(0, L.recruitPtsMax - L.recruitPts);
    L.recruitPtsMax = staffPoints(L, userTeam(L)) + (L.pointsBonus ?? 0);
    L.recruitPts = L.settings.autoRecruit ? 0 : Math.max(0, L.recruitPtsMax - spent);
  }
  L.version = Math.max(L.version ?? 1, DATA_VERSION);
  return L;
}

/** A stable booster-wealth value for saves made before boosters existed. */
function boostersFor(slug: string): number {
  let h = 2166136261;
  for (let i = 0; i < slug.length; i++) h = Math.imul(h ^ slug.charCodeAt(i), 16777619);
  const u1 = ((h >>> 0) % 100000) / 100000 + 0.000005;
  const u2 = ((Math.imul(h, 2654435761) >>> 0) % 100000) / 100000;
  const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  return Math.round(Math.min(3.2, Math.max(0.4, Math.exp(0.5 * z))) * 100) / 100;
}
