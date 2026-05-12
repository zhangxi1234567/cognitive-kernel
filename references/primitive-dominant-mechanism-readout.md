# Primitive: Dominant Mechanism Readout

## Pattern

Many mechanisms are present, but only one scale, one term, one regime, or one instability seam actually controls the outcome.

## Trigger Signal

- the model has many terms but one regime is explicit
- the question is about trend, onset, stability, or asymptotic behavior
- exact full solution feels disproportionate to the asked target
- the language suggests weak/strong, large/small, dilute, near-boundary, or leading-order behavior
- one term, one seam, or one bottleneck visibly dwarfs the rest

## Level-Agnostic Core

Not every visible force deserves equal attention.
Find what dominates first.

## Control Mechanism

The move works because:

- scale separation
- asymptotic dominance
- leading-order control
- bottleneck control
- instability onset controlling the regime switch

## Preserved Structure

Typical preserved items:

- regime identity
- leading-order sign or scale
- threshold / onset logic
- target-relevant behavior under the dominant mechanism
- map from full system to effective reduced story

## Earliest Honest Layer

Ask which effect is doing the real work, and which effects are only corrections.

## Fast Move

1. Name the active regime.
2. Identify the dominant term, mechanism, or seam.
3. Solve the leading-order story first.
4. Add only the smallest check needed to justify ignoring the rest.

## Compression Move

Typical burden deletion:

- many competing effects -> one active driver
- full exact model -> effective regime story
- all terms equal attention -> leading-order readout
- giant search space -> bottleneck / onset analysis

## Level Transfer

- low-complexity form: which side matters more / which pile grows faster
- compact formal form: leading term, monotone driver, or bottleneck
- advanced formal form: asymptotic regime, effective theory, dominant balance, instability trigger

## Cross-Domain Analogue

- debugging: find the first real bottleneck rather than explaining every symptom
- strategy: identify the one constraint actually limiting the system
- learning: ignore decorative formulas and locate the one load-bearing relation

## Where It Transfers

- asymptotics and analysis
- mechanics, thermo, kinetics, and field theory intuition
- optimization under competing effects
- algorithm/runtime reasoning
- complex diagnosis problems

## Failure Mode

- the "small" terms are actually target-critical
- the regime assumption is unstated or false
- crossover between mechanisms happens inside the asked region
- the dominant story is qualitatively right but not quantitatively enough for the asked target

## Verification Bill

State:

- why this mechanism dominates in the current regime
- where the regime would stop being trustworthy

## Seed Examples

- asymptotic comparison routes
- limit / threshold / stability onset attacks
- regime-based reductions in physical or analytical models

## Neighbor Primitives

- `Boundary Witness Probing`
- `Canonical Normalization`
- `Local Seam Controls Global`

## Transfer Promise

This primitive should activate across different surfaces:

- asymptotic analysis and leading-term comparison
- physical regimes with one active mechanism
- algorithm/runtime bottleneck questions
- optimization under one limiting factor
- debugging and diagnosis where one interface or resource is really in charge
