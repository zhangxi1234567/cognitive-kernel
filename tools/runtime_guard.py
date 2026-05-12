#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

ALLOWED_PRIMITIVES = {
    "symmetry",
    "limit_boundary",
    "conservation",
    "projection",
    "assignment",
    "reverse",
    "picture",
    "witness",
    "state_split",
    "compatibility",
    "readout",
    "vector_difference_readout",
    "common_value_compression",
    "container_to_cross_section",
    "area_to_line_readout",
    "matching_instead_of_probability",
    "grid_selection_permutation",
    "compare_without_calculating",
    "dot_product_projection",
    "canonical_normalization",
    "projection_readout",
    "dominant_mechanism_readout",
    "local_seam_controls_global",
    "definition_as_direct_readout",
    "symmetry_as_variable_killer",
    "boundary_as_route_finder",
    "model_calling_before_derivation",
    "special_value_probing",
    "function_archetype_matching",
}

ALLOWED_SKILLS = {
    *ALLOWED_PRIMITIVES,
    "grasp_essence",
    "final_owner",
    "shell_suspicion",
    "thinner_carrier_reselection",
    "exact_closure",
    "counter_question",
    "supervision",
    "metacognition",
    "central_control",
    "hindbrain_guard",
    "reward_penalty_shaping",
}

ALLOWED_RESIDUE_KINDS = {
    "competition_texture",
    "distrust_bias",
    "witness_readiness",
    "readout_sensitivity",
    "boundary_residue",
}

PROBE_LIKE_PRIMITIVES = {
    "witness",
    "assignment",
    "special_value_probing",
    "compare_without_calculating",
    "boundary_as_route_finder",
    "local_seam_controls_global",
    "limit_boundary",
    "symmetry",
    "symmetry_as_variable_killer",
}

READOUT_LIKE_PRIMITIVES = {
    "readout",
    "definition_as_direct_readout",
    "projection_readout",
    "dominant_mechanism_readout",
    "vector_difference_readout",
}

STRUCTURAL_WAKE_SKILLS = {
    "grasp_essence",
    "final_owner",
    "thinner_carrier_reselection",
    "exact_closure",
}

PRIMITIVE_ALIAS_GROUPS = {
    "symmetry": {
        "symmetry",
        "balance",
        "symmetrize the target",
        "quotient by symmetry",
    },
    "limit_boundary": {
        "limit boundary",
        "limit",
        "boundary",
        "degeneration",
        "edge case",
        "first crack",
        "tangency",
    },
    "conservation": {
        "conservation",
        "bookkeeping",
        "ledger",
        "aggregate controls target",
        "collapse to aggregate",
    },
    "projection": {
        "projection",
        "cross section",
        "project",
    },
    "assignment": {
        "assignment",
        "special value",
        "parameter compression",
        "anchor calibration",
    },
    "reverse": {
        "reverse",
        "reverse design",
    },
    "picture": {
        "picture",
        "diagram",
        "visual externalization",
    },
    "witness": {
        "witness",
        "separating check",
        "probe with witness",
    },
    "state_split": {
        "state split",
        "split",
        "quotient",
        "finite state",
        "exact cover",
        "freeze into static skeleton",
    },
    "compatibility": {
        "compatibility",
        "merge",
        "coexistence",
        "collapse to relation",
    },
    "readout": {
        "readout",
        "direct readout",
    },
    "vector_difference_readout": {
        "vector difference readout",
        "vector-difference-readout",
    },
    "common_value_compression": {
        "common value compression",
        "common-value-compression",
        "common value parameter compression",
        "common-value-parameter-compression",
        "collapse to latent controller",
        "latent controller",
    },
    "container_to_cross_section": {
        "container to cross section",
        "container-to-cross-section",
        "container to section",
    },
    "area_to_line_readout": {
        "area to line readout",
        "area-to-line-readout",
    },
    "matching_instead_of_probability": {
        "matching instead of probability",
        "matching-instead-of-probability",
    },
    "grid_selection_permutation": {
        "grid selection permutation",
        "grid-selection-permutation",
    },
    "compare_without_calculating": {
        "compare without calculating",
        "compare-without-calculating",
    },
    "dot_product_projection": {
        "dot product range by projection",
        "dot product projection",
    },
    "canonical_normalization": {
        "canonical normalization",
        "canonical-normalization",
        "normalize",
    },
    "projection_readout": {
        "projection readout",
        "projection-readout",
    },
    "dominant_mechanism_readout": {
        "dominant mechanism readout",
        "dominant-mechanism-readout",
    },
    "local_seam_controls_global": {
        "local seam controls global",
        "local-seam-controls-global",
    },
    "definition_as_direct_readout": {
        "definition as direct readout",
        "definition-as-direct-readout",
        "read out directly",
    },
    "symmetry_as_variable_killer": {
        "symmetry as variable killer",
        "symmetry-as-variable-killer",
    },
    "boundary_as_route_finder": {
        "boundary as route finder",
        "boundary-as-route-finder",
        "push to boundary",
    },
    "model_calling_before_derivation": {
        "model calling before derivation",
        "model-calling-before-derivation",
    },
    "special_value_probing": {
        "special value probing",
        "special-value-probing",
    },
    "function_archetype_matching": {
        "function archetype matching",
        "function-archetype-matching",
    },
}

SKILL_ALIAS_GROUPS = {
    "grasp_essence": {
        "grasp essence",
        "find essence",
        "抓本质",
    },
    "final_owner": {
        "final owner",
        "find final owner",
        "最终控制者",
        "找最终控制者",
    },
    "shell_suspicion": {
        "shell suspicion",
        "suspect the shell",
        "怀疑表面外壳",
    },
    "thinner_carrier_reselection": {
        "thinner carrier reselection",
        "find smaller carrier",
        "先找更小载体",
        "reselection",
    },
    "exact_closure": {
        "exact closure",
        "asked medium closure",
        "闭口",
        "精确封口",
    },
    "counter_question": {
        "counter question",
        "反问",
    },
    "supervision": {
        "supervision",
        "监督",
        "关门",
    },
    "metacognition": {
        "metacognition",
        "元认知",
    },
    "central_control": {
        "central control",
        "中枢",
    },
    "hindbrain_guard": {
        "hindbrain guard",
        "后脑",
    },
    "reward_penalty_shaping": {
        "reward penalty shaping",
        "吸引奖励和惩罚",
        "reward bias penalty bias",
    },
}


def normalize_primitive_token(value: object) -> str:
    if not isinstance(value, str):
        return ""
    lowered = value.strip().lower()
    if not lowered:
        return ""
    if lowered.startswith("primitive-") and lowered.endswith(".md"):
        lowered = lowered[len("primitive-") : -len(".md")]
    elif lowered.endswith(".md"):
        lowered = lowered[: -len(".md")]
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


PRIMITIVE_ALIAS_TO_CANONICAL = {}
for primitive in sorted(ALLOWED_PRIMITIVES):
    PRIMITIVE_ALIAS_TO_CANONICAL[normalize_primitive_token(primitive)] = primitive
    for alias in PRIMITIVE_ALIAS_GROUPS.get(primitive, set()):
        PRIMITIVE_ALIAS_TO_CANONICAL[normalize_primitive_token(alias)] = primitive

SKILL_ALIAS_TO_CANONICAL = {}
for skill in sorted(ALLOWED_SKILLS):
    SKILL_ALIAS_TO_CANONICAL[normalize_primitive_token(skill)] = skill
    for alias in SKILL_ALIAS_GROUPS.get(skill, set()):
        SKILL_ALIAS_TO_CANONICAL[normalize_primitive_token(alias)] = skill


def canonicalize_primitive_token(value: object) -> str:
    normalized = normalize_primitive_token(value)
    if not normalized:
        return ""
    return PRIMITIVE_ALIAS_TO_CANONICAL.get(normalized, "")


def is_allowed_primitive_token(value: object) -> bool:
    return canonicalize_primitive_token(value) in ALLOWED_PRIMITIVES


def canonicalize_skill_token(value: object) -> str:
    primitive = canonicalize_primitive_token(value)
    if primitive:
        return primitive
    normalized = normalize_primitive_token(value)
    if not normalized:
        return ""
    return SKILL_ALIAS_TO_CANONICAL.get(normalized, "")


RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"
PRIMITIVE_SEMANTICS_PATH = RUNTIME_DIR / "primitive_semantics.json"


