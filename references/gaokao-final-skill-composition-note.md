# Gaokao Final Problem Teaching Sample -> Simple Skill-Combo Kill

This note records another direct teaching sample, parallel to the JOI note.

The target is not "one more solved math problem."

The target is:

- a very short mother sequence
- simple enough to fire in seconds
- strong enough to kill a typical gaokao final problem without falling back to ordinary exam routines

## Scope

This is not a "derivative template."

This is a transfer note for problems where:

- a parameter is pretending to be the main object
- the real controller is a thinner value-carrier
- one peak / singular point / symmetry split can unify multiple subquestions

## Core Teaching Signal

The taught solve rhythm here was:

1. 先赋值
2. 画图
3. 抓峰值奇点
4. 用同高双点的对称关系直接读第二问
5. 用左端极限奇点和峰值上界直接爆破第三问

The important thing is not the exact exam surface.

The important thing is:

- first replace the object
- then externalize the carrier
- then let singularity and symmetry take over
- do not regress into ordinary derivative-first exam narration

## Demonstration Problem

Given

```text
f_a(x)=x+\ln x-ax,  x>0
```

1. discuss the number of zeros of `f_a(x)`
2. if `f_a(x)=0` has two distinct roots `x_1<x_2`, prove `x_1x_2>e^2`
3. find the range of `a` such that `f_a(x)<=0` for all `x>0`, and decide whether there exists any real `a` such that `f_a(x)>=0` for all `x>0`

## Fixed Problem Statement

This exact teaching sample should be remembered together with its full surface:

```text
已知函数 f_a(x)=x+lnx-ax (x>0)。
1. 讨论函数 f_a(x) 的零点个数。
2. 若 f_a(x)=0 有两个不同实根 x_1<x_2，证明 x_1x_2>e^2。
3. 求实数 a 的取值范围，使得对任意 x>0，恒有 f_a(x)<=0；
   并判断是否存在实数 a，使得对任意 x>0，恒有 f_a(x)>=0。
```

Do not remember only the method headline.

Remember both:

- the exact problem surface
- the exact short skill-composition chain that killed it

## Fixed Step Chain

This exact sample should be recalled with the following short step chain:

1. 先赋值
   - from `x + ln x - a x = 0`
   - rewrite as `a = 1 + (ln x)/x`

2. 画图
   - study `y = 1 + (ln x)/x`
   - left end drops to `-infinity`
   - right tail approaches `1`
   - it passes through `(1, 1)`
   - it peaks at `(e, 1 + 1/e)`

3. 第一问直接读横线截点
   - the number of roots of `f_a(x)=0`
   - is the number of intersections of `y=a` with the carrier graph

4. 第二问用奇点加对称直接读
   - the two roots are the same-height split around the peak singularity `x=e`
   - the right side opens farther than the left side
   - so the product is forced outward:
     `x_1 x_2 > e^2`

5. 第三问用奇点爆破
   - `f_a(x)<=0` for all `x>0`
     means `a` must stay above the peak `1 + 1/e`
   - `f_a(x)>=0` for all `x>0`
     is killed by the left-end singularity because the carrier drops to `-infinity` as `x -> 0+`

## What Was Actually Taught

The live teaching sequence was not:

- take derivative first
- classify parameters
- then backfill skill names

The live teaching sequence was:

### Step 1: 先赋值

From

```text
x + ln x - a x = 0
```

do not stay on the original shell.

Immediately solve for the parameter:

```text
a = 1 + (ln x)/x
```

This is the first kill.

The problem is no longer "analyze f_a directly."

It becomes:

- study the carrier `y = 1 + (ln x)/x`
- read all three questions from one graph

This is:

- relation before object
- carrier replacement
- direct readout preparation

### Step 2: 画图

Do not demand a perfect software-grade graph first.

Force the control skeleton out:

- `x -> 0+` gives the left-end drop to `-infinity`
- `x -> +infinity` gives the right tail approaching `1`
- `x = 1` gives the easy anchor point `y = 1`
- the carrier reaches its peak at `x = e`
- the peak height is `1 + 1/e`

So the curve:

- rises from `-infinity`
- passes through `(1, 1)`
- peaks at `(e, 1 + 1/e)`
- then falls
- and approaches `1` from above

This is:

- picture
- limit boundary
- anchor readout

### Step 3: 第一问直接读横线截点

After the graph exists, do not reopen ordinary derivation.

Read:

- the number of roots of `f_a(x)=0`
- as the number of intersections of the horizontal line `y=a`
- with the carrier `y = 1 + (ln x)/x`

So:

- `a < 1` -> one intersection
- `a = 1` -> one intersection at `x = 1`
- `1 < a < 1 + 1/e` -> two intersections
- `a = 1 + 1/e` -> one double-touch at the peak
- `a > 1 + 1/e` -> no intersection

This is:

- picture + readout

not ordinary casework regrowth.

### Step 4: 第二问用奇点加对称直接读

If there are two distinct roots `x_1 < x_2`, then they are the two same-height points cut by one horizontal line below the peak.

The peak singular point is:

```text
x = e
```

This is the control center.

The important teaching signal was:

- do not reopen a heavy equation route
- do not immediately introduce fresh substitution machinery
- first read the two roots as a same-height split around the singular peak

Then use symmetry in the honest sense:

- they are not rigidly additive-symmetric around `e`
- the right side opens farther than the left side
- so the multiplicative balance point is broken outward on the right

Therefore the product cannot stay at `e^2`.

It must satisfy:

```text
x_1 x_2 > e^2
```

This is the core simple combo:

- 奇点
- 对称

That pair is enough to kill the second question.

### Step 5: 第三问用峰值奇点和左端奇点爆破

For

```text
f_a(x) <= 0  for all x>0
```

after the parameter assignment, this means:

```text
a >= 1 + (ln x)/x  for all x>0
```

So `a` must sit above the entire carrier.

You do not need broad casework.

Explode the upper singular point directly:

- the peak is `1 + 1/e`

Hence:

```text
a >= 1 + 1/e
```

For

```text
f_a(x) >= 0  for all x>0
```

the rewritten condition is:

```text
a <= 1 + (ln x)/x  for all x>0
```

Now explode the left-end singularity:

- as `x -> 0+`, the carrier goes to `-infinity`

So no fixed real `a` can stay below the whole carrier.

Hence no such `a` exists.

This is:

- peak singularity readout
- left-end singularity explosion

## Why This Sample Matters

This sample teaches a very short transferable kill-chain:

1. 赋值换对象
2. 图像定骨架
3. 峰值做母控制点
4. 同高双点 -> 奇点加对称
5. 全局真假 -> 峰值或端点奇点直接爆破

The point is not just that this solves one gaokao problem.

The point is that later problems should remember:

- do not stay on the original function shell
- do not default to derivative-first ordinary narration
- a graph skeleton plus one singular point can unify many questions at once
- singularity plus symmetry can be a full local combo, not a slogan pair

## Non-Negotiable Reminder

If a later solve does this instead:

- first run a standard derivative route
- then attach `projection` or another broad name afterward

that is regression.

The taught behavior is:

- skill first
- carrier first
- graph first when the assigned carrier is clearer than the original shell
- singularity + symmetry or singularity + limit should directly author the next move

## Short Version

The gaokao teaching signal was:

先赋值，
再画图，
再抓峰值奇点，
第二问用奇点加对称直接读，
第三问用峰值和端点奇点直接爆破。
