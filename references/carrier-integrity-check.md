# Carrier Integrity Check

This file defines a compatibility-layer requirement:

- after a route finds a promising carrier, the package must preserve pressure to check whether that carrier is actually the right object class and deepest useful controller

Its purpose is:

- stop elegant wrong-carrier routes from being mistaken for deep success
- expose object-class mismatch earlier
- do so without scripting the agent's inner questioning sequence

## Core Claim

A route may:

- become smaller
- look elegant
- feel structurally coherent

and still be wrong because:

- it compressed onto the wrong carrier
- it mixed incompatible object classes
- it stopped at a middle layer that looked good but was not the true controlling layer

The package must not ignore this risk.

## What Must Be Preserved

After a carrier is chosen, the package should preserve pressure around:

- object-class integrity
- preserved structure
- failure boundary
- whether a smaller shared controller still plausibly exists

It must not convert that pressure into:

- a mandatory visible checklist
- a forced recursive script

## Relation To Existing Ideal Docs

Use:

- `object-class-boundary-check.md`
- `execution-contract.md`
- `exception-first-seam-check.md`
- `solve-protocol.md`

These ideal-layer documents already contain the needed verification philosophy.

This file lifts that philosophy into the compatibility layer itself.

## Package-Level Rule

The compatibility package should not count a route as mature merely because:

- it found a smaller carrier

It should still preserve doubt around:

- whether the carrier is the correct object class
- whether the preserved structure is truly the right one
- whether a deeper shared controller is still available

## Good Compatibility Behavior

Good compatibility behavior leaves room for the model to discover:

- wrong object class
- wrong local carrier
- wrong middle layer
- missed shared controller

without telling the model exactly how to perform that discovery.

## Final Rule

The compatibility layer should preserve carrier integrity pressure.

It must not assume that a smaller carrier is automatically the right carrier.
