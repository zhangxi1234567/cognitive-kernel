# Deformed Balance Derivation

Let `T = X + S + Y`. The target condition is:

1. `T` is deformed.
2. `T + ")"` is balanced.

## 1. Deformed strings as a two-phase parser

The grammar

- `D -> ")"`
- `D -> "(" D "("`
- `D -> D ")" D`

can be read left-to-right with:

- `phase = NEED_OPERAND` or `NEED_OPERATOR`
- `p = number of pending outer "(" wrappers`

Transitions:

- In `NEED_OPERAND`:
  - `'('` starts one wrapper: `p += 1`
  - `')'` is the atomic leaf, and phase flips to `NEED_OPERATOR`
- In `NEED_OPERATOR`:
  - `'('` must close one pending wrapper, so `p -= 1`
  - `')'` is the binary separator, and phase flips to `NEED_OPERAND`

So a string is deformed iff, starting from `(NEED_OPERAND, p = 0)`, this parser never tries to close a missing wrapper and ends at `(NEED_OPERATOR, p = 0)`.

## 2. Independent ordinary balance counter

The extra condition `T + ")"` balanced is equivalent to:

- every prefix of `T` has ordinary parenthesis balance `b >= 0`
- the final ordinary balance of `T` is exactly `1`

So we only need two counters:

- `p`: parser-wrapper debt
- `b`: ordinary parenthesis balance

and the parser phase.

## 3. What the fixed middle substring does

For a chosen starting phase, scanning `S` does three things:

- toggles the phase once for every `')'`
- changes `b` by `balance(S)`
- changes `p` by:
  - `+1` for `'('` seen in `NEED_OPERAND`
  - `-1` for `'('` seen in `NEED_OPERATOR`

This gives:

- `delta_p(start_phase)`
- `need_p(start_phase)` = minimum initial `p` needed so that every operator-phase `'('` really has a wrapper to close

The ordinary-balance requirement only contributes

- `min_b = -min_prefix_balance(S)`

for the starting `b`.

## 4. Minimal prefix cost to reach a starting state

Let the state before `S` be `(phase, p, b)`.

### Regime A: `p >= b` (or `p > b` when phase is `NEED_OPERATOR`)

The shortest prefix is just

- `'(' * p`
- then enough `')'` to reduce `b` to the target

so its length is `2p - b`.

### Regime B: `p < b`

Now we need one of the smallest gadgets that creates extra ordinary balance beyond wrapper count.

- Ending in `NEED_OPERATOR`: base gadget `()(`, so the shortest length is `b + 2`
- Ending in `NEED_OPERAND`: base gadget `()(` followed by one extra `)`, so the shortest length is `b + 4`

These are exactly the two piecewise prefix formulas used in the code.

## 5. Minimal suffix cost from the state after `S`

If the state after `S` is `(phase, p, b)`:

- From `NEED_OPERATOR`, first close all wrappers with `p` copies of `'('`, then consume balance down to `1` with `')'`. Cost: `2p + b - 1`.
- From `NEED_OPERAND` and `b > 0`, prepend one `')'` to create the atomic leaf, then use the previous case. Cost: `2p + b - 1`.
- From `NEED_OPERAND` and `b = 0`, that leading `')'` would break prefix-balance, so we must first use `"()"` to lift balance. Cost: `2p + 3`.

## 6. Final optimization

For each of the two possible starting phases:

1. compute `delta_p`, `need_p`, and the ending phase after `S`
2. set `low_p = max(need_p, -delta_p)`
3. evaluate the constant number of regime candidates

Only two `p` parities matter in Regime B, so each test case is solved in `O(|S|)` time and `O(1)` extra space.
