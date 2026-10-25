// Cloud saves. Each browser gets a private save code; leagues upload to the
// cloud under that code a few minutes after you play and whenever you leave
// the page, and any device with the same code can load them.
//
// Uploads are incremental: the live league goes up as one compressed file,
// and archived history (box scores, past players, past seasons) goes up as
// small "chunks" of only what's new since the last upload. A manifest file
// points at the current state and chunks.

import { useSyncExternalStore } from "react";
import { put } from "@vercel/blob/client";
import type { League } from "../engine/types";
import { db, deleteLeague, getArchives, lines, metaOf, putArchives, saveLeague, setCloudHooks, type LeagueMeta, type OutboxItem, type Pending, type SyncRec } from "./db";

const SITE = "https://hardwood-dynasty.vercel.app";
// the main site and local dev serve the API themselves; every other copy (the
// downloaded file, other Vercel addresses) uses the main site's, so saves are shared
const SAME_ORIGIN = typeof location !== "undefined" && (location.origin === SITE || /^(localhost|127\.0\.0\.1)$/.test(location.hostname));
const API = `${SAME_ORIGIN ? "" : SITE}/api/saves`;
// keep uploads well inside the free plan: at most one every few minutes while playing
const PUSH_GAP_MS = 10 * 60 * 1000;
const FIRST_PUSH_MS = 20 * 1000;
const MAX_CHUNKS = 40;

export interface Manifest {
  v: 1;
  lid: string;
  head: string;
  updated: number;
  meta: LeagueMeta;
  state: string;
  chunks: string[];
  device: string;
}

// ---------------- the save code ----------------
const ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"; // no I, L, O or U
const K_CODE = "hd.cloud.code";
const K_OFF = "hd.cloud.off";
const K_DEVICE = "hd.cloud.device";

function store(key: string, value?: string | null): string | null {
  try {
    if (value === undefined) return localStorage.getItem(key);
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    // storage blocked: cloud saves just stay off
  }
  return null;
}

function randomCode(n: number): string {
  const bytes = crypto.getRandomValues(new Uint8Array(n));
  return Array.from(bytes, (b) => ALPHABET[b % 32]).join("");
}

/** Accepts a code typed with dashes, spaces or lowercase; returns the 16 characters or null. */
export function normalizeCode(input: string): string | null {
  const c = input
    .toUpperCase()
    .replace(/[^0-9A-Z]/g, "")
    .replace(/O/g, "0")
    .replace(/[IL]/g, "1");
  return /^[0-9A-HJKMNP-TV-Z]{16}$/.test(c) ? c : null;
}

export function formatCode(c: string): string {
  return c.match(/.{1,4}/g)?.join("-") ?? c;
}

export function getCode(): string | null {
  return store(K_CODE);
}

export function cloudOn(): boolean {
  return store(K_OFF) !== "1";
}

function ensureCode(): string {
  let c = getCode();
  if (!c) {
    c = randomCode(16);
    store(K_CODE, c);
  }
  return c;
}

function deviceId(): string {
  let d = store(K_DEVICE);
  if (!d) {
    d = randomCode(8);
    store(K_DEVICE, d);
  }
  return d;
}

/** Link to open the game on another device with this code. */
export function linkFor(code: string): string {
  return `${SITE}/#/link/${formatCode(code)}`;
}

// ---------------- status for the UI ----------------
export interface CloudStatus {
  state: "off" | "idle" | "saving" | "error";
  last: number | null;
  error: string | null;
}
let status: CloudStatus = { state: "idle", last: null, error: null };
const listeners = new Set<() => void>();
function setStatus(s: Partial<CloudStatus>) {
  status = { ...status, ...s };
  for (const l of listeners) l();
}
export function useCloudStatus(): CloudStatus {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => listeners.delete(cb);
    },
    () => status,
  );
}

