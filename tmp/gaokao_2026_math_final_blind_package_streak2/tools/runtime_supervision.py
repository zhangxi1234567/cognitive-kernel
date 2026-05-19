#!/usr/bin/env python3
from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, TypedDict

RuntimeMapping = Mapping[str, object]
BlockerDisposition = Literal["retryable", "terminal", "not_applicable"]

DEFAULT_CONTINUATION_BUDGET: Final[int] = 1
MAX_CONTINUATION_BUDGET: Final[int] = 4
DEFAULT_CONTINUATION_MODE: Final[str] = "stalled_runtime_recompetition"
DEFAULT_REQUIRED_ACTION: Final[str] = "bind_local"
DEFAULT_STALL_SURFACE: Final[str] = "current_layer"

BLOCKER_AMBIGUOUS_BIND_LOCAL: Final[str] = "ambiguous_bind_local"
BLOCKER_AMBIGUOUS_NEXT_TOUCH: Final[str] = "ambiguous_next_touch"
BLOCKER_AMBIGUOUS_THINNER_CARRIER: Final[str] = "ambiguous_thinner_carrier"
BLOCKER_UNRESOLVED_RIVAL: Final[str] = "unresolved_rival"
BLOCKER_SAME_CARRIER_INFERENCE_FAILURE: Final[str] = "same_carrier_inference_failure"
BLOCKER_SAME_CARRIER_LAYER_STALLED: Final[str] = "same_carrier_layer_stalled"
BLOCKER_STRUCTURAL_HOP_LIMIT: Final[str] = "structural_hop_limit"
BLOCKER_INVALID_STATE: Final[str] = "invalid_state"
BLOCKER_RELEASE_NOT_BLOCKED: Final[str] = "release_not_blocked"
BLOCKER_BLOCKING_PROBLEMS: Final[str] = "blocking_problems"
BLOCKER_NO_LIVE_COMPLETION_GAP: Final[str] = "no_live_completion_gap"
BLOCKER_NO_TRIGGER_SIGNALS: Final[str] = "no_trigger_signals"
BLOCKER_NONCONTINUABLE_REFUSAL: Final[str] = "noncontinuable_refusal"
BLOCKER_EXECUTE_LOCAL_INPUT_REQUIRED: Final[str] = "execute_local_input_required"
BLOCKER_SUPERVISOR_STAGNATION_GUARD: Final[str] = "supervisor_stagnation_guard"

IGNORED_STALL_PROBLEMS: Final[frozenset[str]] = frozenset(
    {
        "bound_program is required while release_veto is active",
    }
)


class OutputStatus(TypedDict, total=False):
    touched: bool
    cosmetic_only: bool
    contains_unsupported: bool
    contains_placeholder: bool
    final_artifact_materialized: bool


class CompletionGapPayload(TypedDict):
    explicit_gap: str
    next_local_choice: str
    known_object: str
    ask_surface: str
    same_carrier_preferred: bool


class CompletionSnapshotPayload(CompletionGapPayload):
    release_veto_active: bool
    release_allowed: bool
    final_artifact_materialized: bool
    task_incomplete: bool
    thinner_carrier_due: bool
    supervisory_signals: list[str]
    supervisor_active: bool


class StallContinuationPayload(TypedDict):
    active: bool
    mode: str
    required_action: str
    refusal_reason: str
    trigger_signals: list[str]
    allowed_transition_surfaces: list[str]
    surface: str
    completion_gap: CompletionGapPayload


@dataclass(frozen=True)
class BlockerRule:
    code: str
    reason_fragments: tuple[str, ...]


@dataclass(frozen=True)
class CompletionSnapshot:
    release_veto_active: bool
    release_allowed: bool
    final_artifact_materialized: bool
    task_incomplete: bool
    explicit_gap: str
    next_local_choice: str
    known_object: str
    ask_surface: str
    same_carrier_preferred: bool
    thinner_carrier_due: bool
    supervisory_signals: tuple[str, ...]
    supervisor_active: bool

    def as_gap_payload(self) -> CompletionGapPayload:
        return {
            "explicit_gap": self.explicit_gap,
            "next_local_choice": self.next_local_choice,
            "known_object": self.known_object,
            "ask_surface": self.ask_surface,
            "same_carrier_preferred": self.same_carrier_preferred,
        }

    def as_dict(self) -> CompletionSnapshotPayload:
        payload = self.as_gap_payload()
        payload.update(
            {
                "release_veto_active": self.release_veto_active,
                "release_allowed": self.release_allowed,
                "final_artifact_materialized": self.final_artifact_materialized,
                "task_incomplete": self.task_incomplete,
                "thinner_carrier_due": self.thinner_carrier_due,
                "supervisory_signals": list(self.supervisory_signals),
                "supervisor_active": self.supervisor_active,
            }
        )
        return payload


