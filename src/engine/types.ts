// Core data model. Everything here is plain data so a league can be
// structured-cloned into IndexedDB and exported as JSON.

export type Pos = "PG" | "SG" | "SF" | "PF" | "C";
export const POSITIONS: Pos[] = ["PG", "SG", "SF", "PF", "C"];

export type Race = "white" | "black" | "brown" | "asian";

export interface Ratings {
  ins: number; // inside scoring / finishing
  mid: number; // mid-range
  three: number; // three-point
  ft: number; // free throw
  hnd: number; // ball handling
  pas: number; // passing
  iq: number; // basketball IQ
  perD: number; // perimeter defense
  intD: number; // interior defense
  stl: number; // steals / hands
  blk: number; // shot blocking
  reb: number; // rebounding
  ath: number; // athleticism (speed, quickness, vertical)
  str: number; // strength
  end: number; // endurance
}
export type RatingKey = keyof Ratings;
export const RATING_KEYS: RatingKey[] = [
  "ins", "mid", "three", "ft", "hnd", "pas", "iq",
  "perD", "intD", "stl", "blk", "reb", "ath", "str", "end",
];

/** Per-player shot tendencies the coach controls, 0-10 (5 = normal). */
export interface Tendencies {
  three: number;
  mid: number;
  inside: number;
  drive: number;
}

export interface StatLine {
  g: number;
  gs: number;
  min: number;
  pts: number;
  fgm: number;
  fga: number;
  tpm: number;
  tpa: number;
  ftm: number;
  fta: number;
  orb: number;
  drb: number;
  ast: number;
  stl: number;
  blk: number;
  tov: number;
  pf: number;
}
export const STAT_KEYS: (keyof StatLine)[] = [
  "g", "gs", "min", "pts", "fgm", "fga", "tpm", "tpa", "ftm", "fta",
  "orb", "drb", "ast", "stl", "blk", "tov", "pf",
];

export interface PlayerSeasonStats extends StatLine {
  season: number;
  tid: number;
  year: number; // class year that season (1=FR..5=5th year)
  rs: boolean; // redshirted that season
}

export interface RatingsSnapshot {
  season: number;
  ovr: number;
  pot: number;
  r: Ratings;
}

export type PrefKey = "pt" | "prestige" | "proximity" | "contender" | "coach" | "facilities" | "nil";
export const PREF_KEYS: PrefKey[] = ["pt", "prestige", "proximity", "contender", "coach", "facilities", "nil"];

export type RevealKey = "film" | "live" | "coach";
export type CatKey = "shooting" | "finishing" | "playmaking" | "perimeterD" | "interiorD" | "rebounding" | "athleticism";

export interface Goal {
  id: string;
  kind: "wins" | "conf" | "confchamp" | "recruit" | "ranked" | "ncaa" | "sweet16" | "final4";
  text: string;
  target: number;
  stretch?: boolean;
  reward: { kind: "points" | "prestige" | "security"; amount: number; text: string };
  done: boolean;
  failed?: boolean;
}
export type RecruitStage = "open" | "top5" | "committed" | "signed" | "unsigned";

export interface RecruitInfo {
  kind: "hs" | "portal";
  classSeason: number; // season the player enrolls / becomes eligible
  stars: number; // 1-5 (public)
  rank: number; // national rank among this class
  posRank: number;
  hs?: { pts: number; reb: number; ast: number }; // high school per-game stats
  prefs: Record<PrefKey, number>; // 1-5 importance
  interest: Record<number, number>; // teamId -> interest (0..)
  offers: number[]; // teamIds with scholarship offers
  visits: number[]; // teamIds an official visit was taken to
  nil: Record<number, number>; // teamId -> NIL offer ($K / yr)
  stage: RecruitStage;
  top5: number[];
  committedTo: number | null;
  commitWeek: number; // earliest week a decision can happen
  scout: number; // user team's scouting level 0-3 (one per reveal below)
  /** (older saves) what the user's staff had found out before categories */
  reveals?: RevealKey[];
  /** rating categories the user's staff has scouted */
  seen?: CatKey[];
  /** the user has talked to his coach (work ethic and potential known) */
  talked?: boolean;
  lastAction: Record<string, number>; // `${tid}:${action}` -> week
  /** schools that were already recruiting him (Warm or better) when the rankings came out */
  early?: number[];
  fromTid?: number; // portal: previous team
  history: { week: number; text: string }[]; // events shown on the profile
}

export interface Injury {
  name: string;
  games: number; // games remaining
}

export type PlayerStatus = "active" | "recruit" | "portal" | "graduated" | "drafted" | "left" | "unsigned";

