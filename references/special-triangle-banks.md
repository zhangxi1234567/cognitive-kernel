# Wu Boshi Special Triangle Banks

This file defines the move:

- when a geometry problem compresses to a remembered special triangle, read the rest from the bank instead of rebuilding it

## Core Principle

Some geometric problems become easy only after the controlling triangle is recognized as one of a short family:

- `1:1:sqrt(2)`
- `1:sqrt(3):2`
- `3:4:5`
- golden-ratio style triangles
- other stable remembered ratio families

## Good Use

Use this move when:

- the geometry has already been compressed
- one triangle or ratio is visibly controlling the target
- reading the ratio is cheaper than deriving it from scratch

## Hard Rule

Do not force a banked triangle.
The bank is for readout after compression, not for replacing compression.
