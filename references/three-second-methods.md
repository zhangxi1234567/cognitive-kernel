# Wu Boshi Three-Second Methods

This file stores reusable fast-attack patterns extracted from answer-keyed seed problems.

## Universal-Methods Rule

The patterns in this file are not exam-only tricks.

Current seeds may lean exam math because that corpus is public and dense, but every promoted method here should be described so it can transfer:

- downward to earlier intuition
- upward to more formal work
- sideways to other mathematical and non-mathematical domains

Each entry should prefer:

- low computation
- low notation load
- multiple distinct short routes
- easy transfer to future problems

## Primitive Design Rule

A fast route should only be promoted to a reusable primitive if it passes all of these:

- it works on at least 3 non-identical problems
- it can be stated without mentioning one exam question
- it has one clear legality mechanism
- it has one clear failure mode

If it fails that test, keep it as a `seed tactic`, not a primitive.

Also keep it as a seed tactic if it cannot be explained in a level-flexible way.

## Focus Summary

- `vector difference readout`
  - generalized move: when two effects combine linearly, read the missing vector before doing formula work
- `common-value parameter compression`
  - generalized move: collapse many equal expressions into one hidden control parameter
- `container-to-cross-section`
  - generalized move: reduce a symmetric 3D packing / shape problem to its controlling 2D section
- `matching-instead-of-probability`
  - generalized move: recode story-probability into structure-counting on a matching space
- `permutation recognition`
  - generalized move: whenever every row/column/slot is used exactly once, test if the whole thing is just a permutation

These summaries should be read as universal primitives whose current seeds happen to come from one public corpus.

## Primitive Design Rule

Do not stop at the local trick.
For each fast route, extract the deeper reusable move:

- what structure to recognize
- what quantity or relation is actually preserved
- what compression move kills the fake complexity
- what nearby problem families should now become easier
- what failure signal says the shortcut is no longer safe
- how the same move would look at earlier and later levels of formality

## 1. Vector Difference Readout

### Seed problem

2025 新高考 I 卷 第6题（帆船真风）

### Public answer

- `A. 轻风`

### Fast routes

#### Route A: Coordinate difference

- 真风 = 地面速度 - 相对空气速度
- 图上直接做坐标差，得到向量 `(-2, 2)`
- 长度 `2√2 < 3.3`
- 所以是 `轻风`

#### Route B: Parallelogram completion

- 把两个速度向量首尾拼接
- 真风就是闭合缺口
- 缺口长度肉眼落在 `3.3` 以下

#### Route C: Machine language

- `船速 = 风 + 自身修正`
- 所以 `风 = 船速 - 修正`
- 本质是反向拆机器，不是算大题

### Transfer rule

When two effects combine linearly, try difference geometry before formula grinding.

### Recognition cues

- two arrows / velocities / displacements / forces combine
- one quantity is "true / net / actual" and others are relative or component effects
- linear combination is more natural than scalar equation solving

### Invariant

- vector addition law
- linear closure of the combined effect

### Failure mode

- nonlinear interaction
- hidden rotation / non-Euclidean geometry
- option spacing too tight for pure visual readout

### Generalized primitive

- primitive name: `Composed-motion -> missing-vector recovery`
- recognition cues:
  - two motions / influences add to make one observed result
  - the problem gives two of `{source, correction, output}` and asks for the third
  - arrows, drift, wind/current, relative velocity, force synthesis, displacement composition
- invariant:
  - the composition law is additive, so the unknown is a vector gap, not a new mystery quantity
- reusable move:
  - redraw the system as a triangle or parallelogram
  - solve by “close the gap” instead of by component-heavy setup
  - compare direction and rough length before exact arithmetic
- transfer targets:
  - relative velocity
  - force/resultant problems
  - displacement chains
  - any linear effect-composition picture
- failure mode:
  - if composition is not linear or the frame is changing in a nonlinear way, the gap picture may mislead

## 2. Common-Value Parameter Compression

### Seed problem

2025 新高考 I 卷 第8题（对数公共值）

### Public answer

- `B`

### Fast routes

#### Route A: Common parameter

- 设公共值为 `k`
- 立刻得到：
  - `x = 2^(k+1)`
  - `y = 3^k`
  - `z = 5^(k-2)`
- 取标志点 `k=-1,2,5` 试打选项
- 快速排除错误项

#### Route B: Growth-family comparison

- 这不是解方程题，是看三种底数指数族如何相对变化
- 先把它们都写成“底数的 k 次”
- 再看哪个选项不可能在全部 k 上成立

### Transfer rule

When several ugly equalities secretly share one common value, compress them into one parameter immediately.

