import { useState } from "react";
import { mutate, useLeague } from "../store";
import { coach, seasonLabel, team } from "../../engine/core";
import { acceptJob } from "../../engine/coaches";
import { grade, prestigeStars, prestigeTier } from "../../engine/ratings";
import type { Coach } from "../../engine/types";
import { Card, Logo, Meter, PageHead, Stars, Table, Tabs, TeamLink, type Col, Trophy } from "../components/common";
import { Face } from "../components/Face";

export function CoachPage() {
  const L = useLeague();
  const ch = coach(L, L.userCid)!;
  const ut = team(L, L.userTid);
  const [tab, setTab] = useState<"me" | "all">("me");
  const w = ch.seasons.reduce((a, s) => a + s.w, 0);
  const l = ch.seasons.reduce((a, s) => a + s.l, 0);
  const secColor = ch.security >= 60 ? "var(--good)" : ch.security >= 30 ? "var(--warn)" : "var(--bad)";
  const titles = ch.seasons.filter((s) => s.result === "NCAA Champion").length;
  const ff = ch.seasons.filter((s) => ["NCAA Champion", "NCAA Runner-up", "NCAA Final Four"].includes(s.result)).length;
  const ncaa = ch.seasons.filter((s) => s.result.startsWith("NCAA")).length;
  const coaches = L.coaches.filter((c) => c.tid !== null);
  const cols: Col<Coach>[] = [
    { key: "name", label: "Coach", render: (c) => <span className={c.user ? "bold" : ""}>{c.first} {c.last}</span>, sort: (c) => c.last },
    { key: "team", label: "Program", render: (c) => <TeamLink L={L} tid={c.tid} size={18} />, sort: (c) => team(L, c.tid!).name },
    { key: "age", label: "Age", render: (c) => c.age, sort: (c) => c.age, num: true },
    { key: "yrs", label: "Yrs", render: (c) => L.season - c.hired + 1, sort: (c) => L.season - c.hired, num: true },
    { key: "rec", label: "Career W-L", render: (c) => `${c.seasons.reduce((a, s) => a + s.w, 0)}-${c.seasons.reduce((a, s) => a + s.l, 0)}`, sort: (c) => c.seasons.reduce((a, s) => a + s.w - s.l, 0), num: true },
    { key: "rep", label: "Rep", render: (c) => Math.round(c.rep), sort: (c) => c.rep, num: true },
    { key: "rcr", label: "Recruiting", render: (c) => grade(c.recruiting), sort: (c) => c.recruiting, num: true },
    { key: "dev", label: "Development", render: (c) => grade(c.development), sort: (c) => c.development, num: true },
    { key: "tac", label: "Tactics", render: (c) => grade(c.tactics), sort: (c) => c.tactics, num: true },
  ];
  return (
    <div>
      <PageHead title="Coach & Jobs" />
      {L.jobOffers.length > 0 && (
        <Card title={L.fired ? "You've been fired: choose your next job" : "Job offers"} sub={L.fired ? "If you don't choose, you'll take the best offer when the carousel ends." : "Accepting moves you, and your record, to the new program. Your current commitments stay behind."} className="mb-16">
          <div className="grid g3">
            {L.jobOffers.map((o) => {
              const t = team(L, o.tid);
              const s = t.seasons[t.seasons.length - 1];
              return (
                <div key={o.tid} className="card card-b">
                  <div className="row">
                    <Logo team={t} size={44} />
                    <div>
                      <div className="bold" style={{ fontSize: 16 }}>
                        {t.name}
                      </div>
                      <div className="small muted">{L.conferences[t.cid].name}</div>
                    </div>
                  </div>
                  <div className="mt-8">
                    <Stars n={prestigeStars(t.prestige)} /> <span className="small muted">{prestigeTier(t.prestige)}</span>
                  </div>
                  <div className="small muted">
                    Last season {s.w}-{s.l}
                  </div>
                  <button
                    className="btn btn-primary mt-12"
                    style={{ width: "100%" }}
                    onClick={() => {
                      if (confirm(`Leave ${ut.name} to become head coach at ${t.name}?`)) mutate((LL) => void acceptJob(LL, t.id));
                    }}
                  >
                    Accept job
                  </button>
                </div>
              );
            })}
          </div>
        </Card>
      )}
      {(L.realign ?? [])
        .filter((r) => r.tid === L.userTid)
        .map((r) => {
          const toC = L.conferences[r.toCid];
          const fromC = L.conferences[ut.cid];
          return (
            <Card key={r.toCid} title={`Conference invitation: ${toC.name}`} sub={`Moving up from the ${fromC.short} takes effect next season.`} className="mb-16">
              <div className="row">
                <div style={{ flex: 1 }} className="small">
                  A stronger conference means tougher league games and a better NCAA resume, more prestige upside, a bigger NIL budget, and more appeal to recruits.
                </div>
                {r.accepted === true ? (
                  <span className="badge good">Accepted</span>
                ) : r.accepted === false ? (
                  <span className="badge">Declined</span>
                ) : null}
                <button className="btn btn-primary" disabled={r.accepted === true} onClick={() => mutate(() => void (r.accepted = true))}>
                  Accept
                </button>
                <button className="btn" disabled={r.accepted === false} onClick={() => mutate(() => void (r.accepted = false))}>
                  Decline
                </button>
              </div>
            </Card>
          );
        })}
      <Tabs
        tabs={[
          { key: "me", label: "Your Career" },
          { key: "all", label: "All Coaches" },
        ]}
        value={tab}
        onChange={setTab}
      />
      {tab === "me" ? (
        <div className="grid g-main">
          <div className="col gap-16">
            <div className="card">
              <div className="card-b row gap-16">
                <Face seed={ch.faceSeed} race={ch.race} colors={ut.colors} size={90} />
                <div style={{ flex: 1 }}>
                  <div className="hero-name">
                    {ch.first} {ch.last}
                  </div>
                  <div className="muted">
                    Head coach, {ut.name} · age {ch.age} · {L.season - ch.hired + 1} season(s) at {ut.name}
                  </div>
                  <div className="row mt-8 gap-16">
                    <span>
                      <b>
                        {w}-{l}
                      </b>{" "}
                      <span className="muted">career</span>
                    </span>
                    <span>
                      <b>{ncaa}</b> <span className="muted">NCAA bids</span>
                    </span>
                    <span>
                      <b>{ff}</b> <span className="muted">Final Fours</span>
                    </span>
                    <span>
                      <b>{titles}</b> <span className="muted">titles</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <Card title="Season by season" flush>
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Season</th>
                    <th>Program</th>
                    <th className="n">W-L</th>
                    <th className="n">Conf</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {ch.seasons
                    .slice()
                    .reverse()
                    .map((s) => (
                      <tr key={`${s.season}-${s.tid}`}>
                        <td>{seasonLabel(s.season)}</td>
                        <td>
                          <TeamLink L={L} tid={s.tid} size={18} season={s.season} />
                        </td>
                        <td className="n bold">
                          {s.w}-{s.l}
                        </td>
                        <td className="n">
                          {s.cw}-{s.cl}
                        </td>
                        <td className="small">{s.result}</td>
                      </tr>
                    ))}
                  {!ch.seasons.length && (
                    <tr>
                      <td colSpan={5} className="empty">
                        Your first season is underway.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </Card>
          </div>
          <div className="col gap-16">
            <Card title="Job security">
              <Meter value={ch.security} color={secColor} />
              <div className="row mt-8">
                <b>{ch.security >= 70 ? "Safe" : ch.security >= 45 ? "Stable" : ch.security >= 25 ? "Warm seat" : "Hot seat"}</b>
                <span className="spacer" />
                <span className="muted">{ch.security}/100</span>
              </div>
              <p className="small muted mt-8">
                Security rises when you outperform the program's prestige and falls when you don't. {L.settings.canBeFired ? "At 10 or below after your second season, you can be fired." : "Firing is turned off in this league."}
              </p>
            </Card>
            <Card title="Reputation & skills">
              <dl className="kv">
                <dt>Reputation</dt>
                <dd>{Math.round(ch.rep)} / 100</dd>
                <dt>Recruiting</dt>
                <dd>{grade(ch.recruiting)}</dd>
                <dt>Development</dt>
                <dd>{grade(ch.development)}</dd>
                <dt>Tactics</dt>
                <dd>{grade(ch.tactics)}</dd>
              </dl>
              <p className="small muted mt-8">Reputation drives job offers and how recruits rate you as a head coach. Skills improve with experience and success.</p>
            </Card>
            <Card title="Awards">
              {ch.awards.length ? (
                ch.awards
                  .slice()
                  .reverse()
                  .map((a, i) => (
                    <div key={i} className="row small">
                      <Trophy /> {a.name} <span className="spacer" /> <span className="muted">{seasonLabel(a.season)}</span>
                    </div>
                  ))
              ) : (
                <div className="muted small">None yet.</div>
              )}
            </Card>
          </div>
        </div>
      ) : (
        <Card flush>
          <Table cols={cols} rows={coaches} rowKey={(c) => c.id} initialSort="rep" limit={50} rowClass={(c) => (c.user ? "hl" : undefined)} />
        </Card>
      )}
    </div>
  );
}
