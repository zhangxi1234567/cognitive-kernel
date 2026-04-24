# Wu Boshi Bottom-Layer Why Laws

This file defines the deeper `why` behind recurring reduction moves.

Its purpose is:

- distinguish method names from bottom-layer logic
- explain why recurring tricks work across many surfaces
- keep the library from stopping at "what to do" without answering "why this works"

## Core Rule

The following are **not yet** bottom-layer logic by themselves:

- periodicity compression
- parameter separation
- guess then verify
- dynamic to static
- symmetry extremum

Those are visible route families.

The bottom-layer logic sits beneath them and answers:

- what hidden structural law makes this route lawful and reusable?

## 1. Why Symmetry Often Produces Extremum

Bottom-layer logic:

- asymmetry creates extra degrees of freedom
- when the target penalizes imbalance, the balanced configuration is the place where first-order imbalance disappears
- once fake directional bias is removed, the extreme point often sits at the symmetric configuration

What this explains:

- equal-case first
- centered placement
- isosceles / equilateral / midpoint / average guesses
- "对称出极值"

Deeper law:

- symmetry kills directional drift
- extremum often appears where no direction has unfair advantage

## 2. Why Periodicity Compresses

Bottom-layer logic:

- if the governing rule repeats exactly, then later behavior contains no new structural information beyond one cycle
- the rest is only repetition bookkeeping

What this explains:

- period blocks
- one-cycle counting
- large-index value reduction
- periodic sum compression

Deeper law:

- repeating law means finite generator
- global complexity is fake once the cycle is found

## 3. Why Parameter Separation Works

Bottom-layer logic:

- a parameterized family often contains:
  - one fixed skeleton
  - one moving scalar shell
- if the parameter can be isolated, the fixed geometric/algebraic controller becomes visible

What this explains:

- 恒过定点
- family-wide fixed line / fixed point
- dynamic line -> fixed circle / fixed relation

Deeper law:

- apparent motion is often shell motion
- the real controller is the parameter-free structure left behind after separation

## 4. Why Guessing The Answer Can Be Lawful

Bottom-layer logic:

- after enough structure has already compressed the search space, the candidate set becomes small and shaped
- in that regime, guessing is not gambling
- it is selecting from a structurally narrow live set

What this explains:

- answer-shape pressure
- special-case guessed fixed point
- guess answer then substitute seal

Deeper law:

- guessing becomes lawful when uncertainty has already been structurally collapsed
- the proof burden then shifts from full construction to decisive elimination

## 5. Why Dynamic Can Become Static

Bottom-layer logic:

- many moving stories are governed not by chronology itself but by:
  - invariant transitions
  - state adjacency
  - conserved flow
  - final reachability structure
- if order is not the real burden, the process can be frozen into a static object

What this explains:

- process -> state graph
- game story -> tree / flow map
- probability story -> matching or state-space object

Deeper law:

- time is often shell
- transition structure is often the real object

## 6. Why Thick Objects Can Collapse To Thin Readouts

Bottom-layer logic:

- the target is often linear or monotone in one smaller controller
- once that controller is found, the rest of the object becomes carrying shell

What this explains:

- area -> line
- solid -> section
- vector -> projection
- full object -> one target relation

Deeper law:

- not every dimension pays the proof bill
- one shadow often carries the target-relevant burden

## 7. Why Boundary / Tangency Reveals Mechanism

Bottom-layer logic:

- interior configurations contain slack
- boundary configurations remove slack
- when slack disappears, the equality or hinge that was hidden in the interior becomes exposed

What this explains:

- tangent case
- endpoint case
- coincidence case
- extreme-position route finding

Deeper law:

- boundaries are not merely checks
- they are zero-slack revealers of the controlling relation

## 8. Why Parity Splits Structure

Bottom-layer logic:

- sign-flip symmetry separates behavior into two non-mixing components
- once odd and even parts are split, many fake interactions vanish

What this explains:

- odd/even decomposition
- symmetric cancellation
- parity-driven periodicity

Deeper law:

- parity is a structural decomposition operator
- it cuts one object into two simpler invariant behaviors

## 9. Why Recurrence Can Collapse To Fixed Structure

Bottom-layer logic:

- many recurrences are not about endless updating
- they are about one stable law underneath the update:
  - invariant
  - fixed point
  - arithmetic/geometric model
  - short cycle

What this explains:

- recurrence -> model class
- recurrence -> invariant
- recurrence -> periodic or geometric law

Deeper law:

- repeated update is often shell
- stable law is the real object

## 10. Why Elimination Under Ambiguity Can Still Be Lawful

Bottom-layer logic:

- not every hard problem needs full certainty at the first move
- sometimes visible constraints already kill most of the candidate world
- then structural elimination is an honest reduction step

What this explains:

- bounded uncertainty handling
- fast option elimination
- kill wrong worlds before full proof

Deeper law:

- certainty can be built by shrinking the live candidate set
- not only by full derivation

## Hard Rule

Future additions should be tested at two levels:

1. visible method
   - what move appeared?
2. bottom-layer why
   - what deeper structural law made that move work?

If level 2 cannot be named, the library is still too shallow.
