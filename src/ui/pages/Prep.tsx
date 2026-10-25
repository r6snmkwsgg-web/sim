import { useState } from "react";
import { Link } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { roster, seasonLabel, shortDayLabel, team } from "../../engine/core";
import { classLabel } from "../../engine/ratings";
import { currentRank } from "../../engine/rankings";
import { curSeason } from "../../engine/play";
import { PREP_LEVELS, currentPrep, nextOpponent, projectedLine, setPrep } from "../../engine/prep";
import type { League, Team } from "../../engine/types";
import { Card, Empty, Grade, heroStyle, Logo, PageHead, PlayerLink } from "../components/common";
import { Icon } from "../components/Icons";
import { gameView, nextGame, seasonStatsOf } from "../helpers";

const TEMPO = ["", "Grind", "Slow", "Normal", "Fast", "Run & Gun"];
const OFF = { inside: "Inside", balanced: "Balanced", perimeter: "Perimeter" } as const;
const DEF = { man: "Man-to-Man", zone: "2-3 Zone", press: "Full-Court Press" } as const;
const REB = { crash: "Crash the glass", balanced: "Balanced", getback: "Get back" } as const;

function lineText(L: League, opp: Team, v: number): string {
  // lines move in half points
  const h = Math.round(Math.abs(v) * 2) / 2;
  if (h === 0) return "Pick'em";
  const fav = v > 0 ? team(L, L.userTid).short : opp.short;
  return `${fav} by ${h % 1 ? h.toFixed(1) : h.toFixed(0)}`;
}

/** Players to watch: their best by scoring this season, or by rating before games are played. */
function toWatch(L: League, t: Team) {
  return roster(L, t.id)
    .map((p) => ({ p, s: seasonStatsOf(p, L.season, t.id) }))
    .sort((a, b) => (b.s && b.s.g ? b.s.pts / b.s.g : 0) - (a.s && a.s.g ? a.s.pts / a.s.g : 0) || b.p.ovr - a.p.ovr)
    .slice(0, 5);
}

function keys(L: League, opp: Team): string[] {
  const out: string[] = [];
  const st = opp.strategy;
  const watch = toWatch(L, opp)[0];
  if (st.defense === "press") out.push("They press full court. Take care of the ball: your guards' handles matter.");
  if (st.defense === "zone") out.push("They sit in a 2-3 zone. Your shooters should find open looks from three.");
  if (st.tempo >= 4) out.push(`They want to run (${TEMPO[st.tempo]}). Get back in transition.`);
  if (st.tempo <= 2) out.push(`They slow it down (${TEMPO[st.tempo]}). Every possession counts.`);
  if (st.offense === "perimeter") out.push("They live behind the arc. Run their shooters off the line.");
  if (st.offense === "inside") out.push("They pound it inside. Protect the paint and stay out of foul trouble.");
  if (st.rebounding === "crash") out.push("They crash the offensive glass. Box out.");
  if (watch?.s && watch.s.g > 0) out.push(`Slow down ${watch.p.first} ${watch.p.last}: ${(watch.s.pts / watch.s.g).toFixed(1)} points a game.`);
  if (out.length === 0) out.push("A balanced team without an obvious weakness. Execution wins this one.");
  return out;
}

