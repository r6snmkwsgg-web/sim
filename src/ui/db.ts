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

/** What this device last wrote to (or read from) the cloud for a league. */
export interface SyncRec {
  lid: string;
  code: string;
  head: string;
  updated: number;
  manifest: string;
  state: string;
  chunks: string[];
}

/** An archived record written since the last cloud sync. */
export interface OutboxItem {
  lid: string;
  t: "p" | "b" | "s";
  d: Player | BoxScore | SeasonArchive;
}

interface Schema extends DBSchema {
  meta: { key: string; value: LeagueMeta };
  states: { key: string; value: League };
  players: { key: [string, number]; value: WithLid<Player> };
  boxes: { key: [string, number]; value: WithLid<BoxScore> };
  seasons: { key: [string, number]; value: WithLid<SeasonArchive> };
  sync: { key: string; value: SyncRec };
  outbox: { key: number; value: OutboxItem; indexes: { lid: string } };
}

let dbp: Promise<IDBPDatabase<Schema>> | null = null;

export function db(): Promise<IDBPDatabase<Schema>> {
  if (!dbp) {
    dbp = openDB<Schema>("hardwood-dynasty", 2, {
      upgrade(d, oldVersion) {
        if (oldVersion < 1) {
          d.createObjectStore("meta", { keyPath: "id" });
          d.createObjectStore("states");
          d.createObjectStore("players", { keyPath: ["lid", "id"] });
          d.createObjectStore("boxes", { keyPath: ["lid", "gid"] });
          d.createObjectStore("seasons", { keyPath: ["lid", "season"] });
        }
        if (oldVersion < 2) {
          d.createObjectStore("sync", { keyPath: "lid" });
          d.createObjectStore("outbox", { autoIncrement: true }).createIndex("lid", "lid");
        }
      },
    });
  }
  return dbp;
}

