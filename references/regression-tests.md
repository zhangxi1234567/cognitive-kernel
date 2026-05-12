# Wu Boshi Regression Tests

This file records regression-style validation of the current skill behavior.

Each test should capture:

- problem family
- chosen attack
- whether it drifted toward textbook flow
- whether it used `补一句凭什么` correctly
- whether the final explanation still felt Wu Boshi enough
- whether it truly killed the shell or only shortened the standard route

## Universal-Regression Rule

These regression tests validate behavior of universal primitives.

The current file mixes:

- school-style math seeds
- statistics / applied reasoning seeds
- structural validation tests

That mixture is intentional.

Future regression additions should continue to widen coverage across:

- earlier and later academic layers
- different mathematical domains
- cross-domain reasoning problems

without redefining the core primitives each time.

## New Regression Dimension: Shell Kill Strength

Useful future regression dimensions include:

- `shell-kill: strong`
- `shell-kill: partial`
- `shell-kill: fake`

Meaning:

- `strong`: the shell died early and the route changed
- `partial`: the shell was weakened but the route still leaned standard
- `fake`: the answer only paraphrased the standard route

## New Regression Dimension: Low-Floor Executability

Useful future regression dimensions include:

- `low-floor: pass`
- `low-floor: partial`
- `low-floor: fail`

Meaning:

- `pass`: the claimed lower layer can execute the decisive hinge
- `partial`: the lower layer reveals the route, but one imported formal seal still carries too much weight
- `fail`: the lower layer only motivates; the main route still belongs to the old harder solution

## New Regression Dimension: Mechanism Acquisition

Useful future regression dimensions include:

- `mechanism: pass`
- `mechanism: partial`
- `mechanism: fail`

Meaning:

- `pass`: the answer names the trigger, mechanism, preserved structure, and transfer rule
- `partial`: the answer shows the mechanism but leaves transfer or failure boundary under-specified
- `fail`: the answer solves the seed but teaches only a local trick or replayable route

## Test 1: Small Counting / Probability

### Problem Family

Small arrangement counting framed as probability.

### Representative Problem

`甲、乙、丙、丁四人排成一列，求“丙不在排头，且甲或乙在排尾”的概率。`

### Chosen Attack

- `Count`
- `small case / toy model`
- `good partition before probability language`

### What the skill did well

- immediately stripped the fake probability shell
- turned the task into counting good rows over total rows
- did not introduce formula theater

### What failed before refinement

- a fast explanation compressed one counting step too hard
- the answer said something equivalent to “排头 2 种” without first making the partition trustworthy enough for a careful student

### What fixed it

- `补一句凭什么`
- explicitly stating:
  - fix the tail first
  - then use `3! - 2!`
  - and explain why the cases do not overlap

### Regression Verdict

- correctness: `PASS`
- anti-textbook bias: `PASS`
- trustworthiness: `PASS after fix`
- Wu Boshi feel: `medium-strong`

### Takeaway

For tiny counting problems, the current skill is good if and only if it pays the trust bill on the decisive counting split.

### Shell-Kill Strength

- `strong`

## Test 2: Schedule / Combination Structure

### Problem Family

Combinatorial arrangement with exactly one repeated role.

### Representative Problem

`5名志愿者安排周六、周日服务，每天2人，恰有1人两天都参加，求不同安排数。`

### Chosen Attack

- `Template`
- `choose the repeated role first`
- `count`

### What the skill did well

- identified the repeated object as the controlling structure
- reduced a story problem to a role-allocation problem
- produced a low-load counting path

### Remaining weakness

- this family is naturally friendly to the skill
- so it does not stress-test anti-standard bias as hard as geometry or analytic problems do

### Regression Verdict

- correctness: `PASS`
- anti-textbook bias: `PASS`
- trustworthiness: `PASS`
- Wu Boshi feel: `strong`

### Takeaway

The current skill is already strong on “lock the key role first” counting problems.

### Shell-Kill Strength

- `strong`

## Test 3: Median / 2x2 Table / Statistical Framing

### Problem Family

Advanced-looking statistics problem with a simple cut-and-count core.

### Representative Problem

Two groups of mice, use the median-based `2 x 2` method to judge whether a medicine is related to reduced ozone concentration.

### Chosen Attack

- `Count`
- `Compare`
- `formal check only after intuition`

### What the skill did well

- stripped the statistical shell
- turned the problem into “cut once, then count two sides”
- preserved the formal threshold check only after the structure was clear

### Remaining weakness

- still slightly expository in tone
- could become even punchier without losing honesty

### Regression Verdict

- correctness: `PASS`
- anti-textbook bias: `PASS`
- trustworthiness: `PASS`
- Wu Boshi feel: `medium`

### Takeaway

The skill handles jargon-heavy but structurally simple problems well.

