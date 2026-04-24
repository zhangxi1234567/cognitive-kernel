# Wu Boshi Space-Diagonal Readouts

This file defines the move:

- in symmetric solid or completed-box problems, read the target through the space diagonal before doing anything heavier

## Core Principle

Many 3D problems collapse once the object is recognized as:

- a box
- a completed rectangular solid
- a diagonal-controlled body

Then:

- radius
- center
- longest distance

are all read from the space diagonal.

## Common Uses

- circumscribed sphere of box-like completions
- completed cuboid models
- distance and radius readout in symmetric solids

## Hard Rule

Do not use a space-diagonal readout unless the geometry really has been reduced to a box-like or diagonal-controlled body.
