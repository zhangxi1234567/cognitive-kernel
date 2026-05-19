# Layerwise Natural Skill Internalization - Implementation Plan

**Goal:** Make runtime re-select and apply skill combinations naturally across layers for blind JOI and gaokao runs without regressing into task-shaped routing or exam-template narration.
**Approach:** Strengthen layer-to-layer ownership transfer, same-carrier landing, and problem-born next-touch generation so runtime uses skills as local controllers instead of merely naming them.
**Estimated Total Time:** 90 minutes

## Checkpoint 1: Gap Map And Guardrails
- [ ] Task 1: Re-read teaching references and current blind traces (~5 min)
  - **Action:** Compare JOI and gaokao teaching chains against current `runtime_state.events.jsonl`, `runtime_trace.md`, and `runtime_skill_trace.md`.
  - **Verify:** Have a concrete list of missing natural transitions after first bind-local.
- [ ] Task 2: Record non-regression guardrails (~3 min)
  - **Action:** Preserve clean blind packaging, no teaching-note leakage, no generic runtime-template ownership, no route injection fallback.
  - **Verify:** Constraints are reflected in code-change choices and later reruns.

## Checkpoint 2: Natural Layer Handoff
- [ ] Task 1: Inspect same-carrier / spend / land transition code (~5 min)
  - **Action:** Find where `bound_program`, `layer_composition_if_any`, `gate_binding_if_any`, and `resume_bridge` decide the next layer.
  - **Verify:** Can point to the exact functions that currently stall natural progression.
- [ ] Task 2: Implement problem-born next-layer continuation (~10 min)
  - **Action:** Patch runtime so successful local bites can reopen the next thinner object with owned skill combos instead of cooling into static same-carrier suspension.
  - **Verify:** Code paths produce concrete next-layer objects or next touches with owner/combo metadata.
- [ ] Task 3: Preserve anti-pipeline discipline (~5 min)
  - **Action:** Keep guards that refuse generic or text-only ownership while allowing explicit event-owned progression.
  - **Verify:** No new path can claim skill ownership from pure lexical hints.

## Checkpoint 3: Combo Semantics Expansion
- [ ] Task 1: Add combination-specific continuations for observed teaching chains (~10 min)
  - **Action:** Extend runtime semantics for JOI-like and gaokao-like layer progressions so combination outputs are natural and object-specific.
  - **Verify:** Generated bites mention the actual local carrier and next control object, not generic templates.
- [ ] Task 2: Rebind support for post-bind reselection (~8 min)
  - **Action:** Patch the runtime to re-open primitive competition or same-carrier landing when a bound bite has materially changed the active object.
  - **Verify:** Blind runs can progress past first bind with a believable next layer.

## Checkpoint 4: Clean Blind Retest
- [ ] Task 1: Delete previous blind run artifacts and rebuild packages (~5 min)
  - **Action:** Remove old `runtime_state*`, traces, and outputs; rerun `prepare_blind_package.py` for JOI and gaokao.
  - **Verify:** Clean packages report `teaching_notes_included: false`.
- [ ] Task 2: Blind-test JOI and gaokao from the packaged runtime (~10 min)
  - **Action:** Run canonical `bootstrap-blind-here`, then continue with local transitions until the next natural layer is visible.
  - **Verify:** Traces show owned, layerwise skill composition beyond first bind.

## Checkpoint 5: Compare Against Teaching And Decide
- [ ] Task 1: Compare blind traces against the two teaching notes (~8 min)
  - **Action:** Judge whether runtime is still worse than the taught sequence, especially on layer-by-layer naturality.
  - **Verify:** Differences are written down concretely, not hand-waved.
- [ ] Task 2: Iterate if still inferior (~10 min)
  - **Action:** Keep patching and rerunning until the layerwise naturality is close to the taught rhythm.
  - **Verify:** Final traces show repeated primitive re-selection instead of one-shot combo naming.

## Verification Criteria
- [ ] All checkpoints complete
- [ ] Clean blind packages exclude teaching notes
- [ ] JOI and gaokao both produce owned, problem-born transitions beyond first bind
- [ ] No regression into generic template ownership or task-shaped route injection
- [ ] Final comparison against teaching notes is documented honestly
