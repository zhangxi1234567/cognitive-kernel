# Wu Boshi Anti-Standard-Solution Bias

This file prevents the skill from falling into textbook-default solution flow too early.

Core mandate:

- standard algebraic grind
- coordinate setup
- equation-heavy casework

must be treated as last resorts, not neutral defaults.

## Short-Attack Ladder

Before any standard flow, run this ordered scan:

1. `Picture-first`
2. `Invariant / monotone quantity`
3. `Symmetry / relabeling`
4. `Ratio / proportional structure`
5. `Anchor quantity`
6. `Elimination / avoid solving everything`
7. `Target-only proof`
8. Only then `standard algebra / coordinates`

## Hard Rules

- Never open with coordinates unless the problem is natively analytic.
- Never expand expressions early if a factor, ratio, or conserved quantity may control the problem.
- Never solve for all unknowns if the target can be reached directly.
- Never introduce more variables than the target requires.
- Never run textbook flow just because it is familiar.

If fallback to standard algebra happens, record the failure of shorter routes in one line:

- `Picture gave no stable relation`
- `No usable invariant found`
- `Symmetry did not reduce cases`
- `Target-only route blocked`

## Trigger Hints

### Picture-first

Use when:

- geometry, diagrams, equal angles, equal lengths, collinearity, cyclicity
- midpoint, bisector, parallel, tangent, area, ratio

### Invariant

Use when:

- repeated operations
- transformations
- recursion
- impossibility or uniqueness flavor

### Symmetry

Use when:

- variables or points play interchangeable roles
- target is symmetric but the work is asymmetric

### Ratio

Use when:

- segments, similar triangles, proportional terms, fraction chains

### Anchor quantity

Use when:

- many moving parts seem controlled by one hidden stable number

### Elimination

Use when:

- there are more unknowns than the target needs
- full solving would create bulky intermediates

### Target-only proof

Use when:

- the claim is a clean identity, bound, fixed value, divisibility, or line/point claim
- full reconstruction is unnecessary

## Strict Fallback Gate

Standard algebra / coordinates are allowed only if at least one is true:

- the problem is natively analytic
- the short-attack ladder was attempted and failed honestly
- the standard method is demonstrably shorter than remaining synthetic options

When fallback happens:

- use the minimal variable set
- do not expand blindly
- do not solve everything unless the target forces it
- periodically re-check whether a shorter route has reopened
