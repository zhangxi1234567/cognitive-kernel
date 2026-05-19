#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_guard import build_report, load_json
from runtime_state import (
    active_contract_requires_runtime_evidence,
    build_runtime_evidence,
    build_runtime_evidence_refusal_payload,
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

    next_touch = payload.get("next_touch")
    if next_touch and not _same_program(next_touch, authority_touch):
        payload["next_touch_authority_match"] = False
        payload["non_authoritative_next_touch"] = next_touch
    elif isinstance(next_touch, dict):
        payload["next_touch_authority_match"] = True

    next_primitive_touch = payload.get("next_primitive_touch")
    if next_primitive_touch and not _same_program(next_primitive_touch, authority_touch):
        payload["next_primitive_touch_authority_match"] = False
        payload["non_authoritative_next_primitive_touch"] = next_primitive_touch
    elif isinstance(next_primitive_touch, dict):
        payload["next_primitive_touch_authority_match"] = True

    if winning_skill != "精确封口":
        _retain_shadow_program(
            payload,
            "current_读出_bite_if_any",
            shadow_key="suppressed_读出_bite_if_any",
            authority_touch=authority_touch,
        )

    structural_bite = payload.get("current_structural_bite_if_any")
    if structural_bite and winning_skill == "精确封口":
        interlayer = payload.get("interlayer_discharge_bridge")
        spend_first = (
            interlayer.get("spend_first_program")
            if isinstance(interlayer, dict)
            else None
        )
        if not _same_program(structural_bite, spend_first):
            payload["current_structural_bite_if_any_authority_match"] = False
            payload["suppressed_structural_bite_if_any"] = structural_bite
        else:
            payload["current_structural_bite_if_any_authority_match"] = True


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
        "probe_discipline",
        "interlayer_discharge_bridge",
        "skill_field",
        "skill_competition",
        "skill_inhibition",
        "closure_nucleus",
        "current_structural_bite_if_any",
        "current_读出_bite_if_any",
        "separating_check_if_any",
        "primitive_field",
        "primitive_competition",
        "inhibition_state",
        "control_signals",
        "default_local_action",
        "next_touch",
        "next_primitive_touch",
        "reselection_origin",
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


def quiet_payload_for_active_contract(payload: dict) -> None:
    payload["ordinary_regrowth_forbidden"] = True
    payload["reader_quieted"] = True
    payload["authorized_bite_if_any"] = payload.get("discipline_contract", {}).get(
        "authorized_bite", {}
    )
    payload.pop("primitive_semantics", None)
    payload.pop("skill_semantics", None)
    payload.pop("skill_competition_semantics", None)
    control_signals = payload.get("control_signals")
    if isinstance(control_signals, dict):
        payload["control_signals"] = {
            "current_controller_view": control_signals.get("current_controller_view", {}),
            "primitive_control": control_signals.get("primitive_control", {}),
            "micro_control_surface": control_signals.get("micro_control_surface", {}),
            "probe_discipline": control_signals.get("probe_discipline", {}),
        }
    cool_shortcut_fields(payload)


def build_primitive_读出(state_path: Path) -> tuple[dict, int]:
    state = load_json(state_path)
    report = build_report(state, state_path)
    discipline_contract = report.get("discipline_contract", {})
    if not isinstance(discipline_contract, dict):
        discipline_contract = {}

    if report["problems"]:
        return {
            "state_file": str(state_path),
            "consumed": False,
            "reason": "invalid_state",
            "problems": report["problems"],
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
            "runtime_evidence": build_runtime_evidence(state_path),
        }, 2

    primitive_field = report.get("primitive_field")
    primitive_competition = report.get("primitive_competition")

    if not isinstance(primitive_field, dict) and not isinstance(primitive_competition, dict):
        return {
            "state_file": str(state_path),
            "consumed": False,
            "reason": "no_live_primitive_surface",
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
            "runtime_evidence": build_runtime_evidence(state_path),
        }, 1

    payload = {
        "state_file": str(state_path),
        "consumed": False,
        "inspect_only": True,
        "primitive_field": primitive_field if isinstance(primitive_field, dict) else {},
        "primitive_semantics": report.get("primitive_semantics", {}),
        "primitive_competition": (
            primitive_competition if isinstance(primitive_competition, dict) else {}
        ),
        "primitive_competition_semantics": report.get(
            "primitive_competition_semantics", {}
        ),
        "discipline_contract": discipline_contract,
        "runtime_evidence": build_runtime_evidence(state_path),
        "warnings": report["warnings"],
    }

    layer_composition = report.get("layer_composition")
    if isinstance(layer_composition, dict):
        payload["layer_composition"] = layer_composition

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
    resume_bridge = report.get("resume_bridge")
    if isinstance(resume_bridge, dict):
        payload["resume_bridge"] = resume_bridge
    probe_discipline = report.get("probe_discipline")
    if isinstance(probe_discipline, dict):
        payload["probe_discipline"] = probe_discipline

    interlayer_discharge_bridge = report.get("interlayer_discharge_bridge")
    if isinstance(interlayer_discharge_bridge, dict):
        payload["interlayer_discharge_bridge"] = interlayer_discharge_bridge

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

    inhibition_state = report.get("inhibition_state")
    if isinstance(inhibition_state, dict):
        payload["inhibition_state"] = inhibition_state

    control_signals = report.get("control_signals")
    if isinstance(control_signals, dict):
        payload["control_signals"] = control_signals

    control_bridge = report.get("control_bridge")
    if isinstance(control_bridge, dict) and isinstance(control_bridge.get("primitive_field"), dict):
        payload["default_local_action"] = control_bridge.get("default_local_action", "")
        payload["next_touch"] = control_bridge.get("next_touch", {})

    reselection_bridge = report.get("reselection_bridge")
    if isinstance(reselection_bridge, dict):
        next_primitive_touch = reselection_bridge.get("next_primitive_touch")
        if isinstance(next_primitive_touch, dict):
            payload["next_primitive_touch"] = next_primitive_touch
        payload["reselection_origin"] = reselection_bridge.get("handoff_origin", "")

    if discipline_contract.get("active") is True:
        quiet_payload_for_active_contract(payload)
    elif should_quiet_for_probe_drift(payload):
        payload["ordinary_regrowth_forbidden"] = True
        payload["reader_quieted"] = True
        payload.pop("primitive_semantics", None)
        payload.pop("skill_semantics", None)
        payload.pop("skill_competition_semantics", None)
        cool_shortcut_fields(payload)

    cool_shortcut_fields(payload)
    if active_contract_requires_runtime_evidence(
        payload.get("discipline_contract"),
        payload.get("runtime_evidence"),
        layer_composition=payload.get("layer_composition"),
    ):
        return build_runtime_evidence_refusal_payload(
            state_path,
            discipline_contract=payload.get("discipline_contract"),
            resume_bridge=payload.get("resume_bridge"),
            warnings=payload.get("warnings"),
            layer_composition=payload.get("layer_composition"),
            surface_payload=payload,
        ), 1
    payload = reorder_payload_authority_first(payload)
    return payload, 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "One-shot host reader for the current primitive layer. "
            "It exposes the live primitive field / competition surface without choosing a route."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    args = parser.parse_args()

    payload, exit_code = build_primitive_读出(Path(args.state_file))
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

