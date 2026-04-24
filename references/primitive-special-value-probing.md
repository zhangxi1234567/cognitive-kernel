# Primitive: Special-Value Probing

## Pattern

A problem is not solved by random plugging.
It is unlocked by deliberately chosen values, cases, positions, or representatives that expose the controlling seam.

## Trigger Signal

- direct symbolic solving branches too widely
- one or two landmark values could collapse terms, signs, or structure
- the target is about symmetry, threshold, hidden constants, periodicity, or route selection
- the problem feels underconstrained until a structurally dangerous value is tested
- zero, one, negative one, equal variables, midpoint, boundary value, or a prompt-given anchor all look potentially revealing

## Level-Agnostic Core

Do not ask "what easy number can I try?"
Ask "what value is most likely to expose the control mechanism?"

## Control Mechanism

The move works because:

- special values can collapse algebra or casework
- landmark values expose symmetry, imbalance, hidden constants, or monotone direction
- a well-chosen witness value pressure-tests the route more cheaply than full derivation

## Preserved Structure

Typical preserved items:

- the governing relation under the chosen assignment
- target-relevant sign, equality, or regime information
- admissibility of the chosen representative
- route-relevant behavior that survives after the probe

## Earliest Honest Layer

Before solving, ask:

- which value would make the structure talk?
- which value is dangerous enough to expose the seam?
- if I try `0`, `1`, `-1`, equal variables, midpoint, or the given anchor, what uncertainty disappears?

## Fast Move

1. Choose the structurally most informative value or short sequence of values.
2. Read what the probe reveals: symmetry, sign, constant, threshold, or hidden parameter.
3. Use that revelation to choose or compress the route.
4. Add only the smallest check needed to confirm the probe-driven route.

## Compression Move

Typical burden deletion:

- wide symbolic search -> landmark-value witness
- unknown constants -> anchor-value readout
- unclear route choice -> seam-testing probe
- many branches -> one revealing representative case

## Level Transfer

- low-complexity form: try `0`, `1`, equal values, midpoint, or obvious boundary values
- compact formal form: test anchors, symmetry values, diagonal substitutions, or canonical representatives
- advanced formal form: choose witness regimes, special states, normalization anchors, or structurally dangerous probes

## Cross-Domain Analogue

- debugging: smallest failing input, null input, baseline config, or one special request reveals the bug seam
- strategy: probe one extreme segment or anchor scenario before modeling the whole market
- science: use a calibration point, vacuum state, equilibrium state, or limiting case to expose the law

## Where It Transfers

- functional equations
- parameter and inequality problems
- geometry through convenient coordinates or anchor positions
- abstract algebra via representatives
- debugging and diagnosis through smallest failing cases

## Failure Mode

- the chosen value is easy but not informative
- the probe breaks admissibility or silently changes the problem
- one good-looking value is treated as a full proof when it only suggests the route
- the probe reveals a local pattern that does not generalize

## Verification Bill

State:

- why this value is structurally informative
- what uncertainty it eliminates
- what still remains to be checked after the probe

## Seed Examples

- function problems where `0`, `1`, `-1`, or equal variables reveal constants or symmetry
- trigonometric or parameter questions where a boundary/special angle exposes the route
- geometry problems where a midpoint, symmetric point, or degenerate placement reveals the hinge
- debugging via smallest failing input

## Neighbor Primitives

- `Boundary As Route Finder`
- `Definition As Direct Readout`
- `Local Seam Controls Global`

## Transfer Promise

This primitive should activate across different surfaces:

- abstract algebra and function relations
- parameter thresholds and sign questions
- geometry with anchor placements
- debugging with witness inputs
- any problem where one deliberate probe can expose the mechanism faster than full solving
