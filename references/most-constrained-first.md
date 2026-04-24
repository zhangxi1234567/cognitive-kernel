# Wu Boshi Most-Constrained-First

This file defines the move:

- handle the elements, positions, or conditions with the strongest restrictions first

## Core Principle

Some problems become easy once the tightest restriction is placed first.

Typical forms:

- special people before ordinary people
- restricted slots before free slots
- boundary values before interior values
- known anchors before generic variables

## Why It Works

The most constrained part kills the most freedom.
So placing it first shrinks the search space fastest.

## Common Uses

- combinatorics and arrangement
- probability with restricted actors
- geometry with one fixed point or line
- function problems with one forced anchor value

## Hard Rule

Do not start with the prettiest object.
Start with the object that has the least freedom.
