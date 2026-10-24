import { Link } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { playerName, roster, team } from "../../engine/core";
import { classLabel, heightStr } from "../../engine/ratings";
import { commitsFor } from "../../engine/recruiting";
import { Card, Grade, PageHead, PlayerLink, Stars } from "../components/common";
import { releasePlayer } from "./Roster";

export function Signing() {
  const L = useLeague();
  const t = team(L, L.userTid);
  const cur = roster(L, t.id).slice().sort((a, b) => b.ovr - a.ovr);
  const incoming = commitsFor(L, t.id).filter((p) => p.recruit?.kind === "hs" && p.recruit.stage === "signed");
  const total = cur.length + incoming.length;
  const over = total - L.settings.rosterMax;
  const departed = L.news.filter((n) => n.user && n.season === L.season && (n.kind === "draft" || n.kind === "portal" || (n.kind === "team" && n.text.startsWith("Graduating"))));
  return (
    <div>
      <PageHead
        title="Signing Day"
        sub={`Next season's roster: ${total} of ${L.settings.rosterMax}`}
        right={<span className={`badge ${over > 0 ? "bad" : "good"}`} style={{ height: 26, fontSize: 12.5 }}>{over > 0 ? `${over} over the limit` : `${-over} open spot(s)`}</span>}
      />
      {L.phase !== "signing" && (
        <div className="card card-b mb-16 small">This page shows next season's roster. Signing Day happens after the transfer portal closes.</div>
      )}
      {over > 0 && (
        <div className="card card-b mb-16" style={{ borderColor: "var(--bad)" }}>
          <b className="bad">Roster limit:</b> release {over} player(s) below, or the lowest-rated players will be released automatically when the new season starts.
        </div>
      )}
      <div className="grid g-main">
        <Card title="Returning players" flush>
          <table className="tbl">
            <thead>
              <tr>
                <th>Player</th>
                <th>Pos</th>
                <th>Class next year</th>
                <th className="n">OVR</th>
                <th className="n">POT</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {cur.map((p) => (
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
                  <td>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => {
                        if (confirm(`Release ${playerName(p)}?`)) mutate((LL) => releasePlayer(LL, p));
                      }}
                    >
                      Release
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
        <div className="col gap-16">
          <Card title={`Incoming freshmen (${incoming.length})`} flush>
            {incoming.length ? (
              <table className="tbl compact">
                <tbody>
                  {incoming.map((p) => (
                    <tr key={p.id}>
                      <td>
                        <PlayerLink L={L} p={p} />
                      </td>
                      <td>
                        <Stars n={p.recruit!.stars} />
                      </td>
                      <td>
                        {p.pos} <span className="muted small">{heightStr(p.hgt)}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty">
                No signees. <Link to={`/l/${L.id}/recruiting`}>Recruiting board</Link>
              </div>
            )}
          </Card>
          <Card title="Offseason moves">
            {departed.length ? (
              <div className="col gap-4 small">
                {departed.map((n) => (
                  <div key={n.id}>• {n.text}</div>
                ))}
              </div>
            ) : (
              <div className="muted small">No departures recorded.</div>
            )}
          </Card>
          <Card title="Walk-ons">
            <p className="small muted" style={{ margin: 0 }}>
              If the roster has fewer than 13 players when the season starts, walk-ons fill the open spots automatically.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
