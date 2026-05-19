# Runtime Competition Refactor - Implementation Plan

**Goal:** Remove early candidate pruning and hard-coded combo favoritism so skill lighting, competition, and execution legitimacy better follow the per-layer takeover model.
**Approach:** Keep the current runtime shape, but widen internal candidate fields, add generic combo competition, relax wording-dependent execution gates, and make persisted-vs-derived boundaries explicit in code.
**Estimated Total Time:** 90 minutes

## Checkpoint 1: Plan The Runtime Competition Refactor
- [ ] Task 1: Re-read the affected guard/state paths and map the exact write boundaries (~5 min)
  - **Action:** Inspect `tools/runtime_guard.py`, `tools/runtime_state.py`, and `runtime/control_state.schema.json`.
  - **Verify:** The concrete target functions/constants to change are listed before edits start.
- [ ] Task 2: Split work into disjoint lanes for parallel execution (~5 min)
  - **Action:** Keep `runtime_guard.py` local, delegate `runtime_state.py` and persisted/readout boundary work to separate agents.
  - **Verify:** No delegated task shares a write target with another delegated task.

## Checkpoint 2: Fix Lighting And Competition
- [ ] Task 3: Remove early internal candidate truncation (~10 min)
  - **Action:** Stop returning after the first 2-3 primitive hits in internal competition paths; keep broad fields internally and only summarize later for public readouts.
  - **Verify:** Internal candidate builders can carry a significantly larger set than before.
- [ ] Task 4: Replace fixed combo favoritism with generic combo generation/scoring (~25 min)
  - **Action:** Introduce a generic pair/trio combo evaluation path based on active skills, coactivation hints, and projected gain, then feed it into skill competition.
  - **Verify:** Competition can rank combos that were not explicitly hard-coded beforehand.
- [ ] Task 5: Let advanced attack skills stay visible in frontstage competition (~10 min)
  - **Action:** Expand frontstage lit-skill treatment so second-order attack skills are not filtered out of visible competition/lighting surfaces.
  - **Verify:** `特殊值探针` / `对称消元` / `投影读出`-style skills can survive sanitization when they are active.

## Checkpoint 3: Fix Execution Legitimacy And State Boundaries
- [ ] Task 6: Relax literal wording requirements in `execute-local` (~15 min)
  - **Action:** Allow state-backed skill ownership evidence to satisfy legitimacy checks without forcing templated textual skill mentions.
  - **Verify:** Legitimate skill-owned steps can pass even when wording differs, while post-hoc labeling still fails.
- [ ] Task 7: Make persisted-vs-derived boundaries explicit (~10 min)
  - **Action:** Add explicit derived-readout-only key guards and clear separation logic around persisted state handling.
  - **Verify:** Persisted state rejects derived readout surfaces with a targeted error instead of relying on implicit architectural knowledge.

## Checkpoint 4: Update Tests And Verify
- [ ] Task 8: Update/add tests for the new competition and legitimacy behavior (~10 min)
  - **Action:** Extend `tests/test_runtime_guard.py` and other affected tests to cover broad lighting, generic combos, and relaxed wording legitimacy.
  - **Verify:** New assertions fail without the refactor and pass after it.
- [ ] Task 9: Run the verification suite (~5 min)
  - **Action:** Run focused tests first, then the full test suite if needed.
  - **Verify:** All relevant tests pass.

## Verification Criteria
- [ ] Internal lighting no longer truncates candidate fields before real arbitration
- [ ] Combo competition is not limited to a manually curated tuple list
- [ ] Advanced attack skills can remain visible in lighting/competition surfaces
- [ ] `execute-local` legitimacy no longer depends on literal skill-name narration alone
- [ ] Persisted and derived runtime layers are explicitly separated in code
- [ ] Tests pass
