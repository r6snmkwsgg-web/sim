import { useState } from "react";
import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { roster, team } from "../../engine/core";
import { transferRisk } from "../../engine/offseason";
import { Card, Grade, PageHead, PlayerLink } from "../components/common";
import { RecruitTable } from "../components/RecruitTable";
import { RecruitingSummary } from "./Recruiting";
import { classLabel } from "../../engine/ratings";

export function Portal() {
  const L = useLeague();
  const [pos, setPos] = useState("all");
  const [status, setStatus] = useState("available");
  const ut = team(L, L.userTid);
  const portal = L.players.filter((p) => p.status === "portal" && p.recruit);
  if (L.phase !== "portal") {
    const risks = roster(L, ut.id)
      .map((p) => ({ p, r: transferRisk(L, p) }))
      .sort((a, b) => b.r - a.r);
    return (
      <div>
        <PageHead title="Transfer Portal" sub="The portal opens after the NBA Draft, once the season is over." />
        <Card title="Your players' transfer outlook" sub="Players who aren't getting minutes, stars at programs below their level, and players whose coach leaves are most likely to enter." flush>
          <table className="tbl">
            <thead>
              <tr>
                <th>Player</th>
                <th>Class</th>
                <th className="n">OVR</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              {risks.map(({ p, r }) => (
                <tr key={p.id}>
                  <td>
                    <PlayerLink L={L} p={p} face size={26} colors={ut.colors} />
                  </td>
                  <td>{classLabel(p)}</td>
                  <td className="n">
                    <Grade v={p.ovr} />
                  </td>
                  <td>{r >= 0.25 ? <span className="badge bad">High</span> : r >= 0.12 ? <span className="badge warn">Moderate</span> : <span className="badge good">Low</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    );
  }
  const mine = portal.filter((p) => p.recruit!.fromTid === L.userTid);
  const rows = portal.filter((p) => {
    const r = p.recruit!;
    if (pos !== "all" && p.pos !== pos) return false;
    if (status === "available" && (r.stage === "signed" || (r.stage === "committed" && r.committedTo !== L.userTid))) return false;
    return true;
  });
  return (
    <div>
      <PageHead title="Transfer Portal" sub={`${portal.length} players in the portal · window ${L.portalRound} of 4. Transfers are eligible immediately.`} right={<Link to={`/l/${L.id}/transfers`} className="btn">Transfer history</Link>} />
      <RecruitingSummary />
      {mine.length > 0 && (
        <Card title="Your players in the portal" sub="You keep a head start with players who left your program. Re-recruit them like anyone else." className="mb-16" flush>
          <RecruitTable L={L} rows={mine} kind="portal" showActions limit={20} />
        </Card>
      )}
      <Card flush>
        <div className="card-b row-wrap" style={{ borderBottom: "1px solid var(--border)" }}>
          <select className="select" value={pos} onChange={(e) => setPos(e.target.value)}>
            <option value="all">All positions</option>
            {["PG", "SG", "SF", "PF", "C"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
          <select className="select" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="available">Available</option>
            <option value="all">Everyone</option>
          </select>
          <span className="muted small">{rows.length} shown</span>
        </div>
        <RecruitTable L={L} rows={rows} kind="portal" showActions />
      </Card>
    </div>
  );
}
