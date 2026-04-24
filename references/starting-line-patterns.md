# Wu Boshi Starting-Line Patterns

This file defines the move:

- if a function starts from the same position, same speed, or same baseline, use the earliest local behavior to control the global route

## Core Principle

When a problem tells you, or lets you derive:

- `f(0)=0`
- `f'(0)=0`
- the same starting point or baseline

it may be a starting-line problem.

Then the route becomes:

- compare who accelerates upward first
- compare higher derivatives or local curvature
- let the start determine the whole allowed behavior

## Math-Physics Reading

This is the running-model bridge:

- same position
- same initial speed
- compare acceleration or higher-order change

So many derivative proofs can be re-seen as:

- “they start together, who pulls away first?”

## Common Uses

- proving nonnegativity on one side of the axis
- parameter ranges for monotonicity / convexity
- local-to-global derivative arguments

## Hard Rule

Do not use starting-line language unless the baseline and the next local control really exist and are decisive.
