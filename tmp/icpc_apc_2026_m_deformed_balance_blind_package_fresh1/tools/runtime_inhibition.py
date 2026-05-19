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


def build_inhibition_读出(state_path: Path) -> tuple[dict, int]:
    state = load_json(state_path)
    report = build_report(state, state_path)

    if report["problems"]:
        return {
            "state_file": str(state_path),
            "consumed": False,
            "reason": "invalid_state",
            "problems": report["problems"],
            "warnings": report["warnings"],
        }, 2

    inhibition_state = report.get("inhibition_state")
    if not isinstance(inhibition_state, dict):
        return {
            "state_file": str(state_path),
            "consumed": False,
            "reason": "no_inhibition_state",
            "warnings": report["warnings"],
        }, 1

    payload = {
        "state_file": str(state_path),
        "consumed": False,
        "inspect_only": True,
        "inhibition_state": inhibition_state,
        "discipline_contract": report.get("discipline_contract", {}),
        "layer_composition": report.get("layer_composition", {}),
        "resume_bridge": report.get("resume_bridge", {}),
        "runtime_evidence": build_runtime_evidence(state_path),
        "warnings": report["warnings"],
    }
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
    return payload, 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "One-shot host reader for the current local inhibition surface. "
            "It exposes who currently owns temporary gate authority without scheduling future moves."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    args = parser.parse_args()

    payload, exit_code = build_inhibition_读出(Path(args.state_file))
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

