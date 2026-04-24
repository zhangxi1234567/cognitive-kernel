# Wu Boshi New-Definition Subsystem

This file is the consolidated subsystem for new-definition problems.

Its purpose is:

- make “new definition” problems feel like a stable route family
- turn panic into a predictable reading-translation workflow

For the deeper why behind this family, see:

- `new-definition-logic.md`

## Core Principle

A new-definition problem is usually not difficult because its mathematics is deep.
It is difficult because:

- the wrapper is new
- the grammar is unfamiliar
- the solver starts computing before understanding the object

So the route is:

1. read the definition
2. translate the definition
3. test the definition on tiny examples
4. reconnect it to old mathematics
5. only then solve

## Internal Modules

This subsystem already draws on:

- `Definition Reading`
- `Puzzle Assignment`
- `Read-Not-Solve`
- `Underconstrained Completion`

## The Five-Step New-Definition Route

### 1. Read The Grammar

Ask:

- what is the object?
- what is the operation?
- what are the constraints?

### 2. Translate To Old Math

Ask:

- what old mathematical structure is hiding underneath this new wording?

### 3. Test Tiny Cases

Ask:

- what does the definition do on the smallest lawful inputs?

### 4. Find The Control Structure

Ask:

- is this really a count, compare, symmetry, or matching problem in disguise?

### 5. Solve Only After Translation

Now compute only after the new shell has already died.

## Hard Rule

If the definition has not yet been translated into structure, further calculation is fake progress.
