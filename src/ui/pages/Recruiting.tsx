import { useMemo, useState } from "react";
import { useLeague } from "../store";
import { team } from "../../engine/core";
import { regionOf } from "../../engine/data/cities";
import { OFFICIAL_VISITS, openSpots } from "../../engine/recruiting";
import { Card, PageHead } from "../components/common";
import { RecruitTable } from "../components/RecruitTable";
import type { Player } from "../../engine/types";

export function RecruitingSummary() {
  const L = useLeague();
  const ut = team(L, L.userTid);
  const offers = L.players.filter((p) => p.recruit && p.recruit.offers.includes(L.userTid) && p.recruit.stage !== "signed" && p.recruit.committedTo !== L.userTid).length;
  return (
    <div className="card mb-16">
      {L.settings.autoRecruit && (
        <div className="card-b small" style={{ borderBottom: "1px solid var(--border)", background: "var(--accent-soft)" }}>
          <b>Auto recruiting is on:</b> your staff spends your points each week. Turn it off in Settings to recruit yourself.
        </div>
      )}
      <div className="stat-row">
        <div className="stat">
          <div className="label">Points this week</div>
          <div className="value">
            {L.recruitPts}
            <small>/ {L.recruitPtsMax}</small>
          </div>
        </div>
        <div className="stat">
          <div className="label">Open spots next season</div>
          <div className="value">{openSpots(L, ut.id)}</div>
        </div>
        <div className="stat">
          <div className="label">Outstanding offers</div>
          <div className="value">{offers}</div>
        </div>
        <div className="stat">
          <div className="label">Official visits left</div>
          <div className="value">{OFFICIAL_VISITS - ut.officialVisitsUsed}</div>
        </div>
        <div className="stat">
          <div className="label">Recruiting week</div>
          <div className="value">{L.week}</div>
        </div>
      </div>
    </div>
  );
}

export function RecruitingBoard() {
  const L = useLeague();
  const [pos, setPos] = useState("all");
  const [stars, setStars] = useState(0);
  const [region, setRegion] = useState("all");
  const [status, setStatus] = useState("available");
  const [q, setQ] = useState("");
  const [boardOnly, setBoardOnly] = useState(false);
  const all = useMemo(() => L.players.filter((p) => p.recruit?.kind === "hs" && p.status === "recruit"), [L.players, L.players.length]);
  const regions = useMemo(() => [...new Set(all.map((p) => regionOf(p.state)))].sort(), [all]);
  const rows = all.filter((p: Player) => {
    const r = p.recruit!;
    if (pos !== "all" && p.pos !== pos) return false;
    if (stars && r.stars < stars) return false;
    if (region !== "all" && regionOf(p.state) !== region) return false;
    if (status === "available" && (r.stage === "signed" || r.stage === "unsigned" || (r.stage === "committed" && r.committedTo !== L.userTid))) return false;
    if (status === "committed" && r.stage !== "committed" && r.stage !== "signed") return false;
    if (boardOnly && !L.board.includes(p.id)) return false;
    if (q && !`${p.first} ${p.last} ${p.city} ${p.state}`.toLowerCase().includes(q.toLowerCase())) return false;
    return true;
  });
  const cls = all[0]?.recruit?.classSeason;
  return (
    <div>
      <PageHead title="Recruiting Board" sub={cls ? `Class of ${cls} · ${all.length} prospects` : "No recruiting class right now"} />
      <RecruitingSummary />
      <Card flush>
        <div className="card-b row-wrap" style={{ borderBottom: "1px solid var(--border)" }}>
          <input className="input" placeholder="Search name or hometown…" value={q} onChange={(e) => setQ(e.target.value)} style={{ width: 220 }} />
          <select className="select" value={pos} onChange={(e) => setPos(e.target.value)}>
            <option value="all">All positions</option>
            {["PG", "SG", "SF", "PF", "C"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
          <select className="select" value={stars} onChange={(e) => setStars(Number(e.target.value))}>
            <option value={0}>Any stars</option>
            {[5, 4, 3, 2].map((s) => (
              <option key={s} value={s}>
                {s}★{s < 5 ? "+" : ""}
              </option>
            ))}
          </select>
          <select className="select" value={region} onChange={(e) => setRegion(e.target.value)}>
            <option value="all">All regions</option>
            {regions.map((r) => (
              <option key={r}>{r}</option>
            ))}
          </select>
          <select className="select" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="available">Available</option>
            <option value="committed">Committed / signed</option>
            <option value="all">Everyone</option>
          </select>
          <label className="check">
            <input type="checkbox" checked={boardOnly} onChange={(e) => setBoardOnly(e.target.checked)} /> My board only
          </label>
          <span className="spacer" />
          <span className="muted small">{rows.length} shown · OVR*/POT* are your scouting estimates</span>
        </div>
        <RecruitTable L={L} rows={rows} kind="hs" showActions />
      </Card>
    </div>
  );
}