export interface Player {
  id: number;
  first: string;
  last: string;
  pos: Pos;
  archetype: string;
  hgt: number; // inches
  wgt: number; // lbs
  wing: number; // wingspan inches
  city: string;
  state: string;
  lat: number;
  lon: number;
  faceSeed: number;
  race: Race;
  r: Ratings;
  ovr: number;
  pot: number; // true potential (hidden)
  potErr: number; // persistent error in what the user sees for own players
  workEthic: number; // 0-100
  loyalty: number; // 0-100: resistance to transferring
  tid: number | null;
  status: PlayerStatus;
  year: number; // years in college so far incl. current (1=FR). 0 for HS recruits
  eligUsed: number; // seasons of eligibility used
  redshirt: boolean; // redshirting the current season
  usedRedshirt: boolean;
  jersey: number;
  tend: Tendencies;
  injury: Injury | null;
  stats: PlayerSeasonStats[];
  hist: RatingsSnapshot[];
  awards: { season: number; name: string }[];
  transfers: { season: number; from: number; to: number }[];
  recruit: RecruitInfo | null;
  recruitedBy?: { tid: number; season: number; stars: number; rank: number; kind: "hs" | "portal"; hs?: { pts: number; reb: number; ast: number } };
  draft?: { season: number; round: number; pick: number; team: string };
  nilDeal: number; // $K per year with current team
  morale: number; // 0-100
  leftSeason?: number; // season the player left college
  retiredReason?: string;
  gameHigh: { pts: number; reb: number; ast: number };
}

export type Tempo = 1 | 2 | 3 | 4 | 5; // very slow .. very fast
export type OffFocus = "inside" | "balanced" | "perimeter";
export type DefScheme = "man" | "zone" | "press";
export type RebFocus = "crash" | "balanced" | "getback";

export interface Strategy {
  tempo: Tempo;
  offense: OffFocus;
  defense: DefScheme;
  rebounding: RebFocus;
}

export interface Rotation {
  auto: boolean;
  starters: number[]; // player ids (5)
  minutes: Record<number, number>; // pid -> target minutes
}

export type PracticeFocus = "balanced" | "shooting" | "inside" | "playmaking" | "defense" | "rebounding" | "conditioning";
export type PracticeIntensity = 1 | 2 | 3; // light, normal, intense

export interface PracticePlan {
  focus: PracticeFocus;
  intensity: PracticeIntensity;
  individual: Record<number, PracticeFocus>; // pid -> individual focus
}

export interface TeamSeason {
  season: number;
  coachId: number;
  w: number;
  l: number;
  cw: number;
  cl: number;
  hw: number;
  hl: number;
  aw: number;
  al: number;
  nw: number;
  nl: number;
  pf: number;
  pa: number;
  streak: number; // +n wins / -n losses
  confRank: number | null;
  confChamp: boolean; // regular season conference title (incl. ties)
  confTourney: string | null; // "Champion", "Runner-up", "Semifinals", ...
  post: { event: "ncaa" | "nit" | "cbi"; seed: number; result: string } | null;
  /** early-season event and where the team finished in it */
  event?: { key: string; name: string; place: number; of: number };
  apPre: number | null;
  apFinal: number | null;
  apBest: number | null;
  power: number;
  prestige: number; // prestige at the end of this season
  prestigeStart: number; // prestige when the season began
  recruitRank: number | null;
  recruitPts: number;
  roster: number[];
  /** wins over AP-ranked teams */
  rankedWins?: number;
}

export interface Team {
  id: number;
  slug: string;
  name: string;
  mascot: string;
  abbrev: string;
  short: string;
  cid: number;
  city: string;
  state: string;
  lat: number;
  lon: number;
  colors: [string, string];
  prestige: number;
  facilities: number;
  nilBudget: number; // $K per year
  /** booster/collective wealth: multiplies the NIL budget (1 = typical for the program's level) */
  boosters?: number;
  coachId: number;
  strategy: Strategy;
  rotation: Rotation;
  practice: PracticePlan;
  seasons: TeamSeason[];
  officialVisitsUsed: number;
  recruitPoints: number; // points left this week (AI uses this as budget too)
}

export interface Conference {
  id: number;
  slug: string;
  name: string;
  short: string;
  tier: number;
  confGames: number;
  tourneyTeams: number;
  /** conference tournament rounds played on the higher seed's floor (several one-bid leagues do this) */
  campusRounds?: number;
}

export interface CoachSeason {
  season: number;
  tid: number;
  w: number;
  l: number;
  cw: number;
  cl: number;
  result: string;
}

export interface Coach {
  id: number;
  first: string;
  last: string;
  tid: number | null;
  user: boolean;
  age: number;
  recruiting: number;
  development: number;
  tactics: number;
  rep: number; // reputation 0-100, grows with success
  faceSeed: number;
  race: Race;
  hired: number; // season hired at current team
  seasons: CoachSeason[];
  security: number; // 0-100 (user: job security meter)
  retired: boolean;
  awards: { season: number; name: string }[];
}

