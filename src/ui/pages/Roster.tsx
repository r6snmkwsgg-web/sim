import { useState } from "react";
import { Link } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { playerName, roster, rostersDirty, team, addNews, seasonLabel } from "../../engine/core";
import { classLabel, heightStr, RATING_SHORT } from "../../engine/ratings";
import { commitsFor, likelyPro, openSpots } from "../../engine/recruiting";
import { transferRisk, archivePlayer } from "../../engine/offseason";
import type { League, Player, PlayerSeasonStats, RatingKey } from "../../engine/types";
import { Card, Grade, Logo, PageHead, PlayerLink, Pos, Rating, Stars, Table, Tabs, type Col } from "../components/common";
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
      {likelyPro(p) && L.phase !== "draft" && L.phase !== "portal" && L.phase !== "signing" && <span className="badge gold">NBA prospect</span>}
      {risk >= 0.25 && <span className="badge bad">Transfer risk</span>}
      {risk >= 0.12 && risk < 0.25 && <span className="badge warn">Unhappy</span>}
    </span>
  );
}

const VIEW_KEY = "hd-roster-view2";
type View = "overview" | "stats" | "ratings" | "manage";

const POS_ORDER = "PG SG SF PF C";
const CLASS_LONG: Record<string, string> = { FR: "Freshman", SO: "Sophomore", JR: "Junior", SR: "Senior", GR: "Grad", "RS FR": "RS Freshman", "RS SO": "RS Sophomore", "RS JR": "RS Junior", "RS SR": "RS Senior" };
const SKILL_WORDS: Partial<Record<RatingKey, string>> = {
  ins: "Post scoring",
  mid: "Mid-range",
  three: "Shooting",
  hnd: "Ball handling",
  pas: "Passing",
  iq: "Basketball IQ",
  perD: "Perimeter D",
  intD: "Interior D",
  stl: "Steals",
  blk: "Shot blocking",
  reb: "Rebounding",
  ath: "Athleticism",
  str: "Strength",
};

export function strengths(p: Player, n = 2): string[] {
  return (Object.keys(SKILL_WORDS) as RatingKey[])
    .sort((a, b) => p.r[b] - p.r[a])
    .slice(0, n)
    .map((k) => SKILL_WORDS[k]!);
}

/** The stat line worth showing: this season, else last season, else nothing. */
function lineFor(L: League, p: Player): { s: PlayerSeasonStats; label: string; current: boolean } | null {
  const cur = seasonStatsOf(p, L.season, p.tid ?? undefined);
  if (cur && cur.g > 0) return { s: cur, label: seasonLabel(L.season), current: true };
  const prev = p.stats.filter((x) => x.season === L.season - 1 && x.g > 0);
  if (prev.length) {
    const s = prev[prev.length - 1];
    const at = s.tid !== p.tid ? ` at ${team(L, s.tid).short}` : "";
    return { s, label: `Last season${at}`, current: false };
  }
  return null;
}

function StatTrio({ L, p }: { L: League; p: Player }) {
  const ln = lineFor(L, p);
  if (ln) {
    const s = ln.s;
    return (
      <div className="lu-stats-wrap">
        <div className="lu-stats">
          <div>
            <b>{f1(s.pts / s.g)}</b>
            <span className="lbl">PTS</span>
          </div>
          <div>
            <b>{f1((s.orb + s.drb) / s.g)}</b>
            <span className="lbl">REB</span>
          </div>
          <div>
            <b>{f1(s.ast / s.g)}</b>
            <span className="lbl">AST</span>
          </div>
        </div>
        {!ln.current && <div className="lu-cap">{ln.label}</div>}
      </div>
    );
  }
  const rb = p.recruitedBy;
  if (rb?.kind === "hs" && p.year <= 1 && rb.hs) {
    return (
      <div className="lu-stats-wrap">
        <div className="lu-stats">
          <div>
            <b>{rb.hs.pts.toFixed(1)}</b>
            <span className="lbl">PTS</span>
          </div>
          <div>
            <b>{rb.hs.reb.toFixed(1)}</b>
            <span className="lbl">REB</span>
          </div>
          <div>
            <b>{rb.hs.ast.toFixed(1)}</b>
            <span className="lbl">AST</span>
          </div>
        </div>
        <div className="lu-cap">In high school</div>
      </div>
    );
  }
  return (
    <div className="lu-stats-wrap">
      <div className="lu-tags">
        {strengths(p).map((x) => (
          <span key={x} className="tag">
            {x}
          </span>
        ))}
      </div>
      <div className="lu-cap">{rb?.kind === "hs" && p.year <= 1 && rb.stars ? "Incoming freshman" : "Strengths"}</div>
    </div>
  );
}

