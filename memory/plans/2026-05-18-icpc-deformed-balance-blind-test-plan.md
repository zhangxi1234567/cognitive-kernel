# ICPC APC M Deformed Balance Blind Test Plan

**Goal:** Run one fresh blind test on `2026_icpc_apc_m_deformed_balance` using the full canonical `project-skills on` boundary surface from `BLIND_TEST_BOUNDARY.md`, with one single initial handoff and no follow-up messages to the blind agent.

## Checkpoint 1: Fresh Handoff Surface
- [ ] Confirm the canonical manifest and target problem are the ICPC APC M case.
- [ ] Create one fresh blind package and one fresh run directory using `tools/prepare_blind_package.py`.
- [ ] Ensure the package contains the exact boundary readset and the run dir is bootstrapped with fresh runtime state.

## Checkpoint 2: Single-Agent Blind Run
- [ ] Launch exactly one new blind agent against the fresh package/run surface.
- [ ] Instruct it that the package is the full simultaneous read surface and that no follow-up messages will be sent.
- [ ] Do not send any further messages, nudges, or corrections after the initial handoff.

## Checkpoint 3: Verification
- [ ] Wait for the blind run to finish or time out without intervention.
- [ ] Verify resulting runtime state and artifacts honestly.
- [ ] Record whether the run qualified and where the outputs landed.
