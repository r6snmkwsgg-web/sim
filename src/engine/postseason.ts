import type { Bracket, BracketGame, Game, League } from "./types";
import { addNews, conferenceOf, team } from "./core";
import { curSeason } from "./play";
import { selectionScores } from "./rankings";
import { winPct } from "./stats";

export const REGION_NAMES = ["East", "West", "South", "Midwest"];
export const NCAA_ROUNDS = ["Round of 64", "Round of 32", "Sweet 16", "Elite Eight", "Final Four", "Championship"];
const NCAA_DAYS = [136, 138, 143, 145, 151, 153];
const NCAA_PLAYIN_DAY = 134;
const NIT_ROUNDS = ["First Round", "Second Round", "Quarterfinals", "Semifinals", "Championship"];
const NIT_DAYS = [135, 139, 142, 149, 151];
const CBI_ROUNDS = ["First Round", "Quarterfinals", "Semifinals", "Championship"];
const CBI_DAYS = [137, 139, 141, 143];
export const CT_FINAL_DAY = 131;

export function seedOrder(n: number): number[] {
  let order = [1];
  while (order.length < n) {
    const m = order.length * 2;
    const next: number[] = [];
    for (const s of order) next.push(s, m + 1 - s);
    order = next;
  }
  return order;
}

function nextPow2(n: number): number {
  let b = 1;
  while (b < n) b *= 2;
  return b;
}

// ---------------- standings ----------------
export function confStandings(L: League, cid: number): number[] {
  const members = L.teams.filter((t) => t.cid === cid);
  return members
    .slice()
    .sort((a, b) => {
      const sa = curSeason(a);
      const sb = curSeason(b);
      const ca = winPct(sa.cw, sa.cl);
      const cb = winPct(sb.cw, sb.cl);
      if (cb !== ca) return cb - ca;
      if (sb.cw !== sa.cw) return sb.cw - sa.cw;
      const oa = winPct(sa.w, sa.l);
      const ob = winPct(sb.w, sb.l);
      if (ob !== oa) return ob - oa;
      return (L.power[b.id]?.power ?? 0) - (L.power[a.id]?.power ?? 0);
    })
    .map((t) => t.id);
}

export function finalizeStandings(L: League) {
  for (const c of L.conferences) {
    const order = confStandings(L, c.id);
    if (!order.length) continue;
    const top = curSeason(team(L, order[0]));
    const topPct = winPct(top.cw, top.cl);
    order.forEach((tid, i) => {
      const s = curSeason(team(L, tid));
      s.confRank = i + 1;
      s.confChamp = winPct(s.cw, s.cl) === topPct && s.cw === top.cw;
      if (s.confChamp && tid === L.userTid) addNews(L, "team", `${team(L, tid).name} ${i === 0 && order.length > 1 && winPct(curSeason(team(L, order[1])).cw, curSeason(team(L, order[1])).cl) === topPct ? "shares" : "wins"} the ${c.short} regular season title!`, { tid, user: true });
    });
  }
}

// ---------------- generic bracket ----------------
function makeBracket(key: string, name: string, seeds: number[], rounds: string[], days: number[], neutral: boolean, homeRounds = 0): Bracket {
  const n = seeds.length;
  const B = nextPow2(n);
  const order = seedOrder(B);
  const games: BracketGame[] = [];
  const R = Math.log2(B);
  for (let r = 0; r < R; r++) {
    const count = B / 2 ** (r + 1);
    for (let j = 0; j < count; j++) games.push({ slot: j, round: r, a: null, b: null, sa: null, sb: null, gid: null, winner: null });
  }
  for (let j = 0; j < B / 2; j++) {
    const g = games[j];
    const s1 = order[2 * j];
    const s2 = order[2 * j + 1];
    g.sa = s1;
    g.a = seeds[s1 - 1] ?? null;
    g.sb = s2 <= n ? s2 : null;
    g.b = s2 <= n ? seeds[s2 - 1] : null;
  }
  const br: Bracket = {
    key,
    name,
    rounds: rounds.slice(rounds.length - R),
    games,
    champion: null,
    runnerUp: null,
    neutral,
    homeHigherSeedRounds: homeRounds,
    days: days.slice(days.length - R),
  };
  // byes advance immediately
  for (let j = 0; j < B / 2; j++) {
    const g = games[j];
    if (g.a !== null && g.b === null) {
      g.winner = g.a;
      advanceWinner(br, g);
    }
  }
  return br;
}

