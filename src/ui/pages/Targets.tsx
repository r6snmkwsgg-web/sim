import { Link } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { team } from "../../engine/core";
import { heightStr } from "../../engine/ratings";
import { commitsFor } from "../../engine/recruiting";
import type { League, Player } from "../../engine/types";
import { Card, Empty, Grade, PageHead, PlayerLink, Stars } from "../components/common";
import { KnownOvr, KnownPot, QuickActions, StageCell } from "../components/RecruitTable";
import { HeatMeter } from "./RecruitProfile";
import { RecruitingSummary } from "./Recruiting";
import { money } from "../util";

function TargetRow({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const rival = Object.entries(r.interest)
    .filter(([k]) => Number(k) !== L.userTid)
    .sort((a, b) => b[1] - a[1])[0];
  return (
    <tr className={r.committedTo === L.userTid ? "hl" : ""}>
      <td>
        <PlayerLink L={L} p={p} face size={30} />
        <div className="tiny muted" style={{ marginLeft: 38 }}>
          {r.kind === "portal" ? `Transfer from ${r.fromTid !== undefined ? team(L, r.fromTid).short : "?"}` : `${p.city}, ${p.state}`}
        </div>
      </td>
      <td>
        <Stars n={r.stars} />
        <div className="tiny muted">#{r.rank}</div>
      </td>
      <td>
        {p.pos} <span className="muted small">{heightStr(p.hgt)}</span>
      </td>
      <td>
        {r.kind === "portal" ? <Grade v={p.ovr} /> : <KnownOvr p={p} />} {r.kind === "portal" ? <Grade v={p.pot + p.potErr} /> : <KnownPot p={p} />}
      </td>
      <td style={{ width: 300 }}>
        <HeatMeter L={L} p={p} tid={L.userTid} compact />
        {rival && (
          <div style={{ marginTop: 6 }}>
            <HeatMeter L={L} p={p} tid={Number(rival[0])} compact />
          </div>
        )}
      </td>
      <td>
        <StageCell L={L} p={p} />
        {L.settings.nil && (r.nil[L.userTid] ?? 0) > 0 && <div className="tiny muted">NIL {money(r.nil[L.userTid])}</div>}
      </td>
      <td>{r.stage !== "signed" && r.stage !== "unsigned" ? <QuickActions L={L} p={p} /> : null}</td>
      <td>
        <button className="btn btn-sm btn-ghost" title="Remove from board" onClick={() => mutate((LL) => void (LL.board = LL.board.filter((x) => x !== p.id)))}>
          ✕
        </button>
      </td>
    </tr>
  );
}

export function Targets() {
  const L = useLeague();
  const ut = team(L, L.userTid);
  const pool = L.players.filter((p) => p.recruit && (p.status === "recruit" || p.status === "portal") && p.recruit.stage !== "unsigned");
  const targets = pool
    .filter((p) => L.board.includes(p.id) || (p.recruit!.interest[L.userTid] ?? 0) > 0 || p.recruit!.offers.includes(L.userTid))
    .filter((p) => !(p.recruit!.committedTo !== null && p.recruit!.committedTo !== L.userTid && p.recruit!.stage === "signed"))
    .sort((a, b) => {
      const ca = a.recruit!.committedTo === L.userTid ? 1 : 0;
      const cb = b.recruit!.committedTo === L.userTid ? 1 : 0;
      if (ca !== cb) return ca - cb;
      return (b.recruit!.interest[L.userTid] ?? 0) - (a.recruit!.interest[L.userTid] ?? 0);
    });
  const lost = targets.filter((p) => p.recruit!.committedTo !== null && p.recruit!.committedTo !== L.userTid);
  const live = targets.filter((p) => !lost.includes(p));
  const commits = commitsFor(L, ut.id);
  return (
    <div>
      <PageHead
        title="My Targets"
        sub="Everyone you're recruiting. Spend points every week: they don't carry over."
        right={
          <Link to={`/l/${L.id}/recruiting`} className="btn">
            Find more recruits
          </Link>
        }
      />
      <RecruitingSummary />
      <Card title={`Active targets (${live.length})`} flush>
        {live.length ? (
          <div className="tbl-wrap">
            <table className="tbl">
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Stars</th>
                  <th>Pos</th>
                  <th>OVR / POT</th>
                  <th>You vs. top rival</th>
                  <th>Status</th>
                  <th>Call 3 · Visit 8 · Offer</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {live.map((p) => (
                  <TargetRow key={p.id} L={L} p={p} />
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Empty>
            No targets yet. Open the <Link to={`/l/${L.id}/recruiting`}>Recruiting Board</Link>, find players who fit your program, and start making calls.
          </Empty>
        )}
      </Card>
      {commits.length > 0 && (
        <Card title={`Commitments (${commits.length})`} className="mt-16" flush>
          <table className="tbl">
            <tbody>
              {commits.map((p) => (
                <tr key={p.id}>
                  <td>
                    <PlayerLink L={L} p={p} face size={28} colors={ut.colors} />
                  </td>
                  <td>
                    <Stars n={p.recruit!.stars} />
                  </td>
                  <td>{p.pos}</td>
                  <td className="muted">{p.recruit!.kind === "portal" ? "Transfer" : "Freshman"}</td>
                  <td>
                    <StageCell L={L} p={p} />
                  </td>
                  <td>{p.recruit!.stage === "committed" ? <QuickActions L={L} p={p} keys={["call", "assistant"]} /> : null}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="tiny muted card-b">Verbal commitments can flip if a rival builds a much stronger relationship. Keep in touch until they sign.</div>
        </Card>
      )}
      {lost.length > 0 && (
        <Card title={`Lost to other programs (${lost.length})`} className="mt-16" flush>
          <table className="tbl compact">
            <tbody>
              {lost.map((p) => (
                <tr key={p.id} className="dim">
                  <td>
                    <PlayerLink L={L} p={p} />
                  </td>
                  <td>
                    <Stars n={p.recruit!.stars} />
                  </td>
                  <td>
                    <StageCell L={L} p={p} />
                  </td>
                  <td>{p.recruit!.stage === "committed" ? <QuickActions L={L} p={p} keys={["call", "assistant"]} /> : null}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
