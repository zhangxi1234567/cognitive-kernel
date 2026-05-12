# Wu Boshi Conics Heuristics

Use this file when the problem is about ellipse, hyperbola, parabola, or mixed conic analytic geometry.

Goal:

- stop conics from turning into coordinate sludge
- extract the one stable quantity or one reusable picture first
- prove only the target quantity whenever possible

Conics problems often look complicated for a fake reason:

- too many parameters
- too many moving points
- the statement is written in coordinates but the target is geometric
- the solver starts trying to reconstruct the whole conic instead of the one thing the question actually asks

## First Question

Before doing anything, ask:

- what is the target really asking me to control?

Usually it is only one of these:

- a point is fixed
- a line is fixed
- a slope/product/sum is fixed
- a ratio is fixed
- an area is fixed
- two intercepts can be compared
- a midpoint / chord / tangent has a stable pattern

If the target is only one quantity, do not solve for the whole point unless forced.

## Core Routing For Conics

Run this scan in order.

### 1. Anchor Scan

Ask:

- what are the obvious anchor points?
- what are the canonical anchor lines?

Default anchors:

- ellipse / hyperbola:
  - vertices
  - co-vertices if relevant
  - foci
  - center
  - asymptotes for hyperbola
- parabola:
  - vertex
  - focus
  - directrix
  - axis
  - latus-rectum endpoints when chord structure appears

Operational rule:

- if a moving line or moving point can be measured relative to one of these anchors, do that first
- if a condition mentions slope, tangent, midpoint, distance, or area, try rewriting it against the anchor frame before solving coordinates

### 2. Fixed-Object Scan

Ask:

- is the question secretly asking me to prove a fixed point, fixed line, fixed slope, fixed ratio, or fixed area?

Fast test:

- rewrite the target into a form that has no moving parameter left except one eliminable symbol
- if the target can be written without the full coordinates of the moving point, take that route

Common fixed objects:

- midpoint locus becomes a line
- intersection of two tangents sits on a fixed polar-style line
- chord midpoint and chord slope satisfy a linear relation
- tangent intercept product / sum becomes constant after one substitution
- area with center / focus / axes endpoints collapses to base-times-height on a fixed frame

### 3. Symmetry Scan

Ask:

- what involution leaves the conic unchanged?

Standard symmetries:

- ellipse / hyperbola centered at origin:
  - `(x, y) <-> (-x, -y)`
  - axis reflections
- standard parabola:
  - reflection across the axis
- rectangular or centered hyperbola:
  - asymptote-centered symmetry often kills sign clutter

Operational rule:

- if the statement treats two points asymmetrically but the target is symmetric, relabel or pair them before computing
- if the line through two symmetric points is easier than the points themselves, solve at line level

### 4. Target-Only Scan

Ask:

- do I need coordinates of the points, or only one expression in them?

If the target is:

- slope:
  - eliminate coordinates into slope form directly
- intercepts:
  - work with line equation coefficients, not point coordinates
- area:
  - convert to intercepts, distance-to-line, or determinant structure directly
- fixed line:
  - derive one linear relation and stop
- ratio:
  - normalize early and keep only homogeneous quantities

Hard rule:

- never solve for both intersection points if Vieta on the line parameter already gives the target

### 5. Intercept Scan

Use when the question mentions:

- x-intercept / y-intercept
- tangent intercepts
- triangle with coordinate axes
- compare two lines without caring about the exact contact point

Fast move:

- switch the line to intercept form or slope-intercept form
- substitute once into the conic
- impose the tangency / secant discriminant condition
- read the relation among intercepts

Why this is strong:

- many ugly point coordinates disappear
- area with axes becomes `1/2 * |x-int| * |y-int|`
- comparison questions become comparison of one-variable expressions

### 6. Area Scan

When area appears, ask which of the three cheapest area languages works:

- intercept area
- base-height from a fixed axis or fixed line
- determinant / shoelace from simple coordinates

Operational rule:

- if the vertices already sit on axes, use axis-area immediately
- if one vertex is the center, vertex, or focus, area often reduces to distance from that anchor to a line
- if two moving points lie on one line, area is often "fixed base times variable height", so only the height needs proof

### 7. Chord-And-Tangent Scan

This is the main conics engine.

Ask:

- is the problem really about a line cutting the conic?
- can everything be transferred from point-language to line-language?

Useful reductions:

- secant intersection points -> quadratic roots on one line
- sum/product of roots -> midpoint / chord length / projection data
- tangent condition -> discriminant zero
- chord midpoint -> linear relation between midpoint coordinates and chord slope

Operational rule:

- if a moving point pair lies on one moving line, line-first is usually cheaper than point-first

### 8. Projective-Style Invariant Scan

Use carefully. This is not a license to show off projective geometry.

Only use if it actually shortens the proof and can be explained in plain language.

