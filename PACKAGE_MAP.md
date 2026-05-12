# Wu Boshi Perspective Package Map

This package is being split by function, not by topic.

The goal is not to build a math tactic shelf.

The goal is to preserve a thin cross-domain metacognitive layer while quarantining research-heavy archives away from solve-time behavior.

## Live Layers

### `runtime/`

Runtime-facing thin-bias documents.

These files may shape attention, but must not become:

- a route menu
- a tactic shelf
- a workflow
- a chapter-based teaching ladder

Key live anti-impostor surfaces:

- `runtime/FALSE_ESSENCE_ELIMINATION.md`
- `runtime/CONFLICT_RESOLUTION.md`

Key live runtime-control surfaces:

- `runtime/COGNITIVE_CONSTITUTION.md`
- `runtime/COGNITIVE_DYNAMICS.md`
- `runtime/CONTROL_STATE.md`
- `runtime/PRIMITIVE_SEMANTICS.md`
- `runtime/PRIMITIVE_RUNTIME_COVERAGE.md`

Key live runtime readers / bridges:

- `tools/runtime_guard.py`
- `tools/runtime_state.py`
- `tools/runtime_next_touch.py`
- `tools/runtime_reselection.py`
- `tools/runtime_self_check.py`
- `tools/runtime_primitive.py`
- `tools/runtime_controller.py`
- `tools/runtime_inhibition.py`
- `tools/runtime_catalog.py`
- `tools/runtime_consume.py`

These belong to the live layer because they expose current-layer control state,
primitive state, and closure pressure directly.
They should still remain thinner than archive research and must not become a route machine.

### `benchmarks/`

Verification and transfer evidence.

These files exist to test whether the layer actually survives across:

- math
- coding / debugging
- research / mechanism extraction

Key adversarial benchmark surfaces:

- `benchmarks/MINIMAL_VERIFICATION_PROTOCOL.md`
- `benchmarks/FALSE_ESSENCE_DRIFT_TESTS.md`

### `compat/`

Compatibility-side doctrine that still matters for host behavior, but is too implementation-adjacent or host-specific to live inside the thin runtime constitution.

These files should stay smaller and more operational than archive material, while still avoiding solve-time tactic control.

### Root compatibility files

The root files:

- `AGENTS.md`
- `CLAUDE.md`
- `SKILL.md`
- `COMPATIBILITY.md`
- `skill.manifest.json`

should stay small and point inward to the thin runtime layer.
Their job is to point the host toward the right live reading surface,
not to replace that surface with a host-side summary.

## Archived Layer

### `references/`

`references/` is a research archive, not a solve-time surface.

It contains:

- seed extraction
- primitive studies
- public-source mining
- benchmark notes
- historical experiments
- naming systems that are useful for research but dangerous as runtime menus

The archive may explain where the layer came from.

It must not decide what the live run does next.

Some legacy boundary notes may be copied into `compat/` as the package split is clarified.

## Split Rule

If a file teaches:

- order
- selection
- composition
- named route recall
- explicit tactical activation

then it belongs in archive or research, not in runtime.

If a file changes:

- what the model notices first
- what it distrusts first
- what it compresses first
- what it verifies before settling

then it may belong in runtime.
