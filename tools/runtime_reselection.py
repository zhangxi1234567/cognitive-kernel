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
        "competition_quieted",
        "authorized_bite_if_any",
        "resume_bridge",
        "skill_authority_bridge",
        "control_context",
        "读出",
        "warm_field",
        "closure_nucleus",
        "current_structural_bite_if_any",
        "current_读出_bite_if_any",
        "separating_check_if_any",
        "primitive_field",
        "primitive_competition",
        "skill_field",
        "skill_competition",
        "skill_inhibition",
        "primitive_control",
        "handoff_origin",
        "next_primitive_touch",
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


def quiet_payload_for_active_contract(payload: dict) -> None:
    payload["ordinary_regrowth_forbidden"] = True
    payload["reader_quieted"] = True
    payload["authorized_bite_if_any"] = payload.get("discipline_contract", {}).get(
        "authorized_bite", {}
    )
    payload.pop("primitive_semantics", None)
    payload.pop("skill_semantics", None)
    payload.pop("skill_competition_semantics", None)
    payload["competition_quieted"] = True


def _host_visible_discipline_contract(contract: object) -> dict:
    if not isinstance(contract, dict):
        return {}
    compact: dict = {}
    for key in [
        "active",
        "forbid_ordinary_regrowth",
        "surface",
        "owner",
        "current_object",
        "current_debt",
        "authorized_bite",
        "reason",
        "tears_on",
        "active_skill_combo_if_any",
        "structural_first",
    ]:
        value = contract.get(key)
        if value not in (None, "", [], {}):
            compact[key] = value
    return compact


def _host_visible_layer_composition(layer: object) -> dict:
    if not isinstance(layer, dict):
        return {}
    compact: dict = {}
    for key in [
        "active",
        "surface",
        "layer_object",
        "current_seam",
        "current_debt",
        "reason",
        "event_owned",
        "forbid_ordinary_regrowth",
        "must_bind_local_bite",
        "must_spend_handoff",
        "leading_skill_if_any",
        "active_skill_combo_if_any",
        "authorized_bite",
    ]:
        value = layer.get(key)
        if value not in (None, "", [], {}):
            compact[key] = value
    return compact


def build_reselection_读出(state_path: Path) -> tuple[dict, int]:
    state = load_json(state_path)
    report = build_report(state, state_path)
    discipline_contract = _host_visible_discipline_contract(report.get("discipline_contract", {}))
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
        }, 2

    bridge = report.get("reselection_bridge")
    if not isinstance(bridge, dict):
        return {
            "state_file": str(state_path),
            "consumed": False,
            "reason": "no_reselection_bridge",
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
        }, 1

    payload = {
        "state_file": str(state_path),
        "consumed": False,
        "inspect_only": True,
        "handoff_origin": bridge.get("handoff_origin", ""),
        "control_context": {
            "current_object": bridge.get("current_object", ""),
            "current_seam": bridge.get("current_seam", ""),
            "current_debt": bridge.get("current_debt", ""),
            "next_bite": bridge.get("next_bite", ""),
            "primary_slot": bridge.get("primary_slot", ""),
        },
        "读出": bridge.get("handoff", {}),
        "warm_field": bridge.get("warm_field", {}),
        "closure_nucleus": bridge.get("closure_nucleus", report.get("closure_nucleus", {})),
        "primitive_field": bridge.get("primitive_field", report.get("primitive_field", {})),
        "primitive_semantics": report.get("primitive_semantics", {}),
        "primitive_competition": report.get("primitive_competition", {}),
        "primitive_competition_semantics": report.get(
            "primitive_competition_semantics", {}
        ),
        "skill_field": report.get("skill_field", {}),
        "skill_semantics": report.get("skill_semantics", {}),
        "skill_competition": report.get("skill_competition", {}),
        "skill_competition_semantics": report.get("skill_competition_semantics", {}),
        "skill_inhibition": report.get("skill_inhibition", {}),
        "skill_authority_bridge": report.get("skill_authority_bridge", {}),
        "discipline_contract": discipline_contract,
        "resume_bridge": report.get("resume_bridge", {}),
        "primitive_control": (
            report.get("control_signals", {}).get("primitive_control", {})
            if isinstance(report.get("control_signals"), dict)
            else {}
        ),
        "next_primitive_touch": bridge.get("next_primitive_touch", {}),
        "runtime_evidence": build_runtime_evidence(state_path),
        "inhibition_state": report.get("inhibition_state", {}),
        "warnings": report["warnings"],
    }
    layer_composition = report.get("layer_composition")
    if isinstance(layer_composition, dict):
        payload["layer_composition"] = _host_visible_layer_composition(layer_composition)
    closure_nucleus = payload.get("closure_nucleus")
    if isinstance(closure_nucleus, dict):
        payload["current_structural_bite_if_any"] = closure_nucleus.get(
            "current_structural_bite_if_any", {}
        )
        payload["current_读出_bite_if_any"] = closure_nucleus.get(
            "current_读出_bite_if_any", {}
        )
        payload["separating_check_if_any"] = closure_nucleus.get(
            "separating_check_if_any", ""
        )

    if discipline_contract.get("active") is True:
        quiet_payload_for_active_contract(payload)
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
            "One-shot host reader for a local carrier-change / primitive-reselection handoff. "
            "It only emits the current reselection 读出; it does not choose or execute a route."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    args = parser.parse_args()

    payload, exit_code = build_reselection_读出(Path(args.state_file))
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

