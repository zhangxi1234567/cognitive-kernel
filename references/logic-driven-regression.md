# Wu Boshi Logic-Driven Regression

This file defines how to test the library by deep logic law instead of by chapter label.

Main rule:

- do not ask only “can it solve a conic / derivative / probability problem?”
- also ask “can it activate the right underlying law?”

## Why This Matters

Topic-based evaluation is too shallow.

A solver may appear strong on:

- one conic topic
- one derivative topic

while still failing the deeper law:

- symmetry-to-extremum
- boundary reveals skeleton
- fixed object through revealing cases
- shell translation of new definitions

Logic-driven regression checks whether the library is really transferable.

## Regression Format

For each logic law, record:

1. `Law`
2. `Representative problem surfaces`
3. `What should be noticed early`
4. `What ordinary route should be refused`
5. `What reduced route should appear`
6. `What counts as pass / partial / fail`

## Core Logic-Law Test Families

### 1. Symmetry Pushes Extremes Toward Balance

Representative surfaces:

- triangle extremum
- symmetric placement
- equal-case optimization

Pass if:

- the route explicitly tries the balanced configuration first
- the answer is not reached by blind full algebra before symmetry is used

### 2. Boundary / Limit Reveals Skeleton

Representative surfaces:

- tangent case
- endpoint / vertex
- infinity-direction
- parameter threshold

Pass if:

- the route identifies the revealing edge before the full interior grind

### 3. Special Values Kill Degrees Of Freedom

Representative surfaces:

- abstract function
- parameter screening
- multiple choice elimination

Pass if:

- values are chosen structurally
- not only because they are easy to compute

### 4. Lower-Dimensional Shadow Controls The Object

Representative surfaces:

- area -> line gap
- surface -> line
- solid -> cross-section
- process -> static matching

Pass if:

- the route clearly replaces a larger object by a smaller controller

### 5. Mother Object Beats Surface Novelty

Representative surfaces:

- ellipse -> circle
- strange function -> known family
- transformed object -> mother behavior

Pass if:

- the route identifies the mother object before rebuilding the decorated one

### 6. Fixed Object Through Revealing Cases

Representative surfaces:

- fixed point / fixed line
- invariant direction
- family-wide constant

Pass if:

- the route uses coincidence, tangent, zero/infinite slope, or other revealing cases to expose the fixed controller

### 7. New Shell -> Old Structure

Representative surfaces:

- set / sequence / function new definitions

Pass if:

- the route reads the definition first
- tests tiny examples
- translates back to old structure before serious calculation

### 8. Scale / Dimension Sanity

Representative surfaces:

- option elimination
- geometry size checks
- probability or rate plausibility
- physical/mathematical unit checks

Pass if:

- the route kills bad candidates by structural plausibility before deep derivation

## Hard Rule

The same logic law should be tested on more than one surface topic over time.

If a law only works in one chapter, it has not yet been learned deeply enough.

For concrete sample assignment, see:

- `logic-law-sample-bank.md`
