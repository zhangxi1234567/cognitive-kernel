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

For future host handoff, the canonical single-file manifest for this allowed
`project-skills on` read surface is:

- `BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt`

Do not convert this allowlist into:

- read this first
- read this later
- only unlock tools after docs
- root files first, runtime second, executables last

Those are packaging-side regrowth mistakes.

### Root live entry / host boundary

- `BLIND_TEST_BOUNDARY.md`
- `BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt`
- `AGENTS.md`
- `CLAUDE.md`
- `SKILL.md`
- `COMPATIBILITY.md`

### Runtime live surface

- `runtime/RUNTIME_OVERVIEW.md`
- `runtime/ACTIVE_KERNEL.md`
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
- `runtime/PRIMITIVE_RUNTIME_COVERAGE.md`
- `runtime/primitive_semantics.json`
- `runtime/control_state.schema.json`

### Task-specific teaching notes stay out of blind packages

The JOI/gaokao teaching notes under `references/` are not part of the blind
solve-time surface anymore:

- `references/joi-layerwise-skill-composition-note.md`
- `references/gaokao-final-skill-composition-note.md`

They are task-specific coaching material, so copying them into a true blind
package contaminates authenticity.

If a host wants them for manual study, compatibility work, or another
non-blind packaging mode, they must be added explicitly outside the canonical
blind readset.

### Optional executable thin layer

- `tools/runtime_guard.py`
- `tools/runtime_state.py`
- `tools/runtime_state.py bootstrap-blind`
- `tools/runtime_state.py bootstrap-blind-here`
- `tools/runtime_state.py bind-local`
- `tools/runtime_state.py land-local`
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
- `tools/runtime_supervision.py`
- `tools/runtime_until_done.py`

Interpretation notes for that thin layer:

- `tools/runtime_consume.py` counts as part of the allowed live surface,
  but its default role is inspect-only
- only one explicit one-shot bind request such as `--bind-once`,
  or one fresh-blind local auto-entry triggered by an already-concrete bite,
  may let it persist one local bind or one thinner-carrier spend
- `tools/runtime_supervision.py` and `tools/runtime_until_done.py`
  count as explicit inspect-first completion-supervision surfaces over the same
  one-shot primitives; they may be read as part of the live package surface
  without changing `tools/runtime_consume.py` itself into a default scheduler
- if the run claims `project-skills on` while one active `discipline_contract`
  is already asking for a local bind or spend, pure inspect-only success should
  not count as faithful runtime use anymore
- at least one real one-shot runtime transition should exist as evidence:
  `bind-local`, `land-local`, `rebind-local`, `spend-local`,
  `runtime_consume.py --bind-once`, or one explicit supervisor round from
  `tools/runtime_supervision.py` / `tools/runtime_until_done.py`
  whose recorded action actually changes the state
- for fresh blind runs, the thinnest honest default is to materialize that state
  in the working directory as `runtime_state.json`, letting the runtime own its
  matching sidecars there too:
  `runtime_state.events.jsonl`, `runtime_trace.md`, `runtime_skill_trace.md`,
  and `runtime_solve_trace.md`
- a fresh blind `project-skills on` handoff with a run directory is not complete
  until that run-local `runtime_state.json` exists; an empty run dir does not
  count as a valid runtime-participating handoff
- the truthful distinction is:
  read runtime != consume runtime
- a blind report or trace should be allowed to claim project-runtime participation
  only when that evidence exists
- a thinner-carrier spend should require its own explicit spend-side opt-in such as `--spend-handoff`;
  handoff allowance alone should not silently spend the next layer
- `tools/runtime_state.py spend-local` is allowed because it is still one-shot
  and only collapses one already-live thinner-carrier handoff into one next primitive bite
- outside that explicit supervisor path, none of these tools may be used as a hidden loop,
  scheduler, or route executor during the solve
- if that live surface exposes one active `discipline_contract`,
  the solve lane should not treat broad ordinary derivation as neutral anymore;
  it should stay on that same local bite, bind it, spend it, or tear it honestly
- that rule is still local and one-shot:
  it does not authorize staged unlocks, hidden retry ladders, or host-side future-step scheduling;
  any explicit supervisor use must stay inspect-first and derive the next required action from live state
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
- `references/joi-layerwise-skill-composition-note.md`
- `references/gaokao-final-skill-composition-note.md`
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
  usually as one-shot local read / bind / spend surfaces;
  `tools/runtime_supervision.py` / `tools/runtime_until_done.py` are the only allowed
  explicit completion supervisors, and only when the benchmark intentionally wants
  to expose that live supervision layer rather than a hidden host-side solve pipeline
