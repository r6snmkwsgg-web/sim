// UI state: the live league, change notifications, saving, and the sim runner.

import { useSyncExternalStore } from "react";
import type { League } from "../engine/types";
import { reindex, setSink, syncRng } from "../engine/core";
import { advancePhase, isDayPhase, simDay } from "../engine/advance";
import { currentDateLabel } from "../engine/core";
import { loadLeague, saveLeague, type Pending } from "./db";
import { migrate } from "../engine/migrate";

let league: League | null = null;
let version = 0;
const listeners = new Set<() => void>();
const pending: Pending = { boxes: [], players: [], seasons: [] };

setSink({
  box: (_lid, b) => pending.boxes.push(b),
  archivePlayer: (_lid, p) => pending.players.push(p),
  archiveSeason: (_lid, a) => pending.seasons.push(a),
});

function emit() {
  version++;
  for (const l of listeners) l();
}
function subscribe(fn: () => void) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function bump() {
  emit();
}

export function getLeague(): League | null {
  return league;
}

export function useLeague(): League {
  useSyncExternalStore(subscribe, () => version);
  if (!league) throw new Error("No league loaded");
  return league;
}

export function useLeagueMaybe(): League | null {
  useSyncExternalStore(subscribe, () => version);
  return league;
}

export function useVersion(): number {
  return useSyncExternalStore(subscribe, () => version);
}

export async function openLeague(lid: string): Promise<League | null> {
  if (league?.id === lid) return league;
  const L = await loadLeague(lid);
  if (!L) return null;
  migrate(L);
  reindex(L);
  league = L;
  emit();
  return L;
}

export function setLeague(L: League | null) {
  league = L;
  emit();
}

let saving: Promise<void> | null = null;
export async function save() {
  if (!league) return;
  syncRng(league);
  league.updated = Date.now();
  const L = league;
  // serialize saves
  const prev = saving;
  saving = (async () => {
    if (prev) await prev;
    await saveLeague(L, pending);
  })();
  await saving;
}

let saveTimer: ReturnType<typeof setTimeout> | null = null;

/** Save soon; coalesces bursts of UI edits (e.g. dragging a slider). */
export function saveSoon(delay = 700) {
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    saveTimer = null;
    void save();
  }, delay);
}

/** Apply a mutation from the UI, re-render, and schedule a save. */
export function mutate(fn: (L: League) => void) {
  if (!league) return;
  fn(league);
  emit();
  saveSoon();
}

// make sure pending edits are written when the tab closes
if (typeof window !== "undefined") {
  window.addEventListener("beforeunload", () => {
    if (saveTimer) {
      clearTimeout(saveTimer);
      void save();
    }
  });
}

// ---------------- sim runner ----------------
export type SimTarget = "day" | "week" | "nextGame" | "endRegular" | "selection" | "endPostseason" | "advance" | "endPortal";

interface SimState {
  running: boolean;
  label: string;
  stop: boolean;
  lastResult: { gid: number } | null;
}
const sim: SimState = { running: false, label: "", stop: false, lastResult: null };
let simVersion = 0;
const simListeners = new Set<() => void>();
function simEmit() {
  simVersion++;
  for (const l of simListeners) l();
}
export function useSim(): SimState {
  useSyncExternalStore(
    (fn) => {
      simListeners.add(fn);
      return () => simListeners.delete(fn);
    },
    () => simVersion,
  );
  return sim;
}
export function stopSim() {
  sim.stop = true;
  simEmit();
}

const tick = () => new Promise((r) => setTimeout(r, 0));

export async function runSim(target: SimTarget): Promise<{ userGameId: number | null }> {
  const L = league;
  if (!L || sim.running) return { userGameId: null };
  if (saveTimer) {
    clearTimeout(saveTimer);
    saveTimer = null;
  }
  sim.running = true;
  sim.stop = false;
  sim.label = "Simulating…";
  simEmit();
  let userGameId: number | null = null;
  try {
    if (target === "advance" || !isDayPhase(L)) {
      if (target === "endPortal") {
        while (L.phase === "portal") {
          advancePhase(L);
          sim.label = currentDateLabel(L);
          simEmit();
          await tick();
        }
      } else {
        advancePhase(L);
      }
    } else {
      let last = Date.now();
      let lastFull = last;
      let days = 0;
      const startWeek = L.week;
      for (;;) {
        if (sim.stop) break;
        const before = L.phase;
        const r = simDay(L);
        days++;
        if (r.userPlayed) {
          const g = L.games.filter((x) => x.played && (x.home === L.userTid || x.away === L.userTid)).sort((a, b) => b.day - a.day || b.id - a.id)[0];
          userGameId = g?.id ?? null;
        }
        if (target === "day") break;
        if (target === "nextGame" && r.userPlayed) break;
        if (target === "week" && (L.week !== startWeek || days >= 7)) break;
        if (L.phase !== before) {
          if (target === "endRegular" && L.phase !== "regular") break;
          if (L.phase === "selection" || L.phase === "seasonEnd") break;
        }
        if (!isDayPhase(L)) break;
        if (Date.now() - last > 60) {
          sim.label = currentDateLabel(L);
          simEmit();
          // re-rendering the whole page is the expensive part, so do it less often
          if (Date.now() - lastFull > 700) {
            emit();
            lastFull = Date.now();
          }
          await tick();
          last = Date.now();
        }
      }
    }
    emit();
    sim.label = "Saving…";
    simEmit();
    await save();
  } catch (e) {
    console.error(e);
    alert(`Simulation error: ${(e as Error).message}`);
  } finally {
    sim.running = false;
    sim.label = "";
    sim.lastResult = userGameId !== null ? { gid: userGameId } : null;
    simEmit();
    emit();
  }
  return { userGameId };
}
