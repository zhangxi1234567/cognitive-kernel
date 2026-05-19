# Primitive Semantics

This file is not a tactic shelf.

It exists only to give the live runtime a thin mechanism-facing semantic layer
for the primitive families that are already executable.

The source-of-truth machine-readable registry lives at:

- `runtime/primitive_semantics.json`

That registry should stay small and descriptive.

Its job is not to prescribe a route.

Its job is only to say, for each live primitive family:

- what kind of mechanism it is trying to expose
- what controller-question it naturally asks
- what kinds of local situations tend to wake it
- what one cheap honest touch often tests it
- and what misuse pattern should make the runtime distrust it

## Allowed Effect

Primitive semantics may help the runtime:

- prefer mechanism-facing labels over archive filename recall
- expose why a primitive is live on the current carrier
- surface one or two controller-questions to the host
- surface one or two honest local touches to the host
- warn when a primitive is being used in a fake or decorative way
- keep primitive competition locally interpretable without turning that competition into a route bracket
- mention one tiny finite probe only as a cheap honest touch for the current primitive hypothesis

## Forbidden Drift

Primitive semantics must not become:

- a fixed solve order
- a prerequisite chain
- a route planner
- a per-domain recipe book
- a prompt script
- a flat menu of all archive ideas
- a default "try small cases" reflex
- a second solver that replaces mechanism compression with enumeration

If a semantics entry starts answering:

- what to do second
- what to do after failure
- which domain this always owns
- or how to complete a whole solve

then it has already drifted out of thin runtime semantics and back into workflow.

## Runtime Boundary

The runtime may carry these semantics through:

- `primitive_field_if_any`
- `primitive_competition_if_any`
- `control_signals.operator_bias`
- `control_signals.primitive_control`
- `tools/runtime_primitive.py`
- `tools/runtime_controller.py`
- `tools/runtime_catalog.py`

But the live state should still stay smaller than the registry itself.

State names what is live now.
Semantics explain what that live thing means.

That boundary should stay intact.
