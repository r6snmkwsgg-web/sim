import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { coach, roster, seasonLabel, shortDayLabel, team } from "../../engine/core";
import { curSeason } from "../../engine/play";
import { currentPoll, currentRank, powerRanks } from "../../engine/rankings";
import { prestigeStars, prestigeTier } from "../../engine/ratings";
import { classRankings, commitsFor, openSpots } from "../../engine/recruiting";
import { Card, Logo, Meter, PlayerLink, Stars, TeamLink } from "../components/common";
import { gameView, KIND_COLORS, lastGames, nextGame, standingsRows, streakStr, teamLeaders } from "../helpers";
import { f1, ordinal } from "../util";
import type { League } from "../../engine/types";

function Guide({ L }: { L: League }) {
  const base = `/l/${L.id}`;
  const items: Record<League["phase"], { text: string; to?: string; link?: string }[]> = {
    preseason: [
      { text: "Set your rotation and starters", to: `${base}/rotation`, link: "Rotation" },
      { text: "Choose a team strategy and player tendencies", to: `${base}/tactics`, link: "Tactics" },
      { text: "Redshirt freshmen who won't play", to: `${base}/roster`, link: "Roster" },
      { text: "Spend this week's recruiting points", to: `${base}/recruiting`, link: "Recruiting" },
    ],
    regular: [
      { text: "Spend recruiting points every week; they reset each Monday", to: `${base}/targets`, link: "My Targets" },
      { text: "Adjust practice focus to develop your players", to: `${base}/practice`, link: "Practice" },
      { text: "Check your NCAA Tournament resume", to: `${base}/rankings`, link: "Rankings" },
    ],
    confTourney: [{ text: "Win your conference tournament to clinch an automatic bid", to: `${base}/tournaments`, link: "Brackets" }],
    selection: [{ text: "The brackets are out. See where you landed", to: `${base}/tournaments`, link: "Tournaments" }],
    ncaa: [{ text: "Survive and advance", to: `${base}/tournaments`, link: "Bracket" }],
    seasonEnd: [
      { text: "Review the season and awards", to: `${base}/season-review`, link: "Season Review" },
      { text: "Next: the coaching carousel and possible job offers" },
    ],
    carousel: [{ text: "Consider job offers or stay put", to: `${base}/coach`, link: "Coach & Jobs" }],
    draft: [{ text: "See who left for the NBA and who graduated", to: `${base}/draft`, link: "NBA Draft" }],
    portal: [
      { text: "Recruit transfers to fill open spots", to: `${base}/portal`, link: "Transfer Portal" },
      { text: "Re-recruit your own players who entered the portal" },
      { text: "Unsigned high school recruits are still available", to: `${base}/recruiting`, link: "Recruiting" },
    ],
    signing: [{ text: "Finalize next season's roster", to: `${base}/signing`, link: "Signing Day" }],
  };
  return (
    <Card title="What to do now">
      <div className="col">
        {items[L.phase].map((x, i) => (
          <div key={i} className="row">
            <span style={{ width: 6, height: 6, borderRadius: 3, background: "var(--accent)", flex: "none" }} />
            <span style={{ flex: 1 }}>{x.text}</span>
            {x.to && (
              <Link to={x.to} className="btn btn-sm">
                {x.link}
              </Link>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}

function BracketNext({ L }: { L: League }) {
  const ut = team(L, L.userTid);
  for (const br of L.brackets) {
    if (br.champion !== null) continue;
    const bg = br.games.find((g) => g.winner === null && (g.a === L.userTid || g.b === L.userTid));
    if (!bg) continue;
    const oppId = bg.a === L.userTid ? bg.b : bg.a;
    const opp = oppId !== null ? team(L, oppId) : null;
    const day = bg.round < 0 ? br.playinDay : br.days[bg.round];
    const round = bg.round < 0 ? br.playinName : br.rounds[bg.round];
    const mySeed = bg.a === L.userTid ? bg.sa : bg.sb;
    const oppSeed = bg.a === L.userTid ? bg.sb : bg.sa;
    return (
      <Card title="Next Game" sub={`${day !== undefined ? shortDayLabel(L.season, day) : ""} · ${br.name} ${round}`} right={<Link to={`/l/${L.id}/tournaments`} className="btn btn-sm">Bracket</Link>}>
        <div className="row" style={{ justifyContent: "space-around", padding: "6px 0" }}>
          <div className="col center" style={{ alignItems: "center" }}>
            <Logo team={ut} size={60} />
            <div className="bold">
              {mySeed ? <span className="muted">({mySeed}) </span> : null}
              {ut.name}
            </div>
          </div>
          <div className="center" style={{ fontSize: 22, fontWeight: 800 }}>
            vs
          </div>
          <div className="col center" style={{ alignItems: "center" }}>
            {opp ? <Logo team={opp} size={60} /> : <div className="logo" style={{ width: 60, height: 60, background: "var(--panel-3)", color: "var(--faint)" }}>?</div>}
            <div className="bold">
              {opp && oppSeed ? <span className="muted">({oppSeed}) </span> : null}
              {opp ? <Link to={`/l/${L.id}/team/${opp.id}`}>{opp.name}</Link> : "Winner of the previous round"}
            </div>
          </div>
        </div>
      </Card>
    );
  }
  return null;
}

function NextGameCard({ L }: { L: League }) {
  const g = nextGame(L, L.userTid);
  const ut = team(L, L.userTid);
  if (!g && (L.phase === "confTourney" || L.phase === "ncaa" || L.phase === "selection")) {
    const bn = BracketNext({ L });
    if (bn) return bn;
  }
  if (!g) {
    const s = curSeason(ut);
    return (
      <Card title="Season">
        <div className="row gap-16">
          <Logo team={ut} size={56} />
          <div>
            <div className="bold" style={{ fontSize: 18 }}>
              {s.w}-{s.l} ({s.cw}-{s.cl} conf)
            </div>
            <div className="muted">
              {s.post
                ? `${s.post.event.toUpperCase()}: ${s.post.result}${s.post.event === "ncaa" ? ` (${s.post.seed} seed)` : ""}`
                : L.phase === "preseason"
                  ? "The season hasn't started."
                  : s.confTourney && s.confTourney !== "Champion"
                    ? `Conference tournament: ${s.confTourney === "Did not qualify" ? "did not qualify" : `out in the ${s.confTourney.toLowerCase()}`}. Waiting on Selection Sunday.`
                    : "No games scheduled."}
            </div>
          </div>
        </div>
      </Card>
    );
  }
  const v = gameView(g, L.userTid);
  const opp = team(L, v.opp);
  const os = curSeason(opp);
  const us = curSeason(ut);
  const or = currentRank(L, opp.id);
  const ur = currentRank(L, ut.id);
  return (
    <Card title="Next Game" sub={`${shortDayLabel(L.season, g.day)} · ${g.event ?? (g.type === "conf" ? "Conference game" : g.type === "nc" ? "Non-conference" : "Postseason")}`} right={<Link to={`/l/${L.id}/team/${opp.id}`} className="btn btn-sm">Scout opponent</Link>}>
      <div className="row" style={{ justifyContent: "space-around", padding: "6px 0" }}>
        <div className="col center" style={{ alignItems: "center" }}>
          <Logo team={ut} size={60} />
          <div className="bold">
            {ur ? <span className="muted">#{ur} </span> : null}
            {ut.name}
          </div>
          <div className="muted small">
            {us.w}-{us.l}
          </div>
        </div>
        <div className="center">
          <div style={{ fontSize: 22, fontWeight: 800 }}>{v.loc === "N" ? "vs" : v.home ? "vs" : "@"}</div>
          <div className="muted small">{v.loc === "N" ? "Neutral site" : v.home ? "Home" : "Away"}</div>
        </div>
        <div className="col center" style={{ alignItems: "center" }}>
          <Logo team={opp} size={60} />
          <div className="bold">
            {or ? <span className="muted">#{or} </span> : null}
            <Link to={`/l/${L.id}/team/${opp.id}`}>{opp.name}</Link>
          </div>
          <div className="muted small">
            {os.w}-{os.l} · Power {L.power[opp.id]?.power.toFixed(1)}
          </div>
        </div>
      </div>
    </Card>
  );
}

export function Dashboard() {
  const L = useLeague();
  const ut = team(L, L.userTid);
  const s = curSeason(ut);
  const pr = powerRanks(L);
  const ch = coach(L, L.userCid)!;
  const rows = standingsRows(L, ut.cid);
  const poll = currentPoll(L);
  const leaders = teamLeaders(L, ut.id);
  const recent = lastGames(L, ut.id, 6);
  const cr = classRankings(L).find((x) => x.tid === ut.id);
  const commits = commitsFor(L, ut.id).filter((p) => p.recruit?.kind === "hs");
  const news = L.news.filter((n) => n.user).slice(0, 7);
  const spots = openSpots(L, ut.id);
  const secColor = ch.security >= 60 ? "var(--good)" : ch.security >= 30 ? "var(--warn)" : "var(--bad)";
  return (
    <div className="col gap-16">
      <div className="card">
        <div className="stat-row">
          <div className="stat">
            <div className="label">Record</div>
            <div className="value">
              {s.w}-{s.l}
              <small>{s.cw}-{s.cl} conf</small>
            </div>
          </div>
          <div className="stat">
            <div className="label">AP Poll</div>
            <div className="value">{currentRank(L, ut.id) ? `#${currentRank(L, ut.id)}` : "NR"}</div>
          </div>
          <div className="stat">
            <div className="label">Power Rank</div>
            <div className="value">
              {pr.get(ut.id)}
              <small>of {L.teams.length}</small>
            </div>
          </div>
          <div className="stat">
            <div className="label">Prestige</div>
            <div className="value" style={{ fontSize: 16, paddingTop: 4 }}>
              <Stars n={prestigeStars(ut.prestige)} />
              <div className="small muted" style={{ fontWeight: 500 }}>
                {prestigeTier(ut.prestige)} ({ut.prestige.toFixed(0)})
              </div>
            </div>
          </div>
          <div className="stat">
            <div className="label">Recruiting Class</div>
            <div className="value">
              {cr && cr.n > 0 ? `#${cr.rank}` : "-"}
              <small>{commits.length} commits</small>
            </div>
          </div>
          <div className="stat" style={{ minWidth: 170 }}>
            <div className="label">Job Security</div>
            <div className="value" style={{ fontSize: 16, paddingTop: 6 }}>
              <Meter value={ch.security} color={secColor} />
              <div className="small muted" style={{ fontWeight: 500, marginTop: 4 }}>
                {ch.security >= 70 ? "Safe" : ch.security >= 45 ? "Stable" : ch.security >= 25 ? "Warm seat" : "Hot seat"}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="grid g-main">
        <div className="col gap-16">
          <NextGameCard L={L} />
          <div className="grid g2">
            <Card title="Recent Results" flush right={<Link to={`/l/${L.id}/schedule`} className="btn btn-sm btn-ghost">Schedule</Link>}>
              {recent.length ? (
                <table className="tbl compact">
                  <tbody>
                    {recent.map((g) => {
                      const v = gameView(g, ut.id);
                      return (
                        <tr key={g.id}>
                          <td className="muted small">{shortDayLabel(L.season, g.day)}</td>
                          <td className="small muted">{v.loc === "N" ? "vs" : v.home ? "vs" : "@"}</td>
                          <td>
                            <TeamLink L={L} tid={v.opp} size={18} rank={null} />
                          </td>
                          <td className="n">
                            <Link to={`/l/${L.id}/game/${g.id}`} className={v.won ? "good bold" : "bad bold"}>
                              {v.won ? "W" : "L"} {v.us}-{v.them}
                              {g.ot ? " OT" : ""}
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              ) : (
                <div className="empty">No games played yet.</div>
              )}
            </Card>
            <Card title="Team Leaders" flush>
              {leaders.pts ? (
                <table className="tbl compact">
                  <tbody>
                    {(
                      [
                        ["Points", leaders.pts, (x: typeof leaders.pts) => x.s.pts / x.s.g],
                        ["Rebounds", leaders.reb, (x: typeof leaders.pts) => (x.s.orb + x.s.drb) / x.s.g],
                        ["Assists", leaders.ast, (x: typeof leaders.pts) => x.s.ast / x.s.g],
                        ["Steals", leaders.stl, (x: typeof leaders.pts) => x.s.stl / x.s.g],
                        ["Blocks", leaders.blk, (x: typeof leaders.pts) => x.s.blk / x.s.g],
                      ] as const
                    ).map(([label, x, f]) =>
                      x ? (
                        <tr key={label}>
                          <td className="muted">{label}</td>
                          <td>
                            <PlayerLink L={L} p={x.p} face size={24} colors={ut.colors} />
                          </td>
                          <td className="n bold">{f1(f(x))}</td>
                        </tr>
                      ) : null,
                    )}
                  </tbody>
                </table>
              ) : (
                <div className="empty">Stats appear once games are played.</div>
              )}
            </Card>
          </div>
          <Card title="Inbox" flush right={<Link to={`/l/${L.id}/inbox`} className="btn btn-sm btn-ghost">All news</Link>}>
            {news.length ? (
              news.map((n) => (
                <div key={n.id} className={`news-item ${n.read ? "" : "unread"}`}>
                  <span className="news-kind" style={{ background: KIND_COLORS[n.kind] }} />
                  <div style={{ flex: 1 }}>
                    {n.gid ? <Link to={`/l/${L.id}/game/${n.gid}`}>{n.text}</Link> : n.pid ? <Link to={`/l/${L.id}/player/${n.pid}`}>{n.text}</Link> : n.text}
                    <div className="tiny faint">{n.dateLabel}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty">No news yet.</div>
            )}
          </Card>
        </div>
        <div className="col gap-16">
          <Guide L={L} />
          <Card title={`${L.conferences[ut.cid].short} Standings`} flush right={<Link to={`/l/${L.id}/standings`} className="btn btn-sm btn-ghost">Full</Link>}>
            <table className="tbl compact">
              <thead>
                <tr>
                  <th />
                  <th>Team</th>
                  <th className="n">Conf</th>
                  <th className="n">All</th>
                  <th className="n">Strk</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.t.id} className={r.t.id === ut.id ? "hl" : ""}>
                    <td className="muted">{r.pos}</td>
                    <td>
                      <TeamLink L={L} tid={r.t.id} size={18} short rank={currentRank(L, r.t.id)} />
                    </td>
                    <td className="n">
                      {r.s.cw}-{r.s.cl}
                    </td>
                    <td className="n">
                      {r.s.w}-{r.s.l}
                    </td>
                    <td className="n muted">{streakStr(r.s.streak)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
          <Card title={poll ? `AP Top 25 · ${poll.label}` : "AP Top 25"} flush right={<Link to={`/l/${L.id}/rankings`} className="btn btn-sm btn-ghost">More</Link>}>
            {poll ? (
              <table className="tbl compact">
                <tbody>
                  {poll.ranks.slice(0, 12).map((r) => (
                    <tr key={r.tid} className={r.tid === ut.id ? "hl" : ""}>
                      <td className="muted" style={{ width: 24 }}>
                        {r.rank}
                      </td>
                      <td>
                        <TeamLink L={L} tid={r.tid} size={18} short />
                      </td>
                      <td className="n muted">
                        {r.w}-{r.l}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty">No poll yet.</div>
            )}
          </Card>
          <Card title="Recruiting" right={<Link to={`/l/${L.id}/targets`} className="btn btn-sm btn-ghost">Targets</Link>}>
            <dl className="kv">
              <dt>Points this week</dt>
              <dd>
                {L.recruitPts} / {L.recruitPtsMax}
              </dd>
              <dt>Open spots</dt>
              <dd>{spots}</dd>
              <dt>Commits</dt>
              <dd>{commits.length ? commits.map((p) => `${p.recruit!.stars}★`).join(" ") : "None yet"}</dd>
              <dt>Roster</dt>
              <dd>
                {roster(L, ut.id).length} / {L.settings.rosterMax}
              </dd>
            </dl>
          </Card>
          <Card title="Coach">
            <div className="row">
              <div style={{ flex: 1 }}>
                <div className="bold">
                  {ch.first} {ch.last}
                </div>
                <div className="small muted">
                  {L.season - ch.hired + 1}
                  {ordinal(L.season - ch.hired + 1).slice(-2)} season at {ut.name} · Rep {Math.round(ch.rep)}
                </div>
              </div>
              <Link to={`/l/${L.id}/coach`} className="btn btn-sm">
                Career
              </Link>
            </div>
          </Card>
        </div>
      </div>
      <div className="faint small">{seasonLabel(L.season)}</div>
    </div>
  );
}