export type GameType = "nc" | "conf" | "ctourn" | "ncaa" | "nit" | "cbi";

export interface Game {
  id: number;
  season: number;
  day: number;
  home: number;
  away: number;
  neutral: boolean;
  type: GameType;
  played: boolean;
  hs: number;
  as: number;
  ot: number;
  tourney?: { key: string; round: number; slot: number };
  event?: string; // e.g. holiday tournament name
  /** the user's game prep level for this game (shown on the box score) */
  prep?: number;
  /** user games: the opponent's AP rank and how much stronger they were (power) at tip-off */
  oppRank?: number | null;
  oppEdge?: number;
  /** user games decided in the final seconds: who hit the go-ahead shot, and for which side (0 home, 1 away) */
  clutch?: { pid: number; name: string; side: 0 | 1; secs: number };
  hasBox?: boolean;
  hasPbp?: boolean;
}

export interface BoxLine extends Omit<StatLine, "g" | "gs"> {
  pid: number;
  name: string;
  pos: Pos;
  starter: boolean;
  pm: number;
}

export interface TeamBox {
  tid: number;
  pts: number;
  halves: number[];
  lines: BoxLine[];
}

export type PbpKind = "fg" | "ft" | "orb" | "drb" | "to" | "stl" | "blk" | "foul" | "ofoul" | "sub" | "lu" | "inj" | "info";
export type ShotType = "three" | "mid" | "post" | "drive" | "putback";

/**
 * A compact play-by-play event. t = seconds elapsed in game. The optional
 * fields (newer saves only) let a viewer rebuild the box score and shot
 * chart as the game unfolds.
 */
export interface PbpEvent {
  t: number;
  per: number; // 1,2 halves; 3+ overtimes
  side: 0 | 1; // 0 = home, 1 = away
  text: string;
  hs: number;
  as: number;
  k?: PbpKind;
  /** main player: shooter, rebounder, fouler, blocker, stealer, player subbed in */
  p?: number;
  /** other player: assister, player who lost the ball, blocked shooter, player subbed out */
  q?: number;
  st?: ShotType;
  m?: 0 | 1; // shot or free throw made
  /** shot location in feet on a half court: x across (0-50), y out from the baseline (basket at 25, 5.25) */
  x?: number;
  y?: number;
  /** player ids on the floor for this side after a lineup change */
  lu?: number[];
}

export interface BoxScore {
  gid: number;
  season: number;
  day: number;
  home: TeamBox;
  away: TeamBox;
  ot: number;
  neutral: boolean;
  type: GameType;
  poss: number;
  pbp?: PbpEvent[];
}

export interface BracketGame {
  slot: number;
  round: number;
  a: number | null; // team id
  b: number | null;
  sa: number | null; // seeds
  sb: number | null;
  gid: number | null;
  winner: number | null;
  region?: number;
  label?: string;
  /** play-in games feed a first-round slot */
  feed?: { slot: number; side: 0 | 1 };
  /** early-season events: where the winner goes instead of the next round */
  win?: BracketSpot;
  /** early-season events: losers drop into a consolation game */
  lose?: BracketSpot;
  /** early-season events: a placement game; the winner finishes here, the loser one place lower */
  place?: number;
}

export interface BracketSpot {
  round: number;
  slot: number;
  side: 0 | 1;
}

export interface Bracket {
  key: string; // "conf:12", "ncaa", "nit", "cbi", "mte:3" (early-season event)
  name: string;
  rounds: string[];
  games: BracketGame[];
  regions?: string[];
  champion: number | null;
  runnerUp: number | null;
  neutral: boolean;
  homeHigherSeedRounds?: number; // rounds hosted by higher seed
  days: number[]; // day each round is played
  playinDay?: number;
  playinName?: string;
}

export interface Poll {
  week: number;
  label: string;
  ranks: { tid: number; rank: number; prev: number | null; w: number; l: number; pts: number }[];
}

export interface AwardEntry {
  name: string;
  pid?: number;
  cid?: number; // coach id
  tid: number;
  playerName: string;
  line: string;
  confId?: number;
}

export interface SeasonAwards {
  season: number;
  national: AwardEntry[];
  allAmerica: AwardEntry[][]; // 1st, 2nd, 3rd teams
  conf: Record<number, { awards: AwardEntry[]; teams: AwardEntry[][] }>;
}

export interface SeasonSummary {
  season: number;
  champion: number | null;
  runnerUp: number | null;
  finalFour: number[];
  mop: AwardEntry | null;
  poy: AwardEntry | null;
  nitChamp: number | null;
  cbiChamp: number | null;
  userTid: number;
  userResult: string;
  apTop: number | null;
}

