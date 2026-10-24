import type { League, Player, PrefKey, RecruitInfo, Team } from "./types";
import { PREF_KEYS } from "./types";
import { Rng, clamp, distanceMiles } from "./rng";
import { addNews, addPlayer, coachOf, nextPid, playerName, roster, rngOf, rostersDirty, rosterVersion, team } from "./core";
import { generatePlayer } from "./gen/player";
import { powerRanks } from "./rankings";

export const PREF_LABELS: Record<PrefKey, string> = {
  pt: "Playing Time",
  prestige: "Program Prestige",
  proximity: "Close to Home",
  contender: "Championship Contender",
  coach: "Head Coach",
  facilities: "Facilities",
  nil: "NIL Opportunities",
};

export type ActionKey = "scout" | "call" | "assistant" | "coach" | "visit" | "offer";
export const ACTIONS: Record<ActionKey, { label: string; cost: number; value: number; cooldown: number; once?: boolean; desc: string }> = {
  scout: { label: "Scout", cost: 6, value: 0, cooldown: 0, desc: "Evaluate the player. Each level narrows the uncertainty in his ratings." },
  call: { label: "Phone Call", cost: 3, value: 3, cooldown: 1, desc: "A quick call from your staff. Small interest boost (once per week)." },
  assistant: { label: "Assistant Visit", cost: 8, value: 7, cooldown: 1, desc: "An assistant coach visits. Solid interest boost (once per week)." },
  coach: { label: "Head Coach Visit", cost: 18, value: 14, cooldown: 3, desc: "You visit personally. Big boost, scaled by your recruiting skill (every 3 weeks)." },
  visit: { label: "Official Visit", cost: 20, value: 22, cooldown: 0, once: true, desc: "Bring him to campus. Huge boost (once per recruit, limited per season)." },
  offer: { label: "Offer Scholarship", cost: 0, value: 9, cooldown: 0, once: true, desc: "Required for him to commit. Limited by your open roster spots." },
};

export const OFFICIAL_VISITS = 12;
export const BASE_POINTS = 50;
const STAR_POINTS = [0, 4, 12, 30, 60, 100];
export const NIL_VALUE = [0, 8, 25, 80, 250, 600]; // $K expected by stars
const COMMIT_THRESHOLD = [0, 15, 20, 26, 34, 44];

export function recruitValue(p: Player): number {
  return 0.5 * p.ovr + 0.5 * p.pot;
}

export function starsForRank(rank: number, total: number): number {
  const scale = total / 1500;
  if (rank <= 25 * scale) return 5;
  if (rank <= 150 * scale) return 4;
  if (rank <= 500 * scale) return 3;
  if (rank <= 1000 * scale) return 2;
  return 1;
}

function makePrefs(rng: Rng, stars: number): Record<PrefKey, number> {
  const s = stars - 3;
  const v = (base: number) => clamp(Math.round(base + rng.normal(0, 1)), 1, 5);
  return {
    pt: v(3.1 - 0.3 * s),
    prestige: v(2.9 + 0.5 * s),
    proximity: v(2.7),
    contender: v(2.6 + 0.4 * s),
    coach: v(2.8),
    facilities: v(2.4 + 0.2 * s),
    nil: v(2.5 + 0.5 * s),
  };
}

export function newRecruitInfo(rng: Rng, kind: "hs" | "portal", classSeason: number, stars: number): RecruitInfo {
  const cw = [0, 6, 7, 9, 11, 13][stars];
  return {
    kind,
    classSeason,
    stars,
    rank: 0,
    posRank: 0,
    prefs: makePrefs(rng, stars),
    interest: {},
    offers: [],
    visits: [],
    nil: {},
    stage: "open",
    top5: [],
    committedTo: null,
    commitWeek: kind === "portal" ? rng.int(1, 4) : Math.round(clamp(rng.normal(cw, 4), 1, 27)),
    scout: 0,
    lastAction: {},
    history: [],
  };
}

/** NBA draft stock used for early-entry projections. */
export function draftStock(p: Player): number {
  return p.ovr + 0.4 * (p.pot - p.ovr) - 1.2 * (Math.max(1, p.year) - 1);
}

/** Underclassman projected to leave early for the NBA. */
export function likelyPro(p: Player): boolean {
  return draftStock(p) >= 70;
}

/** Will this player still be on the roster next season (before departures)? */
export function willReturn(L: League, p: Player): boolean {
  if (p.status !== "active") return false;
  if (L.phase === "draft" || L.phase === "portal" || L.phase === "signing") return true;
  const used = p.eligUsed + (p.redshirt ? 0 : 1);
  return used < 4 && p.year < 5 && !likelyPro(p);
}

