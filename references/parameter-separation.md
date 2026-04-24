# Wu Boshi Parameter Separation

This file defines parameter separation as a reusable reduction move.

Its purpose is:

- separate the moving parameter from the fixed geometric or algebraic structure
- expose constant points, lines, or quantities hidden inside parameterized families
- reduce a many-case parameter sweep to one fixed control relation

## Core Rule

When a family is driven by a parameter, ask:

- what changes with the parameter?
- what does not change?
- can the equation be rearranged so the parameter sits in one factor and the fixed structure sits in another?

Then compress:

- parameterized family -> fixed object + one moving scalar

## Trigger Signals

- one symbol appears everywhere as a family parameter
- `for all k` / dynamic line / moving chord / moving point
- repeated slope or intercept parameter
- 恒过定点 / 恒定 relation hints

## Compression Moves

- rearrange to isolate parameter coefficient
- compare parameter-dependent and parameter-free parts
- read fixed point / fixed line from the separated form
- reduce family behavior to one geometric invariant

## Why It Works

- parameters often create fake motion
- once separated, the fixed skeleton appears
- the true task is usually about the fixed controller, not the moving shell

## Good Uses

- dynamic lines
- moving intersections
- parameter inequalities
- family-wide fixed-point / fixed-line questions

## Failure Boundary

Do not overfire this move when:

- the parameter changes the whole mechanism, not just the shell
- separation is algebraically possible but not structurally meaningful
- the target really depends on the full moving family

## Transfer

- school math: parameter lines, inequalities, function families
- university math: one-parameter families, stability thresholds
- research-style transfer: separate control parameter from fixed mechanism
