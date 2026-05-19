# Runtime Closure Reread And Hardening - Implementation Plan

**Goal:** Make fresh blind runtime solving complete its closure path honestly, keep solve-trace qualification aligned with actual owned steps, and clean up adjacent runtime inconsistencies found by a broader reread.
**Approach:** Re-read the closure/materialization and trace-qualification surfaces in parallel, lock the newly observed failure modes with tests, patch the runtime so closure ownership and asked-medium materialization stay consistent after real layer changes, then rerun blind-style checks and a second multi-agent reread.
**Estimated Total Time:** 120-160 minutes

## Checkpoint 1: Re-read And Freeze The Failure Shape
- [ ] Task 1: Read the closure/materialization path in `tools/runtime_state.py` and `tools/runtime_guard.py` (~8 min)
  - **Action:** Trace how `bind-local`, `land-local`, `materialize-asked-medium`, and `trace --format solve-markdown` decide closure ownership and evidence.
  - **Verify:** I can point to the exact functions where gaokao and deformed diverged.
- [ ] Task 2: Parallel-read adjacent runtime areas with subagents (~8 min)
  - **Action:** Dispatch agents for closure/materialization, trace qualification, and broad runtime reread.
  - **Verify:** Each agent returns concrete findings or confirms a surface is coherent.
- [ ] Task 3: Freeze the targeted write set (~5 min)
  - **Action:** Convert the observed failures into a code checklist covering closure owner selection, asked-medium auto-materialization, role-split consistency, and solve-trace export rules.
  - **Verify:** The checklist explains both blind-run failures without hand-waving.

## Checkpoint 2: Lock The Regressions
- [ ] Task 1: Add focused tests for closure materialization after owned landing (~10 min)
  - **Action:** Capture the gaokao-style case where `final.md` is authorized but not materially marked as touched/materialized.
  - **Verify:** The new test fails before the fix in theory and passes after.
- [ ] Task 2: Add focused tests for closure role-split consistency and solve-trace qualification (~10 min)
  - **Action:** Capture the deformed-style case where `final.md` bind succeeds but solve-trace still refuses because the leading skill and role split disagree.
  - **Verify:** The tests distinguish valid closure from pseudo-closure.
- [ ] Task 3: Add one broader guard test if reread finds a neighboring mismatch (~8 min)
  - **Action:** Cover any adjacent inconsistency surfaced by the reread that could reopen the same bug family.
  - **Verify:** The new behavior is explicit and stable.

## Checkpoint 3: Patch Runtime Closure And Trace Logic
- [ ] Task 1: Repair asked-medium closure promotion/materialization in `tools/runtime_state.py` (~15 min)
  - **Action:** Ensure runtime-owned closure on the asked medium becomes materially realized when the closure is actually ready.
  - **Verify:** State/output fields and sidecar evidence agree after materialization.
- [ ] Task 2: Repair role-split and leading-skill alignment around closure (~15 min)
  - **Action:** Make closure qualification compute one consistent owner/check split so genuine closure steps are not rejected as mismatched.
  - **Verify:** A valid closure bind no longer trips the role-split refusal.
- [ ] Task 3: Clean adjacent report/trace surfaces revealed by reread (~12 min)
  - **Action:** Update any nearby reporting or qualification logic that still speaks as if closure happened when the evidence does not, or vice versa.
  - **Verify:** Runtime report, skill trace, and solve trace tell the same story.

## Checkpoint 4: Re-read, Rerun, And Verify
- [ ] Task 1: Run targeted runtime tests (~10 min)
  - **Action:** Execute the focused `unittest` subset for the touched closure/trace behavior, then the full `tests.test_runtime_guard` suite if the subset is clean.
  - **Verify:** Test commands exit cleanly.
- [ ] Task 2: Re-run representative blind-style checks (~20 min)
  - **Action:** Repackage and rerun the gaokao and deformed fresh blind cases enough to confirm the fixed runtime path.
  - **Verify:** The new traces no longer show the specific gaokao/deformed refusal patterns.
- [ ] Task 3: Do a second multi-agent reread after the patch (~10 min)
  - **Action:** Dispatch agents to reread the modified surfaces and adjacent code for anything still inconsistent.
  - **Verify:** Remaining findings are either fixed immediately or explicitly called out.

## Verification Criteria
- [ ] Fresh blind closure can materialize the asked medium when a real runtime-owned closure is ready.
- [ ] Solve-trace qualification agrees with runtime-owned closure instead of rejecting a valid closure bind.
- [ ] Runtime report, skill trace, solve trace, and state/output fields stay consistent.
- [ ] Targeted tests cover the new failure modes and pass.
- [ ] Representative blind reruns no longer show the original gaokao and deformed gaps.

User already selected execution mode: **Dispatch Multiple Agents (parallel)**.