// ---------- recruiting index (commits, outstanding offers, NIL promises per team) ----------
interface RecIndex {
  commits: Map<number, Player[]>;
  offersOut: Map<number, number>;
  nilOut: Map<number, number>;
}
const recIdx = new WeakMap<League, RecIndex>();

function rec(L: League): RecIndex {
  let i = recIdx.get(L);
  if (!i) {
    i = { commits: new Map(), offersOut: new Map(), nilOut: new Map() };
    for (const p of L.players) {
      const r = p.recruit;
      if (!r || r.stage === "unsigned" || (p.status !== "recruit" && p.status !== "portal")) continue;
      if (r.committedTo !== null && (r.stage === "committed" || r.stage === "signed")) {
        const arr = i.commits.get(r.committedTo) ?? [];
        arr.push(p);
        i.commits.set(r.committedTo, arr);
        i.nilOut.set(r.committedTo, (i.nilOut.get(r.committedTo) ?? 0) + (r.nil[r.committedTo] ?? 0));
      }
      if (r.stage === "signed") continue;
      for (const tid of r.offers) {
        if (tid === r.committedTo) continue;
        i.offersOut.set(tid, (i.offersOut.get(tid) ?? 0) + 1);
      }
      for (const k in r.nil) {
        const tid = Number(k);
        if (tid === r.committedTo) continue;
        i.nilOut.set(tid, (i.nilOut.get(tid) ?? 0) + r.nil[k]);
      }
    }
    recIdx.set(L, i);
  }
  return i;
}
export function dirtyRec(L: League) {
  recIdx.delete(L);
}

export function commitsFor(L: League, tid: number): Player[] {
  return rec(L).commits.get(tid) ?? [];
}

export function openSpots(L: League, tid: number): number {
  return L.settings.rosterMax - returningPlayers(L, tid).length - commitsFor(L, tid).length;
}

// ---------- class generation ----------
export function generateRecruitClass(L: League) {
  const rng = rngOf(L);
  let expected = 0;
  for (const t of L.teams) expected += Math.max(1, L.settings.rosterMax - roster(L, t.id).filter((p) => willReturn(L, p)).length);
  // early departures and transfers open more spots later
  const n = Math.round(clamp(expected * 1.18 + 120, 1100, 1900));
  const made: Player[] = [];
  for (let i = 0; i < n; i++) {
    const z = rng.normal(0, 1);
    let pot = 53.5 + 8 * z + Math.max(0, z - 1.6) * 7;
    pot = clamp(pot, 34, 94);
    const growth = clamp(rng.normal(13, 4), 3, 24);
    const ovr = clamp(Math.round(pot - growth), 22, 78);
    const p = generatePlayer(rng, { id: nextPid(L), ovr, pot: Math.round(pot), year: 0 });
    p.status = "recruit";
    p.tid = null;
    made.push(p);
  }
  rankAndStar(L, made, "hs", L.season + 1);
  for (const p of made) addPlayer(L, p);
}

export function rankAndStar(L: League, ps: Player[], kind: "hs" | "portal", classSeason: number) {
  const rng = rngOf(L);
  const scored = ps.map((p) => ({ p, s: recruitValue(p) + rng.normal(0, kind === "hs" ? 2.5 : 1.5) }));
  scored.sort((a, b) => b.s - a.s);
  const posCount: Record<string, number> = {};
  scored.forEach(({ p }, i) => {
    const stars = kind === "hs" ? starsForRank(i + 1, scored.length) : portalStars(i + 1, scored.length);
    p.recruit = newRecruitInfo(rng, kind, classSeason, stars);
    p.recruit.rank = i + 1;
    posCount[p.pos] = (posCount[p.pos] ?? 0) + 1;
    p.recruit.posRank = posCount[p.pos];
    if (kind === "hs") {
      const big = p.pos === "PF" || p.pos === "C";
      const guard = p.pos === "PG" || p.pos === "SG";
      p.recruit.hs = {
        pts: Math.round(clamp(9 + (p.ovr - 28) * 0.6 + rng.normal(0, 3), 4, 38) * 10) / 10,
        reb: Math.round(clamp((big ? 8 : guard ? 3.5 : 5.5) + (p.ovr - 40) * 0.12 + rng.normal(0, 1.5), 1, 18) * 10) / 10,
        ast: Math.round(clamp((p.pos === "PG" ? 5.5 : guard ? 3 : big ? 1.2 : 2.2) + (p.ovr - 40) * 0.07 + rng.normal(0, 1), 0.3, 11) * 10) / 10,
      };
    }
  });
}

function portalStars(rank: number, total: number): number {
  const scale = total / 700;
  if (rank <= 15 * scale) return 5;
  if (rank <= 70 * scale) return 4;
  if (rank <= 250 * scale) return 3;
  if (rank <= 480 * scale) return 2;
  return 1;
}

