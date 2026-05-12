# Wu Boshi Symmetrize The Target

This file defines the move:

- when the target expression is asymmetric, transform it into a symmetric form that the existing machinery can actually control

## Core Principle

Often the obstacle is not the problem itself, but the form of the target.

If the current machinery controls:

- `x1 + x2`
- `x1 x2`

but the target contains:

- `x1 y2 + x2 y1`
- or another non-symmetric expression

then first symmetrize the target.

## Fast Move

1. Identify what symmetric quantities the setup naturally gives.
2. Rewrite the target in terms of those quantities.
3. Only then apply Vieta / midpoint / aggregate machinery.

## Common Uses

- conic chord / slope expressions
- Vieta-based reductions
- paired-root or paired-point problems

## Hard Rule

Do not push standard machinery against a non-symmetric target if one algebraic rewrite can make the target machine-readable.
