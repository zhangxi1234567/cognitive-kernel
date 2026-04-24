# Wu Boshi Constraint First

This file defines the reduction move:

`start from the hardest constraint, not the prettiest object`

## Core Principle

In many problems, one constraint does most of the work.

The fastest route is often:

- identify the tightest constraint
- let it squeeze the rest of the problem

## Trigger

Use this move when the problem has:

- one obvious “must”
- hidden exclusivity
- fixed total
- exact-cover condition
- one dangerous inequality
- one bottleneck resource

## Fast Move

1. List all constraints.
2. Ask which one kills the most freedom.
3. Apply that one first.
4. Let weaker constraints clean up afterward.

## Why It Works

The tightest constraint often collapses the search space fastest.

## Where It Transfers

- combinatorics
- probability
- optimization
- chemistry stoichiometry
- scheduling / assignment
- exact-cover and matching problems

## Failure Mode

- misidentifying the strongest constraint
- using a pretty but weak constraint first
- a hidden side condition matters more than the visible bottleneck
