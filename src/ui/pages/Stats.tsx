import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useLeague } from "../store";
import { team } from "../../engine/core";
import type { League, Player, PlayerSeasonStats } from "../../engine/types";
import { Card, Empty, heroStyle, Logo, PageHead, PlayerLink, SeasonSelect, Table, Tabs, TeamLink, type Col } from "../components/common";
import { Face } from "../components/Face";
import { f1, pct100, useAsync } from "../util";
import { getAllArchivedPlayers } from "../db";

interface Row {
  p: Player;
  s: PlayerSeasonStats;
}

async function seasonRows(L: League, season: number): Promise<Row[]> {
  const pool: Player[] = L.players.filter((p) => p.stats.some((s) => s.season === season));
  if (season !== L.season) {
    const arch = await getAllArchivedPlayers(L.id);
    pool.push(...arch.filter((p) => p.stats.some((s) => s.season === season)));
  }
  const out: Row[] = [];
  for (const p of pool) for (const s of p.stats) if (s.season === season && s.g > 0) out.push({ p, s });
  return out;
}

const LEADERS: { key: string; label: string; f: (s: PlayerSeasonStats) => number; pct?: [keyof PlayerSeasonStats, keyof PlayerSeasonStats, number] }[] = [
  { key: "pts", label: "Points", f: (s) => s.pts / s.g },
  { key: "reb", label: "Rebounds", f: (s) => (s.orb + s.drb) / s.g },
  { key: "ast", label: "Assists", f: (s) => s.ast / s.g },
  { key: "stl", label: "Steals", f: (s) => s.stl / s.g },
  { key: "blk", label: "Blocks", f: (s) => s.blk / s.g },
  { key: "tpm", label: "3-Pointers Made", f: (s) => s.tpm / s.g },
  { key: "fg", label: "Field Goal %", f: (s) => (s.fga ? (100 * s.fgm) / s.fga : 0), pct: ["fgm", "fga", 5] },
  { key: "tp", label: "3-Point %", f: (s) => (s.tpa ? (100 * s.tpm) / s.tpa : 0), pct: ["tpm", "tpa", 2.5] },
  { key: "ft", label: "Free Throw %", f: (s) => (s.fta ? (100 * s.ftm) / s.fta : 0), pct: ["ftm", "fta", 2.5] },
];

