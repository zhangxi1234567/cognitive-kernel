# Wu Boshi First-Jump Main Carrier Selection

This file defines one of the most decisive moments in strong solving:

- the first jump to the main carrier

Many later differences between an ordinary route and a ruthless route come from one early choice:

- what object becomes the main carrier of the solve?

If that first carrier is too large, later compression becomes harder.

If that first carrier is close to minimal, later compression becomes much easier.

## 1. Core Preference

Very strong routes often win because they choose the right main carrier early.

The project should therefore strongly prefer asking:

- what is the smallest carrier that can already hold the controller and the target?

before it starts building ordinary objects.

Use:

- `target-complete-main-carrier.md`

when the missing distinction is:

- a carrier that is merely smaller

versus:

- a carrier that is small enough to finish the target.

## 2. What A Main Carrier Is

A main carrier is the object or representation that carries most of the later solve burden.

Examples:

- one direction parameter instead of two full points
- one displacement variable instead of full coordinates
- one relation instead of the full object
- one determinant form instead of lengths plus heights
- one latent axis instead of many visible quantities

The main carrier is not merely:

- the first notation introduced

It is:

- the structure that most of the route will actually live on

## 3. Why This Matters

If the first carrier is too heavy, later steps often regress into:

- full point reconstruction
- chord length plus distance
- full coordinate elimination
- ordinary symbolic expansion

If the first carrier is close to minimal, later steps can often stay small.

That is one reason first-jump choice matters so much.

## 4. Carrier Choice Questions

Before committing to a main route, ask:

1. is there a smaller carrier than the full object?
2. can the target already be expressed on that smaller carrier?
3. can the controller already be read there?
4. if I choose the larger carrier, what later burden will I be forced to rebuild?

These are not fixed steps.

They are high-value orientation questions.

## 5. Typical Main-Carrier Upgrades

Prefer upgrades such as:

- full line -> one slope parameter
- full points -> one displacement parameter
- full coordinates -> translated local coordinates around the fixed anchor
- object family -> one carrier relation
- final geometric quantity -> determinant / projection / readout form

These upgrades often decide whether the route later feels ordinary or ruthless.

## 6. Final Preference

The project should increasingly learn:

- choose the smallest serious main carrier early

because later compression quality often depends on that first jump.
