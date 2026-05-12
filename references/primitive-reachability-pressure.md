# Primitive Reachability Pressure

This file defines a weak compatibility pressure:

- the current problem may already be reachable by lower-honest-layer primitives

Its purpose is:

- help the package avoid settling too early in a heavier formal shell
- make simpler truthful moves easier to become visible
- without prescribing which primitive must fire

## Core Claim

Some problems can already be carried by more basic primitives than the current route suggests.

Examples of such lower-honest-layer moves may include:

- special value
- boundary case
- symmetry
- direct comparison
- small counting partition
- one-readout projection

The package should preserve pressure that such moves may be available.

It must not:

- prescribe which one to use
- prescribe an order among them
- force a descent ritual

## What This Pressure Means

Primitive reachability pressure means only:

- the current route may still be heavier than the easiest truthful primitive layer

It does not mean:

- now try special values
- now try symmetry
- now try limits

Those decisions remain model-side.

## What The Package May Preserve

The package may preserve:

- `primitive_reachability_pressure`

with values like:

- `low`
- `medium`
- `high`

This is:

- weak visibility pressure toward simpler truthful carriers

Not:

- a primitive-selection command

## Relation To Existing Docs

Use:

- `lowest-honest-layer.md`
- `low-floor-access-priority.md`
- `question-emergence-pressure.md`
- `self-selected-skill-composition.md`

This file adds one package-level implication:

- if lower-honest-layer primitives are already plausibly available, the package should not feel too satisfied with a heavier route

## Final Rule

The package may preserve the possibility that the route is already solvable by simpler truthful primitives.

It must not decide which primitive should be chosen.
