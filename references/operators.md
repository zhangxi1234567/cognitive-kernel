# Wu Boshi Operators

This file defines the operator layer of the project.

The project should not be organized as:

- many flat tricks
- many flat skills
- many flat prompts

It should increasingly be organized as:

1. controller worlds
2. operators
3. primitives
4. local examples / evidence

Operators are the middle layer.

They answer:

- what kind of move should be applied to the current controller world?

They are more concrete than controller worlds,
but deeper and more reusable than local primitives.

Hard reminder:

- this layered organization is a map, not a forced visible solve script

Use:

- `anti-linearization-doctrine.md`

to preserve that distinction.

## 1. Why Operators Matter

If the system jumps directly from:

- problem surface

to:

- one named primitive

then it often becomes brittle.

It may:

- overfit to familiar examples
- miss other valid routes
- treat skills as isolated menu items

The operator layer helps solve this by allowing:

- free composition
- route comparison
- deeper transfer across domains

Short version:

- controller worlds say what kind of control universe the problem is in
- operators say what kind of move to try
- primitives say how that move cashes out locally

Use:

- `essence-to-operator-bridges.md`

when the missing question is not "what is an operator?" but:

- after catching the essence, which operator neighborhood should light up?

## 2. Operator Layer Definition

An operator is a reusable cognitive move that acts on structure.

It is not:

- a chapter routine
- a one-problem trick
- a fixed visible workflow step

It is:

- a structure-changing move
- a burden-reducing move
- a controller-exposing move

## 3. Core Operators

### 3.1 Push To Boundary

Purpose:

- expose the hinge where slack disappears

Use when:

- endpoint, tangent, zero, infinity, threshold, coincidence, or first-failure behavior is likely informative

Typical primitive expressions:

- boundary as route finder
- special-value probing
- tangency as boundary revelation

### 3.2 Degenerate

Purpose:

- collapse a thicker object into a thinner controller-bearing object

Use when:

- surface -> line
- line -> point
- full object -> seam
- dynamic family -> limiting case

Typical primitive expressions:

- area -> line readout
- canonical normalization
- section / slice readout

### 3.3 Project

Purpose:

- read a high-dimensional object through a lower-dimensional carrier

Use when:

- one axis, slice, shadow, or statistic already controls the target

Typical primitive expressions:

- projection readout
- dot-product by projection
- container -> cross-section

### 3.4 Quotient By Symmetry

Purpose:

- remove duplicated work by moving into a balanced or canonical frame

Use when:

- relabeling, mirror symmetry, equalization, periodicity, or centered framing can kill fake degrees of freedom

Typical primitive expressions:

- symmetry as variable killer
- symmetry to periodicity
- centered-difference constructions

### 3.5 Collapse To Aggregate

Purpose:

- replace local clutter with a conserved, total, net, average, or integrated controller

Use when:

- the target is paid for by a whole-system budget rather than local details

Typical primitive expressions:

- aggregate controls target
- read-not-solve
- total-change reasoning

### 3.6 Collapse To Relation

Purpose:

- solve the decisive relation before reconstructing the whole object

Use when:

- the target depends on ordering, dependence, coupling, sign, or one discriminating relation only

Typical primitive expressions:

- relation before object
- target-only reduction
- fixed relation attacks

### 3.7 Collapse To Latent Controller

Purpose:

- replace many visible variables by one hidden scalar, axis, or coupled backbone

Use when:

- many quantities move together under one hidden degree of freedom

Typical primitive expressions:

- common-value parameter compression
- one-control-variable reduction
- archetype compression

### 3.8 Probe With Witness

Purpose:

- use a strategically chosen example, perturbation, or assignment to expose the live mechanism

Use when:

- full solving is premature and a cheap witness can separate the route space

Typical primitive expressions:

- special-value probing
- puzzle assignment
- witness probing

### 3.9 Build Surrogate

Purpose:

- construct a better-behaved object than the one originally given

Use when:

- the given object carries burden badly
- a nearby constructed object preserves the controller more cleanly

Typical primitive expressions:

- constructive surrogates
- mean-value models
- completion methods

### 3.10 Normalize

Purpose:

- rewrite a decorated object into a mother object or canonical form

Use when:

- the current form hides the familiar controller

Typical primitive expressions:

- canonical normalization
- function archetype matching
- mother-pattern routing

### 3.11 Freeze Into Static Skeleton

Purpose:

- replace a time/process story with a state, graph, invariant, or static relation

Use when:

- fake time burden is hiding a simpler structure

Typical primitive expressions:

- process-to-state flow
- exact-cover modeling
- matching instead of probability

### 3.12 Read Out Directly

Purpose:

- stop deriving once the controller already exposes the target

Use when:

- the answer is encoded in a count, ratio, order, sign, or one stable readout

Typical primitive expressions:

- definition as direct readout
- eccentricity direct readouts
- special-ratio readouts

## 4. Operators Compose

Operators are not meant to fire alone only.

They should often combine.

Examples:

- boundary + project
- symmetry + aggregate
- normalize + target-only
- latent-controller + witness probe
- surrogate + direct readout

This is one reason the operator layer matters:

- it enables structured free composition instead of flat skill switching

## 5. World -> Operator -> Primitive

The preferred routing shape is:

1. identify controller world
2. propose several operators
3. select or compose primitives under those operators
4. verify legality
5. store memory in world/operator/primitive form

This should be read as structural abstraction, not as a mandatory linear narration order.

Example:

- world: `symmetry`
- operator: `quotient by symmetry`
- primitive: `symmetry as variable killer`

Example:

- world: `constraint coupling`
- operator: `collapse to latent controller`
- primitive: `common-value parameter compression`

Example:

- world: `boundary revelation`
- operator: `push to boundary`
- primitive: `boundary as route finder`

## 6. Freedom With Structure

This layer is what makes free combination possible without chaos.

Without operators, "free skill combination" may become:

- random skill hopping
- nearest-neighbor imitation
- flat toolbox behavior

With operators, free combination becomes:

- structured search over meaningful moves

That is the form of freedom this project wants.

## 7. Hard Rule

When adding a new primitive, ask:

1. what controller world is it usually serving?
2. what operator is it an expression of?
3. does that operator already exist here?

If the operator is missing, add or clarify the operator layer first.
Do not let the primitive layer carry the whole ontology by itself.
