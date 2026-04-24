# Wu Boshi Witness Probing

This file defines how to use special values of the running variable to test or eliminate candidate parameter values quickly.

## Core Principle

When a global condition, threshold, or case distinction is present, do not begin by controlling everything.

Ask first:

- if a candidate is wrong, where will it break first?

That local place is the witness.

## What Counts As A Witness

A witness is not just any easy number, point, case, or picture.
It is the local seam most likely to expose failure fast.

Good witness locations:

- near singular points
- near moving roots
- endpoints / boundaries
- symmetry points
- midpoint / balance points in symmetric domains
- branch-switch cases
- smallest nontrivial examples
- one dangerous subfigure or subconfiguration
- values that collapse the algebra sharply
- points where sign is easiest to check

## Witness Search Order

Useful probe order:

1. singular-point seam
2. boundary / endpoint
3. moving-root neighborhood
4. symmetry point
5. simple integer / rational point that collapses the expression

## Fast Workflow

1. generate candidate set
2. choose the candidate worth testing first
3. choose the witness most likely to expose failure
4. test only that seam
5. if it fails, eliminate the candidate or a whole candidate region
6. if it survives, compare against the nearest stronger/weaker candidate

Important:

- do not stop after finding one surviving witness
- immediately ask whether the neighboring weaker or stronger candidate can be eliminated by the same seam or the next cheapest seam

## Threshold / Boundary Use

For minimum / maximum / first-break / first-switch problems:

- do not fully solve each candidate
- do not test random local cases
- try to find one witness that separates neighboring candidates

Good internal question:

`有没有一个最危险的 x，能最快把 -2 和 -3 分开？`

Extra good internal questions:

- `有没有一个最危险的局部位置，能最快把相邻候选分开？`
- `有没有一个中点 / 对称点 / 最小样例，会把边界直接暴露出来？`
- `能不能用一个 witness 先卡下界，再用一个全局骨架收尾？`

## Common Witness Families

When the task is about:

- monotonicity / sign / stability
- counting / no-overlap / no-miss
- geometry / tangency / intersection
- threshold / existence / first-switch
- matching / assignment / exact cover

the witness search should strongly prefer:

1. seam where the structure is most balanced or most fragile
2. boundary or branch-switch location
3. smallest nontrivial example or subconfiguration
4. singular-point neighborhood if the expression has blow-up risk

Reason:

- these places often expose the controlling obstruction fastest
- they separate neighboring candidates faster than random checking

## Output Pattern

When using witness probing, the answer should sound like:

- `先别管整体，先找最危险的那个局部接缝。`
- `这个候选如果错，通常会先在这里露馅。`
- `这一步不是全证，是先做最快排除。`

## Failure Mode

Witness probing fails when:

- the chosen witness is not actually part of the relevant structure
- the chosen witness is easy but not dangerous
- one probe is mistaken for a full proof
- the skill never tries to exclude neighboring candidates

## Hard Rule

Witness probing may screen and rank candidates fast.
It may not pretend one lucky probe fully proves a global statement unless the preserved mechanism is explicitly named.

If a witness only proves one inequality, exclusion, or local obstruction, say that plainly.
The final step still needs either:

- a survival check at the surviving candidate
- or a short global skeleton that shows the whole domain is covered
