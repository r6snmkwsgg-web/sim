## OpenCivilization — Milestone 2: Symbols
**Prerequisite:** M1 passed on all five conditions, or failed with a clean diagnosis you understand. The observation channel must be working, because M2 is built on top of it.
---
## 0. Read this first
This is the milestone most likely to fail, and the one I'd bet against. Emergent communication is a live research problem, not an engineering task — the literature has systems that produce signaling, but they are small, brittle, and rarely survive population turnover.
Two consequences for how you run it:
**Budget a partial result.** A lexicon that forms and then collapses each generation is still a finding. Log the failure mode precisely rather than tuning until something moves.
**Do not rescue this with an LLM.** M2 stays at zero LLM calls, and that constraint is the entire point. If you need a language model to produce a lexicon, you have not built emergent language — you have built translation, and the result is meaningless under §2 of the spec. LLM cognition arrives at M3, on top of whatever symbol layer M2 does or doesn't produce.
---
## 1. Target phenomenon
**Two isolated populations independently develop internally-coherent token→referent mappings; those mappings differ between populations; and on contact, tokens cross the boundary.**
Three claims stacked in a required order. The ordering matters more than anything else in this document:
1. **Coherence first.** Agents within a population must agree with each other above chance.
2. **Then divergence.** Only once each population is internally coherent does a difference between them mean anything. Two populations of noise are trivially different. Divergence measured without coherence established is not a result, it is a bug that looks like one.
3. **Then borrowing.** Contact produces token transfer.
If you get 1 and not 2, you have a lexicon with no dialects. If you get 2 without 1, you have nothing.
---
## 2. The mechanism
M1's signal tokens were arbitrary noise. M2 gives them the conditions under which they can acquire meaning — and no more than that.
### 2.1 Partial observability (the enabling change)
Agents currently perceive too much. Restrict perception to the local region: an agent cannot see resource state, hazards, or agent presence outside its immediate surroundings.
This is the load-bearing addition. **Without asymmetric information there is no reason to signal and no way to tell signaling from coincidence.** If both agents can see the thing, apparent agreement is just two agents responding to a shared percept — the classic false positive in this literature, and the one that has killed more emergent-communication results than any other.
### 2.2 The signaling loop
```
A perceives world state S (privately — B cannot perceive S)
A emits token T from its own lexicon
B receives T, has no access to S
B acts on its own inference about what T refers to
World resolves; outcome depends on whether B's action suited S
Both A and B update their (T → referent) confidence on the outcome
```
Requirements on this loop:
- **Meaning is never stored globally.** There is no token→referent table in the mechanic layer. Each agent holds private associations `(token, referent_class, confidence)`. There is no correct mapping, only mappings that coordinate.
- **Referent classes come from the percept schema**, not from a semantic list. An agent can only associate a token with something its perception already distinguishes — a resource type, a hazard, a site, an agent. Do not add a concept inventory.
- **Coining is an action.** When an agent has a percept it has no token for and a listener present, it may emit an unused token. Coinage rate should be low and pressure-driven.
- **Reinforcement is outcome-based, never label-based.** Nothing in the loop tells an agent what T "really" means. Success is defined only by whether B's action worked out.
- **Interests must be partially aligned.** Full alignment makes lexicons trivial; full opposition makes deception dominate and nothing stabilizes. Shared resource pools among familiar agents, with defection possible, is the right band. Deception is allowed to emerge — do not add a `lie()` action.
### 2.3 Transmission across generations
Newborns have empty lexicons. They acquire tokens through the M1 observation channel plus their own signaling attempts.
This is where the milestone probably breaks. Each generation re-learns the lexicon from noisy examples, so transmission fidelity below some threshold means the lexicon dissolves every ~2 generations and never accumulates. Measure fidelity explicitly (§5.5) rather than discovering the collapse by eye.
### 2.4 Scale and structure
Two populations of ~80, spatially separated by impassable terrain. Isolation phase 6,000 ticks, then open a corridor and run 4,000 more. 12 RNG streams. Still T1 utility cognition, still one region per population, still the L3 debug view.
---
## 3. Forbidden vocabulary (mechanic layer)
`word`, `meaning`, `translate`, `dictionary`, `vocabulary`, `grammar`, `semantics`, `language`, `dialect`, `token_meaning`, `global_lexicon`, `shared_lexicon`, `referent_table`.
No population-level lexicon object, and no shared state that isn't the sum of individual agent lexicons. A population's "language" must be computed from individual mappings at measurement time and stored nowhere.
---
## 4. Confounds to design against
Four, in order of how likely they are to fool you:
1. **Shared percept, not communication.** If B can perceive S, agreement proves nothing. Enforce the perceptual asymmetry at the schema level and assert it in tests — not as a config value someone can flip.
2. **Behavioral coordination without symbols.** Agents may coordinate on adjacency, prior routine, or M1 practice inheritance and never use tokens. Measure token-conditional success against token-absent baseline.
3. **Any-signal-works.** If B improves merely because *some* signal fired, the tokens are an alarm bell, not a lexicon. The §5.4 permutation control is what catches this, and it is the single most important test here.
4. **Drift convergence.** Small populations converge on tokens by chance. Compute the drift null, as in M1.
---
## 5. Measurement — preregistered
### 5.1 Within-population coherence
For each referent class, the agreement rate across the population on the modal token. Report against the drift null. **This gates everything else** — if coherence doesn't beat drift, stop and report that; the divergence and borrowing numbers are meaningless.
### 5.2 Communicative success
`P(B acts appropriately | token emitted) vs P(B acts appropriately | no token)`, normalized per signaling opportunity, not per encounter. Contingency ratio, same form as M0 and M1.
### 5.3 Between-population divergence
Distance between the two populations' modal mappings, reported **only for referent classes where both populations clear the §5.1 coherence bar.** Track over the isolation phase; expect it to rise then plateau.
### 5.4 Permutation control — the decisive test
Within the main run, hold emission events constant and permute which token was sent. Communicative success must fall to the no-token baseline.
If success survives permutation, tokens are undifferentiated alarm signals and M2 has failed regardless of what §5.1 says. Run this early — before tuning anything — because it can invalidate the whole run cheaply.
### 5.5 Transmission fidelity
Per generation: proportion of the parent generation's modal mappings still modal in the child generation. Plot across the full run. A declining curve is the collapse mode from §2.3 and predicts failure before the lexicon visibly dies.
### 5.6 Borrowing (contact phase)
For referent classes where the populations diverged: after contact, does either population's modal token shift toward the other's? Report direction, magnitude, and latency. Check whether borrowing correlates with contact-agent trust — if adopted tokens come preferentially from trusted contacts, that is transmission working through the M0 social layer, which is the strongest version of this result.
### 5.7 Ablations
| Ablation | Disables | Expected if the phenomenon is real |
|---|---|---|
| **A — No reinforcement** | Outcome-based confidence update | No coherence; tokens stay random |
| **B — Full observability** | Perceptual asymmetry | Coherence fails to form or drifts freely; no pressure to signal |
| **C — No observation channel** | M1 social learning | Coherence forms within a generation, collapses at turnover |
C is the interesting one. It isolates whether the lexicon is a within-lifetime coordination artifact or something that actually accumulates — which is the difference between signaling and language.
---
## 6. Pass conditions
Graded, because binary pass/fail is the wrong instrument here.
- **Full pass** — coherence beats drift; permutation control collapses success; divergence appears between populations; borrowing occurs on contact; transmission fidelity stable across ≥3 generations.
- **Partial — signaling** — coherence and permutation pass, but fidelity declines and lexicons reset each generation. Real result. Report it. Proceed to M3 with a within-lifetime symbol layer and note the limitation in the spec.
- **Partial — coordination only** — success improves but survives permutation. Tokens are alarms. M2 failed; the alarm layer is still usable, but do not call it language anywhere in the project.
- **Fail** — no coherence above drift.
On a full or signaling-partial result, update §8.1 of the main spec — that's the open problem this milestone was aimed at, and it should record what you actually got.
---
## 7. What not to build
No syntax, no compositionality, no multi-token utterances. No LLM cognition. No writing, no records, no artifacts that persist symbols outside agent memory. No institutions, no technology graph, no rendering work.
Single tokens referring to perceivable things is already the hard part. Compositional structure is a later milestone and only becomes a sensible question if M2 gets a full pass.
