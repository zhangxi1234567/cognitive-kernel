# Primitive: Compare Without Calculating

## Pattern

The problem pretends to ask for values, but the real task is ordering.

## Trigger Signal

- ugly exponents / roots / logs
- answer choices differ by order, not by exact value
- direct calculation is possible but wasteful
- a monotone axis or shared structure is visible
- one threshold such as `0`, `1`, or one landmark value seems decisive

## Level-Agnostic Core

If the target is order, do not pay for full value unless order truly depends on it.

## Control Mechanism

The move works because:

- the compared objects sit on the same monotone axis
- one threshold, sign, or regime split already separates them
- a shared representation lets order survive without full evaluation

## Preserved Structure

Typical preserved items:

- monotone order
- sign or threshold side
- same-axis comparability
- inherited ranking after recoding to the shared axis

## Earliest Honest Layer

This is not a "compute each one" problem.
This is a "put them on the same ruler" problem.

## Fast Move

1. Identify the comparison axis.
2. Recode each object onto that same axis.
3. Use monotonicity / sign / threshold / size around `1` or `0` to rank them.

## Compression Move

Typical burden deletion:

- value finding -> ranking
- ugly expressions -> one monotone axis
- full simplification -> sign / threshold check
- multiple computations -> one shared comparison frame

## Level Transfer

- early level: compare piles, lengths, or simple values
- university level: compare monotone images, norms, signs, or growth rates
- research level: compare dominant scales, leading terms, or controlling mechanisms before full computation

## Cross-Domain Analogue

- debugging: compare candidate failure points on one severity or timing axis
- product/strategy: compare options by one decisive metric before detailed modeling
- science: compare regime strength or scale without solving the full system

## Where It Transfers

- same-base exponent comparisons
- same-exponent base comparisons
- logarithm / root ordering
- function-value ordering
- threshold and sign judgments

## Failure Mode

- the objects do not share one stable comparison axis
- hidden domain changes break monotonicity
- the comparison depends on local behavior, not global ordering
- the chosen threshold is suggestive but not actually decisive

## Verification Bill

- name the monotone axis explicitly
- state why all compared objects really lie on that same axis
- if using `大于1/小于1`, say why that threshold is decisive

## Seed Examples

- 2023 天津卷 第3题
- multiple compare-style seeds from the current corpus

## Neighbor Primitives

- `common-value compression`
- `boundary-condition attack`
- `minimal exact check`

## Transfer Promise

This primitive should activate across different surfaces:

- school comparison questions with ugly expressions
- function and calculus ordering questions
- asymptotic or dominant-term comparisons
- threshold judgment problems in science and modeling
- any problem where the real target is ranking, not full value recovery
