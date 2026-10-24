import { useState } from "react";
import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { dayLabel, team } from "../../engine/core";
import { currentRank } from "../../engine/rankings";
import { Card, Logo, PageHead, Seg } from "../components/common";
import type { Game } from "../../engine/types";

export function Scores() {
  const L = useLeague();
  const days = [...new Set(L.games.map((g) => g.day))].sort((a, b) => a - b);
  const playedDays = days.filter((d) => L.games.some((g) => g.day === d && g.played));
  const defaultDay = playedDays.length ? playedDays[playedDays.length - 1] : days[0] ?? 0;
  const [day, setDay] = useState<number>(defaultDay);
  const [filter, setFilter] = useState<"all" | "top25" | "conf" | "mine">("all");
  const ut = team(L, L.userTid);
  const idx = days.indexOf(day);
  const games = L.games
    .filter((g) => g.day === day)
    .filter((g) => {
      if (filter === "top25") return !!(currentRank(L, g.home) || currentRank(L, g.away));
      if (filter === "conf") return team(L, g.home).cid === ut.cid || team(L, g.away).cid === ut.cid;
      if (filter === "mine") return g.home === L.userTid || g.away === L.userTid;
      return true;
    })
    .sort((a, b) => Math.min(currentRank(L, a.home) ?? 99, currentRank(L, a.away) ?? 99) - Math.min(currentRank(L, b.home) ?? 99, currentRank(L, b.away) ?? 99));
  const line = (g: Game, tid: number, pts: number, won: boolean) => {
    const t = team(L, tid);
    const r = currentRank(L, tid);
    return (
      <div className="row" style={{ gap: 8, opacity: g.played && !won ? 0.6 : 1 }}>
        <Logo team={t} size={22} />
        <Link to={`/l/${L.id}/team/${tid}`} className={won ? "bold" : ""} style={{ flex: 1 }}>
          {r ? <span className="muted small">{r} </span> : null}
          {t.name}
        </Link>
        <span className="bold num" style={{ fontSize: 15 }}>
          {g.played ? pts : ""}
        </span>
      </div>
    );
  };
  return (
    <div>
      <PageHead
        title="Scores"
        sub={days.length ? dayLabel(L.season, day) : "No games scheduled"}
        right={
          <div className="row">
            <Seg
              options={[
                { key: "all", label: "All" },
                { key: "top25", label: "Top 25" },
                { key: "conf", label: L.conferences[ut.cid].short },
                { key: "mine", label: "My team" },
              ]}
              value={filter}
              onChange={setFilter}
            />
            <button className="btn" disabled={idx <= 0} onClick={() => setDay(days[idx - 1])}>
              ‹ Prev
            </button>
            <select className="select" value={day} onChange={(e) => setDay(Number(e.target.value))}>
              {days.map((d) => (
                <option key={d} value={d}>
                  {dayLabel(L.season, d)}
                </option>
              ))}
            </select>
            <button className="btn" disabled={idx >= days.length - 1} onClick={() => setDay(days[idx + 1])}>
              Next ›
            </button>
          </div>
        }
      />
      <div className="muted small mb-12">{games.length} games</div>
      <div className="grid g4">
        {games.map((g) => (
          <Card key={g.id} className={g.home === L.userTid || g.away === L.userTid ? "hl" : ""}>
            <div className="col" style={{ gap: 6 }}>
              {line(g, g.away, g.as, g.as > g.hs)}
              {line(g, g.home, g.hs, g.hs > g.as)}
              <div className="row tiny muted">
                <span>{g.event ?? (g.type === "conf" ? "Conference" : g.type === "nc" ? (g.neutral ? "Neutral" : "Non-conf") : g.type.toUpperCase())}</span>
                <span className="spacer" />
                <Link to={`/l/${L.id}/game/${g.id}`}>{g.played ? `Final${g.ot ? ` (${g.ot > 1 ? g.ot : ""}OT)` : ""}` : "Preview"}</Link>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
