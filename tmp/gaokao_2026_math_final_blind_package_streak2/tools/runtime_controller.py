#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_guard import build_report, load_json
from runtime_state import build_runtime_evidence
from runtime_state import (
    active_contract_requires_runtime_evidence,
    annotate_runtime_surface_payload,
    build_runtime_evidence_refusal_payload,
    fresh_blind_runtime_transition_watchdog,
    pending_runtime_execution_contract,
)


def _normalize_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def _program_signature(payload: object) -> tuple[str, str, str]:
    if not isinstance(payload, dict):
        return ("", "", "")
    return (
        _normalize_text(payload.get("kind")),
        _normalize_text(payload.get("target")),
        _normalize_text(payload.get("operation")),
    )


def _same_program(left: object, right: object) -> bool:
    left_sig = _program_signature(left)
    right_sig = _program_signature(right)
    return bool(all(left_sig)) and left_sig == right_sig


def _authority_touch(payload: dict) -> dict | None:
    bridge = payload.get("skill_authority_bridge")
    if isinstance(bridge, dict) and isinstance(bridge.get("executable_local_touch_if_any"), dict):
        executable = bridge.get("executable_local_touch_if_any")
        if _program_signature(executable) != ("", "", ""):
            return executable
    contract = payload.get("discipline_contract")
    if isinstance(contract, dict) and isinstance(contract.get("authorized_bite"), dict):
        authorized = contract.get("authorized_bite")
        if _program_signature(authorized) != ("", "", ""):
            return authorized
    interlayer = payload.get("interlayer_discharge_bridge")
    if isinstance(interlayer, dict) and isinstance(interlayer.get("spend_first_program"), dict):
        return interlayer.get("spend_first_program")
    return None


def _winning_skill(payload: dict) -> str:
    bridge = payload.get("skill_authority_bridge")
    if isinstance(bridge, dict):
        return _normalize_text(bridge.get("winning_skill_if_any"))
    return ""


def _normalized_skill_list(values: object, *, limit: int = 6) -> list[str]:
    if not isinstance(values, list):
        return []
    ordered: list[str] = []
    for value in values:
        text = _normalize_text(value)
        if text and text not in ordered:
            ordered.append(text)
        if len(ordered) == limit:
            break
    return ordered


def _retain_shadow_program(payload: dict, key: str, *, shadow_key: str, authority_touch: dict | None) -> None:
    candidate = payload.get(key)
    if not isinstance(candidate, dict):
        return
    if authority_touch is not None and _same_program(candidate, authority_touch):
        payload[f"{key}_authority_match"] = True
        return
    payload[f"{key}_authority_match"] = False
    payload[shadow_key] = candidate


def cool_shortcut_fields(payload: dict) -> None:
    authority_touch = _authority_touch(payload)
    winning_skill = _winning_skill(payload)
    if winning_skill != "精确封口":
        _retain_shadow_program(
            payload,
            "current_读出_bite_if_any",
            shadow_key="suppressed_读出_bite_if_any",
            authority_touch=authority_touch,
        )


def reorder_payload_authority_first(payload: dict) -> dict:
    ordered: dict = {}
    preferred = [
        "state_file",
        "consumed",
        "inspect_only",
        "discipline_contract",
        "runtime_evidence",
        "layer_composition",
        "ordinary_regrowth_forbidden",
        "reader_quieted",
        "authorized_bite_if_any",
        "resume_bridge",
        "skill_authority_bridge",
        "skill_lighting_surface",
        "probe_discipline",
        "interlayer_discharge_bridge",
        "skill_field",
        "skill_competition",
        "skill_inhibition",
        "control_signals",
        "closure_nucleus",
        "current_structural_bite_if_any",
        "current_读出_bite_if_any",
        "separating_check_if_any",
        "primitive_field",
        "inhibition_state",
        "warnings",
    ]
    for key in preferred:
        if key in payload:
            ordered[key] = payload[key]
    for key, value in payload.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def should_quiet_for_probe_drift(payload: dict) -> bool:
    discipline = payload.get("probe_discipline")
    active_hypotheses = (
        discipline.get("active_skill_hypotheses")
        if isinstance(discipline, dict)
        else None
    )
    has_plural_binding = isinstance(active_hypotheses, list) and any(
        _normalize_text(value) for value in active_hypotheses
    )
    return isinstance(discipline, dict) and (
        discipline.get("probe_must_bind") is True
        and discipline.get("unbound_probe_is_drift") is True
        and not _normalize_text(discipline.get("active_skill_hypothesis"))
        and not has_plural_binding
    )


