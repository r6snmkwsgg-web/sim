import { useState } from "react";
import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { team } from "../../engine/core";
import { CLASS_LABELS } from "../../engine/ratings";
import { Card, Empty, Grade, PageHead, TeamLink } from "../components/common";

export function DraftPage() {
  const L = useLeague();
  const years = [...new Set(L.draftHistory.map((d) => d.season))].sort((a, b) => b - a);
  const [year, setYear] = useState<number>(years[0] ?? L.season + 1);
  const picks = L.draftHistory.filter((d) => d.season === year).sort((a, b) => a.pick - b.pick);
  const byTeam = new Map<number, number>();
  for (const d of L.draftHistory) byTeam.set(d.tid, (byTeam.get(d.tid) ?? 0) + 1);
  const top = [...byTeam.entries()].sort((a, b) => b[1] - a[1]).slice(0, 15);
  const mine = L.draftHistory.filter((d) => d.tid === L.userTid);
  return (
    <div>
      <PageHead
        title="NBA Draft"
        sub="College players selected in each NBA Draft. Seniors are eligible; underclassmen declare when projected to go high."
        right={
          years.length ? (
            <select className="select" value={year} onChange={(e) => setYear(Number(e.target.value))}>
              {years.map((y) => (
                <option key={y} value={y}>
                  {y} NBA Draft
                </option>
              ))}
            </select>
          ) : null
        }
      />
      {!picks.length ? (
        <Card>
          <Empty>The first draft happens after the season ends.</Empty>
        </Card>
      ) : (
        <div className="grid g-main">
          <Card title={`${year} NBA Draft`} flush>
            <table className="tbl">
              <thead>
                <tr>
                  <th className="n">Pick</th>
                  <th>NBA Team</th>
                  <th>Player</th>
                  <th>College</th>
                  <th>Pos</th>
                  <th>Class</th>
                  <th className="n">OVR</th>
                </tr>
              </thead>
              <tbody>
                {picks.map((d, i) => (
                  <tr key={d.pid} className={d.tid === L.userTid ? "hl" : i === 29 ? "sep" : ""}>
                    <td className="n bold">{d.pick}</td>
                    <td className="muted">{d.nbaTeam}</td>
                    <td>
                      <Link to={`/l/${L.id}/player/${d.pid}`}>{d.name}</Link>
                    </td>
                    <td>
                      <TeamLink L={L} tid={d.tid} size={18} short />
                    </td>
                    <td>{d.pos}</td>
                    <td className="muted">{CLASS_LABELS[Math.min(5, d.year)]}</td>
                    <td className="n">
                      <Grade v={d.ovr} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
          <div className="col gap-16">
            <Card title="Your draftees" flush>
              {mine.length ? (
                <table className="tbl compact">
                  <tbody>
                    {mine
                      .slice()
                      .reverse()
                      .map((d) => (
                        <tr key={d.pid}>
                          <td className="muted">{d.season}</td>
                          <td>
                            <Link to={`/l/${L.id}/player/${d.pid}`}>{d.name}</Link>
                          </td>
                          <td className="n">#{d.pick}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              ) : (
                <div className="empty">No players drafted from {team(L, L.userTid).name} yet.</div>
              )}
            </Card>
            <Card title="Most draft picks (all time)" flush>
              <table className="tbl compact">
                <tbody>
                  {top.map(([tid, n]) => (
                    <tr key={tid}>
                      <td>
                        <TeamLink L={L} tid={tid} size={18} />
                      </td>
                      <td className="n bold">{n}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
