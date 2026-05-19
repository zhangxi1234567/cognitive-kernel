# Control State

This file is not a workflow.

It exists only to keep the live control variables small enough
that different runtime surfaces keep touching the same state
rather than drifting into parallel vocabularies.

## Persisted Boundary

`runtime/control_state.schema.json` is the persisted-state contract.

This means the serialized control-state document should contain only the
explicit state fields that the schema names.

If a surface below is described as a thin derived readout, or as something
that "may also surface from the same state", that does not make it persisted
state automatically.

In particular, these are derived readout surfaces and should not be written
back into the persisted control-state document:

- `self_check_agenda`
- `control_signals`
- `closure_nucleus`
- `gap_object`
- `resume_bridge`
- `skill_field`
- `skill_competition`
- `skill_inhibition`
- `control_bridge`
- `skill_authority_bridge`
- `interlayer_discharge_bridge`
- `inhibition_state`
- `primitive_semantics`

If one of those surfaces is useful at runtime, compute it from persisted
state after load or publish it as an ephemeral side readout.
Do not backfill it into the persisted state document just because it became
locally useful or human-readable.

One narrow clarification matters here:
`layer_composition_if_any.surface = "control_bridge"` is only a provenance
label on a persisted composition object.
It does not mean a top-level `control_bridge` object is itself part of
persisted state.

## Minimal Live State

The live run should usually be readable through these fields:

- `current_object`
- `current_seam` when one crack or rule-change seam is already local enough to name
- `current_debt`
- `next_bite`
- `asked_medium_surface`
- `revocation_handle`
- `uncertainty_mode`
- `primary_slot`
- `bound_program`
- `gate_binding_if_any` when one already-local monitoring pressure has temporarily bought authority for one executable bite on the same carrier
- `primitive_field_if_any` when the current layer has already narrowed to one tiny live primitive competition on the present carrier
- `primitive_competition_if_any` when that competition itself is explicit enough to name as one or two same-layer candidates plus one separating check surface
- `carrier_handoff_if_any` when one thinner carrier has just taken local authority and primitive reselection must stay executable rather than only verbal
- `secondary_rival_if_any`
- `materialization_evidence` if the state is already released and no bound program remains

This is not a required explicit schema at solve time.

It is only the smallest common state face
that lets working memory, action authority, calibration, and reflux
keep referring to the same live thing.

If late-stage authority is already concrete,
the same face may carry one tiny `bound_program` too:

- one `kind`
- one `target`
- one `operation`
- and optionally one success signal

That field exists only to keep one next touch executable.
While `release_veto` is active, it may be surfaced as the default local action.
It is not a workflow shell.
One tiny host consumer may read that default local action through
`tools/runtime_next_touch.py` and stop there.
If the only current bite is probe-like, binding it without a live skill
hypothesis should be refused rather than silently treated as normal progress.

If one already-local monitoring pressure has truly purchased temporary authority,
the same face may also carry one tiny `gate_binding_if_any`:

- one `source_focus`
- one `source_target`
- one `demoted_continuation`
- and one `authority_until`

That object exists only to keep the monitor-to-action bridge honest.
It is not a phase marker, retry counter, or route script.

If the current layer is already thin enough that one tiny live primitive field
can be named, the same face may also carry one `primitive_field_if_any`:

- one `layer_object`
- one or two `active_primitives`
- optionally one `tie_break_check`
- optionally one `selection_basis`
- optionally one `evidence_basis`
- and one short `why_now`

That object exists only so layerwise reselection is visible on the current carrier
instead of remaining a general promise.
It is not a menu, route family, or solver shell.
If the carrier changes, this field should refresh to the new layer object rather than
quietly inheriting the old layer's primitive label.
If two primitives are still live there, one cheap tie-break surface should exist
before the runtime is allowed to collapse them into one executable next bite.
If the field was recovered only from text-level fallback, that should count as a weaker observational state than an explicit primitive hint on the live layer.
`evidence_basis` is the thin way to say whether the field is being carried by:

- `explicit_hint`
- `state_witness`
- `cheap_check`
- `lexical_hint`
- or `mixed`

If the local competition itself is already explicit enough to name,
the same face may also carry one `primitive_competition_if_any`:

- one `layer_object`
- one or two primitive `candidates`
- optionally one `separating_check`
- and optionally one `winner_if_any`

Each candidate should stay tiny:

- one `primitive`
- one `touch_target`
- and one `expected_local_gain`

This object exists only so primitive competition becomes one local falsifiable state
rather than prose about which primitive "feels right".
It is not a route bracket and not a multi-step search tree.
One tiny exhaustive probe may appear here only as one `separating_check`,
`cheap_check`, `exact_check`, or witness-style local surface.
It must not become a stored fallback solver, route family, or multi-case
expansion object.
If the live layer changes, a stale competition object should cool out rather than
quietly constraining the new layer's primitive spend.

If one explicit current-layer competition is still live on the present layer,
that local competition should outrank a merely derived thinner-carrier reselection.

In particular, the runtime should not keep fleeing into reselection
when the current layer already contains:

- one structural/object-side candidate
- one answer-side readout candidate
- and one concrete separating check

That is still one same-layer closure nucleus, not yet a reason to abandon the layer.

In that case one local structural bite may bind first,
even while the answer-side readout candidate stays warm beside it.

If one carrier change or primitive reselection has already become local enough
to name, the same state face may also carry one tiny `carrier_handoff_if_any`:

- one `trigger`
- one `from_slot`
- one `to_object`
- one `winning_pressure`
- optionally one `cooled_pressure_if_any`
- one `why_local`
- and optionally one tiny `warm_field` with at most one or two still-live pressures plus one cheap check surface
- that same `warm_field` may also carry one or two explicit `primitive_hints` when the thinner layer has already made those candidates locally nameable
- and that same `warm_field` may also carry one `evidence_basis` so lexical hinting does not masquerade as structural evidence

That object exists only to keep layerwise reselection and cooling honest on the current seam.
It is not a stage transition log and not a route script.
If the handoff is cleared again, the primitive field should reopen on the now-current layer
rather than silently keeping the thinner layer's primitive label.

If `release_veto` is already down and no `bound_program` remains,
one thin `materialization_evidence` object should still say
why the asked-medium closure is being treated as real:

- one evidence `kind`
- one evidence `location`
- and one short evidence `summary`

During live execution before final asked-medium sealing,
that same object may temporarily carry:

- `kind: inline_text` when the current layer only landed as an inline worked step
- one `worked_step` string for the owned local touch
- and later one `skill_serialized` boolean once the asked-medium artifact has been sealed

Once `release_veto` is down, active control artifacts should cool out:

- no `gate_binding_if_any`
- no `carrier_handoff_if_any`
- no live `primitive_field_if_any`
- and no live `primitive_competition_if_any`

## State Discipline

Do not let nearby files silently talk about different objects
while sounding aligned.

If:

- the current object
- the current seam when one is live
- the current debt
- the next bite
- the asked-medium touch
- or the revocation handle

cannot still be recognized as the same local state,
control is starting to split.

## Handoff Rule

State should change only when one of these happens:

- one same-carrier bite lands
- one hostile witness kills the line
- one exact check tears the carrier
- one asked-medium failure shrinks the residue
- or one smaller residue inherits ownership honestly

Without one of those events,
state drift is usually commentary drift.

## Secondary Rival Rule

If a secondary rival exists,
it should be legible in the same small state face too:

- one rival object or residue
- one rival debt
- one rival bite
- and one rival separating advantage

If the rival cannot be rendered that concretely,
it should cool back down into pressure.

## Self-Check Readout

One thin derived readout may also surface from the same state:

- `self_check_agenda.focus`
- `self_check_agenda.reason`
- `self_check_agenda.touch_target`
- `self_check_agenda.preferred_kinds`

This readout should name only one local checking pressure at a time:

- `seam`
- `rival`
- `carrier`
- or `asked_medium`

It exists only so early monitoring can cash into one current local check surface.
It must not become an exhaustive sweep or a visible checklist.
If a small probe is used there, it should be bound to one current skill or
primitive hypothesis on the same layer; otherwise it is drift, not support.

If one explicit or derived `carrier_handoff_if_any` is already live,
this self-check readout should fall quiet rather than compete for the slot.
At that point the handoff owns the local control face.

## Thin Control Signals

One thin derived `control_signals` readout may also surface from the same state:

