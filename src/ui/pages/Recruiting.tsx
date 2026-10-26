import { useMemo, useState } from "react";
import { useLeague } from "../store";
import { shortDayLabel, team } from "../../engine/core";
import { regionOf } from "../../engine/data/cities";
import { actionMult, classRankings, classUnrated, commitsFor, OFFICIAL_VISITS, openSpots, RATINGS_DAY } from "../../engine/recruiting";
import { Card, Meter, PageHead, Seg, Tabs, Tile } from "../components/common";
import { Icon } from "../components/Icons";
import { RecruitTable, type BoardView } from "../components/RecruitTable";
import type { Player } from "../../engine/types";

export function RecruitingSummary() {
  const L = useLeague();
  const ut = team(L, L.userTid);
  const offers = L.players.filter((p) => p.recruit && p.recruit.offers.includes(L.userTid) && p.recruit.stage !== "signed" && p.recruit.committedTo !== L.userTid).length;
  const commits = commitsFor(L, ut.id).filter((p) => p.recruit?.kind === "hs");
  const cr = classRankings(L).find((x) => x.tid === ut.id);
  const pct = (100 * L.recruitPts) / Math.max(1, L.recruitPtsMax);
  return (
    <>
      {L.settings.autoRecruit && (
        <div className="callout mb-16 small">
          <Icon name="bolt" size={18} />
          <span>
            <b>Auto recruiting is on.</b> Your staff spends your points each week. Turn it off in Settings to recruit yourself.
          </span>
        </div>
      )}
      {L.phase === "preseason" && !L.settings.autoRecruit && (
        <div className="callout mb-16 small">
          <Icon name="recruit" size={18} />
          <span>
            <b>Fall recruiting week.</b> The class spent the summer on the circuit, and programs have already been calling and offering. Your staff made some contacts (see My Targets); offers and official visits are up to you. The other programs make their fall moves when the season tips off.
          </span>
        </div>
      )}
      <div className="tiles g5 mb-16" style={{ display: "grid" }}>
        <Tile label="Coaching points" icon="bolt" value={<>{L.recruitPts}<small>/ {L.recruitPtsMax}</small></>}>
          <div style={{ marginTop: 7 }}>
            <Meter value={pct} color="var(--accent-ink)" />
          </div>
          <div className="foot">Reset Mondays · also buy game prep</div>
        </Tile>
        <Tile label="Open spots" icon="roster" value={openSpots(L, ut.id)} foot="Next season, after departures" />
        <Tile
          label="Your class"
          icon="star"
          value={<>{cr && cr.n > 0 && !classUnrated(L) ? `#${cr.rank}` : "-"}<small>{commits.length} commit{commits.length === 1 ? "" : "s"}</small></>}
          foot={classUnrated(L) ? `Rankings come out ${shortDayLabel(L.season, RATINGS_DAY)}` : commits.length ? commits.map((p) => (p.recruit!.kind === "hs" ? `${p.recruit!.stars}★` : "T")).join(" ") : "No commitments yet"}
        />
        <Tile label="Offers out" icon="check" value={offers} foot="Uncommitted players you've offered" />
        <Tile label="Official visits" icon="plane" value={<>{OFFICIAL_VISITS - ut.officialVisitsUsed}<small>left</small></>} foot={`Recruiting week ${L.week}`} />
      </div>
    </>
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
  // start with recruits who'd actually consider you
  const [realistic, setRealistic] = useState(true);
  const [view, setView] = useState<BoardView>("overview");
  const ut = team(L, L.userTid);
  const all = useMemo(() => L.players.filter((p) => p.recruit?.kind === "hs" && p.status === "recruit"), [L.players, L.players.length]);
  const regions = useMemo(() => [...new Set(all.map((p) => regionOf(p.state)))].sort(), [all]);
  const rows = all.filter((p: Player) => {
    const r = p.recruit!;
    if (pos !== "all" && p.pos !== pos) return false;
    if (stars && !classUnrated(L) && r.stars < stars) return false;
    if (region !== "all" && regionOf(p.state) !== region) return false;
    if (status === "available" && (r.stage === "signed" || r.stage === "unsigned" || (r.stage === "committed" && r.committedTo !== L.userTid))) return false;
    if (status === "committed" && r.stage !== "committed" && r.stage !== "signed") return false;
    if (boardOnly && !L.board.includes(p.id)) return false;
    if (realistic && actionMult(L, ut, p) < 0.45 && !L.board.includes(p.id) && r.committedTo !== L.userTid) return false;
    if (q && !`${p.first} ${p.last} ${p.city} ${p.state}`.toLowerCase().includes(q.toLowerCase())) return false;
    return true;
  });
  const cls = all[0]?.recruit?.classSeason;
  return (
    <div>
      <PageHead eyebrow="Recruiting" title="Recruiting Board" sub={cls ? `Class of ${cls} · ${all.length} prospects` : "No recruiting class right now"} />
      <RecruitingSummary />
      <Card flush>
        <div className="board-views">
          <Tabs
            small
            tabs={[
              { key: "overview", label: "Overview" },
              { key: "stats", label: "HS Stats" },
              { key: "summer", label: "Summer" },
              { key: "near", label: "Near You" },
            ]}
            value={view}
            onChange={setView}
          />
          {view === "summer" && <span className="faint small">Last summer's circuit (17U). The national circuit is the best competition, so numbers there are lower but more honest.</span>}
          {view === "near" && <span className="faint small">Closest to {ut.name} first. Recruits who want to stay close to home lean toward nearby schools.</span>}
        </div>
        <div className="filter-bar">
          <div className="search-box">
            <Icon name="search" size={14} />
            <input className="input" placeholder="Search name or hometown" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
          <Seg options={[{ key: "all", label: "All" }, ...["PG", "SG", "SF", "PF", "C"].map((x) => ({ key: x, label: x }))]} value={pos} onChange={setPos} />
          {!classUnrated(L) && <Seg options={[{ key: 0, label: "Any ★" }, { key: 5, label: "5★" }, { key: 4, label: "4★+" }, { key: 3, label: "3★+" }]} value={stars} onChange={setStars} />}
          <select className="select" value={region} onChange={(e) => setRegion(e.target.value)}>
            <option value="all">All regions</option>
            {regions.map((r) => (
              <option key={r}>{r}</option>
            ))}
          </select>
          <Seg
            options={[
              { key: "available", label: "Available" },
              { key: "committed", label: "Committed" },
              { key: "all", label: "Everyone" },
            ]}
            value={status}
            onChange={setStatus}
          />
          <button className={`chip${boardOnly ? " on" : ""}`} onClick={() => setBoardOnly(!boardOnly)}>
            <Icon name="star" size={12} /> My board
          </button>
          <button className={`chip${realistic ? " on" : ""}`} onClick={() => setRealistic(!realistic)} title="Hide recruits who'd barely notice your program">
            <Icon name="check" size={12} /> Realistic for us
          </button>
          <span className="spacer" />
          <span className="faint small">{rows.length} shown · ? = not scouted yet</span>
        </div>
        <RecruitTable L={L} rows={rows} kind="hs" showActions view={view} />
      </Card>
    </div>
  );
}
