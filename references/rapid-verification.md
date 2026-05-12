# Wu Boshi Rapid Verification

This file defines how the skill should verify a promising candidate or guessed structure quickly.

## Core Principle

Do not fully verify every candidate.

Ask instead:

- if this candidate is wrong, where will it break first?

Then test that seam first.

## Quick Verification Targets

Use fast verification to answer one of these:

- does this candidate even survive the most dangerous point?
- does this guessed structure preserve the real condition?
- does this answer shape immediately contradict one cheap check?

## Weakest-Seam Order

When a candidate appears, test in this order:

1. `core singular point`
2. `boundary / endpoint`
3. `sign / monotonicity seam`
4. `overlap / omission risk`
5. `one substitution`

Stop as soon as the candidate breaks.

## Common Fast Checks

### 1. Singular-point check

Use when the expression has:

- denominator zero risk
- logarithm / square-root domain edge
- tangent / contact point
- branch switch

Question:

- if the candidate were wrong, would the first failure show up near the singular point?

### 2. Boundary check

Use when the problem asks for:

- minimum / maximum parameter
- existence boundary
- just-saturated condition
- equality case

Question:

- does this candidate look like the first value that could possibly work?

### 3. Sign seam

Use when the task is really:

- monotonicity
- positivity / negativity
- inequality
- one-side dominance

Question:

- is there a simple point or interval where the sign would flip if the candidate were wrong?

### 4. Partition / no-leak check

Use when the route depends on:

- counting
- classification
- matching
- case split

Question:

- will this count leak by 漏数 or 重数?

### 5. One substitution

Use when the candidate is:

- one clean numeric value
- one simple formula
- one guessed line / point / constant

Question:

- if I plug it back into the decisive relation, does it survive?

### 6. Exception-class seam

Use when the route may be right for the main case but wrong for one special class.

Examples:

- hostname versus IP
- whitelist versus blocklist override
- null versus non-null
- empty versus non-empty
- finite versus degenerate

Question:

- what special class would break this elegant route first if I forgot to split it out?

## Threshold / Boundary Verification

For minimum / maximum / first-break / first-switch problems:

Do not fully solve each candidate one by one.

Instead:

1. generate a small candidate set
2. ask what makes a candidate fail first
3. check the smallest dangerous seam
4. once one candidate survives, try to exclude the neighboring stronger / weaker candidate family in one shot

Default slogan:

- `先卡边界，再验边界，不要一上来全域硬推。`

## Seam-First Shortcut Pattern

When the problem looks like:

- choose the smallest / largest value that keeps a condition true
- determine where a case split or option switch happens
- prove a global claim by finding where it would fail first
- decide whether a structure survives comparison, counting, matching, or geometry constraints

prefer this fast route:

1. rewrite the target as `candidate + controlling seam`
2. guess the seam where failure, switching, or saturation would show first
3. test that seam first to obtain the lower / upper bound or eliminate neighboring candidates
4. check the surviving boundary candidate globally with one compressed skeleton

Good shapes:

- midpoint or symmetry seam exposes the lower bound
- singular seam exposes the impossible side
- one small example exposes the wrong counting family
- one subfigure or section exposes the controlling geometric obstruction

Bad shape:

- solving the whole object before checking whether one local seam already separates the candidate family

## Output Contract

When using rapid verification, the answer should sound like:

- `先试这个，不是因为它一定对，而是因为它最容易先露馅。`
- `先看最危险的地方，它如果错，会先从这里坏。`
- `这一步不是全验证，是先做最快的排除。`

## Hard Rule

If the candidate survives only after a long derivation, that was not rapid verification.
Downgrade to `稳招` or `最短可靠解`.

For threshold / boundary problems, rapid verification is complete only if:

- one witness seam explains why neighboring candidates fail
- one short global bound or structural skeleton explains why the surviving boundary candidate works

If either half is missing, the route is only half-compressed.
