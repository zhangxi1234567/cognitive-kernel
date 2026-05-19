# Ordinary Operation Contract - Implementation Plan

**Goal:** Make “ordinary methods are subordinate tools, not skill owners” an explicit runtime contract across subjects, not just a derivative-specific heuristic.
**Approach:** Add explicit ordinary-operation families and subordinate-operation policy surfaces, then update execute-local/state-shaping checks to reason over those families instead of relying mainly on keyword alarms.
**Estimated Total Time:** 90 minutes

## Checkpoint 1: Scope The Contract
- [ ] Task 1: Re-read the ordinary-fallback and role-split paths (~5 min)
  - **Action:** Inspect `tools/runtime_state.py`, `tools/runtime_guard.py`, and current execute-local tests.
  - **Verify:** The exact entry points for ordinary-operation classification and policy injection are identified.
- [ ] Task 2: Split write boundaries for parallel work (~5 min)
  - **Action:** Keep production changes local; delegate test updates to a separate agent.
  - **Verify:** No parallel task shares a write target with another task.

## Checkpoint 2: Add Explicit Ordinary-Operation Semantics
- [ ] Task 3: Introduce ordinary-operation families (~15 min)
  - **Action:** Classify ordinary actions into reusable families such as symbolic binding, local calculus probe, case split, enumeration, algebraic manipulation, and equation solving.
  - **Verify:** A worked step can be mapped to one or more ordinary-operation families without depending on a single keyword.
- [ ] Task 4: Project subordinate-operation policy from the live skill layer (~15 min)
  - **Action:** Add explicit `allowed_subordinate_operation_families_if_any` / related policy to the live role split or lighting surface.
  - **Verify:** The current layer exposes which ordinary-operation families may appear as subordinate helpers.
- [ ] Task 5: Enforce the policy in execute-local and state-shaping (~20 min)
  - **Action:** Allow ordinary operations only when the current owner still visibly holds the sentence/layer and the operation family is allowed by the live policy.
  - **Verify:** Helper operations like derivative/check or symbolic binding pass only when subordinate, and fail when they try to own the layer.

## Checkpoint 3: Update Runtime Messages And Tests
- [ ] Task 6: Improve coaching/counter-question copy so it references policy, not just examples (~10 min)
  - **Action:** Replace narrow “设/求导” framing with a broader “ordinary machinery” contract while keeping examples.
  - **Verify:** Rejection/coaching text still explains the failure clearly across disciplines.
- [ ] Task 7: Update and extend tests (~15 min)
  - **Action:** Add tests for allowed subordinate helpers and forbidden ownership-stealing ordinary moves beyond derivative.
  - **Verify:** Tests cover at least one non-calculus ordinary helper and one forbidden fallback.

## Checkpoint 4: Verify
- [ ] Task 8: Run focused tests for ordinary-operation behavior (~5 min)
  - **Action:** Run execute-local/state-shaping ordinary-fallback tests first.
  - **Verify:** Updated ordinary-operation semantics hold.
- [ ] Task 9: Run the full test suite (~5 min)
  - **Action:** Run `pytest -q`.
  - **Verify:** All tests pass.

## Verification Criteria
- [ ] Ordinary operations are classified into explicit families
- [ ] The live skill layer exposes subordinate-operation policy
- [ ] Ordinary helpers are accepted only when subordinate to current-layer ownership
- [ ] Ordinary fallback is still rejected
- [ ] Tests pass
