# Blind solve plan for IMO 2024 Shortlist N7

**Goal:** Independently solve the N7 problem as far as possible and write a self-audited submission package to `E:\stability_blind_imo_n7`.
**Approach:** Use only the problem statement from the local shortlist PDF, avoid reading official solutions/discussions, keep full scratch notes, and verify all claimed deductions.
**Estimated Total Time:** 60-120 minutes

## Checkpoint 1: Recover clean problem statement
- [ ] Task 1: Extract only the N7 problem statement from the problem section (~5 min)
  - **Action:** Read only problem-section pages around N7 and transcribe the statement.
  - **Verify:** Statement copied into notes without solution text.
- [ ] Task 2: Record contamination risk honestly (~2 min)
  - **Action:** Note that a search command exposed part of the answer page and stop using that content.
  - **Verify:** Risk noted in notes/result artifacts.

## Checkpoint 2: Solve from scratch
- [ ] Task 3: Normalize the functional condition and derive forced identities (~15 min)
  - **Action:** Compute consequences for small coprime/non-coprime inputs and special values.
  - **Verify:** Notes contain justified lemmas, not guesses.
- [ ] Task 4: Form candidate description for possible values of f(n) (~15 min)
  - **Action:** Test hypotheses with valuation/radical/coprimality reasoning and counterexample search.
  - **Verify:** Candidate survives self-check on prime powers and mixed factors.
- [ ] Task 5: Complete proof or isolate the obstruction (~20 min)
  - **Action:** Write forward and reverse directions, or identify the exact missing step.
  - **Verify:** Solution draft is submission-grade or explicitly marked incomplete.

## Checkpoint 3: Package and verify
- [ ] Task 6: Write `solution.md`, `notes.txt`, and `result.txt` (~10 min)
  - **Action:** Summarize proof, scratch path, and completion status.
  - **Verify:** Required files exist in target directory.
- [ ] Task 7: Final self-check (~5 min)
  - **Action:** Review logic gaps and artifact completeness.
  - **Verify:** `result.txt` starts with `FINAL: submitted` or `FINAL: incomplete` and includes self-check.

## Verification Criteria
- [ ] All checkpoints completed or honestly marked blocked
- [ ] Every claim in solution traceable to scratch reasoning
- [ ] Blind-run contamination explicitly documented
- [ ] Target directory contains the required artifacts
