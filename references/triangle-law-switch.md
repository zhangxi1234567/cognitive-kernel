# Wu Boshi Triangle-Law Switch

This file defines the move:

- choose the simplest triangle law that the compressed geometry actually needs

## Core Principle

After geometry is reduced to one controlling triangle, the next question is:

- is this triangle right or non-right?

If right:

- prefer the Pythagorean route

If non-right:

- prefer the cosine-theorem route

## Fast Move

1. Compress the geometry to the controlling triangle.
2. Check whether the key angle is right.
3. Choose:
   - `Pythagorean seal`
   - or `Cosine-theorem seal`

## Why It Matters

This is not a trivial choice.
It prevents:

- brute coordinate expansion
- using cosine theorem when a right-triangle collapse already exists
- forcing Pythagorean reasoning into a non-right picture

## Hard Rule

Do not talk about trig laws before the controlling triangle is visible.
The law choice is a final seal decision, not the first move.
