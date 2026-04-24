# Primitive: Area To Line Readout

## Pattern

A 2D or 3D quantity only looks thick.
Its target is actually controlled by a lower-dimensional gap, height, projection, section, or boundary readout.

## Trigger Signal

- the target is area, volume, flux-like size, or another "thick" quantity
- the expression seems linear in one height, width, gap, or section variable
- pushing one feature to 0 or to a boundary case makes the structure clearer
- the hard part is the shape, but the asked quantity seems to care about one readout only
- a base-height, determinant, cross-section, or projection formula is hovering in the background

## Level-Agnostic Core

Do not worship the full region.
If the target is controlled by one lower-dimensional readout, reduce the thick object to that readout first.

## Control Mechanism

The move works because:

- the target is linear or otherwise directly controlled by one lower-dimensional quantity
- degeneration exposes the hinge without changing the target-relevant control relation
- projection or section preserves the decisive readout
- the full shape contributes only through one boundary-controlled parameter

## Preserved Structure

Typical preserved items:

- base-height or analogous line-readout relation
- target-relevant section law
- one gap, distance, or projection that still determines the area/volume family
- map-back from boundary quantity to the original target

## Earliest Honest Layer

Do not ask "what is the whole region doing?"
Ask:

- which line quantity is this area hanging on?
- which section quantity is this volume hanging on?
- if I flatten one feature to a boundary, what control relation stays alive?

## Fast Move

1. Identify the one line / section / projection quantity controlling the thick target.
2. Rewrite the target through that readout.
3. If useful, push to a boundary or degenerate case to expose the relation.
4. Solve the lower-dimensional problem.
5. Map back only what the original target asked for.

## Compression Move

Typical burden deletion:

- area problem -> line-gap / height / projection problem
- volume problem -> section / width / radius / height problem
- region relation -> boundary relation
- full shape chase -> one controlling scalar readout

## Level Transfer

- low-complexity form: area depends on one height or gap; volume depends on one section
- compact formal form: determinant, cross-section, support width, projection, integral kernel readout
- advanced formal form: measure controlled by section law, effective boundary observable, reduced geometric functional

## Cross-Domain Analogue

- physics: total effect determined by one effective cross-section or projected component
- debugging: a huge failure surface is really controlled by one interface metric
- strategy: a broad market picture is really controlled by one funnel width or one bottleneck rate

## Where It Transfers

- triangle, trapezoid, polygon, and chord-area problems
- analytic geometry area relations
- solids and section-volume problems
- optimization with geometric measures
- any setting where a higher-dimensional measure is controlled by one lower-dimensional observable

## Failure Mode

- the lower-dimensional readout does not actually determine the target
- the degenerate case destroys the mechanism instead of exposing it
- a projection preserves one visual feature but not the asked quantity
- the map-back from line/section quantity to target is silently wrong

## Verification Bill

State:

- which lower-dimensional quantity controls the target
- what remains preserved after the flattening / section / projection
- why the degenerate or boundary case is exposing the hinge rather than changing the problem
- how the original target is read back

## Seed Examples

- triangle area read through one height, gap, or projection
- trapezoid or polygon area reduced to one line readout
- chord / conic area relation reduced to center distance or line-gap control
- solid volume read through decisive cross-section behavior
- training bundle: `training-bundle-area-to-line-readout.md`

## Neighbor Primitives

- `Projection Readout`
- `Canonical Normalization`
- `Local Seam Controls Global`

## Transfer Promise

This primitive should activate whenever a thick object is only pretending to be thick:

- area -> height / gap / projection
- volume -> section / radius / support width
- region -> boundary
- complicated measure -> one effective observable
