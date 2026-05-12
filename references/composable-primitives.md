# Wu Boshi Composable Primitives

This file defines the rule:

- one problem should often admit several distinct dimensionality-reduction routes
- each route may be built from a different combination of primitives

Main principle:

- methods are not isolated tricks
- methods are composable primitives

## Why Composition Matters

A real reduction engine should not behave like:

- one problem -> one labeled trick

It should behave like:

- one problem -> several candidate routes
- each route = a different combination of primitives

That is how:

- the same problem supports multiple elegant solutions
- different learners can enter from different lower floors
- the library generates innovation instead of repeating slogans

## Composition Formula

Think in this shape:

`route = shell-kill + main primitive + control primitive + verification primitive`

Examples:

- `demystify + matching instead of probability + count + symmetry`
- `canonical normalization + target-only + aggregate-first + minimal exact check`
- `guess then verify + boundary attack + witness probing`
- `draw-first + compare before compute + no-overlap audit`

## What Counts As A Different Route

Two routes are genuinely different if at least one of these changes:

- the shell-kill
- the main controlling primitive
- the verification primitive
- the representation
- the lower floor from which the route becomes executable

## Core Composition Roles

### 1. Shell-Kill Primitive

Examples:

- demystify
- reframe
- representation switch
- canonical normalization

### 2. Main Primitive

Examples:

- compare before compute
- count before derive
- target-only
- local controls global
- aggregate controls target

### 3. Control / Compression Primitive

Examples:

- symmetry
- concrete instantiation
- boundary attack
- one-control-variable reduction
- degeneration

### 4. Verification Primitive

Examples:

- minimal exact check
- trust bill
- witness probing
- no-double-counting audit
- monotonicity check

## Good Multi-Route Behavior

For one problem, good route diversity looks like:

- one route by comparison
- one route by counting
- one route by symmetry
- one route by normalization
- one route by target-only or aggregate-first

The goal is not to force many routes.
The goal is to see whether different primitive combinations produce genuinely different burdens and different lower-floor access points.

## Bad Multi-Route Behavior

Do not count these as route diversity:

- same algebra, different storytelling
- same setup, different notation
- same formula, different order of presentation

## Composition Checklist

When solving one problem, ask:

1. What shell-kill is strongest here?
2. What is the main primitive?
3. What secondary primitive can shrink it further?
4. What is the cheapest verification primitive?
5. Is there a second route with a different main primitive?
6. Does that second route genuinely change the burden?

## Hard Rule

Do not let the library collapse into one-problem-one-trick thinking.

The same problem should be allowed to spark:

- different shell-kills
- different lower floors
- different controlling primitives
- different final seals