function Leaders({ L, rows }: { L: League; rows: Row[] }) {
  const maxG = Math.max(1, ...rows.map((r) => r.s.g));
  const minG = Math.max(1, Math.floor(maxG * 0.6));
  return (
    <div className="grid g3">
      {LEADERS.map((ld) => {
        const elig = rows.filter((r) => r.s.g >= minG && (!ld.pct || (r.s[ld.pct[1]] as number) >= ld.pct[2] * r.s.g * 0.4 + 10));
        const top = elig.sort((a, b) => ld.f(b.s) - ld.f(a.s)).slice(0, 10);
        return (
          <Card key={ld.key} title={ld.label} flush>
            {top[0] && (
              <Link to={`/l/${L.id}/player/${top[0].p.id}`} className="leader-top" style={heroStyle(team(L, top[0].s.tid).colors)}>
                <Face seed={top[0].p.faceSeed} race={top[0].p.race} colors={team(L, top[0].s.tid).colors} size={60} crop="bust" frame={false} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="ellipsis" style={{ fontWeight: 750, fontSize: 15 }}>
                    {top[0].p.first} {top[0].p.last}
                  </div>
                  <div className="row small" style={{ gap: 6, opacity: 0.85 }}>
                    <Logo team={team(L, top[0].s.tid)} size={16} /> {team(L, top[0].s.tid).name}
                  </div>
                </div>
                <div className="leader-top-v">{f1(ld.f(top[0].s))}</div>
              </Link>
            )}
            <table className="tbl compact">
              <tbody>
                {top.slice(1).map((r, i) => (
                  <tr key={`${r.p.id}-${r.s.tid}`} className={r.s.tid === L.userTid ? "hl" : ""}>
                    <td className="rk" style={{ width: 22 }}>
                      {i + 2}
                    </td>
                    <td>
                      <span className="team-cell">
                        <Logo team={team(L, r.s.tid)} size={18} />
                        <PlayerLink L={L} p={r.p} />
                      </span>
                    </td>
                    <td className="n bold">{f1(ld.f(r.s))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        );
      })}
    </div>
  );
}

function PlayerStats({ L, rows }: { L: League; rows: Row[] }) {
  const [conf, setConf] = useState<number | "all">("all");
  const [pos, setPos] = useState("all");
  const [minG, setMinG] = useState(10);
  const [q, setQ] = useState("");
  const filtered = rows.filter((r) => (conf === "all" || team(L, r.s.tid).cid === conf) && (pos === "all" || r.p.pos === pos) && r.s.g >= minG && (!q || `${r.p.first} ${r.p.last}`.toLowerCase().includes(q.toLowerCase())));
  const pg = (f: (s: PlayerSeasonStats) => number) => (r: Row) => f(r.s) / r.s.g;
  const cols: Col<Row>[] = [
    { key: "name", label: "Player", render: (r) => <PlayerLink L={L} p={r.p} />, sort: (r) => r.p.last },
    { key: "team", label: "Team", render: (r) => <TeamLink L={L} tid={r.s.tid} short size={16} />, sort: (r) => team(L, r.s.tid).short },
    { key: "pos", label: "Pos", render: (r) => r.p.pos },
    { key: "g", label: "G", render: (r) => r.s.g, sort: (r) => r.s.g, num: true },
    { key: "min", label: "MIN", render: (r) => f1(pg((s) => s.min)(r)), sort: pg((s) => s.min), num: true },
    { key: "pts", label: "PTS", render: (r) => <b>{f1(pg((s) => s.pts)(r))}</b>, sort: pg((s) => s.pts), num: true },
    { key: "reb", label: "REB", render: (r) => f1(pg((s) => s.orb + s.drb)(r)), sort: pg((s) => s.orb + s.drb), num: true },
    { key: "ast", label: "AST", render: (r) => f1(pg((s) => s.ast)(r)), sort: pg((s) => s.ast), num: true },
    { key: "stl", label: "STL", render: (r) => f1(pg((s) => s.stl)(r)), sort: pg((s) => s.stl), num: true },
    { key: "blk", label: "BLK", render: (r) => f1(pg((s) => s.blk)(r)), sort: pg((s) => s.blk), num: true },
    { key: "tov", label: "TO", render: (r) => f1(pg((s) => s.tov)(r)), sort: pg((s) => s.tov), num: true },
    { key: "fg", label: "FG%", render: (r) => pct100(r.s.fgm, r.s.fga), sort: (r) => (r.s.fga ? r.s.fgm / r.s.fga : 0), num: true },
    { key: "tp", label: "3P%", render: (r) => pct100(r.s.tpm, r.s.tpa), sort: (r) => (r.s.tpa ? r.s.tpm / r.s.tpa : 0), num: true },
    { key: "tpm", label: "3PM", render: (r) => f1(pg((s) => s.tpm)(r)), sort: pg((s) => s.tpm), num: true },
    { key: "ft", label: "FT%", render: (r) => pct100(r.s.ftm, r.s.fta), sort: (r) => (r.s.fta ? r.s.ftm / r.s.fta : 0), num: true },
  ];
  return (
    <Card flush>
      <div className="card-b row-wrap" style={{ borderBottom: "1px solid var(--border)" }}>
        <input className="input" placeholder="Search…" value={q} onChange={(e) => setQ(e.target.value)} style={{ width: 180 }} />
        <select className="select" value={conf} onChange={(e) => setConf(e.target.value === "all" ? "all" : Number(e.target.value))}>
          <option value="all">All conferences</option>
          {L.conferences.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <select className="select" value={pos} onChange={(e) => setPos(e.target.value)}>
          <option value="all">All positions</option>
          {["PG", "SG", "SF", "PF", "C"].map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
        <label className="row small">
          Min games
          <input className="input" type="number" value={minG} min={0} style={{ width: 70 }} onChange={(e) => setMinG(Number(e.target.value))} />
        </label>
        <span className="muted small">{filtered.length} players</span>
      </div>
      <Table cols={cols} rows={filtered} rowKey={(r) => `${r.p.id}-${r.s.tid}`} initialSort="pts" limit={50} rowClass={(r) => (r.s.tid === L.userTid ? "hl" : undefined)} />
    </Card>
  );
}

interface TRow {
  tid: number;
  g: number;
  ppg: number;
  oppg: number;
  fgp: number;
  tpp: number;
  ftp: number;
  rpg: number;
  apg: number;
  topg: number;
  tpa: number;
}

function TeamStats({ L, rows, season }: { L: League; rows: Row[]; season: number }) {
  const data = useMemo(() => {
    const by = new Map<number, PlayerSeasonStats[]>();
    for (const r of rows) {
      const a = by.get(r.s.tid) ?? [];
      a.push(r.s);
      by.set(r.s.tid, a);
    }
    const out: TRow[] = [];
    for (const t of L.teams) {
      const ts = t.seasons.find((s) => s.season === season);
      const ls = by.get(t.id) ?? [];
      const g = ts ? ts.w + ts.l : 0;
      if (!ts || !g) continue;
      const sum = (k: keyof PlayerSeasonStats) => ls.reduce((a, s) => a + (s[k] as number), 0);
      out.push({
        tid: t.id,
        g,
        ppg: ts.pf / g,
        oppg: ts.pa / g,
        fgp: sum("fga") ? (100 * sum("fgm")) / sum("fga") : 0,
        tpp: sum("tpa") ? (100 * sum("tpm")) / sum("tpa") : 0,
        ftp: sum("fta") ? (100 * sum("ftm")) / sum("fta") : 0,
        rpg: (sum("orb") + sum("drb")) / g,
        apg: sum("ast") / g,
        topg: sum("tov") / g,
        tpa: sum("tpa") / g,
      });
    }
    return out;
  }, [rows, L, season]);
  const c = (key: keyof TRow, label: string, asc = false): Col<TRow> => ({ key, label, render: (r) => f1(r[key] as number), sort: (r) => (asc ? -(r[key] as number) : (r[key] as number)), num: true });
  const cols: Col<TRow>[] = [
    { key: "team", label: "Team", render: (r) => <TeamLink L={L} tid={r.tid} size={18} season={season} />, sort: (r) => team(L, r.tid).name },
    { key: "g", label: "G", render: (r) => r.g, num: true },
    c("ppg", "PPG"),
    c("oppg", "Opp PPG", true),
    { key: "mrg", label: "Margin", render: (r) => f1(r.ppg - r.oppg), sort: (r) => r.ppg - r.oppg, num: true },
    c("fgp", "FG%"),
    c("tpp", "3P%"),
    c("tpa", "3PA"),
    c("ftp", "FT%"),
    c("rpg", "REB"),
    c("apg", "AST"),
    c("topg", "TO", true),
  ];
  return (
    <Card flush>
      <Table cols={cols} rows={data} rowKey={(r) => r.tid} initialSort="mrg" limit={50} rowClass={(r) => (r.tid === L.userTid ? "hl" : undefined)} />
    </Card>
  );
}

export function Stats() {
  const L = useLeague();
  const [sp, setSp] = useSearchParams();
  const season = Number(sp.get("season") ?? L.season);
  const [tab, setTab] = useState<"leaders" | "players" | "teams">("leaders");
  const { data, loading } = useAsync(() => seasonRows(L, season), [season, L.season, season === L.season ? L.day : 0, L.phase]);
  return (
    <div>
      <PageHead
        title="Statistics"
        sub={season !== L.season ? "Past seasons include players who have since left college" : undefined}
        right={
          <div className="row">
            <Link to={`/l/${L.id}/records`} className="btn">
              Record Book
            </Link>
            <SeasonSelect L={L} value={season} onChange={(s) => setSp({ season: String(s) })} />
          </div>
        }
      />
      <Tabs
        tabs={[
          { key: "leaders", label: "Leaders" },
          { key: "players", label: "Player Stats" },
          { key: "teams", label: "Team Stats" },
        ]}
        value={tab}
        onChange={setTab}
      />
      {loading && !data ? (
        <Empty>Loading…</Empty>
      ) : !data?.length ? (
        <Empty>No games played yet this season.</Empty>
      ) : tab === "leaders" ? (
        <Leaders L={L} rows={data} />
      ) : tab === "players" ? (
        <PlayerStats L={L} rows={data} />
      ) : (
        <TeamStats L={L} rows={data} season={season} />
      )}
    </div>
  );
}
