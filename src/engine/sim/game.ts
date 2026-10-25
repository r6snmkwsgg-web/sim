// Possession-by-possession college basketball game simulation.
//
// Each possession: (maybe) intentional foul -> turnover check -> non-shooting
// foul check -> shot loop (shooter, shot type, block/make/foul, rebound).
// Players carry composite skills derived from ratings, energy that drains on
// the floor, and a minutes target from the coach's rotation.

import { PREP_SHOT } from "../prep";
import type { BoxLine, PbpEvent, Player, Pos, ShotType, Strategy, Tendencies } from "../types";
import { Rng, clamp } from "../rng";

export interface SimTeam {
  tid: number;
  name: string;
  players: Player[]; // available players
  starters: number[];
  minutes: Record<number, number>;
  strategy: Strategy;
  tactics: number; // coach tactics 0-100
  /** game prep level 0-3 (the user's scouting) */
  prep?: number;
}

export interface SimOptions {
  neutral: boolean;
  homeAdv: number; // points
  pbp: boolean;
  injuries: boolean;
}

export interface SimInjury {
  pid: number;
  tid: number;
}

export interface SimResult {
  home: { pts: number; halves: number[]; lines: BoxLine[] };
  away: { pts: number; halves: number[]; lines: BoxLine[] };
  ot: number;
  poss: number;
  pbp: PbpEvent[];
  injuries: SimInjury[];
}

const POS_IDX: Record<Pos, number> = { PG: 0, SG: 1, SF: 2, PF: 3, C: 4 };
const TEMPO_POSS = [0, 62, 66, 69.7, 73.7, 77.7];

/** Deterministic pseudo-random [0,1) pair from two integers; keeps shot locations off the game RNG. */
function hash2(a: number, b: number): [number, number] {
  let h = Math.imul(a ^ 0x9e3779b9, 0x85ebca6b) ^ Math.imul(b + 0x632be5ab, 0xc2b2ae35);
  h ^= h >>> 15;
  h = Math.imul(h, 0x2c1b3c6d);
  h ^= h >>> 12;
  const u = (h >>> 0) / 4294967296;
  let g = Math.imul(h ^ 0x27d4eb2d, 0x165667b1);
  g ^= g >>> 15;
  return [u, (g >>> 0) / 4294967296];
}

/** Where on a half court a shot of this type came from (feet; basket at 25, 5.25). */
function shotSpot(type: ShotType, a: number, b: number): [number, number] {
  const [u, v] = hash2(a, b);
  const at = (r: number, deg: number): [number, number] => {
    const th = (deg * Math.PI) / 180;
    return [Math.round((25 + r * Math.sin(th)) * 10) / 10, Math.round((5.25 + r * Math.cos(th)) * 10) / 10];
  };
  switch (type) {
    case "three":
      if (u < 0.28) return [v < 0.5 ? 3 + v * 0.8 : 47 - (1 - v) * 0.8, Math.round((1.5 + ((u * 1000) % 1) * 11) * 10) / 10];
      return at(23.9 + v * 2.6, -68 + ((u - 0.28) / 0.72) * 136);
    case "mid":
      return at(9 + v * 10, -85 + u * 170);
    case "post":
      return at(3 + v * 6, -75 + u * 150);
    default:
      return at(0.6 + v * 3.6, -100 + u * 200);
  }
}

interface GP {
  p: Player;
  pid: number;
  name: string;
  posIdx: number;
  ovr: number;
  hf: number;
  // composites 0..1
  rim: number;
  post: number;
  drive: number;
  mid: number;
  three: number;
  ft: number;
  pass: number;
  sec: number;
  reb: number;
  perD: number;
  intD: number;
  blk: number;
  stl: number;
  foulProp: number;
  /** uncompressed skills, used to decide which teammate gets credit for a play */
  raw: { reb: number; stl: number; blk: number; pass: number };
  offSkill: number;
  end: number;
  tend: Tendencies;
  shotW: number[]; // base weights [three, mid, post, drive]
  usageBase: number;
  // game state
  energy: number;
  on: boolean;
  fouls: number;
  out: boolean; // fouled out or injured
  starter: boolean;
  target: number; // target seconds
  // stats
  sec_: number;
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
  stl_: number;
  blk_: number;
  tov: number;
  pf: number;
  pm: number;
}

interface TS {
  side: 0 | 1;
  tid: number;
  name: string;
  roster: GP[];
  on: GP[];
  onSorted: GP[];
  strat: Strategy;
  tactics: number;
  prep: number;
  pts: number;
  halves: number[];
  teamFouls: number; // current half
  tempoPoss: number;
  shootAdj: number; // home court shooting adjustment
  form: number; // game-day hot/cold shooting
  // on-court aggregates
  aSec: number;
  aStl: number;
  aReb: number;
  aPerD: number;
  aIntD: number;
  aBlk: number;
  aBlkMax: number;
  aPass: number;
}

function R(p: Player, k: keyof Player["r"]) {
  return p.r[k] / 100;
}

