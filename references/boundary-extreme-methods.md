# Wu Boshi Boundary And Extreme Methods

This file defines the mechanism family:

- use vertex limits, endpoint limits, infinite-distance limits, and extreme positions to control the whole problem

## Core Principle

Some range and geometry problems are controlled most cleanly by:

- the nearest extreme
- the farthest extreme
- the vertex case
- the asymptotic / infinite case

The idea is not random extremizing.
It is:

- identify the edge where the structure becomes simplest
- let that edge control the range or answer shape

## Mechanism View

This family should not be stored as:

- "range questions like endpoints"
- "conic questions like vertices"

It should be stored as:

- the edge case preserves the decisive control relation better than the interior does
- a boundary or extreme configuration reveals the governing seam, onset, or locked ratio
- once the edge mechanism is visible, the interior often becomes bookkeeping

## Trigger Signals

- the target is about range, threshold, onset, locking, or feasibility
- the full interior is messy but the edge becomes structurally clean
- one endpoint, vertex, tangent case, or infinite limit seems to expose the same relation in a smaller world
- the problem feels global, but the first dangerous edge already looks load-bearing

## Preserved-Structure Warning

Boundary / extreme thinking is only lawful when the edge case preserves the target-relevant control relation.

You must ask:

- what is still preserved at the edge?
- what gets simpler there?
- what would be lost if I pushed too far?

## Common Uses

- eccentricity ranges
- conic geometry ranges
- parameter bounds
- option elimination
- angle or distance maxima/minima
- seam-first parameter checks
- degenerating shape questions into boundary readouts

## Related Primitives

- `Local Seam Controls Global`
- `Area To Line Readout`
- `Projection Readout`

## Hard Rule

Use boundary / extreme methods only when the edge case preserves the decisive control relation.
