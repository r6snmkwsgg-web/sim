import { useState } from "react";
import { Link } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { playerName, roster, rostersDirty, team, addNews, seasonLabel } from "../../engine/core";
import { classLabel, heightStr, RATING_SHORT } from "../../engine/ratings";
import { commitsFor, likelyPro, openSpots } from "../../engine/recruiting";
import { transferRisk, archivePlayer } from "../../engine/offseason";
import type { League, Player, RatingKey } from "../../engine/types";
import { Card, Grade, heroStyle, Logo, Meter, PageHead, PlayerLink, Pos, Rating, Stars, Table, Tabs, Tile, type Col } from "../components/common";
import { Face } from "../components/Face";
import { Icon } from "../components/Icons";
import { availablePlayers } from "../../engine/play";
import { resolveRotation } from "../../engine/sim/rotation";
import { seasonStatsOf } from "../helpers";
import { f1, money } from "../util";
import { removePlayers } from "../../engine/core";

const KEYS: RatingKey[] = ["ins", "mid", "three", "ft", "hnd", "pas", "iq", "perD", "intD", "reb", "blk", "stl", "ath", "str", "end"];

export function canRedshirt(L: League, p: Player): boolean {
  if (L.phase !== "preseason") return false;
  if (p.usedRedshirt && !p.redshirt) return false;
  return p.eligUsed < 4;
}

export function canRelease(L: League): boolean {
  return L.phase === "preseason" || L.phase === "draft" || L.phase === "portal" || L.phase === "signing" || L.phase === "carousel" || L.phase === "seasonEnd";
}

export function releasePlayer(L: League, p: Player) {
  const t = team(L, L.userTid);
  p.status = "left";
  p.retiredReason = `Released by ${t.name}`;
  archivePlayer(L, p);
  removePlayers(L, new Set([p.id]));
  rostersDirty(L);
  if (t.rotation.minutes[p.id] !== undefined) delete t.rotation.minutes[p.id];
  t.rotation.starters = t.rotation.starters.filter((x) => x !== p.id);
  addNews(L, "team", `${playerName(p)} was released from the roster.`, { tid: t.id, user: true });
}

export function StatusBadges({ L, p }: { L: League; p: Player }) {
  const risk = p.tid === L.userTid ? transferRisk(L, p) : 0;
  return (
    <span className="row gap-4">
      {p.injury && (
        <span className="badge bad" title={p.injury.name}>
          Inj {p.injury.games}g
        </span>
      )}
      {p.redshirt && <span className="badge warn">Redshirt</span>}
      {likelyPro(p) && L.phase !== "draft" && L.phase !== "portal" && L.phase !== "signing" && <span className="badge accent">NBA prospect</span>}
      {risk >= 0.25 && <span className="badge bad">Transfer risk</span>}
      {risk >= 0.12 && risk < 0.25 && <span className="badge warn">Unhappy</span>}
    </span>
  );
}

const VIEW_KEY = "hd-roster-view";
type View = "cards" | "ratings" | "stats" | "status";

function topRatings(p: Player): [RatingKey, number][] {
  return KEYS.map((k) => [k, p.r[k]] as [RatingKey, number])
    .filter(([k]) => k !== "end" && k !== "str")
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);
}