- `control_signals.current_controller_view.essence_status`
- `control_signals.current_controller_view.owner_status`
- `control_signals.current_controller_view.carrier_status`
- `control_signals.current_controller_view.shell_suspicion`
- `control_signals.current_controller_view.middle_object_risk`
- `control_signals.current_controller_view.reselection_needed`
- `control_signals.operator_bias.favored_primitives`
- `control_signals.operator_bias.live_primitives`
- `control_signals.operator_bias.heuristic_primitives`
- `control_signals.operator_bias.cheapest_reality_check`
- `control_signals.operator_bias.controller_questions`
- `control_signals.operator_bias.honest_touches`
- `control_signals.operator_bias.anti_patterns`
- `control_signals.primitive_control.active_primitives`
- `control_signals.primitive_control.selection_basis`
- `control_signals.primitive_control.evidence_basis`
- `control_signals.primitive_control.competition_status`
- `control_signals.primitive_control.competition_candidates`
- `control_signals.primitive_control.separating_check`
- `control_signals.meta_controls.counter_question`
- `control_signals.meta_controls.closure_gate`
- `control_signals.meta_controls.supervisory_pulse`
- `control_signals.meta_controls.god_view`
- `control_signals.meta_controls.metacognition`
- `control_signals.meta_controls.central_control`
- `control_signals.meta_controls.hindbrain_guard`
- `control_signals.incentive_field.attraction_pull`
- `control_signals.incentive_field.reward_bias`
- `control_signals.incentive_field.penalty_bias`
- `control_signals.incentive_field.discomfort_if_ignored`
- `control_signals.micro_control_surface.closure_pull`
- `control_signals.micro_control_surface.reward_bias`
- `control_signals.micro_control_surface.penalty_bias`
- `control_signals.micro_control_surface.supervision_pulse`
- `control_signals.micro_control_surface.counter_question`

This object exists only to keep "grasp essence", "find the final owner",
"suspect the shell", "suspect the beautiful middle carrier", and
"reselect on the thinner carrier" locally consumable by the same primitive runtime.
It is not a new phase layer, not a route script, and not a second planner.

It may bias:

- `self_check_agenda`
- `primitive_field_if_any`
- `primitive_competition_if_any`
- and `carrier_handoff_if_any.warm_field.primitive_hints`

The host should read the explicit primitive-control face before treating heuristic pressure as the real live primitive layer.

That same thin control face may also carry one tiny `micro_control_surface`.

This is not a planner and not a route engine.

It exists only to keep a few brain-like local control jobs explicit on the current layer:

- `closure_pull`: what exact local closure debt still blocks release
- `reward_bias`: what kind of local touch should feel more attractive now
- `penalty_bias`: what kind of decorative continuation should feel more expensive now
- `supervision_pulse`: which local owner currently has anti-drift authority
- `counter_question`: what one smallest falsifier or exact check should stay live

That object must stay:

- current-layer only
- present-tense only
- and non-planning

It must not say:

- what to do second
- what route owns the task
- what phase the run is in
- or how to complete a whole solve

One thin derived `closure_nucleus` may also surface from the same state when
late same-layer closure is already the real owner.

That nucleus may expose only:

- `closure_nucleus.object`
- `closure_nucleus.debt`
- `closure_nucleus.asked_medium_surface`
- `closure_nucleus.revocation_handle`
- `closure_nucleus.current_structural_bite_if_any`
- `closure_nucleus.current_readout_bite_if_any`
- `closure_nucleus.separating_check_if_any`
- `closure_nucleus.same_carrier_only`
- `closure_nucleus.no_route_growth`

It exists only so control / primitive / consume / reselection readouts keep touching
one identical late-stage local body.
It is not a planner, not a route scheduler, and not a multi-step solve shell.

One thin derived `gap_object` may also surface from the same state when
the current unpaid debt is already explicit enough to inherit local ownership
as one smaller residue / carrier / readout object.

That readout may expose only:

- `gap_object.object`
- `gap_object.source_debt`
- `gap_object.cheap_check`
- `gap_object.primitive_hints`
- `gap_object.inherits_authority`

It exists only so a named missing thing can become the current local object
without scripting what should happen after that handoff.
It is not a phase marker, not a decomposition tree, and not a retry workflow.

