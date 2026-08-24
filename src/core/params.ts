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

/**
 * Milestone 1 — Generations (SPEC-M1.md). Everything here is gated behind
 * SimConfig.m1 so the committed M0 canonical ledger stays byte-identical.
 */
export const M1 = {
  AGENTS_START: 60,
  POP_CAP: 200,
  TICKS: 8000,

  // ---- mortality (§3.1): target lifespan ~400 ticks ----------------------
  HAZARD_BASE: 0.0002,       // per-tick death chance before senescence
  HAZARD_AGE: 260,           // senescence onset
  HAZARD_SLOPE: 0.00007,     // hazard growth per tick past onset
  FOUNDER_AGE_MAX: 250,      // founders start age-staggered

  // ---- reproduction and inheritance (§3.2) --------------------------------
  MATURITY: 110,
  REPRO_ENERGY: 45,          // both partners
  REPRO_WEALTH: 4,          // carried + cached energy value, both partners
  REPRO_COOLDOWN: 60,
  REPRO_CHANCE: 0.25,        // per eligible adjacent pair per tick
  REPRO_COST: 12,            // energy per parent
  CHILD_ENERGY: 55,
  HERITABILITY: 0.6,         // child = h·midparent + (1−h)·population draw
  MUTATION_SD: 0.05,
  DEP_AGE: 80,               // dependency: cannot gather until this age
  DEP_DRAIN: 0.55,           // dependents metabolize at this fraction
  KIN_TRUST: 0.5,            // birth bootstraps parent↔child social records
  KIN_FAM: 0.9,

  // ---- the observation channel (§3.3) -------------------------------------
  // Watching is weighting, not copying: a bounded additive bias on the
  // watcher's own scoring, scaled by its regard for the actor and its own
  // conformity, and capped well below the decision noise floor's reach.
  TOKENS: 8,                 // arbitrary signal tokens; zero mechanical effect
  OBS_THROTTLE: 20,          // min ticks between watch entries per (watcher, actor)
  OBS_SALIENCE: 0.25,
  OBS_TAU: 900,              // decay of accumulated observation influence
  OBS_GRID: 16,              // coarse spatial buckets for watched-gather locations
  OBS_GATHER_W: 0.55,
  OBS_GATHER_SAT: 3.0,       // weighted observations at which the bias caps
  // token bias is proportional to the observed frequency of each mark
  // (a hard per-option cap lets several options saturate simultaneously and
  // the differential vanishes — the §8.1 too-weak failure). Bounded by
  // OBS_TOKEN_W × conformity; the most conformist full-consensus observer
  // still deviates a few percent of the time via the decision noise.
  OBS_TOKEN_W: 3.0,
  OBS_TOKEN_DAMP: 0.75,      // pseudo-count damping small samples
  // M1 runs signal more readily than M0 (cheaper, more worth doing): the
  // token dimension only exists as a measurable substrate if agents emit
  // often enough to be heard. §8.1 calibration, mechanically token-neutral.
  SIGNAL_BOOST: 1.8,
  SIGNAL_COST: 0.2,

  // ---- world scaling for a population of ~60–200 --------------------------
  // Pith is arranged as three sites with IDENTICAL node count, cap, and
  // regen, placed rotationally symmetric about the map centre: the §2
  // fitness-neutral gather-site choice. Verified numerically in the report.
  PITH_SITES: 3,
  PITH_PER_SITE: 32,
  PITH_SITE_RADIUS: 20,
  PITH_SPREAD: 4.2,
  PITH_CAP: 8,
  PITH_REGEN: 0.085,
  THREN_NODES: 60,
  THREN_CLUSTERS: 1,
  THREN_REGEN: 0.14,
  THREN_CAP: 38,
  OSK_NODES: 40,
  OSK_CLUSTERS: 5,
  OSK_REGEN: 0.07,
  OSK_CAP: 22,
} as const;

/**
 * Milestone 2 — Symbols (SPEC-M2.md). Gated behind SimConfig.m2; M0 and M1
 * canonical hashes are pinned by tests and must not move.
 */
export const M2 = {
  TICKS: 10000,
  CONTACT_TICK: 6000,        // corridor opens; 4,000 ticks of contact follow
  AGENTS_PER_SIDE: 50,       // founders per population (grows toward ~80)
  POP_CAP: 220,

  // ---- the divide (§2.4): impassable band splitting the region -----------
  BARRIER_X0: 31,
  BARRIER_X1: 32,
  CORRIDOR_Y0: 28,
  CORRIDOR_Y1: 36,

  // ---- partial observability (§2.1, load-bearing) -------------------------
  // sight is local; a call carries beyond sight. The gap between the two
  // radii is where information asymmetry — and any reason to signal — lives.
  VISION: 3,
  SIGNAL_RADIUS: 10,

  // ---- per-side resources (identical mirrored halves) ---------------------
  PITH_SITES_PER_SIDE: 2, PITH_PER_SITE: 26, PITH_SPREAD: 3.6,
  PITH_CAP: 8, PITH_REGEN: 0.13,
  THREN_PANS_PER_SIDE: 1, THREN_PER_PAN: 30, THREN_SPREAD: 6,
  THREN_CAP: 38, THREN_REGEN: 0.17,
  OSK_CLUSTERS_PER_SIDE: 2, OSK_PER_CLUSTER: 12, OSK_SPREAD: 3,
  OSK_CAP: 22, OSK_REGEN: 0.09,

  // ---- private token↔kind associations (§2.2) -----------------------------
  // Each agent holds its own (token, kind, confidence) weights. Nothing is
  // stored at population level; nothing in the loop names a "right" answer.
  REFS: 3,                   // referent classes = the percept schema's kinds
  LEX_CAP: 3,                // confidence ceiling
  LEX_EMIT_MIN: 0.5,         // below this, coining pressure (§2.2)
  LEX_DELTA_FOUND: 0.25,     // hearer, on finding kind k after acting on T
  LEX_DELTA_EMIT: 0.18,      // emitter, on seeing the hearer succeed
  LEX_DELTA_FAIL: 0.18,      // hearer, on arriving and finding nothing
  LEX_DELTA_CO: 0.06,        // hear T while seeing a rich node (acquisition)
  LEX_LAT: 0.06,             // lateral: a grounding also weakens the mark's
                             // other-kind ties (associative competition),
                             // scaled by grounding strength (full at FOUND)
  HEED_W: 1.6,               // scoring weight for acting on an inferred tip
  HEED_CONF_MIN: 0.25,       // will not act on associations weaker than this
  HEED_WINDOW: 50,           // ticks allowed to reach the called site
  HEED_RADIUS: 4,            // "arrived" = within this of the emission origin
  ABUND_Q: 1.3,              // above cap: ONLY bloomed nodes are worth calling about
  // Blooms (§2.1's asymmetry, kept alive): a node occasionally surges far
  // past cap — a transient, privately-discovered windfall. Static sites
  // saturate into common knowledge; blooms are what there is to talk about.
  BLOOM_CHANCE: 0.05,        // per tick, one random node world-wide
  BLOOM_MULT: 2.5,           // surge target, × cap
  TRUST_TIP_GOOD: 0.04,      // a tip that worked out warms the hearer
  TRUST_TIP_BAD: -0.03,      // a wasted trip cools it
} as const;
