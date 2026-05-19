# Frontload Lighting And Fresh Blind Retest - Implementation Plan

**Goal:** Make runtime truly light skills before competition, then validate the change with a from-zero blind rerun of the cylinder-two-spheres problem until the layer handoff is genuinely smooth.
**Approach:** First tighten the generator order so current-layer candidate skills are frontloaded before winner selection, then clear old artifacts, rebuild the blind package, rerun the target problem from scratch, and iterate until the trace shows problem-born layer ownership instead of pipeline-like narration.
**Estimated Total Time:** 65 minutes

## Checkpoint 1: Read and pin the exact generator gap
- [ ] Task 1: Re-read lighting/competition/arena code with the new standard (~5 min)
  - **Action:** Inspect `tools/runtime_guard.py` around `derive_skill_lighting_surface`, `derive_skill_competition`, `derive_layer_arena`, and `derive_first_layer_arena`.
  - **Verify:** We can state exactly where winner generation still happens before real frontloaded lighting.
- [ ] Task 2: Re-read blind-run entrypoints and cleanup surfaces (~5 min)
  - **Action:** Inspect `tools/prepare_blind_package.py`, target `tmp/` state, and any rerun docs/scripts for the gaokao Q14 package.
  - **Verify:** We know which old artifacts to delete and which command path recreates the blind run from zero.

## Checkpoint 2: Move “light first, compete second” into generator logic
- [ ] Task 3: Refactor lighting so current-layer candidates are explicit before winner choice (~8 min)
  - **Action:** Update `derive_skill_lighting_surface` to build a problem-facing lit-candidate set from active skills, probe discipline, and current object pressure before reading the winner.
  - **Verify:** Lighting output can exist even before a final winner is declared, and readout/control-only surfaces are demoted to false-first or support-only.
- [ ] Task 4: Refactor competition to rank only within lit candidates plus necessary partners (~8 min)
  - **Action:** Update `derive_skill_competition` so `winning_skill_if_any` is selected from already-lit candidates and does not let generic write/readout/helper surfaces steal first takeover.
  - **Verify:** Winner selection depends on frontloaded lit candidates, not the other way around.
- [ ] Task 5: Keep layer arena and state payload aligned with the new order (~6 min)
  - **Action:** Update `derive_layer_arena` / `build_layer_composition_state_payload` as needed so candidate skills, role split, and verify touch remain explicit and consistent.
  - **Verify:** Layer payloads expose `candidate_skills_if_any`, `role_split_if_any`, and `verify_touch_if_any` without needing refusal-side reconstruction.

## Checkpoint 3: Regression coverage for frontloaded lighting
- [ ] Task 6: Add tests that prove lighting can precede winner selection (~6 min)
  - **Action:** Extend `tests/test_runtime_guard.py` with focused cases for frontloaded candidate lighting, support-only demotion, and competition within lit candidates.
  - **Verify:** New tests fail before the patch and pass after it.
- [ ] Task 7: Run the guard/runtime test suite (~4 min)
  - **Action:** Run `python -m pytest tests\\test_runtime_guard.py -q`.
  - **Verify:** All tests pass.

## Checkpoint 4: Fresh blind rerun from zero
- [ ] Task 8: Delete prior target-run artifacts and recreate the blind package (~5 min)
  - **Action:** Remove the old `tmp/gaokao_2025_q14_run_*` target artifacts used for this check, then regenerate the blind package with the project script.
  - **Verify:** The next run starts from a clean state with no reused trace/state files.
- [ ] Task 9: Run the target blind test and inspect the new trace (~8 min)
  - **Action:** Execute the fresh blind solve path for the cylinder-two-spheres problem and read `runtime_trace.md`, `runtime_skill_trace.md`, and output state.
  - **Verify:** Mid-layer ownership naturally fronts `projection` over generic conservation narration, and final closure naturally fronts `limit_boundary` or another honest closure owner over `picture`.
- [ ] Task 10: Iterate until the run is acceptable or a new blocker is isolated (~10 min)
  - **Action:** If the new run still regresses, patch the next smallest cause and rerun from zero again.
  - **Verify:** We stop only when the blind rerun actually reflects the intended layered skill behavior.

## Verification Criteria
- [ ] Lighting exists as a real current-layer candidate field before final winner selection.
- [ ] Competition chooses within already-lit problem-facing candidates and necessary partners.
- [ ] Layer payloads keep explicit main/support/check structure.
- [ ] Fresh blind rerun is rebuilt from zero, not reused from stale artifacts.
- [ ] In the fresh gaokao Q14 run, middle ownership feels like `projection` on the thinner carrier and final ownership feels like `limit_boundary` or another honest closure owner, not generic picture/write narration.
- [ ] `python -m pytest tests\\test_runtime_guard.py -q` passes.
