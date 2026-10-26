# Hardwood Dynasty

A college basketball program-building game for the browser (desktop or phone), inspired by *Blue Bloods Basketball*. Take any of the 365 Division I programs and turn it from a no-name into a Blue Blood. Recruit, develop players, set tactics, survive March, and build a legacy that's **kept forever**: every season, roster, box score, bracket, award and record stays browsable.

## Play

```bash
npm install
npm run dev        # then open http://localhost:5173
```

For a production build:

```bash
npm run build
npm run preview    # serves dist/ at http://localhost:4173
```

Or build one self-contained file you can double-click to play, no server needed:

```bash
npm run build:single   # writes release/hardwood-dynasty.html
```

Saves live in your browser (IndexedDB) and autosave after every sim and edit. **Cloud saves** also upload your leagues to the Vercel deployment a few minutes after you play and whenever you leave the page. Each browser gets a private save code (Settings → Cloud saves); open the copy link, or enter the code on another device, and your leagues load there. Uploads are incremental (the live league plus only the new history since the last upload), stored in Vercel Blob under a hash of the code. The downloadable single file syncs too, through the deployed API. Use **Settings → Export** to back up a league to a compressed `.hdsave.gz` file (every season, player, box score and record), and **Import Save** on the start screen to restore it on any computer. Saves belong to the browser and the address you play from, so keep using the same one (or export and import when you switch).

Getting around: five sections (Home, My Team, Recruiting, League, History) sit on the left, or along the bottom on a phone, and each section's pages are tabs under the top bar. Team, player and game pages have a Back button. Press `/` or `Ctrl+K` to search for any team, player or page ("standings", "bracket", "draft"). If you'd rather not manage recruiting week to week, turn on auto recruiting in **Settings** and your staff will handle it.

## What's in it

**Look and feel**
- Dark theme by default (light theme in Settings), with the whole interface painted in your program's colors
- Generated badges for all 365 schools, cartoon players, player cards, scoreboards and rafter banners for titles and Final Fours
- Fonts are bundled, so it looks the same on every computer and works offline