@dataclass(frozen=True)
class StallContinuation:
    active: bool
    mode: str
    required_action: str
    refusal_reason: str
    trigger_signals: tuple[str, ...]
    allowed_transition_surfaces: tuple[str, ...]
    surface: str
    completion_gap: CompletionSnapshot

    def as_dict(self) -> StallContinuationPayload:
        return {
            "active": self.active,
            "mode": self.mode,
            "required_action": self.required_action,
            "refusal_reason": self.refusal_reason,
            "trigger_signals": list(self.trigger_signals),
            "allowed_transition_surfaces": list(self.allowed_transition_surfaces),
            "surface": self.surface,
            "completion_gap": self.completion_gap.as_gap_payload(),
        }


@dataclass(frozen=True)
class BlockerAssessment:
    disposition: BlockerDisposition
    code: str
    refusal_reason: str
    snapshot: CompletionSnapshot
    blocking_problems: tuple[str, ...] = ()
    trigger_signals: tuple[str, ...] = ()
    continuation: StallContinuation | None = None

    @property
    def retryable(self) -> bool:
        return self.disposition == "retryable"

    @property
    def terminal(self) -> bool:
        return self.disposition == "terminal"

    @property
    def not_applicable(self) -> bool:
        return self.disposition == "not_applicable"

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "disposition": self.disposition,
            "code": self.code,
            "refusal_reason": self.refusal_reason,
            "retryable": self.retryable,
            "terminal": self.terminal,
            "not_applicable": self.not_applicable,
            "snapshot": self.snapshot.as_dict(),
        }
        if self.blocking_problems:
            payload["blocking_problems"] = list(self.blocking_problems)
        if self.trigger_signals:
            payload["trigger_signals"] = list(self.trigger_signals)
        if self.continuation is not None:
            payload["continuation"] = self.continuation.as_dict()
        return payload


@dataclass(frozen=True)
class BudgetAdjustment:
    code: str
    delta: int
    applied: bool
    reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "delta": self.delta,
            "applied": self.applied,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ContinuationBudget:
    recommended_rounds: int
    minimum_rounds: int
    maximum_rounds: int
    required_action: str
    snapshot: CompletionSnapshot
    adjustments: tuple[BudgetAdjustment, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "recommended_rounds": self.recommended_rounds,
            "minimum_rounds": self.minimum_rounds,
            "maximum_rounds": self.maximum_rounds,
            "required_action": self.required_action,
            "snapshot": self.snapshot.as_dict(),
            "adjustments": [adjustment.as_dict() for adjustment in self.adjustments],
        }


@dataclass(frozen=True)
class SupervisorRunResult:
    state_file: str
    completed: bool
    inspect_first: bool
    inspect_payload: dict[str, object]
    inspect_exit_code: int
    final_payload: dict[str, object]
    final_exit_code: int
    required_action: str
    action_payload: dict[str, object] | None = None
    action_exit_code: int | None = None
    blocker: BlockerAssessment | None = None
    continuation_budget: ContinuationBudget | None = None
    executed_rounds: int = 0
    step_history: tuple[str, ...] = ()
    reason: str = ""

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "state_file": self.state_file,
            "completed": self.completed,
            "inspect_first": self.inspect_first,
            "inspect_payload": self.inspect_payload,
            "inspect_exit_code": self.inspect_exit_code,
            "final_payload": self.final_payload,
            "final_exit_code": self.final_exit_code,
            "required_action": self.required_action,
            "executed_rounds": self.executed_rounds,
            "step_history": list(self.step_history),
            "reason": self.reason,
        }
        if self.action_payload is not None:
            payload["action_payload"] = self.action_payload
        if self.action_exit_code is not None:
            payload["action_exit_code"] = self.action_exit_code
        if self.blocker is not None:
            payload["blocker"] = self.blocker.as_dict()
        if self.continuation_budget is not None:
            payload["continuation_budget"] = self.continuation_budget.as_dict()
        return payload


CONTINUABLE_STALL_RULES: Final[tuple[BlockerRule, ...]] = (
    BlockerRule(
        code=BLOCKER_AMBIGUOUS_BIND_LOCAL,
        reason_fragments=("no unique local bite became concrete enough to bind",),
    ),
    BlockerRule(
        code=BLOCKER_AMBIGUOUS_NEXT_TOUCH,
        reason_fragments=("no unique next primitive touch is concrete enough",),
    ),
    BlockerRule(
        code=BLOCKER_AMBIGUOUS_THINNER_CARRIER,
        reason_fragments=("no unique thinner-carrier handoff is concrete enough",),
    ),
    BlockerRule(
        code=BLOCKER_UNRESOLVED_RIVAL,
        reason_fragments=("unresolved rival is still live without a unique rival-local bite",),
    ),
    BlockerRule(
        code=BLOCKER_SAME_CARRIER_INFERENCE_FAILURE,
        reason_fragments=("next same-carrier layer could not be inferred",),
    ),
    BlockerRule(
        code=BLOCKER_SAME_CARRIER_LAYER_STALLED,
        reason_fragments=("next same-carrier layer is identical to the current one",),
    ),
    BlockerRule(
        code=BLOCKER_STRUCTURAL_HOP_LIMIT,
        reason_fragments=("bind_once_structural_hop_limit_reached",),
    ),
)


