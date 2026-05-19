# Gaokao Two-Pass Retest - Implementation Plan

**Goal:** Fix the closure/materialization bug, then produce two fresh gaokao blind runs that both qualify with no post-handoff nudges.
**Approach:** Narrow runtime fix first, then rebuild fresh case-specific packages and verify two consecutive qualified runs on separate fresh run directories.
**Estimated Total Time:** 45 minutes

## Checkpoint 1: Repair Closure Promotion
- [x] Task 1: Inspect closure/materialization state transitions (~5 min)
  - **Action:** Trace `bind-local`, `execute-local`, `land-local`, and `materialize-asked-medium`.
  - **Verify:** Root cause identified with exact state transition that prevents asked-medium promotion.
- [x] Task 2: Patch closure candidate promotion (~5 min)
  - **Action:** Update runtime logic so seam-targeted closure bites that explicitly close onto the asked medium can be promoted back into asked-medium closure.
  - **Verify:** Targeted regression tests pass.

## Checkpoint 2: Clean And Rebuild Fresh Blind Surfaces
- [x] Task 1: Remove existing gaokao blind artifacts (~3 min)
  - **Action:** Delete current gaokao blind package/run tmp directories, manifests, and reports.
  - **Verify:** No stale gaokao blind package/run artifacts remain under `tmp/`.
- [x] Task 2: Create case-specific manifests (~4 min)
  - **Action:** Materialize one manifest for `gaokao_2024_new_i_t19` and one for `gaokao_2026_math_final`.
  - **Verify:** Each manifest contains exactly one gaokao problem file plus the allowed live surface.
- [x] Task 3: Build two fresh package/run pairs (~5 min)
  - **Action:** Run `tools/prepare_blind_package.py` separately for pass1 and pass2.
  - **Verify:** Each run dir contains a fresh `runtime_state.json` and matching clean sidecars.

## Checkpoint 3: Run Two Consecutive Qualified Blind Tests
- [x] Task 1: Run pass 1 on `gaokao_2024_new_i_t19` (~8 min)
  - **Action:** Launch one fresh blind agent with only the package surface and no follow-up messages.
  - **Verify:** Pass 1 produces qualified runtime evidence and a qualified solve trace.
- [x] Task 2: Run pass 2 on `gaokao_2026_math_final` (~8 min)
  - **Action:** Launch a second fresh blind agent with only the second package surface and no follow-up messages.
  - **Verify:** Pass 2 also produces qualified runtime evidence and a qualified solve trace.

## Verification Criteria
- [x] The closure promotion bug no longer leaves `final.md` as pre-existing bypass output.
- [x] Both blind runs are fresh and isolated from each other.
- [x] No post-handoff nudges or extra messages are sent to the blind agents.
- [x] Two consecutive gaokao questions qualify before stopping.
