# Primitive: Matching Instead Of Probability

## Universal Primitive Note

This primitive is not about school probability stories specifically.

It is the general move:

- dynamic narrative -> static uniform structure

whenever the random process can be flattened without losing the weighting law.

## Pattern

A probability story is secretly a uniform matching or assignment problem.

## Trigger

- small finite actors
- pairings, assignments, matchups, schedules, seatings
- the narrative sounds sequential, but the outcome is just one global matching
- total sample space is finite and symmetric

## Why It Works

When the random mechanism produces a uniform matching space, probability is just:

`favorable matchings / total matchings`

The story can be flattened into structure.

## Fast Move

1. Stop following the story chronologically.
2. Rewrite the outcome as a static matching object.
3. Count total matchings and favorable matchings structurally.

## Where It Transfers

- card matchups
- assignment probability
- scheduling and seating
- pairing and tournament-style experiments

## Failure Mode

- the sample space is not uniform after flattening
- hidden sequential dependence changes weights
- the same static matching can arise with different probabilities

## Verification Bill

- state why the flattened matching space is uniform
- if not uniform, state the weighting rule instead of raw counts

## Seed Examples

- 2024 新高考 I 卷 第14题

## Neighbor Primitives

- `count-before-derive`
- `permutation recognition`
- `aggregate-first`

## Level Transfer

- early level: stop following the story and line things up
- university level: replace sequential probability language with a combinatorial sample space
- research level: flatten the stochastic description into structural state counting or weighted matching when that preserves the law
