# Layer Smoothness Repair - Implementation Plan

**Goal:** Make JOI/gaokao-style runtime solving keep every layer genuinely lit and smoothly handed off, especially for the 2025 gaokao II Q14 cylinder-spheres run.
**Approach:** Tighten runtime layer qualification so first takeover cannot stay single-skill, mid-layer combos must stay object-specific and thinner-carrier-owned, and final closure cannot degenerate into a generic write-answer layer.
**Estimated Total Time:** 35 minutes

## Checkpoint 1: Re-anchor the teaching chain
- [ ] Task 1: Pin the required layer chain from JOI and gaokao notes (~4 min)
  - **Action:** Map the expected first-layer, recomposition-layer, and closure-layer signals from the reference notes to current runtime fields.
  - **Verify:** We have a concrete list of fields/behaviors that current run_v2 violates.
- [ ] Task 2: Identify the exact qualification gates in runtime code (~4 min)
  - **Action:** Inspect `tools/runtime_state.py` around `_skill_composition_step_refusals`, takeover recomposition, and final closure handling.
  - **Verify:** We can point to the smallest code surfaces that admit the bad chain.

## Checkpoint 2: Tighten layer qualification
- [ ] Task 3: Block single-skill first takeover from counting as a real lit layer (~6 min)
  - **Action:** Adjust first-layer / bind-local qualification so a lone `witness`-style bind cannot become a promoted layer step.
  - **Verify:** The first layer in the target pattern would need a real combo or a more truthful current-layer owner.
- [ ] Task 4: Force thinner-carrier ownership after recomposition (~6 min)
  - **Action:** Tighten recomposition acceptance so the next layer must expose a sharper object and avoid broad retrospective combo narration.
  - **Verify:** Container-to-section style ownership is favored over generic wide combo packaging.
- [ ] Task 5: Prevent final closure from degenerating into a write-answer layer (~6 min)
  - **Action:** Require one explicit closure/root-selection style current-layer owner before `write` can count as the bound bite.
  - **Verify:** Final layer is still skill-owned before answer materialization.

## Checkpoint 3: Regression coverage and validation
- [ ] Task 6: Add focused tests for layer smoothness (~5 min)
  - **Action:** Extend `tests/test_runtime_guard.py` with cases for single-skill first bind rejection and closure-before-write requirements.
  - **Verify:** New tests fail before the patch and pass after it.
- [ ] Task 7: Run the runtime guard test suite (~3 min)
  - **Action:** Run `python -m pytest tests\\test_runtime_guard.py -q`.
  - **Verify:** Full suite passes.
- [ ] Task 8: Re-run the gaokao blind package or targeted state replay (~5 min)
  - **Action:** Validate that the trace shows smoother layer ownership and less ordinary-solution regrowth.
  - **Verify:** Each layer has a genuine owner and the final layer no longer reads like generic answer writing.

## Verification Criteria
- [ ] First promoted layer is not a lone single-skill placeholder.
- [ ] Recomposition exposes a thinner current controller, not just a wider skill narration.
- [ ] Final closure is skill-owned before `answer.md` materialization.
- [ ] `python -m pytest tests\\test_runtime_guard.py -q` passes.
