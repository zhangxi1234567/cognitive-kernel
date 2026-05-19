# Runtime Competition Refactor - Completion Report

**Date Completed:** 2026-05-17
**Original Goal:** Remove early candidate pruning and hard-coded combo favoritism so skill lighting, competition, and execution legitimacy better follow the per-layer takeover model.
**Final Result:** Internal lighting is broader, combo competition is synthesized generically instead of only via fixed tuples, advanced attack skills remain visible in frontstage surfaces, `execute-local` can rely on state-backed ownership evidence, and persisted-vs-derived boundaries are explicit in both schema and runtime validation.

## Completion Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Checkpoints | 4 | 4 |
| Tasks | 9 | 9 |
| Time | 90 min | 95 min |

## Verification Checklist

- [x] All tasks complete
- [x] Quality criteria met
- [x] Full test suite passed

## What Was Delivered

- Broader internal primitive lighting and hint merging in `tools/runtime_guard.py`
- Generic combo candidate synthesis and combo-aware projected-gain scoring
- Frontstage visibility for advanced attack skills such as `特殊值探针`, `对称消元`, and `函数原型匹配`
- State-backed fresh-blind `execute-local` legitimacy in `tools/runtime_state.py`
- Explicit persisted-vs-derived boundary in `runtime/control_state.schema.json`, `runtime/CONTROL_STATE.md`, and guard validation
- Regression tests updated to the new ownership semantics

## Blockers Encountered

1. Broad combo synthesis initially leaked non-lit candidates into explicit lit-only competition lanes
   Resolution: tightened lit-candidate filtering to keep leader ownership inside the explicit lit set.
2. Fresh-blind execute tests encoded the old “literal skill wording” contract
   Resolution: replaced them with state-backed ownership and off-combo relabeling tests.

## Lessons Learned

- The largest semantic gap was not missing primitives, but early candidate truncation before real arbitration.
- Persisted state and derived readout separation needed to be enforced both structurally and behaviorally.
