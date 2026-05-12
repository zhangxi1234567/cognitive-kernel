# Wu Boshi Fast Solve Search

This file defines the top-level fast-solve search engine protocol.

The goal is not to retrieve one memorized trick.
The goal is to actively search for the cheapest truthful route on a new problem.

## Core Principle

For any new problem, do not ask first:

- what chapter is this?
- what standard method matches this?

Ask first:

- is there a faster lawful route hiding here?

## Search Engine Loop

Run this sequence in order:

1. `Demystify`
2. `Downgrade`
3. `Primitive scan`
4. `Analogy reduction`
5. `Guess`
6. `Minimal verification`
7. `Second-layer attacks`
8. `Reverse design`
9. `Mistake mining`
10. `Fallback to shortest reliable solve`

If any earlier layer closes the target honestly, stop.

But preserve a map back upward if the user or domain still needs formal rigor.

## Step 1: Demystify

Rewrite the problem in one blunt sentence.

Questions:

- what is it really asking?
- what part is fake difficulty?

## Step 2: Downgrade

Search one level down from the current abstraction layer:

- research -> graduate -> undergraduate -> secondary -> primary intuition
- or, outside education labels: formal theory -> standard structure -> toy mechanism -> concrete picture

Question:

- what is the earliest honest version of this same skeleton?
- what layer would I need to climb back to after the shortcut works?

## Step 3: Primitive Scan

Check whether the problem is really:

- compare
- count
- balance
- invariant
- symmetry
- boundary
- aggregate
- target-only
- exact-cover / permutation
- projection / slice

If yes, route there first.

Then ask:

- does this primitive survive across levels, or is it only a local school-stage trick?

## Step 4: Analogy Reduction

Try one operational analogy only if it helps solve, not just explain.

Questions:

- what familiar system preserves the same decision structure?
- what next move becomes obvious there?

## Step 5: Guess

Allowed guesses:

- structure
- attack path
- result

Prefer that order.

Guess only if a cheap check is visible.

## Step 6: Minimal Verification

After a guess, verify the weakest seam first:

1. boundary
2. substitution
3. structural consistency
4. symmetry / relabel
5. trust bill

## Step 7: Second-Layer Attacks

If the primitive is right but the problem still does not collapse, run:

1. target-only proof
2. aggregate-first
3. boundary-condition attack
4. fixed-object template
5. representation switch
6. one-control-variable reduction
7. relation-reading instead of object-finding
8. symmetry relabel
9. minimal exact check

## Step 8: Reverse Design

Look backward from:

- answer shape
- target form
- fixed line / fixed point / constant flavor
- likely setter intention

Questions:

- why would the answer be this clean?
- what structure would force that?

## Step 9: Mistake Mining

Ask:

- what standard wrong route is the problem baiting?
- what would most students overcompute?
- what does that reveal about the true bottleneck?

## Step 10: Fallback

If structural exhaustion is reached, downgrade honestly:

- `秒杀`
- `快招`
- `稳招`
- `最短可靠解`

Never fake `秒杀`.

## Hard Rules

- The search ends at the first truthful low-load route, not at the fanciest route.
- Every route must name its legality mechanism.
- Every shortcut must survive one cheap check.
- If the problem has already been reduced, do not let it regrow without a named obstruction.
- Seed examples from one academic layer may inspire the search, but the discovered route must be described in a level-agnostic way whenever possible.

## Success Condition

The search engine is working if it repeatedly finds routes that:

- shrink the problem
- reduce notation load
- reduce moving parts
- preserve truth
- leave one reusable move behind
