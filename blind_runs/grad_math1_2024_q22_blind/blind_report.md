# Blind Report

## Task

题目：总体 \(X\sim U(0,\theta)\), \(\theta>0\) 未知，样本为 \(X_1,\dots,X_n\)，记
\(X_{(n)}=\max\{X_1,\dots,X_n\}\)，\(T_c=cX_{(n)}\)。

要求：

1. 求 \(c\)，使 \(T_c\) 是 \(\theta\) 的无偏估计；
2. 记 \(h(c)=E[(T_c-\theta)^2]\)，求使 \(h(c)\) 最小的 \(c\)。

## Blind Boundary

本次解答只基于用户给定题目与允许的本地 live surface。
未读取 README、benchmarks、references、memory、PACKAGE_MAP、历史 blind 产物、网络题解或答案。

## Solve

设 \(M=X_{(n)}\)。

对 \(0\le x\le \theta\),

\[
P(M\le x)=P(X_1\le x,\dots,X_n\le x)=\left(\frac{x}{\theta}\right)^n.
\]

所以 \(M\) 的分布函数与密度函数分别为

\[
F_M(x)=\left(\frac{x}{\theta}\right)^n,\quad 0\le x\le \theta,
\]

\[
f_M(x)=\frac{n x^{n-1}}{\theta^n},\quad 0\le x\le \theta.
\]

于是

\[
E(M)=\int_0^\theta x\frac{n x^{n-1}}{\theta^n}\,dx
=\frac{n}{\theta^n}\int_0^\theta x^n\,dx
=\frac{n\theta}{n+1}.
\]

所以

\[
E(T_c)=E(cM)=cE(M)=c\frac{n\theta}{n+1}.
\]

要使 \(T_c\) 为 \(\theta\) 的无偏估计，需要

\[
c\frac{n\theta}{n+1}=\theta,
\]

即

\[
\boxed{c=\frac{n+1}{n}}.
\]

再求二阶矩：

\[
E(M^2)=\int_0^\theta x^2\frac{n x^{n-1}}{\theta^n}\,dx
=\frac{n}{\theta^n}\int_0^\theta x^{n+1}\,dx
=\frac{n\theta^2}{n+2}.
\]

因此

\[
h(c)=E[(cM-\theta)^2]
=c^2E(M^2)-2c\theta E(M)+\theta^2.
\]

代入上式得

\[
h(c)=\theta^2\left(\frac{n}{n+2}c^2-\frac{2n}{n+1}c+1\right).
\]

这关于 \(c\) 是开口向上的二次函数，所以最小时满足

\[
\frac{d}{dc}h(c)=\theta^2\left(2\frac{n}{n+2}c-2\frac{n}{n+1}\right)=0.
\]

解得

\[
\boxed{c=\frac{n+2}{n+1}}.
\]

## Final Answer

1. 使 \(T_c=cX_{(n)}\) 成为 \(\theta\) 的无偏估计时，

\[
\boxed{c=\frac{n+1}{n}}.
\]

2. 使 \(h(c)=E[(T_c-\theta)^2]\) 最小时，

\[
\boxed{c=\frac{n+2}{n+1}}.
\]

## Runtime / Layer Honesty

- 真正出现了 runtime/action layer 的读取、状态写入、guard/readout 调用、trace 导出。
- 但没有出现成功的 one-shot runtime consumption。
- 也就是说：这次运行里，runtime 被真实读取并真实试跑过，但没有成功完成 `bind-local` / `rebind-local` / `spend-local` 的消费闭环。
- 因此不能诚实地宣称“project runtime materially participated in the solve”。

## Whether There Was Layerwise Skill Composition

- 有局部的 layerwise surface 暴露：例如 runtime 把 late-stage surface 推向 `exact_closure` / `readout` / `definition_as_direct_readout`。
- 但没有形成成功封口的 layerwise skill composition。
- 更准确地说：出现了 layerwise readout 和 conflict/refusal，不是成功消费后的稳定组合。

## Where It Still Looked Like An Ordinary Solve

- 主体数学解法仍然是普通数理统计解法：先求最大次序统计量分布，再求一阶矩、二阶矩，再做无偏与均方误差最优化。
- runtime 没有改变核心数学路线，只在 late-stage 提供了一个“把答案现金化到 asked medium”的控制面。

## Closure Honesty

- 数学上已封口：常数 \(c\) 的两个答案都已明确求出。
- runtime 使用上未封口：有真实 trace，也有真实 refusal，但没有成功消费事件。

## Verification Snapshot

- `blind_report.md` 与 `solve_trace.md` 已实际写入目标目录。
- `runtime_state.json` 与 `runtime_state_bindonly.json` 都记录了 `final_artifact_materialized: true`。
- `runtime_trace_main.md` 记录了 9 个真实事件。
- `runtime_trace_bindonly.md` 记录了 3 个真实事件。
- `runtime_guard.py` 对两个状态文件都给出了真实 guard 输出；两者仍显示 `release_allowed: false`，原因不是数学未完成，而是 runtime consumption 仍未成功闭环。

## Artifacts

- `blind_report.md`
- `solve_trace.md`
- `runtime_trace_main.md`
- `runtime_trace_bindonly.md`
- `runtime_state.json`
- `runtime_state_bindonly.json`