@lru_cache(maxsize=1)
def load_primitive_semantics_registry() -> dict[str, dict]:
    try:
        payload = json.loads(PRIMITIVE_SEMANTICS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

    registry: dict[str, dict] = {}
    if not isinstance(payload, dict):
        return registry

    for primitive, semantics in payload.items():
        canonical = canonicalize_primitive_token(primitive)
        if canonical not in ALLOWED_PRIMITIVES or not isinstance(semantics, dict):
            continue
        registry[canonical] = semantics
    return registry


def get_primitive_semantics(primitive: object) -> dict:
    canonical = canonicalize_primitive_token(primitive)
    if not canonical:
        return {}
    semantics = load_primitive_semantics_registry().get(canonical, {})
    return semantics if isinstance(semantics, dict) else {}


def summarize_primitive_semantics(primitives: object) -> dict[str, dict]:
    if not isinstance(primitives, list):
        return {}
    summary: dict[str, dict] = {}
    for primitive in primitives:
        canonical = canonicalize_primitive_token(primitive)
        if canonical and canonical not in summary:
            semantics = get_primitive_semantics(canonical)
            if semantics:
                summary[canonical] = semantics
    return summary


CONTROL_SKILL_SEMANTICS = {
    "grasp_essence": {
        "family_type": "control",
        "mechanism": "Delete decorative burden until the smallest still-true controller becomes locally writable.",
        "controller_question": "What thinner, more honest controller would still survive if surface story were removed?",
        "wake_when": [
            "The run sounds descriptive but not compressive",
            "A prettier shell is replacing the live controller",
        ],
        "cheapest_honest_touch": "Rename one smaller controller and tie it to one exact local object or debt.",
        "anti_pattern": "Do not call something essence if it does not reduce the live burden now.",
    },
    "final_owner": {
        "family_type": "control",
        "mechanism": "Bias attention toward the last quantity, carrier, or interface that still has real authority over correctness.",
        "controller_question": "What still has the final right to preserve, reject, or cash out this line?",
        "wake_when": [
            "Several local truths remain but one final controller still decides release",
        ],
        "cheapest_honest_touch": "Name one exact owner and one event that would revoke it.",
        "anti_pattern": "Do not stop at a true local mechanism if a stronger final owner still governs release.",
    },
    "shell_suspicion": {
        "family_type": "control",
        "mechanism": "Keep suspicion on thick or beautiful carriers that still hide the smaller controller.",
        "controller_question": "What part of the current object is decorative shell rather than live controller?",
        "wake_when": [
            "The carrier still feels too thick",
            "A beautiful middle object is absorbing closure pressure",
        ],
        "cheapest_honest_touch": "Name one smaller carrier or seam that would kill the shell earliest.",
        "anti_pattern": "Do not destroy a carrier that still owns truth.",
    },
    "thinner_carrier_reselection": {
        "family_type": "control",
        "mechanism": "Move authority to a thinner carrier only when the same burden survives there more honestly.",
        "controller_question": "Would one thinner carrier keep the same controller while deleting fake burden?",
        "wake_when": [
            "Current carrier is too thick",
            "A local seam already points to a smaller residue",
        ],
        "cheapest_honest_touch": "Name one thinner target object and one winning pressure.",
        "anti_pattern": "Do not reseat authority just to sound deeper.",
    },
    "exact_closure": {
        "family_type": "control",
        "mechanism": "Force the live line to cash into exact asked-medium contact rather than near-miss commentary.",
        "controller_question": "What exact closure object or asked-medium readout is still unpaid?",
        "wake_when": [
            "Release is blocked by one concrete closure debt",
        ],
        "cheapest_honest_touch": "Write one exact readout or one executable local closure bite.",
        "anti_pattern": "Do not confuse closure-shaped language with closure.",
    },
    "counter_question": {
        "family_type": "control",
        "mechanism": "Keep one smallest hostile falsifier live before commentary regains comfort.",
        "controller_question": "What one cheap question could kill fake progress first?",
        "wake_when": [
            "Several nearby lines still feel plausible",
        ],
        "cheapest_honest_touch": "Write one separating witness or exact check.",
        "anti_pattern": "Do not multiply questions when one falsifier is enough.",
    },
    "supervision": {
        "family_type": "control",
        "mechanism": "Temporarily demote drift so one local owner can keep authority until change or kill.",
        "controller_question": "What continuation should lose permission until one local event lands?",
        "wake_when": [
            "Language is outrunning object change",
        ],
        "cheapest_honest_touch": "Name one owner, one demoted continuation, and one gate-until event.",
        "anti_pattern": "Do not turn supervision into a phase machine.",
    },
    "metacognition": {
        "family_type": "control",
        "mechanism": "Re-check owner, carrier, and false essence while keeping the live object small.",
        "controller_question": "What if the current owner or carrier label is slightly wrong?",
        "wake_when": [
            "Control surfaces feel aligned but not yet honest",
        ],
        "cheapest_honest_touch": "Re-name one owner/carrier pair and test whether burden shrinks.",
        "anti_pattern": "Do not reopen broad reflection after the local closure body is already concrete.",
    },
    "central_control": {
        "family_type": "control",
        "mechanism": "Bias one local owner strongly enough that nearby lines cool until an actual tear event occurs.",
        "controller_question": "Who currently owns the slot?",
        "wake_when": [
            "Several lines still feel equally foregrounded",
        ],
        "cheapest_honest_touch": "Bind one owner and one revocation handle.",
        "anti_pattern": "Do not centralize what still needs real plurality.",
    },
    "hindbrain_guard": {
        "family_type": "control",
        "mechanism": "Keep the non-release latch alive and reopen the smallest honest exit when false settlement appears.",
        "controller_question": "What should stop this line from settling too early?",
        "wake_when": [
            "The run is near premature settlement",
        ],
        "cheapest_honest_touch": "Keep one non-release condition explicit on the current layer.",
        "anti_pattern": "Do not keep the guard on after honest materialization has landed.",
    },
    "reward_penalty_shaping": {
        "family_type": "control",
        "mechanism": "Shape local attraction and aversion so better touches feel cheaper than decorative continuation.",
        "controller_question": "What move should feel more attractive, and what drift should feel more expensive, right now?",
        "wake_when": [
            "The line knows enough but still drifts",
        ],
        "cheapest_honest_touch": "Expose one promoted move type and one demoted continuation type.",
        "anti_pattern": "Do not treat reward shaping as a substitute for object-side truth.",
    },
}


def get_skill_semantics(skill: object) -> dict:
    canonical = canonicalize_skill_token(skill)
    if not canonical:
        return {}
    if canonical in ALLOWED_PRIMITIVES:
        return get_primitive_semantics(canonical)
    return CONTROL_SKILL_SEMANTICS.get(canonical, {})


def summarize_skill_semantics(skills: object) -> dict[str, dict]:
    if not isinstance(skills, list):
        return {}
    summary: dict[str, dict] = {}
    for skill in skills:
        canonical = canonicalize_skill_token(skill)
        if canonical and canonical not in summary:
            semantics = get_skill_semantics(canonical)
            if semantics:
                summary[canonical] = semantics
    return summary


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing state file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in {path}: {exc}")


def require_nonempty(state: dict, key: str, problems: list[str]) -> None:
    value = state.get(key)
    if not isinstance(value, str) or not value.strip():
        problems.append(f"{key} is missing or empty")


def nonempty_text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def validate_no_extra_keys(
    obj: dict, allowed_keys: set[str], label: str, problems: list[str]
) -> None:
    for key in obj.keys():
        if key not in allowed_keys:
            problems.append(f"{label} has unexpected key: {key}")


def validate_bound_program(state: dict, problems: list[str]) -> None:
    bound_program = state.get("bound_program")
    if bound_program is None:
        if state.get("release_veto") is True:
            problems.append("bound_program is required while release_veto is active")
        return

    if not isinstance(bound_program, dict):
        problems.append("bound_program must be an object or null")
        return

    validate_no_extra_keys(
        bound_program,
        {"kind", "target", "operation", "success_signal"},
        "bound_program",
        problems,
    )

    for key in ["kind", "target", "operation"]:
        require_nonempty(bound_program, key, problems)

    kind = bound_program.get("kind")
    if isinstance(kind, str) and kind not in {"write", "check", "readout", "witness"}:
        problems.append("bound_program.kind must be write, check, readout, or witness")

    success_signal = bound_program.get("success_signal")
    if success_signal is not None and (
        not isinstance(success_signal, str) or not success_signal.strip()
    ):
        problems.append("bound_program.success_signal must be non-empty when present")


def validate_gate_binding(state: dict, problems: list[str]) -> None:
    gate_binding = state.get("gate_binding_if_any")
    if gate_binding is None:
        return

    if not isinstance(gate_binding, dict):
        problems.append("gate_binding_if_any must be an object or null")
        return

    validate_no_extra_keys(
        gate_binding,
        {"source_focus", "source_target", "demoted_continuation", "authority_until", "owner_skill_if_any"},
        "gate_binding_if_any",
        problems,
    )

    for key in ["source_focus", "source_target", "demoted_continuation", "authority_until"]:
        require_nonempty(gate_binding, key, problems)

    source_focus = gate_binding.get("source_focus")
    if isinstance(source_focus, str) and source_focus not in {"seam", "rival", "carrier", "asked_medium"}:
        problems.append("gate_binding_if_any.source_focus must be seam, rival, carrier, or asked_medium")

    authority_until = gate_binding.get("authority_until")
    if isinstance(authority_until, str) and authority_until not in {
        "same_carrier_change",
        "hostile_witness",
        "exact_check",
        "asked_medium_failure",
    }:
        problems.append(
            "gate_binding_if_any.authority_until must be same_carrier_change, "
            "hostile_witness, exact_check, or asked_medium_failure"
        )

    owner_skill = gate_binding.get("owner_skill_if_any")
    if owner_skill is not None:
        canonical = canonicalize_skill_token(owner_skill)
        if not canonical:
            problems.append("gate_binding_if_any.owner_skill_if_any must be one of the allowed skills when present")


def validate_materialization_evidence(state: dict, problems: list[str]) -> None:
    evidence = state.get("materialization_evidence")
    if evidence is None:
        return

    if not isinstance(evidence, dict):
        problems.append("materialization_evidence must be an object or null")
        return

    validate_no_extra_keys(
        evidence,
        {"kind", "location", "summary"},
        "materialization_evidence",
        problems,
    )
    for key in ["kind", "location", "summary"]:
        require_nonempty(evidence, key, problems)

    kind = evidence.get("kind")
    if isinstance(kind, str) and kind not in {"file", "command", "check", "artifact"}:
        problems.append(
            "materialization_evidence.kind must be file, command, check, or artifact"
        )


def validate_current_seam(state: dict, problems: list[str]) -> None:
    value = state.get("current_seam")
    if value is None or value == "":
        return
    if not isinstance(value, str) or not value.strip():
        problems.append("current_seam must be a non-empty string when present")


def validate_primitive_competition(state: dict, problems: list[str]) -> None:
    competition = state.get("primitive_competition_if_any")
    if competition is None:
        return

    if not isinstance(competition, dict):
        problems.append("primitive_competition_if_any must be an object or null")
        return

    validate_no_extra_keys(
        competition,
        {"layer_object", "candidates", "separating_check", "winner_if_any"},
        "primitive_competition_if_any",
        problems,
    )

    require_nonempty(competition, "layer_object", problems)

    candidates = competition.get("candidates")
    if not isinstance(candidates, list):
        problems.append("primitive_competition_if_any.candidates must be an array")
    else:
        if not 1 <= len(candidates) <= 2:
            problems.append(
                "primitive_competition_if_any.candidates must contain 1 or 2 entries"
            )
        primitives_seen: set[str] = set()
        for idx, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                problems.append(f"primitive_competition_if_any.candidates[{idx}] must be an object")
                continue
            validate_no_extra_keys(
                candidate,
                {"primitive", "touch_target", "expected_local_gain"},
                f"primitive_competition_if_any.candidates[{idx}]",
                problems,
            )
            require_nonempty(candidate, "primitive", problems)
            require_nonempty(candidate, "touch_target", problems)
            require_nonempty(candidate, "expected_local_gain", problems)
            primitive = canonicalize_primitive_token(candidate.get("primitive"))
            if primitive not in ALLOWED_PRIMITIVES:
                problems.append(
                    "primitive_competition_if_any.candidates"
                    f"[{idx}].primitive must be one of: {', '.join(sorted(ALLOWED_PRIMITIVES))}"
                )
            elif primitive in primitives_seen:
                problems.append(
                    f"primitive_competition_if_any.candidates[{idx}].primitive duplicates an earlier candidate"
                )
            else:
                primitives_seen.add(primitive)

    separating_check = competition.get("separating_check")
    if separating_check is not None and (
        not isinstance(separating_check, str) or not separating_check.strip()
    ):
        problems.append(
            "primitive_competition_if_any.separating_check must be non-empty when present"
        )

    winner = competition.get("winner_if_any")
    if winner is None:
        return
    winner = canonicalize_primitive_token(winner)
    if winner not in ALLOWED_PRIMITIVES:
        problems.append(
            "primitive_competition_if_any.winner_if_any must be one of the allowed primitives when present"
        )
        return
    if isinstance(candidates, list):
        candidate_primitives = {
            canonicalize_primitive_token(candidate.get("primitive"))
            for candidate in candidates
            if isinstance(candidate, dict) and canonicalize_primitive_token(candidate.get("primitive"))
        }
        if winner not in candidate_primitives:
            problems.append(
                "primitive_competition_if_any.winner_if_any must match one of the candidate primitives"
            )


def validate_primitive_field(state: dict, problems: list[str]) -> None:
    primitive_field = state.get("primitive_field_if_any")
    if primitive_field is None:
        return

    if not isinstance(primitive_field, dict):
        problems.append("primitive_field_if_any must be an object or null")
        return

    validate_no_extra_keys(
        primitive_field,
        {
            "layer_object",
            "active_primitives",
            "tie_break_check",
            "why_now",
            "selection_basis",
            "evidence_basis",
        },
        "primitive_field_if_any",
        problems,
    )

    require_nonempty(primitive_field, "layer_object", problems)
    require_nonempty(primitive_field, "why_now", problems)

    active_primitives = primitive_field.get("active_primitives")
    if not isinstance(active_primitives, list):
        problems.append("primitive_field_if_any.active_primitives must be an array")
    else:
        if not 1 <= len(active_primitives) <= 2:
            problems.append(
                "primitive_field_if_any.active_primitives must contain 1 or 2 entries"
            )
        for idx, value in enumerate(active_primitives):
            if canonicalize_primitive_token(value) not in ALLOWED_PRIMITIVES:
                problems.append(
                    "primitive_field_if_any.active_primitives"
                    f"[{idx}] must be one of: {', '.join(sorted(ALLOWED_PRIMITIVES))}"
                )

    tie_break_check = primitive_field.get("tie_break_check")
    if tie_break_check is not None and (
        not isinstance(tie_break_check, str) or not tie_break_check.strip()
    ):
        problems.append(
            "primitive_field_if_any.tie_break_check must be non-empty when present"
        )

    selection_basis = primitive_field.get("selection_basis")
    if selection_basis is not None and (
        not isinstance(selection_basis, str)
        or selection_basis
        not in {"explicit_hint", "tie_break", "agenda_hint", "text_fallback"}
    ):
        problems.append(
            "primitive_field_if_any.selection_basis must be explicit_hint, tie_break, "
            "agenda_hint, or text_fallback when present"
        )

    evidence_basis = primitive_field.get("evidence_basis")
    if evidence_basis is not None and (
        not isinstance(evidence_basis, str)
        or evidence_basis
        not in {"explicit_hint", "state_witness", "cheap_check", "lexical_hint", "mixed"}
    ):
        problems.append(
            "primitive_field_if_any.evidence_basis must be explicit_hint, state_witness, "
            "cheap_check, lexical_hint, or mixed when present"
        )


def expected_layer_object(
    state: dict,
    agenda_override: dict | None = None,
    handoff_override: dict | None = None,
    *,
    derive_agenda: bool = True,
) -> str:
    handoff = handoff_override if handoff_override is not None else state.get("carrier_handoff_if_any")
    if isinstance(handoff, dict):
        return (
            nonempty_text(handoff.get("to_object"))
            or nonempty_text(state.get("current_seam"))
            or nonempty_text(state.get("current_object"))
        )

    agenda = agenda_override
    if agenda is None and derive_agenda:
        agenda = derive_self_check_agenda(state, [])

    return (
        nonempty_text(state.get("current_seam"))
        or (nonempty_text(agenda.get("touch_target")) if isinstance(agenda, dict) else "")
        or nonempty_text(state.get("current_object"))
    )


def _gap_object_looks_explicit(
    candidate: str,
    *,
    current_object: str = "",
    current_seam: str = "",
    asked_medium: str = "",
) -> bool:
    normalized = normalize_primitive_token(candidate)
    if not normalized:
        return False

    banned_targets = {
        normalize_primitive_token(current_object),
        normalize_primitive_token(current_seam),
        normalize_primitive_token(asked_medium),
    }
    if normalized in banned_targets:
        return False

    if len(normalized.split()) > 12:
        return False

    blocked_prefixes = (
        "need ",
        "needs ",
        "write ",
        "materialize ",
        "touch ",
        "probe ",
        "check ",
        "find ",
        "derive ",
        "confirm ",
        "verify ",
        "bind ",
        "rebind ",
        "spend ",
        "show ",
        "compute ",
    )
    if any(normalized.startswith(prefix) for prefix in blocked_prefixes):
        return False

    blocked_phrases = (
        "same carrier",
        "asked medium",
        "next touch",
        "better wording",
        "final artifact",
        "release veto",
    )
    if any(phrase in normalized for phrase in blocked_phrases):
        return False

    object_keywords = (
        "coupling",
        "compat",
        "merge",
        "residue",
        "assignment",
        "budget",
        "boundary",
        "split",
        "state",
        "quotient",
        "chain",
        "bucket",
        "witness",
        "carrier",
        "axis",
        "constraint",
        "law",
        "readout",
        "certificate",
        "interface",
        "object",
        "field",
        "surface",
    )
    if any(keyword in normalized for keyword in object_keywords):
        return True

    blocked_verbs = (
        "need",
        "write",
        "materialize",
        "touch",
        "probe",
        "check",
        "find",
        "derive",
        "confirm",
        "verify",
        "bind",
        "rebind",
        "spend",
        "show",
        "compute",
    )
    return not any(f" {verb} " in f" {normalized} " for verb in blocked_verbs)


def derive_gap_object(
    state: dict,
    *,
    closure_nucleus_override: dict | None = None,
) -> dict | None:
    current_object = nonempty_text(state.get("current_object"))
    current_seam = nonempty_text(state.get("current_seam"))
    asked_medium = nonempty_text(state.get("asked_medium_surface"))

    closure_nucleus = closure_nucleus_override
    debt_text = ""
    if isinstance(closure_nucleus, dict):
        debt_text = nonempty_text(closure_nucleus.get("debt"))
    if not debt_text:
        debt_text = nonempty_text(state.get("current_debt")) or nonempty_text(state.get("next_bite"))
    if not debt_text:
        return None

    candidates: list[str] = []
    direct = debt_text.strip()
    if direct:
        candidates.append(direct)

    lowered = normalize_primitive_token(direct)
    lead_patterns = ["need ", "needs ", "missing ", "lack of ", "unpaid "]
    remainder = ""
    for prefix in lead_patterns:
        if lowered.startswith(prefix):
            remainder = direct[len(prefix):].strip(" .,:;")
            break

    for splitter in [" of ", " for ", " around ", " about ", " between ", " under "]:
        if remainder:
            lowered_remainder = remainder.lower()
            if splitter in lowered_remainder:
                idx = lowered_remainder.find(splitter)
                left = remainder[:idx]
                right = remainder[idx + len(splitter):]
                if left.strip():
                    candidates.append(left.strip(" .,:;"))
                if right.strip():
                    candidates.append(right.strip(" .,:;"))

    for splitter in [" in ", " on ", " at ", " into "]:
        if remainder:
            lowered_remainder = remainder.lower()
            if splitter in lowered_remainder:
                idx = lowered_remainder.find(splitter)
                left = remainder[:idx]
                right = remainder[idx + len(splitter):]
                if left.strip():
                    candidates.append(left.strip(" .,:;"))
                if right.strip():
                    candidates.append(right.strip(" .,:;"))

    if remainder:
        candidates.append(remainder)

    chosen = ""
    for candidate in candidates:
        if _gap_object_looks_explicit(
            candidate,
            current_object=current_object,
            current_seam=current_seam,
            asked_medium=asked_medium,
        ):
            chosen = candidate.strip()
            break

    if not chosen:
        return None

    primitive_hints = infer_primitives_from_text(chosen, debt_text, current_seam)
    cheap_check = ""
    if chosen != current_seam and current_seam:
        cheap_check = f"compress {current_seam} into the missing object {chosen}"
    elif chosen != current_object and current_object:
        cheap_check = f"name one same-carrier bite on {chosen}"
    else:
        cheap_check = f"touch {chosen}"

    return {
        "object": chosen,
        "source_debt": debt_text,
        "why_local": (
            "the current unpaid debt is explicit enough to become one smaller live object"
        ),
        "cheap_check": cheap_check,
        "primitive_hints": primitive_hints[:2],
        "inherits_authority": True,
    }


def derive_resume_bridge(
    state: dict,
    *,
    closure_nucleus_override: dict | None = None,
    gap_object_override: dict | None = None,
    reselection_bridge_override: dict | None = None,
    skill_field_override: dict | None = None,
) -> dict | None:
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt")) or nonempty_text(state.get("next_bite"))
    if not (asked_medium or current_object or current_debt):
        return None

    closure_nucleus = closure_nucleus_override
    gap_object = gap_object_override
    reselection_bridge = reselection_bridge_override
    skill_field = skill_field_override

    same_carrier_bite = ""
    if isinstance(closure_nucleus, dict):
        bite = closure_nucleus.get("current_structural_bite_if_any")
        if isinstance(bite, dict):
            same_carrier_bite = nonempty_text(bite.get("target")) or nonempty_text(bite.get("operation"))

    thinner_target = ""
    if isinstance(reselection_bridge, dict):
        handoff = reselection_bridge.get("handoff")
        if isinstance(handoff, dict):
            thinner_target = nonempty_text(handoff.get("to_object"))

    gap_target = ""
    if isinstance(gap_object, dict):
        gap_target = nonempty_text(gap_object.get("object"))

    supporting_skills: list[str] = []
    if isinstance(skill_field, dict):
        full_skills = skill_field.get("full_active_skills")
        if isinstance(full_skills, list) and full_skills:
            supporting_skills = [
                canonicalize_skill_token(skill)
                for skill in full_skills
                if canonicalize_skill_token(skill)
            ]
        elif isinstance(skill_field.get("active_skills"), list):
            supporting_skills = [
                canonicalize_skill_token(skill)
                for skill in skill_field.get("active_skills", [])
                if canonicalize_skill_token(skill)
            ]
    if not supporting_skills and isinstance(gap_object, dict):
        supporting_skills = [
            canonicalize_skill_token(skill)
            for skill in gap_object.get("primitive_hints", [])
            if canonicalize_skill_token(skill)
        ]

    mode = "continue_same_carrier"
    if thinner_target and thinner_target != current_object:
        mode = "reopen_on_thinner_carrier"

    why_now = (
        "rebind the ask, the strongest still-true current object, and the explicit gap before choosing whether to continue locally or reseat on a thinner carrier"
    )
    next_local_choice = same_carrier_bite or thinner_target or gap_target or current_object or asked_medium
    if mode == "reopen_on_thinner_carrier":
        why_now = (
            f"the same explicit gap now survives more honestly on thinner carrier {thinner_target}"
        )
    elif same_carrier_bite:
        why_now = (
            f"the current ask/object/debt triple still cashes into one same-carrier bite on {same_carrier_bite}"
        )

    return {
        "ask_surface": asked_medium,
        "known_object": current_object,
        "explicit_gap": gap_target or current_debt,
        "mode": mode,
        "next_local_choice": next_local_choice,
        "why_now": why_now,
        "supporting_skills": supporting_skills[:5],
        "same_carrier_preferred": mode == "continue_same_carrier",
    }


def primitive_field_is_stale(
    state: dict,
    primitive_field_override: dict | None = None,
    agenda_override: dict | None = None,
    handoff_override: dict | None = None,
) -> bool:
    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    if not isinstance(primitive_field, dict):
        return False

    layer_object = nonempty_text(primitive_field.get("layer_object"))
    expected_object = expected_layer_object(
        state,
        agenda_override=agenda_override,
        handoff_override=handoff_override,
        derive_agenda=agenda_override is not None,
    )
    return bool(layer_object and expected_object and layer_object != expected_object)


def primitive_competition_is_stale(
    state: dict,
    competition_override: dict | None = None,
    agenda_override: dict | None = None,
    handoff_override: dict | None = None,
) -> bool:
    competition = (
        competition_override
        if competition_override is not None
        else state.get("primitive_competition_if_any")
    )
    if not isinstance(competition, dict):
        return False

    layer_object = nonempty_text(competition.get("layer_object"))
    expected_object = expected_layer_object(
        state,
        agenda_override=agenda_override,
        handoff_override=handoff_override,
        derive_agenda=agenda_override is not None,
    )
    return bool(layer_object and expected_object and layer_object != expected_object)


def derive_primitives_from_competition(
    competition: dict,
) -> tuple[list[str], str | None, str]:
    candidates = competition.get("candidates")
    winner = canonicalize_primitive_token(competition.get("winner_if_any"))
    separating_check = nonempty_text(competition.get("separating_check"))
    if not isinstance(candidates, list):
        return [], separating_check or None, "explicit_hint"

    ordered: list[str] = []
    if winner:
        ordered.append(winner)
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        primitive = canonicalize_primitive_token(candidate.get("primitive"))
        if primitive and primitive not in ordered:
            ordered.append(primitive)
        if len(ordered) == 2:
            break
    basis = "tie_break" if winner or (len(ordered) > 1 and separating_check) else "explicit_hint"
    return ordered[:2], separating_check or None, basis


def validate_carrier_handoff(state: dict, problems: list[str]) -> None:
    handoff = state.get("carrier_handoff_if_any")
    if handoff is None:
        return

    if not isinstance(handoff, dict):
        problems.append("carrier_handoff_if_any must be an object or null")
        return

    validate_no_extra_keys(
        handoff,
        {
            "trigger",
            "from_slot",
            "to_object",
            "winning_pressure",
            "cooled_pressure_if_any",
            "why_local",
            "warm_field",
        },
        "carrier_handoff_if_any",
        problems,
    )

    for key in ["trigger", "from_slot", "to_object", "winning_pressure", "why_local"]:
        require_nonempty(handoff, key, problems)

    trigger = handoff.get("trigger")
    if isinstance(trigger, str) and trigger not in {
        "same_carrier_change",
        "hostile_witness",
        "exact_check",
        "asked_medium_failure",
        "residue_inherited",
    }:
        problems.append(
            "carrier_handoff_if_any.trigger must be same_carrier_change, "
            "hostile_witness, exact_check, asked_medium_failure, or residue_inherited"
        )

    cooled = handoff.get("cooled_pressure_if_any")
    if cooled is not None and (not isinstance(cooled, str) or not cooled.strip()):
        problems.append(
            "carrier_handoff_if_any.cooled_pressure_if_any must be non-empty when present"
        )

    warm_field = handoff.get("warm_field")
    if warm_field is None:
        return

    if not isinstance(warm_field, dict):
        problems.append("carrier_handoff_if_any.warm_field must be an object when present")
        return

    validate_no_extra_keys(
        warm_field,
        {"active_pressures", "cheap_check", "primitive_hints", "evidence_basis"},
        "carrier_handoff_if_any.warm_field",
        problems,
    )

    active_pressures = warm_field.get("active_pressures")
    if active_pressures is not None and not isinstance(active_pressures, list):
        problems.append("carrier_handoff_if_any.warm_field.active_pressures must be an array")
    elif isinstance(active_pressures, list):
        if not 1 <= len(active_pressures) <= 2:
            problems.append(
                "carrier_handoff_if_any.warm_field.active_pressures must contain 1 or 2 entries"
            )
        for idx, value in enumerate(active_pressures):
            if not isinstance(value, str) or not value.strip():
                problems.append(
                    "carrier_handoff_if_any.warm_field.active_pressures"
                    f"[{idx}] must be a non-empty string"
                )

    cheap_check = warm_field.get("cheap_check")
    if cheap_check is not None and (
        not isinstance(cheap_check, str) or not cheap_check.strip()
    ):
        problems.append(
            "carrier_handoff_if_any.warm_field.cheap_check must be non-empty when present"
        )

    primitive_hints = warm_field.get("primitive_hints")
    if primitive_hints is not None and not isinstance(primitive_hints, list):
        problems.append(
            "carrier_handoff_if_any.warm_field.primitive_hints must be an array"
        )
    elif isinstance(primitive_hints, list):
        if not 1 <= len(primitive_hints) <= 2:
            problems.append(
                "carrier_handoff_if_any.warm_field.primitive_hints must contain 1 or 2 entries"
            )
        for idx, value in enumerate(primitive_hints):
            if canonicalize_primitive_token(value) not in ALLOWED_PRIMITIVES:
                problems.append(
                    "carrier_handoff_if_any.warm_field.primitive_hints"
                    f"[{idx}] must be one of: {', '.join(sorted(ALLOWED_PRIMITIVES))}"
                )

    if active_pressures is None and primitive_hints is None:
        problems.append(
            "carrier_handoff_if_any.warm_field must carry active_pressures or primitive_hints"
        )

    evidence_basis = warm_field.get("evidence_basis")
    if evidence_basis is not None and (
        not isinstance(evidence_basis, str)
        or evidence_basis
        not in {"explicit_hint", "state_witness", "cheap_check", "lexical_hint", "mixed"}
    ):
        problems.append(
            "carrier_handoff_if_any.warm_field.evidence_basis must be explicit_hint, "
            "state_witness, cheap_check, lexical_hint, or mixed when present"
        )


def infer_primitives_from_text(*values: object) -> list[str]:
    text = normalize_primitive_token(
        " ".join(nonempty_text(value) for value in values if nonempty_text(value))
    )
    if not text:
        return []

    hits: list[str] = []
    explicit_aliases = []
    for primitive, aliases in PRIMITIVE_ALIAS_GROUPS.items():
        phrases = [
            normalize_primitive_token(alias)
            for alias in aliases
            if len(normalize_primitive_token(alias).split()) > 1
        ]
        explicit_aliases.append((primitive, sorted(set(phrases), key=len, reverse=True)))
    for primitive, phrases in explicit_aliases:
        if any(phrase and phrase in text for phrase in phrases):
            hits.append(primitive)
        if len(hits) == 2:
            return hits

    keyword_groups = [
        ("symmetry", ["symmetry", "symmetric", "balance", "balanced", "swap", "mirror"]),
        ("limit_boundary", ["limit", "boundary", "edge", "endpoint", "singular", "degener", "collapse", "tangent"]),
        ("conservation", ["conserv", "invariant", "total", "net", "mass", "flow", "balance sheet"]),
        ("projection", ["project", "projection", "flatten", "shadow", "slice", "cross-section"]),
        ("assignment", ["assign", "special value", "representative", "plug", "coincidence"]),
        ("reverse", ["reverse", "backward", "pullback", "rollback"]),
        ("picture", ["picture", "diagram", "draw", "geometry", "graph", "visual"]),
        ("witness", ["witness", "counterexample", "separate", "kill", "probe", "check", "seam"]),
        (
            "state_split",
            ["state split", "split", "quotient", "dp", "automaton", "finite-state", "state class", "equivalence class"],
        ),
        ("compatibility", ["merge", "compat", "coexist", "joint", "realiz", "supply", "overlap"]),
        ("readout", ["readout", "query", "answer", "output", "certificate", "construct", "materialize"]),
    ]
    for primitive, keywords in keyword_groups:
        if any(keyword in text for keyword in keywords):
            hits.append(primitive)
        if len(hits) == 2:
            break
    return hits


def infer_primitives_from_pressure_hints(values: object) -> list[str]:
    if not isinstance(values, list):
        return []

    mapping = {
        "symmetry": "symmetry",
        "limit boundary": "limit_boundary",
        "conservation": "conservation",
        "projection": "projection",
        "assignment": "assignment",
        "reverse": "reverse",
        "picture": "picture",
        "witness": "witness",
        "check": "witness",
        "state split": "state_split",
        "compatibility": "compatibility",
        "readout": "readout",
        "query": "readout",
    }
    hits: list[str] = []
    for value in values:
        primitive = canonicalize_primitive_token(value) or mapping.get(
            normalize_primitive_token(value)
        )
        if primitive and primitive not in hits:
            hits.append(primitive)
        if len(hits) == 2:
            break
    return hits


def classify_selection_basis(
    explicit_hints: list[str],
    pressure_hints: list[str],
    agenda_hints: list[str],
    text_hints: list[str],
    tie_break_check: str,
) -> str:
    if explicit_hints:
        return "tie_break" if len(explicit_hints) > 1 and tie_break_check else "explicit_hint"
    if pressure_hints or agenda_hints:
        merged = pressure_hints + [hint for hint in agenda_hints if hint not in pressure_hints]
        return "tie_break" if len(merged) > 1 and tie_break_check else "agenda_hint"
    return "tie_break" if len(text_hints) > 1 and tie_break_check else "text_fallback"


def infer_evidence_basis(
    existing_value: object,
    *,
    selection_basis: object = "",
    tie_break_check: object = "",
    explicit_hints: bool = False,
    witness_hints: bool = False,
    lexical_hints: bool = False,
) -> str:
    existing = nonempty_text(existing_value)
    if existing:
        return existing
    if explicit_hints and (witness_hints or lexical_hints):
        return "mixed"
    if explicit_hints:
        return "explicit_hint"
    if nonempty_text(tie_break_check):
        return "cheap_check"
    if witness_hints:
        return "state_witness"
    if lexical_hints:
        return "lexical_hint"

    normalized_selection = nonempty_text(selection_basis)
    if normalized_selection == "explicit_hint":
        return "explicit_hint"
    if normalized_selection in {"agenda_hint", "tie_break"}:
        return "state_witness"
    if normalized_selection == "text_fallback":
        return "lexical_hint"
    return ""


def merge_primitive_hints(*groups: object) -> list[str]:
    merged: list[str] = []
    for group in groups:
        if not isinstance(group, list):
            continue
        for value in group:
            primitive = canonicalize_primitive_token(value)
            if primitive and primitive in ALLOWED_PRIMITIVES and primitive not in merged:
                merged.append(primitive)
            if len(merged) == 2:
                return merged
    return merged


def primitive_is_probe_like(token: object) -> bool:
    return canonicalize_primitive_token(token) in PROBE_LIKE_PRIMITIVES


def skill_first_probe_secondary(
    control_signals: dict | None,
    *,
    focus: str = "",
) -> bool:
    if not isinstance(control_signals, dict):
        return False

    operator_bias = control_signals.get("operator_bias", {})
    meta_controls = control_signals.get("meta_controls", {})
    layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})

    favored_primitives = (
        merge_primitive_hints(operator_bias.get("favored_primitives"))
        if isinstance(operator_bias, dict)
        else []
    )
    has_nonprobe_structural = any(
        primitive and primitive not in PROBE_LIKE_PRIMITIVES
        for primitive in favored_primitives
    )
    wake_skills = [
        canonicalize_skill_token(skill)
        for skill in (
            layerwise_pressure.get("wake_skills", [])
            if isinstance(layerwise_pressure, dict)
            else []
        )
        if canonicalize_skill_token(skill)
    ]
    structural_skill_live = any(skill in STRUCTURAL_WAKE_SKILLS for skill in wake_skills)
    closure_live = (
        isinstance(meta_controls, dict)
        and meta_controls.get("closure_gate", {}).get("active") is True
    )
    counter_question_live = (
        isinstance(meta_controls, dict)
        and meta_controls.get("counter_question", {}).get("active") is True
    )

    if focus == "rival":
        return False
    if counter_question_live and focus == "seam" and not (has_nonprobe_structural or structural_skill_live):
        return False

    return bool(
        closure_live
        or has_nonprobe_structural
        or structural_skill_live
        or (
            isinstance(layerwise_pressure, dict)
            and layerwise_pressure.get("active") is True
        )
    )


