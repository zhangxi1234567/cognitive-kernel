# Blind Self-Activation Fix - Implementation Plan

**Goal:** Make the runtime internalize taught skill composition enough to self-activate on fresh blind problems without turning into a pipeline or exam-template machine.
**Approach:** Re-read the JOI/gaokao teaching notes and current runtime code, isolate the true first-step self-activation gap, patch the activation path conservatively, then blind-test with a many-file package and iterate until the behavior is acceptable.
**Estimated Total Time:** 90-150 minutes

## Checkpoint 1: Reconstruct The Taught Signal
- [ ] Task 1: Read the JOI teaching note closely (~5 min)
  - **Action:** Extract what was taught about layerwise skill composition, wake order, and anti-pipeline constraints.
  - **Verify:** A concise list of runtime-relevant lessons exists.
- [ ] Task 2: Read the gaokao teaching note closely (~5 min)
  - **Action:** Extract what was taught about non-routine transfer, closure resistance, and compositional activation.
  - **Verify:** A concise list of runtime-relevant lessons exists.
- [ ] Task 3: Read blind-boundary constraints (~5 min)
  - **Action:** Confirm what must stay outside true blind packages and how blind runs should be evaluated.
  - **Verify:** Clear guardrails for later testing are written down.

## Checkpoint 2: Map The Current Activation Path
- [ ] Task 4: Trace fresh-blind entrypoints in runtime code (~5 min)
  - **Action:** Read the bootstrap, bind, spend, landing, and consume path in `tools/runtime_state.py`.
  - **Verify:** The current first-step activation chain is summarized.
- [ ] Task 5: Trace competition/authority derivation in guard code (~5 min)
  - **Action:** Read the primitive/skill field, competition, inhibition, authority, and closure path in `tools/runtime_guard.py`.
  - **Verify:** The exact gate that blocks or weakens self-activation is named.
- [ ] Task 6: Compare code behavior against teaching signal (~5 min)
  - **Action:** Identify where the runtime still behaves like external hints or post-hoc competition rather than internalized first-step wake-up.
  - **Verify:** One small, testable change target is chosen.

## Checkpoint 3: Implement Conservative Activation Fix
- [ ] Task 7: Patch the first-step activation logic (~10 min)
  - **Action:** Modify code so taught local skill combinations can self-activate more naturally on fresh blind entry without becoming a rigid workflow.
  - **Verify:** The patch preserves local competition and avoids hard-coded route order.
- [ ] Task 8: Patch any supporting trace/authority logic (~10 min)
  - **Action:** Update adjacent logic only if needed to keep runtime evidence honest and layer composition explicit.
  - **Verify:** Runtime traces still describe real local transitions.
- [ ] Task 9: Run syntax and focused smoke checks (~5 min)
  - **Action:** Run compile/smoke tests on touched files.
  - **Verify:** No syntax or immediate runtime failures remain.

## Checkpoint 4: Blind-Test And Iterate
- [ ] Task 10: Prepare a fresh blind package with many files (~5 min)
  - **Action:** Use the canonical blind package helper and ensure the teaching notes are not leaked into the readset.
  - **Verify:** Package and run directories are fresh and auditable.
- [ ] Task 11: Run a real blind solve (~10 min)
  - **Action:** Give the solver only the blind package surface and let it attempt the target gaokao problem.
  - **Verify:** Runtime artifacts and solve artifacts are produced or the failure mode is clearly visible.
- [ ] Task 12: Audit the blind run (~5 min)
  - **Action:** Check whether the run shows genuine self-activation rather than hand-held route replay or silence.
  - **Verify:** A pass/fail judgment with concrete evidence exists.
- [ ] Task 13: Iterate if the behavior is still off (~15 min)
  - **Action:** Tighten the activation logic and re-run blind testing until the result is acceptable.
  - **Verify:** The final run meets the behavioral bar.

## Verification Criteria
- [ ] JOI/gaokao teaching notes were actually read and reflected in the fix
- [ ] No new pipeline/stage-machine behavior was introduced
- [ ] No new task-specific template or exam machine path was introduced
- [ ] Fresh blind run shows more natural self-activation than before
- [ ] Runtime evidence remains explicit and auditable
