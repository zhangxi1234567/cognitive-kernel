#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_guard import build_report, load_json
from runtime_state import build_runtime_evidence


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
        return bridge.get("executable_local_touch_if_any")
    contract = payload.get("discipline_contract")
    if isinstance(contract, dict) and isinstance(contract.get("authorized_bite"), dict):
        return contract.get("authorized_bite")
    interlayer = payload.get("interlayer_discharge_bridge")
    if isinstance(interlayer, dict) and isinstance(interlayer.get("spend_first_program"), dict):
        return interlayer.get("spend_first_program")
    return None


def _winning_skill(payload: dict) -> str:
    bridge = payload.get("skill_authority_bridge")
    if isinstance(bridge, dict):
        return _normalize_text(bridge.get("winning_skill_if_any"))
    return ""


def cool_shortcut_fields(payload: dict) -> None:
    authority_touch = _authority_touch(payload)
    winning_skill = _winning_skill(payload)

    next_touch = payload.get("next_touch")
    if next_touch and not _same_program(next_touch, authority_touch):
        payload.pop("next_touch", None)
        payload.pop("default_local_action", None)

    next_primitive_touch = payload.get("next_primitive_touch")
    if next_primitive_touch and not _same_program(next_primitive_touch, authority_touch):
        payload.pop("next_primitive_touch", None)
        payload.pop("reselection_origin", None)

    readout_bite = payload.get("current_readout_bite_if_any")
    if readout_bite and winning_skill != "exact_closure" and not _same_program(
        readout_bite, authority_touch
    ):
        payload.pop("current_readout_bite_if_any", None)

    structural_bite = payload.get("current_structural_bite_if_any")
    if structural_bite and winning_skill == "exact_closure":
        interlayer = payload.get("interlayer_discharge_bridge")
        spend_first = (
            interlayer.get("spend_first_program")
            if isinstance(interlayer, dict)
            else None
        )
        if not _same_program(structural_bite, spend_first):
            payload.pop("current_structural_bite_if_any", None)


def reorder_payload_authority_first(payload: dict) -> dict:
    ordered: dict = {}
    preferred = [
        "state_file",
        "consumed",
        "discipline_contract",
        "runtime_evidence",
        "ordinary_regrowth_forbidden",
        "reader_quieted",
        "authorized_bite_if_any",
        "skill_authority_bridge",
        "probe_discipline",
        "interlayer_discharge_bridge",
        "skill_field",
        "skill_competition",
        "skill_inhibition",
        "closure_nucleus",
        "current_structural_bite_if_any",
        "current_readout_bite_if_any",
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
    return isinstance(discipline, dict) and (
        discipline.get("probe_must_bind") is True
        and discipline.get("unbound_probe_is_drift") is True
        and not _normalize_text(discipline.get("active_skill_hypothesis"))
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


def build_primitive_readout(state_path: Path) -> tuple[dict, int]:
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
        "consumed": True,
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
        payload["current_readout_bite_if_any"] = closure_nucleus.get(
            "current_readout_bite_if_any", {}
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

    payload, exit_code = build_primitive_readout(Path(args.state_file))
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
