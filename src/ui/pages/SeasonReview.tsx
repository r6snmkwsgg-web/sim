import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { seasonLabel, team } from "../../engine/core";
import { prestigeTier } from "../../engine/ratings";
import { Card, Empty, heroStyle, Logo, PageHead, TeamLink, Trophy } from "../components/common";
import { Icon } from "../components/Icons";
import { fetchSeason, signed, useAsync } from "../util";

export function SeasonReview() {
  const L = useLeague();
  const h = L.history[L.history.length - 1];
  const { data: archived } = useAsync(async () => (h && h.season !== L.season ? (await fetchSeason(L, h.season))?.polls : undefined), [h?.season, L.season]);
  if (!h) return <Empty>The season review appears after the national championship.</Empty>;
  const ut = team(L, h.userTid);
  const s = ut.seasons.find((x) => x.season === h.season)!;
  const startPrestige = s.prestigeStart ?? s.prestige;
  const aw = L.awards.find((a) => a.season === h.season);
  const myAwards = aw ? [...aw.national, ...aw.allAmerica.flat(), ...Object.values(aw.conf).flatMap((c) => [...c.awards, ...c.teams.flat()])].filter((a) => a.tid === ut.id) : [];
  const champ = h.champion !== null ? team(L, h.champion) : null;
  const polls = archived ?? L.polls;
  const finalPoll = polls.find((p) => p.label === "Final") ?? polls[polls.length - 1];
  return (
    <div className="col gap-16">
      <PageHead eyebrow={seasonLabel(h.season)} title="Season Review" />
      {champ && (
        <div className="hero-banner champ-banner" style={heroStyle(champ.colors)}>
          <div className="hero-inner" style={{ padding: "28px 30px" }}>
            <span className="trophy-big">
              <Icon name="awards" size={46} />
            </span>
            <Logo team={champ} size={96} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div className="hero-kicker">{seasonLabel(h.season)} national champions</div>
              <div className="hero-title" style={{ marginTop: 6 }}>
                {champ.name} {champ.mascot}
              </div>
              <div className="hero-sub">
                Defeated {h.runnerUp !== null ? team(L, h.runnerUp).name : "?"} in the final{h.mop ? ` · Most Outstanding Player: ${h.mop.playerName}` : ""}
              </div>
            </div>
          </div>
        </div>
      )}
      <div className="grid g-main">
        <Card title={`Your season: ${ut.name}`}>
          <div className="stat-row" style={{ margin: "-14px -14px 12px", borderBottom: "1px solid var(--border)" }}>
            <div className="stat">
              <div className="label">Record</div>
              <div className="value">
                {s.w}-{s.l}
              </div>
            </div>
            <div className="stat">
              <div className="label">Conference</div>
              <div className="value">
                {s.cw}-{s.cl}
                <small>{s.confRank ? `${s.confRank} place` : ""}</small>
              </div>
            </div>
            <div className="stat">
              <div className="label">Final AP</div>
              <div className="value">{s.apFinal ? `#${s.apFinal}` : "NR"}</div>
            </div>
            <div className="stat">
              <div className="label">Prestige</div>
              <div className="value">
                {s.prestige.toFixed(0)}
                <small className={s.prestige >= startPrestige ? "good" : "bad"}>{signed(s.prestige - startPrestige)}</small>
              </div>
            </div>
          </div>
          <dl className="kv">
            <dt>Postseason</dt>
            <dd>{h.userResult}</dd>
            <dt>Conference tournament</dt>
            <dd>{s.confTourney ?? "-"}</dd>
            <dt>Recruiting class</dt>
            <dd>{s.recruitRank ? `#${s.recruitRank} nationally` : "No signees ranked"}</dd>
            <dt>Program tier</dt>
            <dd>{prestigeTier(ut.prestige)}</dd>
          </dl>
          {myAwards.length > 0 && (
            <>
              <div className="divider" />
              <div className="bold mb-8">Honors</div>
              {myAwards.map((a, i) => (
                <div key={i} className="row small">
                  <Trophy />
                  <Link to={`/l/${L.id}/player/${a.pid}`}>{a.playerName}</Link>
                  <span className="muted">{a.name}</span>
                </div>
              ))}
            </>
          )}
        </Card>
        <div className="col gap-16">
          <Card title="National awards">
            {aw?.national.map((a) => (
              <div key={a.name} className="row small" style={{ padding: "4px 0" }}>
                <span className="muted" style={{ width: 160 }}>
                  {a.name}
                </span>
                {a.pid !== undefined ? <Link to={`/l/${L.id}/player/${a.pid}`}>{a.playerName}</Link> : <span>{a.playerName}</span>}
                <span className="faint">{team(L, a.tid).short}</span>
              </div>
            ))}
          </Card>
          <Card title="Final Top 10" flush>
            <table className="tbl compact">
              <tbody>
                {finalPoll?.ranks.slice(0, 10).map((r) => (
                  <tr key={r.tid} className={r.tid === ut.id ? "hl" : ""}>
                    <td className="muted">{r.rank}</td>
                    <td>
                      <TeamLink L={L} tid={r.tid} size={18} />
                    </td>
                    <td className="n muted">
                      {r.w}-{r.l}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      </div>
      <Card>
        <div className="row">
          <div style={{ flex: 1 }}>
            <b>Up next: the offseason.</b> <span className="muted">Coaching carousel → NBA Draft & graduation → Transfer portal (4 windows) → Signing day → New season.</span>
          </div>
          <Link to={`/l/${L.id}/history`} className="btn">
            League history
          </Link>
        </div>
      </Card>
    </div>
  );
}
