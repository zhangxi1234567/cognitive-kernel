#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from runtime_guard import (
    ALLOWED_PRIMITIVES,
    build_report,
    canonicalize_primitive_token,
    is_allowed_primitive_token,
    primitive_competition_is_stale,
    derive_bound_program_candidate,
    derive_gate_binding_candidate,
    derive_handoff_candidate,
    derive_primitive_field_candidate,
    derive_primitive_program_candidate,
    load_json,
    primitive_is_probe_like,
    primitive_field_is_stale,
)


DEFAULT_STATE = {
    "current_object": "",
    "current_seam": "",
    "current_debt": "",
    "next_bite": "",
    "asked_medium_surface": "",
    "revocation_handle": "",
    "uncertainty_mode": "unknown",
    "primary_slot": "",
    "bound_program": None,
    "gate_binding_if_any": None,
    "primitive_field_if_any": None,
    "primitive_competition_if_any": None,
    "carrier_handoff_if_any": None,
    "secondary_rival_if_any": None,
    "materialization_evidence": None,
    "release_veto": True,
    "unresolved_markers": [],
    "output_status": {
        "touched": False,
        "cosmetic_only": False,
        "contains_unsupported": False,
        "contains_placeholder": False,
        "final_artifact_materialized": False,
    },
    "memory_residue": [],
}

ALLOWED_RESIDUE_KINDS = {
    "competition_texture",
    "distrust_bias",
    "witness_readiness",
    "readout_sensitivity",
    "boundary_residue",
}


class StateLock:
    def __init__(self, state_path: Path, timeout_seconds: float = 5.0) -> None:
        self.state_path = state_path
        self.lock_path = state_path.with_suffix(state_path.suffix + ".lock")
        self.timeout_seconds = timeout_seconds
        self.acquired = False

    def __enter__(self) -> "StateLock":
        deadline = time.time() + self.timeout_seconds
        while True:
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                self.acquired = True
                return self
            except FileExistsError:
                if time.time() >= deadline:
                    raise SystemExit(f"state lock timeout: {self.lock_path}")
                time.sleep(0.05)

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.acquired and self.lock_path.exists():
            self.lock_path.unlink()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def event_log_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.events.jsonl")


def _deep_copy(payload: dict) -> dict:
    return json.loads(json.dumps(payload))


def _report_excerpt(report: dict) -> dict:
    excerpt: dict = {}
    for key in [
        "gap_object",
        "resume_bridge",
        "primitive_field",
        "primitive_competition",
        "skill_field",
        "skill_competition",
        "skill_inhibition",
        "skill_authority_bridge",
        "probe_discipline",
        "discipline_contract",
        "interlayer_discharge_bridge",
        "closure_nucleus",
        "warnings",
        "problems",
    ]:
        value = report.get(key)
        if value not in (None, {}, [], ""):
            excerpt[key] = value
    return excerpt


def _event_kind(command_name: str) -> str:
    if command_name in {"bind-local", "rebind-local", "spend-local"}:
        return "consumption"
    if command_name == "init":
        return "bootstrap"
    return "mutation"


def _state_focus_summary(state: dict) -> dict:
    summary: dict = {
        "current_object": state.get("current_object", ""),
        "current_seam": state.get("current_seam", ""),
        "current_debt": state.get("current_debt", ""),
        "next_bite": state.get("next_bite", ""),
        "asked_medium_surface": state.get("asked_medium_surface", ""),
        "release_veto": state.get("release_veto"),
    }
    for key in [
        "bound_program",
        "gate_binding_if_any",
        "primitive_field_if_any",
        "primitive_competition_if_any",
        "carrier_handoff_if_any",
        "secondary_rival_if_any",
    ]:
        value = state.get(key)
        if value not in (None, {}, [], ""):
            summary[key] = value
    return summary


def append_runtime_event(
    path: Path,
    *,
    command_name: str,
    before: dict | None,
    after: dict,
    report: dict | None = None,
    note: str = "",
) -> None:
    if report is None:
        report = build_report(after, path)
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "command": command_name,
        "event_kind": _event_kind(command_name),
        "before": _state_focus_summary(before or {}),
        "after": _state_focus_summary(after),
        "report_excerpt": _report_excerpt(report),
    }
    if note:
        event["note"] = note
    log_path = event_log_path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=True) + "\n")


def load_runtime_events(path: Path) -> list[dict]:
    log_path = event_log_path(path)
    if not log_path.exists():
        return []
    events: list[dict] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(payload)
    return events


def build_runtime_evidence(path: Path) -> dict:
    events = load_runtime_events(path)
    consumption_events = [
        event for event in events if str(event.get("event_kind", "")).strip() == "consumption"
    ]
    latest = events[-1] if events else {}
    latest_consumption = consumption_events[-1] if consumption_events else {}
    return {
        "event_log": str(event_log_path(path)),
        "event_count": len(events),
        "consumption_event_count": len(consumption_events),
        "latest_event_command": str(latest.get("command", "")).strip(),
        "latest_consumption_command": str(latest_consumption.get("command", "")).strip(),
        "has_runtime_consumption": bool(consumption_events),
        "runtime_subject_qualified": bool(consumption_events),
    }


def render_runtime_trace_markdown(path: Path) -> str:
    events = load_runtime_events(path)
    if not events:
        return (
            "# Runtime Trace\n\n"
            "No runtime events were captured for this state file.\n"
        )

    lines = ["# Runtime Trace", ""]
    for index, event in enumerate(events, start=1):
        command = str(event.get("command", "")).strip() or "unknown"
        event_kind = str(event.get("event_kind", "")).strip() or "unknown"
        lines.append(f"## Event {index}: `{command}`")
        lines.append(f"- Time: `{str(event.get('ts', '')).strip()}`")
        lines.append(f"- Kind: `{event_kind}`")
        note = str(event.get("note", "")).strip()
        if note:
            lines.append(f"- Note: {note}")
        after = event.get("after", {})
        if isinstance(after, dict):
            current_object = str(after.get("current_object", "")).strip()
            current_debt = str(after.get("current_debt", "")).strip()
            next_bite = str(after.get("next_bite", "")).strip()
            if current_object:
                lines.append(f"- Object: `{current_object}`")
            if current_debt:
                lines.append(f"- Debt: {current_debt}")
            if next_bite:
                lines.append(f"- Next bite: {next_bite}")
        excerpt = event.get("report_excerpt", {})
        if isinstance(excerpt, dict):
            gap_object = excerpt.get("gap_object")
            if isinstance(gap_object, dict):
                gap_target = str(gap_object.get("object", "")).strip()
                if gap_target:
                    lines.append(f"- Gap object: `{gap_target}`")
            resume_bridge = excerpt.get("resume_bridge")
            if isinstance(resume_bridge, dict):
                resume_mode = str(resume_bridge.get("mode", "")).strip()
                if resume_mode:
                    lines.append(f"- Resume mode: `{resume_mode}`")
            skill_bridge = excerpt.get("skill_authority_bridge")
            if isinstance(skill_bridge, dict):
                winning_skill = str(skill_bridge.get("winning_skill_if_any", "")).strip()
                if winning_skill:
                    lines.append(f"- Winning skill: `{winning_skill}`")
            skill_inhibition = excerpt.get("skill_inhibition")
            if isinstance(skill_inhibition, dict):
                promoted = str(skill_inhibition.get("promoted_skill_if_any", "")).strip()
                if promoted:
                    lines.append(f"- Promoted skill: `{promoted}`")
            probe = excerpt.get("probe_discipline")
            if isinstance(probe, dict):
                active_hypothesis = str(probe.get("active_skill_hypothesis", "")).strip()
                if active_hypothesis:
                    lines.append(f"- Active hypothesis: `{active_hypothesis}`")
            primitive_field = excerpt.get("primitive_field")
            if isinstance(primitive_field, dict):
                active_primitives = primitive_field.get("active_primitives")
                if isinstance(active_primitives, list) and active_primitives:
                    lines.append(
                        "- Active primitives: "
                        + ", ".join(f"`{str(value).strip()}`" for value in active_primitives if str(value).strip())
                    )
            handoff = after.get("carrier_handoff_if_any")
            if isinstance(handoff, dict):
                lines.append(f"- Handoff target: `{str(handoff.get('to_object', '')).strip()}`")
            program = after.get("bound_program")
            if isinstance(program, dict):
                lines.append(
                    "- Bound program: "
                    f"`{str(program.get('kind', '')).strip()}` -> "
                    f"`{str(program.get('target', '')).strip()}`"
                )
        lines.append("")
    return "\n".join(lines)


