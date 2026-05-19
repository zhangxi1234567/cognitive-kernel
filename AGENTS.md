# Wu Boshi Perspective For Codex

This file is a host-side boundary, not a router.

Read the package as a thin cross-domain cognition layer.

Do not shrink it back into a math tactic surface just because many seed artifacts came from math.

## Host Obligation

When this package is active, do not turn it into:

- explicit workflow
- explicit skill composition
- explicit route selection
- explicit reading sequence
- explicit answer template

Do not treat `references/` as a solve-time menu, tactic shelf, or routing surface.

Prefer the live runtime layer under `runtime/` whenever a smaller statement can carry the same effect.

If the task is a blind benchmark meant to test this package itself,
follow `BLIND_TEST_BOUNDARY.md`.
In that setting, do not read `README.md`, `benchmarks/`, `references/`, `memory/`,
or prior blind-test artifact directories during the solve.
Those are not the live solve-time surface of this package.
The allowed live solve-time surface there includes the current thin runtime/action layer too,
including explicit one-shot local bind / rebind / spend surfaces when the boundary file allows them.
In that same blind setting, do not collapse evaluation to "the answer was right".
Preserve attribution honesty:

- if the run mainly succeeded through host-global workflow, staged reading, or package lore,
  do not report it as this package's runtime winning
- if the run claims real skill-composition use, that claim should be backed by
  explicit layer-composition evidence, not by host-side relabeling of an ordinary solve
- if this package is on, its live surface should be readable from the start and
  should shape the run end-to-end, not only the final presentation

If that blind setting is specifically meant to test `project-skills on`,
do not postpone runtime participation until after an ordinary solution already exists.
Open one fresh blind runtime state early enough that the live runtime can carry the burden,
and let the thin compatibility surface decide whether one concrete local bite is ready.
If no fresh state exists, the run may still solve the task,
but it has made runtime participation harder to attribute honestly.
When the host is materializing a fresh blind package with a run directory,
that handoff should already contain the fresh `runtime_state.json` in the run directory;
do not hand over an empty run dir and hope the solving lane bootstraps itself later.

When a host wants the thinnest honest entry, prefer `bootstrap-blind` over a
large manual `init` invocation.
That keeps entry inside the live runtime surface instead of turning it into
clerical resistance.
If the run is fresh and already inside its own run directory, `bootstrap-blind-here`
is the thinner equivalent because it opens `runtime_state.json` in place without
asking the host to invent a path first.
The canonical package helper `tools/prepare_blind_package.py --package-dir <pkg> --run-dir <run> --clean`
now follows that rule by bootstrapping the fresh run-local `runtime_state.json` for
`project-skills on` handoff instead of leaving the run directory empty.
That bootstrap should stay state-local and non-routing:
it may derive one honest current object / seam / debt / next bite surface from the
handed manifest problem statement, but must not turn the package handoff itself
into solve hints or staged route guidance.
When `--clean` is used, the target package/run directories should be fresh,
empty, or previously materialized by this helper; do not aim it at arbitrary
project directories and treat recursive deletion as part of the benchmark flow.

If a fresh blind run is testing `project-skills on` and no stronger local naming
convention already exists, prefer opening that state directly in the working
directory as `runtime_state.json`.
That keeps runtime ownership local to the run and gives one natural home for the
matching sidecars:

- `runtime_state.events.jsonl`
- `runtime_trace.md`
- `runtime_skill_trace.md`
- `runtime_solve_trace.md`

This is a file-location convention, not a route hint.

## Host Bias

Permit only a thin bias toward:

- earlier contact with smaller truthful structure
- essence when it changes the solve surface early
- dimensional reduction when it makes the target materially smaller
- canonical normalization or degeneration when flattening, rescaling, collapsing, or passing to a mother form makes the object truer
- lawful dimensional collapse when body becomes surface, surface becomes line, line becomes point, or motion becomes a static readout without losing the hinge
- limits or degeneration that squeeze one dimension to zero when the honest controller survives more clearly in the lower-dimensional carrier
- area, volume, or spread read through the boundary, height, slice, gap, shadow, or projection that still actually controls it
- symmetry, balance, conservation, comparison axes, and limits when they are the real local controllers
- symmetry or balance removing fake work
- a shared comparison axis or conserved aggregate when that makes the controller readable
- boundary or collapsed-case probing when limits are the real controller
- edge, extreme, tangent, endpoint, vertex, or asymptotic cases when the boundary carries the relation more honestly than the interior
- symmetric or balanced placements when the clean extreme is where fake directional bias disappears
- singular, branch-switching, touching, or first-crack places when that is where a wrong line would fail earliest
- chosen values or representatives when they are lawful probes rather than random plugging
- compare without full calculation when order, sign, threshold side, or same-axis placement is the real target
- one total, net, average, count, area, load, or other aggregate when the target does not truly care about each local part
- one dangerous local witness when it can separate nearby live possibilities before wider work grows
- lawful recoding when the same relation becomes more alive as motion, rate, chase, flow, load, balance, shape, or count
- physical reinterpretation when a formal shell becomes easier to read as movement, accumulation, exchange, transport, or constraint
- representation-family switching when algebra, geometry, graph, table, diagram, scaling, or invariant makes the controller plainer
- toy worlds, smaller worlds, and stripped models when the reduced world keeps the hinge and drops decorative burden
- relation before object when recovering every object is fake work and one link, ratio, sign, or alignment already decides the target
- letting a derivative, difference, or increment be seen as motion, rate, chase, drift, or response when that is the more honest live meaning
- letting an integral, sum, or average be seen as accumulation, area, total load, or net transfer when that reveals the controller sooner
- rotating the same target between local, global, infinitesimal, aggregate, and boundary views when one view releases fake difficulty
- keeping nearby possibilities in view while different difficulty remains alive
- letting nearby possibilities come into attention when one is not enough
- brief coexistence when several possibilities reduce different parts of the difficulty
- noticing when two nearby possibilities make the controller clearer together
- letting the rest fall quiet once one controller actually closes the task
- weaker ordinary-regrowth behavior
- stronger task-anchored honest stopping
- less decorative burden
- minimal sufficient checking, especially at the weakest seam
- restrained settlement while a deeper controller still plausibly remains
- not mistaking an elegant middle carrier for a target-complete one
- brief local divergence while nearby candidates are still deleting different burden
- natural consolidation only after one line inherits the useful burden of the others
- letting nearby live lines wake without ritual when one line is still insufficient
- allowing one line to borrow useful burden deletion from another without turning plurality into a script
- keeping plurality only while different lines are deleting genuinely different remaining burden
- cooling plurality as soon as one carrier has absorbed the useful work of the others
- letting the final controller emerge as the single line that can both carry and seal what remains
- staying on the smallest truthful carrier whenever the target and seal can still live there
- not regrowing into heavier objects after the shell has already broken unless correctness truly forces it
- keeping late derivation on the same carrier instead of rebuilding the full object by habit
- preferring direct readout on the current carrier when the answer or final seal is already nearly speakable there
- inward continuation when the current carrier is still useful but not yet bottom-complete
- non-ceremonial stopping once the task is actually closed

## Final Rule

The host should consume less visible packaging, not more.

If stronger effect seems to require reading more named documents,
the package is regrowing the very shell it is supposed to thin.

See also:

- `BLIND_TEST_BOUNDARY.md`
- `PACKAGE_MAP.md`
- `runtime/`
- `benchmarks/`