def reorder_kinds_for_skill_first(
    kinds: list[str],
    *,
    focus: str = "",
    probe_secondary: bool = False,
) -> list[str]:
    normalized = [kind for kind in kinds if kind in {"write", "readout", "check", "witness"}]
    if not normalized:
        return normalized
    if not probe_secondary or focus == "rival":
        return list(dict.fromkeys(normalized))

    ordered = []
    if focus == "asked_medium":
        ordered.extend(["write", "readout", "check", "witness"])
    else:
        ordered.extend(["write", "readout", "check", "witness"])
    ordered.extend([kind for kind in normalized if kind not in ordered])
    return [kind for kind in ordered if kind in normalized or kind in {"write", "readout", "check", "witness"}][:4]


def reorder_primitives_for_skill_first(
    primitives: list[str],
    *,
    focus: str = "",
    probe_secondary: bool = False,
) -> list[str]:
    canonical = [
        canonicalize_primitive_token(primitive)
        for primitive in primitives
        if canonicalize_primitive_token(primitive)
    ]
    if not canonical:
        return []
    if not probe_secondary:
        return list(dict.fromkeys(canonical))

    def rank(primitive: str) -> tuple[int, int]:
        if primitive in PROBE_LIKE_PRIMITIVES:
            return (3, 0)
        if focus == "asked_medium" and primitive in READOUT_LIKE_PRIMITIVES:
            return (0, 0)
        if primitive in {
            "state_split",
            "projection",
            "canonical_normalization",
            "common_value_compression",
            "compatibility",
            "conservation",
            "function_archetype_matching",
            "matching_instead_of_probability",
            "grid_selection_permutation",
            "model_calling_before_derivation",
            "reverse",
            "picture",
        }:
            return (1, 0)
        if primitive in READOUT_LIKE_PRIMITIVES:
            return (2, 0)
        return (2, 1)

    deduped = list(dict.fromkeys(canonical))
    return sorted(deduped, key=rank)


def summarize_primitive_questions(primitives: object) -> list[str]:
    summary: list[str] = []
    for primitive, semantics in summarize_primitive_semantics(primitives).items():
        controller_question = nonempty_text(semantics.get("controller_question"))
        if controller_question and controller_question not in summary:
            summary.append(controller_question)
        if len(summary) == 2:
            break
    return summary


def summarize_primitive_touches(primitives: object) -> list[str]:
    summary: list[str] = []
    for primitive, semantics in summarize_primitive_semantics(primitives).items():
        touch = nonempty_text(semantics.get("cheapest_honest_touch"))
        if touch and touch not in summary:
            summary.append(touch)
        if len(summary) == 2:
            break
    return summary


def summarize_primitive_antipatterns(primitives: object) -> list[str]:
    summary: list[str] = []
    for primitive, semantics in summarize_primitive_semantics(primitives).items():
        anti_pattern = nonempty_text(semantics.get("anti_pattern"))
        if anti_pattern and anti_pattern not in summary:
            summary.append(anti_pattern)
        if len(summary) == 2:
            break
    return summary


