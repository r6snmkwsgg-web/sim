import { useNavigate } from "react-router-dom";
import type { League, Player } from "../../engine/types";
import { team } from "../../engine/core";
import { heightStr, classLabel } from "../../engine/ratings";
import { ACTIONS, actionMult, canAct, doAction, heatOf, openSpots, ratingsHidden, scoutedOvr, seenOf, talkedTo, type ActionKey } from "../../engine/recruiting";
import { distanceMiles } from "../../engine/rng";
import { hsNow, summerNow } from "../../engine/hsStats";
import { mutate } from "../store";
import { CircuitBadge, Grade, Logo, PlayerLink, Pos, ShotPct, shotSort, Stars, Table, type Col } from "./common";
import { Icon } from "./Icons";
import { confirmSpend } from "./Confirm";
import { chanceOf, stageText } from "../pages/RecruitProfile";

export function interestRank(L: League, p: Player): number | null {
  const r = p.recruit!;
  const mine = r.interest[L.userTid];
  if (!mine) return null;
  let rank = 1;
  for (const k in r.interest) if (r.interest[k] > mine) rank++;
  return rank;
}

export function leader(p: Player): number | null {
  const r = p.recruit!;
  let best: number | null = null;
  let bv = 0;
  for (const k in r.interest) {
    if (r.interest[k] > bv) {
      bv = r.interest[k];
      best = Number(k);
    }
  }
  return best;
}