function makeGP(p: Player, starters: number[], minutes: Record<number, number>): GP {
  const hf = clamp((p.hgt - 70) / 16, 0, 1);
  const ins = R(p, "ins");
  const ath = R(p, "ath");
  const str = R(p, "str");
  const hnd = R(p, "hnd");
  const iq = R(p, "iq");
  const rim = 0.45 * ins + 0.2 * ath + 0.15 * str + 0.2 * hf;
  const post = 0.55 * ins + 0.2 * str + 0.25 * hf;
  const drive = 0.35 * hnd + 0.35 * ath + 0.3 * ins;
  const mid = 0.85 * R(p, "mid") + 0.15 * iq;
  const three = 0.9 * R(p, "three") + 0.1 * iq;
  const shots = [three, mid, post, drive].sort((a, b) => b - a);
  const offSkill = 0.42 * shots[0] + 0.25 * shots[1] + 0.13 * iq + 0.1 * ath + 0.1 * hnd;
  // how strongly rating gaps turn into results; shot selection and usage use the raw skills
  const k = (x: number) => 0.5 + SKILL_SCALE * (x - 0.5);
  const gp: GP = {
    p,
    pid: p.id,
    name: `${p.first} ${p.last}`,
    posIdx: POS_IDX[p.pos],
    ovr: p.ovr,
    hf,
    rim: k(rim),
    post: k(post),
    drive: k(drive),
    mid: k(mid),
    three: k(three),
    ft: R(p, "ft"),
    pass: k(0.6 * R(p, "pas") + 0.25 * iq + 0.15 * hnd),
    sec: k(0.5 * hnd + 0.3 * iq + 0.2 * R(p, "pas")),
    reb: k(0.55 * R(p, "reb") + 0.25 * hf + 0.12 * str + 0.08 * ath),
    perD: k(0.6 * R(p, "perD") + 0.25 * ath + 0.15 * iq),
    intD: k(0.5 * R(p, "intD") + 0.25 * hf + 0.15 * str + 0.1 * R(p, "blk")),
    blk: k(0.6 * R(p, "blk") + 0.3 * hf + 0.1 * ath),
    stl: k(0.7 * R(p, "stl") + 0.2 * R(p, "perD") + 0.1 * ath),
    foulProp: clamp(1.25 - 0.6 * iq - 0.25 * R(p, "perD"), 0.4, 1.3),
    raw: {
      reb: 0.55 * R(p, "reb") + 0.25 * hf + 0.12 * str + 0.08 * ath,
      stl: 0.7 * R(p, "stl") + 0.2 * R(p, "perD") + 0.1 * ath,
      blk: 0.6 * R(p, "blk") + 0.3 * hf + 0.1 * ath,
      pass: 0.6 * R(p, "pas") + 0.25 * iq + 0.15 * hnd,
    },
    offSkill,
    end: R(p, "end"),
    tend: p.tend,
    shotW: [
      Math.pow(three, 2.6) * 3.85,
      Math.pow(mid, 2) * 1.15,
      Math.pow(post, 2) * 1.6 * (0.35 + hf),
      Math.pow(drive, 2) * 1.35 * (1 - hf * 0.55),
    ],
    usageBase: Math.exp(3.9 * offSkill),
    energy: 1,
    on: false,
    fouls: 0,
    out: false,
    starter: starters.includes(p.id),
    target: (minutes[p.id] ?? 0) * 60,
    sec_: 0,
    pts: 0,
    fgm: 0,
    fga: 0,
    tpm: 0,
    tpa: 0,
    ftm: 0,
    fta: 0,
    orb: 0,
    drb: 0,
    ast: 0,
    stl_: 0,
    blk_: 0,
    tov: 0,
    pf: 0,
    pm: 0,
  };
  return gp;
}

// game-to-game randomness on shooting, and how much a lead pulls efficiency back
export let FORM_SD = 0.025;
export let SCORE_EFFECT = 0.0025;
export let SKILL_SCALE = 0.87;
/** Calibration hook for scripts. */
export function setTuning(form: number, scoreEffect: number, skillScale = SKILL_SCALE) {
  FORM_SD = form;
  SCORE_EFFECT = scoreEffect;
  SKILL_SCALE = skillScale;
}

export class GameSim {
  rng: Rng;
  opts: SimOptions;
  t: [TS, TS];
  elapsed = 0; // seconds elapsed in current period
  per = 1;
  periodLen = 1200;
  totalPoss = 0;
  pbp: PbpEvent[] = [];
  injuries: SimInjury[] = [];
  deadBall = true;
  needSub = false;
  lastMediaTO = 0;

  constructor(home: SimTeam, away: SimTeam, rng: Rng, opts: SimOptions) {
    this.rng = rng;
    this.opts = opts;
    this.t = [this.makeTS(home, 0), this.makeTS(away, 1)];
    for (const ts of this.t) ts.form = rng.normal(0, FORM_SD);
    const avgTempo = (this.t[0].tempoPoss + this.t[1].tempoPoss) / 2;
    for (const ts of this.t) ts.tempoPoss = 0.55 * ts.tempoPoss + 0.45 * avgTempo;
    if (!opts.neutral) {
      // calibrated so the average home margin matches the setting in points
      const adj = opts.homeAdv * 0.0048;
      this.t[0].shootAdj = adj;
      this.t[1].shootAdj = -adj;
    }
  }

  makeTS(st: SimTeam, side: 0 | 1): TS {
    const roster = st.players.map((p) => makeGP(p, st.starters, st.minutes));
    const press = st.strategy.defense === "press" ? 3 : 0;
    return {
      side,
      tid: st.tid,
      name: st.name,
      roster,
      on: [],
      onSorted: [],
      strat: st.strategy,
      tactics: st.tactics,
      prep: st.prep ?? 0,
      pts: 0,
      halves: [],
      teamFouls: 0,
      tempoPoss: TEMPO_POSS[st.strategy.tempo] + press,
      shootAdj: 0,
      form: 0,
      aSec: 0,
      aStl: 0,
      aReb: 0,
      aPerD: 0,
      aIntD: 0,
      aBlk: 0,
      aBlkMax: 0,
      aPass: 0,
    };
  }

