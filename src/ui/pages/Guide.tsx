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
        </ul>
      </Card>
      <div className="grid g2">
        <Card title="The season">
          <ol className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.7 }}>
            <li>
              <b>Preseason:</b> set your <Link to={`${b}/rotation`}>rotation</Link>, <Link to={`${b}/tactics`}>tactics</Link> and redshirts, and start recruiting.
            </li>
            <li>
              <b>Regular season:</b> about 31 games: non-conference from November, then the conference schedule. Home court matters.
            </li>
            <li>
              <b>Conference tournaments:</b> the winners get automatic NCAA bids.
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
            <li>You get recruiting points every week. They reset on Mondays and don't carry over, so spend them.</li>
            <li>Every recruit weighs playing time, prestige, distance from home, contender status, the head coach, facilities and NIL. Your fit multiplies every action.</li>
            <li>
              <b>Scout</b> to see true ratings. Star ratings are noisy, so there are hidden gems (and busts).
            </li>
            <li>Recruits narrow their list to a top five, then commit to a school that has offered. Verbal commitments can flip until they sign (early signing period in week 3, or signing day).</li>
            <li>Official visits are limited each season. Use them on players you can actually land.</li>
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