// ---------- fit ----------
interface FitCache {
  week: number;
  phase: string;
  rv: number;
  round: number;
  power: Map<number, number>;
  fits: Map<number, number>;
  returning: Map<number, Player[]>;
}
const fitCaches = new WeakMap<League, FitCache>();

function cache(L: League): FitCache {
  let c = fitCaches.get(L);
  const rv = rosterVersion(L);
  if (!c || c.week !== L.week || c.phase !== L.phase || c.rv !== rv || c.round !== L.portalRound) {
    c = { week: L.week, phase: L.phase, rv, round: L.portalRound, power: powerRanks(L), fits: new Map(), returning: new Map() };
    fitCaches.set(L, c);
  }
  return c;
}
export function invalidateFit(L: League) {
  fitCaches.delete(L);
}

function returningPlayers(L: League, tid: number): Player[] {
  const c = cache(L);
  let r = c.returning.get(tid);
  if (!r) {
    r = roster(L, tid).filter((p) => willReturn(L, p));
    c.returning.set(tid, r);
  }
  return r;
}

const POS_N: Record<string, number> = { PG: 0, SG: 1, SF: 2, PF: 3, C: 4 };
const PT_SCORE = [1, 0.85, 0.65, 0.45, 0.3, 0.2, 0.1];

export function factorScores(L: League, t: Team, p: Player): Record<PrefKey, number> {
  const c = cache(L);
  const myPos = POS_N[p.pos];
  const nextOvr = p.ovr + (p.recruit?.kind === "portal" ? 2 : 4);
  let depth = 0;
  for (const q of returningPlayers(L, t.id)) {
    if (Math.abs(POS_N[q.pos] - myPos) <= 1 && q.ovr + (q.year <= 2 ? 3 : 1.5) >= nextOvr - 2) depth++;
  }
  for (const q of commitsFor(L, t.id)) {
    if (q.id !== p.id && Math.abs(POS_N[q.pos] - myPos) <= 1 && q.ovr >= p.ovr - 2) depth++;
  }
  const d = distanceMiles(p.lat, p.lon, t.lat, t.lon);
  let prox = d < 60 ? 1 : Math.max(0, 1 - Math.log(d / 60) / Math.log(3000 / 60));
  if (p.state === t.state) prox = Math.min(1, prox + 0.12);
  const rank = c.power.get(t.id) ?? 180;
  const contender = 0.55 * (1 - (rank - 1) / Math.max(1, L.teams.length - 1)) + 0.45 * (t.prestige / 100);
  const ch = coachOf(L, t.id);
  const stars = p.recruit?.stars ?? 3;
  const offer = p.recruit?.nil[t.id] ?? 0;
  const nil = offer > 0 ? Math.min(1, offer / NIL_VALUE[stars]) * 0.85 + 0.15 : 0.08 + 0.22 * Math.min(1, t.nilBudget / 3000);
  return {
    pt: PT_SCORE[Math.min(6, depth)],
    prestige: Math.pow(t.prestige / 100, 1.35),
    proximity: prox,
    contender,
    coach: (ch?.rep ?? 50) / 100,
    facilities: t.facilities / 100,
    nil,
  };
}

export function fit(L: League, t: Team, p: Player): number {
  const c = cache(L);
  const key = t.id * 1000000 + p.id;
  const hit = c.fits.get(key);
  if (hit !== undefined) return hit;
  const f = factorScores(L, t, p);
  const prefs = p.recruit!.prefs;
  let s = 0;
  let w = 0;
  for (const k of PREF_KEYS) {
    if (k === "nil" && !L.settings.nil) continue;
    let imp = prefs[k];
    if (k === "proximity" && p.lat < 10 && p.lon > -60) imp *= 0.5; // international
    s += imp * imp * f[k];
    w += imp * imp;
  }
  const v = w ? s / w : 0.5;
  c.fits.set(key, v);
  return v;
}

/** How much each action is worth for this team with this recruit. */
export function actionMult(L: League, t: Team, p: Player): number {
  const f = fit(L, t, p);
  // stars-vs-prestige gap: elite recruits pay less attention to small programs
  const stars = p.recruit?.stars ?? 3;
  const reach = Math.max(0, (stars - 1) * 22 - t.prestige) / 100;
  return Math.max(0.1, (0.3 + 1.4 * f) * Math.max(0.15, 1 - reach * 1.8));
}

function addInterest(L: League, p: Player, tid: number, amount: number) {
  const r = p.recruit!;
  if ((r.stage === "top5" || r.stage === "committed") && !r.top5.includes(tid)) amount *= 0.25;
  r.interest[tid] = (r.interest[tid] ?? 0) + amount;
}

