# Wu Boshi Primitive Index

This file is the current top-level index of reusable fast primitives distilled from answer-keyed seed problems.

## Universal-Primitive Index Rule

All primitives indexed here should be interpreted as level-agnostic.

The seed evidence may currently lean school / exam style because public fast-solve examples are dense there.
That does not narrow the primitive.

Primitive identity should be defined by:

- control mechanism
- legality mechanism
- transfer target
- failure mode

not by:

- school stage
- paper source
- exam label

## Current Primitive Candidates

### High-confidence reusable primitives

- `Vector Difference Readout`
- `Common-Value Parameter Compression`
- `Container -> Cross-Section`
- `Area -> Line Readout`
- `Matching Instead Of Probability`
- `Grid Selection -> Permutation`
- `Compare Without Calculating`
- `Dot Product Range By Projection`
- `Canonical Normalization`
- `Projection Readout`
- `Dominant Mechanism Readout`
- `Local Seam Controls Global`
- `Definition As Direct Readout`
- `Symmetry As Variable Killer`
- `Boundary As Route Finder`
- `Model Calling Before Derivation`
- `Special-Value Probing`
- `Function Archetype Matching`

### Primitive cards implemented

- `references/primitive-common-value-compression.md`
- `references/primitive-compare-without-calculating.md`
- `references/primitive-container-to-section.md`
- `references/primitive-area-to-line-readout.md`
- `references/primitive-matching-instead-of-probability.md`
- `references/primitive-grid-selection-permutation.md`
- `references/primitive-dot-product-projection.md`
- `references/primitive-canonical-normalization.md`
- `references/primitive-projection-readout.md`
- `references/primitive-dominant-mechanism-readout.md`
- `references/primitive-local-seam-controls-global.md`
- `references/primitive-definition-as-direct-readout.md`
- `references/primitive-symmetry-as-variable-killer.md`
- `references/primitive-boundary-as-route-finder.md`
- `references/primitive-model-calling-before-derivation.md`
- `references/primitive-special-value-probing.md`
- `references/primitive-function-archetype-matching.md`

## Current Evidence Status

### Better supported by multiple seeds

- `Compare Without Calculating`
  - 2023 天津卷 第3题
  - several earlier compare-style public examples in the existing corpus

- `Dot Product Range By Projection`
  - 2022 北京卷 第10题
  - 2020 新高考全国卷 第7题

- `Container -> Cross-Section`
  - 2025 新高考 II 卷 第14题
  - related symmetric packing / tangency family expected to transfer well

- `Area -> Line Readout`
  - 2025 新课标 II 卷 第16题（area/chord relation pressure-testing）
  - broader triangle / trapezoid / line-gap area family is structurally strong

- `Conics second-layer attacks`
  - 2023 新高考 II 卷第21题第2问（target-only proof on fixed line）
  - 2025 新课标 II 卷 第16题（area/chord relation）
  - current conics heuristic pack pressure-testing

- `Exact-cover / one-to-one encoding`
  - 2024 新高考 II 卷 第14题第一空（row/column -> permutation）
  - 2024 新高考 I 卷 第19题（public解析显式使用精确覆盖建模）

### Good but still seed-thin

- `Common-Value Parameter Compression`
  - currently strongly anchored by 2025 新高考 I 卷 第8题
  - 2024 新高考 I 卷 第18题（1） is a useful adjacent structural seed
  - still needs more cross-topic seeds

- `Parameter-Boundary Guess / Witness Probing`
  - 2024 高考数学 II 卷 第8题 is a useful new seed
  - still needs at least 2-3 more strong seeds before promotion

- `Matching Instead Of Probability`
  - currently strongly anchored by 2024 新高考 I 卷 第14题
  - still needs more non-card, non-schedule seeds

- `Grid Selection -> Permutation`
  - currently strongly anchored by 2024 新高考 II 卷 第14题第一空
  - now has one adjacent exact-cover style seed from 2024 新高考 I 卷 第19题
  - still needs 1-2 more row/column or exact-cover style seeds

- `Canonical Normalization`
  - strongly justified as a universal move
  - still needs a denser explicit seed bank spanning geometry, linear algebra, and physical modeling

- `Projection Readout`
  - partially supported by existing dot-product and cross-section seeds
  - still needs more non-geometry seeds for broader promotion confidence

- `Area -> Line Readout`
  - conceptually strong and matches long-running geometric intuition in the library
  - still needs a denser explicit seed bank spanning triangle area, trapezoid area, chord area, and section-volume transfer

- `Dominant Mechanism Readout`
  - conceptually central for graduate/research transfer
  - still needs a curated advanced seed bank

- `Local Seam Controls Global`
  - already supported by witness / threshold / seam-first doctrine
  - still needs more concrete cross-topic examples as primitive evidence

- `Definition As Direct Readout`
  - strongly supported by the PDF corpus's repeated "定义先上" behavior
  - still needs a cleaner explicit seed bank beyond conics and function equations

- `Symmetry As Variable Killer`
  - strongly supported by corpus-level frequency and repeated balanced-position solving
  - still needs tighter seed bundling across geometry, functions, and combinatorics

- `Boundary As Route Finder`
  - strongly supported by repeated endpoint, tangent, extreme-position, and limiting-case route discovery in the PDF corpus
  - still needs a seed bank separating true route-finding boundaries from fake decorative endpoint checks

- `Model Calling Before Derivation`
  - strongly supported by recurring "模型" behavior across geometry, functions, and space-geometry notes
  - still needs explicit seed bundling across different named model families

- `Special-Value Probing`
  - strongly supported by repeated use of `0/1/-1`, special angles, equal variables, and boundary values in the PDF corpus
  - still needs tighter separation between true seam-probes and mere convenient substitutions

- `Function Archetype Matching`
  - strongly supported by repeated "同构 / 母函数 / family behavior" routing in the PDF corpus
  - still needs denser explicit seed bundling across transformed functions, functional equations, and graph behavior

### Seed tactics that should not yet be over-generalized

- `Hidden 3-4-5 Recognition`
- `肉眼缺口小于某阈值`
- `取几个特殊参数点打选项`

## How to use this index

Use it to decide:

- what is safe to promote into the core skill
- what should stay as a local example only
- what still needs more seed evidence before promotion

When promoting, always ask one extra question:

- does this primitive survive across levels of formality, or does it collapse outside one narrow school-style presentation?