### Shell-Kill Strength

- `strong`

## Test 4: Conic / Target-Only Proof

### Problem Family

Analytic geometry where standard solutions want full coordinate recovery but the target only asks for one fixed quantity.

### Representative Problem

2023 新高考 II 卷第 21 题第 2 问:
prove the intersection point lies on the fixed line `x = -1`.

### Chosen Attack

- `Target-only proof`
- `anchor line`
- `compare the two line heights at x = -1`

### What the skill did well

- correctly refused to solve for full coordinates first
- identified that only the fixed x-coordinate matters
- used a cleaner target-first route than plain textbook flow

### What still drifted toward textbook flow

- after the initial reduction, it still fell back into a familiar algebraic skeleton:
  - parameterize line
  - derive quadratic
  - use Vieta
  - simplify

### Regression Verdict

- correctness: `PASS`
- anti-textbook bias: `partial`
- trustworthiness: `PASS`
- Wu Boshi feel: `medium-weak`

### Takeaway

This is the clearest current failure mode:

- the skill now knows how to reduce the target
- but not yet how to keep avoiding textbook flow after the first reduction

### Shell-Kill Strength

- `partial`

## Current Overall Assessment

### Strong areas

- small counting
- role-based counting
- jargon-heavy problems with simple cut / count / compare cores

### Weak areas

- analytic geometry and conic sections
- problems where the first reduction is good, but the second half still slides into standard algebra

### Most important remaining gap

The skill still needs stronger behavior around:

- searching for a second, deeper short route after the first reduction
- resisting the reflex to complete the standard derivation once algebra appears
- choosing `快招` or `最短可靠解` without imitating the standard answer shape

## Test 5: Primitive Assignment Stress Test

### Purpose

Check whether current fast routes are being promoted at the right level:

- `primitive`
- `family`
- `seed tactic`
- `local-only trick`

### Seed A: 2025 新高考 I 卷 第6题（帆船真风）

Best route:

- `coordinate difference`

Assigned primitive:

- `Vector Difference Readout`

Assigned family:

- `visual readout`

Assigned meta-principle:

- when a system is built by linear composition, recover the missing part by closing the composition gap

Stability judgment:

- `stable primitive`

Why:

- not tied to this one exam
- the legality mechanism is clear: vector addition law
- transfers to force/resultant, displacement, relative velocity, and net-effect systems

What must not be promoted:

- `肉眼看缺口长度就够了`

Verdict:

- primitive assignment: `PASS`
- seed-only caution: `PASS`

### Seed B: 2025 新高考 I 卷 第8题（公共值压缩）

Best route:

- common parameter `k`

Assigned primitive:

- `Common-Value Parameter Compression`

Assigned family:

- `structure compression`

Assigned meta-principle:

- when many visible quantities share one hidden degree of freedom, solve the hidden scalar first

Stability judgment:

- `likely stable primitive`

Why:

- shared-value systems recur often
- legality mechanism is clear: one latent control variable

What must not be promoted:

- `取几个特殊 k 打选项`

Verdict:

- primitive assignment: `PASS`
- local-only trick filtered correctly: `PASS`

### Seed C: 2025 新高考 II 卷 第14题（圆柱内两等球）

Best route:

- cut the 3D configuration into the controlling 2D section

Assigned primitive:

- `Container -> Cross-Section`

Assigned family:

- `dimension reduction`

Assigned meta-principle:

- when a high-dimensional symmetric system is controlled by one slice, solve the slice first

Stability judgment:

- `stable primitive`

Why:

- the mechanism is geometric and transferable
- not tied to lucky numbers
- appears in packing, tangency, shortest-distance, and symmetric solid problems

Verdict:

- primitive assignment: `PASS`

### Seed D: 2025 新高考 II 卷 第6题（抛物线 |AF|）

Best local route:

- focus definition -> hidden `3-4-5`

Candidate primitive:

- `small-structure landmark recognition`

Current judgment:

- `not yet a stable primitive`
- keep as `seed tactic`

Why:

- the exact `3-4-5` is too lucky
- the broader geometric idea is real, but not yet cleanly separated from the local numbers

Verdict:

- over-generalization avoided: `PASS`

## Primitive-Layer Assessment

### Stable or near-stable primitives so far

- `Vector Difference Readout`
- `Common-Value Parameter Compression`
- `Container -> Cross-Section`
- `Matching Instead Of Probability`
- `Grid Selection -> Permutation`
- `Compare Without Calculating`

### Still weak / seed-level

- `Hidden 3-4-5 Recognition`
- any route whose speed depends on lucky option spacing
- any route whose force comes mostly from one unusually clean diagram

### Main lesson

The current skill is now better at not overclaiming:

- it can preserve good local tricks
- without falsely promoting them into universal methods

## Test 6: Fast-Solve Search Engine Regression