def quiet_control_signals(control_signals: dict) -> dict:
    return {
        "current_controller_view": control_signals.get("current_controller_view", {}),
        "composition_pressure": control_signals.get("composition_pressure", {}),
        "probe_discipline": control_signals.get("probe_discipline", {}),
    }


def _composition_combo(payload: dict) -> list[str]:
    skill_authority_bridge = payload.get("skill_authority_bridge")
    if isinstance(skill_authority_bridge, dict):
        combo = skill_authority_bridge.get("active_skill_combo_if_any")
        normalized = _normalized_skill_list(combo)
        if normalized:
            return normalized
    discipline_contract = payload.get("discipline_contract")
    if isinstance(discipline_contract, dict):
        combo = discipline_contract.get("active_skill_combo_if_any")
        normalized = _normalized_skill_list(combo)
        if normalized:
            return normalized
    return []


def _project_program(program: object) -> dict | None:
    if not isinstance(program, dict):
        return None
    projected = dict(program)
    owner_skill = _normalize_text(projected.get("owner_skill_if_any"))
    if owner_skill:
        projected["owner_skill_if_any"] = owner_skill
    else:
        projected.pop("owner_skill_if_any", None)
    combo = _normalized_skill_list(projected.get("owner_skill_combo_if_any"))
    if combo:
        projected["owner_skill_combo_if_any"] = combo[:6]
    else:
        projected.pop("owner_skill_combo_if_any", None)
    return projected


def _host_visible_skill_lighting_surface(report: dict) -> dict:
    surface: dict = {}
    layer = report.get("layer_composition", {})
    for source in [
        layer.get("lighting_if_any") if isinstance(layer, dict) else None,
        report.get("skill_lighting_surface"),
    ]:
        if not isinstance(source, dict):
            continue
        for key in [
            "lit_skill_if_any",
            "candidate_skills_if_any",
            "supporting_skills_if_any",
            "false_first_skill_if_any",
            "false_first_label_if_any",
            "false_skill_reason",
            "verify_touch_if_any",
            "accountability_nudge_if_any",
            "winning_projected_gain_reason",
            "competition_basis",
            "role_split_if_any",
            "ability_branch_if_any",
            "ordinary_operations_are_not_skills",
            "anti_pipeline_note",
        ]:
            value = source.get(key)
            if value not in (None, "", [], {}):
                surface[key] = value
    return surface


def build_next_layer_reselection_surface(payload: dict) -> dict:
    surface: dict = {}
    primitive_field = payload.get("primitive_field")
    if isinstance(primitive_field, dict):
        for key in ["layer_object", "active_primitives", "why_now", "selection_basis"]:
            value = primitive_field.get(key)
            if value not in (None, {}, [], ""):
                surface[key] = value
    skill_field = payload.get("skill_field")
    if isinstance(skill_field, dict):
        for key in ["active_skills", "composition_axes", "composition_ready", "authority_skill_if_any"]:
            value = skill_field.get(key)
            if value not in (None, {}, [], ""):
                surface[key] = value
    resume_bridge = payload.get("resume_bridge")
    if isinstance(resume_bridge, dict):
        for key in ["explicit_gap", "next_local_choice", "mode"]:
            value = resume_bridge.get(key)
            if value not in (None, {}, [], ""):
                surface[key] = value
    closure_nucleus = payload.get("closure_nucleus")
    if isinstance(closure_nucleus, dict):
        for key in ["closure_target", "required_contact", "读出_deferred_by_layerwise_pressure"]:
            value = closure_nucleus.get(key)
            if value not in (None, {}, [], ""):
                surface[key] = value
    return surface


