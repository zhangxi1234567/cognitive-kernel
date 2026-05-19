# Closure Combo Refactor - Completion Report

**Date Completed:** 2026-05-17
**Original Goal:** Stop treating `精确封口` as the final owner skill and make asked-medium closure stay owned by real project skill combinations.
**Final Result:** Closure generation, promotion, normalization, and materialization now preserve real project-owned combos instead of collapsing them into a singleton `精确封口` owner. Singleton exact-closure style is rejected, and closure-facing tests were updated to assert combo-owned finalization.

## Completion Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Checkpoints | 3 | 3 |
| Tasks | 7 | 7 |
| Time | 70 min | 65 min |

## Verification Checklist

- [x] All tasks complete
- [x] Quality criteria met
- [x] Full test suite passed

## What Was Delivered

- `tools/runtime_guard.py`
  - closure combo helper now keeps only real project skills
  - closure frontload no longer rewrites the final owner to a singleton pseudo-skill
  - asked-medium closure candidate generation now depends on real combo sources
- `tools/runtime_state.py`
  - closure combo normalization/promotion now preserves real owner + supporting combo
  - singleton exact-closure style is rejected in promote/materialize/finalize paths
  - same-carrier landing no longer feeds `精确封口` back into primitive fields
- `tests/test_runtime_guard.py`
  - closure tests now assert real project-owned finalization semantics

## Blockers Encountered

1. Closure helper changes initially introduced a `NameError` in compiled 读出 generation
   Resolution: explicitly sourced primitive-field and competition candidates from state inside `derive_object_compiled_读出_candidate`.
2. Several old tests still encoded the prior “`精确封口` is the final owner skill” assumption
   Resolution: rewrote those tests to assert combo-owned closure instead.

## Lessons Learned

- The core bug was not merely in `materialize`; it started earlier, where closure combos were being collapsed during candidate generation and frontload promotion.
- Preventing closure collapse also required stopping `精确封口` from leaking back into primitive reselection state.
