import { useNavigate } from "react-router-dom";
import type { League, Player } from "../../engine/types";
import { team } from "../../engine/core";
import { heightStr, classLabel } from "../../engine/ratings";
import { ACTIONS, actionMult, canAct, doAction, revealsOf, scoutedOvr, type ActionKey } from "../../engine/recruiting";
import { mutate } from "../store";
import { Grade, Logo, PlayerLink, Pos, Stars, Table, type Col } from "./common";
import { Icon } from "./Icons";
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
  return (
    <span className="qa" onClick={(e) => e.stopPropagation()}>
      {keys.map((k) => {
        const c = canAct(L, L.userTid, p, k);
        const done = !c.ok && (c.why === "Done this week" || c.why === "Already offered" || c.why === "Already visited" || c.why === "Fully scouted" || c.why?.startsWith("Available"));
        const tip = `${QUICK_LABEL[k] ?? ACTIONS[k].label} · ${ACTIONS[k].cost} pts${c.ok ? "" : ` · ${c.why}`}`;
        if (k === "offer")
          return (
            <button key={k} className={`btn btn-sm ${done ? "qa-done" : "btn-primary"}`} style={{ minWidth: 62 }} disabled={!c.ok} title={tip} onClick={() => mutate((LL) => void doAction(LL, LL.userTid, p, k))}>
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
          <button key={k} className={`qa-btn${done ? " done" : ""}`} disabled={!c.ok} title={tip} aria-label={ACTIONS[k].label} onClick={() => mutate((LL) => void doAction(LL, LL.userTid, p, k))}>
            <Icon name={done ? "check" : ACTION_ICON[k]} size={14} />
            <span>{ACTIONS[k].cost}</span>
          </button>
        );
      })}
    </span>
  );
}

/** Which of the three scouting looks you've done. */
export function ScoutDots({ p }: { p: Player }) {
  const done = revealsOf(p);
  const all = [
    ["film", "tv", "Film"],
    ["live", "eye", "Watched him play"],
    ["coach", "phone", "Talked to his coach"],
  ] as const;
  return (
    <span className="scout-ics" title={done.length ? `Scouted: ${all.filter(([k]) => done.includes(k)).map(([, , t]) => t).join(", ")}` : "Not scouted"}>
      {all.map(([k, ic]) => (
        <i key={k} className={done.includes(k) ? "on" : ""}>
          <Icon name={ic} size={11} />
        </i>
      ))}
    </span>
  );
}

/** A recruit's rating as far as you know it: "?" until you've scouted him. */
export function KnownOvr({ p }: { p: Player }) {
  const d = revealsOf(p);
  return d.includes("film") || d.includes("live") ? <Grade v={scoutedOvr(p)} /> : <span className="unknown">?</span>;
}
export function KnownPot({ p }: { p: Player }) {
  return revealsOf(p).includes("coach") ? <Grade v={p.pot} /> : <span className="unknown">?</span>;
}

export function RecruitTable({ L, rows, kind, limit = 50, showActions = false }: { L: League; rows: Player[]; kind: "hs" | "portal"; limit?: number; showActions?: boolean }) {
  const nav = useNavigate();
  const cols: Col<Player>[] = [
    { key: "rank", label: "Rk", render: (p) => <span className="faint bold">{p.recruit!.rank}</span>, sort: (p) => -p.recruit!.rank, num: true, defaultDesc: true },
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
    { key: "stars", label: "Stars", render: (p) => <Stars n={p.recruit!.stars} />, sort: (p) => p.recruit!.stars * 10000 - p.recruit!.rank, num: true },
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
      : [
          { key: "hs", label: "HS PPG", title: "High school points per game", render: (p: Player) => (p.recruit!.hs ? p.recruit!.hs.pts.toFixed(1) : "-"), sort: (p: Player) => p.recruit!.hs?.pts ?? 0, num: true },
          { key: "ovr", label: "OVR", title: "Scout him to find out", render: (p: Player) => <KnownOvr p={p} />, sort: (p: Player) => (revealsOf(p).some((x) => x !== "coach") ? scoutedOvr(p) : p.recruit!.stars * 10), num: true },
          { key: "pot", label: "POT", title: "Talk to his coach to find out", render: (p: Player) => <KnownPot p={p} />, sort: (p: Player) => (revealsOf(p).includes("coach") ? p.pot : p.recruit!.stars * 10), num: true },
          { key: "sc", label: "Scouted", title: "Film, watched him play, talked to his coach", render: (p: Player) => <ScoutDots p={p} />, sort: (p: Player) => revealsOf(p).length, center: true },
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
      label: "You",
      title: "Your rank in his interest list",
      render: (p) => {
        const r = interestRank(L, p);
        const offered = p.recruit!.offers.includes(L.userTid);
        return (
          <span className="row gap-4">
            {r ? <span className={`you-rank${r === 1 ? " first" : ""}`}>#{r}</span> : <span className="faint">-</span>}
            {offered && (
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
        );
      },
      sort: (p) => -(interestRank(L, p) ?? 999),
      num: true,
    },
    ...(showActions ? [{ key: "act", label: "", render: (p: Player) => (p.recruit!.stage !== "signed" ? <QuickActions L={L} p={p} /> : null) }] : []),
  ];
  return <Table cols={cols} rows={rows} rowKey={(p) => p.id} initialSort="stars" initialDesc limit={limit} onRowClick={(p) => nav(`/l/${L.id}/player/${p.id}`)} rowClass={(p) => (p.recruit!.committedTo === L.userTid ? "hl" : undefined)} />;
}