export interface RecordEntry {
  pid: number;
  name: string;
  tid: number;
  season: number;
  value: number;
  gid?: number;
  opp?: number;
}

export interface RecordBook {
  game: Record<string, RecordEntry[]>;
  season: Record<string, RecordEntry[]>;
  career: Record<string, RecordEntry[]>;
  teamSeason: Record<string, RecordEntry[]>; // pid = -1, name = team name
  /** program-level career leaders: tid -> stat -> entries */
  program: Record<number, Record<string, RecordEntry[]>>;
  programSeason: Record<number, Record<string, RecordEntry[]>>;
}

export type NewsKind = "game" | "recruit" | "injury" | "award" | "poll" | "job" | "portal" | "draft" | "league" | "milestone" | "team";

export interface NewsItem {
  id: number;
  season: number;
  day: number;
  dateLabel: string;
  kind: NewsKind;
  text: string;
  tid?: number;
  pid?: number;
  gid?: number;
  read: boolean;
  user: boolean; // concerns the user's team
}

export interface JobOffer {
  tid: number;
  season: number;
  reason: string;
}

export interface DraftPick {
  season: number;
  round: number;
  pick: number;
  /** negative for international and pro prospects (not college players) */
  pid: number;
  name: string;
  /** college team, or -1 for international and pro prospects */
  tid: number;
  pos: Pos;
  year: number;
  ovr: number;
  nbaTeam: string;
  /** club and country for international and pro prospects */
  from?: string;
}

export interface TransferMove {
  season: number;
  pid: number;
  name: string;
  from: number;
  to: number | null;
  ovr: number;
  stars: number;
}

export type Phase =
  | "preseason"
  | "regular"
  | "confTourney"
  | "selection"
  | "ncaa"
  | "seasonEnd"
  | "carousel"
  | "draft"
  | "portal"
  | "signing";

export interface Settings {
  nil: boolean;
  portal: boolean;
  bracketSize: 64 | 68 | 76;
  rosterMax: number;
  canBeFired: boolean;
  recruitingDifficulty: 1 | 2 | 3; // easy, normal, hard
  injuries: boolean;
  keepAllBoxScores: boolean;
  homeCourt: number; // points of home advantage, roughly
  autoRecruit: boolean; // the user's staff recruits automatically
  /** transfer portal activity: 1 = modern era (about half of players enter), 0.35 = the early portal years */
  portalRate: number;
}

export interface SeasonArchive {
  season: number;
  games: Game[];
  brackets: Bracket[];
  polls: Poll[];
  power: { tid: number; power: number; off: number; def: number; sos: number }[];
  recruitClasses: { tid: number; pts: number; rank: number; pids: number[] }[];
  draft: DraftPick[];
  transfers: TransferMove[];
  standings: { cid: number; order: number[] }[];
}

export interface League {
  id: string;
  name: string;
  version: number;
  created: number;
  updated: number;
  seed: number;
  rng: number; // rng state
  settings: Settings;
  startSeason: number;
  season: number;
  phase: Phase;
  day: number; // regular-season day index; also used for postseason days
  week: number; // recruiting week counter within the current cycle
  portalRound: number;
  userTid: number;
  userCid: number; // user coach id
  teams: Team[];
  conferences: Conference[];
  players: Player[]; // in-memory players: active, recruits, portal
  coaches: Coach[];
  nextPid: number;
  nextGid: number;
  nextNid: number;
  nextCoachId: number;
  games: Game[]; // current season games
  brackets: Bracket[];
  polls: Poll[];
  power: Record<number, { power: number; off: number; def: number; sos: number }>;
  news: NewsItem[];
  history: SeasonSummary[];
  awards: SeasonAwards[];
  records: RecordBook;
  draftHistory: DraftPick[];
  transfers: TransferMove[]; // current cycle
  transferLog: TransferMove[]; // every completed transfer, kept forever
  jobOffers: JobOffer[];
  vacancies: number[];
  realign: { tid: number; toCid: number; accepted: boolean | null }[];
  fired: boolean;
  /** user's coaching points left this week (recruiting and game prep share them) */
  recruitPts: number;
  recruitPtsMax: number;
  /** this season's goals for the user, with rewards */
  goals?: { season: number; list: Goal[] };
  /** extra weekly coaching points earned from goals this season */
  pointsBonus?: number;
  /** `${season}:${day}` of the last recruiting week started, so each one runs once */
  weekStarted?: string;
  /** goals completed across every season */
  goalsDone?: number;
  /** game prep bought for the user's next game; `weekPaid` is the part paid this week (refundable) */
  prep?: { opp: number; level: number; paid: number; week: number; weekPaid: number };
  /** player ids the user has on the recruiting board */
  board: number[];
  achievements: { season: number; name: string }[];
  /** set when the engine wants the UI to stop simming (e.g. job offers) */
  stopReason: string | null;
}