def quiet_payload_for_active_contract(payload: dict) -> None:
    payload["ordinary_regrowth_forbidden"] = True
    payload["reader_quieted"] = True
    payload["authorized_bite_if_any"] = _project_program(
        payload.get("discipline_contract", {}).get("authorized_bite", {})
    ) or {}
    resume_bridge = payload.get("resume_bridge")
    if isinstance(resume_bridge, dict):
        payload["resume_bridge"] = {
            key: resume_bridge.get(key)
            for key in ["mode", "known_object", "explicit_gap", "next_local_choice"]
            if resume_bridge.get(key) not in (None, {}, [], "")
        }
    skill_authority_bridge = payload.get("skill_authority_bridge")
    if isinstance(skill_authority_bridge, dict):
        projected_touch = _project_program(
            skill_authority_bridge.get("executable_local_touch_if_any")
        )
        payload["skill_authority_bridge"] = {
            key: (
                projected_touch
                if key == "executable_local_touch_if_any"
                else skill_authority_bridge.get(key)
            )
            for key in [
                "winning_skill_if_any",
                "executable_owner_skill_if_any",
                "executable_local_touch_if_any",
                "active_skill_combo_if_any",
                "supporting_skills_if_any",
            ]
            if (
                projected_touch if key == "executable_local_touch_if_any" else skill_authority_bridge.get(key)
            ) not in (None, {}, [], "")
        }
    probe_discipline = payload.get("probe_discipline")
    if isinstance(probe_discipline, dict):
        payload["probe_discipline"] = {
            key: probe_discipline.get(key)
            for key in [
                "active_skill_hypothesis",
                "active_skill_hypotheses",
                "preferred_probe_target",
                "allowed_probe_kinds",
            ]
            if probe_discipline.get(key) not in (None, {}, [], "")
        }
    control_signals = payload.get("control_signals")
    if isinstance(control_signals, dict):
        payload["control_signals"] = quiet_control_signals(control_signals)
    next_layer_surface = build_next_layer_reselection_surface(payload)
    if next_layer_surface:
        payload["next_layer_reselection_surface"] = next_layer_surface
    for key in [
        "closure_nucleus",
        "current_structural_bite_if_any",
        "current_读出_bite_if_any",
        "separating_check_if_any",
        "primitive_field",
        "primitive_semantics",
        "skill_field",
        "skill_semantics",
        "skill_competition",
        "skill_competition_semantics",
        "skill_inhibition",
        "inhibition_state",
        "reselection_bridge",
        "interlayer_discharge_bridge",
    ]:
        payload.pop(key, None)
    cool_shortcut_fields(payload)


