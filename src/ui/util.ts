import { useEffect, useState } from "react";
import type { League, Player, SeasonArchive } from "../engine/types";
import { player as memPlayer } from "../engine/core";
import { getArchivedPlayer, getArchivedPlayers, getSeasonArchive } from "./db";

// ---------------- colors ----------------
export function hexToRgb(h: string): [number, number, number] {
  const x = h.replace("#", "");
  const n = x.length === 3 ? x.split("").map((c) => c + c).join("") : x;
  return [parseInt(n.slice(0, 2), 16), parseInt(n.slice(2, 4), 16), parseInt(n.slice(4, 6), 16)];
}
export function luminance(h: string): number {
  const [r, g, b] = hexToRgb(h).map((c) => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
export function textOn(bg: string): string {
  return luminance(bg) > 0.45 ? "#111827" : "#ffffff";
}
export function mix(a: string, b: string, t: number): string {
  const x = hexToRgb(a);
  const y = hexToRgb(b);
  const c = x.map((v, i) => Math.round(v + (y[i] - v) * t));
  return `#${c.map((v) => v.toString(16).padStart(2, "0")).join("")}`;
}
/** A version of the team color usable as a UI accent (not too light). */
export function accentFor(colors: [string, string]): string {
  const [p, s] = colors;
  if (luminance(p) < 0.6) return p;
  if (luminance(s) < 0.6) return s;
  return mix(p, "#000000", 0.45);
}

// ---------------- formatting ----------------
export const f1 = (x: number) => (Number.isFinite(x) ? (Math.round(x * 10) / 10).toFixed(1) : "-");
export const f0 = (x: number) => (Number.isFinite(x) ? String(Math.round(x)) : "-");
export function pct(m: number, a: number): string {
  if (!a) return "-";
  const v = m / a;
  return v >= 1 ? "1.000" : v.toFixed(3).replace(/^0/, "");
}
export function pct100(m: number, a: number): string {
  if (!a) return "-";
  return (100 * (m / a)).toFixed(1);
}
export function ordinal(n: number): string {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}
export function money(k: number): string {
  if (k >= 1000) return `$${(k / 1000).toFixed(k >= 10000 ? 0 : 1)}M`;
  return `$${Math.round(k)}K`;
}
export function signed(x: number, d = 1): string {
  const v = d === 0 ? Math.round(x) : Math.round(x * 10 ** d) / 10 ** d;
  return (v > 0 ? "+" : "") + v.toFixed(d);
}

// ---------------- async data ----------------
export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]): { data: T | undefined; loading: boolean } {
  const [state, setState] = useState<{ data: T | undefined; loading: boolean }>({ data: undefined, loading: true });
  useEffect(() => {
    let alive = true;
    setState((s) => ({ data: s.data, loading: true }));
    fn().then(
      (data) => alive && setState({ data, loading: false }),
      (e) => {
        console.error(e);
        if (alive) setState({ data: undefined, loading: false });
      },
    );
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return state;
}

/** Look up a player in memory first, then the archive. */
export async function fetchPlayer(L: League, pid: number): Promise<Player | undefined> {
  return memPlayer(L, pid) ?? (await getArchivedPlayer(L.id, pid));
}

export async function fetchPlayers(L: League, pids: number[]): Promise<Player[]> {
  const out: Player[] = [];
  const missing: number[] = [];
  for (const id of pids) {
    const p = memPlayer(L, id);
    if (p) out.push(p);
    else missing.push(id);
  }
  if (missing.length) out.push(...(await getArchivedPlayers(L.id, missing)));
  return out;
}

const archiveCache = new Map<string, SeasonArchive>();
export async function fetchSeason(L: League, season: number): Promise<SeasonArchive | undefined> {
  const key = `${L.id}:${season}`;
  const hit = archiveCache.get(key);
  if (hit) return hit;
  const a = await getSeasonArchive(L.id, season);
  if (a) archiveCache.set(key, a);
  return a;
}

export function seasonsList(L: League): number[] {
  const out: number[] = [];
  for (let s = L.season; s >= L.startSeason; s--) out.push(s);
  return out;
}

export function cls(...xs: (string | false | null | undefined)[]): string {
  return xs.filter(Boolean).join(" ");
}
