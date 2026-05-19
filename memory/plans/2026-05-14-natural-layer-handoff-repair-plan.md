# Natural Layer Handoff Repair - Implementation Plan

**Goal:** Make runtime-owned skill solving preserve winner ownership across layer changes without collapsing into a workflow or ordinary exam-solving pipeline.
**Approach:** Keep the existing competition model, but repair three gaps: winner-driven object rewriting, natural supporting-skill promotion on the next layer, and thinner `authorized_bite` generation that prefers mother-structure readout over ordinary algebraic closure.
**Estimated Total Time:** 75 minutes

## Checkpoint 1: Pin Down Repair Surface
- [ ] Task 1: Audit current winner-to-bite generation in `runtime_guard.py` (~5 min)
  - **Action:** Inspect `derive_skill_authority_bridge`, `derive_bound_program_candidate`, and takeover recomposition paths.
  - **Verify:** Clear list of where picture winners currently regress into algebra-first bites.
- [ ] Task 2: Audit same-carrier landing and recomposition state flow (~5 min)
  - **Action:** Inspect `derive_discipline_contract`, `derive_layer_composition`, and `runtime_state.py` landing/bind refresh logic.
  - **Verify:** Clear list of where next-layer ownership is lost after `land-local`.
- [ ] Task 3: Audit test surface for natural handoff coverage (~5 min)
  - **Action:** Identify gaps in `tests/test_runtime_guard.py` around object rewriting and supporting-skill promotion.
  - **Verify:** List of at least 3 new targeted tests to add.

## Checkpoint 2: Repair Winner-Owned Object Rewriting
- [ ] Task 4: Add heuristics for object-rewriting bites after structure-first winners (~10 min)
  - **Action:** Teach `runtime_guard.py` to prefer geometry/structure/object rewrites when `picture`/`projection`/related winners can compress to a mother object.
  - **Verify:** Generated touch targets stop defaulting to generic algebraic carriers in the targeted scenarios.
- [ ] Task 5: Preserve anti-pipeline boundaries while adding rewrite hints (~5 min)
  - **Action:** Keep outputs one-shot, local, and descriptive-before-prescriptive.
  - **Verify:** No new loop/stage/scheduler semantics appear in runtime outputs.

## Checkpoint 3: Repair Layer-to-Layer Natural Promotion
- [ ] Task 6: Promote supporting skills naturally after same-carrier landing (~10 min)
  - **Action:** Update takeover/landing logic so next-layer candidates can elevate a supporting skill when the rewritten object makes it primary.
  - **Verify:** Post-landing authority can shift from `picture` to a thinner follow-up skill without manual forcing.
- [ ] Task 7: Ensure next-layer gap/object becomes explicit (~10 min)
  - **Action:** Tighten recomposition and layer composition payload generation.
  - **Verify:** `land-local` produces a readable next local object/gap in targeted tests.

## Checkpoint 4: Repair Thin Bite Generation
- [ ] Task 8: Prefer mother-structure readout over ordinary closure (~10 min)
  - **Action:** Refine `authorized_bite` / `bound_program` generation so target objects like polar line / invariant / section readout outrank generic symbolic closure when honestly available.
  - **Verify:** Targeted tests show thinner readout objects winning.
- [ ] Task 9: Guard against turning this into a brush-up exam machine (~5 min)
  - **Action:** Confirm heuristics depend on current-layer object structure, not problem-type templates.
  - **Verify:** Changes are framed by object/skill semantics, not canned gaokao recipes.

## Checkpoint 5: Verification
- [ ] Task 10: Add focused tests (~10 min)
  - **Action:** Add/adjust unit tests in `tests/test_runtime_guard.py`.
  - **Verify:** Tests fail before behavior change and pass after.
- [ ] Task 11: Run focused test suite (~5 min)
  - **Action:** Execute the relevant runtime tests.
  - **Verify:** Test command exits successfully.
- [ ] Task 12: Review results against the original failure mode (~5 min)
  - **Action:** Compare behavior to the blind-run problem shape and summarize remaining risks.
  - **Verify:** Clear statement of what improved and what still remains open.

## Verification Criteria
- [ ] Winner-owned `picture`/structure-first layers can rewrite toward thinner objects instead of collapsing immediately into ordinary algebra.
- [ ] Same-carrier landing exposes a real next local object/gap and can naturally promote a supporting skill.
- [ ] The runtime still stays local, one-shot, and non-pipeline.
- [ ] Focused runtime tests pass.
