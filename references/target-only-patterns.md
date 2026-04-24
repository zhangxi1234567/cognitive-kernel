# Wu Boshi Target-Only Patterns

This file defines the universal move:

- solve only what the question asks
- do not rebuild the whole hidden object unless the target truly depends on it

## Core Principle

Many hard problems look large because the solver silently upgrades:

- target quantity
into
- full object reconstruction

Wu Boshi style forbids this upgrade unless it is necessary.

## Universal Triggers

Use target-only solving when the question only asks for:

- one value
- one sign
- one bound
- one probability
- one equality / inequality
- one fixed property
- one existence or nonexistence result
- one comparison

## Universal Fast Move

1. Write the target alone.
2. Circle the exact objects that enter that target.
3. Delete every variable, point, state, or sub-object not needed for the target.
4. Search for the shortest relation that certifies only the target.

## Typical Reductions

- full process -> endpoint condition
- full geometry object -> one relation
- full probability tree -> one static count
- full function expression -> one monotone or boundary fact
- full algebraic object -> one invariant or obstruction
- full model -> one controlling output

## Where It Transfers

- arithmetic and algebra
- geometry and conics
- calculus and analysis
- probability and combinatorics
- abstract algebra
- debugging
- planning and strategy

## Failure Mode

Target-only fails when:

- the target truly depends on hidden branches not yet controlled
- a discarded variable can change the final target
- the question is secretly about the whole object, not just the visible ask

## Verification Bill

Target-only is valid only if you can say:

- why the discarded parts cannot affect the target
- which exact relation or aggregate still controls the target completely

Use:

- `target-complete-main-carrier.md`

when the route has already found a smaller carrier and must decide whether the target can be finished there directly.

## Hard Rule

Never solve the full object first “just in case”.
Make the necessity visible or stay target-only.
