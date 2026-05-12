# Compat-Active Target-Complete Carrier

This file defines the compatibility-active form of target-complete carrier pressure.

Its purpose is:

- make compat-only execution less likely to stop on a carrier that is small but not finishable
- support deeper single-route inward compression without adding a visible carrier checklist

## Core Claim

Compat-only execution should already allow a route to feel:

- not yet finished on the current carrier

when the carrier is:

- smaller than baseline
- still real
- but not yet target-complete

## What This Means In Compatibility Form

At the compatibility-active level, target-complete carrier pressure means:

- a route is not rewarded only for becoming smaller
- a route is also pressured by whether the target and seal can stay on that carrier
- inward continuation becomes more likely when the carrier is still too intermediate

This is not:

- a forced carrier questionnaire
- a mandatory “go one layer deeper” instruction

## Allowed Compatibility Pressure

The compatibility layer may already preserve:

- `remaining_fake_burden`
- `middle_layer_nonfinality`
- `inward_continuation_pressure`
- `lowest_honest_layer_attraction`

These are enough to support:

- weak target-complete carrier preference

without:

- visible carrier auditing steps

## What Must Stay Forbidden

Do not turn target-complete pressure into:

- “ask if the target is finishable now”
- a fixed carrier comparison ladder
- a required rebuild-vs-readout checklist

## Relation To Existing Docs

Use:

- `target-complete-main-carrier.md`
- `stay-on-the-smallest-carrier.md`
- `single-route-elite-execution.md`
- `compat-only-execution-boundary.md`

This file is the compat-active extraction,
not the full ideal-layer doctrine.

## Final Rule

Compat-only execution should already resist settling on a carrier that is small but not yet finishable.

It must not do so by visible script.
