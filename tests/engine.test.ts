import { describe, expect, it } from "vitest";
import { createLeague } from "../src/engine/league";
import { advancePhase, isDayPhase, simDay } from "../src/engine/advance";
import { getMemorySink, roster } from "../src/engine/core";
import type { League } from "../src/engine/types";

function newLeague(seed = 101): League {
  return createLeague({ name: "Test", teamSlug: "duke", coachFirst: "T", coachLast: "C", seed });
}

describe("league creation", () => {
  const L = newLeague();
  it("has every D1 program with a full roster and a coach", () => {
    expect(L.teams.length).toBeGreaterThan(360);
    for (const t of L.teams) {
      const r = roster(L, t.id);
      expect(r.length).toBeGreaterThanOrEqual(10);
      expect(r.length).toBeLessThanOrEqual(L.settings.rosterMax);
      expect(L.coaches.some((c) => c.id === t.coachId)).toBe(true);
    }
  });
  it("builds a sane schedule", () => {
    const perTeam = new Map<number, number>();
    const perDay = new Set<string>();
    for (const g of L.games) {
      expect(g.home).not.toBe(g.away);
      for (const tid of [g.home, g.away]) {
        perTeam.set(tid, (perTeam.get(tid) ?? 0) + 1);
        const key = `${tid}:${g.day}`;
        expect(perDay.has(key)).toBe(false); // nobody plays twice in a day
        perDay.add(key);
      }
    }
    for (const t of L.teams) {
      const n = perTeam.get(t.id) ?? 0;
      expect(n).toBeGreaterThanOrEqual(24);
      expect(n).toBeLessThanOrEqual(34);
    }
  });
  it("generates a recruiting class and a preseason poll", () => {
    expect(L.players.filter((p) => p.status === "recruit").length).toBeGreaterThan(1000);
    expect(L.polls[0].ranks.length).toBe(25);
  });
  it("can be structured-cloned for IndexedDB", () => {
    expect(() => structuredClone(L)).not.toThrow();
  });
});

describe("a full season", () => {
  const L = newLeague(202);
  advancePhase(L);
  while (isDayPhase(L) || L.phase === "selection") {
    if (L.phase === "selection") advancePhase(L);
    else simDay(L);
  }

  it("plays every game and crowns champions", () => {
    expect(L.phase).toBe("seasonEnd");
    expect(L.games.every((g) => g.played)).toBe(true);
    const ncaa = L.brackets.find((b) => b.key === "ncaa")!;
    expect(ncaa.champion).not.toBeNull();
    expect(L.brackets.filter((b) => b.key.startsWith("conf:")).every((b) => b.champion !== null)).toBe(true);
    expect(L.history.length).toBe(1);
    expect(L.awards.length).toBe(1);
  });

  it("seeds a correct NCAA field", () => {
    const ncaa = L.brackets.find((b) => b.key === "ncaa")!;
    const teams = new Set<number>();
    for (const g of ncaa.games) {
      if (g.round === 0 || g.round === -1) for (const t of [g.a, g.b]) if (t !== null) teams.add(t);
    }
    expect(teams.size).toBe(L.settings.bracketSize);
    for (let reg = 0; reg < 4; reg++) {
      const seeds = ncaa.games.filter((g) => g.round === 0 && g.region === reg).flatMap((g) => [g.sa, g.sb]);
      expect(seeds.sort((a, b) => a! - b!)).toEqual(Array.from({ length: 16 }, (_, i) => i + 1));
    }
  });

  it("keeps box scores consistent with results", () => {
    const boxes = getMemorySink().boxes.slice(-300);
    expect(boxes.length).toBeGreaterThan(100);
    for (const b of boxes) {
      for (const side of [b.home, b.away]) {
        const pts = side.lines.reduce((a, l) => a + l.pts, 0);
        expect(pts).toBe(side.pts);
        const mins = side.lines.reduce((a, l) => a + l.min, 0);
        expect(Math.abs(mins - (200 + 25 * b.ot))).toBeLessThan(2.5);
        for (const l of side.lines) {
          expect(l.fgm).toBeLessThanOrEqual(l.fga);
          expect(l.tpm).toBeLessThanOrEqual(l.tpa);
          expect(l.ftm).toBeLessThanOrEqual(l.fta);
          expect(l.pts).toBe(2 * (l.fgm - l.tpm) + 3 * l.tpm + l.ftm);
        }
      }
    }
  });

  it("matches team records to games", () => {
    for (const t of L.teams.slice(0, 40)) {
      const s = t.seasons[t.seasons.length - 1];
      const games = L.games.filter((g) => g.home === t.id || g.away === t.id);
      const wins = games.filter((g) => (g.home === t.id ? g.hs > g.as : g.as > g.hs)).length;
      expect(s.w).toBe(wins);
      expect(s.l).toBe(games.length - wins);
    }
  });

  it("runs the offseason into a valid new season", () => {
    advancePhase(L); // carousel
    advancePhase(L); // draft
    expect(L.draftHistory.length).toBeGreaterThan(40);
    advancePhase(L); // portal
    while (L.phase === "portal") advancePhase(L);
    expect(L.phase).toBe("signing");
    advancePhase(L); // new season
    expect(L.phase).toBe("preseason");
    expect(L.season).toBe(L.startSeason + 1);
    for (const t of L.teams) {
      const r = roster(L, t.id);
      expect(r.length).toBeLessThanOrEqual(L.settings.rosterMax);
      expect(r.length).toBeGreaterThanOrEqual(12);
      expect(t.seasons[t.seasons.length - 1].season).toBe(L.season);
      for (const p of r) {
        expect(p.eligUsed).toBeLessThan(4);
        expect(p.year).toBeLessThanOrEqual(5);
      }
    }
    expect(L.players.filter((p) => p.status === "recruit").length).toBeGreaterThan(1000);
    expect(() => structuredClone(L)).not.toThrow();
  });
});
