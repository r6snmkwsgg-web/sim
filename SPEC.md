# OpenCivilization
**Specification v2 — an artificial civilization laboratory**
---
## 0. How to read this document
This is a build order, not a wish list. Sections 1–5 are binding: they define what the system is, what it must not do, and the single vertical slice that must work before anything else is written. Section 6 defines how it looks. Section 7 is the roadmap. Section 8 lists the problems we do not know how to solve and are not going to fake.
If you are an implementer and you find yourself building something from Section 7 before Milestone 0 in Section 5 runs end to end, stop. A project like this fails by breadth, not by depth. Sixty half-built subsystems produce nothing; one closed loop over twenty agents produces a research instrument.
---
## 1. Thesis
Build a persistent world in which autonomous agents live, remember, learn, cooperate, betray, invent, believe, and die — and in which the structures we recognize as *civilization* are never written down by us, but arise from those agents' interactions.
The design rule that generates every other rule:
> **Create the conditions for civilization. Do not write the civilization yourself.**
Concretely:
**Don't do this**
```
if population > 10000:
    spawn_government()
```
**Do this**
```
Agents own things.
Agents make agreements.
Agents defect on agreements.
Agents can punish defectors, at a cost.
Agents can delegate punishment to others.
Agents remember who kept their word.
```
The second version has no government in it. Governments are one of the things it can produce. That difference is the whole project.
The success condition is not "the simulation makes civilizations." It is: **the simulation produces at least one structure we can causally trace to agent decisions, that no one on the team designed, and that we cannot explain away as retrieval.** Section 4 defines how we prove that. Everything else is scaffolding for that one claim.
---
## 2. The contamination problem
This is the central technical obstacle and most projects in this space ignore it.
If agents are driven by a pretrained language model, they already know what money is. They know what a king is, what a funeral is, what a rain god is. When such an agent "invents" currency on turn 4,000, we have learned nothing — we have watched a very expensive autocomplete retrieve a human institution and dress it as discovery.
An emergent-civilization simulator built on pretrained models is, by default, a machine for generating false positives.
Three defenses, all required.
### 2.1 An alien substrate
The world must not be Earth. Not cosmetically — structurally.
- Physics with different constants and at least one phenomenon with no Earth analogue.
- Biology with non-mammalian reproduction, lifespan, and kinship structures.
- Resources with properties that don't map to wood, iron, or grain — a material that is only workable during certain atmospheric conditions, a foodstuff that is contagious, an energy source that degrades the terrain it's drawn from.
- No calendar, no compass rose, no metals with familiar names.
The point is not flavor. The point is that a pretrained prior about *iron* is a wrong prior about *thren-salt*, so the agent has to actually reason from what it observed. Where the world is Earth-like, retrieval is indistinguishable from discovery. Where it is not, retrieval visibly fails, and only reasoning survives.
### 2.2 The veil
Agents perceive the world through a strict schema, not through prose describing an English-language scene. An agent receives structured percepts — entity IDs, measured quantities, relationship handles, sensory readings — and returns structured actions. Natural language is used *inside* the agent for reasoning and *between* agents only via the symbol layer (§3.5).
The veil enforces one rule: **the agent never receives a word for a thing it has not itself named.** If it perceives a recurring pattern in the sky, it gets coordinates and luminance, not "a star." Naming is an action agents take, and names propagate socially or not at all.
### 2.3 The prior audit
Every claimed emergent structure is checked against a control: the same prompt, the same agent architecture, zero world history. If a fresh agent with no episodic memory produces the same institution when asked, the institution was retrieved, not emerged. Log the result either way. A project honest about its false positives is worth more than one that isn't.
---
## 3. Architecture
### 3.1 Cognition tiers — the compute budget
This is the constraint that kills naive designs. A hundred thousand agents each making an LLM call per tick is financially impossible by three orders of magnitude. Design for it from line one.
Every agent runs at one of four tiers. Tier is dynamic and re-evaluated each simulation epoch.
| Tier | Population share | Cognition | Cost per decision |
|---|---|---|---|
| **T0 — Statistical** | ~90% | Aggregate demographic model. Individuals exist as rows, not minds. Births, deaths, migration, production. | ~0 |
| **T1 — Utility** | ~9% | Hand-written utility function over drives and percepts. Deterministic given state + seed. Full individual state, no language model. | microseconds |
| **T2 — Reflective** | ~1% | Small/local model. Periodic reasoning, goal revision, memory consolidation. Not every tick — on trigger. | milliseconds, cents |
| **T3 — Deliberative** | 10–100 agents | Frontier model. Full reasoning, invention, persuasion, long-horizon planning. | seconds, dollars |
**Promotion rules.** An agent moves up a tier when it: is observed by the player; enters a state its current tier can't represent (novel problem, contradicted belief, unmodelled relationship); acquires influence above a threshold; or is designated by an experiment. It demotes when idle, distant, and unremarkable.
**The fidelity contract.** Demotion must be lossy but not destructive. A T3 agent demoted to T1 keeps its memory store and its trait vector; it loses only the ability to generate novel reasoning until re-promoted. Nothing about an agent's identity may live only in a model's context window.
This tiering is also the rendering LOD system (§6.4). One hierarchy, two consumers.
### 3.2 Agent state
Persistent, serializable, model-independent. An agent is a database row plus a memory store, never a conversation history.
- **Identity** — id, names (self-given and other-given, these differ), age, species, lineage, birth site, current site, affiliations.
- **Traits** — 12–16 continuous values, normally distributed at birth, heritable with mutation, drifting slowly with experience. Curiosity, aggression, sociability, risk tolerance, conformity, patience, ambition, empathy, persistence, deceptiveness, novelty-seeking, status-sensitivity.
- **Drives** — competing, satiable, and re-weighted by experience. Survival, safety, belonging, status, mastery, novelty, autonomy, legacy. Competition between drives is where individuality comes from; an agent that wants both safety and novelty behaves less predictably than one that wants either alone.
- **Affect** — decaying scalars: satisfaction, fear, frustration, curiosity, loneliness, confidence, grief, attachment. These modulate decisions. They are not claims about experience; see §9.
- **Skills** — procedural competencies with proficiency and decay.
- **Beliefs** — propositions with confidence, source, and last-revision. Beliefs may be false. Beliefs are what religion, science, and propaganda are all made of.
### 3.3 Memory
Five stores, one retrieval interface.
- **Episodic** — timestamped events, each with salience, affect tag, confidence, and participant list.
- **Semantic** — generalizations extracted from episodes during consolidation. Where "fire burns" comes from.
- **Procedural** — skills.
- **Social** — per-relationship: trust, familiarity, affection, respect, fear, resentment, debt. Asymmetric. A's model of B is not B's model of B.
- **Autobiographical** — a compressed self-narrative, rebuilt periodically. This is what makes an agent's account of its own life stable across a thousand years of simulated time and thousands of forgotten episodes.
**Retrieval is scored, not exhaustive**: `salience × recency_decay × relevance × confidence`. Memory must be lossy. Perfect recall destroys the imperfect-information dynamics that make politics possible.
**Consolidation** runs on a schedule: cluster episodes, extract semantics, decay the unretrieved, strengthen the reinforced, and occasionally distort. Distortion is a feature. Two agents remembering the same event differently is the seed of every schism in the world.
### 3.4 Decision loop
```
percept (schema, veiled)
  → memory retrieval
  → drive weighting (traits × affect × situation)
  → candidate generation (tier-dependent)
  → scoring
  → exploration noise (small, tuned, never dominant)
  → action
  → world resolution
  → outcome
  → memory write + affect update + drive re-weight + belief revision
```
Randomness perturbs the ranking. It never replaces it. The target is **predictable rules, unpredictable consequences** — a system whose every step is explicable and whose thousand-step trajectory is not.
### 3.5 The symbol layer
Agents do not communicate in English. They communicate by emitting symbols from a per-population lexicon: `(symbol_token → referent → confidence)`.
- Symbols are coined by agents, initially arbitrary tokens.
- Meaning is negotiated: a listener infers a referent from context, and successful coordination reinforces the mapping while failure weakens it.
- Lexicons are per-population and drift. Isolated populations diverge. Contact produces borrowing.
- The LLM at T2/T3 reasons in English internally but only ever *transmits* through this layer.
This is the only honest way to get language evolution out of a system whose agents think in a fixed pretrained language. It is also research-grade hard — see §8.
---
## 4. Proving emergence
Without this section the project is an art piece.
### 4.1 The causal ledger
Every state change writes an entry attributing it to exactly one of: **world rule**, **agent decision**, **stochastic event**, or **player intervention**. No exceptions, no unattributed mutations. Any event in the world can then be expanded backward into the full tree of causes that produced it.
```
WHY DID THE COASTAL SETTLEMENTS FEDERATE?
  ├ resource shortfall (thren-salt, 12 seasons)      0.82  [world rule]
  ├ prior raid by inland group, year 341             0.64  [agent decision]
  ├ Vessik's status ambition                         0.83  [agent decision]
  ├ failed bilateral agreement, year 358             0.91  [agent decision]
  └ storm season displacement                        0.44  [stochastic]
```
This is not a debugging feature. It is the evidence base for every claim the project makes.
### 4.2 Falsifiable emergence criteria
A phenomenon counts as emergent only if it passes all four:
1. **Unscripted** — no code path names it, and no prompt mentions it.
2. **Traceable** — the ledger produces a complete causal chain to agent decisions.
3. **Reproducible-in-kind** — re-running from seed with a different RNG stream produces a structurally similar outcome at above-chance rate. One-offs are noise.
4. **Non-retrievable** — fails the §2.3 prior audit. A memoryless agent does not produce it on request.
### 4.3 Instrumentation
Run continuously, on every world: institutional count, lexicon divergence between populations, belief-network modularity, Gini coefficient, technology graph depth and branching factor, memory-distortion rate, cooperation-defection ratio, cultural transmission fidelity across generations. These are the numbers that distinguish a working simulation from a beautiful screensaver.
---
## 5. Milestone 0 — the vertical slice
**Nothing else is built until this runs.** Two weeks of work, not six months.
- One seed. One 64×64 region. No planet generation.
- 20 agents, all T1 utility cognition. **Zero LLM calls.**
- 3 resources, one of them seasonal.
- 8 traits, 4 drives, episodic + social memory only.
- Actions: move, gather, eat, store, give, take, follow, attack, signal.
- 2,000 ticks, under 30 seconds wall clock.
- Full causal ledger.
- Rendering: §6 layer L3 only — a top-down data view. No 3D yet.
**The target phenomenon: reciprocal exchange without a trade mechanic.**
There is no `trade()` action. There is `give` and there is `take`. If, over 2,000 ticks, agents develop stable patterns of giving to those who gave to them, and withhold from those who took — and the ledger shows it arose from social memory rather than from the utility function's shape — the architecture works. If it does not happen, the architecture is wrong and no amount of LLM cognition will rescue it.
This milestone is deliberately cheap and deliberately falsifiable. It tests the thesis before the thesis costs money.
---
## 6. Rendering, layers, and art direction
The world must be beautiful, and it must be beautiful in a way that serves observation rather than spectacle. This is not a diorama. It is an instrument.
### 6.1 The governing idea: an instrument, not a diorama
The visual identity **changes with observation altitude**, and each altitude borrows from a real scientific-visualization tradition. Zooming is not just a camera move; it is a change of instrument. This is the project's signature, and it should be the thing people remember.
| Altitude | Tradition it borrows from | Look |
|---|---|---|
| **Orbital** | Astronomical plate / spectral imaging | The planet as a lit body against deep field. Terminator line, atmospheric limb, cloud systems. Terrain readable only as albedo and biome mass. |
| **Regional** | Hypsometric survey chart, Admiralty sea chart | Contour lines, elevation tints, hatched escarpments, river networks drawn as ink. Settlements as symbols, not buildings. Territory as wash. |
| **Settlement** | Architect's chipboard model | Axonometric, physical, low-saturation. Structures as clean volumes with real shadow. Agents as moving marks. |
| **Agent** | Field notebook / case dossier | Portrait, trait plot, relationship graph, life timeline, memory excerpts. Type-driven, near-paper. |
Transitions between these are **continuous, not cut**. Contour lines dissolve into terrain relief as you descend; buildings resolve out of settlement symbols; an agent's dossier slides out of the mark representing it. The continuity is the point — one world, four instruments trained on it.
### 6.2 Palette
Derived from survey cartography and bathymetric charts, not from game UI convention.
```
--abyss        #0B1A2A   deep field, orbital ground
--bathyal      #16394F   ocean, deep panel fills
--shelf        #3E7A8C   shallow water, active state
--lowland      #7A8B5C   hypsometric green
--upland       #C8A97E   hypsometric tan
--summit       #EDE4D2   high elevation, chart paper, primary text on dark
--ink          #1C1A17   linework, text on light
--signal       #E0A02E   live events, anomalies, player attention
--isogloss     #B5479A   culture/language overlays — deliberately non-terrestrial
                          so data never reads as terrain
```
Two rules. Natural phenomena use the earth ramp (abyss → summit). Abstract data — territory, trade flow, language boundaries, belief spread — uses signal and isogloss, colours that cannot occur in the terrain. The player must never confuse a measurement for a place.
**Era drift**: as a civilization's technology graph deepens, its settlements' material palette shifts — earth and fibre, then fired and worked material, then refined and synthetic. The world's colour tells you what century you're in without a label.
### 6.3 The layer stack
Six composited layers, each independently toggleable. This is the "3D/2D layers" architecture:
- **L0 — Terrestrial (3D).** Heightfield terrain, water, atmosphere, weather, day/night. GPU-resident, chunked, streamed. The only layer that is fully volumetric.
- **L1 — Entities (3D, LOD-driven).** Agents and fauna. Billboard impostor → simple mesh → rigged mesh, driven by cognition tier (§3.1). A T3 agent is always a full mesh. A T0 population is a density field, not individuals.
- **L2 — Constructed (2.5D → 3D).** Settlements, roads, fields, monuments. Rendered as instanced modular kits; agent-designed structures assemble from a grammar rather than from a fixed prefab list, so buildings can look like nothing we authored.
- **L3 — Data overlays (2D vector, screen- or world-space).** Territory, trade volume as flow ribbons, climate fields, population density, lexicon isoglosses, belief prevalence, resource pressure. Drawn as clean vector work with real cartographic hatching and stipple, not translucent quads.
- **L4 — Annotation (2D).** Event markers, agent labels, place names in each population's own script, causal-trace threads drawn between related events.
- **L5 — Chrome (2D).** Panels, timeline scrubber, experiment controls. Restrained, near-monochrome, deferring entirely to the world.
Any layer can be soloed. A researcher should be able to run the whole simulation in L3 alone at 10,000× speed, and a player should be able to run L0–L2 with no overlays at all and just watch it live.
### 6.4 LOD is cognition tier
One hierarchy serves both systems. The agent the player is watching is T3-cognition *and* full-mesh rendering. The population beyond the horizon is T0-statistical *and* a density field. Promotion and demotion happen together, so visual detail and simulation detail never disagree — you cannot zoom in on something that isn't being thought about.
### 6.5 Time as a visual medium
The timeline scrubber is a primary interface element, not a debug tool.
- Scrub the entire recorded history at any speed.
- **Trace mode**: select any event; its causal ancestors illuminate across the map and back along the timeline, with everything else falling to near-silhouette.
- **Divergence view**: two experimental worlds side by side, sharing one timeline, with differing regions highlighted in signal.
- Long time-lapse renders — a thousand years of territory, language, and technology in ninety seconds — should be a one-click export. This is how the project shares results.
### 6.6 Motion
Restrained and diegetic. Weather, water, crowd flow, and the day/night terminator move because the world moves. UI motion is limited to the altitude transitions in §6.1 and to trace-mode illumination. No decorative easing, no ambient particle drift, no animated flourish that isn't reporting something true. Respect reduced-motion settings.
### 6.7 Typography and technical target
Display and place names in a humanist face with real cartographic character. Data, coordinates, and ledger output in a monospace. Body text in a neutral, high-legibility sans. Population scripts render in generated glyph sets that drift with their lexicons.
Target: WebGPU (Three.js/Bevy) or Godot 4. 60fps at settlement altitude with 2,000 visible entities; 30fps at orbital with a full continent streamed. Draw-call budget enforced from day one — the layer stack is only affordable if L1 and L2 are aggressively instanced.
---
## 7. Roadmap after Milestone 0
Each phase ships only when the previous phase's target phenomenon is demonstrated and logged.
- **M1 — Generations.** Reproduction, trait inheritance, death, cultural transmission. *Target: a practice that outlives its inventor by three generations.*
- **M2 — Symbols.** The §3.5 lexicon layer. Two isolated populations. *Target: measurable lexical divergence, then borrowing on contact.*
- **M3 — Reflection.** T2/T3 cognition introduced for a small elite. *Target: a goal no utility function could have produced.*
- **M4 — Institutions.** Multi-agent agreements, delegated enforcement. *Target: a rule that persists after every original signatory is dead.*
- **M5 — Technology.** Combinatorial invention over an alien materials graph. *Target: two isolated populations reaching the same capability by different routes.*
- **M6 — Full render stack.** L0–L2 in 3D, altitude transitions, era palette drift.
- **M7 — Experiments.** Paired worlds, controlled variables, automated comparison, publishable output.
- **M8 — Publication.** Seed sharing, world forking, community rulesets.
Modes (Observer, God, Experiment, Chaos, Apocalypse, Sandbox, Participant) layer on from M7. Every God-mode intervention is ledger-tagged as `player intervention` and is visible to any researcher reading the history. Agents interpret unexplained interventions however they will — which is, in itself, one of the more interesting experiments available.
---
## 8. Open research problems
These are stated as unsolved so that no one builds a fake version to close the ticket.
1. **Language evolution.** §3.5 is a plan, not a solution. Emergent signaling systems in the literature produce symbol sets agents cannot *reason in*, while pretrained models reason fluently in a language that cannot drift. Bridging those two layers is unsolved.
   *M2 result (recorded per SPEC-M2 §6; two protocol rounds, mechanics iterated once between them under a declared stopping rule, measurement thresholds never changed).* The drift half of the bridge exists in this codebase at T1: private outcome-grounded token–kind associations — with entrenchment, so a convention that has kept working resists conversion — produce population-level conventions that are kind-differentiated (permutation z 27–54, measured only on hearers who could not see the referent), coherent above the neutral-drift null in 12/12 streams, divergent between isolated populations in 12/12 (typically two classes per stream), and borrowed across a contact corridor in 12/12 (28 adoption events, 5–85 adopters each). Transmission fidelity — round 1's collapse mode, post-contact lexical churn — is stable across generations in 8/12 streams after entrenchment; the §6 verdict is **FULL in 8/12 streams, PARTIAL-SIGNALING floor in 12/12** (no cross-stream aggregation rule was preregistered, so both are recorded). Standing limitations, not tuned away: §5.2 communicative success sits at ≈1× matched controls (median 0.93 — calls predict *what* a hearer finds, never yet *whether*), trust-mediated borrowing is unestablished (adopters warmer in 2/12 streams only), and the low-cap resource class stays chronically thin in qualified speakers. M3 proceeds with a within-lifetime symbol layer per SPEC-M2 §6; nothing in this project calls the current layer "language". Full two-round protocol: docs/m2-protocol-run.txt.
