# Wu Boshi Symmetry To Periodicity

This file defines the move:

- convert symmetry information into periodicity, then convert periodicity into computability

## Core Principle

In many function problems, symmetry is not the endpoint.
It is the bridge to:

- period
- repeated structure
- large-index evaluation
- compressed summation

## Common Bridges

### 1. Odd/Even + Shift

- oddness plus a shifted evenness often reveals a symmetry axis or center
- once the axis/center is found, a period may emerge

### 2. Axis + Center

- one symmetry axis and one symmetry center often force a period
- the period is typically a multiple of the gap between the two

### 3. Symmetric Pair Equation

- relations like `f(a+x) = -f(a-x)` or `f(x)=f(b-x)` often expose the center or axis directly

## Fast Move

1. identify the symmetry type
2. locate the axis or center
3. ask whether a period follows
4. use the period to compress evaluation or summation

## Typical Uses

- large-index function values
- periodic sums
- abstract function properties
- graph-structure reading

## Hard Rule

Do not stop at “it is symmetric”.
Ask what repeated structure the symmetry now forces.
