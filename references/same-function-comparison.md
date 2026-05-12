# Wu Boshi Same-Function Comparison

This file defines the move:

- convert two or more quantities into values of the same function, then compare by monotonicity

## Core Principle

A comparison problem often becomes smaller when different expressions are rewritten as:

- the same function evaluated at different inputs

Then the work shifts from:

- messy expression-to-expression comparison

to:

- one function's monotonicity and input order

## Fast Move

1. Separate variables and expressions until they fit one shared function template.
2. Define that common function.
3. Prove its monotonicity or sign behavior.
4. Read the comparison back from the input order.

## Common Uses

- logarithm comparisons
- exponential comparisons
- expression-order problems
- inequality transforms

## Hard Rule

If the shared function is not really the same object after rewriting, this route is fake.
