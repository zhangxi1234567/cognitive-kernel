# Primitive Semantics Runtime - Completion Report

**Date Completed:** 2026-05-11
**Original Goal:** Strengthen the runtime from primitive-name orchestration toward mechanism-semantic control without turning it into a workflow or tactic shelf.
**Final Result:** Added a thin primitive semantics registry, surfaced it through the runtime readers, and tightened the guard so semantics now weakly shape control bias and distrust without becoming solve order.

## Completion Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Checkpoints | 4 | 4 |
| Tasks | 7 | 7 |
| Time | 35-50 min | ~1 session |

## Verification Checklist

- [x] All tasks complete
- [x] Quality criteria met
- [x] Verification evidence captured

## What Was Delivered

- Added machine-readable primitive semantics in `runtime/primitive_semantics.json`.
- Added runtime boundary docs in `runtime/PRIMITIVE_SEMANTICS.md` and synced runtime/top-level host docs.
- Exposed primitive semantics through `tools/runtime_guard.py`, `tools/runtime_primitive.py`, `tools/runtime_controller.py`, and `tools/runtime_catalog.py`.
- Added a public-kernel articulation in `runtime/ACTIVE_KERNEL.md` and surfaced it through `tools/runtime_catalog.py`.
- Strengthened `tools/runtime_guard.py` so:
  - `control_signals.operator_bias.cheapest_reality_check` can come from primitive `cheapest_honest_touch`
  - text-fallback primitive fields now emit mechanism-touch and misuse-risk warnings
  - derived primitive actions prefer semantics-led touch language instead of harder route-like phrasing
  - `control_signals` now mirrors live primitive-field / primitive-competition state before heuristic pressure is added
  - derived same-carrier pressure no longer masquerades as a default host action; explicit bind and derived candidate are now separated
- Strengthened live-state evidence discipline so:
  - `primitive_field_if_any` can carry `evidence_basis`
  - `carrier_handoff_if_any.warm_field` can carry `evidence_basis`
  - lexical hint, cheap check, explicit hint, and state witness are no longer implicitly treated as the same kind of evidence
- Strengthened `tools/runtime_state.py` so:
  - `bind-local` realigns gate ownership to the bound program itself
  - `bind-local` no longer acts as a silent chooser between same-carrier bind and thinner-carrier handoff
  - `handoff` no longer mixes `active_pressures` and `primitive_hints` into one field
- Strengthened host-facing readers so:
  - `runtime_consume.py` inspect-only mode is now a neutral current-surface readout instead of implicitly choosing reselection/next-touch
  - `runtime_next_touch.py` and `runtime_reselection.py` now surface `primitive_semantics`, `primitive_competition_semantics`, and `primitive_control`

## Verification Evidence

- `py_compile` passed for:
  - `tools/runtime_guard.py`
  - `tools/runtime_state.py`
  - `tools/runtime_consume.py`
  - `tools/runtime_primitive.py`
  - `tools/runtime_controller.py`
  - `tools/runtime_catalog.py`
  - `tools/runtime_next_touch.py`
  - `tools/runtime_reselection.py`
- `python tools/runtime_guard.py tmp/consume_default_test_unbound.json`
  - confirmed `primitive_semantics`, `primitive_competition_semantics`, and control-signal questions/anti-patterns
- `python tools/runtime_primitive.py tmp/consume_default_test_unbound.json`
  - confirmed live primitive readout carries semantics
- `python tools/runtime_controller.py tmp/consume_default_test_unbound.json`
  - confirmed controller readout carries live primitive semantics
- `python tools/runtime_catalog.py`
  - confirmed catalog-wide semantics coverage for executable primitive families
- `python tools/runtime_guard.py tmp/retest_text_fallback.json`
  - confirmed text-fallback warnings now include honest mechanism touch + misuse warning
- `python tools/runtime_guard.py tmp/retest_competition_live.json`
  - confirmed unresolved primitive competition stays explicitly plural in `control_signals`
- `python tools/runtime_controller.py tmp/retest_competition_live.json`
  - confirmed `primitive_control` and live competition state reach the host-facing controller readout
- `python tools/runtime_consume.py tmp/retest_competition_live.json`
  - confirmed inspect-only now exposes the current explicit reselection surface neutrally rather than forcing a next step
- `python tools/runtime_next_touch.py tmp/bind_local_realign_test.json`
  - confirmed next-touch readout now carries primitive semantics + primitive control
- `python tools/runtime_reselection.py tmp/retest_handoff.json`
  - confirmed reselection readout now carries primitive semantics + primitive control
- `python tools/runtime_catalog.py`
  - confirmed public kernel families and direct/alias families are separated in host-facing catalog output

## Blockers Encountered

1. Child-agent availability was uneven.
   Resolution: continued with one successful subagent review plus local verification.

## Lessons Learned

- The most valuable next-step hardening was not adding more tools, but making the existing runtime speak semantics more consistently at the exact local action surface.
- `text_fallback` was the weakest seam; validating that seam gave the clearest evidence that the layer stayed descriptive rather than procedural.
- The final identity gap was less about adding reasoning power and more about cleaning the boundary between public kernel, derived pressure, explicit bind, and debug choreography.