`skill_field.active_skills` is intentionally plural.

One layer may keep one tiny local skill combination warm even while
`skill_authority_bridge` still exposes only one executable local touch.

That means:

- a layer may use one or more nearby skills together
- the current winner may still rely on supporting background skills
- and trace/readout should not flatten every layer into "exactly one skill existed here"

This plurality is still local, not free solve-shelf breadth.
It must stay tied to one burden on one current layer.
That plurality is also not enough to promote a solve step into a genuine
skill-composition step by itself.

In particular:

- `skill_field.active_skills` is background/current-layer capability evidence
- `skill_authority_bridge.supporting_skills_if_any` is support evidence
- `primitive_field.active_primitives` is primitive-layer evidence

None of those fields alone should be allowed to masquerade as one explicit
`layer_composition`.
If a trace wants to claim that one skill combination truly took over a step,
that takeover should surface as one explicit current-layer composition object
with its own owned bite, layer object, and local reason,
rather than being reconstructed afterward from nearby plural fields.

That explicit object is not only a report-time decoration.

When one current-layer combination has already purchased local authority,
`layer_composition_if_any` may act as the thin solve-time takeover object too:

- one current layer
- one owned bite
- one local reason
- one next exposed object or gap
- and one record of why the layer changed

Without that explicit local takeover object,
the runtime may still carry nearby skill or primitive pressure,
but it should not pretend that a genuine layerwise composition step has already happened.
This keeps solve-time ownership and trace-time evidence on the same thin object
instead of letting one exist only after the fact.

One thin derived `resume_bridge` may also surface from the same state when
the run is locally stuck and needs one tiny rebind of ask + object + debt
before choosing whether to continue on the same carrier or reseat on a thinner carrier.

That readout may expose only:

- `resume_bridge.ask_surface`
- `resume_bridge.known_object`
- `resume_bridge.explicit_gap`
- `resume_bridge.mode`
- `resume_bridge.next_local_choice`
- `resume_bridge.supporting_skills`

It exists only so a stuck run can stay local while deciding
"keep pushing here" versus "the same gap is truer on a thinner object".
It is not a restart state machine, not route replay, and not a broad decomposition plan.

One thin derived primitive-semantics readout may also surface beside the live primitive layer:

- `primitive_semantics.<primitive>.mechanism`
- `primitive_semantics.<primitive>.controller_question`
- `primitive_semantics.<primitive>.wake_when`
- `primitive_semantics.<primitive>.cheapest_honest_touch`
- `primitive_semantics.<primitive>.anti_pattern`

This object exists only to keep the current primitive layer mechanism-facing rather
than filename-facing.
It is not a tactic card, not a solve script, and not a route stack.

One thin derived skill-side readout may also surface from the same state:

- `skill_field.active_skills`
- `skill_field.closure_authority_skill_if_any`
- `skill_competition.candidates`
- `skill_competition.separating_check`
- `skill_competition.winning_skill_if_any`
- `skill_inhibition.promoted_skill_if_any`
- `skill_inhibition.demoted_skills`

This object exists only so the live skill-capability layer becomes readable on the
current carrier.
It is not a skill menu, not a chaining surface, and not a planner.

If one skill currently owns one local executable bite,
one thin `skill_authority_bridge` may also surface:

- `skill_authority_bridge.winning_skill_if_any`
- `skill_authority_bridge.executable_local_touch_if_any`
- `skill_authority_bridge.silence_after_contact`

This bridge exists only to connect skill-level authority to one current local bite.
It must not become a route executor or multi-step skill runner.

If a thinner-carrier structural bite and an asked-medium closure bite are both
honestly live at the same time, one thin `interlayer_discharge_bridge` may also
surface:

- `interlayer_discharge_bridge.mode`
- `interlayer_discharge_bridge.reason`
- `interlayer_discharge_bridge.spend_first_program`
- `interlayer_discharge_bridge.post_closure_touch_if_any`
- `interlayer_discharge_bridge.keep_closure_authority`

This bridge exists only to let one structural debt discharge first while closure
pressure stays live.
It must not become a route ladder, a retry tree, or an automatic stage chain.
When `keep_closure_authority` is true, that structural discharge should still
leave `exact_closure` warm enough to retake the asked-medium slot immediately
after the thinner-layer bite is honestly paid.
The same package rule applies to tiny probe-like bites:
they may stay live as validators of the current skill line,
but they should not silently become the main route while a thinner structural
carrier is still honestly compressible.

