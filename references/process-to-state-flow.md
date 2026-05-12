# Wu Boshi Process To State Flow

This file defines how to compress a time-ordered process into a state-flow object.

Its purpose is:

- stop solving chronological stories one event at a time
- turn dynamic procedures into a static state graph or flow map
- let the structure of transitions carry the route

## Core Rule

When a problem is told as a process, ask:

- what are the real states?
- what transitions are allowed?
- what repeats?
- what can be counted, read, or eliminated on the state graph directly?

Then compress:

- chronological story -> state-flow structure

## Trigger Signals

- tournament / game process
- repeated operations
- sequential probability story
- turn-by-turn update
- process described in words but controlled by a small transition set

## Compression Moves

- event sequence -> state graph
- timeline -> transition table
- repeated local rule -> stable flow pattern
- dynamic story -> static counting or reachability object

## Why It Works

- many process stories contain fake time burden
- once the transitions are externalized, the problem becomes structure instead of narration

## Good Uses

- competition / tournament problems
- repeated operation puzzles
- probabilistic processes
- iterative update questions

## Failure Boundary

Do not overfire this move when:

- order really matters in a non-compressible way
- the state space is not small enough to control
- local transitions do not preserve the target-relevant structure

## Transfer

- school math: game and process problems
- university math: Markov-like transition views and dynamical toy models
- cross-domain: workflow debugging, state-machine failure tracing