  // ---------- play-by-play ----------
  log(side: 0 | 1, text: string, extra?: Partial<PbpEvent>) {
    if (!this.opts.pbp) return;
    const t = this.per <= 2 ? (this.per - 1) * 1200 + this.elapsed : 2400 + (this.per - 3) * 300 + this.elapsed;
    this.pbp.push({ t: Math.round(t), per: this.per, side, text, hs: this.t[0].pts, as: this.t[1].pts, ...extra });
  }
  shotLog(side: 0 | 1, text: string, k: "fg" | "blk", p: number, q: number | undefined, st: ShotType, m: 0 | 1) {
    if (!this.opts.pbp) return;
    const shooter = k === "blk" ? q! : p;
    const [x, y] = shotSpot(st, this.pbp.length, shooter);
    this.log(side, text, { k, p, q, st, m, x, y });
  }

  // ---------- lineups ----------
  remaining(): number {
    return this.periodLen - this.elapsed;
  }

  gameElapsed(): number {
    if (this.per <= 2) return (this.per - 1) * 1200 + this.elapsed;
    return 2400;
  }

  lineupScore(ts: TS, g: GP, opp: TS, start: boolean): number {
    const fat = 0.75 + 0.25 * g.energy;
    let s = g.ovr * fat;
    const ge = this.gameElapsed();
    const margin = ts.pts - opp.pts;
    const late = this.per >= 2 ? this.remaining() : 9999;
    const regulation = this.per <= 2;
    if (regulation) {
      const expected = g.target * (ge / 2400);
      const deficit = expected - g.sec_;
      s += clamp(deficit / 25, -25, 25);
      if (g.target <= 0) s -= 60;
    }
    if (g.energy < 0.72) s -= (0.72 - g.energy) * 90;
    if (this.per === 1 && g.fouls >= 2) s -= g.fouls >= 3 ? 30 : 14;
    if (this.per === 2 && g.fouls >= 4 && late > 300) s -= 16;
    if (start && g.starter) s += this.per === 1 ? 1000 : 6;
    // garbage time: empty the bench
    if (this.per === 2 && ((Math.abs(margin) >= 20 && late < 300) || (Math.abs(margin) >= 27 && late < 600))) {
      s = 100 - g.ovr + (g.target > 0 ? 0 : 5);
    } else if (this.per >= 2 && late < 240 && Math.abs(margin) <= 10) {
      // crunch time: best players
      s = g.ovr * (0.8 + 0.2 * g.energy) + (g.starter ? 3 : 0);
      if (g.fouls >= 4) s -= 3;
    }
    return s;
  }

  sbuf = new Float64Array(32);
  setLineup(ts: TS, opp: TS, start: boolean) {
    const roster = ts.roster;
    const n = roster.length;
    const sc = this.sbuf;
    let availN = 0;
    for (let i = 0; i < n; i++) {
      const g = roster[i];
      if (g.out) sc[i] = -1e9;
      else {
        sc[i] = this.lineupScore(ts, g, opp, start);
        availN++;
      }
    }
    if (availN === 0) return;
    // order indices by score (insertion sort, n <= 15)
    const order: number[] = [];
    for (let i = 0; i < n; i++) {
      if (roster[i].out) continue;
      let j = order.length;
      order.push(i);
      while (j > 0 && sc[order[j - 1]] < sc[i]) {
        order[j] = order[j - 1];
        j--;
      }
      order[j] = i;
    }
    const k = Math.min(5, order.length);
    const pick: GP[] = [];
    for (let i = 0; i < k; i++) pick.push(roster[order[i]]);
    // positional sanity: at least one guard, at least one big, at most three bigs
    let guards = 0;
    let bigs = 0;
    for (const g of pick) {
      if (g.posIdx <= 1) guards++;
      else if (g.posIdx >= 3) bigs++;
    }
    if (guards === 0) {
      for (let i = k; i < order.length; i++) {
        const c = roster[order[i]];
        if (c.posIdx <= 1) {
          for (let j = pick.length - 1; j >= 0; j--) {
            if (pick[j].posIdx > 1) {
              if (pick[j].posIdx >= 3) bigs--;
              pick[j] = c;
              guards++;
              break;
            }
          }
          break;
        }
      }
    }
    if (bigs === 0) {
      for (let i = k; i < order.length; i++) {
        const c = roster[order[i]];
        if (c.posIdx >= 3) {
          for (let j = pick.length - 1; j >= 0; j--) {
            if (pick[j].posIdx === 2 || (pick[j].posIdx <= 1 && guards > 1)) {
              if (pick[j].posIdx <= 1) guards--;
              pick[j] = c;
              bigs++;
              break;
            }
          }
          break;
        }
      }
    }
    if (bigs > 3) {
      for (let i = k; i < order.length && bigs > 3; i++) {
        const c = roster[order[i]];
        if (c.posIdx >= 3 || pick.includes(c)) continue;
        for (let j = pick.length - 1; j >= 0; j--) {
          if (pick[j].posIdx >= 3) {
            pick[j] = c;
            bigs--;
            break;
          }
        }
      }
    }
    let final = pick;
    // hysteresis: keep on-court players unless the replacement is clearly better
    if (!start && ts.on.length === 5) {
      const scoreOf = (g: GP) => sc[roster.indexOf(g)];
      const keep: GP[] = [];
      const outgoing: GP[] = [];
      for (const g of ts.on) {
        if (pick.includes(g)) keep.push(g);
        else outgoing.push(g);
      }
      const incoming: GP[] = [];
      for (const g of pick) if (!ts.on.includes(g)) incoming.push(g);
      incoming.sort((a, b) => scoreOf(b) - scoreOf(a));
      outgoing.sort((a, b) => scoreOf(a) - scoreOf(b));
      final = keep;
      for (let i = 0; i < incoming.length; i++) {
        const out = outgoing[i];
        const inn = incoming[i];
        if (!out || out.out || scoreOf(inn) - scoreOf(out) > 2.5) final.push(inn);
        else final.push(out);
      }
      if (final.length > 5) final.length = 5;
    }
    if (this.opts.pbp && !start && ts.on.length) {
      const ins = final.filter((g) => !ts.on.includes(g));
      const outs = ts.on.filter((g) => !final.includes(g));
      for (let i = 0; i < ins.length; i++) {
        this.log(ts.side, `Substitution: ${ins[i].name} in${outs[i] ? ` for ${outs[i].name}` : ""}.`, { k: "sub", p: ins[i].pid, q: outs[i]?.pid });
      }
    }
    const changed = start || final.length !== ts.on.length || final.some((g) => !ts.on.includes(g));
    for (const g of roster) g.on = false;
    for (const g of final) g.on = true;
    ts.on = final;
    if (this.opts.pbp && changed) this.log(ts.side, "", { k: "lu", lu: final.map((g) => g.pid) });
    ts.onSorted = final.slice().sort((a, b) => a.posIdx - b.posIdx);
    this.aggregates(ts);
  }