These names may stay visible as thin runtime control faces:

- `counter_question`: a concrete unpaid debt should quickly cash into one check, witness, or candidate object
- `closure_gate`: near release, nice wording should lose to exact asked-medium closure
- `supervisory_pulse`: if the object still has not changed, renaming should cool
- `god_view`: re-name the problem smaller and shift toward the true controller
- `metacognition`: keep re-checking owner, carrier, and false essence while solving
- `central_control`: one local owner should temporarily dominate until change or tear
- `hindbrain_guard`: keep the non-release latch alive until one executable closure object or honest kill lands

The same thin control face may also carry an incentive side:

- `attraction_pull`: what smaller seam / asked-medium / writable object should pull attention harder now
- `reward_bias`: what kind of move should gain local value now
- `penalty_bias`: what kind of continuation should lose value now
- `discomfort_if_ignored`: what unpaid burden should keep producing local pressure if the pull is ignored

It may not directly write a multi-step route or force a winner without a local separating check.

## Thin Inhibition Readout

One thin derived inhibition readout may also surface while `release_veto` is active:

- `inhibition_state.owner`
- `inhibition_state.promoted_move`
- `inhibition_state.demoted_continuations`
- `inhibition_state.gate_until`

This object exists only to make local monitoring buy local gate change.
It is not a scheduler, retry loop, or route shell.
One tiny host reader may expose that readout directly through
`tools/runtime_inhibition.py`.

## Thin Binding Projection

If `release_veto` is still active and the local gap is already concrete enough
that one current focus can be named,
one optional thin binder may project that same state into exactly one tiny local action.

That projection may bind only:

- one `bound_program`
- or one `carrier_handoff_if_any`

Never both.

It must refuse to act when:

- one `bound_program` already exists
- one `carrier_handoff_if_any` already exists
- more than one local action family is still genuinely live
- or the state is still too broad to name one same-carrier bite

This is not a planner and not a route selector.
It is only a lossy compression from one already-local control state
into one executable local bite.
Without explicit override, plural action families should still refuse to bind.
If the same-carrier bind and thinner-carrier handoff are both concrete, `bind-local` should refuse rather than silently choosing one.

The same thin rule may also be applied one layer later to primitive reselection:

- if the burden has honestly moved to a thinner carrier
- and one local winner pressure is already concrete
- one optional thin rebind may project that state into exactly one tiny `carrier_handoff_if_any`

That rebind must still stay one-shot and local.
It must not accumulate stage history, retries, or future route commitments.

If one thinner-carrier handoff is already explicit and the next primitive bite
is already concrete on that new carrier, one optional one-shot spend may collapse:

- one `carrier_handoff_if_any`
- plus one current `primitive_field_if_any`

into exactly one new-layer `bound_program`.

That spend must still stay one-shot and explicit.
It must not become an automatic multi-step route executor.
After such a spend, the primitive field should refresh again on the new live layer
rather than staying attached to the pre-spend layer object.
If a live `skill_authority_bridge` also names one executable local touch there,
that touch may be consumed only when it agrees with the primitive-side spend
or when no primitive-side spend is yet concrete enough.
If the two local bites disagree, the spend should refuse rather than silently choosing one.
One narrow exception is allowed:
if one live `interlayer_discharge_bridge` says the thinner-carrier structural bite
must land first, `spend-local` may spend that one structural bite and stop there
without treating it as final closure.
If `interlayer_discharge_bridge.keep_closure_authority` is true, that spend may
still carry an asked-medium closure agenda even while the currently bound bite
is the thinner-layer structural discharge itself.
If one live `discipline_contract` says a current local bite is already concrete,
ordinary broad route regrowth should cool until that bite is bound, spent, or honestly torn.
That contract has only veto power against ordinary drift.
It does not inherit authority to settle:

- `primitive_competition_if_any`
- `carrier_handoff_if_any`
- `skill_authority_bridge`
- or `interlayer_discharge_bridge`

Those objects keep their own explicit local authority.
One tiny host reader may expose the primitive-side surface directly through
`tools/runtime_primitive.py`.
