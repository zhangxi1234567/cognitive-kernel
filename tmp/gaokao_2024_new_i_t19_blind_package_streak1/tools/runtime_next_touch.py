#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_guard import build_report, load_json
from runtime_state import (
    active_contract_requires_runtime_evidence,
    annotate_runtime_surface_payload,
    build_runtime_evidence,
    build_runtime_evidence_refusal_payload,
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


def _append_action_candidate(candidates: list[dict], action_name: str, program: object, *, source: str) -> None:
    if not isinstance(program, dict):
        return
    sig = _program_signature(program)
    if not all(sig):
        return
    if any(_program_signature(item.get("program")) == sig for item in candidates):
        return
    candidates.append(
        {
            "action": action_name,
            "source": source,
            "program": program,
        }
    )


def _explicit_layer_composition(report: dict) -> dict:
    layer = report.get("layer_composition")
    return layer if isinstance(layer, dict) else {}


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


def _preferred_action_from_layer_composition(layer_composition: dict) -> str:
    if not isinstance(layer_composition, dict):
        return ""
    if layer_composition.get("must_spend_handoff") is True:
        return "spend_local"
    if layer_composition.get("must_bind_local_bite") is True:
        return "bind_local"
    authorized_bite = layer_composition.get("authorized_bite")
    if _program_signature(authorized_bite) == ("", "", ""):
        return ""
    surface = _normalize_text(layer_composition.get("surface"))
    if surface == "carrier_handoff":
        return "spend_local"
    if surface == "bound_program":
        return "land_local"
    return "bind_local"


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
        "supporting_skills_if_any",
        "authorized_bite",
        "lighting_if_any",
        "false_first_skill_if_any",
        "false_first_label_if_any",
        "false_skill_reason",
        "verify_touch_if_any",
        "accountability_nudge_if_any",
    ]:
        value = layer.get(key)
        if value not in (None, "", [], {}):
            compact[key] = value
    return compact


def _host_visible_skill_lighting_surface(report: dict) -> dict:
    surface: dict = {}
    layer = _explicit_layer_composition(report)
    for source in [layer.get("lighting_if_any"), report.get("skill_lighting_surface")]:
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


