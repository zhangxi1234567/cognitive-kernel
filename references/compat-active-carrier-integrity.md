# Compat-Active Carrier Integrity

This file defines the compatibility-active form of carrier-integrity and target-complete pressure.

Its purpose is:

- make compat-only execution less likely to settle on an elegant but wrong or unfinished carrier
- strengthen the route's internal demand for a carrier that is both honest and finishable

## Core Claim

Compat-only execution should already allow the route to feel:

- this carrier may be locally good
- but not yet the right object class
- or not yet able to finish the target cleanly

That pressure should remain:

- silent
- revisable
- non-procedural

## What This Means In Compatibility Form

At the compatibility-active level, carrier integrity means:

- a carrier is not trusted only because it is smaller
- a carrier is not trusted only because it produced one good insight
- a carrier is pressured by whether it preserves the right structure and can finish the target without heavy regrowth

## Allowed Compatibility Pressure

The compatibility layer may already preserve:

- `composite_shell_risk`
- `remaining_fake_burden`
- `target_complete_readiness`
- `carrier_integrity_pressure`

These are enough to support:

- weak live carrier auditing

without:

- a visible carrier checklist

## What Must Stay Forbidden

Do not turn carrier integrity into:

- “check object class now”
- “check target-complete now”
- a required carrier audit sequence

## Relation To Existing Docs

Use:

- `carrier-integrity-check.md`
- `target-complete-main-carrier.md`
- `stay-on-the-smallest-carrier.md`
- `compat-only-execution-boundary.md`

This file is the compat-active extraction,
not the full ideal-layer doctrine.

## Final Rule

Compat-only execution should already resist elegant wrong-carrier settlement.

It must not do so by visible procedure.