// ---------- actions ----------
export function canAct(L: League, tid: number, p: Player, a: ActionKey): { ok: boolean; why?: string } {
  const r = p.recruit;
  if (!r) return { ok: false, why: "Not a recruit" };
  if (r.stage === "signed") return { ok: false, why: "Already signed" };
  if (r.stage === "unsigned") return { ok: false, why: "No longer available" };
  if (r.committedTo !== null && r.committedTo !== tid && a !== "scout") {
    // can still try to flip a verbal commitment, but not a signed one
  }
  const def = ACTIONS[a];
  const t = team(L, tid);
  const pts = tid === L.userTid ? L.recruitPts : t.recruitPoints;
  if (pts < def.cost) return { ok: false, why: "Not enough recruiting points" };
  if (a === "scout") {
    if (tid !== L.userTid) return { ok: false };
    if (r.scout >= 3) return { ok: false, why: "Fully scouted" };
    return { ok: true };
  }
  if (r.committedTo === tid) {
    if (a === "offer") return { ok: false, why: "Already committed to you" };
  }
  if (a === "offer") {
    if (r.offers.includes(tid)) return { ok: false, why: "Already offered" };
    const spots = openSpots(L, tid);
    if (spots <= 0) return { ok: false, why: "No open roster spots" };
    const outstanding = rec(L).offersOut.get(tid) ?? 0;
    if (outstanding >= spots * 3 + 2) return { ok: false, why: "Too many outstanding offers" };
    return { ok: true };
  }
  if (a === "visit") {
    if (r.visits.includes(tid)) return { ok: false, why: "Already visited" };
    if (t.officialVisitsUsed >= OFFICIAL_VISITS) return { ok: false, why: "No official visits left" };
    return { ok: true };
  }
  const last = r.lastAction[`${tid}:${a}`];
  if (last !== undefined && L.week - last < def.cooldown) return { ok: false, why: def.cooldown > 1 ? `Available in ${def.cooldown - (L.week - last)} wk` : "Done this week" };
  return { ok: true };
}

export function doAction(L: League, tid: number, p: Player, a: ActionKey): { ok: boolean; msg: string } {
  const chk = canAct(L, tid, p, a);
  if (!chk.ok) return { ok: false, msg: chk.why ?? "Not allowed" };
  const rng = rngOf(L);
  const def = ACTIONS[a];
  const t = team(L, tid);
  const r = p.recruit!;
  if (tid === L.userTid) L.recruitPts -= def.cost;
  else t.recruitPoints -= def.cost;
  r.lastAction[`${tid}:${a}`] = L.week;
  const isUser = tid === L.userTid;
  if (a === "scout") {
    r.scout++;
    if (!L.board.includes(p.id)) L.board.push(p.id);
    return { ok: true, msg: `Scouting level ${r.scout}/3` };
  }
  let amt = def.value * actionMult(L, t, p) * rng.uniform(0.85, 1.15);
  if (a === "coach") amt *= 0.8 + 0.4 * ((coachOf(L, tid)?.recruiting ?? 50) / 100);
  if (a === "offer") {
    r.offers.push(tid);
    const idx = rec(L);
    idx.offersOut.set(tid, (idx.offersOut.get(tid) ?? 0) + 1);
    if (isUser) r.history.unshift({ week: L.week, text: `${t.name} offered a scholarship` });
  }
  if (a === "visit") {
    r.visits.push(tid);
    t.officialVisitsUsed++;
    // a good team environment helps
    const s = t.seasons[t.seasons.length - 1];
    if (s && s.streak >= 3) amt *= 1.15;
    if (isUser) r.history.unshift({ week: L.week, text: `Took an official visit to ${t.name}` });
  }
  addInterest(L, p, tid, amt);
  if (isUser && !L.board.includes(p.id)) L.board.push(p.id);
  return { ok: true, msg: `+${amt.toFixed(1)} interest` };
}

/** NIL dollars already promised: returning players' deals plus live offers and commitments. */
export function nilCommitted(L: League, tid: number): number {
  let total = 0;
  for (const p of returningPlayers(L, tid)) total += p.nilDeal;
  return total + (rec(L).nilOut.get(tid) ?? 0);
}

