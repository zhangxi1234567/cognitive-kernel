# Primitive Semantics Runtime - Implementation Plan

**Goal:** Strengthen the runtime from primitive-name orchestration toward mechanism-semantic control without turning it into a workflow or tactic shelf.
**Approach:** Add a thin primitive semantics registry, expose it through host-readable tools, and let the guard use semantics as weak bias/validation context rather than as a route script.
**Estimated Total Time:** 35-50 minutes

## Checkpoint 1: Add a thin primitive semantics layer
- [x] Task 1: Define a minimal semantics schema for live primitive families (~5 min)
  - **Action:** Add a small registry file that maps canonical primitive families to mechanism-facing fields only.
  - **Verify:** Registry covers the current executable primitive set without adding route order or solve scripts.
- [x] Task 2: Keep the semantics thin and non-procedural (~3 min)
  - **Action:** Limit fields to mechanism identity, wake conditions, controller questions, and misuse warnings.
  - **Verify:** No field prescribes fixed multi-step execution.

## Checkpoint 2: Integrate semantics into runtime surfaces
- [x] Task 3: Load semantics from runtime guard without breaking existing control logic (~6 min)
  - **Action:** Add a small loader/helper layer for primitive semantics and expose selected summaries to the report.
  - **Verify:** `build_report()` still succeeds and semantics appear only as descriptive bias/readout.
- [x] Task 4: Expose semantics in host-facing primitive/catalog readers (~5 min)
  - **Action:** Extend the relevant tool readouts so hosts can inspect primitive semantics directly.
  - **Verify:** Tool payloads include semantics summaries for current live primitives or catalog families.

## Checkpoint 3: Align docs with the new layer
- [x] Task 5: Document the semantics boundary (~5 min)
  - **Action:** Update runtime docs to describe semantics as a thin mechanism layer, not a route shelf.
  - **Verify:** Docs stay aligned with code and explicitly reject procedural regression.

## Checkpoint 4: Verify behavior
- [x] Task 6: Run targeted CLI checks (~5 min)
  - **Action:** Exercise the report/catalog/primitive readers against a representative state file.
  - **Verify:** Outputs are valid JSON and include semantics where expected.
- [x] Task 7: Confirm no workflow regression (~3 min)
  - **Action:** Review outputs for route-order or tactic-shelf drift.
  - **Verify:** The new layer biases recognition and interpretation, but does not prescribe a pipeline.

## Verification Criteria
- [x] Primitive semantics are represented in code
- [x] Runtime readouts can surface semantics to hosts
- [x] Existing control loop remains intact
- [x] No fixed route order or solve pipeline was introduced
