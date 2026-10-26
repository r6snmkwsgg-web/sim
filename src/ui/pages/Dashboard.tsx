import { Link } from "react-router-dom";
import { useLeague, useSim } from "../store";
import { canWatchNext, useWatchNext } from "../components/Layout";
import { coach, roster, seasonLabel, shortDayLabel, team, PHASE_LABEL } from "../../engine/core";
import { isEvent } from "../../engine/postseason";
import { curSeason } from "../../engine/play";
import { PREP_LEVELS, currentPrep } from "../../engine/prep";
import { goalProgress } from "../../engine/goals";
import { expectations } from "../../engine/coaches";
import { currentPoll, currentRank, powerRanks } from "../../engine/rankings";
import { prestigeStars, prestigeTier } from "../../engine/ratings";
import { classRankings, commitsFor, openSpots } from "../../engine/recruiting";
import { Card, FormStrip, heroStyle, Logo, Meter, Stars, TeamLink } from "../components/common";
import { Face } from "../components/Face";
import { Icon } from "../components/Icons";
import { gameView, KIND_COLORS, lastGames, nextGame, standingsRows, streakStr, teamLeaders } from "../helpers";
import { f1, ordinal } from "../util";
import type { League } from "../../engine/types";

const KIND_ICON: Record<string, string> = {
  game: "ball",
  recruit: "recruit",
  injury: "heart",
  award: "awards",
  poll: "rankings",
  job: "coach",
  portal: "portal",
  draft: "draft",
  league: "history",
  milestone: "crown",
  team: "team",
};

