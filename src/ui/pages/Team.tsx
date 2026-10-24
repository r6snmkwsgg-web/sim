import { Link, useParams, useSearchParams } from "react-router-dom";
import { useLeague } from "../store";
import { coach, roster, seasonLabel, team } from "../../engine/core";
import type { League, Player, PlayerSeasonStats, Team, TeamSeason } from "../../engine/types";
import { classLabel, grade, heightStr, prestigeStars, prestigeTier, CLASS_LABELS } from "../../engine/ratings";
import { currentRank, rosterStrength } from "../../engine/rankings";
import { Card, Empty, Grade, Logo, PlayerLink, SeasonSelect, Stars, Table, Tabs, type Col } from "../components/common";
import { ScheduleTable } from "./Schedule";
import { fetchPlayers, fetchSeason, f1, pct100, useAsync, textOn } from "../util";
import { TOTAL_STATS, CAREER_EXTRA } from "../../engine/records";
import { careerLine } from "../../engine/stats";

interface RosterRow {
  p: Player;
  s: PlayerSeasonStats | undefined;
}

function SeasonRoster({ L, t, season }: { L: League; t: Team; season: number }) {
  const ts = t.seasons.find((s) => s.season === season);
  const cur = season === L.season;
  const { data, loading } = useAsync(async () => {
    const ps = cur ? roster(L, t.id) : await fetchPlayers(L, ts?.roster ?? []);
    return ps.map((p) => ({ p, s: p.stats.find((x) => x.season === season && x.tid === t.id) }));
  }, [t.id, season, L.season, cur ? L.day : 0, cur ? L.players.length : 0]);
  if (loading && !data) return <Empty>Loading roster…</Empty>;
  const rows = data ?? [];
  const hist = (p: Player) => (cur ? p : p.hist.find((h) => h.season === season) ?? p);
  const pg = (r: RosterRow, f: (s: PlayerSeasonStats) => number) => (r.s && r.s.g ? f(r.s) / r.s.g : -1);
  const cols: Col<RosterRow>[] = [
    { key: "name", label: "Player", render: (r) => <PlayerLink L={L} p={r.p} face size={28} colors={t.colors} />, sort: (r) => r.p.last },
    { key: "pos", label: "Pos", render: (r) => r.p.pos },
    { key: "cls", label: "Class", render: (r) => (cur ? classLabel(r.p) : r.s ? (r.s.rs ? "Redshirt" : CLASS_LABELS[Math.min(5, r.s.year)]) : "-"), sort: (r) => r.s?.year ?? r.p.eligUsed },
    { key: "ht", label: "Ht", render: (r) => heightStr(r.p.hgt), sort: (r) => r.p.hgt, num: true },
    { key: "ovr", label: "OVR", render: (r) => <Grade v={hist(r.p).ovr} />, sort: (r) => hist(r.p).ovr, num: true },
    { key: "g", label: "G", render: (r) => r.s?.g ?? 0, sort: (r) => r.s?.g ?? 0, num: true },
    { key: "min", label: "MIN", render: (r) => (r.s?.g ? f1(r.s.min / r.s.g) : "-"), sort: (r) => pg(r, (s) => s.min), num: true },
    { key: "pts", label: "PTS", render: (r) => (r.s?.g ? <b>{f1(r.s.pts / r.s.g)}</b> : "-"), sort: (r) => pg(r, (s) => s.pts), num: true },
    { key: "reb", label: "REB", render: (r) => (r.s?.g ? f1((r.s.orb + r.s.drb) / r.s.g) : "-"), sort: (r) => pg(r, (s) => s.orb + s.drb), num: true },
    { key: "ast", label: "AST", render: (r) => (r.s?.g ? f1(r.s.ast / r.s.g) : "-"), sort: (r) => pg(r, (s) => s.ast), num: true },
    { key: "stl", label: "STL", render: (r) => (r.s?.g ? f1(r.s.stl / r.s.g) : "-"), sort: (r) => pg(r, (s) => s.stl), num: true },
    { key: "blk", label: "BLK", render: (r) => (r.s?.g ? f1(r.s.blk / r.s.g) : "-"), sort: (r) => pg(r, (s) => s.blk), num: true },
    { key: "fg", label: "FG%", render: (r) => (r.s ? pct100(r.s.fgm, r.s.fga) : "-"), sort: (r) => (r.s?.fga ? r.s.fgm / r.s.fga : -1), num: true },
    { key: "tp", label: "3P%", render: (r) => (r.s ? pct100(r.s.tpm, r.s.tpa) : "-"), sort: (r) => (r.s?.tpa ? r.s.tpm / r.s.tpa : -1), num: true },
    { key: "ft", label: "FT%", render: (r) => (r.s ? pct100(r.s.ftm, r.s.fta) : "-"), sort: (r) => (r.s?.fta ? r.s.ftm / r.s.fta : -1), num: true },
  ];
  return <Table cols={cols} rows={rows} rowKey={(r) => r.p.id} initialSort={rows.some((r) => r.s?.g) ? "pts" : "ovr"} empty="No roster recorded for this season." />;
}

