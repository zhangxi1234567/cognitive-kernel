#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from functools import lru_cache
from datetime import datetime, timedelta, timezone
from pathlib import Path

from runtime_guard import (
    ALLOWED_SKILLS,
    ALLOWED_PRIMITIVES,
    PUBLIC_LIT_SKILLS,
    PRIMITIVE_ALIAS_GROUPS,
    SKILL_ALIAS_GROUPS,
    build_problem_born_touch_for_skill,
    build_report,
    canonicalize_skill_token,
    canonicalize_primitive_token,
    closure_can_take_first_shot,
    extract_explicit_skill_combo,
    get_skill_display_name_zh,
    infer_primitives_from_text,
    is_allowed_primitive_token,
    normalize_primitive_token,
    primitive_competition_is_stale,
    derive_bound_program_candidate,
    derive_object_compiled_读出_candidate,
    derive_gate_binding_candidate,
    derive_handoff_candidate,
    derive_local_skill_coaching_surface,
    derive_primitive_field_candidate,
    derive_primitive_program_candidate,
    fresh_blind_problem_first_touch_pending,
    get_primitive_semantics,
    is_generic_runtime_shell_text,
    is_meta_narration_text,
    program_has_meta_narration,
    load_json,
    primitive_is_probe_like,
    primitive_field_is_stale,
)


DEFAULT_STATE = {
    "current_object": "",
    "current_seam": "",
    "current_debt": "",
    "next_bite": "",
    "asked_medium_surface": "",
    "revocation_handle": "",
    "uncertainty_mode": "unknown",
    "primary_slot": "",
    "bound_program": None,
    "layer_composition_if_any": None,
    "gate_binding_if_any": None,
    "primitive_field_if_any": None,
    "primitive_competition_if_any": None,
    "carrier_handoff_if_any": None,
    "secondary_rival_if_any": None,
    "landed_next_touch_if_any": None,
    "primitive_takeover_gate_if_any": None,
    "materialization_evidence": None,
    "bootstrap_context": None,
    "release_veto": True,
    "unresolved_markers": [],
    "output_status": {
        "touched": False,
        "cosmetic_only": False,
        "contains_unsupported": False,
        "contains_placeholder": False,
        "final_artifact_materialized": False,
    },
    "memory_residue": [],
}

ALLOWED_RESIDUE_KINDS = {
    "competition_texture",
    "distrust_bias",
    "见证_readiness",
    "读出_sensitivity",
    "boundary_residue",
}

READOUT_LIKE_SKILLS = {
    "读出",
    "定义即直接读出",
    "投影读出",
    "主导机制读出",
    "向量差读出",
    "精确封口",
}

NON_PROBLEM_FACING_SKILLS = READOUT_LIKE_SKILLS | {
    "外壳怀疑",
    "最终控制者",
    "抓本质",
    "更薄载体重选",
    "元认知",
    "监督",
    "中枢控制",
    "后脑守卫",
    "奖惩塑形",
    "反问",
}

CLOSURE_COMBO_DISALLOWED_SKILLS = NON_PROBLEM_FACING_SKILLS - READOUT_LIKE_SKILLS
REOPEN_COMPETITION_DISALLOWED_SKILLS = {
    "外壳怀疑",
    "最终控制者",
    "抓本质",
    "更薄载体重选",
    "元认知",
    "监督",
    "中枢控制",
    "后脑守卫",
    "奖惩塑形",
    "反问",
    "精确封口",
}

ORDINARY_ACTION_MARKERS = [
    "设",
    "令",
    "求导",
    "导数",
    "分类",
    "分情况",
    "枚举",
    "解方程",
    "解出",
    "代换",
    "换元",
    "化简",
    "展开",
    "移项",
    "联立",
    "消元",
    "bruteforce",
    "differentiate",
    "derivative",
    "monotonic",
    "monotonicity",
    "increasing",
    "decreasing",
    "critical point",
    "critical points",
    "stationary point",
    "case split",
    "enumerate",
    "substitute",
    "simplify",
    "expand",
    "rearrange",
]

ORDINARY_DENIAL_MARKERS = [
    "不需要",
    "不用",
    "没必要",
    "不必",
    "先不要",
    "不是先",
    "并不需要",
]

ORDINARY_SUBORDINATION_MARKERS = [
    "辅助",
    "辅助操作",
    "只是辅助",
    "只做辅助",
    "只作辅助",
    "作为辅助",
    "借助",
    "借它",
    "借这个",
    "稳一下",
    "稳出来",
    "托出来",
    "只做检查",
    "只作检查",
    "作为检查",
    "用来检查",
    "用于检查",
    "只做验证",
    "只作验证",
    "不是主技能",
    "只是工具",
    "support",
    "helper",
    "subordinate",
    "only as",
    "as a check",
    "to verify",
    "to stabilize",
]

CHECK_CONTEXT_MARKERS = [
    "检查",
    "检验",
    "验证",
    "校验",
    "见证",
    "check",
    "verify",
    "validation",
]

COUNTER_QUESTION_MARKERS = [
    "真的需要",
    "有必要",
    "why",
    "do we need",
    "need to",
    "吗",
    "?",
    "？",
]

SKILL_POSITIVE_HANDOFF_MARKERS = [
    "应该先",
    "先让",
    "先用",
    "先把",
    "改成",
    "压到",
    "统一到",
    "instead",
    "should first",
]

EXPLANATION_ONLY_MARKERS = [
    "解释",
    "说明",
    "叙述",
    "narrate",
    "explain",
    "commentary",
]

EXPLANATION_STALL_MARKERS = [
    "继续解释",
    "只需解释",
    "先解释",
    "补充说明",
    "继续说明",
]

THICK_OBJECT_RETURN_MARKERS = [
    "回到厚对象",
    "回到原对象",
    "回原对象",
    "回到原题",
    "回到大对象",
    "return to the thick object",
    "go back to the thick carrier",
    "back on the original object",
]

ASKED_MEDIUM_RUSH_MARKERS = [
    "最终答案",
    "直接作答",
    "直接写答案",
    "写进 answer.md",
    "asked medium",
    "final answer",
]

COUNTEREXAMPLE_CONTINUATION_MARKERS = [
    "继续举反例",
    "继续反例",
    "counterexample",
    "反例",
    "(()",
]

FALLBACK_ACTION_MARKERS = [
    "画图",
    "画出",
    "取",
    "比较",
    "代入",
    "联立",
    "化为",
    "压到",
    "压成",
    "统一到",
    "构造",
    "检查",
    "检验",
    "截点",
    "峰值",
    "奇点",
    "rewrite",
    "draw",
    "graph",
    "compare",
    "project",
    "split",
    "probe",
    "check",
    "test",
    "boundary",
    "intersection",
    "level set",
]

ORDINARY_ACTION_REGEXES = [
    (re.compile(r"[A-Za-z]\s*'\s*\("), "导数记号"),
    (re.compile(r"\b[a-zA-Z]+'\s*="), "导数记号"),
    (re.compile(r"[A-Za-z](?:_[A-Za-z0-9{}]+)?\s*'\s*(?:_[A-Za-z0-9{}]+)?\s*(?:\(|=)"), "导数记号"),
    (re.compile(r"分\s*(?:两|多)?\s*(?:种)?情形|分\s*(?:两|多)?\s*情况"), "分情况"),
    (re.compile(r"\b(?:case\s+split|cases?)\b"), "分情况"),
    (re.compile(r"\b(?:monotonic|monotonicity|increasing|decreasing|critical\s+points?|stationary\s+points?)\b", re.IGNORECASE), "单调分类"),
    (re.compile(r"\b(?:let|set|define|denote|introduce)\s+[A-Za-z][A-Za-z0-9_]*\s*(?:=|:=|as\b)"), "设元/换元"),
    (re.compile(r"[增减]函?数|单调"), "单调分类"),
    (re.compile(r"解\s*(?:方程|得)|联立|消元"), "解方程"),
    (re.compile(r"代换|换元|substitut"), "设元/换元"),
    (re.compile(r"化简|展开|移项|整理"), "代数整理"),
]

ORDINARY_CONTEXT_SPLIT_REGEX = re.compile(r"[\n\r。！？!?；;，,]+")
ORDINARY_SENTENCE_SPLIT_REGEX = re.compile(r"[\n\r。！？!?；;]+")
STATE_TOUCH_ANCHOR_SPLIT_REGEX = re.compile(r"[\n\r。！？!?；;:：]+")
STATE_TOUCH_FORMULA_REGEX = re.compile(r"[A-Za-z0-9_+\-*/^=<>]+")
SUBORDINATE_ORDINARY_BLOCKERS = [
    "分别算完",
    "分类算完",
    "直接分类",
    "分情况讨论",
    "整理答案",
    "回去整理",
]
ASSIGNMENT_FRIENDLY_SKILLS = {
    "赋值",
    "重编码",
    "投影",
    "规范归一化",
    "容器到截面",
    "点积投影",
    "面积到线读出",
}
AUXILIARY_ASSIGNMENT_REGEX = re.compile(
    r"(?<![A-Za-z0-9_])([A-Za-z](?:_[A-Za-z0-9{}]+)?)\s*=\s*(?=[^,\n;。！？!?]*[A-Za-z\\(])"
)

ORDINARY_OPERATION_FAMILY_BY_HIT = {
    "设": "symbol_binding",
    "令": "symbol_binding",
    "设元/换元": "symbol_binding",
    "代换": "symbol_binding",
    "换元": "symbol_binding",
    "求导": "local_calculus_probe",
    "导数": "local_calculus_probe",
    "导数记号": "local_calculus_probe",
    "单调分类": "local_calculus_probe",
    "分类": "case_split",
    "分情况": "case_split",
    "case split": "case_split",
    "枚举": "enumeration",
    "enumerate": "enumeration",
    "bruteforce": "enumeration",
    "解方程": "equation_solving",
    "解出": "equation_solving",
    "联立": "equation_solving",
    "消元": "equation_solving",
    "化简": "algebraic_manipulation",
    "展开": "algebraic_manipulation",
    "移项": "algebraic_manipulation",
    "代数整理": "algebraic_manipulation",
}

NON_SERIALIZABLE_ORDINARY_OPERATION_FAMILIES = {
    "local_calculus_probe",
    "case_split",
    "equation_solving",
    "algebraic_manipulation",
    "enumeration",
    "full_route_reconstruction",
}

VISIBLE_SUBORDINATE_ORDINARY_OPERATION_FAMILIES = {
    "diagram_annotation",
    "numerical_check",
}


def _explicit_skill_mentions_in_text(*, worked_step: str, candidates: list[str]) -> set[str]:
    normalized_step = normalize_primitive_token(worked_step)
    matched: set[str] = set()
    if not normalized_step:
        return matched
    for skill in candidates:
        aliases = {skill}
        aliases.update(PRIMITIVE_ALIAS_GROUPS.get(skill, set()))
        aliases.update(SKILL_ALIAS_GROUPS.get(skill, set()))
        for alias in aliases:
            normalized_alias = normalize_primitive_token(alias)
            if normalized_alias and normalized_alias in normalized_step:
                matched.add(skill)
                break
    return matched


def _ordered_skill_mentions_in_text(*, worked_step: str, candidates: list[str]) -> list[str]:
    normalized_step = normalize_primitive_token(worked_step)
    if not normalized_step:
        return []

    positioned: list[tuple[int, int, str]] = []
    for order, skill in enumerate(candidates):
        aliases = {skill}
        aliases.update(PRIMITIVE_ALIAS_GROUPS.get(skill, set()))
        aliases.update(SKILL_ALIAS_GROUPS.get(skill, set()))
        best_index: int | None = None
        for alias in aliases:
            normalized_alias = normalize_primitive_token(alias)
            if not normalized_alias:
                continue
            index = normalized_step.find(normalized_alias)
            if index == -1:
                continue
            if best_index is None or index < best_index:
                best_index = index
        if best_index is not None:
            positioned.append((best_index, order, skill))
    positioned.sort()
    return [skill for _, _, skill in positioned]


def _event_worked_step_text(event: dict | None) -> str:
    if not isinstance(event, dict):
        return ""
    after = event.get("after")
    if not isinstance(after, dict):
        return ""
    evidence = after.get("materialization_evidence")
    if not isinstance(evidence, dict):
        return ""
    return str(evidence.get("worked_step", "")).strip()


def _worked_step_visible_skill_combo(
    *,
    worked_step: str,
    explicit_layer: dict | None,
    leading_skill: str,
) -> tuple[list[str], list[str]]:
    combo = _normalized_skill_list(
        explicit_layer.get("active_skill_combo_if_any") if isinstance(explicit_layer, dict) else None,
        limit=8,
    )
    visible_skills = [skill for skill in combo if skill not in READOUT_LIKE_SKILLS]
    inferred = set(infer_primitives_from_text(worked_step))
    inferred.update(_explicit_skill_mentions_in_text(worked_step=worked_step, candidates=visible_skills))
    matched_combo = [skill for skill in visible_skills if skill in inferred]

    runtime_shell_scope = False
    if isinstance(explicit_layer, dict):
        runtime_shell_scope = any(
            is_generic_runtime_shell_text(candidate)
            for candidate in (
                explicit_layer.get("controlled_object"),
                explicit_layer.get("layer_object"),
                ((explicit_layer.get("authorized_bite") or {}) if isinstance(explicit_layer.get("authorized_bite"), dict) else {}).get("target"),
            )
        )
    if runtime_shell_scope:
        ordered_explicit = _ordered_skill_mentions_in_text(
            worked_step=worked_step,
            candidates=[skill for skill in ALLOWED_PRIMITIVES if skill not in READOUT_LIKE_SKILLS],
        )
        matched_combo = []
        for skill in ordered_explicit:
            if skill not in matched_combo:
                matched_combo.append(skill)
        for skill in visible_skills:
            if skill in inferred and skill not in matched_combo:
                matched_combo.append(skill)
    elif leading_skill and leading_skill in visible_skills and leading_skill not in matched_combo:
        matched_combo.insert(0, leading_skill)

    auxiliary_candidates = sorted(
        skill for skill in ALLOWED_SKILLS if canonicalize_skill_token(skill) not in ALLOWED_PRIMITIVES
    )
    explicit_auxiliary = [
        skill
        for skill in auxiliary_candidates
        if skill not in matched_combo
        and skill in _explicit_skill_mentions_in_text(
            worked_step=worked_step,
            candidates=auxiliary_candidates,
        )
    ]
    visible_combo = matched_combo + explicit_auxiliary
    supporting = [skill for skill in visible_combo if skill != leading_skill][:4]
    return visible_combo, supporting


def fresh_blind_bootstrap_context() -> dict:
    return {
        "mode": "fresh_blind_project_skills_on",
        "readset_manifest": "BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt",
        "requires_fresh_state_path": True,
        "requires_new_runtime_transition": True,
        "requires_qualified_layer_composition_for_skill_claims": True,
        "auto_enter_local_action_when_concrete": True,
        "auto_reselect_after_layer_change": True,
        "selection_dynamics": "local_competition_with_persistent_bias",
        "first_runtime_transition_window_seconds": 300,
        "first_runtime_transition_window_started_at": datetime.now(timezone.utc).isoformat(),
    }


def _fresh_blind_mode_active_from_state(state: object) -> bool:
    if not isinstance(state, dict):
        return False
    bootstrap_context = state.get("bootstrap_context")
    return isinstance(bootstrap_context, dict) and str(bootstrap_context.get("mode", "")).strip() == "fresh_blind_project_skills_on"


def _fresh_blind_asked_medium_surface_refusal(asked_medium_surface: object) -> str:
    asked_medium = str(asked_medium_surface or "").strip()
    if not asked_medium:
        return ""
    candidate = Path(asked_medium)
    if candidate.is_absolute():
        return "asked-medium surface must stay a relative markdown artifact path in fresh blind mode"
    if candidate.suffix.lower() != ".md":
        return (
            "asked-medium surface must name one concrete markdown artifact such as "
            "`final.md` in fresh blind mode"
        )
    if any(part in {".", ".."} for part in candidate.parts):
        return "asked-medium surface must not use dot-segments in fresh blind mode"
    return ""


def _extract_markdown_artifact_hint(text: object) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    matches = re.findall(r"[\w./\\-]+\.md\b", raw)
    if matches:
        return matches[-1].replace("\\", "/")
    return raw


def fresh_blind_generic_output_refusal(
    output_path: Path,
    *,
    state: object,
    state_path: Path,
    allow_asked_medium: bool = False,
    allow_markdown_paths: list[Path] | None = None,
) -> str:
    if not _fresh_blind_mode_active_from_state(state):
        return ""
    asked_medium_path = None
    if isinstance(state, dict):
        asked_medium_path = asked_medium_output_path(state=state, state_path=state_path)
    if (
        asked_medium_path is not None
        and _normalized_existing_path_text(str(output_path))
        == _normalized_existing_path_text(str(asked_medium_path))
    ):
        if allow_asked_medium:
            return ""
        return (
            "fresh blind asked-medium artifact must stay runtime-owned; "
            "do not write it through generic output sinks"
        )
    if output_path.suffix.lower() != ".md":
        return ""
    normalized_allowed = {
        _normalized_existing_path_text(str(path))
        for path in (allow_markdown_paths or [])
        if isinstance(path, Path)
    }
    if _normalized_existing_path_text(str(output_path)) in normalized_allowed:
        return ""
    if output_path.name.lower() == "verdict.md":
        return (
            "fresh blind final deliverable `verdict.md` must stay runtime-derived; "
            "do not write it through generic output sinks"
        )
    return (
        "fresh blind generic markdown outputs must stay on the canonical asked-medium "
        "or official runtime sidecar paths"
    )


def _parse_utc_iso_datetime(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fresh_blind_runtime_transition_watchdog(
    state: object,
    *,
    runtime_evidence: object = None,
    now: datetime | None = None,
) -> dict | None:
    if not isinstance(state, dict):
        return None
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return None
    if str(bootstrap_context.get("mode", "")).strip() != "fresh_blind_project_skills_on":
        return None

    started_at = _parse_utc_iso_datetime(
        bootstrap_context.get("first_runtime_transition_window_started_at")
    )
    window_raw = bootstrap_context.get("first_runtime_transition_window_seconds")
    try:
        window_seconds = int(window_raw)
    except (TypeError, ValueError):
        window_seconds = 300
    if window_seconds <= 0 or started_at is None:
        return None

    if not isinstance(runtime_evidence, dict):
        runtime_evidence = {}
    has_real_transition = runtime_evidence.get("has_real_runtime_transition") is True
    current_time = now if isinstance(now, datetime) else datetime.now(timezone.utc)
    current_time = current_time.astimezone(timezone.utc)
    deadline = started_at + timedelta(seconds=window_seconds)
    remaining_seconds = max(0, int((deadline - current_time).total_seconds()))
    expired = current_time >= deadline and not has_real_transition
    status = {
        "active": not has_real_transition,
        "window_seconds": window_seconds,
        "started_at_utc": started_at.isoformat(),
        "deadline_at_utc": deadline.isoformat(),
        "remaining_seconds": remaining_seconds,
        "expired": expired,
        "has_real_runtime_transition": has_real_transition,
    }
    if expired:
        status["reason"] = "bootstrap_runtime_window_expired"
        status["required_action"] = "record_one_real_runtime_transition"
    return status


class StateLock:
    def __init__(self, state_path: Path, timeout_seconds: float = 5.0) -> None:
        self.state_path = state_path
        self.lock_path = state_path.with_suffix(state_path.suffix + ".lock")
        self.timeout_seconds = timeout_seconds
        self.acquired = False

    def __enter__(self) -> "StateLock":
        deadline = time.time() + self.timeout_seconds
        while True:
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                self.acquired = True
                return self
            except FileExistsError:
                if time.time() >= deadline:
                    raise SystemExit(f"state lock timeout: {self.lock_path}")
                time.sleep(0.05)

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.acquired and self.lock_path.exists():
            self.lock_path.unlink()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def event_log_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.events.jsonl")


def default_fresh_blind_state_path(base_dir: Path | None = None) -> Path:
    root = base_dir if isinstance(base_dir, Path) else Path.cwd()
    return root / "runtime_state.json"


def trace_markdown_path(path: Path) -> Path:
    if path.stem == "runtime_state":
        return path.with_name("runtime_trace.md")
    return path.with_name(f"{path.stem}.trace.md")


def skill_trace_markdown_path(path: Path) -> Path:
    if path.stem == "runtime_state":
        return path.with_name("runtime_skill_trace.md")
    return path.with_name(f"{path.stem}.skill_trace.md")


def solve_trace_markdown_path(path: Path) -> Path:
    if path.stem == "runtime_state":
        return path.with_name("runtime_solve_trace.md")
    return path.with_name(f"{path.stem}.solve_trace.md")


def _deep_copy(payload: dict) -> dict:
    return json.loads(json.dumps(payload))


def _report_excerpt(report: dict) -> dict:
    excerpt: dict = {}

    gap_object = report.get("gap_object")
    if isinstance(gap_object, dict):
        compact_gap: dict = {}
        for key in ["object", "source_debt", "why_local", "cheap_check", "inherits_authority"]:
            value = gap_object.get(key)
            if value not in (None, {}, [], ""):
                compact_gap[key] = value
        primitive_hints = gap_object.get("primitive_hints")
        if isinstance(primitive_hints, list) and primitive_hints:
            compact_gap["primitive_hints"] = [
                str(value).strip() for value in primitive_hints if str(value).strip()
            ][:3]
        if compact_gap:
            excerpt["gap_object"] = compact_gap

    resume_bridge = report.get("resume_bridge")
    if isinstance(resume_bridge, dict):
        compact_resume: dict = {}
        for key in ["mode", "known_object", "explicit_gap", "next_local_choice", "same_carrier_preferred"]:
            value = resume_bridge.get(key)
            if value not in (None, {}, [], ""):
                compact_resume[key] = value
        supporting = resume_bridge.get("supporting_skills")
        if isinstance(supporting, list) and supporting:
            compact_resume["supporting_skills"] = [
                str(value).strip() for value in supporting if str(value).strip()
            ][:3]
        if compact_resume:
            excerpt["resume_bridge"] = compact_resume

    primitive_field = report.get("primitive_field")
    if isinstance(primitive_field, dict):
        compact_field: dict = {}
        for key in ["layer_object", "why_now", "selection_basis", "tie_break_check"]:
            value = primitive_field.get(key)
            if value not in (None, {}, [], ""):
                compact_field[key] = value
        active = primitive_field.get("active_primitives")
        if isinstance(active, list) and active:
            compact_field["active_primitives"] = [
                str(value).strip() for value in active if str(value).strip()
            ][:3]
        if compact_field:
            excerpt["primitive_field"] = compact_field

    controller_trigger = report.get("controller_trigger")
    if isinstance(controller_trigger, dict):
        compact_trigger: dict = {}
        for key in ["layer_object", "why_now", "selection_basis", "evidence_basis", "active"]:
            value = controller_trigger.get(key)
            if value not in (None, {}, [], ""):
                compact_trigger[key] = value
        trigger_names = controller_trigger.get("trigger_names")
        if isinstance(trigger_names, list) and trigger_names:
            compact_trigger["trigger_names"] = [
                str(value).strip() for value in trigger_names if str(value).strip()
            ][:3]
        favored = controller_trigger.get("favored_skills")
        if isinstance(favored, list) and favored:
            compact_trigger["favored_skills"] = [
                str(value).strip() for value in favored if str(value).strip()
            ][:4]
        if compact_trigger:
            excerpt["controller_trigger"] = compact_trigger

    skill_field = report.get("skill_field")
    if isinstance(skill_field, dict):
        compact_skill_field: dict = {}
        for key in [
            "layer_object",
            "why_now",
            "selection_basis",
            "composition_ready",
            "composition_reason",
            "authority_skill_if_any",
            "bound_skill_if_any",
        ]:
            value = skill_field.get(key)
            if value not in (None, {}, [], ""):
                compact_skill_field[key] = value
        controller_trigger_if_any = skill_field.get("controller_trigger_if_any")
        if isinstance(controller_trigger_if_any, dict):
            compact_skill_field["controller_trigger_if_any"] = {
                key: controller_trigger_if_any.get(key)
                for key in ["trigger_names", "favored_skills", "why_now"]
                if controller_trigger_if_any.get(key) not in (None, {}, [], "")
            }
        active_skills = skill_field.get("active_skills")
        if isinstance(active_skills, list) and active_skills:
            compact_skill_field["active_skills"] = [
                str(value).strip() for value in active_skills if str(value).strip()
            ][:5]
        background_skills = skill_field.get("background_skills_if_any")
        if isinstance(background_skills, list) and background_skills:
            compact_skill_field["background_skills_if_any"] = [
                str(value).strip() for value in background_skills if str(value).strip()
            ][:5]
        axes = skill_field.get("composition_axes")
        if isinstance(axes, list) and axes:
            compact_skill_field["composition_axes"] = [
                str(value).strip() for value in axes if str(value).strip()
            ][:3]
        if compact_skill_field:
            excerpt["skill_field"] = compact_skill_field

    skill_competition = report.get("skill_competition")
    if isinstance(skill_competition, dict):
        compact_competition: dict = {}
        for key in ["winning_skill_if_any", "surface", "reason"]:
            value = skill_competition.get(key)
            if value not in (None, {}, [], ""):
                compact_competition[key] = value
        candidates = skill_competition.get("candidates")
        if isinstance(candidates, list) and candidates:
            compact_candidates: list[dict] = []
            for candidate in candidates[:4]:
                if not isinstance(candidate, dict):
                    continue
                compact_candidate = {
                    key: candidate.get(key)
                    for key in ["skill", "touch_target", "why_now", "backed_by", "supporting_skills_if_any"]
                    if candidate.get(key) not in (None, {}, [], "")
                }
                if compact_candidate:
                    compact_candidates.append(compact_candidate)
            if compact_candidates:
                compact_competition["candidates"] = compact_candidates
        if compact_competition:
            excerpt["skill_competition"] = compact_competition

    skill_inhibition = report.get("skill_inhibition")
    if isinstance(skill_inhibition, dict):
        compact_inhibition: dict = {}
        for key in ["promoted_skill_if_any", "reason", "suppressed_by"]:
            value = skill_inhibition.get(key)
            if value not in (None, {}, [], ""):
                compact_inhibition[key] = value
        demoted = skill_inhibition.get("demoted_skills")
        if isinstance(demoted, list) and demoted:
            compact_inhibition["demoted_skills"] = [
                str(value).strip() for value in demoted if str(value).strip()
            ][:5]
        if compact_inhibition:
            excerpt["skill_inhibition"] = compact_inhibition

    skill_bridge = report.get("skill_authority_bridge")
    if isinstance(skill_bridge, dict):
        compact_bridge: dict = {}
        for key in [
            "winning_skill_if_any",
            "same_carrier_only",
            "silence_after_contact",
            "executable_owner_skill_if_any",
            "fallback_skill_hint_if_any",
        ]:
            value = skill_bridge.get(key)
            if value not in (None, {}, [], ""):
                compact_bridge[key] = value
        touch = project_bound_program_shape(skill_bridge.get("executable_local_touch_if_any"))
        if isinstance(touch, dict):
            compact_bridge["executable_local_touch_if_any"] = touch
        combo = skill_bridge.get("active_skill_combo_if_any")
        if isinstance(combo, list) and combo:
            compact_bridge["active_skill_combo_if_any"] = [
                str(value).strip() for value in combo if str(value).strip()
            ][:6]
        supporting = skill_bridge.get("supporting_skills_if_any")
        if isinstance(supporting, list) and supporting:
            compact_bridge["supporting_skills_if_any"] = [
                str(value).strip() for value in supporting if str(value).strip()
            ][:3]
        if compact_bridge:
            excerpt["skill_authority_bridge"] = compact_bridge

    first_layer_arena = report.get("first_layer_arena")
    if isinstance(first_layer_arena, dict):
        compact_arena: dict = {}
        for key in [
            "surface",
            "layer_object",
            "focus_target",
            "primary_skill_if_any",
            "supporting_skills_if_any",
            "active_skill_combo_if_any",
            "verify_touch_if_any",
            "role_split_if_any",
            "false_first_skill_if_any",
            "false_skill_reason",
            "winning_projected_gain_reason",
            "competition_basis",
            "anti_pipeline_note",
        ]:
            value = first_layer_arena.get(key)
            if value not in (None, {}, [], ""):
                compact_arena[key] = value
        authorized_touch = project_bound_program_shape(first_layer_arena.get("authorized_touch_if_any"))
        if isinstance(authorized_touch, dict):
            compact_arena["authorized_touch_if_any"] = authorized_touch
        lit_skills = first_layer_arena.get("lit_skills_if_any")
        if isinstance(lit_skills, list) and lit_skills:
            compact_arena["lit_skills_if_any"] = [
                str(value).strip() for value in lit_skills if str(value).strip()
            ][:8]
        if compact_arena:
            excerpt["first_layer_arena"] = compact_arena

    probe = report.get("probe_discipline")
    if isinstance(probe, dict):
        compact_probe: dict = {}
        for key in ["active", "probe_must_bind", "unbound_probe_is_drift", "active_skill_hypothesis"]:
            value = probe.get(key)
            if value not in (None, {}, [], ""):
                compact_probe[key] = value
        hypotheses = probe.get("active_skill_hypotheses")
        if isinstance(hypotheses, list) and hypotheses:
            compact_probe["active_skill_hypotheses"] = [
                str(value).strip() for value in hypotheses if str(value).strip()
            ][:3]
        if compact_probe:
            excerpt["probe_discipline"] = compact_probe

    takeover = report.get("primitive_takeover_gate")
    if isinstance(takeover, dict):
        compact_takeover: dict = {}
        for key in ["trigger", "current_seam", "next_bite", "note"]:
            value = takeover.get(key)
            if value not in (None, {}, [], ""):
                compact_takeover[key] = value
        active = takeover.get("active_primitives")
        if isinstance(active, list) and active:
            compact_takeover["active_primitives"] = [
                str(value).strip() for value in active if str(value).strip()
            ][:3]
        if compact_takeover:
            excerpt["primitive_takeover_gate"] = compact_takeover

    interlayer = report.get("interlayer_discharge_bridge")
    if isinstance(interlayer, dict):
        compact_interlayer: dict = {}
        for key in ["mode", "reason", "keep_closure_authority", "handoff_target"]:
            value = interlayer.get(key)
            if value not in (None, {}, [], ""):
                compact_interlayer[key] = value
        spend_first = project_bound_program_shape(interlayer.get("spend_first_program"))
        if isinstance(spend_first, dict):
            compact_interlayer["spend_first_program"] = spend_first
        post_closure = project_bound_program_shape(interlayer.get("post_closure_touch_if_any"))
        if isinstance(post_closure, dict):
            compact_interlayer["post_closure_touch_if_any"] = post_closure
        if compact_interlayer:
            excerpt["interlayer_discharge_bridge"] = compact_interlayer

    contract = report.get("discipline_contract")
    if isinstance(contract, dict):
        compact_contract: dict = {}
        for key in ["active", "owner", "current_object", "current_debt", "reason", "surface", "structural_first"]:
            value = contract.get(key)
            if value not in (None, {}, [], ""):
                compact_contract[key] = value
        authorized = project_bound_program_shape(contract.get("authorized_bite"))
        if isinstance(authorized, dict):
            compact_contract["authorized_bite"] = authorized
        combo = contract.get("active_skill_combo_if_any")
        if isinstance(combo, list) and combo:
            compact_contract["active_skill_combo_if_any"] = [
                str(value).strip() for value in combo if str(value).strip()
            ][:5]
        if compact_contract:
            excerpt["discipline_contract"] = compact_contract

    layer_composition = report.get("layer_composition")
    if isinstance(layer_composition, dict):
        compact_layer: dict = {}
        for key in [
            "active",
            "surface",
            "layer_object",
            "controlled_object",
            "current_layer_object_if_any",
            "object_transform_if_any",
            "step_outline_if_any",
            "skill_phase_if_any",
            "next_local_choice",
            "gap_object",
            "current_seam",
            "current_debt",
            "reason",
            "leading_skill_if_any",
            "next_local_choice",
            "gap_object",
            "event_owned",
            "transition_change",
            "forbid_ordinary_regrowth",
            "must_bind_local_bite",
            "must_spend_handoff",
            "false_first_skill_if_any",
            "false_first_label_if_any",
            "false_skill_reason",
            "accountability_nudge_if_any",
        ]:
            value = layer_composition.get(key)
            if value not in (None, {}, [], ""):
                compact_layer[key] = value
        combo = layer_composition.get("active_skill_combo_if_any")
        if isinstance(combo, list) and combo:
            compact_layer["active_skill_combo_if_any"] = [
                str(value).strip() for value in combo if str(value).strip()
            ][:6]
        axes = layer_composition.get("composition_axes")
        if isinstance(axes, list) and axes:
            compact_layer["composition_axes"] = [
                str(value).strip() for value in axes if str(value).strip()
            ][:4]
        primitives = layer_composition.get("active_primitives")
        if isinstance(primitives, list) and primitives:
            compact_layer["active_primitives"] = [
                str(value).strip() for value in primitives if str(value).strip()
            ][:4]
        background = layer_composition.get("background_skills_if_any")
        if isinstance(background, list) and background:
            compact_layer["background_skills_if_any"] = [
                str(value).strip() for value in background if str(value).strip()
            ][:6]
        authorized = project_bound_program_shape(layer_composition.get("authorized_bite"))
        if isinstance(authorized, dict):
            compact_layer["authorized_bite"] = authorized
        lighting = layer_composition.get("lighting_if_any")
        if isinstance(lighting, dict):
            lit_skill = str(lighting.get("lit_skill_if_any", "")).strip()
            if lit_skill and "leading_skill_if_any" not in compact_layer:
                compact_layer["leading_skill_if_any"] = lit_skill
            supporting = lighting.get("supporting_skills_if_any")
            if isinstance(supporting, list) and supporting:
                compact_layer["supporting_skills_if_any"] = [
                    str(value).strip() for value in supporting if str(value).strip()
                ][:6]
            for key in [
                "false_first_skill_if_any",
                "false_first_label_if_any",
                "false_skill_reason",
                "accountability_nudge_if_any",
                "winning_projected_gain_reason",
            ]:
                value = lighting.get(key)
                if value not in (None, {}, [], ""):
                    compact_layer[key] = value
            verify_touch = lighting.get("verify_touch_if_any")
            if isinstance(verify_touch, dict) and verify_touch:
                compact_layer["verify_touch_if_any"] = verify_touch
            for key in [
                "candidate_skills_if_any",
                "comparison_skill_if_any",
                "role_split_if_any",
                "ordinary_operations_are_not_skills",
                "anti_pipeline_note",
            ]:
                value = lighting.get(key)
                if value not in (None, {}, [], ""):
                    compact_layer.setdefault("lighting_if_any", {})
                    compact_layer["lighting_if_any"][key] = value
        if compact_layer:
            excerpt["layer_composition"] = compact_layer

    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        excerpt["warnings"] = [str(value).strip() for value in warnings if str(value).strip()][:4]
    problems = report.get("problems")
    if isinstance(problems, list) and problems:
        excerpt["problems"] = [str(value).strip() for value in problems if str(value).strip()][:4]
    return excerpt


def _event_kind(command_name: str) -> str:
    if command_name in {"bind-local", "spend-local", "execute-local"}:
        return "consumption"
    if command_name == "rebind-local":
        return "handoff"
    if command_name == "init":
        return "bootstrap"
    return "mutation"


def _normalized_skill_list(values: object, *, limit: int = 6) -> list[str]:
    if not isinstance(values, list):
        return []
    ordered: list[str] = []
    for value in values:
        text = canonicalize_skill_token(value)
        if text and text not in ordered:
            ordered.append(text)
        if len(ordered) == limit:
            break
    return ordered


def _visible_skill_expression_refusal(
    worked_step: str,
    *,
    state: dict,
) -> str:
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return ""
    if _nonempty_text(bootstrap_context.get("mode")) != "fresh_blind_project_skills_on":
        return ""
    layer = state.get("layer_composition_if_any")
    if not isinstance(layer, dict):
        return ""
    combo = _normalized_skill_list(layer.get("active_skill_combo_if_any"), limit=8)
    visible_skills = [skill for skill in combo if skill not in READOUT_LIKE_SKILLS]
    if not visible_skills:
        return ""
    inferred = set(infer_primitives_from_text(worked_step))
    inferred.update(_explicit_skill_mentions_in_text(worked_step=worked_step, candidates=visible_skills))
    matched = [skill for skill in visible_skills if skill in inferred]
    leading_skill = canonicalize_skill_token(layer.get("leading_skill_if_any"))
    if _worked_step_result_only_refusal(worked_step, state=state):
        return ""
    ordinary_regrowth_refusal = _ordinary_action_regrowth_refusal(
        worked_step,
        state=state,
        visible_skills=visible_skills,
        matched=matched,
        leading_skill=leading_skill,
    )
    if ordinary_regrowth_refusal:
        return ordinary_regrowth_refusal
    fallback_family_refusal = _fallback_family_refusal(
        worked_step,
        state=state,
        visible_skills=visible_skills,
        matched=matched,
        leading_skill=leading_skill,
    )
    if fallback_family_refusal:
        return fallback_family_refusal
    state_backed_context = _fresh_blind_execute_local_state_ownership_context(state)
    if state_backed_context:
        foreign_mentions = _worked_step_foreign_problem_skill_mentions(
            worked_step,
            allowed_skills=state_backed_context.get("owner_combo", []),
        )
        if foreign_mentions:
            active_combo = ", ".join(
                f"`{skill}`"
                for skill in state_backed_context.get("owner_combo", [])[:6]
            ) or "`当前层组合`"
            foreign_text = ", ".join(f"`{skill}`" for skill in foreign_mentions[:4])
            return (
                "execute-local refused: worked_step tried to relabel a live state-owned layer "
                f"with non-active skill labels {foreign_text}. "
                f"Current explicit combo: {active_combo}."
            )
    matched = _semantic_visible_skill_matches(
        worked_step,
        state=state,
        visible_skills=visible_skills,
        matched=matched,
        leading_skill=leading_skill,
        state_backed_context=state_backed_context,
    )
    role_split = _live_role_split(state)
    if leading_skill in visible_skills and leading_skill not in matched:
        return (
            "execute-local refused: visible solve step fell back to ordinary narration; "
            f"the leading skill `{leading_skill}` ({get_skill_display_name_zh(leading_skill)}) "
            "never became explicit in the worked step"
        )
    if (
        leading_skill
        and leading_skill in matched
        and _has_counter_question_skill_handoff_pattern(
            worked_step,
            state=state,
            visible_skills=visible_skills,
            matched=matched,
            leading_skill=leading_skill,
        )
    ):
        return ""
    if role_split and leading_skill and leading_skill in matched:
        return ""
    if role_split and matched:
        return ""
    if len(combo) >= 4:
        required_count = 3
    elif len(visible_skills) >= 2:
        required_count = 2
    else:
        required_count = 1
    required_count = min(required_count, len(visible_skills)) if visible_skills else required_count
    if len(matched) >= required_count:
        return ""
    expected = ", ".join(
        f"`{skill}` ({get_skill_display_name_zh(skill)})"
        for skill in visible_skills[: max(required_count, 2)]
    )
    matched_text = ", ".join(f"`{skill}`" for skill in matched) if matched else "none"
    if matched:
        return (
            "execute-local refused: visible solve step named some live skills, but the current "
            "problem-facing combination never became visible as a combination. "
            f"Needed at least {required_count} active skills among: {expected}. "
            f"Matched: {matched_text}."
        )
    return (
        "execute-local refused: visible solve step fell back to ordinary narration; "
        f"fresh blind output must explicitly express at least {required_count} active "
        f"problem-facing skills on the current layer. Needed among: {expected}. "
        f"Matched: {matched_text}."
    )


def _worked_step_ordinary_action_hits(worked_step: str) -> list[str]:
    hits: list[str] = []
    normalized = normalize_primitive_token(worked_step)
    for marker in ORDINARY_ACTION_MARKERS:
        if marker in worked_step or (normalize_primitive_token(marker) and normalize_primitive_token(marker) in normalized):
            if marker not in hits:
                hits.append(marker)
    for pattern, label in ORDINARY_ACTION_REGEXES:
        if pattern.search(worked_step) and label not in hits:
            hits.append(label)
    return hits


def _ordinary_operation_families(worked_step: str) -> list[str]:
    families: list[str] = []
    for hit in _worked_step_ordinary_action_hits(worked_step):
        family = ORDINARY_OPERATION_FAMILY_BY_HIT.get(hit)
        if family and family not in families:
            families.append(family)
    return families


def _owner_candidates_allow_assignment_surface(owner_candidates: list[str]) -> bool:
    normalized = {
        canonicalize_skill_token(skill)
        for skill in owner_candidates
        if canonicalize_skill_token(skill)
    }
    return bool(normalized.intersection(ASSIGNMENT_FRIENDLY_SKILLS))


def _ordinary_family_can_stay_visible_under_skill_layer(
    family: str,
    *,
    owner_candidates: list[str],
) -> bool:
    if family in VISIBLE_SUBORDINATE_ORDINARY_OPERATION_FAMILIES:
        return True
    if family == "symbol_binding":
        return _owner_candidates_allow_assignment_surface(owner_candidates)
    return False


def _worked_step_auxiliary_assignment_hits(
    worked_step: str,
    *,
    matched: list[str],
    leading_skill: str,
) -> list[str]:
    owner_skills = {canonicalize_skill_token(leading_skill)}
    owner_skills.update(canonicalize_skill_token(skill) for skill in matched)
    owner_skills.discard("")
    if owner_skills & ASSIGNMENT_FRIENDLY_SKILLS:
        return []
    hits: list[str] = []
    for segment in ORDINARY_CONTEXT_SPLIT_REGEX.split(worked_step):
        segment = segment.strip()
        if not segment:
            continue
        if AUXILIARY_ASSIGNMENT_REGEX.search(segment):
            hits.append("设元/换元")
            break
    return hits


def _worked_step_regrowth_hits(
    worked_step: str,
    *,
    matched: list[str],
    leading_skill: str,
) -> list[str]:
    hits = _worked_step_ordinary_action_hits(worked_step)
    for label in _worked_step_auxiliary_assignment_hits(
        worked_step,
        matched=matched,
        leading_skill=leading_skill,
    ):
        if label not in hits:
            hits.append(label)
    return hits


def _ordinary_regrowth_segment_is_excused(segment: str) -> bool:
    return any(marker in segment for marker in ORDINARY_DENIAL_MARKERS + COUNTER_QUESTION_MARKERS)


def _first_unexcused_regrowth_hit(
    worked_step: str,
    *,
    matched: list[str],
    leading_skill: str,
) -> str:
    for segment in ORDINARY_CONTEXT_SPLIT_REGEX.split(worked_step):
        segment = segment.strip()
        if not segment:
            continue
        segment_hits = _worked_step_regrowth_hits(
            segment,
            matched=matched,
            leading_skill=leading_skill,
        )
        if not segment_hits:
            continue
        if _ordinary_regrowth_segment_is_excused(segment):
            continue
        return segment_hits[0]
    return ""


def _ordinary_regrowth_hits_are_explicitly_denied(
    worked_step: str,
    *,
    matched: list[str],
    leading_skill: str,
) -> bool:
    saw_hit = False
    for segment in ORDINARY_CONTEXT_SPLIT_REGEX.split(worked_step):
        segment = segment.strip()
        if not segment:
            continue
        segment_hits = _worked_step_regrowth_hits(
            segment,
            matched=matched,
            leading_skill=leading_skill,
        )
        if not segment_hits:
            continue
        saw_hit = True
        if not _ordinary_regrowth_segment_is_excused(segment):
            return False
    return saw_hit


def _worked_step_marker_hits(worked_step: str, markers: list[str]) -> list[str]:
    hits: list[str] = []
    normalized = normalize_primitive_token(worked_step)
    for marker in markers:
        normalized_marker = normalize_primitive_token(marker)
        if marker in worked_step or (normalized_marker and normalized_marker in normalized):
            if marker not in hits:
                hits.append(marker)
    return hits


def _derive_visible_problem_skills_from_state(
    state: dict,
    *,
    state_path: Path | None = None,
) -> tuple[list[str], str]:
    layer = state.get("layer_composition_if_any")
    combo = (
        _normalized_skill_list(layer.get("active_skill_combo_if_any"), limit=8)
        if isinstance(layer, dict)
        else []
    )
    leading_skill = (
        canonicalize_skill_token(layer.get("leading_skill_if_any"))
        if isinstance(layer, dict)
        else ""
    )
    if not combo and state_path is not None:
        report = build_report(state, state_path)
        report_layer = report.get("layer_composition")
        report_combo = (
            _normalized_skill_list(report_layer.get("active_skill_combo_if_any"), limit=8)
            if isinstance(report_layer, dict)
            else []
        )
        if report_combo:
            combo = report_combo
            leading_skill = canonicalize_skill_token(
                report_layer.get("leading_skill_if_any")
            )
    visible_skills = [skill for skill in combo if skill not in READOUT_LIKE_SKILLS]
    return visible_skills, leading_skill


def _fresh_blind_execute_local_state_ownership_context(state: dict) -> dict:
    if not _fresh_blind_mode_active_from_state(state):
        return {}
    layer = state.get("layer_composition_if_any")
    if not isinstance(layer, dict):
        return {}
    if layer.get("event_owned") is not True:
        return {}
    if _nonempty_text(layer.get("surface")) != "bound_program":
        return {}

    visible_skills, leading_skill = _derive_visible_problem_skills_from_state(state)
    combo = _normalized_skill_list(layer.get("active_skill_combo_if_any"), limit=8)
    if not visible_skills or not leading_skill or leading_skill not in visible_skills:
        return {}
    if leading_skill not in combo:
        return {}

    authorized_bite = project_bound_program_shape(layer.get("authorized_bite"))
    bound_program = project_bound_program_shape(state.get("bound_program"))
    if not isinstance(authorized_bite, dict) or not has_explicit_skill_ownership(authorized_bite):
        return {}
    if not isinstance(bound_program, dict) or not has_explicit_skill_ownership(bound_program):
        return {}
    if programs_conflict(authorized_bite, bound_program):
        return {}

    authorized_owner = canonicalize_skill_token(authorized_bite.get("owner_skill_if_any"))
    bound_owner = canonicalize_skill_token(bound_program.get("owner_skill_if_any"))
    if leading_skill not in {authorized_owner, bound_owner}:
        return {}

    owner_combo = _merged_skill_lists(
        combo,
        extract_explicit_skill_combo(authorized_bite),
        extract_explicit_skill_combo(bound_program),
        limit=8,
    )
    if leading_skill not in owner_combo:
        return {}

    return {
        "leading_skill": leading_skill,
        "visible_skills": visible_skills,
        "owner_combo": owner_combo,
    }


def _state_owned_touch_anchor_candidates(state: dict) -> list[str]:
    texts: list[str] = []
    for key in ["current_object", "current_seam", "current_debt", "next_bite"]:
        text = _nonempty_text(state.get(key))
        if text:
            texts.append(text)
    layer = state.get("layer_composition_if_any")
    if isinstance(layer, dict):
        for key in ["layer_object", "controlled_object", "current_seam", "current_debt"]:
            text = _nonempty_text(layer.get(key))
            if text:
                texts.append(text)
        authorized_bite = project_bound_program_shape(layer.get("authorized_bite"))
        if isinstance(authorized_bite, dict):
            for key in ["target", "operation", "success_signal"]:
                text = _nonempty_text(authorized_bite.get(key))
                if text:
                    texts.append(text)
        lighting = layer.get("lighting_if_any")
        if isinstance(lighting, dict):
            role_split = lighting.get("role_split_if_any")
            if isinstance(role_split, dict):
                text = _nonempty_text(role_split.get("check_target_if_any"))
                if text:
                    texts.append(text)

    bound_program = project_bound_program_shape(state.get("bound_program"))
    if isinstance(bound_program, dict):
        for key in ["target", "operation", "success_signal"]:
            text = _nonempty_text(bound_program.get(key))
            if text:
                texts.append(text)

    candidates: list[str] = []
    seen: set[str] = set()

    def add_candidate(raw: object) -> None:
        text = _nonempty_text(raw)
        if not text or is_generic_runtime_shell_text(text) or is_meta_narration_text(text):
            return
        normalized = normalize_primitive_token(text)
        if not normalized:
            return
        formula_like = any(ch.isdigit() or ch in "=<>+-*/^" for ch in text)
        if not formula_like and len(normalized) < 4:
            return
        if normalized in seen:
            return
        seen.add(normalized)
        candidates.append(text)

    for text in texts:
        add_candidate(text)
        for segment in STATE_TOUCH_ANCHOR_SPLIT_REGEX.split(text):
            add_candidate(segment.strip())
        for formula in STATE_TOUCH_FORMULA_REGEX.findall(text):
            if any(ch.isdigit() or ch in "=<>+-*/^" for ch in formula):
                add_candidate(formula)

    return candidates[:24]


def _worked_step_state_owned_touch_anchor_score(
    worked_step: str,
    *,
    state: dict,
) -> int:
    normalized_step = normalize_primitive_token(worked_step)
    if not normalized_step:
        return 0

    score = 0
    for candidate in _state_owned_touch_anchor_candidates(state):
        normalized_candidate = normalize_primitive_token(candidate)
        if not normalized_candidate or normalized_candidate not in normalized_step:
            continue
        if any(ch.isdigit() or ch in "=<>+-*/^" for ch in candidate) or len(normalized_candidate) >= 8:
            score += 2
        else:
            score += 1
        if score >= 3:
            break
    return score


def _worked_step_has_state_owned_touch_anchor(
    worked_step: str,
    *,
    state: dict,
) -> bool:
    return _worked_step_state_owned_touch_anchor_score(worked_step, state=state) >= 2


def _semantic_visible_skill_matches(
    worked_step: str,
    *,
    state: dict,
    visible_skills: list[str],
    matched: list[str],
    leading_skill: str,
    state_backed_context: dict | None = None,
) -> list[str]:
    if not visible_skills:
        return matched[:]

    ownership_context = (
        state_backed_context
        if isinstance(state_backed_context, dict) and state_backed_context
        else _fresh_blind_execute_local_state_ownership_context(state)
    )
    if not ownership_context:
        return matched[:]

    anchor_score = _worked_step_state_owned_touch_anchor_score(worked_step, state=state)
    if anchor_score < 2:
        return matched[:]

    explicit_visible = _explicit_skill_mentions_in_text(
        worked_step=worked_step,
        candidates=visible_skills,
    )
    touchlike_hits = _worked_step_marker_hits(
        worked_step,
        FALLBACK_ACTION_MARKERS + ORDINARY_ACTION_MARKERS + CHECK_CONTEXT_MARKERS,
    )
    if not explicit_visible and not touchlike_hits and anchor_score < 3:
        return matched[:]

    owner_combo = [
        skill for skill in ownership_context.get("owner_combo", []) if skill in visible_skills
    ]
    return _merged_skill_lists(matched, [leading_skill], owner_combo, limit=8)


def _worked_step_foreign_problem_skill_mentions(
    worked_step: str,
    *,
    allowed_skills: list[str],
) -> list[str]:
    allowed = {
        canonicalize_skill_token(skill)
        for skill in allowed_skills
        if canonicalize_skill_token(skill)
    }
    foreign: list[str] = []
    for skill in _ordered_skill_mentions_in_text(
        worked_step=worked_step,
        candidates=[
            skill
            for skill in ALLOWED_PRIMITIVES
            if skill not in NON_PROBLEM_FACING_SKILLS
        ],
    ):
        normalized = canonicalize_skill_token(skill)
        if not normalized or normalized in allowed or normalized in foreign:
            continue
        foreign.append(normalized)
    return foreign


def _live_role_split(state: dict) -> dict:
    layer = state.get("layer_composition_if_any")
    if not isinstance(layer, dict):
        return {}
    lighting = layer.get("lighting_if_any")
    if not isinstance(lighting, dict):
        return {}
    role_split = lighting.get("role_split_if_any")
    return dict(role_split) if isinstance(role_split, dict) else {}


def _live_ordinary_operation_policy(state: dict) -> tuple[set[str], set[str]]:
    role_split = _live_role_split(state)
    if not isinstance(role_split, dict):
        return set(), set()
    allowed = {
        _nonempty_text(value)
        for value in (role_split.get("allowed_subordinate_operation_families_if_any") or [])
        if _nonempty_text(value)
    }
    blocked = {
        _nonempty_text(value)
        for value in (role_split.get("blocked_ordinary_operation_families_if_any") or [])
        if _nonempty_text(value)
    }
    return allowed, blocked


def _ordinary_action_can_stay_subordinate(
    worked_step: str,
    *,
    state: dict,
    matched: list[str],
    leading_skill: str,
) -> bool:
    role_split = _live_role_split(state)
    allowed_families, blocked_families = _live_ordinary_operation_policy(state)
    owner_candidates = [skill for skill in _merged_skill_lists([leading_skill], matched, limit=8) if skill]
    saw_unexcused_hit = False

    for sentence in ORDINARY_SENTENCE_SPLIT_REGEX.split(worked_step):
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence_hits = _worked_step_regrowth_hits(
            sentence,
            matched=matched,
            leading_skill=leading_skill,
        )
        if not sentence_hits or _ordinary_regrowth_segment_is_excused(sentence):
            continue
        saw_unexcused_hit = True
        if any(marker in sentence for marker in SUBORDINATE_ORDINARY_BLOCKERS):
            return False
        sentence_families = set(_ordinary_operation_families(sentence))
        if blocked_families and sentence_families.intersection(blocked_families):
            return False
        if sentence_families and any(
            family in NON_SERIALIZABLE_ORDINARY_OPERATION_FAMILIES
            for family in sentence_families
        ):
            return False
        if sentence_families and any(
            not _ordinary_family_can_stay_visible_under_skill_layer(
                family,
                owner_candidates=owner_candidates,
            )
            for family in sentence_families
        ):
            return False
        if allowed_families and sentence_families and not sentence_families.issubset(allowed_families):
            return False

        has_owner_touch = bool(
            owner_candidates
            and _explicit_skill_mentions_in_text(
                worked_step=sentence,
                candidates=owner_candidates,
            )
        )
        if not has_owner_touch:
            has_owner_touch = _worked_step_has_state_owned_touch_anchor(sentence, state=state)
        if not has_owner_touch:
            return False

        has_subordination_signal = any(marker in sentence for marker in ORDINARY_SUBORDINATION_MARKERS)
        if not has_subordination_signal and _worked_step_marker_hits(sentence, CHECK_CONTEXT_MARKERS):
            has_subordination_signal = bool(
                canonicalize_skill_token(role_split.get("check_skill_if_any"))
                or _nonempty_text(role_split.get("check_target_if_any"))
                or _nonempty_text(role_split.get("check_kind_if_any"))
            )
        if not has_subordination_signal:
            sentence_anchor_score = _worked_step_state_owned_touch_anchor_score(
                sentence,
                state=state,
            )
            if sentence_anchor_score >= 3 and sentence_families and sentence_families.issubset(
                {"symbol_binding", "algebraic_manipulation", "equation_solving"}
            ):
                has_subordination_signal = True
        if not has_subordination_signal:
            return False

    return saw_unexcused_hit


def _state_shaping_ordinary_regrowth_refusal(
    *,
    state: dict,
    state_path: Path,
    candidate_texts: list[str],
) -> str:
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return ""
    if _nonempty_text(bootstrap_context.get("mode")) != "fresh_blind_project_skills_on":
        return ""
    visible_skills, leading_skill = _derive_visible_problem_skills_from_state(
        state,
        state_path=state_path,
    )
    if not visible_skills:
        return ""
    combined = "\n".join(text for text in candidate_texts if text).strip()
    if not combined:
        return ""
    inferred = set(infer_primitives_from_text(combined))
    inferred.update(
        _explicit_skill_mentions_in_text(worked_step=combined, candidates=visible_skills)
    )
    matched = [skill for skill in visible_skills if skill in inferred]
    ordinary_hits = _worked_step_regrowth_hits(
        combined,
        matched=matched,
        leading_skill=leading_skill,
    )
    if not ordinary_hits:
        return ""
    if _ordinary_action_can_stay_subordinate(
        combined,
        state=state,
        matched=matched,
        leading_skill=leading_skill,
    ):
        return ""
    if _has_counter_question_skill_handoff_pattern(
        combined,
        state=state,
        visible_skills=visible_skills,
        matched=matched,
        leading_skill=leading_skill,
    ):
        return ""
    coaching_surface = derive_local_skill_coaching_surface(state, [])
    denial_hint = ""
    handoff_hint = ""
    if isinstance(coaching_surface, dict):
        denial_hint = _nonempty_text(coaching_surface.get("ordinary_action_denial_if_any"))
        handoff_hint = _nonempty_text(coaching_surface.get("skill_positive_handoff_if_any"))
    hint = " ".join(value for value in [denial_hint, handoff_hint] if value)
    if not hint:
        hint = f"先不要把下一步写成普通动作，先让 `{leading_skill or visible_skills[0]}` 接管。"
    ordinary_text = _first_unexcused_regrowth_hit(
        combined,
        matched=matched,
        leading_skill=leading_skill,
    ) or ordinary_hits[0]
    return (
        "set-core refused: ordinary fallback action `"
        + ordinary_text
        + "` regrew inside the freshly narrowed live layer. "
        + hint
    )


def _has_denial_and_skill_handoff_pattern(
    worked_step: str,
    *,
    visible_skills: list[str],
    matched: list[str],
    leading_skill: str,
) -> bool:
    if not worked_step or not visible_skills:
        return False
    if leading_skill and leading_skill not in matched:
        return False
    if not _ordinary_regrowth_hits_are_explicitly_denied(
        worked_step,
        matched=matched,
        leading_skill=leading_skill,
    ):
        return False
    denial = any(marker in worked_step for marker in ORDINARY_DENIAL_MARKERS)
    positive_handoff = any(marker in worked_step for marker in SKILL_POSITIVE_HANDOFF_MARKERS)
    return bool(denial and positive_handoff and matched)


def _has_counter_question_skill_handoff_pattern(
    worked_step: str,
    *,
    state: dict,
    visible_skills: list[str],
    matched: list[str],
    leading_skill: str,
) -> bool:
    ordinary_hits = _worked_step_regrowth_hits(
        worked_step,
        matched=matched,
        leading_skill=leading_skill,
    )
    if not ordinary_hits:
        return False
    if not _has_denial_and_skill_handoff_pattern(
        worked_step,
        visible_skills=visible_skills,
        matched=matched,
        leading_skill=leading_skill,
    ):
        return False
    counter_question = any(marker in worked_step for marker in COUNTER_QUESTION_MARKERS)
    # A literal question mark is helpful but not mandatory when the worked step
    # already clearly denies the ordinary move and hands control to the live skill.
    return True if counter_question or any(marker in worked_step for marker in ORDINARY_DENIAL_MARKERS) else False


def _ordinary_action_regrowth_refusal(
    worked_step: str,
    *,
    state: dict,
    visible_skills: list[str],
    matched: list[str],
    leading_skill: str,
) -> str:
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return ""
    if _nonempty_text(bootstrap_context.get("mode")) != "fresh_blind_project_skills_on":
        return ""
    if not visible_skills:
        return ""
    ordinary_hits = _worked_step_regrowth_hits(
        worked_step,
        matched=matched,
        leading_skill=leading_skill,
    )
    if not ordinary_hits:
        return ""
    if _ordinary_action_can_stay_subordinate(
        worked_step,
        state=state,
        matched=matched,
        leading_skill=leading_skill,
    ):
        return ""
    if _has_counter_question_skill_handoff_pattern(
        worked_step,
        state=state,
        visible_skills=visible_skills,
        matched=matched,
        leading_skill=leading_skill,
    ):
        return ""
    coaching_surface = derive_local_skill_coaching_surface(state, [])
    denial_hint = ""
    handoff_hint = ""
    if isinstance(coaching_surface, dict):
        denial_hint = _nonempty_text(coaching_surface.get("ordinary_action_denial_if_any"))
        handoff_hint = _nonempty_text(coaching_surface.get("skill_positive_handoff_if_any"))
    ordinary_text = _first_unexcused_regrowth_hit(
        worked_step,
        matched=matched,
        leading_skill=leading_skill,
    ) or ordinary_hits[0]
    leading_text = leading_skill or (matched[0] if matched else (visible_skills[0] if visible_skills else "当前技能"))
    hint = "需要先明确说出这一步不需要该普通动作，并把控制权交回当前层技能。"
    if denial_hint or handoff_hint:
        hint = " ".join(value for value in [denial_hint, handoff_hint] if value)
    return (
        "execute-local refused: ordinary fallback action `"
        + ordinary_text
        + "` regrew inside a live skill-owned layer before the worked step challenged it. "
        + hint
        + f" 当前应先由 `{leading_text}` 接管。"
    )


def _fallback_family_refusal(
    worked_step: str,
    *,
    state: dict,
    visible_skills: list[str],
    matched: list[str],
    leading_skill: str,
) -> str:
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return ""
    if _nonempty_text(bootstrap_context.get("mode")) != "fresh_blind_project_skills_on":
        return ""
    if not visible_skills:
        return ""
    if _has_denial_and_skill_handoff_pattern(
        worked_step,
        visible_skills=visible_skills,
        matched=matched,
        leading_skill=leading_skill,
    ):
        return ""
    coaching_surface = derive_local_skill_coaching_surface(state, [])
    handoff_hint = ""
    if isinstance(coaching_surface, dict):
        handoff_hint = " ".join(
            value
            for value in [
                _nonempty_text(coaching_surface.get("ordinary_action_denial_if_any")),
                _nonempty_text(coaching_surface.get("skill_positive_handoff_if_any")),
            ]
            if value
        )
    if not handoff_hint:
        handoff_hint = f"需要先否定旧动作，再明确由 `{leading_skill or (visible_skills[0] if visible_skills else '当前技能')}` 接管。"

    thick_hits = _worked_step_marker_hits(worked_step, THICK_OBJECT_RETURN_MARKERS)
    if thick_hits:
        return (
            "execute-local refused: worked_step tried to return to a thicker/original object before the current layer finished spending its owned bite. "
            + handoff_hint
        )

    explanation_hits = _worked_step_marker_hits(worked_step, EXPLANATION_ONLY_MARKERS)
    if explanation_hits:
        action_hits = _worked_step_marker_hits(
            worked_step,
            FALLBACK_ACTION_MARKERS + ORDINARY_ACTION_MARKERS,
        )
        if not action_hits or _worked_step_marker_hits(worked_step, EXPLANATION_STALL_MARKERS):
            return (
                "execute-local refused: explanation without touch does not count as progress on a live skill-owned layer. "
                + handoff_hint
            )

    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    if asked_medium:
        asked_hits = _worked_step_marker_hits(worked_step, ASKED_MEDIUM_RUSH_MARKERS + [asked_medium])
        if asked_hits:
            bound_program = project_bound_program_shape(state.get("bound_program"))
            if not program_is_asked_medium_closure(bound_program, asked_medium=asked_medium):
                return (
                    "execute-local refused: worked_step rushed toward the asked medium before the current layer had earned closure ownership. "
                    + handoff_hint
                )

    counterexample_hits = _worked_step_marker_hits(worked_step, COUNTEREXAMPLE_CONTINUATION_MARKERS)
    if counterexample_hits and leading_skill and leading_skill != "反问":
        return (
            "execute-local refused: the worked step kept leaning on an old counterexample thread after authority had already returned to a structural skill. "
            + handoff_hint
        )
    return ""


def _worked_step_result_only_refusal(
    worked_step: str,
    *,
    state: dict,
) -> str:
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return ""
    if _nonempty_text(bootstrap_context.get("mode")) != "fresh_blind_project_skills_on":
        return ""

    normalized = normalize_primitive_token(worked_step)
    if not normalized:
        return ""

    result_only_markers = [
        "解决了",
        "统一解决",
        "锁定",
        "成立",
        "确定",
        "完成了",
        "完成",
        "得出",
        "推出",
        "可以标记为",
        "均已确定",
        "闭合",
        "solved",
        "settled",
        "determined",
        "therefore",
        "hence",
    ]
    action_markers = [
        "改写",
        "重写",
        "画图",
        "画出",
        "取",
        "设",
        "令",
        "比较",
        "代入",
        "联立",
        "化为",
        "压到",
        "压成",
        "统一到",
        "构造",
        "检查",
        "检验",
        "截点",
        "峰值",
        "奇点",
        "rewrite",
        "draw",
        "graph",
        "set",
        "compare",
        "project",
        "split",
        "probe",
        "check",
        "test",
        "boundary",
        "intersection",
        "level set",
    ]
    if not any(marker in worked_step for marker in result_only_markers):
        return ""
    if any(marker in worked_step for marker in action_markers):
        return ""

    layer = state.get("layer_composition_if_any")
    leading_skill = ""
    if isinstance(layer, dict):
        leading_skill = canonicalize_skill_token(layer.get("leading_skill_if_any"))
    if not leading_skill:
        bound_program = project_bound_program_shape(state.get("bound_program"))
        if isinstance(bound_program, dict):
            leading_skill = canonicalize_skill_token(bound_program.get("owner_skill_if_any"))

    if not leading_skill:
        return ""
    return (
        "execute-local refused: worked_step only reported that something was solved, "
        "but did not show the current-layer action owned by the live skill `"
        + leading_skill
        + "`."
    )


def _merged_skill_lists(*values: object, limit: int = 8) -> list[str]:
    merged: list[str] = []
    for value in values:
        for skill_name in _normalized_skill_list(value, limit=limit):
            if skill_name not in merged:
                merged.append(skill_name)
            if len(merged) == limit:
                return merged
    return merged


def _nonempty_text(value: object) -> str:
    return str(value or "").strip()


def _gap_target_from_excerpt(excerpt: dict) -> str:
    gap_object = excerpt.get("gap_object")
    if not isinstance(gap_object, dict):
        return ""
    return _nonempty_text(gap_object.get("object"))


def _synthesize_layer_composition_from_event(event: dict) -> dict | None:
    excerpt = event.get("report_excerpt", {})
    if not isinstance(excerpt, dict):
        excerpt = {}

    raw_layer = excerpt.get("layer_composition")
    if not isinstance(raw_layer, dict):
        return None
    explicit = dict(raw_layer)
    combo = _normalized_skill_list(explicit.get("active_skill_combo_if_any"))
    if not combo:
        return None
    explicit["active_skill_combo_if_any"] = combo
    return explicit


def _explicit_layer_composition_from_event(event: dict) -> dict | None:
    excerpt = event.get("report_excerpt", {})
    raw_layer = None
    after_layer = None
    if isinstance(excerpt, dict):
        candidate = excerpt.get("layer_composition")
        if isinstance(candidate, dict):
            raw_layer = candidate
    after = event.get("after", {})
    if isinstance(after, dict):
        candidate = after.get("layer_composition_if_any")
        if isinstance(candidate, dict) and candidate.get("event_owned") is True:
            after_layer = candidate
    if isinstance(raw_layer, dict) and isinstance(after_layer, dict):
        merged_layer = dict(raw_layer)
        merged_layer.update(after_layer)
        raw_lighting = raw_layer.get("lighting_if_any")
        after_lighting = after_layer.get("lighting_if_any")
        if isinstance(raw_lighting, dict) or isinstance(after_lighting, dict):
            merged_lighting = {}
            if isinstance(raw_lighting, dict):
                merged_lighting.update(raw_lighting)
            if isinstance(after_lighting, dict):
                merged_lighting.update(after_lighting)
            merged_layer["lighting_if_any"] = merged_lighting
        raw_layer = merged_layer
    elif not isinstance(raw_layer, dict) and isinstance(after_layer, dict):
        raw_layer = after_layer
    if not isinstance(raw_layer, dict):
        return None
    layer = dict(raw_layer)
    combo = _normalized_skill_list(layer.get("active_skill_combo_if_any"))
    if not combo:
        return None
    explicit = dict(layer)
    explicit["active_skill_combo_if_any"] = combo
    return explicit


def _runtime_qualified_skill_combo(
    layer: dict | None,
    *,
    leading_skill: str = "",
) -> list[str]:
    if not isinstance(layer, dict):
        return []
    base_combo = _normalized_skill_list(layer.get("active_skill_combo_if_any"))
    supporting = _display_supporting_skills(
        layer,
        leading_skill=leading_skill,
    )
    qualified = _merged_skill_lists(base_combo, supporting, limit=8)
    if leading_skill:
        qualified = _merged_skill_lists([leading_skill], qualified, limit=8)
    return qualified


def _skill_composition_step_refusals(event: dict) -> list[str]:
    layer = _explicit_layer_composition_from_event(event)
    if not isinstance(layer, dict):
        return ["report_excerpt.layer_composition missing or empty"]

    refusals: list[str] = []
    leading_skill = str(layer.get("leading_skill_if_any", "")).strip()
    combo = _runtime_qualified_skill_combo(layer, leading_skill=leading_skill)
    if len(combo) < 2:
        refusals.append("active skill combo never became a real combination")
    problem_facing = [
        skill
        for skill in combo
        if skill not in {
            "外壳怀疑",
            "最终控制者",
            "抓本质",
            "更薄载体重选",
            "精确封口",
            "反问",
            "监督",
            "元认知",
            "中枢控制",
            "后脑守卫",
            "奖惩塑形",
            "读出",
            "定义即直接读出",
            "投影读出",
            "主导机制读出",
            "向量差读出",
        }
    ]
    if not leading_skill:
        refusals.append("leading skill missing")
    elif leading_skill not in combo:
        refusals.append("leading skill is not inside the active combo")

    command = str(event.get("command", "")).strip()
    authorized_bite = project_bound_program_shape(layer.get("authorized_bite"))
    landed_bite = {}
    before = event.get("before", {})
    after = event.get("after", {})
    excerpt = event.get("report_excerpt", {})
    if not isinstance(before, dict):
        before = {}
    if not isinstance(after, dict):
        after = {}
    if not isinstance(excerpt, dict):
        excerpt = {}
    raw_warnings = excerpt.get("warnings")
    warnings = (
        [str(value).strip() for value in raw_warnings if str(value).strip()]
        if isinstance(raw_warnings, list)
        else []
    )
    terminal_asked_medium_读出 = bool(
        isinstance(authorized_bite, dict)
        and str(authorized_bite.get("kind", "")).strip() == "读出"
        and str(authorized_bite.get("target", "")).strip()
        == str(after.get("asked_medium_surface", "")).strip()
    )
    derived_surface_warning = any(
        warning in {
            "bound_program missing; derived next_touch used",
            "bound_program missing; landed next_touch inherited",
            "primitive_field_if_any was stale for the current layer; derived local primitive field used",
            "primitive_field_if_any missing; derived local primitive field used",
        }
        for warning in warnings
    )
    competition_excerpt = excerpt.get("skill_competition", {})
    compact_candidates = (
        competition_excerpt.get("candidates", [])
        if isinstance(competition_excerpt, dict)
        else []
    )
    if isinstance(compact_candidates, list) and compact_candidates:
        leading_backings = [
            str(candidate.get("backed_by", "")).strip()
            for candidate in compact_candidates
            if isinstance(candidate, dict)
            and str(candidate.get("skill", "")).strip() == leading_skill
            and str(candidate.get("backed_by", "")).strip()
        ]
        if leading_backings and all(backing == "primitive_field" for backing in leading_backings):
            partner_supported = any(
                isinstance(candidate, dict)
                and str(candidate.get("skill", "")).strip() == leading_skill
                and isinstance(candidate.get("supporting_skills_if_any"), list)
                and len([value for value in candidate.get("supporting_skills_if_any", []) if str(value).strip()]) > 0
                for candidate in compact_candidates
            )
            if not partner_supported:
                refusals.append(
                    "winning skill never gained support beyond a primitive-field echo"
                )
    if derived_surface_warning:
        if terminal_asked_medium_读出:
            pass
        elif (
            command == "land-local"
            and isinstance(project_bound_program_shape(before.get("bound_program")), dict)
            and project_bound_program_shape(before.get("bound_program"))
            and isinstance(authorized_bite, dict)
            and not is_generic_runtime_operation(project_bound_program_shape(before.get("bound_program")))
            and not is_generic_runtime_operation(authorized_bite)
        ):
            pass
        elif (
            command in {"bind-local", "spend-local", "execute-local", "materialize-asked-medium"}
            and layer.get("event_owned") is True
            and isinstance(authorized_bite, dict)
            and has_explicit_skill_ownership(authorized_bite)
            and not is_generic_runtime_operation(authorized_bite)
        ):
            # Post-transition report refresh may legitimately derive the next
            # primitive surface for continuation, but that should not erase the
            # fact that the transition itself was an explicit owned bite.
            pass
        else:
            refusals.append(
                "report still relied on derived or inherited runtime surfaces instead of one explicitly owned layer transition"
            )
    if not problem_facing and not terminal_asked_medium_读出:
        refusals.append("skill combo never left control/读出-only settling")
    if layer.get("event_owned") is not True:
        refusals.append("layer composition was not recorded as an event-owned step")
    if command == "land-local":
        landed_bite = project_bound_program_shape(before.get("bound_program")) or {}
        if not isinstance(landed_bite, dict) or not landed_bite:
            refusals.append("land-local never exposed the concrete landed bite that changed the layer")
        elif is_generic_runtime_operation(landed_bite):
            refusals.append("landed bite stayed at a generic runtime template instead of a problem-born action")
        elif program_has_meta_narration(landed_bite):
            refusals.append("landed bite stayed at control/meta narration instead of a concrete problem-born action")
        if not isinstance(authorized_bite, dict):
            refusals.append("authorized bite missing from explicit layer composition")
    else:
        if not isinstance(authorized_bite, dict):
            refusals.append("authorized bite missing from explicit layer composition")
        elif is_generic_runtime_operation(authorized_bite):
            refusals.append("authorized bite stayed at a generic runtime template instead of a problem-born action")
        elif program_has_meta_narration(authorized_bite):
            refusals.append("authorized bite stayed at control/meta narration instead of a concrete problem-born action")

    layer_object = str(layer.get("layer_object", "")).strip()
    controlled_object = str(layer.get("controlled_object", "")).strip()
    current_seam = str(layer.get("current_seam", "")).strip()
    current_debt = str(layer.get("current_debt", "")).strip()
    reason = str(layer.get("reason", "")).strip()
    transition_change = str(layer.get("transition_change", "")).strip()
    if not layer_object:
        refusals.append("layer object missing")
    if not controlled_object:
        refusals.append("controlled object missing")
    if not current_debt:
        refusals.append("current debt missing")
    if not reason:
        refusals.append("local takeover reason missing")
    if not transition_change:
        refusals.append("transition change missing")

    previous_object = str(before.get("current_object", "")).strip()
    previous_seam = str(before.get("current_seam", "")).strip()
    previous_debt = str(before.get("current_debt", "")).strip()
    previous_bite = str(before.get("next_bite", "")).strip()
    after_object = str(after.get("current_object", "")).strip()
    after_bite = str(after.get("next_bite", "")).strip()
    surface = str(layer.get("surface", "")).strip()
    next_choice = str(layer.get("next_local_choice", "")).strip()
    gap_object = str(layer.get("gap_object", "")).strip()
    asked_medium = str(after.get("asked_medium_surface", "")).strip()
    authorized_bite = project_bound_program_shape(layer.get("authorized_bite"))
    next_controller = next_choice or gap_object
    distinct_next_controller = bool(
        next_controller
        and next_controller not in {previous_object, layer_object, controlled_object}
    )
    terminal_asked_medium_读出 = bool(
        isinstance(authorized_bite, dict)
        and str(authorized_bite.get("kind", "")).strip() == "读出"
        and asked_medium
        and str(authorized_bite.get("target", "")).strip() == asked_medium
    )
    lighting = layer.get("lighting_if_any")
    if not isinstance(lighting, dict):
        lighting = {}
    candidate_skills = _normalized_skill_list(lighting.get("candidate_skills_if_any"), limit=8)
    lit_skill = str(lighting.get("lit_skill_if_any", "")).strip()
    role_split = lighting.get("role_split_if_any")
    if not isinstance(role_split, dict):
        role_split = {}
    role_primary = str(role_split.get("primary_skill_if_any", "")).strip()
    role_supporting = _normalized_skill_list(role_split.get("supporting_skills_if_any"), limit=4)
    role_check_kind = str(role_split.get("check_kind_if_any", "")).strip()
    role_check_target = str(role_split.get("check_target_if_any", "")).strip()
    if not candidate_skills:
        refusals.append("no candidate skill field was ever lit before the owned bite")
    elif (
        len(candidate_skills) == 1
        and len(combo) >= 2
        and not (command == "execute-local" and role_supporting)
    ):
        refusals.append("supporting skills only appeared after ownership was already declared")
    if lit_skill and lit_skill not in combo:
        refusals.append("the first lit skill never survived into the owned current-layer combo")
    if role_primary and leading_skill and role_primary != leading_skill:
        refusals.append("role split and leading skill disagreed about first takeover")
    if len(combo) >= 2 and not role_supporting:
        refusals.append("current-layer roles never exposed any supporting skills")
    if role_split and role_split.get("ordinary_operations_are_not_skills") is not True:
        refusals.append("role split never marked ordinary operations as non-skills")
    if not terminal_asked_medium_读出 and (not role_check_kind or not role_check_target):
        refusals.append("current-layer roles never exposed a concrete verification touch")

    if command in {"bind-local", "spend-local"}:
        changed_object = bool(
            controlled_object
            and previous_object
            and controlled_object != previous_object
        ) or distinct_next_controller
        if surface != "bound_program":
            refusals.append("local bind/spend did not stay on a bound_program surface")
        if not changed_object:
            refusals.append(
                "step never changed the mathematical object beyond the previous layer"
            )
        if (
            not distinct_next_controller
            and not terminal_asked_medium_读出
            and not (
                command == "bind-local"
                and controlled_object
                and previous_object
                and controlled_object != previous_object
            )
        ):
            refusals.append("step never emitted a distinct next-layer controller")

    if command == "execute-local":
        if surface != "bound_program":
            refusals.append("execute-local did not stay on a bound_program surface")
        evidence = after.get("materialization_evidence")
        if not isinstance(evidence, dict):
            refusals.append("execute-local never recorded execution evidence")
        output_status = after.get("output_status")
        if not isinstance(output_status, dict) or output_status.get("touched") is not True:
            refusals.append("execute-local never marked the live bite as touched")

    if command == "spend-local" and previous_object and after_object and previous_object == after_object:
        refusals.append("spend-local never moved authority onto a different current object")

    if command == "land-local":
        reopened_layer_changed = any(
            [
                bool(previous_object and after_object and previous_object != after_object),
                bool(previous_seam and current_seam and previous_seam != current_seam),
                bool(previous_debt and current_debt and previous_debt != current_debt),
                bool(previous_bite and after_bite and previous_bite != after_bite),
            ]
        )
        reopened_controller_tightened = any(
            [
                bool(previous_seam and current_seam and previous_seam != current_seam),
                bool(previous_debt and current_debt and previous_debt != current_debt),
                bool(previous_bite and after_bite and previous_bite != after_bite),
            ]
        )
        if surface != "takeover_recomposition":
            refusals.append("land-local did not reopen as takeover recomposition")
        if not reopened_layer_changed:
            refusals.append("land-local never changed the current mathematical object")
        if not next_controller:
            refusals.append("recomposition did not expose the next local object or gap")
        elif next_controller == previous_object and not reopened_controller_tightened:
            refusals.append("recomposition never emitted a controller beyond the previous object")

    if isinstance(authorized_bite, dict):
        bite_kind = str(authorized_bite.get("kind", "")).strip()
        bite_target = str(authorized_bite.get("target", "")).strip()
        bite_owner = str(authorized_bite.get("owner_skill_if_any", "")).strip() or leading_skill
        closure_lane_text = " ".join(
            value.strip().lower()
            for value in [bite_target, current_debt, current_seam, gap_object, next_choice]
            if str(value).strip()
        )
        closure_decision_lane = any(
            token in closure_lane_text
            for token in [
                "root",
                "roots",
                "feasible",
                "admissible",
                "reject",
                "exclude",
                "oversized",
                "range",
                "根",
                "可行",
                "舍去",
                "排除",
                "范围",
            ]
        )
        closure_owner_allowed = bite_owner in {
            "精确封口",
            "读出",
            "定义即直接读出",
            "投影读出",
            "主导机制读出",
            "向量差读出",
            "极限边界",
            "赋值",
            "第一裂缝",
        }
        real_combo_skills = [
            skill
            for skill in combo
            if skill
            and skill not in REOPEN_COMPETITION_DISALLOWED_SKILLS
            and skill != "精确封口"
        ]
        readout_combo_live = any(
            skill in {
                "读出",
                "定义即直接读出",
                "投影读出",
                "主导机制读出",
                "向量差读出",
            }
            for skill in combo
        )
        closure_decisive_combo_live = any(
            skill in {
                "见证",
                "极限边界",
                "赋值",
                "第一裂缝",
                "对称",
                "对称消元",
                "特殊值探针",
            }
            for skill in combo
        )
        if not closure_owner_allowed:
            closure_owner_allowed = bool(
                asked_medium
                and bite_target == asked_medium
                and readout_combo_live
                and closure_decisive_combo_live
                and real_combo_skills
            )
        if bite_kind == "write" and asked_medium and bite_target == asked_medium and not closure_owner_allowed:
            refusals.append("write reached the asked medium before a real closure owner took control")
        if (
            surface == "takeover_recomposition"
            and bite_kind == "write"
            and asked_medium
            and bite_target == asked_medium
            and next_controller
            and next_controller != asked_medium
        ):
            refusals.append(
                "reopened layer tried to close on the asked medium before the new current object was spent"
            )
        real_closure_lit = (
            lit_skill in {"精确封口", "读出"}
            or role_primary in {"精确封口", "读出"}
            or leading_skill in {"精确封口", "读出"}
        )
        if (
            bite_kind == "write"
            and closure_decision_lane
            and real_closure_lit
            and bite_owner in {"图像", "读出", "见证"}
            and any(skill in combo for skill in ["极限边界", "赋值", "第一裂缝", "精确封口"])
        ):
            refusals.append(
                "closure-decision layer kept a carrier or 读出 skill in front after a real closure skill was already lit"
            )

    return refusals


def _state_focus_summary(state: dict) -> dict:
    summary: dict = {
        "current_object": state.get("current_object", ""),
        "current_seam": state.get("current_seam", ""),
        "current_debt": state.get("current_debt", ""),
        "next_bite": state.get("next_bite", ""),
        "asked_medium_surface": state.get("asked_medium_surface", ""),
        "release_veto": state.get("release_veto"),
    }
    for key in [
        "bound_program",
        "layer_composition_if_any",
        "gate_binding_if_any",
        "primitive_field_if_any",
        "primitive_competition_if_any",
        "carrier_handoff_if_any",
        "secondary_rival_if_any",
        "landed_next_touch_if_any",
        "primitive_takeover_gate_if_any",
        "materialization_evidence",
        "output_status",
    ]:
        value = state.get(key)
        if value not in (None, {}, [], ""):
            summary[key] = value
    return summary


def append_runtime_event(
    path: Path,
    *,
    command_name: str,
    before: dict | None,
    after: dict,
    report: dict | None = None,
    report_excerpt_override: dict | None = None,
    note: str = "",
) -> None:
    if report is None:
        report = build_report(after, path)
    excerpt = report_excerpt_override if isinstance(report_excerpt_override, dict) else _report_excerpt(report)
    bootstrap_context = after.get("bootstrap_context")
    if (
        command_name == "bootstrap-blind"
        and isinstance(bootstrap_context, dict)
        and (
            bootstrap_context.get("requires_qualified_layer_composition_for_skill_claims") is True
            or str(bootstrap_context.get("mode", "")).strip() == "fresh_blind_project_skills_on"
        )
    ):
        cooled_excerpt = dict(excerpt)
        for key in [
            "skill_field",
            "skill_competition",
            "skill_competition_semantics",
            "skill_inhibition",
            "skill_authority_bridge",
            "skill_coaching_surface",
            "probe_discipline",
        ]:
            cooled_excerpt.pop(key, None)
        layer = cooled_excerpt.get("layer_composition")
        if isinstance(layer, dict) and layer.get("event_owned") is not True:
            pending_layer = dict(layer)
            lighting = pending_layer.get("lighting_if_any")
            if isinstance(lighting, dict):
                pending_layer["lighting_if_any"] = {
                    "candidate_skills_if_any": lighting.get("candidate_skills_if_any", []),
                    "qualified_claims_pending": True,
                }
            pending_layer["qualified_claims_pending"] = True
            cooled_excerpt["layer_composition"] = pending_layer
        lighting_surface = cooled_excerpt.get("skill_lighting_surface")
        if isinstance(lighting_surface, dict):
            cooled_excerpt["skill_lighting_surface"] = {
                "candidate_skills_if_any": lighting_surface.get("candidate_skills_if_any", []),
                "qualified_claims_pending": True,
            }
        excerpt = cooled_excerpt
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "command": command_name,
        "event_kind": _event_kind(command_name),
        "before": _state_focus_summary(before or {}),
        "after": _state_focus_summary(after),
        "report_excerpt": excerpt,
    }
    if note:
        event["note"] = note
    log_path = event_log_path(path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=True) + "\n")
    if isinstance(bootstrap_context, dict) and str(bootstrap_context.get("mode", "")).strip() == "fresh_blind_project_skills_on":
        trace_markdown_path(path).write_text(render_runtime_trace_markdown(path), encoding="utf-8")
        skill_trace_markdown_path(path).write_text(render_runtime_skill_trace_markdown(path), encoding="utf-8")
        solve_trace_markdown_path(path).write_text(render_runtime_solve_steps_markdown(path), encoding="utf-8")


def load_runtime_events(path: Path) -> list[dict]:
    log_path = event_log_path(path)
    if not log_path.exists():
        return []
    events: list[dict] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(payload)
    return events


def _event_command_name(event: dict) -> str:
    return str(event.get("command", "")).strip()


def _is_consumption_event(event: dict) -> bool:
    command_name = _event_command_name(event)
    if command_name in {"bind-local", "rebind-local", "spend-local", "execute-local", "land-local"}:
        return True
    return str(event.get("event_kind", "")).strip() == "consumption"


def _is_handoff_event(event: dict) -> bool:
    command_name = _event_command_name(event)
    if command_name == "rebind-local":
        return True
    return str(event.get("event_kind", "")).strip() == "handoff"


def _display_event_kind(event: dict) -> str:
    command_name = _event_command_name(event)
    if command_name:
        return _event_kind(command_name)
    return str(event.get("event_kind", "")).strip() or "unknown"


def _render_transition_lines(event: dict) -> list[str]:
    command = _event_command_name(event)
    before = event.get("before", {})
    after = event.get("after", {})
    if not isinstance(before, dict):
        before = {}
    if not isinstance(after, dict):
        after = {}

    lines: list[str] = []
    before_program = project_bound_program_shape(before.get("bound_program"))
    after_program = project_bound_program_shape(after.get("bound_program"))
    landed_touch = project_bound_program_shape(after.get("landed_next_touch_if_any"))
    handoff = after.get("carrier_handoff_if_any")

    if command == "bind-local":
        consumed = project_bound_program_shape(before.get("landed_next_touch_if_any")) or after_program
        if isinstance(consumed, dict):
            lines.append(
                "- Consumed touch: "
                f"`{str(consumed.get('kind', '')).strip()}` -> "
                f"`{str(consumed.get('target', '')).strip()}`"
            )
        if isinstance(after_program, dict):
            lines.append(
                "- Bound continuation: "
                f"`{str(after_program.get('kind', '')).strip()}` -> "
                f"`{str(after_program.get('target', '')).strip()}`"
            )
        return lines

    if command == "execute-local":
        if isinstance(after_program, dict):
            lines.append(
                "- Executed touch: "
                f"`{str(after_program.get('kind', '')).strip()}` -> "
                f"`{str(after_program.get('target', '')).strip()}`"
            )
        evidence = after.get("materialization_evidence")
        if isinstance(evidence, dict):
            summary = str(evidence.get("summary", "")).strip()
            location = str(evidence.get("location", "")).strip()
            if summary:
                lines.append(f"- Execution summary: `{summary}`")
            if location:
                lines.append(f"- Execution evidence: `{location}`")
        return lines

    if command == "land-local":
        source = str((before_program or {}).get("target", "")).strip()
        landed_object = str(after.get("current_object", "")).strip()
        if source and landed_object:
            lines.append(f"- Landed transition: `{source}` -> `{landed_object}`")
        if isinstance(landed_touch, dict):
            lines.append(
                "- Reopened next touch: "
                f"`{str(landed_touch.get('kind', '')).strip()}` -> "
                f"`{str(landed_touch.get('target', '')).strip()}`"
            )
        return lines

    if command == "rebind-local" and isinstance(handoff, dict):
        target = str(handoff.get("to_object", "")).strip()
        if target:
            lines.append(f"- Carrier handoff: -> `{target}`")
    return lines


def _consumption_alignment_payload(
    event: dict,
    explicit_layer: dict | None,
) -> tuple[dict, dict, dict]:
    command_name = _event_command_name(event)
    before = event.get("before", {})
    after = event.get("after", {})
    if not isinstance(before, dict):
        before = {}
    if not isinstance(after, dict):
        after = {}

    if command_name == "land-local":
        landed = project_bound_program_shape(before.get("bound_program")) or {}
        reopened = project_bound_program_shape(after.get("landed_next_touch_if_any")) or {}
        return landed, landed, reopened

    if command_name == "rebind-local":
        authorized = {}
        if isinstance(explicit_layer, dict):
            authorized = project_bound_program_shape(explicit_layer.get("authorized_bite")) or {}
        return authorized, authorized, {}

    authorized = {}
    if isinstance(explicit_layer, dict):
        authorized = project_bound_program_shape(explicit_layer.get("authorized_bite")) or {}
    realized = project_bound_program_shape(after.get("bound_program")) or {}
    return authorized, realized, {}


def _consumption_skill_signature(
    event: dict,
    explicit_layer: dict | None,
) -> tuple[str, list[str], list[str], list[str]]:
    command_name = _event_command_name(event)
    before = event.get("before", {})
    if not isinstance(before, dict):
        before = {}

    if command_name == "land-local":
        landed = project_bound_program_shape(before.get("bound_program")) or {}
        combo = _normalized_skill_list(landed.get("owner_skill_combo_if_any"))
        if not combo:
            primitive_field = before.get("primitive_field_if_any")
            if isinstance(primitive_field, dict):
                combo = _normalized_skill_list(primitive_field.get("active_primitives"))
        winner = str(landed.get("owner_skill_if_any", "")).strip()
        if not winner:
            primitive_competition = before.get("primitive_competition_if_any")
            if isinstance(primitive_competition, dict):
                winner = str(primitive_competition.get("winner_if_any", "")).strip()
        if not winner and combo:
            winner = combo[0]
        supporting = [skill for skill in combo if skill != winner][:4]
        hypotheses = combo[:]
        if winner and winner not in hypotheses:
            hypotheses.insert(0, winner)
        if combo or winner:
            return winner, combo, supporting, hypotheses[:6]

    combo = _normalized_skill_list(
        explicit_layer.get("active_skill_combo_if_any") if isinstance(explicit_layer, dict) else None
    )
    winner = ""
    supporting: list[str] = []
    if isinstance(explicit_layer, dict):
        winner = str(explicit_layer.get("leading_skill_if_any", "")).strip()
        supporting = _display_supporting_skills(
            explicit_layer,
            combo=combo,
            leading_skill=winner,
        )[:4]
        combo = _runtime_qualified_skill_combo(explicit_layer, leading_skill=winner)
        worked_step = _event_worked_step_text(event)
        if command_name == "execute-local" and worked_step:
            combo, supporting = _worked_step_visible_skill_combo(
                worked_step=worked_step,
                explicit_layer=explicit_layer,
                leading_skill=winner,
            )
    hypotheses = combo[:]
    if winner and winner not in hypotheses:
        hypotheses.insert(0, winner)
    return winner, combo, supporting, hypotheses[:6]


def build_runtime_evidence(path: Path) -> dict:
    events = load_runtime_events(path)
    consumption_events = [event for event in events if _is_consumption_event(event)]
    runtime_step_events = _runtime_step_events(events)
    handoff_events = [event for event in events if _is_handoff_event(event)]
    latest = events[-1] if events else {}
    latest_consumption = consumption_events[-1] if consumption_events else {}
    latest_qualified_consumption = {}
    latest_qualified_authorized = {}
    latest_qualified_realized = {}
    latest_qualified_reopened = {}
    latest_qualified_winning_skill = ""
    latest_qualified_skill_combo: list[str] = []
    latest_qualified_supporting_skills: list[str] = []
    latest_qualified_skill_hypotheses: list[str] = []
    latest_qualified_refusals: list[str] = []
    latest_qualified_layer: dict | None = None
    for event in reversed(consumption_events):
        explicit_layer = _explicit_layer_composition_from_event(event)
        if not isinstance(explicit_layer, dict):
            continue
        refusals = _skill_composition_step_refusals(event)
        if refusals:
            continue
        authorized, realized, reopened = _consumption_alignment_payload(event, explicit_layer)
        if not authorized or not realized or authorized != realized:
            continue
        latest_qualified_consumption = event
        latest_qualified_authorized = authorized
        latest_qualified_realized = realized
        latest_qualified_reopened = reopened
        (
            latest_qualified_winning_skill,
            latest_qualified_skill_combo,
            latest_qualified_supporting_skills,
            latest_qualified_skill_hypotheses,
        ) = _consumption_skill_signature(event, explicit_layer)
        latest_qualified_layer = explicit_layer
        latest_qualified_refusals = []
        excerpt = event.get("report_excerpt", {})
        if isinstance(excerpt, dict) and not latest_qualified_skill_hypotheses:
            probe = excerpt.get("probe_discipline", {})
            if isinstance(probe, dict):
                raw_hypotheses = probe.get("active_skill_hypotheses")
                if isinstance(raw_hypotheses, list):
                    latest_qualified_skill_hypotheses = [
                        str(value).strip() for value in raw_hypotheses if str(value).strip()
                    ][:4]
                elif str(probe.get("active_skill_hypothesis", "")).strip():
                    latest_qualified_skill_hypotheses = [
                        str(probe.get("active_skill_hypothesis", "")).strip()
                    ]
        break
    latest_after = latest_consumption.get("after", {}) if isinstance(latest_consumption, dict) else {}
    latest_excerpt = (
        latest_consumption.get("report_excerpt", {})
        if isinstance(latest_consumption, dict)
        else {}
    )
    latest_authorized = {}
    latest_realized = {}
    latest_reopened = {}
    latest_winning_skill = ""
    latest_skill_combo: list[str] = []
    latest_supporting_skills: list[str] = []
    latest_skill_hypotheses: list[str] = []
    latest_layer_refusals: list[str] = []
    latest_layer_qualified = False
    if isinstance(latest_excerpt, dict):
        probe = latest_excerpt.get("probe_discipline", {})
        if isinstance(probe, dict):
            raw_hypotheses = probe.get("active_skill_hypotheses")
            if isinstance(raw_hypotheses, list):
                latest_skill_hypotheses = [
                    str(value).strip() for value in raw_hypotheses if str(value).strip()
                ][:4]
            elif str(probe.get("active_skill_hypothesis", "")).strip():
                latest_skill_hypotheses = [
                    str(probe.get("active_skill_hypothesis", "")).strip()
                ]
    if isinstance(latest_consumption, dict):
        explicit_layer = _explicit_layer_composition_from_event(latest_consumption)
        if isinstance(explicit_layer, dict):
            latest_authorized, latest_realized, latest_reopened = _consumption_alignment_payload(
                latest_consumption,
                explicit_layer,
            )
            (
                latest_winning_skill,
                latest_skill_combo,
                latest_supporting_skills,
                latest_skill_hypotheses,
            ) = _consumption_skill_signature(latest_consumption, explicit_layer)
        latest_layer_refusals = _skill_composition_step_refusals(latest_consumption)
        latest_layer_qualified = (
            not latest_layer_refusals
            and bool(latest_authorized)
            and bool(latest_realized)
            and latest_authorized == latest_realized
        )
    if not latest_layer_qualified:
        latest_authorized = {}
        latest_realized = {}
        latest_reopened = {}
        latest_winning_skill = ""
        latest_skill_combo = []
        latest_supporting_skills = []
        latest_skill_hypotheses = []
    authority_alignment = bool(latest_authorized) and bool(latest_realized) and latest_authorized == latest_realized
    return {
        "event_log": str(event_log_path(path)),
        "event_count": len(events),
        "consumption_event_count": len(consumption_events),
        "real_runtime_transition_count": len(runtime_step_events),
        "handoff_event_count": len(handoff_events),
        "latest_event_command": str(latest.get("command", "")).strip(),
        "latest_consumption_command": str(latest_consumption.get("command", "")).strip(),
        "latest_real_runtime_transition_command": (
            str(runtime_step_events[-1].get("command", "")).strip()
            if runtime_step_events
            else ""
        ),
        "has_runtime_consumption": bool(consumption_events),
        "has_real_runtime_transition": bool(runtime_step_events),
        "runtime_subject_qualified": isinstance(latest_qualified_layer, dict),
        "latest_consumption_authority_aligned": authority_alignment,
        "latest_consumption_layer_composition_qualified": latest_layer_qualified,
        "latest_consumption_authorized_bite": latest_authorized,
        "latest_consumption_realized_bite": latest_realized,
        "latest_consumption_reopened_bite": latest_reopened,
        "latest_consumption_winning_skill": latest_winning_skill,
        "latest_consumption_skill_combo": latest_skill_combo,
        "latest_consumption_supporting_skills": latest_supporting_skills,
        "latest_consumption_skill_hypotheses": latest_skill_hypotheses,
        "latest_consumption_layer_composition_refusals": latest_layer_refusals[:6],
        "latest_qualified_consumption_layer_composition": (
            latest_qualified_layer if isinstance(latest_qualified_layer, dict) else {}
        ),
        "latest_qualified_consumption_layer_surface": (
            str(latest_qualified_layer.get("surface", "")).strip()
            if isinstance(latest_qualified_layer, dict)
            else ""
        ),
        "latest_qualified_consumption_command": str(latest_qualified_consumption.get("command", "")).strip(),
        "latest_qualified_consumption_authorized_bite": latest_qualified_authorized,
        "latest_qualified_consumption_realized_bite": latest_qualified_realized,
        "latest_qualified_consumption_reopened_bite": latest_qualified_reopened,
        "latest_qualified_consumption_winning_skill": latest_qualified_winning_skill,
        "latest_qualified_consumption_skill_combo": latest_qualified_skill_combo,
        "latest_qualified_consumption_supporting_skills": latest_qualified_supporting_skills,
        "latest_qualified_consumption_skill_hypotheses": latest_qualified_skill_hypotheses,
        "latest_qualified_consumption_layer_composition_qualified": isinstance(
            latest_qualified_layer,
            dict,
        ),
        "latest_qualified_consumption_layer_composition_refusals": latest_qualified_refusals[:6],
    }


def active_contract_requires_runtime_evidence(
    discipline_contract: object,
    runtime_evidence: object,
    *,
    layer_composition: object = None,
    state: object = None,
) -> bool:
    if not isinstance(discipline_contract, dict) or discipline_contract.get("active") is not True:
        return False
    if pending_runtime_execution_contract(state, layer_composition=layer_composition):
        return True
    if not isinstance(runtime_evidence, dict):
        return True

    latest_command = str(runtime_evidence.get("latest_qualified_consumption_command", "")).strip()
    if not latest_command:
        return True

    current_surface = str(
        (
            (layer_composition.get("surface") if isinstance(layer_composition, dict) else None)
            or discipline_contract.get("surface")
            or ""
        )
    ).strip()
    latest_surface = str(
        runtime_evidence.get("latest_qualified_consumption_layer_surface", "")
    ).strip()
    if current_surface and latest_surface and current_surface != latest_surface:
        return True

    latest_layer = runtime_evidence.get("latest_qualified_consumption_layer_composition")
    current_controlled_object = str(
        (
            (layer_composition.get("controlled_object") if isinstance(layer_composition, dict) else None)
            or (layer_composition.get("layer_object") if isinstance(layer_composition, dict) else None)
            or discipline_contract.get("current_object")
            or ""
        )
    ).strip()
    latest_controlled_object = str(
        (
            (latest_layer.get("controlled_object") if isinstance(latest_layer, dict) else None)
            or (latest_layer.get("layer_object") if isinstance(latest_layer, dict) else None)
            or ""
        )
    ).strip()
    if (
        current_controlled_object
        and latest_controlled_object
        and current_controlled_object != latest_controlled_object
    ):
        return True

    current_authorized = project_bound_program_shape(
        (
            (layer_composition.get("authorized_bite") if isinstance(layer_composition, dict) else None)
            or discipline_contract.get("authorized_bite")
        )
    )
    latest_authorized = project_bound_program_shape(
        runtime_evidence.get("latest_qualified_consumption_authorized_bite")
    )
    if isinstance(current_authorized, dict):
        if not isinstance(latest_authorized, dict):
            return True
        if current_authorized != latest_authorized:
            return True

    current_combo = normalize_skill_combo(
        (
            (layer_composition.get("active_skill_combo_if_any") if isinstance(layer_composition, dict) else None)
            or discipline_contract.get("active_skill_combo_if_any")
        )
    )
    latest_combo = normalize_skill_combo(
        runtime_evidence.get("latest_qualified_consumption_skill_combo")
    )
    if current_combo and current_combo != latest_combo:
        return True

    return False


def pending_runtime_execution_contract(
    state: object,
    *,
    layer_composition: object = None,
) -> dict | None:
    if not isinstance(state, dict):
        return None

    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    layer = layer_composition if isinstance(layer_composition, dict) else {}
    layer_authorized = project_bound_program_shape(layer.get("authorized_bite"))
    if (
        layer.get("active") is True
        and layer.get("must_bind_local_bite") is True
        and isinstance(layer_authorized, dict)
        and not isinstance(state.get("bound_program"), dict)
        and not isinstance(state.get("carrier_handoff_if_any"), dict)
        and not isinstance(project_bound_program_shape(state.get("landed_next_touch_if_any")), dict)
        and not isinstance(state.get("primitive_takeover_gate_if_any"), dict)
    ):
        return {
            "reason": "fresh_blind_first_touch_still_pending",
            "required_action": "bind_local",
            "surface": str(layer.get("surface", "")).strip() or "fresh_blind_first_touch",
            "authorized_bite": layer_authorized,
            "allowed_transition_surfaces": ["bind_local"],
        }
    bound_program = project_bound_program_shape(state.get("bound_program"))
    output_status = state.get("output_status")
    already_touched = (
        isinstance(output_status, dict)
        and output_status.get("touched") is True
    )
    if isinstance(bound_program, dict) and program_is_asked_medium_closure(
        bound_program,
        asked_medium=asked_medium,
    ):
        if has_runtime_owned_asked_medium_materialization(state):
            return None
        return {
            "reason": (
                "closure_bound_program_still_needs_materialization"
                if not already_touched
                else "closure_bound_program_touched_but_not_materialized"
            ),
            "required_action": "materialize_asked_medium",
            "surface": str(layer.get("surface", "")).strip() or "bound_program",
            "authorized_bite": bound_program,
            "allowed_transition_surfaces": [
                "materialize_asked_medium",
                "trace_solve_markdown_to_asked_medium",
            ],
        }
    if isinstance(bound_program, dict) and not program_is_asked_medium_closure(
        bound_program,
        asked_medium=asked_medium,
    ):
        if already_touched and has_runtime_owned_asked_medium_materialization(state):
            return None
        landing_ready = same_carrier_landing_is_ready(state, bound_program)
        return {
            "reason": (
                "non_closure_bound_program_touched_and_ready_to_land"
                if already_touched and landing_ready
                else "non_closure_bound_program_touched_but_layer_not_done"
                if already_touched
                else "non_closure_bound_program_still_needs_execution"
            ),
            "required_action": (
                "land_local"
                if already_touched and landing_ready
                else "execute_local"
            ),
            "surface": str(layer.get("surface", "")).strip() or "bound_program",
            "authorized_bite": bound_program,
            "allowed_transition_surfaces": (
                ["land_local"]
                if already_touched and landing_ready
                else ["execute_local"]
            ),
        }

    handoff = state.get("carrier_handoff_if_any")
    if isinstance(handoff, dict):
        handoff_authorized = (
            layer_authorized
            if isinstance(layer_authorized, dict)
            else project_bound_program_shape(state.get("bound_program"))
        )
        return {
            "reason": "carrier_handoff_still_live",
            "required_action": "spend_local",
            "surface": str(layer.get("surface", "")).strip() or "carrier_handoff",
            "authorized_bite": handoff_authorized if isinstance(handoff_authorized, dict) else {},
            "allowed_transition_surfaces": ["spend_local"],
        }

    landed_touch = project_bound_program_shape(state.get("landed_next_touch_if_any"))
    if isinstance(landed_touch, dict):
        return {
            "reason": "rebound_local_touch_still_live",
            "required_action": "bind_local",
            "surface": str(layer.get("surface", "")).strip() or "takeover_recomposition",
            "authorized_bite": landed_touch,
            "allowed_transition_surfaces": ["bind_local"],
        }

    takeover_gate = state.get("primitive_takeover_gate_if_any")
    if isinstance(takeover_gate, dict):
        return {
            "reason": "primitive_takeover_gate_still_live",
            "required_action": "bind_local",
            "surface": str(layer.get("surface", "")).strip() or "takeover_recomposition",
            "authorized_bite": {},
            "allowed_transition_surfaces": ["bind_local"],
        }

    return None


def build_runtime_evidence_refusal_payload(
    path: Path,
    *,
    discipline_contract: object,
    resume_bridge: object,
    warnings: object,
    layer_composition: object = None,
    surface_payload: dict | None = None,
) -> dict:
    payload = {
        "state_file": str(path),
        "consumed": False,
        "inspect_only": True,
        "ok": False,
        "refused": True,
        "delivery_veto": True,
        "reason": (
            str(surface_payload.get("reason", "")).strip()
            if isinstance(surface_payload, dict) and str(surface_payload.get("reason", "")).strip()
            else "active_discipline_contract_requires_runtime_consumption"
        ),
        "discipline_contract": discipline_contract if isinstance(discipline_contract, dict) else {},
        "runtime_evidence": build_runtime_evidence(path),
        "warnings": warnings if isinstance(warnings, list) else [],
        "trace_preview": render_runtime_skill_trace_markdown(path),
    }
    if isinstance(layer_composition, dict):
        payload["layer_composition"] = layer_composition
    if isinstance(surface_payload, dict):
        for key in [
            "surface",
            "authorized_bite_if_any",
            "skill_lighting_surface",
            "pending_transition",
            "allowed_transition_surfaces",
            "transition_pressure",
            "control_context",
            "runtime_transition_watchdog",
        ]:
            if key in surface_payload and key not in payload:
                payload[key] = surface_payload[key]
    return payload


def annotate_runtime_surface_payload(payload: dict, *, exit_code: int) -> dict:
    if not isinstance(payload, dict):
        return {}
    payload.setdefault("ok", exit_code == 0)
    if exit_code == 0:
        payload.setdefault("refused", False)
        payload.setdefault("delivery_veto", False)
    else:
        payload.setdefault("refused", True)
        payload.setdefault("delivery_veto", True)
    return payload


def _runtime_step_events(events: list[dict]) -> list[dict]:
    return [
        event
        for event in events
        if str(event.get("command", "")).strip()
        in {
            "bind-local",
            "rebind-local",
            "spend-local",
            "execute-local",
            "land-local",
            "materialize-asked-medium",
        }
    ]


def _runtime_step_layer_evidence(event: dict) -> tuple[dict | None, list[str]]:
    layer = _explicit_layer_composition_from_event(event)
    refusals = _skill_composition_step_refusals(event)
    return layer, refusals


def _event_skill_activity_snapshot(
    event: dict,
    *,
    layer: dict | None = None,
    owner_combo: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    excerpt = event.get("report_excerpt", {})
    if not isinstance(excerpt, dict):
        excerpt = {}
    skill_field = excerpt.get("skill_field", {})
    if not isinstance(skill_field, dict):
        skill_field = {}
    owner_combo = owner_combo[:] if isinstance(owner_combo, list) else []
    active_field = _merged_skill_lists(skill_field.get("active_skills"), owner_combo, limit=8)
    background = _merged_skill_lists(
        skill_field.get("background_skills_if_any"),
        layer.get("background_skills_if_any") if isinstance(layer, dict) else None,
        limit=8,
    )
    return active_field, background


def _display_supporting_skills(
    layer: dict | None,
    *,
    combo: list[str] | None = None,
    leading_skill: str = "",
) -> list[str]:
    if not isinstance(layer, dict):
        return []
    combo = _normalized_skill_list(combo)
    lighting = layer.get("lighting_if_any")
    role_split = lighting.get("role_split_if_any") if isinstance(lighting, dict) else None
    supporting = _merged_skill_lists(
        layer.get("supporting_skills_if_any"),
        lighting.get("supporting_skills_if_any") if isinstance(lighting, dict) else None,
        role_split.get("supporting_skills_if_any") if isinstance(role_split, dict) else None,
        limit=8,
    )
    if combo:
        combo_set = set(combo)
        supporting = [skill_name for skill_name in supporting if skill_name in combo_set]
    if leading_skill:
        supporting = [skill_name for skill_name in supporting if skill_name != leading_skill]
    if combo and len(combo) > 2 and len(supporting) < min(len(combo) - 1, 2):
        supporting = [skill_name for skill_name in combo if skill_name != leading_skill][: max(4, len(supporting))]
    return supporting


def _qualified_runtime_step_events(events: list[dict]) -> list[dict]:
    qualified: list[dict] = []
    for event in _runtime_step_events(events):
        layer, refusals = _runtime_step_layer_evidence(event)
        if isinstance(layer, dict) and not refusals:
            qualified.append(event)
    return qualified


def _solve_trace_step_qualification_allowed(events: list[dict]) -> bool:
    step_events = _runtime_step_events(events)
    if not step_events:
        return False
    qualified_events = _qualified_runtime_step_events(events)
    return len(step_events) == len(qualified_events)


def _solve_trace_export_allowed(
    path: Path,
    events: list[dict],
    *,
    allow_pending_materialization: bool = False,
) -> bool:
    if not _solve_trace_step_qualification_allowed(events):
        return False
    state = load_state(path)
    pending_contract = pending_runtime_execution_contract(
        state,
        layer_composition=state.get("layer_composition_if_any"),
    )
    if not isinstance(pending_contract, dict):
        return True
    if not allow_pending_materialization:
        return False
    required_action = str(pending_contract.get("required_action", "")).strip()
    return required_action in {
        "materialize_asked_medium",
        "trace_solve_markdown_to_asked_medium",
    }


def _asked_medium_trace_materialization_allowed(state: dict, *, state_path: Path, events: list[dict]) -> bool:
    if not _solve_trace_export_allowed(
        state_path,
        events,
        allow_pending_materialization=True,
    ):
        return False
    probe_state = json.loads(json.dumps(state))
    asked_medium = _extract_markdown_artifact_hint(probe_state.get("asked_medium_surface", ""))
    if not asked_medium:
        return False
    program = project_bound_program_shape(probe_state.get("bound_program"))
    if not (
        isinstance(program, dict)
        and program_is_asked_medium_closure(program, asked_medium=asked_medium)
    ):
        promoted = promote_report_derived_exact_closure(probe_state, state_path=state_path)
        if promoted:
            program = project_bound_program_shape(probe_state.get("bound_program"))
    return isinstance(program, dict) and program_is_asked_medium_closure(program, asked_medium=asked_medium)


def _skill_trace_export_allowed(events: list[dict]) -> bool:
    return _all_runtime_step_events_qualified(events)


def _all_runtime_step_events_qualified(events: list[dict]) -> bool:
    step_events = _runtime_step_events(events)
    if not step_events:
        return False
    return len(step_events) == len(_qualified_runtime_step_events(events))


def _render_runtime_markdown_refusal(
    path: Path,
    *,
    title: str,
    subject: str,
    events: list[dict],
) -> str:
    evidence = build_runtime_evidence(path)
    lines = [title, ""]
    lines.append(
        f"Runtime refusal: existing runtime skill/layer evidence does not justify exporting {subject}."
    )

    if evidence.get("has_runtime_consumption") is not True:
        lines.append("- Refusal: no runtime consumption event was captured.")
    if evidence.get("latest_consumption_authority_aligned") is not True:
        lines.append(
            "- Refusal: the latest authorized bite and realized bite never aligned."
        )
    if evidence.get("latest_consumption_layer_composition_qualified") is not True:
        layer_refusals = evidence.get("latest_consumption_layer_composition_refusals")
        if isinstance(layer_refusals, list) and layer_refusals:
            for refusal in layer_refusals[:4]:
                text = str(refusal).strip()
                if text:
                    lines.append(f"- Refusal: {text}.")
        else:
            lines.append(
                "- Refusal: no explicit skill/layer composition qualified as a genuine runtime step."
            )

    qualified_count = len(_qualified_runtime_step_events(events))
    if qualified_count:
        lines.append(
            f"- Qualified runtime step count: `{qualified_count}`."
        )
    else:
        lines.append(
            "- Qualified runtime step count: `0`."
        )
    lines.append(
        "The trace can still be inspected as runtime evidence, but it must not be rewritten as ordinary solve prose or generic skill steps."
    )
    lines.append("")
    return "\n".join(lines)


def render_runtime_trace_markdown(path: Path) -> str:
    events = load_runtime_events(path)
    if not events:
        return (
            "# Runtime Trace\n\n"
            "No runtime events were captured for this state file.\n"
        )

    lines = ["# Runtime Trace", ""]
    for index, event in enumerate(events, start=1):
        command = str(event.get("command", "")).strip() or "unknown"
        event_kind = _display_event_kind(event)
        lines.append(f"## Event {index}: `{command}`")
        lines.append(f"- Time: `{str(event.get('ts', '')).strip()}`")
        lines.append(f"- Kind: `{event_kind}`")
        lines.extend(_render_transition_lines(event))
        note = str(event.get("note", "")).strip()
        if note:
            lines.append(f"- Note: {note}")
        after = event.get("after", {})
        if isinstance(after, dict):
            current_object = str(after.get("current_object", "")).strip()
            current_debt = str(after.get("current_debt", "")).strip()
            next_bite = str(after.get("next_bite", "")).strip()
            if current_object:
                lines.append(f"- Object: `{current_object}`")
            if current_debt:
                lines.append(f"- Debt: {current_debt}")
            if next_bite:
                lines.append(f"- Next bite: {next_bite}")
        excerpt = event.get("report_excerpt", {})
        if isinstance(excerpt, dict):
            gap_object = excerpt.get("gap_object")
            if isinstance(gap_object, dict):
                gap_target = str(gap_object.get("object", "")).strip()
                if gap_target:
                    lines.append(f"- Gap object: `{gap_target}`")
            resume_bridge = excerpt.get("resume_bridge")
            if isinstance(resume_bridge, dict):
                resume_mode = str(resume_bridge.get("mode", "")).strip()
                if resume_mode:
                    lines.append(f"- Resume mode: `{resume_mode}`")
            explicit_layer = _explicit_layer_composition_from_event(event)
            explicit_refusals = _skill_composition_step_refusals(event)
            if isinstance(explicit_layer, dict) and not explicit_refusals:
                winning_skill = str(explicit_layer.get("leading_skill_if_any", "")).strip()
                if winning_skill:
                    lines.append(f"- Winning skill: `{winning_skill}`")
                combo = explicit_layer.get("active_skill_combo_if_any")
                if isinstance(combo, list) and combo:
                    lines.append(
                        "- Owner skill combo: "
                        + ", ".join(f"`{str(value).strip()}`" for value in combo if str(value).strip())
                    )
                active_field, background_skills = _event_skill_activity_snapshot(
                    event,
                    layer=explicit_layer,
                    owner_combo=_normalized_skill_list(combo),
                )
                if active_field:
                    lines.append(
                        "- Active skill field: "
                        + ", ".join(f"`{value}`" for value in active_field)
                    )
                if background_skills:
                    lines.append(
                        "- Background/supporting skills: "
                        + ", ".join(f"`{value}`" for value in background_skills)
                    )
            skill_inhibition = excerpt.get("skill_inhibition")
            if isinstance(skill_inhibition, dict):
                promoted = str(skill_inhibition.get("promoted_skill_if_any", "")).strip()
                if promoted:
                    lines.append(f"- Promoted skill: `{promoted}`")
                demoted = skill_inhibition.get("demoted_skills")
                if isinstance(demoted, list) and demoted:
                    lines.append(
                        "- Demoted skills: "
                        + ", ".join(f"`{str(value).strip()}`" for value in demoted if str(value).strip())
                    )
            skill_field = excerpt.get("skill_field")
            if isinstance(skill_field, dict):
                if skill_field.get("composition_ready") is True:
                    axes = skill_field.get("composition_axes")
                    if isinstance(axes, list) and axes:
                        lines.append(
                            "- Skill composition axes: "
                            + ", ".join(f"`{str(value).strip()}`" for value in axes if str(value).strip())
                        )
            skill_competition = excerpt.get("skill_competition")
            if isinstance(skill_competition, dict):
                winner = str(skill_competition.get("winning_skill_if_any", "")).strip()
                if winner:
                    lines.append(f"- Skill competition winner: `{winner}`")
            probe = excerpt.get("probe_discipline")
            if isinstance(probe, dict):
                active_hypothesis = str(probe.get("active_skill_hypothesis", "")).strip()
                if active_hypothesis:
                    lines.append(f"- Active hypothesis: `{active_hypothesis}`")
            primitive_field = excerpt.get("primitive_field")
            if isinstance(primitive_field, dict):
                active_primitives = primitive_field.get("active_primitives")
                if isinstance(active_primitives, list) and active_primitives:
                    lines.append(
                        "- Active primitives: "
                        + ", ".join(f"`{str(value).strip()}`" for value in active_primitives if str(value).strip())
                    )
            takeover = excerpt.get("primitive_takeover_gate")
            if isinstance(takeover, dict):
                trigger = str(takeover.get("trigger", "")).strip()
                if trigger:
                    lines.append(f"- Primitive takeover gate: `{trigger}`")
                active = takeover.get("active_primitives")
                if isinstance(active, list) and active:
                    lines.append(
                        "- Gate live primitives: "
                        + ", ".join(f"`{str(value).strip()}`" for value in active if str(value).strip())
                    )
            handoff = after.get("carrier_handoff_if_any")
            if isinstance(handoff, dict):
                lines.append(f"- Handoff target: `{str(handoff.get('to_object', '')).strip()}`")
            landed_touch = project_bound_program_shape(after.get("landed_next_touch_if_any"))
            if isinstance(landed_touch, dict):
                lines.append(
                    "- Landed next touch: "
                    f"`{str(landed_touch.get('kind', '')).strip()}` -> "
                    f"`{str(landed_touch.get('target', '')).strip()}`"
                )
            program = after.get("bound_program")
            if isinstance(program, dict):
                lines.append(
                    "- Bound program: "
                    f"`{str(program.get('kind', '')).strip()}` -> "
                    f"`{str(program.get('target', '')).strip()}`"
                )
        lines.append("")
    return "\n".join(lines)


def render_runtime_skill_trace_markdown(path: Path) -> str:
    events = load_runtime_events(path)
    if not events:
        return (
            "# Runtime Skill Trace\n\n"
            "No runtime events were captured for this state file.\n"
        )

    step_events = _runtime_step_events(events)
    if not step_events or not _qualified_runtime_step_events(events):
        return _render_runtime_markdown_refusal(
            path,
            title="# Runtime Skill Trace",
            subject="skill-markdown",
            events=events,
        )

    lines = ["# Runtime Skill Trace", ""]
    step_index = 1
    for event in step_events:
        command = str(event.get("command", "")).strip() or "unknown"
        layer, layer_refusals = _runtime_step_layer_evidence(event)
        if not isinstance(layer, dict) or layer_refusals:
            lines.append(
                f"## Step {step_index}: `{command}`"
            )
            lines.append(
                "- Runtime refusal: this event did not qualify as a genuine skill-owned runtime step."
            )
            for refusal in layer_refusals or ["explicit layer composition missing"]:
                lines.append(f"- Refusal: {refusal}.")
            lines.append("")
            step_index += 1
            continue

        event_kind = _display_event_kind(event)
        lines.append(f"## Step {step_index}: `{command}`")
        lines.append(f"- Kind: `{event_kind}`")
        lines.extend(_render_transition_lines(event))

        excerpt = event.get("report_excerpt", {})
        after = event.get("after", {})
        winning_skill = str(layer.get("leading_skill_if_any", "")).strip()
        touch = project_bound_program_shape(layer.get("authorized_bite"))
        touch_owner = (
            str(touch.get("owner_skill_if_any", "")).strip()
            if isinstance(touch, dict)
            else ""
        )
        touch_combo = (
            _normalized_skill_list(touch.get("owner_skill_combo_if_any"))
            if isinstance(touch, dict)
            else []
        )
        touch_outline = (
            str(touch.get("step_outline_if_any", "")).strip()
            if isinstance(touch, dict)
            else ""
        )
        touch_transform = (
            str(touch.get("object_transform_if_any", "")).strip()
            if isinstance(touch, dict)
            else ""
        )
        authoritative_owner = winning_skill or touch_owner
        authoritative_combo = _normalized_skill_list(layer.get("active_skill_combo_if_any")) or touch_combo
        active_field, background_skills = _event_skill_activity_snapshot(
            event,
            layer=layer,
            owner_combo=authoritative_combo,
        )
        if isinstance(excerpt, dict):
            gap_object = excerpt.get("gap_object", {})
            if isinstance(gap_object, dict):
                gap_target = str(gap_object.get("object", "")).strip()
                if gap_target:
                    lines.append(f"- Gap object: `{gap_target}`")
            resume_bridge = excerpt.get("resume_bridge", {})
            if isinstance(resume_bridge, dict):
                resume_mode = str(resume_bridge.get("mode", "")).strip()
                if resume_mode:
                    lines.append(f"- Resume mode: `{resume_mode}`")
            skill_field = excerpt.get("skill_field", {})
            if isinstance(skill_field, dict):
                if active_field:
                    lines.append(
                        "- Active skill field: "
                        + ", ".join(f"`{value}`" for value in active_field)
                    )
            elif active_field:
                lines.append(
                    "- Active skill field: "
                    + ", ".join(f"`{value}`" for value in active_field)
                )
            combo = authoritative_combo
            if isinstance(combo, list) and combo:
                lines.append(
                    "- Live combo on this layer: "
                    + ", ".join(f"`{str(value).strip()}`" for value in combo if str(value).strip())
                )
            if background_skills:
                lines.append(
                    "- Background pressure kept warm: "
                    + ", ".join(f"`{value}`" for value in background_skills)
                )
            supporting = _display_supporting_skills(
                layer,
                combo=combo,
                leading_skill=authoritative_owner,
            )
            if supporting:
                lines.append(
                    "- Supporting skills: "
                    + ", ".join(f"`{value}`" for value in supporting)
                )
            if isinstance(touch, dict):
                lines.append(
                    "- Owned touch: "
                    f"`{str(touch.get('kind', '')).strip()}` -> "
                    f"`{str(touch.get('target', '')).strip()}`"
                )
                if touch_transform:
                    lines.append(f"- Object rewrite: {touch_transform}")
                if touch_outline:
                    lines.append(f"- Step outline: {touch_outline}")
            false_skill = str(layer.get("false_first_skill_if_any", "")).strip()
            false_label = str(layer.get("false_first_label_if_any", "")).strip()
            false_reason = str(layer.get("false_skill_reason", "")).strip()
            if false_skill or false_label or false_reason:
                lines.append(
                    "- False first-skill pressure cooled: "
                    + (
                        f"`{false_skill}`"
                        if false_skill
                        else f"`{false_label}`"
                        if false_label
                        else "one fake first move"
                    )
                    + (f" ({false_reason})" if false_reason else "")
                )
            verify_touch = layer.get("verify_touch_if_any")
            if isinstance(verify_touch, dict):
                verify_target = str(verify_touch.get("target", "")).strip()
                verify_kind = str(verify_touch.get("kind", "")).strip()
                if verify_target and verify_kind:
                    lines.append(
                        f"- Immediate verification touch: `{verify_kind}` -> `{verify_target}`"
                    )
            accountability = str(layer.get("accountability_nudge_if_any", "")).strip()
            if accountability:
                lines.append(f"- Accountability pressure: {accountability}")
            projected_gain_reason = str(layer.get("winning_projected_gain_reason", "")).strip()
            if projected_gain_reason:
                lines.append(f"- Why this skill won now: {projected_gain_reason}")
        if isinstance(after, dict):
            materialization = after.get("materialization_evidence")
            if command == "materialize-asked-medium" and isinstance(materialization, dict):
                summary = str(materialization.get("summary", "")).strip()
                location = str(materialization.get("location", "")).strip()
                if summary:
                    lines.append(f"- Materialized closure: {summary}")
                if location and location != "inline":
                    lines.append(f"- Materialized at: `{location}`")
            program = project_bound_program_shape(after.get("bound_program"))
            if isinstance(program, dict):
                lines.append(
                    "- Bound after event: "
                    f"`{str(program.get('kind', '')).strip()}` -> "
                    f"`{str(program.get('target', '')).strip()}`"
                )
            handoff = after.get("carrier_handoff_if_any")
            if isinstance(handoff, dict):
                handoff_target = str(handoff.get("to_object", "")).strip()
                if handoff_target:
                    lines.append(f"- Handoff after event: `{handoff_target}`")
        note = str(event.get("note", "")).strip()
        if note:
            lines.append(f"- Note: {note}")
        lines.append("")
        step_index += 1
    return "\n".join(lines)


def render_runtime_solve_steps_markdown(path: Path) -> str:
    events = load_runtime_events(path)
    if not events:
        return (
            "# Runtime Solve Steps\n\n"
            "No runtime events were captured for this state file.\n"
        )

    if not _solve_trace_step_qualification_allowed(events):
        return _render_runtime_markdown_refusal(
            path,
            title="# Runtime Solve Steps",
            subject="solve-markdown",
            events=events,
        )

    lines = ["# Runtime Solve Steps", ""]
    step_index = 1
    step_events = _runtime_step_events(events)
    for event in step_events:
        command = str(event.get("command", "")).strip()
        before = event.get("before", {})
        after = event.get("after", {})
        excerpt = event.get("report_excerpt", {})
        if not isinstance(before, dict):
            before = {}
        if not isinstance(after, dict):
            after = {}
        if not isinstance(excerpt, dict):
            excerpt = {}

        layer, layer_refusals = _runtime_step_layer_evidence(event)
        if layer is None or layer_refusals:
            lines.append(
                f"{step_index}. Runtime refusal: `{command or 'unknown'}` did not qualify as one genuine skill-composition step."
            )
            for refusal in layer_refusals or ["explicit layer composition missing"]:
                lines.append(f"   Refusal: {refusal}.")
            lines.append("   The runtime still described control flow or relabeled an ordinary solve, not a problem-born skill-composition step.")
            lines.append("")
            step_index += 1
            continue

        skill_combo = [str(value).strip() for value in layer.get("active_skill_combo_if_any", []) if str(value).strip()]
        active_field, background_skills = _event_skill_activity_snapshot(
            event,
            layer=layer,
            owner_combo=skill_combo,
        )
        active_primitives = [str(value).strip() for value in layer.get("active_primitives", []) if str(value).strip()]
        composition_axes = [str(value).strip() for value in layer.get("composition_axes", []) if str(value).strip()]
        authorized_bite = project_bound_program_shape(layer.get("authorized_bite"))
        layer_object = str(layer.get("layer_object", "")).strip()
        controlled_object = str(layer.get("controlled_object", "")).strip()
        current_seam = str(layer.get("current_seam", "")).strip()
        current_debt = str(layer.get("current_debt", "")).strip()
        reason = str(layer.get("reason", "")).strip()
        leading_skill = str(layer.get("leading_skill_if_any", "")).strip()
        next_choice = str(layer.get("next_local_choice", "")).strip()
        gap_object = str(layer.get("gap_object", "")).strip()
        surface = str(layer.get("surface", "")).strip()
        bite_kind = str(authorized_bite.get("kind", "")).strip() if isinstance(authorized_bite, dict) else ""
        bite_target = str(authorized_bite.get("target", "")).strip() if isinstance(authorized_bite, dict) else ""
        bite_operation = (
            str(authorized_bite.get("operation", "")).strip()
            if isinstance(authorized_bite, dict)
            else ""
        )
        bite_outline = (
            str(authorized_bite.get("step_outline_if_any", "")).strip()
            if isinstance(authorized_bite, dict)
            else ""
        )
        bite_transform = (
            str(authorized_bite.get("object_transform_if_any", "")).strip()
            if isinstance(authorized_bite, dict)
            else ""
        )
        bite_object = controlled_object or bite_target or layer_object
        staged_touch = project_bound_program_shape(before.get("landed_next_touch_if_any"))
        prior_bound = project_bound_program_shape(before.get("bound_program"))
        prior_handoff = before.get("carrier_handoff_if_any")

        if command in {"bind-local", "spend-local"}:
            lines.append(
                f"{step_index}. 当前层把真实触点落在 `{bite_object or layer_object or 'current_object'}` 上。"
            )
            if current_debt:
                lines.append(f"   当前未清 debt: {current_debt}.")
            if layer_object and layer_object != bite_object:
                lines.append(f"   这一层真正承压的对象: `{layer_object}`.")
            if current_seam:
                lines.append(f"   当前 seam: `{current_seam}`.")
            if reason:
                lines.append(f"   这一层之所以接管: {reason}.")
            if skill_combo:
                lines.append(
                    "   这一层真的亮着的组合: "
                    + ", ".join(f"`{value}`" for value in skill_combo)
                    + "."
                )
            supporting = _display_supporting_skills(
                layer,
                combo=skill_combo,
                leading_skill=leading_skill,
            )
            if supporting:
                lines.append(
                    "   辅助但没抢第一接管的技能: "
                    + ", ".join(f"`{value}`" for value in supporting)
                    + "."
                )
            false_skill = str(layer.get("false_first_skill_if_any", "")).strip()
            false_label = str(layer.get("false_first_label_if_any", "")).strip()
            false_reason = str(layer.get("false_skill_reason", "")).strip()
            if false_skill or false_label or false_reason:
                lines.append(
                    "   被压下去的假第一技能: "
                    + (
                        f"`{false_skill}`"
                        if false_skill
                        else f"`{false_label}`"
                        if false_label
                        else "one fake first move"
                    )
                    + (f"，原因是 {false_reason}" if false_reason else "")
                    + "."
                )
            verify_touch = layer.get("verify_touch_if_any")
            if isinstance(verify_touch, dict):
                verify_target = str(verify_touch.get("target", "")).strip()
                verify_kind = str(verify_touch.get("kind", "")).strip()
                if verify_target and verify_kind:
                    lines.append(
                        f"   当层立即验证触点: `{verify_kind}` -> `{verify_target}`."
                    )
            if active_field and active_field != skill_combo:
                lines.append(
                    "   当时同时亮着但没都抢第一接管的 field: "
                    + ", ".join(f"`{value}`" for value in active_field)
                    + "."
                )
            if background_skills:
                lines.append(
                    "   背景里仍在施压的技能: "
                    + ", ".join(f"`{value}`" for value in background_skills)
                    + "."
                )
            if active_primitives:
                lines.append(
                    "   仍在底层托住这一下的 primitive: "
                    + ", ".join(f"`{value}`" for value in active_primitives)
                    + "."
                )
            lines.append("")
            step_index += 1
            continue

        if command == "execute-local":
            if skill_combo:
                lines.append(
                    f"{step_index}. 当前层先由 "
                    + " + ".join(f"`{value}`" for value in skill_combo)
                    + f" 接管，再真正执行 `{bite_object or layer_object or 'current_object'}`。"
                )
            else:
                lines.append(
                    f"{step_index}. 当前层没有停在“下一刀怎么做”的描述上，而是开始实际执行 `{bite_object or layer_object or 'current_object'}` 这一刀。"
                )
            if current_debt:
                lines.append(f"   当前未清 debt: {current_debt}.")
            if skill_combo:
                lines.append(
                    "   执行这一步时亮着的组合: "
                    + ", ".join(f"`{value}`" for value in skill_combo)
                    + "."
                )
            if bite_operation:
                lines.append(f"   原先绑定的 bite: {bite_operation}.")
            evidence = after.get("materialization_evidence")
            if isinstance(evidence, dict):
                worked_step = str(evidence.get("worked_step", "")).strip()
                summary = str(evidence.get("summary", "")).strip()
                location = str(evidence.get("location", "")).strip()
                if worked_step:
                    lines.append("   实际做题文本:")
                    for worked_line in worked_step.splitlines():
                        worked_line = worked_line.rstrip()
                        if worked_line:
                            lines.append(f"   {worked_line}")
                if summary:
                    worked_summary = worked_step.replace("\n", " ").strip() if worked_step else ""
                    if summary != worked_summary:
                        lines.append(f"   实际执行结果: {summary}.")
                if location and location != "inline":
                    lines.append(f"   执行证据写到: `{location}`.")
            lines.append("")
            step_index += 1
            continue

        if command == "materialize-asked-medium":
            combo_text = (
                " + ".join(f"`{value}`" for value in skill_combo)
                if skill_combo
                else f"`{leading_skill or '精确封口'}`"
            )
            lines.append(
                f"{step_index}. 最后一层没有退回普通收口，而是由 {combo_text} 把结果真的封进 asked medium。"
            )
            if skill_combo:
                lines.append(
                    "   最终封口时亮着的组合: "
                    + ", ".join(f"`{value}`" for value in skill_combo)
                    + "."
                )
            if bite_transform:
                lines.append(f"   最终这一刀在做的对象改写: {bite_transform}.")
            if bite_outline:
                lines.append(f"   最终层步骤: {bite_outline}.")
            elif bite_operation:
                lines.append(f"   最终绑定的 bite: {bite_operation}.")
            evidence = after.get("materialization_evidence")
            if isinstance(evidence, dict):
                summary = str(evidence.get("summary", "")).strip()
                location = str(evidence.get("location", "")).strip()
                if summary:
                    lines.append(f"   物化结果: {summary}.")
                if location and location != "inline":
                    lines.append(f"   物化位置: `{location}`.")
            lines.append("")
            step_index += 1
            continue

        if command == "land-local":
            inherited_touch = project_bound_program_shape(after.get("landed_next_touch_if_any"))
            source_object = str((project_bound_program_shape(before.get("bound_program")) or {}).get("target", "")).strip()
            if source_object and layer_object:
                lines.append(
                    f"{step_index}. `{source_object}` 这一下落地后，问题收缩成 `{layer_object}`。"
                )
            elif layer_object:
                lines.append(
                    f"{step_index}. 上一触点落地后，问题收缩成 `{layer_object}`。"
                )
            else:
                lines.append(
                    f"{step_index}. 上一触点落地后，当前对象被压成更小的局部层。"
                )
            if isinstance(prior_bound, dict):
                lines.append(
                    "   落地前挂着的触点: "
                    f"`{str(prior_bound.get('kind', '')).strip()}` -> "
                    f"`{str(prior_bound.get('target', '')).strip()}`."
                )
            if current_debt:
                lines.append(f"   新层留下的 debt: {current_debt}.")
            if gap_object:
                lines.append(f"   新层直接露出的缺口对象: `{gap_object}`.")
            if current_seam:
                lines.append(f"   新层 seam: `{current_seam}`.")
            if reason:
                lines.append(f"   为什么会收缩到这里: {reason}.")
            lines.append(
                "   新层真的亮着的组合: "
                + ", ".join(f"`{value}`" for value in skill_combo)
                + "."
            )
            supporting = _display_supporting_skills(
                layer,
                combo=skill_combo,
                leading_skill=leading_skill,
            )
            if supporting:
                lines.append(
                    "   新层辅助但没抢第一接管的技能: "
                    + ", ".join(f"`{value}`" for value in supporting)
                    + "."
                )
            false_skill = str(layer.get("false_first_skill_if_any", "")).strip()
            false_label = str(layer.get("false_first_label_if_any", "")).strip()
            false_reason = str(layer.get("false_skill_reason", "")).strip()
            if false_skill or false_label or false_reason:
                lines.append(
                    "   新层压下去的假第一技能: "
                    + (
                        f"`{false_skill}`"
                        if false_skill
                        else f"`{false_label}`"
                        if false_label
                        else "one fake first move"
                    )
                    + (f"，原因是 {false_reason}" if false_reason else "")
                    + "."
                )
            if active_field and active_field != skill_combo:
                lines.append(
                    "   这一落地事件里更宽的 active field: "
                    + ", ".join(f"`{value}`" for value in active_field)
                    + "."
                )
            if background_skills:
                lines.append(
                    "   落地后仍在背景施压的技能: "
                    + ", ".join(f"`{value}`" for value in background_skills)
                    + "."
                )
            if layer_object:
                lines.append(f"   新层对象: `{layer_object}`.")
            if controlled_object and controlled_object != layer_object:
                lines.append(f"   新层当前压住的对象: `{controlled_object}`.")
            if surface:
                lines.append(f"   事件表面: `{surface}`.")
            if composition_axes:
                lines.append(
                    "   新层同时醒着的轴: "
                    + ", ".join(f"`{value}`" for value in composition_axes)
                    + "."
                )
            if active_primitives:
                lines.append(
                    "   新层 primitive 支撑: "
                    + ", ".join(f"`{value}`" for value in active_primitives)
                    + "."
                )
            if isinstance(inherited_touch, dict):
                lines.append(
                    "   新层保留下来的下一触点: "
                    f"`{str(inherited_touch.get('kind', '')).strip()}` -> "
                    f"`{str(inherited_touch.get('target', '')).strip()}`."
                )
            lines.append("")
            step_index += 1
            continue

        if command == "rebind-local":
            target = str(after.get("carrier_handoff_if_any", {}).get("to_object", "")).strip()
            if target:
                lines.append(
                    f"{step_index}. 当前对象压不住剩余 debt，于是问题收缩到更薄的 `{target}`。"
                )
            else:
                lines.append(
                    f"{step_index}. 当前对象压不住剩余 debt，于是问题收缩到更薄的一层。"
                )
            if isinstance(prior_bound, dict):
                lines.append(
                    "   改层前还挂着的当前触点: "
                    f"`{str(prior_bound.get('kind', '')).strip()}` -> "
                    f"`{str(prior_bound.get('target', '')).strip()}`."
                )
            if current_debt:
                lines.append(f"   逼出收缩的 debt: {current_debt}.")
            if gap_object:
                lines.append(f"   收缩后盯住的缺口对象: `{gap_object}`.")
            if reason:
                lines.append(f"   为什么必须改在这层看: {reason}.")
            lines.append(
                "   事件自带的组合证据: "
                + ", ".join(f"`{value}`" for value in skill_combo)
                + "."
            )
            if leading_skill:
                lines.append(f"   前台主导技能: `{leading_skill}`.")
            if active_field and active_field != skill_combo:
                lines.append(
                    "   这一步当时更宽的 active field: "
                    + ", ".join(f"`{value}`" for value in active_field)
                    + "."
                )
            if background_skills:
                lines.append(
                    "   背景里仍在施压的技能: "
                    + ", ".join(f"`{value}`" for value in background_skills)
                    + "."
                )
            lines.append("")
            step_index += 1
            continue

        if bite_object and bite_operation:
            lines.append(f"{step_index}. 在 `{bite_object}` 上执行 `{bite_operation}`。")
        elif controlled_object:
            lines.append(f"{step_index}. 当前局部对象落在 `{controlled_object}`。")
        else:
            lines.append(f"{step_index}. 当前层出现了一次局部对象更新。")
        lines.append(
            "   事件自带的组合证据: "
            + ", ".join(f"`{value}`" for value in skill_combo)
            + "."
        )
        if reason:
            lines.append(f"   更新理由: {reason}.")
        lines.append("")
        step_index += 1

    return "\n".join(lines)


def load_state(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing state file: {path}")
    return load_json(path)


def dump(payload: dict) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")


def mutate_state(path: Path, mutator, *, command_name: str = "") -> dict:
    with StateLock(path):
        state = load_state(path)
        before = _deep_copy(state)
        event_override = mutator(state)
        write_json(path, state)
        if command_name and before != state:
            report_excerpt_override = None
            if isinstance(event_override, dict):
                report_excerpt_override = event_override.get("report_excerpt_override")
            if (
                report_excerpt_override is None
                and command_name in {"bind-local", "spend-local", "execute-local", "land-local", "program:set"}
                and isinstance(state.get("layer_composition_if_any"), dict)
            ):
                report = build_report(state, path)
                report_excerpt_override = build_event_report_excerpt_override(
                    report,
                    state.get("layer_composition_if_any"),
                )
            if (
                report_excerpt_override is None
                and command_name == "materialize-asked-medium"
                and isinstance(before.get("layer_composition_if_any"), dict)
            ):
                report = build_report(before, path)
                report_excerpt_override = build_event_report_excerpt_override(
                    report,
                    before.get("layer_composition_if_any"),
                )
            append_runtime_event(
                path,
                command_name=command_name,
                before=before,
                after=state,
                report_excerpt_override=report_excerpt_override,
            )
        return state


def apply_core_updates(state: dict, args: argparse.Namespace) -> None:
    for key in [
        "current_object",
        "current_seam",
        "current_debt",
        "next_bite",
        "asked_medium_surface",
        "revocation_handle",
        "uncertainty_mode",
        "primary_slot",
    ]:
        value = getattr(args, key, None)
        if value is not None:
            state[key] = value


def set_bound_program(state: dict, args: argparse.Namespace) -> None:
    state["bound_program"] = {
        "kind": args.kind,
        "target": args.target,
        "operation": args.operation,
    }
    if args.success_signal is not None:
        state["bound_program"]["success_signal"] = args.success_signal


def set_gate_binding(state: dict, args: argparse.Namespace) -> None:
    state["gate_binding_if_any"] = {
        "source_focus": args.source_focus,
        "source_target": args.source_target,
        "demoted_continuation": args.demoted_continuation,
        "authority_until": args.authority_until,
    }


def set_materialization_evidence(state: dict, args: argparse.Namespace) -> None:
    state["materialization_evidence"] = {
        "kind": args.evidence_kind,
        "location": args.evidence_location,
        "summary": args.evidence_summary,
    }


def resolve_state_relative_output_path(state_path: Path, raw_path: str) -> Path:
    output_path = Path(raw_path)
    cwd = Path.cwd()
    state_dir = state_path.parent
    if not state_dir.is_absolute():
        state_dir = (cwd / state_dir).resolve()
    else:
        state_dir = state_dir.resolve()

    if output_path.is_absolute():
        resolved = output_path.resolve()
    else:
        # If the caller already passed a cwd-relative path that points into the
        # state directory tree, keep that path instead of prefixing the state
        # directory a second time.
        try:
            state_dir_from_cwd = state_dir.relative_to(cwd.resolve())
        except ValueError:
            state_dir_from_cwd = None

        if isinstance(state_dir_from_cwd, Path):
            raw_parts = output_path.parts
            state_parts = state_dir_from_cwd.parts
            if (
                state_parts
                and len(raw_parts) >= len(state_parts)
                and raw_parts[: len(state_parts)] == state_parts
            ):
                resolved = (cwd / output_path).resolve()
            else:
                resolved = (state_dir / output_path).resolve()
        else:
            resolved = (state_dir / output_path).resolve()

    try:
        resolved.relative_to(state_dir)
    except ValueError as exc:
        raise SystemExit(
            "output path refused: paths must stay inside the state directory"
        ) from exc

    return resolved


def _normalized_existing_path_text(raw_path: str) -> str:
    text = str(raw_path or "").strip()
    if not text:
        return ""
    try:
        return str(Path(text).resolve())
    except OSError:
        return text


def _contains_placeholder_text(text: str) -> bool:
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in [
            "todo",
            "placeholder",
            "待补",
            "待完成",
        ]
    )


def _contains_unsupported_text(text: str) -> bool:
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in [
            "unsupported",
            "works only for small cases",
            "仅小样例",
            "只对小范围成立",
        ]
    )


def program_is_asked_medium_closure(program: object, *, asked_medium: str) -> bool:
    payload = project_bound_program_shape(program)
    if not isinstance(payload, dict):
        return False
    kind = str(payload.get("kind", "")).strip()
    target = _extract_markdown_artifact_hint(payload.get("target", ""))
    operation = str(payload.get("operation", "")).strip()
    success_signal = str(payload.get("success_signal", "")).strip()
    normalized_asked_medium = _extract_markdown_artifact_hint(asked_medium)
    if not normalized_asked_medium or target != normalized_asked_medium:
        return False
    return (
        kind == "读出"
        or success_signal == "asked_medium_is_exact_and_executable"
        or operation == "materialize_exact_asked_medium_读出"
    )


def asked_medium_output_path(*, state: dict, state_path: Path) -> Path | None:
    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    if not asked_medium:
        return None
    return resolve_state_relative_output_path(state_path, asked_medium)


def require_fresh_blind_asked_medium_surface(state: object, *, context: str) -> None:
    if not _fresh_blind_mode_active_from_state(state):
        return
    asked_medium = ""
    if isinstance(state, dict):
        asked_medium = str(state.get("asked_medium_surface", "")).strip()
    refusal = _fresh_blind_asked_medium_surface_refusal(asked_medium)
    if refusal:
        raise SystemExit(f"{context}: {refusal}")


def canonical_skill_serialized_asked_medium_text(*, state_path: Path) -> str:
    events = load_runtime_events(state_path)
    if not _solve_trace_export_allowed(
        state_path,
        events,
        allow_pending_materialization=True,
    ):
        return ""
    text = render_runtime_solve_steps_markdown(state_path).strip()
    return text + "\n" if text else ""


def canonical_asked_medium_materialization_text(
    state: dict,
    *,
    state_path: Path,
    program: dict | None,
) -> str:
    canonical_skill_text = canonical_skill_serialized_asked_medium_text(state_path=state_path)
    if canonical_skill_text:
        return canonical_skill_text
    closure_program = project_bound_program_shape(program)
    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    if isinstance(closure_program, dict) and program_is_asked_medium_closure(
        closure_program,
        asked_medium=asked_medium,
    ):
        operation = str(closure_program.get("operation", "")).strip()
        success_signal = str(closure_program.get("success_signal", "")).strip()
        owner_skill = str(closure_program.get("owner_skill_if_any", "")).strip()
        lines = ["# Runtime Solve Steps", ""]
        lines.append(
            (
                f"1. `{owner_skill}`：{operation}"
                if owner_skill and operation
                else operation
                or "1. 将当前 exact closure bite materialize 到 asked medium。"
            )
        )
        if success_signal:
            lines.append(f"2. 验收信号：{success_signal}。")
        return "\n".join(lines).strip() + "\n"
    return ""


def asked_medium_materialization_uses_runtime_solve_steps(state_path: Path) -> bool:
    return bool(canonical_skill_serialized_asked_medium_text(state_path=state_path))


def asked_medium_skill_serialization_errors(
    state: dict,
    *,
    state_path: Path,
) -> list[str]:
    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    if not asked_medium:
        return []
    evidence = state.get("materialization_evidence")
    if not isinstance(evidence, dict):
        return ["materialization evidence is missing"]

    output_path = asked_medium_output_path(state=state, state_path=state_path)
    if output_path is None:
        return ["asked medium output path could not be resolved"]
    location = str(evidence.get("location", "")).strip()
    if _normalized_existing_path_text(location) != _normalized_existing_path_text(str(output_path)):
        return ["materialization evidence does not point at the asked medium file"]
    if evidence.get("skill_serialized") is not True:
        return ["asked medium artifact is not marked as skill-serialized"]
    if not output_path.exists():
        return ["asked medium file does not exist on disk"]

    canonical_text = canonical_skill_serialized_asked_medium_text(state_path=state_path)
    if not canonical_text:
        return ["runtime solve-step serialization is not exportable yet"]
    current_text = output_path.read_text(encoding="utf-8")
    if current_text != canonical_text:
        return ["asked medium file does not match the canonical skill-serialized solve steps"]
    return []


def require_asked_medium_skill_serialization(
    state: dict,
    *,
    state_path: Path,
    context: str,
) -> None:
    errors = asked_medium_skill_serialization_errors(state, state_path=state_path)
    if errors:
        raise SystemExit(f"{context}: " + "; ".join(errors))


def materialize_asked_medium_if_ready(state: dict, *, state_path: Path) -> bool:
    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    program = project_bound_program_shape(state.get("bound_program"))
    if asked_medium and not (
        isinstance(program, dict)
        and program_is_asked_medium_closure(program, asked_medium=asked_medium)
    ):
        promoted = promote_report_derived_exact_closure(
            state,
            state_path=state_path,
        )
        if promoted:
            program = project_bound_program_shape(state.get("bound_program"))
    if not asked_medium or not isinstance(program, dict):
        return False
    if not program_is_asked_medium_closure(program, asked_medium=asked_medium):
        return False
    report = build_report(state, state_path)
    closure_combo = _closure_skill_combo_from_report(
        report,
        fallback=program.get("owner_skill_combo_if_any"),
    )
    if closure_combo:
        updated_program = attach_program_owner_metadata(
            program,
            owner_skill=_closure_owner_from_combo(
                closure_combo,
                preferred_owner=program.get("owner_skill_if_any"),
            ),
            owner_combo=closure_combo,
        )
        if isinstance(updated_program, dict):
            state["bound_program"] = updated_program
            program = updated_program
    if not _closure_combo_is_composite(program.get("owner_skill_combo_if_any")):
        return False

    operation = str(program.get("operation", "")).strip()
    if not operation or operation == "materialize_exact_asked_medium_读出":
        return False

    output_path = asked_medium_output_path(state=state, state_path=state_path)
    if output_path is None:
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    skill_serialized = asked_medium_materialization_uses_runtime_solve_steps(state_path)
    canonical_text = canonical_asked_medium_materialization_text(
        state,
        state_path=state_path,
        program=program,
    )
    if not canonical_text:
        return False
    existing_evidence = state.get("materialization_evidence")
    preserve_existing_output = (
        output_path.exists()
        and output_path.read_text(encoding="utf-8") == canonical_text
        and isinstance(existing_evidence, dict)
        and _normalized_existing_path_text(str(existing_evidence.get("location", "")).strip())
        == _normalized_existing_path_text(str(output_path))
    )
    if not preserve_existing_output:
        output_path.write_text(canonical_text, encoding="utf-8")

    output = state.setdefault("output_status", {})
    output["touched"] = True
    output["cosmetic_only"] = False
    output["contains_unsupported"] = False
    output["contains_placeholder"] = False
    output["final_artifact_materialized"] = True
    state["materialization_evidence"] = {
        "kind": "file",
        "location": str(output_path),
        "skill_serialized": skill_serialized,
        "summary": (
            "runtime sealed the existing asked-medium artifact under exact closure"
            if preserve_existing_output
            else (
                "runtime materialized the exact asked-medium 读出 from solve-step serialization"
                if skill_serialized
                else "runtime materialized the exact asked-medium 读出 from a concrete closure bite"
            )
        ),
    }
    finalize_materialized_closure(state, state_path=state_path)
    return True


def asked_medium_materialization_ready(state: dict) -> bool:
    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    program = project_bound_program_shape(state.get("bound_program"))
    if not asked_medium or not isinstance(program, dict):
        return False
    if not program_is_asked_medium_closure(program, asked_medium=asked_medium):
        return False
    output_status = state.get("output_status")
    if not (isinstance(output_status, dict) and output_status.get("touched") is True):
        return False
    operation = str(program.get("operation", "")).strip()
    return bool(operation and operation != "materialize_exact_asked_medium_读出")


def reset_output_materialization_for_new_local_move(state: dict) -> None:
    state["materialization_evidence"] = None
    output = state.setdefault("output_status", {})
    if not isinstance(output, dict):
        output = {}
        state["output_status"] = output
    output["touched"] = False
    output["cosmetic_only"] = False
    output["contains_unsupported"] = False
    output["contains_placeholder"] = False
    output["final_artifact_materialized"] = False


def promote_report_derived_exact_closure(state: dict, *, state_path: Path) -> bool:
    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    if not asked_medium:
        return False
    takeover_gate = state.get("primitive_takeover_gate_if_any")
    if (
        isinstance(takeover_gate, dict)
        and str(takeover_gate.get("trigger", "")).strip() == "same_carrier_landing"
    ):
        return False
    layer = state.get("layer_composition_if_any")
    if isinstance(layer, dict):
        surface = str(layer.get("surface", "")).strip()
        controlled_object = str(layer.get("controlled_object", "")).strip()
        if surface in {"takeover_recomposition", "bound_program"} and controlled_object and controlled_object != asked_medium:
            return False
    output_status = state.get("output_status")
    if not (isinstance(output_status, dict) and output_status.get("touched") is True):
        return False
    existing_program = project_bound_program_shape(state.get("bound_program"))
    if isinstance(existing_program, dict) and program_is_asked_medium_closure(
        existing_program,
        asked_medium=asked_medium,
    ):
        return False

    report = build_report(state, state_path)
    bridge = report.get("skill_authority_bridge")
    if not isinstance(bridge, dict):
        return False
    closure_touch = project_bound_program_shape(bridge.get("executable_local_touch_if_any"))
    if not isinstance(closure_touch, dict):
        return False
    if not program_is_direct_closure_candidate(closure_touch, state):
        return False

    promoted_program = dict(closure_touch)
    promoted_program["target"] = asked_medium
    promoted_program["success_signal"] = "asked_medium_is_exact_and_executable"
    combo = _closure_skill_combo_from_report(
        report,
        fallback=bridge.get("active_skill_combo_if_any"),
    )
    if not _closure_combo_is_composite(combo):
        return False
    owner_skill = _closure_owner_from_combo(
        bridge.get("active_skill_combo_if_any"),
        bridge.get("supporting_skills_if_any"),
        closure_touch,
        combo,
        preferred_owner=bridge.get("executable_owner_skill_if_any")
        or bridge.get("winning_skill_if_any"),
    )
    if not owner_skill:
        return False
    promoted_program = attach_program_owner_metadata(
        promoted_program,
        owner_skill=owner_skill,
        owner_combo=combo,
    ) or promoted_program
    state["bound_program"] = promoted_program
    state["gate_binding_if_any"] = None
    state["carrier_handoff_if_any"] = None
    state["secondary_rival_if_any"] = None
    state["landed_next_touch_if_any"] = None
    state["primitive_takeover_gate_if_any"] = None
    state["layer_composition_if_any"] = build_layer_composition_state_payload(
        state,
        surface="bound_program",
        authorized_bite=promoted_program,
        skill_winner=owner_skill,
        skill_combo=combo,
        reason="exact closure now owns one local touch and should keep foreground authority until asked-medium contact changes",
        must_bind_local_bite=False,
        must_spend_handoff=False,
        layer_object=str(state.get("current_object", "")).strip(),
        controlled_object=asked_medium,
        current_seam=str(state.get("current_seam", "")).strip(),
        current_debt=str(state.get("current_debt", "")).strip(),
        next_local_choice=asked_medium,
        gap_object=asked_medium,
        transition_change=f"promoted exact closure on {asked_medium}",
        lighting_if_any=_report_skill_lighting(report),
    )
    return True


def has_runtime_owned_asked_medium_materialization(state: dict) -> bool:
    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    if not asked_medium:
        return False
    output_status = state.get("output_status")
    evidence = state.get("materialization_evidence")
    if not isinstance(output_status, dict) or not isinstance(evidence, dict):
        return False
    location = str(evidence.get("location", "")).strip()
    return (
        output_status.get("touched") is True
        and output_status.get("final_artifact_materialized") is True
        and evidence.get("skill_serialized") is True
        and bool(location)
        and Path(location).name == Path(asked_medium).name
    )


def finalize_materialized_closure(state: dict, *, state_path: Path | None = None) -> bool:
    if state.get("release_veto") is not True:
        return False
    if not can_clear_release_veto_without_program(state):
        return False
    bound_program = project_bound_program_shape(state.get("bound_program"))
    if isinstance(bound_program, dict):
        asked_medium = str(state.get("asked_medium_surface", "")).strip()
        if (
            program_is_asked_medium_closure(bound_program, asked_medium=asked_medium)
            and not _closure_combo_is_composite(bound_program.get("owner_skill_combo_if_any"))
        ):
            return False
    if str(state.get("asked_medium_surface", "")).strip():
        if state_path is None:
            return False
        require_asked_medium_skill_serialization(
            state,
            state_path=state_path,
            context="finalize materialized closure refused",
        )

    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    bound_program = state.get("bound_program")
    if isinstance(bound_program, dict) and not program_is_asked_medium_closure(
        bound_program,
        asked_medium=asked_medium,
    ):
        return False

    state["bound_program"] = None
    state["layer_composition_if_any"] = None
    state["gate_binding_if_any"] = None
    state["primitive_field_if_any"] = None
    state["primitive_competition_if_any"] = None
    state["carrier_handoff_if_any"] = None
    state["secondary_rival_if_any"] = None
    state["landed_next_touch_if_any"] = None
    state["primitive_takeover_gate_if_any"] = None
    state["release_veto"] = False
    return True


def set_primitive_field(state: dict, args: argparse.Namespace) -> None:
    primitive_field = {
        "layer_object": args.layer_object,
        "active_primitives": [
            canonicalize_primitive_token(value) for value in (args.active_primitive or [])
        ],
        "why_now": args.why_now,
    }
    if args.tie_break_check is not None:
        primitive_field["tie_break_check"] = args.tie_break_check
    if args.selection_basis is not None:
        primitive_field["selection_basis"] = args.selection_basis
    if args.evidence_basis is not None:
        primitive_field["evidence_basis"] = args.evidence_basis
    state["primitive_field_if_any"] = primitive_field


def set_primitive_competition(state: dict, args: argparse.Namespace) -> None:
    candidates: list[dict] = []
    for raw_candidate in args.candidate or []:
        primitive, touch_target, expected_local_gain = raw_candidate.split("|", 2)
        candidates.append(
            {
                "primitive": canonicalize_primitive_token(primitive),
                "touch_target": touch_target,
                "expected_local_gain": expected_local_gain,
            }
        )
    competition = {
        "layer_object": args.layer_object,
        "candidates": candidates,
    }
    if args.separating_check is not None:
        competition["separating_check"] = args.separating_check
    if args.winner_if_any is not None:
        competition["winner_if_any"] = canonicalize_primitive_token(args.winner_if_any)
    state["primitive_competition_if_any"] = competition


def project_bound_program_shape(payload: object) -> dict | None:
    if not isinstance(payload, dict):
        return None
    kind = str(payload.get("kind", "")).strip()
    target = str(payload.get("target", "")).strip()
    operation = str(payload.get("operation", "")).strip()
    success_signal = str(payload.get("success_signal", "")).strip()
    if not kind or not target or not operation:
        return None
    program = {
        "kind": kind,
        "target": target,
        "operation": operation,
    }
    if success_signal:
        program["success_signal"] = success_signal
    owner_skill = canonicalize_skill_token(payload.get("owner_skill_if_any"))
    if owner_skill:
        program["owner_skill_if_any"] = owner_skill
    raw_combo = payload.get("owner_skill_combo_if_any")
    if isinstance(raw_combo, list):
        owner_combo = normalize_skill_combo(raw_combo)
        if owner_combo:
            program["owner_skill_combo_if_any"] = owner_combo[:6]
    for key in [
        "current_layer_object_if_any",
        "controlled_object_if_any",
        "object_transform_if_any",
        "next_object_if_any",
        "step_outline_if_any",
        "skill_phase_if_any",
    ]:
        value = str(payload.get(key, "")).strip()
        if value:
            program[key] = value
    return program


def normalize_skill_combo(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    combo: list[str] = []
    for value in values:
        token = canonicalize_skill_token(value)
        if token and token not in combo:
            combo.append(token)
    return combo[:6]


def has_explicit_skill_ownership(payload: object) -> bool:
    program = project_bound_program_shape(payload)
    if not isinstance(program, dict):
        return False
    owner = canonicalize_skill_token(program.get("owner_skill_if_any"))
    combo = extract_explicit_skill_combo(program)
    if not owner or not combo:
        return False
    return owner in combo


def attach_program_owner_metadata(
    program: dict | None,
    *,
    owner_skill: str = "",
    owner_combo: object = None,
) -> dict | None:
    payload = project_bound_program_shape(program)
    if not isinstance(payload, dict):
        return None
    resolved_owner = (
        canonicalize_skill_token(owner_skill)
        or canonicalize_skill_token(payload.get("owner_skill_if_any"))
    )
    resolved_combo = normalize_skill_combo(
        owner_combo if owner_combo is not None else payload.get("owner_skill_combo_if_any")
    )
    if resolved_owner and resolved_owner not in resolved_combo:
        resolved_combo = [resolved_owner] + [
            value for value in resolved_combo if value != resolved_owner
        ]
    if not resolved_owner and resolved_combo:
        resolved_owner = resolved_combo[0]
    if resolved_owner:
        payload["owner_skill_if_any"] = resolved_owner
    if resolved_combo:
        payload["owner_skill_combo_if_any"] = resolved_combo[:6]
    return payload


def _merge_closure_skill_combo(*sources: object, limit: int = 6) -> list[str]:
    ordered: list[str] = []
    for source in sources:
        values = extract_explicit_skill_combo(source) if isinstance(source, dict) else normalize_skill_combo(source)
        for value in values:
            token = canonicalize_skill_token(value)
            if (
                token
                and token not in ordered
                and token not in CLOSURE_COMBO_DISALLOWED_SKILLS
                and token != "精确封口"
            ):
                ordered.append(token)
    return ordered[:limit]


def _closure_skill_combo_from_report(report: dict, *, fallback: object = None) -> list[str]:
    if not isinstance(report, dict):
        return _merge_closure_skill_combo(fallback)
    bridge = report.get("skill_authority_bridge")
    competition = report.get("skill_competition")
    lighting = report.get("skill_lighting_surface")
    layer = report.get("layer_composition")
    closure_nucleus = report.get("closure_nucleus")
    return _merge_closure_skill_combo(
        fallback,
        bridge.get("active_skill_combo_if_any") if isinstance(bridge, dict) else None,
        bridge.get("supporting_skills_if_any") if isinstance(bridge, dict) else None,
        competition.get("winning_combo_if_any") if isinstance(competition, dict) else None,
        competition.get("coactive_skills_if_any") if isinstance(competition, dict) else None,
        lighting.get("supporting_skills_if_any") if isinstance(lighting, dict) else None,
        lighting.get("candidate_skills_if_any") if isinstance(lighting, dict) else None,
        layer.get("active_skill_combo_if_any") if isinstance(layer, dict) else None,
        closure_nucleus.get("current_structural_bite_if_any") if isinstance(closure_nucleus, dict) else None,
        closure_nucleus.get("current_读出_bite_if_any") if isinstance(closure_nucleus, dict) else None,
    )


def _closure_combo_is_composite(values: object) -> bool:
    combo = _merge_closure_skill_combo(values)
    return len(combo) >= 2


def _closure_owner_from_combo(*sources: object, preferred_owner: object = "") -> str:
    preferred = canonicalize_skill_token(preferred_owner)
    combo = _merge_closure_skill_combo(*sources)
    if preferred and preferred in combo:
        return preferred
    return combo[0] if combo else ""


def align_program_owner_with_authority(
    program: dict | None,
    authority_program: dict | None,
) -> dict | None:
    payload = project_bound_program_shape(program)
    authority_payload = project_bound_program_shape(authority_program)
    if not isinstance(payload, dict) or not isinstance(authority_payload, dict):
        return payload
    if programs_conflict(payload, authority_payload):
        return payload
    authority_owner = canonicalize_skill_token(authority_payload.get("owner_skill_if_any"))
    authority_combo = extract_explicit_skill_combo(authority_payload)
    if not authority_owner or not authority_combo:
        return payload
    payload_owner = canonicalize_skill_token(payload.get("owner_skill_if_any"))
    payload_combo = extract_explicit_skill_combo(payload)
    if payload_owner == authority_owner and payload_combo == authority_combo:
        return payload
    return (
        attach_program_owner_metadata(
            payload,
            owner_skill=authority_owner,
            owner_combo=authority_combo,
        )
        or payload
    )


def normalize_direct_asked_medium_closure_owner(
    program: dict | None,
    *,
    asked_medium: str,
    preferred_owner: str = "",
    preferred_combo: object = None,
) -> dict | None:
    payload = project_bound_program_shape(program)
    if not isinstance(payload, dict):
        return None
    normalized_asked_medium = _extract_markdown_artifact_hint(asked_medium)
    if not normalized_asked_medium:
        return payload
    if not program_is_asked_medium_closure(payload, asked_medium=normalized_asked_medium):
        return payload
    resolved_owner = canonicalize_skill_token(preferred_owner) or canonicalize_skill_token(
        payload.get("owner_skill_if_any")
    )
    resolved_combo = _merge_closure_skill_combo(
        preferred_combo if preferred_combo is not None else None,
        extract_explicit_skill_combo(payload),
        ["读出"],
    )
    closure_in_play = bool(resolved_owner or resolved_combo)
    if not closure_in_play:
        return payload
    resolved_owner = _closure_owner_from_combo(
        preferred_combo if preferred_combo is not None else None,
        extract_explicit_skill_combo(payload),
        preferred_owner=resolved_owner,
    )
    if not resolved_owner or not _closure_combo_is_composite(resolved_combo):
        return payload
    return (
        attach_program_owner_metadata(
            payload,
            owner_skill=resolved_owner,
            owner_combo=resolved_combo,
        )
        or payload
    )


def normalize_program_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


@lru_cache(maxsize=1)
def _generic_runtime_operation_templates() -> set[str]:
    templates = {
        "same_carrier_local_change_or_check",
        "materialize_exact_asked_medium_读出",
    }
    for primitive in ALLOWED_PRIMITIVES:
        semantics = get_primitive_semantics(primitive)
        touch = normalize_program_text(semantics.get("cheapest_honest_touch"))
        if touch:
            templates.add(touch)
    return templates


def is_generic_runtime_operation(program: object) -> bool:
    if not isinstance(program, dict):
        return False
    operation = normalize_program_text(program.get("operation"))
    if not operation:
        return False
    if operation in _generic_runtime_operation_templates():
        return True
    if (
        operation.startswith("touch ")
        and " with one " in operation
        and " move that directly pressures " in operation
    ):
        return True
    return False


def strongest_explicit_program_owner(programs: object) -> tuple[str, list[str]]:
    if not isinstance(programs, list):
        return "", []
    for candidate in programs:
        program = project_bound_program_shape(candidate)
        if not has_explicit_skill_ownership(program):
            continue
        owner = canonicalize_skill_token(program.get("owner_skill_if_any"))
        combo = extract_explicit_skill_combo(program)
        if owner and combo:
            return owner, combo
    return "", []


def seeded_combo_matches_current_layer(state: dict, combo: list[str]) -> bool:
    normalized_combo = normalize_skill_combo(combo)
    if not normalized_combo:
        return False

    primitive_field = state.get("primitive_field_if_any")
    if isinstance(primitive_field, dict):
        field_primitives = normalize_skill_combo(primitive_field.get("active_primitives"))
        if field_primitives and not set(normalized_combo).intersection(field_primitives):
            return False

    primitive_competition = state.get("primitive_competition_if_any")
    if isinstance(primitive_competition, dict):
        winner = canonicalize_primitive_token(primitive_competition.get("winner_if_any"))
        if winner and winner not in normalized_combo:
            return False
        competition_primitives = normalize_skill_combo(
            [
                candidate.get("primitive")
                for candidate in primitive_competition.get("candidates", [])
                if isinstance(candidate, dict)
            ]
        )
        if competition_primitives and not set(normalized_combo).intersection(competition_primitives):
            return False

    return True


def infer_next_layer_choice_for_bound_program(
    state: dict,
    report: dict,
    candidate_program: dict | None,
) -> str:
    candidate_target = str((candidate_program or {}).get("target", "")).strip()
    current_object = str(state.get("current_object", "")).strip()
    current_seam = str(state.get("current_seam", "")).strip()
    next_bite = str(state.get("next_bite", "")).strip()
    if candidate_target and candidate_target != current_object:
        return candidate_target
    gap_choice = str(((report.get("gap_object") or {}).get("object", ""))).strip()
    if gap_choice and gap_choice not in {current_object, candidate_target}:
        return gap_choice
    resume_choice = str(((report.get("resume_bridge") or {}).get("next_local_choice", ""))).strip()
    if resume_choice and resume_choice not in {current_object, candidate_target}:
        return resume_choice
    for candidate_choice in [next_bite, current_seam]:
        if candidate_choice and candidate_choice not in {current_object, candidate_target}:
            return candidate_choice

    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    if asked_medium and asked_medium not in {current_object, candidate_target}:
        return asked_medium
    return candidate_target or resume_choice


def infer_generic_same_carrier_landing_transition(
    state: dict,
    bound_program: dict,
) -> tuple[str, str, str, str] | None:
    current_object = str(state.get("current_object", "")).strip()
    current_seam = str(state.get("current_seam", "")).strip()
    current_debt = str(state.get("current_debt", "")).strip()
    target = str(bound_program.get("target", "")).strip() or current_seam or current_object
    combo = extract_explicit_skill_combo(bound_program)
    trio = {value for value in combo[:3] if value}
    if not trio:
        return None

    if trio == {"投影", "守恒", "见证"}:
        return (
            f"the projected conserved carrier now controlling {target}",
            f"the first exact feasibility threshold on that carrier for {target}",
            (
                f"separate the first impossible side from the first sufficient side on the explicit carrier for {target}"
                if target
                else current_debt
            ),
            (
                f"evaluate one exact threshold or boundary on the explicit carrier for {target}, "
                f"keep one 见证 on the first feasible side, and cash that boundary into the next unpaid consequence"
            ),
        )

    if trio == {"赋值", "图像", "极限边界"}:
        return (
            f"the explicit assigned carrier now controlling {target}",
            f"the first decisive anchor / peak / endpoint seam on the explicit carrier for {target}",
            (
                f"read the next unpaid consequence directly from the explicit carrier for {target} instead of reopening the original shell"
            ),
            (
                f"draw the carrier graph or skeleton for {target}, pin one anchor and one decisive extreme / singular seam, "
                f"then read the cheapest unpaid consequence directly there"
            ),
        )

    if trio == {"图像", "极限边界", "读出"}:
        return (
            f"the explicit carrier skeleton now controls the next 读出 on {target}",
            f"the cheapest intersection / branch / edge 读出 on that carrier for {target}",
            f"cash one local 读出 on the explicit carrier before reopening any broader narration around {target}",
            (
                f"read one local consequence directly from the explicit carrier on {target}, "
                f"using the controlling edge / branch / intersection before broader continuation"
            ),
        )

    if trio == {"对称", "第一裂缝", "见证"}:
        return (
            f"the singular split around the live seam now controls {target}",
            f"the weakest asymmetric crack around that singular split for {target}",
            f"use the singular split to force the next unpaid global consequence on {target}",
            (
                f"treat the live branches as one controlled split around the singular seam on {target}, "
                f"then 见证 which side must open farther or fail first"
            ),
        )

    if trio == {"第一裂缝", "极限边界", "见证"}:
        return (
            f"the decisive boundary crack now controls the global claim on {target}",
            f"the first global failure seam exposed by that boundary on {target}",
            f"explode the remaining global claim at the controlling boundary rather than reopening interior narration on {target}",
            (
                f"push directly to the controlling edge / endpoint / singular crack on {target}, "
                f"and use one 见证 there to settle the remaining global claim"
            ),
        )

    if trio == {"极限边界", "状态拆分", "见证"}:
        return (
            f"the explicit compatibility split now controlling {target}",
            f"the first impossible / surviving branch on that split for {target}",
            (
                f"separate the uniquely survivable side from the dead or boundary-failing branches "
                f"on the explicit split for {target}"
            ),
            (
                f"compare the rival local orderings or branches on the explicit split for {target}, "
                f"kill the dead boundary sides, and keep only the uniquely survivable line"
            ),
        )

    return None


def infer_same_carrier_landing_transition(
    state: dict,
    bound_program: dict,
) -> tuple[str, str, str, str]:
    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    current_object = str(state.get("current_object", "")).strip()
    current_seam = str(state.get("current_seam", "")).strip()
    current_debt = str(state.get("current_debt", "")).strip()
    target = str(bound_program.get("target", "")).strip()
    generic = infer_generic_same_carrier_landing_transition(state, bound_program)
    if generic is not None:
        return generic

    next_object = target or current_seam or current_debt or current_object
    next_seam = target or current_debt or current_seam or next_object
    next_debt = current_debt or asked_medium
    next_bite = target or next_seam or asked_medium
    return next_object, next_seam, next_debt, next_bite


def same_carrier_landing_is_ready(state: dict, bound_program: dict) -> bool:
    try:
        next_object, next_seam, next_debt, next_bite = infer_same_carrier_landing_transition(
            state,
            bound_program,
        )
    except Exception:
        return False
    if not next_object or not next_debt or not next_bite:
        return False
    current_object = str(state.get("current_object", "")).strip()
    current_seam = str(state.get("current_seam", "")).strip()
    current_debt = str(state.get("current_debt", "")).strip()
    current_bite = str(state.get("next_bite", "")).strip()
    return any(
        [
            next_object != current_object,
            next_seam != current_seam,
            next_debt != current_debt,
            next_bite != current_bite,
        ]
    )


def _direct_closure_takeover_allowed(
    *,
    report: dict,
    state: dict,
    asked_medium: str,
    direct_closure_signal: bool,
    reopened_target: str,
) -> bool:
    if not asked_medium or not isinstance(report, dict):
        return False
    closure_nucleus = report.get("closure_nucleus")
    if not isinstance(closure_nucleus, dict):
        return False
    return closure_can_take_first_shot(
        closure_nucleus=closure_nucleus,
        direct_closure_allowed=direct_closure_signal,
        asked_medium=asked_medium,
    )


def materialize_handoff_layer_authority(
    state: dict,
    path: Path,
    handoff: dict,
    *,
    reason: str,
) -> None:
    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    landed_bite = project_bound_program_shape(state.get("bound_program"))
    report = build_report(state, path)
    closure_nucleus = report.get("closure_nucleus")
    closure_touch = (
        project_bound_program_shape(closure_nucleus.get("current_读出_bite_if_any"))
        if isinstance(closure_nucleus, dict)
        else None
    )
    if closure_touch is None and asked_medium:
        compiled_closure_touch = derive_object_compiled_读出_candidate(
            state,
            asked_medium=asked_medium,
            current_object=str(state.get("current_object", "")).strip(),
            current_debt=str(state.get("current_debt", "")).strip(),
            current_seam=str(state.get("current_seam", "")).strip(),
            next_bite=str(state.get("next_bite", "")).strip(),
            structural_bite=landed_bite if isinstance(landed_bite, dict) else None,
        )
        closure_touch = (
            project_bound_program_shape(compiled_closure_touch)
            if isinstance(compiled_closure_touch, dict)
            else None
        )
    preferred_direct_closure = bool(
        isinstance(closure_touch, dict)
        and program_is_direct_closure_candidate(closure_touch, state)
        and has_explicit_skill_ownership(closure_touch)
    )
    closure_nucleus = report.get("closure_nucleus")
    closure_touch = (
        project_bound_program_shape(closure_nucleus.get("current_读出_bite_if_any"))
        if isinstance(closure_nucleus, dict)
        else None
    )
    if closure_touch is None and asked_medium:
        compiled_closure_touch = derive_object_compiled_读出_candidate(
            state,
            asked_medium=asked_medium,
            current_object=str(state.get("current_object", "")).strip(),
            current_debt=str(state.get("current_debt", "")).strip(),
            current_seam=str(state.get("current_seam", "")).strip(),
            next_bite=str(state.get("next_bite", "")).strip(),
            structural_bite=landed_bite if isinstance(landed_bite, dict) else None,
        )
        closure_touch = (
            project_bound_program_shape(compiled_closure_touch)
            if isinstance(compiled_closure_touch, dict)
            else None
        )
    preferred_direct_closure = bool(
        isinstance(closure_touch, dict)
        and program_is_direct_closure_candidate(closure_touch, state)
        and has_explicit_skill_ownership(closure_touch)
    )
    closure_nucleus = report.get("closure_nucleus")
    closure_touch = (
        project_bound_program_shape(closure_nucleus.get("current_读出_bite_if_any"))
        if isinstance(closure_nucleus, dict)
        else None
    )
    if closure_touch is None and asked_medium:
        compiled_closure_touch = derive_object_compiled_读出_candidate(
            state,
            asked_medium=asked_medium,
            current_object=str(state.get("current_object", "")).strip(),
            current_debt=str(state.get("current_debt", "")).strip(),
            current_seam=str(state.get("current_seam", "")).strip(),
            next_bite=str(state.get("next_bite", "")).strip(),
            structural_bite=landed_bite if isinstance(landed_bite, dict) else None,
        )
        closure_touch = (
            project_bound_program_shape(compiled_closure_touch)
            if isinstance(compiled_closure_touch, dict)
            else None
        )
    preferred_direct_closure = bool(
        isinstance(closure_touch, dict)
        and program_is_direct_closure_candidate(closure_touch, state)
        and has_explicit_skill_ownership(closure_touch)
    )
    skill_winner, skill_combo, skill_program, _silence_after_contact = read_skill_authority_program(
        report,
        require_same_carrier=False,
    )
    candidate_program = project_bound_program_shape(skill_program)
    primitive_program = derive_primitive_program_candidate(state, [])
    primitive_candidate = (
        project_bound_program_shape(primitive_program)
        if isinstance(primitive_program, dict)
        else None
    )
    if not isinstance(candidate_program, dict):
        candidate_program = primitive_candidate
    elif (
        isinstance(primitive_candidate, dict)
        and has_explicit_skill_ownership(primitive_candidate)
        and (
            is_generic_runtime_operation(candidate_program)
            or not has_explicit_skill_ownership(candidate_program)
            or str(candidate_program.get("target", "")).strip()
            != str(primitive_candidate.get("target", "")).strip()
            or str(candidate_program.get("kind", "")).strip()
            != str(primitive_candidate.get("kind", "")).strip()
        )
    ):
        candidate_program = primitive_candidate
    handoff_target = str(handoff.get("to_object", "")).strip()
    if isinstance(candidate_program, dict) and handoff_target:
        current_target = str(candidate_program.get("target", "")).strip()
        thick_object_target = str(state.get("current_object", "")).strip()
        if (
            current_target
            and current_target != handoff_target
            and current_target == thick_object_target
        ):
            rebuilt_owner = canonicalize_skill_token(candidate_program.get("owner_skill_if_any")) or canonicalize_skill_token(skill_winner)
            rebuilt_combo = extract_explicit_skill_combo(candidate_program) or list(skill_combo)
            rebuilt_supporting = [
                skill_name for skill_name in rebuilt_combo if skill_name and skill_name != rebuilt_owner
            ][:3]
            rebuilt_touch = build_problem_born_touch_for_skill(
                state,
                rebuilt_owner or (rebuilt_combo[0] if rebuilt_combo else ""),
                target=handoff_target,
                supporting=rebuilt_supporting,
            )
            rebuilt_candidate = project_bound_program_shape(rebuilt_touch)
            if isinstance(rebuilt_candidate, dict) and has_explicit_skill_ownership(rebuilt_candidate):
                candidate_program = rebuilt_candidate
    if not isinstance(candidate_program, dict) or not has_explicit_skill_ownership(candidate_program):
        state["layer_composition_if_any"] = None
        return
    persisted_skill_winner = (
        str(candidate_program.get("owner_skill_if_any", "")).strip()
        or skill_winner
    )
    event_skill_combo = extract_explicit_skill_combo(candidate_program) or list(skill_combo)
    post_report = build_report(state, path)
    state["layer_composition_if_any"] = build_layer_composition_state_payload(
        state,
        surface="carrier_handoff",
        authorized_bite=candidate_program,
        skill_winner=persisted_skill_winner,
        skill_combo=event_skill_combo,
        reason=reason,
        must_bind_local_bite=False,
        must_spend_handoff=True,
        layer_object=str(state.get("current_object", "")).strip(),
        controlled_object=str(candidate_program.get("target", "")).strip(),
        current_seam=str(state.get("current_seam", "")).strip(),
        current_debt=str(state.get("current_debt", "")).strip(),
        next_local_choice=infer_next_layer_choice_for_bound_program(
            state,
            post_report,
            candidate_program,
        ),
        gap_object=str(((post_report.get("gap_object") or {}).get("object", ""))).strip(),
        transition_change=f"armed handoff into {str(handoff.get('to_object', '')).strip()}",
        lighting_if_any=_report_skill_lighting(post_report),
    )


def arm_primitive_takeover_gate(
    state: dict,
    *,
    trigger: str,
    note: str,
) -> None:
    primitive_field = state.get("primitive_field_if_any")
    active_primitives: list[str] = []
    if isinstance(primitive_field, dict):
        raw_active = primitive_field.get("active_primitives")
        if isinstance(raw_active, list):
            active_primitives = [str(value).strip() for value in raw_active if str(value).strip()][:3]
    gate = {
        "trigger": trigger,
        "current_object": str(state.get("current_object", "")).strip(),
        "current_seam": str(state.get("current_seam", "")).strip(),
        "current_debt": str(state.get("current_debt", "")).strip(),
        "next_bite": str(state.get("next_bite", "")).strip(),
        "note": note,
    }
    if active_primitives:
        gate["active_primitives"] = active_primitives
    state["primitive_takeover_gate_if_any"] = gate


def clear_primitive_takeover_gate(state: dict) -> None:
    state["primitive_takeover_gate_if_any"] = None


def build_layer_composition_state_payload(
    state: dict,
    *,
    surface: str,
    authorized_bite: dict | None,
    skill_winner: str,
    skill_combo: list[str],
    reason: str = "",
    must_bind_local_bite: bool = False,
    must_spend_handoff: bool = False,
    layer_object: str = "",
    controlled_object: str = "",
    current_seam: str = "",
    current_debt: str = "",
    next_local_choice: str = "",
    gap_object: str = "",
    transition_change: str = "",
    lighting_if_any: dict | None = None,
) -> dict | None:
    program = project_bound_program_shape(authorized_bite)
    if not has_explicit_skill_ownership(program):
        program = (
            attach_program_owner_metadata(
                program,
                owner_skill=str(skill_winner).strip(),
                owner_combo=skill_combo,
            )
            or program
        )
    explicit_program_combo = extract_explicit_skill_combo(program)
    if not isinstance(program, dict) or not has_explicit_skill_ownership(program):
        return None
    normalized_combo = explicit_program_combo[:]
    if not normalized_combo:
        return None
    normalized_event_combo = _normalized_skill_list(skill_combo)
    payload = {
        "surface": surface,
        "event_owned": True,
        "forbid_ordinary_regrowth": True,
        "must_bind_local_bite": must_bind_local_bite,
        "must_spend_handoff": must_spend_handoff,
    }
    leading_skill = str(skill_winner).strip()
    if leading_skill and leading_skill not in normalized_combo:
        return None
    if leading_skill:
        payload["leading_skill_if_any"] = leading_skill
    if reason:
        payload["reason"] = reason
    if isinstance(program, dict):
        payload["authorized_bite"] = program
    layer_object = str(layer_object or state.get("current_object", "")).strip()
    if layer_object:
        payload["layer_object"] = layer_object
    controlled_object = str(controlled_object).strip() or (
        str(program.get("controlled_object_if_any", "")).strip() if isinstance(program, dict) else ""
    ) or (
        str(program.get("target", "")).strip() if isinstance(program, dict) else ""
    ) or layer_object
    if controlled_object:
        payload["controlled_object"] = controlled_object
    current_seam = str(current_seam or state.get("current_seam", "")).strip()
    if current_seam:
        payload["current_seam"] = current_seam
    current_debt = str(current_debt or state.get("current_debt", "")).strip()
    if current_debt:
        payload["current_debt"] = current_debt
    next_local_choice = str(next_local_choice).strip() or (
        str(program.get("next_object_if_any", "")).strip() if isinstance(program, dict) else ""
    )
    if next_local_choice:
        payload["next_local_choice"] = next_local_choice
    gap_object = str(gap_object).strip()
    if gap_object:
        payload["gap_object"] = gap_object
    transition_change = str(transition_change).strip()
    if transition_change:
        payload["transition_change"] = transition_change
    projected_lighting: dict = {}
    if isinstance(lighting_if_any, dict):
        for key in [
            "lit_skill_if_any",
            "candidate_skills_if_any",
            "comparison_skill_if_any",
            "supporting_skills_if_any",
            "false_first_skill_if_any",
            "false_first_label_if_any",
            "false_skill_reason",
            "verify_touch_if_any",
            "accountability_nudge_if_any",
            "winning_projected_gain_reason",
            "role_split_if_any",
            "ability_branch_if_any",
            "competition_basis",
            "ordinary_operations_are_not_skills",
            "anti_pipeline_note",
        ]:
            value = lighting_if_any.get(key)
            if value not in (None, "", [], {}):
                if key == "role_split_if_any" and isinstance(value, dict):
                    projected_role_split = {
                        subkey: value.get(subkey)
                        for subkey in [
                            "primary_skill_if_any",
                            "supporting_skills_if_any",
                            "check_skill_if_any",
                            "check_kind_if_any",
                            "check_target_if_any",
                            "ordinary_operations_are_not_skills",
                        ]
                        if value.get(subkey) not in (None, "", [], {})
                    }
                    if projected_role_split:
                        projected_lighting[key] = projected_role_split
                    continue
                if key == "ability_branch_if_any" and isinstance(value, dict):
                    projected_branch = {
                        subkey: value.get(subkey)
                        for subkey in ["support_operation_is_subordinate", "note"]
                        if value.get(subkey) not in (None, "", [], {})
                    }
                    if projected_branch:
                        projected_lighting[key] = projected_branch
                    continue
                projected_lighting[key] = value
    lit_skill = canonicalize_skill_token(projected_lighting.get("lit_skill_if_any"))
    if leading_skill:
        lit_skill = leading_skill
    if not lit_skill:
        lit_skill = leading_skill or normalized_combo[0]
    if lit_skill:
        projected_lighting["lit_skill_if_any"] = lit_skill
    supporting_skills = projected_lighting.get("supporting_skills_if_any")
    if not isinstance(supporting_skills, list) or not supporting_skills:
        supporting_skills = [skill_name for skill_name in normalized_combo if skill_name != lit_skill][:4]
    else:
        supporting_skills = _normalized_skill_list(supporting_skills, limit=4)
        supporting_skills = [skill_name for skill_name in supporting_skills if skill_name != lit_skill]
        if not supporting_skills:
            supporting_skills = [
                skill_name for skill_name in normalized_combo if skill_name != lit_skill
            ][:4]
    if supporting_skills:
        projected_lighting["supporting_skills_if_any"] = supporting_skills
    else:
        projected_lighting.pop("supporting_skills_if_any", None)
    projected_role_split = projected_lighting.get("role_split_if_any")
    if not isinstance(projected_role_split, dict):
        projected_role_split = {}
    if leading_skill:
        projected_role_split["primary_skill_if_any"] = leading_skill
        if supporting_skills:
            projected_role_split["supporting_skills_if_any"] = supporting_skills[:4]
    if not projected_role_split.get("check_skill_if_any"):
        check_skill = canonicalize_skill_token(projected_lighting.get("comparison_skill_if_any"))
        if check_skill and check_skill != leading_skill:
            projected_role_split["check_skill_if_any"] = check_skill
    verify_touch = projected_lighting.get("verify_touch_if_any")
    if isinstance(verify_touch, dict):
        verify_kind = str(verify_touch.get("kind", "")).strip()
        verify_target = str(verify_touch.get("target", "")).strip()
        if verify_kind:
            projected_role_split["check_kind_if_any"] = verify_kind
        if verify_target:
            projected_role_split["check_target_if_any"] = verify_target
    if projected_role_split:
        projected_role_split["ordinary_operations_are_not_skills"] = True
        projected_lighting["role_split_if_any"] = projected_role_split
    else:
        projected_lighting.pop("role_split_if_any", None)
    projected_lighting["ordinary_operations_are_not_skills"] = True
    projected_lighting["anti_pipeline_note"] = (
        str(projected_lighting.get("anti_pipeline_note", "")).strip()
        or "lighting remains a current-layer pressure surface, not a required order"
    )
    enriched_combo = _merged_skill_lists(
        normalized_combo,
        normalized_event_combo,
        [projected_lighting.get("lit_skill_if_any")] if projected_lighting.get("lit_skill_if_any") else [],
        projected_lighting.get("supporting_skills_if_any"),
        projected_role_split.get("supporting_skills_if_any"),
        limit=6,
    )
    if normalized_event_combo:
        missing_from_event = [
            skill_name for skill_name in normalized_combo if skill_name not in normalized_event_combo
        ]
        if missing_from_event and not set(missing_from_event).issubset(set(enriched_combo)):
            return None
    if leading_skill and leading_skill not in enriched_combo:
        enriched_combo = [leading_skill] + [
            skill_name for skill_name in enriched_combo if skill_name != leading_skill
        ]
    payload["active_skill_combo_if_any"] = enriched_combo[:6] if enriched_combo else normalized_combo[:6]
    if projected_lighting:
        payload["lighting_if_any"] = projected_lighting
    return payload


def build_event_report_excerpt_override(report: dict, layer_payload: dict | None) -> dict | None:
    if not isinstance(report, dict):
        return None
    excerpt = _report_excerpt(report)
    if isinstance(layer_payload, dict):
        report_layer = report.get("layer_composition", {})
        if not isinstance(report_layer, dict):
            report_layer = {}
        compact_layer: dict = {}
        for key in [
            "active",
            "surface",
            "layer_object",
            "controlled_object",
            "current_layer_object_if_any",
            "object_transform_if_any",
            "step_outline_if_any",
            "skill_phase_if_any",
            "current_seam",
            "current_debt",
            "reason",
            "leading_skill_if_any",
            "event_owned",
            "transition_change",
            "forbid_ordinary_regrowth",
            "next_local_choice",
            "gap_object",
            "false_first_skill_if_any",
            "false_first_label_if_any",
            "false_skill_reason",
            "accountability_nudge_if_any",
        ]:
            value = layer_payload.get(key)
            if value in (None, {}, [], ""):
                authorized = project_bound_program_shape(layer_payload.get("authorized_bite"))
                if isinstance(authorized, dict):
                    value = authorized.get(key)
            if value in (None, {}, [], ""):
                value = report_layer.get(key)
            if value not in (None, {}, [], ""):
                compact_layer[key] = value
        combo = _merged_skill_lists(
            layer_payload.get("active_skill_combo_if_any"),
            report_layer.get("active_skill_combo_if_any"),
            limit=6,
        )
        if combo:
            compact_layer["active_skill_combo_if_any"] = combo
        axes = _merged_skill_lists(
            layer_payload.get("composition_axes"),
            report_layer.get("composition_axes"),
            limit=4,
        )
        if axes:
            compact_layer["composition_axes"] = axes
        primitives = _merged_skill_lists(
            layer_payload.get("active_primitives"),
            report_layer.get("active_primitives"),
            limit=4,
        )
        if primitives:
            compact_layer["active_primitives"] = primitives
        background = _merged_skill_lists(
            layer_payload.get("background_skills_if_any"),
            report_layer.get("background_skills_if_any"),
            limit=6,
        )
        if background:
            compact_layer["background_skills_if_any"] = background
        supporting = _merged_skill_lists(
            layer_payload.get("supporting_skills_if_any"),
            report_layer.get("supporting_skills_if_any"),
            limit=6,
        )
        if supporting:
            compact_layer["supporting_skills_if_any"] = supporting
        authorized = project_bound_program_shape(layer_payload.get("authorized_bite"))
        if not isinstance(authorized, dict):
            authorized = project_bound_program_shape(report_layer.get("authorized_bite"))
        if isinstance(authorized, dict):
            compact_layer["authorized_bite"] = authorized
        persisted_lighting = layer_payload.get("lighting_if_any")
        if not isinstance(persisted_lighting, dict):
            persisted_lighting = report_layer.get("lighting_if_any")
        coaching_surface = report.get("skill_coaching_surface", {})
        lighting_surface = report.get("skill_lighting_surface", {})
        if isinstance(persisted_lighting, dict):
            projected_lighting = {}
            for key in [
                "lit_skill_if_any",
                "lit_control_skill_if_any",
                "candidate_skills_if_any",
                "comparison_skill_if_any",
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
                value = persisted_lighting.get(key)
                if value not in (None, {}, [], ""):
                    projected_lighting[key] = value
            if projected_lighting:
                compact_layer["lighting_if_any"] = projected_lighting
        if isinstance(coaching_surface, dict):
            for key in [
                "false_first_skill_if_any",
                "false_first_label_if_any",
                "false_skill_reason",
                "accountability_nudge_if_any",
                "winning_projected_gain_reason",
            ]:
                value = layer_payload.get(key)
                if value in (None, {}, [], ""):
                    value = compact_layer.get(key)
                if value in (None, {}, [], ""):
                    value = coaching_surface.get(key)
                if value not in (None, {}, [], ""):
                    compact_layer[key] = value
            verify_touch = coaching_surface.get("verify_touch_if_any")
            if isinstance(verify_touch, dict) and verify_touch:
                compact_layer["verify_touch_if_any"] = verify_touch
            supporting = coaching_surface.get("supporting_skills_if_any")
            if isinstance(supporting, list) and supporting and "supporting_skills_if_any" not in compact_layer:
                compact_layer["supporting_skills_if_any"] = _normalized_skill_list(supporting)
        if isinstance(lighting_surface, dict):
            lit_skill = str(lighting_surface.get("lit_skill_if_any", "")).strip()
            if lit_skill and "leading_skill_if_any" not in compact_layer:
                compact_layer["leading_skill_if_any"] = lit_skill
            for key in [
                "lit_control_skill_if_any",
                "false_first_skill_if_any",
                "false_first_label_if_any",
                "false_skill_reason",
                "accountability_nudge_if_any",
                "winning_projected_gain_reason",
            ]:
                value = lighting_surface.get(key)
                if value not in (None, {}, [], "") and key not in compact_layer:
                    compact_layer[key] = value
            verify_touch = lighting_surface.get("verify_touch_if_any")
            if isinstance(verify_touch, dict) and verify_touch and "verify_touch_if_any" not in compact_layer:
                compact_layer["verify_touch_if_any"] = verify_touch
            supporting = lighting_surface.get("supporting_skills_if_any")
            if isinstance(supporting, list) and supporting and "supporting_skills_if_any" not in compact_layer:
                compact_layer["supporting_skills_if_any"] = _normalized_skill_list(supporting)
            if "lighting_if_any" not in compact_layer:
                projected_lighting = {}
                for key in [
                    "lit_skill_if_any",
                    "lit_control_skill_if_any",
                    "candidate_skills_if_any",
                    "comparison_skill_if_any",
                    "supporting_skills_if_any",
                    "verify_touch_if_any",
                    "winning_projected_gain_reason",
                    "competition_basis",
                    "role_split_if_any",
                    "ordinary_operations_are_not_skills",
                    "anti_pipeline_note",
                ]:
                    value = lighting_surface.get(key)
                    if value not in (None, {}, [], ""):
                        projected_lighting[key] = value
                if projected_lighting:
                    compact_layer["lighting_if_any"] = projected_lighting
        projected_lighting = compact_layer.get("lighting_if_any")
        if isinstance(projected_lighting, dict):
            if "candidate_skills_if_any" not in projected_lighting and combo:
                projected_lighting["candidate_skills_if_any"] = combo[:]
            verify_touch = projected_lighting.get("verify_touch_if_any")
            if not isinstance(verify_touch, dict):
                verify_touch = {}
            if not verify_touch and isinstance(authorized, dict):
                verify_target = str(authorized.get("target", "")).strip()
                verify_kind = str(authorized.get("kind", "")).strip()
                if verify_target and verify_kind:
                    verify_touch = {"target": verify_target, "kind": verify_kind}
                    projected_lighting["verify_touch_if_any"] = verify_touch
            role_split = projected_lighting.get("role_split_if_any")
            if not isinstance(role_split, dict):
                role_split = {}
            primary_skill = str(compact_layer.get("leading_skill_if_any", "")).strip()
            if primary_skill:
                role_split.setdefault("primary_skill_if_any", primary_skill)
            supporting_for_roles = compact_layer.get("supporting_skills_if_any")
            if isinstance(supporting_for_roles, list) and supporting_for_roles:
                role_split.setdefault("supporting_skills_if_any", supporting_for_roles[:4])
            if isinstance(verify_touch, dict):
                verify_target = str(verify_touch.get("target", "")).strip()
                verify_kind = str(verify_touch.get("kind", "")).strip()
                if verify_kind:
                    role_split.setdefault("check_kind_if_any", verify_kind)
                if verify_target:
                    role_split.setdefault("check_target_if_any", verify_target)
            if role_split:
                role_split["ordinary_operations_are_not_skills"] = True
                projected_lighting["role_split_if_any"] = role_split
            projected_lighting["ordinary_operations_are_not_skills"] = True
        excerpt["layer_composition"] = compact_layer
    return excerpt


def _report_skill_lighting(report: dict | None) -> dict | None:
    if not isinstance(report, dict):
        return None
    lighting = report.get("_internal_skill_lighting_surface")
    if isinstance(lighting, dict):
        return lighting
    lighting = report.get("skill_lighting_surface")
    if isinstance(lighting, dict):
        return lighting
    return None


def _problem_facing_skill_list(values: object, *, limit: int = 8) -> list[str]:
    combo = _normalized_skill_list(values, limit=limit)
    return [skill for skill in combo if skill not in NON_PROBLEM_FACING_SKILLS]


def _report_skill_frontload_snapshot(
    report: dict | None,
) -> tuple[str, list[str], dict]:
    if not isinstance(report, dict):
        return "", [], {}
    lighting = _report_skill_lighting(report)
    if not isinstance(lighting, dict):
        layer = report.get("layer_composition")
        if isinstance(layer, dict):
            layer_lighting = layer.get("lighting_if_any")
            if isinstance(layer_lighting, dict):
                lighting = layer_lighting
    if not isinstance(lighting, dict):
        lighting = {}

    winning_skill = ""
    active_combo: list[str] = []
    bridge = report.get("skill_authority_bridge")
    if isinstance(bridge, dict):
        winning_skill = canonicalize_skill_token(
            bridge.get("winning_skill_if_any")
            or bridge.get("executable_owner_skill_if_any")
        )
        active_combo = _normalized_skill_list(
            bridge.get("active_skill_combo_if_any"),
            limit=8,
        )
    if not active_combo:
        layer = report.get("layer_composition")
        if isinstance(layer, dict):
            active_combo = _normalized_skill_list(
                layer.get("active_skill_combo_if_any"),
                limit=8,
            )
            if not winning_skill:
                winning_skill = canonicalize_skill_token(
                    layer.get("leading_skill_if_any")
                )
    if not active_combo:
        contract = report.get("discipline_contract")
        if isinstance(contract, dict):
            active_combo = _normalized_skill_list(
                contract.get("active_skill_combo_if_any"),
                limit=8,
            )
            if not winning_skill:
                authorized = project_bound_program_shape(contract.get("authorized_bite"))
                if isinstance(authorized, dict):
                    winning_skill = canonicalize_skill_token(
                        authorized.get("owner_skill_if_any")
                    )
    if not active_combo:
        active_combo = _normalized_skill_list(
            lighting.get("candidate_skills_if_any"),
            limit=8,
        )
    if not winning_skill and active_combo:
        winning_skill = active_combo[0]
    return winning_skill, active_combo, dict(lighting)


def _report_owned_layer_frontload_refusal(
    report: dict | None,
    candidate_program: dict | None,
    *,
    state: dict | None,
    context: str,
    winning_skill: str = "",
) -> str:
    if not isinstance(report, dict) or not isinstance(state, dict):
        return ""
    program = project_bound_program_shape(candidate_program)
    if not isinstance(program, dict) or not has_explicit_skill_ownership(program):
        return ""
    candidate_owner = canonicalize_skill_token(program.get("owner_skill_if_any"))
    candidate_combo = extract_explicit_skill_combo(program)
    if not candidate_combo:
        return ""

    if (
        program_is_direct_closure_candidate(program, state)
        and candidate_owner in READOUT_LIKE_SKILLS
    ):
        return ""

    expected_winner, expected_combo, lighting = _report_skill_frontload_snapshot(report)
    if winning_skill:
        expected_winner = canonicalize_skill_token(winning_skill) or expected_winner
    candidate_problem = _problem_facing_skill_list(candidate_combo, limit=8)
    expected_problem = _problem_facing_skill_list(expected_combo, limit=8)
    needs_multi_skill_frontload = len(candidate_problem) >= 2 or len(expected_problem) >= 2

    competition = report.get("skill_competition")
    if isinstance(competition, dict):
        competition_winner = canonicalize_skill_token(
            competition.get("winning_skill_if_any")
            or competition.get("winning_control_skill_if_any")
        )
        competition_problem_skills: list[str] = []
        raw_candidates = competition.get("candidates")
        if isinstance(raw_candidates, list):
            for candidate in raw_candidates:
                if not isinstance(candidate, dict):
                    continue
                skill_name = canonicalize_skill_token(candidate.get("skill"))
                if (
                    skill_name
                    and skill_name not in NON_PROBLEM_FACING_SKILLS
                    and skill_name not in competition_problem_skills
                ):
                    competition_problem_skills.append(skill_name)
        if len(competition_problem_skills) >= 2 and not competition_winner:
            return (
                f"{context} refused: current-layer skill competition never settled "
                "a first takeover before ownership was declared"
            )

    if needs_multi_skill_frontload:
        lit_candidates = _normalized_skill_list(
            lighting.get("candidate_skills_if_any"),
            limit=8,
        )
        lit_problem = _problem_facing_skill_list(lit_candidates, limit=8)
        if len(lit_problem) < 2:
            return (
                f"{context} refused: no multi-skill candidate field was explicitly lit "
                "before ownership was declared"
            )
        role_split = lighting.get("role_split_if_any")
        if not isinstance(role_split, dict):
            return (
                f"{context} refused: current-layer role split never became explicit "
                "before ownership was declared"
            )
        role_primary = canonicalize_skill_token(role_split.get("primary_skill_if_any"))
        role_supporting = _normalized_skill_list(
            role_split.get("supporting_skills_if_any"),
            limit=4,
        )
        role_check_kind = str(role_split.get("check_kind_if_any", "")).strip()
        role_check_target = str(role_split.get("check_target_if_any", "")).strip()
        verify_touch = lighting.get("verify_touch_if_any")
        verify_kind = ""
        verify_target = ""
        if isinstance(verify_touch, dict):
            verify_kind = str(verify_touch.get("kind", "")).strip()
            verify_target = str(verify_touch.get("target", "")).strip()
        if not role_primary:
            return (
                f"{context} refused: current-layer first-takeover skill was never "
                "explicitly lit before ownership was declared"
            )
        if not role_supporting:
            return (
                f"{context} refused: supporting skills were only inferred after "
                "ownership was declared"
            )
        if not (role_check_kind and role_check_target) and not (
            verify_kind and verify_target
        ):
            return (
                f"{context} refused: current-layer verification touch never became "
                "explicit before ownership was declared"
            )

    if len(expected_problem) >= 2 and len(candidate_problem) < 2:
        return (
            f"{context} refused: candidate local bite still was not owned by a real "
            "problem-facing skill combination"
        )
    if len(expected_problem) >= 2 and len(candidate_problem) >= 2:
        overlap = [skill for skill in candidate_problem if skill in expected_problem]
        if len(overlap) < 2:
            return (
                f"{context} refused: candidate local bite drifted away from the already "
                "lit current-layer skill combination"
            )
    if (
        expected_winner
        and candidate_owner
        and candidate_owner != expected_winner
        and len(candidate_problem) >= 2
        and expected_winner not in candidate_combo
    ):
        return (
            f"{context} refused: candidate local bite dropped the current-layer first-"
            f"takeover skill `{expected_winner}` from the owned combination"
        )
    return ""


def _explicit_layer_frontload_refusal(
    layer: dict | None,
    *,
    context: str,
    allow_direct_closure: bool = False,
) -> str:
    if not isinstance(layer, dict):
        return f"{context} refused: explicit layer composition never materialized"
    authorized_bite = project_bound_program_shape(layer.get("authorized_bite"))
    combo = _normalized_skill_list(layer.get("active_skill_combo_if_any"), limit=8)
    problem_facing = _problem_facing_skill_list(combo, limit=8)
    if len(combo) < 2:
        return (
            f"{context} refused: active current-layer skill combo never became a real "
            "combination"
        )
    if not problem_facing and not allow_direct_closure:
        return (
            f"{context} refused: current-layer combo never left control/readout-only settling"
        )
    lighting = layer.get("lighting_if_any")
    if not isinstance(lighting, dict):
        lighting = {}
    lit_candidates = _normalized_skill_list(lighting.get("candidate_skills_if_any"), limit=8)
    lit_problem = _problem_facing_skill_list(lit_candidates, limit=8)
    role_split = lighting.get("role_split_if_any")
    if not isinstance(role_split, dict):
        role_split = {}
    role_supporting = _normalized_skill_list(
        role_split.get("supporting_skills_if_any"),
        limit=4,
    )
    role_check_kind = str(role_split.get("check_kind_if_any", "")).strip()
    role_check_target = str(role_split.get("check_target_if_any", "")).strip()
    verify_touch = lighting.get("verify_touch_if_any")
    verify_kind = ""
    verify_target = ""
    if isinstance(verify_touch, dict):
        verify_kind = str(verify_touch.get("kind", "")).strip()
        verify_target = str(verify_touch.get("target", "")).strip()
    if len(problem_facing) >= 2 and len(lit_problem) < 2:
        return (
            f"{context} refused: reopened layer never re-lit a multi-skill candidate field"
        )
    if len(problem_facing) >= 2 and not role_supporting:
        return (
            f"{context} refused: reopened layer never exposed supporting skills before continuing"
        )
    if (
        len(problem_facing) >= 2
        and not (role_check_kind and role_check_target)
        and not (verify_kind and verify_target)
    ):
        return (
            f"{context} refused: reopened layer never exposed a concrete verification touch"
        )
    if not isinstance(authorized_bite, dict) or not has_explicit_skill_ownership(authorized_bite):
        return (
            f"{context} refused: explicit layer composition lost owned authorized bite metadata"
        )
    return ""


def read_skill_authority_program(
    report: dict,
    *,
    require_same_carrier: bool,
) -> tuple[str, list[str], dict | None, bool]:
    bridge = report.get("skill_authority_bridge")
    if not isinstance(bridge, dict):
        return "", [], None, False
    if require_same_carrier and bridge.get("same_carrier_only") is not True:
        return "", [], None, False
    bridge_winner = canonicalize_skill_token(bridge.get("winning_skill_if_any"))
    bridge_executable_owner = canonicalize_skill_token(
        bridge.get("executable_owner_skill_if_any")
    )
    if (
        bridge_winner
        and bridge_executable_owner
        and bridge_winner != bridge_executable_owner
        and bridge_winner in PUBLIC_LIT_SKILLS
        and bridge_executable_owner in PUBLIC_LIT_SKILLS
    ):
        winning_skill = bridge_winner
    else:
        winning_skill = str(
            bridge.get("executable_owner_skill_if_any")
            or bridge.get("winning_skill_if_any", "")
        ).strip()
    touch = project_bound_program_shape(bridge.get("executable_local_touch_if_any"))
    raw_combo = touch.get("owner_skill_combo_if_any") if isinstance(touch, dict) else None
    if not isinstance(raw_combo, list):
        raw_combo = bridge.get("active_skill_combo_if_any")
    skill_combo = _normalized_skill_list(raw_combo)
    if not skill_combo:
        skill_combo = _merged_skill_lists(
            [winning_skill] if winning_skill else [],
            bridge.get("supporting_skills_if_any"),
            limit=6,
        )
    if winning_skill and winning_skill not in skill_combo:
        skill_combo = [winning_skill] + [value for value in skill_combo if value != winning_skill]
    if isinstance(touch, dict) and skill_combo:
        touch = (
            attach_program_owner_metadata(
                touch,
                owner_skill=winning_skill,
                owner_combo=skill_combo,
            )
            or touch
        )
    return winning_skill, skill_combo[:6], touch, bridge.get("silence_after_contact") is True


def infer_program_ownership_from_report(
    state: dict,
    path: Path,
    candidate_program: dict | None,
) -> tuple[str, list[str], dict]:
    payload = project_bound_program_shape(candidate_program)
    if not isinstance(payload, dict):
        return "", [], {}

    report = build_report(state, path)
    current_handoff_live = isinstance(state.get("carrier_handoff_if_any"), dict)
    require_same_carrier_modes = [not current_handoff_live]
    if require_same_carrier_modes[0] is not False:
        require_same_carrier_modes.append(False)

    for require_same_carrier in require_same_carrier_modes:
        winning_skill, skill_combo, touch, _ = read_skill_authority_program(
            report,
            require_same_carrier=require_same_carrier,
        )
        if (
            isinstance(touch, dict)
            and has_explicit_skill_ownership(touch)
            and not programs_conflict(payload, touch)
        ):
            enriched = attach_program_owner_metadata(
                payload,
                owner_skill=str(touch.get("owner_skill_if_any", "")).strip() or winning_skill,
                owner_combo=extract_explicit_skill_combo(touch) or skill_combo,
            )
            if isinstance(enriched, dict):
                return (
                    str(enriched.get("owner_skill_if_any", "")).strip(),
                    extract_explicit_skill_combo(enriched),
                    report,
                )

    for source in [
        state.get("landed_next_touch_if_any"),
        ((report.get("discipline_contract") or {}).get("authorized_bite")),
        ((report.get("layer_composition") or {}).get("authorized_bite")),
    ]:
        touch = project_bound_program_shape(source)
        if (
            isinstance(touch, dict)
            and has_explicit_skill_ownership(touch)
            and not programs_conflict(payload, touch)
        ):
            enriched = attach_program_owner_metadata(
                payload,
                owner_skill=str(touch.get("owner_skill_if_any", "")).strip(),
                owner_combo=extract_explicit_skill_combo(touch),
            )
            if isinstance(enriched, dict):
                return (
                    str(enriched.get("owner_skill_if_any", "")).strip(),
                    extract_explicit_skill_combo(enriched),
                    report,
                )

    return "", [], report


def read_promoted_skill(report: dict) -> str:
    inhibition = report.get("skill_inhibition")
    if not isinstance(inhibition, dict):
        return ""
    return str(inhibition.get("promoted_skill_if_any", "")).strip()


def promoted_skill_gate_refusal(
    report: dict,
    *,
    winning_skill: str = "",
    foreground_program: dict | None = None,
) -> str:
    if not isinstance(report, dict):
        return ""
    bridge = report.get("skill_authority_bridge")
    if isinstance(bridge, dict):
        bridge_touch = project_bound_program_shape(bridge.get("executable_local_touch_if_any"))
        if (
            isinstance(bridge_touch, dict)
            and str(bridge_touch.get("kind", "")).strip() == "读出"
            and str(winning_skill or "").strip() in {"精确封口", "读出"}
        ):
            return ""
    promoted_skill = read_promoted_skill(report)
    if not promoted_skill:
        return ""
    if promoted_skill == "精确封口" and str(winning_skill or "").strip() in {"精确封口", "读出"}:
        return ""
    active_combo: list[str] = []
    explicit_layer = report.get("layer_composition")
    explicit_leading = ""
    explicit_event_owned = False
    if isinstance(explicit_layer, dict):
        explicit_leading = str(explicit_layer.get("leading_skill_if_any", "")).strip()
        explicit_event_owned = explicit_layer.get("event_owned") is True
    if isinstance(bridge, dict):
        raw_combo = bridge.get("active_skill_combo_if_any")
        if isinstance(raw_combo, list):
            active_combo = [str(value).strip() for value in raw_combo if str(value).strip()][:6]
    owned_by = str(winning_skill or "").strip()
    foreground_owner = ""
    foreground_combo: list[str] = []
    contract = report.get("discipline_contract")
    contract_authorized_owner = ""
    contract_surface = ""
    if isinstance(contract, dict):
        contract_surface = str(contract.get("surface", "")).strip()
        contract_authorized = project_bound_program_shape(contract.get("authorized_bite"))
        if isinstance(contract_authorized, dict):
            contract_authorized_owner = str(
                contract_authorized.get("owner_skill_if_any", "")
            ).strip()
    if isinstance(foreground_program, dict):
        foreground_owner = str(foreground_program.get("owner_skill_if_any", "")).strip()
        raw_foreground_combo = foreground_program.get("owner_skill_combo_if_any")
        if isinstance(raw_foreground_combo, list):
            foreground_combo = [
                str(value).strip() for value in raw_foreground_combo if str(value).strip()
            ][:6]
    if (
        contract_surface == "takeover_recomposition"
        and foreground_owner
        and contract_authorized_owner
        and foreground_owner == contract_authorized_owner
    ):
        return ""
    if (
        explicit_event_owned
        and foreground_owner
        and explicit_leading
        and foreground_owner == explicit_leading
    ):
        return ""
    control_promoted_skill = promoted_skill in {
        "反问",
        "抓本质",
        "更薄载体重选",
        "最终控制者",
        "元认知",
        "监督",
        "中枢控制",
        "后脑守卫",
        "奖惩塑形",
    }
    if not owned_by:
        if control_promoted_skill and (foreground_owner or foreground_combo):
            return ""
        if promoted_skill in active_combo:
            return ""
        return (
            "promoted skill gate refused: current layer promotes "
            f"{promoted_skill} but the foreground touch has no explicit skill owner"
        )
    if promoted_skill in active_combo:
        return ""
    if owned_by != promoted_skill:
        return (
            "promoted skill gate refused: current layer promotes "
            f"{promoted_skill} but the foreground touch is owned by {owned_by}"
        )
    return ""


def fresh_blind_same_carrier_first_entry(
    program: dict | None,
    *,
    state: dict | None = None,
) -> bool:
    if not isinstance(program, dict) or not isinstance(state, dict):
        return False
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return False
    if str(bootstrap_context.get("mode", "")).strip() != "fresh_blind_project_skills_on":
        return False
    if isinstance(state.get("bound_program"), dict):
        return False
    if isinstance(state.get("carrier_handoff_if_any"), dict):
        return False
    if isinstance(state.get("layer_composition_if_any"), dict):
        return False
    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    program_target = str(program.get("target", "")).strip()
    program_kind = str(program.get("kind", "")).strip()
    current_object = str(state.get("current_object", "")).strip()
    current_seam = str(state.get("current_seam", "")).strip()
    current_debt = str(state.get("current_debt", "")).strip()
    if not asked_medium or not program_target or program_target == asked_medium:
        return False
    if program_kind not in {"write", "check", "见证"}:
        return False
    if program_target not in {current_object, current_seam, current_debt}:
        return False
    if program_kind == "write":
        current_layer_object = str(program.get("current_layer_object_if_any", "")).strip()
        controlled_object = str(program.get("controlled_object_if_any", "")).strip()
        if current_layer_object and controlled_object and current_layer_object == controlled_object:
            return False
        if current_seam and current_object and current_seam != current_object:
            if program_target == current_object:
                return False
            if controlled_object and controlled_object == current_object:
                return False
    if is_generic_runtime_operation(program) or program_has_meta_narration(program):
        return False
    if program_is_direct_closure_candidate(program, state):
        return False
    return True


def first_entry_读出_owner_refusal(
    program: dict | None,
    report: dict,
    *,
    state: dict | None = None,
    winning_skill: str = "",
) -> str:
    if not isinstance(program, dict) or not isinstance(report, dict) or not isinstance(state, dict):
        return ""
    if not fresh_blind_same_carrier_first_entry(program, state=state):
        return ""

    owner = str(program.get("owner_skill_if_any", "")).strip() or str(winning_skill or "").strip()
    combo = extract_explicit_skill_combo(program)
    active_combo = (
        [str(value).strip() for value in combo if str(value).strip()]
        if combo
        else []
    )
    读出_like = {
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
    }
    if owner not in 读出_like:
        return ""
    if not active_combo:
        active_combo = [owner]
    non_读出_partners = [
        skill for skill in active_combo if skill and skill not in 读出_like
    ]
    if non_读出_partners:
        return (
            "fresh blind first entry refused: the first same-carrier bite is still owned by "
            f"{owner}, so supporting partners {', '.join(non_读出_partners[:3])} never truly took control"
        )
    return (
        "fresh blind first entry refused: 读出-like ownership tried to take the first same-carrier bite "
        "before a problem-facing combination had actually taken control"
    )


def first_entry_asked_medium_short_circuit_refusal(
    program: dict | None,
    report: dict,
    *,
    state: dict | None = None,
    winning_skill: str = "",
) -> str:
    if not isinstance(program, dict) or not isinstance(report, dict) or not isinstance(state, dict):
        return ""
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return ""
    if str(bootstrap_context.get("mode", "")).strip() != "fresh_blind_project_skills_on":
        return ""
    if isinstance(state.get("bound_program"), dict):
        return ""
    if isinstance(state.get("carrier_handoff_if_any"), dict):
        return ""
    if isinstance(state.get("layer_composition_if_any"), dict):
        return ""

    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    target = str(program.get("target", "")).strip()
    owner = str(program.get("owner_skill_if_any", "")).strip() or str(winning_skill or "").strip()
    if not asked_medium or target != asked_medium:
        return ""
    if not fresh_blind_problem_first_touch_pending(state, asked_medium=asked_medium):
        return ""
    if owner not in {
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
    } and str(program.get("kind", "")).strip() in {"check", "见证"}:
        return (
            "fresh blind first entry refused: problem-facing probe/check tried to bind directly on the asked medium "
            "before the first live object-side layer had been honestly taken over"
        )
    if owner not in {
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
    }:
        return ""

    return (
        "fresh blind first entry refused: asked-medium 读出 tried to bind before the first live object-side layer "
        "had been honestly taken over"
    )


def first_recoil_refusal(
    program: dict | None,
    report: dict,
    *,
    state: dict | None = None,
    winning_skill: str = "",
) -> str:
    if not isinstance(program, dict) or not isinstance(report, dict):
        return ""
    interlayer_bridge = read_interlayer_discharge_bridge(report)
    if isinstance(interlayer_bridge, dict):
        spend_first_program = interlayer_bridge.get("spend_first_program")
        if isinstance(spend_first_program, dict) and not programs_conflict(program, spend_first_program):
            return ""

    inhibition_state = report.get("inhibition_state")
    promoted_move = inhibition_state.get("promoted_move") if isinstance(inhibition_state, dict) else None
    gate_binding = report.get("control_bridge", {}).get("gate_binding") if isinstance(report.get("control_bridge"), dict) else None
    if not isinstance(promoted_move, dict) and not isinstance(gate_binding, dict):
        return ""

    program_target = str(program.get("target", "")).strip()
    program_kind = str(program.get("kind", "")).strip()
    discipline_contract = report.get("discipline_contract")
    if isinstance(discipline_contract, dict):
        contract_surface = str(discipline_contract.get("surface", "")).strip()
        contract_bite = project_bound_program_shape(discipline_contract.get("authorized_bite"))
        if (
            contract_surface in {"takeover_recomposition", "bound_program"}
            and isinstance(contract_bite, dict)
            and not programs_conflict(program, contract_bite)
        ):
            return ""
    asked_medium = (
        str(state.get("asked_medium_surface", "")).strip()
        if isinstance(state, dict)
        else ""
    )
    bootstrap_same_carrier_first_entry = fresh_blind_same_carrier_first_entry(
        program,
        state=state,
    )
    promoted_skill = ""
    skill_inhibition = report.get("skill_inhibition")
    if isinstance(skill_inhibition, dict):
        promoted_skill = str(skill_inhibition.get("promoted_skill_if_any", "")).strip()
    promoted_target = ""
    preferred_kinds: list[str] = []
    if isinstance(promoted_move, dict):
        promoted_target = str(promoted_move.get("touch_target", "")).strip()
        raw_kinds = promoted_move.get("preferred_kinds")
        if isinstance(raw_kinds, list):
            preferred_kinds = [str(value).strip() for value in raw_kinds if str(value).strip()]

    skill_bridge = report.get("skill_authority_bridge")
    skill_bridge_touch = None
    same_carrier_composed_authority = False
    if isinstance(skill_bridge, dict):
        skill_bridge_touch = project_bound_program_shape(
            skill_bridge.get("executable_local_touch_if_any")
        )
        same_carrier_composed_authority = (
            skill_bridge.get("same_carrier_only") is True
            and isinstance(skill_bridge_touch, dict)
            and str(skill_bridge_touch.get("target", "")).strip() == program_target
            and str(skill_bridge_touch.get("kind", "")).strip() == program_kind
            and str(skill_bridge.get("winning_skill_if_any", "")).strip() == str(winning_skill or "").strip()
            and isinstance(report.get("skill_field"), dict)
            and report.get("skill_field", {}).get("composition_ready") is True
            and isinstance(report.get("closure_nucleus"), dict)
            and report.get("closure_nucleus", {}).get("读出_deferred_by_layerwise_pressure") is True
        )

    layer_composition = report.get("layer_composition")
    handoff_owned_structural_spend = False
    event_owned_same_carrier_step = False
    if isinstance(layer_composition, dict):
        layer_surface = str(layer_composition.get("surface", "")).strip()
        controlled_object = str(layer_composition.get("controlled_object", "")).strip()
        must_spend_handoff = layer_composition.get("must_spend_handoff") is True
        event_owned = layer_composition.get("event_owned") is True
        layer_leading_skill = str(layer_composition.get("leading_skill_if_any", "")).strip()
        layer_combo = layer_composition.get("active_skill_combo_if_any")
        combo_has_winner = (
            isinstance(layer_combo, list)
            and str(winning_skill or "").strip()
            and str(winning_skill or "").strip() in [str(value).strip() for value in layer_combo]
        )
        handoff_owned_structural_spend = (
            layer_surface == "carrier_handoff"
            and must_spend_handoff
            and controlled_object
            and controlled_object == program_target
            and program_kind in {"write", "check", "见证"}
            and (
                layer_leading_skill == str(winning_skill or "").strip()
                or combo_has_winner
            )
        )
        event_owned_same_carrier_step = (
            event_owned
            and layer_surface in {"takeover_recomposition", "bound_program"}
            and controlled_object
            and controlled_object == program_target
            and program_kind in {"write", "check", "见证", "读出"}
            and (
                layer_leading_skill == str(winning_skill or "").strip()
                or combo_has_winner
                or (
                    isinstance(layer_combo, list)
                    and promoted_skill
                    and promoted_skill in [str(value).strip() for value in layer_combo]
                )
            )
        )

    if isinstance(gate_binding, dict):
        gate_target = str(gate_binding.get("source_target", "")).strip()
        if gate_target and program_target and gate_target != program_target:
            return (
                "first recoil refused: current gate is still holding "
                f"{gate_target} but the foreground touch jumped to {program_target}"
            )

    if (winning_skill == "反问" or promoted_skill == "反问") and program_kind in {"check", "见证"}:
        return ""
    if (
        (winning_skill == "精确封口" or promoted_skill == "精确封口")
        and asked_medium
        and program_target == asked_medium
        and program_kind in {"write", "读出"}
    ):
        return ""
    if (
        asked_medium
        and program_target == asked_medium
        and promoted_target
        and "asked-medium closure" in promoted_target
        and program_kind in set(preferred_kinds or [])
    ):
        return ""
    if (
        same_carrier_composed_authority
        and asked_medium
        and promoted_target == asked_medium
    ):
        return ""
    if event_owned_same_carrier_step and asked_medium and promoted_target == asked_medium:
        return ""
    if handoff_owned_structural_spend and asked_medium and promoted_target == asked_medium:
        return ""
    if (
        bootstrap_same_carrier_first_entry
        and promoted_target
        and promoted_target == asked_medium
    ):
        return ""
    if (
        bootstrap_same_carrier_first_entry
        and promoted_target
        and is_meta_narration_text(promoted_target)
    ):
        return ""
    layer_arena = report.get("layer_arena")
    if not isinstance(layer_arena, dict):
        layer_arena = report.get("first_layer_arena")
    if bootstrap_same_carrier_first_entry and isinstance(layer_arena, dict):
        arena_touch = project_bound_program_shape(layer_arena.get("authorized_touch_if_any"))
        if (
            isinstance(arena_touch, dict)
            and not fresh_blind_same_carrier_first_entry(arena_touch, state=state)
        ):
            return ""
    if (
        isinstance(layer_arena, dict)
        and str((report.get("discipline_contract") or {}).get("surface", "")).strip()
        in {"fresh_blind_first_touch", "takeover_recomposition", "bound_program"}
    ):
        arena_touch = project_bound_program_shape(layer_arena.get("authorized_touch_if_any"))
        if isinstance(arena_touch, dict) and not programs_conflict(program, arena_touch):
            return ""
    if promoted_target and program_target and promoted_target != program_target:
        return (
            "first recoil refused: current promoted move still targets "
            f"{promoted_target} but the foreground touch jumped to {program_target}"
        )
    if preferred_kinds and program_kind and program_kind not in preferred_kinds:
        owner_text = f" under {winning_skill}" if winning_skill else ""
        return (
            "first recoil refused: current promoted move"
            f"{owner_text} prefers {', '.join(preferred_kinds)} but the foreground touch is {program_kind}"
        )
    return ""


def read_interlayer_discharge_bridge(report: dict) -> dict | None:
    bridge = report.get("interlayer_discharge_bridge")
    if not isinstance(bridge, dict):
        return None
    if str(bridge.get("mode", "")).strip() != "primitive_then_closure":
        return None

    spend_first = project_bound_program_shape(bridge.get("spend_first_program"))
    if spend_first is None:
        return None

    payload = {
        "mode": "primitive_then_closure",
        "reason": str(bridge.get("reason", "")).strip(),
        "spend_first_program": spend_first,
        "keep_closure_authority": bridge.get("keep_closure_authority") is True,
        "handoff_target": str(bridge.get("handoff_target", "")).strip(),
    }

    post_touch = project_bound_program_shape(bridge.get("post_closure_touch_if_any"))
    if post_touch is not None:
        payload["post_closure_touch_if_any"] = post_touch
    return payload


def programs_share_slot(left: dict | None, right: dict | None) -> bool:
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    return (
        str(left.get("kind", "")).strip() == str(right.get("kind", "")).strip()
        and str(left.get("target", "")).strip() == str(right.get("target", "")).strip()
    )


def programs_conflict(left: dict | None, right: dict | None) -> bool:
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    return not programs_share_slot(left, right)


def program_is_direct_closure_candidate(program: dict | None, state: dict) -> bool:
    if not isinstance(program, dict) or not isinstance(state, dict):
        return False
    kind = str(program.get("kind", "")).strip()
    target = _extract_markdown_artifact_hint(program.get("target", ""))
    operation = str(program.get("operation", "")).strip()
    step_outline = str(program.get("step_outline_if_any", "")).strip()
    object_transform = str(program.get("object_transform_if_any", "")).strip()
    success_signal = str(program.get("success_signal", "")).strip()
    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    if asked_medium and target == asked_medium and kind in {"write", "读出"}:
        return True
    closure_texts = [
        operation,
        step_outline,
        object_transform,
        success_signal,
    ]
    closure_hints = " ".join(
        " ".join(text.lower().split())
        for text in closure_texts
        if text
    )
    mentions_asked_medium = any(
        _extract_markdown_artifact_hint(text) == asked_medium
        for text in closure_texts
        if asked_medium and text
    )
    closure_markers = (
        "materialize",
        "close onto",
        "close into",
        "seal",
        "asked_medium_is_exact_and_executable",
        "runtime-owned closure",
        "exact closure",
        "final answer",
        "canonical solve-markdown",
        "封口",
    )
    if (
        asked_medium
        and kind in {"write", "读出"}
        and mentions_asked_medium
        and any(marker in closure_hints for marker in closure_markers)
    ):
        return True
    return operation == "materialize_exact_asked_medium_读出"


def primitive_takeover_recomposition_refusal(
    program: dict | None,
    report: dict,
    *,
    state: dict,
) -> str:
    if not isinstance(program, dict) or not isinstance(report, dict) or not isinstance(state, dict):
        return ""
    gate = state.get("primitive_takeover_gate_if_any")
    if not isinstance(gate, dict):
        return ""
    if str(gate.get("trigger", "")).strip() != "same_carrier_landing":
        return ""
    if not program_is_direct_closure_candidate(program, state):
        return ""
    live_layer = state.get("layer_composition_if_any")
    if isinstance(live_layer, dict) and str(live_layer.get("surface", "")).strip() == "takeover_recomposition":
        live_authorized = project_bound_program_shape(live_layer.get("authorized_bite"))
        if isinstance(live_authorized, dict) and not program_is_direct_closure_candidate(
            live_authorized,
            state,
        ):
            return (
                "primitive takeover gate refused: the current layer just changed, so one freshly recomposed "
                "current-layer skill combination must bind before asked-medium closure resumes"
            )
    contract = report.get("discipline_contract")
    if not isinstance(contract, dict):
        return ""
    if str(contract.get("surface", "")).strip() != "takeover_recomposition":
        return ""
    authorized = project_bound_program_shape(contract.get("authorized_bite"))
    if isinstance(authorized, dict) and not program_is_direct_closure_candidate(authorized, state):
        return (
            "primitive takeover gate refused: the current layer just changed, so one freshly recomposed "
            "current-layer skill combination must bind before asked-medium closure resumes"
        )
    return ""


def unbound_probe_refusal(program: dict | None, report: dict) -> str:
    if not isinstance(program, dict) or not isinstance(report, dict):
        return ""
    probe_discipline = report.get("probe_discipline")
    if not isinstance(probe_discipline, dict):
        return ""
    if probe_discipline.get("probe_must_bind") is not True:
        return ""
    if str(probe_discipline.get("active_skill_hypothesis", "")).strip():
        return ""
    active_hypotheses = probe_discipline.get("active_skill_hypotheses")
    if isinstance(active_hypotheses, list) and any(str(value).strip() for value in active_hypotheses):
        return ""
    if probe_discipline.get("unbound_probe_is_drift") is not True:
        return ""
    if not program_counts_as_probe(program, report):
        return ""
    return (
        "probe discipline refused: current probe-like bite is not bound to a live skill hypothesis"
    )


def probe_overreach_refusal(
    program: dict | None,
    report: dict,
    *,
    state: dict | None = None,
    winning_skill: str = "",
) -> str:
    if not isinstance(program, dict) or not isinstance(report, dict):
        return ""
    if not program_counts_as_probe(program, report):
        return ""
    if fresh_blind_same_carrier_first_entry(program, state=state):
        program_owner = str(program.get("owner_skill_if_any", "")).strip()
        if winning_skill and program_owner and winning_skill == program_owner:
            return ""
    discipline_contract = report.get("discipline_contract")
    if isinstance(discipline_contract, dict):
        contract_surface = str(discipline_contract.get("surface", "")).strip()
        contract_bite = project_bound_program_shape(discipline_contract.get("authorized_bite"))
        if (
            contract_surface in {"takeover_recomposition", "bound_program"}
            and isinstance(contract_bite, dict)
            and not programs_conflict(program, contract_bite)
        ):
            return ""
    probe_discipline = report.get("probe_discipline")
    if not isinstance(probe_discipline, dict):
        return ""
    active_hypothesis = str(probe_discipline.get("active_skill_hypothesis", "")).strip()
    active_hypotheses = probe_discipline.get("active_skill_hypotheses")
    plural_hypotheses = (
        [str(value).strip() for value in active_hypotheses if str(value).strip()]
        if isinstance(active_hypotheses, list)
        else []
    )
    if not active_hypothesis and not plural_hypotheses:
        return ""
    if winning_skill == "反问":
        return ""
    if active_hypothesis in {"反问"} or "反问" in plural_hypotheses:
        return ""
    skill_bridge = report.get("skill_authority_bridge")
    if isinstance(skill_bridge, dict):
        bridge_touch = project_bound_program_shape(
            skill_bridge.get("executable_local_touch_if_any")
        )
        if (
            skill_bridge.get("same_carrier_only") is True
            and isinstance(bridge_touch, dict)
            and programs_share_slot(program, bridge_touch)
            and isinstance(report.get("skill_field"), dict)
            and report.get("skill_field", {}).get("composition_ready") is True
            and winning_skill
            and winning_skill == str(skill_bridge.get("winning_skill_if_any", "")).strip()
            and (winning_skill == active_hypothesis or winning_skill in plural_hypotheses)
        ):
            return ""
    layer_composition = report.get("layer_composition")
    if isinstance(layer_composition, dict):
        layer_surface = str(layer_composition.get("surface", "")).strip()
        controlled_object = str(layer_composition.get("controlled_object", "")).strip()
        layer_leading_skill = str(layer_composition.get("leading_skill_if_any", "")).strip()
        layer_combo = layer_composition.get("active_skill_combo_if_any")
        combo_has_winner = (
            isinstance(layer_combo, list)
            and winning_skill
            and winning_skill in [str(value).strip() for value in layer_combo]
        )
        if (
            layer_surface == "carrier_handoff"
            and layer_composition.get("must_spend_handoff") is True
            and controlled_object
            and controlled_object == str(program.get("target", "")).strip()
            and winning_skill
            and (
                winning_skill == active_hypothesis
                or winning_skill in plural_hypotheses
            )
            and (
                layer_leading_skill == winning_skill
                or combo_has_winner
            )
        ):
            return ""
        if (
            layer_composition.get("event_owned") is True
            and layer_surface in {"takeover_recomposition", "bound_program"}
            and controlled_object
            and controlled_object == str(program.get("target", "")).strip()
            and active_hypothesis
            and (
                layer_leading_skill == active_hypothesis
                or (
                    isinstance(layer_combo, list)
                    and active_hypothesis in [str(value).strip() for value in layer_combo]
                )
            )
        ):
            return ""
    skill_competition = report.get("skill_competition")
    if isinstance(skill_competition, dict):
        for candidate in skill_competition.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            skill = str(candidate.get("skill", "")).strip()
            if skill and skill == active_hypothesis and skill not in {"反问"}:
                return (
                    "probe discipline refused: probe-like bite is trying to lead before the live skill "
                    f"hypothesis {active_hypothesis} is compressed into a thinner executable carrier"
                )
    return ""


def program_counts_as_probe(program: dict | None, report: dict) -> bool:
    if not isinstance(program, dict) or not isinstance(report, dict):
        return False
    probe_discipline = report.get("probe_discipline")
    if not isinstance(probe_discipline, dict):
        return False
    kind = str(program.get("kind", "")).strip()
    allowed_probe_kinds = probe_discipline.get("allowed_probe_kinds")
    if isinstance(allowed_probe_kinds, list) and kind in {
        str(value).strip() for value in allowed_probe_kinds
    }:
        return True
    primitive_field = report.get("primitive_field")
    if isinstance(primitive_field, dict):
        active_primitives = primitive_field.get("active_primitives")
        if isinstance(active_primitives, list):
            for value in active_primitives:
                if primitive_is_probe_like(value):
                    return True
    return False


def derive_local_agenda_for_program(
    state: dict,
    program: dict,
    *,
    winning_skill: str = "",
    report: dict | None = None,
) -> dict:
    program_target = str(program.get("target", "")).strip()
    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    current_seam = str(state.get("current_seam", "")).strip()
    interlayer_bridge = report.get("interlayer_discharge_bridge") if isinstance(report, dict) else None
    closure_retained_after_structural_spend = bool(
        winning_skill == "精确封口"
        and isinstance(interlayer_bridge, dict)
        and interlayer_bridge.get("keep_closure_authority") is True
        and program_target
        and program_target != asked_medium
    )

    focus = "carrier"
    if closure_retained_after_structural_spend:
        post_touch = (
            project_bound_program_shape(interlayer_bridge.get("post_closure_touch_if_any"))
            if isinstance(interlayer_bridge, dict)
            else None
        )
        focus = "asked_medium"
        reason = (
            "one thinner-layer structural bite is being spent under closure authority; "
            "asked-medium closure should stay foregrounded until it can retake the slot"
        )
        return {
            "focus": focus,
            "touch_target": asked_medium or program_target,
            "reason": reason,
            "preferred_kinds": [
                str(post_touch.get("kind", "")).strip() or "读出"
            ] if isinstance(post_touch, dict) else ["读出", "write"],
        }
    if winning_skill == "精确封口" or program_target == asked_medium:
        focus = "asked_medium"
    elif winning_skill == "反问":
        agenda = report.get("self_check_agenda") if isinstance(report, dict) else None
        agenda_focus = str(agenda.get("focus", "")).strip() if isinstance(agenda, dict) else ""
        if agenda_focus in {"seam", "rival", "asked_medium"}:
            focus = agenda_focus
        elif program_target and program_target == current_seam:
            focus = "seam"
        else:
            focus = "carrier"
    elif str(program.get("kind", "")).strip() in {"check", "见证"} and program_target == current_seam:
        focus = "seam"

    reason = "a concrete local bind has been purchased and should stay locally owned until it changes again"
    if winning_skill == "精确封口":
        reason = "exact closure now owns one local touch and should keep foreground authority until asked-medium contact changes"
    elif winning_skill == "反问":
        reason = "one hostile falsifier now owns the slot and should keep local authority until it tears or lands"

    return {
        "focus": focus,
        "touch_target": program_target,
        "reason": reason,
    }


def maybe_cool_post_touch_surfaces(
    state: dict,
    program: dict,
    *,
    winning_skill: str = "",
    silence_after_contact: bool = False,
) -> None:
    if silence_after_contact is not True:
        return
    program_target = str(program.get("target", "")).strip()
    program_kind = str(program.get("kind", "")).strip()
    asked_medium = str(state.get("asked_medium_surface", "")).strip()

    if winning_skill == "精确封口":
        if asked_medium and program_target == asked_medium:
            state["primitive_competition_if_any"] = None
            state["secondary_rival_if_any"] = None
            return
    # Keep plural live pressure readable after structural or hostile local contact.
    # Fresh state derivation can cool stale branches naturally; we avoid zeroing the
    # field here because that prematurely erases composition tension.
    if winning_skill == "反问" or program_kind in {"check", "见证"}:
        return

    if program_target and program_target == str(state.get("current_object", "")).strip():
        return


def refresh_primitive_field_for_current_layer(
    state: dict,
    *,
    agenda_override: dict | None = None,
    handoff_override: dict | None = None,
    force: bool = False,
) -> None:
    if state.get("release_veto") is not True:
        return

    if primitive_competition_is_stale(
        state,
        agenda_override=agenda_override,
        handoff_override=handoff_override,
    ):
        state["primitive_competition_if_any"] = None

    stale_field = False
    if state.get("primitive_field_if_any") is not None:
        stale_field = primitive_field_is_stale(
            state,
            agenda_override=agenda_override,
            handoff_override=handoff_override,
        )
        if not force and not stale_field:
            return
        if stale_field:
            state["primitive_field_if_any"] = None

    candidate_primitive_field = derive_primitive_field_candidate(
        state,
        [],
        agenda_override=agenda_override,
        handoff_override=handoff_override,
    )
    if isinstance(candidate_primitive_field, dict):
        state["primitive_field_if_any"] = candidate_primitive_field


def require_core_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--current-object", "current_object"),
            ("--current-debt", "current_debt"),
            ("--next-bite", "next_bite"),
            ("--asked-medium-surface", "asked_medium_surface"),
            ("--revocation-handle", "revocation_handle"),
            ("--primary-slot", "primary_slot"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit(f"init requires core live-state fields: {', '.join(missing)}")


def require_bound_program_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--kind", "kind"),
            ("--target", "target"),
            ("--operation", "operation"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit(
            "bound program requires: " + ", ".join(missing)
        )


def require_gate_binding_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--source-focus", "source_focus"),
            ("--source-target", "source_target"),
            ("--demoted-continuation", "demoted_continuation"),
            ("--authority-until", "authority_until"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit("gate binding requires: " + ", ".join(missing))


def require_materialization_evidence_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--evidence-kind", "evidence_kind"),
            ("--evidence-location", "evidence_location"),
            ("--evidence-summary", "evidence_summary"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit(
            "materialization evidence requires: " + ", ".join(missing)
        )


def require_primitive_field_arguments(args: argparse.Namespace) -> None:
    missing = [
        option
        for option, attr in [
            ("--layer-object", "layer_object"),
            ("--why-now", "why_now"),
        ]
        if getattr(args, attr, None) in (None, "")
    ]
    if missing:
        raise SystemExit("primitive field requires: " + ", ".join(missing))
    active = getattr(args, "active_primitive", None) or []
    if not 1 <= len(active) <= 2:
        raise SystemExit("primitive field requires one or two --active-primitive values")
    invalid = [value for value in active if not is_allowed_primitive_token(value)]
    if invalid:
        raise SystemExit(
            "primitive field contains invalid primitive values: " + ", ".join(invalid)
        )


def can_clear_release_veto_without_program(state: dict) -> bool:
    output_status = state.get("output_status", {})
    evidence = state.get("materialization_evidence")
    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    if asked_medium:
        if not isinstance(evidence, dict) or evidence.get("skill_serialized") is not True:
            return False
    return (
        output_status.get("touched") is True
        and output_status.get("final_artifact_materialized") is True
        and output_status.get("cosmetic_only") is not True
        and output_status.get("contains_unsupported") is not True
        and output_status.get("contains_placeholder") is not True
        and isinstance(evidence, dict)
    )


def require_no_active_control_artifacts_for_release(state: dict) -> None:
    active_fields: list[str] = []
    for key in [
        "bound_program",
        "layer_composition_if_any",
        "gate_binding_if_any",
        "carrier_handoff_if_any",
        "primitive_field_if_any",
        "primitive_competition_if_any",
        "secondary_rival_if_any",
        "landed_next_touch_if_any",
        "primitive_takeover_gate_if_any",
    ]:
        if state.get(key) is not None:
            active_fields.append(key)

    if active_fields:
        raise SystemExit(
            "cannot clear release_veto while active control artifacts remain: "
            + ", ".join(active_fields)
        )


def require_program_or_materialized_output(state: dict, *, state_path: Path | None = None) -> None:
    require_no_active_control_artifacts_for_release(state)
    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    bound_program = project_bound_program_shape(state.get("bound_program"))
    if isinstance(bound_program, dict):
        if asked_medium and program_is_asked_medium_closure(bound_program, asked_medium=asked_medium):
            if state_path is None:
                raise SystemExit(
                    "cannot clear release_veto without a state_path when asked-medium "
                    "closure serialization must be verified"
                )
            require_asked_medium_skill_serialization(
                state,
                state_path=state_path,
                context="release refused",
            )
        return
    if can_clear_release_veto_without_program(state):
        if asked_medium:
            if state_path is None:
                raise SystemExit(
                    "cannot clear release_veto without a state_path when asked-medium "
                    "skill serialization must be verified"
                )
            require_asked_medium_skill_serialization(
                state,
                state_path=state_path,
                context="release refused",
            )
        return
    raise SystemExit(
        "cannot clear release_veto without a bound_program unless the asked medium "
        "has already been touched, the final artifact is materialized, and "
        "materialization evidence is present"
    )


def state_shaping_requires_runtime_spend(state: dict, path: Path) -> str:
    if state.get("release_veto") is not True:
        return ""
    if isinstance(state.get("bound_program"), dict):
        return ""

    report = build_report(state, path)
    probe = report.get("probe_discipline")
    contract = report.get("discipline_contract")
    skill_bridge = report.get("skill_authority_bridge")
    interlayer = report.get("interlayer_discharge_bridge")

    if isinstance(state.get("carrier_handoff_if_any"), dict):
        spend_first = (
            project_bound_program_shape(interlayer.get("spend_first_program"))
            if isinstance(interlayer, dict)
            else None
        )
        if isinstance(spend_first, dict) and not is_generic_runtime_operation(spend_first):
            return (
                "state-shaping refused: thinner-carrier bite is already concrete; "
                "use spend-local instead of more state shaping"
            )

    probe_must_bind = isinstance(probe, dict) and probe.get("probe_must_bind") is True
    if not probe_must_bind:
        return ""

    authorized_bite = (
        project_bound_program_shape(contract.get("authorized_bite"))
        if isinstance(contract, dict)
        else None
    )
    skill_touch = (
        project_bound_program_shape(skill_bridge.get("executable_local_touch_if_any"))
        if isinstance(skill_bridge, dict)
        else None
    )
    if (
        isinstance(authorized_bite, dict)
        and not is_generic_runtime_operation(authorized_bite)
    ) or (
        isinstance(skill_touch, dict)
        and not is_generic_runtime_operation(skill_touch)
    ):
        return (
            "state-shaping refused: probe discipline already has a concrete local bite; "
            "use bind-local, rebind-local, spend-local, or land-local"
        )
    return ""


def apply_output_updates(state: dict, args: argparse.Namespace) -> None:
    output = state.setdefault("output_status", {})
    for field in [
        "touched",
        "cosmetic_only",
        "contains_unsupported",
        "contains_placeholder",
        "final_artifact_materialized",
    ]:
        value = getattr(args, field, None)
        if value is not None:
            output[field] = value


def command_init(args: argparse.Namespace) -> int:
    state = json.loads(json.dumps(DEFAULT_STATE))
    state_path = Path(args.state_file)
    require_core_arguments(args)
    apply_core_updates(state, args)
    apply_output_updates(state, args)
    if args.fresh_blind_project_skills_on:
        state["bootstrap_context"] = fresh_blind_bootstrap_context()
        require_fresh_blind_asked_medium_surface(
            state,
            context="init refused",
        )
    if args.allow_release:
        require_materialization_evidence_arguments(args)
        set_materialization_evidence(state, args)
        require_program_or_materialized_output(state, state_path=state_path)
        state["release_veto"] = False
    else:
        has_program_fields = any(
            getattr(args, attr, None) not in (None, "")
            for attr in ["kind", "target", "operation", "success_signal"]
        )
        if has_program_fields:
            require_bound_program_arguments(args)
            set_bound_program(state, args)
    write_json(state_path, state)
    log_path = event_log_path(state_path)
    if log_path.exists():
        log_path.unlink()
    append_runtime_event(
        state_path,
        command_name="init",
        before=None,
        after=state,
        note=(
            "fresh blind project-skills-on state bootstrap"
            if args.fresh_blind_project_skills_on
            else "state bootstrap"
        ),
    )
    dump(state)
    return 0


def bootstrap_blind_state(
    state_path: Path,
    *,
    current_object: str,
    current_debt: str,
    next_bite: str,
    asked_medium_surface: str,
    current_seam: str = "",
    revocation_handle: str = "",
    uncertainty_mode: str = "",
    primary_slot: str = "",
) -> dict:
    state = json.loads(json.dumps(DEFAULT_STATE))
    state["current_object"] = str(current_object or "").strip()
    state["current_debt"] = str(current_debt or "").strip()
    state["next_bite"] = str(next_bite or "").strip()
    state["asked_medium_surface"] = str(asked_medium_surface or "").strip()
    state["current_seam"] = str(current_seam or "").strip() or state["current_object"]
    state["revocation_handle"] = str(revocation_handle or "").strip() or state_path.stem
    state["uncertainty_mode"] = str(uncertainty_mode or "").strip() or "unknown"
    state["primary_slot"] = str(primary_slot or "").strip() or "solve"
    require_core_arguments(
        argparse.Namespace(
            current_object=state["current_object"],
            current_debt=state["current_debt"],
            next_bite=state["next_bite"],
            asked_medium_surface=state["asked_medium_surface"],
            revocation_handle=state["revocation_handle"],
            primary_slot=state["primary_slot"],
        )
    )
    state["bootstrap_context"] = fresh_blind_bootstrap_context()
    require_fresh_blind_asked_medium_surface(
        state,
        context="bootstrap-blind refused",
    )
    write_json(state_path, state)
    log_path = event_log_path(state_path)
    if log_path.exists():
        log_path.unlink()
    append_runtime_event(
        state_path,
        command_name="bootstrap-blind",
        before=None,
        after=state,
        note="fresh blind project-skills-on thin bootstrap",
    )
    return state


def command_bootstrap_blind(args: argparse.Namespace) -> int:
    state_path = Path(args.state_file)
    state = bootstrap_blind_state(
        state_path,
        current_object=str(args.current_object or ""),
        current_debt=str(args.current_debt or ""),
        next_bite=str(args.next_bite or ""),
        asked_medium_surface=str(args.asked_medium_surface or ""),
        current_seam=str(args.current_seam or ""),
        revocation_handle=str(args.revocation_handle or ""),
        uncertainty_mode=str(args.uncertainty_mode or ""),
        primary_slot=str(args.primary_slot or ""),
    )
    dump(state)
    return 0


def command_bootstrap_blind_here(args: argparse.Namespace) -> int:
    delegated = argparse.Namespace(
        state_file=str(default_fresh_blind_state_path(Path.cwd())),
        current_object=args.current_object,
        current_debt=args.current_debt,
        next_bite=args.next_bite,
        asked_medium_surface=args.asked_medium_surface,
        current_seam=args.current_seam,
        revocation_handle=args.revocation_handle,
        uncertainty_mode=args.uncertainty_mode,
        primary_slot=args.primary_slot,
    )
    return command_bootstrap_blind(delegated)


def command_show(args: argparse.Namespace) -> int:
    dump(load_state(Path(args.state_file)))
    return 0


def set_core_should_route_to_land(state: dict, args: argparse.Namespace) -> bool:
    bound_program = state.get("bound_program")
    if not isinstance(bound_program, dict):
        return False
    asked_medium = str(state.get("asked_medium_surface", "")).strip()
    if program_is_asked_medium_closure(bound_program, asked_medium=asked_medium):
        return False
    if getattr(args, "release_veto", None) is False:
        return False

    next_object = str(getattr(args, "current_object", None) or "").strip()
    next_debt = str(getattr(args, "current_debt", None) or "").strip()
    next_bite = str(getattr(args, "next_bite", None) or "").strip()
    if not next_object or not next_debt or not next_bite:
        return False
    next_seam = str(getattr(args, "current_seam", None) or "").strip() or next_object

    return any(
        [
            next_object != str(state.get("current_object", "")).strip(),
            next_seam != str(state.get("current_seam", "")).strip(),
            next_debt != str(state.get("current_debt", "")).strip(),
            next_bite != str(state.get("next_bite", "")).strip(),
        ]
    )


def apply_same_carrier_landing(
    state: dict,
    path: Path,
    *,
    next_object: str,
    next_seam: str,
    next_debt: str,
    next_bite: str,
) -> None:
    bound_program = state.get("bound_program")
    if not isinstance(bound_program, dict):
        raise SystemExit("land-local refused: no bound_program is live")
    landed_bite = project_bound_program_shape(bound_program)
    landed_combo = extract_explicit_skill_combo(landed_bite)
    landed_owner = str(bound_program.get("owner_skill_if_any", "")).strip()

    asked_medium = _extract_markdown_artifact_hint(state.get("asked_medium_surface", ""))
    kind = str(bound_program.get("kind", "")).strip()
    target = str(bound_program.get("target", "")).strip()
    if program_is_asked_medium_closure(bound_program, asked_medium=asked_medium):
        raise SystemExit(
            "land-local refused: the live bound_program is already asked-medium closure, not a same-carrier structural bite"
        )
    output_status = state.get("output_status")
    if not isinstance(output_status, dict) or output_status.get("touched") is not True:
        raise SystemExit(
            "land-local refused: the live bound_program still needs one real execute-local touch "
            "before same-carrier landing can reopen the next layer"
        )

    if not next_object or not next_debt or not next_bite:
        inferred_object, inferred_seam, inferred_debt, inferred_bite = infer_same_carrier_landing_transition(
            state,
            bound_program,
        )
        if not next_object:
            next_object = inferred_object
        if not next_seam:
            next_seam = inferred_seam
        if not next_debt:
            next_debt = inferred_debt
        if not next_bite:
            next_bite = inferred_bite
    if not next_object or not next_debt or not next_bite:
        raise SystemExit(
            "land-local refused: next same-carrier layer could not be inferred and still needs --current-object, --current-debt, and --next-bite"
        )
    if not next_seam:
        next_seam = next_object
    release_ready_text = " ".join(
        [
            str(next_object or "").strip(),
            str(next_seam or "").strip(),
            str(next_debt or "").strip(),
            str(next_bite or "").strip(),
        ]
    ).lower()
    release_ready_same_carrier = bool(
        asked_medium
        and (
            "release_veto" in release_ready_text
            or "asked medium" in release_ready_text
            or "materialize" in release_ready_text
            or "exact closure" in release_ready_text
            or "封口" in release_ready_text
        )
    )

    changed = any(
        [
            next_object != str(state.get("current_object", "")).strip(),
            next_seam != str(state.get("current_seam", "")).strip(),
            next_debt != str(state.get("current_debt", "")).strip(),
            next_bite != str(state.get("next_bite", "")).strip(),
        ]
    )
    if not changed:
        raise SystemExit(
            "land-local refused: next same-carrier layer is identical to the current one"
        )

    previous_target = target
    previous_kind = kind
    preserved_output_path = asked_medium_output_path(state=state, state_path=path)
    existing_evidence = state.get("materialization_evidence")
    preserve_existing_output = (
        preserved_output_path is not None
        and isinstance(existing_evidence, dict)
        and _normalized_existing_path_text(str(existing_evidence.get("location", "")).strip())
        == _normalized_existing_path_text(str(preserved_output_path))
    )
    state["current_object"] = next_object
    state["current_seam"] = next_seam
    state["current_debt"] = next_debt
    state["next_bite"] = next_bite
    state["bound_program"] = None
    state["layer_composition_if_any"] = None
    state["landed_next_touch_if_any"] = None
    state["gate_binding_if_any"] = None
    state["primitive_field_if_any"] = None
    state["primitive_competition_if_any"] = None
    state["carrier_handoff_if_any"] = None
    state["secondary_rival_if_any"] = None
    state["primitive_takeover_gate_if_any"] = None
    if not preserve_existing_output:
        state["materialization_evidence"] = None

    output_status = state.get("output_status")
    if isinstance(output_status, dict):
        output_status["touched"] = False
        output_status["cosmetic_only"] = False
        output_status["contains_unsupported"] = False
        output_status["contains_placeholder"] = False
        output_status["final_artifact_materialized"] = False

    refresh_primitive_field_for_current_layer(state, force=True)
    primitive_field_after_refresh = state.get("primitive_field_if_any")
    refreshed_layer_primitives: list[str] = []
    if isinstance(primitive_field_after_refresh, dict):
        raw_primitives = primitive_field_after_refresh.get("active_primitives")
        if isinstance(raw_primitives, list):
            refreshed_layer_primitives = [
                canonicalize_skill_token(value)
                for value in raw_primitives
                if canonicalize_skill_token(value)
            ][:4]
        selection_basis = str(primitive_field_after_refresh.get("selection_basis", "")).strip()
        evidence_basis = str(primitive_field_after_refresh.get("evidence_basis", "")).strip()
        if selection_basis == "text_fallback" or evidence_basis == "lexical_hint":
            if landed_owner and landed_combo and landed_owner in landed_combo:
                seeded_primitives = [
                    primitive
                    for primitive in landed_combo
                    if primitive in ALLOWED_PRIMITIVES and primitive != "精确封口"
                ][:3]
                seeded_field_target = str(next_seam or next_object or "").strip()
                if seeded_primitives:
                    state["primitive_field_if_any"] = {
                        "layer_object": seeded_field_target or str(state.get("current_seam", "")).strip(),
                        "active_primitives": seeded_primitives,
                        "why_now": (
                            "the previous same-carrier bite already exposed a thinner live object, "
                            "so keep the last explicit structural combo available until the new layer "
                            "wins a more honest owner"
                        ),
                        "selection_basis": "explicit_hint",
                        "evidence_basis": "state_见证",
                        "tie_break_check": seeded_field_target or str(state.get("current_seam", "")).strip(),
                    }
                    state["primitive_competition_if_any"] = None
                    refreshed_layer_primitives = seeded_primitives[:]
                else:
                    state["primitive_field_if_any"] = None
                    state["primitive_competition_if_any"] = None
            else:
                state["primitive_field_if_any"] = None
                state["primitive_competition_if_any"] = None
    arm_primitive_takeover_gate(
        state,
        trigger="same_carrier_landing",
        note="the live carrier just tightened; rebind one primitive-owned next bite before ordinary continuation resumes",
    )

    report = build_report(state, path)
    direct_closure_takeover_allowed = _direct_closure_takeover_allowed(
        report=report,
        state=state,
        asked_medium=asked_medium,
        direct_closure_signal=release_ready_same_carrier,
        reopened_target=str(next_seam or next_object or "").strip(),
    )
    closure_nucleus = report.get("closure_nucleus")
    closure_touch = (
        project_bound_program_shape(closure_nucleus.get("current_读出_bite_if_any"))
        if isinstance(closure_nucleus, dict)
        else None
    )
    if closure_touch is None and direct_closure_takeover_allowed:
        compiled_closure_touch = derive_object_compiled_读出_candidate(
            state,
            asked_medium=asked_medium,
            current_object=str(state.get("current_object", "")).strip(),
            current_debt=str(state.get("current_debt", "")).strip(),
            current_seam=str(state.get("current_seam", "")).strip(),
            next_bite=str(state.get("next_bite", "")).strip(),
            structural_bite=landed_bite if isinstance(landed_bite, dict) else None,
        )
        closure_touch = (
            project_bound_program_shape(compiled_closure_touch)
            if isinstance(compiled_closure_touch, dict)
            else None
        )
    preferred_direct_closure = bool(
        direct_closure_takeover_allowed
        and isinstance(closure_touch, dict)
        and program_is_direct_closure_candidate(closure_touch, state)
        and has_explicit_skill_ownership(closure_touch)
    )

    def _normalize_release_ready_touch(program: dict | None) -> dict | None:
        if (
            not direct_closure_takeover_allowed
            or not isinstance(program, dict)
            or not asked_medium
            or not program_is_direct_closure_candidate(program, state)
        ):
            return program
        promoted_program = dict(program)
        promoted_program["target"] = asked_medium
        promoted_program["success_signal"] = "asked_medium_is_exact_and_executable"
        return promoted_program

    closure_touch = _normalize_release_ready_touch(closure_touch)

    def read_landing_skill_authority(
        runtime_report: dict,
    ) -> tuple[str, list[str], dict | None, bool]:
        fallback_choice: tuple[str, list[str], dict | None, bool] = ("", [], None, False)
        for require_same_carrier in [True, False]:
            candidate = read_skill_authority_program(
                runtime_report,
                require_same_carrier=require_same_carrier,
            )
            winner, combo, touch, silence_after_contact = candidate
            if isinstance(touch, dict) and has_explicit_skill_ownership(touch):
                return winner, combo, touch, silence_after_contact
            if fallback_choice[2] is None and isinstance(touch, dict):
                fallback_choice = candidate
        return fallback_choice

    (
        landing_skill_winner,
        landing_skill_combo,
        landing_skill_program,
        _landing_silence_after_contact,
    ) = read_landing_skill_authority(report)
    landed_next_touch = (
        project_bound_program_shape(landing_skill_program)
        if isinstance(landing_skill_program, dict)
        else None
    )
    if preferred_direct_closure and (
        landed_next_touch is None
        or is_generic_runtime_operation(landed_next_touch)
        or not has_explicit_skill_ownership(landed_next_touch)
        or not program_is_direct_closure_candidate(landed_next_touch, state)
    ):
        landed_next_touch = closure_touch
    elif (
        direct_closure_takeover_allowed
        and isinstance(landed_next_touch, dict)
        and program_is_direct_closure_candidate(landed_next_touch, state)
        and asked_medium
    ):
        landed_next_touch = _normalize_release_ready_touch(landed_next_touch)
    recomposed_touch = derive_bound_program_candidate(state, [])
    if isinstance(recomposed_touch, dict) and not preferred_direct_closure:
        recomposed_target = str(recomposed_touch.get("target", "")).strip()
        recomposed_operation = str(recomposed_touch.get("operation", "")).strip()
        recomposed_combo = extract_explicit_skill_combo(recomposed_touch)
        landed_operation = (
            str(landed_next_touch.get("operation", "")).strip()
            if isinstance(landed_next_touch, dict)
            else ""
        )
        landed_combo = (
            extract_explicit_skill_combo(landed_next_touch)
            if isinstance(landed_next_touch, dict)
            else []
        )
        if (
            landed_next_touch is None
            or (
                recomposed_target
                and recomposed_target
                in {
                    str(state.get("current_object", "")).strip(),
                    str(state.get("current_seam", "")).strip(),
                    str(state.get("current_debt", "")).strip(),
                }
                and recomposed_operation
                and recomposed_operation != landed_operation
            )
            or (
                isinstance(landed_next_touch, dict)
                and recomposed_target
                and recomposed_target == str(landed_next_touch.get("target", "")).strip()
                and recomposed_operation
                and recomposed_operation == landed_operation
                and recomposed_combo
                and landed_combo
                and recomposed_combo != landed_combo
            )
        ):
            landed_next_touch = recomposed_touch
    strongest_explicit_owner = ""
    strongest_explicit_combo: list[str] = []
    if isinstance(landed_next_touch, dict):
        explicit_owner = str(landed_next_touch.get("owner_skill_if_any", "")).strip()
        explicit_combo = extract_explicit_skill_combo(landed_next_touch)
        if explicit_owner and explicit_combo and explicit_owner in explicit_combo:
            strongest_explicit_owner = explicit_owner
            strongest_explicit_combo = explicit_combo[:]
        landed_next_touch.pop("owner_skill_if_any", None)
        landed_next_touch.pop("owner_skill_combo_if_any", None)
        state["landed_next_touch_if_any"] = landed_next_touch
    effective_owner = ""
    effective_combo: list[str] = []
    seeded_problem_born_touch = None
    current_layer_targets: set[str] = set()
    seeded_target = str(next_seam or next_object or "").strip()
    seeded_operation = str(next_bite or "").strip()
    landed_has_explicit_ownership = has_explicit_skill_ownership(landed_next_touch)
    landed_touch_is_non_generic = (
        isinstance(landed_next_touch, dict)
        and not is_generic_runtime_operation(landed_next_touch)
    )
    landed_operation = (
        str(landed_next_touch.get("operation", "")).strip()
        if isinstance(landed_next_touch, dict)
        else ""
    )
    if seeded_target and seeded_operation:
        seeded_kind = "write"
        seeded_success_signal = f"the next local layer became explicit on {seeded_target}"
        if asked_medium and seeded_target == asked_medium:
            seeded_kind = "读出"
            seeded_success_signal = "asked_medium_is_exact_and_executable"
        seeded_problem_born_touch = {
            "kind": seeded_kind,
            "target": seeded_target,
            "operation": seeded_operation,
            "success_signal": seeded_success_signal,
            "current_layer_object_if_any": str(state.get("current_object", "")).strip()
            or str(state.get("current_seam", "")).strip(),
            "controlled_object_if_any": seeded_target,
            "object_transform_if_any": str(next_debt or current_debt or "").strip(),
            "next_object_if_any": seeded_target,
            "step_outline_if_any": seeded_operation,
            "skill_phase_if_any": "same_carrier_reopened_layer",
        }
        current_layer_targets = {
            value
            for value in [
                str(state.get("current_object", "")).strip(),
                str(state.get("current_seam", "")).strip(),
                str(state.get("current_debt", "")).strip(),
                seeded_target,
            ]
            if value
        }
        landed_target = (
            str(landed_next_touch.get("target", "")).strip()
            if isinstance(landed_next_touch, dict)
            else ""
        )
        landed_off_layer = bool(
            landed_target
            and landed_target not in current_layer_targets
            and not (
                asked_medium
                and landed_target == asked_medium
                and seeded_target == asked_medium
            )
        )
        seeded_can_replace_touch = (
            not landed_touch_is_non_generic
            and (
                not isinstance(landed_next_touch, dict)
                or is_generic_runtime_operation(landed_next_touch)
            )
            and (
                not isinstance(landed_next_touch, dict)
                or seeded_operation not in landed_operation
            )
        )
        if not seeded_can_replace_touch and landed_off_layer:
            seeded_can_replace_touch = True
        if seeded_can_replace_touch and not preferred_direct_closure:
            landed_next_touch = seeded_problem_born_touch
            state["landed_next_touch_if_any"] = landed_next_touch
            landed_has_explicit_ownership = False
            landed_touch_is_non_generic = False
            landed_operation = seeded_operation
            if refreshed_layer_primitives:
                strongest_explicit_owner = refreshed_layer_primitives[0]
                strongest_explicit_combo = refreshed_layer_primitives[:]
    if (
        isinstance(recomposed_touch, dict)
        and not preferred_direct_closure
        and has_explicit_skill_ownership(recomposed_touch)
        and (
            not isinstance(landed_next_touch, dict)
            or not has_explicit_skill_ownership(landed_next_touch)
            or is_generic_runtime_operation(landed_next_touch)
            or (
                current_layer_targets
                and str(recomposed_touch.get("target", "")).strip() in current_layer_targets
                and str(landed_next_touch.get("target", "")).strip() not in current_layer_targets
            )
        )
    ):
        landed_next_touch = recomposed_touch
        state["landed_next_touch_if_any"] = landed_next_touch
        landed_has_explicit_ownership = True
        landed_touch_is_non_generic = not is_generic_runtime_operation(landed_next_touch)
        landed_operation = str(landed_next_touch.get("operation", "")).strip()
    def _overlay_reopened_layer_touch_metadata(program: dict | None) -> dict | None:
        payload = project_bound_program_shape(program)
        if not isinstance(payload, dict):
            return None
        if seeded_problem_born_touch is None:
            return payload
        for key in [
            "current_layer_object_if_any",
            "controlled_object_if_any",
            "object_transform_if_any",
            "next_object_if_any",
            "step_outline_if_any",
            "skill_phase_if_any",
        ]:
            value = str(seeded_problem_born_touch.get(key, "")).strip()
            if value and not str(payload.get(key, "")).strip():
                payload[key] = value
        return payload
    landed_next_touch = _overlay_reopened_layer_touch_metadata(landed_next_touch)
    if preferred_direct_closure and isinstance(closure_touch, dict):
        landed_next_touch = _overlay_reopened_layer_touch_metadata(closure_touch)
    landed_target = (
        str(landed_next_touch.get("target", "")).strip()
        if isinstance(landed_next_touch, dict)
        else ""
    )
    if (
        isinstance(landed_next_touch, dict)
        and asked_medium
        and landed_target == asked_medium
        and seeded_target
        and seeded_target != asked_medium
        and not preferred_direct_closure
    ):
        if (
            isinstance(recomposed_touch, dict)
            and not program_is_asked_medium_closure(recomposed_touch, asked_medium=asked_medium)
        ):
            landed_next_touch = _overlay_reopened_layer_touch_metadata(recomposed_touch)
        elif isinstance(seeded_problem_born_touch, dict):
            landed_next_touch = seeded_problem_born_touch
    if isinstance(landed_next_touch, dict):
        state["landed_next_touch_if_any"] = landed_next_touch
    if (
        not strongest_explicit_combo
        and landing_skill_winner
        and landing_skill_combo
        and landing_skill_winner in landing_skill_combo
    ):
        strongest_explicit_owner = landing_skill_winner
        strongest_explicit_combo = landing_skill_combo[:]
    if not strongest_explicit_combo and landed_owner and landed_combo and landed_owner in landed_combo:
        strongest_explicit_owner = landed_owner
        strongest_explicit_combo = landed_combo[:]
    if (
        not strongest_explicit_combo
        and isinstance(landed_next_touch, dict)
        and refreshed_layer_primitives
    ):
        strongest_explicit_owner = refreshed_layer_primitives[0]
        strongest_explicit_combo = refreshed_layer_primitives[:]
    if strongest_explicit_owner == "反问" and refreshed_layer_primitives:
        structural_followup = [
            skill_name
            for skill_name in refreshed_layer_primitives
            if skill_name and skill_name not in {"反问", "见证"}
        ]
        if structural_followup:
            strongest_explicit_owner = structural_followup[0]
            strongest_explicit_combo = structural_followup[:]
    owned_landed_touch = project_bound_program_shape(landed_next_touch)
    if (
        isinstance(owned_landed_touch, dict)
        and strongest_explicit_owner
        and strongest_explicit_combo
        and not has_explicit_skill_ownership(owned_landed_touch)
    ):
        owned_landed_touch = (
            attach_program_owner_metadata(
                owned_landed_touch,
                owner_skill=strongest_explicit_owner,
                owner_combo=strongest_explicit_combo,
            )
            or owned_landed_touch
        )
    refreshed_combo = (
        strongest_explicit_combo
    )
    refreshed_owner = (
        strongest_explicit_owner
    )
    arm_primitive_takeover_gate(
        state,
        trigger="same_carrier_landing",
        note="the live carrier just tightened; rebind one primitive-owned next bite before ordinary continuation resumes",
    )
    if not refreshed_combo:
        state["primitive_field_if_any"] = None
        state["primitive_competition_if_any"] = None
        gate = state.get("primitive_takeover_gate_if_any")
        if isinstance(gate, dict):
            gate.pop("active_primitives", None)
    if refreshed_combo:
        state["primitive_field_if_any"] = {
            "layer_object": seeded_target or str(state.get("current_seam", "")).strip(),
            "active_primitives": [
                primitive
                for primitive in refreshed_combo
                if primitive in ALLOWED_PRIMITIVES and primitive != "精确封口"
            ][:3],
            "why_now": (
                "the previous same-carrier bite really changed the live object, "
                "so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes"
            ),
            "selection_basis": "explicit_hint",
            "evidence_basis": "state_见证",
            "tie_break_check": seeded_target or str(state.get("current_seam", "")).strip(),
        }
        if (
            isinstance(landed_next_touch, dict)
            and refreshed_owner
        ):
            landed_next_touch["owner_skill_if_any"] = refreshed_owner
            landed_next_touch["owner_skill_combo_if_any"] = refreshed_combo[:6]
        effective_owner = refreshed_owner or effective_owner
        effective_combo = refreshed_combo or effective_combo
    landed_next_touch = (
        normalize_direct_asked_medium_closure_owner(
            landed_next_touch if isinstance(landed_next_touch, dict) else None,
            asked_medium=asked_medium,
            preferred_owner=effective_owner,
            preferred_combo=effective_combo,
        )
        or landed_next_touch
    )
    if isinstance(landed_next_touch, dict):
        state["landed_next_touch_if_any"] = landed_next_touch
        normalized_owner = str(landed_next_touch.get("owner_skill_if_any", "")).strip()
        normalized_combo = extract_explicit_skill_combo(landed_next_touch)
        if normalized_owner and normalized_combo and normalized_owner in normalized_combo:
            effective_owner = normalized_owner
            effective_combo = normalized_combo[:]
    landing_report = build_report(state, path)
    landing_bridge = landing_report.get("skill_authority_bridge")
    if isinstance(landing_bridge, dict):
        closure_touch = project_bound_program_shape(
            landing_bridge.get("executable_local_touch_if_any")
        )
        closure_owner = str(landing_bridge.get("winning_skill_if_any", "")).strip()
        closure_combo = _normalized_skill_list(
            landing_bridge.get("active_skill_combo_if_any")
        )
        asked_medium = str(state.get("asked_medium_surface", "")).strip()
        if (
            closure_owner == "精确封口"
            and isinstance(closure_touch, dict)
            and program_is_asked_medium_closure(closure_touch, asked_medium=asked_medium)
        ):
            landed_next_touch = closure_touch
            state["landed_next_touch_if_any"] = closure_touch
            owned_landed_touch = closure_touch
            effective_owner = closure_owner
            effective_combo = closure_combo or [closure_owner]
    state["layer_composition_if_any"] = build_layer_composition_state_payload(
        state,
        surface="takeover_recomposition",
        authorized_bite=owned_landed_touch if isinstance(owned_landed_touch, dict) else landed_bite,
        skill_winner=effective_owner,
        skill_combo=effective_combo,
        reason=(
            "the previous same-carrier bite really changed the live object, "
            "so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes"
        ),
        must_bind_local_bite=True,
        must_spend_handoff=False,
        layer_object=str(state.get("current_object", "")).strip(),
        controlled_object=(
            str(landed_next_touch.get("target", "")).strip()
            if isinstance(landed_next_touch, dict)
            else str(state.get("current_object", "")).strip()
        ),
        current_seam=str(state.get("current_seam", "")).strip(),
        current_debt=str(state.get("current_debt", "")).strip(),
        next_local_choice=(
            str(landed_next_touch.get("target", "")).strip()
            if isinstance(landed_next_touch, dict)
            else seeded_target or str(state.get("current_seam", "")).strip()
        ),
        gap_object=(
            (
                seeded_target
                if seeded_target
                and seeded_target
                not in {
                    str(state.get("current_object", "")).strip(),
                    (
                        str(landed_next_touch.get("target", "")).strip()
                        if isinstance(landed_next_touch, dict)
                        else ""
                    ),
                }
                else ""
            )
            or (
                str(state.get("current_seam", "")).strip()
                if str(state.get("current_seam", "")).strip()
                not in {
                    str(state.get("current_object", "")).strip(),
                    (
                        str(landed_next_touch.get("target", "")).strip()
                        if isinstance(landed_next_touch, dict)
                        else ""
                    ),
                }
                else ""
            )
        ),
        transition_change=(
            f"landed {previous_kind} on {previous_target} and reopened "
            f"{str((landed_next_touch or {}).get('kind', '')).strip()} on "
            f"{str((landed_next_touch or {}).get('target', '')).strip()}"
        ),
        lighting_if_any=_report_skill_lighting(landing_report),
    )


def command_set_core(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    pre_state = load_state(path)
    if set_core_should_route_to_land(pre_state, args):
        def landing_mutator(state: dict) -> None:
            apply_same_carrier_landing(
                state,
                path,
                next_object=str(args.current_object or "").strip(),
                next_seam=str(args.current_seam or "").strip() or str(args.current_object or "").strip(),
                next_debt=str(args.current_debt or "").strip(),
                next_bite=str(args.next_bite or "").strip(),
            )
        state = mutate_state(path, landing_mutator, command_name="land-local")
        dump(state)
        return 0

    def mutator(state: dict) -> None:
        shaping_refusal = state_shaping_requires_runtime_spend(state, path)
        if shaping_refusal:
            raise SystemExit(shaping_refusal)
        previous_core = {
            "current_object": str(state.get("current_object", "")).strip(),
            "current_seam": str(state.get("current_seam", "")).strip(),
            "current_debt": str(state.get("current_debt", "")).strip(),
            "next_bite": str(state.get("next_bite", "")).strip(),
        }
        apply_core_updates(state, args)
        require_fresh_blind_asked_medium_surface(
            state,
            context="set-core refused",
        )
        ordinary_regrowth_refusal = _state_shaping_ordinary_regrowth_refusal(
            state=state,
            state_path=path,
            candidate_texts=[
                str(state.get("current_debt", "")).strip(),
                str(state.get("next_bite", "")).strip(),
            ],
        )
        if ordinary_regrowth_refusal:
            raise SystemExit(ordinary_regrowth_refusal)
        current_core = {
            "current_object": str(state.get("current_object", "")).strip(),
            "current_seam": str(state.get("current_seam", "")).strip(),
            "current_debt": str(state.get("current_debt", "")).strip(),
            "next_bite": str(state.get("next_bite", "")).strip(),
        }
        if previous_core != current_core:
            primitive_field = state.get("primitive_field_if_any")
            if (
                isinstance(primitive_field, dict)
                and str(primitive_field.get("selection_basis", "")).strip() == "explicit_hint"
            ):
                # Explicit same-carrier narrowing is allowed to stay live within
                # the current layer, but a core rewrite should force reselection.
                state["primitive_field_if_any"] = None
        if args.release_veto is not None:
            if args.release_veto is False:
                require_program_or_materialized_output(state, state_path=path)
            state["release_veto"] = args.release_veto
        if state.get("release_veto") is True:
            refresh_primitive_field_for_current_layer(state)
    state = mutate_state(path, mutator, command_name="set-core")
    dump(state)
    return 0


def command_program(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        if args.mode == "clear":
            if not can_clear_release_veto_without_program(state):
                raise SystemExit(
                    "cannot clear bound_program before the asked medium is touched "
                    "and the final artifact is materialized"
                )
            if str(state.get("asked_medium_surface", "")).strip():
                require_asked_medium_skill_serialization(
                    state,
                    state_path=path,
                    context="program:clear refused",
                )
            state["bound_program"] = None
            state["layer_composition_if_any"] = None
            state["gate_binding_if_any"] = None
            if state.get("release_veto") is True:
                refresh_primitive_field_for_current_layer(state, force=True)
        else:
            require_bound_program_arguments(args)
            pre_program_state = _deep_copy(state)
            set_bound_program(state, args)
            owner_skill, owner_combo, report = infer_program_ownership_from_report(
                pre_program_state,
                path,
                state.get("bound_program"),
            )
            enriched_program = attach_program_owner_metadata(
                state.get("bound_program"),
                owner_skill=owner_skill,
                owner_combo=owner_combo,
            )
            if isinstance(enriched_program, dict):
                state["bound_program"] = enriched_program
            if state.get("release_veto") is True and not has_explicit_skill_ownership(
                state.get("bound_program")
            ):
                raise SystemExit(
                    "program:set refused: bound_program must carry explicit skill owner/combo rather than inheriting a report-side fallback"
                )
            reset_output_materialization_for_new_local_move(state)
            state["layer_composition_if_any"] = None
            state["gate_binding_if_any"] = None
            state["carrier_handoff_if_any"] = None
            state["primitive_takeover_gate_if_any"] = None
            state["landed_next_touch_if_any"] = None
            if state.get("release_veto") is True:
                agenda = derive_local_agenda_for_program(state, state["bound_program"])
                candidate_gate = derive_gate_binding_candidate(state, [], agenda_override=agenda)
                if isinstance(candidate_gate, dict):
                    state["gate_binding_if_any"] = candidate_gate
                state["layer_composition_if_any"] = build_layer_composition_state_payload(
                    state,
                    surface="bound_program",
                    authorized_bite=state.get("bound_program"),
                    skill_winner=str((state.get("bound_program") or {}).get("owner_skill_if_any", "")).strip(),
                    skill_combo=extract_explicit_skill_combo(state.get("bound_program")),
                    reason=str(
                        ((report.get("discipline_contract") or {}).get("reason", ""))
                    ).strip()
                    or "one current-layer local bite is now explicitly bound on the live carrier",
                    must_bind_local_bite=False,
                    must_spend_handoff=False,
                    layer_object=str(state.get("current_object", "")).strip(),
                    controlled_object=str(((state.get("bound_program") or {}).get("target", ""))).strip(),
                    current_seam=str(state.get("current_seam", "")).strip(),
                    current_debt=str(state.get("current_debt", "")).strip(),
                    next_local_choice=infer_next_layer_choice_for_bound_program(
                        state,
                        report,
                        state.get("bound_program"),
                    ),
                    gap_object=str(((report.get("gap_object") or {}).get("object", ""))).strip(),
                    transition_change=(
                        f"bound {str((state.get('bound_program') or {}).get('kind', '')).strip()} "
                        f"on {str((state.get('bound_program') or {}).get('target', '')).strip()}"
                    ),
                    lighting_if_any=_report_skill_lighting(report),
                )
            refresh_primitive_field_for_current_layer(state, force=True)
    state = mutate_state(path, mutator, command_name=f"program:{args.mode}")
    dump(state)
    return 0


def command_gate(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if args.mode == "clear":
            state["gate_binding_if_any"] = None
            if state.get("release_veto") is True:
                refresh_primitive_field_for_current_layer(state, force=True)
            return

        if state.get("release_veto") is not True:
            raise SystemExit("gate set requires release_veto to stay active")
        if state.get("carrier_handoff_if_any") is not None:
            raise SystemExit("gate set refused: carrier_handoff_if_any already owns local authority")

        require_gate_binding_arguments(args)
        require_bound_program_arguments(args)
        set_bound_program(state, args)
        set_gate_binding(state, args)
        refresh_primitive_field_for_current_layer(state, force=True)

    state = mutate_state(path, mutator, command_name=f"gate:{args.mode}")
    dump(state)
    return 0


def command_primitive(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        def _refresh_live_handoff_layer() -> None:
            handoff = state.get("carrier_handoff_if_any")
            if isinstance(handoff, dict):
                materialize_handoff_layer_authority(
                    state,
                    path,
                    handoff,
                    reason=str(((state.get("layer_composition_if_any") or {}).get("reason", ""))).strip()
                    or "the thinner carrier is already explicit, so one current-layer combination now owns the next local bite",
                )

        if args.mode == "clear":
            state["primitive_field_if_any"] = None
            _refresh_live_handoff_layer()
            return
        shaping_refusal = state_shaping_requires_runtime_spend(state, path)
        if shaping_refusal:
            raise SystemExit(shaping_refusal)
        require_primitive_field_arguments(args)
        set_primitive_field(state, args)
        _refresh_live_handoff_layer()

    state = mutate_state(path, mutator, command_name=f"primitive:{args.mode}")
    dump(state)
    return 0


def command_competition(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        def _refresh_live_handoff_layer() -> None:
            handoff = state.get("carrier_handoff_if_any")
            if isinstance(handoff, dict):
                materialize_handoff_layer_authority(
                    state,
                    path,
                    handoff,
                    reason=str(((state.get("layer_composition_if_any") or {}).get("reason", ""))).strip()
                    or "the thinner carrier is already explicit, so one current-layer combination now owns the next local bite",
                )

        if args.mode == "clear":
            state["primitive_competition_if_any"] = None
            refresh_primitive_field_for_current_layer(state, force=True)
            _refresh_live_handoff_layer()
            return
        shaping_refusal = state_shaping_requires_runtime_spend(state, path)
        if shaping_refusal:
            raise SystemExit(shaping_refusal)
        set_primitive_competition(state, args)
        refresh_primitive_field_for_current_layer(state, force=True)
        _refresh_live_handoff_layer()

    state = mutate_state(path, mutator, command_name=f"competition:{args.mode}")
    dump(state)
    return 0


def command_evidence(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        pending_contract = pending_runtime_execution_contract(
            state,
            layer_composition=state.get("layer_composition_if_any"),
        )
        if isinstance(pending_contract, dict):
            required_action = str(pending_contract.get("required_action", "")).strip()
            if required_action:
                raise SystemExit(
                    "evidence set refused: the live runtime contract still requires "
                    f"{required_action} before asked-medium evidence can be rewritten"
                )
        if args.mode == "clear":
            if can_clear_release_veto_without_program(state):
                raise SystemExit(
                    "cannot clear materialization evidence while it still authorizes "
                    "a released state without a bound_program"
                )
            state["materialization_evidence"] = None
        else:
            set_materialization_evidence(state, args)
            if str(state.get("asked_medium_surface", "")).strip():
                require_asked_medium_skill_serialization(
                    state,
                    state_path=path,
                    context="evidence set refused",
                )
            finalize_materialized_closure(state, state_path=path)
    state = mutate_state(path, mutator, command_name=f"evidence:{args.mode}")
    dump(state)
    return 0


def command_set_output(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        pending_contract = pending_runtime_execution_contract(
            state,
            layer_composition=state.get("layer_composition_if_any"),
        )
        if isinstance(pending_contract, dict):
            required_action = str(pending_contract.get("required_action", "")).strip()
            if required_action:
                raise SystemExit(
                    "set-output refused: the live runtime contract still requires "
                    f"{required_action} before asked-medium flags can be updated"
                )
        apply_output_updates(state, args)
        output_status = state.get("output_status", {})
        if (
            str(state.get("asked_medium_surface", "")).strip()
            and isinstance(output_status, dict)
            and output_status.get("final_artifact_materialized") is True
        ):
            require_asked_medium_skill_serialization(
                state,
                state_path=path,
                context="set-output refused",
            )
        finalize_materialized_closure(state, state_path=path)
        if state.get("release_veto") is True:
            refresh_primitive_field_for_current_layer(state, force=True)
    state = mutate_state(path, mutator, command_name="set-output")
    dump(state)
    return 0


def command_marker(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        markers = state.setdefault("unresolved_markers", [])
        if args.mode == "add":
            for marker in args.marker:
                if marker not in markers:
                    markers.append(marker)
        elif args.mode == "remove":
            state["unresolved_markers"] = [m for m in markers if m not in set(args.marker)]
        elif args.mode == "clear":
            state["unresolved_markers"] = []
    state = mutate_state(path, mutator, command_name=f"markers:{args.mode}")
    dump(state)
    return 0


def command_rival(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        if args.mode == "clear":
            state["secondary_rival_if_any"] = None
        else:
            state["secondary_rival_if_any"] = {
                "object": args.object,
                "debt": args.debt,
                "bite": args.bite,
                "separating_advantage": args.separating_advantage,
            }
        if state.get("release_veto") is True:
            refresh_primitive_field_for_current_layer(state, force=True)
    state = mutate_state(path, mutator, command_name=f"rival:{args.mode}")
    dump(state)
    return 0


def command_handoff(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if args.mode == "clear":
            state["carrier_handoff_if_any"] = None
            state["layer_composition_if_any"] = None
            refresh_primitive_field_for_current_layer(state, force=True)
            return
        shaping_refusal = state_shaping_requires_runtime_spend(state, path)
        if shaping_refusal:
            raise SystemExit(shaping_refusal)

        if state.get("release_veto") is not True:
            raise SystemExit("handoff set requires release_veto to stay active")

        handoff = {
            "trigger": args.trigger,
            "from_slot": args.from_slot,
            "to_object": args.to_object,
            "winning_pressure": args.winning_pressure,
            "why_local": args.why_local,
        }
        if args.cooled_pressure is not None:
            handoff["cooled_pressure_if_any"] = args.cooled_pressure
        if args.active_pressure or args.cheap_check:
            active_pressures = args.active_pressure or ["check"]
            handoff["warm_field"] = {
                "active_pressures": active_pressures,
            }
            if args.cheap_check is not None:
                handoff["warm_field"]["cheap_check"] = args.cheap_check
            if args.primitive_hint:
                handoff["warm_field"]["primitive_hints"] = [
                    canonicalize_primitive_token(value) for value in args.primitive_hint
                    if canonicalize_primitive_token(value)
                ]
            handoff["warm_field"]["evidence_basis"] = (
                "cheap_check" if args.cheap_check is not None else "state_见证"
            )
        elif args.primitive_hint:
            handoff["warm_field"] = {
                "active_pressures": ["check"],
                "primitive_hints": [
                    canonicalize_primitive_token(value) for value in args.primitive_hint
                    if canonicalize_primitive_token(value)
                ],
                "evidence_basis": "explicit_hint",
            }

        # A thinner carrier taking authority should clear any stale same-slot program.
        state["bound_program"] = None
        state["layer_composition_if_any"] = None
        state["gate_binding_if_any"] = None
        state["carrier_handoff_if_any"] = handoff
        reset_output_materialization_for_new_local_move(state)
        refresh_primitive_field_for_current_layer(
            state,
            handoff_override=handoff,
            force=True,
        )
        materialize_handoff_layer_authority(
            state,
            path,
            handoff,
            reason="the thinner carrier is already explicit, so one current-layer combination now owns the next local bite",
        )

    state = mutate_state(path, mutator, command_name=f"handoff:{args.mode}")
    dump(state)
    return 0


def command_residue(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    def mutator(state: dict) -> None:
        residue = state.setdefault("memory_residue", [])
        if args.mode == "clear":
            state["memory_residue"] = []
        else:
            if args.kind not in ALLOWED_RESIDUE_KINDS:
                raise SystemExit(f"invalid residue kind: {args.kind}")
            residue.append(
                {
                    "kind": args.kind,
                    "description": args.description,
                    "replayable": args.replayable,
                }
            )
    state = mutate_state(path, mutator, command_name=f"residue:{args.mode}")
    dump(state)
    return 0


def command_check(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    state = load_state(path)
    report = build_report(state, path)
    if report["problems"]:
        dump(report)
        return 2
    layer_composition = report.get("layer_composition")
    pending_contract = pending_runtime_execution_contract(
        state,
        layer_composition=layer_composition,
    )
    runtime_evidence = build_runtime_evidence(path)
    if isinstance(pending_contract, dict) or active_contract_requires_runtime_evidence(
        report.get("discipline_contract"),
        runtime_evidence,
        layer_composition=layer_composition,
        state=state,
    ):
        payload = build_runtime_evidence_refusal_payload(
            path,
            discipline_contract=report.get("discipline_contract"),
            resume_bridge=report.get("resume_bridge"),
            warnings=report.get("warnings"),
            layer_composition=layer_composition,
            surface_payload={
                "surface": report.get("layer_composition", {}).get("surface", "")
                if isinstance(report.get("layer_composition"), dict)
                else "",
                "authorized_bite_if_any": (
                    pending_contract.get("authorized_bite")
                    if isinstance(pending_contract, dict) and isinstance(pending_contract.get("authorized_bite"), dict)
                    else (report.get("layer_composition", {}) or {}).get("authorized_bite", {})
                ),
                "skill_lighting_surface": report.get("skill_lighting_surface", {}),
                "pending_transition": isinstance(pending_contract, dict),
                "allowed_transition_surfaces": (
                    pending_contract.get("allowed_transition_surfaces", [])
                    if isinstance(pending_contract, dict)
                    else []
                ),
                "control_context": {
                    "current_object": report.get("control_bridge", {}).get("current_object", "")
                    if isinstance(report.get("control_bridge"), dict)
                    else "",
                    "current_debt": report.get("control_bridge", {}).get("current_debt", "")
                    if isinstance(report.get("control_bridge"), dict)
                    else "",
                    "asked_medium_surface": report.get("control_bridge", {}).get("asked_medium_surface", "")
                    if isinstance(report.get("control_bridge"), dict)
                    else "",
                },
            },
        )
        dump(payload)
        return 1
    dump(report)
    return 0 if report["release_allowed"] else 1


def fresh_blind_first_entry_skill_program_is_usable(
    program: dict | None,
    *,
    state: dict | None = None,
) -> bool:
    return bool(
        isinstance(program, dict)
        and has_explicit_skill_ownership(program)
        and fresh_blind_same_carrier_first_entry(program, state=state)
    )


def rebuild_fresh_blind_first_entry_skill_program(
    state: dict,
    first_layer_arena: dict | None,
) -> dict | None:
    if not isinstance(first_layer_arena, dict):
        return None
    focus_target = str(first_layer_arena.get("focus_target", "")).strip()
    for candidate in first_layer_arena.get("candidates", [])[:8]:
        if not isinstance(candidate, dict):
            continue
        skill_name = canonicalize_skill_token(candidate.get("skill"))
        touch_target = str(candidate.get("touch_target", "")).strip() or focus_target
        if not skill_name or not touch_target:
            continue
        supporting = _normalized_skill_list(candidate.get("supporting_skills_if_any"))
        rebuilt_touch = build_problem_born_touch_for_skill(
            state,
            skill_name,
            target=touch_target,
            supporting=supporting,
        )
        rebuilt_program = (
            project_bound_program_shape(rebuilt_touch)
            if isinstance(rebuilt_touch, dict)
            else None
        )
        if fresh_blind_first_entry_skill_program_is_usable(rebuilt_program, state=state):
            return rebuilt_program
    return None


def rebuild_reopened_layer_skill_program_candidates(
    state: dict,
    report: dict,
) -> list[dict]:
    candidates: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    def push_from_surface(surface: object, *, fallback_target: str = "") -> None:
        if not isinstance(surface, dict):
            return
        raw_candidates = surface.get("candidates")
        if not isinstance(raw_candidates, list):
            return
        for candidate in raw_candidates[:8]:
            if not isinstance(candidate, dict):
                continue
            skill_name = canonicalize_skill_token(candidate.get("skill"))
            if (
                not skill_name
                or skill_name in REOPEN_COMPETITION_DISALLOWED_SKILLS
            ):
                continue
            touch_target = str(candidate.get("touch_target", "")).strip() or fallback_target
            if not touch_target:
                continue
            supporting = _normalized_skill_list(candidate.get("supporting_skills_if_any"))
            rebuilt_touch = build_problem_born_touch_for_skill(
                state,
                skill_name,
                target=touch_target,
                supporting=supporting,
            )
            rebuilt_program = (
                project_bound_program_shape(rebuilt_touch)
                if isinstance(rebuilt_touch, dict)
                else None
            )
            if not (
                isinstance(rebuilt_program, dict)
                and has_explicit_skill_ownership(rebuilt_program)
            ):
                continue
            signature = (
                str(rebuilt_program.get("kind", "")).strip(),
                str(rebuilt_program.get("target", "")).strip(),
                str(rebuilt_program.get("operation", "")).strip(),
            )
            if not all(signature) or signature in seen:
                continue
            seen.add(signature)
            candidates.append(rebuilt_program)

    first_layer_arena = report.get("first_layer_arena")
    push_from_surface(
        first_layer_arena,
        fallback_target=(
            str(first_layer_arena.get("focus_target", "")).strip()
            if isinstance(first_layer_arena, dict)
            else ""
        ),
    )
    skill_competition = report.get("skill_competition")
    push_from_surface(
        skill_competition,
        fallback_target=str(state.get("current_seam", "")).strip(),
    )
    return candidates[:4]


def reopen_stalled_local_competition(
    state: dict,
    path: Path,
) -> tuple[dict, list[dict]]:
    state["primitive_competition_if_any"] = None
    state["primitive_field_if_any"] = None
    refresh_primitive_field_for_current_layer(state, force=True)
    reopened_report = build_report(state, path)
    reopened_candidates = rebuild_reopened_layer_skill_program_candidates(
        state,
        reopened_report,
    )
    return reopened_report, reopened_candidates


def command_bind_local(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    previous_state = load_json(Path(args.previous_state)) if args.previous_state else None

    def mutator(state: dict) -> None:
        existing_primitive_field = state.get("primitive_field_if_any")
        existing_layer_object = ""
        if isinstance(existing_primitive_field, dict):
            existing_layer_object = str(existing_primitive_field.get("layer_object", "")).strip()
        if state.get("bound_program") is not None:
            raise SystemExit("bind-local refused: bound_program already exists")
        if state.get("carrier_handoff_if_any") is not None:
            raise SystemExit("bind-local refused: carrier_handoff_if_any already exists")

        report = build_report(state, path)
        relaxed_problems = [
            problem
            for problem in report["problems"]
            if not (
                state.get("release_veto") is True
                and problem == "bound_program is required while release_veto is active"
            )
        ]
        if relaxed_problems:
            raise SystemExit(
                "bind-local refused: state has blocking problems: "
                + "; ".join(relaxed_problems)
            )

        if state.get("secondary_rival_if_any") is not None and args.allow_rival is not True:
            agenda = report.get("self_check_agenda") or {}
            if agenda.get("focus") != "rival":
                raise SystemExit(
                    "bind-local refused: unresolved rival is still live without a unique rival-local bite"
                )

        asked_medium = str(state.get("asked_medium_surface", "")).strip()
        fresh_blind_first_touch = fresh_blind_problem_first_touch_pending(
            state,
            asked_medium=asked_medium,
        )
        first_layer_arena = report.get("first_layer_arena")
        arena_touch = (
            project_bound_program_shape(first_layer_arena.get("authorized_touch_if_any"))
            if isinstance(first_layer_arena, dict)
            else None
        )
        arena_skill = (
            str(first_layer_arena.get("primary_skill_if_any", "")).strip()
            if isinstance(first_layer_arena, dict)
            else ""
        )
        arena_combo = (
            _normalized_skill_list(first_layer_arena.get("active_skill_combo_if_any"))
            if isinstance(first_layer_arena, dict)
            else []
        )
        skill_winner, skill_combo, skill_program, silence_after_contact = read_skill_authority_program(
            report,
            require_same_carrier=True,
        )
        if (
            fresh_blind_first_touch
            and isinstance(arena_touch, dict)
            and has_explicit_skill_ownership(arena_touch)
        ):
            skill_program = arena_touch
            skill_winner = (
                str(arena_touch.get("owner_skill_if_any", "")).strip()
                or arena_skill
                or skill_winner
            )
            touch_combo = _normalized_skill_list(arena_touch.get("owner_skill_combo_if_any"))
            skill_combo = touch_combo or arena_combo or skill_combo
            silence_after_contact = skill_winner == "精确封口"
        bootstrap_skill_first_entry = fresh_blind_first_entry_skill_program_is_usable(
            skill_program,
            state=state,
        )
        if fresh_blind_first_touch and not bootstrap_skill_first_entry:
            rebuilt_first_entry = rebuild_fresh_blind_first_entry_skill_program(
                state,
                first_layer_arena if isinstance(first_layer_arena, dict) else None,
            )
            if isinstance(rebuilt_first_entry, dict):
                skill_program = rebuilt_first_entry
                skill_winner = str(rebuilt_first_entry.get("owner_skill_if_any", "")).strip() or skill_winner
                skill_combo = extract_explicit_skill_combo(rebuilt_first_entry) or skill_combo
                silence_after_contact = skill_winner == "精确封口"
                bootstrap_skill_first_entry = True
        landed_touch = state.get("landed_next_touch_if_any")
        candidate_program = (
            project_bound_program_shape(landed_touch)
            if isinstance(landed_touch, dict)
            else None
        )
        candidate_from_landed_touch = isinstance(candidate_program, dict)
        if isinstance(candidate_program, dict) and is_generic_runtime_operation(candidate_program):
            candidate_program = None
            candidate_from_landed_touch = False
        if candidate_program is None:
            candidate_program = derive_bound_program_candidate(
                state, [], previous_state=previous_state
            )
        closure_nucleus = report.get("closure_nucleus")
        closure_program = (
            project_bound_program_shape(closure_nucleus.get("current_读出_bite_if_any"))
            if isinstance(closure_nucleus, dict)
            else None
        )
        normalized_asked_medium = _extract_markdown_artifact_hint(
            state.get("asked_medium_surface", "")
        )
        contract = report.get("discipline_contract")
        authorized_bite = (
            project_bound_program_shape(contract.get("authorized_bite"))
            if isinstance(contract, dict)
            else None
        )
        reopened_target = (
            str(authorized_bite.get("target", "")).strip()
            if isinstance(authorized_bite, dict)
            else (
                str((state.get("layer_composition_if_any") or {}).get("controlled_object", "")).strip()
                if isinstance(state.get("layer_composition_if_any"), dict)
                else ""
            )
        ) or str(state.get("current_seam", "")).strip() or str(state.get("current_object", "")).strip()
        direct_closure_bind_allowed = _direct_closure_takeover_allowed(
            report=report,
            state=state,
            asked_medium=normalized_asked_medium,
            direct_closure_signal=True,
            reopened_target=reopened_target,
        )
        layer_next_local_choice = _extract_markdown_artifact_hint(
            (state.get("layer_composition_if_any") or {}).get("next_local_choice", "")
        )
        takeover_gate = state.get("primitive_takeover_gate_if_any")
        if (
            direct_closure_bind_allowed is not True
            and isinstance(candidate_program, dict)
            and program_is_direct_closure_candidate(candidate_program, state)
            and has_explicit_skill_ownership(candidate_program)
            and normalized_asked_medium
            and layer_next_local_choice == normalized_asked_medium
            and isinstance(takeover_gate, dict)
            and str(takeover_gate.get("trigger", "")).strip() == "same_carrier_landing"
        ):
            direct_closure_bind_allowed = True
        if (
            isinstance(closure_program, dict)
            and program_is_direct_closure_candidate(closure_program, state)
            and direct_closure_bind_allowed
            and not fresh_blind_first_touch
            and (
                candidate_program is None
                or is_generic_runtime_operation(candidate_program)
                or not has_explicit_skill_ownership(candidate_program)
                or program_is_direct_closure_candidate(candidate_program, state)
            )
        ):
            candidate_program = closure_program
            candidate_from_landed_touch = False
        elif (
            isinstance(candidate_program, dict)
            and program_is_direct_closure_candidate(candidate_program, state)
            and direct_closure_bind_allowed
            and not fresh_blind_first_touch
            and not program_is_asked_medium_closure(
                candidate_program,
                asked_medium=normalized_asked_medium,
            )
        ):
            promoted_program = dict(candidate_program)
            if normalized_asked_medium:
                promoted_program["target"] = normalized_asked_medium
            promoted_program["success_signal"] = "asked_medium_is_exact_and_executable"
            candidate_program = promoted_program
            candidate_from_landed_touch = False
        if (
            bootstrap_skill_first_entry
            and isinstance(candidate_program, dict)
            and not has_explicit_skill_ownership(candidate_program)
        ):
            candidate_program = skill_program
        if (
            isinstance(candidate_program, dict)
            and isinstance(skill_program, dict)
            and not programs_conflict(candidate_program, skill_program)
            and has_explicit_skill_ownership(skill_program)
            and (not fresh_blind_first_touch or bootstrap_skill_first_entry)
        ):
            candidate_program = (
                align_program_owner_with_authority(
                    candidate_program,
                    skill_program,
                )
                or candidate_program
            )
        if (
            programs_conflict(candidate_program, skill_program)
            and isinstance(candidate_program, dict)
            and isinstance(skill_program, dict)
            and not is_generic_runtime_operation(candidate_program)
            and is_generic_runtime_operation(skill_program)
        ):
            # Respect the earlier primitive-side arbitration when it already
            # found a problem-born bite and the competing skill touch stayed
            # at a generic runtime template.
            pass
        elif programs_conflict(candidate_program, skill_program):
            if (
                program_is_direct_closure_candidate(candidate_program, state)
                and direct_closure_bind_allowed
            ):
                pass
            elif (
                skill_winner
                and isinstance(skill_program, dict)
                and (not fresh_blind_first_touch or bootstrap_skill_first_entry)
            ):
                candidate_program = skill_program
            else:
                raise SystemExit(
                    "bind-local refused: skill authority touch and local primitive bind diverged"
                )
        if (
            candidate_program is None
            and skill_program is not None
            and (not fresh_blind_first_touch or bootstrap_skill_first_entry)
        ):
            candidate_program = skill_program
        if candidate_program is None:
            reopened_report, reopened_candidates = reopen_stalled_local_competition(
                state,
                path,
            )
            report = reopened_report
            skill_winner, skill_combo, skill_program, silence_after_contact = read_skill_authority_program(
                report,
                require_same_carrier=True,
            )
            if len(reopened_candidates) == 1:
                candidate_program = reopened_candidates[0]
            if candidate_program is None:
                candidate_program = derive_bound_program_candidate(
                    state,
                    [],
                    previous_state=previous_state,
                )
            if (
                candidate_program is None
                and skill_program is not None
                and has_explicit_skill_ownership(skill_program)
            ):
                candidate_program = skill_program
        candidate_handoff = derive_handoff_candidate(state, [])

        if candidate_program is not None and candidate_handoff is not None:
            explicit_skill_owner = bool(skill_winner and isinstance(skill_program, dict))
            if not explicit_skill_owner:
                raise SystemExit(
                    "bind-local refused: same-carrier bind and thinner-carrier handoff are both concrete; "
                    "use rebind-local explicitly if thinner-carrier authority should take over"
                )

        if candidate_program is not None:
            landed_owner = (
                str(candidate_program.get("owner_skill_if_any", "")).strip()
                if candidate_from_landed_touch and isinstance(candidate_program, dict)
                else ""
            )
            landed_combo = (
                _normalized_skill_list(candidate_program.get("owner_skill_combo_if_any"))
                if candidate_from_landed_touch and isinstance(candidate_program, dict)
                else []
            )
            persisted_skill_winner = skill_winner
            if landed_owner:
                persisted_skill_winner = landed_owner
                skill_program = candidate_program
                silence_after_contact = landed_owner == "精确封口"
                event_skill_combo = landed_combo or ([landed_owner] if landed_owner else [])
            else:
                event_skill_combo = list(skill_combo)
            takeover_gate = state.get("primitive_takeover_gate_if_any")
            candidate_owner = str(candidate_program.get("owner_skill_if_any", "")).strip()
            candidate_combo = _normalized_skill_list(
                candidate_program.get("owner_skill_combo_if_any")
            )
            if (
                candidate_owner
                and candidate_combo
                and candidate_owner in candidate_combo
                and not is_generic_runtime_operation(candidate_program)
            ):
                persisted_skill_winner = candidate_owner
                event_skill_combo = candidate_combo[:]
            if (
                isinstance(takeover_gate, dict)
                and str(takeover_gate.get("trigger", "")).strip() == "same_carrier_landing"
                and candidate_owner
                and candidate_owner != skill_winner
                and not is_generic_runtime_operation(candidate_program)
            ):
                persisted_skill_winner = candidate_owner
                skill_program = candidate_program
                silence_after_contact = candidate_owner == "精确封口"
                if candidate_combo:
                    event_skill_combo = candidate_combo[:]
            if not has_explicit_skill_ownership(candidate_program):
                inherited_owner, inherited_combo, _ = infer_program_ownership_from_report(
                    state,
                    path,
                    candidate_program,
                )
                candidate_program = (
                    attach_program_owner_metadata(
                        candidate_program,
                        owner_skill=inherited_owner or persisted_skill_winner,
                        owner_combo=inherited_combo or event_skill_combo,
                    )
                    or candidate_program
                )
                candidate_owner = str(candidate_program.get("owner_skill_if_any", "")).strip()
                candidate_combo = _normalized_skill_list(
                    candidate_program.get("owner_skill_combo_if_any")
                )
                if (
                    candidate_owner
                    and candidate_combo
                    and candidate_owner in candidate_combo
                    and not is_generic_runtime_operation(candidate_program)
                ):
                    persisted_skill_winner = candidate_owner
                    event_skill_combo = candidate_combo[:]
            event_reason = str(
                (report.get("discipline_contract") or {}).get("reason", "")
            ).strip() or "one current-layer skill combination has compressed the object enough to bind one concrete local bite"
            promoted_refusal = promoted_skill_gate_refusal(
                report,
                winning_skill=skill_winner,
                foreground_program=candidate_program,
            )
            if promoted_refusal:
                raise SystemExit(f"bind-local refused: {promoted_refusal}")
            recoil_refusal = first_recoil_refusal(
                candidate_program,
                report,
                state=state,
                winning_skill=skill_winner,
            )
            if recoil_refusal:
                raise SystemExit(f"bind-local refused: {recoil_refusal}")
            direct_closure_candidate = program_is_direct_closure_candidate(
                candidate_program,
                state,
            ) and direct_closure_bind_allowed
            probe_refusal = (
                ""
                if direct_closure_candidate
                else unbound_probe_refusal(candidate_program, report)
            )
            if probe_refusal:
                raise SystemExit(f"bind-local refused: {probe_refusal}")
            overreach_refusal = (
                ""
                if direct_closure_candidate
                else probe_overreach_refusal(
                    candidate_program,
                    report,
                    state=state,
                    winning_skill=skill_winner,
                )
            )
            if overreach_refusal:
                raise SystemExit(f"bind-local refused: {overreach_refusal}")
            first_entry_refusal = first_entry_读出_owner_refusal(
                candidate_program,
                report,
                state=state,
                winning_skill=skill_winner,
            )
            if first_entry_refusal:
                raise SystemExit(f"bind-local refused: {first_entry_refusal}")
            asked_medium_short_circuit = first_entry_asked_medium_short_circuit_refusal(
                candidate_program,
                report,
                state=state,
                winning_skill=skill_winner,
            )
            if asked_medium_short_circuit:
                raise SystemExit(f"bind-local refused: {asked_medium_short_circuit}")
            takeover_refusal = primitive_takeover_recomposition_refusal(
                candidate_program,
                report,
                state=state,
            )
            if takeover_refusal:
                raise SystemExit(f"bind-local refused: {takeover_refusal}")
            if (
                is_generic_runtime_operation(candidate_program)
                and not (
                    fresh_blind_same_carrier_first_entry(candidate_program, state=state)
                    and has_explicit_skill_ownership(candidate_program)
                )
            ):
                raise SystemExit(
                    "bind-local refused: candidate local bite stayed at a generic runtime template "
                    "instead of a problem-born action"
                )
            if program_has_meta_narration(candidate_program):
                raise SystemExit(
                    "bind-local refused: candidate local bite stayed at control/meta narration "
                    "instead of a concrete problem-born action"
                )
            if not has_explicit_skill_ownership(candidate_program):
                raise SystemExit(
                    "bind-local refused: candidate local bite had no explicit skill owner/combo on the bite itself"
                )
            candidate_program = (
                normalize_direct_asked_medium_closure_owner(
                    candidate_program,
                    asked_medium=normalized_asked_medium,
                    preferred_owner=persisted_skill_winner,
                    preferred_combo=event_skill_combo,
                )
                or candidate_program
            )
            normalized_candidate_owner = str(
                candidate_program.get("owner_skill_if_any", "")
            ).strip()
            normalized_candidate_combo = _normalized_skill_list(
                candidate_program.get("owner_skill_combo_if_any")
            )
            if (
                normalized_candidate_owner
                and normalized_candidate_combo
                and normalized_candidate_owner in normalized_candidate_combo
            ):
                persisted_skill_winner = normalized_candidate_owner
                event_skill_combo = normalized_candidate_combo[:]
            state["bound_program"] = candidate_program
            reset_output_materialization_for_new_local_move(state)
            state["layer_composition_if_any"] = build_layer_composition_state_payload(
                state,
                surface="bound_program",
                authorized_bite=candidate_program,
                skill_winner=persisted_skill_winner,
                skill_combo=event_skill_combo,
                reason=event_reason,
                must_bind_local_bite=False,
                must_spend_handoff=False,
                layer_object=str(state.get("current_object", "")).strip(),
                controlled_object=str(candidate_program.get("target", "")).strip(),
                current_seam=str(state.get("current_seam", "")).strip(),
                current_debt=str(state.get("current_debt", "")).strip(),
                next_local_choice=infer_next_layer_choice_for_bound_program(
                    state,
                    report,
                    candidate_program,
                ),
                gap_object=str(((report.get("gap_object") or {}).get("object", ""))).strip(),
                transition_change=f"bound {str(candidate_program.get('kind', '')).strip()} on {str(candidate_program.get('target', '')).strip()}",
                lighting_if_any=_report_skill_lighting(report),
            )
            state["landed_next_touch_if_any"] = None
            clear_primitive_takeover_gate(state)
            agenda = derive_local_agenda_for_program(
                state,
                candidate_program,
                winning_skill=skill_winner,
                report=report,
            )
            candidate_gate = derive_gate_binding_candidate(
                state,
                [],
                agenda_override=agenda,
                winning_skill_override=persisted_skill_winner,
                skill_combo_override=event_skill_combo,
            )
            if isinstance(candidate_gate, dict):
                state["gate_binding_if_any"] = candidate_gate
            maybe_cool_post_touch_surfaces(
                state,
                candidate_program,
                winning_skill=skill_winner,
                silence_after_contact=silence_after_contact,
            )
            preserve_existing_layer_field = bool(
                isinstance(existing_primitive_field, dict)
                and existing_layer_object
                and existing_layer_object == str(candidate_program.get("target", "")).strip()
                and existing_layer_object != str(state.get("asked_medium_surface", "")).strip()
                and skill_winner != "精确封口"
            )
            refresh_primitive_field_for_current_layer(
                state,
                agenda_override=agenda,
                force=not preserve_existing_layer_field,
            )
            return

        if candidate_handoff is not None and args.allow_handoff:
            state["carrier_handoff_if_any"] = candidate_handoff
            reset_output_materialization_for_new_local_move(state)
            arm_primitive_takeover_gate(
                state,
                trigger="thinner_carrier_handoff",
                note="carrier authority moved; one explicit primitive-bound bite should land before ordinary continuation resumes",
            )
            refresh_primitive_field_for_current_layer(
                state,
                handoff_override=candidate_handoff,
                force=True,
            )
            materialize_handoff_layer_authority(
                state,
                path,
                candidate_handoff,
                reason="carrier authority moved; the thinner carrier now owns one explicit spend-side bite",
            )
            return

        if candidate_handoff is not None and args.allow_handoff is not True:
            raise SystemExit(
                "bind-local refused: thinner-carrier reselection is concrete; use rebind-local or pass --allow-handoff"
            )

        raise SystemExit("bind-local refused: no unique local bite became concrete enough to bind")

    state = mutate_state(path, mutator, command_name="bind-local")
    dump(state)
    return 0


def command_rebind_local(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if state.get("carrier_handoff_if_any") is not None:
            raise SystemExit("rebind-local refused: carrier_handoff_if_any already exists")

        report = build_report(state, path)
        blocking = [
            problem
            for problem in report["problems"]
            if problem != "bound_program is required while release_veto is active"
        ]
        if blocking:
            raise SystemExit(
                "rebind-local refused: state has blocking problems: " + "; ".join(blocking)
            )

        if state.get("bound_program") is not None and args.force is not True:
            raise SystemExit(
                "rebind-local refused: bound_program still exists; clear or override it explicitly"
            )

        probe_state = json.loads(json.dumps(state))
        if args.force is True:
            probe_state["bound_program"] = None
            probe_state["gate_binding_if_any"] = None

        candidate_handoff = derive_handoff_candidate(probe_state, [])
        if candidate_handoff is None:
            raise SystemExit("rebind-local refused: no unique thinner-carrier handoff is concrete enough")

        state["bound_program"] = None
        state["gate_binding_if_any"] = None
        state["landed_next_touch_if_any"] = None
        state["carrier_handoff_if_any"] = candidate_handoff
        reset_output_materialization_for_new_local_move(state)
        refresh_primitive_field_for_current_layer(
            state,
            handoff_override=candidate_handoff,
            force=True,
        )
        arm_primitive_takeover_gate(
            state,
            trigger="thinner_carrier_handoff",
            note="carrier authority moved; one explicit primitive-bound bite should land before ordinary continuation resumes",
        )
        materialize_handoff_layer_authority(
            state,
            path,
            candidate_handoff,
            reason="carrier authority moved; the thinner carrier now owns one explicit spend-side bite",
        )
        if not isinstance(state.get("layer_composition_if_any"), dict):
            raise SystemExit(
                "rebind-local refused: thinner-carrier handoff was concrete, "
                "but no explicit lit spend-side layer could be materialized"
            )

    state = mutate_state(path, mutator, command_name="rebind-local")
    dump(state)
    return 0


def command_spend_local(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        if state.get("bound_program") is not None:
            raise SystemExit("spend-local refused: bound_program already exists")

        handoff = state.get("carrier_handoff_if_any")
        if not isinstance(handoff, dict):
            raise SystemExit("spend-local refused: no explicit carrier_handoff_if_any is live")

        report = build_report(state, path)
        blocking = [
            problem
            for problem in report["problems"]
            if problem != "bound_program is required while release_veto is active"
        ]
        if blocking:
            raise SystemExit(
                "spend-local refused: state has blocking problems: " + "; ".join(blocking)
            )

        skill_winner, skill_combo, skill_program, silence_after_contact = read_skill_authority_program(
            report,
            require_same_carrier=False,
        )
        interlayer_bridge = read_interlayer_discharge_bridge(report)
        primitive_program = derive_primitive_program_candidate(state, [])
        if (
            programs_conflict(primitive_program, skill_program)
            and isinstance(primitive_program, dict)
            and isinstance(skill_program, dict)
            and not is_generic_runtime_operation(primitive_program)
            and is_generic_runtime_operation(skill_program)
        ):
            candidate_program = primitive_program
        elif programs_conflict(primitive_program, skill_program):
            if (
                isinstance(interlayer_bridge, dict)
                and programs_conflict(
                    interlayer_bridge.get("spend_first_program"),
                    skill_program,
                )
                and not programs_conflict(
                    interlayer_bridge.get("spend_first_program"),
                    primitive_program,
                )
            ):
                candidate_program = interlayer_bridge["spend_first_program"]
                if interlayer_bridge.get("keep_closure_authority") is True:
                    skill_winner = "精确封口"
                else:
                    skill_winner = ""
                silence_after_contact = False
            else:
                raise SystemExit(
                    "spend-local refused: skill authority touch and thinner-carrier primitive spend diverged"
                )
        else:
            candidate_program = skill_program or primitive_program

        if candidate_program is None and isinstance(interlayer_bridge, dict):
            candidate_program = interlayer_bridge.get("spend_first_program")
            if interlayer_bridge.get("keep_closure_authority") is True:
                skill_winner = "精确封口"
            else:
                skill_winner = ""
            silence_after_contact = False

        if candidate_program is None:
            reopened_report, reopened_candidates = reopen_stalled_local_competition(
                state,
                path,
            )
            report = reopened_report
            skill_winner, skill_combo, skill_program, silence_after_contact = read_skill_authority_program(
                report,
                require_same_carrier=False,
            )
            interlayer_bridge = read_interlayer_discharge_bridge(report)
            primitive_program = derive_primitive_program_candidate(state, [])
            if len(reopened_candidates) == 1:
                candidate_program = reopened_candidates[0]
            elif isinstance(primitive_program, dict):
                candidate_program = primitive_program
            elif isinstance(skill_program, dict) and has_explicit_skill_ownership(skill_program):
                candidate_program = skill_program

        if candidate_program is None:
            raise SystemExit(
                "spend-local refused: no unique next primitive touch is concrete enough"
            )
        if (
            isinstance(candidate_program, dict)
            and isinstance(skill_program, dict)
            and not programs_conflict(candidate_program, skill_program)
            and has_explicit_skill_ownership(skill_program)
        ):
            candidate_program = (
                align_program_owner_with_authority(
                    candidate_program,
                    skill_program,
                )
                or candidate_program
            )
        candidate_owner = str(candidate_program.get("owner_skill_if_any", "")).strip()
        candidate_combo = _normalized_skill_list(
            candidate_program.get("owner_skill_combo_if_any")
        )
        persisted_skill_winner = skill_winner
        if (
            candidate_owner
            and candidate_combo
            and candidate_owner in candidate_combo
            and not is_generic_runtime_operation(candidate_program)
        ):
            persisted_skill_winner = candidate_owner
            event_skill_combo = candidate_combo[:]
        else:
            event_skill_combo = list(skill_combo)
        if not has_explicit_skill_ownership(candidate_program):
            inherited_owner, inherited_combo, _ = infer_program_ownership_from_report(
                state,
                path,
                candidate_program,
            )
            candidate_program = (
                attach_program_owner_metadata(
                    candidate_program,
                    owner_skill=inherited_owner or persisted_skill_winner,
                    owner_combo=inherited_combo or event_skill_combo,
                )
                or candidate_program
            )
            candidate_owner = str(candidate_program.get("owner_skill_if_any", "")).strip()
            candidate_combo = _normalized_skill_list(
                candidate_program.get("owner_skill_combo_if_any")
            )
            if (
                candidate_owner
                and candidate_combo
                and candidate_owner in candidate_combo
                and not is_generic_runtime_operation(candidate_program)
            ):
                persisted_skill_winner = candidate_owner
                event_skill_combo = candidate_combo[:]
        event_reason = str(
            (report.get("discipline_contract") or {}).get("reason", "")
        ).strip() or "the thinner carrier is already explicit, so one current-layer combination now owns the next local bite"
        promoted_refusal = promoted_skill_gate_refusal(
            report,
            winning_skill=skill_winner,
            foreground_program=candidate_program,
        )
        if promoted_refusal:
            raise SystemExit(f"spend-local refused: {promoted_refusal}")
        recoil_refusal = first_recoil_refusal(
            candidate_program,
            report,
            state=state,
            winning_skill=skill_winner,
        )
        if recoil_refusal:
            raise SystemExit(f"spend-local refused: {recoil_refusal}")
        probe_refusal = unbound_probe_refusal(candidate_program, report)
        if probe_refusal:
            raise SystemExit(f"spend-local refused: {probe_refusal}")
        overreach_refusal = probe_overreach_refusal(
            candidate_program,
            report,
            state=state,
            winning_skill=skill_winner,
        )
        if overreach_refusal:
            raise SystemExit(f"spend-local refused: {overreach_refusal}")
        first_entry_refusal = first_entry_读出_owner_refusal(
            candidate_program,
            report,
            state=state,
            winning_skill=skill_winner,
        )
        if first_entry_refusal:
            raise SystemExit(f"spend-local refused: {first_entry_refusal}")
        asked_medium_short_circuit = first_entry_asked_medium_short_circuit_refusal(
            candidate_program,
            report,
            state=state,
            winning_skill=skill_winner,
        )
        if asked_medium_short_circuit:
            raise SystemExit(f"spend-local refused: {asked_medium_short_circuit}")
        takeover_refusal = primitive_takeover_recomposition_refusal(
            candidate_program,
            report,
            state=state,
        )
        if takeover_refusal:
            raise SystemExit(f"spend-local refused: {takeover_refusal}")
        if is_generic_runtime_operation(candidate_program):
            raise SystemExit(
                "spend-local refused: candidate local bite stayed at a generic runtime template "
                "instead of a problem-born action"
            )
        if program_has_meta_narration(candidate_program):
            raise SystemExit(
                "spend-local refused: candidate local bite stayed at control/meta narration "
                "instead of a concrete problem-born action"
            )
        if not has_explicit_skill_ownership(candidate_program):
            raise SystemExit(
                "spend-local refused: candidate local bite had no explicit skill owner/combo on the bite itself"
            )

        target_object = handoff.get("to_object")
        if isinstance(target_object, str) and target_object.strip():
            previous_object = state.get("current_object")
            state["current_object"] = target_object
            if not state.get("current_seam") or state.get("current_seam") == previous_object:
                state["current_seam"] = target_object
        post_report = build_report(state, path)

        state["bound_program"] = candidate_program
        reset_output_materialization_for_new_local_move(state)
        state["layer_composition_if_any"] = build_layer_composition_state_payload(
            state,
            surface="bound_program",
            authorized_bite=candidate_program,
            skill_winner=persisted_skill_winner,
            skill_combo=event_skill_combo,
            reason=event_reason,
            must_bind_local_bite=False,
            must_spend_handoff=False,
            layer_object=str(state.get("current_object", "")).strip(),
            controlled_object=str(candidate_program.get("target", "")).strip(),
            current_seam=str(state.get("current_seam", "")).strip(),
            current_debt=str(state.get("current_debt", "")).strip(),
            next_local_choice=infer_next_layer_choice_for_bound_program(
                state,
                post_report,
                candidate_program,
            ),
            gap_object=str(((post_report.get("gap_object") or {}).get("object", ""))).strip(),
            transition_change=f"spent handoff into {str(candidate_program.get('target', '')).strip()}",
            lighting_if_any=_report_skill_lighting(post_report),
        )
        state["carrier_handoff_if_any"] = None
        state["landed_next_touch_if_any"] = None
        clear_primitive_takeover_gate(state)

        agenda = derive_local_agenda_for_program(
            state,
            candidate_program,
            winning_skill=skill_winner,
            report=report,
        )
        candidate_gate = derive_gate_binding_candidate(
            state,
            [],
            agenda_override=agenda,
            winning_skill_override=persisted_skill_winner,
            skill_combo_override=event_skill_combo,
        )
        state["gate_binding_if_any"] = candidate_gate if isinstance(candidate_gate, dict) else None
        maybe_cool_post_touch_surfaces(
            state,
            candidate_program,
            winning_skill=skill_winner,
            silence_after_contact=silence_after_contact,
        )
        refresh_primitive_field_for_current_layer(
            state,
            agenda_override=agenda,
            force=False,
        )

    state = mutate_state(path, mutator, command_name="spend-local")
    if asked_medium_materialization_ready(state):
        def materialize_mutator(materialize_state: dict) -> None:
            materialize_asked_medium_if_ready(materialize_state, state_path=path)
        state = mutate_state(
            path,
            materialize_mutator,
            command_name="materialize-asked-medium",
        )
    dump(state)
    return 0


def command_execute_local(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> None:
        bound_program = project_bound_program_shape(state.get("bound_program"))
        if not isinstance(bound_program, dict):
            raise SystemExit("execute-local refused: no bound_program is live")

        asked_medium = str(state.get("asked_medium_surface", "")).strip()
        if program_is_asked_medium_closure(bound_program, asked_medium=asked_medium):
            raise SystemExit(
                "execute-local refused: the live bound_program is asked-medium closure; "
                "materialize or release it instead of recording same-carrier execution"
            )
        output_status = state.get("output_status")
        if (
            isinstance(output_status, dict)
            and output_status.get("touched") is True
            and same_carrier_landing_is_ready(state, bound_program)
        ):
            raise SystemExit(
                "execute-local refused: this live bound_program was already touched once; "
                "land-local, spend-local, bind-local, or tear it instead of continuing probe-like work on the same bite"
            )

        worked_step = str(args.worked_step or "").strip()
        if not worked_step:
            raise SystemExit("execute-local refused: --worked-step is required")
        visible_refusal = _visible_skill_expression_refusal(worked_step, state=state)
        if visible_refusal:
            raise SystemExit(visible_refusal)
        result_only_refusal = _worked_step_result_only_refusal(
            worked_step,
            state=state,
        )
        if result_only_refusal:
            raise SystemExit(result_only_refusal)

        evidence_location = "inline"
        evidence_kind = "inline_text"
        if getattr(args, "output_file", None):
            output_path = resolve_state_relative_output_path(path, str(args.output_file))
            asked_medium_path = asked_medium_output_path(state=state, state_path=path)
            if asked_medium_path is not None and output_path == asked_medium_path:
                raise SystemExit(
                    "execute-local refused: direct writes to the asked medium bypass "
                    "skill-serialized closure; write evidence elsewhere and let "
                    "materialize-asked-medium seal the final answer"
                )
            reserved_output_refusal = fresh_blind_generic_output_refusal(
                output_path,
                state=state,
                state_path=path,
                allow_markdown_paths=[path.with_name("evidence.md")],
            )
            if reserved_output_refusal:
                raise SystemExit(f"execute-local refused: {reserved_output_refusal}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                worked_step if worked_step.endswith("\n") else worked_step + "\n",
                encoding="utf-8",
            )
            evidence_location = str(output_path)
            evidence_kind = "file"

        summary = str(args.summary or "").strip()
        if not summary:
            summary = worked_step.replace("\n", " ").strip()
        if len(summary) > 240:
            summary = summary[:237].rstrip() + "..."

        state["materialization_evidence"] = {
            "kind": evidence_kind,
            "location": evidence_location,
            "summary": summary,
            "worked_step": worked_step,
        }

        output = state.setdefault("output_status", {})
        output["touched"] = True
        output["cosmetic_only"] = (
            args.cosmetic_only
            if getattr(args, "cosmetic_only", None) is not None
            else False
        )
        output["contains_unsupported"] = (
            args.contains_unsupported
            if getattr(args, "contains_unsupported", None) is not None
            else _contains_unsupported_text(worked_step)
        )
        output["contains_placeholder"] = (
            args.contains_placeholder
            if getattr(args, "contains_placeholder", None) is not None
            else _contains_placeholder_text(worked_step)
        )
        output["final_artifact_materialized"] = False

    state = mutate_state(path, mutator, command_name="execute-local")
    dump(state)
    return 0


def command_land_local(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def mutator(state: dict) -> dict | None:
        apply_same_carrier_landing(
            state,
            path,
            next_object=str(args.current_object or "").strip(),
            next_seam=str(args.current_seam or "").strip(),
            next_debt=str(args.current_debt or "").strip(),
            next_bite=str(args.next_bite or "").strip(),
        )
        return

    state = mutate_state(path, mutator, command_name="land-local")
    dump(state)
    return 0


def command_materialize_asked_medium(args: argparse.Namespace) -> int:
    path = Path(args.state_file)

    def materialize_mutator(state: dict) -> None:
        if not asked_medium_materialization_ready(state):
            promote_report_derived_exact_closure(state, state_path=path)
        if not materialize_asked_medium_if_ready(state, state_path=path):
            raise SystemExit(
                "materialize-asked-medium refused: fresh blind asked medium still lacks exact closure ownership "
                "or skill-serialized materialization readiness"
            )

    state = mutate_state(
        path,
        materialize_mutator,
        command_name="materialize-asked-medium",
    )
    dump(state)
    return 0


def command_trace(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    state = load_state(path)
    require_fresh_blind_asked_medium_surface(
        state,
        context="trace refused",
    )
    evidence = build_runtime_evidence(path)
    events = load_runtime_events(path)
    if args.format == "json":
        payload = {
            "state_file": str(path),
            "runtime_evidence": evidence,
            "events": events,
        }
        text = json.dumps(payload, ensure_ascii=True, indent=2) + "\n"
    elif args.format == "skill-markdown":
        text = render_runtime_skill_trace_markdown(path)
        if not text.endswith("\n"):
            text += "\n"
    elif args.format == "solve-markdown":
        text = render_runtime_solve_steps_markdown(path)
        if not text.endswith("\n"):
            text += "\n"
    else:
        text = render_runtime_trace_markdown(path)
        if not text.endswith("\n"):
            text += "\n"

    if args.output:
        output_path = resolve_state_relative_output_path(path, str(args.output))
        asked_medium_path = asked_medium_output_path(state=state, state_path=path)
        allowed_markdown_paths: list[Path] = []
        if args.format == "markdown":
            allowed_markdown_paths.append(trace_markdown_path(path))
        elif args.format == "skill-markdown":
            allowed_markdown_paths.append(skill_trace_markdown_path(path))
        elif args.format == "solve-markdown":
            allowed_markdown_paths.append(solve_trace_markdown_path(path))
        reserved_output_refusal = fresh_blind_generic_output_refusal(
            output_path,
            state=state,
            state_path=path,
            allow_asked_medium=True,
            allow_markdown_paths=allowed_markdown_paths,
        )
        if reserved_output_refusal:
            raise SystemExit(f"trace refused: {reserved_output_refusal}")
        if (
            _fresh_blind_mode_active_from_state(state)
            and asked_medium_path is not None
            and _normalized_existing_path_text(str(output_path))
            == _normalized_existing_path_text(str(asked_medium_path))
        ):
            if args.format != "solve-markdown":
                raise SystemExit(
                    "trace refused: fresh blind asked medium may only be written from canonical "
                    "solve-markdown export"
                )
            if not _asked_medium_trace_materialization_allowed(state, state_path=path, events=events):
                raise SystemExit(
                    "trace refused: fresh blind asked medium still lacks exact closure ownership "
                    "or canonical solve-markdown authority"
                )
        if (
            args.format == "solve-markdown"
            and asked_medium_path is not None
            and _normalized_existing_path_text(str(output_path))
            == _normalized_existing_path_text(str(asked_medium_path))
        ):
            def materialize_trace_export(materialize_state: dict) -> None:
                asked_medium = _extract_markdown_artifact_hint(
                    materialize_state.get("asked_medium_surface", "")
                )
                program = project_bound_program_shape(materialize_state.get("bound_program"))
                if not (
                    isinstance(program, dict)
                    and program_is_asked_medium_closure(program, asked_medium=asked_medium)
                ):
                    promote_report_derived_exact_closure(materialize_state, state_path=path)
                if not materialize_asked_medium_if_ready(materialize_state, state_path=path):
                    raise SystemExit(
                        "trace refused: fresh blind asked medium still lacks exact closure ownership "
                        "or skill-serialized materialization readiness"
                    )

            mutate_state(
                path,
                materialize_trace_export,
                command_name="materialize-asked-medium",
            )
            text = output_path.read_text(encoding="utf-8")
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    if args.format == "skill-markdown":
        return 0 if _skill_trace_export_allowed(events) else 1
    if args.format == "solve-markdown":
        return 0 if _solve_trace_export_allowed(path, events) else 1
    return 0 if evidence["event_count"] > 0 else 1


def add_common_core_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--current-object")
    parser.add_argument("--current-seam")
    parser.add_argument("--current-debt")
    parser.add_argument("--next-bite")
    parser.add_argument("--asked-medium-surface")
    parser.add_argument("--revocation-handle")
    parser.add_argument("--uncertainty-mode", choices=["high", "low", "mixed", "unknown"])
    parser.add_argument("--primary-slot")


def add_common_output_arguments(parser: argparse.ArgumentParser) -> None:
    add_bool_argument(parser, "--touched", "touched")
    add_bool_argument(parser, "--cosmetic-only", "cosmetic_only")
    add_bool_argument(parser, "--contains-unsupported", "contains_unsupported")
    add_bool_argument(parser, "--contains-placeholder", "contains_placeholder")
    add_bool_argument(
        parser,
        "--final-artifact-materialized",
        "final_artifact_materialized",
    )


def add_materialization_evidence_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--evidence-kind",
        choices=["file", "command", "check", "artifact", "inline_text"],
    )
    parser.add_argument("--evidence-location")
    parser.add_argument("--evidence-summary")


def add_bool_argument(parser: argparse.ArgumentParser, name: str, dest: str) -> None:
    parser.add_argument(name, dest=dest, action="store_true")
    parser.add_argument(f"--no-{name[2:]}", dest=dest, action="store_false")
    parser.set_defaults(**{dest: None})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Thin mutable control-state tool for Wu Boshi Perspective. "
            "It only edits one tiny runtime state; it does not generate routes."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a new runtime state file")
    init_parser.add_argument("state_file")
    add_common_core_arguments(init_parser)
    add_common_output_arguments(init_parser)
    add_materialization_evidence_arguments(init_parser)
    init_parser.add_argument("--kind", choices=["write", "check", "读出", "见证"])
    init_parser.add_argument("--target")
    init_parser.add_argument("--operation")
    init_parser.add_argument("--success-signal")
    init_parser.add_argument("--allow-release", action="store_true")
    init_parser.add_argument(
        "--fresh-blind-project-skills-on",
        action="store_true",
        help=(
            "Mark this state as a fresh blind project-skills-on bootstrap so later "
            "runtime inspection can require a new live transition before counting participation"
        ),
    )
    init_parser.set_defaults(func=command_init)

    bootstrap_blind_parser = subparsers.add_parser(
        "bootstrap-blind",
        help="Create a fresh blind project-skills-on runtime state with thin defaults",
    )
    bootstrap_blind_parser.add_argument("state_file")
    bootstrap_blind_parser.add_argument("--current-object", required=True)
    bootstrap_blind_parser.add_argument("--current-debt", required=True)
    bootstrap_blind_parser.add_argument("--next-bite", required=True)
    bootstrap_blind_parser.add_argument("--asked-medium-surface", required=True)
    bootstrap_blind_parser.add_argument("--current-seam")
    bootstrap_blind_parser.add_argument("--revocation-handle")
    bootstrap_blind_parser.add_argument("--uncertainty-mode")
    bootstrap_blind_parser.add_argument("--primary-slot")
    bootstrap_blind_parser.set_defaults(func=command_bootstrap_blind)

    bootstrap_blind_here_parser = subparsers.add_parser(
        "bootstrap-blind-here",
        help=(
            "Create a fresh blind project-skills-on runtime_state.json in the current "
            "working directory with thin defaults"
        ),
    )
    bootstrap_blind_here_parser.add_argument("--current-object", required=True)
    bootstrap_blind_here_parser.add_argument("--current-debt", required=True)
    bootstrap_blind_here_parser.add_argument("--next-bite", required=True)
    bootstrap_blind_here_parser.add_argument("--asked-medium-surface", required=True)
    bootstrap_blind_here_parser.add_argument("--current-seam")
    bootstrap_blind_here_parser.add_argument("--revocation-handle")
    bootstrap_blind_here_parser.add_argument("--uncertainty-mode")
    bootstrap_blind_here_parser.add_argument("--primary-slot")
    bootstrap_blind_here_parser.set_defaults(func=command_bootstrap_blind_here)

    show_parser = subparsers.add_parser("show", help="Print a runtime state file")
    show_parser.add_argument("state_file")
    show_parser.set_defaults(func=command_show)

    core_parser = subparsers.add_parser("set-core", help="Update core live-state fields")
    core_parser.add_argument("state_file")
    add_common_core_arguments(core_parser)
    add_bool_argument(core_parser, "--release-veto", "release_veto")
    core_parser.set_defaults(func=command_set_core)

    program_parser = subparsers.add_parser(
        "program",
        help="Set or clear one tiny bound executable program on the current carrier",
    )
    program_parser.add_argument("mode", choices=["set", "clear"])
    program_parser.add_argument("state_file")
    program_parser.add_argument("--kind", choices=["write", "check", "读出", "见证"])
    program_parser.add_argument("--target")
    program_parser.add_argument("--operation")
    program_parser.add_argument("--success-signal")
    program_parser.set_defaults(func=command_program)

    gate_parser = subparsers.add_parser(
        "gate",
        help="Internal/debug: set or clear one tiny monitor-paid gate binding on the current carrier",
    )
    gate_parser.add_argument("mode", choices=["set", "clear"])
    gate_parser.add_argument("state_file")
    gate_parser.add_argument(
        "--source-focus",
        choices=["seam", "rival", "carrier", "asked_medium"],
    )
    gate_parser.add_argument("--source-target")
    gate_parser.add_argument("--demoted-continuation")
    gate_parser.add_argument(
        "--authority-until",
        choices=[
            "same_carrier_change",
            "hostile_见证",
            "exact_check",
            "asked_medium_failure",
        ],
    )
    gate_parser.add_argument("--kind", choices=["write", "check", "读出", "见证"])
    gate_parser.add_argument("--target")
    gate_parser.add_argument("--operation")
    gate_parser.add_argument("--success-signal")
    gate_parser.set_defaults(func=command_gate)

    primitive_parser = subparsers.add_parser(
        "primitive",
        help="Internal/debug: set or clear one tiny current-layer primitive field on the live carrier",
    )
    primitive_parser.add_argument("mode", choices=["set", "clear"])
    primitive_parser.add_argument("state_file")
    primitive_parser.add_argument("--layer-object")
    primitive_parser.add_argument("--active-primitive", action="append")
    primitive_parser.add_argument("--tie-break-check")
    primitive_parser.add_argument("--why-now")
    primitive_parser.add_argument(
        "--selection-basis",
        choices=["explicit_hint", "tie_break", "agenda_hint", "text_fallback"],
    )
    primitive_parser.add_argument(
        "--evidence-basis",
        choices=["explicit_hint", "state_见证", "cheap_check", "lexical_hint", "mixed"],
    )
    primitive_parser.set_defaults(func=command_primitive)

    competition_parser = subparsers.add_parser(
        "competition",
        help="Internal/debug: set or clear one tiny explicit primitive competition object on the current layer",
    )
    competition_parser.add_argument("mode", choices=["set", "clear"])
    competition_parser.add_argument("state_file")
    competition_parser.add_argument("--layer-object")
    competition_parser.add_argument(
        "--candidate",
        action="append",
        help="Format: primitive|touch_target|expected_local_gain",
    )
    competition_parser.add_argument("--separating-check")
    competition_parser.add_argument("--winner-if-any")
    competition_parser.set_defaults(func=command_competition)

    evidence_parser = subparsers.add_parser(
        "evidence",
        help="Set or clear thin materialization evidence for a released state",
    )
    evidence_parser.add_argument("mode", choices=["set", "clear"])
    evidence_parser.add_argument("state_file")
    add_materialization_evidence_arguments(evidence_parser)
    evidence_parser.set_defaults(func=command_evidence)

    output_parser = subparsers.add_parser("set-output", help="Update asked-medium/output flags")
    output_parser.add_argument("state_file")
    add_common_output_arguments(output_parser)
    output_parser.set_defaults(func=command_set_output)

    marker_parser = subparsers.add_parser("markers", help="Manage unresolved markers")
    marker_parser.add_argument("mode", choices=["add", "remove", "clear"])
    marker_parser.add_argument("state_file")
    marker_parser.add_argument("marker", nargs="*")
    marker_parser.set_defaults(func=command_marker)

    rival_parser = subparsers.add_parser("rival", help="Set or clear the warm constructive rival")
    rival_parser.add_argument("mode", choices=["set", "clear"])
    rival_parser.add_argument("state_file")
    rival_parser.add_argument("--object")
    rival_parser.add_argument("--debt")
    rival_parser.add_argument("--bite")
    rival_parser.add_argument("--separating-advantage")
    rival_parser.set_defaults(func=command_rival)

    handoff_parser = subparsers.add_parser(
        "handoff",
        help="Internal/debug: set or clear one tiny carrier-change / primitive-reselection handoff",
    )
    handoff_parser.add_argument("mode", choices=["set", "clear"])
    handoff_parser.add_argument("state_file")
    handoff_parser.add_argument(
        "--trigger",
        choices=[
            "same_carrier_change",
            "hostile_见证",
            "exact_check",
            "asked_medium_failure",
            "residue_inherited",
        ],
    )
    handoff_parser.add_argument("--from-slot")
    handoff_parser.add_argument("--to-object")
    handoff_parser.add_argument("--winning-pressure")
    handoff_parser.add_argument("--cooled-pressure")
    handoff_parser.add_argument("--why-local")
    handoff_parser.add_argument("--active-pressure", action="append")
    handoff_parser.add_argument("--primitive-hint", action="append")
    handoff_parser.add_argument("--cheap-check")
    handoff_parser.set_defaults(func=command_handoff)

    residue_parser = subparsers.add_parser("residue", help="Manage thin memory residue")
    residue_parser.add_argument("mode", choices=["add", "clear"])
    residue_parser.add_argument("state_file")
    residue_parser.add_argument("--kind")
    residue_parser.add_argument("--description")
    add_bool_argument(residue_parser, "--replayable", "replayable")
    residue_parser.set_defaults(func=command_residue)

    check_parser = subparsers.add_parser("check", help="Run the runtime guard against a state file")
    check_parser.add_argument("state_file")
    check_parser.set_defaults(func=command_check)

    bind_parser = subparsers.add_parser(
        "bind-local",
        help=(
            "Project one already-local monitoring state into exactly one tiny local action "
            "without turning it into a workflow"
        ),
    )
    bind_parser.add_argument("state_file")
    bind_parser.add_argument(
        "--previous-state",
        help="Optional immediately previous snapshot used only to detect same-carrier stall",
    )
    bind_parser.add_argument(
        "--allow-handoff",
        action="store_true",
        help="Allow one tiny carrier_handoff_if_any only when no bound_program can be bound",
    )
    bind_parser.add_argument(
        "--allow-rival",
        action="store_true",
        help="Allow binding a rival-local 见证 program when the self-check focus is already rival",
    )
    bind_parser.set_defaults(func=command_bind_local)

    rebind_parser = subparsers.add_parser(
        "rebind-local",
        help=(
            "Project one already-local thinner-carrier primitive reselection into exactly one "
            "tiny carrier_handoff_if_any"
        ),
    )
    rebind_parser.add_argument("state_file")
    rebind_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacing a still-present bound_program when thinner-carrier authority must take over",
    )
    rebind_parser.set_defaults(func=command_rebind_local)

    spend_parser = subparsers.add_parser(
        "spend-local",
        help=(
            "Explicit one-shot: collapse one live thinner-carrier handoff into exactly one "
            "next primitive bound_program on that new layer"
        ),
    )
    spend_parser.add_argument("state_file")
    spend_parser.set_defaults(func=command_spend_local)

    materialize_parser = subparsers.add_parser(
        "materialize-asked-medium",
        help=(
            "Write the exact asked-medium artifact once a live closure bite and recorded execution "
            "make materialization concrete"
        ),
    )
    materialize_parser.add_argument("state_file")
    materialize_parser.set_defaults(func=command_materialize_asked_medium)

    execute_parser = subparsers.add_parser(
        "execute-local",
        help=(
            "Record one real same-carrier execution step for the live bound_program "
            "so the run no longer stops at a descriptive operation string"
        ),
    )
    execute_parser.add_argument("state_file")
    execute_parser.add_argument(
        "--worked-step",
        help="The concrete mathematical/code step that was actually carried out on the live bound_program",
    )
    execute_parser.add_argument(
        "--summary",
        help="Optional short summary of what the execution step established",
    )
    execute_parser.add_argument(
        "--output-file",
        help="Optional state-relative file path where the concrete worked step should be written",
    )
    add_bool_argument(execute_parser, "--cosmetic-only", "cosmetic_only")
    add_bool_argument(execute_parser, "--contains-unsupported", "contains_unsupported")
    add_bool_argument(execute_parser, "--contains-placeholder", "contains_placeholder")
    execute_parser.set_defaults(func=command_execute_local)

    land_parser = subparsers.add_parser(
        "land-local",
        help=(
            "Explicit one-shot: record that one same-carrier structural bite really changed "
            "the live object, then reopen the next thinner local layer without turning it into a workflow"
        ),
    )
    land_parser.add_argument("state_file")
    land_parser.add_argument("--current-object")
    land_parser.add_argument("--current-seam")
    land_parser.add_argument("--current-debt")
    land_parser.add_argument("--next-bite")
    land_parser.set_defaults(func=command_land_local)

    trace_parser = subparsers.add_parser(
        "trace",
        help=(
            "Export the sidecar runtime event trace. "
            "This is evidence of actual runtime consumption, not a free-form solve story."
        ),
    )
    trace_parser.add_argument("state_file")
    trace_parser.add_argument(
        "--format",
        choices=["markdown", "skill-markdown", "solve-markdown", "json"],
        default="markdown",
    )
    trace_parser.add_argument("--output")
    trace_parser.set_defaults(func=command_trace)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "rival" and args.mode == "set":
        missing = [
            name
            for name in ["object", "debt", "bite", "separating_advantage"]
            if getattr(args, name) in (None, "")
        ]
        if missing:
            raise SystemExit(f"missing rival fields: {', '.join(missing)}")

    if args.command == "residue" and args.mode == "add":
        if args.kind is None or args.description is None or args.replayable is None:
            raise SystemExit("residue add requires --kind, --description, and replayable flag")

    if args.command == "markers" and args.mode in {"add", "remove"} and not args.marker:
        raise SystemExit("markers add/remove requires at least one marker")

    if args.command == "program" and args.mode == "set":
        require_bound_program_arguments(args)

    if args.command == "gate" and args.mode == "set":
        require_gate_binding_arguments(args)
        require_bound_program_arguments(args)

    if args.command == "evidence" and args.mode == "set":
        require_materialization_evidence_arguments(args)

    if args.command == "handoff" and args.mode == "set":
        missing = [
            flag
            for flag, attr in [
                ("--trigger", "trigger"),
                ("--from-slot", "from_slot"),
                ("--to-object", "to_object"),
                ("--winning-pressure", "winning_pressure"),
                ("--why-local", "why_local"),
            ]
            if getattr(args, attr) in (None, "")
        ]
        if missing:
            raise SystemExit("handoff set requires: " + ", ".join(missing))
        if args.active_pressure is not None and not 1 <= len(args.active_pressure) <= 2:
            raise SystemExit("handoff set allows one or two --active-pressure values")
        if args.primitive_hint is not None and not 1 <= len(args.primitive_hint) <= 2:
            raise SystemExit("handoff set allows one or two --primitive-hint values")
        invalid_hints = [
            value for value in (args.primitive_hint or []) if not is_allowed_primitive_token(value)
        ]
        if invalid_hints:
            raise SystemExit(
                "handoff set contains invalid --primitive-hint values: "
                + ", ".join(invalid_hints)
            )

    if args.command == "competition" and args.mode == "set":
        if getattr(args, "layer_object", None) in (None, ""):
            raise SystemExit("competition set requires --layer-object")
        raw_candidates = getattr(args, "candidate", None) or []
        if not 1 <= len(raw_candidates) <= 2:
            raise SystemExit("competition set requires one or two --candidate values")
        seen_primitives: set[str] = set()
        for raw_candidate in raw_candidates:
            parts = raw_candidate.split("|", 2)
            if len(parts) != 3 or not all(part.strip() for part in parts):
                raise SystemExit(
                    "competition set candidates must use format primitive|touch_target|expected_local_gain"
                )
            primitive = canonicalize_primitive_token(parts[0].strip())
            if primitive not in ALLOWED_PRIMITIVES:
                raise SystemExit(f"competition set candidate primitive is invalid: {primitive}")
            if primitive in seen_primitives:
                raise SystemExit(f"competition set candidate primitive repeats: {primitive}")
            seen_primitives.add(primitive)
        raw_winner = getattr(args, "winner_if_any", None)
        winner = canonicalize_primitive_token(raw_winner)
        if raw_winner is not None and not winner:
            raise SystemExit("competition set --winner-if-any is invalid")
        if winner and winner not in seen_primitives:
            raise SystemExit("competition set --winner-if-any must match one candidate primitive")

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