function PlayerCard({ L, p, colors, starter }: { L: League; p: Player; colors: [string, string]; starter: boolean }) {
  const st = seasonStatsOf(p, L.season, p.tid ?? undefined);
  return (
    <Link to={`/l/${L.id}/player/${p.id}`} className={`pcard${p.redshirt ? " dim" : ""}`}>
      <div className="pcard-top" style={heroStyle(colors)}>
        <span className="pcard-num">{p.jersey}</span>
        <Face seed={p.faceSeed} race={p.race} colors={colors} size={92} ratio={1.08} frame={false} />
        <div className="pcard-grades">
          <div>
            <Grade v={p.ovr} />
            <small>OVR</small>
          </div>
          <div>
            <Grade v={p.pot + p.potErr} />
            <small>POT</small>
          </div>
        </div>
        {starter && <span className="pcard-starter">Starter</span>}
      </div>
      <div className="pcard-body">
        <div className="pcard-name ellipsis">
          {p.first} <b>{p.last}</b>
        </div>
        <div className="row small muted" style={{ gap: 6, marginTop: 3 }}>
          <Pos p={p.pos} />
          <span>{classLabel(p)}</span>
          <span>·</span>
          <span>{heightStr(p.hgt)}</span>
          <span>·</span>
          <span className="ellipsis">{p.archetype}</span>
        </div>
        {st && st.g > 0 ? (
          <div className="pcard-line">
            <div>
              <b>{f1(st.pts / st.g)}</b>
              <span>PTS</span>
            </div>
            <div>
              <b>{f1((st.orb + st.drb) / st.g)}</b>
              <span>REB</span>
            </div>
            <div>
              <b>{f1(st.ast / st.g)}</b>
              <span>AST</span>
            </div>
            <div>
              <b>{f1(st.min / st.g)}</b>
              <span>MIN</span>
            </div>
          </div>
        ) : (
          <div className="pcard-line">
            {topRatings(p).map(([k, v]) => (
              <div key={k}>
                <b>{Math.round(v)}</b>
                <span>{RATING_SHORT[k]}</span>
              </div>
            ))}
            <div>
              <b>{Math.round(p.r.ath)}</b>
              <span>ATH</span>
            </div>
          </div>
        )}
        <div style={{ minHeight: 20, marginTop: 8 }}>
          <StatusBadges L={L} p={p} />
        </div>
      </div>
    </Link>
  );
}

