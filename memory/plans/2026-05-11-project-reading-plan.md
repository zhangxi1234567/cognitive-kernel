# Project Reading Plan

**Goal:** Build a careful, evidence-backed understanding of this repository's purpose, live runtime surface, executable code paths, and evaluation/compatibility layers.
**Approach:** Read the live package surface first, split independent areas across multiple agents, then integrate the findings into one coherent map.
**Estimated Total Time:** 25 minutes

## Checkpoint 1: Repository Shape
- [ ] Task 1: Confirm top-level layout (~3 min)
  - **Action:** Inspect root directories and core docs.
  - **Verify:** Can explain what each top-level area is for.
- [ ] Task 2: Identify the live vs archived surface (~3 min)
  - **Action:** Read `README.md`, `PACKAGE_MAP.md`, and compatibility notes.
  - **Verify:** Can distinguish runtime-critical files from reference/archive layers.

## Checkpoint 2: Runtime Layer
- [ ] Task 3: Map runtime concepts (~5 min)
  - **Action:** Read `runtime/` overview and state/constitution docs.
  - **Verify:** Can explain the runtime model, state shape, and key control rules.
- [ ] Task 4: Map primitive semantics (~4 min)
  - **Action:** Inspect primitive semantics docs and JSON.
  - **Verify:** Can describe how abstract principles are represented in machine-readable form.

## Checkpoint 3: Executable Layer
- [ ] Task 5: Map Python tools (~4 min)
  - **Action:** Read `tools/` and the small project scripts.
  - **Verify:** Can explain what code is actually runnable and how it supports the runtime.
- [ ] Task 6: Map compatibility checks (~2 min)
  - **Action:** Read `compat/` overview and host contract checker.
  - **Verify:** Can explain how the package constrains host behavior.

## Checkpoint 4: Evaluation Layer
- [ ] Task 7: Inspect benchmarks and blind-test boundaries (~3 min)
  - **Action:** Read benchmark overview and blind-test docs.
  - **Verify:** Can explain how the project evaluates itself and avoids leakage.
- [ ] Task 8: Integrate findings (~1 min)
  - **Action:** Synthesize one project map with open questions and risks.
  - **Verify:** Final summary covers purpose, architecture, runtime, tools, and evaluation.

## Verification Criteria
- [ ] All checkpoints completed
- [ ] Every major claim tied to an inspected file
- [ ] Live runtime surface separated from archive/reference surface
- [ ] Final explanation includes open questions or risks where certainty is limited
