# Wu Boshi New-Definition Logic

This file explains the deeper logic behind new-definition problems.

It answers:

- why should we read before we calculate?
- why are tiny examples so powerful here?
- why does a new shell usually need translation back to old mathematics?

## Core Principle

A new-definition problem is often difficult for only one reason:

- the solver is looking at a new shell and acting as if the old object still has the old name

So the real first job is not calculation.
It is renaming the object correctly.

## Why Reading Comes First

In a new-definition problem, the first failure is usually semantic, not algebraic.

If you misread:

- the object
- the operation
- the constraint
- the scope of quantifiers

then every later step will be built on the wrong object.

So:

- reading is not warm-up
- reading is object-identification

## Why Tiny Examples Work

Tiny examples do three things:

1. they test whether you understood the definition
2. they expose the hidden control structure
3. they reveal what old mathematics the new shell is secretly using

That is why they are not childish.
They are definition checkers.

## Why Translation Back To Old Math Matters

Most good new-definition problems are not asking you to invent a new universe.

They are asking:

- can you strip the wrapper and reconnect it to known structure?

Common hidden old structures:

- count
- compare
- symmetry
- recursion
- matching
- arithmetic progression or periodicity
- graph / geometry picture

## The Three-Layer Route

1. `Read the shell`
2. `Test the shell`
3. `Translate the shell`

Only then:

4. solve the old structure now revealed underneath it

## Hard Rule

If you are still solving inside the untranslated new shell, the reduction has not started yet.
