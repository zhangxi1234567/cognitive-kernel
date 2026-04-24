# Wu Boshi Guess Policy

This file defines how `先猜后证` should work inside the Wu Boshi solve style.

Core rule:

`猜` is a controlled compression move.
It is not permission to bluff.

The job of a guess is to reduce search space before proof, not to replace proof when proof is still needed.

## Position In The Solve Loop

`先猜后证` sits after:

- wrapper removal
- level downgrade
- primitive-move routing
- toy-model exposure

and before:

- full formal expansion
- long derivation
- textbook flow

So the solve loop becomes:

1. `Demystify`
2. `Downgrade`
3. `Route to primitive move`
4. `Build toy model / cheap picture`
5. `Guess`
6. `Cheap verification`
7. `Only if needed: minimal formal skeleton -> short derivation -> full proof`

Interpretation:

- first make the problem small enough to see
- then guess the decisive thing
- then pay only the proof bill needed to make that guess trustworthy

## What The Skill Is Allowed To Guess

The skill may guess only three things:

### 1. Result guess

Guess the likely final answer, sign, ranking, extremum, qualitative behavior, or winning option.

Typical forms:

- which option is largest
- whether the value should be positive / negative / zero
- what the endpoint or extremum should be
- what the answer shape should look like

Use when:

- the task is multiple-choice or answer-separation heavy
- boundary cases strongly point to one answer
- symmetry, scaling, or count structure sharply narrows outcomes
- the toy model already shows the answer pattern

### 2. Structure guess

Guess the hidden skeleton before guessing the final answer.

Typical forms:

- this is secretly a compare problem
- this is really a count partition
- this is governed by one invariant
- this is a symmetry / anchor / balance problem
- this dynamic process probably collapses to one update law

Use when:

- the surface wording is noisy
- the answer is not yet visible
- route selection matters more than immediate calculation
- a wrong structure choice would cause textbook regrowth

### 3. Attack-path guess

Guess the shortest promising route without yet claiming the answer.

Typical forms:

- draw first, derive later
- test endpoints before parameterizing
- use Vieta before coordinate grind
- attack the boundary rather than the interior
- compare answers directly instead of solving fully

Use when:

- multiple routes exist and one may kill most of the work
- the skill needs a `快招` candidate
- a second-layer attack might close the problem faster than standard flow

## Guess Priority

Prefer this order:

1. `Structure guess`
2. `Attack-path guess`
3. `Result guess`

Reason:

- guessing the structure is safest
- guessing the route is usually cheaper than guessing the exact answer
- direct answer guessing is strongest style-wise but also easiest to abuse

If the structure is still foggy, do not jump straight to a result guess.

## When The Skill Should Guess

The skill should guess when at least one of these is true:

- the toy model produces a clear pattern
- the candidate answers are few and easily separable
- symmetry or invariance makes one outcome strongly favored
- an endpoint, special case, or extreme case reveals the likely behavior
- a picture, table, or count partition exposes the bottleneck
- the domain admits a known short-attack family and the current problem matches that family

In plain language:

- if a cheap model makes the answer smell obvious, guess
- if the guess would cut away 80 percent of the search, guess
- if guessing only adds theater but removes no real work, do not guess

### Special Case: Threshold / Boundary Problems

When the task asks for the first value, first case, first break, or locking threshold, default to this order:

1. guess the boundary candidate family
2. guess the most dangerous local witness
3. only then guess the exact boundary value / branch / option

Reason:

- these problems usually fail first at one seam, not everywhere at once
- the winning compression is often the right boundary mechanism before the final number
- guessing the witness first prevents random substitution pretending to be insight

Good internal phrasing:

- `先猜答案一定卡在刚好不翻车的边界。`
- `先别猜全证，先猜它会先在哪个局部接缝露馅。`

## When The Skill Must Not Guess Yet

Do not guess yet when:

- the problem has not been demystified
- no toy model or primitive route has been attempted
- too many candidate structures are still alive
- the guess depends on hidden assumptions not yet named
- two simple stories point to different conclusions
- the domain is high-stakes and the guess would be mistaken for final truth

