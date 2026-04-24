# Wu Boshi Seed-Primitive Mapping

This file defines how answer-keyed seed problems map upward into reusable primitives and families.

## Universal-Mapping Rule

Seeds are evidence, not boundaries.

Their job is:

- show the move in action
- test transfer
- expose legality and failure modes

Their job is not:

- define the only school stage where the move is allowed to exist

Use three layers:

1. `primitive`
2. `family`
3. `seed`

## Layer Roles

### Primitive

The atomic reusable move.

Examples:

- `common-value compression`
- `comparison-axis reduction`
- `container-to-section reduction`
- `projection readout`

### Family

A cluster of related primitives.

Examples:

- `visual readout`
- `comparison and elimination`
- `structure compression`
- `geometry anchoring`

### Seed

One real problem showing the primitive in action.

Examples:

- `2025 新高考 I 卷 第6题`
- `2025 新高考 I 卷 第8题`
- `2025 新高考 II 卷 第14题`
- or any non-exam example that exposes the same mechanism

## Mapping Rules

### A seed may be promoted to a primitive only if

- the move works beyond the exact figure / option set / lucky numbers
- the move has one stable legality mechanism
- the move has a clear transfer target
- the move has a clear failure mode
- the move can be restated in a level-agnostic way

### A seed must stay local-only if

- it depends on option spacing
- it depends on one cute numerical coincidence
- it depends on one special diagram look
- it cannot be stated without naming the original problem

## Suggested Mapping From Current Corpus

### Promote toward primitives

- `Vector Difference Readout`
- `Common-Value Parameter Compression`
- `Container -> Cross-Section`
- `Matching Instead Of Probability`
- `Grid Selection -> Permutation`
- `Compare Without Calculating`
- `Dot Product Range By Projection`

### Keep as seed tactics for now

- `Hidden 3-4-5 Recognition`
- `肉眼缺口小于 3.3`
- `取几个特殊 k 打选项`

## Recording Standard

When documenting a seed, record:

- paper
- year
- question id
- public answer
- route label:
  - `true 秒杀`
  - `快招`
  - `稳招`
  - `local-only trick`
- candidate primitive
- confidence of transfer
- level-transfer note

## Decision Rule

If a route is:

- decisive
- short
- legality-clear
- reusable

then promote it.

But promote the mechanism, not the school-style wrapper.

If it is:

- lucky
- local
- option-dependent
- hard to justify generally

then keep it as a seed only.
