# 2023 新高考 I 卷数学第 22 题 blind report

## 边界说明

本次解答只读取了题目允许的 live surface：

- `AGENTS.md`
- `CLAUDE.md`
- `SKILL.md`
- `COMPATIBILITY.md`
- `BLIND_TEST_BOUNDARY.md`
- `runtime/` 下允许文件中的必要部分

未读取 `README.md`、`benchmarks/`、`references/`、`memory/`、`PACKAGE_MAP.md`、历史 blind 产物，也未联网搜索。

## 题目

在直角坐标系 `xOy` 中，点 `P` 到 `x` 轴的距离等于点 `P` 到点 `(0,1/2)` 的距离，记动点 `P` 的轨迹为 `W`。

1. 求 `W` 的方程；
2. 已知矩形 `ABCD` 有三个顶点在 `W` 上，证明：矩形 `ABCD` 的周长大于 `3\sqrt3`。

---

## 第 1 问

设 `P(x,y) \in W`。

点 `P` 到 `x` 轴的距离为 `|y|`，到点 `(0,1/2)` 的距离为

```math
\sqrt{x^2+\left(y-\frac12\right)^2}.
```

由题意，

```math
|y|=\sqrt{x^2+\left(y-\frac12\right)^2}.
```

两边平方，得

```math
y^2=x^2+y^2-y+\frac14,
```

即

```math
y=x^2+\frac14.
```

因此

```math
W:\ y=x^2+\frac14.
```

这是一条焦点为 `(0,1/2)`、准线为 `y=0` 的抛物线。

---

## 第 2 问

### 1. 把三点写在抛物线上

设矩形中在抛物线上的三个顶点按顺序为 `A,B,C`，其中 `AB \perp BC`。

记

```math
A(a,a^2+\tfrac14),\quad B(b,b^2+\tfrac14),\quad C(c,c^2+\tfrac14).
```

抛物线上两点连线斜率有一个很方便的表达式：

```math
k_{AB}=\frac{a^2-b^2}{a-b}=a+b,\qquad
k_{BC}=\frac{c^2-b^2}{c-b}=b+c.
```

由于 `AB \perp BC`，所以

```math
(a+b)(b+c)=-1.
```

令

```math
m=a+b,\qquad n=b+c,
```

则

```math
mn=-1.
```

### 2. 把两条边长写出来

由两点间距离公式，

```math
AB=|a-b|\sqrt{1+(a+b)^2}=|a-b|\sqrt{1+m^2},
```

```math
BC=|c-b|\sqrt{1+(b+c)^2}=|c-b|\sqrt{1+n^2}.
```

又因为

```math
a-b=m-2b,\qquad c-b=n-2b,
```

故

```math
AB=|m-2b|\sqrt{1+m^2},
\qquad
BC=|n-2b|\sqrt{1+n^2}.
```

### 3. 降成一个参数

由 `mn=-1`，知 `m,n` 异号，且其中至少一个绝对值不小于 `1`。不妨设

```math
|m|\ge 1.
```

于是

```math
|n|=\frac1{|m|}\le 1.
```

分两种情况讨论。

#### 情况一：`|m|=1`

这时 `|n|=1`，所以

```math
\sqrt{1+m^2}=\sqrt{1+n^2}=\sqrt2.
```

于是

```math
AB+BC
=\sqrt2\bigl(|m-2b|+|n-2b|\bigr)
\ge \sqrt2\,|m-n|.
```

又因 `m,n` 异号且 `|m|=|n|=1`，故 `|m-n|=2`，所以

```math
AB+BC\ge 2\sqrt2>\frac{3\sqrt3}{2}.
```

#### 情况二：`|m|>1`

这时

```math
\sqrt{1+n^2}< \sqrt{1+m^2}.
```

因此

```math
AB+BC
=|m-2b|\sqrt{1+m^2}+|n-2b|\sqrt{1+n^2}
```

```math
> \sqrt{1+n^2}\bigl(|m-2b|+|n-2b|\bigr).
```

再由三角不等式，

```math
|m-2b|+|n-2b|\ge |m-n|,
```

从而

```math
AB+BC>\sqrt{1+n^2}\,|m-n|.
```

由 `n=-1/m`，并记 `t=|m|(\ge 1)`，则

```math
\sqrt{1+n^2}\,|m-n|
=\sqrt{1+\frac1{t^2}}\left(t+\frac1t\right)
=\frac{(t^2+1)^{3/2}}{t^2}.
```

令 `s=t^2(\ge 1)`，则只需研究

```math
f(s)=\frac{(s+1)^{3/2}}{s}.
```

求导得

```math
f'(s)=\frac{(s+1)^{1/2}(s-2)}{2s^2}.
```

所以 `f(s)` 在 `s=2` 时取得最小值，最小值为

```math
f(2)=\frac{3^{3/2}}2=\frac{3\sqrt3}{2}.
```

于是，在情况二中

```math
AB+BC>\frac{3\sqrt3}{2}.
```

结合情况一，也有

```math
AB+BC>\frac{3\sqrt3}{2}.
```

矩形 `ABCD` 的周长

```math
L=2(AB+BC)>2\cdot \frac{3\sqrt3}{2}=3\sqrt3.
```

故证：

```math
\boxed{L>3\sqrt3}.
```

---

## 结论

```math
\boxed{W:\ y=x^2+\frac14}
```

且若矩形 `ABCD` 有三个顶点在 `W` 上，则其周长满足

```math
\boxed{C_{ABCD}>3\sqrt3}.
```
