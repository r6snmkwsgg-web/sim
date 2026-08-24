# OpenCivilization — Milestone 1: Generations

**Prerequisite:** M0 passed, including the permutation control. Do not start until the mechanic layer greps clean and the M0 result is committed with its ledger hash.

---

## 0. Amend the M0 spec first

One-line change, before any new code:

> Test 4 is measured on **opportunity-normalized rates** (events per adjacent tick), not raw counts. Raw pairwise counts measure adjacency plus the phenomenon, and adjacency dominates.

Every milestone from here inherits this. The raw-count version produces a false negative at every scale.

---

## 1. What M1 is for

M0 showed that agents change behavior toward *specific others* based on remembered history. M1 asks a harder question:

**Can a behavior outlive the agent who originated it?**

Target phenomenon: **a fitness-neutral behavioral regularity that originates with one agent, spreads through observation, and persists in the population for three full generations after that agent's death.**

If M0 was about memory, M1 is about transmission. It is the smallest possible test of whether this architecture can accumulate anything at all — and if it can't, technology, institutions, and belief are all off the table, because each one is transmission with extra steps.

---

## 2. The critical design constraint: fitness-neutral degrees of freedom

This is the part most implementations get wrong, so it comes before the mechanics.

A behavior that spreads because it *works better* is optimization, not transmission. Every agent independently discovering that food is good is not culture. To detect transmission you need behaviors where **an equally good alternative existed and was not taken.**

So M1 must add arbitrary choices to the action space — decisions with no expected-value difference:

- **Gather-site preference.** Three sites yield the same resource at the same rate. Which one an agent favors is free.
- **Storage placement.** Cached resources can be left at any of several equivalent locations relative to a home site. No decay difference.
- **Gift timing.** Giving may occur at any phase of the seasonal cycle with identical effect.
- **Signal token choice.** The `signal` action can emit any of ~8 arbitrary tokens. Tokens carry no built-in meaning and no mechanical effect.
- **Approach path.** Two routes to any site, equal cost.

Each is a coin flip with no right answer. If a population converges on one option and *keeps* converging after the originator dies, that convergence has no explanation except transmission. That is the whole experiment.

**Do not give any of these options a hidden advantage.** Verify numerically that expected yield is identical across choices before running anything. If one site is 2% better, you have built a fitness gradient and your result is optimization wearing a costume.

---

## 3. Mechanics to add

Minimal. Three systems, nothing else.

### 3.1 Death

- Age-based mortality with a hazard curve, plus starvation.
- Target lifespan ~400 ticks so an 8,000-tick run covers ~20 generations.
- On death: agent state is archived, not deleted. The ledger keeps it queryable. Social memory entries referencing the dead agent persist and decay normally — living agents should be able to hold beliefs about the dead.

### 3.2 Reproduction and inheritance

- Requires resource surplus above a threshold and a co-located partner. Keep the pairing rule as dumb as possible; mate choice is not this milestone.
- Child trait vector = midparent value + Gaussian mutation. Heritability tunable, default ~0.6.
- Child inherits **traits only**. Not memory, not skills, not beliefs, not site preferences. A newborn is a blank behavioral slate with a genetic temperament.
- Children start co-located with a parent and have a dependency period during which they cannot gather.

That last constraint is the load-bearing one. If children inherit behavior directly, you have built genetic transmission and there is nothing to measure.

### 3.3 The observation channel

The only new cognitive mechanism, and it must stay this small:

> When agent A perceives agent B performing an action, A records `(action_type, chosen_option, actor_id, tick)` as a low-salience episodic entry. During A's own action scoring, the distribution of observed options for that action type applies a bounded bias to A's preference.

Notes on getting this right:

- **This is weighting, not copying.** There is no `imitate()`, no `teach()`, no `copy_behavior()`. A never executes B's decision; A's own scoring is nudged by what A has seen.
- Bias magnitude scales with observation count, weighted by A's social memory of the observed actor (trust, familiarity) and A's own conformity trait. High-conformity agents are more swayed; independent agents less.
- The bias must be **bounded well below determinism.** An agent that has only ever seen option 2 should still choose option 1 sometimes. If bias saturates, you get lock-in on tick 300 and nothing interesting after.
- Observation requires adjacency and line of sight, same as any other percept.

