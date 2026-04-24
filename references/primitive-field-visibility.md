# Primitive Field Visibility

This file defines a weak compatibility pressure:

- how visible the lower-honest-layer primitive field currently is

Its purpose is:

- help the package avoid collapsing too early to one formal route
- make nearby simpler primitives easier to remain perceptible
- without prescribing which primitive must be chosen

## Core Claim

Some problems are not missing a route.

They are missing visibility of the primitive field around the route.

If the current route is too dominant too early,
then nearby primitives such as:

- symmetry
- special value
- boundary
- direct comparison
- small counting partition
- simple projection

may never become visible enough to compete.

The package should preserve pressure against that.

## What This Pressure Means

Primitive field visibility means only:

- lower-honest-layer primitives may still be nearby and relevant

It does not mean:

- now activate all primitives
- now try primitives in order
- now run a primitive checklist

## What The Package May Preserve

The package may preserve:

- `primitive_field_visibility`

with values like:

- `low`
- `medium`
- `high`

This is:

- weak visibility pressure

Not:

- a primitive-activation script

## Relation To Existing Docs

Use:

- `primitive-reachability-pressure.md`
- `low-floor-access-priority.md`
- `coactivation-without-choreography.md`

This file adds one specific emphasis:

- not only whether a lower primitive could work,
- but whether the surrounding primitive field is still visible enough to compete

## Final Rule

The package may preserve the visibility of simpler nearby primitives.

It must not decide which one should win.