def derive_control_signals(
    state: dict,
    problems: list[str],
    *,
    handoff_override: dict | None = None,
    primitive_field_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    current_object = nonempty_text(state.get("current_object"))
    current_seam = nonempty_text(state.get("current_seam")) or nonempty_text(
        state.get("next_bite")
    )
    current_debt = nonempty_text(state.get("current_debt"))
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    next_bite = nonempty_text(state.get("next_bite"))
    bound_program = state.get("bound_program")
    gate_binding = state.get("gate_binding_if_any")
    output_status = state.get("output_status")
    handoff = (
        handoff_override
        if handoff_override is not None
        else state.get("carrier_handoff_if_any")
    )
    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    primitive_competition = state.get("primitive_competition_if_any")

    output_touched = isinstance(output_status, dict) and output_status.get("touched") is True
    final_materialized = (
        isinstance(output_status, dict)
        and output_status.get("final_artifact_materialized") is True
    )
    cosmetic_only = (
        isinstance(output_status, dict) and output_status.get("cosmetic_only") is True
    )

    shell_suspicion = bool(
        current_object
        and current_seam
        and current_seam != current_object
        and not isinstance(handoff, dict)
    )
    middle_object_risk = bool(
        current_object
        and output_touched
        and (cosmetic_only or not final_materialized)
        and asked_medium
        and current_object != asked_medium
    )
    reselection_needed = bool(
        current_object
        and current_seam
        and current_seam != current_object
        and state.get("bound_program") is None
        and state.get("gate_binding_if_any") is None
        and not isinstance(handoff, dict)
        and (shell_suspicion or state.get("uncertainty_mode") in {"high", "mixed"} or middle_object_risk)
    )

    if isinstance(bound_program, dict) and nonempty_text(bound_program.get("target")):
        owner_status = "locked"
    elif isinstance(gate_binding, dict) or isinstance(handoff, dict) or isinstance(primitive_field, dict):
        owner_status = "narrowing"
    else:
        owner_status = "unlocked"

    if isinstance(bound_program, dict) or isinstance(gate_binding, dict):
        essence_status = "controller_bound"
    elif current_seam or isinstance(handoff, dict) or isinstance(primitive_field, dict):
        essence_status = "controller_emerging"
    else:
        essence_status = "surface_heavy"

    if isinstance(handoff, dict):
        carrier_status = "thinning"
    elif current_object and current_seam and current_seam != current_object:
        carrier_status = "too_thick"
    else:
        carrier_status = "thin_enough"

    competition_active = isinstance(primitive_competition, dict) and not primitive_competition_is_stale(
        state,
        competition_override=primitive_competition,
        handoff_override=handoff,
    )
    competition_candidates: list[str] = []
    competition_winner = ""
    competition_separating_check = ""
    competition_status = "none"
    if competition_active:
        candidates = primitive_competition.get("candidates", [])
        if isinstance(candidates, list):
            competition_candidates = [
                canonicalize_primitive_token(candidate.get("primitive"))
                for candidate in candidates
                if isinstance(candidate, dict)
                and canonicalize_primitive_token(candidate.get("primitive"))
            ]
        competition_winner = canonicalize_primitive_token(
            primitive_competition.get("winner_if_any")
        )
        competition_separating_check = nonempty_text(
            primitive_competition.get("separating_check")
        )
        if competition_winner:
            competition_status = "resolved"
        elif competition_candidates:
            competition_status = "unresolved"

    primitive_field_active: list[str] = []
    primitive_selection_basis = ""
    primitive_tie_break_check = ""
    primitive_evidence_basis = ""
    if isinstance(primitive_field, dict):
        active_primitives = primitive_field.get("active_primitives")
        if isinstance(active_primitives, list):
            primitive_field_active = [
                canonicalize_primitive_token(value)
                for value in active_primitives
                if canonicalize_primitive_token(value)
            ]
        primitive_selection_basis = nonempty_text(primitive_field.get("selection_basis"))
        primitive_tie_break_check = nonempty_text(primitive_field.get("tie_break_check"))
        primitive_evidence_basis = infer_evidence_basis(
            primitive_field.get("evidence_basis"),
            selection_basis=primitive_selection_basis,
            tie_break_check=primitive_tie_break_check,
            explicit_hints=primitive_selection_basis == "explicit_hint",
            witness_hints=primitive_selection_basis == "agenda_hint",
            lexical_hints=primitive_selection_basis == "text_fallback",
        )

    live_primitives: list[str] = []
    if competition_status == "resolved" and competition_winner:
        live_primitives = [competition_winner]
    elif competition_status == "unresolved" and competition_candidates:
        live_primitives = competition_candidates[:2]
    elif primitive_field_active:
        live_primitives = primitive_field_active[:2]

    heuristic_primitives: list[str] = []
    if middle_object_risk:
        heuristic_primitives.extend(
            ["definition_as_direct_readout", "dominant_mechanism_readout"]
        )
    if reselection_needed:
        heuristic_primitives.extend(
            ["boundary_as_route_finder", "local_seam_controls_global"]
        )
    if state.get("uncertainty_mode") in {"high", "mixed"}:
        heuristic_primitives.extend(["compare_without_calculating", "witness"])
    if not output_touched:
        heuristic_primitives.extend(["readout", "projection_readout"])
    if not heuristic_primitives and shell_suspicion:
        heuristic_primitives.extend(["canonical_normalization", "projection"])

    god_view_active = bool(
        shell_suspicion
        or middle_object_risk
        or (current_object and current_seam and current_seam != current_object)
    )
    counter_question_active = bool(
        state.get("release_veto") is True
        and not isinstance(bound_program, dict)
        and bool(current_debt or next_bite)
    )
    closure_gate_active = bool(
        state.get("release_veto") is True
        and (not output_touched or cosmetic_only or not final_materialized)
    )
    supervisory_pulse_active = bool(
        state.get("release_veto") is True
        and not isinstance(bound_program, dict)
        and not isinstance(handoff, dict)
    )
    metacognition_active = bool(
        god_view_active
        or counter_question_active
        or closure_gate_active
        or owner_status != "locked"
    )
    hindbrain_guard_active = bool(
        state.get("release_veto") is True
        and (
            closure_gate_active
            or state.get("uncertainty_mode") in {"high", "mixed"}
            or bool(state.get("unresolved_markers"))
        )
    )
    central_mode = (
        "closure_gate"
        if closure_gate_active
        else "reselection"
        if isinstance(handoff, dict) or reselection_needed
        else "bound_program"
        if isinstance(bound_program, dict)
        else "monitoring"
    )

    if god_view_active:
        heuristic_primitives = merge_primitive_hints(
            [
                "canonical_normalization",
                "common_value_compression",
                "local_seam_controls_global",
                "projection",
            ],
            heuristic_primitives,
        )
    if counter_question_active:
        heuristic_primitives = merge_primitive_hints(
            ["compare_without_calculating", "witness"],
            heuristic_primitives,
        )
    if closure_gate_active:
        heuristic_primitives = merge_primitive_hints(
            ["definition_as_direct_readout", "readout"],
            heuristic_primitives,
        )

    operator_bias = merge_primitive_hints(live_primitives, heuristic_primitives)
    controller_questions = summarize_primitive_questions(operator_bias)
    honest_touches = summarize_primitive_touches(operator_bias)
    anti_patterns = summarize_primitive_antipatterns(operator_bias)
    attraction_target = (
        asked_medium
        if closure_gate_active and asked_medium
        else current_seam
        if (reselection_needed or state.get("uncertainty_mode") in {"high", "mixed"}) and current_seam
        else current_object
    )
    reward_signal = (
        "nearer exact asked-medium closure should pull harder than commentary"
        if closure_gate_active
        else "smaller truthful carrier and cheaper discriminating witness should pull harder"
        if reselection_needed or god_view_active
        else "same-carrier object change should pull harder than renaming"
    )
    penalty_signal = (
        "penalize closure-shaped language without executable asked-medium contact"
        if closure_gate_active
        else "penalize ordinary-route reconstruction and renaming without burden deletion"
        if god_view_active
        else "penalize commentary that leaves the object unchanged"
    )
    discomfort_source = (
        current_debt
        or next_bite
        or current_seam
        or asked_medium
        or current_object
    )

    cheapest_reality_check = ""
    if competition_separating_check:
        cheapest_reality_check = competition_separating_check
    if not cheapest_reality_check and primitive_tie_break_check:
        cheapest_reality_check = primitive_tie_break_check
    if not cheapest_reality_check and primitive_field_active:
        primitive_touches = summarize_primitive_touches(primitive_field_active)
        if primitive_touches:
            cheapest_reality_check = primitive_touches[0]
    if not cheapest_reality_check and competition_candidates:
        competition_touches = summarize_primitive_touches(competition_candidates)
        if competition_touches:
            cheapest_reality_check = competition_touches[0]
    if not cheapest_reality_check and isinstance(primitive_field, dict):
        if not cheapest_reality_check:
            primitive_touches = summarize_primitive_touches(
                primitive_field.get("active_primitives")
            )
            if primitive_touches:
                cheapest_reality_check = primitive_touches[0]
    if not cheapest_reality_check and isinstance(handoff, dict):
        warm_field = handoff.get("warm_field")
        if isinstance(warm_field, dict):
            cheapest_reality_check = nonempty_text(warm_field.get("cheap_check"))
    if not cheapest_reality_check:
        cheapest_reality_check = current_seam or asked_medium or current_object

    why_now = (
        f"the current shell still looks thicker than the live seam {current_seam}"
        if reselection_needed and current_seam
        else "the current carrier may still be surface-heavy and not yet owner-complete"
        if shell_suspicion
        else "the current object may still be a beautiful middle carrier instead of the final owner"
        if middle_object_risk
        else "the current controller is locally visible enough to stay thin"
    )

    counter_question_target = cheapest_reality_check or current_seam or current_object
    counter_question_text = (
        f"given the ask, the strongest still-true object, and the current gap, what same-carrier check or hostile witness could kill decorative progress on {counter_question_target} first?"
        if counter_question_target
        else "given the ask and the current gap, what same-carrier check could still kill decorative progress first?"
    )
    counter_question_kind = (
        "readout"
        if closure_gate_active and asked_medium
        else "witness"
        if competition_status == "live_rivalry" or owner_status != "locked"
        else "check"
    )
    supervision_owner = (
        "closure"
        if closure_gate_active
        else "reselection"
        if isinstance(handoff, dict) or reselection_needed
        else "rival"
        if competition_status == "live_rivalry"
        else "carrier"
        if shell_suspicion or middle_object_risk
        else "seam"
        if current_seam
        else "object"
    )
    supervision_target = (
        asked_medium
        if supervision_owner == "closure" and asked_medium
        else nonempty_text(handoff.get("to_object"))
        if supervision_owner == "reselection" and isinstance(handoff, dict)
        else competition_separating_check
        if supervision_owner == "rival" and competition_separating_check
        else current_seam
        if supervision_owner == "seam" and current_seam
        else current_object
    )
    supervision_until = (
        "asked_medium_contact_or_exact_executable_closure"
        if supervision_owner == "closure"
        else "handoff_bound_or_exact_check_or_kill_witness"
        if supervision_owner == "reselection"
        else "same_carrier_change_or_kill_witness_or_exact_check"
    )
    supervision_reason = (
        "release should stay vetoed until the asked medium has exact executable contact"
        if supervision_owner == "closure"
        else "thinner-carrier authority is locally due and should not dissolve back into narration"
        if supervision_owner == "reselection"
        else "a live rival still needs one separating witness before ordinary continuation should regain comfort"
        if supervision_owner == "rival"
        else "the current carrier still needs local anti-drift ownership before it can be trusted"
    )
    reward_promote = [
        "exact_readout"
        if closure_gate_active
        else "same_carrier_change",
        "separating_check"
        if competition_status == "live_rivalry" or owner_status != "locked"
        else "object_change",
    ]
    if reselection_needed or isinstance(handoff, dict):
        reward_promote.insert(1, "thinner_carrier_reduction")
    reward_promote = list(dict.fromkeys(reward_promote))
    penalty_demote = [
        "decorative_continuation_without_contact",
        "beautiful_middle_without_interface_cashback"
        if middle_object_risk
        else "renaming_without_object_change",
    ]
    if god_view_active:
        penalty_demote.append("ordinary_route_reconstruction")
    if shell_suspicion or reselection_needed:
        penalty_demote.append("surface_story_without_carrier_change")
    penalty_demote = list(dict.fromkeys(penalty_demote))
    closure_required_contact = (
        "readout"
        if asked_medium
        else "write"
        if isinstance(bound_program, dict)
        and nonempty_text(bound_program.get("kind")) == "write"
        else "check"
    )
    closure_target = asked_medium or current_seam or current_object
    closure_reason = (
        f"exact asked-medium closure on {asked_medium} is still unpaid"
        if closure_gate_active and asked_medium
        else "release should stay closed until one exact executable closure touch lands"
        if closure_gate_active
        else "no local closure debt currently owns the slot"
    )
    micro_control_surface = {
        "scope_rule": "current-layer-only",
        "planning_permission": False,
        "closure_pull": {
            "active": closure_gate_active,
            "target": closure_target,
            "reason": closure_reason,
            "required_contact": closure_required_contact,
            "blocks_release": closure_gate_active,
        },
        "reward_bias": {
            "promote": reward_promote,
            "reason": reward_signal,
        },
        "penalty_bias": {
            "demote": penalty_demote,
            "reason": penalty_signal,
        },
        "supervision_pulse": {
            "active": supervisory_pulse_active or closure_gate_active or reselection_needed,
            "owner": supervision_owner,
            "target": supervision_target,
            "until": supervision_until,
            "reason": supervision_reason,
        },
        "counter_question": {
            "active": counter_question_active,
            "question": counter_question_text,
            "target": counter_question_target,
            "preferred_answer_kind": counter_question_kind,
            "reason": "keep one cheap falsifier or exact check live before commentary regains comfort",
        },
    }

    layerwise_reselection_pressure = derive_layerwise_reselection_pressure(
        {
            "carrier_status": carrier_status,
            "shell_suspicion": shell_suspicion,
            "middle_object_risk": middle_object_risk,
            "reselection_needed": reselection_needed,
            "why_now": why_now,
        },
        {
            "selection_basis": primitive_selection_basis,
            "evidence_basis": primitive_evidence_basis,
        },
        current_seam=current_seam,
        current_object=current_object,
        current_debt=current_debt,
    )

    return {
        "current_controller_view": {
            "essence_status": essence_status,
            "owner_status": owner_status,
            "carrier_status": carrier_status,
            "shell_suspicion": shell_suspicion,
            "middle_object_risk": middle_object_risk,
            "reselection_needed": reselection_needed,
            "why_now": why_now,
        },
        "operator_bias": {
            "live_primitives": live_primitives,
            "favored_primitives": operator_bias,
            "heuristic_primitives": merge_primitive_hints(heuristic_primitives),
            "cheapest_reality_check": cheapest_reality_check,
            "focus_hint": current_seam or next_bite or current_debt or current_object,
            "controller_questions": controller_questions,
            "honest_touches": honest_touches,
            "anti_patterns": anti_patterns,
        },
        "primitive_control": {
            "layer_has_primitive_field": isinstance(primitive_field, dict),
            "active_primitives": primitive_field_active,
            "selection_basis": primitive_selection_basis,
            "evidence_basis": primitive_evidence_basis,
            "competition_status": competition_status,
            "competition_candidates": competition_candidates,
            "winner_if_any": competition_winner,
            "separating_check": competition_separating_check,
        },
        "incentive_field": {
            "attraction_pull": {
                "target": attraction_target,
                "reason": reward_signal,
            },
            "reward_bias": {
                "promote": "object_change_or_exact_readout",
                "why": reward_signal,
            },
            "penalty_bias": {
                "demote": "decorative_continuation_without_contact",
                "why": penalty_signal,
            },
            "discomfort_if_ignored": discomfort_source,
        },
        "micro_control_surface": micro_control_surface,
        "layerwise_reselection_pressure": layerwise_reselection_pressure,
        "meta_controls": {
            "counter_question": {
                "active": counter_question_active,
                "action_tendency": "force_same_carrier_check_or_candidate_object",
            },
            "closure_gate": {
                "active": closure_gate_active,
                "action_tendency": "deny_release_until_exact_asked_medium_contact",
            },
            "supervisory_pulse": {
                "active": supervisory_pulse_active,
                "action_tendency": "demote_renaming_without_object_change",
            },
            "god_view": {
                "active": god_view_active,
                "action_tendency": "rename_smaller_and_shift_to_true_controller",
            },
            "metacognition": {
                "active": metacognition_active,
                "action_tendency": "re-check_owner_carrier_and_false_essence_live",
            },
            "central_control": {
                "mode": central_mode,
                "action_tendency": "bias_one_local_owner_until_change_or_check",
            },
            "hindbrain_guard": {
                "active": hindbrain_guard_active,
                "action_tendency": "keep_non_release_latch_and_reopen_smallest_honest_exit",
            },
        },
    }


def derive_primitive_program_candidate(
    state: dict,
    problems: list[str],
    primitive_field_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    if not isinstance(primitive_field, dict):
        return None

    active_primitives = primitive_field.get("active_primitives")
    if not isinstance(active_primitives, list) or not active_primitives:
        return None
    canonical_primitives = [
        canonicalize_primitive_token(value)
        for value in active_primitives
        if canonicalize_primitive_token(value)
    ]
    if not canonical_primitives:
        return None

    layer_object = nonempty_text(primitive_field.get("layer_object")) or nonempty_text(
        state.get("current_object")
    )
    current_debt = nonempty_text(state.get("current_debt"))
    next_bite = nonempty_text(state.get("next_bite"))
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    tie_break_check = nonempty_text(primitive_field.get("tie_break_check"))
    selection_basis = nonempty_text(primitive_field.get("selection_basis"))
    competition = state.get("primitive_competition_if_any")
    primitive_semantics = get_primitive_semantics(canonical_primitives[0])
    semantic_touch = nonempty_text(primitive_semantics.get("cheapest_honest_touch"))
    semantic_question = nonempty_text(primitive_semantics.get("controller_question"))
    control_signals = derive_control_signals(
        state,
        problems,
        primitive_field_override=primitive_field,
    )
    layerwise_pressure = (
        control_signals.get("layerwise_reselection_pressure", {})
        if isinstance(control_signals, dict)
        else {}
    )
    blocks_direct_closure = (
        isinstance(layerwise_pressure, dict)
        and layerwise_pressure.get("active") is True
        and layerwise_pressure.get("direct_closure_allowed") is not True
    )

    if isinstance(competition, dict) and not primitive_competition_is_stale(state):
        candidates = competition.get("candidates")
        winner = nonempty_text(competition.get("winner_if_any"))
        if isinstance(candidates, list) and len(candidates) > 1 and not winner:
            progressive_candidate = derive_progressive_competition_program_candidate(
                state,
                primitive_field,
                competition,
            )
            if isinstance(progressive_candidate, dict):
                return progressive_candidate
            return None

    if len(canonical_primitives) > 1 and not tie_break_check:
        return None
    if len(canonical_primitives) == 1 and selection_basis == "text_fallback":
        return None

    primitive = canonical_primitives[0]
    seam_target = layer_object or nonempty_text(state.get("current_seam"))
    object_target = layer_object or seam_target
    focus = next_bite or current_debt or semantic_question or layer_object

    def semantic_operation(fallback: str) -> str:
        return semantic_touch or fallback

    if (
        primitive_is_probe_like(primitive)
        and len(canonical_primitives) > 1
        and any(not primitive_is_probe_like(item) for item in canonical_primitives[1:])
        and skill_first_probe_secondary(
            control_signals if isinstance(control_signals, dict) else None,
            focus="asked_medium" if asked_medium else "",
        )
    ):
        return None

    if primitive == "definition_as_direct_readout":
        target = asked_medium or object_target
        if blocks_direct_closure:
            return None
        return {
            "kind": "write" if asked_medium else "readout",
            "target": target,
            "operation": semantic_operation(
                f"materialize one definition-side exact readout for {focus} on {target}"
            ),
            "success_signal": f"definition-side readout landed on {target}",
        }
    if primitive == "dominant_mechanism_readout":
        if blocks_direct_closure:
            return None
        return {
            "kind": "write",
            "target": object_target,
            "operation": f"isolate one dominant mechanism readout for {focus}",
            "success_signal": f"dominant mechanism readout became explicit on {object_target}",
        }
    if primitive == "vector_difference_readout":
        target = asked_medium or object_target
        if blocks_direct_closure:
            return None
        return {
            "kind": "write" if asked_medium else "readout",
            "target": target,
            "operation": semantic_operation(
                f"read the target through one vector-difference controller for {focus}"
            ),
            "success_signal": f"vector-difference readout landed on {target}",
        }
    if primitive == "compare_without_calculating":
        target = seam_target
        return {
            "kind": "check",
            "target": target,
            "operation": (
                f"separate the live options on {target} by comparing without full calculation for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"comparison witness separated the live options on {target}",
        }
    if primitive == "local_seam_controls_global":
        target = seam_target
        return {
            "kind": "check",
            "target": target,
            "operation": (
                f"probe the local seam on {target} as the global controller for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"local seam witness sharpened or killed the global line on {target}",
        }
    if primitive == "grid_selection_permutation":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"materialize one grid-selection to permutation / exact-cover carrier for {focus}"
            ),
            "success_signal": f"grid-selection permutation carrier became explicit on {object_target}",
        }
    if primitive == "matching_instead_of_probability":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"rewrite the burden as one exact matching / coexistence carrier for {focus}"
            ),
            "success_signal": f"matching carrier became explicit on {object_target}",
        }
    if primitive == "function_archetype_matching":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"match the live object to one function archetype family for {focus}"
            ),
            "success_signal": f"function archetype became explicit on {object_target}",
        }
    if primitive == "model_calling_before_derivation":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"call one governing model object before derivation for {focus}"
            ),
            "success_signal": f"governing model became explicit on {object_target}",
        }
    if primitive == "common_value_compression":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"compress the visible variables into one common-value controller for {focus}"
            ),
            "success_signal": f"common-value controller became explicit on {object_target}",
        }
    if primitive == "container_to_cross_section":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"rewrite the burden through one container-to-cross-section carrier for {focus}"
            ),
            "success_signal": f"cross-section carrier became explicit on {object_target}",
        }
    if primitive == "area_to_line_readout":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"collapse the area burden to one line readout for {focus}"
            ),
            "success_signal": f"area-to-line readout became explicit on {object_target}",
        }
    if primitive == "dot_product_projection":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"read the live burden through one dot-product projection controller for {focus}"
            ),
            "success_signal": f"dot-product projection became explicit on {object_target}",
        }
    if primitive == "projection_readout":
        if blocks_direct_closure:
            return None
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"take one projection-side exact readout for {focus}"
            ),
            "success_signal": f"projection readout became explicit on {object_target}",
        }
    if primitive == "canonical_normalization":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"rewrite the current carrier into one canonical normalized form for {focus}"
            ),
            "success_signal": f"canonical normalized carrier became explicit on {object_target}",
        }
    if primitive == "symmetry_as_variable_killer":
        target = object_target
        return {
            "kind": "check",
            "target": target,
            "operation": (
                f"use symmetry to kill fake variables on {target} for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"symmetry killed fake variables on {target}",
        }
    if primitive == "boundary_as_route_finder":
        target = seam_target
        return {
            "kind": "check",
            "target": target,
            "operation": (
                semantic_operation(
                    f"use one boundary / first-crack probe on {target} to sharpen the live controller for {focus}"
                )
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"boundary route-finder sharpened or changed {target}",
        }
    if primitive == "special_value_probing":
        target = object_target
        return {
            "kind": "check",
            "target": target,
            "operation": (
                semantic_operation(
                    f"probe one decisive special value on {target} for {focus}"
                )
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"special-value probe separated the live burden on {target}",
        }

    if primitive == "readout":
        target = asked_medium or object_target
        if blocks_direct_closure:
            return None
        return {
            "kind": "write" if asked_medium else "readout",
            "target": target,
            "operation": semantic_operation(
                f"materialize exact readout for {focus} on {target}"
            ),
            "success_signal": f"exact readout landed on {target}",
        }
    if primitive == "witness":
        target = seam_target
        return {
            "kind": "check",
            "target": target,
            "operation": (
                semantic_operation(
                    f"run one separating witness on {target} for {focus}"
                )
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"witness on {target} changed or killed the current line",
        }
    if primitive == "state_split":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"materialize one exact state split / quotient for {focus}"
            ),
            "success_signal": f"state split became explicit on {object_target}",
        }
    if primitive == "compatibility":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"materialize one compatibility / merge fragment for {focus}"
            ),
            "success_signal": f"compatibility fragment landed on {object_target}",
        }
    if primitive == "picture":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"externalize one picture / graph object for {focus}"
            ),
            "success_signal": f"external picture became explicit on {object_target}",
        }
    if primitive == "reverse":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"rewrite the current carrier in reverse form for {focus}"
            ),
            "success_signal": f"reverse owner became explicit on {object_target}",
        }
    if primitive == "projection":
        return {
            "kind": "write",
            "target": object_target,
            "operation": (
                semantic_touch
                or f"project the burden to a thinner carrier for {focus}"
            ),
            "success_signal": f"projection became explicit on {object_target}",
        }
    if primitive == "conservation":
        return {
            "kind": "write",
            "target": object_target,
            "operation": semantic_touch or f"write one conserved ledger for {focus}",
            "success_signal": f"conserved ledger became explicit on {object_target}",
        }
    if primitive == "limit_boundary":
        target = seam_target
        return {
            "kind": "check",
            "target": target,
            "operation": (
                semantic_touch
                or f"push one boundary / first-crack check on {target}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"boundary check changed or sharpened {target}",
        }
    if primitive == "assignment":
        target = object_target
        return {
            "kind": "check",
            "target": target,
            "operation": (
                semantic_operation(
                    f"probe one controlled assignment / special value on {target}"
                )
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"assignment probe separated the current carrier on {target}",
        }
    if primitive == "symmetry":
        target = object_target
        return {
            "kind": "check",
            "target": target,
            "operation": (
                semantic_touch
                or f"test one symmetry / balance normalization on {target}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"symmetry normalization changed the live burden on {target}",
        }

    return None


def classify_program_progress_priority(
    program: dict,
    *,
    asked_medium: str,
) -> tuple[int, int]:
    kind = nonempty_text(program.get("kind"))
    target = nonempty_text(program.get("target"))

    if kind in {"check", "witness"}:
        return (0, 0)
    if kind == "write" and target and target != asked_medium:
        return (1, 0)
    if kind in {"readout"}:
        return (2, 0)
    if kind == "write" and target == asked_medium:
        return (2, 1)
    return (3, 0)


def program_is_direct_closure_like(
    program: dict | None,
    *,
    asked_medium: str,
) -> bool:
    if not isinstance(program, dict):
        return False

    kind = nonempty_text(program.get("kind"))
    target = nonempty_text(program.get("target"))
    operation = nonempty_text(program.get("operation"))
    if asked_medium and target == asked_medium and kind in {"write", "readout"}:
        return True
    if operation == "materialize_exact_asked_medium_readout":
        return True
    return False


def closure_should_wait_for_structural_discharge(
    *,
    closure_nucleus: object,
    control_signals: object,
    asked_medium: str,
) -> bool:
    if not isinstance(closure_nucleus, dict) or not isinstance(control_signals, dict):
        return False

    layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
    if not (
        isinstance(layerwise_pressure, dict)
        and layerwise_pressure.get("active") is True
        and layerwise_pressure.get("direct_closure_allowed") is not True
    ):
        return False

    structural_bite = closure_nucleus.get("current_structural_bite_if_any")
    if not isinstance(structural_bite, dict):
        return False
    if program_is_direct_closure_like(structural_bite, asked_medium=asked_medium):
        return False

    readout_bite = closure_nucleus.get("current_readout_bite_if_any")
    if not program_is_direct_closure_like(readout_bite, asked_medium=asked_medium):
        return False

    return True


def derive_progressive_competition_program_candidate(
    state: dict,
    primitive_field: dict,
    competition: dict,
) -> dict | None:
    candidates = competition.get("candidates")
    if not isinstance(candidates, list) or len(candidates) < 2:
        return None

    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    tie_break_check = nonempty_text(competition.get("separating_check")) or nonempty_text(
        primitive_field.get("tie_break_check")
    )
    if not tie_break_check:
        return None

    derived: list[tuple[tuple[int, int], dict]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        primitive = canonicalize_primitive_token(candidate.get("primitive"))
        if not primitive:
            continue
        single_field = {
            "layer_object": primitive_field.get("layer_object"),
            "active_primitives": [primitive],
            "why_now": primitive_field.get("why_now"),
            "selection_basis": "explicit_hint",
            "evidence_basis": primitive_field.get("evidence_basis") or "state_witness",
        }
        if tie_break_check:
            single_field["tie_break_check"] = tie_break_check

        probe_state = dict(state)
        probe_state["primitive_competition_if_any"] = None
        program = derive_primitive_program_candidate(
            probe_state,
            [],
            primitive_field_override=single_field,
        )
        if not isinstance(program, dict):
            continue
        derived.append(
            (
                classify_program_progress_priority(program, asked_medium=asked_medium),
                program,
            )
        )

    if len(derived) < 2:
        return None

    derived.sort(key=lambda item: item[0])
    best_priority, best_program = derived[0]
    next_priority, _ = derived[1]

    # Only auto-progress unresolved competition when one candidate is clearly
    # more local in a hostile/separating sense than the others. If the best
    # unresolved move is already a write/readout, the host should not silently
    # collapse rivalry into ordinary continuation.
    if best_priority == next_priority or best_priority != (0, 0):
        return None
    return best_program


def derive_control_bridge(
    state: dict,
    problems: list[str],
    bound_program_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    bound_program = bound_program_override or state.get("bound_program")
    if not isinstance(bound_program, dict):
        return None

    bridge = {
        "current_object": state.get("current_object", ""),
        "current_debt": state.get("current_debt", ""),
        "asked_medium_surface": state.get("asked_medium_surface", ""),
        "revocation_handle": state.get("revocation_handle", ""),
        "primary_slot": state.get("primary_slot", ""),
        "next_touch": {
            "kind": bound_program.get("kind", ""),
            "target": bound_program.get("target", ""),
            "operation": bound_program.get("operation", ""),
            "success_signal": bound_program.get("success_signal", ""),
        },
        "program_origin": "derived" if bound_program_override is not None else "explicit",
    }

    if state.get("release_veto") is True and bound_program_override is None:
        bridge["default_local_action"] = "next_touch"
    elif bound_program_override is not None:
        bridge["candidate_next_touch"] = bridge.pop("next_touch")

    gate_binding = state.get("gate_binding_if_any")
    if isinstance(gate_binding, dict):
        bridge["gate_binding"] = {
            "source_focus": gate_binding.get("source_focus", ""),
            "source_target": gate_binding.get("source_target", ""),
            "demoted_continuation": gate_binding.get("demoted_continuation", ""),
            "authority_until": gate_binding.get("authority_until", ""),
        }

    primitive_field = state.get("primitive_field_if_any")
    if isinstance(primitive_field, dict):
        bridge["primitive_field"] = primitive_field
        bridge["primitive_semantics"] = summarize_primitive_semantics(
            primitive_field.get("active_primitives")
        )

    control_signals = derive_control_signals(
        state,
        problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
    )
    if isinstance(control_signals, dict):
        bridge["control_signals"] = control_signals

    return bridge


def derive_closure_nucleus(
    state: dict,
    problems: list[str],
    agenda_override: dict | None = None,
    primitive_field_override: dict | None = None,
    primitive_competition_override: dict | None = None,
    handoff_override: dict | None = None,
    bound_program_override: dict | None = None,
    bound_program_origin_override: str | None = None,
    control_signals_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    agenda = agenda_override if agenda_override is not None else derive_self_check_agenda(state, problems)
    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    primitive_competition = (
        primitive_competition_override
        if primitive_competition_override is not None
        else state.get("primitive_competition_if_any")
    )
    handoff = (
        handoff_override if handoff_override is not None else state.get("carrier_handoff_if_any")
    )
    bound_program = (
        bound_program_override if bound_program_override is not None else state.get("bound_program")
    )
    control_signals = (
        control_signals_override
        if control_signals_override is not None
        else derive_control_signals(
            state,
            problems,
            handoff_override=handoff,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        )
    )

    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))
    current_seam = nonempty_text(state.get("current_seam"))
    next_bite = nonempty_text(state.get("next_bite"))
    closure_target = asked_medium or current_seam or current_object
    separating_check = ""
    winner_if_any = ""
    competition_candidates: list[str] = []

    if isinstance(primitive_competition, dict):
        separating_check = nonempty_text(primitive_competition.get("separating_check"))
        winner_if_any = nonempty_text(primitive_competition.get("winner_if_any"))
        competition_candidates = [
            canonicalize_primitive_token(candidate.get("primitive"))
            for candidate in primitive_competition.get("candidates", [])
            if isinstance(candidate, dict)
            and canonicalize_primitive_token(candidate.get("primitive"))
        ]

    structural_bite = None
    readout_bite = None
    if isinstance(bound_program, dict):
        operation = nonempty_text(bound_program.get("operation"))
        kind = nonempty_text(bound_program.get("kind"))
        program_origin = nonempty_text(bound_program_origin_override)
        if not program_origin:
            program_origin = (
                "explicit" if isinstance(state.get("bound_program"), dict) else "derived"
            )
        touch = {
            "kind": kind,
            "target": nonempty_text(bound_program.get("target")) or closure_target,
            "operation": operation,
            "success_signal": nonempty_text(bound_program.get("success_signal")),
            "origin": program_origin,
        }
        if kind == "readout" or operation == "materialize_exact_asked_medium_readout":
            readout_bite = touch
        else:
            structural_bite = touch

    if structural_bite is None and isinstance(agenda, dict):
        focus = nonempty_text(agenda.get("focus"))
        target = nonempty_text(agenda.get("touch_target")) or closure_target
        preferred = agenda.get("preferred_kinds")
        preferred_kind = (
            preferred[0]
            if isinstance(preferred, list) and preferred and isinstance(preferred[0], str)
            else ""
        )
        if focus in {"seam", "rival", "carrier", "current_object"} or (
            focus == "asked_medium" and not readout_bite
        ):
            structural_bite = {
                "kind": preferred_kind or "check",
                "target": target,
                "operation": "same_carrier_local_change_or_check",
                "success_signal": "object_changes_or_one_live_rival_dies_or_local_debt_shrinks",
                "origin": "agenda",
            }

    if readout_bite is None and asked_medium:
        readout_bite = {
            "kind": "readout",
            "target": asked_medium,
            "operation": "materialize_exact_asked_medium_readout",
            "success_signal": "asked_medium_is_exact_and_executable",
            "origin": "asked_medium_closure",
        }

    if structural_bite is None and isinstance(primitive_field, dict):
        derived_program = derive_primitive_program_candidate(
            state,
            problems,
            primitive_field_override=primitive_field,
        )
        if isinstance(derived_program, dict):
            structural_bite = {
                "kind": nonempty_text(derived_program.get("kind")),
                "target": nonempty_text(derived_program.get("target")) or closure_target,
                "operation": nonempty_text(derived_program.get("operation")),
                "success_signal": nonempty_text(derived_program.get("success_signal")),
                "origin": "primitive_field",
            }

    competition_live = (
        isinstance(primitive_competition, dict)
        and len(competition_candidates) >= 2
        and not winner_if_any
    )
    same_carrier_only = not isinstance(handoff, dict)
    no_route_growth = same_carrier_only and competition_live
    debt_label = current_debt or next_bite or current_seam or closure_target

    nucleus = {
        "object": current_object,
        "debt": debt_label,
        "asked_medium_surface": asked_medium,
        "revocation_handle": nonempty_text(state.get("revocation_handle")),
        "same_carrier_only": same_carrier_only,
        "no_route_growth": no_route_growth,
        "owner": "same_carrier" if same_carrier_only else "reselection",
        "current_structural_bite_if_any": structural_bite or {},
        "current_readout_bite_if_any": readout_bite or {},
        "separating_check_if_any": separating_check,
        "winner_if_any": winner_if_any,
        "competition_candidates": competition_candidates,
        "resume_rule": (
            "rebind ask + object + debt; continue on the same carrier if one bite is already nameable, otherwise reseat authority only if that same gap survives more honestly on a thinner carrier"
        ),
    }

    if isinstance(control_signals, dict):
        micro_surface = control_signals.get("micro_control_surface", {})
        meta_controls = control_signals.get("meta_controls", {})
        if closure_should_wait_for_structural_discharge(
            closure_nucleus={
                "current_structural_bite_if_any": structural_bite or {},
                "current_readout_bite_if_any": readout_bite or {},
            },
            control_signals=control_signals,
            asked_medium=asked_medium,
        ):
            nucleus["readout_deferred_by_layerwise_pressure"] = True
        if isinstance(micro_surface, dict):
            closure_pull = micro_surface.get("closure_pull", {})
            supervision_pulse = micro_surface.get("supervision_pulse", {})
            if isinstance(closure_pull, dict):
                nucleus["closure_target"] = nonempty_text(closure_pull.get("target")) or closure_target
                nucleus["required_contact"] = nonempty_text(closure_pull.get("required_contact"))
                nucleus["blocks_release"] = closure_pull.get("blocks_release") is True
            if isinstance(supervision_pulse, dict):
                nucleus["supervision_owner"] = nonempty_text(supervision_pulse.get("owner"))
                nucleus["supervision_until"] = nonempty_text(supervision_pulse.get("until"))
        if isinstance(meta_controls, dict):
            closure_gate = meta_controls.get("closure_gate", {})
            nucleus["closure_gate_active"] = (
                isinstance(closure_gate, dict) and closure_gate.get("active") is True
            )

    return nucleus


def derive_reselection_bridge(
    state: dict,
    problems: list[str],
    handoff_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    handoff = handoff_override or state.get("carrier_handoff_if_any")
    if not isinstance(handoff, dict):
        return None

    bridge = {
        "current_object": state.get("current_object", ""),
        "current_seam": state.get("current_seam", ""),
        "current_debt": state.get("current_debt", ""),
        "next_bite": state.get("next_bite", ""),
        "primary_slot": state.get("primary_slot", ""),
        "handoff": {
            "trigger": handoff.get("trigger", ""),
            "from_slot": handoff.get("from_slot", ""),
            "to_object": handoff.get("to_object", ""),
            "winning_pressure": handoff.get("winning_pressure", ""),
            "cooled_pressure_if_any": handoff.get("cooled_pressure_if_any", ""),
            "why_local": handoff.get("why_local", ""),
        },
        "default_local_action": "rebind_local_pressure",
        "handoff_origin": "derived" if handoff_override is not None else "explicit",
    }

    warm_field = handoff.get("warm_field")
    if isinstance(warm_field, dict):
        warm_field_evidence_basis = infer_evidence_basis(
            warm_field.get("evidence_basis"),
            tie_break_check=warm_field.get("cheap_check"),
            explicit_hints=bool(
                infer_primitives_from_pressure_hints(warm_field.get("primitive_hints"))
            ),
            witness_hints=bool(
                infer_primitives_from_pressure_hints(warm_field.get("active_pressures"))
            ),
        )
        bridge["warm_field"] = {
            "active_pressures": warm_field.get("active_pressures", []),
            "cheap_check": warm_field.get("cheap_check", ""),
            "evidence_basis": warm_field_evidence_basis,
            **(
                {"primitive_hints": warm_field.get("primitive_hints", [])}
                if isinstance(warm_field.get("primitive_hints"), list)
                and warm_field.get("primitive_hints")
                else {}
            ),
        }

    primitive_field = state.get("primitive_field_if_any")
    if isinstance(primitive_field, dict):
        bridge["primitive_field"] = primitive_field
        bridge["primitive_semantics"] = summarize_primitive_semantics(
            primitive_field.get("active_primitives")
        )
        primitive_program = derive_primitive_program_candidate(
            state,
            problems,
            primitive_field_override=primitive_field,
        )
        if isinstance(primitive_program, dict):
            bridge["next_primitive_touch"] = primitive_program

    control_signals = derive_control_signals(
        state,
        problems,
        handoff_override=handoff,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
    )
    if isinstance(control_signals, dict):
        bridge["control_signals"] = control_signals

    return bridge


def derive_self_check_agenda(state: dict, problems: list[str]) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    output_status = state.get("output_status", {})
    rival = state.get("secondary_rival_if_any")
    current_seam = state.get("current_seam") or state.get("next_bite", "")
    focus = "carrier"
    reason = "keep the same carrier honest until one same-carrier change or tear lands"
    touch_target = state.get("current_object", "")
    preferred_kinds = ["write", "check"]

    bound_program = state.get("bound_program")
    gate_binding = state.get("gate_binding_if_any")
    primitive_field = state.get("primitive_field_if_any")

    if isinstance(bound_program, dict) or isinstance(gate_binding, dict):
        target = ""
        if isinstance(bound_program, dict):
            target = nonempty_text(bound_program.get("target"))
        if not target and isinstance(gate_binding, dict):
            target = nonempty_text(gate_binding.get("source_target"))
        if not target and isinstance(primitive_field, dict):
            target = nonempty_text(primitive_field.get("layer_object"))

        if isinstance(bound_program, dict) and nonempty_text(bound_program.get("target")) == nonempty_text(
            state.get("asked_medium_surface")
        ):
            focus = "asked_medium"
            reason = "the bound local move already touches the asked medium and should stay policed until it lands"
            touch_target = target or state.get("asked_medium_surface", "")
            preferred_kinds = [nonempty_text(bound_program.get("kind")) or "write", "readout"]
        else:
            focus = "carrier"
            reason = "a local program is already bound and should stay monitored until the same carrier really changes"
            touch_target = target or state.get("current_object", "")
            preferred_kinds = [nonempty_text(bound_program.get("kind")) or "write", "check"]

        return {
            "focus": focus,
            "reason": reason,
            "touch_target": touch_target,
            "preferred_kinds": preferred_kinds,
        }

    if isinstance(rival, dict):
        focus = "rival"
        reason = "a warm constructive rival still survives and needs a separating touch"
        touch_target = rival.get("object", "")
        preferred_kinds = ["witness", "check"]
    elif output_status.get("touched") is not True or output_status.get("cosmetic_only") is True:
        focus = "asked_medium"
        reason = "the asked medium still has not been touched honestly enough"
        touch_target = state.get("asked_medium_surface", "")
        preferred_kinds = ["write", "readout"]
    elif state.get("uncertainty_mode") in {"high", "mixed"}:
        focus = "seam"
        reason = "uncertainty is still live, so the cheapest seam-local separation should stay foregrounded"
        touch_target = current_seam
        preferred_kinds = ["witness", "check"]

    control_signals = derive_control_signals(state, problems)
    if isinstance(control_signals, dict):
        controller_view = control_signals.get("current_controller_view", {})
        operator_bias = control_signals.get("operator_bias", {})
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        probe_secondary = skill_first_probe_secondary(control_signals, focus=focus)
        favored_primitives = operator_bias.get("favored_primitives", [])
        cheap_check = nonempty_text(operator_bias.get("cheapest_reality_check"))
        shell_suspicion = controller_view.get("shell_suspicion") is True
        middle_object_risk = controller_view.get("middle_object_risk") is True
        reselection_needed = controller_view.get("reselection_needed") is True
        direct_closure_blocked = (
            isinstance(layerwise_pressure, dict)
            and layerwise_pressure.get("active") is True
            and layerwise_pressure.get("direct_closure_allowed") is not True
        )

        if reselection_needed and current_seam:
            focus = "seam"
            reason = nonempty_text(controller_view.get("why_now")) or reason
            touch_target = current_seam
            preferred_kinds = ["check", "readout"]
        elif middle_object_risk and not direct_closure_blocked:
            focus = "asked_medium"
            reason = nonempty_text(controller_view.get("why_now")) or reason
            touch_target = state.get("asked_medium_surface", "") or touch_target
            preferred_kinds = ["write", "readout"]
        elif shell_suspicion and current_seam:
            focus = "seam"
            reason = nonempty_text(controller_view.get("why_now")) or reason
            touch_target = current_seam
            preferred_kinds = ["check", "witness"]
        elif direct_closure_blocked:
            focus = "seam" if current_seam else "carrier"
            reason = nonempty_text(layerwise_pressure.get("reason")) or nonempty_text(
                controller_view.get("why_now")
            ) or reason
            touch_target = current_seam or touch_target
            preferred_kinds = ["check", "write"]

        if isinstance(favored_primitives, list):
            mapped_kinds = []
            if any(
                primitive in favored_primitives
                for primitive in [
                    "compare_without_calculating",
                    "boundary_as_route_finder",
                    "local_seam_controls_global",
                    "witness",
                    "special_value_probing",
                ]
            ):
                mapped_kinds.append("check")
            if any(
                primitive in favored_primitives
                for primitive in [
                    "definition_as_direct_readout",
                    "dominant_mechanism_readout",
                    "readout",
                    "projection_readout",
                ]
            ):
                mapped_kinds.append("readout")
            if direct_closure_blocked:
                mapped_kinds = [kind for kind in mapped_kinds if kind != "readout"]
            if mapped_kinds:
                preferred_kinds = mapped_kinds + [
                    kind for kind in preferred_kinds if kind not in mapped_kinds
                ]
        preferred_kinds = reorder_kinds_for_skill_first(
            preferred_kinds,
            focus=focus,
            probe_secondary=probe_secondary,
        )
        if cheap_check and not touch_target:
            touch_target = cheap_check

    return {
        "focus": focus,
        "reason": reason,
        "touch_target": touch_target,
        "preferred_kinds": preferred_kinds,
    }


def same_carrier_stalled(state: dict, previous_state: dict | None = None) -> bool:
    if not isinstance(previous_state, dict):
        return False

    keys = [
        "current_object",
        "current_seam",
        "current_debt",
        "next_bite",
        "asked_medium_surface",
        "primary_slot",
    ]
    return all(nonempty_text(state.get(key)) == nonempty_text(previous_state.get(key)) for key in keys)


def derive_layerwise_reselection_pressure(
    controller_view: object,
    primitive_control: object,
    *,
    current_seam: str = "",
    current_object: str = "",
    current_debt: str = "",
) -> dict:
    if not isinstance(controller_view, dict):
        return {
            "active": False,
            "level": "quiet",
            "reason": "",
            "direct_closure_allowed": True,
            "wake_primitives": [],
            "wake_skills": [],
            "reselect_on_next_layer": False,
        }

    carrier_status = nonempty_text(controller_view.get("carrier_status"))
    shell_suspicion = controller_view.get("shell_suspicion") is True
    middle_object_risk = controller_view.get("middle_object_risk") is True
    reselection_needed = controller_view.get("reselection_needed") is True

    selection_basis = ""
    evidence_basis = ""
    if isinstance(primitive_control, dict):
        selection_basis = nonempty_text(primitive_control.get("selection_basis"))
        evidence_basis = nonempty_text(primitive_control.get("evidence_basis"))

    weak_evidence = selection_basis == "text_fallback" or evidence_basis == "lexical_hint"
    active = bool(
        reselection_needed
        or shell_suspicion
        or middle_object_risk
        or (carrier_status != "thin_enough" and weak_evidence)
    )
    level = (
        "high"
        if reselection_needed or (shell_suspicion and middle_object_risk) or weak_evidence
        else "medium"
        if active
        else "quiet"
    )

    wake_primitives: list[str] = []
    wake_skills: list[str] = []
    if shell_suspicion:
        wake_primitives.extend(["witness", "projection"])
        wake_skills.extend(["grasp_essence", "counter_question"])
    if middle_object_risk:
        wake_primitives.extend(["state_split", "readout"])
        wake_skills.extend(["grasp_essence", "final_owner"])
    if reselection_needed:
        wake_primitives.extend(["state_split", "projection", "witness"])
        wake_skills.extend(["thinner_carrier_reselection", "counter_question"])
    if weak_evidence:
        wake_primitives.extend(["witness", "special_value_probing"])
        wake_skills.extend(["metacognition", "counter_question"])

    deduped_primitives = []
    for primitive in wake_primitives:
        if primitive in ALLOWED_PRIMITIVES and primitive not in deduped_primitives:
            deduped_primitives.append(primitive)
    deduped_skills = []
    for skill in wake_skills:
        if skill in ALLOWED_SKILLS and skill not in deduped_skills:
            deduped_skills.append(skill)

    reason = ""
    if active:
        reason = (
            nonempty_text(controller_view.get("why_now"))
            or current_seam
            or current_object
            or current_debt
        )

    return {
        "active": active,
        "level": level,
        "reason": reason,
        "direct_closure_allowed": not active,
        "wake_primitives": deduped_primitives[:3],
        "wake_skills": deduped_skills[:3],
        "reselect_on_next_layer": reselection_needed or shell_suspicion or middle_object_risk,
    }


def derive_bound_program_candidate(
    state: dict,
    problems: list[str],
    previous_state: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    agenda = derive_self_check_agenda(state, problems)
    if not isinstance(agenda, dict):
        return None

    if state.get("bound_program") is not None and not same_carrier_stalled(state, previous_state):
        return None

    def project_bound_program_shape(payload: dict) -> dict | None:
        if not isinstance(payload, dict):
            return None
        kind = nonempty_text(payload.get("kind"))
        target = nonempty_text(payload.get("target"))
        operation = nonempty_text(payload.get("operation"))
        success_signal = nonempty_text(payload.get("success_signal"))
        if not kind or not target or not operation:
            return None
        program = {
            "kind": kind,
            "target": target,
            "operation": operation,
        }
        if success_signal:
            program["success_signal"] = success_signal
        return program

    skill_authority = derive_skill_authority_bridge(state, problems)
    if isinstance(skill_authority, dict):
        executable_touch = skill_authority.get("executable_local_touch_if_any")
        winning_skill = nonempty_text(skill_authority.get("winning_skill_if_any"))
        if isinstance(executable_touch, dict) and winning_skill:
            projected = project_bound_program_shape(executable_touch)
            if isinstance(projected, dict):
                return projected

    primitive_program = derive_primitive_program_candidate(state, problems)
    if isinstance(primitive_program, dict):
        return primitive_program

    focus = agenda.get("focus")
    target = nonempty_text(agenda.get("touch_target"))
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))
    next_bite = nonempty_text(state.get("next_bite"))
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    seam = nonempty_text(state.get("current_seam")) or next_bite

    if focus == "asked_medium" and asked_medium:
        return {
            "kind": "write",
            "target": asked_medium,
            "operation": f"materialize {next_bite or current_debt} on the asked medium",
            "success_signal": f"asked medium touched at {asked_medium}",
        }

    if focus == "rival" and target:
        return {
            "kind": "witness",
            "target": target,
            "operation": f"separate the rival by landing {next_bite or current_debt}",
            "success_signal": f"rival at {target} is separated or killed",
        }

    if focus == "seam" and target:
        control_signals = derive_control_signals(state, problems)
        if skill_first_probe_secondary(control_signals, focus="seam"):
            return {
                "kind": "write",
                "target": current_object or target,
                "operation": f"compress {current_debt or next_bite} into one smaller exact carrier before probing {target}",
                "success_signal": f"smaller carrier became explicit on {current_object or target}",
            }
        return {
            "kind": "check",
            "target": target,
            "operation": f"run the cheapest separating check on {target} for {current_debt}",
            "success_signal": f"seam-local check on {target} changed the carrier or killed a line",
        }

    if seam:
        control_signals = derive_control_signals(state, problems)
        if skill_first_probe_secondary(control_signals, focus="seam"):
            return {
                "kind": "write",
                "target": current_object or seam,
                "operation": f"compress the live burden into one smaller truthful carrier before probing {seam}",
                "success_signal": f"smaller truthful carrier became explicit on {current_object or seam}",
            }
        return {
            "kind": "check",
            "target": seam,
            "operation": f"probe the current seam {seam}",
            "success_signal": f"current seam {seam} changed or sharpened",
        }

    return None


def derive_gate_binding_candidate(
    state: dict,
    problems: list[str],
    agenda_override: dict | None = None,
    winning_skill_override: str = "",
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    agenda = agenda_override if agenda_override is not None else derive_self_check_agenda(state, problems)
    if not isinstance(agenda, dict):
        return None

    focus = nonempty_text(agenda.get("focus"))
    target = nonempty_text(agenda.get("touch_target"))
    if not focus or not target:
        return None

    demoted = "better_wording_without_object_change"
    authority_until = "same_carrier_change"
    if focus == "seam":
        demoted = "same_carrier_explanation_without_separating_touch"
        authority_until = "exact_check"
    elif focus == "rival":
        demoted = "rival_narration_without_killing_or_binding"
        authority_until = "hostile_witness"
    elif focus == "asked_medium":
        demoted = "structure_talk_before_asked_medium_contact"
        authority_until = "asked_medium_failure"

    payload = {
        "source_focus": focus,
        "source_target": target,
        "demoted_continuation": demoted,
        "authority_until": authority_until,
    }
    owner_skill = canonicalize_skill_token(winning_skill_override)
    if owner_skill:
        payload["owner_skill_if_any"] = owner_skill
    return payload


def derive_handoff_candidate(state: dict, problems: list[str]) -> dict | None:
    if (
        problems
        or state.get("release_veto") is not True
        or state.get("bound_program") is not None
        or state.get("gate_binding_if_any") is not None
        or state.get("carrier_handoff_if_any") is not None
    ):
        return None

    next_bite = nonempty_text(state.get("next_bite"))
    current_object = nonempty_text(state.get("current_object"))
    current_seam = nonempty_text(state.get("current_seam"))
    current_debt = nonempty_text(state.get("current_debt"))
    rival = state.get("secondary_rival_if_any")
    competition = state.get("primitive_competition_if_any")
    control_signals = derive_control_signals(state, problems)
    favored_primitives: list[str] = []
    if isinstance(control_signals, dict):
        operator_bias = control_signals.get("operator_bias", {})
        if isinstance(operator_bias, dict):
            favored_primitives = merge_primitive_hints(
                operator_bias.get("favored_primitives")
            )

    if isinstance(competition, dict) and not primitive_competition_is_stale(state):
        candidates = competition.get("candidates")
        winner = nonempty_text(competition.get("winner_if_any"))
        layer_object = nonempty_text(competition.get("layer_object"))
        expected_object = expected_layer_object(state)
        if (
            isinstance(candidates, list)
            and len(candidates) > 1
            and not winner
            and layer_object
            and expected_object
            and layer_object == expected_object
        ):
            # Keep authority on the same current layer while explicit local
            # primitive competition is still live there. Otherwise the runtime
            # keeps fleeing into reselection before the current closure nucleus
            # has spent its structural bite.
            return None

    if not next_bite:
        return None

    if isinstance(rival, dict):
        rival_object = nonempty_text(rival.get("object"))
        rival_advantage = nonempty_text(rival.get("separating_advantage"))
        if rival_object:
            return {
                "trigger": "hostile_witness",
                "from_slot": nonempty_text(state.get("primary_slot")) or "current_slot",
                "to_object": rival_object,
                "winning_pressure": "rival-separating witness pressure",
                "why_local": rival_advantage
                or f"the current carrier still splits against a live rival on {rival_object}",
                "warm_field": {
                    "active_pressures": ["witness", "check"],
                    "cheap_check": nonempty_text(rival.get("bite")) or f"separate {rival_object}",
                    **(
                        {"primitive_hints": favored_primitives}
                        if favored_primitives
                        else {}
                    ),
                },
            }

    gap_object = derive_gap_object(state)
    if isinstance(gap_object, dict):
        gap_target = nonempty_text(gap_object.get("object"))
        if gap_target and gap_target not in {current_object, current_seam}:
            return {
                "trigger": "residue_inherited",
                "from_slot": nonempty_text(state.get("primary_slot")) or "current_slot",
                "to_object": gap_target,
                "winning_pressure": "explicit missing-gap inheritance",
                "why_local": (
                    nonempty_text(gap_object.get("why_local"))
                    or f"the current debt has sharpened into the smaller object {gap_target}"
                ),
                "warm_field": {
                    "active_pressures": ["state_split", "check"],
                    "cheap_check": nonempty_text(gap_object.get("cheap_check"))
                    or f"touch {gap_target}",
                    **(
                        {"primitive_hints": gap_object.get("primitive_hints", [])}
                        if isinstance(gap_object.get("primitive_hints"), list)
                        and gap_object.get("primitive_hints")
                        else {}
                    ),
                },
            }

    if state.get("uncertainty_mode") in {"high", "mixed"} and current_seam:
        if skill_first_probe_secondary(control_signals, focus="seam"):
            return {
                "trigger": "same_carrier_change",
                "from_slot": nonempty_text(state.get("primary_slot")) or "current_slot",
                "to_object": current_seam,
                "winning_pressure": "structural compression before seam probe",
                "why_local": (
                    f"uncertainty stays live on seam {current_seam}, but probe-like narrowing should stay "
                    "secondary until one smaller truthful carrier is made explicit first"
                ),
                "warm_field": {
                    "active_pressures": ["readout", "check"],
                    "cheap_check": f"compress onto {current_seam} before probing it",
                    **({"primitive_hints": favored_primitives} if favored_primitives else {}),
                },
            }
        return {
            "trigger": "exact_check",
            "from_slot": nonempty_text(state.get("primary_slot")) or "current_slot",
            "to_object": current_seam,
            "winning_pressure": "exact readout/check pressure",
            "why_local": f"uncertainty stays live on seam {current_seam}, so authority should narrow there",
            "warm_field": {
                "active_pressures": ["witness", "check"],
                "cheap_check": f"probe {current_seam}",
                **({"primitive_hints": favored_primitives} if favored_primitives else {}),
            },
        }

    if current_object and current_seam and current_seam != current_object:
        why_local = (
            f"the current burden '{current_debt or next_bite}' is now narrower on seam "
            f"{current_seam} than on the thicker object {current_object}"
        )
        if isinstance(control_signals, dict):
            controller_view = control_signals.get("current_controller_view", {})
            why_local = nonempty_text(controller_view.get("why_now")) or why_local
        return {
            "trigger": "same_carrier_change",
            "from_slot": nonempty_text(state.get("primary_slot")) or "current_slot",
            "to_object": current_seam,
            "winning_pressure": "thinner-carrier reselection pressure",
            "why_local": why_local,
            "warm_field": {
                "active_pressures": ["check", "readout"],
                "cheap_check": f"touch {current_seam}",
                **({"primitive_hints": favored_primitives} if favored_primitives else {}),
            },
        }

    return None


def derive_primitive_field_candidate(
    state: dict,
    problems: list[str],
    agenda_override: dict | None = None,
    handoff_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    control_signals = derive_control_signals(
        state,
        problems,
        handoff_override=handoff_override,
    )
    control_hints: list[str] = []
    control_check = ""
    control_why = ""
    pressure_hints: list[str] = []
    if isinstance(control_signals, dict):
        operator_bias = control_signals.get("operator_bias", {})
        controller_view = control_signals.get("current_controller_view", {})
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        probe_secondary = skill_first_probe_secondary(control_signals)
        if isinstance(operator_bias, dict):
            control_hints = merge_primitive_hints(operator_bias.get("favored_primitives"))
            control_check = nonempty_text(operator_bias.get("cheapest_reality_check"))
        if isinstance(controller_view, dict):
            control_why = nonempty_text(controller_view.get("why_now"))
        if isinstance(layerwise_pressure, dict) and layerwise_pressure.get("active") is True:
            pressure_hints = merge_primitive_hints(layerwise_pressure.get("wake_primitives"))

    gap_object = derive_gap_object(state)

    competition = state.get("primitive_competition_if_any")
    if isinstance(competition, dict):
        expected_object = expected_layer_object(
            state,
            agenda_override=agenda_override,
            handoff_override=handoff_override,
        )
        layer_object = nonempty_text(competition.get("layer_object")) or expected_object
        if expected_object and layer_object != expected_object:
            return None
        active_primitives, tie_break_check, selection_basis = derive_primitives_from_competition(
            competition
        )
        if not active_primitives:
            return None
        candidates = competition.get("candidates")
        why_now = "explicit local primitive competition is live on the current layer"
        if isinstance(candidates, list):
            gains = [
                nonempty_text(candidate.get("expected_local_gain"))
                for candidate in candidates
                if isinstance(candidate, dict) and nonempty_text(candidate.get("expected_local_gain"))
            ]
            if gains:
                why_now = "; ".join(gains[:2])
        return {
            "layer_object": layer_object,
            "active_primitives": active_primitives[:2],
            "why_now": why_now,
            "selection_basis": selection_basis,
            "evidence_basis": "state_witness" if tie_break_check else "cheap_check",
            **({"tie_break_check": tie_break_check} if tie_break_check else {}),
        }

    handoff = handoff_override if handoff_override is not None else state.get("carrier_handoff_if_any")
    if isinstance(handoff, dict):
        layer_object = (
            nonempty_text(handoff.get("to_object"))
            or (
                nonempty_text(gap_object.get("object"))
                if isinstance(gap_object, dict)
                else ""
            )
            or expected_layer_object(state, handoff_override=handoff)
        )
        explicit_hints: list[str] = []
        pressure_hints: list[str] = []
        active_primitives = []
        tie_break_check = None
        if isinstance(handoff.get("warm_field"), dict):
            explicit_hints = infer_primitives_from_pressure_hints(
                handoff["warm_field"].get("primitive_hints")
            )
            pressure_hints = infer_primitives_from_pressure_hints(
                handoff["warm_field"].get("active_pressures")
            )
            tie_break_check = nonempty_text(handoff["warm_field"].get("cheap_check"))
        if isinstance(gap_object, dict):
            explicit_hints = merge_primitive_hints(
                explicit_hints,
                gap_object.get("primitive_hints"),
            )
            if not tie_break_check:
                tie_break_check = nonempty_text(gap_object.get("cheap_check"))
        active_primitives.extend(explicit_hints)
        for primitive in merge_primitive_hints(explicit_hints, pressure_hints, control_hints):
            if primitive not in active_primitives:
                active_primitives.append(primitive)
            if len(active_primitives) == 2:
                break
        text_hints = infer_primitives_from_text(
            handoff.get("winning_pressure"),
            handoff.get("why_local"),
            handoff.get("warm_field", {}).get("active_pressures") if isinstance(handoff.get("warm_field"), dict) else None,
            state.get("next_bite"),
            state.get("current_debt"),
        )
        for primitive in text_hints:
            if primitive not in active_primitives:
                active_primitives.append(primitive)
            if len(active_primitives) == 2:
                break
        if not active_primitives:
            active_primitives = ["state_split"] if probe_secondary else ["witness"]
            if "readout" in infer_primitives_from_text(state.get("next_bite"), state.get("current_debt")):
                active_primitives.append("readout")
                text_hints = (["state_split", "readout"] if probe_secondary else ["witness", "readout"])
        active_primitives = reorder_primitives_for_skill_first(
            active_primitives,
            focus="asked_medium" if nonempty_text(state.get("asked_medium_surface")) and control_why else "",
            probe_secondary=probe_secondary,
        )
        selection_basis = classify_selection_basis(
            explicit_hints,
            pressure_hints,
            [],
            merge_primitive_hints(control_hints, text_hints),
            tie_break_check or control_check or "",
        )
        return {
            "layer_object": layer_object or nonempty_text(state.get("current_object")),
            "active_primitives": active_primitives[:2],
            "why_now": control_why
            or nonempty_text(handoff.get("why_local"))
            or "a thinner carrier has taken authority, so primitive competition should reopen locally",
            "selection_basis": selection_basis,
            "evidence_basis": (
                "explicit_hint"
                if explicit_hints and not pressure_hints and not text_hints
                else "mixed"
                if explicit_hints and (pressure_hints or text_hints)
                else "cheap_check"
                if tie_break_check
                else "state_witness"
                if pressure_hints or control_hints
                else "lexical_hint"
            ),
            **({"tie_break_check": tie_break_check or control_check} if (tie_break_check or control_check) else {}),
        }

    agenda = agenda_override if agenda_override is not None else derive_self_check_agenda(state, problems)
    layer_object = (
        nonempty_text(gap_object.get("object"))
        if isinstance(gap_object, dict)
        else ""
    ) or expected_layer_object(state, agenda_override=agenda)
    agenda_hints = infer_primitives_from_pressure_hints(
        agenda.get("preferred_kinds") if isinstance(agenda, dict) else None
    )
    text_hints = infer_primitives_from_text(
        state.get("next_bite"),
        state.get("current_debt"),
        gap_object.get("object") if isinstance(gap_object, dict) else None,
        state.get("current_object"),
        state.get("current_seam"),
        agenda.get("reason") if isinstance(agenda, dict) else None,
    )
    active_primitives = merge_primitive_hints(pressure_hints, control_hints, agenda_hints)
    for primitive in text_hints:
        if primitive not in active_primitives:
            active_primitives.append(primitive)
        if len(active_primitives) == 2:
            break

    if isinstance(agenda, dict):
        focus = nonempty_text(agenda.get("focus"))
        if focus in {"seam", "rival"} and "witness" not in active_primitives:
            active_primitives = ["witness"] + active_primitives
        elif focus == "asked_medium" and "readout" not in active_primitives:
            active_primitives = ["readout"] + active_primitives
        elif focus == "carrier" and "state_split" not in active_primitives:
            active_primitives = ["state_split"] + active_primitives
    else:
        focus = ""

    if pressure_hints:
        for pressure_primitive in reversed(pressure_hints):
            if pressure_primitive not in active_primitives:
                active_primitives = [pressure_primitive] + active_primitives

    active_primitives = reorder_primitives_for_skill_first(
        active_primitives,
        focus=focus,
        probe_secondary=probe_secondary if 'probe_secondary' in locals() else False,
    )

    deduped: list[str] = []
    for primitive in active_primitives:
        if primitive in ALLOWED_PRIMITIVES and primitive not in deduped:
            deduped.append(primitive)
        if len(deduped) == 2:
            break

    if not deduped:
        return None

    tie_break_check = None
    if isinstance(agenda, dict):
        tie_break_check = nonempty_text(agenda.get("touch_target"))
    selection_basis = classify_selection_basis(
        [],
        [],
        merge_primitive_hints(control_hints, agenda_hints),
        text_hints,
        tie_break_check or control_check or "",
    )

    return {
        "layer_object": layer_object,
        "active_primitives": deduped[:2],
        "why_now": control_why
        or (nonempty_text(agenda.get("reason")) if isinstance(agenda, dict) else "")
        or "the current carrier is still locally live",
        "selection_basis": selection_basis,
        "evidence_basis": (
            "cheap_check"
            if (tie_break_check or control_check)
            else "state_witness"
            if control_hints or agenda_hints
            else "lexical_hint"
        ),
        **({"tie_break_check": tie_break_check or control_check} if (tie_break_check or control_check) else {}),
    }


def has_materialization_evidence(state: dict) -> bool:
    evidence = state.get("materialization_evidence")
    return isinstance(evidence, dict) and all(
        isinstance(evidence.get(key), str) and evidence[key].strip()
        for key in ["kind", "location", "summary"]
    )


def derive_inhibition_state(
    state: dict,
    problems: list[str],
    agenda_override: dict | None = None,
    handoff_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    handoff = handoff_override if handoff_override is not None else state.get("carrier_handoff_if_any")
    agenda = agenda_override if agenda_override is not None else derive_self_check_agenda(state, problems)
    control_signals = derive_control_signals(
        state,
        problems,
        handoff_override=handoff,
    )
    probe_discipline = derive_probe_discipline(
        state,
        problems,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
    )

    owner = "same_carrier"
    promoted_move = None
    if isinstance(handoff, dict):
        owner = "reselection"
        promoted_move = {
            "focus": "reselection",
            "touch_target": handoff.get("to_object", ""),
            "preferred_kinds": ["check", "readout"],
        }
    elif isinstance(agenda, dict) and agenda.get("focus") == "rival":
        owner = "rival"
    elif isinstance(agenda, dict) and agenda.get("focus") == "asked_medium":
        owner = "asked_medium"
    elif isinstance(agenda, dict) and agenda.get("focus") == "seam":
        owner = "seam"
    elif not isinstance(agenda, dict):
        return None

    demoted_continuations = [
        "broad_reframing",
        "family_defense",
        "better_wording_without_object_change",
    ]
    if owner in {"rival", "seam"}:
        demoted_continuations.append("same_carrier_explanation_without_separating_touch")
    elif owner == "asked_medium":
        demoted_continuations.append("structure_talk_before_asked_medium_contact")
    else:
        demoted_continuations.append("rival_narration_without_killing_or_binding")

    if promoted_move is None:
        promoted_move = {
            "focus": agenda.get("focus", ""),
            "touch_target": agenda.get("touch_target", ""),
            "preferred_kinds": agenda.get("preferred_kinds", []),
        }
    gate_until = "same_carrier_change_or_kill_witness_or_exact_check"
    if owner == "asked_medium":
        gate_until = "asked_medium_touch_or_kill_witness_or_exact_check"
    elif owner == "reselection":
        gate_until = "handoff_bound_or_exact_check_or_kill_witness"

    if isinstance(control_signals, dict):
        meta_controls = control_signals.get("meta_controls", {})
        incentive_field = control_signals.get("incentive_field", {})
        micro_control_surface = control_signals.get("micro_control_surface", {})
        if isinstance(meta_controls, dict):
            if meta_controls.get("supervisory_pulse", {}).get("active") is True:
                if "closure_language_without_materialization" not in demoted_continuations:
                    demoted_continuations.append("closure_language_without_materialization")
            if meta_controls.get("god_view", {}).get("active") is True:
                if "ordinary_route_reconstruction" not in demoted_continuations:
                    demoted_continuations.append("ordinary_route_reconstruction")
            if meta_controls.get("closure_gate", {}).get("active") is True:
                gate_until = "asked_medium_contact_or_exact_executable_closure"
        if isinstance(incentive_field, dict):
            penalty_bias = incentive_field.get("penalty_bias", {})
            reward_bias = incentive_field.get("reward_bias", {})
            if isinstance(penalty_bias, dict):
                penalty_demote = nonempty_text(penalty_bias.get("demote"))
                if penalty_demote and penalty_demote not in demoted_continuations:
                    demoted_continuations.append(penalty_demote)
            if (
                isinstance(reward_bias, dict)
                and promoted_move is not None
                and nonempty_text(reward_bias.get("promote")) == "object_change_or_exact_readout"
            ):
                preferred = promoted_move.get("preferred_kinds")
                if isinstance(preferred, list):
                    ordered = ["write", "readout"] + [
                        kind for kind in preferred if kind not in {"write", "readout"}
                    ]
                    promoted_move["preferred_kinds"] = ordered[:3]
        if isinstance(micro_control_surface, dict):
            closure_pull = micro_control_surface.get("closure_pull", {})
            reward_bias = micro_control_surface.get("reward_bias", {})
            penalty_bias = micro_control_surface.get("penalty_bias", {})
            supervision_pulse = micro_control_surface.get("supervision_pulse", {})
            counter_question = micro_control_surface.get("counter_question", {})
            if isinstance(closure_pull, dict) and closure_pull.get("active") is True:
                gate_until = (
                    "asked_medium_contact_or_exact_executable_closure"
                    if nonempty_text(closure_pull.get("target")) == state.get("asked_medium_surface")
                    else nonempty_text(supervision_pulse.get("until"))
                    or "asked_medium_contact_or_exact_executable_closure"
                )
            if isinstance(penalty_bias, dict):
                for penalty_demote in penalty_bias.get("demote", []):
                    penalty_text = nonempty_text(penalty_demote)
                    if penalty_text and penalty_text not in demoted_continuations:
                        demoted_continuations.append(penalty_text)
            if isinstance(counter_question, dict) and promoted_move is not None:
                target = nonempty_text(counter_question.get("target"))
                preferred_kind = nonempty_text(counter_question.get("preferred_answer_kind"))
                if target and owner in {"same_carrier", "seam", "rival"}:
                    promoted_move["touch_target"] = target
                preferred = promoted_move.get("preferred_kinds")
                if isinstance(preferred, list) and preferred_kind:
                    ordered = [preferred_kind] + [
                        kind for kind in preferred if kind != preferred_kind
                    ]
                    promoted_move["preferred_kinds"] = ordered[:3]
            if isinstance(reward_bias, dict) and promoted_move is not None:
                reward_promote = [
                    nonempty_text(value)
                    for value in reward_bias.get("promote", [])
                    if nonempty_text(value)
                ]
                preferred = promoted_move.get("preferred_kinds")
                if isinstance(preferred, list):
                    translated: list[str] = []
                    mapping = {
                        "exact_readout": "readout",
                        "same_carrier_change": "write",
                        "object_change": "write",
                        "separating_check": "check",
                        "thinner_carrier_reduction": "check",
                    }
                    for token in reward_promote:
                        mapped = mapping.get(token)
                        if mapped and mapped not in translated:
                            translated.append(mapped)
                    ordered = translated + [kind for kind in preferred if kind not in translated]
                    if ordered:
                        promoted_move["preferred_kinds"] = ordered[:3]
            if (
                isinstance(supervision_pulse, dict)
                and nonempty_text(supervision_pulse.get("owner")) == "closure"
                and promoted_move is not None
            ):
                promoted_move["focus"] = "asked_medium"
                if state.get("asked_medium_surface"):
                    promoted_move["touch_target"] = state.get("asked_medium_surface")
        if (
            isinstance(probe_discipline, dict)
            and probe_discipline.get("probe_must_bind") is True
            and probe_discipline.get("unbound_probe_is_drift") is True
            and not nonempty_text(probe_discipline.get("active_skill_hypothesis"))
        ):
            drift_signal = nonempty_text(probe_discipline.get("drift_signal")) or "pattern_probe_without_skill_binding"
            if drift_signal not in demoted_continuations:
                demoted_continuations.append(drift_signal)

    payload = {
        "owner": owner,
        "promoted_move": promoted_move,
        "demoted_continuations": demoted_continuations,
        "gate_until": gate_until,
        "source": "release_veto_local_inhibition",
    }
    if isinstance(control_signals, dict):
        payload["meta_controls"] = control_signals.get("meta_controls", {})
        payload["incentive_field"] = control_signals.get("incentive_field", {})
        payload["micro_control_surface"] = control_signals.get("micro_control_surface", {})
    if isinstance(probe_discipline, dict):
        payload["probe_discipline"] = probe_discipline
    return payload


def derive_skill_field(
    state: dict,
    problems: list[str],
    primitive_field_override: dict | None = None,
    control_signals_override: dict | None = None,
    closure_nucleus_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None
    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    bound_program = state.get("bound_program")
    control_signals = (
        control_signals_override
        if control_signals_override is not None
        else derive_control_signals(
            state,
            problems,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        )
    )
    closure_nucleus = (
        closure_nucleus_override
        if closure_nucleus_override is not None
        else derive_closure_nucleus(
            state,
            problems,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        )
    )

    active_skills: list[str] = []
    if isinstance(primitive_field, dict):
        for primitive in primitive_field.get("active_primitives", []):
            canonical = canonicalize_skill_token(primitive)
            if canonical and canonical not in active_skills:
                active_skills.append(canonical)

    if isinstance(control_signals, dict):
        controller_view = control_signals.get("current_controller_view", {})
        meta_controls = control_signals.get("meta_controls", {})
        incentive_field = control_signals.get("incentive_field", {})
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        if isinstance(controller_view, dict):
            if controller_view.get("shell_suspicion") is True and "shell_suspicion" not in active_skills:
                active_skills.append("shell_suspicion")
            if nonempty_text(controller_view.get("owner_status")) in {"narrowing", "locked"} and "final_owner" not in active_skills:
                active_skills.append("final_owner")
            if nonempty_text(controller_view.get("essence_status")) in {"controller_emerging", "controller_visible"} and "grasp_essence" not in active_skills:
                active_skills.append("grasp_essence")
            if controller_view.get("reselection_needed") is True and "thinner_carrier_reselection" not in active_skills:
                active_skills.append("thinner_carrier_reselection")
        if isinstance(meta_controls, dict):
            if meta_controls.get("counter_question", {}).get("active") is True:
                active_skills.append("counter_question")
            if meta_controls.get("closure_gate", {}).get("active") is True:
                active_skills.append("exact_closure")
            if meta_controls.get("supervisory_pulse", {}).get("active") is True:
                active_skills.append("supervision")
            if meta_controls.get("metacognition", {}).get("active") is True:
                active_skills.append("metacognition")
            if isinstance(meta_controls.get("central_control"), dict):
                active_skills.append("central_control")
            if meta_controls.get("hindbrain_guard", {}).get("active") is True:
                active_skills.append("hindbrain_guard")
        if isinstance(incentive_field, dict) and "reward_penalty_shaping" not in active_skills:
            active_skills.append("reward_penalty_shaping")
        if isinstance(layerwise_pressure, dict) and layerwise_pressure.get("active") is True:
            for skill in layerwise_pressure.get("wake_skills", []):
                if skill in ALLOWED_SKILLS and skill not in active_skills:
                    active_skills.append(skill)

    deduped = []
    for skill in active_skills:
        if skill in ALLOWED_SKILLS and skill not in deduped:
            deduped.append(skill)
    active_skills = deduped
    full_active_skills = list(active_skills)

    bound_skill = derive_skill_authority_bridge(
        state,
        problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
    )
    if isinstance(bound_program, dict) and isinstance(bound_skill, dict):
        winning_skill = nonempty_text(bound_skill.get("winning_skill_if_any"))
        compressed: list[str] = []
        if winning_skill:
            compressed.append(winning_skill)
        for control_skill in [
            "exact_closure",
            "counter_question",
            "supervision",
            "metacognition",
            "hindbrain_guard",
        ]:
            if control_skill in active_skills and control_skill not in compressed:
                compressed.append(control_skill)
        active_skills = compressed or active_skills

    if not active_skills:
        return None

    payload = {
        "layer_object": (
            primitive_field.get("layer_object")
            if isinstance(primitive_field, dict)
            else nonempty_text(state.get("current_object")) or nonempty_text(state.get("current_debt"))
        ),
        "active_skills": active_skills,
        "why_now": (
            primitive_field.get("why_now")
            if isinstance(primitive_field, dict)
            else nonempty_text(state.get("current_debt")) or "the current layer still needs local skill-capability ownership"
        ),
        "selection_basis": (
            primitive_field.get("selection_basis")
            if isinstance(primitive_field, dict)
            else "control_surface"
        ),
        "evidence_basis": (
            primitive_field.get("evidence_basis")
            if isinstance(primitive_field, dict)
            else "state_witness"
        ),
        "full_active_skills": full_active_skills,
    }
    if isinstance(closure_nucleus, dict):
        payload["closure_authority_skill_if_any"] = (
            "exact_closure" if closure_nucleus.get("closure_gate_active") is True else ""
        )
    if isinstance(bound_program, dict) and isinstance(bound_skill, dict):
        payload["bound_skill_if_any"] = nonempty_text(bound_skill.get("winning_skill_if_any"))
        background_skills = [
            skill for skill in full_active_skills if skill not in active_skills
        ]
        if background_skills:
            payload["background_skills_if_any"] = background_skills
    return payload


def rank_skill_candidate_for_current_layer(
    skill: str,
    *,
    touch_target: str = "",
    asked_medium: str = "",
    direct_closure_allowed: bool = True,
    current_seam: str = "",
    current_object: str = "",
) -> tuple[int, int, int]:
    canonical = canonicalize_skill_token(skill)
    if not canonical:
        return (9, 9, 9)

    if canonical == "exact_closure":
        return ((0, 0, 0) if direct_closure_allowed else (8, 0, 0))
    if canonical == "counter_question":
        return (7, 0, 0)

    if canonical in {
        "state_split",
        "projection",
        "canonical_normalization",
        "common_value_compression",
        "compatibility",
        "conservation",
        "function_archetype_matching",
        "matching_instead_of_probability",
        "grid_selection_permutation",
        "model_calling_before_derivation",
        "reverse",
        "picture",
        "definition_as_direct_readout",
        "dominant_mechanism_readout",
        "vector_difference_readout",
        "projection_readout",
        "readout",
    }:
        base = 1
    elif canonical in {
        "grasp_essence",
        "final_owner",
        "thinner_carrier_reselection",
        "shell_suspicion",
        "metacognition",
    }:
        base = 2
    elif canonical in {
        "assignment",
        "special_value_probing",
        "compare_without_calculating",
        "witness",
        "boundary_as_route_finder",
        "local_seam_controls_global",
        "limit_boundary",
        "symmetry",
        "symmetry_as_variable_killer",
    }:
        base = 5
    else:
        base = 4

    target_bonus = 0
    if asked_medium and touch_target == asked_medium and direct_closure_allowed:
        target_bonus = -1
    elif current_seam and touch_target == current_seam:
        target_bonus = 0
    elif current_object and touch_target == current_object:
        target_bonus = 1

    probe_penalty = 1 if canonicalize_primitive_token(canonical) in PROBE_LIKE_PRIMITIVES else 0
    return (base, target_bonus, probe_penalty)


def derive_skill_competition(
    state: dict,
    problems: list[str],
    primitive_competition_override: dict | None = None,
    primitive_field_override: dict | None = None,
    control_signals_override: dict | None = None,
    closure_nucleus_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None
    primitive_competition = (
        primitive_competition_override
        if primitive_competition_override is not None
        else state.get("primitive_competition_if_any")
    )
    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    control_signals = (
        control_signals_override
        if control_signals_override is not None
        else derive_control_signals(state, problems)
    )
    closure_nucleus = (
        closure_nucleus_override
        if closure_nucleus_override is not None
        else derive_closure_nucleus(
            state,
            problems,
            primitive_competition_override=primitive_competition if isinstance(primitive_competition, dict) else None,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        )
    )

    candidates: list[dict] = []
    if isinstance(primitive_competition, dict):
        for candidate in primitive_competition.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            skill = canonicalize_skill_token(candidate.get("primitive"))
            if skill:
                candidates.append(
                    {
                        "skill": skill,
                        "touch_target": nonempty_text(candidate.get("touch_target")),
                        "expected_local_gain": nonempty_text(candidate.get("expected_local_gain")),
                        "backed_by": "primitive",
                    }
                )

    micro_control_surface = (
        control_signals.get("micro_control_surface", {})
        if isinstance(control_signals, dict)
        else {}
    )
    counter_surface = (
        micro_control_surface.get("counter_question", {})
        if isinstance(micro_control_surface, dict)
        else {}
    )
    if isinstance(control_signals, dict):
        meta_controls = control_signals.get("meta_controls", {})
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        if isinstance(meta_controls, dict):
            if meta_controls.get("closure_gate", {}).get("active") is True:
                candidates.append(
                    {
                        "skill": "exact_closure",
                        "touch_target": nonempty_text(state.get("asked_medium_surface")),
                        "expected_local_gain": "deny release drift and force exact asked-medium contact",
                        "backed_by": "control",
                    }
                )
            if meta_controls.get("counter_question", {}).get("active") is True:
                candidates.append(
                    {
                        "skill": "counter_question",
                        "touch_target": nonempty_text(counter_surface.get("target"))
                        or nonempty_text(
                            meta_controls.get("counter_question", {}).get("target")
                        )
                        or nonempty_text(state.get("revocation_handle"))
                        or nonempty_text(state.get("current_seam"))
                        or nonempty_text(state.get("current_object")),
                        "expected_local_gain": "kill decorative progress with one cheap falsifier",
                        "backed_by": "control",
                    }
                )
        if isinstance(layerwise_pressure, dict) and layerwise_pressure.get("active") is True:
            for skill in layerwise_pressure.get("wake_skills", []):
                skill_name = canonicalize_skill_token(skill)
                if not skill_name:
                    continue
                candidates.append(
                    {
                        "skill": skill_name,
                        "touch_target": nonempty_text(state.get("current_seam"))
                        or nonempty_text(state.get("current_object"))
                        or nonempty_text(state.get("current_debt")),
                        "expected_local_gain": nonempty_text(layerwise_pressure.get("reason"))
                        or "the current layer still looks thick enough to require primitive reselection",
                        "backed_by": "layerwise_reselection_pressure",
                    }
                )

    deduped: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for candidate in candidates:
        key = (candidate.get("skill", ""), candidate.get("touch_target", ""))
        if candidate.get("skill") and key not in seen:
            seen.add(key)
            deduped.append(candidate)
    candidates = deduped
    if len(candidates) < 2:
        return None

    winning_skill = ""
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    current_seam = nonempty_text(state.get("current_seam"))
    current_object = nonempty_text(state.get("current_object"))
    direct_closure_allowed = True
    layerwise_pressure = {}
    meta_controls = control_signals.get("meta_controls", {}) if isinstance(control_signals, dict) else {}
    if isinstance(control_signals, dict):
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        direct_closure_allowed = not (
            isinstance(layerwise_pressure, dict)
            and layerwise_pressure.get("active") is True
            and layerwise_pressure.get("direct_closure_allowed") is not True
        )
    counter_question = meta_controls.get("counter_question", {}) if isinstance(meta_controls, dict) else {}
    counter_target = (
        nonempty_text(counter_surface.get("target"))
        or nonempty_text(counter_question.get("target"))
        or (
            nonempty_text(closure_nucleus.get("separating_check_if_any"))
            if isinstance(closure_nucleus, dict)
            else ""
        )
        or current_seam
        or current_object
    )
    counter_kind = (
        nonempty_text(counter_surface.get("preferred_answer_kind"))
        or nonempty_text(counter_question.get("preferred_answer_kind"))
    )
    explicit_primitive_winner = (
        nonempty_text(primitive_competition.get("winner_if_any"))
        if isinstance(primitive_competition, dict)
        else ""
    )
    active_primitives = []
    if isinstance(primitive_field, dict):
        raw_active_primitives = primitive_field.get("active_primitives")
        if isinstance(raw_active_primitives, list):
            active_primitives = [
                canonicalize_primitive_token(value)
                for value in raw_active_primitives
                if canonicalize_primitive_token(value)
            ]
    structural_primitives_live = [
        primitive for primitive in active_primitives if primitive not in PROBE_LIKE_PRIMITIVES
    ]
    counter_can_take_first_shot = (
        isinstance(counter_question, dict)
        and counter_question.get("active") is True
        and counter_target
        and counter_kind in {"check", "witness"}
        and not explicit_primitive_winner
        and not structural_primitives_live
    )

    if (
        isinstance(closure_nucleus, dict)
        and closure_nucleus.get("closure_gate_active") is True
        and direct_closure_allowed
    ):
        winning_skill = "exact_closure"
    elif counter_can_take_first_shot:
        winning_skill = "counter_question"
    elif candidates:
        candidate_skills = []
        if isinstance(primitive_field, dict):
            raw_active = primitive_field.get("active_primitives")
            if isinstance(raw_active, list):
                for value in raw_active:
                    canonical = canonicalize_skill_token(value)
                    if canonical and canonical not in candidate_skills:
                        candidate_skills.append(canonical)
        for candidate in candidates:
            skill = canonicalize_skill_token(candidate.get("skill"))
            if skill and skill not in candidate_skills:
                candidate_skills.append(skill)
        if candidate_skills:
            ordered_skills = sorted(
                candidate_skills,
                key=lambda skill: rank_skill_candidate_for_current_layer(
                    skill,
                    touch_target=next(
                        (
                            nonempty_text(candidate.get("touch_target"))
                            for candidate in candidates
                            if canonicalize_skill_token(candidate.get("skill")) == skill
                        ),
                        current_seam or current_object or asked_medium,
                    ),
                    asked_medium=asked_medium,
                    direct_closure_allowed=direct_closure_allowed,
                    current_seam=current_seam,
                    current_object=current_object,
                ),
            )
            if ordered_skills:
                winning_skill = ordered_skills[0]

    return {
        "layer_object": nonempty_text(state.get("current_object")) or nonempty_text(state.get("current_debt")),
        "candidates": candidates[:6],
        "separating_check": (
            nonempty_text(closure_nucleus.get("separating_check_if_any"))
            if isinstance(closure_nucleus, dict)
            else nonempty_text(primitive_competition.get("separating_check")) if isinstance(primitive_competition, dict) else ""
        ),
        "winning_skill_if_any": winning_skill,
    }


def derive_probe_discipline(
    state: dict,
    problems: list[str],
    *,
    primitive_field_override: dict | None = None,
    control_signals_override: dict | None = None,
    skill_field_override: dict | None = None,
    skill_competition_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    control_signals = (
        control_signals_override
        if control_signals_override is not None
        else derive_control_signals(
            state,
            problems,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        )
    )
    skill_field = (
        skill_field_override
        if skill_field_override is not None
        else derive_skill_field(
            state,
            problems,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        )
    )
    skill_competition = (
        skill_competition_override
        if skill_competition_override is not None
        else derive_skill_competition(
            state,
            problems,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        )
    )

    non_hypothesis_skills = {
        "exact_closure",
        "counter_question",
        "supervision",
        "metacognition",
        "central_control",
        "hindbrain_guard",
        "reward_penalty_shaping",
    }

    active_primitives: list[str] = []
    if isinstance(primitive_field, dict):
        raw_primitives = primitive_field.get("active_primitives")
        if isinstance(raw_primitives, list):
            active_primitives = [
                canonicalize_primitive_token(value)
                for value in raw_primitives
                if canonicalize_primitive_token(value)
            ]
    active_probe_primitives = [
        primitive for primitive in active_primitives if primitive in PROBE_LIKE_PRIMITIVES
    ]

    meta_controls = control_signals.get("meta_controls", {}) if isinstance(control_signals, dict) else {}
    micro_control_surface = (
        control_signals.get("micro_control_surface", {})
        if isinstance(control_signals, dict)
        else {}
    )
    counter_surface = (
        micro_control_surface.get("counter_question", {})
        if isinstance(micro_control_surface, dict)
        else {}
    )
    counter_question = meta_controls.get("counter_question", {}) if isinstance(meta_controls, dict) else {}
    probe_like = bool(active_probe_primitives) or (
        isinstance(counter_question, dict) and counter_question.get("active") is True
    )
    if not probe_like:
        return None

    preferred_probe_target = (
        nonempty_text(counter_surface.get("target"))
        or nonempty_text(counter_question.get("target"))
        or (nonempty_text(primitive_field.get("tie_break_check")) if isinstance(primitive_field, dict) else "")
        or nonempty_text(state.get("current_seam"))
        or nonempty_text(state.get("current_object"))
    )
    candidate_hypotheses: list[str] = []
    winning_hypothesis = ""
    gate_binding = state.get("gate_binding_if_any")
    bound_program = state.get("bound_program")
    gate_owner = ""
    if isinstance(gate_binding, dict) and isinstance(bound_program, dict):
        gate_owner = canonicalize_skill_token(gate_binding.get("owner_skill_if_any"))
        if not gate_owner:
            gate_focus = nonempty_text(gate_binding.get("source_focus"))
            bound_kind = nonempty_text(bound_program.get("kind"))
            asked_medium = nonempty_text(state.get("asked_medium_surface"))
            bound_target = nonempty_text(bound_program.get("target"))
            if gate_focus == "asked_medium" or (asked_medium and bound_target == asked_medium):
                gate_owner = "exact_closure"
            elif gate_focus in {"seam", "rival"} and bound_kind in {"check", "witness"}:
                gate_owner = "counter_question"
    counter_kind = (
        nonempty_text(counter_surface.get("preferred_answer_kind"))
        or nonempty_text(counter_question.get("preferred_answer_kind"))
    )
    if gate_owner:
        winning_hypothesis = gate_owner
    if isinstance(skill_competition, dict):
        winning = canonicalize_skill_token(skill_competition.get("winning_skill_if_any"))
        if winning_hypothesis:
            pass
        elif (
            winning == "counter_question"
            and preferred_probe_target
            and counter_kind in {"check", "witness"}
        ):
            winning_hypothesis = winning
        elif winning and winning not in non_hypothesis_skills:
            winning_hypothesis = winning
        for candidate in skill_competition.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            skill = canonicalize_skill_token(candidate.get("skill"))
            if skill and skill not in non_hypothesis_skills and skill not in candidate_hypotheses:
                candidate_hypotheses.append(skill)

    if isinstance(skill_field, dict):
        for skill in skill_field.get("active_skills", []):
            canonical = canonicalize_skill_token(skill)
            if (
                canonical
                and canonical not in non_hypothesis_skills
                and canonical != "readout"
                and canonical not in candidate_hypotheses
            ):
                candidate_hypotheses.append(canonical)

    binding_strength = "explicit_winner" if winning_hypothesis else "unbound"

    allowed_probe_kinds = ["check", "witness"]
    if any(primitive in {"assignment", "special_value_probing"} for primitive in active_primitives):
        allowed_probe_kinds.append("write")

    unbound = not winning_hypothesis
    reason = (
        f"tiny probe work on {preferred_probe_target} should serve the live skill hypothesis {winning_hypothesis}"
        if winning_hypothesis
        else "current probe pressure has no live skill hypothesis binding yet"
    )

    payload = {
        "active": True,
        "probe_must_bind": True,
        "unbound_probe_is_drift": True,
        "probe_like_primitives": active_probe_primitives[:3],
        "preferred_probe_target": preferred_probe_target,
        "allowed_probe_kinds": allowed_probe_kinds[:3],
        "candidate_skill_hypotheses": candidate_hypotheses[:4],
        "active_skill_hypothesis": winning_hypothesis,
        "hypothesis_binding_strength": binding_strength,
        "reason": reason,
    }
    if unbound:
        payload["drift_signal"] = "pattern_probe_without_skill_binding"
    return payload


def derive_skill_inhibition(
    state: dict,
    problems: list[str],
    inhibition_override: dict | None = None,
    skill_field_override: dict | None = None,
    skill_competition_override: dict | None = None,
    closure_nucleus_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None
    inhibition = (
        inhibition_override
        if inhibition_override is not None
        else derive_inhibition_state(state, problems)
    )
    skill_field = (
        skill_field_override
        if skill_field_override is not None
        else derive_skill_field(state, problems)
    )
    skill_competition = (
        skill_competition_override
        if skill_competition_override is not None
        else derive_skill_competition(state, problems)
    )
    closure_nucleus = (
        closure_nucleus_override
        if closure_nucleus_override is not None
        else derive_closure_nucleus(state, problems)
    )
    if not isinstance(skill_field, dict) or not isinstance(inhibition, dict):
        return None

    gate_binding = state.get("gate_binding_if_any")
    bound_program = state.get("bound_program")
    demoted_skills: list[str] = []
    for raw in inhibition.get("demoted_continuations", []):
        text = nonempty_text(raw)
        if "ordinary_route_reconstruction" in text and "thinner_carrier_reselection" not in demoted_skills:
            demoted_skills.append("thinner_carrier_reselection")
        if "decorative_continuation_without_contact" in text and "exact_closure" not in demoted_skills:
            demoted_skills.append("exact_closure")
        if "better_wording_without_object_change" in text and "grasp_essence" not in demoted_skills:
            demoted_skills.append("grasp_essence")

    winning = ""
    if isinstance(skill_competition, dict):
        winning = nonempty_text(skill_competition.get("winning_skill_if_any"))
    gate_owner = ""
    if isinstance(gate_binding, dict) and isinstance(bound_program, dict):
        gate_owner = canonicalize_skill_token(gate_binding.get("owner_skill_if_any"))
        if not gate_owner:
            gate_focus = nonempty_text(gate_binding.get("source_focus"))
            bound_kind = nonempty_text(bound_program.get("kind"))
            asked_medium = nonempty_text(state.get("asked_medium_surface"))
            bound_target = nonempty_text(bound_program.get("target"))
            if gate_focus == "asked_medium" or (asked_medium and bound_target == asked_medium):
                gate_owner = "exact_closure"
            elif gate_focus in {"seam", "rival"} and bound_kind in {"check", "witness"}:
                gate_owner = "counter_question"
    if gate_owner:
        winning = gate_owner
    if (
        not winning
        and isinstance(closure_nucleus, dict)
        and closure_nucleus.get("closure_gate_active") is True
        and closure_nucleus.get("readout_deferred_by_layerwise_pressure") is not True
    ):
        winning = "exact_closure"
    promoted = (
        "exact_closure"
        if nonempty_text(inhibition.get("gate_until")) == "asked_medium_contact_or_exact_executable_closure"
        else winning
    )
    if promoted:
        demoted_skills = [skill for skill in demoted_skills if skill != promoted]
    if winning:
        demoted_skills = [skill for skill in demoted_skills if skill != winning]

    return {
        "owner": nonempty_text(inhibition.get("owner")),
        "promoted_skill_if_any": promoted,
        "demoted_skills": demoted_skills,
        "gate_until": nonempty_text(inhibition.get("gate_until")),
        "winning_skill_if_any": winning,
    }


def derive_skill_authority_bridge(
    state: dict,
    problems: list[str],
    primitive_field_override: dict | None = None,
    skill_competition_override: dict | None = None,
    closure_nucleus_override: dict | None = None,
    control_signals_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    control_signals = (
        control_signals_override
        if control_signals_override is not None
        else derive_control_signals(
            state,
            problems,
            primitive_field_override=(
                primitive_field_override
                if isinstance(primitive_field_override, dict)
                else None
            ),
        )
    )
    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    closure_nucleus = (
        closure_nucleus_override
        if closure_nucleus_override is not None
        else derive_closure_nucleus(
            state,
            problems,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        )
    )
    skill_competition = (
        skill_competition_override
        if skill_competition_override is not None
        else derive_skill_competition(
            state,
            problems,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
            closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        )
    )
    winning_skill = ""
    if isinstance(skill_competition, dict):
        winning_skill = nonempty_text(skill_competition.get("winning_skill_if_any"))
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    closure_waiting_on_structural_discharge = closure_should_wait_for_structural_discharge(
        closure_nucleus=closure_nucleus,
        control_signals=control_signals,
        asked_medium=asked_medium,
    )

    bridge_touch = None
    if isinstance(closure_nucleus, dict):
        structural = closure_nucleus.get("current_structural_bite_if_any")
        readout = closure_nucleus.get("current_readout_bite_if_any")
        if (
            winning_skill == "exact_closure"
            and not closure_waiting_on_structural_discharge
            and isinstance(readout, dict)
        ):
            bridge_touch = readout
        elif winning_skill == "counter_question":
            meta_controls = control_signals.get("meta_controls", {}) if isinstance(control_signals, dict) else {}
            micro_control_surface = (
                control_signals.get("micro_control_surface", {})
                if isinstance(control_signals, dict)
                else {}
            )
            counter_surface = (
                micro_control_surface.get("counter_question", {})
                if isinstance(micro_control_surface, dict)
                else {}
            )
            counter_question = (
                meta_controls.get("counter_question", {}) if isinstance(meta_controls, dict) else {}
            )
            separating_check = nonempty_text(closure_nucleus.get("separating_check_if_any"))
            counter_target = (
                separating_check
                or nonempty_text(counter_surface.get("target"))
                or nonempty_text(counter_question.get("target"))
                or nonempty_text(state.get("current_seam"))
                or nonempty_text(state.get("current_object"))
            )
            counter_kind = (
                nonempty_text(counter_surface.get("preferred_answer_kind"))
                or nonempty_text(counter_question.get("preferred_answer_kind"))
            )
            if counter_kind not in {"check", "witness"}:
                counter_kind = "check"
            if counter_target:
                bridge_touch = {
                    "kind": counter_kind,
                    "target": counter_target,
                    "operation": (
                        f"land one hostile witness on {counter_target}"
                        if counter_kind == "witness"
                        else f"land one hostile separating check on {counter_target}"
                    ),
                    "success_signal": (
                        f"hostile witness on {counter_target} killed decorative progress"
                        if counter_kind == "witness"
                        else f"separating check on {counter_target} killed decorative progress"
                    ),
                }
        elif winning_skill and isinstance(structural, dict):
            bridge_touch = structural

    if not bridge_touch:
        primitive_program = derive_primitive_program_candidate(
            state,
            problems,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        )
        if isinstance(primitive_program, dict):
            if (
                not winning_skill
                and closure_waiting_on_structural_discharge
                and program_is_direct_closure_like(
                    primitive_program,
                    asked_medium=asked_medium,
                )
            ):
                primitive_program = None
        if isinstance(primitive_program, dict):
            bridge_touch = primitive_program
            if not winning_skill and isinstance(primitive_field, dict):
                primitives = primitive_field.get("active_primitives")
                if isinstance(primitives, list) and primitives:
                    ordered = reorder_primitives_for_skill_first(
                        primitives,
                        focus="asked_medium" if asked_medium else "",
                        probe_secondary=skill_first_probe_secondary(control_signals),
                    )
                    if ordered:
                        fallback_skill_hint = canonicalize_skill_token(ordered[0])

    if not isinstance(bridge_touch, dict):
        return None

    supporting_skills: list[str] = []
    if isinstance(skill_competition, dict):
        for candidate in skill_competition.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            skill_name = canonicalize_skill_token(candidate.get("skill"))
            if skill_name and skill_name != winning_skill and skill_name not in supporting_skills:
                supporting_skills.append(skill_name)
    if isinstance(primitive_field, dict):
        for primitive in primitive_field.get("active_primitives", []):
            skill_name = canonicalize_skill_token(primitive)
            if skill_name and skill_name != winning_skill and skill_name not in supporting_skills:
                supporting_skills.append(skill_name)

    payload = {
        "winning_skill_if_any": winning_skill,
        "executable_local_touch_if_any": bridge_touch,
        "silence_after_contact": True,
        "same_carrier_only": not isinstance(state.get("carrier_handoff_if_any"), dict),
    }
    if supporting_skills:
        payload["supporting_skills_if_any"] = supporting_skills[:4]
    if "fallback_skill_hint" in locals() and fallback_skill_hint:
        payload["fallback_skill_hint_if_any"] = fallback_skill_hint
    return payload


def derive_interlayer_discharge_bridge(
    state: dict,
    problems: list[str],
    primitive_field_override: dict | None = None,
    control_signals_override: dict | None = None,
    skill_authority_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    handoff = state.get("carrier_handoff_if_any")
    if not isinstance(handoff, dict):
        return None

    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    primitive_program = derive_primitive_program_candidate(
        state,
        problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
    )
    if not isinstance(primitive_program, dict):
        return None

    skill_authority = (
        skill_authority_override
        if skill_authority_override is not None
        else derive_skill_authority_bridge(
            state,
            problems,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
            control_signals_override=control_signals_override,
        )
    )
    if not isinstance(skill_authority, dict):
        return None

    winning_skill = nonempty_text(skill_authority.get("winning_skill_if_any"))
    skill_touch = skill_authority.get("executable_local_touch_if_any")
    if winning_skill != "exact_closure" or not isinstance(skill_touch, dict):
        return None

    skill_kind = nonempty_text(skill_touch.get("kind"))
    skill_target = nonempty_text(skill_touch.get("target"))
    primitive_kind = nonempty_text(primitive_program.get("kind"))
    primitive_target = nonempty_text(primitive_program.get("target"))
    if not skill_kind or not skill_target or not primitive_kind or not primitive_target:
        return None
    if skill_kind == primitive_kind and skill_target == primitive_target:
        return None

    control_signals = (
        control_signals_override
        if control_signals_override is not None
        else derive_control_signals(
            state,
            problems,
            handoff_override=handoff,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        )
    )
    if not isinstance(control_signals, dict):
        return None

    controller_view = control_signals.get("current_controller_view", {})
    meta_controls = control_signals.get("meta_controls", {})
    micro_surface = control_signals.get("micro_control_surface", {})
    if not (
        isinstance(controller_view, dict)
        and isinstance(meta_controls, dict)
        and isinstance(micro_surface, dict)
    ):
        return None

    if nonempty_text(controller_view.get("carrier_status")) != "thinning":
        return None
    if meta_controls.get("hindbrain_guard", {}).get("active") is not True:
        return None
    if nonempty_text(meta_controls.get("central_control", {}).get("mode")) != "closure_gate":
        return None

    supervision = micro_surface.get("supervision_pulse", {})
    closure_pull = micro_surface.get("closure_pull", {})
    if not (
        isinstance(supervision, dict)
        and isinstance(closure_pull, dict)
        and supervision.get("active") is True
        and closure_pull.get("active") is True
        and closure_pull.get("blocks_release") is True
    ):
        return None

    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    handoff_target = nonempty_text(handoff.get("to_object"))
    structural_primitives = []
    if isinstance(primitive_field, dict):
        raw_primitives = primitive_field.get("active_primitives")
        if isinstance(raw_primitives, list):
            structural_primitives = [
                canonicalize_primitive_token(value)
                for value in raw_primitives
                if canonicalize_primitive_token(value)
            ]
    readout_like = {
        "readout",
        "definition_as_direct_readout",
        "projection_readout",
        "dominant_mechanism_readout",
        "vector_difference_readout",
    }
    if not any(primitive not in readout_like for primitive in structural_primitives):
        return None
    if primitive_kind != "write":
        return None
    if handoff_target and primitive_target != handoff_target:
        return None
    if asked_medium and skill_target != asked_medium:
        return None

    return {
        "mode": "primitive_then_closure",
        "reason": (
            "thinner-carrier structural debt is still live, but exact_closure should "
            "retake final authority immediately after one structural spend"
        ),
        "spend_first_program": primitive_program,
        "post_closure_touch_if_any": {
            "kind": skill_kind,
            "target": skill_target,
            "operation": nonempty_text(skill_touch.get("operation")),
            "success_signal": nonempty_text(skill_touch.get("success_signal")),
        },
        "keep_closure_authority": True,
        "handoff_target": handoff_target,
    }


def derive_discipline_contract(
    state: dict,
    problems: list[str],
    *,
    control_bridge_override: dict | None = None,
    reselection_bridge_override: dict | None = None,
    closure_nucleus_override: dict | None = None,
    inhibition_override: dict | None = None,
    interlayer_override: dict | None = None,
    probe_discipline_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    control_bridge = (
        control_bridge_override
        if control_bridge_override is not None
        else derive_control_bridge(state, problems)
    )
    reselection_bridge = (
        reselection_bridge_override
        if reselection_bridge_override is not None
        else derive_reselection_bridge(state, problems)
    )
    closure_nucleus = (
        closure_nucleus_override
        if closure_nucleus_override is not None
        else derive_closure_nucleus(state, problems)
    )
    inhibition = (
        inhibition_override
        if inhibition_override is not None
        else derive_inhibition_state(state, problems)
    )
    interlayer = (
        interlayer_override
        if interlayer_override is not None
        else derive_interlayer_discharge_bridge(state, problems)
    )
    probe_discipline = (
        probe_discipline_override
        if probe_discipline_override is not None
        else derive_probe_discipline(state, problems)
    )

    bound_program = state.get("bound_program")
    explicit_handoff = state.get("carrier_handoff_if_any")
    gate_until = (
        nonempty_text(inhibition.get("gate_until"))
        if isinstance(inhibition, dict)
        else ""
    )
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))

    if isinstance(bound_program, dict):
        return {
            "active": True,
            "forbid_ordinary_regrowth": True,
            "must_bind_local_bite": False,
            "must_spend_handoff": False,
            "surface": "bound_program",
            "owner": (
                nonempty_text(closure_nucleus.get("owner"))
                if isinstance(closure_nucleus, dict)
                else "same_carrier"
            ),
            "current_object": current_object,
            "current_debt": current_debt,
            "authorized_bite": bound_program,
            "reason": (
                "one local executable bite is already bound; broad derivation should cool "
                "until that same-carrier bite changes, lands, or tears"
            ),
            "tears_on": gate_until or "same_carrier_change_or_exact_check",
            **(
                {
                    "probe_must_bind_skill_hypothesis": True,
                    "active_skill_hypothesis": nonempty_text(probe_discipline.get("active_skill_hypothesis")),
                }
                if isinstance(probe_discipline, dict) and probe_discipline.get("probe_must_bind") is True
                else {}
            ),
        }

    if isinstance(explicit_handoff, dict):
        contract = {
            "active": True,
            "forbid_ordinary_regrowth": True,
            "must_bind_local_bite": False,
            "must_spend_handoff": True,
            "surface": "carrier_handoff",
            "owner": "reselection",
            "current_object": current_object,
            "current_debt": current_debt,
            "authorized_bite": explicit_handoff,
            "reason": (
                "thinner-carrier authority is already explicit; broad route reconstruction "
                "should cool until that local handoff is spent or honestly refused"
            ),
            "tears_on": gate_until or "handoff_spent_or_exact_refusal",
        }
        if isinstance(probe_discipline, dict) and probe_discipline.get("probe_must_bind") is True:
            contract["probe_must_bind_skill_hypothesis"] = True
            contract["active_skill_hypothesis"] = nonempty_text(
                probe_discipline.get("active_skill_hypothesis")
            )
        if isinstance(interlayer, dict):
            contract["interlayer_discharge_bridge"] = interlayer
            contract["reason"] = (
                "thinner-carrier authority is explicit and one structural bite may need "
                "to land before closure retakes the foreground"
            )
        return contract

    if isinstance(control_bridge, dict):
        action_name = nonempty_text(control_bridge.get("default_local_action"))
        action = control_bridge.get(action_name) if action_name else None
        if isinstance(action, dict):
            return {
                "active": True,
                "forbid_ordinary_regrowth": True,
                "must_bind_local_bite": True,
                "must_spend_handoff": False,
                "surface": "control_bridge",
                "owner": "same_carrier",
                "current_object": current_object,
                "current_debt": current_debt,
                "authorized_bite": action,
                "reason": (
                    "one same-carrier local bite is already concrete enough to bind; "
                    "ordinary free-form solving should cool until that bite is bound or torn"
                ),
                "tears_on": gate_until or "bind_or_exact_refusal",
                **(
                    {
                        "probe_must_bind_skill_hypothesis": True,
                        "active_skill_hypothesis": nonempty_text(probe_discipline.get("active_skill_hypothesis")),
                    }
                    if isinstance(probe_discipline, dict) and probe_discipline.get("probe_must_bind") is True
                    else {}
                ),
            }

    return None


def build_report(state: dict, state_path: Path) -> dict:
    problems: list[str] = []
    warnings: list[str] = []

    validate_no_extra_keys(
        state,
        {
            "current_object",
            "current_seam",
            "current_debt",
            "next_bite",
            "asked_medium_surface",
            "revocation_handle",
            "uncertainty_mode",
            "primary_slot",
            "bound_program",
            "gate_binding_if_any",
            "primitive_field_if_any",
            "primitive_competition_if_any",
            "carrier_handoff_if_any",
            "secondary_rival_if_any",
            "materialization_evidence",
            "release_veto",
            "unresolved_markers",
            "output_status",
            "memory_residue",
        },
        "state",
        problems,
    )

    for key in [
        "current_object",
        "current_debt",
        "next_bite",
        "asked_medium_surface",
        "revocation_handle",
        "uncertainty_mode",
        "primary_slot",
    ]:
        require_nonempty(state, key, problems)
    validate_current_seam(state, problems)

    if not isinstance(state.get("release_veto"), bool):
        problems.append("release_veto must be boolean")

    output_status = state.get("output_status")
    if not isinstance(output_status, dict):
        problems.append("output_status must be an object")
        output_status = {}
    else:
        validate_no_extra_keys(
            output_status,
            {
                "touched",
                "cosmetic_only",
                "contains_unsupported",
                "contains_placeholder",
                "final_artifact_materialized",
            },
            "output_status",
            problems,
        )

    for key in [
        "touched",
        "cosmetic_only",
        "contains_unsupported",
        "contains_placeholder",
        "final_artifact_materialized",
    ]:
        if not isinstance(output_status.get(key), bool):
            problems.append(f"output_status.{key} must be boolean")

    unresolved = state.get("unresolved_markers", [])
    if unresolved is None:
        unresolved = []
    if not isinstance(unresolved, list):
        problems.append("unresolved_markers must be an array")
        unresolved = []

    memory_residue = state.get("memory_residue", [])
    if not isinstance(memory_residue, list):
        problems.append("memory_residue must be an array")
        memory_residue = []
    else:
        for idx, item in enumerate(memory_residue):
            if not isinstance(item, dict):
                problems.append(f"memory_residue[{idx}] must be an object")
                continue
            for key in ["kind", "description", "replayable"]:
                if key not in item:
                    problems.append(f"memory_residue[{idx}] is missing required key: {key}")
            if item.get("replayable") is True:
                problems.append(
                    f"memory_residue[{idx}] is replayable; route replay is forbidden"
                )
            validate_no_extra_keys(
                item,
                {"kind", "description", "replayable"},
                f"memory_residue[{idx}]",
                problems,
            )
            kind = item.get("kind")
            if kind not in ALLOWED_RESIDUE_KINDS:
                problems.append(
                    f"memory_residue[{idx}].kind must be one of: {', '.join(sorted(ALLOWED_RESIDUE_KINDS))}"
                )
            description = item.get("description")
            if not isinstance(description, str) or not description.strip():
                problems.append(f"memory_residue[{idx}].description must be non-empty")
            if not isinstance(item.get("replayable"), bool):
                problems.append(f"memory_residue[{idx}].replayable must be boolean")

    if state.get("secondary_rival_if_any") is not None:
        rival = state["secondary_rival_if_any"]
        if not isinstance(rival, dict):
            problems.append("secondary_rival_if_any must be object or null")
        else:
            validate_no_extra_keys(
                rival,
                {"object", "debt", "bite", "separating_advantage"},
                "secondary_rival_if_any",
                problems,
            )
            for key in ["object", "debt", "bite", "separating_advantage"]:
                require_nonempty(rival, key, problems)

    validate_bound_program(state, problems)
    validate_gate_binding(state, problems)
    validate_primitive_field(state, problems)
    validate_primitive_competition(state, problems)
    validate_materialization_evidence(state, problems)
    validate_carrier_handoff(state, problems)

    if state.get("gate_binding_if_any") is not None:
        if state.get("release_veto") is not True:
            problems.append("gate_binding_if_any requires release_veto to stay active")
        if state.get("bound_program") is None:
            problems.append("gate_binding_if_any requires a bound_program on the same carrier")
        if state.get("carrier_handoff_if_any") is not None:
            problems.append("gate_binding_if_any cannot coexist with carrier_handoff_if_any")

    if state.get("release_veto") is not True:
        for key in [
            "gate_binding_if_any",
            "carrier_handoff_if_any",
            "primitive_field_if_any",
            "primitive_competition_if_any",
        ]:
            if state.get(key) is not None:
                problems.append(f"{key} requires release_veto to stay active")

    effective_handoff = None
    if (
        state.get("release_veto") is True
        and state.get("carrier_handoff_if_any") is None
        and state.get("bound_program") is None
        and state.get("gate_binding_if_any") is None
    ):
        candidate_handoff = derive_handoff_candidate(state, [])
        if isinstance(candidate_handoff, dict):
            warnings.append("carrier_handoff_if_any missing; derived reselection used")
            effective_handoff = candidate_handoff

    effective_primitive_field = None
    primitive_field_stale = primitive_field_is_stale(
        state,
        handoff_override=effective_handoff,
    )
    if state.get("primitive_field_if_any") is None or primitive_field_stale:
        candidate_primitive_field = derive_primitive_field_candidate(
            state,
            [],
            handoff_override=effective_handoff,
        )
        if isinstance(candidate_primitive_field, dict):
            if primitive_field_stale:
                warnings.append(
                    "primitive_field_if_any was stale for the current layer; derived local primitive field used"
                )
            else:
                warnings.append("primitive_field_if_any missing; derived local primitive field used")
            effective_primitive_field = candidate_primitive_field

    candidate_probe_discipline = derive_probe_discipline(
        state,
        [],
        primitive_field_override=effective_primitive_field if isinstance(effective_primitive_field, dict) else None,
    )
    derived_program_is_unbound_probe = False
    if isinstance(candidate_probe_discipline, dict):
        active_hypothesis = nonempty_text(candidate_probe_discipline.get("active_skill_hypothesis"))
        if not active_hypothesis:
            if (
                isinstance(effective_primitive_field, dict)
                and nonempty_text(effective_primitive_field.get("selection_basis")) == "text_fallback"
            ):
                derived_program_is_unbound_probe = True

    effective_program = None
    missing_program_problem = "bound_program is required while release_veto is active"
    explicit_handoff_live = state.get("carrier_handoff_if_any") is not None
    if (
        effective_handoff is None
        and not explicit_handoff_live
        and state.get("release_veto") is True
        and state.get("bound_program") is None
    ):
        candidate = derive_bound_program_candidate(state, [])
        if isinstance(candidate, dict):
            lead_program_kind = nonempty_text(candidate.get("kind"))
            if isinstance(candidate_probe_discipline, dict):
                active_hypothesis = nonempty_text(
                    candidate_probe_discipline.get("active_skill_hypothesis")
                )
                allowed_probe_kinds = candidate_probe_discipline.get("allowed_probe_kinds")
                lead_primitives = candidate_probe_discipline.get("probe_like_primitives")
                if (
                    not active_hypothesis
                    and (
                        (
                            isinstance(allowed_probe_kinds, list)
                            and lead_program_kind in allowed_probe_kinds
                        )
                        or (
                            isinstance(lead_primitives, list)
                            and any(primitive_is_probe_like(value) for value in lead_primitives)
                        )
                    )
                ):
                    derived_program_is_unbound_probe = True
            if derived_program_is_unbound_probe:
                warnings.append(
                    "bound_program missing; derived next_touch stayed suppressed because probe-like pressure is still unbound or text-fallback only"
                )
            else:
                problems[:] = [problem for problem in problems if problem != missing_program_problem]
                warnings.append("bound_program missing; derived next_touch used")
                effective_program = candidate

    if (effective_handoff is not None or explicit_handoff_live) and state.get("bound_program") is None:
        problems[:] = [problem for problem in problems if problem != missing_program_problem]
        warnings.append("bound_program deferred while thinner-carrier reselection is active")

    competition = state.get("primitive_competition_if_any")
    effective_competition = competition if isinstance(competition, dict) else None
    if isinstance(competition, dict) and primitive_competition_is_stale(
        state,
        competition_override=competition,
        handoff_override=effective_handoff,
    ):
        warnings.append(
            "primitive competition object is stale for the current layer and is being ignored"
        )
        effective_competition = None

    if isinstance(effective_competition, dict):
        candidate_count = (
            len(effective_competition.get("candidates", []))
            if isinstance(effective_competition.get("candidates"), list)
            else 0
        )
        if candidate_count > 1 and not nonempty_text(
            effective_competition.get("winner_if_any")
        ):
            warnings.append(
                "explicit primitive competition is still unresolved on the current layer"
            )

    primitive_field_for_warning = effective_primitive_field or state.get("primitive_field_if_any")
    if (
        state.get("bound_program") is None
        and isinstance(primitive_field_for_warning, dict)
        and (effective_handoff is not None or explicit_handoff_live)
    ):
        if nonempty_text(primitive_field_for_warning.get("selection_basis")) == "text_fallback":
            warnings.append(
                "primitive field is still text-fallback only; no automatic next primitive bite should be trusted yet"
            )
            fallback_primitives = primitive_field_for_warning.get("active_primitives")
            if isinstance(fallback_primitives, list) and fallback_primitives:
                fallback_semantics = get_primitive_semantics(fallback_primitives[0])
                fallback_touch = nonempty_text(
                    fallback_semantics.get("cheapest_honest_touch")
                )
                fallback_warning = nonempty_text(
                    fallback_semantics.get("anti_pattern")
                )
                if fallback_touch:
                    warnings.append(
                        "text-fallback primitive still needs one honest mechanism touch before binding: "
                        + fallback_touch
                    )
                if fallback_warning:
                    warnings.append(
                        "text-fallback primitive misuse risk: " + fallback_warning
                    )
        active_primitives_for_warning = primitive_field_for_warning.get("active_primitives")
        if (
            isinstance(active_primitives_for_warning, list)
            and len(active_primitives_for_warning) > 1
            and not nonempty_text(primitive_field_for_warning.get("tie_break_check"))
        ):
            warnings.append(
                "primitive field still has multiple live primitives but no tie-break check; next primitive bite stays unbound"
            )
        primitive_program_warning = derive_primitive_program_candidate(
            state,
            [],
            primitive_field_override=primitive_field_for_warning,
        )
        if isinstance(primitive_program_warning, dict):
            warnings.append(
                "next primitive bite is already concrete on the thinner carrier but still unbound"
            )

    release_allowed = True

    if state.get("release_veto") is True:
        release_allowed = False
        warnings.append("release_veto is active")

    if unresolved:
        release_allowed = False
        warnings.append(f"unresolved markers remain: {', '.join(map(str, unresolved))}")

    if output_status.get("contains_unsupported") is True:
        release_allowed = False
        warnings.append("asked medium still contains UNSUPPORTED")

    if output_status.get("contains_placeholder") is True:
        release_allowed = False
        warnings.append("asked medium still contains placeholder content")

    if output_status.get("cosmetic_only") is True:
        release_allowed = False
        warnings.append("asked medium touch is cosmetic only")

    if output_status.get("touched") is not True:
        release_allowed = False
        warnings.append("asked medium has not been touched")

    if output_status.get("final_artifact_materialized") is not True:
        release_allowed = False
        warnings.append("final artifact is not materialized")

    if (
        state.get("release_veto") is not True
        and state.get("bound_program") is None
        and not has_materialization_evidence(state)
    ):
        release_allowed = False
        warnings.append(
            "released state without bound_program must carry materialization evidence"
        )

    self_check_agenda = None if (effective_handoff is not None or explicit_handoff_live) else derive_self_check_agenda(state, problems)
    primitive_field = effective_primitive_field or state.get("primitive_field_if_any")
    primitive_semantics = (
        summarize_primitive_semantics(primitive_field.get("active_primitives"))
        if isinstance(primitive_field, dict)
        else {}
    )
    primitive_competition_semantics = {}
    if isinstance(effective_competition, dict):
        candidate_primitives = [
            candidate.get("primitive")
            for candidate in effective_competition.get("candidates", [])
            if isinstance(candidate, dict)
        ]
        primitive_competition_semantics = summarize_primitive_semantics(
            candidate_primitives
        )
    control_signals = derive_control_signals(
        state,
        problems,
        handoff_override=effective_handoff,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
    )
    inhibition_state = derive_inhibition_state(
        state,
        problems,
        agenda_override=self_check_agenda,
        handoff_override=effective_handoff,
    )
    control_bridge = derive_control_bridge(
        state,
        problems,
        bound_program_override=effective_program,
    )
    reselection_bridge = derive_reselection_bridge(
        state,
        problems,
        handoff_override=effective_handoff,
    )
    closure_nucleus = derive_closure_nucleus(
        state,
        problems,
        agenda_override=self_check_agenda,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        primitive_competition_override=effective_competition if isinstance(effective_competition, dict) else None,
        handoff_override=effective_handoff,
        bound_program_override=effective_program,
        bound_program_origin_override=(
            "explicit" if isinstance(state.get("bound_program"), dict) else "derived"
        ) if isinstance(effective_program, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
    )
    gap_object = derive_gap_object(
        state,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
    )
    skill_field = derive_skill_field(
        state,
        problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
    )
    skill_semantics = (
        summarize_skill_semantics(skill_field.get("active_skills"))
        if isinstance(skill_field, dict)
        else {}
    )
    skill_competition = derive_skill_competition(
        state,
        problems,
        primitive_competition_override=effective_competition if isinstance(effective_competition, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
    )
    skill_competition_semantics = (
        summarize_skill_semantics(
            [
                candidate.get("skill")
                for candidate in skill_competition.get("candidates", [])
                if isinstance(candidate, dict)
            ]
        )
        if isinstance(skill_competition, dict)
        else {}
    )
    skill_inhibition = derive_skill_inhibition(
        state,
        problems,
        inhibition_override=inhibition_state if isinstance(inhibition_state, dict) else None,
        skill_field_override=skill_field if isinstance(skill_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
    )
    skill_authority_bridge = derive_skill_authority_bridge(
        state,
        problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
    )
    probe_discipline = derive_probe_discipline(
        state,
        problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        skill_field_override=skill_field if isinstance(skill_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
    )
    resume_bridge = derive_resume_bridge(
        state,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        gap_object_override=gap_object if isinstance(gap_object, dict) else None,
        reselection_bridge_override=reselection_bridge if isinstance(reselection_bridge, dict) else None,
        skill_field_override=skill_field if isinstance(skill_field, dict) else None,
    )
    if isinstance(control_signals, dict) and isinstance(probe_discipline, dict):
        control_signals["probe_discipline"] = probe_discipline
    interlayer_discharge_bridge = derive_interlayer_discharge_bridge(
        state,
        problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        skill_authority_override=skill_authority_bridge if isinstance(skill_authority_bridge, dict) else None,
    )
    discipline_contract = derive_discipline_contract(
        state,
        problems,
        control_bridge_override=control_bridge if isinstance(control_bridge, dict) else None,
        reselection_bridge_override=reselection_bridge if isinstance(reselection_bridge, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        inhibition_override=inhibition_state if isinstance(inhibition_state, dict) else None,
        interlayer_override=interlayer_discharge_bridge if isinstance(interlayer_discharge_bridge, dict) else None,
        probe_discipline_override=probe_discipline if isinstance(probe_discipline, dict) else None,
    )
    if (
        isinstance(probe_discipline, dict)
        and probe_discipline.get("probe_must_bind") is True
        and probe_discipline.get("unbound_probe_is_drift") is True
        and not nonempty_text(probe_discipline.get("active_skill_hypothesis"))
    ):
        warnings.append(
            "probe-like local search is live without a bound skill hypothesis; further pattern mining counts as drift"
        )
    elif isinstance(probe_discipline, dict) and nonempty_text(
        probe_discipline.get("active_skill_hypothesis")
    ):
        warnings.append(
            "probe work should stay tied to the live skill hypothesis: "
            + nonempty_text(probe_discipline.get("active_skill_hypothesis"))
        )

    if isinstance(primitive_field, dict):
        if isinstance(control_bridge, dict):
            control_bridge["primitive_field"] = primitive_field
            control_bridge["primitive_semantics"] = primitive_semantics
            if isinstance(control_signals, dict):
                control_bridge["control_signals"] = control_signals
            if isinstance(closure_nucleus, dict):
                control_bridge["closure_nucleus"] = closure_nucleus
            if isinstance(gap_object, dict):
                control_bridge["gap_object"] = gap_object
            if isinstance(resume_bridge, dict):
                control_bridge["resume_bridge"] = resume_bridge
        if isinstance(reselection_bridge, dict):
            reselection_bridge["primitive_field"] = primitive_field
            reselection_bridge["primitive_semantics"] = primitive_semantics
            if isinstance(control_signals, dict):
                reselection_bridge["control_signals"] = control_signals
            if isinstance(closure_nucleus, dict):
                reselection_bridge["closure_nucleus"] = closure_nucleus
            if isinstance(gap_object, dict):
                reselection_bridge["gap_object"] = gap_object
            if isinstance(resume_bridge, dict):
                reselection_bridge["resume_bridge"] = resume_bridge
            primitive_program = derive_primitive_program_candidate(
                state,
                problems,
                primitive_field_override=primitive_field,
            )
            if isinstance(primitive_program, dict):
                reselection_bridge["next_primitive_touch"] = primitive_program
    elif isinstance(control_bridge, dict) and isinstance(closure_nucleus, dict):
        control_bridge["closure_nucleus"] = closure_nucleus
    elif isinstance(reselection_bridge, dict) and isinstance(closure_nucleus, dict):
        reselection_bridge["closure_nucleus"] = closure_nucleus

    return {
        "state_file": str(state_path),
        "valid_schema_shape": not problems,
        "release_allowed": release_allowed and not problems,
        "control_bridge": control_bridge,
        "reselection_bridge": reselection_bridge,
        "control_signals": control_signals,
        "gap_object": gap_object,
        "resume_bridge": resume_bridge,
        "primitive_field": primitive_field,
        "primitive_semantics": primitive_semantics,
        "primitive_competition": effective_competition,
        "primitive_competition_semantics": primitive_competition_semantics,
        "self_check_agenda": self_check_agenda,
        "closure_nucleus": closure_nucleus,
        "skill_field": skill_field,
        "skill_semantics": skill_semantics,
        "skill_competition": skill_competition,
        "skill_competition_semantics": skill_competition_semantics,
        "skill_inhibition": skill_inhibition,
        "skill_authority_bridge": skill_authority_bridge,
        "interlayer_discharge_bridge": interlayer_discharge_bridge,
        "probe_discipline": probe_discipline,
        "discipline_contract": discipline_contract,
        "inhibition_state": inhibition_state,
        "problems": problems,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Thin runtime guard for Wu Boshi Perspective. "
            "Checks release-veto conditions and non-replay memory residue."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    args = parser.parse_args()

    state_path = Path(args.state_file)
    state = load_json(state_path)

    report = build_report(state, state_path)
    json.dump(report, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")

    if report["problems"]:
        return 2
    if not report["release_allowed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
