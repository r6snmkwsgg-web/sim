import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useLeague } from "../store";
import { team } from "../../engine/core";
import type { League, Poll } from "../../engine/types";
import { selectionScores } from "../../engine/rankings";
import { confStandings } from "../../engine/postseason";
import { curSeason } from "../../engine/play";
import { Card, Empty, PageHead, SeasonSelect, Table, Tabs, TeamLink, type Col } from "../components/common";
import { fetchSeason, useAsync } from "../util";

function PollView({ L, polls, season }: { L: League; polls: Poll[]; season: number }) {
  const [idx, setIdx] = useState<number>(polls.length - 1);
  const i = Math.min(Math.max(0, idx), polls.length - 1);
  const poll = polls[i];
  if (!poll) return <Empty>No polls yet.</Empty>;
  return (
    <Card
      title={`AP Top 25 · ${poll.label}`}
      flush
      right={
        <select className="select" value={i} onChange={(e) => setIdx(Number(e.target.value))}>
          {polls.map((p, j) => (
            <option key={j} value={j}>
              {p.label}
            </option>
          ))}
        </select>
      }
    >
      <table className="tbl">
        <thead>
          <tr>
            <th className="n">Rk</th>
            <th>Team</th>
            <th className="n">Record</th>
            <th className="n">Pts</th>
            <th className="n">Prev</th>
            <th className="n">Change</th>
          </tr>
        </thead>
        <tbody>
          {poll.ranks.map((r) => {
            const ch = r.prev ? r.prev - r.rank : null;
            return (
              <tr key={r.tid} className={r.tid === L.userTid ? "hl" : ""}>
                <td className="n bold">{r.rank}</td>
                <td>
                  <TeamLink L={L} tid={r.tid} season={season} />
                </td>
                <td className="n">
                  {r.w}-{r.l}
                </td>
                <td className="n muted">{Math.max(0, r.pts)}</td>
                <td className="n muted">{r.prev ?? "NR"}</td>
                <td className={`n ${ch && ch > 0 ? "good" : ch && ch < 0 ? "bad" : "muted"}`}>{ch === null ? "new" : ch > 0 ? `▲${ch}` : ch < 0 ? `▼${-ch}` : "-"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </Card>
  );
}

interface PRow {
  tid: number;
  power: number;
  off: number;
  def: number;
  sos: number;
  w: number;
  l: number;
}

function PowerView({ L, rows, season }: { L: League; rows: PRow[]; season: number }) {
  const sorted = rows.slice().sort((a, b) => b.power - a.power);
  const rank = new Map(sorted.map((r, i) => [r.tid, i + 1]));
  const cols: Col<PRow>[] = [
    { key: "rk", label: "Rk", render: (r) => <b>{rank.get(r.tid)}</b>, sort: (r) => -(rank.get(r.tid) ?? 999), num: true },
    { key: "team", label: "Team", render: (r) => <TeamLink L={L} tid={r.tid} season={season} />, sort: (r) => team(L, r.tid).name },
    { key: "conf", label: "Conf", render: (r) => <span className="muted">{L.conferences[team(L, r.tid).cid].short}</span>, sort: (r) => L.conferences[team(L, r.tid).cid].short },
    { key: "rec", label: "W-L", render: (r) => `${r.w}-${r.l}`, sort: (r) => r.w - r.l, num: true },
    { key: "power", label: "Power", title: "Opponent-adjusted scoring margin vs. an average team", render: (r) => <b>{r.power > 0 ? "+" : ""}{r.power.toFixed(1)}</b>, sort: (r) => r.power, num: true },
    { key: "off", label: "Adj. Off", render: (r) => r.off.toFixed(1), sort: (r) => r.off, num: true },
    { key: "def", label: "Adj. Def", render: (r) => r.def.toFixed(1), sort: (r) => -r.def, num: true },
    { key: "sos", label: "SOS", render: (r) => r.sos.toFixed(1), sort: (r) => r.sos, num: true },
  ];
  return (
    <Card flush>
      <Table cols={cols} rows={rows} rowKey={(r) => r.tid} initialSort="power" limit={50} rowClass={(r) => (r.tid === L.userTid ? "hl" : undefined)} />
    </Card>
  );
}

function Bracketology({ L }: { L: League }) {
  const data = useMemo(() => {
    const sel = selectionScores(L);
    const auto = L.conferences.map((c) => confStandings(L, c.id)[0]).filter((x) => x !== undefined);
    const autoSet = new Set(auto);
    const F = L.settings.bracketSize;
    const atLarge = L.teams
      .filter((t) => !autoSet.has(t.id))
      .sort((a, b) => sel.get(b.id)! - sel.get(a.id)!)
      .slice(0, F - auto.length)
      .map((t) => t.id);
    const field = [...auto, ...atLarge].sort((a, b) => sel.get(b)! - sel.get(a)!);
    const lastIn = atLarge.slice(-4);
    const firstOut = L.teams
      .filter((t) => !autoSet.has(t.id) && !atLarge.includes(t.id))
      .sort((a, b) => sel.get(b.id)! - sel.get(a.id)!)
      .slice(0, 6)
      .map((t) => t.id);
    return { field, autoSet, lastIn, firstOut, sel };
  }, [L, L.day]);
  const userIn = data.field.indexOf(L.userTid);
  return (
    <div className="grid g-main">
      <Card title="Projected NCAA Tournament field" sub="Conference leaders get the automatic bids in this projection" flush>
        <table className="tbl compact">
          <thead>
            <tr>
              <th className="n">Seed</th>
              <th>Team</th>
              <th>Conf</th>
              <th className="n">Record</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {data.field.map((tid, i) => {
              const s = curSeason(team(L, tid));
              return (
                <tr key={tid} className={tid === L.userTid ? "hl" : ""}>
                  <td className="n bold">{Math.min(16, Math.floor(i / 4) + 1)}</td>
                  <td>
                    <TeamLink L={L} tid={tid} size={18} />
                  </td>
                  <td className="muted">{L.conferences[team(L, tid).cid].short}</td>
                  <td className="n">
                    {s.w}-{s.l}
                  </td>
                  <td>{data.autoSet.has(tid) ? <span className="badge">Auto</span> : data.lastIn.includes(tid) ? <span className="badge warn">Last in</span> : null}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
      <div className="col gap-16">
        <Card title="Your outlook">
          {userIn >= 0 ? (
            <div>
              <div style={{ fontSize: 22, fontWeight: 800 }}>Projected {Math.min(16, Math.floor(userIn / 4) + 1)} seed</div>
              <div className="muted small">{data.autoSet.has(L.userTid) ? "Currently leading your conference (automatic bid)." : data.lastIn.includes(L.userTid) ? "On the bubble: among the last teams in." : "Comfortably in the field for now."}</div>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: 18, fontWeight: 700 }}>Outside the field</div>
              <div className="muted small">Win your conference tournament for an automatic bid, or add quality wins.</div>
            </div>
          )}
        </Card>
        <Card title="First four out" flush>
          <table className="tbl compact">
            <tbody>
              {data.firstOut.map((tid) => (
                <tr key={tid} className={tid === L.userTid ? "hl" : ""}>
                  <td>
                    <TeamLink L={L} tid={tid} size={18} />
                  </td>
                  <td className="n">
                    {curSeason(team(L, tid)).w}-{curSeason(team(L, tid)).l}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}

export function Rankings() {
  const L = useLeague();
  const [sp, setSp] = useSearchParams();
  const season = Number(sp.get("season") ?? L.season);
  const [tab, setTab] = useState<"ap" | "power" | "bracket">("ap");
  const { data } = useAsync(async () => {
    if (season === L.season) {
      return {
        polls: L.polls,
        power: L.teams.map((t) => ({ tid: t.id, ...(L.power[t.id] ?? { power: 0, off: 0, def: 0, sos: 0 }), w: curSeason(t).w, l: curSeason(t).l })),
      };
    }
    const a = await fetchSeason(L, season);
    return {
      polls: a?.polls ?? [],
      power: (a?.power ?? []).map((p) => {
        const s = team(L, p.tid).seasons.find((x) => x.season === season);
        return { ...p, w: s?.w ?? 0, l: s?.l ?? 0 };
      }),
    };
  }, [season, L.season, L.polls.length, L.day]);
  const regular = season === L.season && (L.phase === "regular" || L.phase === "confTourney");
  return (
    <div>
      <PageHead title="Rankings" right={<SeasonSelect L={L} value={season} onChange={(s) => setSp({ season: String(s) })} />} />
      <Tabs
        tabs={[
          { key: "ap", label: "AP Poll" },
          { key: "power", label: "Power Ratings" },
          ...(regular ? [{ key: "bracket" as const, label: "Bracketology" }] : []),
        ]}
        value={tab}
        onChange={setTab}
      />
      {tab === "ap" && data && <PollView key={season} L={L} polls={data.polls} season={season} />}
      {tab === "power" && data && <PowerView L={L} rows={data.power} season={season} />}
      {tab === "bracket" && regular && <Bracketology L={L} />}
    </div>
  );
}
