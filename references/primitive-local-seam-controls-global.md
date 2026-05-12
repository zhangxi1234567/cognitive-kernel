# Primitive: Local Seam Controls Global

## Pattern

A global claim is controlled by the first place it could fail, switch, saturate, or break.

## Trigger Signal

- the claim is global but failure would begin locally
- the problem asks for threshold, feasibility, stability, universality, or onset
- one boundary, equality case, witness, or first obstruction seems load-bearing
- brute-force global checking is expensive
- "where would it break first?" feels more natural than "how do I prove all cases?"

## Level-Agnostic Core

Do not inspect the entire universe if one dangerous seam already decides whether the universe survives.

## Control Mechanism

The move works because of:

- extremal witness control
- first-obstruction logic
- boundary onset
- local-to-global forcing structure
- seam behavior that organizes the whole regime

## Preserved Structure

Typical preserved items:

- threshold order
- first-failure logic
- boundary-determined regime split
- witness implication for the global claim
- one dangerous local place whose behavior controls the rest

## Earliest Honest Layer

If it breaks anywhere, where does it break first?
Go there first.

## Fast Move

1. Guess the most dangerous local seam.
2. Test the seam with the cheapest witness.
3. If it survives there, use that seam to control the global condition.
4. Only then pay for broader proof if needed.

## Compression Move

Typical burden deletion:

- all cases -> first dangerous case
- global feasibility -> seam witness
- full regime analysis -> onset analysis
- universal statement -> local obstruction check

## Level Transfer

- low-complexity form: test the weakest point first
- compact formal form: boundary case / extremal witness / smallest dangerous example
- advanced formal form: local obstruction, instability onset, first violated condition, saturation seam

## Cross-Domain Analogue

- debugging: find the first failing interface instead of auditing every layer
- strategy: test the brittle dependency that would kill the whole plan first
- research modeling: locate the instability onset before modeling the whole phase space

## Where It Transfers

- inequalities and parameter thresholds
- geometry feasibility and tangent/boundary arguments
- optimization and stability questions
- proof search and counterexample search
- systems and failure diagnosis

## Failure Mode

- the chosen seam is not actually controlling
- multiple seams compete and only one was checked
- local survival does not imply global survival in this structure
- the local witness is informative but not forcing

## Verification Bill

Explain:

- why this seam is the first dangerous place
- why controlling it is enough, or exactly what extra step remains

## Seed Examples

- witness probing and candidate elimination routes
- threshold / boundary problems
- "guess then verify" attacks whose hinge is a dangerous local seam

## Neighbor Primitives

- `Boundary Witness Probing`
- `Dominant Mechanism Readout`
- `Target-Only Control`

## Transfer Promise

This primitive should activate across different surfaces:

- inequality / parameter thresholds
- tangent or boundary geometry
- stability and optimization onset
- counterexample search and proof search
- debugging the first divergence in a system
