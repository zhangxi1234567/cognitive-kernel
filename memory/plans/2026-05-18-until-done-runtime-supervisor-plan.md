# Until-Done Runtime Supervisor - Implementation Plan

**Goal:** Upgrade the runtime from a one-shot local loop into a global until-done supervisor that keeps re-lighting project skills, re-competing, executing, and reseating layers until release is honestly allowed.
**Approach:** Add a structured supervision layer above the existing local primitives, replace string-only stall detection with blocker taxonomy, and extend execution so the supervisor can carry execute-local progress instead of stopping at pending local work.
**Estimated Total Time:** 90 minutes

## Checkpoint 1: Carve Out Supervisor Primitives
- [ ] Task 1: Map the current stop points and reusable loop surfaces (~5 min)
  - **Action:** Re-read `runtime_consume.py`, `runtime_controller.py`, and `runtime_state.py` around `run_bind_local_once()`, `pending_runtime_execution_contract()`, `command_execute_local()`, and `release_allowed`.
  - **Verify:** Can name the exact points where one-shot behavior and external `worked_step` dependence stop progress.
- [ ] Task 2: Define structured supervision helpers (~10 min)
  - **Action:** Introduce a dedicated supervision helper module for completion snapshots, blocker taxonomy, and continuation decisions.
  - **Verify:** One helper surface can explain “why not done yet,” “what action is next,” and “whether to re-compete or continue execution.”

## Checkpoint 2: Build Global Until-Done Loop
- [ ] Task 3: Add a top-level supervisor loop (~15 min)
  - **Action:** Create a runtime entry point that repeatedly executes local loop phases until `release_veto` is false and `release_allowed` is true, instead of treating `run_bind_local_once()` as terminal.
  - **Verify:** The new loop can advance through repeated `bind_local`, `execute_local`, `land_local`, `spend_local`, and materialization phases without exiting after one local cycle.
- [ ] Task 4: Route local stop conditions through blocker taxonomy (~10 min)
  - **Action:** Replace string-only continuations with structured blocker classification for retryable stalls, invalid state, ordinary-operation drift, and honest dead ends.
  - **Verify:** Re-competition and continuation no longer depend on one exact refusal string.

## Checkpoint 3: Remove Manual Execute-Local Dead Stop
- [ ] Task 5: Teach the supervisor to keep execution ownership live (~15 min)
  - **Action:** Extend runtime surfaces so `execute_local` no longer hard-stops at `pending_execute_local`; the supervisor should carry forward the current skill-owned execution contract and support repeated local progress.
  - **Verify:** Pending local work is expressed as a live supervised phase, not as a terminal helper result.
- [ ] Task 6: Preserve multi-skill layer structure across repeats (~10 min)
  - **Action:** Ensure re-lighting/reselection keeps the current layer’s active combo, candidate skills, and role split legible across retries and carrier changes.
  - **Verify:** The loop keeps “main/support/check/ordinary” separation intact instead of collapsing back to generic local narration.

## Checkpoint 4: Lock the Behavior With Tests
- [ ] Task 7: Add regression tests for until-done supervision (~15 min)
  - **Action:** Extend runtime tests to cover repeated multi-layer progress, structured blocker retries, and non-terminal execute-local supervision.
  - **Verify:** Tests fail before the supervisor changes and pass after them.
- [ ] Task 8: Run focused verification and document outcomes (~10 min)
  - **Action:** Run the affected pytest slices, then the runtime baseline files, and save a completion report.
  - **Verify:** Runtime tests stay green and the completion report explains what changed and what still remains bounded.

## Verification Criteria
- [ ] The runtime can supervise multiple successive layers instead of stopping after one one-shot local cycle.
- [ ] Retry/continue decisions come from structured blocker taxonomy rather than exact refusal wording alone.
- [ ] `execute_local` no longer appears as an automatic terminal dead stop when the task gap is still live.
- [ ] Layerwise multi-skill composition remains visible across re-competition and reselection.
- [ ] Focused runtime pytest verification passes.