### Purpose

Check whether the new top-level search engine actually changes behavior:

- `Demystify`
- `Downgrade`
- `Primitive scan`
- `Guess`
- `Minimal verification`
- `Second-layer attacks`
- `Fallback classification`

### Seed A: 2025 新高考 I 卷 第6题（帆船真风）

#### Public answer

- `A. 轻风`

#### Observed search path

1. `Demystify`
   - not a word problem about sailing
   - really a vector-composition problem
2. `Downgrade`
   - turn it into “one arrow plus one arrow gives the observed arrow”
3. `Primitive scan`
   - `Vector Difference Readout` fits immediately
4. `Guess`
   - structure guess: this is a missing-vector problem, not a component-equation grind
   - result guess: the missing vector is short enough to fall under the `轻风` threshold
5. `Minimal verification`
   - one coordinate-difference check gives `(-2, 2)`
   - length `2√2 < 3.3`
6. `Fallback`
   - not needed

#### Classification

- route class: `true 秒杀`

#### Why this matters

The skill did not:

- write component equations first
- introduce excess symbols
- explain sailing background

It found and verified the shortest lawful route.

#### Verdict

- top-level search behavior: `PASS`
- primitive hit: `PASS`
- style integrity: `PASS`

### Seed B: 2025 新高考 I 卷 第8题（公共值压缩）

#### Public answer

- `B`

#### Observed search path

1. `Demystify`
   - not a logarithm calculation problem
   - really a hidden one-parameter family
2. `Downgrade`
   - rewrite as “three outputs controlled by one shared knob”
3. `Primitive scan`
   - `Common-Value Parameter Compression` hits
4. `Guess`
   - structure guess: all variables live on one latent parameter `k`
   - attack-path guess: option elimination at the `k`-level will be cheaper than explicit solving
5. `Minimal verification`
   - rewrite:
     - `x = 2^(k+1)`
     - `y = 3^k`
     - `z = 5^(k-2)`
   - use landmark values / monotone comparison to eliminate bad options
6. `Fallback`
   - no full fallback, but the route still needs a tiny option-level check

#### Classification

- route class: `快招`

#### Why this matters

The skill did not fake `秒杀`.
It recognized:

- the primitive is right
- but the final elimination still depends on one small verification block

#### Verdict

- top-level search behavior: `PASS`
- primitive hit: `PASS`
- honest downgrade from `秒杀` to `快招`: `PASS`

### Seed C: 2025 新高考 II 卷 第14题（圆柱内两等球）

#### Public answer

- `5/2`

#### Observed search path

1. `Demystify`
   - not a 3D geometry grind
   - really a tangency-distance problem
2. `Downgrade`
   - reduce to the controlling 2D cross-section
3. `Primitive scan`
   - `Container -> Cross-Section` hits
4. `Guess`
   - attack-path guess: one Pythagorean closure should finish it
5. `Minimal verification`
   - sectional distances become:
     - horizontal `8 - 2r`
     - vertical `9 - 2r`
     - center distance `2r`
   - one quadratic closure yields `r = 5/2`
6. `Fallback`
   - not needed

#### Classification

- route class: `true 秒杀`

#### Why this matters

The skill did not let the problem regrow into solid geometry formalism.

#### Verdict

- top-level search behavior: `PASS`
- primitive hit: `PASS`
- anti-regrowth behavior: `PASS`

## Search-Engine Assessment

### Strong signal

The current skill can now distinguish:

- problems that truly admit a `秒杀`
- problems that only deserve `快招`

This is a major improvement over the earlier state where it tended to either:

- overexplain
- or slide back into textbook flow too early

### Remaining gap

The top-level search engine is strongest on:

- compare
- count
- cross-section / slice
- single-parameter compression

It still needs more pressure-testing on:

- hard conics
- harder function / derivative compression
- physics and chemistry problems using the new analogy layer

## Test 7: Function / Derivative Compression

### Problem Family

Function-derivative problem that invites textbook monotonicity grind but may admit structural compression.

### Representative Problem

2024 新高考 I 卷 第18题（1）:

Given
\[
f(x)=\ln\frac{x^2-x+ax+b}{(x-1)^3}
\]
with `b=0` and `f'(x)\ge 0`,
find the minimum value of `a`.

### Public answer source

- https://www.sci-open.net/index.php/ETR/article/download/1109/1230/2905

Reference answer:

- `a_min = -2`

### Chosen search path

1. `Demystify`
   - not a “differentiate and grind” problem first
   - really a monotonicity / sign-control problem
2. `Downgrade`
   - ask what expression actually controls the sign
3. `Primitive scan`
   - `Common-Value / one-control-variable compression` nearby
   - `Compare Without Calculating` nearby
   - but no true instant primitive closes it
