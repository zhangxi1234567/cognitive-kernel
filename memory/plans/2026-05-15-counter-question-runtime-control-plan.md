# Counter-Question Runtime Control - Implementation Plan

**Goal:** Make runtime control actively block ordinary fallback moves by asking whether they are needed, denying them when they are not, and affirming the current skill-owned move instead.
**Approach:** Extend existing skill-lighting and execute-local enforcement so the live layer can surface a counter-question, an explicit denial of ordinary actions like `设` or `求导`, and a positive handoff to the currently owned skill action.
**Estimated Total Time:** 35 minutes

## Checkpoint 1: Control Surface Mapping
- [ ] Task 1: Inspect existing false-first and accountability surfaces (~5 min)
  - **Action:** Review runtime functions that emit `false_first_skill_if_any`, `false_skill_reason`, and `accountability_nudge_if_any`.
  - **Verify:** We have concrete function names and know which payloads already carry control coaching.
- [ ] Task 2: Confirm execute-local enforcement seams (~5 min)
  - **Action:** Review `execute-local` refusal helpers and identify the narrowest place to add ordinary-action denial checks.
  - **Verify:** We know whether to enforce at text validation, layer payload generation, or both.

## Checkpoint 2: Runtime Control Implementation
- [ ] Task 3: Add counter-question coaching payload (~5 min)
  - **Action:** Extend the live layer/control payload with fields for counter-question, ordinary-action denial, and skill-positive handoff when a generic move is tempting.
  - **Verify:** The payload is present in runtime state/report surfaces for applicable layers.
- [ ] Task 4: Enforce denial in execute-local (~10 min)
  - **Action:** Reject worked steps that lean on denied ordinary moves without the required skill-positive handoff, using the live layer combo as authority.
  - **Verify:** A worked step that says `设`/`求导` without the controlling skill framing is refused.

## Checkpoint 3: Regression Coverage
- [ ] Task 5: Add negative tests for ordinary fallback regrowth (~5 min)
  - **Action:** Add tests where a live skill-owned layer still tries to continue with `设`/`求导`-style fallback language.
  - **Verify:** The new tests fail before the patch and pass after.
- [ ] Task 6: Add positive tests for explicit handoff phrasing (~5 min)
  - **Action:** Add tests where worked steps explicitly say the ordinary move is unnecessary and then continue with the correct skill action.
  - **Verify:** These worked steps are accepted and preserved.

## Verification Criteria
- [ ] All checkpoints complete
- [ ] Runtime payloads expose the counter-question control pattern when applicable
- [ ] Execute-local rejects ordinary fallback phrasing on skill-owned layers
- [ ] Positive handoff phrasing is accepted
- [ ] `tests/test_runtime_guard.py` passes
- [ ] `tests/test_prepare_blind_package.py` passes