def render_runtime_skill_trace_markdown(path: Path) -> str:
    events = load_runtime_events(path)
    if not events:
        return (
            "# Runtime Skill Trace\n\n"
            "No runtime events were captured for this state file.\n"
        )

    lines = ["# Runtime Skill Trace", ""]
    for index, event in enumerate(events, start=1):
        command = str(event.get("command", "")).strip() or "unknown"
        event_kind = str(event.get("event_kind", "")).strip() or "unknown"
        lines.append(f"## Event {index}: `{command}`")
        lines.append(f"- Kind: `{event_kind}`")

        excerpt = event.get("report_excerpt", {})
        after = event.get("after", {})
        if isinstance(excerpt, dict):
            gap_object = excerpt.get("gap_object", {})
            if isinstance(gap_object, dict):
                gap_target = str(gap_object.get("object", "")).strip()
                if gap_target:
                    lines.append(f"- Gap object: `{gap_target}`")
            resume_bridge = excerpt.get("resume_bridge", {})
            if isinstance(resume_bridge, dict):
                resume_mode = str(resume_bridge.get("mode", "")).strip()
                next_choice = str(resume_bridge.get("next_local_choice", "")).strip()
                if resume_mode:
                    lines.append(f"- Resume mode: `{resume_mode}`")
                if next_choice:
                    lines.append(f"- Resume choice: `{next_choice}`")
                supporting = resume_bridge.get("supporting_skills")
                if isinstance(supporting, list) and supporting:
                    lines.append(
                        "- Resume skill combo: "
                        + ", ".join(f"`{str(value).strip()}`" for value in supporting if str(value).strip())
                    )
            skill_field = excerpt.get("skill_field", {})
            if isinstance(skill_field, dict):
                active_skills = skill_field.get("active_skills")
                if isinstance(active_skills, list) and active_skills:
                    lines.append(
                        "- Active skills: "
                        + ", ".join(f"`{str(value).strip()}`" for value in active_skills if str(value).strip())
                    )
                background_skills = skill_field.get("background_skills_if_any")
                if isinstance(background_skills, list) and background_skills:
                    lines.append(
                        "- Background skills: "
                        + ", ".join(f"`{str(value).strip()}`" for value in background_skills if str(value).strip())
                    )
            skill_bridge = excerpt.get("skill_authority_bridge", {})
            if isinstance(skill_bridge, dict):
                winning_skill = str(skill_bridge.get("winning_skill_if_any", "")).strip()
                fallback_hint = str(skill_bridge.get("fallback_skill_hint_if_any", "")).strip()
                touch = project_bound_program_shape(
                    skill_bridge.get("executable_local_touch_if_any")
                )
                if winning_skill:
                    lines.append(f"- Skill owner: `{winning_skill}`")
                elif fallback_hint:
                    lines.append(f"- Skill hint: `{fallback_hint}`")
                supporting_skills = skill_bridge.get("supporting_skills_if_any")
                if isinstance(supporting_skills, list) and supporting_skills:
                    lines.append(
                        "- Supporting skills: "
                        + ", ".join(f"`{str(value).strip()}`" for value in supporting_skills if str(value).strip())
                    )
                if isinstance(touch, dict):
                    lines.append(
                        "- Authorized touch: "
                        f"`{str(touch.get('kind', '')).strip()}` -> "
                        f"`{str(touch.get('target', '')).strip()}`"
                    )
            skill_competition = excerpt.get("skill_competition", {})
            if isinstance(skill_competition, dict):
                winner = str(skill_competition.get("winning_skill_if_any", "")).strip()
                if winner:
                    lines.append(f"- Skill competition winner: `{winner}`")
                candidates = skill_competition.get("candidates")
                if isinstance(candidates, list) and candidates:
                    rendered = []
                    for candidate in candidates[:4]:
                        if not isinstance(candidate, dict):
                            continue
                        skill_name = str(candidate.get("skill", "")).strip()
                        target = str(candidate.get("touch_target", "")).strip()
                        if skill_name and target:
                            rendered.append(f"`{skill_name}`@`{target}`")
                        elif skill_name:
                            rendered.append(f"`{skill_name}`")
                    if rendered:
                        lines.append("- Skill candidates: " + ", ".join(rendered))
            skill_inhibition = excerpt.get("skill_inhibition", {})
            if isinstance(skill_inhibition, dict):
                promoted = str(skill_inhibition.get("promoted_skill_if_any", "")).strip()
                if promoted:
                    lines.append(f"- Promoted skill: `{promoted}`")
                demoted = skill_inhibition.get("demoted_skills")
                if isinstance(demoted, list) and demoted:
                    lines.append(
                        "- Demoted skills: "
                        + ", ".join(f"`{str(value).strip()}`" for value in demoted if str(value).strip())
                    )
            probe = excerpt.get("probe_discipline", {})
            if isinstance(probe, dict):
                active_hypothesis = str(probe.get("active_skill_hypothesis", "")).strip()
                if active_hypothesis:
                    lines.append(f"- Active hypothesis: `{active_hypothesis}`")
            interlayer = excerpt.get("interlayer_discharge_bridge", {})
            if isinstance(interlayer, dict):
                mode = str(interlayer.get("mode", "")).strip()
                if mode:
                    lines.append(f"- Discharge bridge: `{mode}`")
            contract = excerpt.get("discipline_contract", {})
            if isinstance(contract, dict) and contract.get("active") is True:
                authorized = project_bound_program_shape(contract.get("authorized_bite"))
                if isinstance(authorized, dict):
                    lines.append(
                        "- Contract bite: "
                        f"`{str(authorized.get('kind', '')).strip()}` -> "
                        f"`{str(authorized.get('target', '')).strip()}`"
                    )
        if isinstance(after, dict):
            program = project_bound_program_shape(after.get("bound_program"))
            if isinstance(program, dict):
                lines.append(
                    "- Bound after event: "
                    f"`{str(program.get('kind', '')).strip()}` -> "
                    f"`{str(program.get('target', '')).strip()}`"
                )
            handoff = after.get("carrier_handoff_if_any")
            if isinstance(handoff, dict):
                handoff_target = str(handoff.get("to_object", "")).strip()
                if handoff_target:
                    lines.append(f"- Handoff after event: `{handoff_target}`")
        note = str(event.get("note", "")).strip()
        if note:
            lines.append(f"- Note: {note}")
        lines.append("")
    return "\n".join(lines)


