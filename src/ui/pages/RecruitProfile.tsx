import { useState } from "react";
import { Link } from "react-router-dom";
import { mutate, useLeague } from "../store";
import { seasonLabel, team, teamMaybe } from "../../engine/core";
import { classLabel, grade, heightStr, RATING_LABELS } from "../../engine/ratings";
import { regionOf } from "../../engine/data/cities";
import {
  ACTIONS, canAct, doAction, factorScores, fit, NIL_VALUE, nilCommitted, OFFICIAL_VISITS, openSpots, PREF_LABELS, pullOffer, scoutedOvr, scoutedPot, scoutNoise, setNilOffer, type ActionKey,
} from "../../engine/recruiting";
import type { League, Player, PrefKey, RatingKey } from "../../engine/types";
import { PREF_KEYS } from "../../engine/types";
import { Bar, Card, Grade, heroStyle, Logo, Stars, Tabs } from "../components/common";
import { Face } from "../components/Face";
import { Icon } from "../components/Icons";
import { money } from "../util";

const IMPORTANCE = ["", "Not important", "Minor", "Somewhat important", "Important", "Very important"];
const ACTION_ICONS: Record<ActionKey, string> = { scout: "eye", call: "phone", assistant: "whistle", coach: "coach", visit: "plane", offer: "draft" };

export function stageText(L: League, p: Player): string {
  const r = p.recruit!;
  if (r.stage === "signed") return `Signed with ${team(L, r.committedTo!).name}`;
  if (r.stage === "committed") return `Committed to ${team(L, r.committedTo!).name}`;
  if (r.stage === "top5") return `Top ${r.top5.length}`;
  if (r.stage === "unsigned") return "Unsigned";
  return "Open";
}

function fitWord(x: number): { t: string; c: string } {
  if (x >= 0.8) return { t: "Excellent", c: "var(--good)" };
  if (x >= 0.6) return { t: "Good", c: "var(--gb)" };
  if (x >= 0.4) return { t: "Fair", c: "var(--gc)" };
  if (x >= 0.2) return { t: "Poor", c: "var(--gd)" };
  return { t: "Bad", c: "var(--bad)" };
}

