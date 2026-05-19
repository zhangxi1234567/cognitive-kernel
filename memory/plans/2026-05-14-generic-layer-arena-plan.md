# Generic Layer Arena - Implementation Plan

**Goal:** Make first layer and every later runtime-owned layer re-light skills through the same arena mechanism, without degrading into a pipeline or exam-template machine.
**Approach:** Extract the reusable arena-building logic from `derive_first_layer_arena`, then route first-touch, bound, recomposed, and explicit event-owned layers through the same object-led skill-lighting surface.
**Estimated Total Time:** 70 minutes

## Checkpoint 1: Identify Reusable Arena Inputs
- [ ] Task 1: Audit arena-specific logic in `derive_first_layer_arena` (~5 min)
  - **Action:** Separate focus-target selection, lighting aggregation, and authorized-touch rebuild behavior.
  - **Verify:** Clear list of logic that should become generic.
- [ ] Task 2: Audit post-transition layer surfaces (~5 min)
  - **Action:** Compare `fresh_blind_first_touch`, `bound_program`, and `takeover_recomposition` paths.
  - **Verify:** Clear list of per-layer inputs a generic arena must accept.

## Checkpoint 2: Extract Generic Layer Arena
- [ ] Task 3: Introduce a generic arena derivation helper in `runtime_guard.py` (~10 min)
  - **Action:** Add a helper that builds an arena from current layer object, explicit layer surface, skill field, competition, authority, and lighting.
  - **Verify:** Helper can describe both first-touch and post-transition layers.
- [ ] Task 4: Rewire `derive_first_layer_arena` to use the generic helper (~5 min)
  - **Action:** Keep the public function name stable while delegating to the generic helper.
  - **Verify:** Existing first-layer behavior remains intact.

## Checkpoint 3: Reuse Arena Across Later Layers
- [ ] Task 5: Feed explicit event-owned layers through the generic arena (~10 min)
  - **Action:** Make recomposed/bound layers reuse the same focus-target, verify-touch, and authorized-touch logic.
  - **Verify:** Later-layer arena focus stays on the newly exposed object/gap instead of drifting to asked-medium.
- [ ] Task 6: Keep anti-pipeline invariants explicit (~5 min)
  - **Action:** Preserve one-bite locality, object-led transition reasoning, and false-first/readout suppression.
  - **Verify:** No required sequence or mechanical skill-calling order is introduced.

## Checkpoint 4: Extend Tests
- [ ] Task 7: Add/adjust focused tests for per-layer re-lighting (~10 min)
  - **Action:** Cover first layer, post-land layer, and post-spend layer with the same arena expectations.
  - **Verify:** Tests fail if later layers stop re-lighting or if asked-medium steals focus too early.
- [ ] Task 8: Update stale assertions that conflict with the new execution surface (~5 min)
  - **Action:** Align tests with `execute_local -> land_local` where appropriate.
  - **Verify:** Test expectations reflect current runtime semantics.

## Checkpoint 5: Verification
- [ ] Task 9: Run focused arena tests (~10 min)
  - **Action:** Execute targeted runtime-guard cases around re-lighting and non-pipeline behavior.
  - **Verify:** Command exits successfully.
- [ ] Task 10: Run full `tests.test_runtime_guard` suite (~5 min)
  - **Action:** Execute the full file.
  - **Verify:** Suite passes.

## Verification Criteria
- [ ] First layer and later layers both derive their active skill combo from the same arena-building logic.
- [ ] Post-transition layers can introduce or promote new skills naturally from the rewritten object.
- [ ] Arena focus remains object-led and does not default to asked-medium while structure is still live.
- [ ] Runtime outputs remain local and non-pipeline.
- [ ] Focused and full runtime tests pass.