**Your program**
- All 365 D1 teams in their 2026-27 conferences (including the rebuilt Pac-12), with school colors and monogram badges
- Rosters of generated players with 15 ratings, archetypes, cartoon faces ([facesjs](https://github.com/zengm-games/facesjs)), hometowns, work ethic and loyalty
- Tactics: tempo, offensive focus, man/zone/press, rebounding, plus per-player shot tendencies (Shoot 3 / Mid-Range / Inside / Drive)
- Rotation: auto, or your own starters and minute targets
- Expectations and job security that scale with your program's prestige
- Practice: team focus, intensity, individual focus; weekly in-season growth and offseason jumps
- Redshirts, releasing players, walk-ons, NIL budgets (each school has its own booster wealth, so a few mid-majors can spend like bigger programs)
- Coaches matter: a great tactician is worth about two points a night, and a great developer grows players noticeably faster, at any level

**The season**
- About 31-game schedules shaped like real ones: real Thanksgiving-week tournaments (Maui, Battle 4 Atlantis and 19 more), 8-team events over three days with consolation and placement games and 4-team events over two, all on neutral floors; December challenge games and holiday showcases against peers; big schools hosting smaller ones
- A possession-by-possession game engine calibrated to real D1 averages (pace, shooting splits, free throws, turnovers, rebounding, blocks, steals, assists, fouls, home-court edge, overtime rate, game-to-game variance), with fatigue, foul trouble, substitutions, score effects and real end-of-game decisions (holding for the last shot, fouling when the shot clock is off, needing a three)
- Watch your games live: a scoreboard, a shot chart on a full court, a live box score, a game-flow chart you can click to rewind, and the play-by-play, at 1x to 8x speed. The result stays hidden until the final buzzer
- Box scores and play-by-play for your games
- Weekly AP-style Top 25, opponent-adjusted power ratings, bracketology
- Conference tournaments (the Patriot, America East, NEC, ASUN and early Horizon rounds are on campus, like the real ones), Selection Sunday with a Quad 1-minded committee, NCAA Tournament (64, 68 with First Four, or 76), NIT and CBI
- Awards: national and conference Player of the Year, Defensive POY, Freshman, Sixth Man, Most Improved, Coach of the Year, All-America and All-Conference teams, Final Four MOP

**Goals, moments and Game Prep**
- Season goals sized to your program (wins, the conference race, a recruit, a stretch goal) with rewards paid the moment you hit them: extra weekly coaching points, prestige or job security; a trophy case on the dashboard
- Big moments pop up after each sim: upsets, buzzer-beaters (and heartbreakers), rank jumps, win streaks, conference titles, Selection Sunday, every NCAA round, commitments ("he chose you over..."), flips, decommitments, recruits you lost to rivals, and Signing Day
- Game Prep: spend the week's coaching points scouting your next opponent (Film study, Scouting report, Full game plan) for about +1 to +2.5 points in that game, with a scouting report and keys to the game

**Recruiting & the offseason**
- About 1,700 high school prospects a year, each with seven preferences: playing time, prestige, proximity, contender, coach, facilities, NIL
- Weekly coaching points (about 85 to 115 by program, a little more with a good recruiter) for calls, assistant visits, head coach visits, official visits, offers and NIL deals, and for Game Prep; practice is free
- Official visits open once a recruit is Hot on you (halfway to committing), like Blue Bloods' campus invite; each recruit has a decision week and then picks among schools that offered and are Ready to commit, usually the leader
- Scouting the Blue Bloods way: seven broad categories (Shooting, Finishing, Playmaking, Perimeter D, Interior D, Rebounding, Athleticism), each a letter grade averaged from the ratings underneath. Game film (2 pts) reveals one at random and Scout a game (5 pts) reveals the one you choose, each once a week per recruit; Talk to his coach (3 pts, once) reveals work ethic and potential; until then it's "?", and star ratings are noisy, so there are sleepers and busts
- Recruit profiles in tabs: Overview (what he wants, scouting and recruiting actions, who's after him), Ratings, and HS Stats (his high school career, with the senior season playing out alongside yours)
- Everything that spends coaching points (scouting, calls, visits, Game Prep) or makes an offer asks you to confirm first; Scout a game opens a popup to pick what to watch for
- Heat meters (Cold, Warm, Hot, Ready to commit) for you and every rival; NIL offers ask for confirmation
- Recruiting opens at tip-off: the high school season starts with the college season, so nobody recruits in the preseason
- Coaching points always visible in the top bar; a "Realistic for us" board filter and a plain-language chance for every recruit
- Top-five lists, verbal commitments that can flip, early and late signing periods
- AI programs recruit under the same rules, following a realistic pecking order
- NBA Draft with early entries and international picks (about 20 of the 58 picks go to players from overseas clubs, as in recent drafts), graduation, and a transfer portal with four windows, where you can re-recruit your own players
- A modern portal: about a third of players enter each spring, for playing time, NIL, a coaching change or a fresh start; winning teams keep their players and losing ones bleed them, and plenty of entrants never land at another D1 school. Settings has a Transfer activity option from pre-portal era to chaos
- Coaching carousel with firings, retirements, poaching, job offers and getting fired, plus conference realignment invitations

**History**
- Team pages for any program and any season: roster with that season's stats, schedule and results, team stats
- Program history: season-by-season table, Final Four banners, career and single-season leaders, NBA draftees
- Player pages with career stats across transfers, game logs, ratings history, awards and draft slot, even years after they've left
- League history, record book (single game, season, career, team), awards archive, draft history, transfer log
- Milestones for your coaching career (first NCAA bid, Final Fours, No. 1 rankings, win totals and more)

## Developer scripts

```bash
npm run typecheck
npm test                              # engine tests (full seasons, offseason, data integrity)
npx tsx scripts/calibrate.ts 4000     # game engine vs. D1 averages
npx tsx scripts/seasons.ts 10 7       # multi-season stability check (talent, prestige, recruiting, upsets)
npx tsx scripts/realism.ts 4 11       # full league vs. real D1: 36 measures from shooting to coaching changes
```

Cloud saves need a Vercel Blob store connected to the project (`vercel blob create-store <name> --access public --yes`). For local development, `vercel env pull` writes the Blob token to `.env.local`, and `npm run dev` serves `api/saves.ts` itself.


## Code layout

```
src/engine/        pure TypeScript simulation (no UI)
  sim/game.ts      possession-based game engine
  sim/rotation.ts  lineups and minutes
  league.ts        league creation
  advance.ts       season state machine
  schedule.ts      schedule generation
  rankings.ts      power ratings, polls, selection
  postseason.ts    conference tournaments, NCAA/NIT/CBI brackets
  events.ts        early-season events: fields, Thanksgiving-week dates, 8- and 4-team brackets
  recruiting.ts    recruiting model and AI
  offseason.ts     awards, draft, portal, signing, rollover
  coaches.ts       prestige, coaching carousel
  realignment.ts   conference realignment
  development.ts   practice and progression
  records.ts       record book
  data/            teams, conferences, names, hometowns
src/ui/            React app (pages, components, IndexedDB persistence)
```

Team names are used for a personal fan project; logos are generated monograms, not official marks.
