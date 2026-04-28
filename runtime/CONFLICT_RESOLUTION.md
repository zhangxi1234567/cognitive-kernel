# Conflict Resolution

This file exists for moments when several candidate controllers still look alive.

It is not a route selector.

It is a tie-break surface.

## Priority Rules

When two candidates both look plausible, prefer:

1. the one with the stronger discriminating witness
2. the one that closes the exact asked interface more directly
3. the one that requires fewer speculative lifts
4. the one that leaves less of the same witnessed law open nearby
5. the one closer to the witnessed boundary

Do not prefer a candidate merely because it is:

- older in the run
- more elegant
- more general
- more upstream
- more familiar

## Rival Rule

Before settling, name the nearest live rival silently and ask:

- what concrete seam separates them?

If no separating seam is available, confidence should not rise too quickly.

## Metadata Rule

When candidates split across:

- producer
- translator
- inference layer
- retention layer
- legality-test owner

prefer the layer that still had real discretion over whether the disputed metadata remained lawful on the result.

If both a broad legality owner and a narrower final pinning owner remain alive, prefer the narrower final pinning owner.

## Completion Rule

A candidate that explains more but closes less should lose to a candidate that explains enough and closes fully.