def normalize_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def normalize_refusal_reason(reason: object) -> str:
    return normalize_text(str(reason or "")).lower()


def _mapping(value: object) -> RuntimeMapping:
    return value if isinstance(value, Mapping) else {}


def _bool_flag(value: object, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _dedupe_ordered(values: list[str]) -> tuple[str, ...]:
    ordered: list[str] = []
    for value in values:
        text = normalize_text(value)
        if text and text not in ordered:
            ordered.append(text)
    return tuple(ordered)


def _output_status_is_final(output_status: RuntimeMapping) -> bool:
    return (
        _bool_flag(output_status.get("touched"))
        and _bool_flag(output_status.get("final_artifact_materialized"))
        and output_status.get("contains_unsupported") is not True
        and output_status.get("contains_placeholder") is not True
    )


def supervisory_signals_from_report(report: RuntimeMapping) -> tuple[str, ...]:
    control_signals = _mapping(report.get("control_signals"))
    meta_controls = _mapping(control_signals.get("meta_controls"))
    micro_surface = _mapping(control_signals.get("micro_control_surface"))
    layerwise_pressure = _mapping(control_signals.get("layerwise_reselection_pressure"))

    signals: list[str] = []
    for key, label in (
        ("god_view", "god_view"),
        ("后脑守卫", "后脑守卫"),
        ("supervisory_pulse", "supervisory_pulse"),
        ("反问", "反问"),
        ("closure_gate", "closure_gate"),
    ):
        control = _mapping(meta_controls.get(key))
        if control.get("active") is True:
            signals.append(label)

    for key, label in (
        ("监督_pulse", "监督_pulse"),
        ("反问", "反问_surface"),
    ):
        control = _mapping(micro_surface.get(key))
        if control.get("active") is True:
            signals.append(label)

    if layerwise_pressure.get("active") is True:
        signals.append("layerwise_reselection_pressure")

    return _dedupe_ordered(signals)


def completion_gap_snapshot(
    state: object,
    report: object,
) -> CompletionSnapshot:
    state_map = _mapping(state)
    report_map = _mapping(report)
    resume_bridge = _mapping(report_map.get("resume_bridge"))
    output_status = _mapping(state_map.get("output_status"))

    final_artifact_materialized = _output_status_is_final(output_status)
    explicit_gap = (
        normalize_text(resume_bridge.get("explicit_gap"))
        or normalize_text(state_map.get("current_debt"))
        or normalize_text(state_map.get("next_bite"))
    )
    next_local_choice = normalize_text(resume_bridge.get("next_local_choice"))
    known_object = (
        normalize_text(resume_bridge.get("known_object"))
        or normalize_text(state_map.get("current_object"))
    )
    ask_surface = (
        normalize_text(resume_bridge.get("ask_surface"))
        or normalize_text(state_map.get("asked_medium_surface"))
    )

    same_carrier_preferred = resume_bridge.get("same_carrier_preferred")
    if not isinstance(same_carrier_preferred, bool):
        same_carrier_preferred = True

    release_veto_active = state_map.get("release_veto") is True
    supervisory_signals = supervisory_signals_from_report(report_map)
    task_incomplete = (
        release_veto_active
        and not final_artifact_materialized
        and bool(explicit_gap or next_local_choice or known_object or ask_surface)
    )
    thinner_carrier_due = (
        normalize_text(resume_bridge.get("mode")) == "reopen_on_thinner_carrier"
        and same_carrier_preferred is False
    )

    return CompletionSnapshot(
        release_veto_active=release_veto_active,
        release_allowed=report_map.get("release_allowed") is True,
        final_artifact_materialized=final_artifact_materialized,
        task_incomplete=task_incomplete,
        explicit_gap=explicit_gap,
        next_local_choice=next_local_choice,
        known_object=known_object,
        ask_surface=ask_surface,
        same_carrier_preferred=same_carrier_preferred,
        thinner_carrier_due=thinner_carrier_due,
        supervisory_signals=supervisory_signals,
        supervisor_active=bool(supervisory_signals),
    )


def build_completion_snapshot(
    state: object,
    report: object,
) -> CompletionSnapshot:
    return completion_gap_snapshot(state, report)


def blocking_report_problems(
    report: object,
    *,
    ignored_problems: Collection[str] = IGNORED_STALL_PROBLEMS,
) -> tuple[str, ...]:
    report_map = _mapping(report)
    problems = report_map.get("problems")
    if not isinstance(problems, list):
        return ()
    filtered: list[str] = []
    ignored = {normalize_text(problem) for problem in ignored_problems}
    for problem in problems:
        text = normalize_text(problem)
        if text and text not in ignored:
            filtered.append(text)
    return tuple(filtered)


def continuation_trigger_signals(
    state: object,
    report: object,
    *,
    snapshot: CompletionSnapshot | None = None,
) -> tuple[str, ...]:
    state_map = _mapping(state)
    report_map = _mapping(report)
    completion = snapshot or completion_gap_snapshot(state_map, report_map)

    signals = list(completion.supervisory_signals)
    layer = _mapping(report_map.get("layer_composition"))
    if layer.get("active") is True:
        signals.append("active_layer")
    if layer.get("must_bind_local_bite") is True:
        signals.append("must_bind_local_bite")
    if layer.get("must_spend_handoff") is True:
        signals.append("must_spend_handoff")

    if not signals:
        if completion.explicit_gap:
            signals.append("unfinished_current_layer")
        if normalize_text(state_map.get("current_seam")):
            signals.append("live_seam")
        if completion.next_local_choice:
            signals.append("supervisor_gap")

    return _dedupe_ordered(signals)


def continuation_allowed_surfaces(
    state: object,
    *,
    required_action: str,
    snapshot: CompletionSnapshot | None = None,
) -> tuple[str, ...]:
    state_map = _mapping(state)
    completion = snapshot or completion_gap_snapshot(state_map, {})
    action = normalize_text(required_action) or DEFAULT_REQUIRED_ACTION

    allowed: list[str] = [DEFAULT_REQUIRED_ACTION]
    if action == "spend_local":
        allowed = ["spend_local", DEFAULT_REQUIRED_ACTION]
    elif isinstance(state_map.get("carrier_handoff_if_any"), Mapping):
        allowed = ["spend_local", DEFAULT_REQUIRED_ACTION]
    elif action in {DEFAULT_REQUIRED_ACTION, "land_local"}:
        allowed = [DEFAULT_REQUIRED_ACTION, "rebind_local_pressure"]

    if (
        completion.same_carrier_preferred is False
        and "rebind_local_pressure" not in allowed
    ):
        allowed.append("rebind_local_pressure")

    return _dedupe_ordered(allowed)


def continuation_surface(state: object, report: object) -> str:
    state_map = _mapping(state)
    report_map = _mapping(report)
    layer = _mapping(report_map.get("layer_composition"))
    return (
        normalize_text(layer.get("surface"))
        or (
            "carrier_handoff"
            if isinstance(state_map.get("carrier_handoff_if_any"), Mapping)
            else DEFAULT_STALL_SURFACE
        )
    )


def match_continuable_stall_rule(normalized_reason: str) -> BlockerRule | None:
    for rule in CONTINUABLE_STALL_RULES:
        for fragment in rule.reason_fragments:
            if fragment == normalized_reason or fragment in normalized_reason:
                return rule
    return None


def classify_runtime_blocker(
    state: object,
    report: object,
    *,
    required_action: str,
    refusal_reason: object,
    ignored_problems: Collection[str] = IGNORED_STALL_PROBLEMS,
) -> BlockerAssessment:
    state_map = _mapping(state)
    report_map = _mapping(report)
    snapshot = completion_gap_snapshot(state_map, report_map)
    normalized_reason = normalize_refusal_reason(refusal_reason)

    if not state_map or not report_map:
        return BlockerAssessment(
            disposition="terminal",
            code=BLOCKER_INVALID_STATE,
            refusal_reason=normalized_reason,
            snapshot=snapshot,
        )

    if snapshot.release_veto_active is not True:
        return BlockerAssessment(
            disposition="not_applicable",
            code=BLOCKER_RELEASE_NOT_BLOCKED,
            refusal_reason=normalized_reason,
            snapshot=snapshot,
        )

    rule = match_continuable_stall_rule(normalized_reason)
    if rule is None:
        return BlockerAssessment(
            disposition="terminal",
            code=BLOCKER_NONCONTINUABLE_REFUSAL,
            refusal_reason=normalized_reason,
            snapshot=snapshot,
        )

    blocking_problems = blocking_report_problems(
        report_map,
        ignored_problems=ignored_problems,
    )
    if blocking_problems:
        return BlockerAssessment(
            disposition="terminal",
            code=BLOCKER_BLOCKING_PROBLEMS,
            refusal_reason=normalized_reason,
            snapshot=snapshot,
            blocking_problems=blocking_problems,
        )

    if snapshot.task_incomplete is not True:
        return BlockerAssessment(
            disposition="terminal",
            code=BLOCKER_NO_LIVE_COMPLETION_GAP,
            refusal_reason=normalized_reason,
            snapshot=snapshot,
        )

    trigger_signals = continuation_trigger_signals(
        state_map,
        report_map,
        snapshot=snapshot,
    )
    if not trigger_signals:
        return BlockerAssessment(
            disposition="terminal",
            code=BLOCKER_NO_TRIGGER_SIGNALS,
            refusal_reason=normalized_reason,
            snapshot=snapshot,
        )

    continuation = StallContinuation(
        active=True,
        mode=DEFAULT_CONTINUATION_MODE,
        required_action=normalize_text(required_action) or DEFAULT_REQUIRED_ACTION,
        refusal_reason=normalized_reason,
        trigger_signals=trigger_signals,
        allowed_transition_surfaces=continuation_allowed_surfaces(
            state_map,
            required_action=required_action,
            snapshot=snapshot,
        ),
        surface=continuation_surface(state_map, report_map),
        completion_gap=snapshot,
    )
    return BlockerAssessment(
        disposition="retryable",
        code=rule.code,
        refusal_reason=normalized_reason,
        snapshot=snapshot,
        trigger_signals=trigger_signals,
        continuation=continuation,
    )


def build_continuation_budget(
    state: object,
    report: object,
    *,
    required_action: str,
    minimum_rounds: int = DEFAULT_CONTINUATION_BUDGET,
    maximum_rounds: int = MAX_CONTINUATION_BUDGET,
) -> ContinuationBudget:
    if minimum_rounds < 1:
        raise ValueError("minimum_rounds must be at least 1")
    if maximum_rounds < minimum_rounds:
        raise ValueError("maximum_rounds must be greater than or equal to minimum_rounds")

    snapshot = completion_gap_snapshot(state, report)
    action = normalize_text(required_action)
    adjustments = (
        BudgetAdjustment(
            code="unfinished_gap",
            delta=1,
            applied=snapshot.task_incomplete,
            reason="one extra round is useful when release is still blocked by a live gap",
        ),
        BudgetAdjustment(
            code="supervisor_active",
            delta=1,
            applied=snapshot.supervisor_active,
            reason="supervisory signals justify one more recompetition attempt",
        ),
        BudgetAdjustment(
            code="thinner_carrier_or_landing",
            delta=1,
            applied=snapshot.thinner_carrier_due or action == "land_local",
            reason="landing or thinner-carrier pressure benefits from one extra continuation cycle",
        ),
    )

    rounds = minimum_rounds + sum(
        adjustment.delta for adjustment in adjustments if adjustment.applied
    )
    rounds = max(minimum_rounds, min(rounds, maximum_rounds))
    return ContinuationBudget(
        recommended_rounds=rounds,
        minimum_rounds=minimum_rounds,
        maximum_rounds=maximum_rounds,
        required_action=action or DEFAULT_REQUIRED_ACTION,
        snapshot=snapshot,
        adjustments=adjustments,
    )


def continuation_round_budget(
    state: object,
    report: object,
    *,
    required_action: str,
    minimum_rounds: int = DEFAULT_CONTINUATION_BUDGET,
    maximum_rounds: int = MAX_CONTINUATION_BUDGET,
) -> int:
    return build_continuation_budget(
        state,
        report,
        required_action=required_action,
        minimum_rounds=minimum_rounds,
        maximum_rounds=maximum_rounds,
    ).recommended_rounds


def _load_runtime_state_and_report(state_path: Path) -> tuple[dict[str, object], dict[str, object]]:
    from runtime_guard import build_report, load_json

    state = load_json(state_path)
    report = build_report(state, state_path)
    return state, report


def _load_runtime_consume_entrypoints():
    from runtime_consume import (
        autonomous_transition_pressure,
        build_inspect_surface,
        run_bind_local_once,
        synthesize_execute_local_worked_step,
    )

    return (
        build_inspect_surface,
        run_bind_local_once,
        autonomous_transition_pressure,
        synthesize_execute_local_worked_step,
    )


def _completed_from_runtime(state: RuntimeMapping, report: RuntimeMapping) -> bool:
    return state.get("release_veto") is not True or report.get("release_allowed") is True


def _required_action_from_payloads(*payloads: object) -> str:
    for payload in payloads:
        payload_map = _mapping(payload)
        action = normalize_text(payload_map.get("required_action"))
        if action:
            return action
        if payload_map.get("pending_transition") is True:
            allowed = payload_map.get("allowed_transition_surfaces")
            if isinstance(allowed, list):
                for candidate in allowed:
                    normalized = normalize_text(candidate)
                    if normalized:
                        return normalized
            binding_action = normalize_text(payload_map.get("binding_action"))
            if binding_action.startswith("pending_"):
                inferred = normalize_text(binding_action.removeprefix("pending_"))
                if inferred:
                    return inferred
    return ""


def _payload_requests_continuation(payload: object) -> bool:
    payload_map = _mapping(payload)
    if payload_map.get("pending_transition") is not True:
        return False
    if normalize_text(payload_map.get("required_action")):
        return True
    allowed = payload_map.get("allowed_transition_surfaces")
    if isinstance(allowed, list) and any(normalize_text(value) for value in allowed):
        return True
    binding_action = normalize_text(payload_map.get("binding_action"))
    return binding_action.startswith("pending_")


def _supervisor_progress_fingerprint(
    state: RuntimeMapping,
    report: RuntimeMapping,
    *,
    required_action: str,
) -> tuple[object, ...]:
    bound_program = _mapping(state.get("bound_program"))
    handoff = _mapping(state.get("carrier_handoff_if_any"))
    layer = _mapping(report.get("layer_composition"))
    output_status = _mapping(state.get("output_status"))
    active_combo = ()
    combo = layer.get("active_skill_combo_if_any")
    if isinstance(combo, list):
        active_combo = tuple(normalize_text(value) for value in combo if normalize_text(value))
    return (
        state.get("release_veto") is True,
        normalize_text(required_action),
        normalize_text(bound_program.get("kind")),
        normalize_text(bound_program.get("target")),
        normalize_text(bound_program.get("operation")),
        normalize_text(handoff.get("target")),
        normalize_text(state.get("current_object")),
        normalize_text(state.get("current_seam")),
        normalize_text(state.get("current_debt")),
        normalize_text(state.get("next_bite")),
        active_combo,
        output_status.get("touched") is True,
    )


def _explicit_supervisor_blocker(
    *,
    code: str,
    reason: str,
    snapshot: CompletionSnapshot,
) -> BlockerAssessment:
    return BlockerAssessment(
        disposition="terminal",
        code=code,
        refusal_reason=normalize_refusal_reason(reason),
        snapshot=snapshot,
    )


def _finalize_supervisor_result(
    *,
    state_file: Path,
    inspect_payload: dict[str, object],
    inspect_exit_code: int,
    final_payload: dict[str, object],
    final_exit_code: int,
    required_action: str,
    completed: bool,
    action_payload: dict[str, object] | None,
    action_exit_code: int | None,
    blocker: BlockerAssessment | None,
    continuation_budget: ContinuationBudget | None,
    executed_rounds: int,
    step_history: list[str],
    reason: str,
) -> SupervisorRunResult:
    return SupervisorRunResult(
        state_file=str(state_file),
        completed=completed,
        inspect_first=True,
        inspect_payload=inspect_payload,
        inspect_exit_code=inspect_exit_code,
        final_payload=final_payload,
        final_exit_code=final_exit_code,
        required_action=normalize_text(required_action),
        action_payload=action_payload,
        action_exit_code=action_exit_code,
        blocker=blocker,
        continuation_budget=continuation_budget,
        executed_rounds=executed_rounds,
        step_history=tuple(step_history),
        reason=normalize_text(reason),
    )


def run_until_done_supervisor(
    state_path: str | Path,
    *,
    allow_handoff: bool = False,
    spend_handoff: bool = False,
    allow_rival: bool = False,
    previous_state: str | None = None,
    worked_step: str | None = None,
    summary: str | None = None,
    output_file: str | None = None,
    cosmetic_only: bool | None = None,
    contains_unsupported: bool | None = None,
    contains_placeholder: bool | None = None,
    allow_autonomous_transition: bool = False,
    stop_after_inspect: bool = False,
    max_supervisor_rounds: int | None = None,
    auto_execute_local: bool = True,
    stagnation_limit: int = 3,
) -> SupervisorRunResult:
    state_file = Path(state_path)
    if max_supervisor_rounds is not None and max_supervisor_rounds < 1:
        raise ValueError("max_supervisor_rounds must be at least 1 when provided")
    if stagnation_limit < 1:
        raise ValueError("stagnation_limit must be at least 1")

    (
        build_inspect_surface,
        run_bind_local_once,
        autonomous_transition_pressure,
        synthesize_execute_local_worked_step,
    ) = _load_runtime_consume_entrypoints()
    inspect_payload, inspect_exit_code = build_inspect_surface(
        state_file,
        allow_autonomous_transition=allow_autonomous_transition,
    )
    step_history = ["inspect"]

    state, report = _load_runtime_state_and_report(state_file)
    required_action = _required_action_from_payloads(inspect_payload)
    continuation_budget = build_continuation_budget(
        state,
        report,
        required_action=required_action or DEFAULT_REQUIRED_ACTION,
    )
    completed = _completed_from_runtime(state, report)
    if stop_after_inspect or completed:
        return _finalize_supervisor_result(
            state_file=state_file,
            inspect_payload=inspect_payload,
            inspect_exit_code=inspect_exit_code,
            final_payload=inspect_payload,
            final_exit_code=inspect_exit_code,
            required_action=required_action,
            completed=completed,
            action_payload=None,
            action_exit_code=None,
            blocker=None,
            continuation_budget=continuation_budget,
            executed_rounds=0,
            step_history=step_history,
            reason=(
                "inspect_complete"
                if completed
                else "inspect_only_boundary"
            ),
        )

    latest_final_payload = inspect_payload
    latest_final_exit_code = inspect_exit_code
    latest_action_payload: dict[str, object] | None = None
    latest_action_exit_code: int | None = None
    latest_blocker: BlockerAssessment | None = None
    round_index = 0
    manual_worked_step_consumed = False
    strict_execute_step = False
    strict_execute_refusal_reason = ""
    seen_fingerprints: dict[tuple[object, ...], int] = {}

    while True:
        state, report = _load_runtime_state_and_report(state_file)
        required_action = _required_action_from_payloads(
            latest_final_payload,
            latest_action_payload,
        )
        continuation_budget = build_continuation_budget(
            state,
            report,
            required_action=required_action or DEFAULT_REQUIRED_ACTION,
        )
        if _completed_from_runtime(state, report):
            return _finalize_supervisor_result(
                state_file=state_file,
                inspect_payload=inspect_payload,
                inspect_exit_code=inspect_exit_code,
                final_payload=latest_final_payload,
                final_exit_code=latest_final_exit_code,
                required_action=required_action,
                completed=True,
                action_payload=latest_action_payload,
                action_exit_code=latest_action_exit_code,
                blocker=latest_blocker,
                continuation_budget=continuation_budget,
                executed_rounds=round_index,
                step_history=step_history,
                reason="release_allowed",
            )

        if max_supervisor_rounds is not None and round_index >= max_supervisor_rounds:
            latest_blocker = _explicit_supervisor_blocker(
                code=BLOCKER_STRUCTURAL_HOP_LIMIT,
                reason="the explicit supervisor reached its configured round cap before completion",
                snapshot=completion_gap_snapshot(state, report),
            )
            return _finalize_supervisor_result(
                state_file=state_file,
                inspect_payload=inspect_payload,
                inspect_exit_code=inspect_exit_code,
                final_payload=latest_final_payload,
                final_exit_code=latest_final_exit_code,
                required_action=required_action,
                completed=False,
                action_payload=latest_action_payload,
                action_exit_code=latest_action_exit_code,
                blocker=latest_blocker,
                continuation_budget=continuation_budget,
                executed_rounds=round_index,
                step_history=step_history,
                reason="supervisor_round_cap_reached",
            )

        if required_action != "execute_local":
            strict_execute_step = False
            strict_execute_refusal_reason = ""

        active_worked_step = worked_step if normalize_text(worked_step) and not manual_worked_step_consumed else None
        active_summary = summary
        if required_action == "execute_local":
            if active_worked_step is not None:
                manual_worked_step_consumed = True
            elif auto_execute_local:
                active_worked_step, active_summary = synthesize_execute_local_worked_step(
                    dict(state),
                    dict(report),
                    strict=strict_execute_step,
                    prior_refusal_reason=strict_execute_refusal_reason,
                )
            else:
                latest_blocker = _explicit_supervisor_blocker(
                    code=BLOCKER_EXECUTE_LOCAL_INPUT_REQUIRED,
                    reason="execute_local requires an explicit worked_step input",
                    snapshot=completion_gap_snapshot(state, report),
                )
                return _finalize_supervisor_result(
                    state_file=state_file,
                    inspect_payload=inspect_payload,
                    inspect_exit_code=inspect_exit_code,
                    final_payload=latest_final_payload,
                    final_exit_code=latest_final_exit_code,
                    required_action=required_action,
                    completed=False,
                    action_payload=latest_action_payload,
                    action_exit_code=latest_action_exit_code,
                    blocker=latest_blocker,
                    continuation_budget=continuation_budget,
                    executed_rounds=round_index,
                    step_history=step_history,
                    reason="execute_local_input_required",
                )

        bootstrap_context = _mapping(state.get("bootstrap_context"))
        pressure = autonomous_transition_pressure(
            dict(state),
            dict(report),
            bootstrap_context=dict(bootstrap_context),
            runtime_evidence={},
        )
        pressure_allow_handoff = isinstance(pressure, dict) and pressure.get("allow_handoff") is True
        pressure_spend_handoff = isinstance(pressure, dict) and pressure.get("spend_handoff") is True
        explicit_handoff = isinstance(state.get("carrier_handoff_if_any"), Mapping)
        round_allow_handoff = allow_handoff or pressure_allow_handoff or explicit_handoff or required_action == "spend_local"
        round_spend_handoff = spend_handoff or pressure_spend_handoff or required_action == "spend_local"

        latest_action_payload, latest_action_exit_code = run_bind_local_once(
            state_file,
            allow_handoff=round_allow_handoff,
            spend_handoff=round_spend_handoff,
            allow_rival=allow_rival,
            previous_state=previous_state,
            worked_step=active_worked_step,
            summary=active_summary,
            output_file=output_file,
            cosmetic_only=cosmetic_only,
            contains_unsupported=contains_unsupported,
            contains_placeholder=contains_placeholder,
        )
        step_history.append("execute")

        latest_final_payload, latest_final_exit_code = build_inspect_surface(
            state_file,
            allow_autonomous_transition=False,
        )
        step_history.append("reinspect")

        state, report = _load_runtime_state_and_report(state_file)
        required_action = _required_action_from_payloads(
            latest_final_payload,
            latest_action_payload,
        )
        continuation_budget = build_continuation_budget(
            state,
            report,
            required_action=required_action or DEFAULT_REQUIRED_ACTION,
        )
        completed = _completed_from_runtime(state, report)
        if completed:
            return _finalize_supervisor_result(
                state_file=state_file,
                inspect_payload=inspect_payload,
                inspect_exit_code=inspect_exit_code,
                final_payload=latest_final_payload,
                final_exit_code=latest_final_exit_code,
                required_action=required_action,
                completed=True,
                action_payload=latest_action_payload,
                action_exit_code=latest_action_exit_code,
                blocker=None,
                continuation_budget=continuation_budget,
                executed_rounds=round_index + 1,
                step_history=step_history,
                reason="supervisor_completed",
            )

        if latest_action_exit_code == 0:
            strict_execute_step = False
            strict_execute_refusal_reason = ""

        latest_blocker = None
        fingerprint = _supervisor_progress_fingerprint(
            state,
            report,
            required_action=required_action,
        )
        seen_fingerprints[fingerprint] = seen_fingerprints.get(fingerprint, 0) + 1
        if seen_fingerprints[fingerprint] >= stagnation_limit:
            latest_blocker = _explicit_supervisor_blocker(
                code=BLOCKER_SUPERVISOR_STAGNATION_GUARD,
                reason="the supervisor saw the same live layer fingerprint repeatedly without honest progress",
                snapshot=completion_gap_snapshot(state, report),
            )
            return _finalize_supervisor_result(
                state_file=state_file,
                inspect_payload=inspect_payload,
                inspect_exit_code=inspect_exit_code,
                final_payload=latest_final_payload,
                final_exit_code=latest_final_exit_code,
                required_action=required_action,
                completed=False,
                action_payload=latest_action_payload,
                action_exit_code=latest_action_exit_code,
                blocker=latest_blocker,
                continuation_budget=continuation_budget,
                executed_rounds=round_index + 1,
                step_history=step_history,
                reason="supervisor_stagnation_guard",
            )

        if latest_action_exit_code and latest_action_exit_code != 0:
            refusal_reason = (
                normalize_text(_mapping(latest_action_payload).get("reason", ""))
                or normalize_text(_mapping(latest_final_payload).get("reason", ""))
            )
            normalized_refusal = refusal_reason.lower()
            if "visible skill expression is required on the live layer" in normalized_refusal:
                strict_execute_step = True
                strict_execute_refusal_reason = refusal_reason
                round_index += 1
                continue
            if "worked_step only reported that something was solved" in normalized_refusal:
                strict_execute_step = True
                strict_execute_refusal_reason = refusal_reason
                round_index += 1
                continue
            if "ordinary fallback action" in normalized_refusal:
                strict_execute_step = True
                strict_execute_refusal_reason = refusal_reason
                round_index += 1
                continue
            if _payload_requests_continuation(latest_action_payload) or _payload_requests_continuation(
                latest_final_payload
            ):
                round_index += 1
                continue
            latest_blocker = classify_runtime_blocker(
                state,
                report,
                required_action=required_action or DEFAULT_REQUIRED_ACTION,
                refusal_reason=refusal_reason,
            )
            if latest_blocker.retryable:
                round_index += 1
                continue
            return _finalize_supervisor_result(
                state_file=state_file,
                inspect_payload=inspect_payload,
                inspect_exit_code=inspect_exit_code,
                final_payload=latest_final_payload,
                final_exit_code=latest_final_exit_code,
                required_action=required_action,
                completed=False,
                action_payload=latest_action_payload,
                action_exit_code=latest_action_exit_code,
                blocker=latest_blocker,
                continuation_budget=continuation_budget,
                executed_rounds=round_index + 1,
                step_history=step_history,
                reason="terminal_blocker",
            )

        round_index += 1


__all__ = [
    "BLOCKER_AMBIGUOUS_BIND_LOCAL",
    "BLOCKER_AMBIGUOUS_NEXT_TOUCH",
    "BLOCKER_AMBIGUOUS_THINNER_CARRIER",
    "BLOCKER_BLOCKING_PROBLEMS",
    "BLOCKER_EXECUTE_LOCAL_INPUT_REQUIRED",
    "BLOCKER_INVALID_STATE",
    "BLOCKER_NO_LIVE_COMPLETION_GAP",
    "BLOCKER_NO_TRIGGER_SIGNALS",
    "BLOCKER_NONCONTINUABLE_REFUSAL",
    "BLOCKER_RELEASE_NOT_BLOCKED",
    "BLOCKER_SAME_CARRIER_INFERENCE_FAILURE",
    "BLOCKER_SAME_CARRIER_LAYER_STALLED",
    "BLOCKER_STRUCTURAL_HOP_LIMIT",
    "BLOCKER_SUPERVISOR_STAGNATION_GUARD",
    "BLOCKER_UNRESOLVED_RIVAL",
    "BlockerAssessment",
    "BlockerDisposition",
    "BudgetAdjustment",
    "CompletionGapPayload",
    "CompletionSnapshot",
    "CompletionSnapshotPayload",
    "ContinuationBudget",
    "SupervisorRunResult",
    "DEFAULT_CONTINUATION_BUDGET",
    "DEFAULT_CONTINUATION_MODE",
    "DEFAULT_REQUIRED_ACTION",
    "IGNORED_STALL_PROBLEMS",
    "MAX_CONTINUATION_BUDGET",
    "OutputStatus",
    "StallContinuation",
    "StallContinuationPayload",
    "blocking_report_problems",
    "completion_gap_snapshot",
    "build_completion_snapshot",
    "build_continuation_budget",
    "classify_runtime_blocker",
    "continuation_allowed_surfaces",
    "continuation_round_budget",
    "continuation_surface",
    "continuation_trigger_signals",
    "match_continuable_stall_rule",
    "normalize_refusal_reason",
    "normalize_text",
    "run_until_done_supervisor",
    "supervisory_signals_from_report",
]