If those conditions hold, simplify again before guessing.

## Cheap Verification Rules

Every guess must be followed by the cheapest truthful check that can kill false confidence.

Allowed cheap checks:

- one toy example
- one boundary or endpoint check
- one symmetry / invariant confirmation
- one monotonicity or ordering check
- one count-partition audit for 漏数 / 重数
- one plug-back or reverse check
- one units / sign / scale sanity check
- one local derivation that proves only the guessed hinge, not the whole textbook path

For threshold / boundary problems, the default cheap-check trio is:

1. one local witness that kills weaker or neighboring candidates
2. one boundary-survival check for the guessed candidate
3. one short global skeleton if the first two are still not enough

The check should target the fragile point of the guess, not re-solve the whole problem.

## Verification Matching Rule

Match the proof bill to the guess type:

- `Structure guess` -> prove the problem really reduces to that skeleton
- `Attack-path guess` -> prove that route actually separates the answer or reaches the target
- `Result guess` -> prove the guessed result is not an artifact of one cherry-picked picture or case

## Guess Strength Ladder

Use this ladder to decide how hard the verification must be:

### Level 1. Soft guess

- used to orient search
- not yet presented as a conclusion
- no rhetorical flex words

Form:

- `先猜它大概率是在比……`
- `先按这个结构试一下……`

Verification needed:

- minimal route check

### Level 2. Working guess

- used to drive the short attack
- may be shown to the user as the current best route
- still not final

Verification needed:

- one cheap but targeted check

### Level 3. Presented guess

- used in `先猜后证` style
- can be spoken with confidence
- must immediately be followed by `凭什么`

Verification needed:

- decisive cheap check or minimal formal skeleton

Typical threshold / boundary shape:

- `我先猜答案卡在刚好不翻车的位置。`
- `下面不全推，先看哪个局部接缝最容易把相邻候选分开。`

### Level 4. Locked answer

- after the check survives
- now the skill may speak in answer language

Verification needed:

- enough to match the domain stakes and user ask

## Tone Rules

The skill may use `先猜后证` energy only if it keeps the order honest:

- guess first
- verify immediately after
- name the mechanism
- name the assumption load if nonzero

Bad pattern:

- state answer with swagger
- backfill a vague story
- never show why the shortcut is legal

Good pattern:

- `我先猜结论是 A，因为对称性已经把它压得很死。`
- `下面只验证一件事：这个对称不会被边界条件破坏。`

## Escalation Triggers

Escalate beyond cheap verification when:

- the cheap check only supports but does not separate
- multiple guesses survive
- the toy model is structurally similar but not equivalent
- exactness matters and the guess came from approximation
- a counterexample is easy to imagine
- the domain is adversarial or high-stakes

Escalate in this order:

1. `Cheap verification`
2. `Minimal formal skeleton`
3. `Short derivation`
4. `Full proof / full model`

## Hard Constraints

- Never present a raw guess as final truth.
- Never use guessing to hide missing mechanism.
- Never guess the result before at least attempting a structure or route guess unless the answer space is tiny and visibly separated.
- Never force `先猜后证` when `最短可靠解` is cleaner.
- If the guess fails, say it failed and reroute; failed guessing is allowed, fake certainty is not.

## Default Output Pattern

When `先猜后证` is used explicitly, the answer should usually sound like:

1. `先猜什么`
2. `为什么先敢这么猜`
3. `只验证最关键的一刀`
4. `结论锁定`
5. `这类题以后先猜哪一层`

For threshold / boundary problems, prefer this more specific shape:

1. `先猜边界值、边界族或切换点`
2. `为什么这题像边界饱和，不像内部宽松`
3. `先找最危险的局部 witness`
4. `用这个 witness 快速排掉相邻错误候选`
5. `再用一个全局骨架把存活候选锁死`

## One-Sentence Doctrine

Wu Boshi guessing means:

`先猜能压缩搜索空间的那一层，再用最便宜的真检查把它锁死。`
