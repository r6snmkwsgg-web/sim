import { describe, expect, it } from "vitest";
import { Rng } from "../src/engine/rng";
import { generateInitialRoster } from "../src/engine/gen/roster";
import { autoRotation } from "../src/engine/sim/rotation";
import { simGame, type SimTeam } from "../src/engine/sim/game";
import { liveState, hasStructuredPbp } from "../src/engine/pbp";
import type { Player, Strategy } from "../src/engine/types";

const STRATS: Strategy[] = [
  { tempo: 3, offense: "balanced", defense: "man", rebounding: "balanced" },
  { tempo: 5, offense: "perimeter", defense: "press", rebounding: "crash" },
  { tempo: 1, offense: "inside", defense: "zone", rebounding: "getback" },
];

function team(rng: Rng, tid: number, prestige: number, pid: { n: number }, strategy: Strategy): SimTeam {
  const players: Player[] = generateInitialRoster(rng, tid, prestige, () => pid.n++, 13);
  const r = autoRotation(players);
  return { tid, name: `T${tid}`, players, starters: r.starters, minutes: r.minutes, strategy, tactics: 50 };
}

describe("play-by-play", () => {
  it("rebuilds the exact box score from structured events", () => {
    const rng = new Rng(2024);
    const pid = { n: 1 };
    for (let g = 0; g < 60; g++) {
      const home = team(rng, 1, 20 + (g % 7) * 12, pid, STRATS[g % 3]);
      const away = team(rng, 2, 25 + (g % 5) * 14, pid, STRATS[(g + 1) % 3]);
      const res = simGame(home, away, rng, { neutral: g % 4 === 0, homeAdv: 3.5, pbp: true, injuries: true });
      expect(hasStructuredPbp(res.pbp)).toBe(true);
      const st = liveState(res.pbp, res.pbp.length - 1);
      for (const [side, tb] of [[0, res.home], [1, res.away]] as const) {
        let pts = 0;
        for (const l of tb.lines) {
          const x = st.lines.get(l.pid);
          const got = x ?? { pts: 0, fgm: 0, fga: 0, tpm: 0, tpa: 0, ftm: 0, fta: 0, orb: 0, drb: 0, ast: 0, stl: 0, blk: 0, tov: 0, pf: 0, sec: 0, side };
          expect({ pid: l.pid, pts: got.pts, fgm: got.fgm, fga: got.fga, tpm: got.tpm, tpa: got.tpa, ftm: got.ftm, fta: got.fta, orb: got.orb, drb: got.drb, ast: got.ast, stl: got.stl, blk: got.blk, tov: got.tov, pf: got.pf }).toEqual({
            pid: l.pid, pts: l.pts, fgm: l.fgm, fga: l.fga, tpm: l.tpm, tpa: l.tpa, ftm: l.ftm, fta: l.fta, orb: l.orb, drb: l.drb, ast: l.ast, stl: l.stl, blk: l.blk, tov: l.tov, pf: l.pf,
          });
          // minutes come from rounded event times, so allow a little slack
          expect(Math.abs(got.sec / 60 - l.min)).toBeLessThan(1.2);
          if (x) expect(x.side).toBe(side);
          pts += l.pts;
        }
        expect(pts).toBe(tb.pts);
      }
      // the final event's score is the final score
      const last = res.pbp[res.pbp.length - 1];
      expect([last.hs, last.as]).toEqual([res.home.pts, res.away.pts]);
      // every shot has a location on the half court
      for (const e of res.pbp) {
        if (e.k === "fg" || e.k === "blk") {
          expect(e.x).toBeGreaterThanOrEqual(0);
          expect(e.x).toBeLessThanOrEqual(50);
          expect(e.y).toBeGreaterThanOrEqual(0);
          expect(e.y).toBeLessThanOrEqual(35);
        }
      }
    }
  });
});
