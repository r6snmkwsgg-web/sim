import { useEffect, useRef, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useLeague } from "../store";
import { dayLabel, shortDayLabel, team } from "../../engine/core";
import type { BoxLine, BoxScore, Game, League, TeamBox } from "../../engine/types";
import { Card, Empty, Logo, Tabs } from "../components/common";
import { getBox } from "../db";
import { fetchSeason, pct100, useAsync, cls, f1, heroColors } from "../util";
import { Icon } from "../components/Icons";
import { curSeason } from "../../engine/play";
import { currentRank, rosterStrength } from "../../engine/rankings";
import { teamLeaders } from "../helpers";
import { grade } from "../../engine/ratings";

function totals(lines: BoxLine[]) {
  const t = { min: 0, pts: 0, fgm: 0, fga: 0, tpm: 0, tpa: 0, ftm: 0, fta: 0, orb: 0, drb: 0, ast: 0, stl: 0, blk: 0, tov: 0, pf: 0 };
  for (const l of lines) for (const k of Object.keys(t) as (keyof typeof t)[]) t[k] += l[k];
  return t;
}

function BoxTable({ L, tb, colors }: { L: League; tb: TeamBox; colors: [string, string] }) {
  const t = team(L, tb.tid);
  const starters = tb.lines.filter((l) => l.starter);
  const bench = tb.lines.filter((l) => !l.starter);
  const tot = totals(tb.lines);
  const row = (l: BoxLine) => (
    <tr key={l.pid}>
      <td>
        <Link to={`/l/${L.id}/player/${l.pid}`} className="bold">
          {l.name}
        </Link>{" "}
        <span className="faint small">{l.pos}</span>
      </td>
      <td className="n">{Math.round(l.min)}</td>
      <td className="n bold">{l.pts}</td>
      <td className="n">
        {l.fgm}-{l.fga}
      </td>
      <td className="n">
        {l.tpm}-{l.tpa}
      </td>
      <td className="n">
        {l.ftm}-{l.fta}
      </td>
      <td className="n">{l.orb}</td>
      <td className="n">{l.drb}</td>
      <td className="n">{l.orb + l.drb}</td>
      <td className="n">{l.ast}</td>
      <td className="n">{l.stl}</td>
      <td className="n">{l.blk}</td>
      <td className="n">{l.tov}</td>
      <td className="n">{l.pf}</td>
      <td className={cls("n", l.pm > 0 ? "good" : l.pm < 0 ? "bad" : "")}>{l.pm > 0 ? `+${l.pm}` : l.pm}</td>
    </tr>
  );
  const head = (label: string) => (
    <tr className="grp">
      <th>{label}</th>
      <th className="n">MIN</th>
      <th className="n">PTS</th>
      <th className="n">FG</th>
      <th className="n">3PT</th>
      <th className="n">FT</th>
      <th className="n">OREB</th>
      <th className="n">DREB</th>
      <th className="n">REB</th>
      <th className="n">AST</th>
      <th className="n">STL</th>
      <th className="n">BLK</th>
      <th className="n">TO</th>
      <th className="n">PF</th>
      <th className="n">+/-</th>
    </tr>
  );
  return (
    <div className="card">
      <div className="card-h box-h" style={{ ["--tc" as string]: heroColors(colors).h1 }}>
        <Logo team={t} size={34} />
        <h2 style={{ fontSize: 20 }}>{t.name}</h2>
        <span className="muted small">{t.mascot}</span>
        <span className="spacer" />
        <span className="box-pts">{tot.pts}</span>
      </div>
      <div className="tbl-wrap">
        <table className="tbl compact">
          <thead>{head("Starters")}</thead>
          <tbody>{starters.map(row)}</tbody>
          <thead>{head("Bench")}</thead>
          <tbody>{bench.map(row)}</tbody>
          <tfoot>
            <tr>
              <td>Totals</td>
              <td className="n">{Math.round(tot.min)}</td>
              <td className="n">{tot.pts}</td>
              <td className="n">
                {tot.fgm}-{tot.fga}
              </td>
              <td className="n">
                {tot.tpm}-{tot.tpa}
              </td>
              <td className="n">
                {tot.ftm}-{tot.fta}
              </td>
              <td className="n">{tot.orb}</td>
              <td className="n">{tot.drb}</td>
              <td className="n">{tot.orb + tot.drb}</td>
              <td className="n">{tot.ast}</td>
              <td className="n">{tot.stl}</td>
              <td className="n">{tot.blk}</td>
              <td className="n">{tot.tov}</td>
              <td className="n">{tot.pf}</td>
              <td />
            </tr>
            <tr>
              <td className="muted">Percentages</td>
              <td />
              <td />
              <td className="n muted">{pct100(tot.fgm, tot.fga)}%</td>
              <td className="n muted">{pct100(tot.tpm, tot.tpa)}%</td>
              <td className="n muted">{pct100(tot.ftm, tot.fta)}%</td>
              <td colSpan={9} />
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}

function TeamCompare({ L, box }: { L: League; box: BoxScore }) {
  const a = totals(box.home.lines);
  const b = totals(box.away.lines);
  const rows: [string, string, string, number, number][] = [
    ["Field goals", `${a.fgm}-${a.fga} (${pct100(a.fgm, a.fga)}%)`, `${b.fgm}-${b.fga} (${pct100(b.fgm, b.fga)}%)`, a.fgm / Math.max(1, a.fga), b.fgm / Math.max(1, b.fga)],
    ["Three-pointers", `${a.tpm}-${a.tpa} (${pct100(a.tpm, a.tpa)}%)`, `${b.tpm}-${b.tpa} (${pct100(b.tpm, b.tpa)}%)`, a.tpm / Math.max(1, a.tpa), b.tpm / Math.max(1, b.tpa)],
    ["Free throws", `${a.ftm}-${a.fta} (${pct100(a.ftm, a.fta)}%)`, `${b.ftm}-${b.fta} (${pct100(b.ftm, b.fta)}%)`, a.ftm, b.ftm],
    ["Rebounds", `${a.orb + a.drb} (${a.orb} off)`, `${b.orb + b.drb} (${b.orb} off)`, a.orb + a.drb, b.orb + b.drb],
    ["Assists", String(a.ast), String(b.ast), a.ast, b.ast],
    ["Turnovers", String(a.tov), String(b.tov), -a.tov, -b.tov],
    ["Steals", String(a.stl), String(b.stl), a.stl, b.stl],
    ["Blocks", String(a.blk), String(b.blk), a.blk, b.blk],
    ["Fouls", String(a.pf), String(b.pf), -a.pf, -b.pf],
    ["Points per possession", (box.home.pts / Math.max(1, box.poss)).toFixed(2), (box.away.pts / Math.max(1, box.poss)).toFixed(2), box.home.pts, box.away.pts],
  ];
  return (
    <Card title="Team Stats" sub={`${box.poss} possessions each`} flush>
      <table className="tbl">
        <thead>
          <tr>
            <th className="n" style={{ width: "35%" }}>
              {team(L, box.home.tid).short}
            </th>
            <th className="c" />
            <th style={{ width: "35%" }}>{team(L, box.away.tid).short}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([label, x, y, vx, vy]) => (
            <tr key={label}>
              <td className={cls("n", vx > vy && "bold")}>{x}</td>
              <td className="c muted small">{label}</td>
              <td className={cls(vy > vx && "bold")}>{y}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

function clock(t: number, per: number): string {
  const start = per <= 2 ? (per - 1) * 1200 : 2400 + (per - 3) * 300;
  const len = per <= 2 ? 1200 : 300;
  const rem = Math.max(0, len - (t - start));
  const m = Math.floor(rem / 60);
  const s = Math.floor(rem % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

function PlayByPlay({ L, box }: { L: League; box: BoxScore }) {
  const [per, setPer] = useState<number>(0);
  const [scoring, setScoring] = useState(false);
  if (!box.pbp) return <Empty>Play-by-play is only kept for your games and late-round NCAA Tournament games.</Empty>;
  const pers = [...new Set(box.pbp.map((e) => e.per))];
  let prev = { hs: 0, as: 0 };
  const rows = box.pbp.filter((e) => {
    const isScore = e.hs !== prev.hs || e.as !== prev.as;
    prev = { hs: e.hs, as: e.as };
    if (per && e.per !== per) return false;
    if (scoring && !isScore) return false;
    return !e.text.startsWith("Substitution") || !scoring;
  });
  const ht = team(L, box.home.tid);
  const at = team(L, box.away.tid);
  let last = { hs: 0, as: 0 };
  return (
    <div className="card">
      <div className="card-h">
        <div className="seg">
          <button className={per === 0 ? "on" : ""} onClick={() => setPer(0)}>
            All
          </button>
          {pers.map((p) => (
            <button key={p} className={per === p ? "on" : ""} onClick={() => setPer(p)}>
              {p === 1 ? "1st Half" : p === 2 ? "2nd Half" : `OT${p > 3 ? p - 2 : ""}`}
            </button>
          ))}
        </div>
        <label className="check small">
          <input type="checkbox" checked={scoring} onChange={(e) => setScoring(e.target.checked)} /> Scoring plays only
        </label>
      </div>
      <div className="pbp">
        {rows.map((e, i) => {
          const isScore = e.hs !== last.hs || e.as !== last.as;
          last = { hs: e.hs, as: e.as };
          const t = e.side === 0 ? ht : at;
          return (
            <div key={i} className={cls("pbp-row", isScore && "score")}>
              <span className="muted num">
                {e.per <= 2 ? `${e.per === 1 ? "1st" : "2nd"} ` : "OT "}
                {clock(e.t, e.per)}
              </span>
              <Logo team={t} size={20} />
              <span>{e.text}</span>
              <span className="num right">
                {e.hs}-{e.as}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}


function LiveReplay({ L, box, onDone }: { L: League; box: BoxScore; onDone: () => void }) {
  const ev = box.pbp ?? [];
  const [i, setI] = useState(0);
  const [speed, setSpeed] = useState(2);
  const [paused, setPaused] = useState(false);
  const feedRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (paused || i >= ev.length - 1) return;
    const delay = [0, 900, 450, 200, 70][speed];
    const t = setTimeout(() => setI((x) => Math.min(ev.length - 1, x + 1)), ev[i]?.text.startsWith("Substitution") ? delay / 3 : delay);
    return () => clearTimeout(t);
  }, [i, paused, speed, ev]);
  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = 0;
  }, [i]);
  if (!ev.length) return null;
  const e = ev[i];
  const ht = team(L, box.home.tid);
  const at = team(L, box.away.tid);
  const done = i >= ev.length - 1;
  const recent = ev.slice(Math.max(0, i - 14), i + 1).reverse();
  const perLabel = e.per === 1 ? "1st Half" : e.per === 2 ? "2nd Half" : `OT${e.per > 3 ? e.per - 2 : ""}`;
  return (
    <div className="card" style={{ overflow: "hidden" }}>
      <div className="scoreboard" style={{ ["--ca" as string]: heroColors(at.colors).h1, ["--ch" as string]: heroColors(ht.colors).h1, borderRadius: 0, border: "none", boxShadow: "none" }}>
        <div className="sb-main">
          <div className="sb-team">
            <Logo team={at} size={68} />
            <div>
              <div className="sb-name">{at.name}</div>
              <div className="sb-sub">{at.mascot}</div>
            </div>
          </div>
          <span className={cls("sb-score", done && e.as < e.hs && "lose")}>{e.as}</span>
          <div className="sb-mid">
            <span className="sb-clock">{done ? "FINAL" : clock(e.t, e.per)}</span>
            <span className="sb-per">{done ? (box.ot ? `${box.ot > 1 ? box.ot : ""}OT` : "") : perLabel}</span>
          </div>
          <span className={cls("sb-score", done && e.hs < e.as && "lose")}>{e.hs}</span>
          <div className="sb-team home">
            <Logo team={ht} size={68} />
            <div>
              <div className="sb-name">{ht.name}</div>
              <div className="sb-sub">{ht.mascot}</div>
            </div>
          </div>
        </div>
        <div className="sb-progress">
          <span style={{ width: `${(100 * i) / Math.max(1, ev.length - 1)}%` }} />
        </div>
      </div>
      <div className="card-h">
        <button className="btn btn-sm" onClick={() => setPaused(!paused)} disabled={done}>
          {paused ? "Resume" : "Pause"}
        </button>
        <div className="seg">
          {[1, 2, 3, 4].map((x) => (
            <button key={x} className={speed === x ? "on" : ""} onClick={() => setSpeed(x)}>
              {["", "1x", "2x", "4x", "Fast"][x]}
            </button>
          ))}
        </div>
        <div className="spacer" />
        <button className="btn btn-sm" onClick={() => setI(ev.length - 1)} disabled={done}>
          Skip to end
        </button>
        <button className="btn btn-sm btn-primary" onClick={onDone}>
          Box score
        </button>
      </div>
      <div ref={feedRef} className="pbp" style={{ maxHeight: 420 }}>
        {recent.map((x, k) => {
          const t = x.side === 0 ? ht : at;
          return (
            <div key={i - k} className="pbp-row" style={{ opacity: k === 0 ? 1 : Math.max(0.35, 1 - k * 0.05), fontWeight: k === 0 ? 650 : undefined }}>
              <span className="muted num">{clock(x.t, x.per)}</span>
              <Logo team={t} size={20} />
              <span>{x.text}</span>
              <span className="num right">
                {x.as}-{x.hs}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Preview({ L, g }: { L: League; g: Game }) {
  const ht = team(L, g.home);
  const at = team(L, g.away);
  const side = (tid: number) => {
    const t = team(L, tid);
    const s = curSeason(t);
    const p = L.power[tid];
    const ld = teamLeaders(L, tid);
    return (
      <Card title={t.name} sub={`${s.w}-${s.l} (${s.cw}-${s.cl}) · ${currentRank(L, tid) ? `#${currentRank(L, tid)}` : "Unranked"}`}>
        <dl className="kv">
          <dt>Power rating</dt>
          <dd>{p ? p.power.toFixed(1) : "-"}</dd>
          <dt>Offense / Defense</dt>
          <dd>{p ? `${p.off.toFixed(1)} / ${p.def.toFixed(1)}` : "-"}</dd>
          <dt>Roster strength</dt>
          <dd>{grade(rosterStrength(L, tid))}</dd>
          <dt>Style</dt>
          <dd className="muted">
            {["", "Grind", "Slow", "Normal", "Fast", "Run & Gun"][t.strategy.tempo]} tempo · {t.strategy.offense} offense · {t.strategy.defense === "man" ? "man-to-man" : t.strategy.defense === "zone" ? "2-3 zone" : "full-court press"}
          </dd>
          {ld.pts && (
            <>
              <dt>Leading scorer</dt>
              <dd>
                <Link to={`/l/${L.id}/player/${ld.pts.p.id}`}>
                  {ld.pts.p.first} {ld.pts.p.last}
                </Link>{" "}
                ({f1(ld.pts.s.pts / ld.pts.s.g)} ppg)
              </dd>
            </>
          )}
        </dl>
      </Card>
    );
  };
  return (
    <div className="grid g2">
      {side(at.id)}
      {side(ht.id)}
    </div>
  );
}

export function GamePage() {
  const L = useLeague();
  const { gid } = useParams();
  const id = Number(gid);
  const { data, loading } = useAsync(async () => {
    let g = L.games.find((x) => x.id === id);
    if (!g) {
      for (const h of L.history.slice().reverse()) {
        const a = await fetchSeason(L, h.season);
        g = a?.games.find((x) => x.id === id);
        if (g) break;
      }
    }
    const box = g?.played ? await getBox(L.id, id) : undefined;
    return { g, box };
  }, [id, L.id, L.games.length, L.day]);
  const [sp, setSp] = useSearchParams();
  const watching = sp.get("watch") === "1";
  const [tab, setTab] = useState<"box" | "team" | "pbp">("box");
  if (loading && !data) return <Empty>Loading…</Empty>;
  const g = data?.g;
  if (!g) return <Empty>Game not found.</Empty>;
  const ht = team(L, g.home);
  const at = team(L, g.away);
  const box = data?.box;
  const halves = box ? box.home.halves.map((_, i) => i) : [];
  return (
    <div className="col gap-16">
      <div className="scoreboard" style={{ ["--ca" as string]: heroColors(at.colors).h1, ["--ch" as string]: heroColors(ht.colors).h1, ...(watching && box?.pbp ? { display: "none" } : null) }}>
        <div className="sb-kicker">
          {dayLabel(g.season, g.day)} · {g.event ?? (g.type === "conf" ? "Conference game" : g.type === "nc" ? "Non-conference" : g.type.toUpperCase())} · {g.neutral ? "Neutral site" : `at ${ht.name}`}
        </div>
        <div className="sb-main">
          <Link to={`/l/${L.id}/team/${at.id}?season=${g.season}`} className="sb-team">
            <Logo team={at} size={80} />
            <div>
              <div className="sb-name">{at.name}</div>
              <div className="sb-sub">{at.mascot}</div>
            </div>
          </Link>
          <span className={cls("sb-score", g.played && g.as < g.hs && "lose")}>{g.played ? g.as : ""}</span>
          <div className="sb-mid">
            <span className="sb-clock">{g.played ? "FINAL" : "VS"}</span>
            <span className="sb-per">{g.played && g.ot ? `${g.ot > 1 ? g.ot : ""}OT` : g.played ? "" : shortDayLabel(g.season, g.day)}</span>
            {box && (
              <table className="sb-lines">
                <thead>
                  <tr>
                    <th />
                    {halves.map((i) => (
                      <th key={i}>{i === 0 ? "1" : i === 1 ? "2" : `OT${i > 2 ? i - 1 : ""}`}</th>
                    ))}
                    <th>T</th>
                  </tr>
                </thead>
                <tbody>
                  {[box.away, box.home].map((tb) => (
                    <tr key={tb.tid}>
                      <td>{team(L, tb.tid).abbrev}</td>
                      {tb.halves.map((h, i) => (
                        <td key={i}>{h}</td>
                      ))}
                      <td className="t">{tb.pts}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          <span className={cls("sb-score", g.played && g.hs < g.as && "lose")}>{g.played ? g.hs : ""}</span>
          <Link to={`/l/${L.id}/team/${ht.id}?season=${g.season}`} className="sb-team home">
            <Logo team={ht} size={80} />
            <div>
              <div className="sb-name">{ht.name}</div>
              <div className="sb-sub">{ht.mascot}</div>
            </div>
          </Link>
        </div>
      </div>
      {watching && box?.pbp ? (
        <LiveReplay L={L} box={box} onDone={() => setSp({})} />
      ) : !g.played ? (
        <Preview L={L} g={g} />
      ) : !box ? (
        <Empty>No box score was saved for this game (box scores for games between other teams can be turned off in Settings).</Empty>
      ) : (
        <>
          <div className="row">
            <Tabs
              tabs={[
                { key: "box", label: "Box Score" },
                { key: "team", label: "Team Stats" },
                { key: "pbp", label: "Play-by-Play" },
              ]}
              value={tab}
              onChange={setTab}
            />
            <div className="spacer" />
            {box.pbp && (
              <button className="btn btn-primary" onClick={() => setSp({ watch: "1" })}>
                <Icon name="play" size={12} /> Watch replay
              </button>
            )}
          </div>
          {tab === "box" && (
            <div className="col gap-16">
              <BoxTable L={L} tb={box.away} colors={at.colors} />
              <BoxTable L={L} tb={box.home} colors={ht.colors} />
            </div>
          )}
          {tab === "team" && <TeamCompare L={L} box={box} />}
          {tab === "pbp" && <PlayByPlay L={L} box={box} />}
        </>
      )}
    </div>
  );
}