  aggregates(ts: TS) {
    let sec = 0, stl = 0, reb = 0, perD = 0, intD = 0, blk = 0, pass = 0, blkMax = 0;
    for (const g of ts.on) {
      const f = 0.86 + 0.14 * g.energy;
      sec += g.sec * f;
      stl += g.stl * f;
      reb += g.reb * f;
      perD += g.perD * f;
      intD += g.intD * f;
      blk += g.blk * f;
      if (g.blk * f > blkMax) blkMax = g.blk * f;
      pass += g.pass * f;
    }
    const n = ts.on.length || 1;
    ts.aSec = sec / n;
    ts.aStl = stl / n;
    ts.aReb = reb / n;
    ts.aPerD = perD / n;
    ts.aIntD = intD / n;
    ts.aBlk = blk / n;
    ts.aBlkMax = blkMax;
    ts.aPass = pass / n;
  }

  anyTired(ts: TS): boolean {
    for (const g of ts.on) if (g.energy < 0.68) return true;
    return false;
  }

  // ---------- clock / fatigue ----------
  runClock(dt: number) {
    const pressMult = [this.t[0], this.t[1]].map((ts) => (ts.strat.defense === "press" ? 1.25 : 1));
    for (let s = 0; s < 2; s++) {
      const ts = this.t[s];
      for (const g of ts.roster) {
        if (g.on) {
          g.sec_ += dt;
          const tempoMult = 0.85 + (ts.tempoPoss - 61) / 100;
          g.energy -= dt * 0.00052 * (1.5 - g.end) * pressMult[s] * tempoMult;
          if (g.energy < 0.3) g.energy = 0.3;
        } else {
          g.energy = Math.min(1, g.energy + dt * 0.0013);
        }
      }
    }
    if (this.opts.injuries && this.rng.next() < dt * 1.5e-5) {
      const ts = this.t[this.rng.next() < 0.5 ? 0 : 1];
      const g = ts.on[Math.floor(this.rng.next() * ts.on.length)];
      if (g && !g.out) {
        g.out = true;
        this.needSub = true;
        this.injuries.push({ pid: g.pid, tid: ts.tid });
        this.log(ts.side, `${g.name} is injured and leaves the game.`, { k: "inj", p: g.pid });
      }
    }
    this.elapsed += dt;
  }

  // ---------- helpers ----------
  wbuf = new Float64Array(32);
  pickWeighted(arr: GP[], w: (g: GP) => number, exclude?: GP): GP {
    let total = 0;
    const ws = this.wbuf;
    for (let i = 0; i < arr.length; i++) {
      const g = arr[i];
      const x = g === exclude ? 0 : Math.max(0, w(g));
      ws[i] = x;
      total += x;
    }
    if (total <= 0) return arr[Math.floor(this.rng.next() * arr.length)];
    let r = this.rng.next() * total;
    for (let i = 0; i < arr.length; i++) {
      r -= ws[i];
      if (r < 0) return arr[i];
    }
    return arr[arr.length - 1];
  }

  score(off: TS, def: TS, g: GP, pts: number) {
    off.pts += pts;
    g.pts += pts;
    for (const x of off.on) x.pm += pts;
    for (const x of def.on) x.pm -= pts;
  }

  foul(def: TS, fouler: GP, shooting: boolean, off: TS) {
    fouler.pf++;
    fouler.fouls++;
    def.teamFouls++;
    this.log(def.side, `${shooting ? "Shooting foul" : "Foul"} on ${fouler.name}.`, { k: "foul", p: fouler.pid });
    if (fouler.fouls >= 5) {
      fouler.out = true;
      this.log(def.side, `${fouler.name} has fouled out.`, { k: "info", p: fouler.pid });
      this.setLineup(def, off, false);
    }
  }