function LineupCard({ L, p, colors }: { L: League; p: Player; colors: [string, string] }) {
  const pot = p.pot + p.potErr;
  return (
    <Link to={`/l/${L.id}/player/${p.id}`} className={`lu-card${p.redshirt ? " dim" : ""}`} style={{ ["--tc" as string]: colors[0] }}>
      <div className="lu-top">
        <span className="lu-num">{p.jersey}</span>
        <span className="lu-pos">{p.pos}</span>
        <Face seed={p.faceSeed} race={p.race} colors={colors} size={112} ratio={1.32} frame={false} />
      </div>
      <div className="lu-body">
        <div className="lu-first">{p.first}</div>
        <div className="lu-last ellipsis">{p.last}</div>
        <div className="lu-meta">
          {CLASS_LONG[classLabel(p)] ?? classLabel(p)} · {heightStr(p.hgt)}
        </div>
        <StatTrio L={L} p={p} />
        <div className="lu-foot">
          <span className="ovr-line">
            OVR <Grade v={p.ovr} />
          </span>
          <span className="ovr-line">
            POT <Grade v={pot} />
          </span>
        </div>
        <div className="lu-badges">
          <StatusBadges L={L} p={p} />
        </div>
      </div>
    </Link>
  );
}

function BenchRow({ L, p, colors }: { L: League; p: Player; colors: [string, string] }) {
  const ln = lineFor(L, p);
  const s = ln?.s;
  const rb = p.recruitedBy;
  return (
    <Link to={`/l/${L.id}/player/${p.id}`} className={`bench-row${p.redshirt ? " dim" : ""}`}>
      <Face seed={p.faceSeed} race={p.race} colors={colors} size={44} />
      <div className="bench-name">
        <div className="ellipsis">
          <span className="faint num" style={{ marginRight: 6 }}>
            {p.jersey}
          </span>
          <b>
            {p.first} {p.last}
          </b>
        </div>
        <div className="row muted small" style={{ gap: 6 }}>
          <Pos p={p.pos} />
          <span>{CLASS_LONG[classLabel(p)] ?? classLabel(p)}</span>
          <span>·</span>
          <span>{heightStr(p.hgt)}</span>
          <span>·</span>
          <span className="ellipsis">{p.archetype}</span>
        </div>
      </div>
      <div className="bench-stats">
        {s ? (
          <>
            <div>
              <b>{f1(s.pts / s.g)}</b>
              <span className="lbl">PTS</span>
            </div>
            <div>
              <b>{f1((s.orb + s.drb) / s.g)}</b>
              <span className="lbl">REB</span>
            </div>
            <div>
              <b>{f1(s.ast / s.g)}</b>
              <span className="lbl">AST</span>
            </div>
            <div>
              <b>{f1(s.min / s.g)}</b>
              <span className="lbl">MIN</span>
            </div>
          </>
        ) : rb?.kind === "hs" && p.year <= 1 && rb.stars ? (
          <div className="bench-note">
            <Stars n={rb.stars} /> <span className="muted small">freshman</span>
          </div>
        ) : (
          <div className="bench-note">
            {strengths(p).map((x) => (
              <span key={x} className="tag">
                {x}
              </span>
            ))}
          </div>
        )}
      </div>
      <div className="bench-cap faint small">{ln && !ln.current ? ln.label : ""}</div>
      <div className="row" style={{ gap: 10, justifyContent: "flex-end" }}>
        <StatusBadges L={L} p={p} />
        <span className="ovr-line">
          OVR <Grade v={p.ovr} />
        </span>
      </div>
    </Link>
  );
}