4. `Second-layer attacks`
   - `Target-only`: only need the lower bound on `a`
   - `Boundary-condition attack`: minimum `a` should occur at a just-saturated sign condition
5. `Guess`
   - structure guess: minimum parameter likely occurs when the derivative-control expression is exactly on the boundary
6. `Minimal verification`
   - enough sign / boundary algebra is still required

### What the skill did well

- did not start with full derivative exposition
- searched for the controlling sign structure first
- recognized this is parameter-threshold logic, not raw computation

### What still resisted full fast collapse

- the exact lower bound still needs a short formal sign analysis
- there is no honest `秒杀` if we want the result to be trustworthy

### Classification

- route class: `稳招`

### Verdict

- correctness alignment with public answer: `PASS`
- anti-standard bias: `PASS`
- false-秒杀 avoided: `PASS`
- Wu Boshi feel: `medium`

### Takeaway

The skill now behaves maturely on harder derivative questions:

- it searches for boundary / threshold structure first
- but it does not pretend that every parameter-monotonicity problem has a one-glance answer

### Shell-Kill Strength

- `partial`

## Test 8: Conics / Multi-Method Pressure Test

### Problem Family

Ellipse chord / area / line interaction problem that can easily regrow into standard coordinate grind.

### Representative Problem

2025 新课标 II 卷 第16题:

Ellipse with
\[
e=\frac{\sqrt2}{2}
\]
major axis `4`.
Line through `(0,-2)` cuts the ellipse at `A,B`.
If
\[
S_{\triangle OAB}=2
\]
find `AB`.

### Public answer source

- https://pdf.hanspub.org/ces_3096033.pdf

Reference answer:

- `AB = 5`

### Chosen search path

1. `Demystify`
   - not a full conic-coordinate recovery problem
   - really a chord-length problem controlled by area and one line family
2. `Downgrade`
   - ask what quantity is truly needed: only `AB`
3. `Primitive scan`
   - `Target-only proof`
   - `Aggregate-first`
   - `Conics / fixed-line chord template`
4. `Second-layer attacks`
   - `Fixed-line chord template`
   - `Root-first, coordinates-later`
   - `Area / slope-product attack`
5. `Guess`
   - attack-path guess: area plus chord relation should close before full point recovery
6. `Minimal verification`
   - one chord/area consistency block needed

### What the skill did well

- did not start by solving both intersection points completely
- kept the target on `AB`
- recognized area as an aggregate controller
- used conics-specific second-layer attacks before allowing standard flow

### What still drifted toward textbook style

- some analytic skeleton still appears to certify the area-to-chord relation
- the problem is not a pure one-line `秒杀`

### Classification

- route class: `快招`

### Verdict

- correctness alignment with public answer: `PASS`
- anti-regrowth improvement over earlier conics test: `PASS`
- true秒杀 restraint: `PASS`
- Wu Boshi feel: `medium-strong`

### Takeaway

The new conics-specific and generalized second-layer attacks are helping:

- the skill stays on the target quantity longer
- it delays full coordinate grind
- it can now produce a fast route that is still auditably correct

### Shell-Kill Strength

- `partial-to-strong`

## Test 9: Essence-First Variable Choice Regression

### Purpose

Check whether the new `catch the essence first` rule really changes variable choice and route order.

### Representative Problem

Fixed distance `9`, same stop time, total time known at speeds:

- `s`
- `s+2`
- ask for total time at `s+1/2`

### Standard trap

The solver says:

- “the essence is fixed-distance walking time plus a shared stop”

but still immediately introduces:

- `s`
- `t`

and follows the ordinary two-equation route.

### Real target behavior

The solver should instead:

1. strip the shared stop as a common translation layer
2. identify the real moving quantity as walking time on distance `9`
3. prefer readout variables such as:
   - `A = 9/s`
   - `B = 9/(s+2)`
4. solve the relation between readouts before reconstructing the original parameters

### Pass condition

All must be true:

- the `本质` sentence names the true object as walking-time change on a fixed distance
- the shared stop time is removed before the main solve
- the first live variables are not automatically the standard `s,t`
- the route after the essence statement is visibly different from textbook parameter setup
- the explanation can say what got smaller, not only what got solved

### Fail condition

Any one of these fails the test:

- the answer says the right essence but still introduces `s,t` first out of habit
- the stop time is called common but remains a main moving part in the route
- deleting the `本质` sentence leaves the same middle skeleton
- the route is only “subtract equations, solve quadratic, back-substitute” with friendlier commentary

### Regression Verdict Labels

- `essence-first: pass`
- `essence-first: partial`
- `essence-first: fail`

### Why this matters

This test checks the hardest recent failure mode:

- the skill can often name the smaller structure correctly
- but still regress into ordinary variable choice and standard derivation

Passing this test means the essence statement is now operational rather than decorative.