  freeThrows(off: TS, def: TS, shooter: GP, n: number, oneAndOne = false): boolean {
    // returns true if the final free throw was missed (live rebound)
    const p = clamp(0.415 + 0.62 * shooter.ft + off.shootAdj * 0.5, 0.35, 0.95);
    let lastMissed = false;
    for (let i = 0; i < n; i++) {
      shooter.fta++;
      if (this.rng.next() < p) {
        shooter.ftm++;
        this.score(off, def, shooter, 1);
        this.log(off.side, `${shooter.name} makes free throw ${i + 1} of ${oneAndOne ? "1-and-1" : n}.`, { k: "ft", p: shooter.pid, m: 1 });
        lastMissed = false;
        if (oneAndOne && i === 0) n = 2;
      } else {
        this.log(off.side, `${shooter.name} misses free throw ${i + 1} of ${oneAndOne ? "1-and-1" : n}.`, { k: "ft", p: shooter.pid, m: 0 });
        lastMissed = true;
        if (oneAndOne && i === 0) break;
      }
    }
    return lastMissed;
  }

  bonusFreeThrows(off: TS, def: TS, shooter: GP): "made" | "miss" | "none" {
    if (def.teamFouls >= 10) return this.freeThrows(off, def, shooter, 2) ? "miss" : "made";
    if (def.teamFouls >= 7) return this.freeThrows(off, def, shooter, 1, true) ? "miss" : "made";
    return "none";
  }

  rebound(off: TS, def: TS, afterFt: boolean, blocked: boolean): boolean {
    // returns true if offense rebounds
    let p = 0.29 * Math.exp(1.9 * (off.aReb - def.aReb));
    if (off.strat.rebounding === "crash") p *= 1.13;
    if (off.strat.rebounding === "getback") p *= 0.84;
    if (def.strat.defense === "zone") p *= 1.07;
    if (afterFt) p *= 0.45;
    if (blocked) p += 0.08;
    p = clamp(p, 0.08, 0.55);
    if (this.rng.next() < p) {
      const g = this.pickWeighted(off.on, (x) => Math.pow(x.raw.reb, 1.5) * (0.7 + 0.6 * x.hf));
      g.orb++;
      this.log(off.side, `Offensive rebound by ${g.name}.`, { k: "orb", p: g.pid });
      return true;
    }
    const g = this.pickWeighted(def.on, (x) => Math.pow(x.raw.reb, 1.5) * (0.75 + 0.6 * x.hf));
    g.drb++;
    this.log(def.side, `Defensive rebound by ${g.name}.`, { k: "drb", p: g.pid });
    return false;
  }

  // ---------- possession ----------
  possession(off: TS, def: TS) {
    const rem = this.remaining();
    const margin = off.pts - def.pts;
    const lateGame = this.per >= 2 && rem < 50;
    // possession length
    let mean = 1200 / off.tempoPoss;
    if (def.strat.defense === "press") mean *= 0.93;
    let dt = mean * (0.35 + 1.3 * this.rng.next());
    // only a few seconds to go the length of the floor: a rushed look at best
    const rushed = rem < 5.5;
    if (lateGame && margin > 0) dt = Math.min(30, rem); // milk the clock
    // tied or within a possession inside the shot clock: play for the last shot
    if (this.per >= 2 && margin <= 0 && margin >= -3 && rem <= 30 && !rushed) dt = Math.max(0.6, rem - (margin === 0 ? this.rng.uniform(0.5, 3) : this.rng.uniform(1.5, 5)));
    else if (lateGame && margin < 0 && margin >= -3) dt = Math.min(dt, Math.max(2, rem - 3));
    if (lateGame && margin < -3) dt = Math.min(dt, 7);

    // intentional foul when the defense trails late: right away when down two
    // possessions, otherwise once the shot clock is off
    if (this.per >= 2 && margin >= 1 && margin <= 8 && rem > 2 && (rem < 34 || (margin >= 4 && rem < 45))) {
      const t = Math.min(rem, this.rng.uniform(2, 6));
      this.runClock(t);
      const handler = this.pickWeighted(off.on, (x) => Math.pow(x.sec, 2));
      const fouler = this.pickWeighted(def.on, () => 1);
      this.foul(def, fouler, false, off);
      const r = this.bonusFreeThrows(off, def, handler);
      if (r === "none") {
        // not in the bonus yet: offense inbounds, play on with less time
        this.halfCourt(off, def, Math.min(this.remaining(), 8));
      } else if (r === "miss") {
        if (this.rebound(off, def, true, false)) this.halfCourt(off, def, Math.min(this.remaining(), 6));
      }
      this.deadBall = true;
      return;
    }

    if (dt >= rem) dt = rem;
    this.halfCourt(off, def, dt, rushed);
  }

