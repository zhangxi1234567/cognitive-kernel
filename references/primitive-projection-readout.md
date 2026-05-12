# Primitive: Projection Readout

## Pattern

A high-dimensional or many-variable object is actually controlled by one projection, slice, gap, or axis.

## Trigger Signal

- too many variables or directions seem active at once
- the question only depends on one distance, width, height, coordinate, or component
- a dot product, slice, support line, center distance, or coordinate gap naturally appears
- the full object looks hard but one side view already feels decisive
- a lower-dimensional readout seems to carry the asked quantity

## Level-Agnostic Core

Do not solve the full object when one lower-dimensional readout already decides the target.

## Control Mechanism

The move works because the target is governed by:

- projection
- slicing
- target-relevant coordinate readout
- lower-dimensional control quantity
- one observable that preserves the decision structure

## Preserved Structure

Typical preserved items:

- target-relevant distance or gap
- order on the controlling axis
- support relation or shadow width
- one component that determines the asked value
- map-back from the readout to the target

## Earliest Honest Layer

Look from the side that actually matters.
Many directions are noise; one direction is load-bearing.

## Fast Move

1. Ask what one readout already controls the target.
2. Collapse the object onto that axis / slice / component.
3. Solve in the reduced view.
4. Ignore the rest unless the verification bill forces them back.

## Compression Move

Typical burden deletion:

- full object -> axis / slice / section
- many coordinates -> one controlling coordinate
- area / geometry relation -> line-gap or projection relation
- many interacting signals -> one decisive observable

## Level Transfer

- low-complexity form: look at width / height / side view
- compact formal form: use one coordinate, projection, or cross-section
- advanced formal form: quotient, principal mode, effective coordinate, observable readout

## Cross-Domain Analogue

- product/strategy: reduce the whole mess to one bottleneck metric
- debugging: isolate the one signal that reveals divergence earliest
- learning: compress many formulas into one comparison axis

## Where It Transfers

- vectors and dot-product problems
- conics and coordinate geometry
- multivariable optimization
- mechanics and field symmetry
- data-flow and systems diagnosis

## Failure Mode

- the chosen projection does not fully control the target
- hidden orthogonal components still affect the answer
- the slice is suggestive but not decisive
- the lower-dimensional view loses the relation you actually need

## Verification Bill

Say why the discarded dimensions cannot change the asked target.

## Seed Examples

- dot-product range by projection
- container -> cross-section reductions
- geometry targets controlled by center distance or coordinate gap
- training bundle: `training-bundle-projection-readout.md`

## Neighbor Primitives

- `Canonical Normalization`
- `Target-Only Control`
- `Local Seam Controls Global`

## Transfer Promise

This primitive should activate across different surfaces:

- vectors -> scalar projection or dot-product readout
- geometry region -> width / height / center-distance readout
- 3D solid -> controlling cross-section
- multivariable system -> one effective coordinate
- operational system -> one bottleneck metric or one revealing signal
