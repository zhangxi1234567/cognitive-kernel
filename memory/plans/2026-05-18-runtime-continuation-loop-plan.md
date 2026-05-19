# Runtime Continuation Loop - Implementation Plan

**Goal:** When a problem is unfinished and the runtime is about to stop on a stalled local bite, reopen one more project-skill competition round instead of giving up.
**Approach:** Add a narrowly gated continuation path in `runtime_consume.py` that only triggers on unfinished runtime stall/refusal, then protect it with regression tests.
**Estimated Total Time:** 40 minutes

## Checkpoint 1: Continuation Gate
- [ ] Task 1: Read the current refusal and hop-limit exits in `run_bind_local_once()` (~5 min)
  - **Action:** Confirm the exact refusal reasons and state predicates that should count as “unfinished but stalling”.
  - **Verify:** Can state the trigger conditions without guessing.
- [ ] Task 2: Add a helper that decides whether stalled runtime should continue (~5 min)
  - **Action:** Encode a narrow gate using `release_veto`, runtime evidence, refusal reason, and active control signals.
  - **Verify:** Helper returns false for finished/invalid states and true for live stalled states.

## Checkpoint 2: Recompetition Reopen
- [ ] Task 3: Add one-shot stalled-competition reopening logic (~10 min)
  - **Action:** Reopen the current layer by clearing stale local competition surfaces and refreshing the live primitive field instead of returning terminal refusal immediately.
  - **Verify:** Reopen path records why it continued and only runs once per stall event.
- [ ] Task 4: Wire `run_bind_local_once()` to use the continuation path on stalled refusal / hop-limit exits (~5 min)
  - **Action:** Intercept bind/spend refusal and structural-hop-limit exits, then route through the new helper when allowed.
  - **Verify:** Non-stalled paths behave the same; stalled unfinished path now returns continuation-shaped output.

## Checkpoint 3: Regression Proof
- [ ] Task 5: Add targeted tests for continuation gating (~5 min)
  - **Action:** Cover unfinished stalled state vs finished state vs invalid state.
  - **Verify:** Tests fail without the new behavior and pass with it.
- [ ] Task 6: Add a `run_bind_local_once()` regression for reopened competition (~5 min)
  - **Action:** Assert that stalled unfinished runtime does not stop as terminal refusal.
  - **Verify:** Returned payload shows continuation/recompetition metadata.

## Verification Criteria
- [ ] Continuation triggers only when `release_veto` is still live and the task is unfinished
- [ ] Finished or invalid states still stop normally
- [ ] No project-external “skills” are introduced
- [ ] `python -m pytest tests/test_runtime_guard.py -q` passes
- [ ] `python -m pytest -q` passes
