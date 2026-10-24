import { mutate, useLeague } from "../store";
import { roster, team, coach } from "../../engine/core";
import { classLabel, grade } from "../../engine/ratings";
import { FOCUS_LABELS, FOCUS_KEYS } from "../../engine/development";
import type { PracticeFocus, PracticeIntensity } from "../../engine/types";
import { Card, Grade, PageHead, PlayerLink } from "../components/common";
import { RATING_LABELS } from "../../engine/ratings";
import { signed } from "../util";

const INTENSITY: { k: PracticeIntensity; label: string; desc: string }[] = [
  { k: 1, label: "Light", desc: "75% development speed. No added injury risk." },
  { k: 2, label: "Normal", desc: "Standard development." },
  { k: 3, label: "Intense", desc: "130% development speed, with a small weekly injury risk." },
];

export function Practice() {
  const L = useLeague();
  const t = team(L, L.userTid);
  const ps = roster(L, t.id).slice().sort((a, b) => b.ovr - a.ovr);
  const ch = coach(L, L.userCid)!;
  return (
    <div>
      <PageHead title="Practice" sub="Players develop every week of the season and make bigger jumps each offseason." />
      <div className="grid g-main">
        <Card title="Team Practice Plan">
          <div className="bold mb-8">Focus</div>
          <div className="grid g4" style={{ gap: 8 }}>
            {(Object.keys(FOCUS_LABELS) as PracticeFocus[]).map((k) => (
              <button
                key={k}
                className={`card card-b ${t.practice.focus === k ? "hl" : ""}`}
                style={{ textAlign: "left", cursor: "pointer", borderColor: t.practice.focus === k ? "var(--accent)" : undefined, boxShadow: t.practice.focus === k ? "0 0 0 2px var(--accent)" : undefined, background: "var(--panel)" }}
                onClick={() => mutate(() => void (t.practice.focus = k))}
              >
                <div className="bold">{FOCUS_LABELS[k]}</div>
                <div className="tiny muted">{FOCUS_KEYS[k].length ? FOCUS_KEYS[k].map((r) => RATING_LABELS[r]).join(", ") : "Even development"}</div>
              </button>
            ))}
          </div>
          <div className="bold mt-16 mb-8">Intensity</div>
          <div className="btn-group">
            {INTENSITY.map((o) => (
              <button key={o.k} className={`btn ${t.practice.intensity === o.k ? "on" : ""}`} onClick={() => mutate(() => void (t.practice.intensity = o.k))}>
                {o.label}
              </button>
            ))}
          </div>
          <div className="small muted mt-8">{INTENSITY.find((o) => o.k === t.practice.intensity)?.desc}</div>
        </Card>
        <Card title="Your Staff">
          <dl className="kv">
            <dt>Player development</dt>
            <dd>
              {Math.round(ch.development)} ({grade(ch.development)})
            </dd>
            <dt>Recruiting</dt>
            <dd>
              {Math.round(ch.recruiting)} ({grade(ch.recruiting)})
            </dd>
            <dt>Game tactics</dt>
            <dd>
              {Math.round(ch.tactics)} ({grade(ch.tactics)})
            </dd>
          </dl>
          <p className="small muted mt-12">Development speed also depends on each player's potential, work ethic and minutes played. Growth slows as a player nears his ceiling.</p>
        </Card>
      </div>
      <Card title="Individual Development" sub="Change since the start of this season" className="mt-16" flush>
        <table className="tbl">
          <thead>
            <tr>
              <th>Player</th>
              <th>Pos</th>
              <th>Class</th>
              <th className="n">OVR</th>
              <th className="n">POT</th>
              <th className="n">Change</th>
              <th>Work ethic</th>
              <th style={{ width: 200 }}>Individual focus</th>
            </tr>
          </thead>
          <tbody>
            {ps.map((p) => {
              const start = p.hist.find((h) => h.season === L.season);
              const d = start ? p.ovr - start.ovr : 0;
              return (
                <tr key={p.id}>
                  <td>
                    <PlayerLink L={L} p={p} face size={26} colors={t.colors} />
                  </td>
                  <td>{p.pos}</td>
                  <td>{classLabel(p)}</td>
                  <td className="n">
                    <Grade v={p.ovr} />
                  </td>
                  <td className="n">
                    <Grade v={p.pot + p.potErr} />
                  </td>
                  <td className={`n bold ${d > 0 ? "good" : d < 0 ? "bad" : "muted"}`}>{start ? signed(d, 0) : "-"}</td>
                  <td className="muted">{p.workEthic >= 75 ? "Gym rat" : p.workEthic >= 55 ? "Hard worker" : p.workEthic >= 35 ? "Average" : "Low"}</td>
                  <td>
                    <select
                      className="select"
                      style={{ height: 28, width: "100%" }}
                      value={t.practice.individual[p.id] ?? "balanced"}
                      onChange={(e) =>
                        mutate(() => {
                          const v = e.target.value as PracticeFocus;
                          if (v === "balanced") delete t.practice.individual[p.id];
                          else t.practice.individual[p.id] = v;
                        })
                      }
                    >
                      {(Object.keys(FOCUS_LABELS) as PracticeFocus[]).map((k) => (
                        <option key={k} value={k}>
                          {k === "balanced" ? "Same as team" : FOCUS_LABELS[k]}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