export function setNilOffer(L: League, tid: number, p: Player, amount: number): { ok: boolean; msg: string } {
  if (!L.settings.nil) return { ok: false, msg: "NIL is disabled" };
  const r = p.recruit;
  if (!r || r.stage === "signed") return { ok: false, msg: "Not available" };
  const t = team(L, tid);
  const current = r.nil[tid] ?? 0;
  const committed = nilCommitted(L, tid) - current;
  if (committed + amount > t.nilBudget) return { ok: false, msg: `Over NIL budget ($${Math.round(t.nilBudget - committed)}K left)` };
  r.nil[tid] = Math.max(0, Math.round(amount));
  dirtyRec(L);
  invalidateFitFor(L, tid, p.id);
  if (tid === L.userTid && amount > 0) r.history.unshift({ week: L.week, text: `${t.name} offered an NIL deal` });
  return { ok: true, msg: amount > 0 ? `NIL offer set to $${Math.round(amount)}K/yr` : "NIL offer withdrawn" };
}

function invalidateFitFor(L: League, tid: number, pid: number) {
  fitCaches.get(L)?.fits.delete(tid * 1000000 + pid);
}

export function pullOffer(L: League, tid: number, p: Player) {
  const r = p.recruit;
  if (!r || r.stage === "signed") return;
  r.offers = r.offers.filter((x) => x !== tid);
  if (r.committedTo === tid) {
    r.committedTo = null;
    r.stage = "top5";
  }
  dirtyRec(L);
}

// ---------- AI ----------
interface AiTargets {
  week: number;
  targets: Map<number, number[]>;
}
const aiTargetCache = new WeakMap<League, AiTargets>();


function pickTargets(L: League, t: Team, pool: Player[], needs: number, pecking: Map<number, number>): number[] {
  const rng = rngOf(L);
  const posHave: Record<string, number> = { PG: 0, SG: 0, SF: 0, PF: 0, C: 0 };
  for (const q of returningPlayers(L, t.id)) posHave[q.pos]++;
  for (const q of commitsFor(L, t.id)) posHave[q.pos]++;
  // where this program sits in the recruiting pecking order -> the recruit rank it can expect
  const q = pecking.get(t.id) ?? 0.5;
  const center = q * pool.length * 0.85;
  const pre: { p: Player; s: number; attainable: boolean }[] = [];
  for (const p of pool) {
    const r = p.recruit!;
    if (r.stage === "signed" || r.stage === "unsigned") continue;
    if (r.committedTo !== null && r.committedTo !== t.id) continue;
    if (r.stage === "top5" && !r.top5.includes(t.id)) continue;
    const rank = r.rank;
    const over = Math.max(0, center - rank);
    const under = Math.max(0, rank - center);
    if (over > pool.length * 0.25 + 30) continue;
    const near = Math.abs(p.lat - t.lat) + Math.abs(p.lon - t.lon) < 8 ? 5 : 0;
    let sc = recruitValue(p) - over * (40 / pool.length) * 2 - under * (10 / pool.length) + near + (r.interest[t.id] ?? 0) * 0.15 + rng.next() * 5;
    if (posHave[p.pos] < 2) sc += 5;
    if (posHave[p.pos] > 3) sc -= 5;
    pre.push({ p, s: sc, attainable: rank >= center - 15 });
  }
  pre.sort((a, b) => b.s - a.s);
  const short = pre.slice(0, Math.max(24, needs * 8));
  const scored = short.map(({ p, s: sc }) => ({ id: p.id, s: sc + 25 * fit(L, t, p) }));
  scored.sort((a, b) => b.s - a.s);
  const main = scored.slice(0, Math.max(3, Math.ceil(needs * 2.5))).map((x) => x.id);
  const chosen = new Set(main);
  const safety = pre
    .filter((x) => x.attainable && !chosen.has(x.p.id))
    .slice(0, Math.max(2, Math.ceil(needs * 1.5)))
    .map((x) => x.p.id);
  return [...main, ...safety];
}

/** Weekly recruiting points for a program's staff. */
export function staffPoints(L: League, t: Team): number {
  const ch = coachOf(L, t.id);
  return Math.round(BASE_POINTS * (0.85 + 0.3 * ((ch?.recruiting ?? 50) / 100)) * (0.85 + 0.3 * (t.prestige / 100)));
}

