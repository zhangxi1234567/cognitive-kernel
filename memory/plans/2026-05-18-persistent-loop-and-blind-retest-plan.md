# Persistent Loop And Blind Retest - Implementation Plan

**Goal:** Push the runtime closer to a true difficult-problem continuation loop, then verify on a fresh strict blind gaokao run whether every layer still lights project skills, competes, and executes to closure.
**Approach:** Repair state-layer stalled continuation first, then reduce final-layer pseudo-skill takeover by `精确封口`, then retest using a fresh isolated blind package and run directory.
**Estimated Total Time:** 90 minutes

## Checkpoint 1: State-Layer Continuation
- [ ] Task 1: Add one-shot stalled reopen inside `command_bind_local()` (~10 min)
  - **Action:** When `bind_local` has no unique concrete bite but the task is unfinished, reopen one current-layer competition round before refusing.
  - **Verify:** A stalled bind can retry once without turning into a retry ladder.
- [ ] Task 2: Add one-shot stalled reopen inside `command_spend_local()` (~10 min)
  - **Action:** Mirror the same behavior for thinner-carrier spend refusal.
  - **Verify:** Spend refusal can reopen once when the layer is still live.

## Checkpoint 2: Final-Layer Ownership
- [ ] Task 3: Remove or demote final-layer `精确封口` skill-owner promotion where possible (~15 min)
  - **Action:** Preserve real project-skill combos at closure-facing surfaces instead of re-promoting `精确封口` as winner/owner.
  - **Verify:** Final layer still exposes real project skills in live combo/owner fields.
- [ ] Task 4: Update regression tests for continuation and closure ownership (~10 min)
  - **Action:** Extend tests around stalled continuation and final-layer ownership.
  - **Verify:** Targeted pytest passes.

## Checkpoint 3: Fresh Blind Retest
- [ ] Task 5: Delete old blind test artifacts and create a fresh gaokao blind package (~10 min)
  - **Action:** Rebuild package/run dirs using only canonical boundary files.
  - **Verify:** Packaging report shows expected entry count and zero forbidden files.
- [ ] Task 6: Spawn a fresh blind-solving agent confined to the new package/run surface (~10 min)
  - **Action:** Let the agent solve only the gaokao problem inside the isolated package.
  - **Verify:** New runtime traces and state files are produced in the fresh run dir.
- [ ] Task 7: Inspect the new traces and decide if the implementation is complete (~15 min)
  - **Action:** Check whether front, middle, and final layers all show project-skill lighting, competition, and execution to closure.
  - **Verify:** If not complete, loop back to Checkpoint 1/2.

## Verification Criteria
- [ ] Stalled unfinished states reopen at state layer instead of only at consumer layer
- [ ] Finished or invalid states still stop
- [ ] Final-layer live owner/combo no longer collapses into `精确封口` as a skill
- [ ] Fresh blind package contains only allowed files
- [ ] Fresh blind run produces runtime evidence and either closes honestly or exposes the next real gap
