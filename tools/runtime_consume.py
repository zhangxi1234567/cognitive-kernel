#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import json
import io
import sys
from pathlib import Path

from runtime_guard import build_report, load_json
from runtime_next_touch import build_consumption
from runtime_reselection import build_reselection_readout
from runtime_state import (
    build_runtime_evidence,
    command_bind_local,
    command_spend_local,
    load_state,
    render_runtime_skill_trace_markdown,
    render_runtime_trace_markdown,
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

    control_bridge = payload.get("control_bridge")
    if isinstance(control_bridge, dict):
        next_touch = control_bridge.get("next_touch")
        if next_touch and not _same_program(next_touch, authority_touch):
            payload.pop("control_bridge", None)

    reselection_bridge = payload.get("reselection_bridge")
    if isinstance(reselection_bridge, dict):
        next_primitive_touch = reselection_bridge.get("next_primitive_touch")
        if next_primitive_touch and not _same_program(next_primitive_touch, authority_touch):
            payload.pop("reselection_bridge", None)

    if winning_skill != "exact_closure":
        readout_bite = payload.get("current_readout_bite_if_any")
        if readout_bite and not _same_program(readout_bite, authority_touch):
            payload.pop("current_readout_bite_if_any", None)


def should_quiet_for_authority(payload: dict) -> bool:
    bridge = payload.get("skill_authority_bridge")
    if isinstance(bridge, dict) and _normalize_text(bridge.get("winning_skill_if_any")):
        return True
    discipline = payload.get("probe_discipline")
    if isinstance(discipline, dict):
        if _normalize_text(discipline.get("active_skill_hypothesis")):
            return True
        if (
            discipline.get("probe_must_bind") is True
            and discipline.get("unbound_probe_is_drift") is True
        ):
            return True
    interlayer = payload.get("interlayer_discharge_bridge")
    return isinstance(interlayer, dict) and _normalize_text(interlayer.get("mode")) != ""


def reorder_payload_authority_first(payload: dict) -> dict:
    ordered: dict = {}
    preferred = [
        "state_file",
        "consumed",
        "inspect_only",
        "surface",
        "discipline_contract",
        "runtime_evidence",
        "ordinary_regrowth_forbidden",
        "inspect_noise_cooled",
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
        "control_signals",
        "inhibition_state",
        "control_bridge",
        "reselection_bridge",
        "self_check_agenda",
        "warnings",
    ]
    for key in preferred:
        if key in payload:
            ordered[key] = payload[key]
    for key, value in payload.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def discipline_contract_from_report(report: dict) -> dict:
    contract = report.get("discipline_contract", {})
    return contract if isinstance(contract, dict) else {}


def attach_discipline_contract(payload: dict, report: dict) -> dict:
    payload["discipline_contract"] = discipline_contract_from_report(report)
    return payload


def attach_runtime_evidence(payload: dict, state_path: Path) -> dict:
    payload["runtime_evidence"] = build_runtime_evidence(state_path)
    return payload


def active_contract_requires_runtime_evidence(payload: dict) -> bool:
    contract = payload.get("discipline_contract")
    if not isinstance(contract, dict) or contract.get("active") is not True:
        return False
    evidence = payload.get("runtime_evidence")
    if not isinstance(evidence, dict):
        return True
    return evidence.get("has_runtime_consumption") is not True


def build_runtime_evidence_refusal(state_path: Path, payload: dict) -> tuple[dict, int]:
    refusal = {
        "state_file": str(state_path),
        "consumed": False,
        "reason": "active_discipline_contract_requires_runtime_consumption",
        "discipline_contract": payload.get("discipline_contract", {}),
        "runtime_evidence": build_runtime_evidence(state_path),
        "warnings": payload.get("warnings", []),
        "trace_preview": render_runtime_skill_trace_markdown(state_path),
    }
    return refusal, 1


def quiet_inspect_payload_for_active_contract(payload: dict, *, surface: str) -> None:
    payload["ordinary_regrowth_forbidden"] = True
    payload["inspect_noise_cooled"] = True
    payload["authorized_bite_if_any"] = payload.get("discipline_contract", {}).get(
        "authorized_bite", {}
    )

    if surface == "explicit_next_touch":
        payload["self_check_agenda"] = {}
        payload["reselection_bridge"] = {}
        payload["skill_competition"] = {}
        payload["skill_competition_semantics"] = {}
        payload["primitive_competition"] = {}
        payload["primitive_competition_semantics"] = {}
        control_signals = payload.get("control_signals", {})
        if isinstance(control_signals, dict):
            payload["control_signals"] = {
                "micro_control_surface": control_signals.get("micro_control_surface", {}),
                "incentive_field": control_signals.get("incentive_field", {}),
                "primitive_control": control_signals.get("primitive_control", {}),
                "probe_discipline": control_signals.get("probe_discipline", {}),
            }
        control_bridge = payload.get("control_bridge", {})
        if isinstance(control_bridge, dict):
            payload["control_bridge"] = {
                "default_local_action": control_bridge.get("default_local_action", ""),
                "program_origin": control_bridge.get("program_origin", ""),
                "next_touch": control_bridge.get("next_touch", {}),
                "gate_binding": control_bridge.get("gate_binding", {}),
            }
    elif surface == "explicit_reselection":
        payload["self_check_agenda"] = {}
        payload["skill_competition"] = {}
        payload["skill_competition_semantics"] = {}
        payload["primitive_competition"] = {}
        payload["primitive_competition_semantics"] = {}
        control_signals = payload.get("control_signals", {})
        if isinstance(control_signals, dict):
            payload["control_signals"] = {
                "micro_control_surface": control_signals.get("micro_control_surface", {}),
                "incentive_field": control_signals.get("incentive_field", {}),
                "primitive_control": control_signals.get("primitive_control", {}),
                "probe_discipline": control_signals.get("probe_discipline", {}),
            }
        reselection_bridge = payload.get("reselection_bridge", {})
        if isinstance(reselection_bridge, dict):
            payload["reselection_bridge"] = {
                "default_local_action": reselection_bridge.get("default_local_action", ""),
                "handoff_origin": reselection_bridge.get("handoff_origin", ""),
                "handoff": reselection_bridge.get("handoff", {}),
                "warm_field": reselection_bridge.get("warm_field", {}),
                "next_primitive_touch": reselection_bridge.get("next_primitive_touch", {}),
            }
    cool_shortcut_fields(payload)


def build_inspect_surface(state_path: Path) -> tuple[dict, int]:
    state = load_json(state_path)
    report = build_report(state, state_path)

    if report["problems"]:
        payload = attach_discipline_contract({
            "state_file": str(state_path),
            "consumed": False,
            "reason": "invalid_state",
            "problems": report["problems"],
            "warnings": report["warnings"],
        }, report)
        return attach_runtime_evidence(payload, state_path), 2

    explicit_handoff = isinstance(state.get("carrier_handoff_if_any"), dict)
    explicit_program = isinstance(state.get("bound_program"), dict)
    surface = (
        "explicit_reselection"
        if explicit_handoff
        else "explicit_next_touch"
        if explicit_program
        else "neutral_inspect"
    )

    payload = {
        "state_file": str(state_path),
        "consumed": False,
        "inspect_only": True,
        "surface": surface,
        "primitive_field": report.get("primitive_field", {}),
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
        "interlayer_discharge_bridge": report.get("interlayer_discharge_bridge", {}),
        "probe_discipline": report.get("probe_discipline", {}),
        "discipline_contract": discipline_contract_from_report(report),
        "closure_nucleus": report.get("closure_nucleus", {}),
        "control_signals": report.get("control_signals", {}),
        "inhibition_state": report.get("inhibition_state", {}),
        "self_check_agenda": report.get("self_check_agenda", {}),
        "control_bridge": report.get("control_bridge", {}),
        "reselection_bridge": report.get("reselection_bridge", {}),
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
    discipline_contract = payload.get("discipline_contract")
    if isinstance(discipline_contract, dict) and discipline_contract.get("active") is True:
        quiet_inspect_payload_for_active_contract(payload, surface=surface)
    elif should_quiet_for_authority(payload):
        payload["ordinary_regrowth_forbidden"] = True
        payload["inspect_noise_cooled"] = True
        payload.pop("primitive_semantics", None)
        payload.pop("skill_semantics", None)
        payload.pop("skill_competition_semantics", None)
        payload["self_check_agenda"] = {}
        cool_shortcut_fields(payload)
    payload = attach_runtime_evidence(payload, state_path)
    payload = reorder_payload_authority_first(payload)
    return payload, 0


def run_bind_local_once(
    state_path: Path,
    allow_handoff: bool,
    spend_handoff: bool,
    allow_rival: bool,
    previous_state: str | None,
) -> tuple[dict, int]:
    state = load_state(state_path)
    if state.get("bound_program") is not None or state.get("carrier_handoff_if_any") is not None:
        report = build_report(state, state_path)
        if state.get("carrier_handoff_if_any") is not None:
            if spend_handoff:
                spend_args = argparse.Namespace(state_file=str(state_path))
                spend_error = None
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        command_spend_local(spend_args)
                except SystemExit as exc:
                    spend_error = str(exc)
                rebound_state = load_json(state_path)
                if rebound_state.get("bound_program") is not None:
                    payload, exit_code = build_consumption(state_path)
                    payload["already_bound"] = False
                    payload["binding_action"] = "spend_local_primitive"
                    payload["primitive_field"] = payload.get(
                        "primitive_field", report.get("primitive_field", {})
                    )
                    payload["primitive_competition"] = payload.get(
                        "primitive_competition", report.get("primitive_competition", {})
                    )
                    return payload, exit_code
                if spend_error is not None:
                    refreshed_report = build_report(rebound_state, state_path)
                    payload = attach_discipline_contract({
                        "state_file": str(state_path),
                        "consumed": False,
                        "binding_action": "spend_local_refused",
                        "reason": spend_error,
                        "primitive_field": refreshed_report.get("primitive_field", {}),
                        "primitive_competition": refreshed_report.get(
                            "primitive_competition", {}
                        ),
                        "warnings": refreshed_report["warnings"],
                        "problems": refreshed_report["problems"],
                    }, refreshed_report)
                    return attach_runtime_evidence(payload, state_path), 1
            payload, exit_code = build_reselection_readout(state_path)
            payload["already_bound"] = True
            payload["binding_action"] = "none"
            payload["primitive_field"] = payload.get("primitive_field", report.get("primitive_field", {}))
            payload["primitive_competition"] = payload.get(
                "primitive_competition", report.get("primitive_competition", {})
            )
            return payload, exit_code
        payload, exit_code = build_consumption(state_path)
        payload["already_bound"] = True
        payload["binding_action"] = "none"
        payload["primitive_field"] = payload.get("primitive_field", report.get("primitive_field", {}))
        payload["primitive_competition"] = payload.get(
            "primitive_competition", report.get("primitive_competition", {})
        )
        return payload, exit_code

    args = argparse.Namespace(
        state_file=str(state_path),
        previous_state=previous_state,
        allow_handoff=allow_handoff,
        allow_rival=allow_rival,
    )

    try:
        with contextlib.redirect_stdout(io.StringIO()):
            command_bind_local(args)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        report = build_report(load_json(state_path), state_path)
        payload = attach_discipline_contract({
            "state_file": str(state_path),
            "consumed": False,
            "binding_action": "refused",
            "reason": str(exc),
            "primitive_field": report.get("primitive_field", {}),
            "primitive_competition": report.get("primitive_competition", {}),
            "warnings": report["warnings"],
            "problems": report["problems"],
        }, report)
        return attach_runtime_evidence(payload, state_path), code

    rebound_state = load_json(state_path)
    if rebound_state.get("carrier_handoff_if_any") is not None:
        payload, exit_code = build_reselection_readout(state_path)
        payload["already_bound"] = False
        payload["binding_action"] = "rebind_local_pressure"
        payload["primitive_field"] = payload.get("primitive_field", {})
        payload["primitive_competition"] = payload.get("primitive_competition", {})
        return payload, exit_code

    payload, exit_code = build_consumption(state_path)
    payload["already_bound"] = False
    payload["binding_action"] = "next_touch"
    payload["primitive_field"] = payload.get("primitive_field", {})
    payload["primitive_competition"] = payload.get("primitive_competition", {})
    return payload, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Thin host consumer for one already-local runtime action. "
            "By default it only inspects the current local action surface. "
            "Use --bind-once to persist exactly one local action object when the state is local enough, then stop."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    parser.add_argument(
        "--bind-once",
        action="store_true",
        help="Persist exactly one local bind/handoff if the state is already local enough",
    )
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Compatibility alias for the default inspect-only behavior",
    )
    parser.add_argument(
        "--allow-handoff",
        action="store_true",
        help=(
            "Allow one thinner-carrier handoff if same-carrier binding is not the unique live bite"
        ),
    )
    parser.add_argument(
        "--spend-handoff",
        action="store_true",
        help="If a thinner-carrier handoff is already explicit, allow one one-shot spend on that new layer",
    )
    parser.add_argument(
        "--allow-rival",
        action="store_true",
        help="Allow one rival-local witness bind when the unique focus is already rival",
    )
    parser.add_argument(
        "--previous-state",
        help="Optional immediately previous snapshot used only for same-carrier stall detection",
    )
    parser.add_argument(
        "--require-runtime-evidence",
        action="store_true",
        help=(
            "Refuse inspect-only success under an active discipline contract "
            "until at least one bind-local/rebind-local/spend-local event has really happened"
        ),
    )
    parser.add_argument(
        "--trace-output",
        help="Optional path to export the sidecar runtime trace markdown",
    )
    args = parser.parse_args()

    state_path = Path(args.state_file)
    if args.bind_once is not True:
        payload, exit_code = build_inspect_surface(state_path)
    else:
        payload, exit_code = run_bind_local_once(
            state_path,
            allow_handoff=args.allow_handoff,
            spend_handoff=args.spend_handoff,
            allow_rival=args.allow_rival,
            previous_state=args.previous_state,
        )

    payload = attach_runtime_evidence(payload, state_path)
    if args.trace_output:
        trace_path = Path(args.trace_output)
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text(render_runtime_trace_markdown(state_path), encoding="utf-8")
    if args.require_runtime_evidence and active_contract_requires_runtime_evidence(payload):
        payload, exit_code = build_runtime_evidence_refusal(state_path, payload)

    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
