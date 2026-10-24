import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { seasonLabel, teamMaybe, shortDayLabel } from "../../engine/core";
import { classLabel, grade, heightStr, RATING_LABELS, CLASS_LABELS } from "../../engine/ratings";
import type { BoxLine, Game, League, Player, PlayerSeasonStats, RatingKey, Tendencies } from "../../engine/types";
import { careerLine } from "../../engine/stats";
import { FOCUS_LABELS } from "../../engine/development";
import { Card, Empty, Gauge, Grade, heroStyle, Logo, Rating, RatingBar, Stars, Tabs, TeamLink } from "../components/common";
import { Icon } from "../components/Icons";
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
  const pot = p.pot + p.potErr;
  const statusLine =
    p.status === "drafted" && p.draft
      ? `Drafted ${p.draft.season} · Round ${p.draft.round}, pick ${p.draft.pick} (${p.draft.team})`
      : p.status === "graduated"
        ? `Graduated ${p.leftSeason !== undefined ? p.leftSeason + 1 : ""}`
        : p.retiredReason ?? "Left college";
  return (
    <div className="col gap-16">
      <div className="hero-banner" style={heroStyle(colors)}>
        <div className="hero-inner" style={{ paddingBottom: 0, alignItems: "stretch" }}>
          <div className="player-portrait">
            {p.status === "active" && <span className="portrait-num">{p.jersey}</span>}
            <Face seed={p.faceSeed} race={p.race} colors={colors} size={150} ratio={1.06} frame={false} />
          </div>
          <div style={{ flex: 1, minWidth: 0, paddingBottom: 22, display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <div className="hero-kicker">
              {p.status === "active" && t ? `#${p.jersey} · ` : ""}
              {p.pos} · {p.archetype}
              {p.status === "active" ? ` · ${classLabel(p)}` : ""}
            </div>
            <div className="hero-title" style={{ marginTop: 6 }}>
              <span style={{ fontSize: "0.62em", fontWeight: 700, opacity: 0.9 }}>{p.first}</span>
              <br />
              {p.last}
            </div>
            <div className="row-wrap" style={{ marginTop: 12, gap: 8 }}>
              <span className="chip-light">
                <b>{heightStr(p.hgt)}</b> · {p.wgt} lbs · {heightStr(p.wing)} wing
              </span>
              <span className="chip-light">
                <Icon name="pin" size={13} /> {p.city}, {p.state}
              </span>
              {p.status === "active" && t ? (
                <Link to={`/l/${L.id}/team/${t.id}`} className="chip-light">
                  <Logo team={t} size={16} /> {t.name}
                </Link>
              ) : (
                <span className="chip-light">{statusLine}</span>
              )}
              {p.status !== "active" && lastTid !== undefined && teamMaybe(L, lastTid) && (
                <Link to={`/l/${L.id}/team/${lastTid}`} className="chip-light">
                  <Logo team={teamMaybe(L, lastTid)} size={16} /> Last: {teamMaybe(L, lastTid)!.name}
                </Link>
              )}
              {p.recruitedBy && (
                <span className="chip-light">
                  {p.recruitedBy.kind === "portal" ? "Transfer" : `Class of ${p.recruitedBy.season}`}
                  {p.recruitedBy.stars ? (
                    <>
                      {" "}
                      <Stars n={p.recruitedBy.stars} />
                      {p.recruitedBy.rank ? ` #${p.recruitedBy.rank}` : ""}
                    </>
                  ) : (
                    " · walk-on"
                  )}
                </span>
              )}
            </div>
            {(p.status === "active" || p.injury) && (
              <div className="row-wrap" style={{ marginTop: 8, gap: 6 }}>
                {p.status === "active" && <StatusBadges L={L} p={p} />}
                {p.injury && <span className="badge bad">{p.injury.name}</span>}
              </div>
            )}
          </div>
          <div className="row" style={{ gap: 14, paddingBottom: 22 }}>
            <Gauge v={p.ovr} size={92} label="Overall" text={grade(p.ovr)} track="rgba(255,255,255,0.18)" />
            <Gauge v={pot} size={92} label="Potential" text={grade(pot)} track="rgba(255,255,255,0.18)" />
          </div>
        </div>
        <div className="hero-stats">
          {cur && cur.g > 0 ? (
            (
              [
                ["Points", f1(cur.pts / cur.g)],
                ["Rebounds", f1((cur.orb + cur.drb) / cur.g)],
                ["Assists", f1(cur.ast / cur.g)],
                ["Minutes", f1(cur.min / cur.g)],
                ["FG%", pct100(cur.fgm, cur.fga)],
                ["3P%", pct100(cur.tpm, cur.tpa)],
              ] as const
            ).map(([k, v]) => (
              <div key={k}>
                <div className="label">
                  {seasonLabel(L.season)} {k}
                </div>
                <div className="value">{v}</div>
              </div>
            ))
          ) : (
            <>
              <div>
                <div className="label">Career high pts</div>
                <div className="value">{p.gameHigh.pts}</div>
              </div>
              <div>
                <div className="label">Career high reb</div>
                <div className="value">{p.gameHigh.reb}</div>
              </div>
              <div>
                <div className="label">Career high ast</div>
                <div className="value">{p.gameHigh.ast}</div>
              </div>
              <div>
                <div className="label">Seasons played</div>
                <div className="value">{p.stats.filter((x) => x.g > 0).length}</div>
              </div>
            </>
          )}
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
            <Card title="Ratings" sub={`Overall ${p.ovr} · Potential ${grade(pot)}`}>
              <div className="grid g3" style={{ gap: 28 }}>
                {GROUPS.map((g) => (
                  <div key={g.name}>
                    <div className="section-title">{g.name}</div>
                    {g.keys.map((k) => (
                      <RatingBar key={k} name={RATING_LABELS[k]} v={p.r[k]} />
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
            <Card title="Awards & Honors">
              {p.awards.length ? (
                <div className="col gap-4">
                  {p.awards
                    .slice()
                    .reverse()
                    .map((a, i) => (
                      <div key={i} className="row award-row">
                        <span className="award-ic">
                          <Icon name="awards" size={14} />
                        </span>
                        <span className="bold">{a.name}</span>
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
