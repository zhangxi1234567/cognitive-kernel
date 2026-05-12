# Wu Boshi Three-Second Corpus

This file tracks answer-keyed seed problems that admit very fast low-computation attacks.

These are not all pure `秒杀`.
The selection standard is:

- public answer available
- multiple low-load routes exist or are strongly plausible
- the task can be collapsed by structure, not by brute computation

## Corpus Role Rule

This corpus is a seed bank, not the outer boundary of the skill.

Many current seeds come from exam math because:

- public answers exist
- the tasks are compact
- fast-vs-standard routes are easy to compare

But the function of this file is to provide:

- evidence
- stress tests
- primitive-mining seeds

not to imply that the underlying methods belong only to one school stage.

## High-Confidence Seed Set

### 1. 2025 新高考 I 卷 第6题

- theme: 帆船真风
- answer: `A. 轻风`
- source:
  - https://www.woaigaokao.com/wp-content/uploads/2025/10/2025%E9%AB%98%E8%80%83%E7%9C%9F%E9%A2%98%EF%BC%88%E6%96%B0%E9%AB%98%E8%80%83%E2%85%A0%E5%8D%B7%EF%BC%89%E6%95%B0%E5%AD%A6%E7%AD%94%E6%A1%88.pdf
- why selected:
  - vector picture
  - almost pure observation
  - multiple fast routes
- route labels:
  - coordinate difference -> `true 秒杀`
  - parallelogram completion -> `local-only trick`
  - machine language -> `快招`

### 2. 2025 新高考 I 卷 第8题

- theme: `2+log2 x = 3+log3 y = 5+log5 z`
- answer: `B`
- source:
  - https://www.woaigaokao.com/wp-content/uploads/2025/10/2025%E9%AB%98%E8%80%83%E7%9C%9F%E9%A2%98%EF%BC%88%E6%96%B0%E9%AB%98%E8%80%83%E2%85%A0%E5%8D%B7%EF%BC%89%E6%95%B0%E5%AD%A6%E7%AD%94%E6%A1%88.pdf
- why selected:
  - parameter compression
  - sample-point elimination
  - compare without heavy computation
- route labels:
  - common parameter + sample points -> `local-only trick`
  - growth-family comparison -> `稳招`

### 3. 2025 新高考 II 卷 第6题

- theme: 抛物线，求 `|AF|`
- answer: `C. 5`
- source:
  - https://www.woaigaokao.com/wp-content/uploads/2025/10/2025%E9%AB%98%E8%80%83%E7%9C%9F%E9%A2%98%EF%BC%88%E6%96%B0%E9%AB%98%E8%80%83%E2%85%A1%E5%8D%B7%EF%BC%89%E6%95%B0%E5%AD%A6%E6%95%B0%E5%AD%A6%E7%AD%94%E6%A1%88.pdf
- why selected:
  - focus definition
  - hidden `3-4-5`
  - geometry and coordinate routes both short
- route labels:
  - focus definition -> hidden 3-4-5 -> `local-only trick`
  - geometry-first -> `快招`

### 4. 2025 新高考 II 卷 第14题

- theme: 圆柱内两等球
- answer: `5/2`
- source:
  - https://www.woaigaokao.com/wp-content/uploads/2025/10/2025%E9%AB%98%E8%80%83%E7%9C%9F%E9%A2%98%EF%BC%88%E6%96%B0%E9%AB%98%E8%80%83%E2%85%A1%E5%8D%B7%EF%BC%89%E6%95%B0%E5%AD%A6%E6%95%B0%E5%AD%A6%E7%AD%94%E6%A1%88.pdf
- why selected:
  - sectional reduction
  - one-line Pythagorean closure
  - strong container-to-cross-section analogy
- route labels:
  - cross-section flattening -> `true 秒杀`
  - packing picture -> `快招`

### 5. 2024 新高考 I 卷 第14题

- theme: 卡片比赛 / 总得分不少于2
- answer: `1/2`
- sources:
  - https://www.xbjy.com/xhtml/202409/738.html
  - https://www.bilibili.com/video/BV1nw4m1e7u6/
- why selected:
  - permutation matching model
  - structural counting
  - multiple low-load counting routes
- route labels:
  - permutation view -> `稳招`
  - lock the worst card -> `稳招`
  - dominance partition -> `稳招`

### 6. 2024 新高考 II 卷 第14题（第一空）

- theme: 4×4 方格，每行每列各选1格
- answer: `24`
- sources:
  - https://www.xbjy.com/xhtml/202409/1005.html
  - https://www.bilibili.com/video/BV1w7421d73N/
- why selected:
  - pure permutation structure
  - very strong `4!` recognition route
- route labels:
  - `4!` -> `true 秒杀`
  - rook placement -> `true 秒杀`

### 7. 2023 天津卷 第3题

- theme: compare `1.01^0.5, 1.01^0.6, 0.6^0.5`
- answer: `D, b>a>c`
- source:
  - https://pdf.hanspub.org/ae2025151_11167910.pdf
- why selected:
  - classic compare-without-calculating
  - monotonicity and base/exponent recognition