### 3.4 Scale

60 agents, growing to a cap of ~200. Still **T1 utility cognition. Still zero LLM calls.** One region. 8,000 ticks, target under 5 minutes wall clock.

---

## 4. Forbidden vocabulary (mechanic layer)

Grep must come back clean on: `tradition`, `culture`, `custom`, `ritual`, `norm`, `practice`, `teach`, `imitate`, `copy_behavior`, `meme`, `conform_to_group`, `inherit_behavior`, `lineage_preference`.

As in M0, metrics and test files may name what they measure. The mechanic layer may not.

Also forbidden: any group-level entity. No tribe object, no population-preference field, no shared state that isn't the sum of individual agent states. Group-level regularity must be *detected*, never stored.

---

## 5. Measurement — preregistered

Write these before you look at any output.

### 5.1 Definitions

- **Generation** = lineage depth from the founder cohort, not wall-clock time.
- **Practice** = for a given fitness-neutral choice, an option held by ≥60% of living agents for ≥500 consecutive ticks.
- **Origin** = the first agent to exhibit the option at above-baseline rate, before any population-level skew exists.
- **Survival** = the practice still meets threshold at a tick when all living agents are ≥3 generations downstream of the origin, and the origin is dead.

### 5.2 Primary test

For each fitness-neutral choice dimension: does at least one option reach practice threshold and survive three post-origin generations?

Report per dimension, across 12 RNG streams. Also report the null expectation — drift alone will occasionally produce convergence, so compute the rate at which an unbiased random walk over the same option count and population size hits threshold. **Your result must beat drift, not zero.**

### 5.3 Transmission metric (opportunity-normalized, per §0)

`P(agent adopts option X | exposed to X) vs P(adopt X | not exposed)`, where exposure is counted **per adjacent tick with the actor visible**, not per encounter. Report as a contingency ratio, same form as M0.

### 5.4 Ablations — all three required

| Ablation | Disables | Expected if transmission is real |
|---|---|---|
| **A — No observation** | The §3.3 channel | Practices fail to form, or form and die with their originator |
| **B — No trait inheritance** | Children get random traits | Practices still form and persist |
| **C — Spatial scramble** | Children relocated to random sites at independence | Practices weaken but persist above ablation A |

A separates transmission from everything. B rules out genetic similarity between parent and child masquerading as culture. C rules out children independently re-deriving the parent's choice because they live in the same place.

C is the subtle one and it is the confound that will bite you. If a child gathers at site 2 because site 2 is nearest to where it was born, that is geography, not inheritance of a practice.

### 5.5 Permutation control

Same shape as M0's: within the main run, hold exposure constant and permute *which* actor was observed. Transmission contingency should fall to ~1.0. Choice-of-metric cannot manufacture this separation.

---

## 6. What not to build

No language, no symbol negotiation beyond the arbitrary tokens in §2 — tokens are a substrate for M2, not a communication system yet. No institutions, no agreements, no technology graph, no LLM cognition, no rendering beyond the existing L3 debug view, no planet generation, no multi-region.

If M1 tempts you toward any of these, that temptation is the milestone working — it means transmission is producing structure — and it still waits for M2.

---

## 7. Pass condition

M1 passes when, across 12 streams:

1. At least one fitness-neutral practice forms and survives three post-origin generations in the majority of streams;
2. At a rate clearly above the drift null;
3. Ablation A collapses it;
4. Ablation B does not;
5. The permutation control falls to ~1.0.

Anything less is a partial result. Log it honestly and say which of the five failed — a failed M1 with a clean diagnosis is worth more than a passed M1 you don't trust, and the M0 debt-term catch is the proof of that.

---

## 8. If it fails

Most likely causes, in order:

1. **Observation bias too weak** — swamped by utility scoring. Practices never reach threshold.
2. **Observation bias too strong** — instant lock-in on tick ~200, no diversity, nothing to transmit.
3. **Lifespan too long relative to run** — not enough generations to test survival.
4. **Options aren't actually fitness-neutral** — check the yields again, numerically.
5. **Children too spatially clustered** — ablation C won't separate; scatter starting positions more.

Tune (1) and (2) before concluding anything about the architecture. There is a band where transmission works, and finding it is expected work, not failure.