Safe projective-style ideas:

- tangency is more stable at line level than point level
- two secant intersection points are often better handled by root sum/product than by explicit coordinates
- pole/polar flavor:
  - if "intersection of tangents", "contact chord", "line of corresponding points" keeps appearing, expect one fixed linear relation
- cross-ratio language is usually too heavy for first pass; replace it with:
  - harmonic split
  - root pairing
  - linear-fractional invariance on one chosen line

Hard rule:

- if a projective phrase cannot be downgraded to line-root or tangent-line language in one sentence, do not use it in the first pass

## Domain-Specific Heuristics

## Ellipse

Primary anchors:

- center
- two vertices
- two foci
- four standard extremal points

Try first:

- use symmetry about center or axes before expanding
- if a line cuts the ellipse at `A, B`, use the line parameter plus Vieta for:
  - midpoint
  - `x_A + x_B`, `y_A + y_B`
  - chord midpoint locus
- if tangent from an external point appears, move to tangent equation or discriminant
- if area with center/focus/vertex appears, reduce to one height or one intercept

Strong reusable move:

- ellipse problems often hide "four-point anchor thinking":
  - compare everything against vertices/foci/center first
  - many moving configurations become obvious once attached to this rigid frame

## Hyperbola

Primary anchors:

- center
- vertices
- foci
- asymptotes

Try first:

- asymptotes are not decoration; they are the cheapest coordinate-free frame
- if slopes multiply to something simple, check asymptote symmetry
- if the problem looks messy, rotate viewpoint toward:
  - relation to asymptotes
  - chord midpoint
  - tangent family
- for conjugate-looking expressions, normalize by asymptote directions before expanding

Strong reusable move:

- many hyperbola questions become "how does this line sit relative to the asymptotes?" rather than "where exactly are the points?"

## Parabola

Primary anchors:

- vertex
- focus
- directrix
- axis

Try first:

- if distance appears, use focus-directrix definition, not standard equation grinding
- if tangent appears, line form plus discriminant is usually cheapest
- if two points on parabola and one line appear, look for:
  - parameter midpoint trick
  - tangent-normal relation
  - chord through focus / parallel to directrix simplifications
- if angle or equal-distance flavor appears, reflect to the directrix picture

Strong reusable move:

- parabola often wants you to switch from coordinates back to "point equals focus distance equals directrix distance"

## Only-Prove-The-Target Rules

This section is mandatory for conics.

If the target is:

### Fixed line

Do:

- derive one linear equation satisfied by the claimed moving point / midpoint / intersection
- stop when the coefficients are constant

Do not:

- fully parametrize the locus unless the question asks for the whole locus

### Fixed quantity

Do:

- compress the target to one symmetric expression
- use Vieta, discriminant, or intercept relation to evaluate it directly

Do not:

- solve for both roots separately

### Comparison

Do:

- convert to one comparison axis:
  - slope
  - intercept
  - distance to axis
  - area
  - one-variable rational function

Do not:

- compute both full objects if their order follows from one monotone expression

### Area

Do:

- reduce area to one base and one height, or intercept product
- prove only the part that changes

Do not:

- expand every coordinate determinant unless no simpler frame exists

## Anti-Regrowth Rules

Conics solutions rot by regrowth very fast.

Stop the regrowth when you notice:

- introducing point parameters for every moving point
- solving two intersections explicitly when only sum/product matters
- deriving the whole conic equation from conditions even though the question only needs a tangent or line relation
- expanding quartics or nested radicals
- mixing geometric and coordinate languages without one clear target

When this happens, force a reset:

1. say the target in one line
2. say which object is actually moving
3. say which quantity is supposed to stay fixed
4. choose line-language, not point-language, if the moving object is a line
5. choose anchor-language, not raw coordinates, if the target is geometric

## Minimal Answer Shapes For Conics

Use one of these short shapes.

### Shape A: Fixed-Line Proof

1. `Target`: what must stay on one line
2. `Anchor`: which rigid frame is cheapest
3. `Elimination`: remove moving parameters
4. `Line`: show one linear relation
5. `Reuse`: midpoint / chord / tangent problems often do this

### Shape B: Intercept / Area Shortcut

1. `Line first`
2. `Tangency or secant condition`
3. `Read intercept relation`
4. `Translate to area / comparison`
5. `Stop`

### Shape C: Focus-Directrix Shortcut

1. `Strip coordinates`
2. `Use equal-distance meaning`
3. `Turn shape into one comparison or one reflection`
4. `Map back to symbols`

## One-Line Memory Hooks

- `椭圆先找锚点，不先找参数`
- `双曲线先看渐近线，不先看大式子`
- `抛物线先回定义，不先回公式`
- `弦的问题先看线，不先看点`
- `只证题目要的量，不把整道题都解完`