export function Roster() {
  const L = useLeague();
  const t = team(L, L.userTid);
  const [tab, setTabState] = useState<View>(() => {
    try {
      return (localStorage.getItem(VIEW_KEY) as View) || "overview";
    } catch {
      return "overview";
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
  const starterIds = resolveRotation(availablePlayers(L, t.id), t.rotation).starters;
  const starters = new Set(starterIds);
  const lineup = ps.filter((p) => starters.has(p.id)).sort((a, b) => POS_ORDER.indexOf(a.pos) - POS_ORDER.indexOf(b.pos));
  const bench = ps
    .filter((p) => !starters.has(p.id))
    .sort((a, b) => Number(a.redshirt) - Number(b.redshirt) || (t.rotation.minutes[b.id] ?? 0) - (t.rotation.minutes[a.id] ?? 0) || b.ovr - a.ovr);
  const top8 = ps.slice().sort((a, b) => b.ovr - a.ovr).slice(0, 8);
  const avgOvr = top8.length ? top8.reduce((a, p) => a + p.ovr, 0) / top8.length : 0;
  const base: Col<Player>[] = [
    { key: "num", label: "#", render: (p) => <span className="faint bold">{p.jersey}</span>, sort: (p) => p.jersey, num: true, width: 34 },
    {
      key: "name",
      label: "Player",
      render: (p) => <PlayerLink L={L} p={p} face size={32} colors={t.colors} meta={`${p.pos} · ${classLabel(p)} · ${heightStr(p.hgt)}`} />,
      sort: (p) => p.last,
    },
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
  const cols = tab === "ratings" ? [...base, ...ratingCols] : tab === "stats" ? [...base.slice(0, 2), ...statCols, base[2]] : [...base.slice(0, 2), ...statusCols];
  return (
    <div>
      <PageHead
        logo={<Logo team={t} size={52} />}
        eyebrow={`${t.name} ${t.mascot} · ${seasonLabel(L.season)}`}
        title="Roster"
        right={
          <Link to={`/l/${L.id}/team/${t.id}`} className="btn">
            <Icon name="team" size={14} /> Team page
          </Link>
        }
      />
      <div className="summary-strip mb-16">
        <div>
          <span>Players</span>
          <b>
            {ps.length}
            <small>/{L.settings.rosterMax}</small>
          </b>
        </div>
        <div>
          <span>Team strength</span>
          <b>
            <Grade v={avgOvr} md />
          </b>
        </div>
        <div>
          <span>Open spots next year</span>
          <b>{openSpots(L, t.id)}</b>
        </div>
        <div>
          <span>Incoming</span>
          <b>{incoming.length}</b>
        </div>
        {L.settings.nil && (
          <div style={{ flex: 1.4 }}>
            <span>NIL spent</span>
            <b>
              {money(nilUsed)}
              <small> of {money(t.nilBudget)}</small>
            </b>
          </div>
        )}
      </div>
      <Tabs
        tabs={[
          { key: "overview", label: "Lineup" },
          { key: "stats", label: "Stats" },
          { key: "ratings", label: "Ratings" },
          { key: "manage", label: "Manage" },
        ]}
        value={tab}
        onChange={setTab}
      />
      {tab === "overview" ? (
        <div className="col gap-20">
          <div>
            <div className="row" style={{ marginBottom: 10 }}>
              <div className="section-title" style={{ margin: 0 }}>
                Starting five
              </div>
              <span className="spacer" />
              <Link to={`/l/${L.id}/rotation`} className="btn btn-sm btn-ghost">
                Change rotation
              </Link>
            </div>
            <div className="lineup">
              {lineup.map((p) => (
                <LineupCard key={p.id} L={L} p={p} colors={t.colors} />
              ))}
            </div>
          </div>
          <div>
            <div className="section-title">Bench</div>
            <div className="card">
              {bench.map((p) => (
                <BenchRow key={p.id} L={L} p={p} colors={t.colors} />
              ))}
            </div>
          </div>
          {L.phase === "preseason" && (
            <div className="callout small">
              <Icon name="bolt" size={18} />
              <span>
                Redshirt players who won't play this season (they keep a year of eligibility) from the <b>Manage</b> tab.
              </span>
            </div>
          )}
        </div>
      ) : (
        <div className="card">
          <Table cols={cols} rows={ps} rowKey={(p) => p.id} initialSort={tab === "stats" ? "pts" : "ovr"} initialDesc rowClass={(p) => (p.redshirt ? "dim" : undefined)} />
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
