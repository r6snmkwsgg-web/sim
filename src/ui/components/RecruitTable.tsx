import { useNavigate } from "react-router-dom";
import type { League, Player } from "../../engine/types";
import { team } from "../../engine/core";
import { heightStr, classLabel } from "../../engine/ratings";
import { ACTIONS, canAct, doAction, scoutedOvr, scoutedPot, type ActionKey } from "../../engine/recruiting";
import { mutate } from "../store";
import { Grade, Logo, PlayerLink, Pos, Stars, Table, type Col } from "./common";
import { Icon } from "./Icons";
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
        <span className={r.committedTo === L.userTid ? "good bold" : "bold"}>{t.short}</span>
        <span className={`badge ${r.stage === "signed" ? "good" : "warn"}`}>{r.stage === "signed" ? "Signed" : "Verbal"}</span>
      </span>
    );
  }
  if (r.stage === "unsigned") return <span className="badge">Unsigned</span>;
  return r.stage === "top5" ? <span className="badge gold">Top {r.top5.length}</span> : <span className="badge">Open</span>;
}

const ACTION_ICON: Record<ActionKey, string> = { scout: "eye", call: "phone", assistant: "whistle", coach: "coach", visit: "plane", offer: "check" };

export function QuickActions({ L, p, keys = ["call", "assistant", "coach", "visit", "offer"] }: { L: League; p: Player; keys?: ActionKey[] }) {
  return (
    <span className="qa" onClick={(e) => e.stopPropagation()}>
      {keys.map((k) => {
        const c = canAct(L, L.userTid, p, k);
        const done = !c.ok && (c.why === "Done this week" || c.why === "Already offered" || c.why === "Already visited" || c.why === "Fully scouted" || c.why?.startsWith("Available"));
        const tip = `${ACTIONS[k].label} · ${ACTIONS[k].cost} pts${c.ok ? "" : ` · ${c.why}`}`;
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

export function ScoutDots({ n }: { n: number }) {
  return (
    <span className="dots3" title={`Scouting ${n}/3`}>
      {[0, 1, 2].map((i) => (
        <i key={i} className={i < n ? "on" : ""} />
      ))}
    </span>
  );
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
          { key: "ovr", label: "OVR*", title: "Your scouted estimate", render: (p: Player) => <span title={`Scouting ${p.recruit!.scout}/3`}><Grade v={scoutedOvr(p)} /></span>, sort: (p: Player) => scoutedOvr(p), num: true },
          { key: "pot", label: "POT*", title: "Your scouted estimate", render: (p: Player) => <Grade v={scoutedPot(p)} />, sort: (p: Player) => scoutedPot(p), num: true },
          { key: "sc", label: "Scout", title: "Scouting level", render: (p: Player) => <ScoutDots n={p.recruit!.scout} />, sort: (p: Player) => p.recruit!.scout, center: true },
        ]),
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
