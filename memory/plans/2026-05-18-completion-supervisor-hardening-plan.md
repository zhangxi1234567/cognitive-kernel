# Completion Supervisor Hardening - Implementation Plan

**Goal:** Make the runtime refuse to stop while the task-level gap is still live, not just while a local anti-release guard is active.
**Approach:** Strengthen runtime continuation supervision around unfinished gaps, broaden recompetition triggers, and lock the behavior with regression tests before widening any loop budgets.
**Estimated Total Time:** 45 minutes

## Checkpoint 1: Confirm Current Failure Shape
- [ ] Task 1: Pin the existing early-stop behavior in `runtime_consume.py` (~5 min)
  - **Action:** Inspect `run_bind_local_once()`, `stalled_runtime_continuation()`, and `pending_runtime_execution_contract()`.
  - **Verify:** Can point to the current one-round continuation cap and non-retrying branches.
- [ ] Task 2: Find the existing tests around stalled continuation (~5 min)
  - **Action:** Read the `tests/test_runtime_guard.py` cases covering `stalled_runtime_continuation()` and `run_bind_local_once()`.
  - **Verify:** Can name the current expectations that only reopen competition once.

## Checkpoint 2: Harden Supervisor Continuation
- [ ] Task 3: Add a stronger unfinished-gap continuation signal (~10 min)
  - **Action:** Update `tools/runtime_consume.py` so continuation can be driven by live task gap evidence such as `resume_bridge`, `current_debt`, `current_seam`, and supervisory controls, not only a narrow refusal-string whitelist.
  - **Verify:** New logic clearly distinguishes “unfinished, keep going” from “invalid/refuse honestly”.
- [ ] Task 4: Expand continuation behavior to cover more live blocker states (~10 min)
  - **Action:** Allow multi-round recompetition within a bounded supervisor budget, and make `land_local` refusal paths eligible for continuation just like bind/spend refusal paths.
  - **Verify:** `run_bind_local_once()` no longer hard-stops after the first reopen when the completion gap is still explicit.

## Checkpoint 3: Lock Behavior With Tests
- [ ] Task 5: Add regression tests for repeated continuation under a live gap (~10 min)
  - **Action:** Extend `tests/test_runtime_guard.py` with cases for multi-round recompetition and `land_local` retry behavior under an unfinished supervised gap.
  - **Verify:** Tests fail before the code change and pass after it.
- [ ] Task 6: Run focused verification (~5 min)
  - **Action:** Run the affected pytest slice, then the existing runtime test files.
  - **Verify:** All targeted tests pass and no pre-existing runtime assertions regress.

## Verification Criteria
- [ ] The runtime keeps a bounded continuation loop while `release_veto` is active and the task gap is still explicit.
- [ ] `land_local` blocker/refusal paths are no longer unconditional stop points.
- [ ] Regression tests cover the new continuation expectations.
- [ ] Focused pytest verification passes.
