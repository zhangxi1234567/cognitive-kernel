# Wu Boshi General Anti-Regrowth

This file contains domain-agnostic anti-regrowth rules.

These rules apply after a reduction has already been found.

## Core Principle

Once the problem has been made smaller, do not let it grow back unless a named obstruction forces it.

## General Rules

### 1. Freeze the reduced core

State the reduced object in one line:

- invariant
- bottleneck
- controlling variable
- decisive comparison

If later steps do not touch that core, they are suspect.

### 2. Permit only necessity-expanding moves

Every new symbol, case split, lemma, or definition must answer:

`What obstruction does this remove?`

If it removes no named obstruction, do not add it.

### 3. Keep representation subordinate

Diagrams, formulas, notation, and formalism are allowed only as compression of the reduced insight, not as a fresh search space.

### 4. Stay on the shortest causal chain

Prefer the path that goes directly from the reduced core to the target quantity, conclusion, or prediction.

Reject side derivations that are true but non-binding.

### 5. Check by consequence, not by ceremony

Verification should prefer:

- unit check
- sign check
- scale check
- boundary check
- sanity check
- counterexample check

Do not reopen a full textbook derivation once the reduced mechanism already determines the answer.

### 6. Localize uncertainty

When stuck, name the exact missing link.

Do not respond to one local gap by rebuilding the whole standard framework.

### 7. One abstraction level at a time

Do not mix:

- intuition
- formal derivation
- edge-case taxonomy

in the same step.

Finish the current level, then escalate only if forced.

### 8. Stop at sufficiency

When the reduced form already discriminates the answer or structure, stop.

Do not convert a solved problem into a full exposition.

## Domain Translation

### Math

Protect:

- invariant
- monotonicity
- symmetry
- extremal object
- substitution
- normalization

Do not theorem-dump unless the theorem is the actual bridge.

### Physics

Protect:

- governing principle
- regime assumption
- conservation
- scaling
- force balance

Do not farm equations once the principle already fixes the result.

### Chemistry

Protect:

- limiting species
- dominant equilibrium
- oxidation-state change
- stoichiometric bottleneck

Do not let factor-label algebra hide the chemical control story.

### General Reasoning

Protect:

- decisive premise
- hidden assumption
- threshold comparison

Do not turn one hinge point into an essay.

## Failure Signals

- textbook chapter order starts reappearing
- new notation appears faster than new information
- the answer is setting up more than deciding
- case splits multiply before contradiction or need appears
- one local confusion triggers a total restart
- the explanation becomes more general than the problem
- formal correctness rises, but decision pressure drops
- you can no longer say in one sentence why the reduction solved it

## Operational Stop-Test

Before adding anything, ask:

`Does this step sharpen the reduced core, bridge one named gap, or verify the answer?`

If not, it is regrowth.
