# Wu Boshi Before-After Comparisons

This file records side-by-side contrasts:

- standard solution
- fake reduction
- real reduction

The goal is not style critique.
The goal is to train the difference between:

- nicer wording
- genuine structural compression

## Comparison Template

For each problem, record:

1. `Problem shell`
2. `Standard route`
3. `Fake reduction version`
4. `Real reduction version`
5. `What actually got smaller`
6. `Reusable primitive`

## Example 1: Compound Growth

### Problem shell

- finance / interest / compounding language

### Standard route

- identify formula
- plug into compound-interest template
- simplify

### Fake reduction version

- say “本质上是复利公式”
- still plug into the same template immediately

### Real reduction version

- rename the task as “same multiplier repeated many times”
- count the number of periods first
- treat the whole problem as repeated growth, not as finance jargon

### What actually got smaller

- formula prestige disappeared
- the problem became repeated multiplication

### Reusable primitive

- `transformation rewrite`
- `count before derive`

## Example 2: Probability Story

### Problem shell

- sequential random story with many small events

### Standard route

- follow branches chronologically
- build a probability tree

### Fake reduction version

- say “这其实就是排列”
- but still continue with the full branch tree

### Real reduction version

- flatten the process into one static matching space
- count favorable structures over total structures

### What actually got smaller

- time-ordering burden vanished
- the story became a static combinatorial object

### Reusable primitive

- `matching instead of probability`

## Example 3: Target-Only Geometry

### Problem shell

- full coordinate or conic reconstruction seems required

### Standard route

- find all coordinates
- solve the whole object
- only then extract the target quantity

### Fake reduction version

- say “只需求这个量”
- but still reconstruct everything

### Real reduction version

- write only the target relation
- discard unrelated object recovery
- introduce only what certifies the target

### What actually got smaller

- object burden dropped to relation burden

### Reusable primitive

- `target-only proof`

## Example 4: Fixed Distance With A Shared Time Offset

### Problem shell

- same route
- several speeds
- one shared stop time
- looks like a standard two-unknown word problem

### Standard route

- set unknown speed `s`
- set unknown stop time `t`
- write two total-time equations
- subtract
- solve a quadratic in `s`
- back-substitute for `t`
- compute the requested final time

### Fake reduction version

- say “本质上是固定路程下速度变化影响时间”
- maybe mention that the stop time is the same
- then still introduce `s,t` immediately and follow the same standard skeleton

Why it is still fake:

- the wording improved
- but the chosen objects did not change
- the route is still “solve the usual parameters first”

### Real reduction version

- rename the task as “read the walking-time change on the same distance `9`”
- strip the shared stop time away as a common translation layer
- replace `speed` as the main object with the walking-time readouts:
  - `A = 9/s`
  - `B = 9/(s+2)`
- use:
  - `A - B = total-time difference`
  - `9/B - 9/A = 2`
- solve the relation between the two walking times first
- only then recover the needed final time

### What actually got smaller

- the shared stop time stopped being a live moving part
- the object changed from “solve two parameters” to “compare two readouts on one reciprocal law”
- variable choice was controlled by the essence, not by textbook habit

### Reusable primitive

- `essence-first variable choice`
- `shared-offset stripping`
- `projection readout`
- `relation before object`

## Hard Rule

Every new “good example” should be able to survive this comparison format.
If the real-reduction column is not clearly different from the fake-reduction column, the example is not strong enough.
