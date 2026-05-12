# Wu Boshi Bad Examples

This file contains negative examples of what the skill must avoid.

## Bad Example 1: Textbook drift

### Problem shape

A problem only asks for one fixed quantity, but the answer solves every variable.

### Bad answer

设所有点坐标，联立所有方程，分别求出每个量，再代回目标。

### What is wrong

- solves everything instead of only the target
- defaults to standard school flow without checking for a shorter lawful attack
- high cognitive load for no gain

### Repair

- ask what exact quantity is being asked for
- try target-only proof before full reconstruction

## Bad Example 2: Fake simplification

### Bad answer

这题其实很简单，直接数就行，答案是 8。

### What is wrong

- the tone says “simple”
- but the mechanism is hidden
- a careful student immediately asks “为什么这样数不会漏？”

### Repair

- add one line naming the partition or counting principle

## Bad Example 3: Fake 秒杀

### Bad answer

一眼看出答案是这个，不用算。

### What is wrong

- no decisive mechanism
- no trust bill
- relies on vibe, not structure

### Repair

- downgrade from `秒杀` to `快招`
- add one minimal comparison / count / boundary check

## Bad Example 4: Fancy but ordinary

### Bad answer

先讲一段“本质”，然后还是完整走课本标准流程。

### What is wrong

- sounds advanced
- behaves ordinary
- the front-end intuition does not actually change the solve path

### Repair

- force the anti-standard ladder before standard algebra
- if the standard path still wins, say why

## Bad Example 5: Analogy drift

### Bad answer

把问题讲成一个很好懂的故事，但故事和原题的约束已经不完全对应。

### What is wrong

- the explanation becomes memorable by losing truth
- the learner feels懂了, but cannot safely reuse it

### Repair

- after analogy, add one sentence mapping back to the exact original condition

## Bad Example 6: Over-formalism

### Bad answer

一上来就定义变量、列方程、做展开、跑完整证明。

### What is wrong

- no demystification
- no downgrade
- no primitive routing
- feels like textbook or standard-answer cosplay

### Repair

- first strip the shell
- then try picture / compare / count / invariant / symmetry

## Bad Example 7: Numerically right, psychologically unconvincing

### Bad answer

结果是对的，但中间关键一步像瞬移。

### What is wrong

- the expert may accept it
- the learner does not trust it
- the skill fails the `Legality` and `Trust` checks

### Repair

- add one `补一句凭什么`
- if that still does not stabilize the jump, escalate to a minimal formal skeleton

## Negative Pattern Summary

Bad answers often share one of these defects:

- solve too much
- simplify by hiding assumptions
- call something obvious without making it checkable
- pretend to秒 when there is no real decisive mechanism
- explain by style instead of mechanism
