# Wu Boshi Relation Before Object

This file defines the reduction move:

`solve the relation before solving the object`

## Core Principle

Most hard problems are overcomputed because people try to recover every object.

Often the target only needs:

- one relation
- one difference
- one ratio
- one alignment
- one invariant link

So do not ask:

- what are all the objects?

Ask:

- what relation actually decides the answer?

## Trigger

Use this move when the target asks for:

- fixed line / fixed point
- slope / direction
- midpoint / average
- ratio
- sign
- ordering
- dependence / independence

## Fast Move

1. Name the target relation.
2. Keep only the symbols needed for that relation.
3. Prove or compute the relation directly.
4. Ignore full object recovery unless the target forces it.

## Why It Works

Relations are often much lower-dimensional than the full objects that produce them.

## Where It Transfers

- conics
- vector geometry
- algebraic identities
- dependence questions
- system behavior / debugging traces

## Failure Mode

- the target secretly depends on hidden object details
- the relation alone cannot distinguish branches
- the compressed relation loses admissibility information
