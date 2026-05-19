#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import json
import io
import re
import sys
from pathlib import Path

from runtime_guard import build_report, load_json
from runtime_next_touch import build_consumption
from runtime_reselection import build_reselection_读出
from runtime_state import (
    add_bool_argument,
    active_contract_requires_runtime_evidence as contract_requires_runtime_evidence,
    annotate_runtime_surface_payload,
    arm_primitive_takeover_gate,
    build_runtime_evidence_refusal_payload,
    build_runtime_evidence,
    command_bind_local,
    command_execute_local,
    command_land_local,
    command_spend_local,
    fresh_blind_generic_output_refusal,
    fresh_blind_runtime_transition_watchdog,
    load_state,
    materialize_asked_medium_if_ready,
    mutate_state,
    pending_runtime_execution_contract,
    refresh_primitive_field_for_current_layer,
    resolve_state_relative_output_path,
    render_runtime_skill_trace_markdown,
    render_runtime_trace_markdown,
    trace_markdown_path,
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


_ORDINARY_ACTION_REFUSAL_RE = re.compile(r"ordinary fallback action `([^`]+)`", re.IGNORECASE)
_HANDOFF_SKILL_REFUSAL_RE = re.compile(r"(?:先让|先用|当前应先由) `([^`]+)`")


def _merge_skill_names(*groups: object, limit: int = 6) -> list[str]:
    merged: list[str] = []
    for group in groups:
        if isinstance(group, (list, tuple)):
            values = group
        else:
            values = [group]
        for value in values:
            skill = _normalize_text(value)
            if not skill or skill in merged:
                continue
            merged.append(skill)
            if len(merged) >= limit:
                return merged
    return merged


def _execute_local_retry_guidance(
    refusal_reason: str,
    *,
    owner_skill: str,
    combo: list[str],
) -> dict:
    normalized_reason = _normalize_text(refusal_reason)
    ordinary_action = ""
    handoff_mentions: list[str] = []
    if refusal_reason:
        action_match = _ORDINARY_ACTION_REFUSAL_RE.search(refusal_reason)
        if action_match:
            ordinary_action = _normalize_text(action_match.group(1))
        handoff_mentions = [
            _normalize_text(match)
            for match in _HANDOFF_SKILL_REFUSAL_RE.findall(refusal_reason)
            if _normalize_text(match)
        ]

    primary_skill = handoff_mentions[-1] if handoff_mentions else owner_skill
    supporting_skills = [
        skill
        for skill in _merge_skill_names(handoff_mentions[:-1], combo)
        if skill and skill != primary_skill
    ]

    normalized_lower = normalized_reason.lower()
    refusal_kind = "generic"
    if ordinary_action:
        refusal_kind = "ordinary_fallback"
    elif "worked_step only reported that something was solved" in normalized_lower:
        refusal_kind = "result_only"
    elif "visible skill expression is required on the live layer" in normalized_lower:
        refusal_kind = "visible_skill"

    return {
        "ordinary_action": ordinary_action,
        "primary_skill": primary_skill or owner_skill,
        "supporting_skills": supporting_skills[:3],
        "refusal_kind": refusal_kind,
        "normalized_reason": normalized_reason,
    }


def _explicit_layer_composition(report: dict) -> dict:
    layer = report.get("layer_composition")
    return layer if isinstance(layer, dict) else {}


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
        "current_layer_object_if_any",
        "object_transform_if_any",
        "step_outline_if_any",
        "skill_phase_if_any",
        "reason",
        "event_owned",
        "forbid_ordinary_regrowth",
        "must_bind_local_bite",
        "must_spend_handoff",
        "leading_skill_if_any",
        "active_skill_combo_if_any",
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
    persisted = layer.get("lighting_if_any")
    derived = report.get("skill_lighting_surface")
    for source in [persisted, derived]:
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


def _requires_qualified_claim_gating(
    bootstrap_context: object,
    runtime_evidence: object,
) -> bool:
    if not isinstance(bootstrap_context, dict):
        return False
    if (
        bootstrap_context.get("requires_qualified_layer_composition_for_skill_claims") is not True
        and _normalize_text(bootstrap_context.get("mode")) != "fresh_blind_project_skills_on"
    ):
        return False
    if not isinstance(runtime_evidence, dict):
        return True
    if runtime_evidence.get("latest_qualified_consumption_layer_composition_qualified") is True:
        return False
    return True


def cool_unqualified_skill_claims(
    payload: dict,
    *,
    bootstrap_context: object,
    runtime_evidence: object,
) -> None:
    if not _requires_qualified_claim_gating(bootstrap_context, runtime_evidence):
        return
    for key in [
        "skill_field",
        "skill_semantics",
        "skill_competition",
        "skill_competition_semantics",
        "skill_inhibition",
        "skill_authority_bridge",
        "skill_coaching_surface",
        "probe_discipline",
        "control_signals",
        "control_bridge",
        "reselection_bridge",
        "current_structural_bite_if_any",
        "current_读出_bite_if_any",
        "separating_check_if_any",
    ]:
        payload.pop(key, None)

    lighting = payload.get("skill_lighting_surface")
    if isinstance(lighting, dict):
        candidate_only = {
            "candidate_skills_if_any": lighting.get("candidate_skills_if_any", []),
            "false_first_skill_if_any": lighting.get("false_first_skill_if_any", ""),
            "false_first_label_if_any": lighting.get("false_first_label_if_any", ""),
            "false_skill_reason": lighting.get("false_skill_reason", ""),
            "accountability_nudge_if_any": lighting.get("accountability_nudge_if_any", ""),
            "anti_pipeline_note": (
                "candidate skills are visible, but no skill is counted as lit until one "
                "qualified runtime transition owns the layer"
            ),
            "qualified_claims_pending": True,
        }
        candidate_only = {
            key: value
            for key, value in candidate_only.items()
            if value not in (None, "", [], {})
        }
        if candidate_only:
            payload["skill_lighting_surface"] = candidate_only
        else:
            payload.pop("skill_lighting_surface", None)

    layer = payload.get("layer_composition")
    if isinstance(layer, dict) and layer.get("event_owned") is not True:
        pending_layer = dict(layer)
        if isinstance(pending_layer.get("lighting_if_any"), dict):
            pending_layer["lighting_if_any"] = {
                "candidate_skills_if_any": pending_layer["lighting_if_any"].get(
                    "candidate_skills_if_any",
                    [],
                ),
                "qualified_claims_pending": True,
                "anti_pipeline_note": (
                    "this layer is projected from a pending contract and is not yet a "
                    "qualified lit-skill ownership event"
                ),
            }
        pending_layer["qualified_claims_pending"] = True
        payload["layer_composition"] = pending_layer


def attach_runtime_transition_watchdog(payload: dict, *, state: object) -> None:
    runtime_evidence = payload.get("runtime_evidence")
    watchdog = fresh_blind_runtime_transition_watchdog(
        state,
        runtime_evidence=runtime_evidence if isinstance(runtime_evidence, dict) else None,
    )
    if isinstance(watchdog, dict):
        payload["runtime_transition_watchdog"] = watchdog
        if watchdog.get("expired") is True:
            payload["reason"] = "bootstrap_runtime_window_expired"


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


def _authority_touch(payload: dict) -> dict | None:
    bridge = payload.get("skill_authority_bridge")
    if isinstance(bridge, dict) and isinstance(bridge.get("executable_local_touch_if_any"), dict):
        executable = bridge.get("executable_local_touch_if_any")
        if _program_signature(executable) != ("", "", ""):
            return executable
    interlayer = payload.get("interlayer_discharge_bridge")
    if isinstance(interlayer, dict) and isinstance(interlayer.get("spend_first_program"), dict):
        return interlayer.get("spend_first_program")
    contract = payload.get("discipline_contract")
    if isinstance(contract, dict) and isinstance(contract.get("authorized_bite"), dict):
        authorized = contract.get("authorized_bite")
        if _program_signature(authorized) != ("", "", ""):
            return authorized
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

    control_bridge = payload.get("control_bridge")
    if isinstance(control_bridge, dict):
        suppressed_action_keys: list[str] = []
        next_touch = control_bridge.get("next_touch")
        candidate_authorized_bite = control_bridge.get("candidate_authorized_bite")
        if next_touch and not _same_program(next_touch, authority_touch):
            suppressed_action_keys.append("next_touch")
        if candidate_authorized_bite and not _same_program(
            candidate_authorized_bite,
            authority_touch,
        ):
            suppressed_action_keys.append("candidate_authorized_bite")
        if suppressed_action_keys:
            payload["non_authoritative_control_bridge"] = {
                "program_origin": control_bridge.get("program_origin", ""),
                "suppressed_action_keys": suppressed_action_keys,
                "authority_match": False,
            }

    reselection_bridge = payload.get("reselection_bridge")
    if isinstance(reselection_bridge, dict):
        next_primitive_touch = reselection_bridge.get("next_primitive_touch")
        if next_primitive_touch and not _same_program(next_primitive_touch, authority_touch):
            payload["non_authoritative_reselection_bridge"] = {
                "handoff_origin": reselection_bridge.get("handoff_origin", ""),
                "suppressed_action_keys": ["next_primitive_touch"],
                "authority_match": False,
            }

    if winning_skill != "精确封口":
        _retain_shadow_program(
            payload,
            "current_读出_bite_if_any",
            shadow_key="suppressed_读出_bite_if_any",
            authority_touch=authority_touch,
        )


def cool_fresh_blind_initial_读出_shadow(payload: dict, *, state: dict) -> None:
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return
    if _normalize_text(bootstrap_context.get("mode")) != "fresh_blind_project_skills_on":
        return
    if isinstance(state.get("bound_program"), dict):
        return
    if isinstance(state.get("carrier_handoff_if_any"), dict):
        return
    if isinstance(state.get("layer_composition_if_any"), dict):
        return

    asked_medium = _normalize_text(state.get("asked_medium_surface"))
    if not asked_medium:
        return

    bridge = payload.get("skill_authority_bridge")
    executable = (
        bridge.get("executable_local_touch_if_any")
        if isinstance(bridge, dict)
        else None
    )
    if not isinstance(executable, dict):
        return

    target = _normalize_text(executable.get("target"))
    owner = _normalize_text(executable.get("owner_skill_if_any"))
    if target != asked_medium:
        return
    if owner not in {
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
    }:
        return

    payload["fresh_blind_first_step_guard"] = (
        "asked-medium 读出 stays cooled until one object-side layer has actually taken control"
    )
    payload.pop("current_读出_bite_if_any", None)
    payload.pop("suppressed_读出_bite_if_any", None)

    closure_nucleus = payload.get("closure_nucleus")
    if isinstance(closure_nucleus, dict):
        cooled_nucleus = dict(closure_nucleus)
        cooled_nucleus.pop("current_读出_bite_if_any", None)
        payload["closure_nucleus"] = cooled_nucleus

    if isinstance(bridge, dict):
        cooled_bridge = dict(bridge)
        cooled_bridge.pop("executable_local_touch_if_any", None)
        cooled_bridge["fresh_blind_first_step_suppressed"] = True
        payload["skill_authority_bridge"] = cooled_bridge


def should_quiet_for_authority(payload: dict) -> bool:
    bridge = payload.get("skill_authority_bridge")
    if isinstance(bridge, dict):
        executable = bridge.get("executable_local_touch_if_any")
        if isinstance(executable, dict) and _program_signature(executable) != ("", "", ""):
            return True
    discipline_contract = payload.get("discipline_contract")
    if isinstance(discipline_contract, dict):
        authorized = discipline_contract.get("authorized_bite")
        if isinstance(authorized, dict) and _program_signature(authorized) != ("", "", ""):
            return True
    interlayer = payload.get("interlayer_discharge_bridge")
    if isinstance(interlayer, dict):
        spend_first = interlayer.get("spend_first_program")
        if isinstance(spend_first, dict) and _program_signature(spend_first) != ("", "", ""):
            return True
    return False


def reorder_payload_authority_first(payload: dict) -> dict:
    ordered: dict = {}
    preferred = [
        "state_file",
        "consumed",
        "inspect_only",
        "surface",
        "layer_composition",
        "discipline_contract",
        "runtime_evidence",
        "ordinary_regrowth_forbidden",
        "inspect_noise_cooled",
        "authorized_bite_if_any",
        "resume_bridge",
        "skill_authority_bridge",
        "skill_lighting_surface",
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


def attach_discipline_contract(payload: dict, report: dict) -> dict:
    payload["discipline_contract"] = discipline_contract_from_report(report)
    return payload


def attach_runtime_evidence(payload: dict, state_path: Path) -> dict:
    payload["runtime_evidence"] = build_runtime_evidence(state_path)
    return payload


def active_contract_requires_runtime_evidence(payload: dict) -> bool:
    return contract_requires_runtime_evidence(
        payload.get("discipline_contract"),
        payload.get("runtime_evidence"),
        layer_composition=payload.get("layer_composition"),
        state=payload.get("_state"),
    )


def bootstrap_context_from_state(state: dict) -> dict:
    context = state.get("bootstrap_context")
    return context if isinstance(context, dict) else {}


def fresh_blind_project_skills_on_requires_transition(
    bootstrap_context: dict,
    runtime_evidence: dict,
) -> bool:
    return (
        _normalize_text(bootstrap_context.get("mode")) == "fresh_blind_project_skills_on"
        and bootstrap_context.get("requires_new_runtime_transition") is True
        and runtime_evidence.get("has_real_runtime_transition") is not True
    )


def autonomous_runtime_entry_enabled(bootstrap_context: dict) -> bool:
    return (
        _normalize_text(bootstrap_context.get("mode")) == "fresh_blind_project_skills_on"
        and bootstrap_context.get("auto_enter_local_action_when_concrete") is not False
    )


def _control_default_action(report: dict) -> str:
    layer_composition = _explicit_layer_composition(report)
    if layer_composition.get("must_spend_handoff") is True:
        return "spend_local"
    if layer_composition.get("must_bind_local_bite") is True:
        return "bind_local"
    control_bridge = report.get("control_bridge")
    if isinstance(control_bridge, dict):
        action = _normalize_text(control_bridge.get("default_local_action"))
        if action:
            return action
    reselection_bridge = report.get("reselection_bridge")
    if isinstance(reselection_bridge, dict):
        action = _normalize_text(reselection_bridge.get("default_local_action"))
        if action:
            return action
    return ""


def _concrete_authority_touch(report: dict) -> dict | None:
    composition_touch = _explicit_layer_composition(report).get("authorized_bite")
    if _program_signature(composition_touch) == ("", "", ""):
        composition_touch = None
    if composition_touch is not None:
        return composition_touch
    touch = _authority_touch(report)
    if _program_signature(touch) != ("", "", ""):
        return touch
    return None


def _append_transition_candidate(
    candidates: list[dict],
    action: str,
    *,
    reason: str,
    program: object = None,
) -> None:
    normalized_action = _normalize_text(action)
    normalized_reason = _normalize_text(reason)
    if not normalized_action or not normalized_reason:
        return
    for existing in candidates:
        if _normalize_text(existing.get("action")) == normalized_action:
            existing_reasons = existing.setdefault("reasons", [])
            if normalized_reason not in existing_reasons:
                existing_reasons.append(normalized_reason)
            if (
                isinstance(program, dict)
                and _program_signature(program) != ("", "", "")
                and not isinstance(existing.get("program"), dict)
            ):
                existing["program"] = program
            return
    entry = {
        "action": normalized_action,
        "reasons": [normalized_reason],
    }
    if isinstance(program, dict) and _program_signature(program) != ("", "", ""):
        entry["program"] = program
    candidates.append(entry)


def _resolve_transition_action(candidates: list[dict]) -> str:
    priority = {
        "spend_local": 0,
        "land_local": 1,
        "rebind_local_pressure": 2,
        "bind_local": 3,
    }
    ranked = sorted(
        (
            candidate
            for candidate in candidates
            if _normalize_text(candidate.get("action"))
        ),
        key=lambda candidate: priority.get(
            _normalize_text(candidate.get("action")),
            len(priority),
        ),
    )
    if not ranked:
        return ""
    return _normalize_text(ranked[0].get("action"))


def _distinct_concrete_programs(candidates: list[dict]) -> list[tuple[str, str, str]]:
    ordered: list[tuple[str, str, str]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        signature = _program_signature(candidate.get("program"))
        if signature == ("", "", "") or signature in ordered:
            continue
        ordered.append(signature)
    return ordered


def autonomous_transition_pressure(
    state: dict,
    report: dict,
    *,
    bootstrap_context: dict,
    runtime_evidence: dict,
) -> dict | None:
    if not autonomous_runtime_entry_enabled(bootstrap_context):
        return None

    trigger_signals: list[str] = []
    if fresh_blind_project_skills_on_requires_transition(
        bootstrap_context,
        runtime_evidence,
    ):
        trigger_signals.append("fresh_blind_requires_transition")

    takeover_gate = state.get("primitive_takeover_gate_if_any")
    if isinstance(takeover_gate, dict):
        trigger = _normalize_text(takeover_gate.get("trigger"))
        if trigger:
            trigger_signals.append(f"takeover_gate:{trigger}")

    probe_discipline = report.get("probe_discipline")
    if isinstance(probe_discipline, dict):
        if (
            probe_discipline.get("probe_must_bind") is True
            and probe_discipline.get("unbound_probe_is_drift") is True
        ):
            trigger_signals.append("probe_must_bind")
        active_hypothesis = _normalize_text(
            probe_discipline.get("active_skill_hypothesis")
        )
        if active_hypothesis:
            trigger_signals.append(f"active_hypothesis:{active_hypothesis}")

    discipline_contract = report.get("discipline_contract")
    if isinstance(discipline_contract, dict) and discipline_contract.get("active") is True:
        if _program_signature(discipline_contract.get("authorized_bite")) != ("", "", ""):
            trigger_signals.append("discipline_contract_authorized_bite")

    interlayer = report.get("interlayer_discharge_bridge")
    if isinstance(interlayer, dict) and _normalize_text(interlayer.get("mode")):
        trigger_signals.append(
            "interlayer:" + _normalize_text(interlayer.get("mode"))
        )

    default_action = _control_default_action(report)
    if default_action:
        trigger_signals.append(f"default_action:{default_action}")

    authority_touch = _concrete_authority_touch(report)
    explicit_handoff = isinstance(state.get("carrier_handoff_if_any"), dict)
    explicit_program = isinstance(state.get("bound_program"), dict)
    landed_touch = state.get("landed_next_touch_if_any")
    landed_concrete = isinstance(landed_touch, dict) and _program_signature(landed_touch) != ("", "", "")
    primitive_field = report.get("primitive_field")
    primitive_field_ready = (
        isinstance(primitive_field, dict)
        and isinstance(primitive_field.get("active_primitives"), list)
        and bool(
            [
                _normalize_text(value)
                for value in primitive_field.get("active_primitives", [])
                if _normalize_text(value)
            ]
        )
    )

    if not trigger_signals:
        return None
    if (
        authority_touch is None
        and not explicit_handoff
        and not landed_concrete
        and not explicit_program
    ):
        return None

    spend_handoff = explicit_handoff
    allow_handoff = bool(
        explicit_handoff
        or _normalize_text(default_action) == "rebind_local_pressure"
        or (
            isinstance(interlayer, dict)
            and _program_signature(interlayer.get("spend_first_program")) != ("", "", "")
        )
        or (
            isinstance(takeover_gate, dict)
            and _normalize_text(takeover_gate.get("trigger")) == "thinner_carrier_handoff"
        )
    )

    selected_target = (
        _normalize_text((authority_touch or {}).get("target"))
        or _normalize_text((landed_touch or {}).get("target"))
        or _normalize_text(
            ((discipline_contract or {}).get("authorized_bite", {}) or {}).get("target")
        )
    )
    layer_composition = _explicit_layer_composition(report)
    preferred_action = _preferred_action_from_layer_composition(layer_composition)
    pending_contract = pending_runtime_execution_contract(
        state,
        layer_composition=layer_composition,
    )
    contract_required_action = (
        _normalize_text(pending_contract.get("required_action"))
        if isinstance(pending_contract, dict)
        else ""
    )
    contract_authorized_bite = (
        pending_contract.get("authorized_bite")
        if isinstance(pending_contract, dict)
        and isinstance(pending_contract.get("authorized_bite"), dict)
        else None
    )
    candidate_actions: list[dict] = []
    if explicit_handoff:
        _append_transition_candidate(
            candidate_actions,
            "spend_local",
            reason="explicit_handoff_surface",
            program=state.get("carrier_handoff_if_any"),
        )
    if explicit_program and not explicit_handoff and contract_required_action:
        _append_transition_candidate(
            candidate_actions,
            contract_required_action,
            reason="bound_program_surface",
            program=contract_authorized_bite or state.get("bound_program"),
        )
    if authority_touch is not None:
        _append_transition_candidate(
            candidate_actions,
            "bind_local",
            reason="same_carrier_authority_touch",
            program=authority_touch,
        )
    if landed_concrete:
        _append_transition_candidate(
            candidate_actions,
            "bind_local",
            reason="landed_next_touch_available",
            program=landed_touch,
        )
    if allow_handoff and not authority_touch:
        handoff_program = None
        if isinstance(interlayer, dict):
            handoff_program = interlayer.get("spend_first_program")
        _append_transition_candidate(
            candidate_actions,
            "rebind_local_pressure",
            reason="thinner_carrier_handoff_reopened",
            program=handoff_program,
        )
    if default_action == "rebind_local_pressure":
        _append_transition_candidate(
            candidate_actions,
            "rebind_local_pressure",
            reason="control_bridge_default",
        )
    elif default_action:
        _append_transition_candidate(
            candidate_actions,
            "bind_local",
            reason="control_bridge_default",
        )

    concrete_programs = _distinct_concrete_programs(candidate_actions)
    if not concrete_programs:
        return None
    if len(concrete_programs) > 1:
        return None

    if preferred_action:
        _append_transition_candidate(
            candidate_actions,
            preferred_action,
            reason="layer_composition_execution_bit",
            program=layer_composition.get("authorized_bite"),
        )
        selected_action = contract_required_action or preferred_action
    else:
        selected_action = contract_required_action or _resolve_transition_action(candidate_actions)
    if not selected_action:
        return None

    return {
        "mode": "local_competition_disinhibition",
        "trigger_signals": trigger_signals,
        "reopened_competition": True,
        "candidate_actions": candidate_actions,
        "selected_action": selected_action,
        "selected_target": selected_target,
        "allow_handoff": allow_handoff,
        "spend_handoff": spend_handoff,
    }


def maybe_run_autonomous_transition(
    state_path: Path,
    *,
    state: dict,
    report: dict,
    bootstrap_context: dict,
    runtime_evidence: dict,
) -> tuple[dict, int] | None:
    pressure = autonomous_transition_pressure(
        state,
        report,
        bootstrap_context=bootstrap_context,
        runtime_evidence=runtime_evidence,
    )
    if pressure is None:
        return None

    pressure_view = {
        "mode": pressure.get("mode", ""),
        "trigger_signals": pressure.get("trigger_signals", []),
        "reopened_competition": pressure.get("reopened_competition") is True,
        "selected_target": pressure.get("selected_target", ""),
        "allow_handoff": pressure.get("allow_handoff") is True,
        "spend_handoff": pressure.get("spend_handoff") is True,
    }
    payload, exit_code = run_bind_local_once(
        state_path,
        allow_handoff=pressure["allow_handoff"],
        spend_handoff=pressure["spend_handoff"],
        allow_rival=False,
        previous_state=None,
    )
    payload["autonomous_transition"] = pressure_view
    return payload, exit_code


def build_fresh_blind_transition_refusal(
    state_path: Path,
    *,
    payload: dict,
    bootstrap_context: dict,
    runtime_evidence: dict,
    reason: str,
) -> tuple[dict, int]:
    refusal = {
        "state_file": str(state_path),
        "consumed": False,
        "inspect_only": True,
        "reason": reason,
        "bootstrap_context": bootstrap_context,
        "runtime_evidence": runtime_evidence,
        "warnings": payload.get("warnings", []) if isinstance(payload.get("warnings"), list) else [],
        "pending_transition": True,
        "runtime_transition_required": True,
        "trace_preview": render_runtime_skill_trace_markdown(state_path),
    }
    for key in [
        "surface",
        "layer_composition",
        "authorized_bite_if_any",
        "skill_lighting_surface",
        "allowed_transition_surfaces",
        "runtime_transition_watchdog",
    ]:
        if key in payload:
            refusal[key] = payload[key]
    return annotate_runtime_surface_payload(refusal, exit_code=1), 1


def build_runtime_evidence_refusal(state_path: Path, payload: dict) -> tuple[dict, int]:
    refusal = build_runtime_evidence_refusal_payload(
        state_path,
        discipline_contract=payload.get("discipline_contract", {}),
        resume_bridge=payload.get("resume_bridge", {}),
        warnings=payload.get("warnings", []),
        layer_composition=payload.get("layer_composition"),
        surface_payload=payload,
    )
    return refusal, 1


def _normalize_refusal_reason(reason: object) -> str:
    return _normalize_text(str(reason or "")).lower()


def _continuable_refusal_reason(normalized_reason: str) -> bool:
    return (
        "no unique local bite became concrete enough to bind" in normalized_reason
        or "no unique next primitive touch is concrete enough" in normalized_reason
        or "no unique thinner-carrier handoff is concrete enough" in normalized_reason
        or "unresolved rival is still live without a unique rival-local bite" in normalized_reason
        or "next same-carrier layer could not be inferred" in normalized_reason
        or "next same-carrier layer is identical to the current one" in normalized_reason
        or normalized_reason == "bind_once_structural_hop_limit_reached"
    )


def _completion_gap_snapshot(state: dict, report: dict) -> dict:
    resume_bridge = report.get("resume_bridge")
    if not isinstance(resume_bridge, dict):
        resume_bridge = {}

    output_status = state.get("output_status")
    final_artifact_materialized = (
        isinstance(output_status, dict)
        and output_status.get("touched") is True
        and output_status.get("final_artifact_materialized") is True
        and output_status.get("contains_unsupported") is not True
        and output_status.get("contains_placeholder") is not True
    )

    explicit_gap = (
        _normalize_text(resume_bridge.get("explicit_gap"))
        or _normalize_text(state.get("current_debt"))
        or _normalize_text(state.get("next_bite"))
    )
    next_local_choice = _normalize_text(resume_bridge.get("next_local_choice"))
    known_object = (
        _normalize_text(resume_bridge.get("known_object"))
        or _normalize_text(state.get("current_object"))
    )
    ask_surface = (
        _normalize_text(resume_bridge.get("ask_surface"))
        or _normalize_text(state.get("asked_medium_surface"))
    )
    same_carrier_preferred = resume_bridge.get("same_carrier_preferred")
    if not isinstance(same_carrier_preferred, bool):
        same_carrier_preferred = True

    control_signals = report.get("control_signals", {})
    meta_controls = (
        control_signals.get("meta_controls", {})
        if isinstance(control_signals, dict)
        else {}
    )
    micro_surface = (
        control_signals.get("micro_control_surface", {})
        if isinstance(control_signals, dict)
        else {}
    )
    layerwise_pressure = (
        control_signals.get("layerwise_reselection_pressure", {})
        if isinstance(control_signals, dict)
        else {}
    )

    supervisory_signals: list[str] = []
    if isinstance(meta_controls, dict):
        if isinstance(meta_controls.get("god_view"), dict) and meta_controls["god_view"].get("active") is True:
            supervisory_signals.append("god_view")
        if isinstance(meta_controls.get("后脑守卫"), dict) and meta_controls["后脑守卫"].get("active") is True:
            supervisory_signals.append("后脑守卫")
        if isinstance(meta_controls.get("supervisory_pulse"), dict) and meta_controls["supervisory_pulse"].get("active") is True:
            supervisory_signals.append("supervisory_pulse")
        if isinstance(meta_controls.get("反问"), dict) and meta_controls["反问"].get("active") is True:
            supervisory_signals.append("反问")
        if isinstance(meta_controls.get("closure_gate"), dict) and meta_controls["closure_gate"].get("active") is True:
            supervisory_signals.append("closure_gate")
    if isinstance(micro_surface, dict):
        if isinstance(micro_surface.get("监督_pulse"), dict) and micro_surface["监督_pulse"].get("active") is True:
            supervisory_signals.append("监督_pulse")
        if isinstance(micro_surface.get("反问"), dict) and micro_surface["反问"].get("active") is True:
            supervisory_signals.append("反问_surface")
    if isinstance(layerwise_pressure, dict) and layerwise_pressure.get("active") is True:
        supervisory_signals.append("layerwise_reselection_pressure")

    task_incomplete = (
        state.get("release_veto") is True
        and not final_artifact_materialized
        and bool(explicit_gap or next_local_choice or known_object or ask_surface)
    )
    thinner_carrier_due = (
        isinstance(resume_bridge, dict)
        and _normalize_text(resume_bridge.get("mode")) == "reopen_on_thinner_carrier"
        and not same_carrier_preferred
    )

    return {
        "task_incomplete": task_incomplete,
        "explicit_gap": explicit_gap,
        "next_local_choice": next_local_choice,
        "known_object": known_object,
        "ask_surface": ask_surface,
        "same_carrier_preferred": same_carrier_preferred,
        "thinner_carrier_due": thinner_carrier_due,
        "supervisory_signals": supervisory_signals,
        "supervisor_active": bool(supervisory_signals),
    }


def synthesize_execute_local_worked_step(
    state: dict,
    report: dict,
    *,
    strict: bool = False,
    prior_refusal_reason: str = "",
) -> tuple[str, str]:
    bound_program = state.get("bound_program")
    if not isinstance(bound_program, dict):
        return "", ""

    owner_skill = _normalize_text(bound_program.get("owner_skill_if_any")) or "当前技能"
    owner_combo = bound_program.get("owner_skill_combo_if_any")
    if isinstance(owner_combo, list):
        combo = [skill for skill in owner_combo if _normalize_text(skill)]
    else:
        combo = []
    combo_text = " + ".join(combo[:6]) if combo else owner_skill

    target = _normalize_text(bound_program.get("target")) or _normalize_text(state.get("current_seam"))
    operation = _normalize_text(bound_program.get("operation")) or _normalize_text(state.get("next_bite"))
    success_signal = _normalize_text(bound_program.get("success_signal")) or _normalize_text(state.get("current_debt"))
    current_debt = _normalize_text(state.get("current_debt"))
    current_seam = _normalize_text(state.get("current_seam"))
    retry_guidance = _execute_local_retry_guidance(
        prior_refusal_reason,
        owner_skill=owner_skill,
        combo=combo,
    )

    worked_step = (
        f"使用 {combo_text} 在当前层直接执行：围绕 `{target}` 去 {operation}；"
        f"把当前 seam `{current_seam or target}` 压成一个可见的 skill-owned touch，"
        f"并把成功信号压到 `{success_signal}`，而不是回到普通做法。"
    )
    if strict:
        primary_skill = retry_guidance["primary_skill"] or owner_skill
        supporting_skills = retry_guidance["supporting_skills"]
        refusal_kind = retry_guidance["refusal_kind"]
        ordinary_action = retry_guidance["ordinary_action"]

        denial_clause = "这一步不回到普通做法。"
        if refusal_kind == "ordinary_fallback" and ordinary_action:
            denial_clause = f"这一步先不要 `{ordinary_action}`，也不回到普通做法。"
        elif refusal_kind == "result_only":
            denial_clause = "这一步不只汇报“已经解决”，而是先写出当前层真正拥有的动作。"
        elif refusal_kind == "visible_skill":
            denial_clause = "这一步不要只报抽象结论，先把当前层技能动作写出来。"

        support_clause = ""
        if supporting_skills:
            support_text = "、".join(f"`{skill}`" for skill in supporting_skills)
            support_clause = (
                f"{support_text} 只作为 `{primary_skill}` 的同层支持或检查，不单独接管，也不长成普通动作。"
            )

        owned_action = (
            f"先让 `{primary_skill}` 在 `{target}` 上接管这一层，"
            f"把当前 seam `{current_seam or target}` 直接压向 `{success_signal}`。"
        )
        if refusal_kind == "generic" and operation:
            owned_action = f"先让 `{primary_skill}` 在 `{target}` 上接管这一层动作：{operation}。"

        worked_step = (
            f"{denial_clause}"
            f" {owned_action}"
            f" 当前技能组合是 {combo_text}，服务的当前层债务是 `{current_debt or success_signal}`。"
            f" 目标是在同一层把 `{success_signal}` 压成可见证据，而不是回到厚对象或只报结果。"
        )
        if support_clause:
            worked_step += f" {support_clause}"

    summary = (
        f"{retry_guidance['primary_skill'] or owner_skill} 接管 `{target}`，执行当前层动作并把成功信号压向 `{success_signal}`。"
    )
    return worked_step, summary


def _continuation_round_budget(state: dict, report: dict, *, required_action: str) -> int:
    budget = 1
    gap = _completion_gap_snapshot(state, report)
    if gap["task_incomplete"]:
        budget += 1
    if gap["supervisor_active"]:
        budget += 1
    if gap["thinner_carrier_due"] or required_action == "land_local":
        budget += 1
    return max(1, min(budget, 4))


def stalled_runtime_continuation(
    state: dict,
    report: dict,
    *,
    required_action: str,
    refusal_reason: str,
    transition_history: list[str],
) -> dict | None:
    if not isinstance(state, dict) or not isinstance(report, dict):
        return None
    if state.get("release_veto") is not True:
        return None

    normalized_reason = _normalize_refusal_reason(refusal_reason)
    if not _continuable_refusal_reason(normalized_reason):
        return None

    blocking = [
        problem
        for problem in report.get("problems", [])
        if problem != "bound_program is required while release_veto is active"
    ]
    if blocking:
        return None

    gap = _completion_gap_snapshot(state, report)
    if not gap["task_incomplete"]:
        return None

    trigger_signals = gap["supervisory_signals"][:]
    layer = report.get("layer_composition")
    if isinstance(layer, dict):
        if layer.get("active") is True:
            trigger_signals.append("active_layer")
        if layer.get("must_bind_local_bite") is True:
            trigger_signals.append("must_bind_local_bite")
        if layer.get("must_spend_handoff") is True:
            trigger_signals.append("must_spend_handoff")
    if not trigger_signals:
        if gap["explicit_gap"]:
            trigger_signals.append("unfinished_current_layer")
        if _normalize_text(state.get("current_seam")):
            trigger_signals.append("live_seam")
        if gap["next_local_choice"]:
            trigger_signals.append("supervisor_gap")

    if not trigger_signals:
        return None

    allowed_transition_surfaces = ["bind_local"]
    if required_action == "spend_local":
        allowed_transition_surfaces = ["spend_local", "bind_local"]
    elif isinstance(state.get("carrier_handoff_if_any"), dict):
        allowed_transition_surfaces = ["spend_local", "bind_local"]
    elif required_action in {"bind_local", "land_local"}:
        allowed_transition_surfaces = ["bind_local", "rebind_local_pressure"]
    if gap["same_carrier_preferred"] is False and "rebind_local_pressure" not in allowed_transition_surfaces:
        allowed_transition_surfaces.append("rebind_local_pressure")

    surface = (
        _normalize_text(layer.get("surface"))
        if isinstance(layer, dict)
        else ""
    ) or (
        "carrier_handoff" if isinstance(state.get("carrier_handoff_if_any"), dict) else "current_layer"
    )

    return {
        "active": True,
        "mode": "stalled_runtime_recompetition",
        "required_action": required_action or "bind_local",
        "refusal_reason": normalized_reason,
        "trigger_signals": trigger_signals,
        "allowed_transition_surfaces": allowed_transition_surfaces,
        "surface": surface,
        "completion_gap": {
            "explicit_gap": gap["explicit_gap"],
            "next_local_choice": gap["next_local_choice"],
            "known_object": gap["known_object"],
            "ask_surface": gap["ask_surface"],
            "same_carrier_preferred": gap["same_carrier_preferred"],
        },
    }


def reopen_stalled_local_competition(
    state_path: Path,
    *,
    continuation: dict,
) -> dict:
    def mutator(state: dict) -> None:
        if state.get("release_veto") is not True:
            return
        if (
            continuation.get("required_action") == "land_local"
            and isinstance(state.get("bound_program"), dict)
        ):
            state["bound_program"] = None
            state["layer_composition_if_any"] = None
            state["gate_binding_if_any"] = None
            state["landed_next_touch_if_any"] = None
            state["materialization_evidence"] = None
            output_status = state.get("output_status")
            if isinstance(output_status, dict):
                output_status["touched"] = False
                output_status["cosmetic_only"] = False
                output_status["contains_unsupported"] = False
                output_status["contains_placeholder"] = False
                output_status["final_artifact_materialized"] = False
            arm_primitive_takeover_gate(
                state,
                trigger="same_carrier_landing",
                note=(
                    "same-carrier landing stayed unfinished; reopen one stronger local "
                    "skill combination on the still-live task gap before ordinary continuation resumes"
                ),
            )
        state["primitive_competition_if_any"] = None
        state["primitive_field_if_any"] = None
        refresh_primitive_field_for_current_layer(state, force=True)

    state = mutate_state(
        state_path,
        mutator,
        command_name="continue-competing",
    )
    report = build_report(state, state_path)
    return {
        "mode": continuation.get("mode", "stalled_runtime_recompetition"),
        "required_action": continuation.get("required_action", ""),
        "refusal_reason": continuation.get("refusal_reason", ""),
        "trigger_signals": continuation.get("trigger_signals", []),
        "allowed_transition_surfaces": continuation.get(
            "allowed_transition_surfaces",
            [],
        ),
        "surface": continuation.get("surface", ""),
        "completion_gap": continuation.get("completion_gap", {}),
        "primitive_field": report.get("primitive_field", {}),
    }


def _attach_continuation_loop(
    payload: dict,
    *,
    transition_history: list[str],
    continuation_rounds_used: int,
    last_continuation: dict | None,
) -> dict:
    if not isinstance(payload, dict):
        return {}
    if continuation_rounds_used <= 0:
        return payload
    payload["continuation_loop"] = {
        "active": True,
        "rounds_used": continuation_rounds_used,
        "transition_history": transition_history[:],
    }
    if isinstance(last_continuation, dict):
        payload["continuation_loop"]["last_recompetition"] = last_continuation
    return payload


def write_trace_output(state_path: Path, output_path_text: str) -> None:
    state = load_state(state_path)
    output_path = resolve_state_relative_output_path(state_path, output_path_text)
    refusal = fresh_blind_generic_output_refusal(
        output_path,
        state=state,
        state_path=state_path,
        allow_asked_medium=False,
        allow_markdown_paths=[trace_markdown_path(state_path)],
    )
    if refusal:
        raise SystemExit(f"trace-output refused: {refusal}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_runtime_trace_markdown(state_path), encoding="utf-8")


def quiet_inspect_payload_for_active_contract(payload: dict, *, surface: str) -> None:
    payload["ordinary_regrowth_forbidden"] = True
    payload["inspect_noise_cooled"] = True
    payload["authorized_bite_if_any"] = payload.get("discipline_contract", {}).get(
        "authorized_bite", {}
    )
    bridge_summary = {}
    bridge = payload.get("skill_authority_bridge")
    if isinstance(bridge, dict):
        for key in [
            "winning_skill_if_any",
            "active_skill_combo_if_any",
            "supporting_skills_if_any",
        ]:
            value = bridge.get(key)
            if value not in (None, "", [], {}):
                bridge_summary[key] = value
        executable = bridge.get("executable_local_touch_if_any")
        if isinstance(executable, dict):
            bridge_summary["executable_local_touch_if_any"] = executable
    for key in [
        "skill_field",
        "skill_semantics",
        "skill_competition",
        "skill_competition_semantics",
        "skill_inhibition",
        "skill_authority_bridge",
        "skill_coaching_surface",
        "probe_discipline",
    ]:
        payload.pop(key, None)
    if bridge_summary:
        payload["skill_authority_bridge"] = bridge_summary

    if surface == "explicit_next_touch":
        payload["self_check_agenda"] = {}
        payload["competition_quieted"] = True
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
                "program_origin": control_bridge.get("program_origin", ""),
                "gate_binding": control_bridge.get("gate_binding", {}),
            }
    elif surface == "explicit_reselection":
        payload["self_check_agenda"] = {}
        payload["competition_quieted"] = True
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
                "handoff_origin": reselection_bridge.get("handoff_origin", ""),
                "handoff": reselection_bridge.get("handoff", {}),
                "warm_field": reselection_bridge.get("warm_field", {}),
            }
    cool_shortcut_fields(payload)


def strip_host_action_routing(payload: dict) -> None:
    control_bridge = payload.get("control_bridge")
    if isinstance(control_bridge, dict):
        filtered_control: dict = {}
        for key in ["program_origin", "gate_binding", "primitive_field"]:
            if key in control_bridge:
                filtered_control[key] = control_bridge[key]
        payload["control_bridge"] = filtered_control

    reselection_bridge = payload.get("reselection_bridge")
    if isinstance(reselection_bridge, dict):
        filtered_reselection: dict = {}
        for key in ["handoff_origin", "handoff", "warm_field", "closure_nucleus"]:
            if key in reselection_bridge:
                filtered_reselection[key] = reselection_bridge[key]
        payload["reselection_bridge"] = filtered_reselection


def build_inspect_surface(
    state_path: Path,
    *,
    allow_autonomous_transition: bool = False,
) -> tuple[dict, int]:
    state = load_json(state_path)
    report = build_report(state, state_path)
    bootstrap_context = bootstrap_context_from_state(state)
    bootstrap_autostart = autonomous_runtime_entry_enabled(bootstrap_context)
    deferred_bootstrap_problems = {
        "bound_program is required while release_veto is active",
    }

    if report["problems"] and not (
        bootstrap_autostart
        and set(report["problems"]).issubset(deferred_bootstrap_problems)
    ):
        payload = attach_discipline_contract({
            "state_file": str(state_path),
            "consumed": False,
            "reason": "invalid_state",
            "problems": report["problems"],
            "warnings": report["warnings"],
        }, report)
        payload = attach_runtime_evidence(payload, state_path)
        attach_runtime_transition_watchdog(payload, state=state)
        return payload, 2

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
        "_state": state,
        "surface": surface,
        "layer_composition": _host_visible_layer_composition(_explicit_layer_composition(report)),
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
        "skill_lighting_surface": _host_visible_skill_lighting_surface(report),
        "skill_coaching_surface": report.get("skill_coaching_surface", {}),
        "interlayer_discharge_bridge": report.get("interlayer_discharge_bridge", {}),
        "probe_discipline": report.get("probe_discipline", {}),
        "discipline_contract": discipline_contract_from_report(report),
        "resume_bridge": report.get("resume_bridge", {}),
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
        payload["current_读出_bite_if_any"] = closure_nucleus.get(
            "current_读出_bite_if_any", {}
        )
        payload["separating_check_if_any"] = closure_nucleus.get(
            "separating_check_if_any", ""
        )
    layer_composition = payload.get("layer_composition")
    if isinstance(layer_composition, dict):
        authorized_bite = layer_composition.get("authorized_bite")
        if isinstance(authorized_bite, dict) and _program_signature(authorized_bite) != ("", "", ""):
            payload["authorized_bite_if_any"] = authorized_bite
    cool_fresh_blind_initial_读出_shadow(payload, state=state)
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
    coaching_surface = payload.get("skill_coaching_surface")
    if isinstance(coaching_surface, dict):
        speech_acts = coaching_surface.get("speech_acts")
        if isinstance(speech_acts, dict) and not speech_acts:
            payload.pop("skill_coaching_surface", None)
    lighting_surface = payload.get("skill_lighting_surface")
    if isinstance(lighting_surface, dict) and not lighting_surface:
        payload.pop("skill_lighting_surface", None)
    strip_host_action_routing(payload)
    payload["bootstrap_context"] = bootstrap_context
    payload = attach_runtime_evidence(payload, state_path)
    attach_runtime_transition_watchdog(payload, state=state)
    cool_unqualified_skill_claims(
        payload,
        bootstrap_context=bootstrap_context,
        runtime_evidence=payload.get("runtime_evidence", {}),
    )
    if fresh_blind_project_skills_on_requires_transition(
        bootstrap_context,
        payload.get("runtime_evidence", {}),
    ) and (
        isinstance(payload.get("runtime_transition_watchdog"), dict)
        and payload["runtime_transition_watchdog"].get("expired") is True
    ):
        return build_fresh_blind_transition_refusal(
            state_path,
            payload=payload,
            bootstrap_context=bootstrap_context,
            runtime_evidence=payload.get("runtime_evidence", {}),
            reason="bootstrap_runtime_window_expired",
        )
    should_allow_autonomous_transition = (
        allow_autonomous_transition or bootstrap_autostart
    )
    if should_allow_autonomous_transition:
        transition_result = maybe_run_autonomous_transition(
            state_path,
            state=state,
            report=report,
            bootstrap_context=bootstrap_context,
            runtime_evidence=payload.get("runtime_evidence", {}),
        )
        if transition_result is not None:
            transition_payload, transition_code = transition_result
            transition_payload = attach_runtime_evidence(transition_payload, state_path)
            return transition_payload, transition_code
    if fresh_blind_project_skills_on_requires_transition(
        bootstrap_context,
        payload.get("runtime_evidence", {}),
    ):
        return build_fresh_blind_transition_refusal(
            state_path,
            payload=payload,
            bootstrap_context=bootstrap_context,
            runtime_evidence=payload.get("runtime_evidence", {}),
            reason=(
                "bootstrap_runtime_window_expired"
                if isinstance(payload.get("runtime_transition_watchdog"), dict)
                and payload["runtime_transition_watchdog"].get("expired") is True
                else "fresh_blind_project_skills_on_requires_new_runtime_transition"
            ),
        )
    pending_contract = pending_runtime_execution_contract(
        state,
        layer_composition=payload.get("layer_composition"),
    )
    if isinstance(pending_contract, dict):
        payload["pending_transition"] = True
        if (
            isinstance(payload.get("runtime_transition_watchdog"), dict)
            and payload["runtime_transition_watchdog"].get("expired") is True
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
        return build_runtime_evidence_refusal(state_path, payload)
    if active_contract_requires_runtime_evidence(payload):
        return build_runtime_evidence_refusal(state_path, payload)
    payload.pop("_state", None)
    payload = reorder_payload_authority_first(payload)
    return payload, 0


def run_bind_local_once(
    state_path: Path,
    allow_handoff: bool,
    spend_handoff: bool,
    allow_rival: bool,
    previous_state: str | None,
    worked_step: str | None = None,
    summary: str | None = None,
    output_file: str | None = None,
    cosmetic_only: bool | None = None,
    contains_unsupported: bool | None = None,
    contains_placeholder: bool | None = None,
) -> tuple[dict, int]:
    max_structural_hops = 4
    max_possible_continuation_rounds = 4

    def closed_payload(rebound_state: dict, *, binding_action: str) -> tuple[dict, int]:
        refreshed_report = build_report(rebound_state, state_path)
        payload = attach_discipline_contract({
            "state_file": str(state_path),
            "consumed": True,
            "inspect_only": False,
            "already_bound": False,
            "binding_action": binding_action,
            "primitive_field": refreshed_report.get("primitive_field", {}),
            "primitive_competition": refreshed_report.get("primitive_competition", {}),
            "warnings": refreshed_report["warnings"],
            "problems": refreshed_report["problems"],
        }, refreshed_report)
        payload = _attach_continuation_loop(
            payload,
            transition_history=transition_history,
            continuation_rounds_used=continuation_rounds_used,
            last_continuation=last_continuation,
        )
        return attach_runtime_evidence(payload, state_path), 0

    transition_history: list[str] = []
    continuation_rounds_used = 0
    last_continuation: dict | None = None
    execute_evidence_used = False
    iteration_budget = max_structural_hops + max_possible_continuation_rounds

    def maybe_continue(
        state: dict,
        report: dict,
        *,
        required_action: str,
        refusal_reason: str,
    ) -> bool:
        nonlocal continuation_rounds_used, last_continuation
        max_continuation_rounds = _continuation_round_budget(
            state,
            report,
            required_action=required_action,
        )
        if continuation_rounds_used >= max_continuation_rounds:
            return False
        continuation = stalled_runtime_continuation(
            state,
            report,
            required_action=required_action,
            refusal_reason=refusal_reason,
            transition_history=transition_history,
        )
        if not isinstance(continuation, dict):
            return False
        last_continuation = reopen_stalled_local_competition(
            state_path,
            continuation=continuation,
        )
        continuation_rounds_used += 1
        transition_history.append("continue_competing")
        return True

    for _ in range(iteration_budget):
        state = load_state(state_path)
        bootstrap_context = bootstrap_context_from_state(state)
        if state.get("release_veto") is False:
            final_report = build_report(state, state_path)
            if final_report.get("release_allowed") is True:
                binding_action = transition_history[-1] if transition_history else "materialized_closure"
                return closed_payload(rebound_state=state, binding_action=binding_action)
            payload = attach_discipline_contract({
                "state_file": str(state_path),
                "consumed": bool(transition_history),
                "inspect_only": False,
                "already_bound": False,
                "binding_action": "release_not_allowed",
                "reason": "release_veto dropped before the supervisor judged the task complete",
                "primitive_field": final_report.get("primitive_field", {}),
                "primitive_competition": final_report.get("primitive_competition", {}),
                "warnings": final_report["warnings"],
                "problems": final_report["problems"],
            }, final_report)
            if transition_history:
                payload["transition_history"] = transition_history[:]
            payload = _attach_continuation_loop(
                payload,
                transition_history=transition_history,
                continuation_rounds_used=continuation_rounds_used,
                last_continuation=last_continuation,
            )
            return attach_runtime_evidence(payload, state_path), 1

        report = build_report(state, state_path)
        effective_layer_composition = state.get("layer_composition_if_any")
        if not isinstance(effective_layer_composition, dict):
            report_layer_composition = report.get("layer_composition")
            if isinstance(report_layer_composition, dict):
                effective_layer_composition = report_layer_composition
        pending_contract = pending_runtime_execution_contract(
            state,
            layer_composition=effective_layer_composition,
        )
        required_action = (
            _normalize_text(pending_contract.get("required_action"))
            if isinstance(pending_contract, dict)
            else ""
        )
        primitive_field = report.get("primitive_field", {})
        primitive_competition = report.get("primitive_competition", {})

        if required_action == "execute_local":
            if worked_step and execute_evidence_used is not True:
                execute_error = None
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        command_execute_local(
                            argparse.Namespace(
                                state_file=str(state_path),
                                worked_step=worked_step,
                                summary=summary,
                                output_file=output_file,
                                cosmetic_only=cosmetic_only,
                                contains_unsupported=contains_unsupported,
                                contains_placeholder=contains_placeholder,
                            )
                        )
                except SystemExit as exc:
                    execute_error = str(exc)
                rebound_state = load_json(state_path)
                if rebound_state.get("release_veto") is False:
                    return closed_payload(
                        rebound_state,
                        binding_action="execute_local_closure",
                    )
                if execute_error is not None:
                    refreshed_report = build_report(rebound_state, state_path)
                    payload = attach_discipline_contract({
                        "state_file": str(state_path),
                        "consumed": False,
                        "inspect_only": False,
                        "already_bound": False,
                        "binding_action": "execute_local_refused",
                        "reason": execute_error,
                        "primitive_field": refreshed_report.get("primitive_field", {}),
                        "primitive_competition": refreshed_report.get(
                            "primitive_competition",
                            {},
                        ),
                        "warnings": refreshed_report["warnings"],
                        "problems": refreshed_report["problems"],
                    }, refreshed_report)
                    if transition_history:
                        payload["transition_history"] = transition_history[:]
                    payload = _attach_continuation_loop(
                        payload,
                        transition_history=transition_history,
                        continuation_rounds_used=continuation_rounds_used,
                        last_continuation=last_continuation,
                    )
                    return attach_runtime_evidence(payload, state_path), 1
                execute_evidence_used = True
                transition_history.append("execute_local")
                continue

            payload, exit_code = build_consumption(state_path)
            payload["consumed"] = bool(transition_history)
            payload["inspect_only"] = False
            payload["already_bound"] = False
            payload["binding_action"] = "pending_execute_local"
            payload["primitive_field"] = payload.get("primitive_field", primitive_field)
            payload["primitive_competition"] = payload.get(
                "primitive_competition",
                primitive_competition,
            )
            if transition_history:
                payload["transition_history"] = transition_history[:]
            payload = _attach_continuation_loop(
                payload,
                transition_history=transition_history,
                continuation_rounds_used=continuation_rounds_used,
                last_continuation=last_continuation,
            )
            return payload, exit_code

        if required_action == "materialize_asked_medium":
            materialize_error = None
            try:
                def materialize_mutator(materialize_state: dict) -> None:
                    if not materialize_asked_medium_if_ready(materialize_state, state_path=state_path):
                        raise SystemExit(
                            "materialize-asked-medium refused: asked-medium closure is not ready for runtime materialization"
                        )
                mutate_state(
                    state_path,
                    materialize_mutator,
                    command_name="materialize-asked-medium",
                )
            except SystemExit as exc:
                materialize_error = str(exc)
            rebound_state = load_json(state_path)
            refreshed_report = build_report(rebound_state, state_path)
            if rebound_state.get("release_veto") is False:
                return closed_payload(rebound_state, binding_action="materialize_asked_medium")
            payload = attach_discipline_contract({
                "state_file": str(state_path),
                "consumed": materialize_error is None,
                "inspect_only": False,
                "already_bound": False,
                "binding_action": (
                    "materialize_asked_medium_refused"
                    if materialize_error is not None
                    else "materialize_asked_medium_pending"
                ),
                "reason": materialize_error or "asked-medium closure remains live after materialization attempt",
                "primitive_field": refreshed_report.get("primitive_field", {}),
                "primitive_competition": refreshed_report.get("primitive_competition", {}),
                "warnings": refreshed_report["warnings"],
                "problems": refreshed_report["problems"],
            }, refreshed_report)
            if transition_history:
                payload["transition_history"] = transition_history[:]
            payload = _attach_continuation_loop(
                payload,
                transition_history=transition_history,
                continuation_rounds_used=continuation_rounds_used,
                last_continuation=last_continuation,
            )
            return attach_runtime_evidence(payload, state_path), 1 if materialize_error is not None else 0

        if not required_action:
            if isinstance(state.get("carrier_handoff_if_any"), dict):
                payload, exit_code = build_reselection_读出(state_path)
                payload["consumed"] = bool(transition_history)
                payload["inspect_only"] = False
                payload["already_bound"] = False
                payload["binding_action"] = (
                    transition_history[-1] if transition_history else "rebind_local_pressure"
                )
                payload["primitive_field"] = payload.get("primitive_field", primitive_field)
                payload["primitive_competition"] = payload.get(
                    "primitive_competition",
                    primitive_competition,
                )
                if transition_history:
                    payload["transition_history"] = transition_history[:]
                payload = _attach_continuation_loop(
                    payload,
                    transition_history=transition_history,
                    continuation_rounds_used=continuation_rounds_used,
                    last_continuation=last_continuation,
                )
                return payload, exit_code

            payload, exit_code = build_consumption(state_path)
            payload["consumed"] = bool(transition_history)
            payload["inspect_only"] = False
            payload["already_bound"] = False
            payload["binding_action"] = (
                transition_history[-1] if transition_history else "next_touch"
            )
            payload["primitive_field"] = payload.get("primitive_field", primitive_field)
            payload["primitive_competition"] = payload.get(
                "primitive_competition",
                primitive_competition,
            )
            if transition_history:
                payload["transition_history"] = transition_history[:]
            payload = _attach_continuation_loop(
                payload,
                transition_history=transition_history,
                continuation_rounds_used=continuation_rounds_used,
                last_continuation=last_continuation,
            )
            return payload, exit_code

        if required_action == "spend_local" and spend_handoff is not True:
            runtime_evidence = build_runtime_evidence(state_path)
            payload, _ = build_reselection_读出(state_path)
            payload["allowed_transition_surfaces"] = pending_contract.get(
                "allowed_transition_surfaces",
                ["spend_local"],
            )
            if isinstance(pending_contract.get("authorized_bite"), dict):
                payload["authorized_bite_if_any"] = pending_contract.get("authorized_bite")
            if transition_history:
                payload["transition_history"] = transition_history[:]
            return build_fresh_blind_transition_refusal(
                state_path,
                payload=payload,
                bootstrap_context=bootstrap_context,
                runtime_evidence=runtime_evidence,
                reason="bind_once_requires_explicit_spend_handoff",
            )

        if required_action == "bind_local":
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
                rebound_state = load_json(state_path)
                report = build_report(rebound_state, state_path)
                if maybe_continue(
                    rebound_state,
                    report,
                    required_action="bind_local",
                    refusal_reason=str(exc),
                ):
                    continue
                payload = attach_discipline_contract({
                    "state_file": str(state_path),
                    "consumed": False,
                    "inspect_only": False,
                    "binding_action": "refused",
                    "reason": str(exc),
                    "primitive_field": report.get("primitive_field", {}),
                    "primitive_competition": report.get("primitive_competition", {}),
                    "warnings": report["warnings"],
                    "problems": report["problems"],
                }, report)
                if transition_history:
                    payload["transition_history"] = transition_history[:]
                payload = _attach_continuation_loop(
                    payload,
                    transition_history=transition_history,
                    continuation_rounds_used=continuation_rounds_used,
                    last_continuation=last_continuation,
                )
                return attach_runtime_evidence(payload, state_path), code
            transition_history.append("bind_local")
            continue

        if required_action == "spend_local":
            spend_error = None
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    command_spend_local(argparse.Namespace(state_file=str(state_path)))
            except SystemExit as exc:
                spend_error = str(exc)
            rebound_state = load_json(state_path)
            if rebound_state.get("release_veto") is False:
                return closed_payload(rebound_state, binding_action="spend_local_closure")
            if spend_error is not None:
                refreshed_report = build_report(rebound_state, state_path)
                if maybe_continue(
                    rebound_state,
                    refreshed_report,
                    required_action="spend_local",
                    refusal_reason=spend_error,
                ):
                    continue
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
                if transition_history:
                    payload["transition_history"] = transition_history[:]
                payload = _attach_continuation_loop(
                    payload,
                    transition_history=transition_history,
                    continuation_rounds_used=continuation_rounds_used,
                    last_continuation=last_continuation,
                )
                return attach_runtime_evidence(payload, state_path), 1
            transition_history.append("spend_local")
            continue

        if required_action == "land_local":
            landing_error = None
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    command_land_local(
                        argparse.Namespace(
                            state_file=str(state_path),
                            current_object="",
                            current_seam="",
                            current_debt="",
                            next_bite="",
                        )
                    )
            except SystemExit as exc:
                landing_error = str(exc)
            rebound_state = load_json(state_path)
            refreshed_report = build_report(rebound_state, state_path)
            if rebound_state.get("release_veto") is False:
                return closed_payload(rebound_state, binding_action="land_local_closure")
            if landing_error is not None:
                if maybe_continue(
                    rebound_state,
                    refreshed_report,
                    required_action="land_local",
                    refusal_reason=landing_error,
                ):
                    continue
                payload = attach_discipline_contract({
                    "state_file": str(state_path),
                    "consumed": False,
                    "inspect_only": False,
                    "binding_action": "land_local_refused",
                    "reason": landing_error,
                    "primitive_field": refreshed_report.get("primitive_field", {}),
                    "primitive_competition": refreshed_report.get("primitive_competition", {}),
                    "warnings": refreshed_report["warnings"],
                    "problems": refreshed_report["problems"],
                }, refreshed_report)
                if transition_history:
                    payload["transition_history"] = transition_history[:]
                payload = _attach_continuation_loop(
                    payload,
                    transition_history=transition_history,
                    continuation_rounds_used=continuation_rounds_used,
                    last_continuation=last_continuation,
                )
                return attach_runtime_evidence(payload, state_path), 1
            transition_history.append("land_local")
            continue

    state = load_state(state_path)
    report = build_report(state, state_path)
    payload, exit_code = build_consumption(state_path)
    payload["consumed"] = bool(transition_history)
    payload["inspect_only"] = False
    payload["already_bound"] = False
    payload["binding_action"] = "structural_hop_limit"
    payload["reason"] = "bind_once_structural_hop_limit_reached"
    payload["primitive_field"] = payload.get("primitive_field", report.get("primitive_field", {}))
    payload["primitive_competition"] = payload.get(
        "primitive_competition",
        report.get("primitive_competition", {}),
    )
    if transition_history:
        payload["transition_history"] = transition_history[:]
    payload = _attach_continuation_loop(
        payload,
        transition_history=transition_history,
        continuation_rounds_used=continuation_rounds_used,
        last_continuation=last_continuation,
    )
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
        help="Allow one rival-local 见证 bind when the unique focus is already rival",
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
            "until at least one bind-local/spend-local event has really happened"
        ),
    )
    parser.add_argument(
        "--trace-output",
        help="Optional path to export the sidecar runtime trace markdown",
    )
    parser.add_argument(
        "--worked-step",
        help=(
            "Optional explicit execute-local evidence. "
            "When the live pending action is execute_local, the helper can consume "
            "this one worked step and continue the one-shot runtime loop."
        ),
    )
    parser.add_argument("--summary")
    parser.add_argument("--output-file")
    add_bool_argument(parser, "--cosmetic-only", "cosmetic_only")
    add_bool_argument(parser, "--contains-unsupported", "contains_unsupported")
    add_bool_argument(parser, "--contains-placeholder", "contains_placeholder")
    parser.add_argument(
        "--auto-transition",
        action="store_true",
        help=(
            "Allow inspect mode to actually execute one autonomous transition. "
            "By default inspect only exposes pressure/candidates and stays read-only, "
            "except for one-shot fresh-blind auto-entry when the live state already makes a unique local transition concrete."
        ),
    )
    args = parser.parse_args()

    state_path = Path(args.state_file)
    if args.bind_once is not True:
        payload, exit_code = build_inspect_surface(
            state_path,
            allow_autonomous_transition=args.auto_transition,
        )
    else:
        payload, exit_code = run_bind_local_once(
            state_path,
            allow_handoff=args.allow_handoff,
            spend_handoff=args.spend_handoff,
            allow_rival=args.allow_rival,
            previous_state=args.previous_state,
            worked_step=args.worked_step,
            summary=args.summary,
            output_file=args.output_file,
            cosmetic_only=args.cosmetic_only,
            contains_unsupported=args.contains_unsupported,
            contains_placeholder=args.contains_placeholder,
        )

    payload = attach_runtime_evidence(payload, state_path)
    if args.trace_output:
        write_trace_output(state_path, args.trace_output)
    if args.require_runtime_evidence and active_contract_requires_runtime_evidence(payload):
        payload, exit_code = build_runtime_evidence_refusal(state_path, payload)

    payload = annotate_runtime_surface_payload(payload, exit_code=exit_code)
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

