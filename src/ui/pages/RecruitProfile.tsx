import { useState } from "react";
import { mutate, useLeague } from "../store";
import { seasonLabel, team, teamMaybe } from "../../engine/core";
import { classLabel, heightStr } from "../../engine/ratings";
import { distanceMiles } from "../../engine/rng";
import { regionOf } from "../../engine/data/cities";
import {
  ACTIONS, actionMult, canAct, CAT_KEYS, CATS, catValue, doAction, factorScores, fit, heatOf, HOT, hsCareer, NIL_VALUE, nilCommitted, OFFICIAL_VISITS, openSpots, PREF_LABELS, pullOffer, recruitingOpen,
  SCOUT_COST, scoutedOvr, scoutGame, seenOf, setNilOffer, talkedTo, talkToCoach, watchFilm, weeksToDecide, type ActionKey,
} from "../../engine/recruiting";
import type { CatKey, League, Player, PrefKey } from "../../engine/types";
import { PREF_KEYS } from "../../engine/types";
import { Card, Grade, heroStyle, Logo, Stars, Tabs } from "../components/common";
import { Face } from "../components/Face";
import { Icon } from "../components/Icons";
import { confirmSpend, pickAndConfirm } from "../components/Confirm";
import { inkOn, money } from "../util";

const IMPORTANCE = ["", "Doesn't care", "Minor", "Nice to have", "Important", "Must have"];
const ACTION_ICONS: Record<ActionKey, string> = { scout: "eye", call: "phone", assistant: "whistle", coach: "coach", visit: "plane", offer: "draft" };
const ACTION_TEXT: Record<ActionKey, { label: string; desc: string }> = {
  scout: { label: "Scout", desc: "" },
  call: { label: "Call", desc: "Small boost. Once a week." },
  assistant: { label: "Visit", desc: "An assistant visits. Solid boost. Once a week." },
  coach: { label: "Head coach visit", desc: "You go yourself. Big boost. Every 3 weeks." },
  visit: { label: "Official visit", desc: "Bring him to campus. Huge boost. Once, and only once he's Hot on you." },
  offer: { label: "Offer scholarship", desc: "He can only commit to schools that offered." },
};

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

/** A school's heat with a recruit: Cold, Warm, Hot, Ready to commit, in its colors. */
export function HeatMeter({ L, p, tid, showTeam = true, compact }: { L: League; p: Player; tid: number; showTeam?: boolean; compact?: boolean }) {
  const h = heatOf(L, p, tid);
  const t = team(L, tid);
  const dark = document.documentElement.dataset.theme !== "light";
  const fill = inkOn(t.colors[0], dark ? "#151c2a" : "#f7f8fb", 2.2);
  return (
    <div className={`heat${tid === L.userTid ? " me" : ""}`}>
      {showTeam && (
        <span className="heat-team">
          <Logo team={t} size={24} />
          <span className="ellipsis">{tid === L.userTid ? (compact ? "You" : `${t.short} (you)`) : compact ? t.short : t.name}</span>
        </span>
      )}
      <div className="heat-track">
        <i style={{ width: `${Math.max(3, h.v * 100)}%`, background: fill }} />
        <b style={{ left: "25%" }} />
        <b style={{ left: `${HOT * 100}%` }} />
      </div>
      <span className={`heat-label l${h.level}`}>{h.label}</span>
    </div>
  );
}

