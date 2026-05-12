# Wu Boshi Minimal Verification

This file defines the cheapest lawful verification after a guessed answer, guessed structure, or guessed shortcut.

Main rule:

- a guess may start the route
- a guess may not end the route
- after a guess, pay the smallest verification cost that blocks the most likely failure mode

The target is not full proof.
The target is:

- enough checking to make the shortcut auditable
- without regrowing into textbook flow

## Core Principle

After a guess, verify the thing that would fail first.

Prefer this order:

1. `Boundary`
2. `Substitution`
3. `Structural consistency`
4. `Symmetry / relabel`
5. `Trust bill`

Stop as soon as the shortcut becomes lawfully checkable.
Escalate only if one layer does not seal the risk.

## What Counts As A Guess

Treat these as guesses:

- a candidate final answer chosen by pattern, picture, elimination, or instinct
- a guessed form such as linear, symmetric, conserved, monotone, tangent, extremal, or factorized
- a toy-model pattern lifted to the real problem
- a visual readout
- a "probably by symmetry" move
- a "this should just substitute back" move

## Cheapest Lawful Verification Ladder

### 1. Boundary Check

Use first when the guess concerns:

- max / min
- endpoint behavior
- equality case
- feasibility
- sign
- branch selection
- threshold

Cheap checks:

- plug the edge value
- test the smallest / largest allowed case
- test equality or collision case
- test zero / one / empty / full case when meaningful

Question to answer:

`Does the guess survive the places where the structure is most likely to break?`

### 2. Substitution Check

Use first when the guess is:

- a concrete numerical answer
- a candidate root
- a proposed formula
- a proposed construction
- a guessed invariant relation

Cheap checks:

- substitute into the defining equation or constraint
- substitute into the target statement instead of rebuilding the whole derivation
- test one representative instance if the claim is structural and the system has already been reduced to one control variable

Question to answer:

`Does the candidate actually satisfy the thing it claims to satisfy?`

### 3. Structural Consistency Check

Use when the guess is about form, not only value.

Check only the structure that must stay preserved:

- units / dimensions
- sign
- order
- degree
- parity
- count partition
- monotonicity direction
- conserved quantity
- branch count
- assumption load

Cheap checks:

- if the form is symmetric, does the expression stay symmetric?
- if the route used a substitution, did it keep all admissible cases?
- if the route used counting, is the partition disjoint and complete?
- if the route used comparison, is there one stable comparison axis?
- if the route used approximation, is the error direction harmless for the claim being made?

Question to answer:

`Did the shortcut keep the skeleton of the original problem, or only produce a nice-looking answer?`

### 4. Symmetry / Relabel Check

Use when the shortcut says or implies:

- "by symmetry"
- "without loss of generality"
- paired objects should behave the same
- one computed case can stand for several cases

Cheap checks:

- swap labels and see whether the claim is unchanged
- reflect or reverse the setup and see whether the target should stay the same
- check whether the supposed symmetry accidentally deletes an asymmetric boundary case

Question to answer:

`Is the symmetry real, or just a convenient story caused by the current labels?`

### 5. Trust Bill

If the answer still sounds like:

- `直接`
- `一眼`
- `不用算`
- `画图就出`

it must pay one final sentence.

That sentence must name:

- what mechanism preserves truth
- what leakage risk was ruled out

Good trust-bill shapes:

- `之所以可以直接代回去判，是因为目标只要求满足这个约束，不要求重建全过程。`
- `之所以边界一查就够，是因为中间情况被单调性夹住了，不会突然翻转。`
- `之所以按对称只算一边就行，是因为交换两边不会改变约束，唯一要防的是端点退化，而这个端点刚才已经单查过。`
- `之所以可以直接数，是因为分块是互不重叠且覆盖完全的，所以不会漏也不会重。`

## Routing By Guess Type

### A. Guessed final answer

Default cheapest route:

1. `Substitution`
2. `Boundary` if there are endpoints or branch risks
3. `Trust bill`

### B. Guessed structure

Examples:

- "this should be symmetric"
- "this should be monotone"
- "this should factor this way"
- "this should be conserved"

Default cheapest route:

1. `Structural consistency`
2. `One substitution or representative check`
3. `Symmetry` if relabeling is part of the claim
4. `Trust bill`

### C. Visual or toy-model guess

Default cheapest route:

1. `Boundary`
2. `Structural consistency`
3. `One exact substitution or count check`
4. `Trust bill`

### D. Guess from elimination / comparison

Default cheapest route:

1. `Boundary or counter-option test`
2. `Structural consistency of the comparison axis`
3. `Trust bill`

## Hard Stop Rules

Do not stop at minimal verification if:

- the check passes only on one toy case but not on the real constraints
- two guesses survive the same cheap check
- symmetry is only approximate
- substitution validates the candidate value but not uniqueness when uniqueness matters
- the shortcut used cancellation, division, approximation, or case merging with hidden domain conditions
- the domain is high-stakes or adversarial

Then escalate to:

1. `Minimal formal skeleton`
2. `Short derivation`
3. `Edge-case audit`

## Operational Test

Before stopping, ask:

`What is the cheapest check that would most likely catch me if this guess were wrong?`

If you cannot answer that in one sentence, the verification is not designed yet.

## One-Line Summary

Guess fast, but verify at the weakest seam first:
edge, plug-back, preserved structure, symmetry, then one trust-bill sentence.
