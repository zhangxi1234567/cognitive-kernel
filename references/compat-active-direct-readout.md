# Compat-Active Direct Readout

This file defines the compatibility-active form of direct readout pressure.

Its purpose is:

- make compat-only execution more likely to switch from derivation to faithful readout when the carrier already contains the answer
- do so without turning readout into a visible recipe

## Core Claim

Compat-only execution should already allow a route to feel:

- the answer may already be here

That means:

- not every reduced route should continue deriving
- some reduced routes should become readout routes

## What This Means In Compatibility Form

At the compatibility-active level, direct readout means:

- a strong carrier can warm answer extraction over further construction
- target-complete readiness can increase pressure toward readout
- the seal can become one cheap fidelity check rather than a longer derivation tail

This is not:

- a mandatory “read, not solve” command
- a visible switch step

## Allowed Compatibility Pressure

The compatibility layer may already preserve:

- `target_complete_readiness`
- `inward_continuation_pressure`
- `competition_saturation`
- `minimal_honest_seal`

These are enough to support:

- weak direct-readout readiness

without:

- a readout checklist

## What Must Stay Forbidden

Do not turn direct readout into:

- “now stop deriving”
- “now read the answer directly”
- a required answer-extraction stage

## Relation To Existing Docs

Use:

- `read-not-solve.md`
- `target-complete-main-carrier.md`
- `compat-only-execution-boundary.md`

This file is the compat-active extraction,
not the full ideal-layer doctrine.

## Final Rule

Compat-only execution should already allow the route to become a readout when the carrier is ready.

It must not expose that transition as workflow.
