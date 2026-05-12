# AGC012F Blind Test - Completion Report

**Date Completed:** 2026-05-10
**Original Goal:** Produce a blind, submit-ready attempt for `AGC012F - Prefix Median` with local evidence only.
**Final Result:** Honest blind-run artifact set with exact small-case tooling, derivation notes, failed-conjecture evidence, and a compiled incomplete solver.

## Completion Summary

| Metric | Planned | Actual |
|--------|---------|--------|
| Checkpoints | 3 | 3 |
| Tasks | 7 | 7 |
| Time | 60-120 min | ~75 min |

## Verification Checklist

- [x] Artifact set includes `solution.cpp`, `notes.txt`, `result.txt`
- [x] Local brute/checker files exist
- [x] `solution.cpp` compiles
- [x] Samples 1 and 2 pass
- [x] Known failure on sample 3 documented honestly
- [x] Residual risk and missing theory documented

## What Was Delivered

- `E:\stability_blind_agc012f\solution.cpp`
- `E:\stability_blind_agc012f\notes.txt`
- `E:\stability_blind_agc012f\result.txt`
- Supporting brute/checker scripts used during the blind run

## Blockers Encountered

1. The naive sorted-window product rule matched many small cases but failed on locally discovered N=4 counterexamples.
   Resolution: documented the failure and avoided presenting it as a solved result.
2. The binary threshold reduction gave necessary conditions but not a sufficient multivalue compatibility rule.
   Resolution: recorded the partial structure and stopped short of claiming a full solution.

## Lessons Learned

- The problem has a real cross-threshold coupling that survives beyond simple per-position interval bounds.
- Local brute-force tooling was sufficient to disprove several tempting but false simplifications early.
