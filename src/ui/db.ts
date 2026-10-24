// IndexedDB persistence. One record holds the live league; separate stores
// keep everything that has left memory so history is never lost.

import { openDB, type DBSchema, type IDBPDatabase } from "idb";
import type { BoxScore, League, Player, SeasonArchive } from "../engine/types";

export interface LeagueMeta {
  id: string;
  name: string;
  teamName: string;
  teamAbbrev: string;
  colors: [string, string];
  coach: string;
  season: number;
  phase: string;
  record: string;
  created: number;
  updated: number;
}

type WithLid<T> = T & { lid: string };

interface Schema extends DBSchema {
  meta: { key: string; value: LeagueMeta };
  states: { key: string; value: League };
  players: { key: [string, number]; value: WithLid<Player> };
  boxes: { key: [string, number]; value: WithLid<BoxScore> };
  seasons: { key: [string, number]; value: WithLid<SeasonArchive> };
}

let dbp: Promise<IDBPDatabase<Schema>> | null = null;

export function db(): Promise<IDBPDatabase<Schema>> {
  if (!dbp) {
    dbp = openDB<Schema>("hardwood-dynasty", 1, {
      upgrade(d) {
        d.createObjectStore("meta", { keyPath: "id" });
        d.createObjectStore("states");
        d.createObjectStore("players", { keyPath: ["lid", "id"] });
        d.createObjectStore("boxes", { keyPath: ["lid", "gid"] });
        d.createObjectStore("seasons", { keyPath: ["lid", "season"] });
      },
    });
  }
  return dbp;
}

export function metaOf(L: League): LeagueMeta {
  const t = L.teams[L.userTid];
  const s = t.seasons[t.seasons.length - 1];
  const c = L.coaches.find((x) => x.id === L.userCid);
  return {
    id: L.id,
    name: L.name,
    teamName: t.name,
    teamAbbrev: t.abbrev,
    colors: t.colors,
    coach: c ? `${c.first} ${c.last}` : "",
    season: L.season,
    phase: L.phase,
    record: s ? `${s.w}-${s.l}` : "0-0",
    created: L.created,
    updated: L.updated,
  };
}

export async function listLeagues(): Promise<LeagueMeta[]> {
  const d = await db();
  const all = await d.getAll("meta");
  return all.sort((a, b) => b.updated - a.updated);
}

export interface Pending {
  boxes: BoxScore[];
  players: Player[];
  seasons: SeasonArchive[];
}

export async function saveLeague(L: League, pending: Pending) {
  const d = await db();
  const tx = d.transaction(["meta", "states", "players", "boxes", "seasons"], "readwrite");
  const lid = L.id;
  const boxes = pending.boxes.splice(0);
  const players = pending.players.splice(0);
  const seasons = pending.seasons.splice(0);
  for (const b of boxes) tx.objectStore("boxes").put({ ...b, lid });
  for (const p of players) tx.objectStore("players").put({ ...p, lid });
  for (const s of seasons) tx.objectStore("seasons").put({ ...s, lid });
  tx.objectStore("states").put(L, lid);
  tx.objectStore("meta").put(metaOf(L));
  await tx.done;
}

export async function loadLeague(lid: string): Promise<League | undefined> {
  const d = await db();
  return d.get("states", lid);
}

function range(lid: string) {
  return IDBKeyRange.bound([lid, -Infinity], [lid, Infinity]);
}

export async function deleteLeague(lid: string) {
  const d = await db();
  const tx = d.transaction(["meta", "states", "players", "boxes", "seasons"], "readwrite");
  tx.objectStore("meta").delete(lid);
  tx.objectStore("states").delete(lid);
  tx.objectStore("players").delete(range(lid));
  tx.objectStore("boxes").delete(range(lid));
  tx.objectStore("seasons").delete(range(lid));
  await tx.done;
}

export async function getBox(lid: string, gid: number): Promise<BoxScore | undefined> {
  const d = await db();
  return d.get("boxes", [lid, gid]);
}

export async function getArchivedPlayer(lid: string, pid: number): Promise<Player | undefined> {
  const d = await db();
  return d.get("players", [lid, pid]);
}

export async function getArchivedPlayers(lid: string, pids: number[]): Promise<Player[]> {
  const d = await db();
  const tx = d.transaction("players");
  const out = await Promise.all(pids.map((pid) => tx.store.get([lid, pid])));
  await tx.done;
  return out.filter((p): p is WithLid<Player> => !!p);
}

export async function getAllArchivedPlayers(lid: string): Promise<Player[]> {
  const d = await db();
  return d.getAll("players", range(lid));
}

export async function getSeasonArchive(lid: string, season: number): Promise<SeasonArchive | undefined> {
  const d = await db();
  return d.get("seasons", [lid, season]);
}

// ---------------- export / import ----------------
interface ExportFile {
  format: "hardwood-dynasty";
  version: 1;
  league: League;
  players: Player[];
  boxes: BoxScore[];
  seasons: SeasonArchive[];
}

export async function exportLeague(L: League): Promise<Blob> {
  const d = await db();
  const [players, boxes, seasons] = await Promise.all([
    d.getAll("players", range(L.id)),
    d.getAll("boxes", range(L.id)),
    d.getAll("seasons", range(L.id)),
  ]);
  const strip = <T extends { lid?: string }>(x: T) => {
    const { lid: _lid, ...rest } = x;
    return rest;
  };
  const data: ExportFile = {
    format: "hardwood-dynasty",
    version: 1,
    league: L,
    players: players.map(strip) as Player[],
    boxes: boxes.map(strip) as BoxScore[],
    seasons: seasons.map(strip) as SeasonArchive[],
  };
  const json = new Blob([JSON.stringify(data)], { type: "application/json" });
  if (typeof CompressionStream !== "undefined") {
    const stream = json.stream().pipeThrough(new CompressionStream("gzip"));
    return await new Response(stream).blob();
  }
  return json;
}

export async function importLeague(file: File): Promise<string> {
  let text: string;
  const head = new Uint8Array(await file.slice(0, 2).arrayBuffer());
  if (head[0] === 0x1f && head[1] === 0x8b && typeof DecompressionStream !== "undefined") {
    const stream = file.stream().pipeThrough(new DecompressionStream("gzip"));
    text = await new Response(stream).text();
  } else {
    text = await file.text();
  }
  const data = JSON.parse(text) as ExportFile;
  if (data.format !== "hardwood-dynasty") throw new Error("Not a Hardwood Dynasty save file");
  const L = data.league;
  // avoid clobbering an existing league with the same id
  const existing = await loadLeague(L.id);
  if (existing) L.id = `${L.id}-${Date.now().toString(36)}`;
  await saveLeague(L, { boxes: data.boxes, players: data.players, seasons: data.seasons });
  return L.id;
}
