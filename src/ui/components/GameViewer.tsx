import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import type { BoxScore, League, PbpEvent, Team } from "../../engine/types";
import { team } from "../../engine/core";
import { clockOf, hasStructuredPbp, liveState, periodLabel, type LiveLine } from "../../engine/pbp";
import { replayPosition, setReplayPosition, setWatchGuard } from "../store";
import { cls, heroColors, hexToRgb, inkOn } from "../util";
import { Logo, Seg } from "./common";
import { Icon } from "./Icons";

const COURT_BG = "#121a26";
const SPEEDS = [
  { k: 1, label: "1x", perSec: 70, min: 420 },
  { k: 2, label: "2x", perSec: 34, min: 210 },
  { k: 4, label: "4x", perSec: 15, min: 95 },
  { k: 8, label: "8x", perSec: 6, min: 40 },
] as const;

function rgbDist(a: string, b: string): number {
  const [r1, g1, b1] = hexToRgb(a);
  const [r2, g2, b2] = hexToRgb(b);
  return Math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2);
}
/** Marker colors for both teams on the dark court; the away team switches colors when they'd clash. */
function teamInks(ht: Team, at: Team): [string, string] {
  const home = inkOn(ht.colors[0], COURT_BG, 3);
  for (const c of [at.colors[0], at.colors[1], "#e7ecf3", "#f2b631"]) {
    const ink = inkOn(c, COURT_BG, 3);
    if (rgbDist(ink, home) > 110) return [home, ink];
  }
  return [home, "#e7ecf3"];
}

/** Index of the next event worth showing (lineup bookkeeping events are skipped). */
function nextShown(ev: PbpEvent[], i: number): number {
  let j = i + 1;
  while (j < ev.length - 1 && ev[j].k === "lu") j++;
  return Math.min(j, ev.length - 1);
}

function gameLength(ev: PbpEvent[]): number {
  const last = ev[ev.length - 1];
  return last.per <= 2 ? 2400 : 2400 + (last.per - 2) * 300;
}

// ---------------- court ----------------
const ARC = 22.15; // NCAA three-point distance (ft)
const CORNER_Y = 25 - 21.65;
const ARC_X = 5.25 + Math.sqrt(ARC * ARC - 21.65 * 21.65);

function CourtLines() {
  const side = (right: boolean) => {
    const X = (x: number) => (right ? 94 - x : x);
    const sweep = right ? 0 : 1;
    return (
      <g>
        <rect x={right ? 75 : 0} y={19} width={19} height={12} className="cl-paint" />
        <path d={`M${X(19)},19 A6,6 0 0,${sweep} ${X(19)},31`} />
        <path d={`M${X(19)},19 A6,6 0 0,${1 - sweep} ${X(19)},31`} strokeDasharray="1 1" opacity={0.6} />
        <path d={`M${X(0)},${CORNER_Y} L${X(ARC_X)},${CORNER_Y} A${ARC},${ARC} 0 0,${sweep} ${X(ARC_X)},${50 - CORNER_Y} L${X(0)},${50 - CORNER_Y}`} />
        <path d={`M${X(5.25)},21 A4,4 0 0,${sweep} ${X(5.25)},29`} />
        <line x1={X(4)} y1={22} x2={X(4)} y2={28} strokeWidth={0.35} />
        <circle cx={X(5.25)} cy={25} r={0.75} className="cl-rim" />
      </g>
    );
  };
  return (
    <g className="cl">
      <rect x={0} y={0} width={94} height={50} />
      <line x1={47} y1={0} x2={47} y2={50} />
      <circle cx={47} cy={25} r={6} />
      <circle cx={47} cy={25} r={2} />
      {side(false)}
      {side(true)}
    </g>
  );
}

interface Shot {
  i: number;
  home: boolean;
  X: number;
  Y: number;
  made: boolean;
  three: boolean;
}

function shotsUpTo(ev: PbpEvent[], upto: number): Shot[] {
  const out: Shot[] = [];
  for (let i = 0; i <= upto && i < ev.length; i++) {
    const e = ev[i];
    if ((e.k !== "fg" && e.k !== "blk") || e.x === undefined || e.y === undefined) continue;
    // a block is logged for the defense; the shooting team is the other side
    const shooterSide = e.k === "blk" ? (e.side === 0 ? 1 : 0) : e.side;
    const home = shooterSide === 0;
    // home attacks the right basket, away the left
    const X = home ? 94 - e.y : e.y;
    const Y = home ? 50 - e.x : e.x;
    out.push({ i, home, X, Y, made: e.k === "fg" && e.m === 1, three: e.st === "three" });
  }
  return out;
}

