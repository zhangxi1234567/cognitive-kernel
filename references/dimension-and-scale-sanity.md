# Wu Boshi Dimension And Scale Sanity

This file defines the move:

- test whether a route or answer is dimensionally, scalewise, and structurally reasonable before deeper commitment

## Core Principle

Many wrong routes fail before formal proof because they already violate:

- dimension
- scale
- growth order
- geometric plausibility
- physical plausibility

This move is not a last-resort patch.
It is an early control tool.

## The Three Checks

### 1. Dimension Check

Ask:

- are we adding like with like?
- does this expression have the right unit or structural type?
- is a length being compared to an area, or a probability to a count, or a slope to a distance without translation?

### 2. Scale Check

Ask:

- is the answer too big or too small for the structure?
- does the order of magnitude fit the picture?
- would this answer force an impossible geometry or impossible count?

### 3. Plausibility Check

Ask:

- does the answer respect symmetry, bounds, and special cases?
- if I move to an edge case, does this still look possible?

## Common Uses

- option elimination
- geometry length / area sanity
- probability bounds
- derivative and growth-rate comparisons
- physical interpretation checks
- algebraic shape screening

## Why It Works

Reasonableness is often the first low-cost witness against a bad route.

It helps the solver:

- abandon impossible branches early
- choose smaller routes
- avoid fake confidence

For the deeper why behind this family, see:

- `reasonableness-and-dimension-logic.md`
- `dimensional-compatibility.md`
- `scale-first-elimination.md`

## Hard Rule

Do not use sanity as a substitute for proof.
Use it to kill bad routes early or to pressure route choice.