export function aiRecruitWeek(L: League, kind: "hs" | "portal" | "both" = "both") {
  const rng = rngOf(L);
  const diff = [0, 0.8, 1, 1.2][L.settings.recruitingDifficulty];
  const pool = L.players.filter((p) => p.recruit && (kind === "both" || p.recruit.kind === kind) && (p.status === "recruit" || p.status === "portal"));
  if (!pool.length) return;
  let tc = aiTargetCache.get(L);
  const refresh = !tc || L.week - tc.week >= 3 || L.week < tc.week;
  if (refresh) {
    tc = { week: L.week, targets: new Map() };
    aiTargetCache.set(L, tc);
  }
  const byId = new Map(pool.map((p) => [p.id, p]));
  // pecking order by prestige blended with current strength
  const order = L.teams.slice().sort((a, b) => b.prestige - a.prestige);
  const pecking = new Map(order.map((t, i) => [t.id, i / order.length]));
  const hsPool = pool.filter((p) => p.recruit!.kind === "hs");
  const portalPool = pool.filter((p) => p.recruit!.kind === "portal");
  for (const t of L.teams) {
    if (t.id === L.userTid) continue;
    const needs = openSpots(L, t.id);
    if (needs <= 0) continue;
    t.recruitPoints = Math.round(staffPoints(L, t) * diff);
    let targets = tc!.targets.get(t.id);
    const lost = targets
      ? targets.filter((id) => {
          const q = byId.get(id);
          return !q || (q.recruit!.committedTo !== null && q.recruit!.committedTo !== t.id) || (q.recruit!.stage === "top5" && !q.recruit!.top5.includes(t.id));
        }).length
      : 0;
    if (!targets || refresh || lost > targets.length * 0.3) {
      targets = [];
      if (hsPool.length) targets.push(...pickTargets(L, t, hsPool, needs, pecking));
      if (portalPool.length) targets.push(...pickTargets(L, t, portalPool, Math.max(1, Math.ceil(needs / 2)), pecking));
      tc!.targets.set(t.id, targets);
    }
    const live = targets
      .map((id) => byId.get(id))
      .filter((p): p is Player => !!p && p.recruit!.stage !== "signed" && (p.recruit!.committedTo === null || p.recruit!.committedTo === t.id));
    // judge where we stand with each target
    const plan = live.map((p) => {
      const r = p.recruit!;
      let best = 0;
      let bestOther = 0;
      for (const k in r.interest) {
        const v = r.interest[k];
        if (v > best) best = v;
        if (Number(k) !== t.id && v > bestOther) bestOther = v;
      }
      const mine = r.interest[t.id] ?? 0;
      const thr = COMMIT_THRESHOLD[r.stars] * (r.kind === "portal" ? 0.6 : 1);
      let mode: "commit" | "lead" | "chase" | "drop" = "chase";
      if (r.committedTo === t.id) mode = "commit";
      else if (mine >= thr && mine > bestOther * 1.2) mode = "lead";
      else if (bestOther > 25 && mine < bestOther * 0.6 && L.week >= 4) mode = "drop";
      return { p, mode };
    });
    let i = 0;
    for (const { p, mode } of plan) {
      if (t.recruitPoints < 3) break;
      const r = p.recruit!;
      if (mode === "commit" || mode === "lead") {
        if (!r.offers.includes(t.id) && canAct(L, t.id, p, "offer").ok) doAction(L, t.id, p, "offer");
        if (canAct(L, t.id, p, "call").ok) doAction(L, t.id, p, "call");
        if (mode === "lead") i++;
        continue;
      }
      if (mode === "drop") continue;
      if (i < needs * 2.5 && canAct(L, t.id, p, "offer").ok) {
        doAction(L, t.id, p, "offer");
        if (L.settings.nil && t.nilBudget > 0) {
          const amt = Math.round(NIL_VALUE[r.stars] * Math.min(1.3, t.nilBudget / 2500) * rng.uniform(0.6, 1.1));
          if (nilCommitted(L, t.id) + amt <= t.nilBudget) {
            r.nil[t.id] = amt;
            const idx = rec(L);
            idx.nilOut.set(t.id, (idx.nilOut.get(t.id) ?? 0) + amt);
          }
        }
      }
      if (i < needs * 1.2 && L.week >= 2 && canAct(L, t.id, p, "coach").ok) doAction(L, t.id, p, "coach");
      if (i < needs * 1.5 && L.week >= 4 && r.offers.includes(t.id) && canAct(L, t.id, p, "visit").ok && rng.chance(0.4)) doAction(L, t.id, p, "visit");
      if (canAct(L, t.id, p, "assistant").ok) doAction(L, t.id, p, "assistant");
      else if (canAct(L, t.id, p, "call").ok) doAction(L, t.id, p, "call");
      i++;
    }
  }
}

