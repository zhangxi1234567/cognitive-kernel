# Wu Boshi Local Controls Global

This file defines the reduction move:

`use one local seam to control the whole problem`

## Core Principle

A global condition often fails first at one local weak point.

So instead of controlling the whole object, search for:

- one dangerous point
- one boundary seam
- one branch switch
- one bottleneck location
- one local witness

If that local piece already decides the global fate, use it.

## Trigger

Use this move when the problem says or implies:

- for all
- always
- monotone
- nonnegative / nonpositive
- stable for every case
- minimum / maximum parameter
- existence threshold

## Fast Move

1. Ask where the condition is most fragile.
2. Probe that local seam first.
3. If it breaks there, the global claim dies.
4. If it survives there, check whether nearby values / branches can be eliminated together.

## Why It Works

Many “global” questions are governed by the first place the structure can break.

## Where It Transfers

- parameter inequalities
- monotonicity conditions
- branch-sensitive algebra
- physical stability thresholds
- chemistry equilibrium / limiting conditions

## Failure Mode

- the local seam is not actually the controlling seam
- multiple unrelated seams compete
- the problem requires full global structure, not just the first failure point
