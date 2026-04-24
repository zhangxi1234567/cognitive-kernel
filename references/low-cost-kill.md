# Wu Boshi Low-Cost Kill

This file defines the reduction move:

`do not solve the whole problem if one cheap blow can kill most candidates`

## Core Principle

The fastest route is often not “find the answer.”

It is:

- kill wrong options
- kill wrong branches
- kill wrong parameter regions
- kill wrong models

until only one plausible path remains.

## Trigger

Use this move when:

- multiple choice is present
- candidate answers are few
- parameter candidates can be ranked
- a branch / case split is large
- one cheap check can eliminate many possibilities

## Fast Move

1. Identify the weakest candidates.
2. Find the cheapest lethal check.
3. Eliminate them in groups, not one by one.
4. Repeat until only one route or answer remains.

## Why It Works

Exclusion is often cheaper than construction.

## Where It Transfers

- multiple-choice math
- parameter screening
- inequality direction checks
- geometry branch elimination
- debugging root-cause search

## Failure Mode

- every candidate needs a full solve
- checks are not actually group-killing
- elimination depends on a hidden unstated assumption
