# OpenCivilization

An artificial civilization laboratory. The governing rule, from [SPEC.md](SPEC.md):

> **Create the conditions for civilization. Do not write the civilization yourself.**

This repository currently contains exactly one thing, built to completion before
anything else: **Milestone 0, the vertical slice** (SPEC §5). Per §0, nothing
from the §7 roadmap exists yet — a project like this fails by breadth, not by
depth.

## Milestone 0 — status: target phenomenon demonstrated

The slice: one 64×64 region, 20 agents, all T1 utility cognition (**zero LLM
calls**), 8 traits, 4 drives, episodic + social memory only, 3 resources (one
seasonal), nine actions (`move gather eat store give take follow attack
signal`), 2,000 ticks in ~1 second wall clock, and a **complete causal ledger**
— every state change attributed to a world rule, an agent decision, a
stochastic event, or a player intervention, verified by bit-for-bit replay.

**The target phenomenon (§5): reciprocal exchange without a trade mechanic.**
There is no `trade()` action and no reciprocity term wired into the world.
There is `give`, there is `take`, and there is a social memory that records
who did which to whom.

### Result

Giving is measured per *opportunity* (a tick spent adjacent to another agent
while carrying enough to give), classified by what the giver has experienced
of the target:

| give rate toward… | main run | social memory ablated |
|---|---|---|
| prior givers | 4.71% | 3.15% |
| strangers | 1.93% | 2.70% |
| known transgressors | 1.46% | 2.31% |
| **reciprocity contingency** | **2.44×** | **1.16×** |
| **withholding ratio** | **0.76×** | 0.85× |
| pairwise rate correlation | 0.68 | 0.16 |

(seed 11, stream 1 — reproduce with `npm run demo`)

Agents give to those who gave to them at ~2.4× the rate they give to
strangers, and give known transgressors less than strangers — stable
partnerships with alternating gifts, visible as concentrated ribbons in the
viewer's gift-flow overlay. (An earlier build carried a balance-tracking term
in the give-scoring; the Test 1 scan below caught it and it was deleted — the
pattern survives on learned trust alone, which makes the claim stronger.)

### Held to the §4.2 emergence criteria

1. **Unscripted** — no `trade` code path; the give-scoring uses empathy ×
   perceived need plus the *learned* trust record, nothing pair-specific — and `npm run verify` scans the mechanic layer for trading vocabulary.
2. **Traceable** — `npm run trace` expands any gift backward through the
   ledger: gift → decision → trust record → the counter-gift that built it →
   … (a test asserts this chain exists).
3. **Reproducible-in-kind** — `npm run sweep`: **11/12** independent noise
   streams on the same world show the pattern (median contingency 2.44×).
4. **Non-retrievable** — no pretrained model to retrieve from at M0. The
   analogous control is the **ablation**: the same world, same utility
   function, same noise stream, with social memory writes frozen. **0/12**
   ablated runs reach the bar (median contingency 1.21×, correlation ≈ 0).
   The pattern demonstrably comes from social memory, not from the utility
   function's shape — which is precisely what §5 demands.

`npm run verify` runs a six-step falsification protocol in order, stopping at
the first failure: mechanic-layer vocabulary scan, ledger-hash determinism, a
per-decision log of the social memory read while scoring (the memory→decision
edge, inspectable), windowed pair correlation with a punishment check, the
ablated null, and a ten-stream repetition. It prints both raw-count and
opportunity-normalized correlations; the raw-count form is confounded by
co-location (pairs that spend a window together give more in both directions
regardless of memory — the ablated run proves it), so the normalized form is
the discriminating one.

Honest caveats: the withholding ratio is noisy across streams (0.2×–1.5×; the
transgressor class is small because defections are rare), and trust-weighted
giving is itself a designed capacity — what emerges is the *pattern* of who
ends up bound to whom, not the capacity to be bound. M0 validates the
architecture; it does not claim an institution.

## Running it

```
npm install        # dev tooling only; the simulation has zero runtime deps
npm test           # determinism, ledger replay, veil, perf, reciprocity
npm run demo       # canonical run + ablated control → runs/
npm run sweep      # 12 noise streams × (main + ablated)
npm run trace      # causal ancestry of the run's final gift (§4.1)
npm run view       # L3 viewer at http://localhost:8737
```

`node dist/cli/run.js --seed N --stream N [--ablate-social] [--out dir]` for
arbitrary runs.

## The viewer (SPEC §6, layer L3 only)

A top-down data view in the §6.2 survey-cartography palette: hypsometric
terrain kept near-silhouette, resources on the earth ramp (seasonal nodes draw
hollow while the atmosphere seals them), agents as marks, gifts in `--signal`,
defections in `--isogloss`, cumulative exchange as flow ribbons, the final
trust web on demand. The timeline scrubber shows the seasonal windows and
every social event; **trace mode** (click any event) illuminates its causal
ancestors and drops everything else to near-silhouette, per §6.5. No 3D yet —
that is M6.

## Layout

```
SPEC.md                     the binding document (v2)
src/core/params.ts          every tunable constant, in one file
src/core/rng.ts             seeded RNG; no Math.random, no clock, anywhere
src/world/world.ts          worldgen + world rules (atmosphere, regrowth)
src/agents/agent.ts         agent state (§3.2 subset)
src/agents/memory.ts        episodic ring buffer + scored retrieval; social records
src/agents/decide.ts        the T1 utility decision loop (§3.4)
src/engine/engine.ts        tick loop; every mutation writes a ledger entry
src/engine/ledger.ts        the causal ledger (§4.1) + trace trees
src/engine/replay.ts        rebuilds the full state from the ledger alone
src/engine/metrics.ts       §4.3 instrumentation (M0 subset)
src/cli/                    run / sweep / trace / serve
src/test/                   the five invariants, as tests
viewer/index.html           the L3 instrument
```

Design invariants the tests enforce:

- **Determinism** — a run is a pure function of (seed, stream). Same seed +
  different stream = same world, different luck (§4.2.3's setup).
- **Ledger completeness** — replaying the ledger from the seed reproduces the
  final state, memory and social records included, bit for bit. No
  unattributed mutations (§4.1).
- **The veil** (§2.2) — percepts are ids, coordinates, and quantities.
  Resource kinds are integers; the names thren/pith/osk exist only in the
  viewer and this file. A test greps percepts for leaked human words.
- **Budget** — 2,000 ticks under 30s (currently ~1s).

## What is deliberately not here

Cognition tiers T0/T2/T3, reproduction and death by age, the symbol layer,
beliefs, semantic/procedural/autobiographical memory, institutions,
technology, 3D rendering, God mode. Each belongs to a §7 milestone and ships
only when the previous milestone's target phenomenon is demonstrated and
logged. The next gate is **M1 — Generations**: a practice that outlives its
inventor by three generations.
