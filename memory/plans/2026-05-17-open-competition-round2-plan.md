# Open Competition Round 2 - Implementation Plan

**Goal:** Push the runtime closer to broad skill lighting, open combo competition, semantic execution validation, and true layer-by-layer reselection.
**Approach:** Remove shortlist-style gating in `runtime_guard.py`, expand combo search/ranking, reduce handwritten reselection shortcuts, and relax wording-bound execute checks in `runtime_state.py` while updating tests to match the new semantics.
**Estimated Total Time:** 120 minutes

## Checkpoint 1: Confirm Boundaries
- [ ] Task 1: Re-read the remaining findings and map them to concrete code sections (~5 min)
  - **Action:** Inspect the filtering, gain-ranking, combo synthesis, follow-up reselection, and execute-local guard paths.
  - **Verify:** Each remaining finding has an implementation target before edits begin.
- [ ] Task 2: Split write scopes for parallel work (~5 min)
  - **Action:** Keep `tools/runtime_guard.py` local; delegate `tools/runtime_state.py` and `tests/test_runtime_guard.py` to separate agents.
  - **Verify:** No parallel task shares a write target.

## Checkpoint 2: Open The Competition Field
- [ ] Task 3: Remove shortlist-style lit/frontload hard filtering (~15 min)
  - **Action:** Make frontloaded/lit sets advisory instead of decisive, and keep a broad internal candidate pool alive through arbitration.
  - **Verify:** Competition can still evaluate non-frontloaded candidates on the same layer.
- [ ] Task 4: Expand combo search depth and breadth (~20 min)
  - **Action:** Generate and score more than just leader-plus-1/2-supporter patterns; let combo objects compete more explicitly.
  - **Verify:** Multi-skill combos beyond shallow support shells can appear and win.
- [ ] Task 5: Reduce handwritten follow-up routing after a peel (~15 min)
  - **Action:** Replace hard-coded post-peel leader choice heuristics with fresh re-competition wherever possible.
  - **Verify:** Reopened layers re-arbitrate instead of inheriting route scripts.

## Checkpoint 3: Strengthen Semantic Execution
- [ ] Task 6: Lower execute-local dependence on wording heuristics (~15 min)
  - **Action:** Let state/action alignment dominate over literal phrasing where the bound program is semantically consumed.
  - **Verify:** Legitimate skill-led execution is accepted even with different wording, while ordinary fallback is still blocked.
- [ ] Task 7: Keep ordinary operations subordinate, not banned by keyword alone (~10 min)
  - **Action:** Distinguish “ordinary operation as subordinate tool” from “ordinary fallback regrowth.”
  - **Verify:** `picture`-owned steps can include helper operations without reclassifying ownership.

## Checkpoint 4: Update Tests And Verify
- [ ] Task 8: Rewrite stale tests that encode shortlist/literal-wording behavior (~15 min)
  - **Action:** Update targeted tests in `tests/test_runtime_guard.py` to assert open competition and semantic ownership instead.
  - **Verify:** The suite expects the new behavior rather than the old hand-coded route assumptions.
- [ ] Task 9: Run focused tests, then the full suite (~20 min)
  - **Action:** Run the changed-area tests first and `pytest -q` last.
  - **Verify:** All tests pass.

## Verification Criteria
- [ ] Frontloaded/lit skills no longer act as hard winner filters
- [ ] Combo competition explores a wider space than leader + 1/2 supporters
- [ ] Post-peel owner selection is freshly re-arbitrated more often
- [ ] `execute-local` legitimacy is more semantic and less wording-bound
- [ ] Tests pass