2. **Authentic incorrect science.** Requires alien physics deep enough that pretrained priors genuinely fail, plus agents that reason only from in-world evidence. Partially addressed by §2.1; not solved.
3. **Genuinely novel concepts.** Recombination and invention are externally indistinguishable. §4.2 narrows the gap. It does not close it.
4. **Evolution at LLM timescales.** Selection needs thousands of generations; T3 cognition costs dollars per thousand ticks. These timescales differ by ~10³. The tier system is a mitigation, not an answer.
5. **Long-horizon coherence.** Whether an agent can remain recognizably itself across a million ticks of lossy memory is an empirical question this project is partly designed to ask.
---
## 9. Boundaries
**Sandboxing.** Agents may create unlimited chaos inside the world. Nothing inside the simulation grants real-world capability. No agent path reaches financial accounts, credentials, private communications, other users' data, unrestricted OS privileges, or network egress. Agents may improve their own in-world tools, knowledge, and organizations; modification of the simulation kernel, security boundary, or infrastructure requires explicit out-of-band authorization. **Maximum internal autonomy must never require elevated external permission** — this is a design constraint on the architecture, not a policy bolted on afterward.
**Interpretability without intrusion.** The thought log shows structured influences on a decision — drives, weights, retrieved memories, candidates considered — not raw private reasoning transcripts.
**Claims.** The affect variables in §3.2 are computational states that produce complex behavior. They are not evidence of subjective experience, and the project will not describe them as such. Consciousness is treated as an open question the simulation is not equipped to settle.
OpenCivilization does not claim to show that reality is simulated, or that anything about human minds follows from what happens here. It claims something narrower and more defensible: **that complex artificial worlds can be generated from simple rules and autonomous agents, and that we can prove which parts we did not write.**
---
## 10. The experience
You choose a seed. You set the physics, the biology, the scarcity. You press start.
Then you watch a world you do not control invent things you did not think of, for reasons you can trace and did not intend.
> *"I wrote the rules. I have no idea what happens next — and I can prove I didn't write this part."*
**END OF SPECIFICATION**

