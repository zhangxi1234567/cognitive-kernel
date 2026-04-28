# Quarterly Freq Win Note

This file records a benchmarked win pattern.

It is not a solve script.

It exists to preserve one important anti-false-essence lesson.

## Benchmark Lesson

In quarterly-like `freq` bugs, many layers can look guilty:

- alias maps
- family equivalence helpers
- inference logic
- conversion layers
- broad validators

Those are often sheep skins.

The winning question was:

**who is the final narrow owner that still decides whether this exact `freq` may remain attached to this exact finished result?**

For the successful blind run, the answer was:

- `pandas/core/arrays/datetimelike.py`
- `_maybe_pin_freq`

Not because it is the deepest layer.

Not because it is the most general layer.

But because it is the last narrow pinning owner with real discretion to keep or clear `freq` on the finished result.

## Reusable Win Pattern

When a metadata dispute survives several candidate layers:

1. kill alias-family explanations first
2. kill producer/translator layers if they no longer own the final decision
3. kill broad validators if a narrower result-specific pinning owner still exists
4. prefer the narrowest function that still has final discretion over metadata survival on the actual result

## Why This Matters

This is the concrete shape of:

- legality owner over retention layer
- validator over producer
- lowest complete boundary over deeper elegant story

## Anti-Regression Signal

The package is regressing on this class if it repeatedly settles on:

- `get_period_alias`
- `to_period`
- generic quarterly inference
- broad `_validate_frequency`

when a narrower final pinning owner still exists.