// cloud saves hook in here: queue newly archived records, and hear about saves
let queueForCloud = () => false;
let onSaved: ((lid: string) => void) | null = null;
export function setCloudHooks(queue: () => boolean, saved: (lid: string) => void) {
  queueForCloud = queue;
  onSaved = saved;
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

/** Write the live league and anything it archived. `quiet` skips cloud bookkeeping (used when the save came from the cloud). */
export async function saveLeague(L: League, pending: Pending, opts: { quiet?: boolean } = {}) {
  const d = await db();
  const tx = d.transaction(["meta", "states", "players", "boxes", "seasons", "outbox"], "readwrite");
  const lid = L.id;
  const boxes = pending.boxes.splice(0);
  const players = pending.players.splice(0);
  const seasons = pending.seasons.splice(0);
  const queue = !opts.quiet && queueForCloud();
  for (const b of boxes) tx.objectStore("boxes").put({ ...b, lid });
  for (const p of players) tx.objectStore("players").put({ ...p, lid });
  for (const s of seasons) tx.objectStore("seasons").put({ ...s, lid });
  if (queue) {
    const out = tx.objectStore("outbox");
    for (const b of boxes) out.add({ lid, t: "b", d: b });
    for (const p of players) out.add({ lid, t: "p", d: p });
    for (const s of seasons) out.add({ lid, t: "s", d: s });
  }
  tx.objectStore("states").put(L, lid);
  tx.objectStore("meta").put(metaOf(L));
  await tx.done;
  if (!opts.quiet) onSaved?.(lid);
}

/** Every archived record of a league, for a full cloud upload. */
export async function getArchives(lid: string): Promise<{ players: Player[]; boxes: BoxScore[]; seasons: SeasonArchive[] }> {
  const d = await db();
  const [players, boxes, seasons] = await Promise.all([d.getAll("players", range(lid)), d.getAll("boxes", range(lid)), d.getAll("seasons", range(lid))]);
  return { players, boxes, seasons };
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
  const tx = d.transaction(["meta", "states", "players", "boxes", "seasons", "sync", "outbox"], "readwrite");
  tx.objectStore("meta").delete(lid);
  tx.objectStore("states").delete(lid);
  tx.objectStore("players").delete(range(lid));
  tx.objectStore("boxes").delete(range(lid));
  tx.objectStore("seasons").delete(range(lid));
  tx.objectStore("sync").delete(lid);
  const out = tx.objectStore("outbox");
  for (const k of await out.index("lid").getAllKeys(lid)) out.delete(k);
  await tx.done;
}

/** Write archived records in one transaction (used when restoring). */
export async function putArchives(lid: string, batch: Pending) {
  const d = await db();
  const tx = d.transaction(["players", "boxes", "seasons"], "readwrite");
  for (const b of batch.boxes.splice(0)) tx.objectStore("boxes").put({ ...b, lid });
  for (const p of batch.players.splice(0)) tx.objectStore("players").put({ ...p, lid });
  for (const a of batch.seasons.splice(0)) tx.objectStore("seasons").put({ ...a, lid });
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
// Saves are newline-delimited JSON: a header line with the live league, then
// one line per archived player, box score and season. Written and read as
// streams so even very long dynasties back up without hitting string limits.

interface Header {
  format: "hardwood-dynasty";
  version: 2;
  league: League;
}

export async function exportLeague(L: League): Promise<Blob> {
  const d = await db();
  const [players, boxes, seasons] = await Promise.all([
    d.getAll("players", range(L.id)),
    d.getAll("boxes", range(L.id)),
    d.getAll("seasons", range(L.id)),
  ]);
  const parts: string[] = [];
  const header: Header = { format: "hardwood-dynasty", version: 2, league: L };
  parts.push(JSON.stringify(header), "\n");
  const line = (t: string, x: { lid?: string }) => {
    const { lid: _lid, ...rest } = x;
    parts.push(JSON.stringify({ t, d: rest }), "\n");
  };
  for (const p of players) line("p", p);
  for (const b of boxes) line("b", b);
  for (const a of seasons) line("s", a);
  const blob = new Blob(parts, { type: "application/x-ndjson" });
  if (typeof CompressionStream !== "undefined") {
    const stream = blob.stream().pipeThrough(new CompressionStream("gzip"));
    return await new Response(stream).blob();
  }
  return blob;
}

export async function* lines(file: Blob): AsyncGenerator<string> {
  const head = new Uint8Array(await file.slice(0, 2).arrayBuffer());
  // the DOM lib's stream generics don't line up across TS versions; the
  // runtime types are fine
  let stream: ReadableStream<any> = file.stream();
  if (head[0] === 0x1f && head[1] === 0x8b) {
    if (typeof DecompressionStream === "undefined") throw new Error("This browser can't read compressed saves");
    stream = stream.pipeThrough(new DecompressionStream("gzip"));
  }
  const reader = (stream.pipeThrough(new TextDecoderStream()) as ReadableStream<string>).getReader();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += value;
    let i: number;
    while ((i = buf.indexOf("\n")) >= 0) {
      const ln = buf.slice(0, i);
      buf = buf.slice(i + 1);
      if (ln.trim()) yield ln;
    }
  }
  if (buf.trim()) yield buf;
}

export async function importLeague(file: File): Promise<string> {
  const it = lines(file);
  const first = await it.next();
  if (first.done) throw new Error("Empty file");
  const parsed = JSON.parse(first.value);
  // older single-document saves
  if (parsed.format === "hardwood-dynasty" && parsed.version === 1) {
    const L = parsed.league as League;
    if (await loadLeague(L.id)) L.id = `${L.id}-${Date.now().toString(36)}`;
    await saveLeague(L, { boxes: parsed.boxes ?? [], players: parsed.players ?? [], seasons: parsed.seasons ?? [] });
    return L.id;
  }
  const header = parsed as Header;
  if (header.format !== "hardwood-dynasty") throw new Error("Not a Hardwood Dynasty save file");
  const L = header.league;
  if (await loadLeague(L.id)) L.id = `${L.id}-${Date.now().toString(36)}`;
  const batch: Pending = { boxes: [], players: [], seasons: [] };
  const flush = async () => {
    if (!batch.boxes.length && !batch.players.length && !batch.seasons.length) return;
    await putArchives(L.id, batch);
  };
  for await (const ln of it) {
    const rec = JSON.parse(ln) as { t: string; d: never };
    if (rec.t === "p") batch.players.push(rec.d);
    else if (rec.t === "b") batch.boxes.push(rec.d);
    else if (rec.t === "s") batch.seasons.push(rec.d);
    if (batch.boxes.length + batch.players.length >= 2000) await flush();
  }
  await flush();
  await saveLeague(L, { boxes: [], players: [], seasons: [] });
  return L.id;
}