function InterestedTeams({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const list = Object.entries(r.interest)
    .map(([k, v]) => ({ tid: Number(k), v }))
    .filter((x) => x.v > 0.5)
    .sort((a, b) => b.v - a.v)
    .slice(0, 15);
  const max = Math.max(10, ...list.map((x) => x.v));
  if (!list.length) return <div className="empty">No programs have shown interest yet.</div>;
  return (
    <div className="col" style={{ gap: 6 }}>
      {list.map((x, i) => {
        const t = team(L, x.tid);
        const offered = r.offers.includes(x.tid);
        const visited = r.visits.includes(x.tid);
        const committed = r.committedTo === x.tid;
        const out = (r.stage === "top5" || r.stage === "committed") && !r.top5.includes(x.tid);
        return (
          <div key={x.tid} className={`int-row${x.tid === L.userTid ? " me" : ""}`} style={{ opacity: out ? 0.42 : 1 }}>
            <span className="faint bold" style={{ width: 20, textAlign: "right" }}>
              {i + 1}
            </span>
            <Logo team={t} size={30} />
            <Link to={`/l/${L.id}/team/${t.id}`} style={{ width: 160 }} className="bold ellipsis">
              {t.name}
            </Link>
            <div style={{ flex: 1 }}>
              <Bar value={x.v} max={max} color={x.tid === L.userTid ? "var(--accent-ink)" : "color-mix(in srgb, var(--text) 35%, transparent)"} />
            </div>
            <span style={{ width: 96 }} className="row gap-4">
              {committed && (
                <span title="Committed" className="mark good">
                  <Icon name="check" size={12} />
                </span>
              )}
              {offered && (
                <span title="Scholarship offered" className="mark">
                  <Icon name="draft" size={12} />
                </span>
              )}
              {visited && (
                <span title="Official visit" className="mark">
                  <Icon name="plane" size={12} />
                </span>
              )}
              {L.settings.nil && (r.nil[x.tid] ?? 0) > 0 && (
                <span title={`NIL offer ${money(r.nil[x.tid])}`} className="mark gold">
                  <Icon name="money" size={12} />
                </span>
              )}
            </span>
          </div>
        );
      })}
      <div className="row-wrap tiny muted mt-8" style={{ gap: 12 }}>
        <span className="row gap-4">
          <span className="mark">
            <Icon name="draft" size={11} />
          </span>
          Offered
        </span>
        <span className="row gap-4">
          <span className="mark">
            <Icon name="plane" size={11} />
          </span>
          Official visit
        </span>
        <span className="row gap-4">
          <span className="mark gold">
            <Icon name="money" size={11} />
          </span>
          NIL offer
        </span>
        <span>Faded = eliminated from his list</span>
      </div>
    </div>
  );
}

function Preferences({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const ut = team(L, L.userTid);
  const f = factorScores(L, ut, p);
  const keys = PREF_KEYS.filter((k) => k !== "nil" || L.settings.nil);
  const overall = fit(L, ut, p);
  const ratingKeys: RatingKey[] = ["ins", "mid", "three", "ft", "hnd", "pas", "iq", "perD", "intD", "stl", "blk", "reb", "ath", "str", "end"];
  const sd = [9, 5.5, 3, 1][r.scout];
  return (
    <div className="col gap-16">
      <Card title="What matters to him" sub={`Overall fit with ${ut.name}: ${fitWord(overall).t}`}>
        <table className="tbl compact">
          <thead>
            <tr>
              <th>Factor</th>
              <th>Importance</th>
              <th>Your program</th>
            </tr>
          </thead>
          <tbody>
            {keys
              .slice()
              .sort((a, b) => r.prefs[b] - r.prefs[a])
              .map((k: PrefKey) => {
                const w = fitWord(f[k]);
                return (
                  <tr key={k}>
                    <td className="bold">{PREF_LABELS[k]}</td>
                    <td>
                      <span className="pref-dots" title={IMPORTANCE[r.prefs[k]]}>
                        {[1, 2, 3, 4, 5].map((i) => (
                          <span key={i} className={i <= r.prefs[k] ? "on" : ""} />
                        ))}
                      </span>
                    </td>
                    <td>
                      <span style={{ color: w.c, fontWeight: 650 }}>{w.t}</span>
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
        <p className="tiny muted mt-12">
          Fit multiplies the effect of every recruiting action. Playing time depends on who returns at his position next season; proximity is distance from {p.city}; contender blends your power ranking and prestige.
        </p>
      </Card>
      <Card
        title="Scouting Report"
        sub={r.scout >= 3 ? "Fully scouted" : `Scouting level ${r.scout}/3 · estimates ±${Math.round(sd)}`}
        right={
          r.scout < 3 ? (
            <button className="btn btn-sm" disabled={!canAct(L, L.userTid, p, "scout").ok} onClick={() => mutate((LL) => void doAction(LL, LL.userTid, p, "scout"))}>
              Scout ({ACTIONS.scout.cost} pts)
            </button>
          ) : null
        }
      >
        <div className="row gap-16 mb-12">
          <div className="center">
            <div className="tiny muted bold">EST. OVR</div>
            <Grade v={scoutedOvr(p)} />
          </div>
          <div className="center">
            <div className="tiny muted bold">EST. POT</div>
            <Grade v={scoutedPot(p)} />
          </div>
          <div className="small muted" style={{ flex: 1 }}>
            {r.scout === 0 ? "Unscouted: you only know what the recruiting services say. Scout him to see his real ratings." : r.scout === 3 ? "Your staff has a complete read on him." : "Your staff's evaluation is getting sharper."}
          </div>
        </div>
        <div className="grid g2" style={{ gap: "4px 20px" }}>
          {ratingKeys.map((k, i) => {
            const est = Math.round(Math.max(1, Math.min(99, p.r[k] + scoutNoise(p, 10 + i, r.scout))));
            const lo = Math.max(1, Math.round(est - sd));
            const hi = Math.min(99, Math.round(est + sd));
            return (
              <div key={k} className="row" style={{ gap: 8 }}>
                <span className="muted" style={{ width: 92 }}>
                  {RATING_LABELS[k]}
                </span>
                <span className="bold num" style={{ width: 52 }}>
                  {r.scout >= 3 ? est : `${lo}-${hi}`}
                </span>
                <span className="faint small">{grade(est)}</span>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

function Actions({ L, p }: { L: League; p: Player }) {
  const r = p.recruit!;
  const ut = team(L, L.userTid);
  const [msg, setMsg] = useState<string>("");
  const [nil, setNil] = useState<number>(r.nil[L.userTid] ?? Math.round(NIL_VALUE[r.stars] * 0.8));
  const act = (a: ActionKey) =>
    mutate((LL) => {
      const res = doAction(LL, LL.userTid, p, a);
      setMsg(res.msg);
    });
  const spots = openSpots(L, ut.id);
  const nilLeft = ut.nilBudget - nilCommitted(L, ut.id) + (r.nil[L.userTid] ?? 0);
  const keys: ActionKey[] = ["call", "assistant", "coach", "visit", "offer"];
  return (
    <div className="col gap-16">
      <Card title="Recruit Him" sub={`${L.recruitPts}/${L.recruitPtsMax} points left · ${spots} open spot${spots === 1 ? "" : "s"} · ${OFFICIAL_VISITS - ut.officialVisitsUsed} official visits left`}>
        {r.stage === "signed" ? (
          <div className="muted">He has signed. Recruiting is over.</div>
        ) : (
          <div className="col gap-8">
            {keys.map((a) => {
              const chk = canAct(L, L.userTid, p, a);
              const def = ACTIONS[a];
              return (
                <div key={a} className="act-row">
                  <span className="act-ic">
                    <Icon name={ACTION_ICONS[a]} size={16} />
                  </span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="bold">
                      {def.label} <span className="faint small">· {def.cost} pts</span>
                    </div>
                    <div className="tiny muted">{def.desc}</div>
                  </div>
                  <button className={`btn btn-sm ${chk.ok ? "btn-primary" : ""}`} style={{ width: 96 }} disabled={!chk.ok} title={chk.why} onClick={() => act(a)}>
                    {chk.ok ? "Do it" : chk.why && chk.why.length < 14 ? chk.why : "Unavailable"}
                  </button>
                </div>
              );
            })}
            {r.offers.includes(L.userTid) && r.stage !== "committed" && (
              <button className="btn btn-sm btn-danger" onClick={() => mutate((LL) => pullOffer(LL, LL.userTid, p))}>
                Pull scholarship offer
              </button>
            )}
            {msg && <div className="small good">{msg}</div>}
          </div>
        )}
      </Card>
      {L.settings.nil && r.stage !== "signed" && (
        <Card title="NIL Offer" sub={`Budget left: ${money(Math.max(0, nilLeft))} · typical for a ${r.stars}★: ${money(NIL_VALUE[r.stars])}`}>
          <div className="row">
            <input type="range" min={0} max={Math.max(50, Math.round(NIL_VALUE[r.stars] * 2))} step={5} value={nil} onChange={(e) => setNil(Number(e.target.value))} style={{ flex: 1 }} />
            <span className="bold num" style={{ width: 64, textAlign: "right" }}>
              {money(nil)}
            </span>
            <button className="btn btn-sm" onClick={() => mutate((LL) => setMsg(setNilOffer(LL, LL.userTid, p, nil).msg))}>
              Offer
            </button>
          </div>
          <div className="tiny muted mt-8">Current offer: {r.nil[L.userTid] ? money(r.nil[L.userTid]) + "/yr" : "none"}. NIL matters more to higher-rated recruits.</div>
        </Card>
      )}
    </div>
  );
}

function Timeline({ p }: { p: Player }) {
  const r = p.recruit!;
  return r.history.length ? (
    <div className="timeline">
      {r.history.slice(0, 24).map((h, i) => (
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
  const [tab, setTab] = useState<"teams" | "prefs" | "timeline">("teams");
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
            <Face seed={p.faceSeed} race={p.race} colors={colors as [string, string]} size={150} ratio={1.3} frame={false} />
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
            <div className="label">Est. overall</div>
            <div className="value" style={{ paddingTop: 2 }}>
              <Grade v={r.kind === "portal" ? p.ovr : scoutedOvr(p)} />
            </div>
          </div>
          <div>
            <div className="label">Est. potential</div>
            <div className="value" style={{ paddingTop: 2 }}>
              <Grade v={r.kind === "portal" ? p.pot + p.potErr : scoutedPot(p)} />
            </div>
          </div>
          <div>
            <div className="label">Your interest rank</div>
            <div className="value">{ir ? `#${ir}` : "-"}</div>
          </div>
        </div>
      </div>
      <div className="grid g-main">
        <div>
          <Tabs
            tabs={[
              { key: "teams", label: "Interested Teams" },
              { key: "prefs", label: "Preferences & Scouting" },
              { key: "timeline", label: "Timeline" },
            ]}
            value={tab}
            onChange={setTab}
          />
          {tab === "teams" && (
            <div className="card card-b">
              <InterestedTeams L={L} p={p} />
            </div>
          )}
          {tab === "prefs" && <Preferences L={L} p={p} />}
          {tab === "timeline" && (
            <div className="card card-b">
              <Timeline p={p} />
            </div>
          )}
        </div>
        <Actions L={L} p={p} />
      </div>
    </div>
  );
}