/** Who's recruiting him, and where you stand. */
function WhosAfterHim({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const list = Object.entries(r.interest)
    .map(([k, v]) => ({ tid: Number(k), v }))
    .filter((x) => x.v > 0.5)
    .sort((a, b) => b.v - a.v)
    .slice(0, 6);
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
        <div className="col" style={{ gap: 8 }}>
          {list.map((x) => {
            const out = (r.stage === "top5" || r.stage === "committed") && !r.top5.includes(x.tid);
            const notes = [r.committedTo === x.tid && "Committed", r.offers.includes(x.tid) && "Offered", r.visits.includes(x.tid) && "Official visit", L.settings.nil && (r.nil[x.tid] ?? 0) > 0 && "NIL offer"].filter(Boolean);
            return (
              <div key={x.tid} style={{ opacity: out ? 0.42 : 1 }}>
                <HeatMeter L={L} p={p} tid={x.tid} />
                {notes.length > 0 && <div className="tiny muted heat-notes">{notes.join(" · ")}</div>}
              </div>
            );
          })}
          <div className="tiny muted">
            {r.committedTo === null && (() => {
              const w = weeksToDecide(L, p);
              return w > 0 ? `He starts deciding in about ${w} week${w === 1 ? "" : "s"}. ` : "He's deciding now, and the longer he waits the less it takes. ";
            })()}
            Hot (halfway) opens an official visit. When he decides, he picks among schools that offered him and are Ready to commit, usually the one furthest ahead.
          </div>
        </div>
      ) : (
        <div className="muted small">{L.phase === "preseason" && r.kind === "hs" ? "Recruiting opens when the season tips off." : "Be the first: a call or a visit gets you on his list."}</div>
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

/** Everything that costs points: scouting him and recruiting him. Every spend asks first. */
function RecruitPanel({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const ut = team(L, L.userTid);
  const [msg, setMsg] = useState<{ ok: boolean; msg: string } | null>(null);
  const open = recruitingOpen(L, p);
  const seen = seenOf(p);
  const talked = talkedTo(p);
  const hs = r.kind === "hs";
  const name = `${p.first} ${p.last}`;
  const cost = (pts: number) => ({ pts, have: L.recruitPts });
  const spots = openSpots(L, ut.id);
  const act = async (a: ActionKey) => {
    const txt = ACTION_TEXT[a];
    const ok = await confirmSpend(
      a === "offer"
        ? { title: `Offer ${name} a scholarship?`, body: `He can only commit to schools that offered him. You have ${spots} open spot${spots === 1 ? "" : "s"} next season.`, ok: "Offer scholarship" }
        : { title: `${txt.label}: ${name}?`, body: txt.desc, cost: cost(ACTIONS[a].cost), ok: txt.label },
    );
    if (ok) mutate((LL) => setMsg(doAction(LL, LL.userTid, p, a)));
  };
  const nilLeft = ut.nilBudget - nilCommitted(L, ut.id) + (r.nil[L.userTid] ?? 0);
  const keys: ActionKey[] = ["call", "assistant", "coach", "visit", "offer"];
  const typical = NIL_VALUE[r.stars];
  const nilNow = r.nil[L.userTid] ?? 0;
  const nilOpts = [
    { label: "None", v: 0 },
    { label: "Fair", v: Math.round(typical / 5) * 5 },
    { label: "Big", v: Math.round((typical * 1.6) / 5) * 5 },
  ];
  const offerNil = async (o: { label: string; v: number }) => {
    const ok = await confirmSpend(
      o.v
        ? {
            title: "Offer this NIL deal?",
            body: (
              <>
                Offer <b>{name}</b> a <b>{money(o.v)} a year</b> NIL deal ({o.label.toLowerCase()}){nilNow ? `, replacing your ${money(nilNow)} offer` : ""}. It comes out of your NIL budget, which has {money(Math.max(0, nilLeft - nilNow))} left.
              </>
            ),
            ok: `Offer ${money(o.v)}`,
          }
        : { title: "Withdraw your NIL offer?", body: `Take back your ${money(nilNow)} a year NIL offer to ${name}?`, ok: "Withdraw", danger: true },
    );
    if (ok) mutate((LL) => setMsg(setNilOffer(LL, LL.userTid, p, o.v)));
  };
  const unseen = CAT_KEYS.filter((k) => !seen.includes(k));
  const film = async () => {
    if (await confirmSpend({ title: `Watch game film on ${name}?`, body: "Shows one rating category you haven't seen yet, picked at random.", cost: cost(SCOUT_COST.film), ok: "Watch film" }))
      mutate((LL) => setMsg(watchFilm(LL, p)));
  };
  const game = async () => {
    const k = await pickAndConfirm({
      title: `Scout one of ${p.first}'s games`,
      body: "Pick what you want to watch for. You'll see his grade in it.",
      choices: unseen.map((c) => ({ key: c, label: CATS[c].label, sub: CATS[c].desc })),
      cost: cost(SCOUT_COST.game),
      ok: "Scout the game",
    });
    if (k) mutate((LL) => setMsg(scoutGame(LL, p, k as CatKey)));
  };
  const coach = async () => {
    if (await confirmSpend({ title: `Talk to ${p.first}'s coach?`, body: "Learn his work ethic and how good he can become.", cost: cost(SCOUT_COST.coach), ok: "Make the call" }))
      mutate((LL) => setMsg(talkToCoach(LL, p)));
  };
  const pull = async () => {
    if (await confirmSpend({ title: `Pull your offer to ${name}?`, body: "He won't be able to commit to you unless you offer again.", ok: "Pull offer", danger: true }))
      mutate((LL) => pullOffer(LL, LL.userTid, p));
  };
  const scoutRow = (icon: string, label: string, desc: string, pts: number, onClick: () => void, disabled: boolean, done = false) => (
    <button className={`rec-act${done ? " done" : ""}`} disabled={disabled} onClick={onClick}>
      <span className="act-ic">
        <Icon name={done ? "check" : icon} size={16} />
      </span>
      <span style={{ flex: 1, minWidth: 0, textAlign: "left" }}>
        <b>{label}</b>
        <span className="tiny muted" style={{ display: "block" }}>
          {desc}
        </span>
      </span>
      <span className="prep-cost">{done ? "Done" : `${pts} pts`}</span>
    </button>
  );
  return (
    <div className="col gap-16">
      <div className="points-line" style={{ marginBottom: 0 }}>
        <Icon name="bolt" size={15} /> <b>{L.recruitPts}</b> of {L.recruitPtsMax} coaching points left this week
        {!open.ok && <span className="muted" style={{ marginLeft: "auto" }}>{open.why}</span>}
      </div>
      {hs && (
        <Card title="Scout him" sub={`${seen.length} of 7 categories scouted${talked ? " · talked to his coach" : ""}`}>
          <div className="col" style={{ gap: 8 }}>
            {scoutRow("tv", "Watch game film", unseen.length ? "Reveals one category you haven't seen, at random." : "You've seen everything.", SCOUT_COST.film, film, !open.ok || !unseen.length || L.recruitPts < SCOUT_COST.film)}
            {scoutRow("eye", "Scout a game", unseen.length ? "Go see him play and pick what to watch for." : "You've seen everything.", SCOUT_COST.game, game, !open.ok || !unseen.length || L.recruitPts < SCOUT_COST.game)}
            {scoutRow("phone", "Talk to his coach", "His work ethic and how good he can become.", SCOUT_COST.coach, coach, !open.ok || talked || L.recruitPts < SCOUT_COST.coach, talked)}
          </div>
        </Card>
      )}
      <Card title="Recruit him">
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
                <button key={a} className={`rec-act${a === "offer" ? " offer" : ""}${done ? " done" : ""}`} disabled={!chk.ok} title={chk.why} onClick={() => void act(a)}>
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
                  {nilOpts.map((o) => {
                    const on = nilNow === o.v || (o.v > 0 && nilNow > 0 && Math.abs(nilNow - o.v) < 5);
                    return (
                      <button key={o.label} className={on ? "on" : ""} disabled={on || !open.ok} onClick={() => void offerNil(o)}>
                        {o.label}
                        {o.v ? ` ${money(o.v)}` : ""}
                      </button>
                    );
                  })}
                </div>
                <span className="tiny muted">
                  Current: {nilNow ? `${money(nilNow)}/yr` : "none"} · {money(Math.max(0, nilLeft - nilNow))} left in your NIL budget. Bigger names care more about NIL.
                </span>
              </div>
            )}
            {r.offers.includes(L.userTid) && r.stage !== "committed" && (
              <button className="btn btn-sm btn-ghost btn-danger" style={{ alignSelf: "flex-start" }} onClick={() => void pull()}>
                Pull scholarship offer
              </button>
            )}
          </div>
        )}
      </Card>
      {msg && <div className={`small ${msg.ok ? "good" : "bad"}`}>{msg.msg}</div>}
    </div>
  );
}

