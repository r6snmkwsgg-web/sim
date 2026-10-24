import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { seasonLabel, teamMaybe, shortDayLabel } from "../../engine/core";
import { classLabel, grade, heightStr, RATING_LABELS, CLASS_LABELS } from "../../engine/ratings";
import type { BoxLine, Game, League, Player, PlayerSeasonStats, RatingKey, Tendencies } from "../../engine/types";
import { careerLine } from "../../engine/stats";
import { FOCUS_LABELS } from "../../engine/development";
import { regionOf } from "../../engine/data/cities";
import { Card, Empty, Grade, Logo, Rating, Stars, Tabs, TeamLink } from "../components/common";
import { Face } from "../components/Face";
import { StatusBadges } from "./Roster";
import { RecruitProfile } from "./RecruitProfile";
import { fetchPlayer, fetchSeason, f1, pct100, useAsync, cls } from "../util";
import { getBox } from "../db";

const GROUPS: { name: string; keys: RatingKey[] }[] = [
  { name: "Offense", keys: ["ins", "mid", "three", "ft", "hnd", "pas", "iq"] },
  { name: "Defense", keys: ["perD", "intD", "stl", "blk", "reb"] },
  { name: "Physical", keys: ["ath", "str", "end"] },
];

function RatingRow({ k, v }: { k: RatingKey; v: number }) {
  const g = grade(v);
  const color = v >= 71 ? "var(--ga)" : v >= 59 ? "var(--gb)" : v >= 47 ? "var(--gc)" : v >= 35 ? "var(--gd)" : "var(--gf)";
  return (
    <div className="row" style={{ gap: 10 }}>
      <span style={{ width: 96 }} className="muted">
        {RATING_LABELS[k]}
      </span>
      <div className="meter" style={{ flex: 1 }}>
        <span style={{ width: `${v}%`, background: color }} />
      </div>
      <span style={{ width: 26 }} className="right bold num">
        {Math.round(v)}
      </span>
      <span style={{ width: 22 }} className="faint small">
        {g}
      </span>
    </div>
  );
}

function StatsTable({ L, p, mode }: { L: League; p: Player; mode: "pg" | "tot" }) {
  const rows = p.stats.filter((s) => s.g > 0 || s.rs);
  const d = (x: number, g: number) => (mode === "pg" ? (g ? f1(x / g) : "-") : String(Math.round(x)));
  const line = (s: PlayerSeasonStats | ReturnType<typeof careerLine>, label: React.ReactNode, team: React.ReactNode, year: string) => (
    <>
      <td>{label}</td>
      <td>{team}</td>
      <td>{year}</td>
      <td className="n">{s.g}</td>
      <td className="n">{s.gs}</td>
      <td className="n">{d(s.min, s.g)}</td>
      <td className="n bold">{d(s.pts, s.g)}</td>
      <td className="n">{d(s.orb + s.drb, s.g)}</td>
      <td className="n">{d(s.ast, s.g)}</td>
      <td className="n">{d(s.stl, s.g)}</td>
      <td className="n">{d(s.blk, s.g)}</td>
      <td className="n">{d(s.tov, s.g)}</td>
      <td className="n">{pct100(s.fgm, s.fga)}</td>
      <td className="n">{pct100(s.tpm, s.tpa)}</td>
      <td className="n">{pct100(s.ftm, s.fta)}</td>
    </>
  );
  const career = careerLine(p);
  return (
    <div className="tbl-wrap">
      <table className="tbl">
        <thead>
          <tr>
            <th>Season</th>
            <th>Team</th>
            <th>Class</th>
            <th className="n">G</th>
            <th className="n">GS</th>
            <th className="n">MIN</th>
            <th className="n">PTS</th>
            <th className="n">REB</th>
            <th className="n">AST</th>
            <th className="n">STL</th>
            <th className="n">BLK</th>
            <th className="n">TO</th>
            <th className="n">FG%</th>
            <th className="n">3P%</th>
            <th className="n">FT%</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((s) => (
            <tr key={`${s.season}-${s.tid}`}>{line(s, seasonLabel(s.season), <TeamLink L={L} tid={s.tid} short size={18} season={s.season} />, s.rs ? "Redshirt" : CLASS_LABELS[Math.min(5, s.year)] ?? "")}</tr>
          ))}
          {!rows.length && (
            <tr>
              <td colSpan={15} className="empty">
                No college games played yet.
              </td>
            </tr>
          )}
        </tbody>
        {rows.length > 1 && (
          <tfoot>
            <tr>{line(career, "Career", "", "")}</tr>
          </tfoot>
        )}
      </table>
    </div>
  );
}

