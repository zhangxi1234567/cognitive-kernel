# Wu Boshi Set-But-Do-Not-Solve

This file defines the move:

- introduce the right variables, but stop short of full object recovery

## Core Principle

Many algebraic or analytic routes only need:

- a symbolic handle
- not the full explicit solution of every hidden object

So the route becomes:

- set it
- keep it symbolic
- extract the target relation

instead of:

- set it
- solve everything
- return later to the target

## Common Uses

- midpoint-chord problems
- conic line intersections
- target-only geometry
- parameterized algebraic systems

## Hard Rule

If you introduce variables and then immediately solve all of them, you lost the point of this move.
