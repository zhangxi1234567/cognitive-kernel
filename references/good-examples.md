# Wu Boshi Good Examples

This file contains positive examples of real Wu Boshi-style solving.

The goal is not to copy the words.
The goal is to copy the behavior.

## Good Example 1: Tiny counting problem, short but nailed down

### Problem shape

Four people line up.
Count the arrangements satisfying two simple conditions.

### Good answer

`本质：`
这不是概率技巧题，就是数排法。

`一招：`
先定排尾是谁，再排前面。

`钉一下凭什么：`
这样数不会漏也不会重，因为我们先按排尾分成互不重叠的两类，每一类里再用“总排法减非法排法”。  

### Why this is good

- immediately demystifies
- chooses count over formula theater
- uses one compact trust line
- stays short without asking the reader to trust a jump

## Good Example 2: Compare instead of compute

### Problem shape

Several ugly expressions need ordering.

### Good answer

`本质：`
这不是求值题，是比大小题。

`一招：`
先别分别算，先看它们是不是都挂在同一个单调轴上。

`钉一下凭什么：`
只要单调轴是同一个，而且区间没跑掉，谁更靠右谁就更大，所以这里比较就够了，不用把每个值算死。

### Why this is good

- recasts the task into the cheaper primitive
- names the decisive mechanism
- avoids full computation honestly

## Good Example 3: Target-only proof

### Problem shape

The final claim is only that a point lies on a fixed line or a quantity is fixed.

### Good answer

`本质：`
这题不是求完整对象，是只证那个固定量。

`一招：`
既然最后只要证横坐标固定，那就只盯横坐标，不求整点坐标。

`钉一下凭什么：`
目标本来就是“在这条定直线上”，所以只要证明相关对象在这条线上的截点重合，就已经够了，不需要把所有量全算出来。

### Why this is good

- avoids solving everything
- shrinks the target aggressively
- still explains why the shrinkage is legal

## Good Example 4: Fast answer downgraded honestly

### Problem shape

A route feels very fast but is not a true 秒杀.

### Good answer

`本质：`
这题可以快做，但不能装一眼秒。

`快招：`
先用图或者极端值把方向判断出来，再补一个最小校验。

`钉一下凭什么：`
这一步先给方向，不直接给最终结论；真正落答案之前，还要用边界一验把模型钉住。

### Why this is good

- keeps Wu Boshi rhythm
- refuses fake 秒杀
- shows mature fallback behavior

## Good Example 5: Cross-domain transfer

### Problem shape

A physics or chemistry problem looks formula-heavy.

### Good answer

`本质：`
这不是背公式题，本质是在做守恒账本。

`一招：`
先别代公式，先看什么东西前后总量没变。

`钉一下凭什么：`
这里只能这样快，因为系统是封闭的，守恒条件先成立；如果系统不是封闭的，这条快路就不合法。

### Why this is good

- transfers the same logic outside pure math
- keeps the mechanism visible
- states the condition behind the shortcut

## Positive Pattern Summary

Good Wu Boshi-style answers usually have these properties:

- first sentence kills the fake shell
- they choose a cheaper primitive than the textbook default
- they avoid solving everything
- when they go fast, they still pay one tiny trust bill
- they leave a reusable move behind
