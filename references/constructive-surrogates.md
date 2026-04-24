# Wu Boshi Constructive Surrogates

This file defines the move:

- construct a better-behaved object to carry the burden the original object carries badly

## Core Principle

Some problems are not meant to be solved inside the original object.

Instead:

- build an auxiliary function
- build a comparison object
- build a normalized surrogate

and let the surrogate do the hard work.

## Common Uses

- inequality proofs
- comparison of expressions
- derivative and monotonicity routes
- turning a hard target into a better-controlled function

## Hard Rule

Do not construct for decoration.
The surrogate must remove a real burden:

- sign analysis
- monotonicity control
- comparison control
- route compression