- route labels:
  - same-base / same-exponent monotonicity -> `true 秒杀`
  - log / monotone recode -> `快招`

### 8. 2022 北京卷 第10题

- theme: right triangle, moving point, range of dot product
- answer: `[-4,6]`
- source:
  - https://pdf.hanspub.org/ae2024145_2291166163.pdf
- why selected:
  - vector recoding
  - polarization / projection routes
  - not instant, but often fast after the right recode
- route labels:
  - projection -> `稳招`
  - polarization identity -> `稳招`

## Additional Seed Set

### 9. 2023 天津卷 第3题（补强 compare primitive）

- theme: compare `1.01^0.5, 1.01^0.6, 0.6^0.5`
- answer: `D, b>a>c`
- source:
  - https://pdf.hanspub.org/ae2025151_11167910.pdf
- why selected:
  - strong evidence for `Compare Without Calculating`
  - explicit `一眼看出` flavor
- route labels:
  - same-base / same-exponent monotonicity -> `true 秒杀`
  - monotone recode -> `快招`

### 10. 2022 全国甲卷 第16题

- theme: triangle geometry, minimize `AC/AB`, find `BD`
- answer: `BD = √3 - 1`
- source:
  - https://pdf.hanspub.org/ae20230800000_87399712.pdf
- why selected:
  - explicit `多解`
  - good seed for deciding what remains local geometry trick vs transferable primitive
- route labels:
  - geometry construction -> `快招`
  - coordinate / discriminant / derivative -> `稳招`

### 11. 2025 新课标 II 卷 第16题

- theme: ellipse chord / area / chord length
- answer: `AB = 5`
- source:
  - https://pdf.hanspub.org/ces_3096033.pdf
- why selected:
  - explicit `多种解法`
  - useful for pressure-testing conics heuristics and second-layer attacks
- route labels:
  - area + chord relation -> `快招`
  - coordinate area / axis intercept route -> `稳招`

### 12. 2024 新高考 I 卷 第18题（1）

- theme: logarithmic expression monotonicity, find minimum `a`
- answer: `a_min = -2`
- source:
  - https://www.sci-open.net/index.php/ETR/article/download/1109/1230/2905
- why selected:
  - explicit `一题多解`
  - strong candidate for common-value / monotonicity / parameter compression adjacent primitives
- route labels:
  - derivative / monotonicity skeleton -> `稳招`
  - structural recode if compressed well -> `快招`

### 13. 2020 新高考全国卷 第7题

- theme: regular hexagon, range of dot product
- answer: `(-2,6), option A`
- source:
  - https://pdf.hanspub.org/ae2024145_2291166163.pdf
- why selected:
  - cross-validates `Dot Product Range By Projection`
  - gives a second seed for that primitive
- route labels:
  - projection / geometric readout -> `快招`
  - vector identity route -> `稳招`

### 14. 2024 新高考 I 卷 第19题

- theme: 可分数列 / 删除两项后分组
- public answer:
  - 第1问：`(1,2), (1,6), (5,6)`
  - 第2问：删去 `2,13`
  - 第3问：`P_m > 1/8`
- sources:
  - https://www.cnblogs.com/qinchenhao/p/18240720
  - https://www.cnblogs.com/yuzusbase/p/18250944
- why selected:
  - public解析明确指出可建模为 `精确覆盖`
  - this is high-value for pushing from local trick toward `exact-cover / one-to-one encoding / partition` families
- route labels:
  - exact-cover modeling -> `稳招`
  - structure-first grouping -> `快招`

### 15. 2024 高考数学 II 卷 第8题

- theme: \((x+a)\ln(x+b)\ge 0\)，求 \(a^2+b^2\) 的最小值
- public answer:
  - source page explicitly states it is a solved exam item with answer/analysis
- source:
  - https://www.cnblogs.com/xuebajunlutiji/p/18242868
- why selected:
  - public page title explicitly says `用通法不秒杀`
  - strong candidate for training:
    - parameter-boundary guess
    - witness-value probing
    - rapid verification
    - anti-standard-solution bias
- route labels:
  - boundary / witness probing -> `快招`
  - full formal derivation -> `稳招`

### 16. 2024 新高考 I 卷 第5题

- theme: 圆柱与圆锥侧面积相等，且高相等，求圆锥体积
- answer: `B. 3π`
- source:
  - https://www.xbjy.com/xhtml/202409/351.html
- why selected:
  - small calculation footprint
  - can be attacked by “先抓半径”而不是完整立体几何流程
  - good for testing whether the skill sees the core relation before expanding formulas
- route labels:
  - side-area equality -> radius first -> `快招`
  - direct formula substitution -> `稳招`

## Label Rubric

Use this rubric across all future seeds:

- `true 秒杀`
  - one dominant mechanism
  - one-step or near one-step separation
  - one tiny check
  - transferable as a method family

- `快招`
  - fast intuition is right
  - still needs one trust line or tiny check

- `稳招`
  - cheap primitive is right
  - still needs a minimal skeleton: partition, invariant, comparison axis, or case split

- `local-only trick`
  - fast because of this exact figure / options / lucky numbers
  - should stay an instance hint, not a universal method claim
