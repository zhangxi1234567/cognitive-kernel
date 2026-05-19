# Skill-Owned Execute Rewrite - Completion Report

**Date Completed:** 2026-05-18
**Original Goal:** Make execute-local retries rewrite themselves from the refusal reason instead of repeating ordinary fallback language.
**Final Result:** Supervisor retries now consume execute-local refusal reasons, synthesize denial-plus-handoff worked steps, and avoid replaying ordinary-action wording in strict retries.

## Completion Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Checkpoints | 3 | 3 |
| Tasks | 5 | 5 |
| Time | 25 min | 25 min |

## Verification Checklist

- [x] All tasks complete
- [x] Quality criteria met
- [x] Targeted runtime probes improved

## What Was Delivered

- Added refusal parsing in `tools/runtime_consume.py` so strict execute-local retries can extract the denied ordinary action and the skill handoff named in the rejection text.
- Threaded the last execute-local refusal through `tools/runtime_supervision.py` so retries use the real rejection reason instead of a generic strict toggle.
- Rewrote strict worked-step synthesis to explicitly deny the rejected ordinary move, restore current-layer skill ownership, and avoid echoing ordinary-looking bound-program operations.
- Extended `tests/test_runtime_until_done.py` to verify both refusal threading and refusal-aware strict text synthesis.

## Blockers Encountered

1. The first refusal-aware draft still failed on the real blind-run state because it repeated the raw bound-program operation, which itself contained ordinary-action markers like `case/check`.
   Resolution: strict retries now switch to skill-owned seam-to-signal wording instead of replaying the raw operation text.

## Lessons Learned

- Refusal-aware retries need both semantic guidance and lexical hygiene; replaying an ordinary-looking operation string can retrigger the same guard even after explicit denial.
- The remaining blind-run stop is no longer the ordinary-fallback refusal path; it now sits later in supervisor progress tracking around repeated pending runtime consumption.