function GameLog({ L, p }: { L: League; p: Player }) {
  const seasons = [...new Set(p.stats.map((s) => s.season))].sort((a, b) => b - a);
  const [season, setSeason] = useState<number>(seasons[0] ?? L.season);
  const { data, loading } = useAsync(async () => {
    const tids = new Set(p.stats.filter((s) => s.season === season).map((s) => s.tid));
    let games: Game[];
    if (season === L.season) games = L.games;
    else games = (await fetchSeason(L, season))?.games ?? [];
    const mine = games.filter((g) => g.played && g.hasBox && (tids.has(g.home) || tids.has(g.away))).sort((a, b) => a.day - b.day);
    const boxes = await Promise.all(mine.map((g) => getBox(L.id, g.id)));
    const out: { g: Game; line: BoxLine; tid: number }[] = [];
    boxes.forEach((b, i) => {
      if (!b) return;
      for (const side of [b.home, b.away]) {
        const line = side.lines.find((l) => l.pid === p.id);
        if (line) out.push({ g: mine[i], line, tid: side.tid });
      }
    });
    return out;
  }, [p.id, season, L.games.length, L.season]);
  if (!seasons.length) return <Empty>No games yet.</Empty>;
  return (
    <div>
      <div className="row card-b">
        <select className="select" value={season} onChange={(e) => setSeason(Number(e.target.value))}>
          {seasons.map((s) => (
            <option key={s} value={s}>
              {seasonLabel(s)}
            </option>
          ))}
        </select>
        {loading && <span className="muted small">Loading…</span>}
      </div>
      <div className="tbl-wrap">
        <table className="tbl compact">
          <thead>
            <tr>
              <th>Date</th>
              <th>Opponent</th>
              <th>Result</th>
              <th className="n">MIN</th>
              <th className="n">PTS</th>
              <th className="n">FG</th>
              <th className="n">3PT</th>
              <th className="n">FT</th>
              <th className="n">REB</th>
              <th className="n">AST</th>
              <th className="n">STL</th>
              <th className="n">BLK</th>
              <th className="n">TO</th>
              <th className="n">PF</th>
              <th className="n">+/-</th>
            </tr>
          </thead>
          <tbody>
            {(data ?? []).map(({ g, line, tid }) => {
              const home = g.home === tid;
              const us = home ? g.hs : g.as;
              const them = home ? g.as : g.hs;
              return (
                <tr key={g.id}>
                  <td className="muted">{shortDayLabel(g.season, g.day)}</td>
                  <td>
                    <span className="muted small">{g.neutral ? "vs " : home ? "vs " : "@ "}</span>
                    <TeamLink L={L} tid={home ? g.away : g.home} short size={16} />
                  </td>
                  <td>
                    <Link to={`/l/${L.id}/game/${g.id}`} className={us > them ? "good" : "bad"}>
                      {us > them ? "W" : "L"} {us}-{them}
                    </Link>
                  </td>
                  <td className="n">{Math.round(line.min)}</td>
                  <td className="n bold">{line.pts}</td>
                  <td className="n">
                    {line.fgm}-{line.fga}
                  </td>
                  <td className="n">
                    {line.tpm}-{line.tpa}
                  </td>
                  <td className="n">
                    {line.ftm}-{line.fta}
                  </td>
                  <td className="n">{line.orb + line.drb}</td>
                  <td className="n">{line.ast}</td>
                  <td className="n">{line.stl}</td>
                  <td className="n">{line.blk}</td>
                  <td className="n">{line.tov}</td>
                  <td className="n">{line.pf}</td>
                  <td className={cls("n", line.pm > 0 ? "good" : line.pm < 0 ? "bad" : "")}>{line.pm > 0 ? `+${line.pm}` : line.pm}</td>
                </tr>
              );
            })}
            {!loading && !(data ?? []).length && (
              <tr>
                <td colSpan={15} className="empty">
                  No box scores stored for this season.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Instructions({ p }: { p: Player }) {
  const L = useLeague();
  const t = teamMaybe(L, p.tid)!;
  const set = (k: keyof Tendencies, v: number) => mutate(() => void (p.tend[k] = v));
  const labels: [keyof Tendencies, string, string][] = [
    ["three", "Shoot 3", "How often he looks for three-point shots"],
    ["mid", "Shoot Mid-Range", "Pull-ups and mid-range jumpers"],
    ["inside", "Shoot Inside", "Post-ups and shots around the basket"],
    ["drive", "Drive", "Attacking the rim off the dribble (draws fouls)"],
  ];
  return (
    <div className="grid g2">
      <Card title="Shot Tendencies" sub="5 is his natural tendency. 0 means never; 10 means twice as often.">
        <div className="col gap-12">
          {labels.map(([k, label, desc]) => (
            <div key={k}>
              <div className="slider-row">
                <span className="bold">{label}</span>
                <input type="range" min={0} max={10} step={1} value={p.tend[k]} onChange={(e) => set(k, Number(e.target.value))} />
                <span className="right bold num">{p.tend[k]}</span>
              </div>
              <div className="tiny muted" style={{ marginLeft: 120 }}>
                {desc}
              </div>
            </div>
          ))}
          <div className="row">
            <button className="btn btn-sm" onClick={() => mutate(() => void (p.tend = { three: 5, mid: 5, inside: 5, drive: 5 }))}>
              Reset to 5
            </button>
          </div>
        </div>
      </Card>
      <Card title="Individual Practice Focus" sub="Added on top of the team's practice plan">
        <select
          className="select"
          value={t.practice.individual[p.id] ?? "balanced"}
          onChange={(e) =>
            mutate(() => {
              const v = e.target.value as keyof typeof FOCUS_LABELS;
              if (v === "balanced") delete t.practice.individual[p.id];
              else t.practice.individual[p.id] = v;
            })
          }
        >
          {Object.entries(FOCUS_LABELS).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
        <p className="small muted mt-12">Focus areas develop roughly twice as fast as the rest of his game. Development is also driven by potential, work ethic, minutes played and your coaching.</p>
      </Card>
    </div>
  );
}

export function PlayerPage() {
  const L = useLeague();
  const { pid } = useParams();
  const id = Number(pid);
  const { data: p, loading } = useAsync(() => fetchPlayer(L, id), [id, L.id]);
  const [tab, setTab] = useState<"overview" | "stats" | "log" | "ratings" | "instr">("overview");
  const colors = useMemo<[string, string]>(() => {
    const tid = p?.tid ?? p?.stats[p.stats.length - 1]?.tid ?? p?.recruit?.committedTo ?? null;
    return teamMaybe(L, tid)?.colors ?? ["#4b5563", "#e5e7eb"];
  }, [p, L]);
  if (loading && !p) return <Empty>Loading…</Empty>;
  if (!p) return <Empty>Player not found.</Empty>;
  if ((p.status === "recruit" || p.status === "portal") && p.recruit) return <RecruitProfile p={p} />;
  const t = teamMaybe(L, p.tid);
  const isUser = p.tid === L.userTid && p.status === "active";
  const cur = p.stats.find((s) => s.season === L.season && s.tid === p.tid);
  const lastTid = p.stats[p.stats.length - 1]?.tid;
  return (
    <div className="col gap-16">
      <div className="card" style={{ overflow: "hidden" }}>
        <div style={{ display: "flex", gap: 0 }}>
          <div style={{ background: colors[0], padding: "16px 18px 0", display: "flex", alignItems: "flex-end" }}>
            <Face seed={p.faceSeed} race={p.race} colors={colors} size={120} />
          </div>
          <div style={{ padding: 18, flex: 1 }}>
            <div className="row">
              <div>
                <div className="muted small">
                  {p.status === "active" && t ? `#${p.jersey} · ` : ""}
                  {p.pos} · {p.archetype}
                </div>
                <div className="hero-name">
                  {p.first} {p.last}
                </div>
              </div>
              <div className="spacer" />
              <div className="row gap-16">
                <div className="center">
                  <div className="tiny muted bold">OVR</div>
                  <div style={{ fontSize: 22 }}>
                    <Grade v={p.ovr} />
                  </div>
                </div>
                <div className="center">
                  <div className="tiny muted bold">POT</div>
                  <div style={{ fontSize: 22 }}>
                    <Grade v={p.pot + p.potErr} />
                  </div>
                </div>
              </div>
            </div>
            <div className="row-wrap mt-8" style={{ gap: 18 }}>
              <span>
                <b>{heightStr(p.hgt)}</b> <span className="muted">· {p.wgt} lbs · {heightStr(p.wing)} wingspan</span>
              </span>
              <span className="muted">
                {p.city}, {p.state} ({regionOf(p.state)})
              </span>
              {p.status === "active" ? (
                <span>
                  {classLabel(p)} at <TeamLink L={L} tid={p.tid} size={18} />
                </span>
              ) : (
                <span className="badge dark">
                  {p.status === "drafted" && p.draft
                    ? `Drafted ${p.draft.season} · Rd ${p.draft.round}, Pick ${p.draft.pick} (${p.draft.team})`
                    : p.status === "graduated"
                      ? `Graduated ${p.leftSeason !== undefined ? p.leftSeason + 1 : ""}`
                      : p.retiredReason ?? "Left college"}
                </span>
              )}
              {p.status !== "active" && lastTid !== undefined && (
                <span className="muted">
                  Last team: <TeamLink L={L} tid={lastTid} size={16} />
                </span>
              )}
              {p.status === "active" && <StatusBadges L={L} p={p} />}
              {p.injury && <span className="bad small">{p.injury.name}</span>}
            </div>
            <div className="row-wrap mt-8 small" style={{ gap: 18 }}>
              {p.recruitedBy && (
                <span className="muted">
                  {p.recruitedBy.kind === "portal" ? "Transferred" : "Recruited"} {p.recruitedBy.season}:{" "}
                  {p.recruitedBy.stars ? (
                    <>
                      <Stars n={p.recruitedBy.stars} /> {p.recruitedBy.rank ? `#${p.recruitedBy.rank}` : ""}
                    </>
                  ) : (
                    "walk-on / unranked"
                  )}
                </span>
              )}
              {p.transfers.map((tr) => (
                <span key={tr.season} className="muted">
                  Transfer {tr.season}: {teamMaybe(L, tr.from)?.name} → {teamMaybe(L, tr.to)?.name}
                </span>
              ))}
              <span className="muted">
                Career highs: {p.gameHigh.pts} pts · {p.gameHigh.reb} reb · {p.gameHigh.ast} ast
              </span>
            </div>
          </div>
        </div>
      </div>
      <Tabs
        tabs={[
          { key: "overview", label: "Overview" },
          { key: "stats", label: "Career Stats" },
          { key: "log", label: "Game Log" },
          { key: "ratings", label: "Ratings History" },
          ...(isUser ? [{ key: "instr" as const, label: "Instructions" }] : []),
        ]}
        value={tab}
        onChange={setTab}
      />
      {tab === "overview" && (
        <div className="grid g-main">
          <div className="col gap-16">
            <Card title="Ratings" sub={`Overall ${p.ovr} (${grade(p.ovr)}) · Potential ${grade(p.pot + p.potErr)}`}>
              <div className="grid g3" style={{ gap: 24 }}>
                {GROUPS.map((g) => (
                  <div key={g.name} className="col">
                    <div className="bold small muted" style={{ textTransform: "uppercase", letterSpacing: "0.05em" }}>
                      {g.name}
                    </div>
                    {g.keys.map((k) => (
                      <RatingRow key={k} k={k} v={p.r[k]} />
                    ))}
                  </div>
                ))}
              </div>
            </Card>
            <Card title="Career" flush>
              <StatsTable L={L} p={p} mode="pg" />
            </Card>
          </div>
          <div className="col gap-16">
            {cur && cur.g > 0 && (
              <Card title={`${seasonLabel(L.season)} Season`}>
                <div className="stat-row" style={{ margin: "-14px" }}>
                  {(
                    [
                      ["PTS", cur.pts],
                      ["REB", cur.orb + cur.drb],
                      ["AST", cur.ast],
                      ["MIN", cur.min],
                    ] as const
                  ).map(([k, v]) => (
                    <div key={k} className="stat">
                      <div className="label">{k}</div>
                      <div className="value">{f1(v / cur.g)}</div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
            <Card title="Awards & Honors">
              {p.awards.length ? (
                <div className="col gap-4">
                  {p.awards
                    .slice()
                    .reverse()
                    .map((a, i) => (
                      <div key={i} className="row">
                        <span className="trophy">🏆</span>
                        <span>{a.name}</span>
                        <span className="spacer" />
                        <span className="muted small">{seasonLabel(a.season)}</span>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="muted">None yet.</div>
              )}
            </Card>
            <Card title="Profile">
              <dl className="kv">
                <dt>Work ethic</dt>
                <dd>{p.workEthic >= 75 ? "Gym rat" : p.workEthic >= 55 ? "Hard worker" : p.workEthic >= 35 ? "Average" : "Needs motivation"}</dd>
                <dt>Loyalty</dt>
                <dd>{p.loyalty >= 70 ? "Very loyal" : p.loyalty >= 45 ? "Loyal" : "Open to moving"}</dd>
                {L.settings.nil && (
                  <>
                    <dt>NIL deal</dt>
                    <dd>{p.nilDeal ? `$${p.nilDeal}K / yr` : "None"}</dd>
                  </>
                )}
              </dl>
            </Card>
            {t && (
              <Card title="Team">
                <div className="row">
                  <Logo team={t} size={36} />
                  <div>
                    <Link to={`/l/${L.id}/team/${t.id}`} className="bold">
                      {t.name} {t.mascot}
                    </Link>
                    <div className="muted small">{L.conferences[t.cid].name}</div>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}
      {tab === "stats" && (
        <StatsTabs L={L} p={p} />
      )}
      {tab === "log" && (
        <div className="card">
          <GameLog L={L} p={p} />
        </div>
      )}
      {tab === "ratings" && (
        <div className="card">
          <div className="tbl-wrap">
            <table className="tbl">
              <thead>
                <tr>
                  <th>Season</th>
                  <th className="n">OVR</th>
                  <th className="n">POT</th>
                  {(Object.keys(RATING_LABELS) as RatingKey[]).map((k) => (
                    <th key={k} className="n" title={RATING_LABELS[k]}>
                      {k === "three" ? "3PT" : k.toUpperCase()}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[...p.hist, ...(p.status === "active" ? [{ season: -1, ovr: p.ovr, pot: p.pot, r: p.r }] : [])].map((h, i) => (
                  <tr key={i}>
                    <td>{h.season === -1 ? <b>Now</b> : `${seasonLabel(h.season)} (start)`}</td>
                    <td className="n">
                      <Grade v={h.ovr} letter={false} />
                    </td>
                    <td className="n">
                      <Grade v={h.pot + p.potErr} letter={false} />
                    </td>
                    {(Object.keys(RATING_LABELS) as RatingKey[]).map((k) => (
                      <td key={k} className="n">
                        <Rating v={h.r[k]} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {tab === "instr" && isUser && <Instructions p={p} />}
    </div>
  );
}

function StatsTabs({ L, p }: { L: League; p: Player }) {
  const [mode, setMode] = useState<"pg" | "tot">("pg");
  return (
    <div className="card">
      <div className="card-h">
        <h2>Career Statistics</h2>
        <div className="spacer" />
        <div className="seg">
          <button className={mode === "pg" ? "on" : ""} onClick={() => setMode("pg")}>
            Per game
          </button>
          <button className={mode === "tot" ? "on" : ""} onClick={() => setMode("tot")}>
            Totals
          </button>
        </div>
      </div>
      <StatsTable L={L} p={p} mode={mode} />
    </div>
  );
}