export function Prep() {
  const L = useLeague();
  const [msg, setMsg] = useState<string | null>(null);
  const oppId = nextOpponent(L);
  if (oppId === null)
    return (
      <div>
        <PageHead title="Game Prep" sub="Scout your next opponent with this week's coaching points." />
        <Empty>No game coming up. Game prep opens when you have an opponent.</Empty>
      </div>
    );
  const opp = team(L, oppId);
  const os = curSeason(opp);
  const or = currentRank(L, opp.id);
  const g = nextGame(L, L.userTid);
  const v = g && (g.home === opp.id || g.away === opp.id) ? gameView(g, L.userTid) : null;
  const home = v ? (v.loc === "N" ? null : v.home) : null;
  const level = currentPrep(L);
  const base = projectedLine(L, opp.id, home, 0);
  const withPrep = projectedLine(L, opp.id, home, level);
  const paid = L.prep && L.prep.opp === opp.id ? L.prep.paid : 0;
  const coach = L.coaches.find((c) => c.id === opp.coachId);
  const players = toWatch(L, opp);
  const where = v ? (v.loc === "N" ? "Neutral site" : v.home ? "Home" : "Away") : "Tournament";
  return (
    <div className="col gap-16">
      <PageHead title="Game Prep" sub="Spend coaching points scouting your next opponent. Your team plays it smarter: better shots on offense, and a defense that knows their sets." />
      <div className="hero-banner" style={heroStyle(opp.colors)}>
        <div className="hero-inner">
          <Logo team={opp} size={86} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="hero-kicker">
              Next game{g && v ? ` · ${shortDayLabel(L.season, g.day)}` : ""} · {where}
              {g?.event ? ` · ${g.event}` : ""}
            </div>
            <div className="hero-title" style={{ marginTop: 6, fontSize: 38 }}>
              <span style={{ opacity: 0.7 }}>{v?.loc === "A" ? "at " : "vs "}</span>
              {or ? <span style={{ opacity: 0.8 }}>#{or} </span> : null}
              {opp.name}
            </div>
            <div className="hero-sub">
              {os.w}-{os.l} ({os.cw}-{os.cl} {L.conferences[opp.cid].short}) · {seasonLabel(L.season)}
            </div>
          </div>
          <div className="prep-line">
            <div className="hero-kicker">The line</div>
            <div className="prep-line-v">{lineText(L, opp, base)}</div>
            {level > 0 && <div className="prep-line-s">With your prep: {lineText(L, opp, withPrep)}</div>}
          </div>
        </div>
      </div>

      <Card
        title="Your prep"
        sub={
          L.settings.autoRecruit
            ? "Auto recruiting is on, so your staff spends your coaching points. Turn it off in Settings to use them here."
            : `${L.recruitPts} of ${L.recruitPtsMax} coaching points left this week. Recruiting uses the same points, and they reset every Monday.`
        }
      >
        <div className="prep-grid">
          {PREP_LEVELS.map((lv) => {
            const on = lv.level === level;
            const extra = lv.cost - paid;
            const short = extra > L.recruitPts;
            return (
              <button
                key={lv.level}
                className={`prep-opt${on ? " on" : ""}`}
                disabled={on || short}
                onClick={() => {
                  let res: { ok: boolean; msg?: string } = { ok: false };
                  mutate((LL) => {
                    res = setPrep(LL, lv.level);
                  });
                  setMsg(res.ok ? null : res.msg ?? null);
                }}
              >
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <b>{lv.name}</b>
                  {on ? <Icon name="check" size={16} /> : <span className="prep-cost">{lv.cost ? `${lv.cost} pts` : "Free"}</span>}
                </div>
                <div className="prep-edge">{lv.edge ? `About +${lv.edge} point${lv.edge > 1 ? "s" : ""}` : "No edge"}</div>
                <div className="small muted">{lv.desc}</div>
                {!on && short && <div className="small" style={{ color: "var(--bad)" }}>Needs {extra} points</div>}
              </button>
            );
          })}
        </div>
        {msg && <div className="small" style={{ color: "var(--bad)", marginTop: 10 }}>{msg}</div>}
        <div className="small muted" style={{ marginTop: 10 }}>
          Prep counts for this game only. Points spent this week come back if you lower it.
        </div>
      </Card>

      <div className="grid g-main">
        <Card title="Players to watch" flush right={<Link to={`/l/${L.id}/team/${opp.id}`} className="btn btn-sm">Team page</Link>}>
          <table className="tbl">
            <thead>
              <tr>
                <th>Player</th>
                <th>Class</th>
                <th className="c">OVR</th>
                <th className="n">PTS</th>
                <th className="n">REB</th>
                <th className="n">AST</th>
                <th className="n">3P%</th>
              </tr>
            </thead>
            <tbody>
              {players.map(({ p, s }) => (
                <tr key={p.id}>
                  <td>
                    <PlayerLink L={L} p={p} face colors={opp.colors} meta={p.pos} />
                  </td>
                  <td>{classLabel(p)}</td>
                  <td className="c">
                    <Grade v={p.ovr} />
                  </td>
                  <td className="n">
                    <b>{s && s.g ? (s.pts / s.g).toFixed(1) : "-"}</b>
                  </td>
                  <td className="n">{s && s.g ? ((s.orb + s.drb) / s.g).toFixed(1) : "-"}</td>
                  <td className="n">{s && s.g ? (s.ast / s.g).toFixed(1) : "-"}</td>
                  <td className="n">{s && s.tpa ? ((100 * s.tpm) / s.tpa).toFixed(1) : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
        <Card title="Scouting report">
          <div className="col gap-12">
            <div className="prep-style">
              <div>
                <span>Tempo</span>
                <b>{TEMPO[opp.strategy.tempo]}</b>
              </div>
              <div>
                <span>Offense</span>
                <b>{OFF[opp.strategy.offense]}</b>
              </div>
              <div>
                <span>Defense</span>
                <b>{DEF[opp.strategy.defense]}</b>
              </div>
              <div>
                <span>Boards</span>
                <b>{REB[opp.strategy.rebounding]}</b>
              </div>
            </div>
            {coach && (
              <div className="row small" style={{ gap: 8 }}>
                <Icon name="coach" size={14} /> Coach {coach.first} {coach.last} · game planning <Grade v={coach.tactics} />
              </div>
            )}
            <div>
              <div className="section-title" style={{ marginBottom: 6 }}>
                Keys to the game
              </div>
              <ul className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.7 }}>
                {keys(L, opp).map((k) => (
                  <li key={k}>{k}</li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
