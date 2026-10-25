import { useState } from "react";
import { Link } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { seasonLabel, team, teamMaybe } from "../../engine/core";
import { classLabel, heightStr, RATING_LABELS } from "../../engine/ratings";
import { distanceMiles } from "../../engine/rng";
import { regionOf } from "../../engine/data/cities";
import {
  ACTIONS, actionMult, canAct, doAction, factorScores, fit, NIL_VALUE, nilCommitted, OFFICIAL_VISITS, openSpots, PREF_LABELS, pullOffer, reveal, REVEALS, revealsOf, scoutedOvr, setNilOffer, type ActionKey,
} from "../../engine/recruiting";
import type { League, Player, PrefKey, RevealKey } from "../../engine/types";
import { PREF_KEYS } from "../../engine/types";
import { Bar, Card, Grade, heroStyle, Logo, Stars } from "../components/common";
import { Face } from "../components/Face";
import { Icon } from "../components/Icons";
import { money } from "../util";

const IMPORTANCE = ["", "Doesn't care", "Minor", "Nice to have", "Important", "Must have"];
const ACTION_ICONS: Record<ActionKey, string> = { scout: "eye", call: "phone", assistant: "whistle", coach: "coach", visit: "plane", offer: "draft" };
const ACTION_TEXT: Record<ActionKey, { label: string; desc: string }> = {
  scout: { label: "Scout", desc: "" },
  call: { label: "Call", desc: "Small boost. Once a week." },
  assistant: { label: "Visit", desc: "An assistant visits. Solid boost. Once a week." },
  coach: { label: "Head coach visit", desc: "You go yourself. Big boost. Every 3 weeks." },
  visit: { label: "Official visit", desc: "Bring him to campus. Huge boost. Once." },
  offer: { label: "Offer scholarship", desc: "He can only commit to schools that offered." },
};
const REVEAL_ICONS: Record<RevealKey, string> = { film: "tv", live: "eye", coach: "phone" };

export function stageText(L: League, p: Player): string {
  const r = p.recruit!;
  if (r.stage === "signed") return `Signed with ${team(L, r.committedTo!).name}`;
  if (r.stage === "committed") return `Committed to ${team(L, r.committedTo!).name}`;
  if (r.stage === "top5") return `Top ${r.top5.length}`;
  if (r.stage === "unsigned") return "Unsigned";
  return "Open";
}

/** How seriously a recruit takes you: fit, plus stars against your program's level. */
export function chanceOf(mult: number): { t: string; long: string; c: string; rank: number } {
  if (mult >= 1.15) return { t: "Great", long: "Great fit: everything you do counts extra.", c: "var(--good)", rank: 4 };
  if (mult >= 0.8) return { t: "Good", long: "Good fit: he's listening.", c: "var(--gb)", rank: 3 };
  if (mult >= 0.45) return { t: "Tough", long: "Tough sell: your pitches only land about half as well.", c: "var(--gc)", rank: 2 };
  return { t: "Long shot", long: "Long shot: he barely notices programs like yours.", c: "var(--bad)", rank: 1 };
}

function fitWord(x: number): { t: string; c: string } {
  if (x >= 0.8) return { t: "Excellent", c: "var(--good)" };
  if (x >= 0.6) return { t: "Good", c: "var(--gb)" };
  if (x >= 0.4) return { t: "Fair", c: "var(--gc)" };
  if (x >= 0.2) return { t: "Poor", c: "var(--gd)" };
  return { t: "Bad", c: "var(--bad)" };
}

