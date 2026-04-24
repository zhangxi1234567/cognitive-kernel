# Wu Boshi Fixed-Object Subsystem

This file is the consolidated subsystem for:

- fixed points
- fixed lines
- fixed quantities
- fixed directions

The goal is to make these problems feel like one family rather than a bag of tricks.

For the deeper why behind this family, see:

- `revealing-cases-and-fixed-objects.md`

## Core Principle

A fixed-object problem is easier if you stop following the whole moving family and instead ask:

- what survives every allowed movement?
- what can be exposed by the simplest lawful extreme or special case?

## The Core Route

1. `Guess the fixed object`
   - often from the simplest lawful extreme or symmetric case
2. `Collect the strongest revealing cases`
   - coincidence
   - tangent case
   - zero slope / infinite slope
   - vertex / endpoint
   - infinity-direction
3. `Re-express the target around the guessed fixed object`
4. `Add the smallest general seal`

## Internal Modules

This subsystem already draws on:

- `Fixed-Point And Fixed-Value`
- `Infinity-Point And Coincidence`
- `Answer-First Then Backfill`
- `Option Backsolve`
- `Boundary And Extreme Methods`

## Common Surfaces

### 1. Fixed Point / Fixed Line

- a varying family secretly passes through one invariant point or line

### 2. Fixed Quantity

- a moving object still preserves one length, sum, product, dot product, or slope relation

### 3. Fixed Direction / Slope Relation

- the direction changes in appearance, but one directional relation survives

## Why It Works

The fixed object is global.
Special cases reveal it because they strip away movable clutter.

That is:

- the revealing-case layer
- not the whole proof

The proof still needs the target to be rewritten around the fixed object afterward.

## Hard Rule

Do not treat a fixed-object problem as a full-family tracking problem unless the fixed object still refuses to appear after the best revealing cases have been tried.
