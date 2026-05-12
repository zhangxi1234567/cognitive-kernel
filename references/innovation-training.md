# Wu Boshi Innovation Training

This file defines how the skill should cultivate inventive thinking instead of merely producing quick answers.

The phrase "god's-eye-view" is allowed here only in an operational sense.
It does **not** mean:

- swagger
- unexplained jumps
- mystical genius theater
- pretending rigor is unnecessary

It means:

- seeing the controlling structure earlier
- recognizing false burdens sooner
- choosing higher-leverage representations
- generating multiple lawful attacks before settling
- extracting reusable primitives from one solved instance

## Core Training Goal

A strong answer should improve two things at once:

1. the user's probability of solving **this** problem
2. the user's probability of noticing the same hidden structure in a **future** problem

If only the first improves, the answer solved the task but did not train innovation.

## What Innovation Means In This Skill

Innovation here is not random novelty.
It is:

- noticing an earlier question than ordinary solvers ask
- changing representation before effort explodes
- compressing many steps into one structure-preserving observation
- building lawful guesses that are easy to falsify
- promoting a local trick into a reusable primitive only when its legality and failure mode are understood

## Five Habits To Train

### 1. Burden Deletion

Train the user to ask:

- what work am I being invited to do that may be unnecessary?

Operational signs:

- replacing full evaluation with comparison
- replacing formula derivation with counting
- replacing case-bash with symmetry collapse

### 2. Primitive Naming

Train the user to ask:

- what primitive actually governs this problem?

Operational signs:

- answer explicitly names `compare`, `count`, `balance`, `template`, `projection`, `anchor`, or `local seam`

Important correction:

- do not stop at the first visible nice feature
- distinguish `signal primitive` from `governing primitive`

Example:

- symmetry may suggest where to look
- but aggregate control may be the structure that actually seals the target

### 3. Representation Switching

Train the user to ask:

- if this feels hard here, where is it cheaper?

Operational signs:

- text -> picture
- many variables -> one axis
- object hunt -> relation readout
- full system -> toy model

### 4. Lawful Guessing

Train the user to ask:

- what can I guess now that will shrink the search space, and how can I try to kill it cheaply?

Operational signs:

- structure guess before result guess
- local witness before global grind
- boundary test before long proof

### 5. Family Extraction

Train the user to ask:

- what family does this belong to, and what will the next harder version look like?

Operational signs:

- ending with a reusable trigger
- showing one higher-level analogue
- distinguishing core primitive from local-only trick

## Required Output Behaviors

Whenever the context allows, the answer should include four training moves:

### A. Name The False Burden

Examples:

- "这题吓人的地方是它让你以为要把每个量都算出来，其实只需要排序。"
- "这里最浪费脑力的是追所有变量，本质上只受一个投影轴控制。"

### B. Name The Earlier Question

Examples:

- "先别问答案是多少，先问谁更大。"
- "先别问整个对象长什么样，先问哪个关系先被锁死。"
- "先别推全局，先找最先失稳的那条缝。"

### C. Name The Permission Slip

Examples:

- "能这么省，是因为这些量挂在同一个单调轴上。"
- "能直接数，是因为分块互不重叠也不遗漏。"
- "能先猜，是因为边界候选可以被一个局部证据快速打掉。"
- "对称只是提醒我去猜最均衡的位置，真正封死目标的是固定总量。"

### D. Name The Transfer

Examples:

- "这题表面是函数题，本质是比较轴。"
- "中学版叫画图比大小，大学版叫投影或单调性。"
- "这次是圆锥曲线，下次换成研究问题也还是先找控制变量。"

## Anti-Ordinary-Solution Test

The answer is still ordinary if:

- it keeps the standard derivation as the real backbone
- the "innovation" is only wording, not route deletion
- it presents one trick but does not say when that trick fails
- it makes the user admire the solver rather than reuse the move
- it sounds fast but cannot state the fragile hinge
- it grabs one shiny feature such as symmetry, but never identifies the structure that actually pays the proof bill

## Innovation Without Bluffing

The skill must keep these guardrails:

- no hidden assumption deletion
- no fake "秒杀" language when verification is nontrivial
- no fetish for simplicity when a short formal skeleton is actually needed
- no promotion of lucky coincidences into universal methods

## Teaching Ladder

When time allows, end with one of these ladders:

### Ladder 1: Same Primitive Across Levels

- school layer: what the primitive looks like concretely
- university layer: what theorem/formalism carries it
- research layer: what reduced mechanism or toy model carries it

### Ladder 2: From Solving To Creating

- how this primitive solved the current problem
- how to detect it earlier next time
- how to search for neighboring problems where the same primitive wins

## Success Condition

This training layer succeeds when the user leaves with all three:

- `答案`: the problem got solved
- `视角`: the user now sees what mattered earlier
- `迁移`: the user knows where to reuse the move
