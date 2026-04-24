# Competition Saturation

This file defines one compatibility rule:

- single-route or single-skill settling should happen only after competition has become sufficiently informative

Its purpose is:

- stop premature collapse
- preserve natural route choice
- still avoid visible workflow

## Core Claim

The package should not reward:

- first plausible route
- first plausible skill
- first elegant local carrier

as if that were already enough to settle the competition.

The package should prefer:

- natural settling after nearby candidates have become weak enough
- natural consolidation when several candidates have effectively merged into one smaller carrier

## What Saturation Means

Competition is saturated enough when:

- nearby alternatives no longer delete comparable burden
- verification pressure clearly favors one route
- carrier-integrity pressure no longer points strongly elsewhere
- keeping alternatives alive adds little information
- or several alternatives have already been absorbed into one carrier and no longer need separate survival

This should remain:

- descriptive
- local
- provisional

Not:

- a required stage gate

## What Must Not Happen

Do not turn saturation into:

- “after N comparisons, settle”
- “always keep three candidates alive”
- “always run a second route”

Those are workflow rules, not compatibility rules.

## Relation To Single-Route Execution

Use:

- `single-route-elite-execution.md`

Single-route execution is still the mature goal.

This file adds only one guard:

- maturity should come after enough informative competition,
- not after arbitrary early lock-in

## Relation To Coactivation

Use:

- `coactivation-without-choreography.md`

That file preserves multiple weakly alive candidates.

This file clarifies when those candidates may naturally stop mattering.

It also allows one more honest outcome:

- some candidates do not merely lose
- they cool because their useful burden deletion has already consolidated into one route

## Final Rule

The package should let one route or one skill win when competition has genuinely cooled around it.

It must not decide that moment in advance.
