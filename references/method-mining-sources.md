# Wu Boshi Public Seed Mining Sources

Role note:

- this file is a public-source seed map
- it records where reusable moves can be mined from
- source concentration in exam material reflects current evidence availability, not the allowed scope of the method

This file lists high-yield public sources for mining additional fast-solve methods and reusable primitives.

The goal is not to collect more papers for their own sake.
The goal is to find sources that naturally expose:

- multiple solution routes
- fast/low-computation methods
- alternative representations
- hidden-structure attacks

## High-Yield Public Seed Sources

### 1. 2025 新高考 I 卷答案 PDF

Source:

- https://www.woaigaokao.com/wp-content/uploads/2025/10/2025%E9%AB%98%E8%80%83%E7%9C%9F%E9%A2%98%EF%BC%88%E6%96%B0%E9%AB%98%E8%80%83%E2%85%A0%E5%8D%B7%EF%BC%89%E6%95%B0%E5%AD%A6%E7%AD%94%E6%A1%88.pdf

Best for mining:

- vector difference
- common-value compression
- comparison-first multiple-choice attacks

### 2. 2025 新高考 II 卷答案 PDF

Source:

- https://www.woaigaokao.com/wp-content/uploads/2025/10/2025%E9%AB%98%E8%80%83%E7%9C%9F%E9%A2%98%EF%BC%88%E6%96%B0%E9%AB%98%E8%80%83%E2%85%A1%E5%8D%B7%EF%BC%89%E6%95%B0%E5%AD%A6%E6%95%B0%E5%AD%A6%E7%AD%94%E6%A1%88.pdf

Best for mining:

- conic target-only routes
- container-to-section reduction
- geometry-first shortcuts

### 3. 心标教育 2024 新高考 I 卷第14题

Source:

- https://www.xbjy.com/xhtml/202409/738.html

Best for mining:

- matching instead of probability
- static-structure recoding of story probability

### 4. 心标教育 2024 新高考 II 卷第14题

Source:

- https://www.xbjy.com/xhtml/202409/1005.html

Best for mining:

- permutation recognition
- exact-cover / one-to-one encoding

### 5. Hans PDF: 2023 天津卷比较大小

Source:

- https://pdf.hanspub.org/ae2025151_11167910.pdf

Best for mining:

- compare without calculating
- monotonicity-first attacks

### 6. Hans PDF: 2022 全国甲卷第16题

Source:

- https://pdf.hanspub.org/ae20230800000_87399712.pdf

Best for mining:

- one problem, multiple routes
- deciding which are universal vs local-only geometry tricks

### 7. Hans PDF: 2022 北京卷 / 2020 新高考全国卷 向量题

Source:

- https://pdf.hanspub.org/ae2024145_2291166163.pdf

Best for mining:

- dot product by projection
- range by geometric recoding
- fast vector primitives

### 8. Pure Mathematics 解析几何 15 种路径探析

Source:

- https://pdf.hanspub.org/PM20231200000_76819830.pdf

Best for mining:

- second-layer attacks for conics
- alternate route families
- target-only and root-level conic strategies

## Mining Rule

Prefer sources that expose:

- more than one legitimate route
- a route that reduces moving parts
- a route that changes representation
- a route that avoids reconstructing the full object

Do not prioritize sources that only give:

- one polished standard derivation
- lots of algebra with no route contrast
- local numerical tricks without transfer value

Interpretation rule:

- many current high-yield seeds happen to be exam-facing because those public pages expose route contrast clearly
- mine the transferable primitive, not the school-stage wrapper
