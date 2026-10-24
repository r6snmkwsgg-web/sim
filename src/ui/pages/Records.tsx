import { useState } from "react";
import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { seasonLabel, team } from "../../engine/core";
import type { League, RecordEntry } from "../../engine/types";
import { CAREER_EXTRA, GAME_STATS, TEAM_SEASON_STATS, TOTAL_STATS } from "../../engine/records";
import { careerLine } from "../../engine/stats";
import { Card, PageHead, Seg, TeamLink } from "../components/common";

type Kind = "game" | "season" | "career" | "team";

function List({ L, entries, avg, kind, pctFmt }: { L: League; entries: RecordEntry[]; avg?: boolean; kind: Kind; pctFmt?: boolean }) {
  if (!entries.length) return <div className="empty">No records yet.</div>;
  return (
    <table className="tbl compact">
      <tbody>
        {entries.map((e, i) => (
          <tr key={`${e.pid}-${e.season}-${e.gid ?? 0}-${i}`} className={e.tid === L.userTid ? "hl" : ""}>
            <td className="muted" style={{ width: 24 }}>
              {i + 1}
            </td>
            <td>
              {kind === "team" ? (
                <TeamLink L={L} tid={e.tid} size={18} season={e.season} />
              ) : (
                <>
                  <Link to={`/l/${L.id}/player/${e.pid}`}>{e.name}</Link> <span className="faint small">{team(L, e.tid).short}</span>
                </>
              )}
            </td>
            <td className="muted small">
              {kind === "game" && e.gid !== undefined ? (
                <Link to={`/l/${L.id}/game/${e.gid}`}>
                  {seasonLabel(e.season)} {e.opp !== undefined ? `vs ${team(L, e.opp).short}` : ""}
                </Link>
              ) : kind === "career" ? (
                `thru ${seasonLabel(e.season)}`
              ) : (
                seasonLabel(e.season)
              )}
            </td>
            <td className="n bold">{pctFmt ? e.value.toFixed(3).replace(/^0/, "") : avg ? e.value.toFixed(1) : e.value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function Records() {
  const L = useLeague();
  const [kind, setKind] = useState<Kind>("game");
  const R = L.records;
  // active players count toward career records too
  const careerList = (key: string): RecordEntry[] => {
    const st = [...TOTAL_STATS, ...CAREER_EXTRA].find((x) => x.key === key)!;
    const list = (R.career[key] ?? []).slice();
    for (const p of L.players) {
      if (p.status !== "active" || !p.stats.length) continue;
      const c = careerLine(p);
      if ("avg" in st && st.avg && c.g < 60) continue;
      const v = Math.round(st.get(c) * 10) / 10;
      if (v <= 0) continue;
      if (list.length >= 25 && v <= list[list.length - 1].value) continue;
      list.push({ pid: p.id, name: `${p.first} ${p.last}`, tid: p.tid ?? p.stats[p.stats.length - 1].tid, season: L.season, value: v });
      list.sort((a, b) => b.value - a.value);
      if (list.length > 25) list.length = 25;
    }
    return list;
  };
  return (
    <div>
      <PageHead
        title="Record Book"
        sub="League-wide records since the league began. Program records are on each team's history page."
        right={
          <Seg
            options={[
              { key: "game", label: "Single Game" },
              { key: "season", label: "Single Season" },
              { key: "career", label: "Career" },
              { key: "team", label: "Team Season" },
            ]}
            value={kind}
            onChange={setKind}
          />
        }
      />
      <div className="grid g3">
        {kind === "game" &&
          GAME_STATS.map((s) => (
            <Card key={s.key} title={s.label} flush>
              <List L={L} entries={R.game[s.key] ?? []} kind="game" />
            </Card>
          ))}
        {kind === "season" &&
          TOTAL_STATS.map((s) => (
            <Card key={s.key} title={s.label} flush>
              <List L={L} entries={R.season[s.key] ?? []} kind="season" avg={s.avg} />
            </Card>
          ))}
        {kind === "career" &&
          [...TOTAL_STATS, ...CAREER_EXTRA].map((s) => (
            <Card key={s.key} title={s.label} flush>
              <List L={L} entries={careerList(s.key)} kind="career" avg={"avg" in s ? Boolean(s.avg) : false} />
            </Card>
          ))}
        {kind === "team" &&
          TEAM_SEASON_STATS.map((s) => (
            <Card key={s.key} title={s.label} flush>
              <List L={L} entries={R.teamSeason[s.key] ?? []} kind="team" avg={s.key === "ppg" || s.key === "margin"} pctFmt={s.key === "wpct"} />
            </Card>
          ))}
      </div>
    </div>
  );
}
