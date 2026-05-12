#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_guard import build_report, load_json


def build_consumption(state_path: Path) -> tuple[dict, int]:
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
        }, 2

    bridge = report.get("control_bridge")
    if not isinstance(bridge, dict):
        return {
            "state_file": str(state_path),
            "consumed": False,
            "reason": "no_control_bridge",
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
        }, 1

    action_name = bridge.get("default_local_action")
    if not isinstance(action_name, str) or not action_name:
        return {
            "state_file": str(state_path),
            "consumed": False,
            "reason": "no_default_local_action",
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
        }, 1

    action = bridge.get(action_name)
    if not isinstance(action, dict):
        return {
            "state_file": str(state_path),
            "consumed": False,
            "reason": "missing_default_local_action_payload",
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
        }, 1

    payload = {
        "state_file": str(state_path),
        "consumed": True,
        "default_local_action": action_name,
        "program_origin": bridge.get("program_origin", ""),
        "control_context": {
            "current_object": bridge.get("current_object", ""),
            "current_debt": bridge.get("current_debt", ""),
            "asked_medium_surface": bridge.get("asked_medium_surface", ""),
            "revocation_handle": bridge.get("revocation_handle", ""),
            "primary_slot": bridge.get("primary_slot", ""),
        },
        "readout": action,
        "gate_binding": bridge.get("gate_binding", {}),
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
        "primitive_control": (
            report.get("control_signals", {}).get("primitive_control", {})
            if isinstance(report.get("control_signals"), dict)
            else {}
        ),
        "meta_controls": (
            report.get("control_signals", {}).get("meta_controls", {})
            if isinstance(report.get("control_signals"), dict)
            else {}
        ),
        "incentive_field": (
            report.get("control_signals", {}).get("incentive_field", {})
            if isinstance(report.get("control_signals"), dict)
            else {}
        ),
        "micro_control_surface": (
            report.get("control_signals", {}).get("micro_control_surface", {})
            if isinstance(report.get("control_signals"), dict)
            else {}
        ),
        "inhibition_state": report.get("inhibition_state", {}),
        "warnings": report["warnings"],
    }
    closure_nucleus = payload.get("closure_nucleus")
    if isinstance(closure_nucleus, dict):
        payload["current_structural_bite_if_any"] = closure_nucleus.get(
            "current_structural_bite_if_any", {}
        )
        payload["current_readout_bite_if_any"] = closure_nucleus.get(
            "current_readout_bite_if_any", {}
        )
        payload["separating_check_if_any"] = closure_nucleus.get(
            "separating_check_if_any", ""
        )
    return payload, 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "One-shot host consumer for control_bridge.next_touch. "
            "It only surfaces the default local action readout; it does not execute it."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    args = parser.parse_args()

    payload, exit_code = build_consumption(Path(args.state_file))
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
