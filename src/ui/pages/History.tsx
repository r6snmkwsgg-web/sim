import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { seasonLabel, team } from "../../engine/core";
import { Card, Empty, Logo, PageHead, TeamLink } from "../components/common";

export function LeagueHistory() {
  const L = useLeague();
  const hist = L.history.slice().reverse();
  const titles = new Map<number, number>();
  const ffs = new Map<number, number>();
  for (const h of L.history) {
    if (h.champion !== null) titles.set(h.champion, (titles.get(h.champion) ?? 0) + 1);
    for (const t of h.finalFour) ffs.set(t, (ffs.get(t) ?? 0) + 1);
  }
  const champs = [...titles.entries()].sort((a, b) => b[1] - a[1] || (ffs.get(b[0]) ?? 0) - (ffs.get(a[0]) ?? 0));
  const ach = L.achievements.slice().reverse();
  return (
    <div>
      <PageHead title="League History" sub={`${L.history.length} completed season${L.history.length === 1 ? "" : "s"} since ${seasonLabel(L.startSeason)}`} />
      {!hist.length ? (
        <Card>
          <Empty>History is written at the end of each season. Every champion, award and record will be kept here.</Empty>
        </Card>
      ) : (
        <div className="col gap-16">
          <Card title="Champions" flush>
            <div className="tbl-wrap">
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Season</th>
                    <th>National Champion</th>
                    <th>Runner-up</th>
                    <th>Final Four</th>
                    <th>Player of the Year</th>
                    <th>NIT</th>
                    <th>Your result</th>
                  </tr>
                </thead>
                <tbody>
                  {hist.map((h) => (
                    <tr key={h.season}>
                      <td>
                        <Link to={`/l/${L.id}/tournaments?season=${h.season}`}>{seasonLabel(h.season)}</Link>
                      </td>
                      <td>
                        <span className="row" style={{ gap: 6 }}>
                          <span className="trophy">🏆</span>
                          <TeamLink L={L} tid={h.champion} size={20} season={h.season} />
                        </span>
                      </td>
                      <td>
                        <TeamLink L={L} tid={h.runnerUp} size={18} short season={h.season} />
                      </td>
                      <td>
                        <span className="row" style={{ gap: 4 }}>
                          {h.finalFour.map((t) => (
                            <Link key={t} to={`/l/${L.id}/team/${t}?season=${h.season}`} title={team(L, t).name}>
                              <Logo team={team(L, t)} size={20} />
                            </Link>
                          ))}
                        </span>
                      </td>
                      <td>
                        {h.poy ? (
                          <>
                            <Link to={`/l/${L.id}/player/${h.poy.pid}`}>{h.poy.playerName}</Link> <span className="faint small">{team(L, h.poy.tid).short}</span>
                          </>
                        ) : (
                          "-"
                        )}
                      </td>
                      <td>
                        <TeamLink L={L} tid={h.nitChamp} size={16} short />
                      </td>
                      <td className="small">
                        <span className="muted">{team(L, h.userTid).short}:</span> {h.userResult}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
          <div className="grid g2">
            <Card title="Most titles" flush>
              <table className="tbl compact">
                <tbody>
                  {champs.map(([tid, n]) => (
                    <tr key={tid} className={tid === L.userTid ? "hl" : ""}>
                      <td>
                        <TeamLink L={L} tid={tid} size={20} />
                      </td>
                      <td className="n bold">{n} 🏆</td>
                      <td className="n muted">{ffs.get(tid) ?? 0} FF</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
            <Card title="Your achievements">
              {ach.length ? (
                <div className="col gap-4">
                  {ach.map((a, i) => (
                    <div key={i} className="row">
                      <span className="trophy">★</span>
                      <span style={{ flex: 1 }}>{a.name}</span>
                      <span className="muted small">{seasonLabel(a.season)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="muted">Make a Final Four, win a title, or reach Blue Blood status.</div>
              )}
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
