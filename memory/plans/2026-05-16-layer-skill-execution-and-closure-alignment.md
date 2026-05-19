# Layer Skill Execution And Closure Alignment - Implementation Plan

**Goal:** Make fresh-blind runtime stop treating skills as mere labels on late closure layers, keep asked-medium closure ownership honest, and align pending-action / trace-export behavior with real runtime materialization.
**Approach:** Re-read the execution chain and blind artifacts in parallel, lock the observed drift with regression tests, patch closure-owner normalization plus materialization gating, then rerun tests and do a second multi-agent reread.
**Estimated Total Time:** 90-140 minutes

## Checkpoint 1: Freeze The Failure Surfaces
- [ ] Task 1: Trace bind/land/materialize/trace behavior in `tools/runtime_state.py` (~10 min)
  - **Action:** Confirm where direct asked-medium closure inherits a structural owner instead of a closure owner.
  - **Verify:** I can point to the exact normalization gap and the contradictory pending action.
- [ ] Task 2: Parallel-read adjacent logic with subagents (~10 min)
  - **Action:** Dispatch agents for execution-chain drift, closure/trace dead-end analysis, and test coverage.
  - **Verify:** Each agent returns concrete findings or confirms a surface is coherent.
- [ ] Task 3: Freeze the write set (~5 min)
  - **Action:** Convert the failure into a short checklist covering closure-owner normalization, pending contract action naming, solve-trace export gating, and affected tests.
  - **Verify:** The checklist explains both “skill became label only” and “closure looked done but still not honestly released”.

## Checkpoint 2: Lock Regressions
- [ ] Task 1: Update the direct-closure bind contract test (~8 min)
  - **Action:** Replace the old expectation that asked-medium closure still requires `execute_local`.
  - **Verify:** The test now demands the real materialization action.
- [ ] Task 2: Add a regression for solve-trace premature export (~8 min)
  - **Action:** Capture a state with qualified runtime events but still-pending asked-medium closure.
  - **Verify:** Solve-trace export is blocked until the closure is materially ready.
- [ ] Task 3: Add a regression for closure-owner normalization after same-carrier landing (~10 min)
  - **Action:** Capture the deformed-style case where `final.md` is reopened with combo containing `精确封口` but the owner/leading skill drifts to a structural skill.
  - **Verify:** The rebound touch and bound layer are normalized back to `精确封口`.

## Checkpoint 3: Patch Runtime Behavior
- [ ] Task 1: Normalize direct asked-medium closure ownership (~15 min)
  - **Action:** Add one helper that promotes direct closure bites to a closure owner/combo when the asked-medium closure is genuinely in play.
  - **Verify:** Closure owner, combo, gate binding, and layer leading skill agree.
- [ ] Task 2: Align pending-action and materialization behavior (~12 min)
  - **Action:** Stop advertising `execute_local` for asked-medium closure and route pending closure toward explicit materialization instead.
  - **Verify:** Runtime consume/report surfaces no longer point to a refused action.
- [ ] Task 3: Tighten solve-trace qualification (~10 min)
  - **Action:** Refuse solve-trace export when a runtime-owned closure is still pending, even if prior step events are individually qualified.
  - **Verify:** Trace output cannot outrun actual closure.

## Checkpoint 4: Verify And Re-read
- [ ] Task 1: Run focused runtime tests (~10 min)
  - **Action:** Execute the relevant `tests.test_runtime_guard` subset, then the full module if the subset passes.
  - **Verify:** Test commands exit cleanly.
- [ ] Task 2: Second multi-agent reread (~10 min)
  - **Action:** Ask fresh/updated agents to reread the modified surfaces and report any remaining inconsistency.
  - **Verify:** Remaining findings are either fixed immediately or called out explicitly.

## Verification Criteria
- [ ] Asked-medium closure never advertises a forbidden `execute_local` action.
- [ ] Direct closure bites targeting the asked medium normalize to `精确封口` ownership when closure is the real live owner.
- [ ] Solve-trace export waits for honest runtime closure instead of only checking per-step qualification.
- [ ] Regression tests cover the new failure family and pass.
