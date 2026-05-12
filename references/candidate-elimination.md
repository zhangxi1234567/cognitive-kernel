# Wu Boshi Candidate Elimination

This file defines how the skill should generate, rank, and eliminate candidates without bluffing.

## Core Principle

Guessing is not enough.

The useful workflow is:

1. generate a small candidate set
2. rank candidates by how likely they are to be boundary / clean / decisive
3. use the cheapest seam test to eliminate whole regions, not just one value at a time

## Candidate Generation

Generate candidates from:

- collision values
- symmetry values
- degeneration values
- clean integer / rational / simple-ratio values
- values that align moving roots / lines / thresholds with key points

## Candidate Ranking

Rank higher when the value is:

- close to the apparent boundary
- structurally clean
- likely to be the first value that could work
- cheap to test

Rank lower when the value is:

- far from the apparent boundary
- only pretty, not structurally motivated
- expensive to test

## Elimination Goal

Do not only ask:

- does `a = -2` work?

Also ask:

- if `a = -2` works, can I quickly see whether all smaller values fail?
- if `a = -2` fails, can I kill a whole neighborhood, not just this one point?

## Elimination Tools

### 1. Threshold direction

If making the parameter smaller always pushes the dangerous seam in the bad direction, eliminate all smaller values together.

### 2. Neighbor test

If the target is a minimum or maximum, compare the surviving candidate against the nearest natural neighbor first.

### 3. Structural monotonicity

If the controlling structure worsens monotonically as the parameter moves, eliminate a whole ray.

### 4. Boundary lock

If a candidate creates the just-saturated structure, larger or smaller values may be ruled out by the same boundary law.

## Output Contract

Good language:

- `不是先把每个值都算一遍，而是先看谁最像边界，再看比它更小的是不是会一起坏。`
- `这里不是逐点试值，是沿着参数方向做排除。`
- `先验最危险的邻居，不对就整片砍掉。`

## Failure Mode

Candidate elimination fails when:

- every candidate is being fully solved separately
- the ranking is based only on aesthetic preference
- no effort is made to eliminate a region or neighbor family
- the answer pretends one tested value settles the minimum / maximum without excluding nearby candidates
