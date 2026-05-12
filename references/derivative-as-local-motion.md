# Wu Boshi Derivative As Local Motion

This file defines the bottom-layer view:

- derivative is not first a symbol manipulation object
- it is the local change law of a moving quantity

## Core Rule

When a derivative problem appears, ask:

- what is moving?
- what does positive/negative derivative mean in this motion story?
- where does the motion stop, speed up, slow down, or turn around?

Then compress:

- derivative shell -> local motion controller

## Bottom-Layer Logic

- `f` is position/state
- `f'` is local change rate / velocity
- `f''` is change of change / acceleration

This is not a metaphor pasted on top.
It is the operational low-floor carrier for many derivative questions.

## What This Explains

- monotonicity -> forward/backward motion
- extremum -> turnaround candidate
- convexity / concavity -> acceleration sign
- mean-value intuition -> secant/tangent local speed comparison
- parameter threshold -> when motion law changes regime

## Good Uses

- derivative sign problems
- monotonicity and extremum
- concavity / convexity
- graph behavior
- comparing functions on intervals

## Failure Boundary

Do not overfire this move when:

- the physical carrier hides an essential discrete or nonlocal condition
- the target depends on a formal identity that motion intuition alone cannot certify
- the analogy changes the decision structure

## Transfer

- elementary layer: road, speed, acceleration
- university layer: local linearization and rate law
- research-style transfer: local response law, sensitivity, regime change
