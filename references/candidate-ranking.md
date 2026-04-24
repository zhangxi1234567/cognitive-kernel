# Wu Boshi Candidate Ranking

This file defines how the skill should rank candidate values or candidate structures before verification.

## Core Rule

Do not test candidates in random order.

Rank higher when a candidate is:

- close to the likely boundary
- structurally clean
- likely to be the first value that could work
- cheap to test with a strong witness

Rank lower when a candidate is:

- only aesthetically nice
- far from the apparent boundary
- expensive to test
- hard to eliminate neighbors from

## Candidate Types

Common candidate sources:

- collision values
- degeneration values
- symmetry values
- clean integer / rational values
- values that align roots / lines / thresholds with key points

## Ranking Question

For each candidate, ask:

1. Why is this value even in the set?
2. Why is it worth testing before its neighbors?
3. If it passes, can I eliminate nearby candidates quickly?
4. If it fails, can I eliminate a whole region quickly?

If you cannot answer 2-4, the ranking is weak.

## Output Pattern

Good wording:

- `先试这个，不是因为它一定对，而是因为它最靠近边界、最容易先露馅。`
- `这个值先测最值钱，因为过了它就能顺手去砍邻居。`