- if the run never records one real local runtime transition,
  it may still solve the task, but it should not be scored as
  "this package's runtime materially participated"
- if one current-layer `discipline_contract` says a live bite is already concrete,
  continuing with broad free-form route growth should count as drift rather than as faithful use of this package
- pure state narration does not count as a promoted layer step:
  `set-core`, `primitive:*`, `competition:*`, or `handoff:set` may prepare or expose
  a live layer, but they do not by themselves count as that layer's owned solve step
- when a current-layer owned bite is already concrete, the faithful runtime step is
  the real transition that spends or binds it:
  `bind-local`, `land-local`, `rebind-local`, `spend-local`,
  `runtime_consume.py --bind-once` / `--spend-handoff`,
  or one explicit supervisor round that still records those same state-changing transitions
- if a run claims that this package produced a real skill-composition solve trace,
  each promoted step must carry one explicit `report_excerpt.layer_composition`
  rather than a host-side reconstruction from nearby skill/background fields
- `skill_field.active_skills`, `skill_authority_bridge.supporting_skills_if_any`,
  `primitive_field`, or generic control language do not by themselves count as
  skill-composition evidence
- a normal derivation with a few skill names pasted onto it does not count as a
  skill-composition step
- each promoted skill-composition step should make all of these locally legible:
  why this combination woke now, which current-layer object it took over, which
  authorized bite it owned, what thinner object / gap / next local choice it
  exposed, and why the next layer changed
- if that evidence is missing, the run may still be scored as an ordinary solve
  or runtime-assisted ordinary solve, but not as a genuine skill-composition solve
- in particular, changing `current_object` repeatedly with `set-core` while leaving the
  owned bite unspent should be treated as preparatory state shaping, not as end-to-end
  layerwise runtime solving
- the root live entry files, including `AGENTS.md` and `SKILL.md`, should stay
  readable from the start of the run when `project-skills on` is being tested;
  otherwise the run is not a faithful read of this project's live skill surface
- if the host declares a fresh blind solve, it should not leak any prior
  runtime state or runtime event log from earlier runs into that solve context
- if the host declares a continuation / resume run instead, it should provide
  exactly one live state path and its matching event-log path together with the
  same read surface, so the agent can decide bind / rebind / spend against the
  actual current state rather than against philosophy alone
- that fresh vs resume distinction is a handoff-mode distinction, not a route hint:
  it must clarify state ownership, not teach the mathematical solution

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

## Host Handoff Rule

When a future host, wrapper, or subagent launcher needs to hand the allowed
`project-skills on` surface to a fresh blind-run agent, it should default to:

- reading `BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt`
- expanding those paths relative to the project root
- handing over that exact set without adding forbidden archive/history files

The host should also declare one handoff mode explicitly:

- `fresh blind solve`
- or `resume runtime-localized state`

For `fresh blind solve`:

- start from one fresh per-run runtime state path if project runtime participation
  will be claimed
- when packaging an isolated blind package, the canonical helper is
  `python tools/prepare_blind_package.py --package-dir <pkg> --run-dir <run> --clean`
  so the exact readset manifest is copied, verified, and bootstrapped into one
  fresh run-local `runtime_state.json` rather than reconstructed by hand
- that helper-side bootstrap may seed one honest current object / seam / debt /
  next bite surface from the handed manifest problem statement, but it must stay
  non-routing and must not inject problem-specific route hints into the handoff
- if a manual or non-blind package intentionally needs the JOI/gaokao teaching
  notes too, add `--include-teaching-notes`; that opt-in is not part of the
  canonical blind path
- when `--clean` is used, only point it at fresh, empty, or helper-owned package
  / run directories; do not treat arbitrary recursive deletion as part of the
  blind packaging flow
- if no stronger local convention already exists, use one working-directory state
  path such as `runtime_state.json` so the runtime sidecars land in the same run folder
- do not pass any prior `blind_runtime_state*.json`
- do not pass any prior `blind_runtime_state*.events.jsonl`
- do not let old runtime evidence stand in for new runtime participation
- if `runtime_consume.py --bind-once` is used, count it only when that call
  creates one new bind / rebind / spend / land transition on this run's state;
  `inspect_only`, `already_bound`, or unchanged-state readout does not count

For `resume runtime-localized state`:

- pass the same static readset
- and also pass exactly one live state file path plus its matching event-log path
- so bind / rebind / spend decisions can be made against the active state itself

This mode declaration must not include route hints or solution hints.
Its purpose is only to separate clean fresh tests from legitimate runtime continuations.

This manifest is a packaging convenience for exact handoff only.
It does not create a reading order, route order, or staged unlock sequence.
