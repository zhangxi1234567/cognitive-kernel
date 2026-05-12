# Deformed Balance - Implementation Plan

**Goal:** Solve the blind-test instance of `2026 ICPC APC M - Deformed Balance` and leave a ready-to-submit artifact set.
**Approach:** Build a deterministic PDA model for deformed strings, derive constant-candidate optimization around the fixed middle substring, then verify against brute force.
**Estimated Total Time:** 60-90 minutes

## Checkpoint 1: Ground The Model
- [x] Task 1: Read only the statement and samples
  - **Action:** Avoid benchmarks, editorials, discussions, and existing code
  - **Verify:** Only statement facts are used
- [x] Task 2: Enumerate small deformed / deformed-balance strings
  - **Action:** Write quick local brute snippets
  - **Verify:** Observed patterns match the grammar
- [x] Task 3: Derive a deterministic PDA
  - **Action:** Compress the grammar into `NeedNode / AfterNode + depth`
  - **Verify:** PDA recognizes exactly the brute-generated deformed strings

## Checkpoint 2: Turn It Into An Algorithm
- [x] Task 1: Reverse-run the fixed substring
  - **Action:** Derive `(start_state, delta, req_after_depth)` for each end state
  - **Verify:** Forward / reverse simulations agree on brute cases
- [x] Task 2: Derive shortest prefix / suffix formulas for a fixed config
  - **Action:** Separate low / high balance regions
  - **Verify:** Formula lengths match BFS for small states
- [x] Task 3: Reduce to O(1) candidate endpoints
  - **Action:** Keep `req`, `req+1`, and low-threshold neighbors
  - **Verify:** Matches exhaustive BFS on all short test strings

## Checkpoint 3: Ship Artifacts
- [ ] Task 1: Implement `solution.cpp`
  - **Action:** Translate the formulas and candidate evaluation
  - **Verify:** Code compiles cleanly
- [ ] Task 2: Save notes and brute validator
  - **Action:** Write `notes.txt` and `brute_check.py`
  - **Verify:** Files reflect the blind workflow honestly
- [ ] Task 3: Run compile + sample + brute self-check
  - **Action:** Execute local verification commands
  - **Verify:** Sample outputs and brute cross-check both pass

## Verification Criteria
- [ ] All checkpoints complete
- [ ] `solution.cpp` compiles
- [ ] Samples pass
- [ ] Brute check passes on all strings of length <= 9
- [ ] Final report written to `E:\\stability_blind_deformed\\result.txt`
