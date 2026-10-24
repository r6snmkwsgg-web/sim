import { Link, useSearchParams } from "react-router-dom";
import { useLeague } from "../store";
import { seasonLabel, shortDayLabel, team } from "../../engine/core";
import type { Game, League } from "../../engine/types";
import { Card, Empty, Logo, PageHead, SeasonSelect, TeamLink } from "../components/common";
import { currentRank } from "../../engine/rankings";
import { fetchSeason, useAsync } from "../util";

export function ScheduleTable({ L, tid, games, season }: { L: League; tid: number; games: Game[]; season: number }) {
  const mine = games.filter((g) => g.home === tid || g.away === tid).sort((a, b) => a.day - b.day || a.id - b.id);
  let w = 0;
  let l = 0;
  let cw = 0;
  let cl = 0;
  const isCur = season === L.season;
  return (
    <table className="tbl">
      <thead>
        <tr>
          <th>Date</th>
          <th>Opponent</th>
          <th>Type</th>
          <th>Result</th>
          <th className="n">Record</th>
          <th className="n">Conf</th>
        </tr>
      </thead>
      <tbody>
        {mine.map((g) => {
          const home = g.home === tid;
          const opp = home ? g.away : g.home;
          const us = home ? g.hs : g.as;
          const them = home ? g.as : g.hs;
          if (g.played) {
            if (us > them) w++;
            else l++;
            if (g.type === "conf") {
              if (us > them) cw++;
              else cl++;
            }
          }
          const ot = team(L, opp);
          const os = ot.seasons.find((s) => s.season === season);
          return (
            <tr key={g.id} className={g.played ? "" : "dim"}>
              <td className="muted">{shortDayLabel(season, g.day)}</td>
              <td>
                <span className="row" style={{ gap: 6 }}>
                  <span className="muted small" style={{ width: 18 }}>
                    {g.neutral ? "vs" : home ? "vs" : "@"}
                  </span>
                  <TeamLink L={L} tid={opp} size={20} rank={isCur ? currentRank(L, opp) : null} season={season} />
                  {os && <span className="faint small">({os.w}-{os.l})</span>}
                </span>
              </td>
              <td className="muted small">{g.event ?? (g.type === "conf" ? "Conference" : g.type === "nc" ? "Non-conf" : g.type === "ctourn" ? "Conf. Tournament" : g.type.toUpperCase())}</td>
              <td>
                {g.played ? (
                  <Link to={`/l/${L.id}/game/${g.id}`} className={us > them ? "good bold" : "bad bold"}>
                    {us > them ? "W" : "L"} {us}-{them}
                    {g.ot ? ` (${g.ot > 1 ? g.ot : ""}OT)` : ""}
                  </Link>
                ) : (
                  <Link to={`/l/${L.id}/game/${g.id}`} className="muted">
                    Preview
                  </Link>
                )}
              </td>
              <td className="n">{g.played ? `${w}-${l}` : ""}</td>
              <td className="n">{g.played && g.type === "conf" ? `${cw}-${cl}` : ""}</td>
            </tr>
          );
        })}
        {!mine.length && (
          <tr>
            <td colSpan={6} className="empty">
              No games.
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

export function Schedule() {
  const L = useLeague();
  const [sp, setSp] = useSearchParams();
  const tid = Number(sp.get("tid") ?? L.userTid);
  const season = Number(sp.get("season") ?? L.season);
  const { data: games, loading } = useAsync(async () => (season === L.season ? L.games : (await fetchSeason(L, season))?.games ?? []), [season, L.season, L.games]);
  const t = team(L, tid);
  const ts = t.seasons.find((s) => s.season === season);
  return (
    <div>
      <PageHead
        logo={<Logo team={t} size={44} />}
        title={`${t.name} Schedule`}
        sub={ts ? `${seasonLabel(season)} · ${ts.w}-${ts.l} (${ts.cw}-${ts.cl} conf)${ts.post ? ` · ${ts.post.event.toUpperCase()} ${ts.post.result}` : ""}` : seasonLabel(season)}
        right={
          <div className="row">
            <select className="select" value={tid} onChange={(e) => setSp({ tid: e.target.value, season: String(season) })}>
              {L.teams
                .slice()
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((x) => (
                  <option key={x.id} value={x.id}>
                    {x.name}
                  </option>
                ))}
            </select>
            <SeasonSelect L={L} value={season} onChange={(s) => setSp({ tid: String(tid), season: String(s) })} />
          </div>
        }
      />
      <Card flush>{loading && !games ? <Empty>Loading…</Empty> : <ScheduleTable L={L} tid={tid} games={games ?? []} season={season} />}</Card>
    </div>
  );
}
