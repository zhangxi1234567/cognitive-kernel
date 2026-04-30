# Multi-Agent Blind Elimination Protocol

This file does not belong to runtime.

It belongs to benchmark pressure.

Its purpose is not to teach the model how to think.

Its purpose is to test whether the runtime layer can survive adversarial selection pressure and still converge on the truer controller faster than weaker runs.

Use it when you want to compare:

- no-skill vs skill
- older skill vs newer skill
- one multi-agent answer-shaping scheme vs another

Do not turn it into a mandatory solve workflow.

It is an evaluation harness.

## Core Goal

The goal is not plurality for its own sake.

The goal is to force several candidate runs to compete under hard pressure until one line:

- reaches the true owner
- closes the asked interface
- survives minimum witness checks
- beats nearby impostors

If a run sounds smart but cannot close, it should lose.

If a run reaches a pretty explanation but misses the final owner, it should lose.

If a run widens without witness, it should lose.

## Tournament Shape

For one benchmark problem:

1. Launch multiple independent agents in parallel.
2. Give each agent the same thin-bias package inputs.
3. Keep the task blind:
   - no official answer
   - no rubric
   - no hidden fix commit
   - no web lookup unless the benchmark itself requires public source reading
4. Impose a hard timeout.
5. Eliminate any run that:
   - times out
   - fails to produce a complete answer
   - misses the true owner
   - closes less than a competing run
   - widens without witness
6. Keep only the strongest surviving line.
7. Reuse that winning answer-shaping scheme on older weak-score benchmarks.

## Default Pressure Rules

Unless a benchmark demands something else, use:

- parallel launch
- hard timeout per agent
- blind read of the problem only
- no code edits
- no answer leakage

Suggested default timeout:

- 180 seconds for reasoning-only blind diagnosis
- longer only when the task itself demands heavier local reading

## What Every Candidate Must Close

Every candidate should be forced to answer all of these, implicitly or explicitly:

1. What is the visible phenomenon?
2. What is the final owner?
3. What is the nearest live rival?
4. What concrete seam separates owner from rival?
5. What sibling completion is truly required?
6. What widening would be fake?
7. What is the minimum complete patch or answer surface?
8. What is the cheapest verification witness?

If a candidate cannot answer these, it is not yet stable enough to win.

## Domain-Specific Pressure Extensions

### Coding / Debugging

Require the candidate to distinguish:

- phenomenon layer vs final authorization layer
- transport wrapper vs decision boundary
- producer vs validator
- local patch point vs shared invariant boundary

Strong coding candidates should explicitly state:

- final owner
- nearest rival
- sibling completion
- minimum patch surface
- minimum witness test

### Research / Mechanism Extraction

Require the candidate to distinguish:

- mechanism story vs true limiting factor
- local binding claim vs in vivo net effect
- one-cell benefit vs whole-network outcome
- direct target effect vs off-target or system spillover

Strong research candidates should explicitly pressure:

- local concentration vs affinity
- direct mechanism vs indirect mechanism
- parallel pathway comparison
- production or delivery feasibility
- toxicity window
- network spillover

Whenever the prompt or evidence permits, do not leave these at generic category names.

Prefer concrete closure such as:

- which rival family is nearest
- which compartment or population carries the spillover
- which occupancy, concentration, or threshold boundary is really decisive
- which toxicity or selectivity split is most likely to become dose-limiting

For therapeutic or whole-system research benchmarks, do not treat coverage of these as optional flavor.

If the benchmark asks for therapeutic significance, limitations, or net in vivo effect, a candidate is not closed unless it explicitly reaches all live faces that remain evidenced:

1. intrinsic local mechanism
2. nearest rival or indirect mechanism
3. competition / concentration / occupancy limit
4. production or delivery feasibility
5. toxicity or selectivity window
6. network spillover across neighboring populations or compartments

If one of these remains live and unclosed, the run may still sound smart but should not be promoted as a winner.

Likewise, if all six faces are mentioned but only at generic category level, confidence should stay lower.

For promotion on hard research benchmarks, prefer candidates that turn category-level talk into:

- a named rival family
- a measurable limiting boundary
- a concrete falsification seam

### Math / Formal Reasoning

Require the candidate to distinguish:

- elegant route vs smallest truthful carrier
- local pattern vs mother structure
- symbolic thickness vs comparison axis
- apparent complexity vs one final positivity / monotonicity / symmetry closure

Strong math candidates should explicitly pressure:

- symmetry / balance
- boundary / degeneration
- compare without calculating
- direct readout on the smallest carrier

## Elimination Logic

A candidate should be eliminated immediately if:

- it times out
- it never reaches a complete answer
- it mistakes the visible crack for the true owner
- it widens to siblings or helpers without witness
- it climbs to a cleaner but less evidenced story
- it names a deep cause but cannot cash back into the asked interface
- on research benchmarks, it finds a local true mechanism but leaves a stronger limiting ceiling unresolved even though the prompt explicitly asks for therapeutic significance, limitations, or whole-system outcome

Tie-break preference:

1. truer owner
2. cleaner closure
3. fewer speculative lifts
4. less fake widening
5. smaller honest verification surface
6. faster convergence

Speed matters only after truth and closure.

## Reuse Rule

Once a candidate wins one hard benchmark, do not trust it yet.

Immediately reuse the same answer-shaping scheme on earlier weak-score problems.

A scheme is only promoted if it improves or at least preserves quality across:

- one research benchmark
- one coding/debug benchmark
- one earlier weak-score benchmark

If it spikes on one task and regresses on the older weak-score set, it is not yet a true improvement.

## Promotion Rule

Promote a tournament-derived scheme only if it consistently causes agents to:

- find the owner faster
- reject nearby impostors earlier
- keep patch surfaces smaller
- improve old weak-score benchmarks

Do not promote a scheme just because one run looked brilliant.

Single-run brilliance is not enough.

Cross-benchmark survival is the standard.
