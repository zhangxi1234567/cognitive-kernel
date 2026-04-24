# Wu Boshi Fast Primitives

This file stores the smallest reusable attack primitives behind the public ruler-method / Wu Boshi style.

Each primitive is written as a deployable move, not as a theory note.

## Primitive 1: Comparison Axis

- **Pattern**: the real task is to decide larger/smaller, earlier/later, higher/lower, or more/less.
- **Trigger**: exact computation feels heavy, but ranking would already answer the question.
- **Why it works**: many problems only need order, not value.
- **Transfer**: inequality, monotonicity, optimization, graph reading, decision making.
- **Failure mode**: choosing the wrong axis or assuming local order equals global order.

## Primitive 2: Visual Proxy

- **Pattern**: use a diagram, ruler, anchor point, or rough geometric readout.
- **Trigger**: the expression is hard, but the shape is easy to see.
- **Why it works**: visual structure often preserves the decisive relation even if it drops exact decimals.
- **Transfer**: geometry, functions, conics, data flow, strategy maps.
- **Failure mode**: the proxy distorts the relation or hides a critical case.

## Primitive 3: Prototype Match

- **Pattern**: route the problem into one of a few known families.
- **Trigger**: the problem feels new, but there is a strong family resemblance.
- **Why it works**: the hard part is recognition, not derivation.
- **Transfer**: function types, geometry families, bug classes, recurring strategy shapes.
- **Failure mode**: forcing a bad template fit.

## Primitive 4: Anchor First

- **Pattern**: identify the load-bearing point, line, value, or relation.
- **Trigger**: too many moving parts.
- **Why it works**: once the anchor is fixed, the rest of the structure is much easier to constrain.
- **Transfer**: conics, graph analysis, system debugging, planning.
- **Failure mode**: picking a non-structural anchor.

## Primitive 5: Count Instead of Derive

- **Pattern**: the answer is already encoded in cases, pieces, regions, or repetitions.
- **Trigger**: the structure repeats or partitions cleanly.
- **Why it works**: counting can skip formula-building.
- **Transfer**: combinatorics, geometry partitions, workflow analysis.
- **Failure mode**: missing overlap or double counting.

## Primitive 6: Boundary Check

- **Pattern**: test endpoints, extreme values, or simplest substitutions first.
- **Trigger**: a claim looks plausible but unverified.
- **Why it works**: many false shortcuts break at boundaries.
- **Transfer**: proof checks, model validation, debugging, optimization.
- **Failure mode**: boundary behavior differs from interior behavior.

## Primitive 7: Freeze the Motion

- **Pattern**: turn a moving or changing system into a single snapshot.
- **Trigger**: the process is hard to reason about dynamically.
- **Why it works**: static relationships are easier to compare than moving ones.
- **Transfer**: kinematics, graphs, state machines, process analysis.
- **Failure mode**: the snapshot misses path dependence.

## Primitive 8: Smallest Truthful Model

- **Pattern**: shrink the problem until only the decision-making structure remains.
- **Trigger**: the original problem feels overloaded.
- **Why it works**: the extra details are often decoration, not load-bearing structure.
- **Transfer**: all domains.
- **Failure mode**: shrinking away a real assumption.

## Primitive 9: One-Line Legality Check

- **Pattern**: every shortcut must have one sentence explaining why it is legal.
- **Trigger**: any speed claim is made.
- **Why it works**: fast answers fail when they skip the trust bill.
- **Transfer**: all high-trust reasoning.
- **Failure mode**: confidence theater.

## Primitive 10: Score the Result, Not the Algebra

- **Pattern**: ask what actually decides the score, not what produces the prettiest derivation.
- **Trigger**: exam-style or decision-style problem.
- **Why it works**: the goal is correct action or correct choice, not symbolic excess.
- **Transfer**: tests, product tradeoffs, strategy, diagnostics.
- **Failure mode**: over-optimizing elegance instead of decision quality.

## Operating Rule

When a new problem arrives, try to resolve it by stacking these primitives in this order:

1. comparison axis
2. visual proxy
3. prototype match
4. anchor first
5. count instead of derive
6. boundary check
7. freeze the motion
8. smallest truthful model
9. one-line legality check
10. score the result, not the algebra
