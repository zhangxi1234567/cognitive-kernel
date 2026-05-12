# Wu Boshi Baited-Route Recognition

This file defines the move:

- detect the ordinary route the problem wants most solvers to overcommit to
- then refuse it early

## Core Principle

Many elegant problems hide their easiest route behind a stronger-looking bait route.

Typical bait routes:

- full coordinate setup
- full probability tree
- full symbolic elimination
- chapter-default theorem chain
- term-by-term brute force

Wu Boshi style should ask:

- what route is the shell trying to bait me into?
- what smaller route becomes available if I refuse that bait?

## Trigger

Use this when:

- the standard route is very obvious
- the notation strongly suggests one chapter-default method
- the problem looks too dressed-up for the final answer shape
- the first route that comes to mind is long and bureaucratic

## Fast Move

1. Name the bait route explicitly.
2. Name what burden that route would force.
3. Search for the primitive that kills that burden instead.

## Common Bait Pairs

- process tree -> static matching
- full object recovery -> target-only relation
- symbolic grind -> comparison axis
- full geometry coordinates -> normalized mother object or landmark reading
- full derivative flow -> boundary / witness / monotonicity seam

## Hard Rule

Do not reward the library for noticing the bait if it still walks into it afterward.
