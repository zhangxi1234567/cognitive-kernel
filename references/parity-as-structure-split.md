# Wu Boshi Parity As Structure Split

This file defines odd/even structure as a reduction move.

Its purpose is:

- use parity to split behavior cleanly
- exploit odd/even structure to kill half the work
- treat parity as a route-finder rather than a side property

## Core Rule

When odd/even behavior is present, ask:

- what disappears on the symmetric split?
- what survives under `x -> -x`?
- which part is odd, which part is even, and which target only depends on one part?

Then compress:

- full function/object -> odd part + even part

## Trigger Signals

- `f(-x)` appears explicitly
- symmetric domain around zero
- odd/even function conditions
- sum or product of symmetric terms
- periodicity or cancellation driven by sign reversal

## Compression Moves

- full expression -> odd part + even part
- two-sided analysis -> one-sided analysis
- full graph -> symmetric half plus rule
- hard integral/sum -> cancellation by parity

## Why It Works

- parity exposes preserved structure under sign flip
- odd parts and even parts obey different control laws
- many fake degrees of freedom disappear once the split is made

## Good Uses

- abstract function questions
- graph symmetry
- integrals, sums, and paired terms
- sequence patterns with alternating signs

## Failure Boundary

Do not overfire this move when:

- the domain is not symmetric
- the target depends on asymmetric data
- parity is present but not controlling

## Transfer

- school math: odd/even functions and symmetric sums
- university math: decomposition into invariant parts
- cross-domain: split a system into preserved and sign-changing components