def load_state(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing state file: {path}")
    return load_json(path)


def dump(payload: dict) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")


def mutate_state(path: Path, mutator, *, command_name: str = "") -> dict:
    with StateLock(path):
        state = load_state(path)
        before = _deep_copy(state)
        mutator(state)
        write_json(path, state)
        if command_name and before != state:
            append_runtime_event(path, command_name=command_name, before=before, after=state)
        return state


def apply_core_updates(state: dict, args: argparse.Namespace) -> None:
    for key in [
        "current_object",
        "current_seam",
        "current_debt",
        "next_bite",
        "asked_medium_surface",
        "revocation_handle",
        "uncertainty_mode",
        "primary_slot",
    ]:
        value = getattr(args, key, None)
        if value is not None:
            state[key] = value


def set_bound_program(state: dict, args: argparse.Namespace) -> None:
    state["bound_program"] = {
        "kind": args.kind,
        "target": args.target,
        "operation": args.operation,
    }
    if args.success_signal is not None:
        state["bound_program"]["success_signal"] = args.success_signal


def set_gate_binding(state: dict, args: argparse.Namespace) -> None:
    state["gate_binding_if_any"] = {
        "source_focus": args.source_focus,
        "source_target": args.source_target,
        "demoted_continuation": args.demoted_continuation,
        "authority_until": args.authority_until,
    }


def set_materialization_evidence(state: dict, args: argparse.Namespace) -> None:
    state["materialization_evidence"] = {
        "kind": args.evidence_kind,
        "location": args.evidence_location,
        "summary": args.evidence_summary,
    }


def set_primitive_field(state: dict, args: argparse.Namespace) -> None:
    primitive_field = {
        "layer_object": args.layer_object,
        "active_primitives": [
            canonicalize_primitive_token(value) for value in (args.active_primitive or [])
        ],
        "why_now": args.why_now,
    }
    if args.tie_break_check is not None:
        primitive_field["tie_break_check"] = args.tie_break_check
    if args.selection_basis is not None:
        primitive_field["selection_basis"] = args.selection_basis
    if args.evidence_basis is not None:
        primitive_field["evidence_basis"] = args.evidence_basis
    state["primitive_field_if_any"] = primitive_field


def set_primitive_competition(state: dict, args: argparse.Namespace) -> None:
    candidates: list[dict] = []
    for raw_candidate in args.candidate or []:
        primitive, touch_target, expected_local_gain = raw_candidate.split("|", 2)
        candidates.append(
            {
                "primitive": canonicalize_primitive_token(primitive),
                "touch_target": touch_target,
                "expected_local_gain": expected_local_gain,
            }
        )
    competition = {
        "layer_object": args.layer_object,
        "candidates": candidates,
    }
    if args.separating_check is not None:
        competition["separating_check"] = args.separating_check
    if args.winner_if_any is not None:
        competition["winner_if_any"] = canonicalize_primitive_token(args.winner_if_any)
    state["primitive_competition_if_any"] = competition


def project_bound_program_shape(payload: object) -> dict | None:
    if not isinstance(payload, dict):
        return None
    kind = str(payload.get("kind", "")).strip()
    target = str(payload.get("target", "")).strip()
    operation = str(payload.get("operation", "")).strip()
    success_signal = str(payload.get("success_signal", "")).strip()
    if not kind or not target or not operation:
        return None
    program = {
        "kind": kind,
        "target": target,
        "operation": operation,
    }
    if success_signal:
        program["success_signal"] = success_signal
    return program


def normalize_program_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def read_skill_authority_program(
    report: dict,
    *,
    require_same_carrier: bool,
) -> tuple[str, dict | None, bool]:
    bridge = report.get("skill_authority_bridge")
    if not isinstance(bridge, dict):
        return "", None, False
    if require_same_carrier and bridge.get("same_carrier_only") is not True:
        return "", None, False
    winning_skill = str(bridge.get("winning_skill_if_any", "")).strip()
    touch = project_bound_program_shape(bridge.get("executable_local_touch_if_any"))
    return winning_skill, touch, bridge.get("silence_after_contact") is True


def read_promoted_skill(report: dict) -> str:
    inhibition = report.get("skill_inhibition")
    if not isinstance(inhibition, dict):
        return ""
    return str(inhibition.get("promoted_skill_if_any", "")).strip()


def promoted_skill_gate_refusal(
    report: dict,
    *,
    winning_skill: str = "",
) -> str:
    if not isinstance(report, dict):
        return ""
    promoted_skill = read_promoted_skill(report)
    if not promoted_skill:
        return ""
    owned_by = str(winning_skill or "").strip()
    if not owned_by:
        return (
            "promoted skill gate refused: current layer promotes "
            f"{promoted_skill} but the foreground touch has no explicit skill owner"
        )
    if owned_by != promoted_skill:
        return (
            "promoted skill gate refused: current layer promotes "
            f"{promoted_skill} but the foreground touch is owned by {owned_by}"
        )
    return ""


def first_recoil_refusal(
    program: dict | None,
    report: dict,
    *,
    state: dict | None = None,
    winning_skill: str = "",
) -> str:
    if not isinstance(program, dict) or not isinstance(report, dict):
        return ""
    interlayer_bridge = read_interlayer_discharge_bridge(report)
    if isinstance(interlayer_bridge, dict):
        spend_first_program = interlayer_bridge.get("spend_first_program")
        if isinstance(spend_first_program, dict) and not programs_conflict(program, spend_first_program):
            return ""

    inhibition_state = report.get("inhibition_state")
    promoted_move = inhibition_state.get("promoted_move") if isinstance(inhibition_state, dict) else None
    gate_binding = report.get("control_bridge", {}).get("gate_binding") if isinstance(report.get("control_bridge"), dict) else None
    if not isinstance(promoted_move, dict) and not isinstance(gate_binding, dict):
        return ""

    program_target = str(program.get("target", "")).strip()
    program_kind = str(program.get("kind", "")).strip()
    asked_medium = (
        str(state.get("asked_medium_surface", "")).strip()
        if isinstance(state, dict)
        else ""
    )
    promoted_skill = ""
    skill_inhibition = report.get("skill_inhibition")
    if isinstance(skill_inhibition, dict):
        promoted_skill = str(skill_inhibition.get("promoted_skill_if_any", "")).strip()
    promoted_target = ""
    preferred_kinds: list[str] = []
    if isinstance(promoted_move, dict):
        promoted_target = str(promoted_move.get("touch_target", "")).strip()
        raw_kinds = promoted_move.get("preferred_kinds")
        if isinstance(raw_kinds, list):
            preferred_kinds = [str(value).strip() for value in raw_kinds if str(value).strip()]

    if isinstance(gate_binding, dict):
        gate_target = str(gate_binding.get("source_target", "")).strip()
        if gate_target and program_target and gate_target != program_target:
            return (
                "first recoil refused: current gate is still holding "
                f"{gate_target} but the foreground touch jumped to {program_target}"
            )

    if (winning_skill == "counter_question" or promoted_skill == "counter_question") and program_kind in {"check", "witness"}:
        return ""
    if (
        (winning_skill == "exact_closure" or promoted_skill == "exact_closure")
        and asked_medium
        and program_target == asked_medium
        and program_kind in {"write", "readout"}
    ):
        return ""
    if (
        asked_medium
        and program_target == asked_medium
        and promoted_target
        and "asked-medium closure" in promoted_target
        and program_kind in set(preferred_kinds or [])
    ):
        return ""
    if promoted_target and program_target and promoted_target != program_target:
        return (
            "first recoil refused: current promoted move still targets "
            f"{promoted_target} but the foreground touch jumped to {program_target}"
        )
    if preferred_kinds and program_kind and program_kind not in preferred_kinds:
        owner_text = f" under {winning_skill}" if winning_skill else ""
        return (
            "first recoil refused: current promoted move"
            f"{owner_text} prefers {', '.join(preferred_kinds)} but the foreground touch is {program_kind}"
        )
    return ""


def read_interlayer_discharge_bridge(report: dict) -> dict | None:
    bridge = report.get("interlayer_discharge_bridge")
    if not isinstance(bridge, dict):
        return None
    if str(bridge.get("mode", "")).strip() != "primitive_then_closure":
        return None

    spend_first = project_bound_program_shape(bridge.get("spend_first_program"))
    if spend_first is None:
        return None

    payload = {
        "mode": "primitive_then_closure",
        "reason": str(bridge.get("reason", "")).strip(),
        "spend_first_program": spend_first,
        "keep_closure_authority": bridge.get("keep_closure_authority") is True,
        "handoff_target": str(bridge.get("handoff_target", "")).strip(),
    }

    post_touch = project_bound_program_shape(bridge.get("post_closure_touch_if_any"))
    if post_touch is not None:
        payload["post_closure_touch_if_any"] = post_touch
    return payload


def programs_share_slot(left: dict | None, right: dict | None) -> bool:
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    return (
        str(left.get("kind", "")).strip() == str(right.get("kind", "")).strip()
        and str(left.get("target", "")).strip() == str(right.get("target", "")).strip()
    )


def programs_conflict(left: dict | None, right: dict | None) -> bool:
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    return not programs_share_slot(left, right)


def unbound_probe_refusal(program: dict | None, report: dict) -> str:
    if not isinstance(program, dict) or not isinstance(report, dict):
        return ""
    probe_discipline = report.get("probe_discipline")
    if not isinstance(probe_discipline, dict):
        return ""
    if probe_discipline.get("probe_must_bind") is not True:
        return ""
    if str(probe_discipline.get("active_skill_hypothesis", "")).strip():
        return ""
    if probe_discipline.get("unbound_probe_is_drift") is not True:
        return ""
    if not program_counts_as_probe(program, report):
        return ""
    return (
        "probe discipline refused: current probe-like bite is not bound to a live skill hypothesis"
    )


def probe_overreach_refusal(
    program: dict | None,
    report: dict,
    *,
    winning_skill: str = "",
) -> str:
    if not isinstance(program, dict) or not isinstance(report, dict):
        return ""
    if not program_counts_as_probe(program, report):
        return ""
    probe_discipline = report.get("probe_discipline")
    if not isinstance(probe_discipline, dict):
        return ""
    active_hypothesis = str(probe_discipline.get("active_skill_hypothesis", "")).strip()
    if not active_hypothesis:
        return ""
    if winning_skill == "counter_question":
        return ""
    if active_hypothesis in {"counter_question"}:
        return ""
    skill_competition = report.get("skill_competition")
    if isinstance(skill_competition, dict):
        for candidate in skill_competition.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            skill = str(candidate.get("skill", "")).strip()
            if skill and skill == active_hypothesis and skill not in {"counter_question"}:
                return (
                    "probe discipline refused: probe-like bite is trying to lead before the live skill "
                    f"hypothesis {active_hypothesis} is compressed into a thinner executable carrier"
                )
    return ""


def program_counts_as_probe(program: dict | None, report: dict) -> bool:
    if not isinstance(program, dict) or not isinstance(report, dict):
        return False
    probe_discipline = report.get("probe_discipline")
    if not isinstance(probe_discipline, dict):
        return False
    kind = str(program.get("kind", "")).strip()
    allowed_probe_kinds = probe_discipline.get("allowed_probe_kinds")
    if isinstance(allowed_probe_kinds, list) and kind in {
        str(value).strip() for value in allowed_probe_kinds
    }:
        return True
    primitive_field = report.get("primitive_field")
    if isinstance(primitive_field, dict):
        active_primitives = primitive_field.get("active_primitives")
        if isinstance(active_primitives, list):
            for value in active_primitives:
                if primitive_is_probe_like(value):
                    return True
    return False


def derive_local_agenda_for_program(
    state: dict,
    program: dict,
    *,
    winning_skill: str = "",
    report: dict | None = None,
) -> dict:
    program_target = str(program.get("target", "")).strip()
    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    current_seam = str(state.get("current_seam", "")).strip()
    interlayer_bridge = report.get("interlayer_discharge_bridge") if isinstance(report, dict) else None
    closure_retained_after_structural_spend = bool(
        winning_skill == "exact_closure"
        and isinstance(interlayer_bridge, dict)
        and interlayer_bridge.get("keep_closure_authority") is True
        and program_target
        and program_target != asked_medium
    )

    focus = "carrier"
    if closure_retained_after_structural_spend:
        post_touch = (
            project_bound_program_shape(interlayer_bridge.get("post_closure_touch_if_any"))
            if isinstance(interlayer_bridge, dict)
            else None
        )
        focus = "asked_medium"
        reason = (
            "one thinner-layer structural bite is being spent under closure authority; "
            "asked-medium closure should stay foregrounded until it can retake the slot"
        )
        return {
            "focus": focus,
            "touch_target": asked_medium or program_target,
            "reason": reason,
            "preferred_kinds": [
                str(post_touch.get("kind", "")).strip() or "readout"
            ] if isinstance(post_touch, dict) else ["readout", "write"],
        }
    if winning_skill == "exact_closure" or program_target == asked_medium:
        focus = "asked_medium"
    elif winning_skill == "counter_question":
        agenda = report.get("self_check_agenda") if isinstance(report, dict) else None
        agenda_focus = str(agenda.get("focus", "")).strip() if isinstance(agenda, dict) else ""
        if agenda_focus in {"seam", "rival", "asked_medium"}:
            focus = agenda_focus
        elif program_target and program_target == current_seam:
            focus = "seam"
        else:
            focus = "carrier"
    elif str(program.get("kind", "")).strip() in {"check", "witness"} and program_target == current_seam:
        focus = "seam"

    reason = "a concrete local bind has been purchased and should stay locally owned until it changes again"
    if winning_skill == "exact_closure":
        reason = "exact closure now owns one local touch and should keep foreground authority until asked-medium contact changes"
    elif winning_skill == "counter_question":
        reason = "one hostile falsifier now owns the slot and should keep local authority until it tears or lands"

    return {
        "focus": focus,
        "touch_target": program_target,
        "reason": reason,
    }


def maybe_cool_post_touch_surfaces(
    state: dict,
    program: dict,
    *,
    winning_skill: str = "",
    silence_after_contact: bool = False,
) -> None:
    if silence_after_contact is not True:
        return
    program_target = str(program.get("target", "")).strip()
    program_kind = str(program.get("kind", "")).strip()
    asked_medium = str(state.get("asked_medium_surface", "")).strip()

    if winning_skill == "exact_closure":
        if asked_medium and program_target == asked_medium:
            state["primitive_competition_if_any"] = None
            state["secondary_rival_if_any"] = None
            return

    if winning_skill == "counter_question" or program_kind in {"check", "witness"}:
        state["primitive_competition_if_any"] = None
        state["secondary_rival_if_any"] = None
        return

    if program_target and program_target == str(state.get("current_object", "")).strip():
        state["primitive_competition_if_any"] = None


def refresh_primitive_field_for_current_layer(
    state: dict,
    *,
    agenda_override: dict | None = None,
    handoff_override: dict | None = None,
    force: bool = False,
) -> None:
    if state.get("release_veto") is not True:
        return

    if primitive_competition_is_stale(
        state,
        agenda_override=agenda_override,
        handoff_override=handoff_override,
    ):
        state["primitive_competition_if_any"] = None

    stale_field = False
    if state.get("primitive_field_if_any") is not None:
        stale_field = primitive_field_is_stale(
            state,
            agenda_override=agenda_override,
            handoff_override=handoff_override,
        )
        if not force and not stale_field:
            return
        if stale_field:
            state["primitive_field_if_any"] = None

    candidate_primitive_field = derive_primitive_field_candidate(
        state,
        [],
        agenda_override=agenda_override,
        handoff_override=handoff_override,
    )
    if isinstance(candidate_primitive_field, dict):
        state["primitive_field_if_any"] = candidate_primitive_field


def require_core_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--current-object", "current_object"),
            ("--current-debt", "current_debt"),
            ("--next-bite", "next_bite"),
            ("--asked-medium-surface", "asked_medium_surface"),
            ("--revocation-handle", "revocation_handle"),
            ("--primary-slot", "primary_slot"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit(f"init requires core live-state fields: {', '.join(missing)}")


def require_bound_program_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--kind", "kind"),
            ("--target", "target"),
            ("--operation", "operation"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit(
            "bound program requires: " + ", ".join(missing)
        )


def require_gate_binding_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--source-focus", "source_focus"),
            ("--source-target", "source_target"),
            ("--demoted-continuation", "demoted_continuation"),
            ("--authority-until", "authority_until"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit("gate binding requires: " + ", ".join(missing))


def require_materialization_evidence_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--evidence-kind", "evidence_kind"),
            ("--evidence-location", "evidence_location"),
            ("--evidence-summary", "evidence_summary"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit(
            "materialization evidence requires: " + ", ".join(missing)
        )


def require_primitive_field_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--layer-object", "layer_object"),
            ("--why-now", "why_now"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit("primitive field requires: " + ", ".join(missing))
    active = getattr(args, "active_primitive", None) or []
    if not 1 <= len(active) <= 2:
        raise SystemExit("primitive field requires one or two --active-primitive values")
    invalid = [value for value in active if not is_allowed_primitive_token(value)]
    if invalid:
        raise SystemExit(
            "primitive field contains invalid primitive values: " + ", ".join(invalid)
        )


def can_clear_release_veto_without_program(state: dict) -> bool:
    output_status = state.get("output_status", {})
    return (
        output_status.get("touched") is True
        and output_status.get("final_artifact_materialized") is True
        and output_status.get("cosmetic_only") is not True
        and output_status.get("contains_unsupported") is not True
        and output_status.get("contains_placeholder") is not True
        and isinstance(state.get("materialization_evidence"), dict)
    )


def require_no_active_control_artifacts_for_release(state: dict) -> None:
    active_fields: list[str] = []
    for key in [
        "gate_binding_if_any",
        "carrier_handoff_if_any",
        "primitive_field_if_any",
        "primitive_competition_if_any",
    ]:
        if state.get(key) is not None:
            active_fields.append(key)

    if active_fields:
        raise SystemExit(
            "cannot clear release_veto while active control artifacts remain: "
            + ", ".join(active_fields)
        )


def require_program_or_materialized_output(state: dict) -> None:
    require_no_active_control_artifacts_for_release(state)
    if state.get("bound_program") is not None:
        return
    if can_clear_release_veto_without_program(state):
        return
    raise SystemExit(
        "cannot clear release_veto without a bound_program unless the asked medium "
        "has already been touched, the final artifact is materialized, and "
        "materialization evidence is present"
    )


def apply_output_updates(state: dict, args: argparse.Namespace) -> None:
    output = state.setdefault("output_status", {})
    for field in [
        "touched",
        "cosmetic_only",
        "contains_unsupported",
        "contains_placeholder",
        "final_artifact_materialized",
    ]:
        value = getattr(args, field, None)
        if value is not None:
            output[field] = value


def command_init(args: argparse.Namespace) -> int:
    state = json.loads(json.dumps(DEFAULT_STATE))
    require_core_arguments(args)
    apply_core_updates(state, args)
    apply_output_updates(state, args)
    if args.allow_release:
        require_materialization_evidence_arguments(args)
        set_materialization_evidence(state, args)
        require_program_or_materialized_output(state)
        state["release_veto"] = False
    else:
        has_program_fields = any(
            getattr(args, attr, None) not in (None, "")
            for attr in ["kind", "target", "operation", "success_signal"]
        )
        if has_program_fields:
            require_bound_program_arguments(args)
            set_bound_program(state, args)
    state_path = Path(args.state_file)
    write_json(state_path, state)
    log_path = event_log_path(state_path)
    if log_path.exists():
        log_path.unlink()
    append_runtime_event(
        state_path,
        command_name="init",
        before=None,
        after=state,
        note="state bootstrap",
    )
    dump(state)
    return 0


def command_show(args: argparse.Namespace) -> int:
    dump(load_state(Path(args.state_file)))
    return 0


def command_set_core(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        apply_core_updates(state, args)
        if args.release_veto is not None:
            if args.release_veto is False:
                require_program_or_materialized_output(state)
            state["release_veto"] = args.release_veto
        if state.get("release_veto") is True:
            refresh_primitive_field_for_current_layer(state)
    state = mutate_state(path, mutator, command_name="set-core")
    dump(state)
    return 0


def command_program(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        if args.mode == "clear":
            if not can_clear_release_veto_without_program(state):
                raise SystemExit(
                    "cannot clear bound_program before the asked medium is touched "
                    "and the final artifact is materialized"
                )
            state["bound_program"] = None
            state["gate_binding_if_any"] = None
            if state.get("release_veto") is True:
                refresh_primitive_field_for_current_layer(state, force=True)
        else:
            set_bound_program(state, args)
            state["gate_binding_if_any"] = None
            if state.get("release_veto") is True:
                agenda = derive_local_agenda_for_program(state, state["bound_program"])
                candidate_gate = derive_gate_binding_candidate(state, [], agenda_override=agenda)
                if isinstance(candidate_gate, dict):
                    state["gate_binding_if_any"] = candidate_gate
            refresh_primitive_field_for_current_layer(state, force=True)
    state = mutate_state(path, mutator, command_name=f"program:{args.mode}")
    dump(state)
    return 0


def command_gate(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if args.mode == "clear":
            state["gate_binding_if_any"] = None
            if state.get("release_veto") is True:
                refresh_primitive_field_for_current_layer(state, force=True)
            return

        if state.get("release_veto") is not True:
            raise SystemExit("gate set requires release_veto to stay active")
        if state.get("carrier_handoff_if_any") is not None:
            raise SystemExit("gate set refused: carrier_handoff_if_any already owns local authority")

        require_gate_binding_arguments(args)
        require_bound_program_arguments(args)
        set_bound_program(state, args)
        set_gate_binding(state, args)
        refresh_primitive_field_for_current_layer(state, force=True)

    state = mutate_state(path, mutator, command_name=f"gate:{args.mode}")
    dump(state)
    return 0


def command_primitive(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if args.mode == "clear":
            state["primitive_field_if_any"] = None
            return
        require_primitive_field_arguments(args)
        set_primitive_field(state, args)

    state = mutate_state(path, mutator, command_name=f"primitive:{args.mode}")
    dump(state)
    return 0


def command_competition(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if args.mode == "clear":
            state["primitive_competition_if_any"] = None
            refresh_primitive_field_for_current_layer(state, force=True)
            return
        set_primitive_competition(state, args)
        refresh_primitive_field_for_current_layer(state, force=True)

    state = mutate_state(path, mutator, command_name=f"competition:{args.mode}")
    dump(state)
    return 0


def command_evidence(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        if args.mode == "clear":
            if can_clear_release_veto_without_program(state):
                raise SystemExit(
                    "cannot clear materialization evidence while it still authorizes "
                    "a released state without a bound_program"
                )
            state["materialization_evidence"] = None
        else:
            set_materialization_evidence(state, args)
    state = mutate_state(path, mutator, command_name=f"evidence:{args.mode}")
    dump(state)
    return 0


def command_set_output(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        apply_output_updates(state, args)
        if state.get("release_veto") is True:
            refresh_primitive_field_for_current_layer(state, force=True)
    state = mutate_state(path, mutator, command_name="set-output")
    dump(state)
    return 0


def command_marker(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        markers = state.setdefault("unresolved_markers", [])
        if args.mode == "add":
            for marker in args.marker:
                if marker not in markers:
                    markers.append(marker)
        elif args.mode == "remove":
            state["unresolved_markers"] = [m for m in markers if m not in set(args.marker)]
        elif args.mode == "clear":
            state["unresolved_markers"] = []
    state = mutate_state(path, mutator, command_name=f"markers:{args.mode}")
    dump(state)
    return 0


def command_rival(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        if args.mode == "clear":
            state["secondary_rival_if_any"] = None
        else:
            state["secondary_rival_if_any"] = {
                "object": args.object,
                "debt": args.debt,
                "bite": args.bite,
                "separating_advantage": args.separating_advantage,
            }
        if state.get("release_veto") is True:
            refresh_primitive_field_for_current_layer(state, force=True)
    state = mutate_state(path, mutator, command_name=f"rival:{args.mode}")
    dump(state)
    return 0


def command_handoff(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if args.mode == "clear":
            state["carrier_handoff_if_any"] = None
            refresh_primitive_field_for_current_layer(state, force=True)
            return

        if state.get("release_veto") is not True:
            raise SystemExit("handoff set requires release_veto to stay active")

        handoff = {
            "trigger": args.trigger,
            "from_slot": args.from_slot,
            "to_object": args.to_object,
            "winning_pressure": args.winning_pressure,
            "why_local": args.why_local,
        }
        if args.cooled_pressure is not None:
            handoff["cooled_pressure_if_any"] = args.cooled_pressure
        if args.active_pressure or args.cheap_check:
            active_pressures = args.active_pressure or ["check"]
            handoff["warm_field"] = {
                "active_pressures": active_pressures,
            }
            if args.cheap_check is not None:
                handoff["warm_field"]["cheap_check"] = args.cheap_check
            if args.primitive_hint:
                handoff["warm_field"]["primitive_hints"] = [
                    canonicalize_primitive_token(value) for value in args.primitive_hint
                    if canonicalize_primitive_token(value)
                ]
            handoff["warm_field"]["evidence_basis"] = (
                "cheap_check" if args.cheap_check is not None else "state_witness"
            )
        elif args.primitive_hint:
            handoff["warm_field"] = {
                "active_pressures": ["check"],
                "primitive_hints": [
                    canonicalize_primitive_token(value) for value in args.primitive_hint
                    if canonicalize_primitive_token(value)
                ],
                "evidence_basis": "explicit_hint",
            }

        # A thinner carrier taking authority should clear any stale same-slot program.
        state["bound_program"] = None
        state["gate_binding_if_any"] = None
        state["carrier_handoff_if_any"] = handoff
        refresh_primitive_field_for_current_layer(
            state,
            handoff_override=handoff,
            force=True,
        )

    state = mutate_state(path, mutator, command_name=f"handoff:{args.mode}")
    dump(state)
    return 0


def command_residue(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        residue = state.setdefault("memory_residue", [])
        if args.mode == "clear":
            state["memory_residue"] = []
        else:
            if args.kind not in ALLOWED_RESIDUE_KINDS:
                raise SystemExit(f"invalid residue kind: {args.kind}")
            residue.append(
                {
                    "kind": args.kind,
                    "description": args.description,
                    "replayable": args.replayable,
                }
            )
    state = mutate_state(path, mutator, command_name=f"residue:{args.mode}")
    dump(state)
    return 0


def command_check(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    state = load_state(path)
    report = build_report(state, path)
    dump(report)
    if report["problems"]:
        return 2
    return 0 if report["release_allowed"] else 1


def command_bind_local(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    previous_state = load_json(Path(args.previous_state)) if args.previous_state else None

    def mutator(state: dict) -> None:
        if state.get("bound_program") is not None:
            raise SystemExit("bind-local refused: bound_program already exists")
        if state.get("carrier_handoff_if_any") is not None:
            raise SystemExit("bind-local refused: carrier_handoff_if_any already exists")

        report = build_report(state, path)
        relaxed_problems = [
            problem
            for problem in report["problems"]
            if not (
                state.get("release_veto") is True
                and problem == "bound_program is required while release_veto is active"
            )
        ]
        if relaxed_problems:
            raise SystemExit(
                "bind-local refused: state has blocking problems: "
                + "; ".join(relaxed_problems)
            )

        if state.get("secondary_rival_if_any") is not None and args.allow_rival is not True:
            agenda = report.get("self_check_agenda") or {}
            if agenda.get("focus") != "rival":
                raise SystemExit(
                    "bind-local refused: unresolved rival is still live without a unique rival-local bite"
                )

        skill_winner, skill_program, silence_after_contact = read_skill_authority_program(
            report,
            require_same_carrier=True,
        )
        candidate_program = derive_bound_program_candidate(
            state, [], previous_state=previous_state
        )
        if programs_conflict(candidate_program, skill_program):
            if skill_winner and isinstance(skill_program, dict):
                candidate_program = skill_program
            else:
                raise SystemExit(
                    "bind-local refused: skill authority touch and local primitive bind diverged"
                )
        if candidate_program is None and skill_program is not None:
            candidate_program = skill_program
        candidate_handoff = derive_handoff_candidate(state, [])

        if candidate_program is not None and candidate_handoff is not None:
            explicit_skill_owner = bool(skill_winner and isinstance(skill_program, dict))
            if not explicit_skill_owner:
                raise SystemExit(
                    "bind-local refused: same-carrier bind and thinner-carrier handoff are both concrete; "
                    "use rebind-local explicitly if thinner-carrier authority should take over"
                )

        if candidate_program is not None:
            promoted_refusal = promoted_skill_gate_refusal(
                report,
                winning_skill=skill_winner,
            )
            if promoted_refusal:
                raise SystemExit(f"bind-local refused: {promoted_refusal}")
            recoil_refusal = first_recoil_refusal(
                candidate_program,
                report,
                state=state,
                winning_skill=skill_winner,
            )
            if recoil_refusal:
                raise SystemExit(f"bind-local refused: {recoil_refusal}")
            probe_refusal = unbound_probe_refusal(candidate_program, report)
            if probe_refusal:
                raise SystemExit(f"bind-local refused: {probe_refusal}")
            overreach_refusal = probe_overreach_refusal(
                candidate_program,
                report,
                winning_skill=skill_winner,
            )
            if overreach_refusal:
                raise SystemExit(f"bind-local refused: {overreach_refusal}")
            state["bound_program"] = candidate_program
            agenda = derive_local_agenda_for_program(
                state,
                candidate_program,
                winning_skill=skill_winner,
                report=report,
            )
            candidate_gate = derive_gate_binding_candidate(
                state,
                [],
                agenda_override=agenda,
                winning_skill_override=skill_winner,
            )
            if isinstance(candidate_gate, dict):
                state["gate_binding_if_any"] = candidate_gate
            maybe_cool_post_touch_surfaces(
                state,
                candidate_program,
                winning_skill=skill_winner,
                silence_after_contact=silence_after_contact,
            )
            refresh_primitive_field_for_current_layer(
                state,
                agenda_override=agenda,
                force=True,
            )
            return

        if candidate_handoff is not None and args.allow_handoff:
            state["carrier_handoff_if_any"] = candidate_handoff
            refresh_primitive_field_for_current_layer(
                state,
                handoff_override=candidate_handoff,
                force=True,
            )
            return

        if candidate_handoff is not None and args.allow_handoff is not True:
            raise SystemExit(
                "bind-local refused: thinner-carrier reselection is concrete; use rebind-local or pass --allow-handoff"
            )

        raise SystemExit("bind-local refused: no unique local bite became concrete enough to bind")

    state = mutate_state(path, mutator, command_name="bind-local")
    dump(state)
    return 0


def command_rebind_local(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if state.get("carrier_handoff_if_any") is not None:
            raise SystemExit("rebind-local refused: carrier_handoff_if_any already exists")

        report = build_report(state, path)
        blocking = [
            problem
            for problem in report["problems"]
            if problem != "bound_program is required while release_veto is active"
        ]
        if blocking:
            raise SystemExit(
                "rebind-local refused: state has blocking problems: " + "; ".join(blocking)
            )

        if state.get("bound_program") is not None and args.force is not True:
            raise SystemExit(
                "rebind-local refused: bound_program still exists; clear or override it explicitly"
            )

        probe_state = json.loads(json.dumps(state))
        if args.force is True:
            probe_state["bound_program"] = None
            probe_state["gate_binding_if_any"] = None

        candidate_handoff = derive_handoff_candidate(probe_state, [])
        if candidate_handoff is None:
            raise SystemExit("rebind-local refused: no unique thinner-carrier handoff is concrete enough")

        state["bound_program"] = None
        state["gate_binding_if_any"] = None
        state["carrier_handoff_if_any"] = candidate_handoff
        refresh_primitive_field_for_current_layer(
            state,
            handoff_override=candidate_handoff,
            force=True,
        )

    state = mutate_state(path, mutator, command_name="rebind-local")
    dump(state)
    return 0


def command_spend_local(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if state.get("bound_program") is not None:
            raise SystemExit("spend-local refused: bound_program already exists")

        handoff = state.get("carrier_handoff_if_any")
        if not isinstance(handoff, dict):
            raise SystemExit("spend-local refused: no explicit carrier_handoff_if_any is live")

        report = build_report(state, path)
        blocking = [
            problem
            for problem in report["problems"]
            if problem != "bound_program is required while release_veto is active"
        ]
        if blocking:
            raise SystemExit(
                "spend-local refused: state has blocking problems: " + "; ".join(blocking)
            )

        skill_winner, skill_program, silence_after_contact = read_skill_authority_program(
            report,
            require_same_carrier=False,
        )
        interlayer_bridge = read_interlayer_discharge_bridge(report)
        primitive_program = derive_primitive_program_candidate(state, [])
        if programs_conflict(primitive_program, skill_program):
            if (
                isinstance(interlayer_bridge, dict)
                and programs_conflict(
                    interlayer_bridge.get("spend_first_program"),
                    skill_program,
                )
                and not programs_conflict(
                    interlayer_bridge.get("spend_first_program"),
                    primitive_program,
                )
            ):
                candidate_program = interlayer_bridge["spend_first_program"]
                if interlayer_bridge.get("keep_closure_authority") is True:
                    skill_winner = "exact_closure"
                else:
                    skill_winner = ""
                silence_after_contact = False
            else:
                raise SystemExit(
                    "spend-local refused: skill authority touch and thinner-carrier primitive spend diverged"
                )
        else:
            candidate_program = skill_program or primitive_program

        if candidate_program is None and isinstance(interlayer_bridge, dict):
            candidate_program = interlayer_bridge.get("spend_first_program")
            if interlayer_bridge.get("keep_closure_authority") is True:
                skill_winner = "exact_closure"
            else:
                skill_winner = ""
            silence_after_contact = False

        if candidate_program is None:
            raise SystemExit(
                "spend-local refused: no unique next primitive touch is concrete enough"
            )
        promoted_refusal = promoted_skill_gate_refusal(
            report,
            winning_skill=skill_winner,
        )
        if promoted_refusal:
            raise SystemExit(f"spend-local refused: {promoted_refusal}")
        recoil_refusal = first_recoil_refusal(
            candidate_program,
            report,
            state=state,
            winning_skill=skill_winner,
        )
        if recoil_refusal:
            raise SystemExit(f"spend-local refused: {recoil_refusal}")
        probe_refusal = unbound_probe_refusal(candidate_program, report)
        if probe_refusal:
            raise SystemExit(f"spend-local refused: {probe_refusal}")
        overreach_refusal = probe_overreach_refusal(
            candidate_program,
            report,
            winning_skill=skill_winner,
        )
        if overreach_refusal:
            raise SystemExit(f"spend-local refused: {overreach_refusal}")

        target_object = handoff.get("to_object")
        if isinstance(target_object, str) and target_object.strip():
            previous_object = state.get("current_object")
            state["current_object"] = target_object
            if not state.get("current_seam") or state.get("current_seam") == previous_object:
                state["current_seam"] = target_object

        state["bound_program"] = candidate_program
        state["carrier_handoff_if_any"] = None

        agenda = derive_local_agenda_for_program(
            state,
            candidate_program,
            winning_skill=skill_winner,
            report=report,
        )
        candidate_gate = derive_gate_binding_candidate(
            state,
            [],
            agenda_override=agenda,
            winning_skill_override=skill_winner,
        )
        state["gate_binding_if_any"] = candidate_gate if isinstance(candidate_gate, dict) else None
        maybe_cool_post_touch_surfaces(
            state,
            candidate_program,
            winning_skill=skill_winner,
            silence_after_contact=silence_after_contact,
        )
        refresh_primitive_field_for_current_layer(
            state,
            agenda_override=agenda,
            force=False,
        )

    state = mutate_state(path, mutator, command_name="spend-local")
    dump(state)
    return 0


def command_trace(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    evidence = build_runtime_evidence(path)
    if args.format == "json":
        payload = {
            "state_file": str(path),
            "runtime_evidence": evidence,
            "events": load_runtime_events(path),
        }
        text = json.dumps(payload, ensure_ascii=True, indent=2) + "\n"
    elif args.format == "skill-markdown":
        text = render_runtime_skill_trace_markdown(path)
        if not text.endswith("\n"):
            text += "\n"
    else:
        text = render_runtime_trace_markdown(path)
        if not text.endswith("\n"):
            text += "\n"

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if evidence["event_count"] > 0 else 1


def add_common_core_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--current-object")
    parser.add_argument("--current-seam")
    parser.add_argument("--current-debt")
    parser.add_argument("--next-bite")
    parser.add_argument("--asked-medium-surface")
    parser.add_argument("--revocation-handle")
    parser.add_argument("--uncertainty-mode", choices=["high", "low", "mixed", "unknown"])
    parser.add_argument("--primary-slot")


def add_common_output_arguments(parser: argparse.ArgumentParser) -> None:
    add_bool_argument(parser, "--touched", "touched")
    add_bool_argument(parser, "--cosmetic-only", "cosmetic_only")
    add_bool_argument(parser, "--contains-unsupported", "contains_unsupported")
    add_bool_argument(parser, "--contains-placeholder", "contains_placeholder")
    add_bool_argument(
        parser,
        "--final-artifact-materialized",
        "final_artifact_materialized",
    )


def add_materialization_evidence_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--evidence-kind",
        choices=["file", "command", "check", "artifact"],
    )
    parser.add_argument("--evidence-location")
    parser.add_argument("--evidence-summary")


def add_bool_argument(parser: argparse.ArgumentParser, name: str, dest: str) -> None:
    parser.add_argument(name, dest=dest, action="store_true")
    parser.add_argument(f"--no-{name[2:]}", dest=dest, action="store_false")
    parser.set_defaults(**{dest: None})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Thin mutable control-state tool for Wu Boshi Perspective. "
            "It only edits one tiny runtime state; it does not generate routes."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a new runtime state file")
    init_parser.add_argument("state_file")
    add_common_core_arguments(init_parser)
    add_common_output_arguments(init_parser)
    add_materialization_evidence_arguments(init_parser)
    init_parser.add_argument("--kind", choices=["write", "check", "readout", "witness"])
    init_parser.add_argument("--target")
    init_parser.add_argument("--operation")
    init_parser.add_argument("--success-signal")
    init_parser.add_argument("--allow-release", action="store_true")
    init_parser.set_defaults(func=command_init)

    show_parser = subparsers.add_parser("show", help="Print a runtime state file")
    show_parser.add_argument("state_file")
    show_parser.set_defaults(func=command_show)

    core_parser = subparsers.add_parser("set-core", help="Update core live-state fields")
    core_parser.add_argument("state_file")
    add_common_core_arguments(core_parser)
    add_bool_argument(core_parser, "--release-veto", "release_veto")
    core_parser.set_defaults(func=command_set_core)

    program_parser = subparsers.add_parser(
        "program",
        help="Set or clear one tiny bound executable program on the current carrier",
    )
    program_parser.add_argument("mode", choices=["set", "clear"])
    program_parser.add_argument("state_file")
    program_parser.add_argument("--kind", choices=["write", "check", "readout", "witness"])
    program_parser.add_argument("--target")
    program_parser.add_argument("--operation")
    program_parser.add_argument("--success-signal")
    program_parser.set_defaults(func=command_program)

    gate_parser = subparsers.add_parser(
        "gate",
        help="Internal/debug: set or clear one tiny monitor-paid gate binding on the current carrier",
    )
    gate_parser.add_argument("mode", choices=["set", "clear"])
    gate_parser.add_argument("state_file")
    gate_parser.add_argument(
        "--source-focus",
        choices=["seam", "rival", "carrier", "asked_medium"],
    )
    gate_parser.add_argument("--source-target")
    gate_parser.add_argument("--demoted-continuation")
    gate_parser.add_argument(
        "--authority-until",
        choices=[
            "same_carrier_change",
            "hostile_witness",
            "exact_check",
            "asked_medium_failure",
        ],
    )
    gate_parser.add_argument("--kind", choices=["write", "check", "readout", "witness"])
    gate_parser.add_argument("--target")
    gate_parser.add_argument("--operation")
    gate_parser.add_argument("--success-signal")
    gate_parser.set_defaults(func=command_gate)

    primitive_parser = subparsers.add_parser(
        "primitive",
        help="Internal/debug: set or clear one tiny current-layer primitive field on the live carrier",
    )
    primitive_parser.add_argument("mode", choices=["set", "clear"])
    primitive_parser.add_argument("state_file")
    primitive_parser.add_argument("--layer-object")
    primitive_parser.add_argument("--active-primitive", action="append")
    primitive_parser.add_argument("--tie-break-check")
    primitive_parser.add_argument("--why-now")
    primitive_parser.add_argument(
        "--selection-basis",
        choices=["explicit_hint", "tie_break", "agenda_hint", "text_fallback"],
    )
    primitive_parser.add_argument(
        "--evidence-basis",
        choices=["explicit_hint", "state_witness", "cheap_check", "lexical_hint", "mixed"],
    )
    primitive_parser.set_defaults(func=command_primitive)

    competition_parser = subparsers.add_parser(
        "competition",
        help="Internal/debug: set or clear one tiny explicit primitive competition object on the current layer",
    )
    competition_parser.add_argument("mode", choices=["set", "clear"])
    competition_parser.add_argument("state_file")
    competition_parser.add_argument("--layer-object")
    competition_parser.add_argument(
        "--candidate",
        action="append",
        help="Format: primitive|touch_target|expected_local_gain",
    )
    competition_parser.add_argument("--separating-check")
    competition_parser.add_argument("--winner-if-any")
    competition_parser.set_defaults(func=command_competition)

    evidence_parser = subparsers.add_parser(
        "evidence",
        help="Set or clear thin materialization evidence for a released state",
    )
    evidence_parser.add_argument("mode", choices=["set", "clear"])
    evidence_parser.add_argument("state_file")
    add_materialization_evidence_arguments(evidence_parser)
    evidence_parser.set_defaults(func=command_evidence)

    output_parser = subparsers.add_parser("set-output", help="Update asked-medium/output flags")
    output_parser.add_argument("state_file")
    add_common_output_arguments(output_parser)
    output_parser.set_defaults(func=command_set_output)

    marker_parser = subparsers.add_parser("markers", help="Manage unresolved markers")
    marker_parser.add_argument("mode", choices=["add", "remove", "clear"])
    marker_parser.add_argument("state_file")
    marker_parser.add_argument("marker", nargs="*")
    marker_parser.set_defaults(func=command_marker)

    rival_parser = subparsers.add_parser("rival", help="Set or clear the warm constructive rival")
    rival_parser.add_argument("mode", choices=["set", "clear"])
    rival_parser.add_argument("state_file")
    rival_parser.add_argument("--object")
    rival_parser.add_argument("--debt")
    rival_parser.add_argument("--bite")
    rival_parser.add_argument("--separating-advantage")
    rival_parser.set_defaults(func=command_rival)

    handoff_parser = subparsers.add_parser(
        "handoff",
        help="Internal/debug: set or clear one tiny carrier-change / primitive-reselection handoff",
    )
    handoff_parser.add_argument("mode", choices=["set", "clear"])
    handoff_parser.add_argument("state_file")
    handoff_parser.add_argument(
        "--trigger",
        choices=[
            "same_carrier_change",
            "hostile_witness",
            "exact_check",
            "asked_medium_failure",
            "residue_inherited",
        ],
    )
    handoff_parser.add_argument("--from-slot")
    handoff_parser.add_argument("--to-object")
    handoff_parser.add_argument("--winning-pressure")
    handoff_parser.add_argument("--cooled-pressure")
    handoff_parser.add_argument("--why-local")
    handoff_parser.add_argument("--active-pressure", action="append")
    handoff_parser.add_argument("--primitive-hint", action="append")
    handoff_parser.add_argument("--cheap-check")
    handoff_parser.set_defaults(func=command_handoff)

    residue_parser = subparsers.add_parser("residue", help="Manage thin memory residue")
    residue_parser.add_argument("mode", choices=["add", "clear"])
    residue_parser.add_argument("state_file")
    residue_parser.add_argument("--kind")
    residue_parser.add_argument("--description")
    add_bool_argument(residue_parser, "--replayable", "replayable")
    residue_parser.set_defaults(func=command_residue)

    check_parser = subparsers.add_parser("check", help="Run the runtime guard against a state file")
    check_parser.add_argument("state_file")
    check_parser.set_defaults(func=command_check)

    bind_parser = subparsers.add_parser(
        "bind-local",
        help=(
            "Project one already-local monitoring state into exactly one tiny local action "
            "without turning it into a workflow"
        ),
    )
    bind_parser.add_argument("state_file")
    bind_parser.add_argument(
        "--previous-state",
        help="Optional immediately previous snapshot used only to detect same-carrier stall",
    )
    bind_parser.add_argument(
        "--allow-handoff",
        action="store_true",
        help="Allow one tiny carrier_handoff_if_any only when no bound_program can be bound",
    )
    bind_parser.add_argument(
        "--allow-rival",
        action="store_true",
        help="Allow binding a rival-local witness program when the self-check focus is already rival",
    )
    bind_parser.set_defaults(func=command_bind_local)

    rebind_parser = subparsers.add_parser(
        "rebind-local",
        help=(
            "Project one already-local thinner-carrier primitive reselection into exactly one "
            "tiny carrier_handoff_if_any"
        ),
    )
    rebind_parser.add_argument("state_file")
    rebind_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacing a still-present bound_program when thinner-carrier authority must take over",
    )
    rebind_parser.set_defaults(func=command_rebind_local)

    spend_parser = subparsers.add_parser(
        "spend-local",
        help=(
            "Explicit one-shot: collapse one live thinner-carrier handoff into exactly one "
            "next primitive bound_program on that new layer"
        ),
    )
    spend_parser.add_argument("state_file")
    spend_parser.set_defaults(func=command_spend_local)

    trace_parser = subparsers.add_parser(
        "trace",
        help=(
            "Export the sidecar runtime event trace. "
            "This is evidence of actual runtime consumption, not a free-form solve story."
        ),
    )
    trace_parser.add_argument("state_file")
    trace_parser.add_argument(
        "--format",
        choices=["markdown", "skill-markdown", "json"],
        default="markdown",
    )
    trace_parser.add_argument("--output")
    trace_parser.set_defaults(func=command_trace)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "rival" and args.mode == "set":
        missing = [
            name
            for name in ["object", "debt", "bite", "separating_advantage"]
            if getattr(args, name) in (None, "")
        ]
        if missing:
            raise SystemExit(f"missing rival fields: {', '.join(missing)}")

    if args.command == "residue" and args.mode == "add":
        if args.kind is None or args.description is None or args.replayable is None:
            raise SystemExit("residue add requires --kind, --description, and replayable flag")

    if args.command == "markers" and args.mode in {"add", "remove"} and not args.marker:
        raise SystemExit("markers add/remove requires at least one marker")

    if args.command == "program" and args.mode == "set":
        require_bound_program_arguments(args)

    if args.command == "gate" and args.mode == "set":
        require_gate_binding_arguments(args)
        require_bound_program_arguments(args)

    if args.command == "evidence" and args.mode == "set":
        require_materialization_evidence_arguments(args)

    if args.command == "handoff" and args.mode == "set":
        missing = [
            flag
            for flag, attr in [
                ("--trigger", "trigger"),
                ("--from-slot", "from_slot"),
                ("--to-object", "to_object"),
                ("--winning-pressure", "winning_pressure"),
                ("--why-local", "why_local"),
            ]
            if getattr(args, attr) in (None, "")
        ]
        if missing:
            raise SystemExit("handoff set requires: " + ", ".join(missing))
        if args.active_pressure is not None and not 1 <= len(args.active_pressure) <= 2:
            raise SystemExit("handoff set allows one or two --active-pressure values")
        if args.primitive_hint is not None and not 1 <= len(args.primitive_hint) <= 2:
            raise SystemExit("handoff set allows one or two --primitive-hint values")
        invalid_hints = [
            value for value in (args.primitive_hint or []) if not is_allowed_primitive_token(value)
        ]
        if invalid_hints:
            raise SystemExit(
                "handoff set contains invalid --primitive-hint values: "
                + ", ".join(invalid_hints)
            )

    if args.command == "competition" and args.mode == "set":
        if getattr(args, "layer_object", None) in (None, ""):
            raise SystemExit("competition set requires --layer-object")
        raw_candidates = getattr(args, "candidate", None) or []
        if not 1 <= len(raw_candidates) <= 2:
            raise SystemExit("competition set requires one or two --candidate values")
        seen_primitives: set[str] = set()
        for raw_candidate in raw_candidates:
            parts = raw_candidate.split("|", 2)
            if len(parts) != 3 or not all(part.strip() for part in parts):
                raise SystemExit(
                    "competition set candidates must use format primitive|touch_target|expected_local_gain"
                )
            primitive = canonicalize_primitive_token(parts[0].strip())
            if primitive not in ALLOWED_PRIMITIVES:
                raise SystemExit(f"competition set candidate primitive is invalid: {primitive}")
            if primitive in seen_primitives:
                raise SystemExit(f"competition set candidate primitive repeats: {primitive}")
            seen_primitives.add(primitive)
        raw_winner = getattr(args, "winner_if_any", None)
        winner = canonicalize_primitive_token(raw_winner)
        if raw_winner is not None and not winner:
            raise SystemExit("competition set --winner-if-any is invalid")
        if winner and winner not in seen_primitives:
            raise SystemExit("competition set --winner-if-any must match one candidate primitive")

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