def reorder_payload_authority_first(payload: dict) -> dict:
    ordered: dict = {}
    preferred = [
        "state_file",
        "consumed",
        "inspect_only",
        "discipline_contract",
        "runtime_evidence",
        "layer_composition",
        "authorized_bite_if_any",
        "skill_authority_bridge",
        "skill_lighting_surface",
        "resume_bridge",
        "读出",
        "available_authority_touches",
        "control_context",
        "closure_nucleus",
        "current_structural_bite_if_any",
        "current_读出_bite_if_any",
        "separating_check_if_any",
        "primitive_field",
        "skill_field",
        "warnings",
    ]
    for key in preferred:
        if key in payload:
            ordered[key] = payload[key]
    for key, value in payload.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def build_consumption(state_path: Path) -> tuple[dict, int]:
    state = load_json(state_path)
    report = build_report(state, state_path)
    discipline_contract = _host_visible_discipline_contract(report.get("discipline_contract", {}))
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
        }, exit_code=2), 2

    bridge = report.get("control_bridge")
    layer_composition = _host_visible_layer_composition(_explicit_layer_composition(report))
    if not isinstance(bridge, dict) and not layer_composition:
        return annotate_runtime_surface_payload({
            "state_file": str(state_path),
            "consumed": False,
            "reason": "no_control_bridge",
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
        }, exit_code=1), 1

    action_candidates: list[dict] = []
    preferred_action = _preferred_action_from_layer_composition(layer_composition)
    if preferred_action:
        _append_action_candidate(
            action_candidates,
            preferred_action,
            layer_composition.get("authorized_bite"),
            source="layer_composition",
        )
    action_name = preferred_action or (bridge.get("default_local_action") if isinstance(bridge, dict) else "")
    if isinstance(action_name, str) and action_name:
        _append_action_candidate(
            action_candidates,
            action_name,
            bridge.get(action_name) if isinstance(bridge, dict) else None,
            source="control_bridge.default_local_action",
        )
    _append_action_candidate(
        action_candidates,
        "next_touch",
        bridge.get("next_touch") if isinstance(bridge, dict) else None,
        source="control_bridge.next_touch",
    )
    skill_bridge = report.get("skill_authority_bridge", {})
    if isinstance(skill_bridge, dict):
        _append_action_candidate(
            action_candidates,
            "authorized_touch",
            skill_bridge.get("executable_local_touch_if_any"),
            source="skill_authority_bridge",
        )
    closure_nucleus = report.get("closure_nucleus", {})
    if isinstance(closure_nucleus, dict):
        _append_action_candidate(
            action_candidates,
            "structural_bite",
            closure_nucleus.get("current_structural_bite_if_any"),
            source="closure_nucleus.structural",
        )
        _append_action_candidate(
            action_candidates,
            "读出_bite",
            closure_nucleus.get("current_读出_bite_if_any"),
            source="closure_nucleus.读出",
        )

    if not action_candidates:
        return annotate_runtime_surface_payload({
            "state_file": str(state_path),
            "consumed": False,
            "reason": "no_authority_touch",
            "warnings": report["warnings"],
            "discipline_contract": discipline_contract,
        }, exit_code=1), 1

    if not isinstance(action_name, str) or not action_name:
        action_name = str(action_candidates[0].get("action", "")).strip()

    action = bridge.get(action_name) if isinstance(bridge, dict) and isinstance(bridge.get(action_name), dict) else action_candidates[0].get("program", {})

    payload = {
        "state_file": str(state_path),
        "consumed": False,
        "inspect_only": True,
        "layer_composition": layer_composition,
        "program_origin": bridge.get("program_origin", "") if isinstance(bridge, dict) else "",
        "control_context": {
            "current_object": bridge.get("current_object", "") if isinstance(bridge, dict) else "",
            "current_debt": bridge.get("current_debt", "") if isinstance(bridge, dict) else "",
            "asked_medium_surface": bridge.get("asked_medium_surface", "") if isinstance(bridge, dict) else "",
            "revocation_handle": bridge.get("revocation_handle", "") if isinstance(bridge, dict) else "",
            "primary_slot": bridge.get("primary_slot", "") if isinstance(bridge, dict) else "",
        },
        "读出": action,
        "available_authority_touches": [
            {
                "source": candidate.get("source", ""),
                "program": candidate.get("program", {}),
            }
            for candidate in action_candidates
            if isinstance(candidate, dict)
        ],
        "gate_binding": bridge.get("gate_binding", {}) if isinstance(bridge, dict) else {},
        "closure_nucleus": bridge.get("closure_nucleus", report.get("closure_nucleus", {})) if isinstance(bridge, dict) else report.get("closure_nucleus", {}),
        "primitive_field": bridge.get("primitive_field", report.get("primitive_field", {})) if isinstance(bridge, dict) else report.get("primitive_field", {}),
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
        "skill_lighting_surface": _host_visible_skill_lighting_surface(report),
        "discipline_contract": discipline_contract,
        "resume_bridge": report.get("resume_bridge", {}),
        "runtime_evidence": build_runtime_evidence(state_path),
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
    authorized_bite = layer_composition.get("authorized_bite")
    if isinstance(authorized_bite, dict) and _program_signature(authorized_bite) != ("", "", ""):
        payload["authorized_bite_if_any"] = authorized_bite
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
    control_signals = report.get("control_signals")
    if isinstance(control_signals, dict):
        payload["control_signals"] = {
            "current_controller_view": control_signals.get("current_controller_view", {}),
            "primitive_control": control_signals.get("primitive_control", {}),
            "incentive_field": control_signals.get("incentive_field", {}),
            "micro_control_surface": control_signals.get("micro_control_surface", {}),
            "probe_discipline": control_signals.get("probe_discipline", {}),
        }
    if discipline_contract.get("active") is True:
        payload["ordinary_regrowth_forbidden"] = True
        payload["reader_quieted"] = True
        payload["authorized_bite_if_any"] = discipline_contract.get("authorized_bite", {})
        payload.pop("primitive_semantics", None)
        payload.pop("skill_semantics", None)
        payload.pop("skill_competition_semantics", None)
        payload["competition_quieted"] = True
    pending_contract = pending_runtime_execution_contract(
        state,
        layer_composition=payload.get("layer_composition"),
    )
    if isinstance(pending_contract, dict):
        payload["pending_transition"] = True
        payload["required_action"] = pending_contract.get("required_action", "")
        payload["allowed_transition_surfaces"] = pending_contract.get(
            "allowed_transition_surfaces",
            [],
        )
        if isinstance(pending_contract.get("authorized_bite"), dict) and pending_contract.get(
            "authorized_bite"
        ):
            payload["authorized_bite_if_any"] = pending_contract.get("authorized_bite")
        return build_runtime_evidence_refusal_payload(
            state_path,
            discipline_contract=payload.get("discipline_contract"),
            resume_bridge=payload.get("resume_bridge"),
            warnings=payload.get("warnings"),
            layer_composition=payload.get("layer_composition"),
            surface_payload=payload,
        ), 1
    if active_contract_requires_runtime_evidence(
        payload.get("discipline_contract"),
        payload.get("runtime_evidence"),
        layer_composition=payload.get("layer_composition"),
        state=state,
    ):
        return build_runtime_evidence_refusal_payload(
            state_path,
            discipline_contract=payload.get("discipline_contract"),
            resume_bridge=payload.get("resume_bridge"),
            warnings=payload.get("warnings"),
            layer_composition=payload.get("layer_composition"),
            surface_payload=payload,
        ), 1
    return annotate_runtime_surface_payload(
        reorder_payload_authority_first(payload),
        exit_code=0,
    ), 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "One-shot host consumer for control_bridge.next_touch. "
            "It only surfaces the default local action 读出; it does not execute it."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    args = parser.parse_args()

    payload, exit_code = build_consumption(Path(args.state_file))
    payload = annotate_runtime_surface_payload(payload, exit_code=exit_code)
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

