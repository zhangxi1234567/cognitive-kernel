# Wu Boshi Diagram Instant Kill

This file defines diagram-based instant-kill methods as a first-class attack layer.

This is not “draw a picture because pictures are nice.”
This is:

- draw the smallest legal picture
- expose the hidden controlling relation
- let the picture kill most of the algebra

## Core Principle

Many hard problems are not hard because they need formulas.
They are hard because the right picture has not been drawn yet.

The diagram is successful only if it reduces the solve path.

If it only makes the explanation prettier, it is decoration, not `图解秒杀`.

## When To Trigger Diagram Instant Kill

Use this layer when at least one is true:

- the problem is really about relative position, not exact coordinates
- a shape, section, slope, area, distance, or symmetry relation is hiding in text
- the target is a comparison, count, fixed line, fixed point, or sign
- a 3D object has one controlling 2D slice
- a function question is really about graph behavior
- a probability / counting story can be turned into a grid, matching, or partition picture

## Minimal Drawing Rule

Do not draw everything.

Draw only:

- the controlling object
- the comparison axis
- the anchor points
- the partition boundaries
- the moving quantity in its simplest visible form

If a drawn object does not help decide the answer, remove it.

## Diagram Kill Sequence

1. `Find the control object`
   - line
   - axis
   - section
   - anchor point
   - region partition
   - monotone graph

2. `Redraw for structure, not labels`
   - remove clutter
   - exaggerate the invariant relation if it helps
   - place the picture in the easiest frame

3. `Read the decisive relation`
   - compare lengths
   - compare areas
   - count regions
   - see symmetry
   - see tangency / boundary
   - read slope / projection / alignment

4. `Pay one trust bill`
   - why the picture preserves the decision structure
   - why it does not leak through wrong scale, omitted case, or fake visual impression

5. `Only then map back`

## Common Diagram Instant-Kill Patterns

### 1. Comparison Axis Picture

Use when:

- the real task is ranking, not computing

Draw:

- one axis
- all candidates projected onto it

Kill move:

- read order directly from one shared axis

### 2. Cross-Section Kill

Use when:

- 3D is controlled by one 2D slice

Draw:

- the symmetry section through all critical centers / contacts

Kill move:

- solve the 2D picture, inherit back

### 3. Area Partition Kill

Use when:

- the answer is encoded in region decomposition

Draw:

- the minimal partition that is complete and non-overlapping

Kill move:

- count or compare area pieces

### 4. Fixed-Line / Fixed-Point Kill

Use when:

- the target only asks for constancy, alignment, or passing through a fixed object

Draw:

- the fixed object
- the moving object only through its relation to the fixed one

Kill move:

- prove coincidence on the fixed line / point, not full reconstruction

### 5. Monotone Graph Kill

Use when:

- symbols hide a simple trend

Draw:

- rough graph with just enough anchor points and behavior

Kill move:

- use direction / crossing / monotonicity instead of symbolic grind

### 6. Matching Grid Kill

Use when:

- a story problem is really matching or exact-cover

Draw:

- grid / bipartite matching frame

Kill move:

- count legal placements instead of narrating the process

## Legality Rules

Every diagram kill must answer:

1. What exact structure is preserved by the drawing?
2. What is not to scale and does not matter?
3. Why is this picture enough to decide the target?

If those three cannot be answered, the method is not yet legal.

## Failure Modes

- pretty but irrelevant picture
- relying on “looks bigger” when scale is not justified
- drawing too much and losing the controlling relation
- hiding a case split inside an oversimplified picture
- treating a suggestive sketch as proof

## Downgrade Rule

If the picture gives:

- a clear answer and one trust line -> `秒杀`
- the right direction but still needs one small check -> `快招`
- only a useful orientation -> `稳招`

If the picture cannot carry the decisive mechanism, abandon `图解秒杀` and reroute.

## One-Line Summary

The right diagram does not illustrate the solution.
It *is* the compressed solution.
