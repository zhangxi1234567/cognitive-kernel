# AGC012F Prefix Median - Blind Test Plan

**Goal:** Run a fresh strict blind test on `AGC012F - Prefix Median` using only the allowed boundary readset and evaluate whether the runtime now stays layerwise project-skill-owned without giving up mid-problem.
**Approach:** Reset the test environment, materialize an isolated blind package for the AGC problem, run a new blind-solving agent, and inspect only the fresh runtime artifacts.
**Estimated Total Time:** 35 minutes

## Checkpoint 1: Reset
- [ ] Task 1: Close active agents (~2 min)
  - **Action:** Shut down any currently open blind-testing or analysis agents.
  - **Verify:** No active task lane remains from previous tests.
- [ ] Task 2: Delete old blind test artifacts (~3 min)
  - **Action:** Clear `tmp/` test outputs while keeping unrelated helper folders intact.
  - **Verify:** Only the preserved helper directory remains.

## Checkpoint 2: Fresh AGC Blind Package
- [ ] Task 3: Create/update the AGC blind case file (~3 min)
  - **Action:** Materialize a local problem file for `AGC012F - Prefix Median`.
  - **Verify:** File exists under `blind_cases/agc/`.
- [ ] Task 4: Build a fresh manifest and isolated package/run dirs (~5 min)
  - **Action:** Replace the canonical problem entry with the AGC blind case and run `prepare_blind_package.py`.
  - **Verify:** Packaging report shows 41 entries, zero forbidden, and bootstrapped runtime state.

## Checkpoint 3: Blind Solve
- [ ] Task 5: Spawn a fresh blind solver agent (~2 min)
  - **Action:** Give the agent only the isolated package/run dirs and the boundary readset.
  - **Verify:** Agent starts without repository-wide context.
- [ ] Task 6: Monitor and inspect fresh runtime artifacts (~10 min)
  - **Action:** Track `runtime_state.json`, `runtime_state.events.jsonl`, `runtime_skill_trace.md`, and `runtime_solve_trace.md`.
  - **Verify:** Determine whether the run cleanly closes or exactly where it fails.

## Checkpoint 4: Verification
- [ ] Task 7: Summarize closure status and layerwise ownership (~5 min)
  - **Action:** Report whether the run stayed project-skill-owned layer by layer and whether it avoided giving up mid-problem.
  - **Verify:** Final report cites only the fresh AGC run artifacts.

## Verification Criteria
- [ ] Old test artifacts removed before the run
- [ ] Fresh isolated AGC package contains only allowed files
- [ ] New blind solver reads only from the isolated package/run dirs
- [ ] Final assessment is based only on the fresh AGC runtime artifacts
