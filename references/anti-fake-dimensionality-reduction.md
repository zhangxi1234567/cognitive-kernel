# Wu Boshi Anti-Fake Dimensionality Reduction

This file defines what does **not** count as real dimensionality reduction.

Main principle:

- shorter is not automatically lower-dimensional
- friendlier wording is not automatically structural compression
- a standard solution with fewer words is still a standard solution if the burden did not actually move

## What Real Dimensionality Reduction Must Do

A real dimensionality reduction move should do at least one of these:

- kill a fake wrapper before the main solve begins
- replace many moving parts with one controlling structure
- switch to a representation that removes most of the work
- reduce proof burden by attacking the decisive hinge instead of the full object
- leave behind a reusable primitive instead of one local trick

If none of those happened, the answer is probably only shorter, not smaller.

## Common Fake Forms

### 1. Shortened Standard Solution

Shape:

- same route as the textbook or answer key
- fewer steps shown
- more conversational wording

Why it fails:

- the user still had to carry the same structure
- no fake complexity was removed

### 2. Cosmetic “本质上就是”

Shape:

- starts with “本质上就是……”
- then immediately continues with the same heavy route

Why it fails:

- the sentence names a structure
- but the solve path does not actually use that structure to reduce work

### 3. Formula First, Intuition After

Shape:

- gives the standard formula or setup first
- only afterward explains the intuition

Why it fails:

- the formal burden still arrived before the shell was killed

### 4. Toy Model That Does No Work

Shape:

- provides a cute small example
- but the example does not reveal the real hinge or cut the real search space

Why it fails:

- the toy model became decoration, not control

### 5. Faster Arithmetic, Same Cognitive Shape

Shape:

- same algebraic route
- slightly cleverer arithmetic

Why it fails:

- computation got shorter
- the dimension of the problem did not change

## Positive Test

Ask these questions:

1. Did the shell die early?
2. Did the number of real moving parts shrink?
3. Did the main solve route change because of that shrinkage?
4. Would the user now name the problem differently?
5. Could the same move transfer to a nearby problem?

If at least three answers are not clearly yes, do not call it dimensionality reduction.

## Comparison Test

A candidate answer is probably fake if:

- its middle skeleton matches the standard key
- the same variables are introduced in the same order
- the same heavy object is reconstructed before the target is attacked
- the “insight” line could be deleted without changing the actual route

## Hard Rule

Never label a solution as Wu Boshi-style dimensionality reduction if:

- the route is still standard-key-first
- the intuition did not actually change what was computed
- the shell was described but not destroyed
