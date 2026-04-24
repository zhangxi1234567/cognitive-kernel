# Settlement Confidence

This file defines a weak compatibility signal:

- how justified it is to treat the current route as sufficiently settled

Its purpose is:

- stop the package from endorsing premature certainty
- without prescribing any next move

## Core Claim

The package should not only preserve:

- why the current route may still be incomplete

It should also preserve:

- how confident the host should be that the current route is already enough

This must remain:

- descriptive
- provisional
- non-binding

## What This Signal Means

`settlement_confidence` measures only:

- how stable the current route settlement currently appears

It does not mean:

- settle now
- continue now
- compare one more route

Those decisions remain model-side.

## Suggested Values

- `low`
- `medium`
- `high`

Examples:

- `low`
  - the route is good but still may be composite
- `medium`
  - the route is leading and nearby alternatives are fading
- `high`
  - nearby candidates are no longer informative and the carrier looks stable

## Relation To Existing Pressures

This signal may be informed by:

- `bottom_layer_priority`
- `composite_shell_risk`
- `premature_settling_risk`
- `coexisting_weak_candidates`
- `question_emergence_pressure`

It should summarize them weakly.

It must not override them by script.

## Final Rule

The package may preserve how settled the current route appears.

It must not convert settlement into an externally imposed decision.
