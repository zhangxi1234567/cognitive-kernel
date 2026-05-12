#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_guard import build_report, load_json


def quiet_payload_for_active_contract(payload: dict) -> None:
    payload["ordinary_regrowth_forbidden"] = True
    payload["reader_quieted"] = True
    payload["authorized_bite_if_any"] = payload.get("discipline_contract", {}).get(
        "authorized_bite", {}
    )
    payload.pop("primitive_semantics", None)
    payload.pop("skill_semantics", None)
    payload.pop("skill_competition_semantics", None)
    payload["primitive_competition_semantics"] = {}
    payload["skill_competition"] = {}
    payload["skill_competition_semantics"] = {}


def build_reselection_readout(state_path: Path) -> tuple[dict, int]:
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
        "consumed": True,
        "default_local_action": bridge.get("default_local_action", ""),
        "handoff_origin": bridge.get("handoff_origin", ""),
        "control_context": {
            "current_object": bridge.get("current_object", ""),
            "current_seam": bridge.get("current_seam", ""),
            "current_debt": bridge.get("current_debt", ""),
            "next_bite": bridge.get("next_bite", ""),
            "primary_slot": bridge.get("primary_slot", ""),
        },
        "readout": bridge.get("handoff", {}),
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
        "primitive_control": (
            report.get("control_signals", {}).get("primitive_control", {})
            if isinstance(report.get("control_signals"), dict)
            else {}
        ),
        "next_primitive_touch": bridge.get("next_primitive_touch", {}),
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

    if discipline_contract.get("active") is True:
        quiet_payload_for_active_contract(payload)
    return payload, 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "One-shot host reader for a local carrier-change / primitive-reselection handoff. "
            "It only emits the current reselection readout; it does not choose or execute a route."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    args = parser.parse_args()

    payload, exit_code = build_reselection_readout(Path(args.state_file))
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
