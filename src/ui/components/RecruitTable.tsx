import { useNavigate } from "react-router-dom";
import type { League, Player } from "../../engine/types";
import { team } from "../../engine/core";
import { heightStr, classLabel } from "../../engine/ratings";
import { ACTIONS, canAct, doAction, scoutedOvr, scoutedPot, type ActionKey } from "../../engine/recruiting";
import { mutate } from "../store";
import { Grade, Logo, PlayerLink, Stars, Table, type Col } from "./common";
import { stageText } from "../pages/RecruitProfile";

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
        <span className={r.committedTo === L.userTid ? "good bold" : ""}>{t.short}</span>
        <span className={`badge ${r.stage === "signed" ? "good" : "warn"}`}>{r.stage === "signed" ? "Signed" : "Verbal"}</span>
      </span>
    );
  }
  if (r.stage === "unsigned") return <span className="muted">Unsigned</span>;
  return <span className={r.stage === "top5" ? "warn" : "muted"}>{r.stage === "top5" ? `Top ${r.top5.length}` : "Open"}</span>;
}

export function QuickActions({ L, p, keys = ["call", "assistant", "coach", "visit", "offer"] }: { L: League; p: Player; keys?: ActionKey[] }) {
  const short: Record<ActionKey, string> = { scout: "Scout", call: "Call", assistant: "Asst", coach: "HC", visit: "Visit", offer: "Offer" };
  return (
    <span className="row gap-4" onClick={(e) => e.stopPropagation()}>
      {keys.map((k) => {
        const c = canAct(L, L.userTid, p, k);
        const done = !c.ok && (c.why === "Done this week" || c.why === "Already offered" || c.why === "Already visited" || c.why === "Fully scouted" || c.why?.startsWith("Available"));
        return (
          <button
            key={k}
            className={`btn btn-sm ${done ? "" : "btn-primary"}`}
            style={{ minWidth: 44, padding: "0 7px", opacity: done ? 0.55 : undefined }}
            disabled={!c.ok}
            title={`${ACTIONS[k].label} · ${ACTIONS[k].cost} pts${c.ok ? "" : ` · ${c.why}`}`}
            onClick={() => mutate((LL) => void doAction(LL, LL.userTid, p, k))}
          >
            {done ? "✓ " : ""}
            {short[k]}
          </button>
        );
      })}
    </span>
  );
}

export function RecruitTable({ L, rows, kind, limit = 50, showActions = false }: { L: League; rows: Player[]; kind: "hs" | "portal"; limit?: number; showActions?: boolean }) {
  const nav = useNavigate();
  const cols: Col<Player>[] = [
    { key: "rank", label: "Rk", render: (p) => <span className="muted">{p.recruit!.rank}</span>, sort: (p) => -p.recruit!.rank, num: true, defaultDesc: true },
    {
      key: "name",
      label: "Player",
      render: (p) => (
        <span className="row" style={{ gap: 8 }}>
          <PlayerLink L={L} p={p} face size={28} />
          <span className="tiny muted" style={{ lineHeight: 1.2 }}>
            {heightStr(p.hgt)}
            <br />
            {kind === "portal" && p.recruit!.fromTid !== undefined ? `from ${team(L, p.recruit!.fromTid).short}` : `${p.city}, ${p.state}`}
          </span>
        </span>
      ),
      sort: (p) => p.last,
    },
    { key: "pos", label: "Pos", render: (p) => p.pos, sort: (p) => "PG SG SF PF C".indexOf(p.pos) },
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
          { key: "ovr", label: "OVR*", title: "Your scouted estimate", render: (p: Player) => <span title={`Scouting ${p.recruit!.scout}/3`}><Grade v={scoutedOvr(p)} /></span>, sort: (p: Player) => scoutedOvr(p), num: true },
          { key: "pot", label: "POT*", title: "Your scouted estimate", render: (p: Player) => <Grade v={scoutedPot(p)} />, sort: (p: Player) => scoutedPot(p), num: true },
          { key: "sc", label: "Sct", title: "Scouting level", render: (p: Player) => <span className="muted">{p.recruit!.scout}/3</span>, sort: (p: Player) => p.recruit!.scout, num: true },
        ]),
    { key: "status", label: "Status", render: (p) => <StageCell L={L} p={p} />, sort: (p) => ({ open: 0, top5: 1, committed: 2, signed: 3, unsigned: 4 })[p.recruit!.stage] },
    {
      key: "lead",
      label: "Leader",
      render: (p) => {
        const l = leader(p);
        return l !== null ? (
          <span className="team-cell">
            <Logo team={team(L, l)} size={18} />
            <span className={l === L.userTid ? "good bold" : "muted"}>{team(L, l).short}</span>
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
            {r ? <span className={r === 1 ? "good bold" : ""}>#{r}</span> : <span className="faint">-</span>}
            {offered && <span title="You offered">🎓</span>}
            {L.board.includes(p.id) && <span title="On your board">★</span>}
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
