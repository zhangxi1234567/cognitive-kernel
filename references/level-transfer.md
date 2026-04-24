# Wu Boshi Level Transfer

This file defines how one primitive should transfer across levels.

Main rule:

- do not build separate skills for primary, secondary, undergraduate, graduate, and research layers if the underlying structure is the same
- build one primitive, then learn its different surfaces

## What Counts As Real Transfer

A method really transfers when all are true:

- the same decisive structure appears at multiple levels
- the representation changes, but the control mechanism stays
- the legality check can be restated at each level
- the move becomes more formal upward, not fundamentally different

If the move only works in one narrow school-style format, it is a local tactic, not a core primitive.

## Transfer Template

For each primitive, ask:

1. `Primary intuition`
   What would this look like with the smallest concrete picture or count?
2. `Secondary structure`
   What school-style pattern or comparison does it become?
3. `University formalism`
   What definition, theorem, or algebraic skeleton carries the same move?
4. `Research toy model`
   What reduced mechanism or local model plays the same role in advanced work?
5. `Cross-domain analogue`
   Where does the same control structure show up outside math?

## Example Transfer Families

### Compare Instead Of Compute

Primary intuition:

- line up two piles and see which grows faster

Secondary structure:

- compare size, slope, angle, or area without full exact value

University formalism:

- monotonicity, convexity, norm comparison, asymptotic dominance

Research toy model:

- compare leading-order terms or dominant mechanisms before solving the full model

Cross-domain analogue:

- compare bottlenecks before optimizing the whole system

### Concrete Instantiation / 赋值

Primary intuition:

- replace letters with easy numbers or objects so the structure becomes visible

Secondary structure:

- test special values, special positions, small cases, or easy examples

University formalism:

- choose canonical representatives, basis vectors, extremal points, sample functions, or simple models

Research toy model:

- construct a witness instance, limiting regime, sanity-check example, or counterexample candidate

Cross-domain analogue:

- run the smallest meaningful scenario before building the full theory

### Symmetry / 对称

Primary intuition:

- left and right behave the same, so one side already tells the story

Secondary structure:

- mirror symmetry, center symmetry, relabel symmetry, balanced configuration

University formalism:

- invariance under transformation, relabeling, or conserved form

Research toy model:

- symmetry reduction, canonical representative, invariant manifold, conserved quantity

Cross-domain analogue:

- collapse equivalent cases instead of analyzing the same structure many times

### Guess Then Verify / 先猜后证

Primary intuition:

- guess the pattern, then test it on the easiest dangerous case

Secondary structure:

- guess the structure / route / answer, then pay the smallest trust bill

University formalism:

- make a conjectural reduction, then justify the hinge with a short argument

Research toy model:

- propose a mechanism, scaling law, or dominant regime, then attack the weakest seam first

Cross-domain analogue:

- make a working hypothesis, then try to kill it cheaply before investing in full proof or build-out

### Count Instead Of Derive

Primary intuition:

- count pieces directly

Secondary structure:

- count cases, regions, paths, transitions

University formalism:

- partition arguments, state counting, combinatorial classes

Research toy model:

- count degrees of freedom, states, modes, or admissible objects before building a closed-form derivation

Cross-domain analogue:

- count failure modes, requests, retries, or state transitions before theorizing

### One Local Seam Controls Global

Primary intuition:

- if it breaks, it will break first at the weakest point

Secondary structure:

- test boundary, symmetry point, smallest dangerous example, or branch switch

University formalism:

- local obstruction, extremal witness, saturation point, controlling constraint

Research toy model:

- probe the instability onset, dominant perturbation, or first violated condition

Cross-domain analogue:

- find the first failing interface, threshold, or brittle dependency

### Slice / Projection Reduction

Primary intuition:

- look at the side view or one important cross-section

Secondary structure:

- turn 3D into 2D, many variables into one axis

University formalism:

- projection, quotient, reduction to a subspace, effective one-variable control

Research toy model:

- analyze the reduced manifold, principal mode, or effective theory first

Cross-domain analogue:

- compress a messy system to the one dashboard metric or one critical path that controls the rest

### Canonical Normalization / Degeneration

Primary intuition:

- turn the hard shape into the easy shape, or let the big thing collapse to the line or point that controls it

Secondary structure:

- ellipse to circle, area to height, figure to boundary, quantity to one convenient assigned frame

University formalism:

- affine normalization, normal form, scaling reduction, dimensionless rewrite, quotient or reduced representation

Research toy model:

- canonical model, reduced manifold, prototype system, asymptotic or degenerate limit

Cross-domain analogue:

- replace a complicated system by the canonical test case or one control coordinate before full analysis

## Output Rule

When useful, answers may end with a level-transfer note such as:

- `小学版看成分堆，本科版看成单调性，本质是同一个比较轴。`
- `中学版是数格子，大学版是分割与覆盖，本质是同一个 exact-cover 结构。`
- `研究层写成局部稳定性，直觉层就是先看最先失稳的那条缝。`

## Hard Rule

Do not use level transfer as empty rhetoric.

You must preserve:

- the same structure
- the same control mechanism
- the same truth conditions

If those are not preserved, you changed the problem instead of transferring it.