function findGame(br: Bracket, round: number, slot: number): BracketGame | undefined {
  return br.games.find((g) => g.round === round && g.slot === slot);
}

function advanceWinner(br: Bracket, g: BracketGame) {
  const w = g.winner!;
  const seed = w === g.a ? g.sa : g.sb;
  if (g.round < 0 && g.feed) {
    const target = findGame(br, 0, g.feed.slot)!;
    if (g.feed.side === 0) {
      target.a = w;
      target.sa = seed;
    } else {
      target.b = w;
      target.sb = seed;
    }
    return;
  }
  const maxRound = Math.max(...br.games.map((x) => x.round));
  if (g.round === maxRound) {
    br.champion = w;
    br.runnerUp = w === g.a ? g.b : g.a;
    return;
  }
  const next = findGame(br, g.round + 1, Math.floor(g.slot / 2))!;
  if (g.slot % 2 === 0) {
    next.a = w;
    next.sa = seed;
  } else {
    next.b = w;
    next.sb = seed;
  }
}

// ---------------- conference tournaments ----------------
export function createConfTourneys(L: League) {
  L.brackets = [];
  for (const c of L.conferences) {
    const order = confStandings(L, c.id);
    const n = Math.min(order.length, c.tourneyTeams);
    if (n < 2) continue;
    const seeds = order.slice(0, n);
    const B = nextPow2(n);
    const R = Math.log2(B);
    const days = Array.from({ length: R }, (_, r) => CT_FINAL_DAY - (R - 1 - r));
    const rounds = ["First Round", "Second Round", "Quarterfinals", "Semifinals", "Championship"];
    const br = makeBracket(`conf:${c.id}`, `${c.short} Tournament`, seeds, rounds.slice(5 - R), days, true);
    L.brackets.push(br);
    for (const tid of order.slice(n)) curSeason(team(L, tid)).confTourney = "Did not qualify";
  }
}

const CT_RESULT = (R: number, round: number): string => {
  const fromEnd = R - 1 - round;
  return ["Runner-up", "Semifinals", "Quarterfinals", "Second Round", "First Round"][fromEnd] ?? "First Round";
};

