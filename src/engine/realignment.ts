// Conference realignment: rising programs in lower-tier leagues get invited up.
// Invitations are decided during the coaching carousel and take effect when
// the next season begins.

import type { League, Team } from "./types";
import { mean, distanceMiles } from "./rng";
import { addNews, rngOf, team } from "./core";
import { reindex } from "./core";

const REQUIRED = [0, 999, 74, 66, 58]; // prestige needed to be invited out of a tier

function centroid(L: League, cid: number): { lat: number; lon: number } {
  const ms = L.teams.filter((t) => t.cid === cid);
  return { lat: mean(ms.map((t) => t.lat)), lon: mean(ms.map((t) => t.lon)) };
}

function eligible(L: League, t: Team): boolean {
  const c = L.conferences[t.cid];
  if (c.tier <= 1) return false;
  if (t.prestige < REQUIRED[c.tier]) return false;
  const avg = mean(L.teams.filter((x) => x.cid === c.id).map((x) => x.prestige));
  if (t.prestige - avg < 14) return false;
  // sustained success, not a one-year spike
  const recent = t.seasons.slice(-2);
  return recent.length >= 2 && recent.every((s) => s.prestige >= REQUIRED[c.tier] - 6);
}

function destination(L: League, t: Team): number | null {
  const c = L.conferences[t.cid];
  const targetTier = c.tier - 1;
  const options = L.conferences.filter((x) => x.tier === targetTier && L.teams.filter((m) => m.cid === x.id).length < 18);
  if (!options.length) return null;
  options.sort((a, b) => {
    const ca = centroid(L, a.id);
    const cb = centroid(L, b.id);
    return distanceMiles(t.lat, t.lon, ca.lat, ca.lon) - distanceMiles(t.lat, t.lon, cb.lat, cb.lon);
  });
  return options[0].id;
}

/** During the carousel: decide which programs are invited to move up. */
export function proposeRealignment(L: League) {
  const rng = rngOf(L);
  L.realign = [];
  const sizes = new Map<number, number>();
  for (const c of L.conferences) sizes.set(c.id, L.teams.filter((t) => t.cid === c.id).length);
  let moves = 0;
  const cands = L.teams.filter((t) => eligible(L, t)).sort((a, b) => b.prestige - a.prestige);
  for (const t of cands) {
    if (moves >= 3) break;
    if ((sizes.get(t.cid) ?? 0) <= 6) continue;
    const to = destination(L, t);
    if (to === null) continue;
    const isUser = t.id === L.userTid;
    if (!isUser && !rng.chance(0.35)) continue;
    L.realign.push({ tid: t.id, toCid: to, accepted: isUser ? null : true });
    sizes.set(t.cid, (sizes.get(t.cid) ?? 0) - 1);
    sizes.set(to, (sizes.get(to) ?? 0) + 1);
    moves++;
    const toC = L.conferences[to];
    if (isUser) {
      addNews(L, "milestone", `The ${toC.name} has invited ${t.name} to join! Accept or decline on the Coach & Jobs page before the new season.`, { tid: t.id, user: true });
    } else {
      addNews(L, "league", `Realignment: ${t.name} will leave the ${L.conferences[t.cid].short} for the ${toC.short} next season.`, { tid: t.id, user: false });
    }
  }
}

/** At the start of the new season: apply accepted moves. */
export function applyRealignment(L: League) {
  for (const r of L.realign ?? []) {
    if (r.accepted !== true) continue;
    const t = team(L, r.tid);
    const from = L.conferences[t.cid];
    t.cid = r.toCid;
    if (t.id === L.userTid) addNews(L, "milestone", `${t.name} officially joins the ${L.conferences[r.toCid].name}, leaving the ${from.short}.`, { tid: t.id, user: true });
  }
  L.realign = [];
  reindex(L);
}