// ---------- decisions ----------
function commitTo(L: League, p: Player, tid: number) {
  const r = p.recruit!;
  const prev = r.committedTo;
  const idx = recIdx.get(L);
  if (idx) {
    // keep the index in sync incrementally
    if (prev !== null) {
      const arr = idx.commits.get(prev);
      if (arr) idx.commits.set(prev, arr.filter((q) => q !== p));
      if (r.offers.includes(prev)) idx.offersOut.set(prev, (idx.offersOut.get(prev) ?? 0) + 1);
    }
    const arr = idx.commits.get(tid) ?? [];
    arr.push(p);
    idx.commits.set(tid, arr);
    if (r.offers.includes(tid)) idx.offersOut.set(tid, Math.max(0, (idx.offersOut.get(tid) ?? 0) - 1));
  }
  r.committedTo = tid;
  r.stage = "committed";
  if (!r.top5.includes(tid)) r.top5 = [tid, ...r.top5].slice(0, 5);
  const t = team(L, tid);
  r.history.unshift({ week: L.week, text: `Committed to ${t.name}` });
  const isUser = tid === L.userTid;
  const wasUserTarget = L.board.includes(p.id) || (r.interest[L.userTid] ?? 0) > 5;
  const kindTxt = r.kind === "portal" ? "Transfer" : `${r.stars}★ ${p.pos}`;
  if (isUser) {
    addNews(L, "recruit", `${kindTxt} ${playerName(p)} has committed to ${t.name}!`, { tid, pid: p.id, user: true });
  } else if (prev === L.userTid) {
    addNews(L, "recruit", `${playerName(p)} has flipped his commitment from ${team(L, L.userTid).name} to ${t.name}.`, { tid, pid: p.id, user: true });
  } else if (wasUserTarget) {
    addNews(L, "recruit", `${kindTxt} ${playerName(p)}, one of your targets, committed to ${t.name}.`, { tid, pid: p.id, user: true });
  } else if (r.kind === "hs" && r.rank <= 25) {
    addNews(L, "recruit", `No. ${r.rank} recruit ${playerName(p)} (${p.pos}) commits to ${t.name}.`, { tid, pid: p.id, user: false });
  }
}

export function recruitDecisions(L: League, kind: "hs" | "portal" | "both" = "both") {
  const rng = rngOf(L);
  const spotsCache = new Map<number, number>();
  const spots = (tid: number) => {
    let s = spotsCache.get(tid);
    if (s === undefined) {
      s = openSpots(L, tid);
      spotsCache.set(tid, s);
    }
    return s;
  };
  for (const p of L.players) {
    const r = p.recruit;
    if (!r || r.stage === "signed" || r.stage === "unsigned") continue;
    if (kind !== "both" && r.kind !== kind) continue;
    // decay
    for (const k in r.interest) r.interest[k] *= 0.97;
    const sorted = Object.entries(r.interest)
      .map(([k, v]) => [Number(k), v] as [number, number])
      .sort((a, b) => b[1] - a[1]);
    if (!sorted.length) continue;
    const top = sorted[0][1];
    const wk = r.kind === "portal" ? L.portalRound : L.week;
    if (r.stage === "open" && top >= 18 && wk >= r.commitWeek - 3 && r.offers.length > 0) {
      // schools that offered come first, then the most interested others
      const offering = sorted.filter(([tid]) => r.offers.includes(tid));
      const others = sorted.filter(([tid]) => !r.offers.includes(tid));
      r.stage = "top5";
      r.top5 = [...offering, ...others].slice(0, 5).map((x) => x[0]);
      if (r.top5.includes(L.userTid) || L.board.includes(p.id)) {
        r.history.unshift({ week: L.week, text: `Narrowed list to ${r.top5.length}` });
      }
    }
    if (r.stage === "committed") {
      // decommitment risk if another offering school is far ahead
      const cur = r.interest[r.committedTo!] ?? 0;
      const rival = sorted.find(([tid]) => tid !== r.committedTo && r.offers.includes(tid));
      if (rival && rival[1] > cur * 1.4 && rng.chance(0.1) && spots(rival[0]) > 0) {
        const old = r.committedTo!;
        r.history.unshift({ week: L.week, text: `Decommitted from ${team(L, old).name}` });
        if (old === L.userTid) addNews(L, "recruit", `${playerName(p)} has decommitted from ${team(L, old).name}.`, { tid: old, pid: p.id, user: true });
        spotsCache.set(old, spots(old) + 1);
        commitTo(L, p, rival[0]);
        spotsCache.set(rival[0], spots(rival[0]) - 1);
      }
      continue;
    }
    if (wk < r.commitWeek) continue;
    const late = wk - r.commitWeek;
    const patience = Math.max(0.45, 1 - 0.07 * late);
    const thr = COMMIT_THRESHOLD[r.stars] * (r.kind === "portal" ? 0.6 : 1) * patience;
    const cands = sorted.filter(([tid, v]) => r.offers.includes(tid) && v >= thr && spots(tid) > 0);
    if (!cands.length) continue;
    // weighted choice favouring the leader
    const w = cands.map(([, v]) => Math.pow(v, 4));
    const pick = cands[rng.weighted(w)][0];
    commitTo(L, p, pick);
    spotsCache.set(pick, spots(pick) - 1);
  }
}

