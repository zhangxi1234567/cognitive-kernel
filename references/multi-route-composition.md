# Wu Boshi Multi-Route Composition

This file defines what counts as a meaningful one-problem multi-route solve.

Main rule:

- multiple solutions should differ by controlling primitive
- not only by surface wording or equation order

## What Counts As Distinct Routes

Two routes are genuinely distinct only if at least one changes:

- the primitive family
- the representation
- the decisive hinge
- the verification bill

## Good Differences

Examples:

- compare route vs count route
- symmetry route vs direct algebra route
- target-only route vs aggregate-first route
- static matching route vs chronological process route
- boundary attack vs full interior analysis

## Fake Differences

These do **not** count as meaningful multi-route composition:

- same formula, different notation
- same derivation, different sentence order
- same object reconstruction, slightly shorter arithmetic
- one route is just the other with omitted steps

## Route Recording Template

For each route, record:

1. `Route label`
2. `Controlling primitive`
3. `Representation`
4. `What burden was killed`
5. `Verification bill`
6. `Why this route is not just a paraphrase of another`

## Fire-Spark Test

Routes “spark” only if the second route reveals something the first route hides.

Good sparks:

- Route A shows the counting structure.
- Route B shows the symmetry that explains why the count was so clean.

- Route A shows the formal invariant.
- Route B shows the low-complexity picture that makes the invariant obvious.

## Hard Rule

For evaluation runs, do not claim “one problem, many routes” unless:

- at least two routes are genuinely distinct by the criteria above
- each route is faithful to its own primitive
- the library can explain why both routes belong to the same deeper method family or why they illuminate different families