### Recognition cues

- chained equal signs
- different expressions all equal the same thing
- direct solving fans out into many variables

### Invariant

- one hidden degree of freedom controls all expressions

### Failure mode

- domain restrictions hidden by reparameterization
- local equality mistaken for global equality

### Generalized primitive

- primitive name: `Shared-output -> one-parameter family`
- recognition cues:
  - several expressions are all equal to the same thing
  - direct elimination looks ugly, but each term can be solved cleanly once the common value is named
  - answer choices ask for order, truth across all cases, or impossible statements rather than an exact triple
- invariant:
  - all variables live on one hidden track; the common value is the real degree of freedom
- reusable move:
  - name the shared value first
  - rewrite every variable as a function of one parameter
  - replace simultaneous solving with “family comparison” or “test landmark parameter values”
- transfer targets:
  - log equalities
  - trigonometric common-value systems
  - symmetric algebraic conditions
  - any multi-variable condition with one latent freedom
- failure mode:
  - if extra independent constraints remain after compression, one parameter is not the whole story

## 3. Hidden 3-4-5 Recognition

### Seed problem

2025 新高考 II 卷 第6题（抛物线，求 `|AF|`）

### Public answer

- `5`

### Fast routes

#### Route A: Focus definition

- 先认焦点
- 再由点到焦点 = 点到准线
- 很快锁出一个 `3-4-5`

#### Route B: Geometry-first

- 先不进抛物线公式
- 先看这个点到焦点和到准线的距离关系
- 结构一出来，就是勾股

### Transfer rule

When a conic problem hides a clean integer length, search for a small triangle before expanding equations.

### Recognition cues

- conic / geometry data hint at focal distance and simple coordinates
- clean small integer lengths appear

### Invariant

- Pythagorean structure

### Failure mode

- lucky-number coincidence
- not stable enough to promote as a universal primitive yet

## 4. Container -> Cross-Section

### Seed problem

2025 新高考 II 卷 第14题（圆柱内两等球）

### Public answer

- `5/2`

### Fast routes

#### Route A: Cross-section flattening

- 三维别硬做
- 直接切成截面
- 两球心距离 = `2r`
- 横向、纵向关系直接勾股

#### Route B: Packing picture

- 这不是立体几何炫技题
- 本质就是“两个圆在长方形截面里怎么挤”

### Transfer rule

Whenever a 3D packing problem has symmetry, cut it to the controlling 2D section first.

### Recognition cues

- symmetric 3D object
- distances controlled by one planar slice
- multiple equal spheres / cylinders / cones

### Invariant

- the controlling contact geometry lives in one section

### Failure mode

- the selected section is not actually the controlling one
- asymmetry makes the 2D slice incomplete

### Generalized primitive

- primitive name: `Spatial container -> controlling slice`
- recognition cues:
  - 3D packing / tangency / distance problem with strong symmetry
  - the real constraint is between centers, radii, and walls
  - the picture feels “round objects inside a regular shell”
- invariant:
  - the decisive distances are preserved in the symmetry section through the relevant centers
- reusable move:
  - identify the slice that contains all critical centers and contact directions
  - flatten the solid to a 2D circle-in-container problem
  - pay the geometry bill there, usually with one Pythagorean closure
- transfer targets:
  - spheres in cylinders, cones, boxes
  - tangent-ball arrangements
  - rotationally symmetric solids
  - shortest-distance-in-solid problems
- failure mode:
  - if the extremal relation does not lie in one controlling plane, the cross-section shortcut can drop a degree of freedom

## 5. Matching Instead Of Probability

### Seed problem

2024 新高考 I 卷 第14题（卡片比赛）

### Public answer

- `1/2`

### Fast routes

#### Route A: Permutation view

- 这不是概率过程题
- 本质是 4 张对 4 张的匹配
- 全集就是 `4!`
- 有利情况数一数，再比

#### Route B: Lock the worst card

- 先锁死最弱卡的输赢结构
- 再看其余牌如何补位
- 结构比逐局模拟轻

#### Route C: Dominance partition

- 按“必胜 / 必败 / 互咬”分层
- 再做小计数

### Transfer rule

A lot of probability stories are really matching-count problems in disguise.

### Recognition cues

- story probability with small finite actors
- pairings, assignments, matchups, schedules

### Invariant

- uniform counting space under a matching or permutation model

### Failure mode

- nonuniform probability space
- hidden sequential dependence matters

### Generalized primitive

- primitive name: `Random process story -> structural matching count`
- recognition cues:
  - the probability experiment is equivalent to pairing, assignment, seating, or matchup
  - outcomes are finite and symmetric
  - simulation language hides that every global outcome is just one matching in a uniform sample space
