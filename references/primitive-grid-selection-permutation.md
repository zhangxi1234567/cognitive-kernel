# Primitive: Grid Selection To Permutation

## Universal Primitive Note

This primitive is one surface of a more general move:

- exact one-to-one constraint -> bijection / permutation encoding

It should transfer whenever the real object is a matching or exact-cover structure.

## Pattern

A board or table problem is really a bijection problem.

## Trigger

- one choice per row
- one choice per column
- nonattacking rook flavor
- row-column assignment with exact-cover structure

## Why It Works

Legal configurations are in one-to-one correspondence with permutations.

## Fast Move

1. Replace the board by a mapping `row -> column`.
2. Recognize that every legal configuration is a bijection.
3. Count or analyze the permutation instead of the picture.

## Where It Transfers

- rook placement
- assignment tables
- permutation matrices
- exact-cover row/column puzzles

## Failure Mode

- extra geometry or weighting constraints break the simple bijection
- multiple picks per row/column are allowed
- forbidden structure creates a filtered, not full, permutation space

## Verification Bill

- state the bijection explicitly
- state whether extra constraints only filter the permutation set or destroy the encoding

## Seed Examples

- 2024 新高考 II 卷 第14题第一空

## Neighbor Primitives

- `matching instead of probability`
- `exact-cover as permutation`
- `count-before-derive`

## Level Transfer

- early level: one box matched to one box
- university level: bijection, permutation, assignment matrix, exact-cover encoding
- research level: structural encoding of admissible states by one-to-one correspondence