function Court({ ev, upto, homeInk, awayInk }: { ev: PbpEvent[]; upto: number; homeInk: string; awayInk: string }) {
  const shots = useMemo(() => shotsUpTo(ev, upto), [ev, upto]);
  const lastShot = shots[shots.length - 1];
  return (
    <svg viewBox="-1 -1 96 52" className="court-svg" role="img" aria-label="Shot chart">
      <defs>
        <linearGradient id="floor" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#141d2b" />
          <stop offset="0.5" stopColor="#18233a" />
          <stop offset="1" stopColor="#141d2b" />
        </linearGradient>
      </defs>
      <rect x={-1} y={-1} width={96} height={52} rx={1.5} fill="url(#floor)" />
      <CourtLines />
      {shots.map((s) => {
        const c = s.home ? homeInk : awayInk;
        return s.made ? (
          <circle key={s.i} cx={s.X} cy={s.Y} r={0.95} fill={c} stroke={COURT_BG} strokeWidth={0.3} />
        ) : (
          <g key={s.i} stroke={c} strokeWidth={0.32} opacity={0.75} strokeLinecap="round">
            <line x1={s.X - 0.6} y1={s.Y - 0.6} x2={s.X + 0.6} y2={s.Y + 0.6} />
            <line x1={s.X - 0.6} y1={s.Y + 0.6} x2={s.X + 0.6} y2={s.Y - 0.6} />
          </g>
        );
      })}
      {lastShot && lastShot.i === upto && (
        <circle key={`p${lastShot.i}`} cx={lastShot.X} cy={lastShot.Y} r={1} fill="none" stroke={lastShot.home ? homeInk : awayInk} strokeWidth={0.35} className="shot-pulse" />
      )}
    </svg>
  );
}

// ---------------- lead tracker ----------------
function LeadTracker({
  ev,
  upto,
  ht,
  at,
  homeInk,
  awayInk,
  onSeek,
}: {
  ev: PbpEvent[];
  upto: number;
  ht: Team;
  at: Team;
  homeInk: string;
  awayInk: string;
  onSeek: (i: number) => void;
}) {
  const W = 600;
  const H = 96;
  const total = gameLength(ev);
  const ref = useRef<SVGSVGElement>(null);
  const [hover, setHover] = useState<number | null>(null);
  const pts = useMemo(() => {
    const out: { t: number; m: number; i: number }[] = [{ t: 0, m: 0, i: 0 }];
    for (let i = 0; i <= upto && i < ev.length; i++) out.push({ t: ev[i].t, m: ev[i].hs - ev[i].as, i });
    return out;
  }, [ev, upto]);
  let maxAbs = 10;
  for (const p of pts) maxAbs = Math.max(maxAbs, Math.abs(p.m));
  maxAbs = Math.ceil(maxAbs / 5) * 5;
  const X = (t: number) => (t / total) * W;
  const Y = (m: number) => H / 2 - (m / maxAbs) * (H / 2 - 10);
  const line = pts.map((p, k) => `${k ? "L" : "M"}${X(p.t).toFixed(1)},${Y(p.m).toFixed(1)}`).join("");
  const lastX = X(pts[pts.length - 1].t);
  const area = `${line}L${lastX.toFixed(1)},${H / 2}L0,${H / 2}Z`;
  const hp = hover !== null ? pts.reduce((best, p) => (Math.abs(X(p.t) - hover) < Math.abs(X(best.t) - hover) ? p : best), pts[0]) : null;
  const he = hp ? ev[hp.i] : null;
  return (
    <div className="lead-wrap">
      <div className="lead-keys">
        <span>
          <i style={{ background: homeInk }} /> {ht.short} lead
        </span>
        <span>
          <i style={{ background: awayInk }} /> {at.short} lead
        </span>
        <span className="spacer" />
        <span className="faint">Click to rewind</span>
      </div>
      <svg
        ref={ref}
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        className="lead-svg"
        onMouseMove={(e) => {
          const r = ref.current!.getBoundingClientRect();
          const x = ((e.clientX - r.left) / r.width) * W;
          setHover(x <= lastX + 4 ? x : null);
        }}
        onMouseLeave={() => setHover(null)}
        onClick={() => hp && onSeek(hp.i)}
      >
        <defs>
          <clipPath id="above">
            <rect x={0} y={0} width={W} height={H / 2} />
          </clipPath>
          <clipPath id="below">
            <rect x={0} y={H / 2} width={W} height={H / 2} />
          </clipPath>
        </defs>
        {[2400 / 2, 2400].map((t) => (t < total ? <line key={t} x1={X(t)} x2={X(t)} y1={0} y2={H} className="lead-grid" /> : null))}
        <line x1={0} x2={W} y1={H / 2} y2={H / 2} className="lead-zero" />
        <path d={area} fill={homeInk} opacity={0.22} clipPath="url(#above)" />
        <path d={area} fill={awayInk} opacity={0.22} clipPath="url(#below)" />
        <path d={line} fill="none" className="lead-line" strokeWidth={2} vectorEffect="non-scaling-stroke" />
        {hp && <line x1={X(hp.t)} x2={X(hp.t)} y1={0} y2={H} className="lead-cross" vectorEffect="non-scaling-stroke" />}
      </svg>
      {hp && he && (
        <div className="lead-tip" style={{ left: `${(X(hp.t) / W) * 100}%` }}>
          <b>
            {at.abbrev} {he.as} - {he.hs} {ht.abbrev}
          </b>
          <span>
            {clockOf(he)} {periodLabel(he.per)}
          </span>
        </div>
      )}
      <div className="lead-axis">
        <span>Tip</span>
        <span>Half</span>
        <span>{total > 2400 ? "End of reg." : "Final"}</span>
      </div>
    </div>
  );
}