// ---------------- server calls ----------------
async function call<T>(action: string, body: Record<string, unknown>): Promise<T> {
  const r = await fetch(API, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ action, ...body }) });
  const data = (await r.json().catch(() => ({}))) as T & { error?: string };
  if (!r.ok) throw new Error(data.error ?? `Cloud error ${r.status}`);
  return data;
}

async function gzip(parts: BlobPart[], type: string): Promise<Blob> {
  const raw = new Blob(parts);
  if (typeof CompressionStream === "undefined") throw new Error("This browser can't compress saves");
  const out = await new Response(raw.stream().pipeThrough(new CompressionStream("gzip"))).blob();
  return new Blob([out], { type });
}

async function download(url: string): Promise<Blob> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Download failed (${r.status})`);
  return r.blob();
}

async function gunzipText(b: Blob): Promise<string> {
  // the stream generics differ between TS DOM versions; the runtime types are fine
  const s = (b.stream() as ReadableStream<any>).pipeThrough(new DecompressionStream("gzip"));
  return new Response(s).text();
}

// ---------------- upload ----------------
const pushing = new Map<string, Promise<void>>();

/** Upload whatever changed in a saved league since its last upload. */
export function pushLeague(lid: string): Promise<void> {
  const prev = pushing.get(lid) ?? Promise.resolve();
  const next = prev.catch(() => undefined).then(() => doPush(lid));
  pushing.set(lid, next);
  return next;
}

async function doPush(lid: string): Promise<void> {
  if (!cloudOn()) return;
  const code = ensureCode();
  const d = await db();
  // one snapshot of the saved league and the history it archived since the last upload
  const tx = d.transaction(["states", "sync", "outbox"], "readonly");
  const L = await tx.objectStore("states").get(lid);
  const rec = await tx.objectStore("sync").get(lid);
  const keys = await tx.objectStore("outbox").index("lid").getAllKeys(lid);
  const items = await tx.objectStore("outbox").index("lid").getAll(lid);
  await tx.done;
  if (!L) return;
  if (rec && rec.code === code && rec.updated === L.updated && items.length === 0) return;
  const ts = Date.now();
  const names = { state: `state-${ts}.json.gz`, manifest: `manifest-${ts}.json`, chunk: `chunk-${ts}.ndjson.gz` };
  const { tokens, current } = await call<{ tokens: Record<string, { token: string; pathname: string }>; current: string | null }>("tokens", {
    code,
    lid,
    files: [names.state, names.manifest, names.chunk],
  });
  // a full copy the first time, after a code change, when chunks pile up, or
  // when another device uploaded since this one last did (the newest play wins)
  const rebase = !rec || rec.code !== code || rec.chunks.length >= MAX_CHUNKS || current !== rec.manifest;
  let chunk: Blob | null = null;
  if (rebase) {
    const a = await getArchives(lid);
    const parts: string[] = [];
    const line = (t: string, x: object) => {
      const { lid: _lid, ...rest } = x as { lid?: string };
      parts.push(JSON.stringify({ t, d: rest }), "\n");
    };
    for (const p of a.players) line("p", p);
    for (const b of a.boxes) line("b", b);
    for (const s of a.seasons) line("s", s);
    if (parts.length) chunk = await gzip(parts, "application/gzip");
  } else if (items.length) {
    chunk = await gzip(
      items.flatMap((it: OutboxItem) => [JSON.stringify({ t: it.t, d: it.d }), "\n"]),
      "application/gzip",
    );
  }
  const up = (name: string, body: Blob | string, contentType: string) => {
    const t = tokens[name];
    const size = typeof body === "string" ? body.length : body.size;
    return put(t.pathname, body, { access: "public", token: t.token, contentType, multipart: size > 90 * 1024 * 1024 });
  };
  const stateBlob = await gzip([JSON.stringify({ format: "hardwood-dynasty", version: 2, league: L })], "application/gzip");
  const [st, ch] = await Promise.all([up(names.state, stateBlob, "application/gzip"), chunk ? up(names.chunk, chunk, "application/gzip") : Promise.resolve(null)]);
  const chunks = [...(rebase ? [] : rec!.chunks), ...(ch ? [ch.url] : [])];
  const manifest: Manifest = { v: 1, lid, head: String(ts), updated: L.updated, meta: metaOf(L), state: st.url, chunks, device: deviceId() };
  const mf = await up(names.manifest, JSON.stringify(manifest), "application/json");
  const next: SyncRec = { lid, code, head: manifest.head, updated: L.updated, manifest: mf.url, state: st.url, chunks };
  const tx2 = d.transaction(["sync", "outbox"], "readwrite");
  tx2.objectStore("sync").put(next);
  for (const k of keys) tx2.objectStore("outbox").delete(k);
  await tx2.done;
  // files the new manifest replaced (deleting is free); after a full copy,
  // listing cleans up whatever else is left over
  if (rec && rec.code === code && !rebase) void call("delete", { code, urls: [rec.manifest, rec.state] }).catch(() => undefined);
  else if (rebase) void listCloud().catch(() => undefined);
}

// ---------------- scheduling ----------------
const dirty = new Set<string>();
let timer: ReturnType<typeof setTimeout> | null = null;
let lastPush = 0;

function schedule(delay?: number) {
  if (timer) return;
  const wait = delay ?? Math.max(FIRST_PUSH_MS, lastPush + PUSH_GAP_MS - Date.now());
  timer = setTimeout(() => {
    timer = null;
    void flushCloud();
  }, wait);
}

/** Upload every league with unsaved changes now. */
export async function flushCloud(): Promise<void> {
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
  if (!cloudOn() || dirty.size === 0) return;
  const lids = [...dirty];
  dirty.clear();
  setStatus({ state: "saving" });
  try {
    for (const lid of lids) await pushLeague(lid);
    lastPush = Date.now();
    setStatus({ state: "idle", last: lastPush, error: null });
  } catch (e) {
    for (const lid of lids) dirty.add(lid);
    setStatus({ state: "error", error: (e as Error).message });
    schedule(2 * 60 * 1000);
  }
}

function noteSaved(lid: string) {
  if (!cloudOn()) return;
  dirty.add(lid);
  schedule();
}

/** Call once at startup. */
export function initCloud() {
  setCloudHooks(() => cloudOn(), noteSaved);
  if (!cloudOn()) {
    setStatus({ state: "off" });
    return;
  }
  ensureCode();
  if (typeof document !== "undefined") {
    // leaving the page or switching apps uploads right away
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") void flushCloud();
    });
  }
}

// ---------------- download ----------------
export interface CloudLeague {
  manifest: Manifest;
  manifestUrl: string;
}

/** Every league saved under this device's code. */
export async function listCloud(): Promise<CloudLeague[]> {
  if (!cloudOn()) return [];
  const code = ensureCode();
  const { leagues } = await call<{ leagues: Record<string, { manifest: string | null; manifestAt: number; files: { url: string; uploadedAt: number }[] }> }>("list", { code });
  const out: CloudLeague[] = [];
  const stale: string[] = [];
  await Promise.all(
    Object.values(leagues).map(async (e) => {
      if (!e.manifest) return;
      try {
        const m = (await (await fetch(e.manifest)).json()) as Manifest;
        out.push({ manifest: m, manifestUrl: e.manifest });
        // leftovers from interrupted uploads
        const keep = new Set([e.manifest, m.state, ...m.chunks]);
        for (const f of e.files) if (!keep.has(f.url) && Date.now() - f.uploadedAt > 30 * 60 * 1000) stale.push(f.url);
      } catch {
        // skip a league whose manifest can't be read right now
      }
    }),
  );
  if (stale.length) void call("delete", { code, urls: stale }).catch(() => undefined);
  return out;
}

/** What this device last synced for each league. */
export async function syncRecords(): Promise<Map<string, SyncRec>> {
  const d = await db();
  return new Map((await d.getAll("sync")).map((r) => [r.lid, r]));
}

/** Replace this device's copy of a league with the cloud copy. */
export async function pullLeague(c: CloudLeague, onProgress?: (done: number, total: number) => void): Promise<void> {
  try {
    await pullOnce(c, onProgress);
  } catch (e) {
    // another device may have uploaded mid-download and replaced these files: try its newer copy
    const fresh = (await listCloud()).find((x) => x.manifest.lid === c.manifest.lid);
    if (!fresh || fresh.manifestUrl === c.manifestUrl) throw e;
    await pullOnce(fresh, onProgress);
  }
}

async function pullOnce(c: CloudLeague, onProgress?: (done: number, total: number) => void): Promise<void> {
  const m = c.manifest;
  const total = m.chunks.length + 1;
  onProgress?.(0, total);
  // fetch everything first, so a failed download never touches this device's copy
  const stateFile = await download(m.state);
  const chunkFiles: Blob[] = [];
  for (let i = 0; i < m.chunks.length; i++) {
    chunkFiles.push(await download(m.chunks[i]));
    onProgress?.(i + 1, total);
  }
  const header = JSON.parse(await gunzipText(stateFile)) as { league: League };
  const L = header.league;
  await deleteLeague(m.lid);
  const batch: Pending = { boxes: [], players: [], seasons: [] };
  for (let i = 0; i < chunkFiles.length; i++) {
    for await (const ln of lines(chunkFiles[i])) {
      const rec = JSON.parse(ln) as { t: string; d: never };
      if (rec.t === "p") batch.players.push(rec.d);
      else if (rec.t === "b") batch.boxes.push(rec.d);
      else if (rec.t === "s") batch.seasons.push(rec.d);
      if (batch.boxes.length + batch.players.length >= 2000) await putArchives(m.lid, batch);
    }
    await putArchives(m.lid, batch);
  }
  await saveLeague(L, { boxes: [], players: [], seasons: [] }, { quiet: true });
  const d = await db();
  await d.put("sync", { lid: m.lid, code: ensureCode(), head: m.head, updated: m.updated, manifest: c.manifestUrl, state: m.state, chunks: m.chunks });
  onProgress?.(total, total);
}

/** Remove a league from the cloud too. */
export async function deleteCloudLeague(lid: string): Promise<void> {
  const code = getCode();
  if (!code || !cloudOn()) return;
  dirty.delete(lid);
  await call("delete", { code, lid });
}

/** Switch to a code from another device; this device's leagues upload under it too. */
export async function switchCode(input: string): Promise<boolean> {
  const c = normalizeCode(input);
  if (!c) return false;
  store(K_CODE, c);
  store(K_OFF, null);
  setStatus({ state: "idle", error: null });
  const d = await db();
  for (const lid of await d.getAllKeys("states")) dirty.add(lid);
  void flushCloud();
  return true;
}

export function setCloudOn(on: boolean) {
  store(K_OFF, on ? null : "1");
  if (on) {
    ensureCode();
    setStatus({ state: "idle" });
    void db()
      .then((d) => d.getAllKeys("states"))
      .then((ks) => {
        for (const k of ks) dirty.add(k);
        void flushCloud();
      });
  } else setStatus({ state: "off" });
}

/** Upload every local league that has never been uploaded (first run after updating). */
export async function pushUnsynced(): Promise<void> {
  if (!cloudOn()) return;
  const d = await db();
  const [lids, recs] = await Promise.all([d.getAllKeys("states"), d.getAll("sync")]);
  const code = ensureCode();
  const done = new Set(recs.filter((r) => r.code === code).map((r) => r.lid));
  let any = false;
  for (const lid of lids)
    if (!done.has(lid)) {
      dirty.add(lid);
      any = true;
    }
  if (any) schedule(FIRST_PUSH_MS);
}

/** Upload every league on this device now. */
export async function saveAllNow(): Promise<void> {
  const d = await db();
  for (const lid of await d.getAllKeys("states")) dirty.add(lid);
  await flushCloud();
}
