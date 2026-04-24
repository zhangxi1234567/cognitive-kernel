# Wu Boshi Canonical Normalization And Degeneration

This file defines the universal move:

- reduce a complicated object to its mother object
- or collapse a higher-dimensional object to a lower-dimensional control object

Main slogan:

- ellipse -> circle
- surface -> line
- line -> point
- many-parameter object -> one canonical form

## Core Principle

Many hard problems do not need to be solved in their original shape.

Instead ask:

- what simpler canonical object is this secretly the same as?
- what lower-dimensional shadow still controls the answer?
- what happens if one controlling quantity is assigned, flattened, normalized, or degenerated?

This is not cheating.
It is lawful structure compression.

## Three Main Forms

### 1. Canonical Normalization

Turn a nonstandard object into a standard mother object.

Examples:

- ellipse -> circle by scaling
- general quadratic form -> diagonal / normal form
- ugly expression -> dimensionless or normalized form
- weighted system -> unweighted mother model

### 2. Degeneration

Push a structure to a limiting or collapsed case that still reveals the controlling relation.

Examples:

- area -> base times height, then examine height shrinking to 0
- surface or region -> boundary line
- line family -> tangent case
- volume / area relation -> cross-section or endpoint case

### 3. Lower-Dimensional Projection

Keep only the projection, slice, difference, or coordinate that actually controls the target.

Examples:

- chord geometry -> center distance and projection
- polygon / region -> one width, height, or coordinate gap
- many variables -> one axis or one control parameter

## Trigger Questions

Ask:

1. Can this object be mapped to a cleaner prototype?
2. Can this 2D / 3D thing be controlled by one line, one distance, or one section?
3. Can I force the decisive relation to show up by collapsing one quantity to 0 or to a boundary case?
4. If I assign one convenient value or frame, does the hidden structure become visible?
5. What is the mother object behind this decorated object?

## Why It Works

The legality comes from one of these:

- affine or similarity invariance
- normalization preserving the relevant relation
- limiting case preserving the decisive mechanism
- projection preserving the target-relevant quantity
- degeneration exposing the hinge without changing the truth conditions

## Fast Move

1. Identify the decorated object.
2. Name the mother object or lower-dimensional control object.
3. State what is preserved under the reduction.
4. Solve in the reduced world.
5. Map back only what the target actually needs.

## Typical Powerful Patterns

### Ellipse -> Circle

- use scaling to move to the unit circle
- solve the chord / angle / tangent structure there
- map back the target quantity with the correct distortion rule

### Area -> Line Gap

- rewrite area using coordinates, determinant, or base-height
- let cancellation expose a single coordinate difference
- solve the line-gap problem instead of the full planar geometry

### Region -> Boundary

- when the target depends only on width / height / support line / envelope, solve on the boundary first

### Multi-Object -> One Assigned Frame

- fix one origin, axis, representative, or convenient value
- let symmetry / invariance carry the rest

## Where It Transfers

- primary and secondary geometry
- conics and analytic geometry
- calculus and analysis by normalization
- abstract algebra via normal forms
- physics via dimensionless reduction
- optimization via boundary collapse
- debugging via canonical reproducer

## Role Of Concrete Instantiation / 赋值

Concrete instantiation often helps this move:

- assign a convenient frame
- assign a representative value
- assign a normalized scale

This is not random plugging.
It is choosing a lawful viewpoint that exposes the hidden prototype.

## Failure Mode

This move fails when:

- the reduction does not preserve the target-relevant quantity
- a degeneration destroys the very relation the problem asks about
- normalization changes the meaning of the quantity and the map-back is ignored
- the lower-dimensional shadow is suggestive but not actually controlling

## Verification Bill

You must state:

- what is preserved
- what is not preserved
- how the target is translated back

If lengths, angles, areas, probabilities, or norms distort under the reduction, say so explicitly.

## Hard Rule

Do not merely say “化成圆” or “化成线”.
You must say:

- what is preserved
- why the target can still be read there
- how the answer maps back
