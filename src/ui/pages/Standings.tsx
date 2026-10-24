import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useLeague } from "../store";
import { team } from "../../engine/core";
import type { League, TeamSeason } from "../../engine/types";
import { currentRank, powerRanks } from "../../engine/rankings";
import { confStandings } from "../../engine/postseason";
import { Card, PageHead, SeasonSelect, TeamLink } from "../components/common";
import { fetchSeason, useAsync } from "../util";
import { streakStr } from "../helpers";

function ConfTable({ L, cid, season, order }: { L: League; cid: number; season: number; order: number[] }) {
  const cur = season === L.season;
  const pr = cur ? powerRanks(L) : null;
  const rows = order.map((tid) => ({ t: team(L, tid), s: team(L, tid).seasons.find((x) => x.season === season) as TeamSeason | undefined }));
  return (
    <table className="tbl compact">
      <thead>
        <tr>
          <th />
          <th>Team</th>
          <th className="n">Conf</th>
          <th className="n">Pct</th>
          <th className="n">Overall</th>
          <th className="n">Home</th>
          <th className="n">Away</th>
          <th className="n">Neutral</th>
          <th className="n">Strk</th>
          <th className="n" title="Power rating rank">Pwr</th>
          <th>Postseason</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(({ t, s }, i) =>
          s ? (
            <tr key={t.id} className={t.id === L.userTid ? "hl" : ""}>
              <td className="muted">{i + 1}</td>
              <td>
                <TeamLink L={L} tid={t.id} size={20} rank={cur ? currentRank(L, t.id) : s.apFinal} season={season} />
                {s.confChamp && <span title="Regular season champion" className="trophy"> ★</span>}
              </td>
              <td className="n bold">
                {s.cw}-{s.cl}
              </td>
              <td className="n muted">{s.cw + s.cl ? (s.cw / (s.cw + s.cl)).toFixed(3).replace(/^0/, "") : "-"}</td>
              <td className="n">
                {s.w}-{s.l}
              </td>
              <td className="n muted">
                {s.hw}-{s.hl}
              </td>
              <td className="n muted">
                {s.aw}-{s.al}
              </td>
              <td className="n muted">
                {s.nw}-{s.nl}
              </td>
              <td className="n muted">{streakStr(s.streak)}</td>
              <td className="n muted">{pr ? pr.get(t.id) : ""}</td>
              <td className="small">
                {s.confTourney === "Champion" && <span className="badge good">Conf. champ</span>}{" "}
                {s.post ? <span className="muted">{s.post.event.toUpperCase()} {s.post.event === "ncaa" ? `(${s.post.seed}) ` : ""}{s.post.result}</span> : null}
              </td>
            </tr>
          ) : null,
        )}
      </tbody>
    </table>
  );
}

export function Standings() {
  const L = useLeague();
  const [sp, setSp] = useSearchParams();
  const season = Number(sp.get("season") ?? L.season);
  const [view, setView] = useState<number | "all">(team(L, L.userTid).cid);
  const { data } = useAsync(async () => {
    if (season === L.season) return L.conferences.map((c) => ({ cid: c.id, order: confStandings(L, c.id) }));
    return (await fetchSeason(L, season))?.standings ?? [];
  }, [season, L.season, L.day]);
  const confs = view === "all" ? L.conferences : L.conferences.filter((c) => c.id === view);
  return (
    <div>
      <PageHead
        title="Standings"
        right={
          <div className="row">
            <select className="select" value={view} onChange={(e) => setView(e.target.value === "all" ? "all" : Number(e.target.value))}>
              <option value="all">All conferences</option>
              {L.conferences.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            <SeasonSelect L={L} value={season} onChange={(s) => setSp({ season: String(s) })} />
          </div>
        }
      />
      <div className="col gap-16">
        {confs.map((c) => {
          const order = data?.find((x) => x.cid === c.id)?.order ?? [];
          return (
            <Card key={c.id} title={c.name} sub={`${c.confGames} conference games · top ${c.tourneyTeams} make the tournament`} flush>
              <ConfTable L={L} cid={c.id} season={season} order={order} />
            </Card>
          );
        })}
      </div>
    </div>
  );
}