function TeamTotals({ L, t, season }: { L: League; t: Team; season: number }) {
  const ts = t.seasons.find((s) => s.season === season);
  const cur = season === L.season;
  const { data } = useAsync(async () => {
    const ps = cur ? roster(L, t.id) : await fetchPlayers(L, ts?.roster ?? []);
    const lines = ps.map((p) => p.stats.find((x) => x.season === season && x.tid === t.id)).filter((x): x is PlayerSeasonStats => !!x);
    const tot = lines.reduce(
      (a, s) => {
        for (const k of ["fgm", "fga", "tpm", "tpa", "ftm", "fta", "orb", "drb", "ast", "stl", "blk", "tov", "pf"] as const) a[k] += s[k];
        return a;
      },
      { fgm: 0, fga: 0, tpm: 0, tpa: 0, ftm: 0, fta: 0, orb: 0, drb: 0, ast: 0, stl: 0, blk: 0, tov: 0, pf: 0 },
    );
    return tot;
  }, [t.id, season, cur ? L.day : 0]);
  if (!ts || !data) return null;
  const g = ts.w + ts.l || 1;
  const items: [string, string][] = [
    ["Points", f1(ts.pf / g)],
    ["Opp. points", f1(ts.pa / g)],
    ["Margin", f1((ts.pf - ts.pa) / g)],
    ["FG%", pct100(data.fgm, data.fga)],
    ["3P%", pct100(data.tpm, data.tpa)],
    ["FT%", pct100(data.ftm, data.fta)],
    ["Rebounds", f1((data.orb + data.drb) / g)],
    ["Assists", f1(data.ast / g)],
    ["Turnovers", f1(data.tov / g)],
    ["Steals", f1(data.stl / g)],
    ["Blocks", f1(data.blk / g)],
    ["3PA / game", f1(data.tpa / g)],
  ];
  return (
    <div className="grid g4">
      {items.map(([k, v]) => (
        <div key={k} className="card card-b">
          <div className="tiny muted bold" style={{ textTransform: "uppercase" }}>
            {k}
          </div>
          <div style={{ fontSize: 22, fontWeight: 750 }} className="num">
            {v}
          </div>
        </div>
      ))}
    </div>
  );
}

function resultText(s: TeamSeason): string {
  if (!s.post) return "";
  if (s.post.event === "ncaa") return `NCAA ${s.post.result} (${s.post.seed})`;
  return `${s.post.event.toUpperCase()} ${s.post.result}`;
}

