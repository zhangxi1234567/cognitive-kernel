# Wu Boshi Seed Validation from Public Exam Sources

Role note:

- this file belongs to the `source / seed / evidence layer`
- gaokao-style items are validation seeds, not the method boundary
- keep the public exam material, but do not read it as "the skill only serves exam math"

This file records a first public-answer validation pass using public exam-style math questions.

Purpose:

- check whether the skill can actually solve problems that match this public seed style
- verify that the protocol produces correct answers, not just good rhetoric
- note where the source-backed protocol still needs tightening

## Test 1: 2024 全国甲卷文科数学 概率题

### Paraphrased problem

Four people `甲、乙、丙、丁` stand in a row.
Find the probability that:

- `丙` is not first
- and either `甲` or `乙` is last

### Public answer source

- https://www.jhgk.cn/upload/file/20240616/1718501141110021511.pdf

Reference answer:

- `B`
- `1/3`

### Wu Boshi-style solve

`本质`

This is not a hard probability problem.
It is just counting good rows out of all rows.

`壳为什么唬人`

The wording mixes two conditions, so it looks like you need formulas.
But the structure is tiny: only 4 people, so just count.

`最早诚实直觉层 / 低复杂度层 / 直觉版`

Treat it like arranging 4 cards.

All rows:

- `4! = 24`

Good rows:

- last seat must be `甲` or `乙`: `2` choices
- first seat cannot be `丙`
- after fixing the last seat, the first seat has `2` valid choices
- the middle two seats then arrange in `2` ways

So good rows:

- `2 * 2 * 2 = 8`

Probability:

- `8 / 24 = 1/3`

`下次记什么`

Tiny probability arrangements are often just counting rows, not probability tricks.

### Result

- Skill answer: `1/3`
- Public answer: `1/3`
- Verdict: `PASS`

### What this tests

- count-before-formula
- remove intimidation
- low cognitive load

## Test 2: 2023 全国甲卷 计数题

### Paraphrased problem

There are `5` volunteers.
On Saturday and Sunday, each day `2` people are assigned.
Each volunteer can participate on at most one day, except the condition asks for arrangements where exactly `1` person serves on both days.

Find the number of different arrangements.

### Public answer source

- https://tiku.baidu.com/paperdetail/c630887addccda38376baf2b

Reference answer shown on page:

- `B`
- `60`

### Wu Boshi-style solve

`本质`

This is not a scary arrangement problem.
It is: choose the repeated person, then distribute the remaining slots.

`壳为什么唬人`

The problem sounds like a weekend scheduling story, but the skeleton is just:

- one duplicated person
- three remaining single-use slots

`最早诚实直觉层 / 低复杂度层 / 直觉版`

Think of the schedule as four seats:

- Saturday seat 1
- Saturday seat 2
- Sunday seat 1
- Sunday seat 2

Exactly one person appears twice.

Step 1:

- choose the repeated person: `5` ways

Step 2:

- choose which one of the remaining `4` people is excluded: `4` ways

Step 3:

- from the remaining `3` people, choose who joins Saturday and who joins Sunday
- equivalently, choose the Saturday partner: `3` ways

Step 4:

- each day has two seats but partner order inside a day does not matter

So total:

- `5 * 4 * 3 = 60`

`下次记什么`

When a counting problem says “exactly one repeats,” lock the repeated object first.

### Result

- Skill answer: `60`
- Public answer: `60`
- Verdict: `PASS`

### What this tests

- prototype compression
- choose-the-repeater-first tactic
- anti-overformal behavior

## Test 3: 2023 全国甲卷 统计检验题（第 19 题第 2 问）

### Paraphrased problem

Two groups of mice are observed:

- control group
- experimental group

The question asks whether the medicine can be considered related to reduced ozone concentration, using the median-based `2 x 2` contingency-table method shown in the problem.

### Public answer source

- https://tiku.baidu.com/paperdetail/c630887addccda38376baf2b

Reference answer shown on page:

- `能`

### Wu Boshi-style solve

`本质`

This is not really a scary statistics proof.
It is: draw a line at the median and see whether the two groups fall differently on the two sides.

`壳为什么唬人`

The problem wraps a very simple idea in statistical wording.
But the core is just:

- find the middle cutoff
- compare how the two groups are distributed around it

`最早诚实直觉层 / 低复杂度层 / 直觉版`

Put all `40` measurements together and sort them.
The median is the average of the `20`th and `21`st values.

Using the public data from the problem:

- 20th = `23.2`
- 21st = `23.6`
- median `m = 23.4`

Now count below / at-or-above `23.4`:

- control: `6` below, `14` at-or-above
- experiment: `14` below, `6` at-or-above

This already shows a strong shift.

If we compute the `2 x 2` chi-square value:

- `chi^2 = 6.4`

That exceeds the standard `0.05` threshold `3.841`, so the association is supported.

`下次记什么`

A lot of statistics questions are really “cut, count, compare,” not “memorize scary formulas.”

### Result

- Skill answer: `能`
- Public answer: `能`
- Verdict: `PASS`

### What this tests

- balance/count route in a more advanced-looking setting
- downgrade from statistics jargon to cut-and-count structure
- ability to add minimal formal verification after intuition

## Evidence-Layer Verdict

Current result:

- `3 / 3` public-answer checks passed

What worked well:

- the method naturally prefers count / compare / toy-model routes
- the answer style can stay simple without becoming false
- advanced-looking wording can still be reduced honestly inside this seed set

Remaining risks:

- sparse public corpus for some branded families means the evidence layer is still stronger on public wrappers than on hidden full-course contents
- direct testing so far is stronger on math seeds than on physics/chemistry seeds
- future validation should include:
  - one geometry / conics item
  - one function/compression-list style item
  - one physics item
  - one chemistry item

Boundary reminder:

- these passes only show that the method survives public exam-style seeds cleanly
- they do not imply the method is restricted to gaokao, school, or one academic stage
