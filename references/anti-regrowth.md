# Wu Boshi Anti-Regrowth Rules

This file prevents reduced conics solutions from swelling back into textbook coordinate grind.

## Operational Rules

- Start with the geometric object, not the full equation:
  - center
  - axis
  - focus
  - tangent
  - chord
  - symmetry line
  - signed distance
- Normalize once, then stop. Translate / rotate / scale only if it removes a real nuisance.
- Track only the target quantity:
  - slope
  - midpoint
  - chord length
  - root sum / product
  - discriminant sign
  - distance to focus
  - area
- Use line-conic interaction as a one-parameter problem.
- Prefer relation-reading over point-finding.
- Freeze symbolic surface area:
  at each step, the number of free symbols should stay the same or go down.
- Ban early expansion.
- Every `直接看出` step must name the preserved structure:
  - symmetry axis
  - equal power
  - Vieta pair
  - discriminant threshold
  - distance definition

## Failure Signals

- solving both intersection coordinates when the target only needs slope, midpoint, existence, or range
- expression length grows for two consecutive steps
- introducing a second auxiliary point or parameter with no immediate target payoff
- expanding a quadratic or quartic before checking discriminant, Vieta, or symmetry
- drifting from “what geometric quantity controls this?” to “let me compute everything”
- losing the ability to explain the step as picture, symmetry, root relation, or one decisive comparison
- turning a conic problem into generic elimination with no geometric interpretation attached to coefficients

## Fallback Conditions

Escalate to `稳招` when picture / symmetry / Vieta / discriminant suggest the route but cannot separate cases cleanly.

Allow minimal coordinate grind only when:

- the target is explicitly analytic
- line-conic substitution has already reduced it to one quadratic with usable structure
- a discriminant or range condition must be computed exactly
- the synthetic story cannot rule out hidden branches or boundary cases

When fallback happens, enforce:

- one coordinate frame
- one moving parameter
- one quadratic at a time
- stop at the target quantity
- after each algebra block, translate back to geometry immediately

If even that fails, switch from `快招` to `最短可靠解` and say why:

- symmetry did not close
- discriminant alone was insufficient
- target required explicit branch resolution
