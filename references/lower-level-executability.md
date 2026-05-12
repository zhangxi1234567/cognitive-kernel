# Wu Boshi Lower-Level Executability

This file defines how to test whether a lowered route is executable, not merely understandable.

## Understandable vs Executable

Many answers are:

- understandable at a lower level

but not:

- executable at a lower level

Wu Boshi style wants executable reduction whenever it claims true lowering.

## Executability Test

A lower-level route is executable if the lower-level solver can:

1. name the real object
2. perform the decisive move
3. justify the shortcut with one visible mechanism
4. reach the answer or reach the final minimal seal

If they can only understand the story but cannot perform the hinge, the reduction is incomplete.

## Common Failures

- the picture is elementary, the hinge is still advanced
- the toy model is clean, the real route still needs imported formal machinery
- the learner can repeat the slogan but not do the next move
- the lower layer only identifies the direction, not the decisive action

## Good Outcomes

Good execution feels like:

- “I can actually do the next step.”
- “The smaller route is not just motivational.”
- “The answer key got replaced, not summarized.”

## Evaluation Prompt

When reviewing a lowered route, ask:

- could a solver one layer lower reproduce the main path from this explanation?
- where exactly would they get stuck?
- is that stuck point necessary or a sign that the route was not lowered enough?

## Hard Rule

If the lower-level solver loses control before the decisive hinge, the route fails lower-level executability.
