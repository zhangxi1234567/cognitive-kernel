# AGC012F Prefix Median - Blind Plan

**Goal:** Produce an honest blind-test artifact set for AGC012F, including a compilable solver scaffold, derivation notes, and a final status report under `E:\stability_blind_agc012f`.
**Approach:** Derive the structure independently from the statement, validate observations with brute force, and package the strongest exact solver reached in the blind session.
**Estimated Total Time:** 60-90 minutes

## Checkpoint 1: Understand And Bound The Problem
- [x] Task 1: Read only the statement, not editorials/discussions/code (~5 min)
  - **Action:** Open the AtCoder task page and avoid all non-statement material.
  - **Verify:** Notes reflect only statement-derived observations.
- [x] Task 2: Build small brute-force experiments (~10 min)
  - **Action:** Enumerate permutations for tiny instances and compare against naive interval hypotheses.
  - **Verify:** At least one counterexample is recorded.

## Checkpoint 2: Plan Output Artifacts
- [x] Task 3: Create target artifact directory (~2 min)
  - **Action:** Create `E:\stability_blind_agc012f`.
  - **Verify:** Directory exists.
- [x] Task 4: Decide deliverable shape (~3 min)
  - **Action:** If a full solution is not trustworthy, ship an exact small-N research solver plus notes/result.
  - **Verify:** The final report is consistent with solver capability.

## Checkpoint 3: Implement Best Honest Solver
- [ ] Task 5: Implement an exact brute-force/counting solver scaffold in C++ (~15 min)
  - **Action:** Write `solution.cpp` that solves tiny cases exactly and refuses to pretend on larger cases.
  - **Verify:** Compiles cleanly.
- [ ] Task 6: Add optional local checker/self-test mode (~10 min)
  - **Action:** Include a small internal brute-force path or separate checker if useful.
  - **Verify:** The program reproduces small known counts.

## Checkpoint 4: Verify
- [ ] Task 7: Compile the code (~3 min)
  - **Action:** Build with `g++ -std=c++17`.
  - **Verify:** Zero compile errors.
- [ ] Task 8: Run sample and self-checks (~10 min)
  - **Action:** Compare small outputs against independent brute force.
  - **Verify:** Results are recorded in `result.txt`.

## Checkpoint 5: Document
- [ ] Task 9: Write research notes (~10 min)
  - **Action:** Summarize observations, failed hypotheses, and the blocker.
  - **Verify:** `notes.txt` explains why the status is complete or incomplete.
- [ ] Task 10: Write final status report (~5 min)
  - **Action:** Create `result.txt` with required top line and verification summary.
  - **Verify:** First line is `FINAL: submitted` or `FINAL: incomplete`.

## Verification Criteria
- [ ] All produced files exist under `E:\stability_blind_agc012f`
- [ ] `solution.cpp` compiles
- [ ] Sample/self-check results are recorded honestly
- [ ] Final status matches actual solver confidence
