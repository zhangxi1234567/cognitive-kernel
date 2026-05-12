# Wu Boshi Answer Guess Then Substitute Seal

This file defines a specific fast route:

- guess the structural answer first
- then seal it by substitution instead of deriving it from scratch

Its purpose is:

- reduce heavy derivation when the answer shape can be guessed cleanly
- turn “find first” into “verify first” when the candidate is structurally visible

## Core Rule

When the answer or fixed object can be guessed from special cases, symmetry, or geometry, ask:

- can I guess the object first?
- can I verify it directly instead of deriving it from zero?

Then compress:

- full derivation -> answer guess + substitution seal

## Trigger Signals

- fixed point / fixed line problems
- answer shape is simple and stable
- several special cases point to the same candidate
- deriving the general form is much heavier than checking one candidate

## Compression Moves

- find special cases
- infer candidate answer object
- substitute the candidate into the general relation
- verify directly

## Why It Works

- sometimes the hard part is not checking the candidate
- it is inventing it
- once the candidate is visible, substitution is the cheapest honest seal

## Good Uses

- fixed-point / fixed-line geometry
- parameter family answers
- multiple-choice and answer-shape pressure settings

## Failure Boundary

Do not overfire this move when:

- the guess is driven only by aesthetics
- the candidate is not structurally supported
- substitution does not actually certify the full claim

## Transfer

- school math: guess result from special cases, then plug back
- university math: conjectural structure with minimal formal seal
- research-style transfer: generate candidate mechanism, then run the cheapest decisive test
