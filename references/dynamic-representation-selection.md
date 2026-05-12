# Wu Boshi Dynamic Representation Selection

This file defines how the skill should choose a representation dynamically rather than by habit.

The goal is:

- do not ask first "what do people usually set?"
- ask first "what representation makes the controlling structure cheapest to read?"

## Core Rule

Representation choice must be downstream of:

- essence
- target type
- control mechanism
- current rigor needs

It must not be downstream of:

- textbook habit
- chapter stereotype
- the first algebraic notation that looks available

## Representation Candidates

A problem may be represented as:

- words
- picture
- table
- graph
- balance sheet
- partition
- state graph
- flow
- quotient / symmetry class
- projection / slice
- reduced readout variable
- toy model
- formal skeleton
- experiment / observation design

None of these is globally privileged.

## Selection Questions

Before committing, ask:

1. what is the target?
2. what object actually controls the target?
3. which representation makes that controller easiest to see?
4. which representation kills the most fake moving parts?
5. which representation gives the cheapest honest verification?

## Common Dynamic Switches

- full object -> target relation
- process -> static structure
- many variables -> one readout
- 3D object -> 2D section
- 2D quantity -> 1D controller
- symbolic story -> balance sheet
- many mechanisms -> dominant regime
- full system -> reduced subsystem
- hypothesis list -> separating experiment

## Domain-Neutral Examples

### Math

- ugly expression -> one monotone axis
- area problem -> height / gap / projection
- probability process -> matching space

### Physics

- vector field -> symmetry axis
- many coupled terms -> dominant scaling regime
- time evolution -> conserved ledger

### Research

- full mechanistic narrative -> one decisive observable
- many candidate causes -> one falsifying experiment
- high-dimensional data -> one latent control factor

### Debugging

- many symptoms -> one first-broken transition
- full trace -> smallest failing path
- full system state -> one invariant that stopped holding

## Anti-Habit Check

A representation choice is suspect if:

- it was chosen before the essence was stated
- it matches textbook habit but not the smaller controller
- it increases the number of live moving parts
- another available representation would separate answers faster

## Hard Rule

Do not ask:

- "what is the normal setup for this kind of problem?"

before asking:

- "what is the cheapest truthful representation for this exact control structure?"