function History({ L, t }: { L: League; t: Team }) {
  const seasons = t.seasons.slice().reverse();
  const done = t.seasons.filter((s) => s.season < L.season || L.phase === "seasonEnd" || L.phase === "carousel" || L.phase === "draft" || L.phase === "portal" || L.phase === "signing");
  const titles = done.filter((s) => s.post?.event === "ncaa" && s.post.result === "Champion");
  const ff = done.filter((s) => s.post?.event === "ncaa" && ["Champion", "Runner-up", "Final Four"].includes(s.post.result));
  const ncaa = done.filter((s) => s.post?.event === "ncaa");
  const confReg = done.filter((s) => s.confChamp);
  const confT = done.filter((s) => s.confTourney === "Champion");
  const wins = done.reduce((a, s) => a + s.w, 0);
  const losses = done.reduce((a, s) => a + s.l, 0);
  const prog = L.records.program[t.id] ?? {};
  const progS = L.records.programSeason[t.id] ?? {};
  const draftees = L.draftHistory.filter((d) => d.tid === t.id);
  // merge active players' totals into program career leaders
  const active = roster(L, t.id);
  const careerFor = (key: string) => {
    const st = [...TOTAL_STATS, ...CAREER_EXTRA].find((x) => x.key === key)!;
    const list = (prog[key] ?? []).slice();
    for (const p of active) {
      const c = careerLine(p, t.id);
      if (!c.g) continue;
      if ("avg" in st && st.avg && c.g < 50) continue;
      const v = Math.round(st.get(c) * 10) / 10;
      const i = list.findIndex((e) => e.pid === p.id);
      if (i >= 0) list.splice(i, 1);
      list.push({ pid: p.id, name: `${p.first} ${p.last}`, tid: t.id, season: L.season, value: v });
    }
    return list.sort((a, b) => b.value - a.value).slice(0, 5);
  };
  return (
    <div className="col gap-16">
      <div className="card">
        <div className="stat-row">
          <div className="stat">
            <div className="label">All-time record</div>
            <div className="value">
              {wins}-{losses}
            </div>
          </div>
          <div className="stat">
            <div className="label">National titles</div>
            <div className="value">{titles.length}</div>
          </div>
          <div className="stat">
            <div className="label">Final Fours</div>
            <div className="value">{ff.length}</div>
          </div>
          <div className="stat">
            <div className="label">NCAA bids</div>
            <div className="value">{ncaa.length}</div>
          </div>
          <div className="stat">
            <div className="label">Conf. titles</div>
            <div className="value">
              {confReg.length}
              <small>+{confT.length} tourney</small>
            </div>
          </div>
          <div className="stat">
            <div className="label">NBA draftees</div>
            <div className="value">{draftees.length}</div>
          </div>
        </div>
      </div>
      {(titles.length > 0 || ff.length > 0) && (
        <div className="row-wrap">
          {ff
            .slice()
            .reverse()
            .map((s) => (
              <div key={s.season} className="card card-b center" style={{ background: t.colors[0], color: textOn(t.colors[0]), minWidth: 120 }}>
                <div style={{ fontSize: 22 }}>{s.post!.result === "Champion" ? "🏆" : "🏀"}</div>
                <div className="bold">{s.post!.result === "Champion" ? "National Champions" : s.post!.result === "Runner-up" ? "National Runner-up" : "Final Four"}</div>
                <div className="small" style={{ opacity: 0.85 }}>
                  {seasonLabel(s.season)}
                </div>
              </div>
            ))}
        </div>
      )}
      <Card title="Season by season" flush>
        <div className="tbl-wrap">
          <table className="tbl">
            <thead>
              <tr>
                <th>Season</th>
                <th>Coach</th>
                <th className="n">W-L</th>
                <th className="n">Conf</th>
                <th className="n">Finish</th>
                <th>Conf. tourney</th>
                <th>Postseason</th>
                <th className="n">AP Pre</th>
                <th className="n">AP Final</th>
                <th className="n">Class</th>
                <th className="n">Prestige</th>
              </tr>
            </thead>
            <tbody>
              {seasons.map((s) => {
                const c = coach(L, s.coachId);
                return (
                  <tr key={s.season}>
                    <td>
                      <Link to={`/l/${L.id}/team/${t.id}?season=${s.season}`}>{seasonLabel(s.season)}</Link>
                    </td>
                    <td className="muted">{c ? `${c.first} ${c.last}` : "-"}</td>
                    <td className="n bold">
                      {s.w}-{s.l}
                    </td>
                    <td className="n">
                      {s.cw}-{s.cl}
                    </td>
                    <td className="n">
                      {s.confRank ?? "-"}
                      {s.confChamp ? " ★" : ""}
                    </td>
                    <td className="small">{s.confTourney ?? ""}</td>
                    <td className="small">{resultText(s)}</td>
                    <td className="n muted">{s.apPre ?? ""}</td>
                    <td className="n">{s.apFinal ?? ""}</td>
                    <td className="n muted">{s.recruitRank ? `#${s.recruitRank}` : ""}</td>
                    <td className="n">{s.prestige.toFixed(0)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
      <div className="grid g3">
        {(["pts", "reb", "ast", "ppg", "blk", "tpm"] as const).map((k) => {
          const st = TOTAL_STATS.find((x) => x.key === k)!;
          const list = careerFor(k);
          const sl = (progS[k] ?? []).slice(0, 3);
          return (
            <Card key={k} title={`Career ${st.label}`} flush>
              <table className="tbl compact">
                <tbody>
                  {list.map((e, i) => (
                    <tr key={`${e.pid}-${i}`}>
                      <td className="muted" style={{ width: 20 }}>
                        {i + 1}
                      </td>
                      <td>
                        <Link to={`/l/${L.id}/player/${e.pid}`}>{e.name}</Link>
                      </td>
                      <td className="n bold">{st.avg ? e.value.toFixed(1) : e.value}</td>
                    </tr>
                  ))}
                  {!list.length && (
                    <tr>
                      <td className="muted">No records yet</td>
                    </tr>
                  )}
                  {sl.length > 0 && (
                    <tr className="grp">
                      <th colSpan={3}>Single season</th>
                    </tr>
                  )}
                  {sl.map((e, i) => (
                    <tr key={`s${i}`}>
                      <td className="muted">{i + 1}</td>
                      <td>
                        <Link to={`/l/${L.id}/player/${e.pid}`}>{e.name}</Link> <span className="faint small">{seasonLabel(e.season)}</span>
                      </td>
                      <td className="n">{st.avg ? e.value.toFixed(1) : e.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          );
        })}
      </div>
      {draftees.length > 0 && (
        <Card title="NBA Draft picks" flush>
          <table className="tbl compact">
            <tbody>
              {draftees
                .slice()
                .reverse()
                .map((d) => (
                  <tr key={d.pid}>
                    <td className="muted">{d.season}</td>
                    <td>
                      <Link to={`/l/${L.id}/player/${d.pid}`}>{d.name}</Link>
                    </td>
                    <td>{d.pos}</td>
                    <td>
                      Round {d.round}, Pick {d.pick}
                    </td>
                    <td className="muted">{d.nbaTeam}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}

export function TeamPage() {
  const L = useLeague();
  const { tid } = useParams();
  const [sp, setSp] = useSearchParams();
  const t = team(L, Number(tid));
  const season = Number(sp.get("season") ?? L.season);
  const tab = (sp.get("tab") ?? "roster") as "roster" | "schedule" | "stats" | "history";
  const setTab = (k: string) => setSp({ tab: k, season: String(season) });
  const ts = t.seasons.find((s) => s.season === season) ?? t.seasons[t.seasons.length - 1];
  const c = coach(L, ts.coachId) ?? coach(L, t.coachId);
  const rank = season === L.season ? currentRank(L, t.id) : ts.apFinal;
  const { data: games } = useAsync(async () => (season === L.season ? L.games : (await fetchSeason(L, season))?.games ?? []), [season, L.season, L.games.length, L.day]);
  const fg = textOn(t.colors[0]);
  return (
    <div className="col gap-16">
      <div className="card" style={{ overflow: "hidden" }}>
        <div style={{ background: t.colors[0], color: fg, padding: "18px 20px", display: "flex", gap: 18, alignItems: "center" }}>
          <Logo team={t} size={76} />
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em" }}>
              {rank ? <span style={{ opacity: 0.8 }}>#{rank} </span> : null}
              {t.name} {t.mascot}
            </div>
            <div style={{ opacity: 0.85 }}>
              {L.conferences[t.cid].name} · {t.city}, {t.state} · Coach {c ? `${c.first} ${c.last}` : "vacant"}
              {t.id === L.userTid ? " (you)" : ""}
            </div>
          </div>
          <div className="right">
            <div style={{ fontSize: 28, fontWeight: 800 }}>
              {ts.w}-{ts.l}
            </div>
            <div style={{ opacity: 0.85 }}>
              {ts.cw}-{ts.cl} conf · {seasonLabel(season)}
            </div>
          </div>
        </div>
        <div className="stat-row">
          <div className="stat">
            <div className="label">Prestige</div>
            <div className="value" style={{ fontSize: 15, paddingTop: 4 }}>
              <Stars n={prestigeStars(t.prestige)} /> <span className="small muted">{prestigeTier(t.prestige)}</span>
            </div>
          </div>
          <div className="stat">
            <div className="label">Roster strength</div>
            <div className="value">{grade(rosterStrength(L, t.id))}</div>
          </div>
          <div className="stat">
            <div className="label">Power</div>
            <div className="value">{(season === L.season ? L.power[t.id]?.power : ts.power)?.toFixed(1) ?? "-"}</div>
          </div>
          <div className="stat">
            <div className="label">Facilities</div>
            <div className="value">{grade(t.facilities)}</div>
          </div>
          {L.settings.nil && (
            <div className="stat">
              <div className="label">NIL budget</div>
              <div className="value">${(t.nilBudget / 1000).toFixed(1)}M</div>
            </div>
          )}
          <div className="stat">
            <div className="label">Postseason</div>
            <div className="value" style={{ fontSize: 14, paddingTop: 6 }}>
              {resultText(ts) || "-"}
            </div>
          </div>
        </div>
      </div>
      <div className="row">
        <Tabs
          tabs={[
            { key: "roster", label: "Roster" },
            { key: "schedule", label: "Schedule" },
            { key: "stats", label: "Team Stats" },
            { key: "history", label: "Program History" },
          ]}
          value={tab}
          onChange={setTab}
        />
        <div className="spacer" />
        {tab !== "history" && <SeasonSelect L={L} value={season} onChange={(s) => setSp({ tab, season: String(s) })} />}
      </div>
      {tab === "roster" && (
        <div className="card">
          <SeasonRoster L={L} t={t} season={season} />
        </div>
      )}
      {tab === "schedule" && <div className="card">{games ? <ScheduleTable L={L} tid={t.id} games={games} season={season} /> : <Empty>Loading…</Empty>}</div>}
      {tab === "stats" && <TeamTotals L={L} t={t} season={season} />}
      {tab === "history" && <History L={L} t={t} />}
    </div>
  );
}
