# Hardwood Dynasty

A college basketball program-building game for the desktop browser, inspired by *Blue Bloods Basketball*. Take any of the 365 Division I programs and turn it from a no-name into a Blue Blood. Recruit, develop players, set tactics, survive March, and build a legacy that's **kept forever**: every season, roster, box score, bracket, award and record stays browsable.

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

Saves live in your browser (IndexedDB) and autosave after every sim and edit. Use **Settings → Export** to back up a league to a compressed `.hdsave.gz` file (every season, player, box score and record), and **Import Save** on the start screen to restore it on any computer. Saves belong to the browser and the address you play from, so keep using the same one (or export and import when you switch).

Tips: press `/` or `Ctrl+K` to search for any team or player. If you'd rather not manage recruiting week to week, turn on auto recruiting in **Settings** and your staff will handle it.

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
- Redshirts, releasing players, walk-ons, NIL budgets

**The season**
- About 31-game schedules with home, away and neutral-site games, including Thanksgiving events
- A possession-by-possession game engine calibrated to real D1 averages (pace, shooting splits, free throws, turnovers, rebounding, blocks, steals, assists, fouls, home-court edge, overtime rate, game-to-game variance), with fatigue, foul trouble, substitutions, score effects and real end-of-game decisions (holding for the last shot, fouling when the shot clock is off, needing a three)
- Watch your games live: a scoreboard, a shot chart on a full court, a live box score, a game-flow chart you can click to rewind, and the play-by-play, at 1x to 8x speed. The result stays hidden until the final buzzer
- Box scores and play-by-play for your games
- Weekly AP-style Top 25, opponent-adjusted power ratings, bracketology
- Conference tournaments, Selection Sunday, NCAA Tournament (64, 68 with First Four, or 76), NIT and CBI
- Awards: national and conference Player of the Year, Defensive POY, Freshman, Sixth Man, Most Improved, Coach of the Year, All-America and All-Conference teams, Final Four MOP

**Recruiting & the offseason**
- About 1,700 high school prospects a year, each with seven preferences: playing time, prestige, proximity, contender, coach, facilities, NIL
- Weekly recruiting points for calls, assistant visits, head coach visits, official visits, offers and NIL deals
- Scouting that reveals true ratings; star ratings are noisy, so there are sleepers and busts
- Top-five lists, verbal commitments that can flip, early and late signing periods
- AI programs recruit under the same rules, following a realistic pecking order
- NBA Draft with early entries, graduation, and a transfer portal with four windows, where you can re-recruit your own players
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
```

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