---

## Amendments

**A1 (M0 verification, adopted before M1).** Test 4 of the M0 verification
protocol is measured on **opportunity-normalized rates** (events per adjacent
tick), not raw counts. Raw pairwise counts measure adjacency plus the
phenomenon, and adjacency dominates — the M0 ablated control produced a raw
windowed correlation of 0.56 with no social memory at all. Every milestone
from here inherits this rule. The raw-count version produces a false negative
at every scale.

**A2 (M1 verification, adopted before M2).** The M1 §5.5 permutation
control gates on a **within-agent option permutation**: each agent's
exposure multiset is held constant and the option each exposure count
attaches to is permuted. The preregistered across-acts label shuffle is
still computed and reported, but it preserves the population's
option-frequency structure and therefore cannot fall to ~1.0 in a converged
population (M1 canonical stream: observed contingency 11.45×, label-shuffle
null 3.04×, within-agent null 1.00×). The spec's literal actor permutation
is a no-op under the §5.3 exposure metric, which never conditions on actor
identity. Same lesson as A1: a null model must break exactly the linkage
the claim rests on, and nothing else.

**A3 (M2 verification, adopted during the M2 protocol).** Four disclosed
amendments to the preregistered M2 measurement (a1–a4, full text in
`src/engine/metrics-m2.ts` and `docs/m2-protocol-run.txt`), each fixing an
instrument that was undefined or misattributing **by construction**: a
fidelity offset that measured only dead agents, a share metric with no
minimum denominator, baseline controls contaminated inside their own scored
window, and a drift gate whose passing bar was arithmetically above 1.
Standard adopted for all future milestones: an unpassable gate is a broken
instrument, not a strict one — but the replacement must test the same
null's *discriminating* prediction (here: single-pool drift concentrates,
yet cannot hold two classes simultaneously coherent on distinct tokens),
and the amendment must be made and disclosed before any finite value of
the metric has been observed.

**A4 (M2 ablation B, adopted after protocol round 1).** SPEC-M2 §5.7's
expected signature for ablation B (full observability) — "successful
coordination without symbol differentiation" — was a wrong prediction, not
a failed mechanism: with vision equal to signal radius, differentiation
*persists* (10/12 streams, z 4–15), because outcome grounding never needed
privacy; and universal far sight collapses demography, so B is not a clean
minimal pair. The corrected reading, binding for reruns: the shared-percept
confound (§4.1 item 1) is controlled **per measured event** — every §5.2 and
§5.4 hear event requires the hearer could not see any rich open node — and
ablation B is retained as a secondary, demography-confounded manipulation
whose expected signature is *weakened differentiation and inflated
§5.2 contingency of non-communicative origin*, not the absence of
differentiation.

Milestone specifications after M0 live beside this file:
[SPEC-M1.md](SPEC-M1.md), [SPEC-M2.md](SPEC-M2.md).
