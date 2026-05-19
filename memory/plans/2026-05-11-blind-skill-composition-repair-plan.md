# Blind Skill Composition Repair - Implementation Plan

**Goal:** Make fresh blind agents materially more likely to produce genuine layerwise skill-composition traces instead of ordinary solve prose, then verify from a clean slate on the geometry problem.
**Approach:** Investigate the live runtime/docs/handoff gap, patch the narrowest surfaces that currently leave fresh blind runs read-only, and re-test with all prior artifacts deleted.
**Estimated Total Time:** 90 minutes

## Checkpoint 1: Root Cause Audit
- [ ] Task 1: Read the live blind boundary, runtime docs, and JOI composition bridge (~5 min)
  - **Action:** Inspect `BLIND_TEST_BOUNDARY.md`, `SKILL.md`, `runtime/ACTIVE_KERNEL.md`, `runtime/COGNITIVE_DYNAMICS.md`, `runtime/CONTROL_STATE.md`, and `references/joi-layerwise-skill-composition-note.md`.
  - **Verify:** Can state the top 2-3 reasons a fresh blind run falls back to ordinary solving.
- [ ] Task 2: Read the runtime evidence path for event-owned layer composition (~5 min)
  - **Action:** Inspect `tools/runtime_state.py`, `tools/runtime_guard.py`, `tools/runtime_consume.py`, and `tools/runtime_controller.py`.
  - **Verify:** Can point to the exact functions that qualify or refuse a skill-composition step.
- [ ] Task 3: Collect parallel second opinions (~5 min)
  - **Action:** Run independent subagents for doc-side, runtime-side, and handoff-side analysis.
  - **Verify:** Have concrete readouts from each agent with no code changes yet.

## Checkpoint 2: Narrow Repair
- [ ] Task 4: Patch the smallest host-handoff surface that turns blind runtime use from optional atmosphere into explicit same-run evidence discipline (~10 min)
  - **Action:** Update the narrowest blind-read files to require a fresh runtime state and real event-owned transitions when a run claims layerwise skill composition.
  - **Verify:** The new wording stays anti-workflow but makes the evidence contract executable.
- [ ] Task 5: Patch the runtime/tooling surface that should help fresh agents start from the current layer (~15 min)
  - **Action:** Update the narrowest docs and/or tool surfaces so a fresh run can initialize and carry one local layer composition without guessing a whole route.
  - **Verify:** The patch reduces ambiguity around initial state, bind/spend, and layer transition reporting.
- [ ] Task 6: Re-check for accidental workflow regression (~5 min)
  - **Action:** Re-read the modified surfaces for signs of staged unlocks, route menus, or rigid ladders.
  - **Verify:** The package still biases attention rather than prescribing a solve script.

## Checkpoint 3: Fresh Blind Retest
- [ ] Task 7: Delete prior blind artifacts and stray runtime outputs (~5 min)
  - **Action:** Remove prior blind-run outputs before retesting.
  - **Verify:** The relevant artifact directories/files are absent before the new run starts.
- [ ] Task 8: Launch a fresh blind agent from zero using the canonical readset (~5 min)
  - **Action:** Spawn a new agent, point it at `BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt`, and give only the problem statement plus evidence expectations.
  - **Verify:** The new agent is distinct from earlier blind agents and starts from a clean output surface.
- [ ] Task 9: Verify the returned trace against the genuine skill-composition standard (~10 min)
  - **Action:** Check for explicit layer composition, owned bites, next-layer changes, and absence of fallback-to-ordinary-solve behavior.
  - **Verify:** Can honestly classify the result as genuine composition, runtime-assisted ordinary solve, or failure.

## Verification Criteria
- [ ] All checkpoints complete
- [ ] The modified surface makes the fresh-run evidence contract clearer without turning into a route script
- [ ] All stale blind outputs are deleted before the final retest
- [ ] A brand-new blind agent is used for the retest
- [ ] Final classification is based on explicit trace evidence, not just correctness of the math answer