def build_controller_读出(state_path: Path) -> tuple[dict, int]:
    state = load_json(state_path)
    report = build_report(state, state_path)
    runtime_evidence = build_runtime_evidence(state_path)
    runtime_transition_watchdog = fresh_blind_runtime_transition_watchdog(
        state,
        runtime_evidence=runtime_evidence,
    )
    discipline_contract = report.get("discipline_contract", {})
    if not isinstance(discipline_contract, dict):
        discipline_contract = {}

    if report["problems"]:
        return annotate_runtime_surface_payload({
            "state_file": str(state_path),
            "consumed": False,
            "reason": "invalid_state",
            "problems": report["problems"],
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
            "runtime_evidence": runtime_evidence,
            **(
                {"runtime_transition_watchdog": runtime_transition_watchdog}
                if isinstance(runtime_transition_watchdog, dict)
                else {}
            ),
        }, exit_code=2), 2

    control_signals = report.get("control_signals")
    if not isinstance(control_signals, dict):
        pending_contract = pending_runtime_execution_contract(
            state,
            layer_composition=report.get("layer_composition"),
        )
        if isinstance(pending_contract, dict):
            payload = {
                "state_file": str(state_path),
                "consumed": False,
                "inspect_only": True,
                "discipline_contract": discipline_contract,
                "runtime_evidence": runtime_evidence,
                "warnings": report["warnings"],
                "layer_composition": report.get("layer_composition", {}),
                "pending_transition": True,
                "reason": (
                    "bootstrap_runtime_window_expired"
                    if isinstance(runtime_transition_watchdog, dict)
                    and runtime_transition_watchdog.get("expired") is True
                    else "active_discipline_contract_requires_runtime_consumption"
                ),
                "required_action": pending_contract.get("required_action", ""),
                "allowed_transition_surfaces": pending_contract.get(
                    "allowed_transition_surfaces",
                    [],
                ),
            }
            if isinstance(runtime_transition_watchdog, dict):
                payload["runtime_transition_watchdog"] = runtime_transition_watchdog
            if isinstance(pending_contract.get("authorized_bite"), dict) and pending_contract.get(
                "authorized_bite"
            ):
                payload["authorized_bite_if_any"] = pending_contract.get("authorized_bite")
            return annotate_runtime_surface_payload(build_runtime_evidence_refusal_payload(
                state_path,
                discipline_contract=payload.get("discipline_contract"),
                resume_bridge={},
                warnings=payload.get("warnings"),
                layer_composition=payload.get("layer_composition"),
                surface_payload=payload,
            ), exit_code=1), 1
        return annotate_runtime_surface_payload({
            "state_file": str(state_path),
            "consumed": False,
            "reason": "no_live_control_surface",
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
            "runtime_evidence": runtime_evidence,
            **(
                {"runtime_transition_watchdog": runtime_transition_watchdog}
                if isinstance(runtime_transition_watchdog, dict)
                else {}
            ),
        }, exit_code=1), 1

    payload = {
        "state_file": str(state_path),
        "consumed": False,
        "inspect_only": True,
        "control_signals": control_signals,
        "discipline_contract": discipline_contract,
        "runtime_evidence": runtime_evidence,
        "warnings": report["warnings"],
    }
    if isinstance(runtime_transition_watchdog, dict):
        payload["runtime_transition_watchdog"] = runtime_transition_watchdog

    self_check_agenda = report.get("self_check_agenda")
    if isinstance(self_check_agenda, dict):
        payload["self_check_agenda"] = self_check_agenda

    closure_nucleus = report.get("closure_nucleus")
    if isinstance(closure_nucleus, dict):
        payload["closure_nucleus"] = closure_nucleus
        payload["current_structural_bite_if_any"] = closure_nucleus.get(
            "current_structural_bite_if_any", {}
        )
        payload["current_读出_bite_if_any"] = closure_nucleus.get(
            "current_读出_bite_if_any", {}
        )
        payload["separating_check_if_any"] = closure_nucleus.get(
            "separating_check_if_any", ""
        )

    layer_composition = report.get("layer_composition")
    if isinstance(layer_composition, dict):
        payload["layer_composition"] = layer_composition

    primitive_field = report.get("primitive_field")
    if isinstance(primitive_field, dict):
        payload["primitive_field"] = primitive_field
        payload["primitive_semantics"] = report.get("primitive_semantics", {})

    skill_field = report.get("skill_field")
    if isinstance(skill_field, dict):
        payload["skill_field"] = skill_field
        payload["skill_semantics"] = report.get("skill_semantics", {})

    skill_competition = report.get("skill_competition")
    if isinstance(skill_competition, dict):
        payload["skill_competition"] = skill_competition
        payload["skill_competition_semantics"] = report.get(
            "skill_competition_semantics", {}
        )

    skill_inhibition = report.get("skill_inhibition")
    if isinstance(skill_inhibition, dict):
        payload["skill_inhibition"] = skill_inhibition

    skill_authority_bridge = report.get("skill_authority_bridge")
    if isinstance(skill_authority_bridge, dict):
        payload["skill_authority_bridge"] = skill_authority_bridge
    skill_lighting_surface = _host_visible_skill_lighting_surface(report)
    if skill_lighting_surface:
        payload["skill_lighting_surface"] = skill_lighting_surface
    resume_bridge = report.get("resume_bridge")
    if isinstance(resume_bridge, dict):
        payload["resume_bridge"] = resume_bridge
    probe_discipline = report.get("probe_discipline")
    if isinstance(probe_discipline, dict):
        payload["probe_discipline"] = probe_discipline

    interlayer_discharge_bridge = report.get("interlayer_discharge_bridge")
    if isinstance(interlayer_discharge_bridge, dict):
        payload["interlayer_discharge_bridge"] = interlayer_discharge_bridge

    inhibition_state = report.get("inhibition_state")
    if isinstance(inhibition_state, dict):
        payload["inhibition_state"] = inhibition_state

    reselection_bridge = report.get("reselection_bridge")
    if isinstance(reselection_bridge, dict):
        payload["reselection_bridge"] = reselection_bridge

    if discipline_contract.get("active") is True:
        quiet_payload_for_active_contract(payload)
    elif should_quiet_for_probe_drift(payload):
        payload["ordinary_regrowth_forbidden"] = True
        payload["reader_quieted"] = True
        cool_shortcut_fields(payload)

    cool_shortcut_fields(payload)
    pending_contract = pending_runtime_execution_contract(
        state,
        layer_composition=payload.get("layer_composition"),
    )
    if isinstance(pending_contract, dict):
        payload["pending_transition"] = True
        if (
            isinstance(runtime_transition_watchdog, dict)
            and runtime_transition_watchdog.get("expired") is True
        ):
            payload["reason"] = "bootstrap_runtime_window_expired"
        payload["required_action"] = pending_contract.get("required_action", "")
        payload["allowed_transition_surfaces"] = pending_contract.get(
            "allowed_transition_surfaces",
            [],
        )
        if isinstance(pending_contract.get("authorized_bite"), dict) and pending_contract.get(
            "authorized_bite"
        ):
            payload["authorized_bite_if_any"] = pending_contract.get("authorized_bite")
        return annotate_runtime_surface_payload(build_runtime_evidence_refusal_payload(
            state_path,
            discipline_contract=payload.get("discipline_contract"),
            resume_bridge=payload.get("resume_bridge"),
            warnings=payload.get("warnings"),
            layer_composition=payload.get("layer_composition"),
            surface_payload=payload,
        ), exit_code=1), 1
    if active_contract_requires_runtime_evidence(
        payload.get("discipline_contract"),
        payload.get("runtime_evidence"),
        layer_composition=payload.get("layer_composition"),
        state=state,
    ):
        return annotate_runtime_surface_payload(build_runtime_evidence_refusal_payload(
            state_path,
            discipline_contract=payload.get("discipline_contract"),
            resume_bridge=payload.get("resume_bridge"),
            warnings=payload.get("warnings"),
            layer_composition=payload.get("layer_composition"),
            surface_payload=payload,
        ), exit_code=1), 1
    payload = annotate_runtime_surface_payload(
        reorder_payload_authority_first(payload),
        exit_code=0,
    )
    return payload, 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "One-shot host reader for the current top-level control signal surface. "
            "It exposes essence/owner/carrier suspicion as thin runtime bias, not as a route."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    args = parser.parse_args()

    payload, exit_code = build_controller_读出(Path(args.state_file))
    payload = annotate_runtime_surface_payload(payload, exit_code=exit_code)
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

