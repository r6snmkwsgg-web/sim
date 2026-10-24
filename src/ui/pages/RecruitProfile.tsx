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
import { Bar, Card, Grade, Logo, Stars, Tabs } from "../components/common";
import { Face } from "../components/Face";
import { Icon } from "../components/Icons";
import { money } from "../util";

const IMPORTANCE = ["", "Not important", "Minor", "Somewhat important", "Important", "Very important"];

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
          <div key={x.tid} className="row" style={{ gap: 12, padding: "6px 4px", borderRadius: 6, background: x.tid === L.userTid ? "var(--accent-soft)" : undefined, opacity: out ? 0.45 : 1 }}>
            <span className="muted bold" style={{ width: 20, textAlign: "right" }}>
              {i + 1}
            </span>
            <div style={{ flex: 1 }}>
              <Bar value={x.v} max={max} />
            </div>
            <Logo team={t} size={30} />
            <Link to={`/l/${L.id}/team/${t.id}`} style={{ width: 150 }} className="bold">
              {t.short}
            </Link>
            <span style={{ width: 70 }} className="row gap-4">
              {committed && <span title="Committed" className="good"><Icon name="check" size={18} /></span>}
              {offered && <span title="Scholarship offered">🎓</span>}
              {visited && <span title="Official visit">✈️</span>}
              {L.settings.nil && (r.nil[x.tid] ?? 0) > 0 && <span title={`NIL offer ${money(r.nil[x.tid])}`}>💵</span>}
            </span>
          </div>
        );
      })}
      <div className="tiny muted mt-8">🎓 offered · ✈️ official visit · 💵 NIL offer · faded = eliminated from his list</div>
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
    <div className="grid g2">
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
    <div className="grid g2">
      <Card title="Recruiting Actions" sub={`${L.recruitPts} of ${L.recruitPtsMax} points left this week · ${spots} open spot(s) · ${OFFICIAL_VISITS - ut.officialVisitsUsed} official visits left`}>
        {r.stage === "signed" ? (
          <div className="muted">He has signed. Recruiting is over.</div>
        ) : (
          <div className="col gap-8">
            {keys.map((a) => {
              const chk = canAct(L, L.userTid, p, a);
              const def = ACTIONS[a];
              return (
                <div key={a} className="row" style={{ gap: 12, padding: "6px 0", borderBottom: "1px solid var(--border)" }}>
                  <div style={{ flex: 1 }}>
                    <div className="bold">{def.label}</div>
                    <div className="tiny muted">{def.desc}</div>
                  </div>
                  <span className="pill">{def.cost} pts</span>
                  <button className="btn btn-sm btn-primary" style={{ width: 92 }} disabled={!chk.ok} title={chk.why} onClick={() => act(a)}>
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
      <div className="col gap-16">
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
        <Card title="Recruiting Timeline">
          {r.history.length ? (
            <div className="col gap-4">
              {r.history.slice(0, 14).map((h, i) => (
                <div key={i} className="row small">
                  <span className="faint" style={{ width: 54 }}>
                    Wk {h.week}
                  </span>
                  <span>{h.text}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="muted small">Nothing yet.</div>
          )}
        </Card>
      </div>
    </div>
  );
}

export function RecruitProfile({ p }: { p: Player }) {
  const L = useLeague();
  const r = p.recruit!;
  const [tab, setTab] = useState<"teams" | "prefs" | "actions">("teams");
  const from = r.fromTid !== undefined ? teamMaybe(L, r.fromTid) : undefined;
  const committed = r.committedTo !== null ? team(L, r.committedTo) : undefined;
  const colors = (committed ?? from)?.colors ?? ["#334155", "#e2e8f0"];
  const onBoard = L.board.includes(p.id);
  const last = p.stats[p.stats.length - 1];
  return (
    <div className="col gap-16">
      <div className="card" style={{ overflow: "hidden" }}>
        <div style={{ display: "flex" }}>
          <div style={{ background: colors[0], padding: "16px 18px 0", display: "flex", alignItems: "flex-end" }}>
            <Face seed={p.faceSeed} race={p.race} colors={colors as [string, string]} size={120} />
          </div>
          <div style={{ padding: 18, flex: 1 }}>
            <div className="row">
              <div>
                <div className="muted small">
                  {r.kind === "portal" ? `Transfer portal · from ${from?.name ?? "?"}` : `Class of ${r.classSeason}`} · {p.pos}
                </div>
                <div className="hero-name">
                  {p.first} <span style={{ textTransform: "uppercase" }}>{p.last}</span>
                </div>
                <div className="mt-8" style={{ fontSize: 22 }}>
                  <Stars n={r.stars} />
                </div>
              </div>
              <div className="spacer" />
              <div className="col" style={{ alignItems: "flex-end" }}>
                <span className={`badge ${r.stage === "signed" || r.stage === "committed" ? "good" : r.stage === "top5" ? "warn" : ""}`} style={{ fontSize: 12, height: 24 }}>
                  {stageText(L, p)}
                </span>
                <div className="muted small">
                  #{r.rank} overall · #{r.posRank} {p.pos}
                </div>
                <button
                  className="btn btn-sm"
                  onClick={() =>
                    mutate((LL) => {
                      LL.board = onBoard ? LL.board.filter((x) => x !== p.id) : [...LL.board, p.id];
                    })
                  }
                >
                  {onBoard ? "★ On your board" : "☆ Add to board"}
                </button>
              </div>
            </div>
            <div className="row-wrap mt-8" style={{ gap: 18 }}>
              <span>
                <b>{heightStr(p.hgt)}</b> <span className="muted">· {p.wgt} lbs · {heightStr(p.wing)} wingspan</span>
              </span>
              <span className="muted">
                {p.city}, {p.state} · {regionOf(p.state)}
              </span>
              <span className="muted">{p.archetype}</span>
              {r.kind === "portal" && <span className="muted">{classLabel(p)} · eligibility left: {4 - p.eligUsed}</span>}
            </div>
          </div>
        </div>
        <div className="stat-row" style={{ borderTop: "1px solid var(--border)", background: "var(--panel-2)" }}>
          {r.kind === "hs" && r.hs ? (
            <>
              <div className="stat">
                <div className="label">PTS (HS)</div>
                <div className="value">{r.hs.pts.toFixed(1)}</div>
              </div>
              <div className="stat">
                <div className="label">REB (HS)</div>
                <div className="value">{r.hs.reb.toFixed(1)}</div>
              </div>
              <div className="stat">
                <div className="label">AST (HS)</div>
                <div className="value">{r.hs.ast.toFixed(1)}</div>
              </div>
            </>
          ) : last ? (
            <>
              <div className="stat">
                <div className="label">PTS ({seasonLabel(last.season)})</div>
                <div className="value">{last.g ? (last.pts / last.g).toFixed(1) : "-"}</div>
              </div>
              <div className="stat">
                <div className="label">REB</div>
                <div className="value">{last.g ? ((last.orb + last.drb) / last.g).toFixed(1) : "-"}</div>
              </div>
              <div className="stat">
                <div className="label">AST</div>
                <div className="value">{last.g ? (last.ast / last.g).toFixed(1) : "-"}</div>
              </div>
              <div className="stat">
                <div className="label">MIN</div>
                <div className="value">{last.g ? (last.min / last.g).toFixed(1) : "-"}</div>
              </div>
            </>
          ) : null}
          <div className="stat">
            <div className="label">Your interest rank</div>
            <div className="value">
              {(() => {
                const sorted = Object.entries(r.interest).sort((a, b) => b[1] - a[1]);
                const i = sorted.findIndex(([k]) => Number(k) === L.userTid);
                return i >= 0 ? `#${i + 1}` : "-";
              })()}
            </div>
          </div>
        </div>
      </div>
      <Tabs
        tabs={[
          { key: "teams", label: "Interested Teams" },
          { key: "prefs", label: "Preferences & Scouting" },
          { key: "actions", label: "Actions" },
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
      {tab === "actions" && <Actions L={L} p={p} />}
    </div>
  );
}
