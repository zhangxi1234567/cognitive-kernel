# Frontstage Skill Execution Rewrite - Implementation Plan

**Goal:** Make each runtime layer start from frontstage skill lighting and competition, then bind, execute, verify, and reopen on the next layer without slipping back into ordinary analysis.
**Approach:** Rewire the runtime control chain so skill names are not just report labels; they become the owning execution program for each layer, with explicit main/support/check/ordinary role separation and stronger anti-regrowth enforcement.
**Estimated Total Time:** 90-120 minutes

## Checkpoint 1: Re-read And Scope The Write Set
- [ ] Task 1: Map the local write surfaces in `tools/runtime_guard.py` and `tools/runtime_state.py` (~5 min)
  - **Action:** Identify the exact functions that decide frontstage activation, competition, bind ownership, execute-local refusals, and next-layer reopening.
  - **Verify:** I can name the target functions and their responsibilities before editing.
- [ ] Task 2: Parallel-read independent concern areas with subagents (~5 min)
  - **Action:** Dispatch agents for runtime frontstage/competition, execute-local/refusal semantics, and regression-test coverage.
  - **Verify:** Each agent returns concrete file/function recommendations without overlapping write ownership.
- [ ] Task 3: Freeze the change shape (~5 min)
  - **Action:** Convert the user’s logic into a code-level checklist: light skills first, rank by projected depth-to-goal, choose first owner, split main/support/check/ordinary, require a real execution touch, reopen and relight after layer change.
  - **Verify:** The checklist covers every stage from first lighting to next-layer reopening.

## Checkpoint 2: Rewire Frontstage Lighting And Ownership
- [ ] Task 1: Strengthen current-layer lighting/competition semantics in `tools/runtime_guard.py` (~10 min)
  - **Action:** Make frontstage activation favor explicit candidate plurality, competition by “deepest/closest to target” rather than generic compressive narration, and preserve multiple lit skills until a first owner is justified.
  - **Verify:** Reports distinguish lit candidates, winning skill, supporting skills, check skill, and ordinary operations.
- [ ] Task 2: Upgrade layer payload construction in `tools/runtime_state.py` (~10 min)
  - **Action:** Ensure bound/layer payloads carry main/support/check/ordinary role structure and keep compression as an outcome of owned work, not the pre-emptive goal language.
  - **Verify:** A newly bound layer exposes who owns the layer, what supports it, how it is checked, and which ordinary operations are subordinate only.
- [ ] Task 3: Rework bind-side guardrails (~10 min)
  - **Action:** Make `bind-local` refuse generic meta/template bites and prefer skill-owned first touches that actually express the lit combination’s control claim.
  - **Verify:** A successful bind has an explicit owner combo and a problem-facing bite aligned with the frontstage winner.

## Checkpoint 3: Rewire Execution And Reopening
- [ ] Task 1: Tighten `execute-local` against ordinary drift (~10 min)
  - **Action:** Reject worked steps that use ordinary operations as owners instead of as subordinate moves under the live main skill/check split.
  - **Verify:** Execute-local errors clearly distinguish “ordinary operation used as owner” from “ordinary operation used in service of the owner.”
- [ ] Task 2: Improve next-layer reopening after real layer change (~10 min)
  - **Action:** After `land-local` / `spend-local`, force relighting and recompetition on the new layer instead of coasting on stale compression or stale winners.
  - **Verify:** Reopened layers no longer inherit the previous layer’s owner silently.
- [ ] Task 3: Sync public traces/readers to the new logic (~10 min)
  - **Action:** Update runtime trace/report surfaces so they show frontstage lighting, first takeover, role split, and real execution evidence.
  - **Verify:** Trace output makes it obvious whether a layer was merely lit, only bound, or actually executed and reopened.

## Checkpoint 4: Regression Tests And Validation
- [ ] Task 1: Add or revise tests in `tests/test_runtime_guard.py` (~15 min)
  - **Action:** Cover “many skills lit is okay,” “first owner chosen by projected depth-to-goal,” “ordinary ops demoted under a real owner,” and “new layer must relight/recompete.”
  - **Verify:** New tests fail before the fix in theory and pass after the implementation.
- [ ] Task 2: Run targeted runtime tests (~10 min)
  - **Action:** Execute the runtime test subset that exercises lighting, bind, execute, land/rebind/spend, and skill-composition evidence.
  - **Verify:** Targeted test command exits cleanly.
- [ ] Task 3: Run broader regression as needed (~10 min)
  - **Action:** If targeted tests pass, run the related blind packaging/runtime suite.
  - **Verify:** No unexpected regression in neighboring runtime behaviors.

## Verification Criteria
- [ ] Frontstage lighting happens before solve ownership is chosen.
- [ ] Competition is based on current-layer projected depth/goal proximity, not “can be used at all.”
- [ ] Each bound layer explicitly separates main skill, supporting skills, checking skills, and ordinary operations.
- [ ] Compression appears as the result of skill-owned work, not as a fallback replacement for doing the work.
- [ ] After a real layer change, the runtime relights and recompetes instead of coasting.
- [ ] Tests cover the new behavior and pass.

User already selected execution mode: **Dispatch Multiple Agents (parallel)**.
