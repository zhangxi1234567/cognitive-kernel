# Wu Boshi Answer-Shape Pressure

This file defines the move:

- let the shape of a clean answer pressure the route selection before full solving

## Core Principle

Some problems advertise their own clean structure through the answer shape:

- an integer
- a small radical
- a fixed constant
- a simple ratio
- a short multiple-choice separation

Wu Boshi style should ask:

- what kind of structure would force an answer this clean?
- what route would preserve that cleanliness instead of burying it?

## Trigger

Use this move when:

- the public or expected answer is unusually clean
- the standard route is much uglier than the answer
- one branch of work is clearly answer-shape preserving while others are not

## Fast Move

1. Name the answer shape.
2. Ask what primitive naturally produces that shape.
3. Search for the smallest route consistent with that forcing structure.

## Common Uses

- choose between counting and formula expansion
- choose between symmetry and case explosion
- choose between target-only and full reconstruction
- guide guess-then-verify with a non-random answer-shape prior

## Hard Rule

Do not hallucinate from answer shape alone.
Use answer-shape pressure to guide route search, then pay the smallest honest verification bill.