- invariant:
  - probability = favorable matchings / total matchings once the random mechanism is flattened correctly
- reusable move:
  - stop following the story chronologically
  - rewrite the experiment as a static matching object
  - count structure classes instead of branch-by-branch probability trees
- transfer targets:
  - card matchups
  - random assignments
  - derangements / seating / pairing
  - tournament-style comparison experiments
- failure mode:
  - if outcomes are not equally likely after flattening, raw matching counts need weighting

## 6. Grid Selection -> Permutation

### Seed problem

2024 新高考 II 卷 第14题第一空（4×4方格）

### Public answer

- `24`

### Fast routes

#### Route A: `4!`

- 每行选 1 格、每列选 1 格
- 本质就是列的一个排列
- 所以直接 `4! = 24`

#### Route B: Rook placement

- 这不是方格题，是“车互不攻击”模型
- 一眼就是排列数

### Transfer rule

Whenever every row and every column must be used exactly once, check if the whole thing is just a permutation.

### Recognition cues

- exactly one per row and one per column
- no attack / no conflict placement

### Invariant

- bijection between row choices and column permutation

### Failure mode

- extra geometric or weighting constraints change the simple permutation count

### Generalized primitive

- primitive name: `One-per-line constraints -> permutation encoding`
- recognition cues:
  - each row chooses exactly one column, and each column is used exactly once
  - “nonattacking rooks”, Latin-style placement, bijection, assignment table
  - the object looks geometric, but the rule is really “choose a bijection”
- invariant:
  - legal configurations are in one-to-one correspondence with permutations
- reusable move:
  - replace the board by a function `row -> column`
  - count or analyze the induced permutation instead of the picture
  - if extra conditions appear, treat them as permutation filters, not as new geometry
- transfer targets:
  - rook placement
  - assignment problems
  - permutation matrices
  - row-column selection puzzles
- failure mode:
  - if some rows/columns allow multiple picks or forbidden structure breaks bijection, plain `n!` recognition is incomplete

## Focus Summary: The Reusable Moves Behind The Local Tricks

### 1. Vector-difference

- local trick: subtract two arrows
- reusable move:
  - when a system is built by linear composition, recover the unknown by finding the missing side of the composition polygon

### 2. Common-value parameter compression

- local trick: set everything equal to `k`
- reusable move:
  - when many variables are chained by one shared output, collapse the whole system to one latent degree of freedom

### 3. Container-to-cross-section

- local trick: cut the cylinder and treat spheres as circles
- reusable move:
  - when a high-dimensional configuration is controlled by one symmetry slice, solve in the slice and inherit the answer back

### 4. Matching-instead-of-probability

- local trick: turn the card game into a permutation count
- reusable move:
  - when the random narrative only generates uniform global matchings, replace probability flow with static combinatorial structure

### 5. Permutation recognition

- local trick: `4 x 4` row-column choice is `4!`
- reusable move:
  - when constraints force a bijection, encode the whole object as a permutation before doing anything else

## 7. Compare Without Calculating

### Seed problem

2023 天津卷 第3题（比较 `a,b,c`）

### Public answer

- `b > a > c`

### Fast routes

#### Route A: Same-base / same-exponent monotonicity

- `1.01^0.6 > 1.01^0.5`
- so `b>a`
- and `1.01^0.5 > 1 > 0.6^0.5`
- so `a>c`

#### Route B: Log / monotone recode

- 全部放到“谁大于 1，谁小于 1”这条轴上
- 再看指数增减

### Transfer rule

In compare-size problems, first ask:
is this a monotonicity problem wearing a computation costume?

### Recognition cues

- ugly exponents / roots / logs
- ordering question, not exact value question

### Invariant

- monotonicity of the relevant base / exponent / function

### Failure mode

- comparison axis not shared
- hidden domain switch changes monotonicity

## 8. Dot Product Range By Projection

### Seed problem

2022 北京卷 第10题（动点与点积范围）

### Public answer

- `[-4,6]`

### Fast routes

#### Route A: Projection

- 点积不是神秘量
- 本质就是“一个向量在另一个方向上的投影再乘长度”
- 所以范围题先看投影最远和最近

#### Route B: Polarization identity

- 把点积改写成长度组合
- 再用圆/轨迹约束看最大最小

### Transfer rule

Dot-product range problems are often projection or length-combination problems, not brute vector multiplication problems.

### Recognition cues

- dot product
- moving point
- range / max / min

### Invariant

- projection meaning of dot product
- length-combination identities

### Failure mode

- projection picture alone does not pin the endpoint geometry
- still needs a minimal range skeleton
