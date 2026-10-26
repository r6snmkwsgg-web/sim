import { Link } from "react-router-dom";
import { useLeague } from "../store";
import { Card, PageHead } from "../components/common";

export function Guide() {
  const L = useLeague();
  const b = `/l/${L.id}`;
  return (
    <div>
      <PageHead title="How to Play" sub="Build a program that wins for decades. Everything that happens is kept forever." />
      <Card title="Getting around" className="mb-16">
        <ul className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.7 }}>
          <li>
            Five sections live on the left (along the bottom on a phone): <b>Home</b>, <b>My Team</b>, <b>Recruiting</b>, <b>League</b> and <b>History</b>. Each one opens where you left it.
          </li>
          <li>The tabs under the top bar are the pages in that section. On a team, player or game page, the Back button takes you where you came from.</li>
          <li>
            Press <kbd>/</kbd> (or tap the search button) and type a team, a player or a page name, like "standings", "bracket" or "draft".
          </li>
          <li>The big button in the top right always does the next thing: play your next game, start the tournament, open the portal. The arrow beside it has more sim options.</li>
          <li>Your coaching points are always in the top bar (the lightning bolt). Spend them on recruits or on Game Prep; they reset every Monday.</li>
          <li>Each season you get goals on the dashboard. Hit them for rewards: extra weekly points, prestige or job security. Big wins, buzzer-beaters, commitments and March runs pop up as they happen.</li>
        </ul>
      </Card>
      <div className="grid g2">
        <Card title="The season">
          <ol className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.7 }}>
            <li>
              <b>Preseason:</b> set your <Link to={`${b}/rotation`}>rotation</Link>, <Link to={`${b}/tactics`}>tactics</Link> and redshirts. It's also the fall recruiting week: offers and official visits are open.
            </li>
            <li>
              <b>Regular season:</b> about 31 games: non-conference from November, including a Thanksgiving-week event (Maui, Battle 4 Atlantis and more) where you play three games (two in a four-team event), then the conference schedule. Home court matters.
            </li>
            <li>
              <b>Conference tournaments:</b> the winners get automatic NCAA bids. Every bracket lives under <Link to={`${b}/tournaments`}>Tournaments</Link>: the NCAA Tournament, all 32 conference tournaments, the NIT and CBI, and the early-season events.
            </li>
            <li>
              <b>Selection Sunday:</b> at-large teams are picked on power rating and resume (quality wins, bad losses). The next teams go to the NIT and CBI.
            </li>
            <li>
              <b>Postseason:</b> First Four, then Round of 64 through the title game.
            </li>
            <li>
              <b>Offseason:</b> awards → coaching carousel (job offers, firings, realignment) → NBA Draft and graduation → transfer portal (4 windows) → signing day → players develop → new season.
            </li>
          </ol>
        </Card>
        <Card title="Recruiting">
          <ul className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.7 }}>
            <li>You get coaching points every week: about 85 at the smallest programs up to about 115 at blue bloods, plus a little for a good recruiter. They reset on Mondays and don't carry over, so spend them: on recruits, or on <Link to={`${b}/prep`}>Game Prep</Link> to scout your next opponent (about +1 to +2.5 points in that game).</li>
            <li>Every recruit weighs playing time, prestige, distance from home, contender status, the head coach, facilities and NIL. Your fit multiplies every action.</li>
            <li>
              <b>Scout</b> to see his ratings in seven categories (shooting, finishing, playmaking, perimeter D, interior D, rebounding, athleticism). Game film (2 pts) shows one at random and scouting a game (5 pts) shows the one you pick, each once a week per recruit; talking to his coach (3 pts, once) tells you his work ethic and potential. Star ratings are noisy, so there are hidden gems (and busts).
            </li>
            <li>Recruiting goes year-round. Each new class arrives after a summer on the circuit: programs have already called, visited and offered the kids they like, and your staff has made contact with some realistic targets (offers, NIL and official visits are left to you). Summer contact gets a school as far as Hot; nobody commits before the season. The preseason is the fall recruiting week, then the high school season tips off with yours.</li>
            <li>The new class is unrated until the start of week 3: no stars or national rankings for anyone, so go by high school and summer stats and your own scouting. Recruits don't narrow their lists until the rankings show them their market. If a kid turns out bigger than his buzz and you'd already offered him and were Hot with him, he keeps taking you seriously: bigger programs will still come after him, but you're in the race.</li>
            <li>
              Reading the numbers: high school stats say who can score, not who the five-stars are. A star on a loaded prep team might average 14 while a small-town kid in a weak league puts up 30, and a weak league pads field-goal percentage too. Free-throw percentage is the honest one. The summer circuit (the board's Summer view) is better evidence: the national circuit puts the best prospects against each other, so numbers there run lower but mean more, while regional numbers come easier. Summers are short, so their percentages bounce around.
            </li>
            <li>The heat meter shows how close a recruit is to committing to each school: Cold, Warm, Hot, Ready to commit. NIL offers ask you to confirm before they go out.</li>
            <li>Each recruit has his own decision week (shown on his profile). From then on he commits to a school that offered him and is Ready to commit, usually the one furthest ahead; several schools can be Ready at once. The longer he waits, the less it takes.</li>
            <li>The AI programs recruit under the same rules and points. Their moves (and recruits' decisions) happen at the start of each week, so what you do during the week counts before they decide.</li>
            <li>Recruits narrow their list to a top five, then commit to a school that has offered. Verbal commitments can flip until they sign (early signing period in week 3, or signing day).</li>
            <li>Official visits are the biggest boost and are limited each season. One opens once a recruit is Hot on you (halfway to committing), so they close the deal rather than open it.</li>
            <li>Open roster spots depend on who's returning. Projected NBA early entries count as departures.</li>
            <li>
              Don't want to manage recruiting? Turn on <Link to={`${b}/settings`}>auto recruiting</Link> and your staff will handle it (about as well as an average AI program).
            </li>
          </ul>
        </Card>
        <Card title="Players & development">
          <ul className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.7 }}>
            <li>Ratings run 1-99. OVR and POT are shown as letter grades (C is a typical D1 rotation player; A is an All-American).</li>
            <li>
              Players grow every week through <Link to={`${b}/practice`}>practice</Link> (team focus, intensity, individual focus) and jump in the offseason. Minutes, work ethic and your development skill all help.
            </li>
            <li>Redshirting keeps a year of eligibility. Players have 4 seasons to play within 5 years.</li>
            <li>Unhappy players (no minutes, a coaching change, a star at a small school) may enter the transfer portal. You can release players in the offseason.</li>
          </ul>
        </Card>
        <Card title="Prestige, jobs & legacy">
          <ul className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.7 }}>
            <li>Program prestige rises with sustained power, tournament runs, titles and great classes. Tiers: Rebuild → Low-Major → Mid-Major → Solid → Power Program → Elite → Blue Blood.</li>
            <li>Rising mid-majors can be invited to stronger conferences (realignment).</li>
            <li>Job security reflects results against expectations. Success brings offers from bigger programs; you can stay and build, or move up.</li>
            <li>
              History is permanent: <Link to={`${b}/program`}>program history</Link>, past rosters and stats, every box score, brackets, awards, the <Link to={`${b}/records`}>record book</Link>, and the draft and transfer logs.
            </li>
          </ul>
        </Card>
        <Card title="Saving">
          <p className="small" style={{ margin: 0 }}>
            The game saves automatically after every sim and edit, and with cloud saves on it also uploads your leagues a few minutes after you play. To play on another device, open <Link to={`${b}/settings`}>Settings → Cloud saves</Link> and use your save code or link there. You can also export a backup file.
          </p>
        </Card>
      </div>
    </div>
  );
}