function ethicWord(v: number): string {
  return v >= 75 ? "Gym rat" : v >= 55 ? "Hard worker" : v >= 35 ? "Average" : "Needs motivation";
}

/** Broad ratings, revealed one category at a time. */
function RatingsTab({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const seen = seenOf(p);
  const talked = talkedTo(p);
  const open = recruitingOpen(L, p);
  const scoutable = r.kind === "hs" && open.ok;
  return (
    <Card title="Ratings" sub={r.kind === "portal" ? "He's played college ball, so his ratings are known." : `${seen.length} of 7 scouted. Tap a ? to scout that category (${SCOUT_COST.game} pts).`}>
      <div className="cat-grid">
        {CAT_KEYS.map((k) => {
          const known = seen.includes(k);
          return (
            <div key={k} className={`cat-card${known ? "" : " unknown-card"}`}>
              <div style={{ minWidth: 0 }}>
                <b>{CATS[k].label}</b>
                <div className="tiny muted">{CATS[k].desc}</div>
              </div>
              {known ? (
                <Grade v={catValue(p, k)} md />
              ) : (
                <button className="unknown big" disabled={!scoutable || L.recruitPts < SCOUT_COST.game} title={scoutable ? `Scout a game for his ${CATS[k].label.toLowerCase()} (${SCOUT_COST.game} pts)` : open.why} onClick={async () => {
                    if (await confirmSpend({ title: `Scout his ${CATS[k].label.toLowerCase()}?`, body: `Go see ${p.first} play and watch for it. ${CATS[k].desc}.`, cost: { pts: SCOUT_COST.game, have: L.recruitPts }, ok: "Scout it" }))
                      mutate((LL) => void scoutGame(LL, p, k));
                  }}>
                  ?
                </button>
              )}
            </div>
          );
        })}
        <div className={`cat-card${talked ? "" : " unknown-card"}`}>
          <div style={{ minWidth: 0 }}>
            <b>Work ethic</b>
            <div className="tiny muted">{talked ? `${ethicWord(p.workEthic)} · how fast he grows` : "How fast he grows and takes to training"}</div>
          </div>
          {talked ? <Grade v={p.workEthic} md /> : <span className="unknown big">?</span>}
        </div>
        <div className={`cat-card${talked ? "" : " unknown-card"}`}>
          <div style={{ minWidth: 0 }}>
            <b>Potential</b>
            <div className="tiny muted">How good he can become</div>
          </div>
          {talked ? <Grade v={p.pot} md /> : <span className="unknown big">?</span>}
        </div>
      </div>
      {!talked && r.kind === "hs" && <div className="tiny muted mt-12">Talk to his coach (on the Overview tab) to learn his work ethic and potential.</div>}
    </Card>
  );
}

/** High school career; the senior year plays out alongside the college season. */
function HsStatsTab({ L, p }: { L: League; p: Player }) {
  const rows = hsCareer(L, p);
  const last = p.stats[p.stats.length - 1];
  if (p.recruit?.kind === "portal")
    return (
      <Card title="College stats">
        {last && last.g ? (
          <div className="small">
            {seasonLabel(last.season)}: {(last.pts / last.g).toFixed(1)} PTS, {((last.orb + last.drb) / last.g).toFixed(1)} REB, {(last.ast / last.g).toFixed(1)} AST in {last.g} games.
          </div>
        ) : (
          <div className="muted">No college stats.</div>
        )}
      </Card>
    );
  return (
    <Card title="High school career" sub={`${p.city}, ${p.state}`} flush>
      <table className="tbl">
        <thead>
          <tr>
            <th>Year</th>
            <th className="n">G</th>
            <th className="n">PTS</th>
            <th className="n">REB</th>
            <th className="n">AST</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((x) => (
            <tr key={x.year}>
              <td>
                <b>{x.year}</b> {x.live && <span className="badge gold">{x.g ? "In progress" : "Starts with your season"}</span>}
              </td>
              <td className="n">{x.g || "-"}</td>
              <td className="n">{x.g ? x.pts.toFixed(1) : "-"}</td>
              <td className="n">{x.g ? x.reb.toFixed(1) : "-"}</td>
              <td className="n">{x.g ? x.ast.toFixed(1) : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
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

type TabKey = "overview" | "ratings" | "stats";

export function RecruitProfile({ p }: { p: Player }) {
  const L = useLeague();
  const r = p.recruit!;
  const [tab, setTab] = useState<TabKey>("overview");
  const seen = seenOf(p);
  const talked = talkedTo(p);
  const from = r.fromTid !== undefined ? teamMaybe(L, r.fromTid) : undefined;
  const committed = r.committedTo !== null ? team(L, r.committedTo) : undefined;
  const colors = (committed ?? from)?.colors ?? ["#273449", "#f2b631"];
  const onBoard = L.board.includes(p.id);
  const last = p.stats[p.stats.length - 1];
  const career = hsCareer(L, p);
  const hsNow = career.length ? (career[career.length - 1].g ? career[career.length - 1] : career[career.length - 2]) : null;
  const heat = heatOf(L, p, L.userTid);
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
          {r.kind === "hs" && hsNow ? (
            <>
              <div>
                <div className="label">{hsNow.year} PPG</div>
                <div className="value">{hsNow.pts.toFixed(1)}</div>
              </div>
              <div>
                <div className="label">RPG</div>
                <div className="value">{hsNow.reb.toFixed(1)}</div>
              </div>
              <div>
                <div className="label">APG</div>
                <div className="value">{hsNow.ast.toFixed(1)}</div>
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
              {r.kind === "portal" ? <Grade v={p.ovr} /> : seen.length >= 4 ? <Grade v={scoutedOvr(p)} /> : <span className="unknown light">?</span>}
            </div>
          </div>
          <div>
            <div className="label">Potential</div>
            <div className="value" style={{ paddingTop: 2 }}>
              {talked ? <Grade v={p.pot} /> : r.kind === "portal" ? <Grade v={p.pot + p.potErr} /> : <span className="unknown light">?</span>}
            </div>
          </div>
          <div>
            <div className="label">Your heat</div>
            <div className="value" style={{ fontSize: 16, paddingTop: 4 }}>
              {heat.label}
            </div>
          </div>
        </div>
      </div>
      <Tabs
        tabs={[
          { key: "overview", label: "Overview" },
          { key: "ratings", label: r.kind === "hs" ? `Ratings · ${seen.length}/7` : "Ratings" },
          { key: "stats", label: r.kind === "hs" ? "HS Stats" : "College Stats" },
        ]}
        value={tab}
        onChange={setTab}
      />
      {tab === "overview" && (
        <div className="grid g2" style={{ alignItems: "start" }}>
          <div className="col gap-16">
            <WhatHeWants L={L} p={p} />
            <RecruitPanel L={L} p={p} />
          </div>
          <div className="col gap-16">
            <WhosAfterHim L={L} p={p} />
            <Card title="Timeline">
              <Timeline p={p} />
            </Card>
          </div>
        </div>
      )}
      {tab === "ratings" && <RatingsTab L={L} p={p} />}
      {tab === "stats" && <HsStatsTab L={L} p={p} />}
    </div>
  );
}