export function Roster() {
  const L = useLeague();
  const t = team(L, L.userTid);
  const [tab, setTabState] = useState<View>(() => {
    try {
      return (localStorage.getItem(VIEW_KEY) as View) || "cards";
    } catch {
      return "cards";
    }
  });
  const setTab = (v: View) => {
    setTabState(v);
    try {
      localStorage.setItem(VIEW_KEY, v);
    } catch {
      // ignore
    }
  };
  const ps = roster(L, t.id);
  const incoming = commitsFor(L, t.id);
  const nilUsed = ps.reduce((a, p) => a + p.nilDeal, 0);
  const starters = new Set(resolveRotation(availablePlayers(L, t.id), t.rotation).starters);
  const avgOvr = ps.length ? ps.slice().sort((a, b) => b.ovr - a.ovr).slice(0, 8).reduce((a, p) => a + p.ovr, 0) / Math.min(8, ps.length) : 0;
  const base: Col<Player>[] = [
    { key: "num", label: "#", render: (p) => <span className="faint bold">{p.jersey}</span>, sort: (p) => p.jersey, num: true, width: 34 },
    {
      key: "name",
      label: "Player",
      render: (p) => (
        <PlayerLink
          L={L}
          p={p}
          face
          size={32}
          colors={t.colors}
          meta={
            <span className="row" style={{ gap: 5 }}>
              {starters.has(p.id) && <span className="accent-ink bold">Starter</span>}
              <span>{p.archetype}</span>
              <StatusBadges L={L} p={p} />
            </span>
          }
        />
      ),
      sort: (p) => p.last,
    },
    { key: "pos", label: "Pos", render: (p) => <Pos p={p.pos} />, sort: (p) => "PG SG SF PF C".indexOf(p.pos) },
    { key: "cls", label: "Class", render: (p) => classLabel(p), sort: (p) => p.eligUsed * 2 + (p.redshirt ? 1 : 0) },
    { key: "ht", label: "Ht", render: (p) => heightStr(p.hgt), sort: (p) => p.hgt, num: true },
    { key: "ovr", label: "OVR", render: (p) => <Grade v={p.ovr} />, sort: (p) => p.ovr, num: true },
    { key: "pot", label: "POT", render: (p) => <Grade v={p.pot + p.potErr} />, sort: (p) => p.pot + p.potErr, num: true },
  ];
  const ratingCols: Col<Player>[] = KEYS.map((k) => ({ key: k, label: RATING_SHORT[k], render: (p: Player) => <Rating v={p.r[k]} />, sort: (p: Player) => p.r[k], num: true, center: true }));
  const statCols: Col<Player>[] = [
    { key: "g", label: "G", render: (p) => seasonStatsOf(p, L.season, t.id)?.g ?? 0, sort: (p) => seasonStatsOf(p, L.season, t.id)?.g ?? 0, num: true },
    ...(
      [
        ["min", "MIN", (s: NonNullable<ReturnType<typeof seasonStatsOf>>) => s.min],
        ["pts", "PTS", (s: NonNullable<ReturnType<typeof seasonStatsOf>>) => s.pts],
        ["reb", "REB", (s: NonNullable<ReturnType<typeof seasonStatsOf>>) => s.orb + s.drb],
        ["ast", "AST", (s: NonNullable<ReturnType<typeof seasonStatsOf>>) => s.ast],
        ["stl", "STL", (s: NonNullable<ReturnType<typeof seasonStatsOf>>) => s.stl],
        ["blk", "BLK", (s: NonNullable<ReturnType<typeof seasonStatsOf>>) => s.blk],
        ["tov", "TO", (s: NonNullable<ReturnType<typeof seasonStatsOf>>) => s.tov],
      ] as const
    ).map(([key, label, f]) => ({
      key,
      label,
      num: true,
      render: (p: Player) => {
        const s = seasonStatsOf(p, L.season, t.id);
        return s && s.g ? f1(f(s) / s.g) : "-";
      },
      sort: (p: Player) => {
        const s = seasonStatsOf(p, L.season, t.id);
        return s && s.g ? f(s) / s.g : -1;
      },
    })),
    {
      key: "fg",
      label: "FG%",
      num: true,
      render: (p) => {
        const s = seasonStatsOf(p, L.season, t.id);
        return s && s.fga ? (100 * (s.fgm / s.fga)).toFixed(1) : "-";
      },
      sort: (p) => {
        const s = seasonStatsOf(p, L.season, t.id);
        return s && s.fga ? s.fgm / s.fga : -1;
      },
    },
    {
      key: "tp",
      label: "3P%",
      num: true,
      render: (p) => {
        const s = seasonStatsOf(p, L.season, t.id);
        return s && s.tpa ? (100 * (s.tpm / s.tpa)).toFixed(1) : "-";
      },
      sort: (p) => {
        const s = seasonStatsOf(p, L.season, t.id);
        return s && s.tpa ? s.tpm / s.tpa : -1;
      },
    },
  ];
  const statusCols: Col<Player>[] = [
    { key: "arch", label: "Archetype", render: (p) => <span className="muted">{p.archetype}</span>, sort: (p) => p.archetype },
    { key: "home", label: "Hometown", render: (p) => `${p.city}, ${p.state}`, sort: (p) => p.state },
    { key: "rec", label: "Recruited", render: (p) => (p.recruitedBy ? p.recruitedBy.kind === "portal" ? <span className="badge">Transfer</span> : p.recruitedBy.stars ? <Stars n={p.recruitedBy.stars} /> : <span className="muted">Walk-on</span> : "-"), sort: (p) => p.recruitedBy?.stars ?? 0 },
    { key: "nil", label: "NIL", render: (p) => (p.nilDeal ? money(p.nilDeal) : "-"), sort: (p) => p.nilDeal, num: true },
    { key: "status", label: "Status", render: (p) => <StatusBadges L={L} p={p} /> },
    {
      key: "act",
      label: "",
      render: (p) => (
        <span className="row gap-4">
          {canRedshirt(L, p) && (
            <button className="btn btn-sm" onClick={() => mutate(() => void (p.redshirt = !p.redshirt))}>
              {p.redshirt ? "Remove redshirt" : "Redshirt"}
            </button>
          )}
          {canRelease(L) && (
            <button
              className="btn btn-sm btn-danger"
              onClick={() => {
                if (confirm(`Release ${playerName(p)}? He'll leave the program for good.`)) mutate((LL) => releasePlayer(LL, p));
              }}
            >
              Release
            </button>
          )}
        </span>
      ),
    },
  ];
  const cols = tab === "ratings" ? [...base, ...ratingCols] : tab === "stats" ? [...base, ...statCols] : [...base, ...statusCols];
  const sortedCards = ps.slice().sort((a, b) => Number(starters.has(b.id)) - Number(starters.has(a.id)) || b.ovr - a.ovr);
  return (
    <div>
      <PageHead
        logo={<Logo team={t} size={56} />}
        eyebrow={`${t.name} ${t.mascot} · ${seasonLabel(L.season)}`}
        title="Roster"
        right={
          <Link to={`/l/${L.id}/team/${t.id}`} className="btn">
            <Icon name="team" size={14} /> Team page
          </Link>
        }
      />
      <div className="tiles g5 mb-16" style={{ display: "grid" }}>
        <Tile label="Players" icon="roster" value={<>{ps.length}<small>/ {L.settings.rosterMax}</small></>} foot={`${ps.filter((p) => p.redshirt).length} redshirting`} />
        <Tile label="Top-8 average" icon="stats" value={<Grade v={avgOvr} />} foot={`${avgOvr.toFixed(1)} OVR`} />
        <Tile label="Open spots" icon="recruit" value={openSpots(L, t.id)} foot="Next season, after departures" />
        <Tile label="Incoming" icon="star" value={incoming.length} foot={incoming.length ? incoming.map((p) => `${p.recruit!.stars}★`).join(" ") : "No commitments yet"} />
        <Tile label="NIL" icon="money" value={L.settings.nil ? money(nilUsed) : "Off"} foot={L.settings.nil ? `of ${money(t.nilBudget)} budget` : "NIL is turned off"}>
          {L.settings.nil && (
            <div style={{ marginTop: 6 }}>
              <Meter value={(100 * nilUsed) / Math.max(1, t.nilBudget)} color="var(--accent-ink)" />
            </div>
          )}
        </Tile>
      </div>
      {L.phase === "preseason" && (
        <div className="callout mb-16 small">
          <Icon name="bolt" size={18} />
          <span>
            <b>Redshirts:</b> a redshirting player practices with the team but can't play this season, and keeps a year of eligibility. Each player can redshirt once. Use the Status tab.
          </span>
        </div>
      )}
      <Tabs
        tabs={[
          { key: "cards", label: "Cards" },
          { key: "ratings", label: "Ratings" },
          { key: "stats", label: "Season Stats" },
          { key: "status", label: "Status & Actions" },
        ]}
        value={tab}
        onChange={setTab}
      />
      {tab === "cards" ? (
        <div className="pcard-grid">
          {sortedCards.map((p) => (
            <PlayerCard key={p.id} L={L} p={p} colors={t.colors} starter={starters.has(p.id)} />
          ))}
        </div>
      ) : (
        <div className="card">
          <Table cols={cols} rows={ps} rowKey={(p) => p.id} initialSort="ovr" initialDesc rowClass={(p) => (p.redshirt ? "dim" : undefined)} />
        </div>
      )}
      {incoming.length > 0 && (
        <Card title="Incoming" sub="Committed and signed players joining next season" className="mt-16" flush>
          <Table
            cols={[
              { key: "name", label: "Player", render: (p: Player) => <PlayerLink L={L} p={p} face size={28} colors={t.colors} />, sort: (p: Player) => p.last },
              { key: "kind", label: "Type", render: (p: Player) => (p.recruit?.kind === "portal" ? <span className="badge">Transfer</span> : <span className="badge">Freshman</span>) },
              { key: "stars", label: "Stars", render: (p: Player) => <Stars n={p.recruit!.stars} />, sort: (p: Player) => p.recruit!.stars, num: true },
              { key: "rank", label: "Rank", render: (p: Player) => `#${p.recruit!.rank}`, sort: (p: Player) => -p.recruit!.rank, num: true },
              { key: "pos", label: "Pos", render: (p: Player) => <Pos p={p.pos} /> },
              { key: "ht", label: "Ht", render: (p: Player) => heightStr(p.hgt), num: true },
              { key: "stage", label: "Status", render: (p: Player) => (p.recruit!.stage === "signed" ? <span className="badge good">Signed</span> : <span className="badge warn">Verbal</span>) },
            ]}
            rows={incoming}
            rowKey={(p) => p.id}
            initialSort="stars"
          />
        </Card>
      )}
    </div>
  );
}
