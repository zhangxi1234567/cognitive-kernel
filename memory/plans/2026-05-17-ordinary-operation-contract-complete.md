# Ordinary Operation Contract - Completion Report

**Date Completed:** 2026-05-17
**Original Goal:** Make “ordinary methods are subordinate tools, not skill owners” an explicit runtime contract across subjects, not just a derivative-specific heuristic.
**Final Result:** The runtime now classifies ordinary operations into reusable families, projects subordinate-operation policy from the live skill layer, and enforces that policy during `execute-local` / state-shaping checks so ordinary machinery can assist but not steal current-layer ownership.

## Completion Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Checkpoints | 4 | 4 |
| Tasks | 9 | 9 |
| Time | 90 min | 85 min |

## Verification Checklist

- [x] All tasks complete
- [x] Quality criteria met
- [x] Full test suite passed

## What Was Delivered

- Broader ordinary-operation markers and regexes in `tools/runtime_state.py`
- Explicit ordinary-operation families such as `symbol_binding`, `local_calculus_probe`, `case_split`, `equation_solving`, and `algebraic_manipulation`
- Live role-split policy fields describing allowed subordinate operation families and blocked ordinary fallbacks
- `execute-local` / state-shaping checks that use current-layer policy instead of only narrow derivative wording
- New tests proving non-derivative subordinate helpers can pass while ownership-stealing ordinary moves still fail

## Blockers Encountered

1. The persisted `lighting_if_any.role_split_if_any` path originally dropped any new ordinary-operation policy metadata
   Resolution: extended validation and projection paths so the policy survives state/report round-trips.
2. Existing tests were too derivative-specific
   Resolution: added `case split`-based ordinary-helper tests and broadened old assertions to “ordinary machinery” semantics.

## Lessons Learned

- The key shift was not just blocking more keywords; it was turning ordinary operations into named families governed by the live owner layer.
- This makes the runtime less math-special-case and more reusable across disciplines, even though the family policy is still heuristic rather than fully learned.
