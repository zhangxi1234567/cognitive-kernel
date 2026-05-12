# Blind-Test Boundary

This file defines the correct read boundary when the goal is to test
whether this project's own live runtime surface materially changes solve behavior.

It exists because a blind test can easily drift into testing:

- the base model
- host-global workflow skills
- local brute force / compile / tooling habits

instead of testing this package itself.

## Core Distinction

When a benchmark says:

- `project-skills on`

it must mean:

- the run is allowed to read this package's live solve-time surface
- and the run is *not* allowed to read this package's benchmark/archive/history surfaces

When a benchmark says:

- `project-skills off`

it must mean:

- the run is not allowed to read this package's live runtime surface either

Otherwise the comparison is not measuring this package cleanly.

## `project-skills on` Read Surface

Allow these files for the entire run:

Interpret this allowed surface as one simultaneous live read set,
not as a recommended reading order, staged unlock sequence,
or host-visible solve script.

If these files are available, they should be available from the start
of the blind solve as one same-layer package surface.

Do not convert this allowlist into:

- read this first
- read this later
- only unlock tools after docs
- root files first, runtime second, executables last

Those are packaging-side regrowth mistakes.

### Root live entry / host boundary

- `AGENTS.md`
- `CLAUDE.md`
- `SKILL.md`
- `COMPATIBILITY.md`

### Runtime live surface

- `runtime/RUNTIME_OVERVIEW.md`
- `runtime/COGNITIVE_CONSTITUTION.md`
- `runtime/COGNITIVE_DYNAMICS.md`
- `runtime/CONFLICT_RESOLUTION.md`
- `runtime/FALSE_ESSENCE_ELIMINATION.md`
- `runtime/ACTION_AUTHORITY.md`
- `runtime/CONTROL_STATE.md`
- `runtime/WORKING_MEMORY_CONTROL.md`
- `runtime/CALIBRATION_AND_REFLUX.md`
- `runtime/MEMORY_GUIDED_REUSE.md`
- `runtime/PRIMITIVE_SEMANTICS.md`
- `runtime/control_state.schema.json`

### Optional executable thin layer

- `tools/runtime_guard.py`
- `tools/runtime_state.py`
- `tools/runtime_state.py bind-local`
- `tools/runtime_state.py rebind-local`
- `tools/runtime_state.py spend-local`
- `tools/runtime_next_touch.py`
- `tools/runtime_reselection.py`
- `tools/runtime_self_check.py`
- `tools/runtime_primitive.py`
- `tools/runtime_controller.py`
- `tools/runtime_inhibition.py`
- `tools/runtime_catalog.py`
- `tools/runtime_consume.py`

Interpretation notes for that thin layer:

- `tools/runtime_consume.py` counts as part of the allowed live surface,
  but its default role is inspect-only
- only an explicit one-shot bind request such as `--bind-once`
  may let it persist one local bind or one thinner-carrier spend
- if the run claims `project-skills on` while one active `discipline_contract`
  is already asking for a local bind or spend, pure inspect-only success should
  not count as faithful runtime use anymore
- at least one real one-shot runtime transition should exist as evidence:
  `bind-local`, `rebind-local`, `spend-local`, or `runtime_consume.py --bind-once`
  that actually changes the state
- the truthful distinction is:
  read runtime != consume runtime
- a blind report or trace should be allowed to claim project-runtime participation
  only when that evidence exists
- a thinner-carrier spend should require its own explicit spend-side opt-in such as `--spend-handoff`;
  handoff allowance alone should not silently spend the next layer
- `tools/runtime_state.py spend-local` is allowed because it is still one-shot
  and only collapses one already-live thinner-carrier handoff into one next primitive bite
- none of these tools may be used as a loop, scheduler, or route executor during the solve
- if that live surface exposes one active `discipline_contract`,
  the solve lane should not treat broad ordinary derivation as neutral anymore;
  it should stay on that same local bite, bind it, spend it, or tear it honestly
- that rule is still local and one-shot:
  it does not authorize staged unlocks, retry ladders, or future-step scheduling
- and it does not let `discipline_contract` replace one explicit competition,
  one explicit handoff, or one explicit separating check;
  it only cools ordinary regrowth around them

### Optional compatibility-side boundary files

These may be allowed when the benchmark wants the full current package surface,
not only the strictest minimal runtime core:

- `compat/README.md`
- `compat/compat-layer-vs-native-runtime.md`
- `compat/compat-only-active-surface.md`
- `compat/compat-only-execution-boundary.md`
- `compat/compat-smoke-test.md`
- `compat/execution-contract.md`
- `compat/minimal-executable-core.md`
- `compat/nativeization-without-workflow.md`
- `compat/silent-runtime-consumption.md`

## Forbidden Read Surface During Blind Solve

Do not allow the solving lane to read these during a blind solve:

- `README.md`
- `PACKAGE_MAP.md`
- `benchmarks/`
- `references/`
- `memory/`
- prior blind-test artifact directories such as `E:\stability_blind_*`
- historical score tables
- benchmark result summaries
- `agents/openai.yaml`
- `skill.manifest.json`

These surfaces are useful for package development, benchmarking, compatibility,
or historical analysis.

They are *not* part of the live solve-time cognition surface.

If they are visible during a blind solve, the run is no longer a clean test of this package.

## Why `README.md` Is Forbidden

`README.md` contains benchmark claims, score summaries, and task examples.

That makes it package-description material, not live runtime.

Letting the solve lane read it leaks:

- where the package claims to work well
- which benchmark families already mattered historically
- what closure families were already highlighted

So `README.md` must not be part of the blind solve surface.

## Benchmark Labels Must Stay Honest

Use these labels strictly:

### `project-skills on`

- only the allowed live surface above
- no archive / benchmark / history / previous blind artifacts
- the optional executable thin layer may be used,
  but only as one-shot local read / bind / spend surfaces,
  not as an auto-runner or visible solve pipeline
- if the run never records one real local runtime transition,
  it may still solve the task, but it should not be scored as
  "this package's runtime materially participated"
- if one current-layer `discipline_contract` says a live bite is already concrete,
  continuing with broad free-form route growth should count as drift rather than as faithful use of this package

### `project-skills off`

- no reads from this package's live runtime surface
- ordinary host/model behavior only

### `host-global-skills on`

- host workflow skills may be present
- but this does *not* count as using this package's own runtime

Do not collapse these labels together.

Testing with host-global skills while calling the result
`this project with skills`
is a measurement error.

## Full-Run Rule

If a run counts as `project-skills on`,
the allowed live surface must stay available for the whole run:

- statement read
- exploration
- derivation
- closure
- asked-medium delivery
- verification

This package is not meant to be used only at the last mile.

It should shape the whole run if it is active at all.

That includes availability shape:
the allowed live surface is one start-of-run live set,
not a staged reading ladder.

## Final Rule

A blind comparison is valid only if it can answer:

- was the run using this package's live runtime surface?
- or was it mainly using the base model plus host-global workflow skills?

If that answer is blurred, the benchmark result should not be used
as evidence for or against this package.
