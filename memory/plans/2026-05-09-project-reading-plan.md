# Project Reading Plan

**Goal:** Build a reliable understanding of this repository's purpose, live runtime surface, supporting archives, executable examples, and evidence story.
**Approach:** Read the thin live layer first, then split independent analysis across subagents for runtime doctrine, sample code, and benchmark/evidence surfaces, and finally integrate the results.
**Estimated Total Time:** 20-30 minutes

## Checkpoint 1: Map the repository
- [x] Task 1: List top-level files and directories (~2 min)
  - **Action:** Inspect the repository tree and identify major areas.
  - **Verify:** A clear map exists for runtime, benchmarks, compat, references, code samples, and memory.
- [x] Task 2: Read host entry documents (~3 min)
  - **Action:** Read `README.md`, `SKILL.md`, `PACKAGE_MAP.md`, and `runtime/RUNTIME_OVERVIEW.md`.
  - **Verify:** The project's stated purpose and "live vs archive" split are understood.

## Checkpoint 2: Parallel deep reading
- [ ] Task 3: Analyze runtime doctrine (~5 min)
  - **Action:** Read the core runtime files and summarize the actual active guidance layer.
  - **Verify:** The difference between active runtime bias and forbidden workflow behavior is concrete.
- [ ] Task 4: Analyze executable code (~5 min)
  - **Action:** Read the Python files and any benchmark sample implementation that reveals how the repo is used in practice.
  - **Verify:** The code's role in the repo is understood and not mistaken for product code.
- [ ] Task 5: Analyze benchmarks and compatibility surfaces (~5 min)
  - **Action:** Read benchmark and compatibility docs that define evaluation, portability, and evidence claims.
  - **Verify:** The project's validation story and host adaptation story are concrete.

## Checkpoint 3: Integrate and verify
- [ ] Task 6: Synthesize findings (~5 min)
  - **Action:** Combine the parallel analyses into one concise mental model of the project.
  - **Verify:** The synthesis explains purpose, structure, active surfaces, supporting evidence, and sample artifacts.
- [ ] Task 7: Verify coverage against the plan (~2 min)
  - **Action:** Compare findings back to the plan and note any remaining blind spots.
  - **Verify:** Remaining uncertainties are explicitly called out.

## Verification Criteria
- [ ] Top-level structure explained
- [ ] Live runtime core identified
- [ ] Archive/research layer distinguished from active layer
- [ ] Code samples correctly categorized
- [ ] Benchmark/evidence story summarized
- [ ] Remaining uncertainties stated honestly
