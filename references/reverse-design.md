# Wu Boshi Reverse Design

This file defines how to search backward from target form, answer shape, and setter intention.

## Core Principle

Many problems become easier when you stop pushing forward from the givens and instead pull backward from:

- the target
- the likely answer shape
- the setter's bait

## Reverse-Design Questions

Before doing heavy work, ask:

1. What kind of answer would be unusually clean here?
2. Why would the setter want that clean answer?
3. What structure would force such an answer?
4. What wrong route is the problem inviting?

## Answer-Shape Search

Cheap answer-shape guesses:

- integer
- simple rational
- `±1`
- fixed constant
- fixed line / fixed point
- midpoint / average / sum / product
- exact-cover count like `n!`
- `3-4-5` / small triangle / small ratio

Use these guesses only as search compression, not as proof.

## Target-Form Search

If the target asks for:

- fixed line / fixed point
  -> try `target-only proof`, `fixed-object`, `relation-reading`
- range / max / min
  -> try `boundary-condition attack`
- comparison
  -> try `comparison-axis reduction`
- count
  -> try `partition`, `permutation`, `matching`
- area / chord / midpoint
  -> try `aggregate-first`, `projection`, `slice`

## Setter-Intention Search

Ask:

- what standard method is this baiting?
- if I were setting this question, what lazy route would I expect students to miss?

Common setter bait:

- story shell hiding counting
- formula shell hiding comparison
- conic shell hiding fixed quantity
- probability shell hiding matching
- coordinate shell hiding symmetry

## Cheap Reverse Checks

After a backward guess, verify by:

- plug the guessed clean result
- test edge cases
- see whether the target becomes structurally natural
- check whether the guessed answer kills most of the algebra

## Failure Mode

Reverse design fails when:

- you guess a pretty answer but have no mechanism
- multiple clean answers are equally plausible
- the guessed shape saves no work
- it becomes answer worship instead of structure search

## Success Condition

Reverse design is working if the guessed target form suggests a cheaper route than forward brute force.
