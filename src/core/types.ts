import type { TraitName } from './params.js';

/** Resource kinds are opaque integers inside the simulation (the veil, §2.2). */
export type Kind = 0 | 1 | 2;
export const KINDS: Kind[] = [0, 1, 2];

// ---------------------------------------------------------------------------
// Ledger (§4.1)
// ---------------------------------------------------------------------------

/** Every state change is attributed to exactly one of these. */
export type CauseKind = 'world' | 'agent' | 'stochastic' | 'player';

export interface LedgerEntry {
  id: number;
  tick: number;
  kind: CauseKind;
  /** machine-readable entry type, e.g. 'act.give', 'mem.trust', 'world.regen' */
  type: string;
  /** primary subject (agent id, or -1 for the world) */
  subject: number;
  /** entry-type-specific payload; must be sufficient to replay the mutation */
  data: Record<string, unknown>;
  /** ledger ids of the entries that caused this one */
  causes: number[];
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------

export type Action =
  | { t: 'move'; dx: number; dy: number }
  | { t: 'gather' }
  | { t: 'eat'; kind: Kind }
  | { t: 'store'; kind: Kind }
  | { t: 'give'; target: number; kind: Kind }
  | { t: 'take'; target: number; kind: Kind }        // target: agent id, or cache via takeCache
  | { t: 'takeCache'; owner: number; kind: Kind }
  | { t: 'follow'; target: number }
  | { t: 'attack'; target: number }
  | { t: 'signal'; mode: 0 | 1 }                     // 0 = distress, 1 = abundance ping
  | { t: 'rest' };

// ---------------------------------------------------------------------------
// Percepts (§2.2 — structured, no words for unnamed things)
// ---------------------------------------------------------------------------

export interface NodePercept {
  x: number; y: number; k: Kind; q: number; open: boolean;
}
export interface AgentPercept {
  id: number; x: number; y: number;
  /** coarse energy band 0..2 — you can see someone is starving, not their number */
  band: number;
  /** coarse carried-load band 0..2 */
  load: number;
}
export interface SignalPercept {
  from: number; x: number; y: number; mode: 0 | 1; age: number;
}
export interface CachePercept {
  owner: number; x: number; y: number; q: [number, number, number];
}
export interface Percept {
  tick: number;
  self: { x: number; y: number; energy: number; health: number;
          carried: [number, number, number]; cached: [number, number, number] };
  atmos: number;                       // 0..1 scalar, not a season name
  nodes: NodePercept[];
  agents: AgentPercept[];
  signals: SignalPercept[];
  caches: CachePercept[];
  spills: { x: number; y: number; k: Kind; q: number }[];
}

// ---------------------------------------------------------------------------
// Memory (§3.3 — M0: episodic + social only)
// ---------------------------------------------------------------------------

export type EpisodeType =
  | 'node-seen' | 'gift-in' | 'gift-out' | 'theft-in' | 'theft-seen'
  | 'attack-in' | 'attack-out' | 'attack-seen' | 'signal-heard' | 'ate'
  | 'starving' | 'gather-sealed';

export interface Episode {
  tick: number;
  type: EpisodeType;
  who: number;          // other agent involved, -1 if none
  x: number; y: number;
  k: number;            // resource kind, -1 if none
  amount: number;
  salience: number;     // 0..1
  ledger: number;       // id of the ledger entry that wrote this memory
}

export interface SocialRecord {
  trust: number;        // -1..1, learned
  familiarity: number;  // 0..1
  debt: number;         // net value received from them (positive = I owe)
  lastTick: number;
  lastLedger: number;   // ledger id of the most recent update to this record
}

// ---------------------------------------------------------------------------
// Agent state (§3.2 — persistent, serializable, model-independent)
// ---------------------------------------------------------------------------

export interface AgentState {
  id: number;
  alive: boolean;
  x: number; y: number;
  energy: number;
  health: number;
  carried: [number, number, number];
  traits: Record<TraitName, number>;
  followTarget: number;             // -1 none
  homeX: number; homeY: number;     // preferred cache site
  episodic: Episode[];
  epHead: number;                   // ring buffer write head
  social: Map<number, SocialRecord>;
  bornTick: number;
  diedTick: number;                 // -1 if alive
}

// ---------------------------------------------------------------------------
// World state
// ---------------------------------------------------------------------------

export interface ResourceNode {
  id: number;
  x: number; y: number;
  k: Kind;
  q: number;
}

export interface Cache {
  owner: number;
  x: number; y: number;
  q: [number, number, number];
}

export interface Spill {
  x: number; y: number;
  q: [number, number, number];
}

export interface ActiveSignal {
  from: number; x: number; y: number; mode: 0 | 1; tick: number;
}

export interface WorldState {
  tick: number;
  nodes: ResourceNode[];
  caches: Cache[];                  // one per (owner, site) actually used
  spills: Spill[];
  signals: ActiveSignal[];
  elevation: Float32Array;          // viewer flavor only; does not gate movement
}

export interface SimConfig {
  seed: number;
  stream: number;
  ticks: number;
  /** freeze social memory (trust/familiarity/debt) — the §5 control */
  ablateSocial: boolean;
}