// ---------------- live box ----------------
function LiveBox({ L, lines, on, starters, tid, names }: { L: League; lines: LiveLine[]; on: number[]; starters: number[]; tid: number; names: Map<number, string> }) {
  const t = team(L, tid);
  const order = lines
    .slice()
    .sort((a, b) => Number(starters.includes(b.pid)) - Number(starters.includes(a.pid)) || b.sec - a.sec || b.pts - a.pts);
  const tot = lines.reduce(
    (a, l) => {
      a.pts += l.pts;
      a.reb += l.orb + l.drb;
      a.ast += l.ast;
      a.fgm += l.fgm;
      a.fga += l.fga;
      a.tpm += l.tpm;
      a.tpa += l.tpa;
      return a;
    },
    { pts: 0, reb: 0, ast: 0, fgm: 0, fga: 0, tpm: 0, tpa: 0 },
  );
  return (
    <table className="tbl compact live-box">
      <thead>
        <tr>
          <th>{t.short}</th>
          <th className="n">MIN</th>
          <th className="n">PTS</th>
          <th className="n">REB</th>
          <th className="n">AST</th>
          <th className="n">FG</th>
          <th className="n">3PT</th>
          <th className="n">PF</th>
        </tr>
      </thead>
      <tbody>
        {order.map((l) => (
          <tr key={l.pid} className={on.includes(l.pid) ? "on" : ""}>
            <td>
              <span className="row" style={{ gap: 7 }}>
                <span className={cls("on-dot", on.includes(l.pid) && "lit")} />
                <Link to={`/l/${L.id}/player/${l.pid}`}>{names.get(l.pid) ?? `#${l.pid}`}</Link>
              </span>
            </td>
            <td className="n faint">{Math.round(l.sec / 60)}</td>
            <td className="n bold">{l.pts}</td>
            <td className="n">{l.orb + l.drb}</td>
            <td className="n">{l.ast}</td>
            <td className="n">
              {l.fgm}-{l.fga}
            </td>
            <td className="n">
              {l.tpm}-{l.tpa}
            </td>
            <td className={cls("n", l.pf >= 4 ? "bad bold" : "faint")}>{l.pf}</td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr>
          <td>Team</td>
          <td />
          <td className="n">{tot.pts}</td>
          <td className="n">{tot.reb}</td>
          <td className="n">{tot.ast}</td>
          <td className="n">
            {tot.fgm}-{tot.fga}
          </td>
          <td className="n">
            {tot.tpm}-{tot.tpa}
          </td>
          <td />
        </tr>
      </tfoot>
    </table>
  );
}

// ---------------- viewer ----------------
export function GameViewer({ L, box, onDone }: { L: League; box: BoxScore; onDone: () => void }) {
  const ev = box.pbp ?? [];
  const structured = hasStructuredPbp(ev);
  const [i, setI] = useState(() => Math.min(replayPosition(box.gid), Math.max(0, ev.length - 1)));
  const [speed, setSpeed] = useState<number>(() => {
    try {
      return Number(localStorage.getItem("hd-watch-speed")) || 2;
    } catch {
      return 2;
    }
  });
  const [paused, setPaused] = useState(false);
  const ht = team(L, box.home.tid);
  const at = team(L, box.away.tid);
  const [homeInk, awayInk] = teamInks(ht, at);
  // short names from the box score, so archived players still show up
  const names = useMemo(() => {
    const m = new Map<number, string>();
    for (const l of [...box.home.lines, ...box.away.lines]) {
      const parts = l.name.split(" ");
      m.set(l.pid, parts.length > 1 ? `${parts[0][0]}. ${parts.slice(1).join(" ")}` : l.name);
    }
    return m;
  }, [box]);
  const done = i >= ev.length - 1;
  const userSide: 0 | 1 = box.away.tid === L.userTid ? 1 : 0;
  const [boxSide, setBoxSide] = useState<0 | 1>(userSide);

  // advance the replay
  useEffect(() => {
    if (paused || done || !ev.length) return;
    const sp = SPEEDS.find((s) => s.k === speed) ?? SPEEDS[1];
    const j = nextShown(ev, i);
    const gap = Math.max(0, ev[j].t - ev[i].t);
    let delay = Math.max(sp.min, Math.min(gap * sp.perSec, 4200 / sp.k));
    if (ev[i].k === "info" && i > 0) delay += 1400 / sp.k;
    if (ev[j].k === "sub") delay = sp.min * 0.5;
    const t = setTimeout(() => setI(j), delay);
    return () => clearTimeout(t);
  }, [i, paused, speed, ev, done]);

  // the result is revealed once the replay ends (leaving for anything but a player's page also clears it; see Layout)
  useEffect(() => {
    setReplayPosition(box.gid, done ? null : i);
    if (done) setWatchGuard(null);
  }, [done, i, box.gid]);

  // space bar pauses
  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      if (e.code === "Space" && (e.target as HTMLElement)?.tagName !== "INPUT") {
        e.preventDefault();
        setPaused((p) => !p);
      }
    };
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, []);

  const state = useMemo(() => (structured ? liveState(ev, i) : null), [ev, i, structured]);
  const starters = useMemo<[number[], number[]]>(() => {
    const s: [number[], number[]] = [[], []];
    for (const e of ev) {
      if (e.k !== "lu") continue;
      if (!s[e.side].length) s[e.side] = e.lu ?? [];
      if (s[0].length && s[1].length) break;
    }
    return s;
  }, [ev]);

  if (!ev.length) return null;
  const e = ev[i];
  const half = ev.findIndex((x) => x.k === "info" && x.text.startsWith("End of 1st half"));
  const recent: { e: PbpEvent; idx: number }[] = [];
  for (let k = i; k >= 0 && recent.length < 40; k--) if (ev[k].k !== "lu" && ev[k].text) recent.push({ e: ev[k], idx: k });
  const bonus = (side: 0 | 1) => {
    const f = state?.fouls[side === 0 ? 1 : 0] ?? 0; // fouls committed by the other team put this side in the bonus
    return f >= 10 ? "Double bonus" : f >= 7 ? "Bonus" : null;
  };
  const sideLines = (side: 0 | 1) => (state ? [...state.lines.values()].filter((l) => l.side === side) : []);
  let shown = e;
  for (let k = i; k >= 0; k--) {
    if (ev[k].k !== "lu" && ev[k].k !== "sub" && ev[k].text) {
      shown = ev[k];
      break;
    }
  }
  const lastScore = (shown.k === "fg" || shown.k === "ft") && shown.m === 1;
  const sp = (k: number) => {
    setSpeed(k);
    try {
      localStorage.setItem("hd-watch-speed", String(k));
    } catch {
      // ignore
    }
  };

  return (
    <div className="col gap-16">
      <div className="scoreboard compact" style={{ ["--ca" as string]: heroColors(at.colors).h1, ["--ch" as string]: heroColors(ht.colors).h1 }}>
        <div className="sb-main">
          <div className="sb-team">
            <Logo team={at} size={58} />
            <div>
              <div className="sb-name">{at.name}</div>
              <div className="sb-sub">
                {at.mascot}
                {bonus(1) && <span className="bonus-chip">{bonus(1)}</span>}
              </div>
            </div>
          </div>
          <span className={cls("sb-score", done && e.as < e.hs && "lose")}>{e.as}</span>
          <div className="sb-mid">
            <span className="sb-clock">{done ? "FINAL" : clockOf(e)}</span>
            <span className="sb-per">{done ? (box.ot ? `${box.ot > 1 ? box.ot : ""}OT` : "") : periodLabel(e.per)}</span>
          </div>
          <span className={cls("sb-score", done && e.hs < e.as && "lose")}>{e.hs}</span>
          <div className="sb-team home">
            <Logo team={ht} size={58} />
            <div>
              <div className="sb-name">{ht.name}</div>
              <div className="sb-sub">
                {bonus(0) && <span className="bonus-chip">{bonus(0)}</span>}
                {ht.mascot}
              </div>
            </div>
          </div>
        </div>
        <div className="sb-progress">
          <span style={{ width: `${(100 * i) / Math.max(1, ev.length - 1)}%` }} />
        </div>
      </div>

      <div className="watch-bar">
        <button className="btn btn-primary" style={{ width: 104 }} onClick={() => setPaused(!paused)} disabled={done}>
          <Icon name={paused ? "play" : "pause"} size={13} /> {paused ? "Resume" : "Pause"}
        </button>
        <Seg options={SPEEDS.map((s) => ({ key: s.k as number, label: s.label }))} value={speed} onChange={sp} />
        {half > i && (
          <button className="btn" onClick={() => setI(half)}>
            Skip to halftime
          </button>
        )}
        <button className="btn" onClick={() => setI(ev.length - 1)} disabled={done}>
          Skip to end
        </button>
        <div className={cls("last-play", lastScore && "score")}>
          {shown.k !== "info" && <Logo team={shown.side === 0 ? ht : at} size={22} />}
          <span className="ellipsis">{shown.text}</span>
        </div>
        <button
          className="btn"
          onClick={() => {
            setReplayPosition(box.gid, null);
            setWatchGuard(null);
            onDone();
          }}
        >
          {done ? "Box score" : "Exit"}
        </button>
      </div>

      {structured && state ? (
        <div className="watch-grid">
          <div className="col gap-16">
            <div className="card">
              <div className="card-h">
                <h2>Shot chart</h2>
                <span className="sub">
                  {at.short} attacks left · {ht.short} attacks right
                </span>
                <span className="spacer" />
                <span className="shot-key">
                  <i className="mk made" /> Made <i className="mk miss">×</i> Missed
                </span>
              </div>
              <div className="card-b" style={{ padding: "10px 12px 12px" }}>
                <Court ev={ev} upto={i} homeInk={homeInk} awayInk={awayInk} />
                <div className="section-title" style={{ margin: "12px 0 6px" }}>
                  Game flow
                </div>
                <LeadTracker ev={ev} upto={i} ht={ht} at={at} homeInk={homeInk} awayInk={awayInk} onSeek={(k) => setI(k)} />
              </div>
            </div>
          </div>
          <div className="col gap-16">
            <div className="card">
              <div className="card-h">
                <h2>Live box score</h2>
                <span className="spacer" />
                <Seg
                  options={[
                    { key: 1 as 0 | 1, label: at.short },
                    { key: 0 as 0 | 1, label: ht.short },
                  ]}
                  value={boxSide}
                  onChange={setBoxSide}
                />
              </div>
              <LiveBox L={L} lines={sideLines(boxSide)} on={state.on[boxSide]} starters={starters[boxSide]} tid={boxSide === 0 ? ht.id : at.id} names={names} />
            </div>
            <PlayFeed ev={recent} ht={ht} at={at} />
          </div>
        </div>
      ) : (
        <div className="col gap-16">
          <div className="callout small">
            <Icon name="bolt" size={18} />
            <span>The shot chart and live box score are available for games played after this update. This one has the play-by-play.</span>
          </div>
          <PlayFeed ev={recent} ht={ht} at={at} />
        </div>
      )}
    </div>
  );
}

function PlayFeed({ ev, ht, at }: { ev: { e: PbpEvent; idx: number }[]; ht: Team; at: Team }) {
  return (
    <div className="card">
      <div className="card-h">
        <h2>Play-by-play</h2>
      </div>
      <div className="pbp" style={{ maxHeight: 360 }}>
        {ev.map(({ e, idx }, k) => {
          const scored = (e.k === "fg" || e.k === "ft") && e.m === 1;
          return (
            <div key={idx} className={cls("pbp-row", scored && "score", k === 0 && "now", e.k === "sub" && "sub")}>
              <span className="muted num">{clockOf(e)}</span>
              {e.k === "info" ? <span /> : <Logo team={e.side === 0 ? ht : at} size={20} />}
              <span>{e.text}</span>
              <span className="num right">
                {e.as}-{e.hs}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