// ---------------- selection ----------------
export function runSelection(L: League) {
  const sel = selectionScores(L);
  const auto: number[] = [];
  for (const br of L.brackets) if (br.key.startsWith("conf:") && br.champion !== null) auto.push(br.champion);
  const F = L.settings.bracketSize;
  const autoSet = new Set(auto);
  const atLarge = L.teams
    .filter((t) => !autoSet.has(t.id))
    .sort((a, b) => sel.get(b.id)! - sel.get(a.id)!)
    .slice(0, Math.max(0, F - auto.length))
    .map((t) => t.id);
  const field = [...auto, ...atLarge];
  const score = (tid: number) => sel.get(tid) ?? -99;
  const P = F - 64; // play-in games
  const autoPI = Math.ceil(P / 2);
  const atPI = P - autoPI;
  const autoSorted = auto.slice().sort((a, b) => score(a) - score(b)); // worst first
  const autoPlayin = autoSorted.slice(0, autoPI * 2);
  const atSorted = atLarge.slice().sort((a, b) => score(a) - score(b));
  const atPlayin = atSorted.slice(0, atPI * 2);
  const playin = new Set([...autoPlayin, ...atPlayin]);
  type Entry = { tids: number[]; score: number };
  const entries: Entry[] = [];
  for (const tid of field) if (!playin.has(tid)) entries.push({ tids: [tid], score: score(tid) });
  for (let i = 0; i < atPI; i++) {
    const pair = [atPlayin[2 * i], atPlayin[2 * i + 1]];
    entries.push({ tids: pair, score: Math.max(score(pair[0]), score(pair[1])) });
  }
  entries.sort((a, b) => b.score - a.score);
  for (let i = 0; i < autoPI; i++) {
    entries.push({ tids: [autoPlayin[2 * i], autoPlayin[2 * i + 1]], score: -999 });
  }
  // keep exactly 64 entries
  const e64 = entries.slice(0, 64);
  // S-curve: seed line k gets entries 4k..4k+3, regions snake
  const regionSeeds: (Entry | null)[][] = [[], [], [], []];
  for (let line = 0; line < 16; line++) {
    const group = e64.slice(line * 4, line * 4 + 4);
    const regs = line % 2 === 0 ? [0, 1, 2, 3] : [3, 2, 1, 0];
    group.forEach((e, i) => (regionSeeds[regs[i]][line] = e));
  }
  const order = seedOrder(16);
  const games: BracketGame[] = [];
  for (let r = 0; r < 6; r++) {
    const count = 64 / 2 ** (r + 1);
    for (let j = 0; j < count; j++) {
      const g: BracketGame = { slot: j, round: r, a: null, b: null, sa: null, sb: null, gid: null, winner: null };
      if (r <= 3) g.region = Math.floor(j / (count / 4));
      games.push(g);
    }
  }
  let piSlot = 0;
  for (let reg = 0; reg < 4; reg++) {
    for (let j = 0; j < 8; j++) {
      const g = games[reg * 8 + j];
      const s1 = order[2 * j];
      const s2 = order[2 * j + 1];
      const place = (seed: number, side: 0 | 1) => {
        const e = regionSeeds[reg][seed - 1];
        if (!e) return;
        if (e.tids.length === 1) {
          if (side === 0) {
            g.a = e.tids[0];
            g.sa = seed;
          } else {
            g.b = e.tids[0];
            g.sb = seed;
          }
        } else {
          games.push({
            slot: piSlot++,
            round: -1,
            a: e.tids[0],
            b: e.tids[1],
            sa: seed,
            sb: seed,
            gid: null,
            winner: null,
            region: reg,
            feed: { slot: reg * 8 + j, side },
          });
          if (side === 0) g.sa = seed;
          else g.sb = seed;
        }
      };
      place(s1, 0);
      place(s2, 1);
    }
  }
  const ncaa: Bracket = {
    key: "ncaa",
    name: "NCAA Tournament",
    rounds: NCAA_ROUNDS,
    games,
    regions: REGION_NAMES,
    champion: null,
    runnerUp: null,
    neutral: true,
    days: NCAA_DAYS,
    playinDay: P > 0 ? NCAA_PLAYIN_DAY : undefined,
    playinName: "First Four",
  };
  for (let reg = 0; reg < 4; reg++) {
    for (let line = 0; line < 16; line++) {
      const e = regionSeeds[reg][line];
      if (!e) continue;
      for (const tid of e.tids) {
        curSeason(team(L, tid)).post = { event: "ncaa", seed: line + 1, result: e.tids.length > 1 ? "First Four" : "Round of 64" };
      }
    }
  }
  const inField = new Set(field);
  const rest = L.teams.filter((t) => !inField.has(t.id)).sort((a, b) => score(b.id) - score(a.id));
  const nitTeams = rest.slice(0, 32).map((t) => t.id);
  const cbiTeams = rest.slice(32, 48).map((t) => t.id);
  const nit = makeBracket("nit", "NIT", nitTeams, NIT_ROUNDS, NIT_DAYS, false, 3);
  const cbi = makeBracket("cbi", "CBI", cbiTeams, CBI_ROUNDS, CBI_DAYS, true);
  nitTeams.forEach((tid, i) => (curSeason(team(L, tid)).post = { event: "nit", seed: i + 1, result: NIT_ROUNDS[0] }));
  cbiTeams.forEach((tid, i) => (curSeason(team(L, tid)).post = { event: "cbi", seed: i + 1, result: CBI_ROUNDS[0] }));
  L.brackets.push(ncaa, nit, cbi);

  // news
  const user = curSeason(team(L, L.userTid));
  const ut = team(L, L.userTid);
  if (user.post?.event === "ncaa") {
    addNews(L, "team", `Selection Sunday: ${ut.name} is in the NCAA Tournament as a ${user.post.seed} seed!`, { tid: ut.id, user: true });
  } else if (user.post?.event === "nit") {
    addNews(L, "team", `${ut.name} missed the NCAA Tournament and accepted a bid to the NIT.`, { tid: ut.id, user: true });
  } else if (user.post?.event === "cbi") {
    addNews(L, "team", `${ut.name} missed the NCAA Tournament and will play in the CBI.`, { tid: ut.id, user: true });
  } else {
    addNews(L, "team", `${ut.name} was not selected for the postseason.`, { tid: ut.id, user: true });
  }
  const ones = regionSeeds.map((r) => r[0]?.tids[0]).filter((x) => x !== undefined) as number[];
  addNews(L, "league", `NCAA Tournament field announced. No. 1 seeds: ${ones.map((t) => team(L, t).name).join(", ")}.`, { user: false });
}

