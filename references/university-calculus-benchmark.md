# Wu Boshi University Calculus Benchmark

This file tests whether the current skill can attack representative university-calculus problems without regrowing into ordinary textbook flow.

The goal is not to prove full coverage.
The goal is to see whether the skill can:

- hua-gui the problem into a smaller truthful class
- route to a real primitive
- produce a shorter lawful attack
- leave behind a transferable move

## Benchmark 1: Limit By Dominant Mechanism

### Prompt

Evaluate:

\[
\lim_{x \to \infty} \left(\sqrt{x^2+3x}-x\right)
\]

### Ordinary route

- multiply by the conjugate
- simplify formally
- then take the limit

This route is fine, but it still feels like standard algebra-first flow.

### Wu Boshi route

#### 本质

This is not really a "root-expression limit problem."
It is a **dominant-balance / leftover-gap** problem.

#### 划归

- decorated expression -> dominant term plus correction
- full expression -> target gap

#### Primitive

- `Dominant Mechanism Readout`
- `Target-Only Control`

#### Fast attack

\[
\sqrt{x^2+3x}=x\sqrt{1+\frac{3}{x}}
\]

For large \(x\), the inside is just "1 plus a small thing."
So the whole expression is asking:

- after the dominant \(x\) is removed,
- what constant-sized leftover remains?

Using the first-order small-change rule:

\[
\sqrt{1+u}\approx 1+\frac{u}{2}
\quad (u\to 0)
\]

with \(u=\frac{3}{x}\),

\[
x\left(\sqrt{1+\frac{3}{x}}-1\right)
\approx
x\left(\frac{3}{2x}\right)=\frac{3}{2}
\]

So the limit is:

\[
\boxed{\frac{3}{2}}
\]

#### 补一句凭什么

The move is legal because the target is only the leading leftover after cancellation of the dominant term, so first-order control is enough.

#### Transfer

When a high-order expression asks for a small leftover after two big terms cancel, first ask for the **dominant mechanism plus correction**, not for full simplification.

### Verdict

`Pass`

The route genuinely changed:

- full symbolic manipulation -> dominant leftover readout

## Benchmark 2: Derivative By Structure, Not Ritual

### Prompt

Find the derivative of:

\[
y=\ln\!\left(x+\sqrt{x^2+1}\right)
\]

### Ordinary route

- chain rule
- quotient cleanup
- more algebra

### Wu Boshi route

#### 本质

This is not a "nested log derivative drill."
It is a **hidden canonical function** problem.

#### 划归

- decorated expression -> mother object

#### Primitive

- `Canonical Normalization`
- `Mother-Pattern Recognition`

#### Fast attack

Recognize:

\[
\operatorname{arcsinh}x
=
\ln\!\left(x+\sqrt{x^2+1}\right)
\]

So the problem is already in a known mother form:

\[
y=\operatorname{arcsinh}x
\]

Hence

\[
y'=\frac{1}{\sqrt{x^2+1}}
\]

#### 补一句凭什么

The shortcut is legal because the given expression is exactly the canonical logarithmic form of \(\operatorname{arcsinh}x\), not just a similar-looking expression.

#### Transfer

In higher calculus, many ugly expressions are not meant to be differentiated raw.
They are meant to be **recognized as canonical forms first**.

### Verdict

`Pass`

The route genuinely changed:

- chain-rule grind -> canonical-form recognition

## Benchmark 3: Integral By Symmetry And Target Compression

### Prompt

Compute:

\[
I=\int_{0}^{\pi}\frac{\sin x}{1+\cos^2 x}\,dx
\]

### Ordinary route

- substitution \(u=\cos x\)
- track bounds carefully

This route is already short, so the benchmark asks:

- can the skill still make the structure smaller without becoming theatrical?

### Wu Boshi route

#### 本质

This is a **target-only substitution integral**.
The numerator is already the derivative shadow of the denominator's inner geometry.

#### 划归

- trigonometric integral -> one-variable rational target

#### Primitive

- `Target-Only Control`
- `Projection Readout`

#### Fast attack

Let

\[
u=\cos x,\quad du=-\sin x\,dx
\]

Then

\[
I
=
\int_{1}^{-1}\frac{-1}{1+u^2}\,du
=
\int_{-1}^{1}\frac{1}{1+u^2}\,du
\]

