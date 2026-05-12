# Primitive: Common-Value Compression

## Pattern

Several ugly expressions are secretly tied to one shared quantity.

The visible variables are many, but the real degree of freedom is one.

## Trigger Signal

- repeated `=`
- different expressions all equal the same thing
- direct solving branches outward into many variables
- the task is comparison / elimination / impossible-option detection, not full reconstruction
- many visible quantities seem to turn together when one hidden knob changes

## Level-Agnostic Core

Do not manage several visible variables as if they were independent when one hidden scalar is actually controlling them all.

## Control Mechanism

The move works because:

- many visible quantities share one latent control parameter
- the equal-value relation collapses many degrees of freedom into one
- comparison, elimination, or threshold checking becomes cheaper at the hidden-parameter level

## Preserved Structure

Typical preserved items:

- equality-to-parameter correspondence
- option-separating order on the hidden variable
- monotone dependence of visible quantities on the shared value
- domain constraints after reparameterization

## Earliest Honest Layer

Several ugly outputs are hanging on one knob.
Name the knob first.

## Fast Move

1. Name the shared value `k`.
2. Rewrite each visible quantity as a function of `k`.
3. Compare, eliminate, or check options at the `k`-level instead of the original variable level.

## Compression Move

Typical burden deletion:

- many expressions -> one hidden scalar
- many variables -> one comparison axis
- explicit reconstruction -> option elimination or threshold check
- symbolic clutter -> latent-parameter picture

## Level Transfer

- early level: set the common thing to one easy symbol and simplify
- university level: collapse many visible quantities into one latent degree of freedom
- research level: reduce a multi-parameter surface to one controlling parameter before full analysis

## Cross-Domain Analogue

- debugging: many symptoms tied to one root setting or one broken dependency
- strategy: many metrics moving with one underlying driver
- science/modeling: several observables controlled by one hidden state variable

## Where It Transfers

- logarithmic equalities
- exponential chains
- trigonometric equal-value systems
- hidden-control-variable systems
- any multi-variable equality with one latent freedom

## Failure Mode

- the equalities are only local or conditional
- domain restrictions get hidden by reparameterization
- extra independent constraints remain after compression
- the hidden variable helps describe the system but does not actually control the asked target

## Verification Bill

- check domain after substitution
- check monotonicity / comparison axis if the problem becomes an ordering problem
- if using sample values of `k`, state why the options are separated by those landmarks

## Seed Examples

- 2025 新高考 I 卷 第8题
- 2024 新高考 I 卷 第18题（1） as an adjacent structural seed

## Neighbor Primitives

- `comparison-axis reduction`
- `one-control-variable reduction`
- `aggregate-first`

## Transfer Promise

This primitive should activate across different surfaces:

- equal-value algebra problems
- shared-output function systems
- latent-parameter inequality / threshold problems
- multivariable models controlled by one hidden state
- any problem where many visible quantities are just shadows of one knob
