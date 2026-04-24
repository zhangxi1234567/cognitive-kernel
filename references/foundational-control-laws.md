# Wu Boshi Foundational Control Laws

This file defines the deepest universal control laws of the project.

This is the layer that should still survive if you remove:

- chapter labels
- school-stage labels
- subject boundaries
- teacher-style wording
- local tricks

Its purpose is:

- make the project truly universal
- organize mathematics, physics, chemistry, debugging, and research under one shared control layer
- stop the library from collapsing into a large but shallow trick catalog

## Core Rule

If a law cannot transfer from:

- school math
- to advanced math
- to research-style reasoning

then it is not foundational enough.

Foundational control laws are not:

- problem types
- chapter routines
- named micro-techniques

They are:

- cross-domain reasons why reduction works

## The Foundational Control Laws

### 1. Controller Selection Law

Every hard problem contains many visible variables but only a few true controllers.

Core question:

- what quantity, relation, or state actually controls the target?

What this law does:

- deletes fake moving parts
- separates load-bearing structure from decorative structure

Math surface:

- one axis controls comparison
- one parameter controls a family
- one relation controls the target

Research surface:

- one pathway, one bottleneck, one readout, or one regime controls the outcome

### 2. Fake-Degree Elimination Law

Difficulty often comes from freedoms that are not truly independent.

Core question:

- which degrees of freedom are fake, duplicated, shell-level, or quotiented out by symmetry, invariance, or aggregation?

What this law does:

- collapses dimension
- reduces case count
- turns many visible variables into one effective variable

### 3. Carrier Rewrite Law

A hard high-level object should be rewritten into a lower carrier that is easier to operate on.

Core question:

- what lower carrier can faithfully carry this problem?

Typical rewrites:

- function -> input-output relation carrier
- derivative -> local motion law
- process -> state-flow object
- parameter family -> fixed skeleton + moving shell
- thick object -> thin readout

This law is central to universality because it lets the same deep logic operate in different domains.

### 3.5 Lowest Honest Layer Law

High formal surface does not automatically imply high controlling mechanism.

Core question:

- what is the lowest honest layer at which the same controller can still be rebuilt without cheating?

What this law does:

- allows return from prestige form to controller form
- explains why advanced notation can often be routed through earlier mechanism intuition
- protects against both prestige inflation and fake oversimplification

Examples:

- derivative -> local rate-of-change controller
- second derivative -> change-of-change / acceleration controller
- matrices -> linked linear-constraint controller
- conics -> mother-shape / preserved-relation controller
- triangle extrema -> balance / symmetry / boundary controller

Hard rule:

- the lowered layer must still own the decisive hinge
- otherwise the reduction is decorative, not real

### 4. Boundary Revelation Law

Mechanisms are often clearest where slack disappears.

Core question:

- what boundary, tangent, endpoint, coincidence, or limiting regime removes the most slack?

What this law does:

- reveals hinges
- exposes fixed anchors
- separates competing mechanisms

This is why:

- tangent cases
- endpoint cases
- extreme values
- critical thresholds

are so powerful across disciplines.

### 5. Probe Law

Not every problem should be fully solved before it is understood.

Core question:

- what is the cheapest probe that stresses the live mechanism?

What this law does:

- uses special values, assignments, perturbations, toy cases, and minimal experiments to expose structure

Math surface:

- `0`, `1`, `-1`, equal variables, symmetric points

Research surface:

- one perturbation, one assay, one stress condition

Debugging surface:

- one minimal reproducer

### 6. Static Skeleton Law

Many dynamic or chronological problems are governed by a static skeleton.

Core question:

- what state, graph, invariant transition structure, or reachability object sits beneath the time story?

What this law does:

- turns process into structure
- turns history into state
- kills fake time burden

### 7. Balance Law

When imbalance creates burden or penalty, balanced structure is often where decisive behavior lives.

Core question:

- where does directional bias disappear?

What this law does:

- explains symmetry extremum
- explains centered and equal-case guesses
- explains why equilibrium and balance are not cosmetic but controlling

### 8. Anchor Exposure Law

A moving family becomes manageable once a fixed anchor is found.

Core question:

- what fixed point, fixed line, fixed value, fixed baseline, or fixed bottleneck survives the motion?

What this law does:

- turns family tracking into anchor reading
- supports fixed-point, fixed-line, and fixed-value attacks

### 9. Candidate-Space Compression Law

Hard reasoning does not always require full certainty immediately.

Core question:

- how can the live candidate world be made much smaller before full proof?

What this law does:

- makes guess-then-verify lawful
- enables elimination under ambiguity
- shifts burden from full construction to decisive discrimination

### 10. Readout Law

Once the right controller is found, the final step is often readout, not derivation.

Core question:

- after compression, what can now be directly read rather than rebuilt?

What this law does:

- explains direct count
- direct ratio readout
- direct range/controller readout
- reduced-seal solving

### 11. Minimum Honest Seal Law

After reduction, verification should be local, targeted, and honest.

Core question:

- what is the cheapest seal that can still kill a wrong route?

What this law does:

- prevents fake elegance
- keeps simplification lawful
- makes reduced routes auditable

### 12. Low-Floor Ownership Law

A route only counts as real dimensional reduction if a meaningfully weaker solver can still own the decisive hinge.

Core question:

- did the route become executable at a lower floor, or only explainable there?

What this law does:

- separates real lowering from motivational lowering
- keeps the project aligned with true `降维打击`

## Universal Workflow From These Laws

For any hard problem, the foundational order is:

1. choose the true controller
2. eliminate fake degrees of freedom
3. rewrite to a lower carrier
4. find the lowest honest layer that still preserves the controller
5. look for a revealing boundary or anchor
6. probe the mechanism cheaply
7. freeze dynamic burden into a static skeleton when possible
8. compress the candidate space
9. read out what can now be directly read
10. seal the route with the minimum honest verification
11. check whether the lowered route is truly executable

## What This Changes In The Project

The project should now be read as:

- foundational control laws
- universal mechanisms
- bottom-layer why laws
- carrier-layer rewrites
- visible methods and primitives
- benchmark and regression protocols

That is:

- control laws first
- tricks last

## Hard Rule

Any future addition should be able to answer all three:

1. Which foundational control law does this rely on?
2. What lower carrier does it rewrite the object into?
3. What minimum honest seal makes it trustworthy?

If it cannot answer these, it is still too surface-level.