So

\[
I=\left[\arctan u\right]_{-1}^{1}
=
\frac{\pi}{4}-\left(-\frac{\pi}{4}\right)
=
\boxed{\frac{\pi}{2}}
\]

#### 补一句凭什么

This is a real reduction because the full trig surface disappears and the target becomes one clean rational integral.

#### Transfer

When the numerator is already carrying the motion of the denominator's inner variable, solve the target directly instead of staying loyal to the original surface form.

### Verdict

`Pass, but modest`

This is a good reminder:

- not every university-calculus problem needs a dramatic shortcut
- the skill still works when the best reduced route is simply a very clean substitution

## Benchmark 4: Global Monotonicity By Local Seam

### Prompt

Show that:

\[
f(x)=x-\ln(1+x)\quad (x>0)
\]

satisfies \(f(x)>0\).

### Ordinary route

- compute derivative
- prove monotonic increase
- use \(f(0)=0\) idea

### Wu Boshi route

#### 本质

This is not mainly a function-value problem.
It is a **local seam controls global** problem.

#### 划归

- global inequality -> behavior near the controlling seam \(x=0\)

#### Primitive

- `Local Seam Controls Global`
- `Dominant Mechanism Readout`

#### Fast attack

Look at the derivative:

\[
f'(x)=1-\frac{1}{1+x}=\frac{x}{1+x}>0
\quad (x>0)
\]

So once the function leaves the seam \(x=0\), it can only move upward.

And

\[
f(0)=0-\ln 1=0
\]

Hence for every \(x>0\),

\[
f(x)>0
\]

#### 补一句凭什么

The seam is \(x=0\): once the derivative is positive on the whole right side, that seam value controls the entire inequality.

#### Transfer

Many global inequalities are really:

- find the seam value
- prove one-sided monotonic escape from that seam

### Verdict

`Pass`

The route is standard-adjacent, but the skill correctly renames the burden:

- not "prove for all \(x\)" by raw manipulation
- but "control the global claim from the seam"

## Benchmark 5: Multivariable Extremum By Projection Mindset

### Prompt

Find the maximum of \(xy\) subject to:

\[
x^2+y^2=1
\]

### Ordinary route

- Lagrange multipliers
- or substitution \(y=\sqrt{1-x^2}\)

### Wu Boshi route

#### 本质

This is not an optimization-with-constraints ritual problem.
It is a **projection / symmetry** problem on the unit circle.

#### 划归

- constrained optimization -> compare one transformed target on a symmetric set

#### Primitive

- `Projection Readout`
- `Compare Without Calculating`

#### Fast attack

Use:

\[
(x-y)^2\ge 0
\]

So

\[
x^2+y^2\ge 2xy
\]

Under the constraint \(x^2+y^2=1\),

\[
1\ge 2xy
\]

hence

\[
xy\le \frac{1}{2}
\]

Equality holds when \(x=y\), and then on the unit circle:

\[
x=y=\frac{1}{\sqrt{2}}
\]

So the maximum is:

\[
\boxed{\frac{1}{2}}
\]

#### 补一句凭什么

The constraint already gives the total square mass, so the target \(xy\) is controlled by one symmetric comparison inequality.

#### Transfer

Before reaching for Lagrange multipliers, ask whether the constraint already gives a fixed total that can dominate the target directly.

### Verdict

`Strong pass`

The route genuinely changed:

- optimization routine -> symmetric comparison on a fixed total

## Overall Assessment

### Strongly passing university-calculus families

- canonical-form recognition
- dominant leftover / asymptotic gap reading
- seam-controlled monotonicity
- symmetric constrained optimization
- target-only substitution integrals

### Still needing more seed coverage

- epsilon-delta style proofs
- uniform convergence / series interchange questions
- multivariable geometry beyond simple symmetric constraints
- differential equations
- rigorous mean-value / Taylor remainder problems

## Conclusion

The current skill can already produce genuine non-ordinary routes on several representative university-calculus problems.

It is strongest when the problem can be hua-gui'd into:

- mother form
- target-only control
- symmetry / comparison
- dominant mechanism
- local seam control

It still needs a denser advanced seed bank before claiming stable coverage of all higher-calculus terrain.