function Guide({ L }: { L: League }) {
  const base = `/l/${L.id}`;
  const items: Record<League["phase"], { text: string; to?: string; link?: string }[]> = {
    preseason: [
      { text: "Set your rotation and starters", to: `${base}/rotation`, link: "Rotation" },
      { text: "Choose a team strategy and player tendencies", to: `${base}/tactics`, link: "Tactics" },
      { text: "Redshirt freshmen who won't play", to: `${base}/roster`, link: "Roster" },
      { text: "Spend this week's coaching points on recruits", to: `${base}/recruiting`, link: "Recruiting" },
    ],
    regular: [
      { text: "Spend coaching points every week (they reset each Monday) on recruits", to: `${base}/targets`, link: "Targets" },
      { text: "Or scout your next opponent with them for an edge in the game", to: `${base}/prep`, link: "Game Prep" },
      { text: "Adjust practice focus to develop your players", to: `${base}/practice`, link: "Practice" },
      { text: "Check your NCAA Tournament resume", to: `${base}/rankings`, link: "Rankings" },
    ],
    confTourney: [
      { text: "Win your conference tournament to clinch an automatic bid", to: `${base}/conf-tourneys`, link: "Brackets" },
      { text: "Scout each opponent with your coaching points", to: `${base}/prep`, link: "Game Prep" },
    ],
    selection: [{ text: "The brackets are out. See where you landed", to: `${base}/tournaments`, link: "Tournaments" }],
    ncaa: [
      { text: "Survive and advance", to: `${base}/tournaments`, link: "Bracket" },
      { text: "Big game? Spend coaching points on a full game plan", to: `${base}/prep`, link: "Game Prep" },
    ],
    seasonEnd: [
      { text: "Review the season and awards", to: `${base}/season-review`, link: "Review" },
      { text: "Next: the coaching carousel and possible job offers" },
    ],
    carousel: [{ text: "Consider job offers or stay put", to: `${base}/coach`, link: "Coach & Jobs" }],
    draft: [{ text: "See who left for the NBA and who graduated", to: `${base}/draft`, link: "NBA Draft" }],
    portal: [
      { text: "Recruit transfers to fill open spots", to: `${base}/portal`, link: "Portal" },
      { text: "Re-recruit your own players who entered the portal" },
      { text: "Unsigned high school recruits are still available", to: `${base}/recruiting`, link: "Recruiting" },
    ],
    signing: [{ text: "Finalize next season's roster", to: `${base}/signing`, link: "Signing Day" }],
  };
  return (
    <Card title="To do">
      <div className="col gap-12">
        {items[L.phase].map((x, i) => (
          <div key={i} className="row" style={{ gap: 10 }}>
            <span className="todo-n">{i + 1}</span>
            <span style={{ flex: 1, lineHeight: 1.35 }}>{x.text}</span>
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

/** This season's goals, their progress and rewards. */
function GoalsCard({ L }: { L: League }) {
  const goals = L.goals?.season === L.season ? L.goals.list : [];
  if (!goals.length) return null;
  const done = goals.filter((g) => g.done).length;
  return (
    <Card title="Season goals" sub={`${done} of ${goals.length} complete · rewards pay out the moment you hit them`}>
      <div className="col" style={{ gap: 10 }}>
        {goals.map((g) => {
          const [cur, max] = goalProgress(L, g);
          return (
            <div key={g.id} className={`goal${g.done ? " done" : g.failed ? " failed" : ""}`}>
              <span className="goal-ic">
                <Icon name={g.done ? "check" : g.failed ? "x" : g.stretch ? "fire" : "star"} size={14} />
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="row" style={{ gap: 6 }}>
                  <b>{g.text}</b>
                  {g.stretch && <span className="badge gold">Stretch</span>}
                </div>
                <div className="tiny muted">{g.done ? `Earned: ${g.reward.text}` : g.failed ? "Missed this season" : `Reward: ${g.reward.text}`}</div>
                {!g.done && !g.failed && max > 1 && (
                  <div className="row" style={{ gap: 8, marginTop: 5 }}>
                    <div style={{ flex: 1 }}>
                      <Meter value={(100 * cur) / max} color="var(--accent-ink)" />
                    </div>
                    <span className="tiny bold">
                      {cur}/{max}
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

/** Everything the program has won, at a glance. */
function TrophyCase({ L }: { L: League }) {
  const t = team(L, L.userTid);
  const ss = t.seasons;
  const deep = (r: string | undefined) => !!r && ["Final Four", "Championship", "Runner-up", "Champion"].includes(r);
  const items: [string, string, number][] = [
    ["crown", "National titles", ss.filter((s) => s.post?.event === "ncaa" && s.post.result === "Champion").length],
    ["awards", "Final Fours", ss.filter((s) => s.post?.event === "ncaa" && deep(s.post.result)).length],
    ["bracket", "NCAA bids", ss.filter((s) => s.post?.event === "ncaa").length],
    ["standings", "Conference titles", ss.filter((s) => s.confChamp).length],
    ["records", "Tournament titles", ss.filter((s) => s.confTourney === "Champion").length],
    ["star", "Goals hit", L.goalsDone ?? 0],
  ];
  return (
    <Card title="Trophy case" right={<Link to={`/l/${L.id}/program`} className="btn btn-sm btn-ghost">History</Link>}>
      <div className="trophies">
        {items.map(([ic, label, n]) => (
          <div key={label} className={`trophy${n ? " won" : ""}`}>
            <Icon name={ic} size={18} />
            <b>{n}</b>
            <span>{label}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

/** Opens Game Prep; shows what's been bought for the next game. */
function PrepButton({ L }: { L: League }) {
  const lvl = currentPrep(L);
  return (
    <Link to={`/l/${L.id}/prep`} className="btn btn-sm btn-glass" title="Spend coaching points scouting this opponent">
      <Icon name={lvl ? "check" : "eye"} size={13} /> {lvl ? PREP_LEVELS[lvl].name : "Game prep"}
    </Link>
  );
}

/** The right side of the hero: the next game, the next bracket game, or the season summary. */
function NextUp({ L }: { L: League }) {
  const ut = team(L, L.userTid);
  const watchNext = useWatchNext();
  const sim = useSim();
  const watchBtn = canWatchNext(L) ? (
    <button className="btn btn-sm btn-white" disabled={sim.running} onClick={() => void watchNext()}>
      <Icon name="tv" size={13} /> Watch live
    </button>
  ) : null;
  const g = nextGame(L, L.userTid);
  if (g) {
    const v = gameView(g, L.userTid);
    const opp = team(L, v.opp);
    const os = curSeason(opp);
    const or = currentRank(L, opp.id);
    const where = v.loc === "N" ? "Neutral site" : v.home ? "Home" : "Away";
    const label = g.event ?? (g.type === "conf" ? "Conference" : g.type === "nc" ? "Non-conference" : "Postseason");
    return (
      <div className="next-panel">
        <div className="hero-kicker">
          Next game · {shortDayLabel(L.season, g.day)} · {where}
        </div>
        <div className="row" style={{ gap: 14, marginTop: 10 }}>
          <Logo team={opp} size={60} />
          <div style={{ minWidth: 0 }}>
            <div className="np-opp ellipsis">
              <span style={{ opacity: 0.7 }}>{v.loc === "A" ? "at " : "vs "}</span>
              {or ? <span style={{ opacity: 0.8 }}>#{or} </span> : null}
              {opp.name}
            </div>
            <div className="small" style={{ opacity: 0.85 }}>
              {os.w}-{os.l} · {L.conferences[opp.cid].short} · {label}
            </div>
          </div>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          {watchBtn}
          <PrepButton L={L} />
          <Link to={`/l/${L.id}/schedule`} className="btn btn-sm btn-glass">
            <Icon name="schedule" size={13} /> Schedule
          </Link>
        </div>
      </div>
    );
  }
  for (const br of L.brackets) {
    if (br.champion !== null) continue;
    const bg = br.games.find((x) => x.winner === null && (x.a === L.userTid || x.b === L.userTid));
    if (!bg) continue;
    const oppId = bg.a === L.userTid ? bg.b : bg.a;
    const opp = oppId !== null ? team(L, oppId) : null;
    const day = bg.round < 0 ? br.playinDay : br.days[bg.round];
    const round = bg.round < 0 ? br.playinName : br.rounds[bg.round];
    const mySeed = bg.a === L.userTid ? bg.sa : bg.sb;
    const oppSeed = bg.a === L.userTid ? bg.sb : bg.sa;
    return (
      <div className="next-panel">
        <div className="hero-kicker">
          {br.name} · {round}
          {day !== undefined ? ` · ${shortDayLabel(L.season, day)}` : ""}
        </div>
        <div className="row" style={{ gap: 14, marginTop: 10 }}>
          <Logo team={opp ?? undefined} size={60} />
          <div style={{ minWidth: 0 }}>
            <div className="np-opp ellipsis">
              {opp ? (
                <>
                  <span style={{ opacity: 0.7 }}>vs </span>
                  {oppSeed ? <span style={{ opacity: 0.8 }}>({oppSeed}) </span> : null}
                  {opp.name}
                </>
              ) : (
                "Opponent TBD"
              )}
            </div>
            <div className="small" style={{ opacity: 0.85 }}>{mySeed ? `You're the ${mySeed} seed` : "Win and advance"}</div>
          </div>
        </div>
        <div className="row" style={{ marginTop: 12 }}>
          {watchBtn}
          <Link to={`/l/${L.id}/${isEvent(br) ? "events" : br.key.startsWith("conf:") ? "conf-tourneys" : br.key === "ncaa" ? "tournaments" : "nit"}`} className="btn btn-sm btn-glass">
            <Icon name="bracket" size={13} /> Bracket
          </Link>
          {opp && <PrepButton L={L} />}
        </div>
      </div>
    );
  }
  const s = curSeason(ut);
  const line = s.post
    ? `${s.post.event.toUpperCase()}: ${s.post.result}${s.post.event === "ncaa" ? ` (${s.post.seed} seed)` : ""}`
    : L.phase === "preseason"
      ? "Tip-off is coming. Set your rotation and start recruiting."
      : s.confTourney && s.confTourney !== "Champion"
        ? `Conference tournament: ${s.confTourney === "Did not qualify" ? "did not qualify" : `out in the ${s.confTourney.toLowerCase()}`}. ${L.phase === "confTourney" || L.phase === "selection" ? "Waiting on Selection Sunday." : "No postseason bid this year."}`
        : PHASE_LABEL[L.phase];
  return (
    <div className="next-panel">
      <div className="hero-kicker">{L.phase === "preseason" ? "Preseason" : "Season"}</div>
      <div className="np-opp" style={{ marginTop: 8 }}>
        {s.w}-{s.l}
        <span style={{ opacity: 0.7, fontSize: 18, marginLeft: 8 }}>
          {s.cw}-{s.cl} conf
        </span>
      </div>
      <div className="small" style={{ opacity: 0.88, marginTop: 4, maxWidth: 300 }}>
        {line}
      </div>
    </div>
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
  const news = L.news.filter((n) => n.user).slice(0, 6);
  const spots = openSpots(L, ut.id);
  const rank = currentRank(L, ut.id);
  const exp = expectations(s.prestigeStart ?? ut.prestige);
  const secColor = ch.security >= 60 ? "var(--ga)" : ch.security >= 30 ? "var(--gc)" : "var(--gf)";
  const secLabel = ch.security >= 70 ? "Safe" : ch.security >= 45 ? "Stable" : ch.security >= 25 ? "Warm seat" : "Hot seat";
  const yr = L.season - ch.hired + 1;
  const leaderCards = [
    ["Points", leaders.pts, (x: NonNullable<typeof leaders.pts>) => x.s.pts / x.s.g],
    ["Rebounds", leaders.reb, (x: NonNullable<typeof leaders.pts>) => (x.s.orb + x.s.drb) / x.s.g],
    ["Assists", leaders.ast, (x: NonNullable<typeof leaders.pts>) => x.s.ast / x.s.g],
    ["Steals", leaders.stl, (x: NonNullable<typeof leaders.pts>) => x.s.stl / x.s.g],
    ["Blocks", leaders.blk, (x: NonNullable<typeof leaders.pts>) => x.s.blk / x.s.g],
  ] as const;
  return (
    <div className="col gap-16">
      <div className="hero-banner" style={heroStyle(ut.colors)}>
        <div className="hero-inner">
          <Logo team={ut} size={108} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="hero-kicker">
              {seasonLabel(L.season)} · {L.conferences[ut.cid].name} · {PHASE_LABEL[L.phase]}
            </div>
            <div className="hero-title" style={{ marginTop: 6 }}>
              {ut.name}
              <br />
              <span style={{ opacity: 0.85 }}>{ut.mascot}</span>
            </div>
            <div className="row-wrap" style={{ marginTop: 12, gap: 8 }}>
              <span className="chip-light">
                <Stars n={prestigeStars(ut.prestige)} /> {prestigeTier(ut.prestige)}
              </span>
              <span className="chip-light">
                <Icon name="coach" size={13} /> Coach {ch.last} · {ordinal(yr)} season
              </span>
              <span className="chip-light">
                <Icon name="pin" size={13} /> {ut.city}, {ut.state}
              </span>
            </div>
          </div>
          <NextUp L={L} />
        </div>
        <div className="hero-stats">
          <div>
            <div className="label">Record</div>
            <div className="value">
              {s.w}-{s.l}
              <small>{s.cw}-{s.cl} conf</small>
            </div>
          </div>
          <div>
            <div className="label">AP Poll</div>
            <div className="value">{rank ? `#${rank}` : "NR"}</div>
          </div>
          <div>
            <div className="label">Power</div>
            <div className="value">
              {ordinal(pr.get(ut.id) ?? 0)}
              <small>of {L.teams.length}</small>
            </div>
          </div>
          <div>
            <div className="label">Last 5</div>
            <div className="value" style={{ paddingTop: 3 }}>
              <FormStrip results={recent.map((g) => gameView(g, ut.id).won)} />
            </div>
          </div>
          <div>
            <div className="label">Streak</div>
            <div className="value">{streakStr(s.streak)}</div>
          </div>
          <div>
            <div className="label">Recruiting class</div>
            <div className="value">
              {cr && cr.n > 0 ? `#${cr.rank}` : "-"}
              <small>
                {commits.length} commit{commits.length === 1 ? "" : "s"}
              </small>
            </div>
          </div>
        </div>
      </div>

      <div className="grid g-main">
        <div className="col gap-16">
          <Card title="Team Leaders" right={<Link to={`/l/${L.id}/roster`} className="btn btn-sm btn-ghost">Roster</Link>}>
            {leaders.pts ? (
              <div className="grid g5" style={{ gap: 10 }}>
                {leaderCards.map(([label, x, f]) =>
                  x ? (
                    <Link key={label} to={`/l/${L.id}/player/${x.p.id}`} className="leader">
                      <Face seed={x.p.faceSeed} race={x.p.race} colors={ut.colors} size={66} />
                      <div className="leader-v">{f1(f(x))}</div>
                      <div className="leader-l">{label}</div>
                      <div className="leader-n ellipsis">
                        {x.p.first[0]}. {x.p.last}
                      </div>
                    </Link>
                  ) : (
                    <div key={label} />
                  ),
                )}
              </div>
            ) : (
              <div className="empty" style={{ padding: 14 }}>
                Stats appear once games are played.
              </div>
            )}
          </Card>
          <div className="grid g2">
            <Card title="Recent Results" flush right={<Link to={`/l/${L.id}/schedule`} className="btn btn-sm btn-ghost">Schedule</Link>}>
              {recent.length ? (
                <div>
                  {recent.map((g) => {
                    const v = gameView(g, ut.id);
                    const opp = team(L, v.opp);
                    return (
                      <Link key={g.id} to={`/l/${L.id}/game/${g.id}`} className="res-row">
                        <span className={`res-wl ${v.won ? "w" : "l"}`}>{v.won ? "W" : "L"}</span>
                        <Logo team={opp} size={24} />
                        <span className="ellipsis" style={{ flex: 1 }}>
                          <span className="faint small">{v.loc === "N" ? "vs " : v.home ? "vs " : "@ "}</span>
                          <b>{opp.name}</b>
                        </span>
                        <span className="res-score">
                          {v.us}-{v.them}
                          {g.ot ? <span className="faint small"> OT</span> : null}
                        </span>
                        <span className="faint small" style={{ width: 48, textAlign: "right" }}>
                          {shortDayLabel(L.season, g.day)}
                        </span>
                      </Link>
                    );
                  })}
                </div>
              ) : (
                <div className="empty">No games played yet.</div>
              )}
            </Card>
            <Card title="Inbox" flush right={<Link to={`/l/${L.id}/inbox`} className="btn btn-sm btn-ghost">All news</Link>}>
              {news.length ? (
                news.map((n) => (
                  <div key={n.id} className={`news-item ${n.read ? "" : "unread"}`}>
                    <span className="news-ic" style={{ background: `${KIND_COLORS[n.kind]}22`, color: KIND_COLORS[n.kind] }}>
                      <Icon name={KIND_ICON[n.kind] ?? "ball"} />
                    </span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div className="news-text" style={{ lineHeight: 1.35 }}>
                        {n.gid ? <Link to={`/l/${L.id}/game/${n.gid}`}>{n.text}</Link> : n.pid ? <Link to={`/l/${L.id}/player/${n.pid}`}>{n.text}</Link> : n.text}
                      </div>
                      <div className="tiny faint" style={{ marginTop: 2 }}>
                        {n.dateLabel}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty">No news yet.</div>
              )}
            </Card>
          </div>
          <Card title={poll ? `AP Top 25` : "AP Top 25"} sub={poll?.label} flush right={<Link to={`/l/${L.id}/rankings`} className="btn btn-sm btn-ghost">Rankings</Link>}>
            {poll ? (
              <div className="poll-grid">
                {poll.ranks.slice(0, 25).map((r) => (
                  <Link key={r.tid} to={`/l/${L.id}/team/${r.tid}`} className={`poll-row${r.tid === ut.id ? " me" : ""}`}>
                    <span className="poll-rk">{r.rank}</span>
                    <Logo team={team(L, r.tid)} size={22} />
                    <span className="ellipsis" style={{ flex: 1, fontWeight: 600 }}>
                      {team(L, r.tid).name}
                    </span>
                    <span className="faint small num">
                      {r.w}-{r.l}
                    </span>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="empty">The first poll comes out in the preseason.</div>
            )}
          </Card>
        </div>

        <div className="col gap-16">
          <Card title="Your Program">
            <div className="col gap-12">
              <div>
                <div className="row">
                  <span className="muted small bold" style={{ textTransform: "uppercase", letterSpacing: "0.08em", fontSize: 10.5 }}>
                    Job security
                  </span>
                  <span className="spacer" />
                  <span className="bold" style={{ color: secColor }}>
                    {secLabel}
                  </span>
                </div>
                <div style={{ marginTop: 6 }}>
                  <Meter value={ch.security} color={secColor} />
                </div>
              </div>
              <div className="small muted">
                Your boss wants: <b style={{ color: "var(--text)" }}>{exp.goal}</b> (about {exp.wins} wins).
              </div>
              <div className="grid g3" style={{ gap: 8 }}>
                <div className="mini-stat">
                  <span>Roster</span>
                  <b>
                    {roster(L, ut.id).length}/{L.settings.rosterMax}
                  </b>
                </div>
                <div className="mini-stat">
                  <span>Open spots</span>
                  <b>{spots}</b>
                </div>
                <div className="mini-stat">
                  <span>Coach pts</span>
                  <b>
                    {L.recruitPts}/{L.recruitPtsMax}
                  </b>
                </div>
              </div>
              {commits.length > 0 && (
                <div className="row-wrap small">
                  <span className="muted">Commits:</span>
                  {commits.map((p) => (
                    <Link key={p.id} to={`/l/${L.id}/player/${p.id}`} className="pill">
                      {p.recruit!.stars}★ {p.last}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </Card>
          <GoalsCard L={L} />
          <Guide L={L} />
          <TrophyCase L={L} />
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
                    <td className="rk">{r.pos}</td>
                    <td>
                      <TeamLink L={L} tid={r.t.id} size={20} rank={currentRank(L, r.t.id)} />
                    </td>
                    <td className="n bold">
                      {r.s.cw}-{r.s.cl}
                    </td>
                    <td className="n muted">
                      {r.s.w}-{r.s.l}
                    </td>
                    <td className={`n small ${r.s.streak > 0 ? "good" : r.s.streak < 0 ? "bad" : "faint"}`}>{streakStr(r.s.streak)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      </div>
    </div>
  );
}