export function StageCell({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  if ((r.stage === "committed" || r.stage === "signed") && r.committedTo !== null) {
    const t = team(L, r.committedTo);
    return (
      <span className="team-cell" title={stageText(L, p)}>
        <Logo team={t} size={20} />
        <span className={r.committedTo === L.userTid ? "good bold" : "bold"}>{t.short}</span>
        <span className={`badge ${r.stage === "signed" ? "good" : "warn"}`}>{r.stage === "signed" ? "Signed" : "Verbal"}</span>
      </span>
    );
  }
  if (r.stage === "unsigned") return <span className="badge">Unsigned</span>;
  return r.stage === "top5" ? <span className="badge gold">Top {r.top5.length}</span> : <span className="badge">Open</span>;
}

const ACTION_ICON: Record<ActionKey, string> = { scout: "eye", call: "phone", assistant: "whistle", coach: "coach", visit: "plane", offer: "check" };

const QUICK_LABEL: Partial<Record<ActionKey, string>> = { call: "Call", assistant: "Visit", coach: "Head coach visit", visit: "Official visit" };

export function QuickActions({ L, p, keys = ["call", "assistant", "offer"] }: { L: League; p: Player; keys?: ActionKey[] }) {
  const run = async (k: ActionKey) => {
    const name = `${p.first} ${p.last}`;
    const spots = openSpots(L, L.userTid);
    const ok = await confirmSpend(
      k === "offer"
        ? { title: `Offer ${name} a scholarship?`, body: `He can only commit to schools that offered him. You have ${spots} open spot${spots === 1 ? "" : "s"} next season.`, ok: "Offer scholarship" }
        : { title: `${QUICK_LABEL[k] ?? ACTIONS[k].label}: ${name}?`, body: ACTIONS[k].desc, cost: { pts: ACTIONS[k].cost, have: L.recruitPts }, ok: QUICK_LABEL[k] ?? ACTIONS[k].label },
    );
    if (ok) mutate((LL) => void doAction(LL, LL.userTid, p, k));
  };
  return (
    <span className="qa" onClick={(e) => e.stopPropagation()}>
      {keys.map((k) => {
        const c = canAct(L, L.userTid, p, k);
        const done = !c.ok && (c.why === "Done this week" || c.why === "Already offered" || c.why === "Already visited" || c.why === "Fully scouted" || c.why?.startsWith("Available"));
        const tip = `${QUICK_LABEL[k] ?? ACTIONS[k].label} · ${ACTIONS[k].cost} pts${c.ok ? "" : ` · ${c.why}`}`;
        if (k === "offer")
          return (
            <button key={k} className={`btn btn-sm ${done ? "qa-done" : "btn-primary"}`} style={{ minWidth: 62 }} disabled={!c.ok} title={tip} onClick={() => void run(k)}>
              {done ? (
                <>
                  <Icon name="check" size={12} /> Offered
                </>
              ) : (
                "Offer"
              )}
            </button>
          );
        return (
          <button key={k} className={`qa-btn${done ? " done" : ""}`} disabled={!c.ok} title={tip} aria-label={ACTIONS[k].label} onClick={() => void run(k)}>
            <Icon name={done ? "check" : ACTION_ICON[k]} size={14} />
            <span>{ACTIONS[k].cost}</span>
          </button>
        );
      })}
    </span>
  );
}

/** How much of him you've scouted: categories seen out of 7. */
export function ScoutDots({ p }: { p: Player }) {
  const n = seenOf(p).length;
  const t = talkedTo(p);
  return (
    <span className={`scout-count${n === 7 ? " full" : n ? " some" : ""}`} title={`${n} of 7 categories scouted${t ? ", talked to his coach" : ""}`}>
      {n}/7{t ? " +" : ""}
    </span>
  );
}

/** A recruit's rating as far as you know it: "?" until you've scouted most of him. */
export function KnownOvr({ p }: { p: Player }) {
  return seenOf(p).length >= 4 ? <Grade v={scoutedOvr(p)} /> : <span className="unknown">?</span>;
}
export function KnownPot({ p }: { p: Player }) {
  return talkedTo(p) ? <Grade v={p.pot} /> : <span className="unknown">?</span>;
}

/** Your heat with him as a short colored label. */
export function HeatTag({ L, p }: { L: League; p: Player }) {
  const h = heatOf(L, p, L.userTid);
  if (!(p.recruit!.interest[L.userTid] ?? 0)) return <span className="faint">-</span>;
  return <span className={`heat-label l${h.level}`}>{h.label}</span>;
}

const HS_STATS: ["pts" | "reb" | "ast" | "blk" | "stl", string, string][] = [
  ["pts", "PPG", "High school points per game"],
  ["reb", "RPG", "High school rebounds per game"],
  ["ast", "APG", "High school assists per game"],
  ["blk", "BPG", "High school blocks per game"],
  ["stl", "SPG", "High school steals per game"],
];

/** His stars, or "Unrated" until the rankings come out. */
export function RecruitStars({ L, p, lg }: { L: League; p: Player; lg?: boolean }) {
  return ratingsHidden(L, p) ? <span className="unrated">Unrated</span> : <Stars n={p.recruit!.stars} lg={lg} />;
}

/** The board's views of the high school class: the recruiting picture, his high school numbers, or how close he lives. */
export type BoardView = "overview" | "stats" | "summer" | "near";

export function RecruitTable({ L, rows, kind, limit = 50, showActions = false, view = "overview" }: { L: League; rows: Player[]; kind: "hs" | "portal"; limit?: number; showActions?: boolean; view?: BoardView }) {
  const nav = useNavigate();
  // until the rankings come out there's no rank to sort by: high school scoring is the best public guide
  const unrated = kind === "hs" && rows.length > 0 && ratingsHidden(L, rows[0]);
  const hsPts = (p: Player) => hsNow(L, p)?.pts ?? 0;
  const ut = team(L, L.userTid);
  const milesFrom = (p: Player) => Math.round(distanceMiles(p.lat, p.lon, ut.lat, ut.lon));
  const cols: Col<Player>[] = [
    {
      key: "rank",
      label: "Rk",
      render: (p) => <span className="faint bold">{unrated ? "-" : p.recruit!.rank}</span>,
      sort: (p) => (unrated ? hsPts(p) : -p.recruit!.rank),
      num: true,
      defaultDesc: true,
    },
    {
      key: "name",
      label: "Player",
      render: (p) => (
        <PlayerLink
          L={L}
          p={p}
          face
          size={30}
          colors={kind === "portal" && p.recruit!.fromTid !== undefined ? team(L, p.recruit!.fromTid).colors : undefined}
          meta={`${heightStr(p.hgt)} · ${kind === "portal" && p.recruit!.fromTid !== undefined ? `from ${team(L, p.recruit!.fromTid).short}` : `${p.city}, ${p.state}`}`}
        />
      ),
      sort: (p) => p.last,
    },
    { key: "pos", label: "Pos", render: (p) => <Pos p={p.pos} />, sort: (p) => "PG SG SF PF C".indexOf(p.pos) },
    { key: "stars", label: "Stars", render: (p) => <RecruitStars L={L} p={p} />, sort: (p) => (unrated ? hsPts(p) : p.recruit!.stars * 10000 - p.recruit!.rank), num: true },
    ...(kind === "portal"
      ? [
          { key: "cls", label: "Class", render: (p: Player) => classLabel(p), sort: (p: Player) => p.eligUsed },
          {
            key: "ppg",
            label: "PPG",
            num: true,
            render: (p: Player) => {
              const s = p.stats[p.stats.length - 1];
              return s && s.g ? (s.pts / s.g).toFixed(1) : "-";
            },
            sort: (p: Player) => {
              const s = p.stats[p.stats.length - 1];
              return s && s.g ? s.pts / s.g : 0;
            },
          },
          { key: "ovr", label: "OVR", render: (p: Player) => <Grade v={p.ovr} />, sort: (p: Player) => p.ovr, num: true },
          { key: "pot", label: "POT", render: (p: Player) => <Grade v={p.pot + p.potErr} />, sort: (p: Player) => p.pot, num: true },
        ]
      : view === "stats"
        ? [
            { key: "ht", label: "Ht", render: (p: Player) => heightStr(p.hgt), sort: (p: Player) => p.hgt, num: true },
            {
              key: "yr",
              label: "Season",
              title: "The season these numbers are from: his junior year until he's 6 games into his senior year",
              render: (p: Player) => {
                const h = hsNow(L, p);
                return h ? <span className="faint nowrap">{h.year === "Senior" ? "Sr" : "Jr"} · {h.g} G</span> : "-";
              },
              sort: (p: Player) => hsNow(L, p)?.g ?? 0,
              num: true,
            },
            ...HS_STATS.map(([k, label, title]) => ({
              key: k,
              label,
              title,
              render: (p: Player) => {
                const h = hsNow(L, p);
                return h ? h[k].toFixed(1) : "-";
              },
              sort: (p: Player) => hsNow(L, p)?.[k] ?? 0,
              num: true,
            })),
          ]
        : view === "summer"
          ? [
              { key: "ht", label: "Ht", render: (p: Player) => heightStr(p.hgt), sort: (p: Player) => p.hgt, num: true },
              {
                key: "circuit",
                label: "Circuit",
                title: "Where he played last summer (17U): the national circuit and youth national teams are the best competition, regional numbers come easier",
                render: (p: Player) => {
                  const s = summerNow(p);
                  return s ? <CircuitBadge c={s.circuit} /> : <span className="faint">None</span>;
                },
                sort: (p: Player) => {
                  const c = summerNow(p)?.circuit;
                  return c === "National" ? 3 : c === "International" ? 2 : c === "Regional" ? 1 : 0;
                },
              },
              { key: "sg", label: "G", render: (p: Player) => summerNow(p)?.g ?? "-", sort: (p: Player) => summerNow(p)?.g ?? 0, num: true },
              ...(["pts", "reb", "ast"] as const).map((k) => ({
                key: `s${k}`,
                label: { pts: "PPG", reb: "RPG", ast: "APG" }[k],
                render: (p: Player) => summerNow(p)?.[k].toFixed(1) ?? "-",
                sort: (p: Player) => summerNow(p)?.[k] ?? -1,
                num: true,
              })),
              ...([["fg", "FG%", "fgm", "fga"], ["tp", "3P%", "tpm", "tpa"], ["ft", "FT%", "ftm", "fta"]] as const).map(([key, label, m, a]) => ({
                key,
                label,
                render: (p: Player) => {
                  const s = summerNow(p);
                  return s ? <ShotPct m={s[m]} a={s[a]} g={s.g} when="all summer" /> : "-";
                },
                sort: (p: Player) => {
                  const s = summerNow(p);
                  return s ? shotSort(s[m], s[a], s.g) : -3;
                },
                num: true,
              })),
            ]
        : view === "near"
          ? [
              { key: "ht", label: "Ht", render: (p: Player) => heightStr(p.hgt), sort: (p: Player) => p.hgt, num: true },
              { key: "home", label: "Hometown", render: (p: Player) => <span className="nowrap">{p.city}, {p.state}</span>, sort: (p: Player) => `${p.state} ${p.city}` },
              {
                key: "dist",
                label: "Distance",
                title: `Miles from ${ut.name}`,
                render: (p: Player) => (
                  <span className="nowrap">
                    <b>{milesFrom(p).toLocaleString()}</b> mi{p.state === ut.state && <span className="badge" style={{ marginLeft: 6 }}>In state</span>}
                  </span>
                ),
                sort: (p: Player) => milesFrom(p),
                num: true,
              },
            ]
          : [
          { key: "hs", label: "HS PPG", title: "High school points per game this season (last season until he's 6 games into his senior year)", render: (p: Player) => hsNow(L, p)?.pts.toFixed(1) ?? "-", sort: (p: Player) => hsPts(p), num: true },
          { key: "ovr", label: "OVR", title: "Scout 4 of his 7 categories to estimate it", render: (p: Player) => <KnownOvr p={p} />, sort: (p: Player) => (seenOf(p).length >= 4 ? scoutedOvr(p) : unrated ? 0 : p.recruit!.stars * 10), num: true },
          { key: "pot", label: "POT", title: "Talk to his coach to find out", render: (p: Player) => <KnownPot p={p} />, sort: (p: Player) => (talkedTo(p) ? p.pot : unrated ? 0 : p.recruit!.stars * 10), num: true },
          { key: "sc", label: "Scouted", title: "Categories scouted out of 7 (+ = talked to his coach)", render: (p: Player) => <ScoutDots p={p} />, sort: (p: Player) => seenOf(p).length, center: true },
        ]),
    {
      key: "chance",
      label: "Chance",
      title: "How seriously he'd take your program",
      render: (p) => {
        const c = chanceOf(actionMult(L, team(L, L.userTid), p));
        return <span style={{ color: c.c, fontWeight: 700 }}>{c.t}</span>;
      },
      sort: (p) => actionMult(L, team(L, L.userTid), p),
      num: true,
    },
    { key: "status", label: "Status", render: (p) => <StageCell L={L} p={p} />, sort: (p) => ({ open: 0, top5: 1, committed: 2, signed: 3, unsigned: 4 })[p.recruit!.stage] },
    {
      key: "lead",
      label: "Leader",
      render: (p) => {
        const l = leader(p);
        return l !== null ? (
          <span className="team-cell">
            <Logo team={team(L, l)} size={20} />
            <span className={l === L.userTid ? "good bold" : "text-2"}>{team(L, l).short}</span>
          </span>
        ) : (
          <span className="faint">-</span>
        );
      },
    },
    {
      key: "you",
      label: "Your heat",
      title: "How close you are to landing him",
      render: (p) => (
        <span className="row gap-4">
          <HeatTag L={L} p={p} />
          {p.recruit!.offers.includes(L.userTid) && (
            <span className="you-ic" title="You offered">
              <Icon name="check" size={11} />
            </span>
          )}
          {L.board.includes(p.id) && (
            <span className="you-ic star" title="On your board">
              <Icon name="star" size={11} />
            </span>
          )}
        </span>
      ),
      sort: (p) => p.recruit!.interest[L.userTid] ?? 0,
      num: true,
    },
    ...(showActions ? [{ key: "act", label: "", render: (p: Player) => (p.recruit!.stage !== "signed" ? <QuickActions L={L} p={p} /> : null) }] : []),
  ];
  // the stats and status columns that only fit the overview
  const shown = view === "overview" ? cols : cols.filter((c) => !["status", "lead"].includes(c.key));
  const [initialSort, initialDesc] = view === "stats" ? ["pts", true] : view === "summer" ? ["spts", true] : view === "near" ? ["dist", false] : ["stars", true];
  return (
    <Table
      key={view}
      cols={shown}
      rows={rows}
      rowKey={(p) => p.id}
      initialSort={initialSort as string}
      initialDesc={initialDesc as boolean}
      limit={limit}
      onRowClick={(p) => nav(`/l/${L.id}/player/${p.id}`)}
      rowClass={(p) => (p.recruit!.committedTo === L.userTid ? "hl" : undefined)}
    />
  );
}