/** Who's recruiting him, and where you stand. */
function WhosAfterHim({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const list = Object.entries(r.interest)
    .map(([k, v]) => ({ tid: Number(k), v }))
    .filter((x) => x.v > 0.5)
    .sort((a, b) => b.v - a.v)
    .slice(0, 6);
  const max = Math.max(10, ...list.map((x) => x.v));
  const mine = list.findIndex((x) => x.tid === L.userTid);
  const lead = list[0] ? team(L, list[0].tid) : null;
  const sub =
    r.committedTo !== null
      ? stageText(L, p)
      : !list.length
        ? "Nobody has made a move yet"
        : mine === 0
          ? "You're leading!"
          : mine > 0
            ? `You're #${mine + 1}. ${lead!.name} leads.`
            : `${lead!.name} leads. You're not on his list yet.`;
  return (
    <Card title="Who's after him" sub={sub}>
      {list.length ? (
        <div className="col" style={{ gap: 6 }}>
          {list.map((x, i) => {
            const t = team(L, x.tid);
            const out = (r.stage === "top5" || r.stage === "committed") && !r.top5.includes(x.tid);
            return (
              <div key={x.tid} className={`int-row${x.tid === L.userTid ? " me" : ""}`} style={{ opacity: out ? 0.42 : 1 }}>
                <span className="faint bold" style={{ width: 16, textAlign: "right" }}>
                  {i + 1}
                </span>
                <Logo team={t} size={28} />
                <Link to={`/l/${L.id}/team/${t.id}`} style={{ width: 140 }} className="bold ellipsis">
                  {t.name}
                </Link>
                <div style={{ flex: 1 }}>
                  <Bar value={x.v} max={max} color={x.tid === L.userTid ? "var(--accent-ink)" : "color-mix(in srgb, var(--text) 35%, transparent)"} />
                </div>
                <span className="small muted" style={{ width: 92, textAlign: "right" }}>
                  {r.committedTo === x.tid ? "Committed" : r.visits.includes(x.tid) ? "Visited" : r.offers.includes(x.tid) ? "Offered" : ""}
                </span>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="muted small">Be the first: a call or a visit gets you on his list.</div>
      )}
    </Card>
  );
}

/** What he's looking for, and how your school stacks up. */
function WhatHeWants({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const ut = team(L, L.userTid);
  const f = factorScores(L, ut, p);
  const [all, setAll] = useState(false);
  const keys = PREF_KEYS.filter((k) => k !== "nil" || L.settings.nil)
    .slice()
    .sort((a, b) => r.prefs[b] - r.prefs[a]);
  const shown = all ? keys : keys.slice(0, 3);
  const overall = fit(L, ut, p);
  const mult = actionMult(L, ut, p);
  const miles = Math.round(distanceMiles(p.lat, p.lon, ut.lat, ut.lon));
  const hint = (k: PrefKey) => (k === "proximity" ? `${miles.toLocaleString()} miles from home` : "");
  return (
    <Card title="What he wants" sub={`${chanceOf(mult).long} (overall fit: ${fitWord(overall).t.toLowerCase()})`}>
      <div className="col" style={{ gap: 8 }}>
        {shown.map((k) => {
          const w = fitWord(f[k]);
          const ok = f[k] >= 0.6 ? "check" : f[k] >= 0.35 ? "trend" : "x";
          return (
            <div key={k} className="want-row">
              <span className="want-ic" style={{ color: w.c }}>
                <Icon name={ok} size={14} />
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="bold">{PREF_LABELS[k]}</div>
                <div className="tiny muted">
                  {IMPORTANCE[r.prefs[k]]}
                  {hint(k) ? ` · ${hint(k)}` : ""}
                </div>
              </div>
              <span style={{ color: w.c, fontWeight: 700 }}>{w.t}</span>
            </div>
          );
        })}
        <button className="btn btn-sm btn-ghost" style={{ alignSelf: "flex-start" }} onClick={() => setAll(!all)}>
          {all ? "Show less" : `Show all ${keys.length}`}
        </button>
      </div>
    </Card>
  );
}

const GROUPS: { k: RevealKey; title: string }[] = [
  { k: "film", title: "Skills" },
  { k: "live", title: "Body & defense" },
];

/** Blue Bloods-style scouting: three looks, each revealing part of him. */
function Scouting({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const portal = r.kind === "portal";
  const done = portal ? (["film", "live"] as RevealKey[]).concat(revealsOf(p).filter((x) => x === "coach")) : revealsOf(p);
  const [msg, setMsg] = useState("");
  const keys: RevealKey[] = portal ? ["coach"] : ["film", "live", "coach"];
  const val = (v: number) => Math.round(Math.max(1, Math.min(99, v)));
  return (
    <Card title="Scouting" sub={portal ? "He's played college ball, so his ratings are known. Talk to his coach to learn the rest." : "Spend a few points to find out what he really is. Stars only tell you so much."}>
      {r.stage !== "signed" && (
        <div className="reveal-grid">
          {keys.map((k) => {
            const def = REVEALS[k];
            const has = done.includes(k);
            const short = !has && L.recruitPts < def.cost;
            return (
              <button
                key={k}
                className={`reveal-opt${has ? " done" : ""}`}
                disabled={has || short}
                onClick={() =>
                  mutate((LL) => {
                    setMsg(reveal(LL, p, k).msg);
                  })
                }
              >
                <span className="row" style={{ gap: 6, justifyContent: "space-between" }}>
                  <span className="row" style={{ gap: 6 }}>
                    <Icon name={has ? "check" : REVEAL_ICONS[k]} size={15} />
                    <b>{def.label}</b>
                  </span>
                  {!has && <span className="prep-cost">{def.cost} pts</span>}
                </span>
                <span className="tiny muted">{def.reveals}</span>
              </button>
            );
          })}
        </div>
      )}
      {msg && <div className="small good mt-8">{msg}</div>}
      <div className="grid g2 mt-12" style={{ gap: 14 }}>
        {GROUPS.map((g) => (
          <div key={g.k}>
            <div className="section-title" style={{ marginBottom: 6 }}>
              {g.title}
            </div>
            {REVEALS[g.k].keys.map((k) => {
              const known = done.includes(g.k);
              const v = val(p.r[k]);
              return (
                <div key={k} className="rate-row">
                  <span className="muted">{RATING_LABELS[k]}</span>
                  {known ? (
                    <>
                      <div className="rate-bar">
                        <i style={{ width: `${v}%` }} />
                      </div>
                      <b className="num">{v}</b>
                    </>
                  ) : (
                    <span className="unknown">?</span>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>
      <div className="section-title mt-12" style={{ marginBottom: 6 }}>
        Character
      </div>
      <div className="row-wrap" style={{ gap: 16 }}>
        {[
          ["Work ethic", p.workEthic],
          ["Loyalty", p.loyalty],
          ["Potential", p.pot],
        ].map(([label, v]) => (
          <div key={label as string} className="row" style={{ gap: 8 }}>
            <span className="muted">{label}</span>
            {done.includes("coach") ? <Grade v={v as number} /> : <span className="unknown">?</span>}
          </div>
        ))}
      </div>
    </Card>
  );
}

function Actions({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const ut = team(L, L.userTid);
  const [msg, setMsg] = useState<string>("");
  const act = (a: ActionKey) =>
    mutate((LL) => {
      const res = doAction(LL, LL.userTid, p, a);
      setMsg(res.msg);
    });
  const spots = openSpots(L, ut.id);
  const nilLeft = ut.nilBudget - nilCommitted(L, ut.id) + (r.nil[L.userTid] ?? 0);
  const keys: ActionKey[] = ["call", "assistant", "coach", "visit", "offer"];
  const typical = NIL_VALUE[r.stars];
  const nilNow = r.nil[L.userTid] ?? 0;
  const nilOpts = [
    { label: "None", v: 0 },
    { label: "Fair", v: Math.round(typical / 5) * 5 },
    { label: "Big", v: Math.round((typical * 1.6) / 5) * 5 },
  ];
  return (
    <Card title="Recruit him">
      <div className="points-line">
        <Icon name="bolt" size={15} /> <b>{L.recruitPts}</b> of {L.recruitPtsMax} coaching points left this week
      </div>
      {r.stage === "signed" ? (
        <div className="muted">He has signed. Recruiting is over.</div>
      ) : (
        <div className="col" style={{ gap: 8 }}>
          {keys.map((a) => {
            const chk = canAct(L, L.userTid, p, a);
            const def = ACTIONS[a];
            const txt = ACTION_TEXT[a];
            const done = !chk.ok && (chk.why === "Done this week" || chk.why === "Already offered" || chk.why === "Already visited");
            return (
              <button key={a} className={`rec-act${a === "offer" ? " offer" : ""}${done ? " done" : ""}`} disabled={!chk.ok} title={chk.why} onClick={() => act(a)}>
                <span className="act-ic">
                  <Icon name={done ? "check" : ACTION_ICONS[a]} size={16} />
                </span>
                <span style={{ flex: 1, minWidth: 0, textAlign: "left" }}>
                  <b>{txt.label}</b>
                  <span className="tiny muted" style={{ display: "block" }}>
                    {chk.ok || done ? txt.desc : chk.why}
                    {a === "visit" ? ` ${OFFICIAL_VISITS - ut.officialVisitsUsed} left this year.` : ""}
                    {a === "offer" ? ` ${spots} open spot${spots === 1 ? "" : "s"}.` : ""}
                  </span>
                </span>
                <span className="prep-cost">{done ? "Done" : def.cost ? `${def.cost} pts` : "Free"}</span>
              </button>
            );
          })}
          {L.settings.nil && (
            <div className="nil-pick">
              <span className="bold">NIL deal</span>
              <div className="seg">
                {nilOpts.map((o) => (
                  <button key={o.label} className={nilNow === o.v || (o.v > 0 && nilNow > 0 && Math.abs(nilNow - o.v) < 5) ? "on" : ""} onClick={() => mutate((LL) => setMsg(setNilOffer(LL, LL.userTid, p, o.v).msg))}>
                    {o.label}
                    {o.v ? ` ${money(o.v)}` : ""}
                  </button>
                ))}
              </div>
              <span className="tiny muted">{money(Math.max(0, nilLeft))} left in your NIL budget. Bigger names care more about NIL.</span>
            </div>
          )}
          {r.offers.includes(L.userTid) && r.stage !== "committed" && (
            <button className="btn btn-sm btn-ghost btn-danger" style={{ alignSelf: "flex-start" }} onClick={() => mutate((LL) => pullOffer(LL, LL.userTid, p))}>
              Pull scholarship offer
            </button>
          )}
          {msg && <div className="small good">{msg}</div>}
        </div>
      )}
    </Card>
  );
}

function Timeline({ p }: { p: Player }) {
  const r = p.recruit!;
  return r.history.length ? (
    <div className="timeline">
      {r.history.slice(0, 8).map((h, i) => (
        <div key={i} className="tl-row">
          <span className="tl-wk">Wk {h.week}</span>
          <span className="tl-dot" />
          <span>{h.text}</span>
        </div>
      ))}
    </div>
  ) : (
    <div className="muted">Nothing yet.</div>
  );
}

export function RecruitProfile({ p }: { p: Player }) {
  const L = useLeague();
  const r = p.recruit!;
  const seen = revealsOf(p);
  const from = r.fromTid !== undefined ? teamMaybe(L, r.fromTid) : undefined;
  const committed = r.committedTo !== null ? team(L, r.committedTo) : undefined;
  const colors = (committed ?? from)?.colors ?? ["#273449", "#f2b631"];
  const onBoard = L.board.includes(p.id);
  const last = p.stats[p.stats.length - 1];
  const ir = (() => {
    const sorted = Object.entries(r.interest).sort((a, b) => b[1] - a[1]);
    const i = sorted.findIndex(([k]) => Number(k) === L.userTid);
    return i >= 0 ? i + 1 : null;
  })();
  return (
    <div className="col gap-16">
      <div className="hero-banner" style={heroStyle(colors as [string, string])}>
        <div className="hero-inner" style={{ paddingBottom: 0, alignItems: "stretch" }}>
          <div className="player-portrait">
            <Face seed={p.faceSeed} race={p.race} colors={colors as [string, string]} size={152} frame={false} />
          </div>
          <div style={{ flex: 1, minWidth: 0, paddingBottom: 22, display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <div className="hero-kicker">
              {r.kind === "portal" ? `Transfer portal · from ${from?.name ?? "?"}` : `Class of ${r.classSeason}`} · {p.pos} · {p.archetype}
            </div>
            <div className="hero-title" style={{ marginTop: 6 }}>
              <span style={{ fontSize: "0.62em", fontWeight: 700, opacity: 0.9 }}>{p.first}</span>
              <br />
              {p.last}
            </div>
            <div className="row" style={{ marginTop: 10, gap: 12 }}>
              <Stars n={r.stars} lg />
              <span className="bold">
                #{r.rank} overall · #{r.posRank} {p.pos}
              </span>
            </div>
            <div className="row-wrap" style={{ marginTop: 10, gap: 8 }}>
              <span className="chip-light">
                <b>{heightStr(p.hgt)}</b> · {p.wgt} lbs · {heightStr(p.wing)} wing
              </span>
              <span className="chip-light">
                <Icon name="pin" size={13} /> {p.city}, {p.state} · {regionOf(p.state)}
              </span>
              {r.kind === "portal" && (
                <span className="chip-light">
                  {classLabel(p)} · {4 - p.eligUsed} yr{4 - p.eligUsed === 1 ? "" : "s"} left
                </span>
              )}
            </div>
          </div>
          <div className="col" style={{ alignItems: "flex-end", justifyContent: "center", paddingBottom: 22, gap: 10 }}>
            <span className={`stage-pill ${r.stage}`}>
              {committed && <Logo team={committed} size={20} />}
              {stageText(L, p)}
            </span>
            <button
              className="btn btn-glass"
              onClick={() =>
                mutate((LL) => {
                  LL.board = onBoard ? LL.board.filter((x) => x !== p.id) : [...LL.board, p.id];
                })
              }
            >
              <Icon name="star" size={14} /> {onBoard ? "On your board" : "Add to board"}
            </button>
          </div>
        </div>
        <div className="hero-stats">
          {r.kind === "hs" && r.hs ? (
            <>
              <div>
                <div className="label">HS points</div>
                <div className="value">{r.hs.pts.toFixed(1)}</div>
              </div>
              <div>
                <div className="label">HS rebounds</div>
                <div className="value">{r.hs.reb.toFixed(1)}</div>
              </div>
              <div>
                <div className="label">HS assists</div>
                <div className="value">{r.hs.ast.toFixed(1)}</div>
              </div>
            </>
          ) : last ? (
            <>
              <div>
                <div className="label">{seasonLabel(last.season)} PTS</div>
                <div className="value">{last.g ? (last.pts / last.g).toFixed(1) : "-"}</div>
              </div>
              <div>
                <div className="label">REB</div>
                <div className="value">{last.g ? ((last.orb + last.drb) / last.g).toFixed(1) : "-"}</div>
              </div>
              <div>
                <div className="label">AST</div>
                <div className="value">{last.g ? (last.ast / last.g).toFixed(1) : "-"}</div>
              </div>
            </>
          ) : null}
          <div>
            <div className="label">Overall</div>
            <div className="value" style={{ paddingTop: 2 }}>
              {r.kind === "portal" ? <Grade v={p.ovr} /> : seen.includes("film") || seen.includes("live") ? <Grade v={scoutedOvr(p)} /> : <span className="unknown light">?</span>}
            </div>
          </div>
          <div>
            <div className="label">Potential</div>
            <div className="value" style={{ paddingTop: 2 }}>
              {seen.includes("coach") ? <Grade v={p.pot} /> : r.kind === "portal" ? <Grade v={p.pot + p.potErr} /> : <span className="unknown light">?</span>}
            </div>
          </div>
          <div>
            <div className="label">You're</div>
            <div className="value">{ir ? `#${ir}` : "-"}</div>
          </div>
        </div>
      </div>
      <div className="grid g-main" style={{ alignItems: "start" }}>
        <div className="col gap-16">
          <WhatHeWants L={L} p={p} />
          <Scouting L={L} p={p} />
          <WhosAfterHim L={L} p={p} />
        </div>
        <div className="col gap-16">
          <Actions L={L} p={p} />
          <Card title="Timeline">
            <Timeline p={p} />
          </Card>
        </div>
      </div>
    </div>
  );
}
