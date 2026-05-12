# Wu Boshi Orientation Branching

This file defines the move:

- before solving, decide which orientation branch the object belongs to

## Core Principle

Some problems look like one object but actually split into different structural branches depending on orientation or sign.

Typical examples:

- horizontal vs vertical conic
- ellipse vs hyperbola after parameter sign
- increasing vs decreasing branch
- left/right or upper/lower geometric control branch

## Fast Move

1. Name the parameter or feature that controls orientation.
2. Split the problem into the smallest valid branches.
3. Solve only inside the correct branch formula or geometry picture.

## Why It Matters

This is not routine casework.
It prevents:

- using the wrong prototype
- reading the wrong eccentricity formula
- missing valid parameter signs

## Hard Rule

If orientation changes the mother object, branch first.
Do not compress two different geometric worlds into one fake formula.
