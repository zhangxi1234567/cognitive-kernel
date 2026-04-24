# Wu Boshi Puzzle Assignment

This file defines the move:

- do not assign values randomly
- assign a sequence of key values like puzzle pieces until the hidden structure locks

## Core Principle

In many abstract-function and relation problems, one special value is not enough.

The right move is:

- zero value
- unit value
- negative value
- equal variables
- problem-given anchor

used in a deliberate order, like assembling a puzzle.

## Typical Assignment Order

1. `0`
   - identity / vanishing / baseline
2. `1`
   - unit / normalization / scaling anchor
3. `-1`
   - parity / symmetry / sign reversal
4. `equal variables`
   - self-interaction / recurrence / diagonal
5. `problem-given anchor`
   - the special point already named in the prompt

## What It Reveals

- odd/even behavior
- period hints
- recurrence patterns
- hidden constants
- normalization values
- contradiction or counterexample slots

## Hard Rule

The values should be chosen as a sequence with purpose.
If the next value does not reduce uncertainty, it is not puzzle assignment, only blind plugging.