/** Sign all verbal commitments (early or late signing period). */
export function signCommits(L: League, label: string) {
  let userSigned = 0;
  for (const p of L.players) {
    const r = p.recruit;
    if (!r || r.stage !== "committed" || r.kind !== "hs") continue;
    r.stage = "signed";
    r.history.unshift({ week: L.week, text: `Signed with ${team(L, r.committedTo!).name}` });
    if (r.committedTo === L.userTid) userSigned++;
  }
  dirtyRec(L);
  if (userSigned) addNews(L, "recruit", `${label}: ${userSigned} recruit${userSigned > 1 ? "s" : ""} signed letters of intent with ${team(L, L.userTid).name}.`, { tid: L.userTid, user: true });
}

/** Class points for a team (stars-based). */
export function classPoints(L: League, tid: number, kind: "hs" | "portal" = "hs"): number {
  let pts = 0;
  for (const p of commitsFor(L, tid)) if (p.recruit!.kind === kind) pts += STAR_POINTS[p.recruit!.stars];
  return pts;
}

export function classRankings(L: League, kind: "hs" | "portal" = "hs"): { tid: number; pts: number; rank: number; n: number; avgStars: number }[] {
  const by = new Map<number, { pts: number; n: number; stars: number }>();
  for (const p of L.players) {
    const r = p.recruit;
    if (!r || r.kind !== kind || r.committedTo === null || (r.stage !== "committed" && r.stage !== "signed")) continue;
    const e = by.get(r.committedTo) ?? { pts: 0, n: 0, stars: 0 };
    e.pts += STAR_POINTS[r.stars];
    e.n++;
    e.stars += r.stars;
    by.set(r.committedTo, e);
  }
  const arr = L.teams.map((t) => {
    const e = by.get(t.id) ?? { pts: 0, n: 0, stars: 0 };
    return { tid: t.id, pts: e.pts, n: e.n, avgStars: e.n ? e.stars / e.n : 0, rank: 0 };
  });
  arr.sort((a, b) => b.pts - a.pts || b.avgStars - a.avgStars);
  arr.forEach((x, i) => (x.rank = i + 1));
  return arr;
}

/** Final signing: uncommitted recruits pick the best offer they have. */
export function finalSigning(L: League) {
  const rng = rngOf(L);
  signCommits(L, "Signing Day");
  const open = L.players
    .filter((p) => p.recruit && p.recruit.kind === "hs" && p.recruit.stage !== "signed")
    .sort((a, b) => recruitValue(b) - recruitValue(a));
  for (const p of open) {
    const r = p.recruit!;
    const cands = Object.entries(r.interest)
      .map(([k, v]) => [Number(k), v] as [number, number])
      .filter(([tid]) => r.offers.includes(tid) && openSpots(L, tid) > 0)
      .sort((a, b) => b[1] - a[1]);
    if (cands.length) {
      commitTo(L, p, cands[0][0]);
      r.stage = "signed";
      continue;
    }
    // late scramble: programs with open spots take remaining players at their level
    if (rng.chance(0.65)) {
      const needy = L.teams.filter((t) => t.id !== L.userTid && openSpots(L, t.id) > 0);
      const level = (pr: number) => 38 + 0.26 * pr;
      const fits = needy.filter((t) => level(t.prestige) - (p.ovr + 6) < 9);
      if (fits.length) {
        const ts = fits.sort((a, b) => Math.abs(level(a.prestige) - (p.ovr + 6)) - Math.abs(level(b.prestige) - (p.ovr + 6))).slice(0, 6);
        const t = rng.pick(ts);
        r.offers.push(t.id);
        commitTo(L, p, t.id);
        r.stage = "signed";
        continue;
      }
    }
    r.stage = "unsigned";
    p.status = "unsigned";
  }
  dirtyRec(L);
  rostersDirty(L);
}

/** Scouted view of a rating for the user. Deterministic noise per player and level. */
export function scoutNoise(p: Player, salt: number, level: number): number {
  const sds = [9, 5.5, 3, 1];
  let h = (p.faceSeed ^ (salt * 2654435761)) >>> 0;
  h = Math.imul(h ^ (h >>> 16), 0x45d9f3b) >>> 0;
  h = Math.imul(h ^ (h >>> 16), 0x45d9f3b) >>> 0;
  const u1 = ((h & 0xffff) + 1) / 65537;
  const u2 = ((h >>> 16) + 1) / 65537;
  const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  return z * sds[Math.min(3, Math.max(0, level))];
}

export function scoutedOvr(p: Player): number {
  const lvl = p.recruit?.scout ?? 3;
  return Math.round(clamp(p.ovr + scoutNoise(p, 1, lvl), 1, 99));
}
export function scoutedPot(p: Player): number {
  const lvl = p.recruit?.scout ?? 3;
  return Math.round(clamp(p.pot + scoutNoise(p, 2, lvl) * 1.3, 1, 99));
}