  halfCourt(off: TS, def: TS, dt: number, rushed = false) {
    const buzzer = rushed || (dt >= this.remaining() - 0.01 && this.remaining() < 4);
    this.runClock(dt * 0.6);
    // turnover
    let to = 0.168 * Math.exp(-2.05 * (off.aSec - 0.5)) * Math.exp(1.7 * (def.aStl - 0.5));
    if (def.strat.defense === "press") to *= 1.22;
    if (def.strat.defense === "zone") to *= 0.95;
    to *= 1 - (off.tactics - 50) / 500 + (def.tactics - 50) / 700;
    if (this.rng.next() < to) {
      const g = this.pickWeighted(off.on, (x) => x.usageBase * (1.35 - x.sec));
      g.tov++;
      let stealP = 0.5 * Math.exp(1.6 * (def.aStl - 0.5));
      if (def.strat.defense === "press") stealP *= 1.15;
      if (def.strat.defense === "zone") stealP *= 0.88;
      if (this.rng.next() < stealP) {
        const s = this.pickWeighted(def.on, (x) => Math.pow(x.raw.stl, 1.25) * (x.posIdx <= 2 ? 1.15 : 0.9));
        s.stl_++;
        this.log(def.side, `${s.name} steals the ball from ${g.name}.`, { k: "stl", p: s.pid, q: g.pid });
        this.deadBall = false;
      } else if (this.rng.next() < 0.18) {
        g.pf++;
        g.fouls++;
        this.log(off.side, `Offensive foul on ${g.name}.`, { k: "ofoul", p: g.pid });
        if (g.fouls >= 5) {
          g.out = true;
          this.log(off.side, `${g.name} has fouled out.`, { k: "info", p: g.pid });
          this.setLineup(off, def, false);
        }
        this.deadBall = true;
      } else {
        this.log(off.side, `Turnover by ${g.name}.`, { k: "to", p: g.pid });
        this.deadBall = true;
      }
      this.runClock(dt * 0.4);
      return;
    }
    // non-shooting foul
    let nsf = 0.158;
    if (def.strat.defense === "press") nsf *= 1.15;
    if (def.strat.defense === "zone") nsf *= 0.85;
    if (this.rng.next() < nsf) {
      const fouler = this.pickWeighted(def.on, (x) => x.foulProp);
      const victim = this.pickWeighted(off.on, (x) => x.usageBase);
      this.foul(def, fouler, false, off);
      const r = this.bonusFreeThrows(off, def, victim);
      if (r !== "none") {
        this.runClock(dt * 0.4);
        if (r === "miss" && !this.rebound(off, def, true, false)) {
          this.deadBall = false;
          return;
        }
        if (r === "made") {
          this.deadBall = true;
          return;
        }
      }
    }
    this.runClock(dt * 0.4);
    // shot loop
    let shots = 0;
    let putback = false;
    while (shots < 5) {
      shots++;
      const res = this.shot(off, def, putback, buzzer && shots === 1);
      if (res === "made" || res === "ft-made") {
        this.deadBall = true;
        return;
      }
      if (res === "ft-dead") {
        this.deadBall = true;
        return;
      }
      // missed: rebound
      const blocked = res === "blocked";
      const orb = this.rebound(off, def, res === "ft-miss", blocked);
      if (!orb) {
        this.deadBall = false;
        return;
      }
      if (this.remaining() <= 0.5) return;
      // putback chance right away, else reset
      putback = this.rng.next() < 0.42;
      const extra = putback ? 2 : Math.min(this.remaining(), this.rng.uniform(4, 14));
      this.runClock(Math.min(extra, this.remaining()));
    }
  }

  chooseShot(off: TS, def: TS, g: GP, putback: boolean): ShotType {
    if (putback) return "putback";
    const t = g.tend;
    const w = [
      g.shotW[0] * (t.three / 5),
      g.shotW[1] * (t.mid / 5),
      g.shotW[2] * (t.inside / 5),
      g.shotW[3] * (t.drive / 5),
    ];
    if (off.strat.offense === "inside") {
      w[0] *= 0.78;
      w[2] *= 1.3;
      w[3] *= 1.15;
    } else if (off.strat.offense === "perimeter") {
      w[0] *= 1.3;
      w[2] *= 0.78;
      w[1] *= 1.05;
    }
    if (def.strat.defense === "zone") {
      w[0] *= 1.17;
      w[2] *= 0.85;
      w[3] *= 0.85;
    }
    const margin = off.pts - def.pts;
    if (this.per >= 2 && this.remaining() < 30 && margin <= -3 && margin >= -5) w[0] *= 6;
    if (this.per >= 2 && this.remaining() < 120 && margin < -6) w[0] *= 1.7;
    const i = this.rng.weighted(w);
    return (["three", "mid", "post", "drive"] as const)[i];
  }

