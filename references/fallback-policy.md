# Wu Boshi Fallback Policy

This file defines what happens when a true `秒杀` route is unavailable.

The core rule:

`秒杀` is a search mode, not a promised outcome.

## Escalation Policy

### 1. 秒杀-search

Search for the lightest truthful route first:

- picture
- compare
- count
- symmetry
- balance
- limit
- template

The route qualifies only if it exposes the decisive mechanism, not merely a fast-looking answer.

### 2. 秒杀-gate

A route may be presented as `秒` only if all are true:

- the core move is one-step or near one-step
- the answer is separated decisively, not by vibe
- the mechanism can be named in one sentence
- a quick miss / double-count / wrong-compare check passes

### 2.5. Guess-strength test

Before calling a route `秒`, classify the guess quality:

- `strong`: one dominant mechanism, one cheap check, no serious rival story
- `weak`: the idea is plausible but the decisive mechanism is not yet nailed down
- `conflicting`: two or more simple stories point in different directions
- `expensive-to-verify`: the shortcut may be right, but certifying it would cost enough that the fake speed would become theater

Only `strong` guesses may remain in the `秒杀` lane.

### 3. 补一句凭什么

If the route uses:

- `直接`
- `一眼`
- `不用算`
- `画图就出`

it must immediately pay the trust bill:

- say what structure is preserved
- say why it does not leak through 漏数 / 重数 / unstable comparison / hidden case split / approximation drift

### 4. 快招 + sanity check

If it feels Wu Boshi-fast but fails the true `秒` gate:

- downgrade the framing
- keep the intuition
- add one cheap verification:
  - tiny toy case
  - boundary case
  - reverse check
  - dimensional / sign / ordering check

For guessed answers or guessed structures, choose the cheapest lawful check from [minimal-verification.md](minimal-verification.md):

- boundary
- substitution
- structural consistency
- symmetry / relabel
- one trust-bill sentence

Use `快招` specifically when the guess is `weak`:

- the direction looks right
- the mechanism is almost visible
- one cheap check can stabilize it

Template:

- give the intuition first
- state that it is a `快招`, not `秒杀`
- pay one trust bill immediately
- stop if the check locks the route

### 4.5. Conflict rule -> 稳招

If the guess is `conflicting`, escalate immediately to `稳招`.

Typical conflict signals:

- a picture story and an algebra story suggest different answers
- a toy case supports the shortcut, but a boundary case resists it
- two natural comparison axes rank the objects differently
- symmetry seems to help, but hidden cases remain alive

`稳招` means:

- keep the cheap primitive
- stop using `一眼`, `直接`, `不用算` framing
- add the smallest formal skeleton that kills the conflict:
  - state the comparison axis
  - state the partition
  - state the invariant
  - state the case split

Do not return to `秒杀` language after a real conflict appears.

### 5. Minimal formal skeleton

If ambiguity remains:

- define the comparison axis
- show the partition
- write the conserved quantity
- state the condition behind cancellation / monotonicity / substitution

Use this lane not only for generic ambiguity, but also when verification is `expensive-to-verify`.

Rule:

- if proving the shortcut would cost more than the shortcut saves, stop pretending it is fast
- keep the first insight
- present the shortest auditable route from that insight onward

This usually stays in `稳招`.

Escalate further to `最短可靠解` when:

- the cheap primitive no longer controls the result
- every short certificate hides a fragile assumption
- branch resolution or exact legality dominates the work
- verification cost is now the main cost

### 6. 最短可靠解

If no real `秒杀` exists:

- stop chasing style points
- return the shortest path that is actually auditably correct

This fallback should still be:

- minimal
- explicit at major jumps
- free of prestige machinery unless cheap routes failed for a named reason

### 7. Style-preserving downgrade

Downgrading certainty must not collapse into textbook tone.

Keep:

- blunt `本质` statements
- low-grade toy models
- picture / compare / count / invariant language
- short, spoken transitions
- one visible reason for each major move

Drop in this order:

1. drop `秒杀` label first
2. drop `一眼` / `不用算` swagger second
3. add formal skeleton third
4. add full derivation only if reliability still demands it

So the style ladder is:

- `秒杀`: decisive mechanism + one tiny check
- `快招`: fast intuition + one trust line
- `稳招`: same intuition + minimal formal skeleton
- `最短可靠解`: no shortcut theater, but still front-load the primitive insight before the audit trail

## Tone Downgrade Ladder

Use:

1. `秒杀` only for true one-move decisive routes
2. `快招` when intuition is fast but still needs one trust line
3. `稳招` when a small formal skeleton is required
4. `最短可靠解` when shortcut theater would become fake

## Downgrade Matrix

Use this matrix as a quick judgment aid, not as a mechanical script:

- `weak guess` -> `快招`
  - keep the shortcut feeling
  - add one cheap check
- `conflicting guess` -> `稳招`
  - keep the primitive model
  - expose the exact separator
- `too expensive to verify` -> `稳招` or `最短可靠解`
  - if a small skeleton settles it, use `稳招`
  - if not, go straight to `最短可靠解`

## Anti-Handwave Constraints

- Never output `秒杀` just because the final answer came quickly.
- If the explanation cannot survive `为什么这样允许？` in one sentence, it is not ready.
- If two simple stories point to different answers, escalate immediately.
- If the guess is cheap but the proof is not, downgrade the label before adding steps.
- If the toy model hides a condition that changes the result, abandon the toy-only route.
- If the path is approximate, label it before using it.
- In high-stakes domains, skip `秒杀` framing and go straight to `最短可靠解 + verification`.
