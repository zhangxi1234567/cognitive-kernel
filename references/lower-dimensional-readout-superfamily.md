# Wu Boshi Lower-Dimensional Readout Superfamily

This file groups the primitives that all share one deep move:

- a thick object is secretly controlled by a thinner readout

The point is to stop storing these as separate local tricks.

They are different surfaces of one superfamily.

## Core Superfamily Law

When a problem looks high-dimensional, first ask:

- what is the thinnest object that still preserves the target?

This superfamily covers moves such as:

- area -> line readout
- volume -> section readout
- full figure -> one gap or center distance
- full vector system -> one projection
- full solid -> controlling cross-section

## Why This Superfamily Matters

Without this file, the library risks storing:

- `Area To Line Readout`
- `Projection Readout`
- `Container To Section`

as independent cards.

But the deeper move is one:

- do not solve the thick object directly if one thin controller already decides the target

## Member Primitives

### 1. `Area To Line Readout`

Use when:

- a 2D or 3D measure is controlled by height, gap, projection, section, or support width

### 2. `Projection Readout`

Use when:

- one axis, component, or observable already preserves the target-relevant decision structure

### 3. `Container To Section`

Use when:

- a high-dimensional symmetric configuration is controlled by one slice or section

## Shared Trigger Signals

This superfamily is likely live when:

- the full object looks thick, noisy, or expensive
- the target depends on one distance, one gap, one support line, one section, or one component
- a side view, slice, projection, or lower-dimensional observable looks decisive
- the full relation web is larger than the asked target

## Shared Control Mechanism

All members work because:

- a thinner readout preserves the target-relevant structure
- the discarded dimensions are not actually in charge
- the target is governed by one observable rather than the whole object

## Shared Preserved Structure

Typical preserved items across the superfamily:

- target-relevant distance or gap
- section law
- projection law
- center / support / tangency relation
- map-back from thin readout to the original target

## Shared Failure Modes

This superfamily fails when:

- the thinner view is helpful but not controlling
- discarded dimensions still change the target
- the slice or projection is pretty, but not decisive
- the map-back to the original target is silently wrong

## Routing Guidance

When the superfamily fires, choose the member primitive like this:

- if the target is explicitly measure-like: start with `Area To Line Readout`
- if one axis/component/shadow is already visible: start with `Projection Readout`
- if the object is genuinely high-dimensional and symmetric: start with `Container To Section`

## Training Guidance

When training this superfamily, do not ask only:

- "did the model choose the right card?"

Also ask:

- "did the model notice that the whole object was too thick for the target?"
- "did it search for the thinnest lawful controller?"
- "did it know what was preserved after thinning?"

## Hard Rule

Do not let this superfamily collapse back into chapter labels like:

- area trick
- vector trick
- solid geometry trick

It is one deeper move:

- **thin controller behind thick target**
