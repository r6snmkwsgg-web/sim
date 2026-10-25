// Rebuild a box score from play-by-play events, up to any point in a game.
// Used by the live game viewer; tests check it against the real box score.

import type { PbpEvent } from "./types";

export interface LiveLine {
  pid: number;
  side: 0 | 1;
  sec: number;
  pts: number;
  fgm: number;
  fga: number;
  tpm: number;
  tpa: number;
  ftm: number;
  fta: number;
  orb: number;
  drb: number;
  ast: number;
  stl: number;
  blk: number;
  tov: number;
  pf: number;
}

export interface LiveState {
  lines: Map<number, LiveLine>;
  /** player ids on the floor, [home, away] */
  on: [number[], number[]];
  /** team fouls this half (or overtime period), [home, away] */
  fouls: [number, number];
}

/** True when the events carry the structured fields a live box score needs. */
export function hasStructuredPbp(ev: PbpEvent[] | undefined): boolean {
  return !!ev && ev.some((e) => e.k === "lu");
}

/** Apply events [0, upto] (inclusive) and return each player's line so far. */
export function liveState(ev: PbpEvent[], upto: number): LiveState {
  const lines = new Map<number, LiveLine>();
  const on: [number[], number[]] = [[], []];
  const fouls: [number, number] = [0, 0];
  const L = (pid: number, side: 0 | 1): LiveLine => {
    let l = lines.get(pid);
    if (!l) {
      l = { pid, side, sec: 0, pts: 0, fgm: 0, fga: 0, tpm: 0, tpa: 0, ftm: 0, fta: 0, orb: 0, drb: 0, ast: 0, stl: 0, blk: 0, tov: 0, pf: 0 };
      lines.set(pid, l);
    }
    return l;
  };
  const other = (s: 0 | 1): 0 | 1 => (s === 0 ? 1 : 0);
  let lastT = 0;
  let per = 1;
  const end = Math.min(upto, ev.length - 1);
  for (let i = 0; i <= end; i++) {
    const e = ev[i];
    // time on the floor since the previous event
    const dt = e.t - lastT;
    if (dt > 0) {
      for (const s of [0, 1] as const) for (const pid of on[s]) L(pid, s).sec += dt;
      lastT = e.t;
    }
    if (e.per !== per) {
      per = e.per;
      fouls[0] = 0;
      fouls[1] = 0;
    }
    switch (e.k) {
      case "lu":
        on[e.side] = e.lu ?? [];
        for (const pid of on[e.side]) L(pid, e.side);
        break;
      case "fg": {
        const l = L(e.p!, e.side);
        l.fga++;
        if (e.st === "three") l.tpa++;
        if (e.m) {
          l.fgm++;
          if (e.st === "three") l.tpm++;
          l.pts += e.st === "three" ? 3 : 2;
          if (e.q !== undefined) L(e.q, e.side).ast++;
        }
        break;
      }
      case "blk": {
        // logged on the defense; the shooter is on the other side
        L(e.p!, e.side).blk++;
        const sh = L(e.q!, other(e.side));
        sh.fga++;
        if (e.st === "three") sh.tpa++;
        break;
      }
      case "ft": {
        const l = L(e.p!, e.side);
        l.fta++;
        if (e.m) {
          l.ftm++;
          l.pts++;
        }
        break;
      }
      case "orb":
        L(e.p!, e.side).orb++;
        break;
      case "drb":
        L(e.p!, e.side).drb++;
        break;
      case "to":
        L(e.p!, e.side).tov++;
        break;
      case "stl":
        L(e.p!, e.side).stl++;
        L(e.q!, other(e.side)).tov++;
        break;
      case "foul":
        L(e.p!, e.side).pf++;
        fouls[e.side]++;
        break;
      case "ofoul": {
        const l = L(e.p!, e.side);
        l.pf++;
        l.tov++;
        break;
      }
    }
  }
  return { lines, on, fouls };
}

/** Game clock for an event: "12:34" left in the half, or in overtime. */
export function clockOf(e: Pick<PbpEvent, "t" | "per">): string {
  const start = e.per <= 2 ? (e.per - 1) * 1200 : 2400 + (e.per - 3) * 300;
  const len = e.per <= 2 ? 1200 : 300;
  const left = Math.max(0, len - (e.t - start));
  const m = Math.floor(left / 60);
  const s = Math.floor(left % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function periodLabel(per: number): string {
  return per === 1 ? "1st Half" : per === 2 ? "2nd Half" : per === 3 ? "OT" : `${per - 2}OT`;
}
