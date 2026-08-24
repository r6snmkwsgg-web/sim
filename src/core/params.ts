/**
 * Every tunable constant in Milestone 0, in one file.
 *
 * The emergence claim (§5) is only meaningful if the utility function's shape
 * is fixed and inspectable. If you tune anything, tune it here, and re-run the
 * ablation control — the target pattern must come from social memory, not
 * from a parameter that hard-codes it.
 */

export const P = {
  // ---- world -------------------------------------------------------------
  WORLD: 64,                 // grid side (§5: one 64×64 region)
  TICKS: 2000,               // §5
  N_AGENTS: 20,              // §5

  // Atmospheric cycle. Resource kind 0 is only gatherable while the cycle is
  // in its "open" phase (§2.1: a material workable only during certain
  // atmospheric conditions). Agents perceive the scalar, never a season name.
  ATMOS_PERIOD: 250,
  ATMOS_OPEN: 90,            // ticks per period during which kind 0 is open

  // ---- resources ---------------------------------------------------------
  // Kinds are numeric everywhere inside the simulation (the veil, §2.2).
  // Display names (thren / pith / osk) exist only in the viewer and docs.
  RESOURCES: [
    { // kind 0 — "thren": seasonal, nutritious, hoardable
      nodes: 26, clusterSpread: 9, cap: 34, regen: 0.09, gatherRate: 1.3,
      nutrition: 11, carryDecay: 0.004, cacheDecay: 0.0008, seasonal: true,
    },
    { // kind 1 — "pith": common subsistence, decays too fast to hoard
      nodes: 85, clusterSpread: 26, cap: 9, regen: 0.030, gatherRate: 1.5,
      nutrition: 5, carryDecay: 0.045, cacheDecay: 0.035, seasonal: false,
    },
    { // kind 2 — "osk": few rich clusters → local surplus, spatial inequality
      nodes: 16, clusterSpread: 4, cap: 22, regen: 0.045, gatherRate: 1.1,
      nutrition: 8, carryDecay: 0.010, cacheDecay: 0.003, seasonal: false,
    },
  ],
  N_CLUSTERS: [4, 10, 3],    // spatial clusters per kind

  // ---- agent physiology --------------------------------------------------
  ENERGY_MAX: 100,
  START_ENERGY: 70,
  BASE_DRAIN: 0.32,          // energy per tick, existing
  MOVE_DRAIN: 0.12,          // extra per move
  HEALTH_MAX: 100,
  STARVE_DAMAGE: 0.6,        // health per tick at zero energy
  HEALTH_REGEN: 0.12,        // per tick when energy > 55
  EAT_AMOUNT: 1.6,           // units consumed per eat action
  CARRY_MAX: 24,             // total units carried

  // ---- perception --------------------------------------------------------
  VISION: 7,                 // chebyshev radius
  SIGNAL_RADIUS: 13,
  SIGNAL_TTL: 6,             // ticks a signal stays audible
  SPILL_DECAY: 0.02,         // dropped goods rot fast

  // ---- actions -----------------------------------------------------------
  GIVE_FRACTION: 0.45,       // fraction of carried stock offered per give
  GIVE_MAX: 3.0,
  TAKE_AMOUNT: 2.4,
  ATTACK_DAMAGE: 9,
  ATTACK_SPOIL: 0.35,        // fraction of victim's carried goods mugged
  SIGNAL_COST: 0.4,

  // ---- traits (8 of the §3.2 list) ---------------------------------------
  TRAITS: ['curiosity', 'aggression', 'sociability', 'riskTolerance',
           'conformity', 'patience', 'empathy', 'statusSensitivity'] as const,
  TRAIT_MEAN: 0.5,
  TRAIT_SD: 0.16,

  // ---- drives (4 of the §3.2 list) ----------------------------------------
  // survival: energy. safety: freedom from recent threat. belonging: recency
  // of positive social contact. status: relative stored wealth.
  DRIVES: ['survival', 'safety', 'belonging', 'status'] as const,
  DRIVE_BASE: { survival: 1.0, safety: 0.75, belonging: 0.62, status: 0.4 },
  BELONGING_DECAY: 0.006,    // belonging satiation decay per tick
  SAFETY_RECOVERY: 0.012,    // threat memory fades
  STATUS_HALF_WEALTH: 26,    // stored value at which status satiation = 0.5

  // ---- memory ------------------------------------------------------------
  EPISODIC_CAP: 256,         // ring buffer per agent (§3.3: memory is lossy)
  RECENCY_TAU: 260,          // ticks, retrieval recency decay
  RETRIEVE_K: 6,

  // social memory update sizes
  TRUST_GIFT: 0.16,          // received a gift
  TRUST_GIFT_GIVER: 0.05,    // giving also warms the giver toward recipient
  TRUST_THEFT: -0.30,        // was robbed (and saw it)
  TRUST_ATTACK: -0.45,
  TRUST_DECAY: 0.0006,       // drift toward 0 per tick (relationships fade)
  FAMILIARITY_STEP: 0.02,

  // ---- decision scoring ---------------------------------------------------
  NOISE_TEMP: 0.35,          // gumbel temperature (§3.4: never dominant)
  // give scoring: w_need * empathy * perceivedNeed + w_trust * trust + w_fam * familiarity
  GIVE_W_NEED: 2.1,
  GIVE_W_TRUST: 3.2,         // ← the social-memory term the ablation freezes
  GIVE_W_FAM: 0.5,
  GIVE_COST_W: 2.6,          // marginal food value of what is given away
  TAKE_W_NEED: 3.0,
  TAKE_RISK_W: 2.2,
  TAKE_TRUST_W: 2.8,         // don't rob those you trust
  ATTACK_THRESHOLD: 0.55,    // aggression gate
  FOLLOW_W: 1.1,
  EXPLORE_W: 0.8,

  // distress signalling: emitted when starving; empathetic hearers respond
  DISTRESS_ENERGY: 22,
  RESPOND_W: 1.6,
} as const;

export type TraitName = (typeof P.TRAITS)[number];
export type DriveName = (typeof P.DRIVES)[number];