  shot(off: TS, def: TS, putback: boolean, buzzer: boolean): "made" | "miss" | "blocked" | "ft-made" | "ft-miss" | "ft-dead" {
    // shooter
    let g: GP;
    // down three late: look for the best shooter and a three to tie
    const needThree = !putback && this.per >= 2 && this.remaining() < 35 && def.pts - off.pts === 3;
    // down two late: most coaches go to the rim for the tie
    const needTwo = !putback && this.per >= 2 && this.remaining() < 30 && def.pts - off.pts === 2 && this.rng.next() < 0.7;
    if (putback) {
      g = this.pickWeighted(off.on, (x) => Math.pow(x.raw.reb, 3) * (0.6 + x.hf));
    } else if (needThree) {
      g = this.pickWeighted(off.on, (x) => Math.pow(x.three, 4) * x.usageBase);
    } else {
      g = this.pickWeighted(off.on, (x) => x.usageBase * ((x.tend.three + x.tend.mid + x.tend.inside + x.tend.drive) / 20 + 0.02));
    }
    const type = needThree ? "three" : needTwo ? (g.posIdx >= 3 ? "post" : "drive") : this.chooseShot(off, def, g, putback);
    // matchup defender: same lineup slot by position order
    const sortedDef = def.onSorted;
    const sortedOff = off.onSorted;
    const slot = Math.max(0, sortedOff.indexOf(g));
    const md = sortedDef[Math.min(slot, sortedDef.length - 1)] ?? def.on[0];
    const ef = 0.92 + 0.08 * g.energy;
    const zone = def.strat.defense === "zone";
    const perD = zone ? def.aPerD : 0.6 * md.perD + 0.4 * def.aPerD;
    const intD = zone ? def.aIntD + 0.02 : 0.5 * md.intD + 0.5 * def.aIntD;
    let p: number;
    let blockP: number;
    let foulP: number;
    let assistP: number;
    let isThree = false;
    switch (type) {
      case "three":
        p = 0.322 + 0.36 * (g.three - 0.5) - 0.11 * (perD - 0.5);
        blockP = 0.015;
        foulP = 0.022;
        assistP = 0.88;
        isThree = true;
        break;
      case "mid":
        p = 0.37 + 0.31 * (g.mid - 0.5) - 0.1 * (0.5 * perD + 0.5 * intD - 0.5);
        blockP = 0.045;
        foulP = 0.08;
        assistP = 0.46;
        break;
      case "post":
        p = 0.495 + 0.34 * (g.post - 0.5) - 0.24 * (intD - 0.5);
        blockP = 0.115;
        foulP = 0.2;
        assistP = 0.54;
        break;
      case "drive":
        p = 0.52 + 0.31 * (g.drive - 0.5) - 0.19 * (0.4 * perD + 0.6 * intD - 0.5);
        blockP = 0.105;
        foulP = 0.255;
        assistP = 0.25;
        break;
      default:
        p = 0.57 + 0.26 * (g.rim - 0.5) - 0.13 * (intD - 0.5);
        blockP = 0.09;
        foulP = 0.17;
        assistP = 0.04;
    }
    // game planning on both ends: a great tactician is worth about two points a night per standout
    p = p * ef + off.shootAdj + off.form + (off.tactics - 50) * 0.0006 - (def.tactics - 50) * 0.0004;
    // scouting: a prepared offense gets better looks, a prepared defense knows the sets
    p += PREP_SHOT[off.prep] - PREP_SHOT[def.prep];
    // score effects: teams with a lead relax and trailing teams press, more so as the game goes on
    const lead = Math.max(-20, Math.min(20, off.pts - def.pts));
    p -= lead * SCORE_EFFECT * (0.4 + this.gameElapsed() / 2400);
    if (def.strat.defense === "press") p += 0.012; // press gives up easier looks when broken
    if (def.strat.rebounding === "crash") p += 0.006; // transition opportunities
    if (buzzer) p *= 0.45;
    // the last shot of a close game is a set play against a set defense
    else if (this.per >= 2 && this.remaining() < 8 && Math.abs(off.pts - def.pts) <= 3) p *= 0.82;
    p = clamp(p, 0.05, 0.9);
    // rim protection: the best shot-blocker on the floor matters as much as the average
    blockP *= Math.exp(3.2 * (0.45 * def.aBlk + 0.55 * def.aBlkMax - 0.56));
    // shooting foul?
    if (!buzzer && this.rng.next() < foulP) {
      const fouler = this.rng.next() < 0.55 ? md : this.pickWeighted(def.on, (x) => x.foulProp * (type === "three" ? 1 : 0.5 + x.hf));
      const andOneP = p * 0.42;
      g.fga++;
      if (isThree) g.tpa++;
      this.foul(def, fouler, true, off);
      if (this.rng.next() < andOneP) {
        g.fgm++;
        if (isThree) g.tpm++;
        this.score(off, def, g, isThree ? 3 : 2);
        this.shotLog(off.side, `${g.name} scores and draws the foul! ${this.shotText(type, true)}`, "fg", g.pid, undefined, type, 1);
        const missed = this.freeThrows(off, def, g, 1);
        return missed ? "ft-miss" : "ft-made";
      }
      // a fouled missed shot is not an FGA
      g.fga--;
      if (isThree) g.tpa--;
      const missed = this.freeThrows(off, def, g, isThree ? 3 : 2);
      return missed ? "ft-miss" : "ft-made";
    }
    g.fga++;
    if (isThree) g.tpa++;
    if (this.rng.next() < p) {
      g.fgm++;
      if (isThree) g.tpm++;
      this.score(off, def, g, isThree ? 3 : 2);
      let assister: GP | null = null;
      if (this.rng.next() < assistP * (0.75 + 0.5 * off.aPass)) {
        assister = this.pickWeighted(off.on, (x) => Math.pow(x.raw.pass, 5) * (x.posIdx === 0 ? 1.7 : x.posIdx === 1 ? 1.15 : 1), g);
        if (assister === g) assister = null;
        else assister.ast++;
      }
      this.shotLog(off.side, `${g.name} ${this.shotText(type, true)}${assister ? ` (assist: ${assister.name})` : ""}`, "fg", g.pid, assister?.pid, type, 1);
      return "made";
    }
    // miss: blocked?
    if (this.rng.next() < Math.min(0.6, blockP / (1 - p))) {
      const b = this.pickWeighted(def.on, (x) => Math.pow(x.raw.blk, 7) * (0.4 + x.hf) * (x === md ? 1.4 : 1));
      b.blk_++;
      this.shotLog(def.side, `${b.name} blocks ${g.name}'s shot!`, "blk", b.pid, g.pid, type, 0);
      return "blocked";
    }
    this.shotLog(off.side, `${g.name} ${this.shotText(type, false)}`, "fg", g.pid, undefined, type, 0);
    return "miss";
  }