// ---------------- daily bracket games ----------------
export function createBracketGames(L: League, day: number): Game[] {
  const out: Game[] = [];
  for (const br of L.brackets) {
    if (br.champion !== null) continue;
    for (const g of br.games) {
      if (g.gid !== null || g.winner !== null || g.a === null || g.b === null) continue;
      const d = g.round < 0 ? br.playinDay : br.days[g.round];
      if (d !== day) continue;
      let home = g.a;
      let away = g.b;
      let neutral = br.neutral;
      if (br.homeHigherSeedRounds && g.round < br.homeHigherSeedRounds) {
        neutral = false;
        if ((g.sb ?? 99) < (g.sa ?? 99)) [home, away] = [away, home];
      }
      const type: Game["type"] = br.key === "ncaa" ? "ncaa" : br.key === "nit" ? "nit" : br.key === "cbi" ? "cbi" : "ctourn";
      const game: Game = {
        id: L.nextGid++,
        season: L.season,
        day,
        home,
        away,
        neutral,
        type,
        played: false,
        hs: 0,
        as: 0,
        ot: 0,
        tourney: { key: br.key, round: g.round, slot: g.slot },
        event: g.round < 0 ? br.playinName : `${br.name} ${br.rounds[g.round]}`,
      };
      g.gid = game.id;
      L.games.push(game);
      out.push(game);
    }
  }
  return out;
}

export function recordBracketResult(L: League, game: Game) {
  if (!game.tourney) return;
  const br = L.brackets.find((b) => b.key === game.tourney!.key);
  if (!br) return;
  const g = br.games.find((x) => x.gid === game.id);
  if (!g) return;
  const winner = game.hs > game.as ? game.home : game.away;
  const loser = winner === game.home ? game.away : game.home;
  g.winner = winner;
  advanceWinner(br, g);
  const maxRound = Math.max(...br.games.map((x) => x.round));
  const ls = curSeason(team(L, loser));
  const ws = curSeason(team(L, winner));
  if (br.key.startsWith("conf:")) {
    const R = maxRound + 1;
    ls.confTourney = CT_RESULT(R, g.round);
    if (br.champion !== null) {
      ws.confTourney = "Champion";
      const c = conferenceOf(L, winner);
      addNews(L, winner === L.userTid ? "team" : "league", `${team(L, winner).name} wins the ${c.short} Tournament and earns an automatic NCAA bid!`, { tid: winner, user: winner === L.userTid });
    }
    return;
  }
  // national postseason
  const roundName = (r: number) => (r < 0 ? br.playinName ?? "First Four" : br.rounds[r]);
  if (ls.post) {
    if (g.round === maxRound) ls.post.result = "Runner-up";
    else ls.post.result = roundName(g.round);
  }
  if (ws.post) {
    if (br.champion !== null) ws.post.result = "Champion";
    else ws.post.result = roundName(g.round + 1);
  }
  if (br.key === "ncaa") {
    if (br.champion !== null) {
      addNews(L, "league", `${team(L, winner).name} wins the national championship, defeating ${team(L, loser).name} ${Math.max(game.hs, game.as)}-${Math.min(game.hs, game.as)}!`, { tid: winner, gid: game.id, user: winner === L.userTid || loser === L.userTid });
    } else if (g.round === 3) {
      addNews(L, "league", `${team(L, winner).name} advances to the Final Four.`, { tid: winner, gid: game.id, user: winner === L.userTid });
    }
  }
}

export function confTourneysDone(L: League): boolean {
  return L.brackets.filter((b) => b.key.startsWith("conf:")).every((b) => b.champion !== null);
}
export function nationalDone(L: League): boolean {
  const nat = L.brackets.filter((b) => !b.key.startsWith("conf:"));
  return nat.length > 0 && nat.every((b) => b.champion !== null);
}
