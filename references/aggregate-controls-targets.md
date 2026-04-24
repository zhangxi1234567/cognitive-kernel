# Wu Boshi Aggregate Controls Targets

This file defines the universal move:

- many local parts are noisy
- one total, net, average, conserved amount, or combined structure actually controls the target

## Core Principle

The target often does not care about each piece separately.
It cares about:

- the total
- the average
- the net
- the combined count
- the combined area / mass / score / load
- one summary statistic

If so, solve the aggregate first.

## Trigger

Use this move when:

- many terms appear only through one combined quantity
- the final question asks for one summary-level output
- local detail is noisy but the total is stable
- the standard route computes every piece separately before recombining them

Strong signal:

- symmetry suggests where the optimum, equality case, or clean guess may live
- but the real proof burden is paid by one fixed total, conserved amount, or summary constraint

## Universal Fast Move

1. Ask what aggregate the target actually depends on.
2. Rewrite the target in terms of that aggregate.
3. Control the total directly before separating any local pieces.

## Signal Vs Controller

Do not confuse:

- `route signal`
with
- `control mechanism`

Typical pattern:

- symmetry tells you where to look
- the aggregate tells you why the target is globally trapped

Example shape:

- target: maximize \(xy\)
- condition: \(x^2+y^2=1\)

What symmetry does:

- suggests the best point should occur near the balanced place \(x=y\)

What the aggregate does:

- actually seals the target through
  \[
  x^2+y^2 \ge 2xy
  \]
  so the fixed total \(x^2+y^2=1\) globally controls \(xy\)

This distinction matters.
If you stop at symmetry, you only have a plausible route guess.
If you identify the aggregate, you have the real controller.

## Common Aggregate Families

- sum / product
- average / expectation
- total count
- total score / net gain
- whole-region area / volume
- total flow / conserved budget
- one summary statistic or one sufficient encoding

## Where It Transfers

- number and algebra problems
- geometry and measure problems
- probability and statistics
- optimization
- mechanics and chemistry bookkeeping
- debugging and systems analysis

## Failure Mode

This move fails when:

- the target actually depends on internal arrangement, not only the total
- aggregation hides the one distinction the question cares about
- the combined quantity gives only direction but not enough separation

## Verification Bill

You must state:

- why the target is really controlled by the aggregate
- what information is safely thrown away
- whether one minimal exact check is still needed afterward

If symmetry was used on the way, also state:

- whether it only suggested the candidate
- or whether it truly carries the whole proof bill

## Hard Rule

Do not compute every local term first if the target only reads the total.
That is ordinary-solution thinking.

Do not promote a route signal into the final mechanism.
Symmetry, pretty equality cases, or a balanced guess may point you to the answer.
They do not by themselves certify the answer unless they also control the target globally.