  shotText(type: ShotType, made: boolean): string {
    switch (type) {
      case "three":
        return made ? "hits a three-pointer." : "misses a three-pointer.";
      case "mid":
        return made ? "knocks down a mid-range jumper." : "misses a mid-range jumper.";
      case "post":
        return made ? "scores in the post." : "misses a hook shot in the post.";
      case "drive":
        return made ? (this.rng.next() < 0.3 ? "throws down a dunk on the drive!" : "finishes a layup on the drive.") : "misses a driving layup.";
      default:
        return made ? "puts back the offensive rebound." : "misses the putback.";
    }
  }

  // ---------- game loop ----------
  playPeriod(first: 0 | 1) {
    let off = first;
    this.elapsed = 0;
    for (const ts of this.t) ts.teamFouls = 0;
    this.lastMediaTO = 0;
    while (this.remaining() > 0.25) {
      // substitutions at dead balls and media timeouts
      const mediaMark = Math.floor(this.elapsed / 240);
      const media = this.per <= 2 && mediaMark > this.lastMediaTO;
      if (media) {
        this.lastMediaTO = mediaMark;
        for (const ts of this.t) for (const g of ts.roster) if (!g.on) g.energy = Math.min(1, g.energy + 0.02);
      }
      const late = this.per >= 2 && this.remaining() < 300;
      const tired = this.deadBall && (this.anyTired(this.t[0]) || this.anyTired(this.t[1]));
      if (media || this.needSub || tired || (this.deadBall && this.rng.next() < (late ? 0.5 : 0.18))) {
        this.needSub = false;
        this.setLineup(this.t[0], this.t[1], false);
        this.setLineup(this.t[1], this.t[0], false);
      } else {
        this.aggregates(this.t[0]);
        this.aggregates(this.t[1]);
      }
      const o = this.t[off];
      const d = this.t[1 - off];
      this.totalPoss++;
      this.possession(o, d);
      off = (1 - off) as 0 | 1;
    }
  }

  run(): SimResult {
    const [h, a] = this.t;
    this.setLineup(h, a, true);
    this.setLineup(a, h, true);
    this.log(0, `Tip-off: ${h.name} vs ${a.name}.`, { k: "info" });
    const firstPoss: 0 | 1 = this.rng.next() < 0.5 ? 0 : 1;
    // 1st half
    this.per = 1;
    this.periodLen = 1200;
    this.playPeriod(firstPoss);
    h.halves.push(h.pts);
    a.halves.push(a.pts);
    this.log(0, `End of 1st half: ${h.name} ${h.pts}, ${a.name} ${a.pts}.`, { k: "info" });
    for (const ts of this.t) for (const g of ts.roster) g.energy = Math.min(1, g.energy + 0.45);
    this.per = 2;
    this.periodLen = 1200;
    this.elapsed = 0;
    this.setLineup(h, a, true);
    this.setLineup(a, h, true);
    this.playPeriod((1 - firstPoss) as 0 | 1);
    h.halves.push(h.pts - h.halves[0]);
    a.halves.push(a.pts - a.halves[0]);
    let ot = 0;
    while (h.pts === a.pts) {
      ot++;
      this.per = 2 + ot;
      this.periodLen = 300;
      this.elapsed = 0;
      this.log(0, `Overtime ${ot > 1 ? ot : ""}`.trim() + ` - tied at ${h.pts}.`, { k: "info" });
      for (const ts of this.t) for (const g of ts.roster) g.energy = Math.min(1, g.energy + 0.12);
      const hb = h.pts;
      const ab = a.pts;
      this.setLineup(h, a, false);
      this.setLineup(a, h, false);
      this.playPeriod(this.rng.next() < 0.5 ? 0 : 1);
      h.halves.push(h.pts - hb);
      a.halves.push(a.pts - ab);
      if (ot > 8) break;
    }
    this.log(0, `Final: ${h.name} ${h.pts}, ${a.name} ${a.pts}${ot ? ` (${ot > 1 ? ot : ""}OT)` : ""}.`, { k: "info" });
    const lines = (ts: TS): BoxLine[] =>
      ts.roster
        .filter((g) => g.sec_ > 0 || g.starter)
        .map((g) => ({
          pid: g.pid,
          name: g.name,
          pos: g.p.pos,
          starter: g.starter,
          min: Math.round(g.sec_ / 6) / 10,
          pts: g.pts,
          fgm: g.fgm,
          fga: g.fga,
          tpm: g.tpm,
          tpa: g.tpa,
          ftm: g.ftm,
          fta: g.fta,
          orb: g.orb,
          drb: g.drb,
          ast: g.ast,
          stl: g.stl_,
          blk: g.blk_,
          tov: g.tov,
          pf: g.pf,
          pm: g.pm,
        }))
        .sort((x, y) => Number(y.starter) - Number(x.starter) || y.min - x.min);
    return {
      home: { pts: h.pts, halves: h.halves, lines: lines(h) },
      away: { pts: a.pts, halves: a.halves, lines: lines(a) },
      ot,
      poss: Math.round(this.totalPoss / 2),
      pbp: this.pbp,
      injuries: this.injuries,
    };
  }
}

export function simGame(home: SimTeam, away: SimTeam, rng: Rng, opts: SimOptions): SimResult {
  return new GameSim(home, away, rng, opts).run();
}
