# Wu Boshi Conics Short Attacks

Use this file as the pre-coordinate checklist for conics and analytic geometry.

Goal:

- try the short route before full parameterization
- keep the attack at line-level, anchor-level, or target-level as long as possible

## Short-Attack Ladder

Before standard parameterization, run this exact order:

1. `Anchor points`
2. `Fixed line / fixed quantity`
3. `Chord or tangent in line form`
4. `Intercept comparison`
5. `Area reduction`
6. `Symmetry relabel`
7. `Vieta instead of explicit roots`
8. `Focus-directrix meaning`
9. `Asymptote frame`
10. Only then `full coordinates / full parameters`

## Attack 1: Anchor The Picture

### Trigger

- ellipse/hyperbola/parabola named explicitly
- one moving point or line but the conic itself is fixed

### Fast move

- mark center / vertex / focus / directrix / asymptotes first
- rewrite every new object relative to those anchors

### Replaces

- blind coordinate introduction

### Stop condition

- once the target is visibly about one stable anchor relation

## Attack 2: Prove Only The Target Quantity

### Trigger

- "prove fixed"
- "find the range of one expression"
- "show the midpoint lies on..."
- "compare two quantities"

### Fast move

- write only the target expression
- eliminate all variables not appearing in the target
- if a linear relation appears, stop immediately

### Replaces

- solving all coordinates of all points

### Warning

- if the target expression still depends on two unrelated moving parameters, step back and change representation

## Attack 3: Turn Point-Pairs Into One Line

### Trigger

- line cuts conic at `A, B`
- secant / chord / moving line language

### Fast move

- write the line equation first
- substitute into the conic
- use root sum/product instead of separate coordinates

### Best for

- midpoint
- chord length comparison
- fixed-point or fixed-line claims
- area with a chord

## Attack 4: Tangent Means Discriminant Zero

### Trigger

- tangent line
- external point with two tangents
- tangent intercept problem

### Fast move

- choose line form
- substitute once
- set discriminant to zero
- read the relation you need

### Best for

- intercept product/sum
- tangent family envelope-style questions
- fixed line from tangent intersections

## Attack 5: Intercept Form Before Contact Point

### Trigger

- line with axes makes triangle
- tangent intercepts
- need area or compare lengths on axes

### Fast move

- use intercept form
- apply tangency condition
- convert directly to area or inequality

### Why it is short

- the contact point is usually irrelevant noise

## Attack 6: Area = Base x Height, Not Expression Explosion

### Trigger

- triangle area with center / focus / axes / tangent / chord

### Fast move

- choose the cheapest fixed base
- prove only the height relation
- if the axes are involved, switch to intercept area immediately

### Common win

- one determinant line can be replaced by one distance-to-line observation

## Attack 7: Use Symmetry To Pair Work

### Trigger

- two points play mirror roles
- centered conic
- target is symmetric

### Fast move

- pair points by reflection or central symmetry
- compute one side and copy by symmetry
- or move to the midpoint directly

### Best for

- ellipse / hyperbola midpoint problems
- equal slope / opposite slope structures
- paired tangent questions

## Attack 8: Hyperbola -> Look At Asymptotes

### Trigger

- hyperbola question looks uglier than ellipse question
- slope/product/angle behavior

### Fast move

- redraw the problem with asymptotes emphasized
- compare the line to asymptote directions
- normalize expressions against asymptote slope if possible

### Why it works

- asymptotes are the hidden coordinate system

## Attack 9: Parabola -> Go Back To Focus And Directrix

### Trigger

- distance
- angle
- tangent/reflection flavor
- focus enters the statement

### Fast move

- replace equation-thinking with definition-thinking
- use equal distances to focus and directrix
- reflect if that turns angle/distance into a straight-line statement

### Replaces

- grinding on `y^2 = 2px` or `x^2 = 2py` too early

## Attack 10: Midpoint First

### Trigger

- midpoint of a chord
- locus of midpoint
- line through midpoint

### Fast move

- use root sum or average coordinates
- derive midpoint relation directly from the line parameter
- prove the midpoint locus first, then recover extra claims only if needed

### Why it wins

- midpoint statements are usually linear even when the endpoints are quadratic

## Attack 11: Compare Slopes Instead Of Coordinates

### Trigger

- "parallel", "perpendicular", "angle fixed", "slope product fixed"

### Fast move

- convert the whole problem to slope relations
- avoid explicit endpoints unless a slope formula needs one last substitution

### Best for

- tangent-chord relations
- hyperbola asymptote comparisons
- fixed-angle families

## Attack 12: One Variable Is Enough

### Trigger

- standard solution introduces `k`, `m`, and point parameters together

### Fast move

- keep only the line parameter or only one point parameter
- eliminate everything else immediately

### Hard rule

- if the target is one-dimensional, the setup should also be one-dimensional unless impossible

## Quick Routing By Conic Type

### Ellipse

- first try `anchor points`
- then `midpoint / chord`
- then `intercept or area`

### Hyperbola

- first try `asymptote frame`
- then `slope comparison`
- then `tangent / secant line form`

### Parabola

- first try `focus-directrix meaning`
- then `tangent discriminant`
- then `midpoint / line parameter`

## Anti-Standard Reminders

- do not parametrize both intersection points unless the target explicitly depends on both separately
- do not reconstruct the conic if the question only asks about one associated line
- do not chase the contact point if the tangent relation already closes in line variables
- do not expand quartics generated by bad substitution choices
- if the algebra starts growing, switch back to line-language or anchor-language
