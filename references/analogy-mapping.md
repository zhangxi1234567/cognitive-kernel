# Wu Boshi Analogy Mapping

This file defines when analogies are useful, when they are only scaffolding, how to map them back to the real problem, and how to stop analogy drift from creating fake understanding.

## Main Principle

- analogy is allowed only when it preserves the decision-making structure of the original problem
- the analogy is never the answer itself
- the real target is always the original mechanism, constraint, or comparison

## When Analogy Helps

Use analogy when at least one of these is true:

- the original wording is abstract, but the hidden structure is simple
- the same invariant, conservation law, ordering, symmetry, or bottleneck becomes obvious in a lower-level picture
- the user is blocked by notation rather than by the core logic
- a smaller, concrete, or everyday version exposes which quantity really matters
- the analogy reduces cognitive load without changing what decides the result

Good uses:

- advanced algebra -> balance, partition, or monotone-axis picture
- geometry -> distance, folding, cutting, or shadow picture
- physics -> flow, bookkeeping, or competing tendencies picture
- chemistry -> particles, slots, accounting, and constraint picture
- debugging / systems -> pipeline, queue, bottleneck, or invariant picture

## When Analogy Is Only Scaffolding

Treat the analogy as scaffolding, not as proof, when any of these is true:

- it helps the user feel the direction, but does not preserve all exact constraints
- it gets the sign, trend, or route right, but not the exact threshold
- it hides discrete cases, boundary effects, or quantization
- it compresses many variables into one picture and therefore drops interactions
- it matches the emotional intuition of the problem more than the exact mechanism
- the task requires proof, auditability, or exam-standard legality

Operational consequence:

- if the analogy is only scaffolding, label it before using it
- after the analogy, switch to the minimal formal skeleton needed to re-ground the answer

## Hard Requirements Before Using An Analogy

Before using an analogy, check all of these:

1. What exact part of the original problem am I trying to illuminate?
2. Which structure is preserved?
3. Which parts are distorted, ignored, or collapsed?
4. Can I translate the conclusion back into the original terms in one or two sentences?
5. Would the analogy still point the same way on a boundary case?

If you cannot answer these, do not use the analogy.

## Preserve / Drop Table

Every nontrivial analogy should be mentally checked with this table:

- preserve:
  - invariant
  - ordering axis
  - conservation / bookkeeping rule
  - symmetry
  - bottleneck / dominant constraint
  - no-overlap / no-omission counting structure
- may drop:
  - exact units
  - numerical scale
  - second-order effects
  - domain-specific terminology
  - formal proof details

If the analogy drops something that can change the answer, escalate immediately.

## Map-Back Protocol

After the analogy, explicitly return to the original problem.

Required map-back shape:

1. `In the analogy`
   State the toy picture in one sentence.
2. `In the real problem this corresponds to`
   Name the exact original objects, symbols, or constraints.
3. `What stays true`
   Name the preserved mechanism: invariant, monotonicity, partition, symmetry, conservation, or comparison axis.
4. `What does not carry over`
   Name the distortion or limit of the analogy.
5. `So back in the original problem`
   State the real conclusion in the original language.

If the answer skips step 4, it is likely pretending the analogy is exact when it is not.

## Anti-Fake-Understanding Checks

The explanation fails if any of these happen:

- the user can repeat the story but cannot identify the original decisive quantity
- the analogy is memorable, but the map-back sentence is vague or missing
- the analogy makes the result feel obvious while the legality of the step stays hidden
- the analogy supports multiple different conclusions depending on which detail you stare at
- the analogy depends on visual similarity while the real problem is decided by a non-visual constraint
- the analogy smooths out a discrete problem into a continuous story
- the analogy turns a many-case problem into one cute picture

## Misleading Analogy Triggers

Be suspicious when:

- continuous is standing in for discrete
- average behavior is standing in for worst-case behavior
- one-dimensional motion is standing in for multi-constraint feasibility
- geometric neatness is standing in for algebraic legality
- flow language is standing in for conservation when there is actual loss, gain, or branching
- everyday causality is standing in for a purely structural comparison

These are common sources of fake understanding.

## Safe Output Pattern

When analogy is used, the answer should usually contain these micro-lines:

- `先把它看成……`
- `这个类比只负责帮你看见结构，不是严格证明。`
- `翻回原题，对应的是……`
- `这里真正没变的是……`
- `这个类比不能替代……`

This keeps the explanation intuitive without laundering the analogy into proof.

## Escalation Triggers

Escalate beyond analogy when:

- two plausible analogies suggest different answers
- the analogy cannot survive an edge case
- exact thresholds, counts, or legality matter
- the domain is high-stakes
- the user explicitly asks for proof or rigorous derivation
- the analogy is doing more persuasion work than explanation work

Escalation ladder:

1. analogy for orientation
2. minimal formal skeleton
3. exact derivation / proof
4. assumption and edge-case audit
