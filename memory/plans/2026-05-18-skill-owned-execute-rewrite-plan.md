# Skill-Owned Execute Rewrite - Implementation Plan

**Goal:** Make execute-local retries rewrite themselves from the refusal reason instead of repeating ordinary fallback language.
**Approach:** Parse the execute-local refusal into "denied ordinary move + current skill handoff" signals, feed that into worked-step synthesis, and lock it with focused supervisor tests.
**Estimated Total Time:** 25 minutes

## Checkpoint 1: Refusal Signal Extraction
- [ ] Task 1: Inspect current execute-local refusal formats and identify reusable markers for denied ordinary action and leading-skill handoff. (~5 min)
  - **Action:** Read runtime_state refusal builders and runtime_consume worked-step synthesis.
  - **Verify:** I can point to exact strings/markers that the rewrite should mirror.
- [ ] Task 2: Add a small parser/helper for extracting retry guidance from execute-local refusal text. (~5 min)
  - **Action:** Implement a helper near worked-step synthesis.
  - **Verify:** Helper returns stable fields for ordinary-action denial and skill handoff.

## Checkpoint 2: Worked-Step Rewrite
- [ ] Task 3: Thread the last execute-local refusal into the supervisor retry path. (~5 min)
  - **Action:** Pass refusal text into strict retry synthesis.
  - **Verify:** Retry synthesis receives the real refusal reason after a rejected execute-local round.
- [ ] Task 4: Rewrite strict worked-step synthesis to explicitly deny the rejected ordinary move and hand control back to the current skill combo. (~5 min)
  - **Action:** Update worked-step text generation with refusal-aware wording.
  - **Verify:** Generated text contains both denial markers and skill-positive handoff markers.

## Checkpoint 3: Regression Coverage
- [ ] Task 5: Add focused tests for refusal-aware execute-local retries. (~5 min)
  - **Action:** Extend runtime_until_done supervisor tests.
  - **Verify:** Tests fail without the new rewrite behavior and pass with it.

## Verification Criteria
- [ ] Supervisor retries do not blindly repeat the same ordinary fallback wording after refusal.
- [ ] Generated strict worked_step includes explicit denial of the rejected ordinary action.
- [ ] Generated strict worked_step explicitly hands control to the live current-layer skill.
- [ ] Focused pytest coverage passes.
