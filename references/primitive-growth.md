# Wu Boshi Primitive Growth

This file defines the recursive growth path:

`seed -> primitive -> family -> meta-principle`

## Level 1: Seed

A seed is one real problem instance with a fast route.

Question:

- what local trick worked here?
- what was the earliest honest layer where the trick first became visible?

## Level 2: Primitive

A primitive is the smallest reusable move behind the seed.

Question:

- what mechanism made the trick legal?
- what part survives when the presentation, domain, or complexity layer changes?

Examples:

- common-value compression
- compare without calculating
- permutation recognition

## Level 3: Family

A family groups primitives with the same deep move.

Question:

- what bigger solving posture unifies these primitives?
- what complexity layers can this posture survive across?

Examples:

- `comparison and elimination`
- `structure compression`
- `visual readout`
- `geometry anchoring`

## Level 4: Meta-Principle

A meta-principle is one of the deepest reusable habits that can generate new families.

Question:

- what habit of thought keeps recreating these families?
- what transfer habit lets the same family survive across domains?

Examples:

- `replace local detail with a controlling aggregate`
- `solve only the target quantity`
- `change representation before increasing computation`
- `turn dynamic mess into one fixed object`
- `turn many cases into one partition`

## Recursive Growth Rule

Whenever a seed is added, do all four checks:

1. What is the seed tactic?
2. What primitive does it instantiate?
3. What family does that primitive belong to?
4. What meta-principle generated that family?
5. What is the earliest honest layer where the structure is already visible?
6. What cross-domain analogue shows the same skeleton?

If steps 2-6 are missing, the skill is memorizing tricks instead of learning style.

## Expansion Example 1

Seed:

- 4x4 grid, each row and column choose one cell
- fast route: `4!`

Primitive:

- `permutation recognition`

Family:

- `exact-cover / one-to-one encoding`

Meta-principle:

- if every object must match exactly one other object, encode the whole thing as a bijection before doing anything else
- earliest honest layer: one-to-one slot matching

## Expansion Example 2

Seed:

- many ugly equalities all share one common value

Primitive:

- `common-value compression`

Family:

- `hidden-control-variable methods`

Meta-principle:

- if many visible quantities are controlled by one hidden scalar, solve the scalar first and stop treating the visible quantities as independent
- earliest honest layer: many outputs, one hidden knob

## Expansion Example 3

Seed:

- 3D packing reduced to one 2D slice

Primitive:

- `container-to-section reduction`

Family:

- `dimension reduction by controlling slice`

Meta-principle:

- when a high-dimensional system is symmetric, find the lowest-dimensional slice that still contains all decisive constraints
- earliest honest layer: cut one decisive section instead of carrying the whole object

## Promotion Rule

A new method is strong only if it can move upward:

- one seed is not enough for a primitive
- one primitive is not enough for a family
- one family is not enough for a meta-principle
- one domain is not enough for a transferable primitive
- one presentation layer is not enough for a level-agnostic primitive

But every real method should be traceable downward:

- meta-principle -> family -> primitive -> seed
- advanced form -> compact form -> earliest honest layer

That keeps the skill from becoming vague.

## Practical Use

When the skill meets a new problem, it should ask:

- which existing primitive fits?
- if none fits, is this a new seed?
- if it is a new seed, what primitive might be born from it?
- what lower-complexity layer reveals it fastest?
- what non-native domain would express the same skeleton?

That is how the skill keeps learning without becoming a random trick list.
