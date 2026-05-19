#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from itertools import combinations
from pathlib import Path

ALLOWED_PRIMITIVES = {
    "反证",
    "第一裂缝",
    "重编码",
    "对称",
    "极限边界",
    "守恒",
    "投影",
    "赋值",
    "反向",
    "图像",
    "见证",
    "状态拆分",
    "相容",
    "读出",
    "向量差读出",
    "公共值压缩",
    "容器到截面",
    "面积到线读出",
    "匹配替代概率",
    "格点选排",
    "不算而比",
    "点积投影",
    "规范归一化",
    "投影读出",
    "主导机制读出",
    "局部缝控制整体",
    "定义即直接读出",
    "对称消元",
    "边界找路",
    "先调模型后推导",
    "特殊值探针",
    "函数原型匹配",
}

ALLOWED_PRIMITIVE_TAKEOVER_TRIGGERS = {
    "same_carrier_landing",
    "thinner_carrier_handoff",
}

ALLOWED_SKILLS = {
    *ALLOWED_PRIMITIVES,
    "抓本质",
    "最终控制者",
    "外壳怀疑",
    "更薄载体重选",
    "精确封口",
    "反问",
    "监督",
    "元认知",
    "中枢控制",
    "后脑守卫",
    "奖惩塑形",
}

PUBLIC_LIT_SKILLS = {
    *ALLOWED_PRIMITIVES,
}
PUBLIC_CONTROL_SKILLS = {
    skill for skill in ALLOWED_SKILLS if skill not in PUBLIC_LIT_SKILLS
}

ALLOWED_RESIDUE_KINDS = {
    "competition_texture",
    "distrust_bias",
    "见证_readiness",
    "读出_sensitivity",
    "boundary_residue",
}

PROBE_LIKE_PRIMITIVES = {
    "反证",
    "第一裂缝",
    "见证",
    "赋值",
    "特殊值探针",
    "不算而比",
    "边界找路",
    "局部缝控制整体",
    "极限边界",
    "对称",
    "对称消元",
}

READOUT_LIKE_PRIMITIVES = {
    "读出",
    "定义即直接读出",
    "投影读出",
    "主导机制读出",
    "向量差读出",
}

COMPRESSION_HEAVY_PRIMITIVES = {
    "公共值压缩",
    *READOUT_LIKE_PRIMITIVES,
}

TRANSFORM_SUPPORT_PRIMITIVES = {
    "重编码",
    "对称",
    "对称消元",
    "投影",
    "反向",
    "图像",
    "状态拆分",
    "相容",
    "守恒",
    "规范归一化",
    "容器到截面",
    "匹配替代概率",
    "格点选排",
    "函数原型匹配",
    "先调模型后推导",
    "点积投影",
    "面积到线读出",
}

GENERIC_CLOSURE_HELPER_PRIMITIVES = {
    "投影",
    "读出",
    "定义即直接读出",
    "投影读出",
    "主导机制读出",
    "向量差读出",
    "公共值压缩",
    "精确封口",
}

STRUCTURE_NUCLEUS_PRIMITIVES = {
    "对称",
    "对称消元",
    "极限边界",
    "第一裂缝",
    "守恒",
    "赋值",
    "图像",
    "状态拆分",
    "边界找路",
    "特殊值探针",
    "局部缝控制整体",
    "相容",
    "反向",
}

STRUCTURAL_WAKE_SKILLS = {
    "抓本质",
    "最终控制者",
    "更薄载体重选",
    "精确封口",
}

INTERNAL_CANDIDATE_LIGHT_LIMIT = 48
GENERIC_COMBO_SUPPORT_LIMIT = 4
MAX_GENERIC_COMBO_CANDIDATES = 96

PERSISTED_STATE_KEYS = {
    "current_object",
    "current_seam",
    "current_debt",
    "next_bite",
    "asked_medium_surface",
    "revocation_handle",
    "uncertainty_mode",
    "primary_slot",
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
    "bootstrap_context",
    "release_veto",
    "unresolved_markers",
    "output_status",
    "memory_residue",
}

DERIVED_READOUT_ONLY_KEYS = {
    "control_bridge",
    "control_signals",
    "closure_nucleus",
    "gap_object",
    "resume_bridge",
    "discipline_contract",
    "skill_field",
    "skill_competition",
    "skill_inhibition",
    "skill_authority_bridge",
    "skill_lighting_surface",
    "skill_coaching_surface",
    "probe_discipline",
    "interlayer_discharge_bridge",
    "inhibition_state",
    "first_layer_arena",
    "layer_composition",
    "runtime_evidence",
    "self_check_agenda",
}

PRIMITIVE_ALIAS_GROUPS = {
    "对称": {
        "对称",
        "balance",
        "symmetrize the target",
        "quotient by 对称",
        "对称",
        "平衡",
    },
    "反证": {
        "反证",
        "impossibility",
        "route killer",
        "illegal structure",
        "反证",
        "矛盾",
    },
    "第一裂缝": {
        "first crack",
        "singularity",
        "branch switch",
        "weakest seam",
        "explosion point",
        "第一裂缝",
        "裂点",
        "奇点爆破",
    },
    "重编码": {
        "re-encoding",
        "重编码",
        "dimension shift",
        "change carrier",
        "representation replacement",
        "重编码",
        "换载体",
        "换表征",
    },
    "极限边界": {
        "limit boundary",
        "limit",
        "boundary",
        "degeneration",
        "edge case",
        "first crack",
        "tangency",
        "极限",
        "边界",
        "极限边界",
        "退化",
    },
    "守恒": {
        "守恒",
        "bookkeeping",
        "ledger",
        "aggregate controls target",
        "collapse to aggregate",
        "守恒",
        "总量控制",
    },
    "投影": {
        "投影",
        "cross section",
        "project",
        "投影",
        "截面",
    },
    "赋值": {
        "赋值",
        "special value",
        "parameter compression",
        "anchor calibration",
        "赋值",
        "特殊值",
        "锚点",
    },
    "反向": {
        "反向",
        "反向 design",
        "反向",
        "逆推",
    },
    "图像": {
        "图像",
        "diagram",
        "visual externalization",
        "图像",
        "画图",
        "图",
    },
    "见证": {
        "见证",
        "separating check",
        "probe with 见证",
        "见证",
        "证伪点",
    },
    "状态拆分": {
        "state split",
        "split",
        "quotient",
        "finite state",
        "exact cover",
        "freeze into static skeleton",
        "分类讨论",
        "状态拆分",
        "拆状态",
    },
    "相容": {
        "相容",
        "merge",
        "coexistence",
        "collapse to relation",
        "相容",
        "兼容",
        "共存",
    },
    "读出": {
        "读出",
        "direct 读出",
        "读出",
        "直接读出",
    },
    "向量差读出": {
        "vector difference 读出",
        "vector-difference-读出",
    },
    "公共值压缩": {
        "common value compression",
        "common-value-compression",
        "common value parameter compression",
        "common-value-parameter-compression",
        "collapse to latent controller",
        "latent controller",
    },
    "容器到截面": {
        "container to cross section",
        "container-to-cross-section",
        "container to section",
    },
    "面积到线读出": {
        "area to line 读出",
        "area-to-line-读出",
    },
    "匹配替代概率": {
        "matching instead of probability",
        "matching-instead-of-probability",
    },
    "格点选排": {
        "grid selection permutation",
        "grid-selection-permutation",
    },
    "不算而比": {
        "compare without calculating",
        "compare-without-calculating",
    },
    "点积投影": {
        "dot product range by 投影",
        "dot product 投影",
    },
    "规范归一化": {
        "canonical normalization",
        "canonical-normalization",
        "normalize",
    },
    "投影读出": {
        "投影 读出",
        "投影-读出",
    },
    "主导机制读出": {
        "dominant mechanism 读出",
        "dominant-mechanism-读出",
    },
    "局部缝控制整体": {
        "local seam controls global",
        "local-seam-controls-global",
    },
    "定义即直接读出": {
        "definition as direct 读出",
        "definition-as-direct-读出",
        "read out directly",
    },
    "对称消元": {
        "对称 as variable killer",
        "对称-as-variable-killer",
    },
    "边界找路": {
        "boundary as route finder",
        "boundary-as-route-finder",
        "push to boundary",
    },
    "先调模型后推导": {
        "model calling before derivation",
        "model-calling-before-derivation",
    },
    "特殊值探针": {
        "special value probing",
        "special-value-probing",
        "special value",
        "landmark value",
        "extreme case method",
        "guess then verify",
        "guess-and-verify",
    },
    "函数原型匹配": {
        "function archetype matching",
        "function-archetype-matching",
    },
}

SKILL_DISPLAY_NAME_ZH = {
    "赋值": "赋值",
    "相容": "相容",
    "守恒": "守恒",
    "反证": "反证",
    "反问": "反问",
    "精确封口": "精确封口",
    "最终控制者": "最终控制者",
    "第一裂缝": "第一裂缝",
    "函数原型匹配": "函数原型匹配",
    "抓本质": "抓本质",
    "后脑守卫": "后脑守卫",
    "极限边界": "极限边界",
    "元认知": "元认知",
    "图像": "图像",
    "投影": "投影",
    "读出": "读出",
    "重编码": "重编码",
    "反向": "反向",
    "奖惩塑形": "奖惩塑形",
    "外壳怀疑": "外壳怀疑",
    "状态拆分": "状态拆分",
    "监督": "监督",
    "对称": "对称",
    "更薄载体重选": "更薄载体重选",
    "见证": "见证",
    "中枢控制": "中枢控制",
    "向量差读出": "向量差读出",
    "公共值压缩": "公共值压缩",
    "容器到截面": "容器到截面",
    "面积到线读出": "面积到线读出",
    "匹配替代概率": "匹配替代概率",
    "格点选排": "格点选排",
    "不算而比": "不算而比",
    "点积投影": "点积投影",
    "规范归一化": "规范归一化",
    "投影读出": "投影读出",
    "主导机制读出": "主导机制读出",
    "局部缝控制整体": "局部缝控制整体",
    "定义即直接读出": "定义即直接读出",
    "对称消元": "对称消元",
    "边界找路": "边界找路",
    "先调模型后推导": "先调模型后推导",
    "特殊值探针": "特殊值探针",
}

SKILL_ALIAS_GROUPS = {
    "抓本质": {
        "grasp essence",
        "find essence",
        "抓本质",
    },
    "最终控制者": {
        "final owner",
        "find final owner",
        "最终控制者",
        "找最终控制者",
    },
    "外壳怀疑": {
        "shell suspicion",
        "suspect the shell",
        "怀疑表面外壳",
    },
    "更薄载体重选": {
        "thinner carrier reselection",
        "find smaller carrier",
        "先找更小载体",
        "reselection",
    },
    "精确封口": {
        "exact closure",
        "asked medium closure",
        "闭口",
        "精确封口",
    },
    "反问": {
        "counter question",
        "反问",
    },
    "监督": {
        "监督",
        "监督",
        "关门",
    },
    "元认知": {
        "元认知",
        "元认知",
    },
    "中枢控制": {
        "central control",
        "中枢",
    },
    "后脑守卫": {
        "hindbrain guard",
        "后脑",
    },
    "奖惩塑形": {
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
    return re.sub(r"[\W_]+", " ", lowered, flags=re.UNICODE).strip()


PRIMITIVE_ALIAS_TO_CANONICAL = {}
for primitive in sorted(ALLOWED_PRIMITIVES):
    PRIMITIVE_ALIAS_TO_CANONICAL[normalize_primitive_token(primitive)] = primitive
for primitive in sorted(ALLOWED_PRIMITIVES):
    for alias in PRIMITIVE_ALIAS_GROUPS.get(primitive, set()):
        normalized_alias = normalize_primitive_token(alias)
        if normalized_alias and normalized_alias not in PRIMITIVE_ALIAS_TO_CANONICAL:
            PRIMITIVE_ALIAS_TO_CANONICAL[normalized_alias] = primitive

SKILL_ALIAS_TO_CANONICAL = {}
for skill in sorted(ALLOWED_SKILLS):
    SKILL_ALIAS_TO_CANONICAL[normalize_primitive_token(skill)] = skill
for skill in sorted(ALLOWED_SKILLS):
    for alias in SKILL_ALIAS_GROUPS.get(skill, set()):
        normalized_alias = normalize_primitive_token(alias)
        if normalized_alias and normalized_alias not in SKILL_ALIAS_TO_CANONICAL:
            SKILL_ALIAS_TO_CANONICAL[normalized_alias] = skill


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


def get_skill_display_name_zh(skill: object) -> str:
    canonical = canonicalize_skill_token(skill)
    if not canonical:
        return ""
    return SKILL_DISPLAY_NAME_ZH.get(canonical, canonical)


def _append_skill_labels_zh(payload: dict | None) -> dict | None:
    if not isinstance(payload, dict):
        return payload
    localized = dict(payload)
    list_fields = [
        "active_skills",
        "full_active_skills",
        "background_control_skills_if_any",
        "candidate_skills_if_any",
        "supporting_skills_if_any",
        "coactive_skills_if_any",
    ]
    scalar_fields = [
        "skill",
        "authority_skill_if_any",
        "bound_skill_if_any",
        "closure_authority_skill_if_any",
        "winning_skill_if_any",
        "winning_control_skill_if_any",
        "lit_skill_if_any",
        "lit_control_skill_if_any",
        "false_first_skill_if_any",
        "comparison_skill_if_any",
        "primary_skill_if_any",
    ]
    for key in list_fields:
        values = localized.get(key)
        if isinstance(values, list):
            labels = [get_skill_display_name_zh(value) for value in values]
            labels = [label for label in labels if label]
            if labels:
                localized[f"{key}_zh"] = labels
    for key in scalar_fields:
        label = get_skill_display_name_zh(localized.get(key))
        if label:
            localized[f"{key}_zh"] = label
    role_split = localized.get("role_split_if_any")
    if isinstance(role_split, dict):
        localized["role_split_if_any"] = _append_skill_labels_zh(role_split)
    candidates = localized.get("candidates")
    if isinstance(candidates, list):
        localized["candidates"] = [
            _append_skill_labels_zh(candidate) if isinstance(candidate, dict) else candidate
            for candidate in candidates
        ]
    competing = localized.get("competing_routes_if_any")
    if isinstance(competing, list):
        projected_routes = []
        for route in competing:
            if isinstance(route, dict):
                projected_routes.append(_append_skill_labels_zh(route))
            else:
                projected_routes.append(route)
        localized["competing_routes_if_any"] = projected_routes
    return localized


def is_public_lit_skill(value: object) -> bool:
    return canonicalize_skill_token(value) in PUBLIC_LIT_SKILLS


def is_public_control_skill(value: object) -> bool:
    return canonicalize_skill_token(value) in PUBLIC_CONTROL_SKILLS


def collapse_public_lit_skill_split(
    winning_skill: object,
    executable_owner_skill: object,
) -> tuple[str, str]:
    winning = canonicalize_skill_token(winning_skill)
    executable = canonicalize_skill_token(executable_owner_skill)
    if (
        winning
        and executable
        and winning != executable
        and winning in PUBLIC_LIT_SKILLS
        and executable in PUBLIC_LIT_SKILLS
    ):
        return executable, ""
    return winning, executable


def _filter_public_lit_skills(values: object, *, limit: int | None = None) -> list[str]:
    if not isinstance(values, list):
        return []
    filtered: list[str] = []
    for value in values:
        canonical = canonicalize_skill_token(value)
        if canonical and canonical in PUBLIC_LIT_SKILLS and canonical not in filtered:
            filtered.append(canonical)
            if limit is not None and len(filtered) >= limit:
                break
    return filtered


def _filter_public_control_skills(values: object, *, limit: int | None = None) -> list[str]:
    if not isinstance(values, list):
        return []
    filtered: list[str] = []
    for value in values:
        canonical = canonicalize_skill_token(value)
        if canonical and canonical in PUBLIC_CONTROL_SKILLS and canonical not in filtered:
            filtered.append(canonical)
            if limit is not None and len(filtered) >= limit:
                break
    return filtered


def _sanitize_public_skill_field(payload: dict | None) -> dict | None:
    if not isinstance(payload, dict):
        return payload
    sanitized = dict(payload)
    active = _filter_public_lit_skills(payload.get("active_skills"))
    full_active = _filter_public_lit_skills(payload.get("full_active_skills"))
    background_control = _filter_public_control_skills(
        payload.get("background_skills_if_any")
    )
    if active:
        sanitized["active_skills"] = active
    else:
        sanitized.pop("active_skills", None)
    if full_active:
        sanitized["full_active_skills"] = full_active
    else:
        sanitized.pop("full_active_skills", None)
    if background_control:
        sanitized["background_control_skills_if_any"] = background_control
    sanitized.pop("background_skills_if_any", None)
    authority_skill = canonicalize_skill_token(payload.get("authority_skill_if_any"))
    if authority_skill not in PUBLIC_LIT_SKILLS:
        sanitized.pop("authority_skill_if_any", None)
    bound_skill = canonicalize_skill_token(payload.get("bound_skill_if_any"))
    if bound_skill not in PUBLIC_LIT_SKILLS:
        sanitized.pop("bound_skill_if_any", None)
    closure_skill = canonicalize_skill_token(payload.get("closure_authority_skill_if_any"))
    if closure_skill in PUBLIC_CONTROL_SKILLS:
        sanitized["closure_authority_skill_if_any"] = closure_skill
    elif not closure_skill:
        sanitized.pop("closure_authority_skill_if_any", None)
    return _append_skill_labels_zh(sanitized)


def _sanitize_public_skill_competition(payload: dict | None) -> dict | None:
    if not isinstance(payload, dict):
        return payload
    sanitized = dict(payload)
    candidates: list[dict] = []
    for candidate in payload.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        skill = canonicalize_skill_token(candidate.get("skill"))
        if skill not in PUBLIC_LIT_SKILLS:
            continue
        projected = dict(candidate)
        projected["skill"] = skill
        supporting = _filter_public_lit_skills(
            candidate.get("supporting_skills_if_any"),
            limit=3,
        )
        if supporting:
            projected["supporting_skills_if_any"] = supporting
        else:
            projected.pop("supporting_skills_if_any", None)
        rank = projected.get("projected_gain_rank")
        if isinstance(rank, int):
            projected["projected_progress_percent_if_selected"] = projected_progress_percent_for_gain_rank(rank)
        candidates.append(projected)
    sanitized["candidates"] = candidates
    coactive = _filter_public_lit_skills(payload.get("coactive_skills_if_any"), limit=8)
    if coactive:
        sanitized["coactive_skills_if_any"] = coactive
    else:
        sanitized.pop("coactive_skills_if_any", None)
    winning = canonicalize_skill_token(payload.get("winning_skill_if_any"))
    if winning in PUBLIC_LIT_SKILLS:
        sanitized["winning_skill_if_any"] = winning
    else:
        sanitized.pop("winning_skill_if_any", None)
        if winning in PUBLIC_CONTROL_SKILLS:
            sanitized["winning_control_skill_if_any"] = winning
    winning_rank = sanitized.get("winning_projected_gain_rank")
    if isinstance(winning_rank, int):
        sanitized["winning_projected_progress_percent_if_selected"] = projected_progress_percent_for_gain_rank(
            winning_rank
        )
    return _append_skill_labels_zh(sanitized)


def _sanitize_public_skill_lighting_surface(payload: dict | None) -> dict | None:
    if not isinstance(payload, dict):
        return payload
    sanitized = dict(payload)
    lit_skill = canonicalize_skill_token(payload.get("lit_skill_if_any"))
    if lit_skill in PUBLIC_LIT_SKILLS:
        sanitized["lit_skill_if_any"] = lit_skill
    else:
        sanitized.pop("lit_skill_if_any", None)
        if lit_skill in PUBLIC_CONTROL_SKILLS:
            sanitized["lit_control_skill_if_any"] = lit_skill
    for key in ["candidate_skills_if_any", "supporting_skills_if_any"]:
        filtered = _filter_public_lit_skills(payload.get(key), limit=8)
        if filtered:
            sanitized[key] = filtered
        else:
            sanitized.pop(key, None)
    false_first = canonicalize_skill_token(payload.get("false_first_skill_if_any"))
    if false_first in PUBLIC_LIT_SKILLS:
        sanitized["false_first_skill_if_any"] = false_first
    else:
        sanitized.pop("false_first_skill_if_any", None)
    role_split = payload.get("role_split_if_any")
    if isinstance(role_split, dict):
        projected_role_split = dict(role_split)
        primary = canonicalize_skill_token(role_split.get("primary_skill_if_any"))
        if primary in PUBLIC_LIT_SKILLS:
            projected_role_split["primary_skill_if_any"] = primary
        else:
            projected_role_split.pop("primary_skill_if_any", None)
        supporting = _filter_public_lit_skills(
            role_split.get("supporting_skills_if_any"),
            limit=8,
        )
        if supporting:
            projected_role_split["supporting_skills_if_any"] = supporting
        else:
            projected_role_split.pop("supporting_skills_if_any", None)
        sanitized["role_split_if_any"] = projected_role_split
    comparison = canonicalize_skill_token(payload.get("comparison_skill_if_any"))
    if comparison in PUBLIC_LIT_SKILLS:
        sanitized["comparison_skill_if_any"] = comparison
    else:
        sanitized.pop("comparison_skill_if_any", None)
    competing = payload.get("competing_routes_if_any")
    if isinstance(competing, list):
        projected_routes: list[dict] = []
        for route in competing:
            if not isinstance(route, dict):
                continue
            skill = canonicalize_skill_token(route.get("skill"))
            if skill not in PUBLIC_LIT_SKILLS:
                continue
            projected = dict(route)
            projected["skill"] = skill
            projected_routes.append(projected)
        if projected_routes:
            sanitized["competing_routes_if_any"] = projected_routes
        else:
            sanitized.pop("competing_routes_if_any", None)
    return _append_skill_labels_zh(sanitized)


RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"
PRIMITIVE_SEMANTICS_PATH = RUNTIME_DIR / "primitive_semantics.json"

BUILTIN_PRIMITIVE_SEMANTICS = {
    "反证": {
        "family_type": "generic",
        "mechanism": "Kill a fake route by showing it creates an illegal or impossible structure earlier than full derivation.",
        "controller_question": "What local consequence would make this route impossible inside the original problem family?",
        "wake_when": [
            "A candidate interpretation looks coherent but may be structurally illegal",
            "One early impossibility could delete a large false branch",
        ],
        "cheapest_honest_touch": "Push one route to the first impossible consequence and use it to kill that branch.",
        "anti_pattern": "Do not save 反证 for late verification if one early impossible consequence already decides the route.",
        "coactivate_with": ["图像", "见证", "第一裂缝"],
    },
    "第一裂缝": {
        "family_type": "generic",
        "mechanism": "Locate the earliest seam, branch switch, or singular point where a wrong route breaks first.",
        "controller_question": "Where does the current route crack first if it is wrong?",
        "wake_when": [
            "The object looks stable except at one branch seam or singular place",
            "A first failure point would expose the real controller cheaply",
        ],
        "cheapest_honest_touch": "Write the first branch switch, singular seam, or instability point and test the route there.",
        "anti_pattern": "Do not keep broad smooth reasoning alive when one first-crack seam already governs truth.",
        "coactivate_with": ["极限边界", "见证", "赋值"],
        "claim_requires_partner": True,
    },
    "重编码": {
        "family_type": "generic",
        "mechanism": "Change representation when the current carrier is still too thick, so the same burden survives on a thinner encoding.",
        "controller_question": "What re-encoding would preserve the task while deleting surface burden?",
        "wake_when": [
            "The first useful representation has become inertia",
            "A thinner carrier exists but has not yet been made explicit",
        ],
        "cheapest_honest_touch": "Rewrite the live burden on one thinner carrier and keep the same controller visible there.",
        "anti_pattern": "Do not re-encode just to sound deeper; the same burden must survive more honestly.",
        "coactivate_with": ["投影", "状态拆分", "赋值"],
        "claim_requires_partner": True,
    },
}


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
    if isinstance(semantics, dict) and semantics:
        return semantics
    fallback = BUILTIN_PRIMITIVE_SEMANTICS.get(canonical, {})
    return fallback if isinstance(fallback, dict) else {}


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
    "抓本质": {
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
    "最终控制者": {
        "family_type": "control",
        "mechanism": "Bias attention toward the last quantity, carrier, or interface that still has real authority over correctness.",
        "controller_question": "What still has the final right to preserve, reject, or cash out this line?",
        "wake_when": [
            "Several local truths remain but one final controller still decides release",
        ],
        "cheapest_honest_touch": "Name one exact owner and one event that would revoke it.",
        "anti_pattern": "Do not stop at a true local mechanism if a stronger final owner still governs release.",
    },
    "外壳怀疑": {
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
    "更薄载体重选": {
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
    "精确封口": {
        "family_type": "control",
        "mechanism": "Force the live line to cash into exact asked-medium contact rather than near-miss commentary.",
        "controller_question": "What exact closure object or asked-medium 读出 is still unpaid?",
        "wake_when": [
            "Release is blocked by one concrete closure debt",
        ],
        "cheapest_honest_touch": "Write one exact 读出 or one executable local closure bite.",
        "anti_pattern": "Do not confuse closure-shaped language with closure.",
    },
    "反问": {
        "family_type": "control",
        "mechanism": "Keep one smallest hostile falsifier live before commentary regains comfort.",
        "controller_question": "What one cheap question could kill fake progress first?",
        "wake_when": [
            "Several nearby lines still feel plausible",
        ],
        "cheapest_honest_touch": "Write one separating 见证 or exact check.",
        "anti_pattern": "Do not multiply questions when one falsifier is enough.",
    },
    "监督": {
        "family_type": "control",
        "mechanism": "Temporarily demote drift so one local owner can keep authority until change or kill.",
        "controller_question": "What continuation should lose permission until one local event lands?",
        "wake_when": [
            "Language is outrunning object change",
        ],
        "cheapest_honest_touch": "Name one owner, one demoted continuation, and one gate-until event.",
        "anti_pattern": "Do not turn 监督 into a phase machine.",
    },
    "元认知": {
        "family_type": "control",
        "mechanism": "Re-check owner, carrier, and false essence while keeping the live object small.",
        "controller_question": "What if the current owner or carrier label is slightly wrong?",
        "wake_when": [
            "Control surfaces feel aligned but not yet honest",
        ],
        "cheapest_honest_touch": "Re-name one owner/carrier pair and test whether burden shrinks.",
        "anti_pattern": "Do not reopen broad reflection after the local closure body is already concrete.",
    },
    "中枢控制": {
        "family_type": "control",
        "mechanism": "Bias one local owner strongly enough that nearby lines cool until an actual tear event occurs.",
        "controller_question": "Who currently owns the slot?",
        "wake_when": [
            "Several lines still feel equally foregrounded",
        ],
        "cheapest_honest_touch": "Bind one owner and one revocation handle.",
        "anti_pattern": "Do not centralize what still needs real plurality.",
    },
    "后脑守卫": {
        "family_type": "control",
        "mechanism": "Keep the non-release latch alive and reopen the smallest honest exit when false settlement appears.",
        "controller_question": "What should stop this line from settling too early?",
        "wake_when": [
            "The run is near premature settlement",
        ],
        "cheapest_honest_touch": "Keep one non-release condition explicit on the current layer.",
        "anti_pattern": "Do not keep the guard on after honest materialization has landed.",
    },
    "奖惩塑形": {
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


def extract_markdown_artifact_hint(value: object) -> str:
    text = nonempty_text(value)
    if not text:
        return ""
    match = re.search(r"([A-Za-z0-9._-]+\.md)\b", text)
    return match.group(1) if match else ""


PROGRAM_METADATA_KEYS = (
    "current_layer_object_if_any",
    "controlled_object_if_any",
    "object_transform_if_any",
    "next_object_if_any",
    "step_outline_if_any",
    "skill_phase_if_any",
)


def attach_program_metadata_fields(program: dict, payload: object) -> dict:
    if not isinstance(program, dict) or not isinstance(payload, dict):
        return program
    for key in PROGRAM_METADATA_KEYS:
        value = nonempty_text(payload.get(key))
        if value:
            program[key] = value
    return program


def extract_explicit_skill_combo(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return []
    ordered: list[str] = []
    raw_combo = payload.get("owner_skill_combo_if_any")
    if not isinstance(raw_combo, list) or not raw_combo:
        return []
    for value in raw_combo:
        canonical = canonicalize_skill_token(value)
        if canonical and canonical not in ordered:
            ordered.append(canonical)
    owner_skill = canonicalize_skill_token(payload.get("owner_skill_if_any"))
    if owner_skill and owner_skill not in ordered:
        ordered.insert(0, owner_skill)
    return ordered[:6]


CONTROL_META_SKILLS = {
    "外壳怀疑",
    "抓本质",
    "最终控制者",
    "更薄载体重选",
    "元认知",
    "监督",
    "中枢控制",
    "后脑守卫",
    "奖惩塑形",
    "反问",
}


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
    if state.get("release_veto") is not True:
        problems.append("bound_program requires release_veto to stay active")

    validate_no_extra_keys(
        bound_program,
        {
            "kind",
            "target",
            "operation",
            "success_signal",
            "owner_skill_if_any",
            "owner_skill_combo_if_any",
            *PROGRAM_METADATA_KEYS,
        },
        "bound_program",
        problems,
    )

    for key in ["kind", "target", "operation"]:
        require_nonempty(bound_program, key, problems)

    kind = bound_program.get("kind")
    if isinstance(kind, str) and kind not in {"write", "check", "读出", "见证"}:
        problems.append("bound_program.kind must be write, check, 读出, or 见证")

    success_signal = bound_program.get("success_signal")
    if success_signal is not None and (
        not isinstance(success_signal, str) or not success_signal.strip()
    ):
        problems.append("bound_program.success_signal must be non-empty when present")
    owner_skill = bound_program.get("owner_skill_if_any")
    if owner_skill is not None:
        canonical = canonicalize_skill_token(owner_skill)
        if not canonical:
            problems.append("bound_program.owner_skill_if_any must be one of the allowed skills when present")
    owner_combo = bound_program.get("owner_skill_combo_if_any")
    if state.get("release_veto") is True and owner_combo is None:
        problems.append("bound_program.owner_skill_combo_if_any is required while release_veto is active")
    if owner_combo is not None:
        if not isinstance(owner_combo, list) or not owner_combo:
            problems.append("bound_program.owner_skill_combo_if_any must be a non-empty list when present")
        else:
            for value in owner_combo:
                canonical = canonicalize_skill_token(value)
                if not canonical:
                    problems.append(
                        "bound_program.owner_skill_combo_if_any must contain only allowed skills when present"
                    )
            if owner_skill is not None:
                canonical_owner = canonicalize_skill_token(owner_skill)
                canonical_combo = [
                    canonicalize_skill_token(value)
                    for value in owner_combo
                    if canonicalize_skill_token(value)
                ]
                if canonical_owner and canonical_owner not in canonical_combo:
                    problems.append(
                        "bound_program.owner_skill_combo_if_any must include bound_program.owner_skill_if_any"
                    )
            if state.get("release_veto") is True and owner_skill is None:
                canonical_combo = [
                    canonicalize_skill_token(value)
                    for value in owner_combo
                    if canonicalize_skill_token(value)
                ]
                if not canonical_combo:
                    problems.append(
                        "bound_program must expose at least one explicit local skill in owner_skill_combo_if_any while release_veto is active"
                    )


def validate_layer_composition(state: dict, problems: list[str]) -> None:
    layer = state.get("layer_composition_if_any")
    if layer is None:
        return

    if not isinstance(layer, dict):
        problems.append("layer_composition_if_any must be an object or null")
        return
    if state.get("release_veto") is not True:
        problems.append("layer_composition_if_any requires release_veto to stay active")

    validate_no_extra_keys(
        layer,
        {
            "surface",
            "active_skill_combo_if_any",
            "forbid_ordinary_regrowth",
            "must_bind_local_bite",
            "must_spend_handoff",
            "leading_skill_if_any",
            "reason",
            "authorized_bite",
            "layer_object",
            "controlled_object",
            "current_seam",
            "current_debt",
            "next_local_choice",
            "gap_object",
            "event_owned",
            "transition_change",
            "lighting_if_any",
        },
        "layer_composition_if_any",
        problems,
    )

    require_nonempty(layer, "surface", problems)

    surface = layer.get("surface")
    if isinstance(surface, str) and surface not in {
        "bound_program",
        "carrier_handoff",
        "takeover_recomposition",
        "control_bridge",
        "unknown",
    }:
        problems.append(
            "layer_composition_if_any.surface must be bound_program, carrier_handoff, "
            "takeover_recomposition, control_bridge, or unknown"
        )

    for key in [
        "forbid_ordinary_regrowth",
        "must_bind_local_bite",
        "must_spend_handoff",
        "event_owned",
    ]:
        if key in layer and not isinstance(layer.get(key), bool):
            problems.append(f"layer_composition_if_any.{key} must be boolean")

    for key in [
        "reason",
        "layer_object",
        "controlled_object",
        "current_seam",
        "current_debt",
        "next_local_choice",
        "gap_object",
        "transition_change",
    ]:
        value = layer.get(key)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            problems.append(f"layer_composition_if_any.{key} must be non-empty when present")

    if layer.get("event_owned") is True:
        if not nonempty_text(layer.get("transition_change")):
            problems.append(
                "layer_composition_if_any.event_owned steps must record transition_change"
            )
        surface_name = nonempty_text(surface)
        if surface_name in {"bound_program", "takeover_recomposition"} and not (
            nonempty_text(layer.get("next_local_choice"))
            or nonempty_text(layer.get("gap_object"))
        ):
            problems.append(
                "layer_composition_if_any.event_owned steps must expose next_local_choice or gap_object"
            )

    leading_skill = layer.get("leading_skill_if_any")
    if leading_skill is not None:
        canonical = canonicalize_skill_token(leading_skill)
        if not canonical:
            problems.append(
                "layer_composition_if_any.leading_skill_if_any must be one of the allowed skills when present"
            )

    combo = layer.get("active_skill_combo_if_any")
    if not isinstance(combo, list) or not combo:
        problems.append("layer_composition_if_any.active_skill_combo_if_any must be a non-empty list")
    else:
        for value in combo:
            canonical = canonicalize_skill_token(value)
            if not canonical:
                problems.append(
                    "layer_composition_if_any.active_skill_combo_if_any must contain only allowed skills"
                )

    authorized_bite = layer.get("authorized_bite")
    if authorized_bite is not None:
        if not isinstance(authorized_bite, dict):
            problems.append("layer_composition_if_any.authorized_bite must be an object when present")
        else:
            validate_no_extra_keys(
                authorized_bite,
                {
                    "kind",
                    "target",
                    "operation",
                    "success_signal",
                    "owner_skill_if_any",
                    "owner_skill_combo_if_any",
                    *PROGRAM_METADATA_KEYS,
                },
                "layer_composition_if_any.authorized_bite",
                problems,
            )
            for key in ["kind", "target", "operation"]:
                require_nonempty(authorized_bite, key, problems)
            bite_combo = extract_explicit_skill_combo(authorized_bite)
            if not bite_combo:
                problems.append(
                    "layer_composition_if_any.authorized_bite.owner_skill_combo_if_any must be present"
                )
            elif isinstance(combo, list):
                normalized_layer_combo = [
                    canonicalize_skill_token(value)
                    for value in combo
                    if canonicalize_skill_token(value)
                ]
                if normalized_layer_combo and bite_combo != normalized_layer_combo[: len(bite_combo)] and bite_combo != normalized_layer_combo:
                    problems.append(
                        "layer_composition_if_any.authorized_bite combo must match layer_composition_if_any.active_skill_combo_if_any"
                    )

    lighting = layer.get("lighting_if_any")
    if lighting is not None:
        if not isinstance(lighting, dict):
            problems.append("layer_composition_if_any.lighting_if_any must be an object when present")
        else:
            validate_no_extra_keys(
                lighting,
                {
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
                },
                "layer_composition_if_any.lighting_if_any",
                problems,
            )
            for key in [
                "lit_skill_if_any",
                "false_first_skill_if_any",
                "false_first_label_if_any",
                "false_skill_reason",
                "accountability_nudge_if_any",
                "winning_projected_gain_reason",
                "anti_pipeline_note",
            ]:
                value = lighting.get(key)
                if value is not None and (not isinstance(value, str) or not value.strip()):
                    problems.append(f"layer_composition_if_any.lighting_if_any.{key} must be non-empty when present")
            for key in ["lit_skill_if_any", "comparison_skill_if_any", "false_first_skill_if_any"]:
                value = lighting.get(key)
                if value is not None and not canonicalize_skill_token(value):
                    problems.append(
                        f"layer_composition_if_any.lighting_if_any.{key} must be one of the allowed skills when present"
                    )
            candidate_skills = lighting.get("candidate_skills_if_any")
            if candidate_skills is not None:
                if not isinstance(candidate_skills, list):
                    problems.append("layer_composition_if_any.lighting_if_any.candidate_skills_if_any must be an array when present")
                else:
                    for value in candidate_skills:
                        if not canonicalize_skill_token(value):
                            problems.append(
                                "layer_composition_if_any.lighting_if_any.candidate_skills_if_any must contain only allowed skills when present"
                            )
            supporting = lighting.get("supporting_skills_if_any")
            if supporting is not None:
                if not isinstance(supporting, list):
                    problems.append("layer_composition_if_any.lighting_if_any.supporting_skills_if_any must be an array when present")
                else:
                    for value in supporting:
                        if not canonicalize_skill_token(value):
                            problems.append(
                                "layer_composition_if_any.lighting_if_any.supporting_skills_if_any must contain only allowed skills when present"
                            )
            verify_touch = lighting.get("verify_touch_if_any")
            if verify_touch is not None:
                if not isinstance(verify_touch, dict):
                    problems.append("layer_composition_if_any.lighting_if_any.verify_touch_if_any must be an object when present")
                else:
                    validate_no_extra_keys(
                        verify_touch,
                        {"target", "kind"},
                        "layer_composition_if_any.lighting_if_any.verify_touch_if_any",
                        problems,
                    )
                    for key in ["target", "kind"]:
                        require_nonempty(verify_touch, key, problems)
            role_split = lighting.get("role_split_if_any")
            if role_split is not None:
                if not isinstance(role_split, dict):
                    problems.append("layer_composition_if_any.lighting_if_any.role_split_if_any must be an object when present")
                else:
                    validate_no_extra_keys(
                        role_split,
                        {
                            "primary_skill_if_any",
                            "supporting_skills_if_any",
                            "check_skill_if_any",
                            "check_kind_if_any",
                            "check_target_if_any",
                            "allowed_subordinate_operation_families_if_any",
                            "blocked_ordinary_operation_families_if_any",
                            "ordinary_operations_are_not_skills",
                        },
                        "layer_composition_if_any.lighting_if_any.role_split_if_any",
                        problems,
                    )
                    for key in [
                        "allowed_subordinate_operation_families_if_any",
                        "blocked_ordinary_operation_families_if_any",
                    ]:
                        values = role_split.get(key)
                        if values is None:
                            continue
                        if not isinstance(values, list):
                            problems.append(
                                f"layer_composition_if_any.lighting_if_any.role_split_if_any.{key} must be an array when present"
                            )
                            continue
                        for value in values:
                            if not isinstance(value, str) or not value.strip():
                                problems.append(
                                    f"layer_composition_if_any.lighting_if_any.role_split_if_any.{key} must contain only non-empty strings"
                                )
            ability_branch = lighting.get("ability_branch_if_any")
            if ability_branch is not None:
                if not isinstance(ability_branch, dict):
                    problems.append("layer_composition_if_any.lighting_if_any.ability_branch_if_any must be an object when present")
                else:
                    validate_no_extra_keys(
                        ability_branch,
                        {
                            "support_operation_is_subordinate",
                            "note",
                            "ordinary_operation_policy_if_any",
                        },
                        "layer_composition_if_any.lighting_if_any.ability_branch_if_any",
                        problems,
                    )
            ordinary_flag = lighting.get("ordinary_operations_are_not_skills")
            if ordinary_flag is not None and not isinstance(ordinary_flag, bool):
                problems.append(
                    "layer_composition_if_any.lighting_if_any.ordinary_operations_are_not_skills must be boolean when present"
                )


def validate_gate_binding(state: dict, problems: list[str]) -> None:
    gate_binding = state.get("gate_binding_if_any")
    if gate_binding is None:
        return

    if not isinstance(gate_binding, dict):
        problems.append("gate_binding_if_any must be an object or null")
        return

    validate_no_extra_keys(
        gate_binding,
        {
            "source_focus",
            "source_target",
            "demoted_continuation",
            "authority_until",
            "owner_skill_if_any",
            "owner_skill_combo_if_any",
        },
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
        "hostile_见证",
        "exact_check",
        "asked_medium_failure",
    }:
        problems.append(
            "gate_binding_if_any.authority_until must be same_carrier_change, "
            "hostile_见证, exact_check, or asked_medium_failure"
        )

    owner_skill = gate_binding.get("owner_skill_if_any")
    if owner_skill is not None:
        canonical = canonicalize_skill_token(owner_skill)
        if not canonical:
            problems.append("gate_binding_if_any.owner_skill_if_any must be one of the allowed skills when present")
    owner_combo = gate_binding.get("owner_skill_combo_if_any")
    if owner_combo is not None:
        if not isinstance(owner_combo, list) or not owner_combo:
            problems.append("gate_binding_if_any.owner_skill_combo_if_any must be a non-empty list when present")
        else:
            for value in owner_combo:
                canonical = canonicalize_skill_token(value)
                if not canonical:
                    problems.append(
                        "gate_binding_if_any.owner_skill_combo_if_any must contain only allowed skills when present"
                    )


def validate_materialization_evidence(state: dict, problems: list[str]) -> None:
    evidence = state.get("materialization_evidence")
    if evidence is None:
        return

    if not isinstance(evidence, dict):
        problems.append("materialization_evidence must be an object or null")
        return

    validate_no_extra_keys(
        evidence,
        {"kind", "location", "summary", "worked_step", "skill_serialized"},
        "materialization_evidence",
        problems,
    )
    for key in ["kind", "location", "summary"]:
        require_nonempty(evidence, key, problems)

    kind = evidence.get("kind")
    if isinstance(kind, str) and kind not in {"file", "command", "check", "artifact", "inline_text"}:
        problems.append(
            "materialization_evidence.kind must be file, command, check, artifact, or inline_text"
        )
    worked_step = evidence.get("worked_step")
    if worked_step is not None and (not isinstance(worked_step, str) or not worked_step.strip()):
        problems.append("materialization_evidence.worked_step must be a non-empty string when present")
    skill_serialized = evidence.get("skill_serialized")
    if skill_serialized is not None and not isinstance(skill_serialized, bool):
        problems.append("materialization_evidence.skill_serialized must be boolean when present")


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
        if not 1 <= len(active_primitives) <= 3:
            problems.append(
                "primitive_field_if_any.active_primitives must contain 1 to 3 entries"
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
        not in {"explicit_hint", "state_见证", "cheap_check", "lexical_hint", "mixed"}
    ):
        problems.append(
            "primitive_field_if_any.evidence_basis must be explicit_hint, state_见证, "
            "cheap_check, lexical_hint, or mixed when present"
        )


def validate_primitive_takeover_gate(state: dict, problems: list[str]) -> None:
    gate = state.get("primitive_takeover_gate_if_any")
    if gate is None:
        return

    if not isinstance(gate, dict):
        problems.append("primitive_takeover_gate_if_any must be an object or null")
        return

    validate_no_extra_keys(
        gate,
        {
            "trigger",
            "current_object",
            "current_seam",
            "current_debt",
            "next_bite",
            "note",
            "active_primitives",
        },
        "primitive_takeover_gate_if_any",
        problems,
    )

    for key in ["trigger", "current_object", "current_seam", "current_debt", "next_bite", "note"]:
        require_nonempty(gate, key, problems)

    trigger = nonempty_text(gate.get("trigger"))
    if trigger and trigger not in ALLOWED_PRIMITIVE_TAKEOVER_TRIGGERS:
        problems.append(
            "primitive_takeover_gate_if_any.trigger must be one of: "
            + ", ".join(sorted(ALLOWED_PRIMITIVE_TAKEOVER_TRIGGERS))
        )

    active_primitives = gate.get("active_primitives")
    if active_primitives is None:
        return
    if not isinstance(active_primitives, list):
        problems.append("primitive_takeover_gate_if_any.active_primitives must be an array")
        return
    if not 1 <= len(active_primitives) <= 3:
        problems.append(
            "primitive_takeover_gate_if_any.active_primitives must contain 1 to 3 entries"
        )
    for idx, value in enumerate(active_primitives):
        if canonicalize_primitive_token(value) not in ALLOWED_PRIMITIVES:
            problems.append(
                "primitive_takeover_gate_if_any.active_primitives"
                f"[{idx}] must be one of: {', '.join(sorted(ALLOWED_PRIMITIVES))}"
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
            or nonempty_text(
                ((state.get("layer_composition_if_any") or {}).get("controlled_object"))
            )
            or nonempty_text(
                (((state.get("layer_composition_if_any") or {}).get("authorized_bite") or {}).get("target"))
            )
            or nonempty_text(state.get("current_seam"))
            or nonempty_text(state.get("current_object"))
        )

    agenda = agenda_override
    if agenda is None and derive_agenda:
        agenda = derive_self_check_agenda(state, [])

    explicit_layer = state.get("layer_composition_if_any")
    explicit_controlled = ""
    explicit_target = ""
    if (
        isinstance(explicit_layer, dict)
        and explicit_layer.get("event_owned") is True
        and not _same_carrier_takeover_active(state)
    ):
        explicit_controlled = nonempty_text(explicit_layer.get("controlled_object"))
        authorized_bite = explicit_layer.get("authorized_bite")
        if isinstance(authorized_bite, dict):
            explicit_target = nonempty_text(authorized_bite.get("target"))
    live_bound = state.get("bound_program")
    bound_target = nonempty_text(live_bound.get("target")) if isinstance(live_bound, dict) else ""
    agenda_target = nonempty_text(agenda.get("touch_target")) if isinstance(agenda, dict) else ""
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    if (
        agenda_target
        and agenda_target == asked_medium
        and fresh_blind_problem_first_touch_pending(state, asked_medium=asked_medium)
    ):
        agenda_target = ""

    return (
        explicit_controlled
        or explicit_target
        or bound_target
        or agenda_target
        or nonempty_text(state.get("current_seam"))
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
        "赋值",
        "budget",
        "boundary",
        "split",
        "state",
        "quotient",
        "chain",
        "bucket",
        "见证",
        "carrier",
        "axis",
        "constraint",
        "law",
        "读出",
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
    if state.get("release_veto") is not True:
        return None
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
    selection_basis = nonempty_text(primitive_field.get("selection_basis"))
    explicit_same_carrier_narrowing = (
        selection_basis == "explicit_hint"
        and not isinstance(
            handoff_override if handoff_override is not None else state.get("carrier_handoff_if_any"),
            dict,
        )
        and state.get("bound_program") is None
        and state.get("gate_binding_if_any") is None
    )
    if explicit_same_carrier_narrowing:
        return False
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
        "hostile_见证",
        "exact_check",
        "asked_medium_failure",
        "residue_inherited",
    }:
        problems.append(
            "carrier_handoff_if_any.trigger must be same_carrier_change, "
            "hostile_见证, exact_check, asked_medium_failure, or residue_inherited"
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
        if not 1 <= len(primitive_hints) <= 3:
            problems.append(
                "carrier_handoff_if_any.warm_field.primitive_hints must contain 1 to 3 entries"
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
        not in {"explicit_hint", "state_见证", "cheap_check", "lexical_hint", "mixed"}
    ):
        problems.append(
            "carrier_handoff_if_any.warm_field.evidence_basis must be explicit_hint, "
            "state_见证, cheap_check, lexical_hint, or mixed when present"
        )


def infer_primitives_from_text(*values: object) -> list[str]:
    text = normalize_primitive_token(
        " ".join(nonempty_text(value) for value in values if nonempty_text(value))
    )
    if not text:
        return []

    binary_code_like = "binary" in text and "string" in text
    ledger_like = any(
        token in text
        for token in [
            "capacity ledger",
            "code capacity ledger",
            "exact available capacity",
            "exact ledger",
            "sum i 1 l",
            "2 i",
        ]
    )
    length_counting_like = (
        any(token in text for token in ["length", "lengths", "exact length", "exact lengths"])
        and any(token in text for token in ["string", "strings", "capacity", "count", "count how many"])
    )
    count_under_cap_like = (
        binary_code_like
        and any(
            token in text
            for token in [
                "count how many",
                "available strings",
                "strings exist",
                "non empty binary strings",
            ]
        )
        and any(
            token in text
            for token in [
                "up to length",
                "length cap",
                "maximum codeword length",
                "worst case length",
            ]
        )
    )
    finite_code_budget_like = (
        binary_code_like
        and any(token in text for token in ["injective", "injectively", "message", "messages", "codeword"])
        and any(
            token in text
            for token in [
                "up to length",
                "length cap",
                "maximum codeword length",
                "worst case length",
                "available strings",
            ]
        )
    )
    if (
        binary_code_like
        and any(token in text for token in ["maximum codeword length", "worst case length", "worst-case length"])
        and any(token in text for token in ["length", "up to length", "code space", "available strings"])
    ):
        return ["投影", "守恒"]
    if (
        ((binary_code_like or length_counting_like) and ledger_like)
        or count_under_cap_like
        or finite_code_budget_like
    ):
        return ["投影", "守恒"]

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
        if len(hits) >= INTERNAL_CANDIDATE_LIGHT_LIMIT:
            return hits

    keyword_groups = [
        ("对称", ["对称", "symmetric", "balance", "balanced", "swap", "mirror", "equalize"]),
        ("极限边界", ["limit", "boundary", "edge", "endpoint", "singular", "degener", "collapse", "tangent", "extreme", "extremum"]),
        ("守恒", ["conserv", "invariant", "total", "net", "mass", "flow", "balance sheet"]),
        ("投影", ["project", "投影", "flatten", "shadow", "slice", "cross-section"]),
        ("赋值", ["assign", "representative", "plug", "coincidence"]),
        ("反向", ["反向", "backward", "pullback", "rollback"]),
        ("图像", ["图像", "diagram", "draw", "geometry", "graph", "visual"]),
        ("见证", ["见证", "counterexample", "separate", "kill", "probe", "check", "seam"]),
        (
            "状态拆分",
            ["state split", "split", "quotient", "dp", "automaton", "finite-state", "state class", "equivalence class"],
        ),
        ("相容", ["merge", "compat", "coexist", "joint", "realiz", "supply", "overlap"]),
        (
            "特殊值探针",
            [
                "special value",
                "landmark value",
                "test one value",
                "controlled probe",
                "lawful probe",
                "special case probe",
            ],
        ),
        (
            "边界找路",
            [
                "boundary route",
                "push to boundary",
                "first crack",
                "edge family",
                "boundary candidate",
                "saturation",
                "lower bound",
                "upper bound",
                "optimiz",
                "extrem",
            ],
        ),
        # "construct" / "materialize" are too broad on problem statements and were
        # prematurely collapsing fresh blind runs into 读出-first ordinary solving.
        ("读出", ["读出", "query", "answer", "output", "certificate"]),
    ]
    for primitive, keywords in keyword_groups:
        if any(keyword in text for keyword in keywords):
            hits.append(primitive)
        if len(hits) == 3:
            break
    return hits


def infer_skills_from_problem_text(*values: object, limit: int = 8) -> list[str]:
    text = normalize_primitive_token(
        " ".join(nonempty_text(value) for value in values if nonempty_text(value))
    )
    if not text:
        return []

    ordered: list[str] = []

    def push(skill: str) -> None:
        canonical = canonicalize_skill_token(skill)
        if canonical and canonical in ALLOWED_SKILLS and canonical not in ordered:
            ordered.append(canonical)

    for primitive in infer_primitives_from_text(*values):
        push(primitive)

    explicit_aliases = []
    for skill, aliases in SKILL_ALIAS_GROUPS.items():
        phrases = [
            normalize_primitive_token(alias)
            for alias in aliases
            if len(normalize_primitive_token(alias).split()) > 1
        ]
        explicit_aliases.append((skill, sorted(set(phrases), key=len, reverse=True)))
    for skill, phrases in explicit_aliases:
        if any(phrase and phrase in text for phrase in phrases):
            push(skill)

    function_lane = any(
        token in text
        for token in [
            "f(",
            "function",
            "monotonic",
            "derivative",
            "graph",
            "curve",
            "root",
            "zero",
            "函数",
            "单调",
            "导数",
            "图像",
            "曲线",
            "零点",
        ]
    )
    target_only_lane = (
        any(
            token in text
            for token in [
                "fixed line",
                "fixed value",
                "fixed x",
                "only need",
                "only prove",
                "target only",
                "anchor line",
                "prove the intersection point lies",
                "定直线",
                "定值",
                "固定横坐标",
                "只证",
                "只要证",
                "锚线",
                "交点",
                "横坐标",
            ]
        )
        or (
            "prove" in text
            and any(token in text for token in ["line", "value", "intersection", "point"])
        )
    )
    parameter_boundary_lane = any(
        token in text
        for token in [
            "minimum",
            "maximum",
            "lower bound",
            "upper bound",
            "boundary",
            "saturation",
            "parameter",
            "optimiz",
            "extrem",
            "最小值",
            "最大值",
            "下界",
            "上界",
            "边界",
            "饱和",
            "参数",
            "极值",
            "压线",
        ]
    )
    grouping_lane = any(
        token in text
        for token in [
            "exact cover",
            "one to one",
            "delete two",
            "partition",
            "grouping",
            "matching",
            "permutation",
            "删去",
            "删除",
            "分组",
            "覆盖",
            "一一",
            "精确覆盖",
            "匹配",
            "排列",
            "可分",
        ]
    )
    geometry_lane = any(
        token in text
        for token in [
            "conic",
            "parabola",
            "ellipse",
            "hyperbola",
            "line",
            "intersection",
            "height",
            "圆锥曲线",
            "抛物线",
            "椭圆",
            "双曲线",
            "直线",
            "交点",
            "高度",
        ]
    )

    if function_lane:
        for skill in [
            "图像",
            "极限边界",
            "赋值",
            "函数原型匹配",
            "见证",
            "读出",
        ]:
            push(skill)
    if target_only_lane:
        for skill in [
            "图像",
            "投影",
            "见证",
            "赋值",
            "读出",
        ]:
            push(skill)
    if parameter_boundary_lane:
        for skill in [
            "极限边界",
            "边界找路",
            "特殊值探针",
            "赋值",
            "不算而比",
            "见证",
        ]:
            push(skill)
    if grouping_lane:
        for skill in [
            "状态拆分",
            "相容",
            "投影",
            "赋值",
            "匹配替代概率",
            "格点选排",
        ]:
            push(skill)
    if geometry_lane:
        for skill in ["图像", "投影", "见证"]:
            push(skill)

    parenthesis_balance_lane = any(
        token in text
        for token in [
            "balanced",
            "balance",
            "parentheses",
            "parenthesis",
            "prefix",
            "suffix",
            "concatenation",
            "concatenate",
            "括号",
            "平衡",
            "前缀",
            "后缀",
            "拼接",
        ]
    )
    hostile_falsifier_lane = any(
        token in text
        for token in [
            "counterexample",
            "ordinary heuristic",
            "naive heuristic",
            "heuristic",
            "fails on",
            "refute",
            "kill the wrong route",
            "counter route",
            "wrong route",
            "ordinary balanced-prefix",
            "class-+1",
            "反例",
            "反问",
            "启发式",
            "假主线",
            "错误路线",
            "打掉",
            "失败",
            "杀掉",
        ]
    )
    if parenthesis_balance_lane:
        for skill in [
            "守恒",
            "状态拆分",
            "见证",
            "对称",
            "极限边界",
        ]:
            push(skill)
    if hostile_falsifier_lane:
        push("反问")

    keyword_groups = [
        (
            "图像",
            ["图像", "draw", "graph", "diagram", "visual", "图像", "画图", "示意图", "图解"],
        ),
        (
            "投影",
            ["投影", "project", "height", "slice", "cross-section", "投影", "高度", "截面", "截点"],
        ),
        (
            "赋值",
            ["assign", "representative", "anchor", "plug", "赋值", "代表", "锚点", "取值"],
        ),
        (
            "见证",
            ["见证", "check", "verify", "probe", "compare", "见证", "检验", "验证", "比较", "检查"],
        ),
        (
            "状态拆分",
            ["split", "partition", "case", "group", "拆分", "分类", "分组", "分情况"],
        ),
        (
            "相容",
            ["compat", "coexist", "fit together", "覆盖", "相容", "共存", "约束"],
        ),
        (
            "规范归一化",
            ["normalize", "standardize", "canonical", "规范", "归一", "标准化"],
        ),
        (
            "函数原型匹配",
            ["archetype", "prototype", "母函数", "原型", "函数类型", "函数家族"],
        ),
        (
            "特殊值探针",
            ["special value", "test one value", "landmark value", "特殊值", "试值", "探针"],
        ),
        (
            "读出",
            ["读出", "read off", "直接读", "读出", "答案", "输出"],
        ),
    ]
    for skill, keywords in keyword_groups:
        if any(keyword in text for keyword in keywords):
            push(skill)

    return ordered[:limit]


def problem_wants_hostile_falsifier(*values: object) -> bool:
    text = normalize_primitive_token(
        " ".join(nonempty_text(value) for value in values if nonempty_text(value))
    )
    if not text:
        return False
    return any(
        token in text
        for token in [
            "counterexample",
            "ordinary heuristic",
            "naive heuristic",
            "heuristic",
            "fails on",
            "refute",
            "kill the wrong route",
            "counter route",
            "wrong route",
            "ordinary balanced-prefix",
            "class-+1",
            "ordinary prefix",
            "反例",
            "启发式",
            "假主线",
            "错误路线",
            "打掉",
            "失败",
            "杀掉",
        ]
    )


def derive_problem_skill_frontload(
    state: dict,
    *,
    primitive_field: dict | None = None,
    control_signals: dict | None = None,
) -> dict | None:
    if state.get("release_veto") is not True:
        return None

    current_object = nonempty_text(state.get("current_object"))
    current_seam = nonempty_text(state.get("current_seam"))
    current_debt = nonempty_text(state.get("current_debt"))
    next_bite = nonempty_text(state.get("next_bite"))
    asked_medium = nonempty_text(state.get("asked_medium_surface"))

    candidate_skills = infer_skills_from_problem_text(
        current_object,
        current_seam,
        current_debt,
        next_bite,
    )
    if isinstance(primitive_field, dict):
        raw_active = primitive_field.get("active_primitives")
        if isinstance(raw_active, list):
            for value in raw_active:
                canonical = canonicalize_skill_token(value)
                if canonical and canonical not in candidate_skills:
                    candidate_skills.append(canonical)
        evidence_basis = nonempty_text(primitive_field.get("evidence_basis"))
        if evidence_basis not in {"lexical_hint", "text_fallback"}:
            for value in derive_semantic_coactivation_hints(
                primitive_field.get("active_primitives", [])
            ):
                if value and value not in candidate_skills:
                    candidate_skills.append(value)
    controller_trigger = None
    if isinstance(control_signals, dict):
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        if isinstance(layerwise_pressure, dict) and layerwise_pressure.get("active") is True:
            for value in layerwise_pressure.get("wake_skills", []):
                canonical = canonicalize_skill_token(value)
                if canonical and canonical not in candidate_skills:
                    candidate_skills.append(canonical)
        controller_trigger = derive_controller_trigger_surface(
            state,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
            control_signals_override=control_signals,
        )
        if isinstance(controller_trigger, dict):
            for value in _normalize_skill_combo(
                controller_trigger.get("favored_combo"),
                limit=6,
            ):
                if value and value not in candidate_skills:
                    candidate_skills.append(value)
            for value in _normalize_skill_combo(
                controller_trigger.get("favored_skills"),
                limit=4,
            ):
                if value and value not in candidate_skills:
                    candidate_skills.append(value)

    allow_counter_question = problem_wants_hostile_falsifier(
        current_object,
        current_seam,
        current_debt,
        next_bite,
    )
    candidate_skills = [
        skill
        for skill in candidate_skills
        if skill in ALLOWED_SKILLS
        and (
            skill not in CONTROL_META_SKILLS
            or (allow_counter_question and skill == "反问")
        )
    ]
    if not candidate_skills:
        return None

    touch_target = current_seam or current_object or current_debt or asked_medium
    reason = (
        current_debt
        or next_bite
        or "the current layer should light multiple project skills before ordinary continuation starts"
    )
    return {
        "candidate_skills": candidate_skills[:8],
        "touch_target": touch_target,
        "why_now": reason,
        "selection_basis": "problem_frontload",
        "evidence_basis": "problem_text",
        "arbitration_skill_if_any": (
            canonicalize_skill_token(controller_trigger.get("arbitration_skill_if_any"))
            if isinstance(controller_trigger, dict)
            else ""
        ),
        "counter_question_if_any": (
            nonempty_text(controller_trigger.get("counter_question_if_any"))
            if isinstance(controller_trigger, dict)
            else ""
        ),
        "favored_combo_if_any": (
            _normalize_skill_combo(controller_trigger.get("favored_combo"), limit=6)
            if isinstance(controller_trigger, dict)
            else []
        ),
    }


def _normalize_skill_combo(values: object, *, limit: int = 6) -> list[str]:
    if not isinstance(values, list):
        return []
    ordered: list[str] = []
    for value in values:
        canonical = canonicalize_skill_token(value)
        if canonical and canonical not in ordered:
            ordered.append(canonical)
        if len(ordered) >= limit:
            break
    return ordered


def _attach_skill_metadata(
    program: dict | None,
    *,
    owner_skill: str = "",
    combo: object = None,
) -> dict | None:
    if not isinstance(program, dict):
        return None
    payload = dict(program)
    normalized_owner = canonicalize_skill_token(owner_skill) or canonicalize_skill_token(
        payload.get("owner_skill_if_any")
    )
    normalized_combo = _normalize_skill_combo(combo)
    if normalized_owner:
        payload["owner_skill_if_any"] = normalized_owner
    if normalized_combo:
        if normalized_owner and normalized_owner not in normalized_combo:
            normalized_combo.insert(0, normalized_owner)
        payload["owner_skill_combo_if_any"] = normalized_combo[:6]
    return payload


def _has_explicit_owner_combo(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    combo = payload.get("owner_skill_combo_if_any")
    if not isinstance(combo, list):
        return False
    return bool(_normalize_skill_combo(combo))


def _event_owned_layer_has_explicit_authorized_bite(layer: object) -> bool:
    if not isinstance(layer, dict) or layer.get("event_owned") is not True:
        return False
    authorized_bite = layer.get("authorized_bite")
    return _has_explicit_owner_combo(authorized_bite)


def _project_runtime_program_shape(payload: object) -> dict | None:
    if not isinstance(payload, dict):
        return None
    kind = nonempty_text(payload.get("kind"))
    target = nonempty_text(payload.get("target"))
    operation = nonempty_text(payload.get("operation"))
    if not kind or not target or not operation:
        return None
    program = {
        "kind": kind,
        "target": target,
        "operation": operation,
    }
    success_signal = nonempty_text(payload.get("success_signal"))
    if success_signal:
        program["success_signal"] = success_signal
    owner_skill = canonicalize_skill_token(payload.get("owner_skill_if_any"))
    if owner_skill:
        program["owner_skill_if_any"] = owner_skill
    owner_combo = extract_explicit_skill_combo(payload)
    if owner_combo:
        program["owner_skill_combo_if_any"] = owner_combo[:6]
    return attach_program_metadata_fields(program, payload)


def _runtime_program_signature(payload: object) -> tuple[str, str, str]:
    program = _project_runtime_program_shape(payload)
    if not isinstance(program, dict):
        return ("", "", "")
    return (
        nonempty_text(program.get("kind")),
        nonempty_text(program.get("target")),
        nonempty_text(program.get("operation")),
    )


def _event_owned_layer_matches_live_surface(state: dict, layer: object) -> bool:
    if not isinstance(state, dict) or not isinstance(layer, dict):
        return False
    if layer.get("event_owned") is not True:
        return False
    surface = nonempty_text(layer.get("surface"))
    if not surface:
        return False

    authorized_signature = _runtime_program_signature(layer.get("authorized_bite"))
    if surface == "bound_program":
        live_signature = _runtime_program_signature(state.get("bound_program"))
        return bool(all(authorized_signature) and authorized_signature == live_signature)
    if surface == "takeover_recomposition":
        landed_touch = state.get("landed_next_touch_if_any")
        if not (isinstance(landed_touch, dict) and _has_explicit_owner_combo(landed_touch)):
            return False
        layer_object = (
            nonempty_text(layer.get("layer_object"))
            or nonempty_text(layer.get("current_object"))
            or nonempty_text(state.get("current_object"))
        )
        live_object = nonempty_text(state.get("current_object"))
        landed_target = nonempty_text(landed_touch.get("target"))
        layer_target = (
            nonempty_text(layer.get("controlled_object"))
            or nonempty_text(layer.get("current_seam"))
            or nonempty_text(layer.get("next_local_choice"))
            or authorized_signature[1]
        )
        live_target = (
            nonempty_text(state.get("current_seam"))
            or nonempty_text(state.get("current_debt"))
            or layer_target
        )
        if layer_object and live_object and layer_object != live_object:
            return False
        if layer_object and landed_target and layer_object != landed_target:
            return False
        return bool(layer_target and live_target and layer_target == live_target)
    if surface == "carrier_handoff":
        handoff = state.get("carrier_handoff_if_any")
        if not isinstance(handoff, dict):
            return False
        live_target = nonempty_text(handoff.get("to_object"))
        layer_target = (
            nonempty_text(layer.get("controlled_object"))
            or nonempty_text(layer.get("next_local_choice"))
            or authorized_signature[1]
        )
        return bool(live_target and layer_target and live_target == layer_target)
    return False


def state_has_explicit_local_ownership_evidence(state: dict) -> bool:
    explicit_layer = state.get("layer_composition_if_any")
    if (
        _event_owned_layer_has_explicit_authorized_bite(explicit_layer)
        and _event_owned_layer_matches_live_surface(state, explicit_layer)
        and not _same_carrier_takeover_active(state)
    ):
        return True

    gate_binding = state.get("gate_binding_if_any")
    if isinstance(gate_binding, dict) and _has_explicit_owner_combo(gate_binding):
        return True

    bound_program = state.get("bound_program")
    if isinstance(bound_program, dict) and _has_explicit_owner_combo(bound_program):
        return True

    landed_next_touch = state.get("landed_next_touch_if_any")
    if isinstance(landed_next_touch, dict) and _has_explicit_owner_combo(landed_next_touch):
        return True

    return False


def state_allows_task_route_synthesis(state: dict) -> bool:
    if state_has_explicit_local_ownership_evidence(state):
        return True
    primitive_takeover_gate = state.get("primitive_takeover_gate_if_any")
    if not isinstance(primitive_takeover_gate, dict):
        return False
    if nonempty_text(primitive_takeover_gate.get("trigger")) != "same_carrier_landing":
        return False
    landed_next_touch = state.get("landed_next_touch_if_any")
    return isinstance(landed_next_touch, dict) and _has_explicit_owner_combo(landed_next_touch)


def infer_primitives_from_pressure_hints(values: object) -> list[str]:
    if not isinstance(values, list):
        return []

    mapping = {
        "对称": "对称",
        "limit boundary": "极限边界",
        "守恒": "守恒",
        "投影": "投影",
        "赋值": "赋值",
        "反向": "反向",
        "图像": "图像",
        "见证": "见证",
        "check": "见证",
        "state split": "状态拆分",
        "相容": "相容",
        "读出": "读出",
        "query": "读出",
    }
    hits: list[str] = []
    for value in values:
        primitive = canonicalize_primitive_token(value) or mapping.get(
            normalize_primitive_token(value)
        )
        if primitive and primitive not in hits:
            hits.append(primitive)
        if len(hits) >= INTERNAL_CANDIDATE_LIGHT_LIMIT:
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
    见证_hints: bool = False,
    lexical_hints: bool = False,
) -> str:
    existing = nonempty_text(existing_value)
    if existing:
        return existing
    if explicit_hints and (见证_hints or lexical_hints):
        return "mixed"
    if explicit_hints:
        return "explicit_hint"
    if nonempty_text(tie_break_check):
        return "cheap_check"
    if 见证_hints:
        return "state_见证"
    if lexical_hints:
        return "lexical_hint"

    normalized_selection = nonempty_text(selection_basis)
    if normalized_selection == "explicit_hint":
        return "explicit_hint"
    if normalized_selection in {"agenda_hint", "tie_break"}:
        return "state_见证"
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
            if len(merged) >= INTERNAL_CANDIDATE_LIGHT_LIMIT:
                return merged
    return merged


def _normalized_primitive_list(values: object, *, limit: int = INTERNAL_CANDIDATE_LIGHT_LIMIT) -> list[str]:
    if not isinstance(values, list):
        return []
    ordered: list[str] = []
    for value in values:
        primitive = canonicalize_primitive_token(value)
        if primitive and primitive not in ordered:
            ordered.append(primitive)
        if len(ordered) >= limit:
            break
    return ordered


def text_hints_deserve_front_seat(text_hints: object) -> bool:
    normalized = _normalized_primitive_list(text_hints, limit=6)
    if len(normalized) < 2:
        return False
    structural_hits = [
        primitive for primitive in normalized if primitive in STRUCTURE_NUCLEUS_PRIMITIVES
    ]
    probe_hits = [
        primitive for primitive in normalized if primitive in PROBE_LIKE_PRIMITIVES
    ]
    transform_hits = [
        primitive for primitive in normalized if primitive in TRANSFORM_SUPPORT_PRIMITIVES
    ]
    readout_hits = [
        primitive for primitive in normalized if primitive in GENERIC_CLOSURE_HELPER_PRIMITIVES
    ]
    if len(structural_hits) >= 2:
        return True
    if structural_hits and probe_hits:
        return True
    if transform_hits and (structural_hits or probe_hits):
        return True
    if readout_hits and structural_hits:
        return True
    if any(primitive_claim_requires_partner(primitive) for primitive in normalized[:3]):
        return True
    return False


def derive_controller_trigger_surface(
    state: dict,
    *,
    primitive_field_override: dict | None = None,
    control_signals_override: dict | None = None,
) -> dict | None:
    if state.get("release_veto") is not True:
        return None
    control_signals = (
        control_signals_override
        if control_signals_override is not None
        else derive_control_signals(
            state,
            [],
            primitive_field_override=primitive_field_override if isinstance(primitive_field_override, dict) else None,
        )
    )
    controller_view = (
        control_signals.get("current_controller_view", {})
        if isinstance(control_signals, dict)
        else {}
    )
    meta_controls = (
        control_signals.get("meta_controls", {})
        if isinstance(control_signals, dict)
        else {}
    )
    micro_control_surface = (
        control_signals.get("micro_control_surface", {})
        if isinstance(control_signals, dict)
        else {}
    )
    counter_surface = (
        micro_control_surface.get("反问", {})
        if isinstance(micro_control_surface, dict)
        else {}
    )
    counter_meta = (
        meta_controls.get("反问", {})
        if isinstance(meta_controls, dict)
        else {}
    )
    counter_active = isinstance(counter_meta, dict) and counter_meta.get("active") is True
    counter_target = (
        nonempty_text(counter_surface.get("target"))
        or nonempty_text(counter_meta.get("target"))
        or nonempty_text(state.get("current_seam"))
        or nonempty_text(state.get("current_object"))
    )
    counter_question = (
        nonempty_text(counter_surface.get("question"))
        or nonempty_text(counter_meta.get("question"))
    )
    problem_skill_candidates = [
        skill
        for skill in infer_skills_from_problem_text(
            state.get("current_object"),
            state.get("current_seam"),
            state.get("current_debt"),
            state.get("next_bite"),
        )
        if skill in ALLOWED_SKILLS and skill not in CONTROL_META_SKILLS
    ]
    primitive_field = (
        primitive_field_override
        if primitive_field_override is not None
        else state.get("primitive_field_if_any")
    )
    active_primitives: list[str] = []
    if isinstance(primitive_field, dict):
        active_primitives = _normalized_primitive_list(
            primitive_field.get("active_primitives"),
            limit=6,
        )
    if not active_primitives and not (counter_active and len(problem_skill_candidates) >= 2):
        return None
    triggers: list[tuple[str, list[str], str]] = []
    active_set = set(active_primitives)
    if {"投影", "守恒"}.issubset(active_set):
        triggers.append(
            (
                "aggregate_control",
                ["投影", "守恒"],
                "one aggregate ledger already controls the layer more honestly than local branch narration",
            )
        )
    if "对称" in active_set and active_set.intersection(
        {"第一裂缝", "极限边界", "见证", "对称消元"}
    ):
        triggers.append(
            (
                "对称_collapse",
                ["对称", "极限边界", "第一裂缝", "见证"],
                "a 对称-like flattening is live and one boundary / crack 见证 can kill fake a对称 cheaply",
            )
        )
    if {"第一裂缝", "极限边界"}.issubset(active_set):
        triggers.append(
            (
                "singular_boundary",
                ["第一裂缝", "极限边界", "见证"],
                "the earliest honest control sits on the first crack or boundary rather than on bulk derivation",
            )
        )
    if "赋值" in active_set and active_set.intersection(
        {"图像", "状态拆分", "极限边界", "特殊值探针"}
    ):
        triggers.append(
            (
                "representative_anchor",
                ["赋值", "图像", "状态拆分", "极限边界"],
                "one representative anchor can delete fake burden before ordinary symbolic continuation grows",
            )
        )
    if (
        {"状态拆分", "投影"}.issubset(active_set)
        and isinstance(controller_view, dict)
        and (
            controller_view.get("外壳怀疑") is True
            or nonempty_text(controller_view.get("owner_status")) in {"narrowing", "locked"}
        )
    ):
        triggers.append(
            (
                "carrier_collapse",
                ["状态拆分", "投影", "见证"],
                "the current carrier still looks thick, so authority should stay with the smallest residue that survives collapse",
            )
        )
    if (
        problem_wants_hostile_falsifier(
            state.get("current_object"),
            state.get("current_seam"),
            state.get("current_debt"),
            state.get("next_bite"),
        )
        and active_set.intersection({"守恒", "对称", "见证", "状态拆分", "极限边界"})
    ):
        triggers.append(
            (
                "hostile_falsifier_first",
                ["反问", "守恒", "对称", "见证", "状态拆分", "极限边界"],
                "one cheap hostile falsifier can delete the fake main line before the structural carrier is allowed to thicken",
            )
        )
    if not triggers and not (counter_active and len(problem_skill_candidates) >= 2):
        return None
    favored: list[str] = []
    trigger_names: list[str] = []
    reasons: list[str] = []
    for name, primitives, reason in triggers:
        trigger_names.append(name)
        reasons.append(reason)
        for primitive in primitives:
            skill = canonicalize_skill_token(primitive)
            if (
                skill
                and skill in ALLOWED_SKILLS
                and (skill in active_set or skill in CONTROL_META_SKILLS)
                and skill not in favored
            ):
                favored.append(skill)
    if not favored:
        favored = problem_skill_candidates[:]
    structural_counter_combo: list[str] = []
    for skill in favored + active_primitives + problem_skill_candidates:
        canonical = canonicalize_skill_token(skill)
        if (
            canonical
            and canonical not in CONTROL_META_SKILLS
            and canonical != "精确封口"
            and canonical not in structural_counter_combo
        ):
            structural_counter_combo.append(canonical)
    hostile_counter_first = "hostile_falsifier_first" in trigger_names and "反问" in favored
    counter_arbitration_active = (
        counter_active
        and len(structural_counter_combo) >= 2
        and not hostile_counter_first
    )
    if counter_arbitration_active and "counter_question_arbitration" not in trigger_names:
        trigger_names.insert(0, "counter_question_arbitration")
    if counter_arbitration_active:
        favored = structural_counter_combo + [
            skill for skill in favored if skill not in structural_counter_combo
        ]
    if hostile_counter_first:
        favored = ["反问"] + [skill for skill in favored if skill != "反问"]
    primary_reason = reasons[0] if reasons else ""
    if hostile_counter_first:
        for name, _, reason in triggers:
            if name == "hostile_falsifier_first":
                primary_reason = reason
                break
    elif counter_arbitration_active:
        primary_reason = (
            nonempty_text(state.get("current_debt"))
            or nonempty_text(state.get("next_bite"))
            or "let the lit structural skills compete under one counter-question before the layer picks an owner"
        )
    favored_combo = (
        structural_counter_combo[:6]
        if structural_counter_combo
        else [skill for skill in favored if skill != "反问"][:6]
    )
    mode = (
        "hostile_falsifier_first"
        if hostile_counter_first
        else "counter_question_arbitration"
        if counter_arbitration_active
        else "controller_trigger"
    )
    return {
        "active": True,
        "layer_object": (
            nonempty_text(primitive_field.get("layer_object"))
            if isinstance(primitive_field, dict)
            else nonempty_text(state.get("current_object"))
            or nonempty_text(state.get("current_debt"))
        ),
        "trigger_names": trigger_names[:3],
        "favored_skills": favored[:4],
        "favored_combo": favored_combo[:6],
        "selection_basis": "controller_trigger",
        "evidence_basis": (
            nonempty_text(primitive_field.get("evidence_basis"))
            if isinstance(primitive_field, dict)
            else "problem_text"
        ),
        "why_now": primary_reason,
        "mode": mode,
        "arbitration_skill_if_any": "反问" if (counter_arbitration_active or hostile_counter_first) else "",
        "counter_target": counter_target,
        "counter_question_if_any": counter_question,
    }


def apply_controller_trigger_to_combo(
    combo: list[str],
    *,
    leading_skill: str = "",
    controller_trigger: dict | None = None,
) -> tuple[str, list[str]]:
    ordered_combo = [skill for skill in combo if canonicalize_skill_token(skill)]
    normalized_leading = canonicalize_skill_token(leading_skill)
    if not isinstance(controller_trigger, dict):
        return (normalized_leading or (ordered_combo[0] if ordered_combo else ""), ordered_combo[:6])
    trigger_mode = nonempty_text(controller_trigger.get("mode"))
    favored = _normalize_skill_combo(controller_trigger.get("favored_skills"), limit=4)
    favored_combo = _normalize_skill_combo(controller_trigger.get("favored_combo"), limit=6)
    if trigger_mode == "counter_question_arbitration" and favored_combo:
        structural_order = favored_combo + [skill for skill in favored if skill not in favored_combo]
        preferred_leading = next(
            (
                skill
                for skill in structural_order
                if skill in ordered_combo
                and skill not in GENERIC_CLOSURE_HELPER_PRIMITIVES
                and skill != "反问"
            ),
            "",
        )
        if not preferred_leading:
            preferred_leading = next(
                (skill for skill in structural_order if skill in ordered_combo and skill != "反问"),
                "",
            )
        ordered_combo = structural_order + [skill for skill in ordered_combo if skill not in structural_order]
        resolved_leading = preferred_leading or normalized_leading or (ordered_combo[0] if ordered_combo else "")
        if resolved_leading and resolved_leading in ordered_combo:
            ordered_combo = [resolved_leading] + [skill for skill in ordered_combo if skill != resolved_leading]
        return resolved_leading, ordered_combo[:6]
    preferred_leading = next(
        (
            skill
            for skill in favored
            if skill in ordered_combo and skill not in GENERIC_CLOSURE_HELPER_PRIMITIVES
        ),
        "",
    )
    if not preferred_leading:
        preferred_leading = next((skill for skill in favored if skill in ordered_combo), "")
    if favored:
        ordered_combo = favored + [skill for skill in ordered_combo if skill not in favored]
    resolved_leading = preferred_leading or normalized_leading or (ordered_combo[0] if ordered_combo else "")
    if resolved_leading and resolved_leading in ordered_combo:
        ordered_combo = [resolved_leading] + [skill for skill in ordered_combo if skill != resolved_leading]
    return resolved_leading, ordered_combo[:6]


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
    反问_live = (
        isinstance(meta_controls, dict)
        and meta_controls.get("反问", {}).get("active") is True
    )

    if focus == "rival":
        return False
    if 反问_live and focus == "seam" and not (has_nonprobe_structural or structural_skill_live):
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


def derive_check_methods(
    *,
    focus: str = "",
    has_structural_lead: bool = False,
    has_tie_break_check: bool = False,
    asked_medium_live: bool = False,
) -> list[str]:
    methods: list[str] = []
    if has_structural_lead:
        methods.append("structural_consistency_check")
    if focus in {"seam", "rival", "carrier"}:
        methods.append("boundary_or_counterexample_check")
    if has_tie_break_check:
        methods.append("targeted_tie_break_check")
    if asked_medium_live:
        methods.append("asked_medium_contact_check")
    if has_structural_lead:
        methods.append("small_scale_enumeration_after_compression_only")
    deduped: list[str] = []
    for method in methods:
        if method not in deduped:
            deduped.append(method)
    return deduped


def derive_composition_pressure(*groups: object) -> dict:
    ordered: list[str] = []
    for group in groups:
        if not isinstance(group, list):
            continue
        for value in group:
            primitive = canonicalize_primitive_token(value)
            if primitive and primitive in ALLOWED_PRIMITIVES and primitive not in ordered:
                ordered.append(primitive)

    transform_support = [
        primitive for primitive in ordered if primitive in TRANSFORM_SUPPORT_PRIMITIVES
    ]
    读出_or_compression = [
        primitive
        for primitive in ordered
        if primitive in READOUT_LIKE_PRIMITIVES or primitive in COMPRESSION_HEAVY_PRIMITIVES
    ]
    probe_support = [
        primitive for primitive in ordered if primitive in PROBE_LIKE_PRIMITIVES
    ]
    composition_axes: list[str] = []
    if transform_support:
        composition_axes.append("transform")
    if 读出_or_compression:
        composition_axes.append("读出_or_compression")
    if probe_support:
        composition_axes.append("probe")

    composition_ready = bool(
        len(composition_axes) >= 2
        or len(transform_support) >= 2
    )
    compression_without_support = bool(读出_or_compression and not transform_support)

    return {
        "ordered_primitives": ordered[:6],
        "supporting_transform_primitives": transform_support[:4],
        "读出_or_compression_primitives": 读出_or_compression[:4],
        "probe_support_primitives": probe_support[:4],
        "composition_axes": composition_axes,
        "composition_ready": composition_ready,
        "compression_without_support": compression_without_support,
        "reason": (
            "读出/compression is currently unsupported by any transform-side skill"
            if compression_without_support
            else "multiple live skill axes are simultaneously active on the same layer"
            if composition_ready
            else "one live skill family is visible, but real composition is not yet earned"
        ),
    }


def reorder_kinds_for_skill_first(
    kinds: list[str],
    *,
    focus: str = "",
    probe_secondary: bool = False,
) -> list[str]:
    normalized = [kind for kind in kinds if kind in {"write", "读出", "check", "见证"}]
    if not normalized:
        return normalized
    if not probe_secondary or focus == "rival":
        return list(dict.fromkeys(normalized))

    ordered = []
    if focus == "asked_medium":
        ordered.extend(["write", "读出", "check", "见证"])
    else:
        ordered.extend(["write", "读出", "check", "见证"])
    ordered.extend([kind for kind in normalized if kind not in ordered])
    return [kind for kind in ordered if kind in normalized or kind in {"write", "读出", "check", "见证"}][:4]


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
            "状态拆分",
            "投影",
            "规范归一化",
            "公共值压缩",
            "相容",
            "守恒",
            "函数原型匹配",
            "匹配替代概率",
            "格点选排",
            "先调模型后推导",
            "反向",
            "图像",
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


def _semantics_list_values(semantics: dict, key: str) -> list[str]:
    if not isinstance(semantics, dict):
        return []
    raw = semantics.get(key)
    if not isinstance(raw, list):
        return []
    ordered: list[str] = []
    for value in raw:
        canonical = canonicalize_skill_token(value)
        if canonical and canonical not in ordered:
            ordered.append(canonical)
    return ordered


def _closure_combo_from_sources(*sources: object, limit: int = 6) -> list[str]:
    ordered: list[str] = []
    for source in sources:
        if isinstance(source, dict):
            values = extract_explicit_skill_combo(source)
        else:
            values = _normalize_skill_combo(source, limit=limit)
        for value in values:
            canonical = canonicalize_skill_token(value)
            if (
                canonical
                and canonical not in ordered
                and canonical not in CONTROL_META_SKILLS
                and canonical != "精确封口"
            ):
                ordered.append(canonical)
    return ordered[:limit]


def _closure_owner_from_combo(*sources: object, preferred_owner: object = "") -> str:
    preferred = canonicalize_skill_token(preferred_owner)
    combo = _closure_combo_from_sources(*sources)
    if preferred and preferred in combo:
        return preferred
    return combo[0] if combo else ""


def primitive_claim_requires_partner(primitive: object) -> bool:
    semantics = get_primitive_semantics(primitive)
    return isinstance(semantics, dict) and semantics.get("claim_requires_partner") is True


def derive_semantic_coactivation_hints(primitives: object) -> list[str]:
    ordered: list[str] = []
    if not isinstance(primitives, list):
        return ordered
    seen_primitives = {
        canonicalize_primitive_token(value)
        for value in primitives
        if canonicalize_primitive_token(value)
    }
    for primitive in seen_primitives:
        semantics = get_primitive_semantics(primitive)
        for canonical in _semantics_list_values(semantics, "coactivate_with"):
            if canonical in ALLOWED_SKILLS and canonical not in ordered and canonical not in seen_primitives:
                ordered.append(canonical)
    return ordered


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

    外壳怀疑 = bool(
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
        and (外壳怀疑 or state.get("uncertainty_mode") in {"high", "mixed"} or middle_object_risk)
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
            见证_hints=primitive_selection_basis == "agenda_hint",
            lexical_hints=primitive_selection_basis == "text_fallback",
        )

    live_primitives: list[str] = []
    if competition_status == "resolved" and competition_winner:
        live_primitives = [competition_winner]
    elif competition_status == "unresolved" and competition_candidates:
        live_primitives = competition_candidates[:3]
    elif primitive_field_active:
        live_primitives = primitive_field_active[:4]

    heuristic_primitives: list[str] = []
    if middle_object_risk:
        heuristic_primitives.extend(
            ["规范归一化", "投影", "定义即直接读出"]
        )
    if reselection_needed:
        heuristic_primitives.extend(
            ["边界找路", "局部缝控制整体", "状态拆分"]
        )
    if state.get("uncertainty_mode") in {"high", "mixed"}:
        heuristic_primitives.extend(
            ["状态拆分", "不算而比", "见证"]
        )
    function_图像_first = bool(
        ("f(" in current_object or "function" in current_object.lower())
        and any(
            token in (current_debt or "").lower()
            for token in ["monotonic", "graph", "curve", "inequality"]
        )
    )
    if not output_touched:
        if function_图像_first:
            heuristic_primitives.extend(["图像", "投影", "状态拆分"])
        elif asked_medium and current_object and current_object != asked_medium:
            heuristic_primitives.extend(["投影", "图像", "状态拆分"])
        else:
            heuristic_primitives.extend(["投影", "读出", "投影读出"])
    if not heuristic_primitives and 外壳怀疑:
        heuristic_primitives.extend(
            ["规范归一化", "投影", "对称消元"]
        )

    god_view_active = bool(
        外壳怀疑
        or middle_object_risk
        or (current_object and current_seam and current_seam != current_object)
    )
    反问_active = bool(
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
    元认知_active = bool(
        god_view_active
        or 反问_active
        or closure_gate_active
        or owner_status != "locked"
    )
    后脑守卫_active = bool(
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
                "规范归一化",
                "对称消元",
                "局部缝控制整体",
                "投影",
            ],
            heuristic_primitives,
        )
    if 反问_active:
        heuristic_primitives = merge_primitive_hints(
            ["不算而比", "见证"],
            heuristic_primitives,
        )
    if closure_gate_active:
        heuristic_primitives = merge_primitive_hints(
            ["投影", "定义即直接读出", "读出"],
            heuristic_primitives,
        )

    raw_composition_pressure = derive_composition_pressure(
        live_primitives,
        primitive_field_active,
        competition_candidates,
        heuristic_primitives,
    )
    composition_pressure = raw_composition_pressure
    suggested_support_primitives: list[str] = []
    if raw_composition_pressure.get("compression_without_support") is True:
        suggested_support_primitives = [
            "投影",
            "状态拆分",
            "对称消元",
        ]
        heuristic_primitives = merge_primitive_hints(
            suggested_support_primitives,
            heuristic_primitives,
        )
        composition_pressure = derive_composition_pressure(
            live_primitives,
            primitive_field_active,
            competition_candidates,
            heuristic_primitives,
        )
        composition_pressure["compression_without_support"] = True
        composition_pressure["reason"] = raw_composition_pressure.get("reason")
        composition_pressure["raw_composition_ready"] = raw_composition_pressure.get(
            "composition_ready"
        ) is True
        composition_pressure["suggested_support_primitives"] = suggested_support_primitives

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
        else "smaller truthful carrier and cheaper discriminating 见证 should pull harder"
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
        if 外壳怀疑
        else "the current object may still be a beautiful middle carrier instead of the final owner"
        if middle_object_risk
        else "the current controller is locally visible enough to stay thin"
    )

    反问_target = cheapest_reality_check or current_seam or current_object
    反问_text = (
        f"given the ask, the strongest still-true object, and the current gap, what same-carrier check or hostile 见证 could kill decorative progress on {反问_target} first?"
        if 反问_target
        else "given the ask and the current gap, what same-carrier check could still kill decorative progress first?"
    )
    反问_kind = (
        "读出"
        if (
            closure_gate_active
            and asked_medium
            and not reselection_needed
            and not 外壳怀疑
            and not middle_object_risk
            and owner_status == "locked"
        )
        else "check"
    )
    反问_methods = derive_check_methods(
        focus="asked_medium" if closure_gate_active and asked_medium else "seam",
        has_structural_lead=bool(live_primitives),
        has_tie_break_check=bool(cheapest_reality_check),
        asked_medium_live=bool(asked_medium),
    )
    监督_owner = (
        "closure"
        if closure_gate_active
        else "reselection"
        if isinstance(handoff, dict) or reselection_needed
        else "rival"
        if competition_status == "live_rivalry"
        else "carrier"
        if 外壳怀疑 or middle_object_risk
        else "seam"
        if current_seam
        else "object"
    )
    监督_target = (
        asked_medium
        if 监督_owner == "closure" and asked_medium
        else nonempty_text(handoff.get("to_object"))
        if 监督_owner == "reselection" and isinstance(handoff, dict)
        else competition_separating_check
        if 监督_owner == "rival" and competition_separating_check
        else current_seam
        if 监督_owner == "seam" and current_seam
        else current_object
    )
    监督_until = (
        "asked_medium_contact_or_exact_executable_closure"
        if 监督_owner == "closure"
        else "handoff_bound_or_exact_check_or_kill_见证"
        if 监督_owner == "reselection"
        else "same_carrier_change_or_kill_见证_or_exact_check"
    )
    监督_reason = (
        "release should stay vetoed until the asked medium has exact executable contact"
        if 监督_owner == "closure"
        else "thinner-carrier authority is locally due and should not dissolve back into narration"
        if 监督_owner == "reselection"
        else "a live rival still needs one separating 见证 before ordinary continuation should regain comfort"
        if 监督_owner == "rival"
        else "the current carrier still needs local anti-drift ownership before it can be trusted"
    )
    reward_promote = [
        "exact_读出"
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
    if 外壳怀疑 or reselection_needed:
        penalty_demote.append("surface_story_without_carrier_change")
    penalty_demote = list(dict.fromkeys(penalty_demote))
    closure_required_contact = (
        "读出"
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
        "监督_pulse": {
            "active": supervisory_pulse_active or closure_gate_active or reselection_needed,
            "owner": 监督_owner,
            "target": 监督_target,
            "until": 监督_until,
            "reason": 监督_reason,
        },
        "反问": {
            "active": 反问_active,
            "question": 反问_text,
            "target": 反问_target,
            "preferred_answer_kind": 反问_kind,
            "reason": "keep one cheap falsifier or exact check live before commentary regains comfort",
            "check_skill_active": True,
            "allowed_check_methods": 反问_methods,
            "small_scale_enumeration_role": (
                "optional_post_compression_verifier"
                if "small_scale_enumeration_after_compression_only" in 反问_methods
                else "not_primary"
            ),
        },
    }


def derive_frontloaded_skill_candidates(
    state: dict,
    *,
    skill_field: dict | None = None,
    probe_discipline: dict | None = None,
    controller_trigger: dict | None = None,
) -> tuple[list[str], str]:
    non_teaching_skills = {
        "外壳怀疑",
        "最终控制者",
        "抓本质",
        "更薄载体重选",
        "元认知",
        "监督",
        "中枢控制",
        "后脑守卫",
        "奖惩塑形",
    }
    读出_like_skills = {
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
    }
    ordered: list[str] = []

    def push(raw_skill: object) -> None:
        canonical = canonicalize_skill_token(raw_skill)
        if canonical and canonical not in non_teaching_skills and canonical not in ordered:
            ordered.append(canonical)

    explicit_layer = state.get("layer_composition_if_any")
    if isinstance(explicit_layer, dict):
        push(explicit_layer.get("leading_skill_if_any"))
        authorized_bite = explicit_layer.get("authorized_bite")
        if isinstance(authorized_bite, dict):
            push(authorized_bite.get("owner_skill_if_any"))
            for value in authorized_bite.get("owner_skill_combo_if_any", []):
                push(value)

    if isinstance(probe_discipline, dict):
        push(probe_discipline.get("active_skill_hypothesis"))
        for value in probe_discipline.get("active_skill_hypotheses", []):
            push(value)

    if isinstance(skill_field, dict):
        for key in [
            "authority_skill_if_any",
            "bound_skill_if_any",
            "closure_authority_skill_if_any",
        ]:
            push(skill_field.get(key))
        for value in skill_field.get("active_skills", []):
            push(value)

    if isinstance(controller_trigger, dict):
        for value in controller_trigger.get("favored_combo", []):
            push(value)
        for value in controller_trigger.get("favored_skills", []):
            push(value)

    lead_skill = next(
        (skill for skill in ordered if skill not in 读出_like_skills),
        ordered[0] if ordered else "",
    )
    return ordered[:INTERNAL_CANDIDATE_LIGHT_LIMIT], lead_skill


def derive_skill_lighting_surface(
    state: dict,
    problems: list[str],
    *,
    control_signals_override: dict | None = None,
    skill_field_override: dict | None = None,
    skill_competition_override: dict | None = None,
    probe_discipline_override: dict | None = None,
    self_check_agenda_override: dict | None = None,
) -> dict | None:
    if problems:
        return None

    control_signals = (
        control_signals_override
        if control_signals_override is not None
        else derive_control_signals(state, problems)
    )
    skill_field = (
        skill_field_override
        if skill_field_override is not None
        else derive_skill_field(
            state,
            problems,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        )
    )
    probe_discipline = (
        probe_discipline_override
        if probe_discipline_override is not None
        else derive_probe_discipline(
            state,
            problems,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        )
    )
    agenda = (
        self_check_agenda_override
        if self_check_agenda_override is not None
        else derive_self_check_agenda(state, problems)
    )
    frontloaded_candidates, frontloaded_lead = derive_frontloaded_skill_candidates(
        state,
        skill_field=skill_field if isinstance(skill_field, dict) else None,
        probe_discipline=probe_discipline if isinstance(probe_discipline, dict) else None,
    )
    skill_competition = (
        skill_competition_override
        if skill_competition_override is not None
        else derive_skill_competition(
            state,
            problems,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
            skill_field_override=skill_field if isinstance(skill_field, dict) else None,
            probe_discipline_override=probe_discipline if isinstance(probe_discipline, dict) else None,
            lit_candidate_override=frontloaded_candidates,
        )
    )

    non_teaching_skills = {
        "外壳怀疑",
        "最终控制者",
        "抓本质",
        "更薄载体重选",
        "元认知",
        "监督",
        "中枢控制",
        "后脑守卫",
        "奖惩塑形",
    }
    读出_like_skills = {
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
    }

    lead_skill = frontloaded_lead
    candidate_skills: list[str] = frontloaded_candidates[:]
    candidate_routes: list[dict] = []
    if isinstance(skill_competition, dict):
        competition_winner = canonicalize_skill_token(skill_competition.get("winning_skill_if_any"))
        if competition_winner and competition_winner in candidate_skills:
            lead_skill = competition_winner
        elif not lead_skill and competition_winner:
            lead_skill = competition_winner
        winning_gain_reason = nonempty_text(skill_competition.get("winning_projected_gain_reason"))
        for candidate in skill_competition.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            canonical = canonicalize_skill_token(candidate.get("skill"))
            if canonical and canonical not in non_teaching_skills and canonical not in candidate_skills:
                candidate_skills.append(canonical)
            if canonical and canonical not in non_teaching_skills:
                candidate_routes.append(
                    {
                        "skill": canonical,
                        "projected_gain_rank": int(candidate.get("projected_gain_rank", 8)),
                        "projected_gain_reason": nonempty_text(candidate.get("projected_gain_reason")),
                    }
                )
    else:
        winning_gain_reason = ""
    candidate_routes = sorted(
        candidate_routes,
        key=lambda item: (
            int(item.get("projected_gain_rank", 8)),
            0 if str(item.get("skill", "")).strip() == lead_skill else 1,
            str(item.get("skill", "")).strip(),
        ),
    )
    deduped_routes: list[dict] = []
    seen_route_skills: set[str] = set()
    for route in candidate_routes:
        skill_name = str(route.get("skill", "")).strip()
        if skill_name and skill_name not in seen_route_skills:
            seen_route_skills.add(skill_name)
            deduped_routes.append(route)
    candidate_routes = deduped_routes[:4]
    if not lead_skill and isinstance(skill_competition, dict):
        lead_skill = canonicalize_skill_token(skill_competition.get("winning_skill_if_any"))
    if not lead_skill and candidate_skills:
        lead_skill = next(
            (skill for skill in candidate_skills if skill not in 读出_like_skills),
            candidate_skills[0],
        )
    if lead_skill and lead_skill not in candidate_skills:
        candidate_skills.insert(0, lead_skill)
    if not candidate_skills and not lead_skill:
        return None
    controller_trigger = (
        skill_field.get("controller_trigger_if_any", {})
        if isinstance(skill_field, dict)
        else {}
    )

    partner_skill = next((skill for skill in candidate_skills if skill and skill != lead_skill), "")
    if candidate_routes:
        partner_skill = next(
            (
                str(route.get("skill", "")).strip()
                for route in candidate_routes
                if str(route.get("skill", "")).strip()
                and str(route.get("skill", "")).strip() != lead_skill
            ),
            partner_skill,
        )
    structural_partner = next(
        (
            skill for skill in candidate_skills
            if skill and skill != lead_skill and skill not in 读出_like_skills
        ),
        "",
    )

    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    touch_target = nonempty_text(state.get("current_object"))
    preferred_kind = "check"
    if isinstance(agenda, dict):
        touch_target = nonempty_text(agenda.get("touch_target")) or touch_target
        raw_kinds = agenda.get("preferred_kinds")
        if isinstance(raw_kinds, list) and raw_kinds:
            preferred_kind = nonempty_text(raw_kinds[0]) or preferred_kind
    if isinstance(probe_discipline, dict):
        touch_target = nonempty_text(probe_discipline.get("preferred_probe_target")) or touch_target
        raw_probe_kinds = probe_discipline.get("allowed_probe_kinds")
        if isinstance(raw_probe_kinds, list) and raw_probe_kinds:
            preferred_kind = nonempty_text(raw_probe_kinds[0]) or preferred_kind

    false_first_skill = ""
    false_first_label = ""
    false_skill_reason = ""
    if lead_skill and lead_skill not in 读出_like_skills and any(
        skill in 读出_like_skills for skill in candidate_skills
    ):
        false_first_skill = "读出"
        false_skill_reason = f"`读出` 更像 `{lead_skill}` 接管之后的读出层，不该抢第一接管。"
    elif lead_skill == "反问":
        false_first_label = "explanation_without_touch"
        false_skill_reason = "继续解释不算进展，先让一个 `check` 或 `见证` 真落地。"
    explicit_layer = state.get("layer_composition_if_any")
    accountability_nudge = ""
    if (
        lead_skill
        and not isinstance(explicit_layer, dict)
        and isinstance(probe_discipline, dict)
        and probe_discipline.get("probe_must_bind") is True
    ):
        accountability_nudge = (
            f"如果 `{lead_skill}` 真在接管，它应该先在当前层留下一个可执行触点，而不是事后补标签。"
        )
    supporting_skills = [
        skill for skill in candidate_skills
        if skill and skill != lead_skill
    ][:4]
    probe_or_check_skills = {
        "见证",
        "反问",
        "极限边界",
        "边界找路",
        "特殊值探针",
        "相容",
        "不算而比",
        "对称",
        "对称消元",
    }
    check_skill = next(
        (
            skill
            for skill in candidate_skills
            if skill and skill != lead_skill and skill in probe_or_check_skills
        ),
        "",
    )
    if not check_skill:
        check_skill = next(
            (
                canonicalize_skill_token(route.get("skill"))
                for route in candidate_routes
                if isinstance(route, dict)
                and canonicalize_skill_token(route.get("skill"))
                and canonicalize_skill_token(route.get("skill")) != lead_skill
                and canonicalize_skill_token(route.get("skill")) in probe_or_check_skills
            ),
            "",
        )
    if check_skill and check_skill not in supporting_skills and check_skill != lead_skill:
        supporting_skills = [check_skill] + [
            skill for skill in supporting_skills if skill != check_skill
        ]
        supporting_skills = supporting_skills[:4]
    verify_touch = {}
    if touch_target:
        verify_touch = {
            "target": touch_target,
            "kind": preferred_kind,
        }
    asked_medium_warning = ""
    if asked_medium and touch_target == asked_medium:
        asked_medium_warning = "现在如果直接扑向 asked medium，先确认这是不是当前层真正的第一接管。"
    if not (
        lead_skill
        or false_first_skill
        or false_first_label
        or candidate_skills
        or supporting_skills
        or verify_touch
        or accountability_nudge
        or asked_medium_warning
    ):
        return None

    def derive_subordinate_ordinary_operation_policy() -> tuple[list[str], list[str]]:
        allowed: list[str] = []
        blocked: list[str] = [
            "local_calculus_probe",
            "case_split",
            "equation_solving",
            "enumeration",
            "full_route_reconstruction",
        ]
        if lead_skill:
            allowed.append("symbol_binding")
        if check_skill or (
            isinstance(verify_touch, dict)
            and nonempty_text(verify_touch.get("kind")) in {"check", "见证"}
        ):
            allowed.append("numerical_check")
        if lead_skill in {"图像", "投影", "函数原型匹配", "容器到截面", "面积到线读出"}:
            allowed.extend(["diagram_annotation", "symbol_binding"])
        return (
            [value for value in dict.fromkeys(allowed) if value],
            [value for value in dict.fromkeys(blocked) if value],
        )

    allowed_subordinate_operation_families, blocked_ordinary_operation_families = (
        derive_subordinate_ordinary_operation_policy()
    )

    role_split_if_any: dict = {}
    if lead_skill:
        role_split_if_any["primary_skill_if_any"] = lead_skill
    if supporting_skills:
        role_split_if_any["supporting_skills_if_any"] = supporting_skills[:4]
    if check_skill:
        role_split_if_any["check_skill_if_any"] = check_skill
    if isinstance(verify_touch, dict):
        verify_target = nonempty_text(verify_touch.get("target"))
        verify_kind = nonempty_text(verify_touch.get("kind"))
        if verify_kind:
            role_split_if_any["check_kind_if_any"] = verify_kind
        if verify_target:
            role_split_if_any["check_target_if_any"] = verify_target
    if allowed_subordinate_operation_families:
        role_split_if_any["allowed_subordinate_operation_families_if_any"] = (
            allowed_subordinate_operation_families[:8]
        )
    if blocked_ordinary_operation_families:
        role_split_if_any["blocked_ordinary_operation_families_if_any"] = (
            blocked_ordinary_operation_families[:8]
        )
    if role_split_if_any:
        role_split_if_any["ordinary_operations_are_not_skills"] = True

    ability_branch_if_any = {
        "support_operation_is_subordinate": True,
        "note": (
            "if the leading skill already lands directly, keep helper operations quiet; "
            "otherwise use one support touch or ordinary helper only to stabilize or verify the same leading skill"
        ),
        "ordinary_operation_policy_if_any": {
            "allowed_subordinate_families_if_any": allowed_subordinate_operation_families[:8],
            "blocked_families_if_any": blocked_ordinary_operation_families[:8],
        },
    }
    competition_basis = "projected_gain_first_takeover"
    arbitration_skill = ""
    counter_question = ""
    favored_combo = []
    if isinstance(controller_trigger, dict):
        arbitration_skill = canonicalize_skill_token(controller_trigger.get("arbitration_skill_if_any")) or ""
        counter_question = nonempty_text(controller_trigger.get("counter_question_if_any"))
        favored_combo = _normalize_skill_combo(controller_trigger.get("favored_combo"), limit=6)
        if arbitration_skill == "反问" and nonempty_text(controller_trigger.get("mode")) == "counter_question_arbitration":
            competition_basis = "counter_question_arbitrated_projected_gain"

    payload = {
        "lit_skill_if_any": lead_skill,
        "candidate_skills_if_any": candidate_skills[:6],
        "supporting_skills_if_any": supporting_skills,
        "false_first_skill_if_any": false_first_skill,
        "false_first_label_if_any": false_first_label,
        "false_skill_reason": false_skill_reason,
        "verify_touch_if_any": verify_touch,
        "accountability_nudge_if_any": accountability_nudge,
        "winning_projected_gain_reason": winning_gain_reason,
        "competing_routes_if_any": candidate_routes,
        "comparison_skill_if_any": structural_partner or partner_skill,
        "competition_basis": competition_basis,
        "role_split_if_any": role_split_if_any,
        "ability_branch_if_any": ability_branch_if_any,
        "asked_medium_warning_if_any": asked_medium_warning,
        "project_skill_only": True,
        "ordinary_operations_are_not_skills": True,
        "local_only": True,
        "anti_pipeline_note": "these prompts are current-layer pressure surfaces, not a required order",
    }
    if arbitration_skill:
        payload["arbitration_skill_if_any"] = arbitration_skill
    if counter_question:
        payload["counter_question_if_any"] = counter_question
    if favored_combo:
        payload["favored_combo_if_any"] = favored_combo[:6]
    return {
        key: value
        for key, value in payload.items()
        if value not in (None, "", [], {})
    }


def derive_layer_arena(
    state: dict,
    problems: list[str],
    *,
    skill_field_override: dict | None = None,
    skill_competition_override: dict | None = None,
    skill_authority_override: dict | None = None,
    skill_lighting_override: dict | None = None,
    probe_discipline_override: dict | None = None,
    arena_surface: str = "layer_arena",
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

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
    skill_authority = (
        skill_authority_override
        if skill_authority_override is not None
        else derive_skill_authority_bridge(state, problems)
    )
    probe_discipline = (
        probe_discipline_override
        if probe_discipline_override is not None
        else derive_probe_discipline(
            state,
            problems,
            skill_field_override=skill_field if isinstance(skill_field, dict) else None,
            skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
        )
    )
    lighting = (
        skill_lighting_override
        if skill_lighting_override is not None
        else derive_skill_lighting_surface(
            state,
            problems,
            skill_field_override=skill_field if isinstance(skill_field, dict) else None,
            skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
            probe_discipline_override=probe_discipline if isinstance(probe_discipline, dict) else None,
        )
    )
    if not any(
        isinstance(surface, dict)
        for surface in [skill_field, skill_competition, skill_authority, lighting]
    ):
        return None

    explicit_layer = state.get("layer_composition_if_any")
    explicit_focus_target = ""
    if isinstance(explicit_layer, dict):
        explicit_focus_target = (
            nonempty_text(explicit_layer.get("next_local_choice"))
            or nonempty_text(explicit_layer.get("controlled_object"))
            or nonempty_text(explicit_layer.get("gap_object"))
            or nonempty_text(explicit_layer.get("current_seam"))
        )

    primary_skill = canonicalize_skill_token((lighting or {}).get("lit_skill_if_any"))
    if not primary_skill:
        primary_skill = canonicalize_skill_token(
            (skill_authority or {}).get("winning_skill_if_any")
            or (skill_competition or {}).get("winning_skill_if_any")
        )
    focus_target = nonempty_text(((lighting or {}).get("verify_touch_if_any") or {}).get("target"))
    preferred_kind = nonempty_text(((lighting or {}).get("verify_touch_if_any") or {}).get("kind"))
    winning_candidate = None
    if isinstance(skill_competition, dict) and primary_skill:
        winning_candidate = next(
            (
                candidate
                for candidate in skill_competition.get("candidates", [])
                if isinstance(candidate, dict)
                and canonicalize_skill_token(candidate.get("skill")) == primary_skill
            ),
            None,
        )
    focus_target = (
        (
            explicit_focus_target
            if isinstance(explicit_layer, dict)
            and explicit_layer.get("event_owned") is True
            and _event_owned_layer_matches_live_surface(state, explicit_layer)
            and nonempty_text(explicit_layer.get("surface")) in {"bound_program", "takeover_recomposition"}
            else ""
        )
        or focus_target
        or nonempty_text((winning_candidate or {}).get("touch_target"))
        or nonempty_text(state.get("current_seam"))
        or nonempty_text(state.get("current_debt"))
        or nonempty_text(state.get("next_bite"))
        or nonempty_text(state.get("current_object"))
        or nonempty_text(state.get("asked_medium_surface"))
    )

    lit_skills: list[str] = []
    if isinstance(lighting, dict):
        for value in lighting.get("candidate_skills_if_any", []):
            canonical = canonicalize_skill_token(value)
            if canonical and canonical not in lit_skills:
                lit_skills.append(canonical)
    if isinstance(skill_field, dict):
        for value in skill_field.get("active_skills", []):
            canonical = canonicalize_skill_token(value)
            if canonical and canonical not in lit_skills:
                lit_skills.append(canonical)

    supporting_skills = [
        canonicalize_skill_token(value)
        for value in ((lighting or {}).get("supporting_skills_if_any") or [])
        if canonicalize_skill_token(value)
    ]
    role_split = (
        dict((lighting or {}).get("role_split_if_any"))
        if isinstance((lighting or {}).get("role_split_if_any"), dict)
        else {}
    )
    check_skill = canonicalize_skill_token(role_split.get("check_skill_if_any"))
    if check_skill and check_skill != primary_skill and check_skill not in supporting_skills:
        supporting_skills.append(check_skill)
    verify_touch = None
    if focus_target:
        verify_touch = {
            "target": focus_target,
            "kind": preferred_kind or "check",
        }

    authorized_touch = None
    if isinstance(skill_authority, dict):
        raw_touch = skill_authority.get("executable_local_touch_if_any")
        if isinstance(raw_touch, dict):
            authorized_touch = {
                key: raw_touch.get(key)
                for key in [
                    "kind",
                    "target",
                    "operation",
                    "success_signal",
                    "owner_skill_if_any",
                    "owner_skill_combo_if_any",
                ]
                if raw_touch.get(key) not in (None, "", [], {})
            }
    generic_authorized_touch = (
        isinstance(authorized_touch, dict)
        and is_generic_runtime_operation(authorized_touch)
    )
    if (
        focus_target
        and primary_skill
        and (
            not isinstance(authorized_touch, dict)
            or nonempty_text(authorized_touch.get("target")) != focus_target
            or generic_authorized_touch
        )
    ):
        rebuilt = build_problem_born_touch_for_skill(
            state,
            primary_skill,
            target=focus_target,
            supporting=supporting_skills,
        )
        if isinstance(rebuilt, dict) and not is_generic_runtime_operation(rebuilt):
            authorized_touch = rebuilt
            generic_authorized_touch = False

    executable_touch_ready = (
        isinstance(authorized_touch, dict)
        and not is_generic_runtime_operation(authorized_touch)
    )
    if not executable_touch_ready:
        authorized_touch = None
        primary_skill = ""
        supporting_skills = []
        role_split = {}
        check_skill = ""

    active_skill_combo = []
    if isinstance(authorized_touch, dict):
        active_skill_combo = extract_explicit_skill_combo(authorized_touch)
    if not active_skill_combo and primary_skill:
        active_skill_combo.append(primary_skill)
    for value in supporting_skills:
        canonical = canonicalize_skill_token(value)
        if canonical and canonical not in active_skill_combo:
            active_skill_combo.append(canonical)
    if check_skill and check_skill not in active_skill_combo:
        active_skill_combo.append(check_skill)

    payload = {
        "active": True,
        "surface": arena_surface,
        "layer_object": nonempty_text(state.get("current_object")) or nonempty_text(state.get("current_debt")),
        "focus_target": focus_target,
        "primary_skill_if_any": primary_skill,
        "lit_skills_if_any": lit_skills[:8],
        "supporting_skills_if_any": supporting_skills[:6],
        "active_skill_combo_if_any": active_skill_combo[:6],
        "verify_touch_if_any": verify_touch,
        "role_split_if_any": role_split,
        "false_first_skill_if_any": nonempty_text((lighting or {}).get("false_first_skill_if_any")),
        "false_skill_reason": nonempty_text((lighting or {}).get("false_skill_reason")),
        "winning_projected_gain_reason": nonempty_text((lighting or {}).get("winning_projected_gain_reason")),
        "anti_pipeline_note": nonempty_text((lighting or {}).get("anti_pipeline_note")),
        "competition_basis": nonempty_text((lighting or {}).get("competition_basis")) or "projected_gain_first_takeover",
    }
    if isinstance(skill_competition, dict):
        payload["competition_winner_if_any"] = nonempty_text(skill_competition.get("winning_skill_if_any"))
        candidates = []
        for candidate in skill_competition.get("candidates", [])[:8]:
            if not isinstance(candidate, dict):
                continue
            compact = {
                key: candidate.get(key)
                for key in [
                    "skill",
                    "touch_target",
                    "projected_gain_rank",
                    "projected_gain_reason",
                    "backed_by",
                    "supporting_skills_if_any",
                ]
                if candidate.get(key) not in (None, "", [], {})
            }
            if compact:
                candidates.append(compact)
        if candidates:
            payload["candidates"] = candidates
    if isinstance(authorized_touch, dict):
        payload["authorized_touch_if_any"] = authorized_touch
        payload["preferred_kinds"] = [nonempty_text(authorized_touch.get("kind"))]
    elif preferred_kind:
        payload["preferred_kinds"] = [preferred_kind]
    if isinstance(skill_authority, dict):
        payload["same_carrier_only"] = skill_authority.get("same_carrier_only") is True
    return {
        key: value
        for key, value in payload.items()
        if value not in (None, "", [], {})
    }


def derive_first_layer_arena(
    state: dict,
    problems: list[str],
    *,
    skill_field_override: dict | None = None,
    skill_competition_override: dict | None = None,
    skill_authority_override: dict | None = None,
    skill_lighting_override: dict | None = None,
    probe_discipline_override: dict | None = None,
) -> dict | None:
    return derive_layer_arena(
        state,
        problems,
        skill_field_override=skill_field_override,
        skill_competition_override=skill_competition_override,
        skill_authority_override=skill_authority_override,
        skill_lighting_override=skill_lighting_override,
        probe_discipline_override=probe_discipline_override,
        arena_surface="first_layer_arena",
    )


def derive_local_skill_coaching_surface(
    state: dict,
    problems: list[str],
    *,
    control_signals_override: dict | None = None,
    skill_field_override: dict | None = None,
    skill_competition_override: dict | None = None,
    probe_discipline_override: dict | None = None,
    self_check_agenda_override: dict | None = None,
) -> dict | None:
    lighting = derive_skill_lighting_surface(
        state,
        problems,
        control_signals_override=control_signals_override,
        skill_field_override=skill_field_override,
        skill_competition_override=skill_competition_override,
        probe_discipline_override=probe_discipline_override,
        self_check_agenda_override=self_check_agenda_override,
    )
    if not isinstance(lighting, dict):
        return None

    lead_skill = canonicalize_skill_token(lighting.get("lit_skill_if_any"))
    comparison_skill = canonicalize_skill_token(lighting.get("comparison_skill_if_any"))
    false_skill_reason = nonempty_text(lighting.get("false_skill_reason"))
    accountability_nudge = nonempty_text(lighting.get("accountability_nudge_if_any"))
    asked_medium_warning = nonempty_text(lighting.get("asked_medium_warning_if_any"))
    verify_touch = lighting.get("verify_touch_if_any")
    role_split = lighting.get("role_split_if_any")
    ordinary_action_counter_question = ""
    ordinary_action_denial = ""
    skill_positive_handoff = ""
    if isinstance(role_split, dict) and role_split.get("ordinary_operations_are_not_skills") is True and lead_skill:
        ordinary_action_counter_question = "这一步真的需要先引入新的普通流程、先设/求导/分类/解方程，或回到厚对象吗？"
        ordinary_action_denial = "这里不需要先长出新的普通 machinery（设元、求导、分类、解方程等）或回到厚对象，普通操作不等于当前层技能接管。"
        skill_positive_handoff = f"应该先让 `{lead_skill}` 在当前授权触点上真的接管，再决定是否需要后续从属检查。"

    speech_acts: dict[str, str] = {}
    if lead_skill:
        speech_acts["反问"] = f"这一步第一层不就是 `{lead_skill}` 吗？"
        speech_acts["assertion"] = f"这一层先点亮的就是 `{lead_skill}`。"
        speech_acts["layer_split"] = f"这一层是谁在接管，谁只是在辅助 `{lead_skill}`？"
    if lead_skill and comparison_skill and comparison_skill != lead_skill:
        speech_acts["contrast"] = (
            f"这里第一步该上 `{lead_skill}` 还是 `{comparison_skill}`？谁才是第一接管？"
        )
    if false_skill_reason:
        speech_acts["negation"] = false_skill_reason
    if isinstance(verify_touch, dict):
        verify_target = nonempty_text(verify_touch.get("target"))
        verify_kind = nonempty_text(verify_touch.get("kind"))
        if verify_target and verify_kind:
            speech_acts["do_now"] = (
                f"别只附和，现在就在 `{verify_target}` 上做一个 `{verify_kind}` 看看。"
            )
    if accountability_nudge:
        speech_acts["accountability"] = accountability_nudge
    if asked_medium_warning:
        speech_acts["asked_medium_warning"] = asked_medium_warning
    if ordinary_action_counter_question:
        speech_acts["ordinary_counter_question"] = ordinary_action_counter_question
    if ordinary_action_denial:
        speech_acts["ordinary_denial"] = ordinary_action_denial
    if skill_positive_handoff:
        speech_acts["skill_handoff"] = skill_positive_handoff

    payload = dict(lighting)
    payload["candidate_skill_if_any"] = lighting.get("lit_skill_if_any", "")
    if ordinary_action_counter_question:
        payload["ordinary_action_counter_question_if_any"] = ordinary_action_counter_question
    if ordinary_action_denial:
        payload["ordinary_action_denial_if_any"] = ordinary_action_denial
    if skill_positive_handoff:
        payload["skill_positive_handoff_if_any"] = skill_positive_handoff
    payload["speech_acts"] = speech_acts
    return payload

    layerwise_reselection_pressure = derive_layerwise_reselection_pressure(
        {
            "carrier_status": carrier_status,
            "外壳怀疑": 外壳怀疑,
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
            "外壳怀疑": 外壳怀疑,
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
        "composition_pressure": composition_pressure,
        "raw_composition_pressure": raw_composition_pressure,
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
                "promote": "object_change_or_exact_读出",
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
            "反问": {
                "active": 反问_active,
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
            "元认知": {
                "active": 元认知_active,
                "action_tendency": "re-check_owner_carrier_and_false_essence_live",
            },
            "中枢控制": {
                "mode": central_mode,
                "action_tendency": "bias_one_local_owner_until_change_or_check",
            },
            "后脑守卫": {
                "active": 后脑守卫_active,
                "action_tendency": "keep_non_release_latch_and_reopen_smallest_honest_exit",
            },
        },
    }

def derive_object_compiled_program_candidate(
    state: dict,
    *,
    primitives: list[str],
    layer_object: str,
    current_debt: str,
    next_bite: str,
    seam_target: str,
    object_target: str,
    tie_break_check: str,
) -> dict | None:
    if not state_allows_task_route_synthesis(state):
        return None

    text_bank = " ".join(
        value
        for value in [
            nonempty_text(state.get("current_object")),
            nonempty_text(state.get("current_seam")),
            layer_object,
            current_debt,
            next_bite,
            seam_target,
            object_target,
        ]
        if value
    ).lower()
    trio = {value for value in primitives[:3] if value}
    pair = {value for value in primitives[:2] if value}
    normalized_combo = _normalize_skill_combo(primitives[:3])
    lead_skill = normalized_combo[0] if normalized_combo else ""
    decisive_check_owner = (
        "见证"
        if "见证" in normalized_combo
        else lead_skill
    )

    abs_like = "|" in text_bank or "absolute" in text_bank
    fixed_k_like = "fixed-k" in text_bank or "fixed k" in text_bank or "min_x" in text_bank
    piecewise_like = "piecewise" in text_bank or "branch" in text_bank
    slope_like = "slope" in text_bank or "middle-interval" in text_bank
    boundary_like = any(token in text_bank for token in ["k<1", "k>1", "k=1", "infinity"])
    binary_code_like = "binary" in text_bank and "string" in text_bank
    capacity_ledger_like = "capacity ledger" in text_bank or "code-capacity ledger" in text_bank
    length_capacity_like = "length" in text_bank and any(
        token in text_bank
        for token in [
            "capacity",
            "2^",
            "sum_{i=1}^l",
            "sum_{i=1}^l 2^i",
            "code space",
            "count how many",
            "available strings",
            "up to length",
            "length cap",
            "maximum codeword length",
            "worst-case length",
            "worst case length",
        ]
    )
    message_budget_like = "100000" in text_bank or "distinct messages" in text_bank
    finite_code_budget_like = (
        binary_code_like
        and any(
            token in text_bank
            for token in ["injective", "injectively", "message", "messages", "codeword", "codewords"]
        )
        and any(
            token in text_bank
            for token in [
                "up to length",
                "length cap",
                "maximum codeword length",
                "worst-case length",
                "worst case length",
                "available strings",
                "count how many",
            ]
        )
    )
    threshold_16_like = any(
        token in text_bank
        for token in ["65534", "131070", "l=15", "l = 15", "l=16", "l = 16", "16 is minimal"]
    )
    decoding_like = any(
        token in text_bank
        for token in [
            "decode",
            "injective encoding",
            "lengths up to 16",
            "remaining 34466",
            "first 34466",
        ]
    )
    deterministic_forward_map_like = any(
        token in text_bank
        for token in [
            "functional graph",
            "forward orbit",
            "orbit structure",
            "unique forward path",
            "unique forward paths",
        ]
    )
    path_membership_feasibility_like = any(
        token in text_bank
        for token in [
            "feasible",
            "impossible",
            "reachability",
            "destination lies",
            "impossibility filter",
            "reachability 见证",
        ]
    )
    pre_optimization_gate_like = any(
        token in text_bank
        for token in [
            "before any queueing optimization",
            "before optimization",
            "queueing optimization",
            "schedulable",
        ]
    )
    if (
        deterministic_forward_map_like
        and path_membership_feasibility_like
        and (pre_optimization_gate_like or "interval" in text_bank)
        and {"投影", "图像", "见证"}.issubset(trio)
    ):
        target = seam_target or object_target
        return _attach_skill_metadata({
            "kind": "check",
            "target": target,
            "operation": (
                "draw the forward-orbit 图像, project each request to its unique orbit interval, "
                "and land one feasibility 见证 separating impossible requests from schedulable ones"
            ),
            "success_signal": f"orbit-interval feasibility 见证 became explicit on {target}",
        }, owner_skill=decisive_check_owner, combo=normalized_combo)

    if (
        pair == {"投影", "守恒"}
        and (
            (binary_code_like and length_capacity_like and (message_budget_like or finite_code_budget_like))
            or (capacity_ledger_like and "2^" in text_bank)
        )
    ):
        target = seam_target or object_target
        ledger_combo = _normalize_skill_combo(["投影", "守恒"])
        return _attach_skill_metadata({
            "kind": "write",
            "target": target,
            "operation": (
                "collapse raw strings into the exact per-length capacity ledger and write "
                "C(L)=2^1+2^2+...+2^L = 2^{L+1}-2 before any feasibility verdict"
            ),
            "success_signal": f"per-length capacity ledger became explicit on {target}",
        }, owner_skill="投影", combo=ledger_combo)

    if abs_like and fixed_k_like and (
        trio == {"状态拆分", "投影", "见证"}
        or trio == {"投影", "见证", "特殊值探针"}
        or pair == {"投影", "见证"}
    ):
        target = object_target or seam_target
        return _attach_skill_metadata({
            "kind": "write",
            "target": target,
            "operation": (
                "fix the parameter, rewrite the expression as a weighted sum of two distances on the real line, "
                "decide the minimizer by the middle-interval slope / weighted-median check, probe the decisive center ordering if needed, "
                "and materialize the exact piecewise minimum carrier"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"fixed-parameter weighted-absolute-value minimum became explicit on {target}",
        }, owner_skill=decisive_check_owner, combo=normalized_combo)

    if piecewise_like and boundary_like and {"投影", "见证", "极限边界"}.issubset(trio):
        target = seam_target or object_target
        return _attach_skill_metadata({
            "kind": "check",
            "target": target,
            "operation": (
                "compare the piecewise branches on the true boundary set, test k<1 / k=1 / k>1 against the branch switch, "
                "and decide whether the global minimum is attained or only approached at infinity"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"piecewise boundary controller became explicit on {target}",
        }, owner_skill=decisive_check_owner, combo=normalized_combo)

    if piecewise_like and boundary_like and {"第一裂缝", "极限边界"}.issubset(trio):
        target = seam_target or object_target
        return _attach_skill_metadata({
            "kind": "check",
            "target": target,
            "operation": (
                "locate the first branch switch / weakest seam in the piecewise family, push the true boundary there, and use that crack to decide the global settlement"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"first-crack boundary controller became explicit on {target}",
        }, owner_skill=decisive_check_owner, combo=normalized_combo)

    if abs_like and slope_like and pair == {"投影", "见证"}:
        target = seam_target or object_target
        return _attach_skill_metadata({
            "kind": "check",
            "target": target,
            "operation": (
                "project the absolute-value carrier onto the interval-slope comparison and use one sign 见证 to decide which side owns the minimizer"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"interval-slope 见证 separated the live minimizer on {target}",
        }, owner_skill=primitive, combo=normalized_combo)

    return None


def derive_object_compiled_读出_candidate(
    state: dict,
    *,
    asked_medium: str,
    current_object: str,
    current_debt: str,
    current_seam: str,
    next_bite: str,
    structural_bite: dict | None = None,
) -> dict | None:
    if not asked_medium:
        return None

    text_bank = " ".join(
        value
        for value in [asked_medium, current_object, current_debt, current_seam, next_bite]
        if value
    ).lower()
    abs_like = "|" in text_bank or "absolute" in text_bank
    piecewise_like = "piecewise" in text_bank or "branch" in text_bank
    minimum_like = "minimum" in text_bank or "min" in text_bank or "infimum" in text_bank
    boundary_like = any(token in text_bank for token in ["k<1", "k>1", "k=1", "infinity", "boundary"])
    operation = ""

    if piecewise_like and minimum_like and boundary_like:
        operation = (
            "write the exact piecewise minimum on the asked medium, compare the branches at the true switch and at infinity, "
            "and state clearly whether the infimum is attained or only approached"
        )
    elif abs_like and minimum_like:
        operation = (
            "write the fixed-parameter minimum and then seal it into the asked medium as the exact piecewise answer with the final attainment conclusion"
        )
    elif current_object or current_debt:
        object_phrase = current_object or current_debt
        seam_phrase = current_seam or next_bite
        operation = (
            f"seal the current thinner carrier into the asked medium by writing the exact answer forced by {object_phrase}"
            + (f" and closing the live seam {seam_phrase}" if seam_phrase else "")
        )

    if not operation:
        return None

    primitive_field = state.get("primitive_field_if_any")
    primitive_active = (
        primitive_field.get("active_primitives")
        if isinstance(primitive_field, dict)
        else None
    )
    primitive_competition = state.get("primitive_competition_if_any")
    competition_candidates = (
        [
            canonicalize_skill_token(candidate.get("primitive"))
            for candidate in primitive_competition.get("candidates", [])
            if isinstance(candidate, dict)
            and canonicalize_skill_token(candidate.get("primitive"))
        ]
        if isinstance(primitive_competition, dict)
        else None
    )
    owner_combo = _closure_combo_from_sources(
        structural_bite if isinstance(structural_bite, dict) else None,
        primitive_active,
        competition_candidates,
    )
    owner_skill = _closure_owner_from_combo(
        structural_bite if isinstance(structural_bite, dict) else None,
        primitive_active,
        competition_candidates,
        preferred_owner="读出",
    )
    if not owner_combo or not owner_skill:
        return None

    return {
        "kind": "write",
        "target": asked_medium,
        "operation": operation,
        "success_signal": "asked_medium_is_exact_and_executable",
        "origin": "asked_medium_closure_compiled",
        "owner_skill_if_any": owner_skill,
        "owner_skill_combo_if_any": owner_combo[:6],
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
        primitive_field = derive_primitive_field_candidate(state, problems)
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
    evidence_basis = nonempty_text(primitive_field.get("evidence_basis"))
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
    explicit_layer = state.get("layer_composition_if_any")
    carrier_handoff = state.get("carrier_handoff_if_any")
    handoff_target = (
        nonempty_text(carrier_handoff.get("to_object"))
        if isinstance(carrier_handoff, dict)
        else ""
    )
    handoff_target_must_bind = bool(
        handoff_target
        and (
            isinstance(carrier_handoff, dict)
            or (
                isinstance(explicit_layer, dict)
                and explicit_layer.get("must_spend_handoff") is True
            )
        )
    )
    fresh_blind_first_touch_pending = fresh_blind_problem_first_touch_pending(
        state,
        asked_medium=asked_medium,
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
    secondary_primitive = canonical_primitives[1] if len(canonical_primitives) > 1 else ""
    lead_skill = primitive
    normalized_combo = _normalize_skill_combo(canonical_primitives[:3])

    def owned(program: dict | None) -> dict | None:
        shaped = _attach_skill_metadata(program, owner_skill=primitive, combo=normalized_combo)
        if (
            isinstance(shaped, dict)
            and fresh_blind_first_touch_pending
            and nonempty_text(shaped.get("target")) == asked_medium
            and nonempty_text(shaped.get("kind")) in {"check", "见证"}
        ):
            return None
        return shaped
    unsupported_compression = bool(
        primitive in COMPRESSION_HEAVY_PRIMITIVES
        and (
            (
                selection_basis == "text_fallback"
                and evidence_basis in {"", "lexical_hint"}
            )
            or (
                isinstance(control_signals, dict)
                and isinstance(control_signals.get("raw_composition_pressure"), dict)
                and control_signals["raw_composition_pressure"].get(
                    "compression_without_support"
                )
                is True
            )
        )
    )
    seam_target = choose_problem_facing_runtime_target(
        layer_object,
        state.get("current_seam"),
        state.get("current_object"),
        state.get("current_debt"),
    )
    object_target = choose_problem_facing_runtime_target(
        layer_object,
        seam_target,
        state.get("current_object"),
        state.get("current_debt"),
    )
    if handoff_target_must_bind:
        seam_target = handoff_target
        object_target = handoff_target
    focus = next_bite or current_debt or semantic_question or layer_object

    compiled_program = derive_object_compiled_program_candidate(
        state,
        primitives=canonical_primitives,
        layer_object=layer_object,
        current_debt=current_debt,
        next_bite=next_bite,
        seam_target=seam_target,
        object_target=object_target,
        tie_break_check=tie_break_check,
    )
    if isinstance(compiled_program, dict):
        return compiled_program

    def semantic_operation(fallback: str) -> str:
        return semantic_touch or fallback

    # Keep live two-skill formation executable when the current layer clearly has
    # both a transform-side owner and a 读出/probe-side owner. This prevents
    # the runtime from retaining plural skill pressure in 读出 only while
    # executing just the first primitive as a flattened placeholder.
    pair = {primitive, secondary_primitive} if secondary_primitive else {primitive}
    trio = {value for value in canonical_primitives[:3] if value}
    if trio == {"状态拆分", "投影", "见证"}:
        return _attach_skill_metadata({
            "kind": "check",
            "target": seam_target or object_target,
            "operation": (
                f"project onto {seam_target or object_target}, write the smallest exact state split there, and land one separating 见证 for {focus}"
            ),
            "success_signal": f"projected state split and 见证 became explicit on {seam_target or object_target}",
        }, owner_skill=primitive, combo=normalized_combo)
    if trio == {"投影", "守恒", "见证"}:
        target = seam_target or object_target
        anchor_touch = next_bite or f"project the live burden to one conserved ledger for {focus}"
        return _attach_skill_metadata({
            "kind": "write",
            "target": target,
            "operation": (
                f"{anchor_touch}, by projecting the current object to one conserved countable carrier and landing one 见证 on {target}"
            ),
            "success_signal": f"projected conserved carrier became explicit on {target}",
        }, owner_skill="投影", combo=normalized_combo)
    if trio == {"赋值", "图像", "极限边界"}:
        target = seam_target or object_target
        rewrite_touch = next_bite or f"draw the decisive boundary picture on {target} for {focus}"
        return _attach_skill_metadata({
            "kind": "write",
            "target": target,
            "operation": (
                f"{rewrite_touch}, by drawing one minimal problem diagram there, pinning one decisive boundary or landmark, and rewriting the governing relation for {focus}"
            ),
            "success_signal": f"thinner carrier 图像 with one anchored boundary controller became explicit on {target}",
        }, owner_skill=lead_skill or "图像", combo=normalized_combo)
    if pair == {"状态拆分", "投影"}:
        return _attach_skill_metadata({
            "kind": "write",
            "target": object_target,
            "operation": (
                f"project the burden onto {object_target} and materialize the smallest exact state split there for {focus}"
            ),
            "success_signal": f"projected state split became explicit on {object_target}",
        }, owner_skill=lead_skill, combo=normalized_combo)
    if {"对称", "极限边界"}.issubset(trio):
        return _attach_skill_metadata({
            "kind": "check",
            "target": seam_target,
            "operation": (
                f"guess the balanced boundary candidate on {seam_target} and test the first-crack seam for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"balanced boundary candidate was sharpened on {seam_target}",
        }, owner_skill=lead_skill, combo=normalized_combo)
    if {"投影", "定义即直接读出", "极限边界"}.issubset(trio):
        target = seam_target or object_target
        return _attach_skill_metadata({
            "kind": "check" if blocks_direct_closure else "write",
            "target": target,
            "operation": (
                f"project onto {target}, read the defining controller there, and push one first-crack boundary check for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"projected definition-side boundary controller sharpened on {target}",
        }, owner_skill=lead_skill, combo=normalized_combo)
    if {"边界找路", "特殊值探针"}.issubset(trio):
        return _attach_skill_metadata({
            "kind": "check",
            "target": seam_target,
            "operation": (
                f"push to the boundary candidate family on {seam_target} and test it with one decisive landmark value for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"boundary candidate family was separated on {seam_target}",
        }, owner_skill=lead_skill, combo=normalized_combo)
    if pair == {"对称", "极限边界"}:
        return _attach_skill_metadata({
            "kind": "check",
            "target": seam_target,
            "operation": (
                f"push one symmetric boundary / first-crack check on {seam_target} for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"symmetric boundary check sharpened or changed {seam_target}",
        }, owner_skill=lead_skill, combo=normalized_combo)
    if pair == {"对称", "特殊值探针"}:
        return _attach_skill_metadata({
            "kind": "check",
            "target": seam_target or object_target,
            "operation": (
                f"probe one 对称-locked landmark value on {seam_target or object_target} for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"对称-locked landmark probe sharpened {seam_target or object_target}",
        }, owner_skill=lead_skill, combo=normalized_combo)
    if pair == {"边界找路", "特殊值探针"}:
        return _attach_skill_metadata({
            "kind": "check",
            "target": seam_target,
            "operation": (
                f"guess the boundary candidate on {seam_target} and test it with one decisive landmark probe for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"boundary candidate family was separated on {seam_target}",
        }, owner_skill=lead_skill, combo=normalized_combo)
    if pair == {"投影", "定义即直接读出"}:
        target = asked_medium or object_target
        if blocks_direct_closure:
            return None
        return _attach_skill_metadata({
            "kind": "write" if asked_medium else "读出",
            "target": target,
            "operation": (
                f"project onto {target} and read the answer directly through the defining relation for {focus}"
            ),
            "success_signal": f"projected definition-side 读出 landed on {target}",
        }, owner_skill=lead_skill, combo=normalized_combo)

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

    if unsupported_compression:
        return None

    if primitive == "定义即直接读出":
        target = asked_medium or object_target
        if blocks_direct_closure:
            return None
        return owned({
            "kind": "write" if asked_medium else "读出",
            "target": target,
            "operation": semantic_operation(
                f"materialize one definition-side exact 读出 for {focus} on {target}"
            ),
            "success_signal": f"definition-side 读出 landed on {target}",
        })
    if primitive == "主导机制读出":
        if blocks_direct_closure:
            return None
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": f"isolate one dominant mechanism 读出 for {focus}",
            "success_signal": f"dominant mechanism 读出 became explicit on {object_target}",
        })
    if primitive == "向量差读出":
        target = asked_medium or object_target
        if blocks_direct_closure:
            return None
        return owned({
            "kind": "write" if asked_medium else "读出",
            "target": target,
            "operation": semantic_operation(
                f"read the target through one vector-difference controller for {focus}"
            ),
            "success_signal": f"vector-difference 读出 landed on {target}",
        })
    if primitive == "不算而比":
        target = seam_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                f"separate the live options on {target} by comparing without full calculation for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"comparison 见证 separated the live options on {target}",
        })
    if primitive == "反证":
        target = seam_target or object_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                f"push the current route on {target} to one impossible consequence and kill the branch if the original family would become illegal for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"反证 killed or sharply narrowed the live route on {target}",
        })
    if primitive == "第一裂缝":
        target = seam_target or object_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                f"write the earliest branch switch / singular seam on {target} and test the route exactly at that first crack for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"first-crack seam separated the live route on {target}",
        })
    if primitive == "重编码":
        target = object_target
        return owned({
            "kind": "write",
            "target": target,
            "operation": semantic_operation(
                f"re-encode the current carrier into one thinner truthful representation for {focus}"
            ),
            "success_signal": f"thinner re-encoded carrier became explicit on {target}",
        })
    if primitive == "局部缝控制整体":
        target = seam_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                f"probe the local seam on {target} as the global controller for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"local seam 见证 sharpened or killed the global line on {target}",
        })
    if primitive == "格点选排":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"materialize one grid-selection to permutation / exact-cover carrier for {focus}"
            ),
            "success_signal": f"grid-selection permutation carrier became explicit on {object_target}",
        })
    if primitive == "匹配替代概率":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"rewrite the burden as one exact matching / coexistence carrier for {focus}"
            ),
            "success_signal": f"matching carrier became explicit on {object_target}",
        })
    if primitive == "函数原型匹配":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"match the live object to one function archetype family for {focus}"
            ),
            "success_signal": f"function archetype became explicit on {object_target}",
        })
    if primitive == "先调模型后推导":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"call one governing model object before derivation for {focus}"
            ),
            "success_signal": f"governing model became explicit on {object_target}",
        })
    if primitive == "公共值压缩":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"compress the visible variables into one common-value controller for {focus}"
            ),
            "success_signal": f"common-value controller became explicit on {object_target}",
        })
    if primitive == "容器到截面":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"rewrite the burden through one container-to-cross-section carrier for {focus}"
            ),
            "success_signal": f"cross-section carrier became explicit on {object_target}",
        })
    if primitive == "面积到线读出":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"collapse the area burden to one line 读出 for {focus}"
            ),
            "success_signal": f"area-to-line 读出 became explicit on {object_target}",
        })
    if primitive == "点积投影":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"read the live burden through one dot-product 投影 controller for {focus}"
            ),
            "success_signal": f"dot-product 投影 became explicit on {object_target}",
        })
    if primitive == "投影读出":
        if blocks_direct_closure:
            return None
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"take one 投影-side exact 读出 for {focus}"
            ),
            "success_signal": f"投影 读出 became explicit on {object_target}",
        })
    if primitive == "规范归一化":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"rewrite the current carrier into one canonical normalized form for {focus}"
            ),
            "success_signal": f"canonical normalized carrier became explicit on {object_target}",
        })
    if primitive == "对称消元":
        target = object_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                f"use 对称 to kill fake variables on {target} for {focus}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"对称 killed fake variables on {target}",
        })
    if primitive == "边界找路":
        target = seam_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                semantic_operation(
                    f"use one boundary / first-crack probe on {target} to sharpen the live controller for {focus}"
                )
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"boundary route-finder sharpened or changed {target}",
        })
    if primitive == "特殊值探针":
        target = object_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                semantic_operation(
                    f"probe one decisive special value on {target} for {focus}"
                )
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"special-value probe separated the live burden on {target}",
        })

    if primitive == "读出":
        target = asked_medium or object_target
        if blocks_direct_closure:
            return None
        return owned({
            "kind": "write" if asked_medium else "读出",
            "target": target,
            "operation": semantic_operation(
                f"materialize exact 读出 for {focus} on {target}"
            ),
            "success_signal": f"exact 读出 landed on {target}",
        })
    if primitive == "见证":
        target = seam_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                semantic_operation(
                    f"run one separating 见证 on {target} for {focus}"
                )
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"见证 on {target} changed or killed the current line",
        })
    if primitive == "状态拆分":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"materialize one exact state split / quotient for {focus}"
            ),
            "success_signal": f"state split became explicit on {object_target}",
        })
    if primitive == "相容":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"materialize one 相容 / merge fragment for {focus}"
            ),
            "success_signal": f"相容 fragment landed on {object_target}",
        })
    if primitive == "图像":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"externalize one 图像 / graph object for {focus}"
            ),
            "success_signal": f"external 图像 became explicit on {object_target}",
        })
    if primitive == "反向":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_operation(
                f"rewrite the current carrier in 反向 form for {focus}"
            ),
            "success_signal": f"反向 owner became explicit on {object_target}",
        })
    if primitive == "投影":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": (
                semantic_touch
                or f"project the burden to a thinner carrier for {focus}"
            ),
            "success_signal": f"投影 became explicit on {object_target}",
        })
    if primitive == "守恒":
        return owned({
            "kind": "write",
            "target": object_target,
            "operation": semantic_touch or f"write one conserved ledger for {focus}",
            "success_signal": f"conserved ledger became explicit on {object_target}",
        })
    if primitive == "极限边界":
        target = seam_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                semantic_touch
                or f"push one boundary / first-crack check on {target}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"boundary check changed or sharpened {target}",
        })
    if primitive == "赋值":
        target = object_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                semantic_operation(
                    f"probe one controlled 赋值 / special value on {target}"
                )
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"赋值 probe separated the current carrier on {target}",
        })
    if primitive == "对称":
        target = object_target
        return owned({
            "kind": "check",
            "target": target,
            "operation": (
                semantic_touch
                or f"test one 对称 / balance normalization on {target}"
                + (f" using {tie_break_check}" if tie_break_check else "")
            ),
            "success_signal": f"对称 normalization changed the live burden on {target}",
        })

    return None


def classify_program_progress_priority(
    program: dict,
    *,
    asked_medium: str,
) -> tuple[int, int]:
    kind = nonempty_text(program.get("kind"))
    target = nonempty_text(program.get("target"))

    if kind in {"check", "见证"}:
        return (0, 0)
    if kind == "write" and target and target != asked_medium:
        return (1, 0)
    if kind in {"读出"}:
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
    owner = canonicalize_skill_token(program.get("owner_skill_if_any"))
    exact_like_operation = operation in {
        "materialize_exact_asked_medium_读出",
        "materialize_exact_answer_读出",
    } or any(
        token in operation.lower()
        for token in ["materialize", "exact 读出", "final answer", "asked medium"]
    )
    closure_owner_ok = owner in {
        "",
        "精确封口",
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
    }
    if asked_medium and target == asked_medium and kind in {"write", "读出"} and exact_like_operation and closure_owner_ok:
        return True
    if operation == "materialize_exact_asked_medium_读出":
        return True
    return False


def is_generic_runtime_operation(program: dict | None) -> bool:
    if not isinstance(program, dict):
        return False
    operation = " ".join(nonempty_text(program.get("operation")).split())
    if not operation:
        return False

    templates = {
        "same_carrier_local_change_or_check",
        "materialize_exact_asked_medium_读出",
    }
    for primitive in ALLOWED_PRIMITIVES:
        semantics = get_primitive_semantics(primitive)
        touch = " ".join(nonempty_text(semantics.get("cheapest_honest_touch")).split())
        if touch:
            templates.add(touch)

    if operation in templates:
        return True
    return (
        operation.startswith("touch ")
        and " with one " in operation
        and " move that directly pressures " in operation
    )


def is_meta_narration_text(value: object) -> bool:
    text = nonempty_text(value)
    if not text:
        return False
    lowered = " ".join(text.lower().split())
    strong_markers = (
        "need a thinner carrier",
        "supports exact minimization",
        "ordinary continuation regrows",
        "rewrite the live burden",
        "continue only on",
        "current layer onto",
        "deformed recursion is awkward",
        "without turning the bootstrap itself into route guidance",
        "without adding route hints",
        "problem-specific solve staging",
        "local, honest, and non-scripted",
        "thinner controller-bearing carrier",
        "bind one concrete local touch on the current carrier",
        "do not close early",
        "stay on the thinner carrier",
        "run directory",
        "isolated directory",
        "runtime transition",
        "contract surface",
        "inspect-only",
        "package history",
        "runtime-owned verification bite",
    )
    if any(marker in lowered for marker in strong_markers):
        return True
    if (
        ("need " in lowered or "needs " in lowered or "awkward" in lowered)
        and any(token in lowered for token in ("carrier", "criterion", "minimization"))
    ):
        return True
    return False


def choose_problem_facing_runtime_target(*candidates: object) -> str:
    fallback = ""
    for candidate in candidates:
        text = nonempty_text(candidate)
        if not text:
            continue
        if not fallback:
            fallback = text
        if not is_meta_narration_text(text):
            return text
    return fallback


def is_generic_runtime_shell_text(value: object) -> bool:
    text = nonempty_text(value)
    if not text:
        return False
    lowered = " ".join(text.lower().split())
    strong_markers = (
        "problem summary",
        "fresh blind package run",
        "run in isolated directory",
        "current contract surface",
        "runtime-owned verification bite",
        "without reading forbidden package history",
        "runtime_state.json",
        "runtime_state.events.jsonl",
    )
    if any(marker in lowered for marker in strong_markers):
        return True
    if "runtime transition" in lowered and any(
        marker in lowered
        for marker in (
            "run directory",
            "contract surface",
            "runtime-owned",
            "forbidden package history",
        )
    ):
        return True
    return False


def is_genuine_problem_facing_runtime_text(value: object) -> bool:
    text = nonempty_text(value)
    return bool(text) and not is_meta_narration_text(text) and not is_generic_runtime_shell_text(text)


def choose_genuine_problem_facing_runtime_target(*candidates: object) -> str:
    target = choose_problem_facing_runtime_target(*candidates)
    if is_genuine_problem_facing_runtime_text(target):
        return target
    return ""


def program_has_meta_narration(program: dict | None) -> bool:
    if not isinstance(program, dict):
        return False
    target = program.get("target")
    if is_meta_narration_text(target) and not is_generic_runtime_shell_text(target):
        return True
    operation = nonempty_text(program.get("operation"))
    lowered_operation = " ".join(operation.lower().split())
    operation_markers = (
        "need a thinner carrier",
        "supports exact minimization",
        "ordinary continuation regrows",
        "rewrite the live burden",
        "continue only on",
        "current layer onto",
        "without turning the bootstrap itself into route guidance",
        "without adding route hints",
        "problem-specific solve staging",
        "local, honest, and non-scripted",
        "thinner controller-bearing carrier",
    )
    return any(marker in lowered_operation for marker in operation_markers)


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

    读出_bite = closure_nucleus.get("current_读出_bite_if_any")
    if not program_is_direct_closure_like(读出_bite, asked_medium=asked_medium):
        return False

    return True


def closure_can_take_first_shot(
    *,
    closure_nucleus: object,
    direct_closure_allowed: bool,
    asked_medium: str,
) -> bool:
    if not isinstance(closure_nucleus, dict):
        return False
    if closure_nucleus.get("closure_gate_active") is not True:
        return False
    if direct_closure_allowed is not True:
        return False
    if closure_nucleus.get("读出_deferred_by_layerwise_pressure") is True:
        return False
    if closure_nucleus.get("same_carrier_only") is not True:
        return False
    if nonempty_text(closure_nucleus.get("owner")) == "reselection":
        return False
    structural_bite = closure_nucleus.get("current_structural_bite_if_any")
    if isinstance(structural_bite, dict) and not program_is_direct_closure_like(
        structural_bite,
        asked_medium=asked_medium,
    ):
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
            "evidence_basis": primitive_field.get("evidence_basis") or "state_见证",
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
    # unresolved move is already a write/读出, the host should not silently
    # collapse rivalry into ordinary continuation.
    if best_priority == next_priority or best_priority != (0, 0):
        return None
    return best_program


def derive_control_bridge(
    state: dict,
    problems: list[str],
    bound_program_override: dict | None = None,
    bound_program_origin_override: str | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None

    bound_program = bound_program_override or state.get("bound_program")
    if not isinstance(bound_program, dict):
        return None

    def short_circuit_first_asked_medium_读出(program: dict | None) -> bool:
        if not isinstance(program, dict):
            return False
        bootstrap_context = state.get("bootstrap_context")
        if not isinstance(bootstrap_context, dict):
            return False
        if nonempty_text(bootstrap_context.get("mode")) != "fresh_blind_project_skills_on":
            return False
        if isinstance(state.get("bound_program"), dict):
            return False
        if isinstance(state.get("carrier_handoff_if_any"), dict):
            return False
        if isinstance(state.get("layer_composition_if_any"), dict):
            return False
        asked_medium = nonempty_text(state.get("asked_medium_surface"))
        target = nonempty_text(program.get("target"))
        owner = canonicalize_skill_token(program.get("owner_skill_if_any"))
        if not asked_medium or target != asked_medium:
            return False
        return owner in READOUT_LIKE_PRIMITIVES

    suppress_first_读出_candidate = (
        bound_program_override is not None
        and short_circuit_first_asked_medium_读出(bound_program_override)
    )

    def project_program_shape(payload: dict | None) -> dict | None:
        if not isinstance(payload, dict):
            return None
        kind = nonempty_text(payload.get("kind"))
        target = nonempty_text(payload.get("target"))
        operation = nonempty_text(payload.get("operation"))
        if not kind or not target or not operation:
            return None
        projected = {
            "kind": kind,
            "target": target,
            "operation": operation,
        }
        success_signal = nonempty_text(payload.get("success_signal"))
        if success_signal:
            projected["success_signal"] = success_signal
        owner_skill = canonicalize_skill_token(payload.get("owner_skill_if_any"))
        if owner_skill:
            projected["owner_skill_if_any"] = owner_skill
        owner_combo = extract_explicit_skill_combo(payload)
        if owner_combo:
            projected["owner_skill_combo_if_any"] = owner_combo[:6]
        origin = nonempty_text(bound_program_origin_override)
        if origin:
            projected["origin"] = origin
        return projected

    program_origin = nonempty_text(bound_program_origin_override) or (
        "derived" if bound_program_override is not None else "explicit"
    )
    bridge = {
        "current_object": state.get("current_object", ""),
        "current_debt": state.get("current_debt", ""),
        "asked_medium_surface": state.get("asked_medium_surface", ""),
        "revocation_handle": state.get("revocation_handle", ""),
        "primary_slot": state.get("primary_slot", ""),
        "program_origin": program_origin,
    }
    projected_program = project_program_shape(bound_program)
    if not isinstance(projected_program, dict):
        return bridge

    explicit_live_program = bound_program_override is None
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    explicit_non_closure_program = explicit_live_program and not program_is_direct_closure_like(
        bound_program,
        asked_medium=asked_medium,
    )

    if explicit_non_closure_program:
        bridge["execution_required"] = True
        bridge["required_action"] = "execute_local"
        bridge["authorized_bite"] = projected_program
    elif not suppress_first_读出_candidate:
        bridge["next_touch"] = projected_program

    if bound_program_override is not None and "next_touch" in bridge:
        bridge["candidate_next_touch"] = bridge.pop("next_touch")
        bridge["candidate_authorized_bite"] = projected_program
    elif suppress_first_读出_candidate:
        bridge["suppressed_candidate_reason"] = (
            "fresh_blind_first_asked_medium_读出_stays_non_authoritative_until_one_object_side_layer_takes_control"
        )
    elif explicit_live_program and "next_touch" in bridge:
        bridge["default_local_action"] = "next_touch"

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
    读出_bite = None
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
        owner_skill = canonicalize_skill_token(bound_program.get("owner_skill_if_any"))
        if owner_skill:
            touch["owner_skill_if_any"] = owner_skill
        raw_combo = bound_program.get("owner_skill_combo_if_any")
        if isinstance(raw_combo, list):
            owner_combo: list[str] = []
            for value in raw_combo:
                canonical = canonicalize_skill_token(value)
                if canonical and canonical not in owner_combo:
                    owner_combo.append(canonical)
            if owner_combo:
                touch["owner_skill_combo_if_any"] = owner_combo[:6]
        if kind == "读出" or operation == "materialize_exact_asked_medium_读出":
            读出_bite = touch
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
            focus == "asked_medium" and not 读出_bite
        ):
            structural_bite = {
                "kind": preferred_kind or "check",
                "target": target,
                "operation": "same_carrier_local_change_or_check",
                "success_signal": "object_changes_or_one_live_rival_dies_or_local_debt_shrinks",
                "origin": "agenda",
            }

    if 读出_bite is None and asked_medium:
        compiled_读出 = derive_object_compiled_读出_candidate(
            state,
            asked_medium=asked_medium,
            current_object=current_object,
            current_debt=current_debt,
            current_seam=current_seam,
            next_bite=next_bite,
            structural_bite=structural_bite if isinstance(structural_bite, dict) else None,
        )
        if isinstance(compiled_读出, dict):
            读出_bite = compiled_读出
        else:
            读出_bite = {
                "kind": "读出",
                "target": asked_medium,
                "operation": "materialize_exact_asked_medium_读出",
                "success_signal": "asked_medium_is_exact_and_executable",
                "origin": "asked_medium_closure",
                "owner_skill_if_any": "精确封口",
                "owner_skill_combo_if_any": ["精确封口"],
            }

    if structural_bite is None and isinstance(primitive_field, dict):
        derived_program = derive_primitive_program_candidate(
            state,
            problems,
            primitive_field_override=primitive_field,
        )
        if isinstance(derived_program, dict):
            if (
                nonempty_text(state.get("asked_medium_surface"))
                and nonempty_text(derived_program.get("target")) == nonempty_text(state.get("asked_medium_surface"))
                and canonicalize_skill_token(derived_program.get("owner_skill_if_any")) in READOUT_LIKE_PRIMITIVES
                and isinstance(state.get("bootstrap_context"), dict)
                and nonempty_text(state.get("bootstrap_context", {}).get("mode")) == "fresh_blind_project_skills_on"
                and not isinstance(state.get("bound_program"), dict)
                and not isinstance(state.get("carrier_handoff_if_any"), dict)
                and not isinstance(state.get("layer_composition_if_any"), dict)
            ):
                derived_program = None
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
        "current_读出_bite_if_any": 读出_bite or {},
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
                "current_读出_bite_if_any": 读出_bite or {},
            },
            control_signals=control_signals,
            asked_medium=asked_medium,
        ):
            nucleus["读出_deferred_by_layerwise_pressure"] = True
        if isinstance(micro_surface, dict):
            closure_pull = micro_surface.get("closure_pull", {})
            监督_pulse = micro_surface.get("监督_pulse", {})
            if isinstance(closure_pull, dict):
                nucleus["closure_target"] = nonempty_text(closure_pull.get("target")) or closure_target
                nucleus["required_contact"] = nonempty_text(closure_pull.get("required_contact"))
                nucleus["blocks_release"] = closure_pull.get("blocks_release") is True
            if isinstance(监督_pulse, dict):
                nucleus["监督_owner"] = nonempty_text(监督_pulse.get("owner"))
                nucleus["监督_until"] = nonempty_text(监督_pulse.get("until"))
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
            见证_hints=bool(
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
    cheap_check = ""

    bound_program = state.get("bound_program")
    gate_binding = state.get("gate_binding_if_any")
    primitive_field = state.get("primitive_field_if_any")
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    fresh_blind_first_touch_pending = fresh_blind_problem_first_touch_pending(
        state,
        asked_medium=asked_medium,
    )

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
            preferred_kinds = [nonempty_text(bound_program.get("kind")) or "write", "读出"]
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
        preferred_kinds = ["check", "见证"]
    elif output_status.get("touched") is not True or output_status.get("cosmetic_only") is True:
        if fresh_blind_first_touch_pending:
            focus, touch_target, preferred_kinds, reason = _fresh_blind_problem_facing_target(state)
        else:
            focus = "asked_medium"
            reason = "the asked medium still has not been touched honestly enough"
            touch_target = state.get("asked_medium_surface", "")
            preferred_kinds = ["write", "读出"]
    elif state.get("uncertainty_mode") in {"high", "mixed"}:
        focus = "seam"
        reason = "uncertainty is still live, so the cheapest seam-local separation should stay foregrounded"
        touch_target = current_seam
        preferred_kinds = ["check", "见证"]

    control_signals = derive_control_signals(state, problems)
    if isinstance(control_signals, dict):
        controller_view = control_signals.get("current_controller_view", {})
        operator_bias = control_signals.get("operator_bias", {})
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        probe_secondary = skill_first_probe_secondary(control_signals, focus=focus)
        favored_primitives = operator_bias.get("favored_primitives", [])
        cheap_check = nonempty_text(operator_bias.get("cheapest_reality_check"))
        外壳怀疑 = controller_view.get("外壳怀疑") is True
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
            preferred_kinds = ["check", "读出"]
        elif middle_object_risk and not direct_closure_blocked and not fresh_blind_first_touch_pending:
            focus = "asked_medium"
            reason = nonempty_text(controller_view.get("why_now")) or reason
            touch_target = state.get("asked_medium_surface", "") or touch_target
            preferred_kinds = ["write", "读出"]
        elif 外壳怀疑 and current_seam:
            focus = "seam"
            reason = nonempty_text(controller_view.get("why_now")) or reason
            touch_target = current_seam
            preferred_kinds = ["check", "见证"]
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
                    "不算而比",
                    "边界找路",
                    "局部缝控制整体",
                    "见证",
                    "特殊值探针",
                ]
            ):
                mapped_kinds.append("check")
            if any(
                primitive in favored_primitives
                for primitive in [
                    "定义即直接读出",
                    "主导机制读出",
                    "读出",
                    "投影读出",
                ]
            ):
                mapped_kinds.append("读出")
            if direct_closure_blocked:
                mapped_kinds = [kind for kind in mapped_kinds if kind != "读出"]
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

    if fresh_blind_first_touch_pending and touch_target == asked_medium:
        focus, touch_target, preferred_kinds, reason = _fresh_blind_problem_facing_target(state)

    allowed_check_methods = derive_check_methods(
        focus=focus,
        has_structural_lead=bool(
            preferred_kinds and preferred_kinds[0] in {"write", "check", "读出"}
        ),
        has_tie_break_check=bool(cheap_check),
        asked_medium_live=bool(nonempty_text(state.get("asked_medium_surface"))),
    )
    return {
        "focus": focus,
        "reason": reason,
        "touch_target": touch_target,
        "preferred_kinds": preferred_kinds,
        "check_skill_active": True,
        "allowed_check_methods": allowed_check_methods,
        "small_scale_enumeration_role": (
            "optional_post_compression_verifier"
            if "small_scale_enumeration_after_compression_only" in allowed_check_methods
            else "not_primary"
        ),
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


def fresh_blind_problem_first_touch_pending(
    state: dict,
    *,
    asked_medium: str = "",
) -> bool:
    if not isinstance(state, dict):
        return False
    bootstrap_context = state.get("bootstrap_context")
    if not isinstance(bootstrap_context, dict):
        return False
    if nonempty_text(bootstrap_context.get("mode")) != "fresh_blind_project_skills_on":
        return False
    if isinstance(state.get("bound_program"), dict):
        return False
    if isinstance(state.get("carrier_handoff_if_any"), dict):
        return False
    if isinstance(state.get("layer_composition_if_any"), dict):
        return False
    if isinstance(state.get("landed_next_touch_if_any"), dict):
        return False
    if isinstance(state.get("materialization_evidence"), dict):
        return False
    asked_medium = asked_medium or nonempty_text(state.get("asked_medium_surface"))
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))
    next_bite = nonempty_text(state.get("next_bite"))
    if not asked_medium or not current_object:
        return False
    if current_debt and current_debt != asked_medium:
        return True
    if next_bite and next_bite != asked_medium:
        return True
    return False


def fresh_blind_frontload_problems(
    state: dict,
    problems: list[str],
) -> list[str]:
    if not isinstance(problems, list):
        return []
    if not fresh_blind_problem_first_touch_pending(state):
        return list(problems)
    frontload_candidates = [
        nonempty_text(state.get("current_seam")),
        nonempty_text(state.get("current_object")),
        nonempty_text(state.get("current_debt")),
        nonempty_text(state.get("next_bite")),
    ]
    problem_facing_candidates = [
        candidate
        for candidate in frontload_candidates
        if candidate and not is_meta_narration_text(candidate)
    ]
    if not problem_facing_candidates:
        return list(problems)
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    frontload_target = choose_problem_facing_runtime_target(
        *problem_facing_candidates,
        asked_medium,
    )
    if (
        not frontload_target
        or frontload_target == asked_medium
        or is_meta_narration_text(frontload_target)
    ):
        return list(problems)
    deferred = {
        "bound_program is required while release_veto is active",
    }
    return [problem for problem in problems if problem not in deferred]


def _fresh_blind_problem_facing_target(state: dict) -> tuple[str, str, list[str], str]:
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    current_seam = nonempty_text(state.get("current_seam"))
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))
    next_bite = nonempty_text(state.get("next_bite"))
    target = choose_problem_facing_runtime_target(
        current_seam,
        current_debt,
        next_bite,
        current_object,
        asked_medium,
    )
    focus = "carrier"
    if target and target == current_seam and not is_meta_narration_text(current_seam):
        focus = "seam"
    elif target and target == current_debt and not is_meta_narration_text(current_debt):
        focus = "debt"
    elif target and target == asked_medium:
        fallback_target = current_seam or current_object or current_debt or next_bite
        if fallback_target:
            target = fallback_target
            if fallback_target == current_seam:
                focus = "seam"
            elif fallback_target == current_debt:
                focus = "debt"
    preferred_kinds = ["write", "check"] if focus == "carrier" else ["check", "write"]
    reason = (
        choose_problem_facing_runtime_target(
            current_debt,
            next_bite,
            current_seam,
            current_object,
        )
        or "the first fresh-blind touch must stay on the problem-facing layer before asked-medium closure"
    )
    return focus, target, preferred_kinds, reason


def build_problem_born_touch_for_skill(
    state: dict,
    skill: str,
    *,
    target: str,
    supporting: list[str] | None = None,
) -> dict | None:
    canonical = canonicalize_skill_token(skill)
    target = nonempty_text(target)
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))
    current_seam = nonempty_text(state.get("current_seam"))
    next_bite = nonempty_text(state.get("next_bite"))
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    if not canonical or not target:
        return None
    if canonical in CONTROL_META_SKILLS:
        return None
    if canonical in {
        "图像",
        "赋值",
        "投影",
        "重编码",
        "状态拆分",
        "规范归一化",
        "容器到截面",
        "格点选排",
        "匹配替代概率",
        "点积投影",
        "面积到线读出",
        "局部缝控制整体",
    }:
        kind = "write"
    elif canonical in {
        "见证",
        "极限边界",
        "边界找路",
        "特殊值探针",
        "相容",
        "不算而比",
        "函数原型匹配",
        "反证",
        "对称",
        "对称消元",
    }:
        kind = "check"
    else:
        kind = "check"

    fresh_first_touch = fresh_blind_problem_first_touch_pending(state)
    if fresh_first_touch and kind == "write":
        target = (
            choose_genuine_problem_facing_runtime_target(
                current_seam,
                current_debt,
                target,
                current_object,
                asked_medium,
            )
            or choose_problem_facing_runtime_target(
                current_seam,
                current_debt,
                target,
                current_object,
                asked_medium,
            )
        )
    else:
        target = choose_problem_facing_runtime_target(
            target,
            current_seam,
            current_debt,
            current_object,
            asked_medium,
        )
    source_object = choose_problem_facing_runtime_target(
        current_debt,
        current_seam,
        current_object,
        target,
    )
    if fresh_first_touch and kind == "write":
        controlled_object = (
            choose_genuine_problem_facing_runtime_target(
                target,
                current_seam,
                current_debt,
                current_object,
            )
            or choose_problem_facing_runtime_target(
                target,
                current_seam,
                current_debt,
                current_object,
            )
        )
    else:
        controlled_object = choose_problem_facing_runtime_target(
            target,
            current_seam,
            current_debt,
            current_object,
        )
    if (
        fresh_first_touch
        and kind == "write"
        and source_object
        and controlled_object == source_object
    ):
        alternate_controlled_object = ""
        for candidate in [current_debt, current_seam, target, current_object]:
            candidate_text = choose_genuine_problem_facing_runtime_target(candidate)
            if candidate_text and candidate_text != source_object:
                alternate_controlled_object = candidate_text
                break
        controlled_object = alternate_controlled_object or source_object
    next_object = (
        choose_problem_facing_runtime_target(current_debt, controlled_object, source_object)
        if current_debt and current_debt not in {source_object, controlled_object}
        else controlled_object
    )
    skill_phase = "structural_rewrite" if kind == "write" else "separating_check"
    lane_text = normalize_primitive_token(
        " ".join(
            value
            for value in [current_object, current_seam, current_debt, next_bite, target]
            if value
        )
    )
    balance_state_graph_lane = (
        any(
            token in lane_text
            for token in [
                "balanced",
                "balance",
                "parentheses",
                "parenthesis",
                "prefix",
                "suffix",
                "concatenation",
                "class-+1",
                "bracket",
                "括号",
                "平衡",
                "前缀",
                "后缀",
                "拼接",
            ]
        )
        and any(
            token in lane_text
            for token in [
                "string",
                "strings",
                "state",
                "lane",
                "edit",
                "minimize",
                "criterion",
                "状态",
                "车道",
                "最小",
                "判定",
            ]
        )
    )
    symmetry_comparison_lane = any(
        token in lane_text
        for token in [
            "same-height",
            "equal-height",
            "mirror",
            "symmetric",
            "symmetry",
            "two sides",
            "left/right",
            "same cost",
            "breakpoint",
            "double-root",
            "two-root",
            "equal-value",
            "equal level",
            "等高",
            "两侧",
            "对称",
            "镜像",
            "前缀",
            "后缀",
            "断点",
            "双根",
            "同一笔账",
            "同值",
        ]
    )
    parameter_anchor_lane = any(
        token in lane_text
        for token in [
            "parameter",
            "anchor",
            "special value",
            "representative",
            "peak",
            "threshold",
            "height",
            "参数",
            "锚",
            "特殊值",
            "代表值",
            "峰值",
            "阈值",
            "高度",
        ]
    )
    function_graph_lane = any(
        token in lane_text
        for token in [
            "f(",
            "function",
            "graph",
            "curve",
            "intersection",
            "root",
            "zero",
            "单调",
            "函数",
            "图像",
            "曲线",
            "交点",
            "零点",
        ]
    )
    hostile_falsifier_lane = problem_wants_hostile_falsifier(
        current_object,
        current_seam,
        current_debt,
        next_bite,
        target,
    )

    operations = {
        "图像": (
            f"draw one minimal problem diagram for {source_object} on {target}, mark the decisive turning / ordering feature there, and rewrite the governing relation onto {controlled_object}"
        ),
        "赋值": (
            f"place one representative anchor on {target}, rewrite the decisive local relation around that anchor, and see whether it already settles {current_debt or current_object or target}"
        ),
        "投影": (
            f"project {source_object} onto the decisive coordinate / height / ledger at {target}, keep only that controlling data, and move the layer onto {controlled_object}"
        ),
        "极限边界": (
            f"push {target} to one honest boundary or saturation case and check whether {current_debt or current_object or target} is already decided there"
        ),
        "边界找路": (
            f"use one boundary 见证 on {target} to choose the route before full derivation regrows around {current_debt or current_object or target}"
        ),
        "特殊值探针": (
            f"probe one lawful special value on {target} and check whether it pins the live parameter debt {current_debt or current_object or target}"
        ),
        "见证": (
            f"land one separating 见证 on {target} and check whether it kills the wrong route for {current_debt or current_object or target}"
        ),
        "状态拆分": (
            f"split {source_object} into the minimum honest states on {target}, keep that state summary explicit, and continue on {controlled_object}"
        ),
        "相容": (
            f"check whether the local constraints on {target} are jointly compatible before any bulk enumeration of {current_debt or current_object or target}"
        ),
        "函数原型匹配": (
            f"match {target} to one function archetype and keep only the graph behavior that controls {current_debt or current_object or target}"
        ),
        "不算而比": (
            f"compare the decisive quantities on {target} without full calculation and check whether that already settles {current_debt or current_object or target}"
        ),
        "规范归一化": (
            f"rewrite {source_object} into one canonical form centered on {target}, then keep only the normalized object {controlled_object}"
        ),
        "对称": (
            f"put {source_object} onto one 对称-controlled comparison axis at {target} and check whether the remaining burden already reduces to {controlled_object}"
        ),
        "对称消元": (
            f"use 对称 on {target} to kill fake degrees of freedom in {source_object} and expose the smaller object {controlled_object}"
        ),
    }
    if canonical == "图像" and balance_state_graph_lane and not hostile_falsifier_lane:
        operation = (
            f"draw the live balance object as a two-lane state graph on {target}, keep only the local "
            f"state ledger, and rewrite the burden as one direct prefix/suffix balance criterion on {controlled_object}"
        )
        success_signal = (
            f"the two-lane state graph exposed the exact balance criterion on {target} and killed ordinary prefix-repair drift"
        )
        skill_phase = "state_graph_rewrite"
    elif canonical == "图像" and function_graph_lane:
        operation = (
            f"treat {source_object} as one intersection / graph-skeleton problem on {target}, keep only the anchors and turning feature "
            f"that control the root count, and rewrite the layer onto {controlled_object}"
        )
        success_signal = (
            f"the graph skeleton on {target} made the decisive root-count controller explicit"
        )
    elif canonical == "赋值" and parameter_anchor_lane:
        operation = (
            f"pin {target} to the decisive anchor values first, compare the live parameter directly against those anchors, "
            f"and let the surviving range decide {current_debt or current_object or target}"
        )
        success_signal = (
            f"anchor-value comparison on {target} settled or sharply narrowed the live parameter layer"
        )
    elif canonical == "对称" and symmetry_comparison_lane:
        operation = (
            f"put the mirrored / equal-height points on one symmetry axis at {target}, compare the two sides directly, "
            f"and let that force the surviving inequality for {current_debt or current_object or target}"
        )
        success_signal = (
            f"the symmetry comparison on {target} forced the decisive inequality without reopening thick derivation"
        )
    else:
        operation = operations.get(
            canonical,
            f"touch {target} with one {canonical} move that directly pressures {current_debt or current_object or current_seam or target}",
        )
        success_signal = (
            f"{canonical} on {target} changed, narrowed, or killed the current layer around {current_debt or current_object or target}"
        )
    combo = [canonical]
    for value in supporting or []:
        normalized = canonicalize_skill_token(value)
        if normalized and normalized not in combo:
            combo.append(normalized)
    return {
        "kind": kind,
        "target": target,
        "operation": operation,
        "success_signal": success_signal,
        "current_layer_object_if_any": source_object,
        "controlled_object_if_any": controlled_object,
        "object_transform_if_any": f"{canonical} rewrites `{source_object}` toward `{controlled_object}`",
        "next_object_if_any": next_object,
        "step_outline_if_any": f"use `{canonical}` on `{target}` to move from `{source_object}` to `{controlled_object}`, then continue on `{next_object}`",
        "skill_phase_if_any": skill_phase,
        "owner_skill_if_any": canonical,
        "owner_skill_combo_if_any": combo[:6],
    }


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
    外壳怀疑 = controller_view.get("外壳怀疑") is True
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
        or 外壳怀疑
        or middle_object_risk
        or (carrier_status != "thin_enough" and weak_evidence)
    )
    level = (
        "high"
        if reselection_needed or (外壳怀疑 and middle_object_risk) or weak_evidence
        else "medium"
        if active
        else "quiet"
    )

    wake_primitives: list[str] = []
    wake_skills: list[str] = []
    if 外壳怀疑:
        wake_primitives.extend(["见证", "投影"])
        wake_skills.extend(["抓本质", "反问"])
    if middle_object_risk:
        wake_primitives.extend(["状态拆分", "读出"])
        wake_skills.extend(["抓本质", "最终控制者"])
    if reselection_needed:
        wake_primitives.extend(["状态拆分", "投影", "见证"])
        wake_skills.extend(["更薄载体重选", "反问"])
    if weak_evidence:
        wake_primitives.extend(["见证", "特殊值探针"])
        wake_skills.extend(["元认知", "反问"])

    semantic_wake = derive_semantic_coactivation_hints(wake_primitives)
    for skill in semantic_wake:
        if skill in ALLOWED_SKILLS and skill not in wake_primitives:
            wake_primitives.append(skill)

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
        "reselect_on_next_layer": reselection_needed or 外壳怀疑 or middle_object_risk,
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

    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    primitive_takeover_gate = state.get("primitive_takeover_gate_if_any")
    same_carrier_takeover_active = (
        isinstance(primitive_takeover_gate, dict)
        and nonempty_text(primitive_takeover_gate.get("trigger")) == "same_carrier_landing"
    )
    fresh_blind_pending_first_touch = fresh_blind_problem_first_touch_pending(
        state,
        asked_medium=asked_medium,
    )

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
        owner_skill = canonicalize_skill_token(payload.get("owner_skill_if_any"))
        if owner_skill:
            program["owner_skill_if_any"] = owner_skill
        raw_combo = payload.get("owner_skill_combo_if_any")
        if isinstance(raw_combo, list):
            owner_combo = []
            for value in raw_combo:
                canonical = canonicalize_skill_token(value)
                if canonical and canonical not in owner_combo:
                    owner_combo.append(canonical)
            if owner_combo:
                program["owner_skill_combo_if_any"] = owner_combo[:6]
        return attach_program_metadata_fields(program, payload)

    def programs_conflict(left: dict | None, right: dict | None) -> bool:
        if not isinstance(left, dict) or not isinstance(right, dict):
            return False
        left_signature = (
            nonempty_text(left.get("kind")),
            nonempty_text(left.get("target")),
            nonempty_text(left.get("operation")),
        )
        right_signature = (
            nonempty_text(right.get("kind")),
            nonempty_text(right.get("target")),
            nonempty_text(right.get("operation")),
        )
        return bool(all(left_signature) and all(right_signature) and left_signature != right_signature)

    primitive_program = derive_primitive_program_candidate(state, problems)
    if not isinstance(primitive_program, dict):
        fallback_field = derive_primitive_field_candidate(state, problems)
        if isinstance(fallback_field, dict):
            primitive_program = derive_primitive_program_candidate(
                state,
                problems,
                primitive_field_override=fallback_field,
            )

    skill_authority = derive_skill_authority_bridge(state, problems)
    if isinstance(skill_authority, dict):
        executable_touch = skill_authority.get("executable_local_touch_if_any")
        winning_skill = nonempty_text(
            skill_authority.get("executable_owner_skill_if_any")
            or skill_authority.get("winning_skill_if_any")
        )
        if isinstance(executable_touch, dict) and winning_skill:
            projected = project_bound_program_shape(executable_touch)
            if isinstance(projected, dict):
                projected_combo = extract_explicit_skill_combo(projected)
                primitive_combo = (
                    extract_explicit_skill_combo(primitive_program)
                    if isinstance(primitive_program, dict)
                    else []
                )
                if (
                    is_generic_runtime_operation(projected)
                    and isinstance(primitive_program, dict)
                    and not is_generic_runtime_operation(primitive_program)
                ):
                    return primitive_program
                if (
                    fresh_blind_pending_first_touch
                    and is_generic_runtime_operation(projected)
                ):
                    return None
                if (
                    fresh_blind_pending_first_touch
                    and isinstance(primitive_program, dict)
                    and not program_is_direct_closure_like(
                        primitive_program,
                        asked_medium=asked_medium,
                    )
                    and nonempty_text(projected.get("target")) == asked_medium
                ):
                    return primitive_program
                if (
                    same_carrier_takeover_active
                    and isinstance(primitive_program, dict)
                    and not program_is_direct_closure_like(
                        primitive_program,
                        asked_medium=asked_medium,
                    )
                    and program_is_direct_closure_like(projected, asked_medium=asked_medium)
                ):
                    return primitive_program
                if (
                    same_carrier_takeover_active
                    and isinstance(primitive_program, dict)
                    and not programs_conflict(projected, primitive_program)
                    and not is_generic_runtime_operation(primitive_program)
                ):
                    primitive_target = nonempty_text(primitive_program.get("target"))
                    projected_target = nonempty_text(projected.get("target"))
                    current_object = nonempty_text(state.get("current_object"))
                    current_seam = nonempty_text(state.get("current_seam"))
                    current_debt = nonempty_text(state.get("current_debt"))
                    current_bite = nonempty_text(state.get("next_bite"))
                    if (
                        primitive_target
                        and primitive_target in {current_object, current_seam, current_debt, current_bite}
                        and projected_target
                        and projected_target not in {current_object, current_seam, current_debt, current_bite}
                    ):
                        return primitive_program
                if (
                    same_carrier_takeover_active
                    and isinstance(primitive_program, dict)
                    and not programs_conflict(projected, primitive_program)
                    and projected_combo
                    and primitive_combo
                    and projected_combo != primitive_combo
                ):
                    return primitive_program
                return projected

    if isinstance(primitive_program, dict):
        if (
            fresh_blind_pending_first_touch
            and is_generic_runtime_operation(primitive_program)
        ):
            return None
        return primitive_program

    focus = agenda.get("focus")
    target = nonempty_text(agenda.get("touch_target"))
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))
    next_bite = nonempty_text(state.get("next_bite"))
    seam = nonempty_text(state.get("current_seam")) or next_bite

    if focus == "asked_medium" and asked_medium and not fresh_blind_pending_first_touch:
        return {
            "kind": "write",
            "target": asked_medium,
            "operation": f"materialize {next_bite or current_debt} on the asked medium",
            "success_signal": f"asked medium touched at {asked_medium}",
        }

    if focus == "rival" and target:
        return {
            "kind": "见证",
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
    skill_combo_override: list[str] | None = None,
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
        authority_until = "hostile_见证"
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
    if isinstance(skill_combo_override, list):
        owner_combo = []
        for value in skill_combo_override:
            canonical = canonicalize_skill_token(value)
            if canonical and canonical not in owner_combo:
                owner_combo.append(canonical)
        if owner_combo:
            payload["owner_skill_combo_if_any"] = owner_combo[:6]
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

    same_carrier_program = derive_bound_program_candidate(state, problems)
    if isinstance(same_carrier_program, dict):
        return None

    if not next_bite:
        return None

    if isinstance(rival, dict):
        rival_object = nonempty_text(rival.get("object"))
        rival_advantage = nonempty_text(rival.get("separating_advantage"))
        if rival_object:
            return {
                "trigger": "hostile_见证",
                "from_slot": nonempty_text(state.get("primary_slot")) or "current_slot",
                "to_object": rival_object,
                "winning_pressure": "rival-separating 见证 pressure",
                "why_local": rival_advantage
                or f"the current carrier still splits against a live rival on {rival_object}",
                "warm_field": {
                    "active_pressures": ["见证", "check"],
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
                    "active_pressures": ["状态拆分", "check"],
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
                    "active_pressures": ["读出", "check"],
                    "cheap_check": f"compress onto {current_seam} before probing it",
                    **({"primitive_hints": favored_primitives} if favored_primitives else {}),
                },
            }
        return {
            "trigger": "exact_check",
            "from_slot": nonempty_text(state.get("primary_slot")) or "current_slot",
            "to_object": current_seam,
            "winning_pressure": "exact 读出/check pressure",
            "why_local": f"uncertainty stays live on seam {current_seam}, so authority should narrow there",
            "warm_field": {
                "active_pressures": ["见证", "check"],
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
                "active_pressures": ["check", "读出"],
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
    外壳怀疑 = False
    owner_status = ""
    probe_secondary = False
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
            外壳怀疑 = controller_view.get("外壳怀疑") is True
            owner_status = nonempty_text(controller_view.get("owner_status"))
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
            "active_primitives": active_primitives[:3],
            "why_now": why_now,
            "selection_basis": selection_basis,
            "evidence_basis": "state_见证" if tie_break_check else "cheap_check",
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
        text_hints = infer_primitives_from_text(
            handoff.get("winning_pressure"),
            handoff.get("why_local"),
            handoff.get("warm_field", {}).get("active_pressures") if isinstance(handoff.get("warm_field"), dict) else None,
            state.get("next_bite"),
            state.get("current_debt"),
        )
        for primitive in merge_primitive_hints(explicit_hints, text_hints, pressure_hints, control_hints):
            if primitive not in active_primitives:
                active_primitives.append(primitive)
            if len(active_primitives) == 3:
                break
        if not active_primitives:
            conservative_hints = merge_primitive_hints(
                infer_primitives_from_text(
                    state.get("current_seam"),
                    gap_object.get("object") if isinstance(gap_object, dict) else None,
                ),
                control_hints,
                pressure_hints,
            )
            active_primitives = [
                primitive
                for primitive in conservative_hints
                if primitive not in READOUT_LIKE_PRIMITIVES
            ][:3]
        if not active_primitives:
            return None
        preserve_problem_born_order = text_hints_deserve_front_seat(text_hints)
        if preserve_problem_born_order:
            active_primitives = text_hints + [
                primitive for primitive in active_primitives if primitive not in text_hints
            ]
        active_primitives = reorder_primitives_for_skill_first(
            active_primitives,
            focus="asked_medium" if nonempty_text(state.get("asked_medium_surface")) and control_why else "",
            probe_secondary=(probe_secondary and not preserve_problem_born_order),
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
            "active_primitives": active_primitives[:3],
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
                else "state_见证"
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
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    fresh_blind_first_touch_pending = fresh_blind_problem_first_touch_pending(
        state,
        asked_medium=asked_medium,
    )
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
    active_primitives = merge_primitive_hints(text_hints, pressure_hints, control_hints, agenda_hints)
    for primitive in text_hints:
        if primitive not in active_primitives:
            active_primitives.append(primitive)
        if len(active_primitives) == 3:
            break

    if isinstance(agenda, dict):
        focus = nonempty_text(agenda.get("focus"))
        transform_live = any(
            primitive in TRANSFORM_SUPPORT_PRIMITIVES
            for primitive in active_primitives
        )
        ledger_first_live = {"投影", "守恒"}.issubset(
            set(merge_primitive_hints(active_primitives, text_hints))
        )
        route_side_live = any(
            primitive in {
                "对称",
                "极限边界",
                "边界找路",
                "特殊值探针",
                "对称消元",
                "先调模型后推导",
            }
            for primitive in merge_primitive_hints(active_primitives, text_hints)
        )
        structure_nucleus_live = any(
            primitive in STRUCTURE_NUCLEUS_PRIMITIVES
            for primitive in merge_primitive_hints(active_primitives, text_hints, control_hints)
        )
        if focus in {"seam", "rival"} and "见证" not in active_primitives:
            active_primitives = (
                ["状态拆分", "见证"] + active_primitives
                if not transform_live
                else ["见证"] + active_primitives
            )
        elif (
            focus == "asked_medium"
            and "读出" not in active_primitives
            and not fresh_blind_first_touch_pending
        ):
            if structure_nucleus_live:
                active_primitives = active_primitives
            elif route_side_live:
                active_primitives = (
                    ["投影"] + active_primitives
                    if not transform_live and "投影" not in active_primitives
                    else active_primitives
                )
            else:
                active_primitives = (
                    ["投影", "读出"] + active_primitives
                    if not transform_live
                    else ["读出"] + active_primitives
                )
        elif (
            focus == "carrier"
            and "状态拆分" not in active_primitives
            and not ledger_first_live
        ):
            active_primitives = ["状态拆分"] + active_primitives
        elif focus == "carrier" and ledger_first_live:
            active_primitives = ["投影", "守恒"] + active_primitives
            # On a ledger-first carrier, keep the foreground exact: 投影 +
            # 守恒 should bind the capacity ledger before a 见证 wakes.
            # Boundary 见证es belong to the next layer after the ledger lands.
            if (
                nonempty_text(state.get("current_object"))
                and "ledger" in nonempty_text(state.get("current_object")).lower()
                and "见证" in active_primitives[:3]
            ):
                active_primitives = [
                    primitive for primitive in active_primitives if primitive != "见证"
                ] + ["见证"]
        # When asked-medium closure is live but the carrier is still thick, keep one
        # transform/controller primitive in the foreground so the runtime does not
        # collapse straight into 读出-only behavior.
        if (
            focus == "asked_medium"
            and (外壳怀疑 or owner_status in {"narrowing", "locked"})
            and nonempty_text(state.get("current_seam"))
            and nonempty_text(state.get("current_seam")) != nonempty_text(state.get("current_object"))
            and not any(
                primitive in TRANSFORM_SUPPORT_PRIMITIVES
                for primitive in active_primitives[:3]
            )
        ):
            active_primitives = ["投影", "状态拆分"] + active_primitives
    else:
        focus = ""

    if pressure_hints:
        for pressure_primitive in reversed(pressure_hints):
            if pressure_primitive not in active_primitives:
                active_primitives = [pressure_primitive] + active_primitives

    preserve_problem_born_order = text_hints_deserve_front_seat(text_hints)
    if preserve_problem_born_order:
        active_primitives = text_hints + [
            primitive for primitive in active_primitives if primitive not in text_hints
        ]

    active_primitives = reorder_primitives_for_skill_first(
        active_primitives,
        focus=focus,
        probe_secondary=(
            (probe_secondary if 'probe_secondary' in locals() else False)
            and not preserve_problem_born_order
        ),
    )

    deduped: list[str] = []
    for primitive in active_primitives:
        if primitive in ALLOWED_PRIMITIVES and primitive not in deduped:
            deduped.append(primitive)
        if len(deduped) == 3:
            break

    if not deduped:
        return None

    tie_break_check = None
    if isinstance(agenda, dict):
        tie_break_check = nonempty_text(agenda.get("touch_target"))
        if fresh_blind_first_touch_pending and tie_break_check == asked_medium:
            tie_break_check = nonempty_text(state.get("current_seam")) or nonempty_text(
                state.get("current_object")
            )
    selection_basis = classify_selection_basis(
        [],
        [],
        merge_primitive_hints(control_hints, agenda_hints),
        text_hints,
        tie_break_check or control_check or "",
    )

    return {
        "layer_object": layer_object,
        "active_primitives": deduped[:3],
        "why_now": control_why
        or (nonempty_text(agenda.get("reason")) if isinstance(agenda, dict) else "")
        or "the current carrier is still locally live",
        "selection_basis": selection_basis,
        "evidence_basis": (
            "cheap_check"
            if (tie_break_check or control_check)
            else "state_见证"
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
            "preferred_kinds": ["check", "读出"],
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
    gate_until = "same_carrier_change_or_kill_见证_or_exact_check"
    if owner == "asked_medium":
        gate_until = "asked_medium_touch_or_kill_见证_or_exact_check"
    elif owner == "reselection":
        gate_until = "handoff_bound_or_exact_check_or_kill_见证"

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
                and nonempty_text(reward_bias.get("promote")) == "object_change_or_exact_读出"
            ):
                preferred = promoted_move.get("preferred_kinds")
                if isinstance(preferred, list):
                    ordered = ["write", "读出"] + [
                        kind for kind in preferred if kind not in {"write", "读出"}
                    ]
                    promoted_move["preferred_kinds"] = ordered[:3]
        if isinstance(micro_control_surface, dict):
            closure_pull = micro_control_surface.get("closure_pull", {})
            reward_bias = micro_control_surface.get("reward_bias", {})
            penalty_bias = micro_control_surface.get("penalty_bias", {})
            监督_pulse = micro_control_surface.get("监督_pulse", {})
            反问 = micro_control_surface.get("反问", {})
            if isinstance(closure_pull, dict) and closure_pull.get("active") is True:
                gate_until = (
                    "asked_medium_contact_or_exact_executable_closure"
                    if nonempty_text(closure_pull.get("target")) == state.get("asked_medium_surface")
                    else nonempty_text(监督_pulse.get("until"))
                    or "asked_medium_contact_or_exact_executable_closure"
                )
            if isinstance(penalty_bias, dict):
                for penalty_demote in penalty_bias.get("demote", []):
                    penalty_text = nonempty_text(penalty_demote)
                    if penalty_text and penalty_text not in demoted_continuations:
                        demoted_continuations.append(penalty_text)
            if isinstance(反问, dict) and promoted_move is not None:
                target = nonempty_text(反问.get("target"))
                preferred_kind = nonempty_text(反问.get("preferred_answer_kind"))
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
                        "exact_读出": "读出",
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
                isinstance(监督_pulse, dict)
                and nonempty_text(监督_pulse.get("owner")) == "closure"
                and promoted_move is not None
            ):
                fresh_blind_pending_first_touch = fresh_blind_problem_first_touch_pending(
                    state,
                    asked_medium=nonempty_text(state.get("asked_medium_surface")),
                )
                if fresh_blind_pending_first_touch:
                    focus, target, preferred_kinds, _ = _fresh_blind_problem_facing_target(state)
                    promoted_move["focus"] = focus
                    if target:
                        promoted_move["touch_target"] = target
                    if preferred_kinds:
                        promoted_move["preferred_kinds"] = preferred_kinds[:3]
                else:
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
    controller_trigger_override: dict | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None
    explicit_layer = state.get("layer_composition_if_any")
    if (
        isinstance(explicit_layer, dict)
        and explicit_layer.get("event_owned") is True
        and _event_owned_layer_matches_live_surface(state, explicit_layer)
        and not _same_carrier_takeover_active(state)
    ):
        authorized_bite = explicit_layer.get("authorized_bite")
        combo = extract_explicit_skill_combo(authorized_bite)
        if combo:
            controller_trigger = (
                controller_trigger_override
                if controller_trigger_override is not None
                else derive_controller_trigger_surface(
                    state,
                    primitive_field_override=state.get("primitive_field_if_any")
                    if isinstance(state.get("primitive_field_if_any"), dict)
                    else None,
                    control_signals_override=control_signals_override
                    if isinstance(control_signals_override, dict)
                    else None,
                )
            )
            leading_skill = canonicalize_skill_token(
                explicit_layer.get("leading_skill_if_any")
                or (authorized_bite.get("owner_skill_if_any") if isinstance(authorized_bite, dict) else "")
            )
            leading_skill, combo = apply_controller_trigger_to_combo(
                combo,
                leading_skill=leading_skill,
                controller_trigger=controller_trigger if isinstance(controller_trigger, dict) else None,
            )
            payload = {
                "layer_object": (
                    nonempty_text(explicit_layer.get("controlled_object"))
                    or nonempty_text(explicit_layer.get("next_local_choice"))
                    or nonempty_text(explicit_layer.get("layer_object"))
                    or nonempty_text(state.get("current_object"))
                    or nonempty_text(state.get("current_debt"))
                ),
                "active_skills": combo[:8],
                "why_now": (
                    nonempty_text(explicit_layer.get("reason"))
                    or "the current layer already carries one explicit event-owned skill combination"
                ),
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
                "full_active_skills": combo[:8],
                "composition_ready": len(combo) >= 2,
                "composition_reason": "the current layer already carries one explicit event-owned skill combination",
            }
            if leading_skill:
                payload["authority_skill_if_any"] = leading_skill
            if isinstance(state.get("bound_program"), dict):
                if leading_skill:
                    payload["bound_skill_if_any"] = leading_skill
            if nonempty_text(state.get("asked_medium_surface")):
                payload["closure_authority_skill_if_any"] = "精确封口"
            return payload
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
    background_skills: list[str] = []
    primitive_field_selection_basis = ""
    primitive_field_evidence_basis = ""
    if isinstance(primitive_field, dict):
        primitive_field_selection_basis = nonempty_text(primitive_field.get("selection_basis"))
        primitive_field_evidence_basis = nonempty_text(primitive_field.get("evidence_basis"))
        active_primitives = [
            canonicalize_primitive_token(value)
            for value in primitive_field.get("active_primitives", [])
            if canonicalize_primitive_token(value)
        ]
        weak_primitive_field = primitive_field_evidence_basis in {
            "lexical_hint",
            "text_fallback",
        }
        semantic_skills = [] if weak_primitive_field else derive_semantic_coactivation_hints(active_primitives)
        active_primitive_set = set(active_primitives)
        semantic_skill_set = set(semantic_skills)
        for primitive in primitive_field.get("active_primitives", []):
            canonical = canonicalize_skill_token(primitive)
            if not canonical or canonical in active_skills:
                continue
            if primitive_claim_requires_partner(canonical):
                has_partner = bool((active_primitive_set | semantic_skill_set) - {canonical})
                strong_evidence = primitive_field_evidence_basis not in {
                    "lexical_hint",
                    "text_fallback",
                }
                if not has_partner or not strong_evidence:
                    continue
                active_skills.append(canonical)
            else:
                active_skills.append(canonical)
        for skill in semantic_skills:
            if skill not in active_skills:
                active_skills.append(skill)

    if isinstance(control_signals, dict):
        controller_view = control_signals.get("current_controller_view", {})
        meta_controls = control_signals.get("meta_controls", {})
        incentive_field = control_signals.get("incentive_field", {})
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        if isinstance(controller_view, dict):
            if controller_view.get("外壳怀疑") is True and "外壳怀疑" not in background_skills:
                background_skills.append("外壳怀疑")
            if nonempty_text(controller_view.get("owner_status")) in {"narrowing", "locked"} and "最终控制者" not in background_skills:
                background_skills.append("最终控制者")
            if nonempty_text(controller_view.get("essence_status")) in {"controller_emerging", "controller_visible"} and "抓本质" not in background_skills:
                background_skills.append("抓本质")
            if controller_view.get("reselection_needed") is True and "更薄载体重选" not in background_skills:
                background_skills.append("更薄载体重选")
        if isinstance(meta_controls, dict):
            if meta_controls.get("反问", {}).get("active") is True and "反问" not in background_skills:
                background_skills.append("反问")
            if meta_controls.get("closure_gate", {}).get("active") is True and "精确封口" not in background_skills:
                background_skills.append("精确封口")
            if meta_controls.get("supervisory_pulse", {}).get("active") is True and "监督" not in background_skills:
                background_skills.append("监督")
            if meta_controls.get("元认知", {}).get("active") is True and "元认知" not in background_skills:
                background_skills.append("元认知")
            中枢控制 = meta_controls.get("中枢控制", {})
            if (
                isinstance(中枢控制, dict)
                and nonempty_text(中枢控制.get("mode"))
                and nonempty_text(中枢控制.get("mode")) != "monitoring"
            ):
                background_skills.append("中枢控制")
            if meta_controls.get("后脑守卫", {}).get("active") is True and "后脑守卫" not in background_skills:
                background_skills.append("后脑守卫")
        if isinstance(incentive_field, dict) and "奖惩塑形" not in background_skills:
            background_skills.append("奖惩塑形")
        if isinstance(layerwise_pressure, dict) and layerwise_pressure.get("active") is True:
            for skill in layerwise_pressure.get("wake_skills", []):
                if skill in ALLOWED_SKILLS and skill not in active_skills and skill not in {
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
                }:
                    active_skills.append(skill)

    frontload = derive_problem_skill_frontload(
        state,
        primitive_field=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals=control_signals if isinstance(control_signals, dict) else None,
    )
    frontloaded_skills = (
        _normalize_skill_combo(frontload.get("candidate_skills"), limit=8)
        if isinstance(frontload, dict)
        else []
    )
    weak_skill_activation = (
        not active_skills
        or len(active_skills) < 2
        or primitive_field_evidence_basis in {"lexical_hint", "text_fallback"}
    )
    if frontloaded_skills:
        if weak_skill_activation:
            active_skills = frontloaded_skills + [
                skill for skill in active_skills if skill not in frontloaded_skills
            ]
        else:
            for skill in frontloaded_skills:
                if skill not in active_skills:
                    active_skills.append(skill)

    deduped = []
    for skill in active_skills:
        if skill in ALLOWED_SKILLS and skill not in deduped:
            deduped.append(skill)
    active_skills = deduped
    deduped_background = []
    for skill in background_skills:
        if skill in ALLOWED_SKILLS and skill not in deduped_background and skill not in active_skills:
            deduped_background.append(skill)
    background_skills = deduped_background
    controller_trigger = (
        controller_trigger_override
        if controller_trigger_override is not None
        else derive_controller_trigger_surface(
            state,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        )
    )
    if isinstance(controller_trigger, dict):
        favored_skills = _normalize_skill_combo(controller_trigger.get("favored_skills"), limit=4)
        if favored_skills:
            active_skills = favored_skills + [
                skill for skill in active_skills if skill not in favored_skills
            ]
    full_active_skills = list(active_skills) + [
        skill for skill in background_skills if skill not in active_skills
    ]
    composition_pressure = (
        control_signals.get("composition_pressure", {})
        if isinstance(control_signals, dict)
        else {}
    )

    bound_skill = derive_skill_authority_bridge(
        state,
        problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
            control_signals_override=control_signals if isinstance(control_signals, dict) else None,
            closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        )

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
            frontload.get("selection_basis")
            if weak_skill_activation and isinstance(frontload, dict)
            else
            "controller_trigger"
            if isinstance(controller_trigger, dict)
            and nonempty_text(controller_trigger.get("selection_basis"))
            else primitive_field.get("selection_basis")
            if isinstance(primitive_field, dict)
            else "control_surface"
        ),
        "evidence_basis": (
            frontload.get("evidence_basis")
            if weak_skill_activation and isinstance(frontload, dict)
            else
            primitive_field.get("evidence_basis")
            if isinstance(primitive_field, dict)
            else "state_见证"
        ),
        "full_active_skills": full_active_skills,
    }
    if isinstance(controller_trigger, dict):
        payload["controller_trigger_if_any"] = {
            "trigger_names": [
                str(value).strip()
                for value in controller_trigger.get("trigger_names", [])
                if str(value).strip()
            ][:3],
            "favored_skills": _normalize_skill_combo(controller_trigger.get("favored_skills"), limit=4),
            "favored_combo": _normalize_skill_combo(controller_trigger.get("favored_combo"), limit=6),
            "why_now": nonempty_text(controller_trigger.get("why_now")),
            "mode": nonempty_text(controller_trigger.get("mode")),
            "arbitration_skill_if_any": canonicalize_skill_token(
                controller_trigger.get("arbitration_skill_if_any")
            ),
            "counter_question_if_any": nonempty_text(controller_trigger.get("counter_question_if_any")),
        }
    if background_skills:
        payload["background_skills_if_any"] = background_skills[:8]
    if frontloaded_skills:
        payload["frontloaded_skills_if_any"] = frontloaded_skills[:8]
    if isinstance(composition_pressure, dict):
        payload["composition_axes"] = composition_pressure.get("composition_axes", [])
        payload["composition_ready"] = (
            composition_pressure.get("composition_ready") is True
            and len(active_skills) >= 2
        )
        payload["composition_reason"] = nonempty_text(composition_pressure.get("reason"))
        if (
            payload.get("composition_ready") is not True
            and len(active_skills) >= 2
            and not nonempty_text(payload.get("composition_reason"))
        ):
            payload["composition_ready"] = True
            payload["composition_reason"] = (
                "multiple project skills are already live on the current layer and should compete before ordinary continuation"
            )
    elif len(active_skills) >= 2:
        payload["composition_ready"] = True
        payload["composition_reason"] = (
            "multiple project skills are already live on the current layer and should compete before ordinary continuation"
        )
    if isinstance(closure_nucleus, dict):
        payload["closure_authority_skill_if_any"] = (
            "精确封口" if closure_nucleus.get("closure_gate_active") is True else ""
        )
    if isinstance(bound_program, dict) and isinstance(bound_skill, dict):
        payload["bound_skill_if_any"] = nonempty_text(bound_skill.get("winning_skill_if_any"))
        payload["authority_skill_if_any"] = nonempty_text(bound_skill.get("winning_skill_if_any"))
    return payload


def rank_skill_candidate_for_current_layer(
    skill: str,
    *,
    touch_target: str = "",
    asked_medium: str = "",
    direct_closure_allowed: bool = True,
    current_seam: str = "",
    current_object: str = "",
    support_rank: int = 3,
    projected_gain_rank: int = 3,
) -> tuple[int, int, int, int]:
    canonical = canonicalize_skill_token(skill)
    if not canonical:
        return (9, 9, 9, 9)

    if canonical == "精确封口":
        return (
            (0, 0, 0, 0)
            if direct_closure_allowed and asked_medium and touch_target == asked_medium
            else (8, 0, 0, 0)
        )
    if canonical in CONTROL_META_SKILLS:
        return (projected_gain_rank, 7, 0, 0)

    if asked_medium and touch_target == asked_medium:
        base = 0 if canonical in {"读出", "投影读出", "定义即直接读出"} and direct_closure_allowed else 2
    elif current_seam and touch_target == current_seam:
        base = 0
    elif current_object and touch_target == current_object:
        base = 1
    elif touch_target:
        base = 2
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
    return (projected_gain_rank, base + support_rank, target_bonus, probe_penalty)


def _skill_role_labels(skill: object) -> set[str]:
    canonical = canonicalize_skill_token(skill)
    if not canonical:
        return set()
    roles: set[str] = set()
    if canonical in CONTROL_META_SKILLS:
        roles.add("control")
    if canonical in PROBE_LIKE_PRIMITIVES:
        roles.add("probe")
    if canonical in READOUT_LIKE_PRIMITIVES or canonical in COMPRESSION_HEAVY_PRIMITIVES:
        roles.add("readout")
    if canonical in TRANSFORM_SUPPORT_PRIMITIVES or canonical in STRUCTURE_NUCLEUS_PRIMITIVES:
        roles.add("structural")
    return roles


def _apply_combo_support_bonus(
    rank: int,
    reason: str,
    *,
    skill: object,
    supporters: list[str] | None = None,
) -> tuple[int, str]:
    canonical = canonicalize_skill_token(skill)
    normalized_supporters = _normalize_skill_combo(supporters, limit=4)
    if not canonical or not normalized_supporters:
        return rank, reason

    semantic_supporters = set(
        _semantics_list_values(get_skill_semantics(canonical), "coactivate_with")
    )
    leader_roles = _skill_role_labels(canonical)
    support_role_pool: set[str] = set()
    bonus = 0

    if any(supporter in semantic_supporters for supporter in normalized_supporters):
        bonus += 1
    for supporter in normalized_supporters:
        support_roles = _skill_role_labels(supporter)
        support_role_pool.update(support_roles)
        if "probe" in leader_roles and "structural" in support_roles:
            bonus += 1
        if "structural" in leader_roles and "probe" in support_roles:
            bonus += 1
        if "readout" in leader_roles and "structural" in support_roles:
            bonus += 1
        if "structural" in leader_roles and "readout" in support_roles:
            bonus += 1
    if len(normalized_supporters) >= 2 and len(support_role_pool) >= 2:
        bonus += 1

    if bonus <= 0:
        return rank, reason
    reduced_rank = max(rank - min(bonus, 2), 0)
    support_text = ", ".join(normalized_supporters[:2])
    return (
        reduced_rank,
        reason.rstrip(".") + f"; combo support from {support_text} pushes the current layer deeper",
    )


def projected_gain_profile_for_skill(
    skill: str,
    *,
    touch_target: str = "",
    asked_medium: str = "",
    current_object: str = "",
    current_debt: str = "",
    direct_closure_allowed: bool = True,
    supporting_skills: list[str] | None = None,
) -> tuple[int, str]:
    canonical = canonicalize_skill_token(skill)
    if not canonical:
        return 8, "no projected layer gain could be estimated"

    lower_object = current_object.lower()
    lower_debt = current_debt.lower()
    combined = f"{lower_object} {lower_debt}"
    function_graph_lane = (
        "f(" in current_object
        or "function" in combined
        or "monotonic" in combined
        or "curve" in combined
        or "graph" in combined
        or "root" in combined
        or "zero" in combined
        or "函数" in combined
        or "单调" in combined
        or "图像" in combined
        or "曲线" in combined
        or "零点" in combined
        or "导数" in combined
    )
    relation_lane = any(
        token in combined
        for token in [
            "relation",
            "comparable",
            "compare",
            "same-height",
            "balance",
            "split",
            "inequality",
            "比较",
            "等高",
            "相等",
            "关系",
            "不等式",
            "分组",
        ]
    )
    balance_state_graph_lane = (
        any(
            token in combined
            for token in [
                "balanced",
                "balance",
                "parentheses",
                "parenthesis",
                "prefix",
                "suffix",
                "concatenation",
                "括号",
                "平衡",
                "前缀",
                "后缀",
                "拼接",
            ]
        )
        and any(
            token in combined
            for token in [
                "string",
                "strings",
                "state",
                "lane",
                "minimize",
                "criterion",
                "状态",
                "车道",
                "最小",
                "判定",
            ]
        )
    )
    symmetry_comparison_lane = any(
        token in combined
        for token in [
            "same-height",
            "equal-height",
            "mirror",
            "symmetric",
            "symmetry",
            "two sides",
            "left/right",
            "same cost",
            "breakpoint",
            "double-root",
            "two-root",
            "equal-value",
            "equal level",
            "等高",
            "两侧",
            "对称",
            "镜像",
            "前缀",
            "后缀",
            "断点",
            "双根",
            "同一笔账",
            "同值",
        ]
    )
    target_only_geometry_lane = any(
        token in combined
        for token in [
            "fixed line",
            "intersection",
            "anchor line",
            "定直线",
            "交点",
            "横坐标",
            "定值",
        ]
    )
    parameter_boundary_lane = any(
        token in combined
        for token in [
            "minimum",
            "maximum",
            "lower bound",
            "upper bound",
            "parameter",
            "boundary",
            "最小值",
            "最大值",
            "下界",
            "上界",
            "参数",
            "边界",
            "饱和",
        ]
    )
    parameter_anchor_lane = any(
        token in combined
        for token in [
            "anchor",
            "special value",
            "representative",
            "peak",
            "threshold",
            "height",
            "锚",
            "特殊值",
            "代表值",
            "峰值",
            "阈值",
            "高度",
        ]
    )
    grouping_lane = any(
        token in combined
        for token in [
            "exact cover",
            "partition",
            "grouping",
            "matching",
            "删去",
            "删除",
            "分组",
            "覆盖",
            "匹配",
            "可分",
        ]
    )
    supporters = [
        canonicalize_skill_token(value)
        for value in (supporting_skills or [])
        if canonicalize_skill_token(value)
    ]
    读出_like = {
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
        "公共值压缩",
    }

    hostile_falsifier_lane = problem_wants_hostile_falsifier(
        current_object,
        current_debt,
        touch_target,
    )

    if asked_medium and touch_target == asked_medium and canonical in 读出_like:
        if direct_closure_allowed and current_debt == asked_medium:
            return _apply_combo_support_bonus(
                0,
                "this touch can close the asked medium immediately",
                skill=canonical,
                supporters=supporters,
            )
        return _apply_combo_support_bonus(
            4,
            "this mostly writes out before the current object has been honestly thinned",
            skill=canonical,
            supporters=supporters,
        )
    if canonical == "反问" and hostile_falsifier_lane:
        return _apply_combo_support_bonus(
            0,
            "one hostile falsifier can cheaply kill the fake main line before the structural combo thickens",
            skill=canonical,
            supporters=supporters,
        )
    if canonical == "图像":
        if balance_state_graph_lane and not hostile_falsifier_lane:
            return _apply_combo_support_bonus(
                0,
                "one 图像 can externalize the balance object as a two-lane state graph and expose the real controller immediately",
                skill=canonical,
                supporters=supporters,
            )
        if function_graph_lane or target_only_geometry_lane:
            return _apply_combo_support_bonus(
                0,
                "one 图像 can externalize the carrier skeleton and almost settle the current layer",
                skill=canonical,
                supporters=supporters,
            )
        return _apply_combo_support_bonus(
            1,
            "one 图像 can expose the live controller on the current layer",
            skill=canonical,
            supporters=supporters,
        )
    if canonical == "投影":
        if target_only_geometry_lane:
            return _apply_combo_support_bonus(
                0,
                "投影 can compress the fixed-line or intersection claim to one thinner carrier immediately",
                skill=canonical,
                supporters=supporters,
            )
        if grouping_lane:
            return _apply_combo_support_bonus(
                1,
                "投影 can shrink the grouping burden to one exact-cover style carrier",
                skill=canonical,
                supporters=supporters,
            )
        if relation_lane or function_graph_lane:
            return _apply_combo_support_bonus(
                1,
                "投影 can compress the burden to one thinner comparable carrier",
                skill=canonical,
                supporters=supporters,
            )
        return _apply_combo_support_bonus(
            2,
            "投影 helps, but it still looks like preparation rather than immediate takeover",
            skill=canonical,
            supporters=supporters,
        )
    if canonical in {"状态拆分", "相容"} and grouping_lane:
        return _apply_combo_support_bonus(
            1,
            "this can own the grouping / exact-cover layer before brute enumeration starts",
            skill=canonical,
            supporters=supporters,
        )
    if canonical == "对称" and symmetry_comparison_lane:
        return _apply_combo_support_bonus(
            0,
            "one 对称 comparison can collapse the equal-height / mirrored layer before algebra regrows",
            skill=canonical,
            supporters=supporters,
        )
    if canonical in {"极限边界", "守恒", "对称消元"}:
        if parameter_boundary_lane:
            return _apply_combo_support_bonus(
                1,
                "this can expose the decisive boundary controller behind the parameter target",
                skill=canonical,
                supporters=supporters,
            )
        if target_only_geometry_lane:
            return _apply_combo_support_bonus(
                2,
                "this can help, but the fixed-line claim still wants a more direct carrier first",
                skill=canonical,
                supporters=supporters,
            )
        return _apply_combo_support_bonus(
            1,
            "this can expose one decisive controller rather than just decorate the layer",
            skill=canonical,
            supporters=supporters,
        )
    if canonical in {"状态拆分", "赋值", "见证"}:
        if balance_state_graph_lane and canonical == "状态拆分":
            return _apply_combo_support_bonus(
                1,
                "state splitting can own the balance ledger once the two-lane carrier is visible",
                skill=canonical,
                supporters=supporters,
            )
        if balance_state_graph_lane and canonical == "见证":
            return _apply_combo_support_bonus(
                1,
                "one witness can cheaply kill fake balance heuristics once the state graph is visible",
                skill=canonical,
                supporters=supporters,
            )
        if parameter_anchor_lane and canonical == "赋值":
            return _apply_combo_support_bonus(
                0,
                "one anchor-value assignment can pin the live parameter layer before derivative-heavy continuation",
                skill=canonical,
                supporters=supporters,
            )
        if parameter_boundary_lane and canonical == "赋值":
            return _apply_combo_support_bonus(
                1,
                "one representative 赋值 can pin the parameter boundary almost immediately",
                skill=canonical,
                supporters=supporters,
            )
        if relation_lane or function_graph_lane:
            return _apply_combo_support_bonus(
                2,
                "this can support a real takeover, but it usually still needs one stronger carrier move",
                skill=canonical,
                supporters=supporters,
            )
        return _apply_combo_support_bonus(
            3,
            "this looks more like support or verification than first takeover",
            skill=canonical,
            supporters=supporters,
        )
    if canonical == "反问":
        return _apply_combo_support_bonus(
            3,
            "this is mainly a falsifier unless no structural first move is live",
            skill=canonical,
            supporters=supporters,
        )
    if canonical in 读出_like:
        if any(
            value in supporters
            for value in ["图像", "投影", "极限边界", "守恒", "对称消元"]
        ):
            return _apply_combo_support_bonus(
                2,
                "this 读出 becomes valuable once a structural carrier is already live",
                skill=canonical,
                supporters=supporters,
            )
        return _apply_combo_support_bonus(
            4,
            "this reads or writes more than it actually changes the layer",
            skill=canonical,
            supporters=supporters,
        )
    return _apply_combo_support_bonus(
        3,
        "this move may help, but its projected layer gain is still moderate",
        skill=canonical,
        supporters=supporters,
    )


def best_projected_gain_for_skill(
    skill: str,
    candidates: list[dict],
    *,
    asked_medium: str = "",
    current_object: str = "",
    current_debt: str = "",
    direct_closure_allowed: bool = True,
) -> tuple[int, str]:
    best_rank = 8
    best_reason = "no projected layer gain could be estimated"
    canonical = canonicalize_skill_token(skill)
    if not canonical:
        return best_rank, best_reason
    for candidate in candidates:
        if canonicalize_skill_token(candidate.get("skill")) != canonical:
            continue
        rank, reason = projected_gain_profile_for_skill(
            canonical,
            touch_target=nonempty_text(candidate.get("touch_target")),
            asked_medium=asked_medium,
            current_object=current_object,
            current_debt=current_debt,
            direct_closure_allowed=direct_closure_allowed,
            supporting_skills=(
                candidate.get("supporting_skills_if_any")
                if isinstance(candidate.get("supporting_skills_if_any"), list)
                else []
            ),
        )
        if rank < best_rank:
            best_rank = rank
            best_reason = reason
    return best_rank, best_reason


def projected_progress_percent_for_gain_rank(rank: int) -> int:
    ladder = {
        0: 12,
        1: 10,
        2: 8,
        3: 6,
        4: 5,
        5: 4,
        6: 3,
        7: 2,
        8: 1,
    }
    if rank in ladder:
        return ladder[rank]
    if rank < 0:
        return 12
    return 1


def strongest_support_rank_for_skill(skill: str, candidates: list[dict]) -> int:
    best = 3
    canonical = canonicalize_skill_token(skill)
    if not canonical:
        return best
    for candidate in candidates:
        if canonicalize_skill_token(candidate.get("skill")) != canonical:
            continue
        backed_by = nonempty_text(candidate.get("backed_by"))
        partner_count = len(
            [
                canonicalize_skill_token(value)
                for value in candidate.get("supporting_skills_if_any", [])
                if canonicalize_skill_token(value)
            ]
        ) if isinstance(candidate.get("supporting_skills_if_any"), list) else 0
        if backed_by == "event_owned_layer":
            rank = 0
        elif backed_by == "controller_trigger":
            rank = 0
        elif backed_by == "takeover_seed":
            rank = 1
        elif backed_by in {"closure_readiness", "counter_readiness"}:
            rank = 1
        elif backed_by == "semantic_coactivation":
            rank = 2
        elif backed_by == "primitive":
            rank = 1 if partner_count else 2
        elif backed_by == "primitive_field":
            rank = 2 if partner_count else 3
        else:
            rank = 3
        if rank < best:
            best = rank
    return best


def _candidate_support_rank(candidate: dict) -> int:
    backed_by = nonempty_text(candidate.get("backed_by"))
    partner_count = len(
        _normalize_skill_combo(candidate.get("supporting_skills_if_any"), limit=4)
    )
    if backed_by in {"event_owned_layer", "controller_trigger"}:
        return 0
    if backed_by in {"takeover_seed", "closure_readiness", "counter_readiness"}:
        return 1
    if backed_by == "generic_combo_competition":
        return 1 if partner_count >= 2 else 2
    if backed_by == "semantic_coactivation":
        return 2
    if backed_by == "primitive":
        return 1 if partner_count else 2
    if backed_by == "primitive_field":
        return 2 if partner_count else 3
    return 3


def _best_touch_target_for_skill(skill: str, candidates: list[dict], *, fallback: str = "") -> str:
    canonical = canonicalize_skill_token(skill)
    if not canonical:
        return fallback
    for candidate in candidates:
        if canonicalize_skill_token(candidate.get("skill")) != canonical:
            continue
        target = nonempty_text(candidate.get("touch_target"))
        if target:
            return target
    return fallback


def _build_generic_combo_candidates(
    candidates: list[dict],
    *,
    support_pool: list[str],
    default_target: str,
) -> list[dict]:
    combo_candidates: list[dict] = []
    ordered_skills: list[str] = []
    for candidate in candidates:
        canonical = canonicalize_skill_token(candidate.get("skill"))
        if canonical and canonical not in ordered_skills:
            ordered_skills.append(canonical)
    for canonical in support_pool:
        if canonical and canonical not in ordered_skills:
            ordered_skills.append(canonical)

    for skill in ordered_skills:
        if not skill or skill in CONTROL_META_SKILLS or skill == "精确封口":
            continue
        semantic_supporters = _semantics_list_values(
            get_skill_semantics(skill),
            "coactivate_with",
        )
        seen_supporters: list[str] = []
        for candidate in candidates:
            if canonicalize_skill_token(candidate.get("skill")) != skill:
                continue
            for value in _normalize_skill_combo(
                candidate.get("supporting_skills_if_any"),
                limit=4,
            ):
                if value and value != skill and value not in seen_supporters:
                    seen_supporters.append(value)
        for value in semantic_supporters + support_pool:
            canonical = canonicalize_skill_token(value)
            if (
                canonical
                and canonical != skill
                and canonical not in CONTROL_META_SKILLS
                and canonical not in seen_supporters
            ):
                seen_supporters.append(canonical)
        if primitive_claim_requires_partner(skill) and not seen_supporters:
            continue
        if not seen_supporters:
            continue
        target = _best_touch_target_for_skill(skill, candidates, fallback=default_target)
        if not target:
            continue
        shortlisted = seen_supporters[:GENERIC_COMBO_SUPPORT_LIMIT]
        max_combo_width = min(GENERIC_COMBO_SUPPORT_LIMIT, len(shortlisted))
        for width in range(1, max_combo_width + 1):
            for supporter_combo in combinations(shortlisted, width):
                combo_candidates.append(
                    {
                        "skill": skill,
                        "touch_target": target,
                        "expected_local_gain": "combo-supported takeover on the current layer",
                        "backed_by": "generic_combo_competition",
                        "supporting_skills_if_any": list(supporter_combo),
                    }
                )
                if len(combo_candidates) >= MAX_GENERIC_COMBO_CANDIDATES:
                    return combo_candidates
    return combo_candidates


def _same_carrier_takeover_active(state: dict) -> bool:
    primitive_takeover_gate = state.get("primitive_takeover_gate_if_any")
    return bool(
        isinstance(primitive_takeover_gate, dict)
        and nonempty_text(primitive_takeover_gate.get("trigger")) == "same_carrier_landing"
    )


def _derive_natural_followup_skill_for_rewritten_layer(
    state: dict,
    combo: list[str],
    *,
    leading_skill: str = "",
    touch_target: str = "",
) -> str:
    ordered_combo = [
        canonicalize_skill_token(value)
        for value in combo
        if canonicalize_skill_token(value)
    ]
    if not ordered_combo:
        return ""
    normalized_leading = canonicalize_skill_token(leading_skill) or ordered_combo[0]
    if normalized_leading not in {"图像", "投影", "状态拆分"}:
        return ""
    combined = " ".join(
        value
        for value in [
            nonempty_text(state.get("current_object")),
            nonempty_text(state.get("current_seam")),
            nonempty_text(state.get("current_debt")),
            nonempty_text(state.get("next_bite")),
            touch_target,
        ]
        if value
    ).lower()
    target_only_geometry_lane = any(
        token in combined
        for token in [
            "fixed line",
            "fixed point",
            "intersection",
            "coordinate",
            "x=",
            "y=",
            "anchor line",
            "polar line",
            "pole",
            "定直线",
            "定点",
            "交点",
            "横坐标",
            "纵坐标",
            "极线",
            "极点",
            "读数",
            "定值",
        ]
    )
    anchor_or_boundary_lane = any(
        token in combined
        for token in [
            "boundary",
            "endpoint",
            "edge",
            "extreme",
            "saturation",
            "anchor",
            "compare at",
            "at x",
            "at y",
            "special value",
            "landmark",
            "边界",
            "端点",
            "极值",
            "饱和",
            "锚",
            "锚线",
            "赋值",
            "比较",
        ]
    )
    rewritten_object_lane = any(
        token in combined
        for token in [
            "thinner carrier",
            "carrier skeleton",
            "explicit carrier",
            "projected carrier",
            "极线",
            "骨架",
            "截面",
            "投影",
            "更薄",
            "控制对象",
        ]
    )
    if "极限边界" in ordered_combo and anchor_or_boundary_lane:
        return "极限边界"
    if "赋值" in ordered_combo and (target_only_geometry_lane or anchor_or_boundary_lane):
        return "赋值"
    if "投影" in ordered_combo and rewritten_object_lane:
        return "投影"
    return ""


def _derive_rewritten_layer_promoted_touch(
    state: dict,
    landed_touch: dict,
    *,
    leading_skill: str = "",
    controller_trigger: dict | None = None,
) -> tuple[dict | None, str, list[str]]:
    landed_combo = extract_explicit_skill_combo(landed_touch)
    if not landed_combo:
        return None, "", []
    normalized_leading, reordered_combo = apply_controller_trigger_to_combo(
        landed_combo,
        leading_skill=leading_skill,
        controller_trigger=controller_trigger,
    )
    promoted = _derive_natural_followup_skill_for_rewritten_layer(
        state,
        reordered_combo,
        leading_skill=normalized_leading,
        touch_target=nonempty_text(landed_touch.get("target")),
    )
    if not promoted or promoted == normalized_leading:
        return None, normalized_leading, reordered_combo
    promoted_combo = [promoted] + [
        skill_name for skill_name in reordered_combo if skill_name != promoted
    ]
    promoted_target = (
        nonempty_text(state.get("current_seam"))
        or nonempty_text(landed_touch.get("target"))
        or nonempty_text(state.get("current_object"))
        or nonempty_text(state.get("current_debt"))
    )
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    if promoted in READOUT_LIKE_PRIMITIVES and promoted_target == asked_medium:
        return None, normalized_leading, reordered_combo
    supporting = [skill_name for skill_name in promoted_combo if skill_name != promoted][:3]
    promoted_touch = build_problem_born_touch_for_skill(
        state,
        promoted,
        target=promoted_target,
        supporting=supporting,
    )
    if not isinstance(promoted_touch, dict):
        return None, normalized_leading, reordered_combo
    return promoted_touch, promoted, promoted_combo[:6]


def derive_skill_competition(
    state: dict,
    problems: list[str],
    primitive_competition_override: dict | None = None,
    primitive_field_override: dict | None = None,
    control_signals_override: dict | None = None,
    closure_nucleus_override: dict | None = None,
    controller_trigger_override: dict | None = None,
    skill_field_override: dict | None = None,
    probe_discipline_override: dict | None = None,
    lit_candidate_override: list[str] | None = None,
) -> dict | None:
    if problems or state.get("release_veto") is not True:
        return None
    seeded_candidates: list[dict] = []
    seeded_leading_skill = ""
    seeded_combo: list[str] = []

    if _same_carrier_takeover_active(state):
        landed_touch = state.get("landed_next_touch_if_any")
        landed_combo = extract_explicit_skill_combo(landed_touch)
        if isinstance(landed_touch, dict) and landed_combo:
            controller_trigger = (
                controller_trigger_override
                if controller_trigger_override is not None
                else derive_controller_trigger_surface(
                    state,
                    primitive_field_override=primitive_field_override if isinstance(primitive_field_override, dict) else None,
                    control_signals_override=control_signals_override if isinstance(control_signals_override, dict) else None,
                )
            )
            leading_skill = canonicalize_skill_token(
                landed_touch.get("owner_skill_if_any")
            )
            leading_skill, landed_combo = apply_controller_trigger_to_combo(
                landed_combo,
                leading_skill=leading_skill,
                controller_trigger=controller_trigger if isinstance(controller_trigger, dict) else None,
            )
            touch_target = (
                nonempty_text(
                    landed_touch.get("target")
                )
                or nonempty_text(state.get("current_seam"))
                or nonempty_text(state.get("current_object"))
            )
            reason = (
                "the carrier just tightened; recompute and bind one fresh current-layer skill combo before ordinary continuation regains value"
            )
            primitive_field = (
                primitive_field_override
                if primitive_field_override is not None
                else state.get("primitive_field_if_any")
            )
            primitive_supporters: list[str] = []
            if isinstance(primitive_field, dict):
                raw_active = primitive_field.get("active_primitives")
                if isinstance(raw_active, list):
                    for value in raw_active:
                        canonical = canonicalize_skill_token(value)
                        if canonical and canonical not in primitive_supporters:
                            primitive_supporters.append(canonical)
                    for value in derive_semantic_coactivation_hints(
                        [
                            canonicalize_primitive_token(value)
                            for value in raw_active
                            if canonicalize_primitive_token(value)
                        ]
                    ):
                        if value not in primitive_supporters:
                            primitive_supporters.append(value)
            for skill_name in landed_combo[:6]:
                payload = {
                    "skill": skill_name,
                    "touch_target": touch_target,
                    "expected_local_gain": reason,
                    "backed_by": "takeover_seed",
                }
                supporters = [
                    value for value in primitive_supporters if value and value != skill_name
                ]
                if supporters:
                    payload["supporting_skills_if_any"] = supporters[:3]
                seeded_candidates.append(payload)
            for skill_name in primitive_supporters:
                if skill_name in landed_combo:
                    continue
                seeded_candidates.append(
                    {
                        "skill": skill_name,
                        "touch_target": touch_target,
                        "expected_local_gain": reason,
                        "backed_by": "primitive_field",
                        "supporting_skills_if_any": [
                            value for value in landed_combo[:3] if value != skill_name
                        ][:3],
                    }
                )
            seeded_leading_skill = leading_skill
            seeded_combo = [
                value
                for value in list(dict.fromkeys(landed_combo + primitive_supporters))
                if value
            ][:INTERNAL_CANDIDATE_LIGHT_LIMIT]
    explicit_layer = state.get("layer_composition_if_any")
    if (
        isinstance(explicit_layer, dict)
        and explicit_layer.get("event_owned") is True
        and _event_owned_layer_matches_live_surface(state, explicit_layer)
        and not _same_carrier_takeover_active(state)
    ):
        authorized_bite = explicit_layer.get("authorized_bite")
        combo = extract_explicit_skill_combo(authorized_bite)
        if combo:
            controller_trigger = (
                controller_trigger_override
                if controller_trigger_override is not None
                else derive_controller_trigger_surface(
                    state,
                    primitive_field_override=primitive_field_override if isinstance(primitive_field_override, dict) else None,
                    control_signals_override=control_signals_override if isinstance(control_signals_override, dict) else None,
                )
            )
            leading_skill = canonicalize_skill_token(
                explicit_layer.get("leading_skill_if_any")
                or (authorized_bite.get("owner_skill_if_any") if isinstance(authorized_bite, dict) else "")
            )
            leading_skill, combo = apply_controller_trigger_to_combo(
                combo,
                leading_skill=leading_skill,
                controller_trigger=controller_trigger if isinstance(controller_trigger, dict) else None,
            )
            touch_target = (
                nonempty_text(explicit_layer.get("current_seam"))
                or nonempty_text(explicit_layer.get("controlled_object"))
                or nonempty_text(explicit_layer.get("next_local_choice"))
                or nonempty_text(state.get("current_object"))
                or nonempty_text(state.get("current_debt"))
            )
            reason = (
                nonempty_text(explicit_layer.get("reason"))
                or "the current layer already carries one explicit event-owned skill combination"
            )
            payload = {
                "layer_object": nonempty_text(explicit_layer.get("layer_object"))
                or nonempty_text(state.get("current_object"))
                or nonempty_text(state.get("current_debt")),
            }
            for skill_name in combo[:INTERNAL_CANDIDATE_LIGHT_LIMIT]:
                seeded_candidates.append(
                    {
                        "skill": skill_name,
                        "touch_target": touch_target,
                        "expected_local_gain": reason,
                        "backed_by": "event_owned_layer",
                    }
                )
            if not seeded_leading_skill:
                seeded_leading_skill = leading_skill
            if not seeded_combo:
                seeded_combo = combo[:INTERNAL_CANDIDATE_LIGHT_LIMIT]
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
    controller_trigger = (
        controller_trigger_override
        if controller_trigger_override is not None
        else derive_controller_trigger_surface(
            state,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
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
    if isinstance(primitive_field, dict):
        primitive_touch_target = (
            nonempty_text(state.get("current_seam"))
            or nonempty_text(primitive_field.get("layer_object"))
            or nonempty_text(state.get("current_object"))
        )
        primitive_gain = (
            nonempty_text(primitive_field.get("why_now"))
            or "the current layer already carries executable primitive pressure"
        )
        raw_active_primitives = [
            canonicalize_primitive_token(value)
            for value in primitive_field.get("active_primitives", [])
            if canonicalize_primitive_token(value)
        ]
        weak_primitive_field = nonempty_text(primitive_field.get("evidence_basis")) in {
            "lexical_hint",
            "text_fallback",
        }
        semantic_supporters = [] if weak_primitive_field else derive_semantic_coactivation_hints(raw_active_primitives)
        primitive_support_pool = list(dict.fromkeys(raw_active_primitives + semantic_supporters))
        for primitive in raw_active_primitives:
            skill = canonicalize_skill_token(primitive)
            if skill:
                if primitive_claim_requires_partner(skill):
                    supporters = [value for value in primitive_support_pool if value != skill]
                    if weak_primitive_field or not supporters:
                        continue
                else:
                    supporters = [value for value in primitive_support_pool if value != skill][:3]
                candidates.append(
                    {
                        "skill": skill,
                        "touch_target": primitive_touch_target,
                        "expected_local_gain": primitive_gain,
                        "backed_by": "primitive_field",
                        **(
                            {"supporting_skills_if_any": supporters[:3]}
                            if supporters
                            else {}
                        ),
                    }
                )
        if not weak_primitive_field:
            for skill in semantic_supporters:
                candidates.append(
                    {
                        "skill": skill,
                        "touch_target": primitive_touch_target,
                        "expected_local_gain": primitive_gain,
                        "backed_by": "semantic_coactivation",
                        "supporting_skills_if_any": raw_active_primitives[:3],
                    }
                )
    if isinstance(controller_trigger, dict):
        favored_skills = _normalize_skill_combo(controller_trigger.get("favored_skills"), limit=4)
        trigger_names = _normalize_skill_combo(controller_trigger.get("trigger_names"), limit=3)
        trigger_reason = nonempty_text(controller_trigger.get("why_now"))
        trigger_target = (
            nonempty_text(state.get("current_seam"))
            or (
                nonempty_text(primitive_field.get("layer_object"))
                if isinstance(primitive_field, dict)
                else ""
            )
            or nonempty_text(state.get("current_object"))
            or nonempty_text(state.get("current_debt"))
        )
        for skill in favored_skills:
            candidates.append(
                {
                    "skill": skill,
                    "touch_target": trigger_target,
                    "expected_local_gain": trigger_reason,
                    "backed_by": "controller_trigger",
                    **(
                        {"supporting_skills_if_any": [value for value in favored_skills if value != skill][:3]}
                        if len(favored_skills) >= 2
                        else {}
                    ),
                    **({"why_now": trigger_reason} if trigger_reason else {}),
                    **({"surface": "controller_trigger"} if trigger_names else {}),
                }
            )

    micro_control_surface = (
        control_signals.get("micro_control_surface", {})
        if isinstance(control_signals, dict)
        else {}
    )
    counter_surface = (
        micro_control_surface.get("反问", {})
        if isinstance(micro_control_surface, dict)
        else {}
    )
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    current_seam = nonempty_text(state.get("current_seam"))
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))
    next_bite = nonempty_text(state.get("next_bite"))
    layerwise_pressure = {}
    读出_like_skills = {
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
        "公共值压缩",
        "精确封口",
    }
    if isinstance(control_signals, dict):
        meta_controls = control_signals.get("meta_controls", {})
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        if isinstance(meta_controls, dict):
            active_primitives = []
            if isinstance(primitive_field, dict):
                raw_active = primitive_field.get("active_primitives")
                if isinstance(raw_active, list):
                    active_primitives = [
                        canonicalize_primitive_token(value)
                        for value in raw_active
                        if canonicalize_primitive_token(value)
                    ]
            closure_blocking_primitives = [
                primitive for primitive in active_primitives if primitive not in 读出_like_skills
            ]
            if (
                meta_controls.get("closure_gate", {}).get("active") is True
                and closure_can_take_first_shot(
                    closure_nucleus=closure_nucleus,
                    direct_closure_allowed=True,
                    asked_medium=asked_medium,
                )
                and not _same_carrier_takeover_active(state)
                and (
                    not closure_blocking_primitives
                    or (asked_medium and current_debt == asked_medium and next_bite == asked_medium)
                )
            ):
                candidates.append(
                    {
                        "skill": "精确封口",
                        "touch_target": asked_medium,
                        "expected_local_gain": "deny release drift and force exact asked-medium contact",
                        "backed_by": "control",
                    }
                )
            structural_primitives_live = [
                primitive for primitive in active_primitives if primitive not in PROBE_LIKE_PRIMITIVES
            ]
            if (
                meta_controls.get("反问", {}).get("active") is True
            ):
                hostile_target = (
                    nonempty_text(counter_surface.get("target"))
                    or nonempty_text(
                        meta_controls.get("反问", {}).get("target")
                    )
                    or nonempty_text(state.get("revocation_handle"))
                    or nonempty_text(state.get("current_seam"))
                    or nonempty_text(state.get("current_object"))
                )
                supporting = structural_primitives_live[:3]
                candidates.append(
                    {
                        "skill": "反问",
                        "touch_target": hostile_target,
                        "expected_local_gain": (
                            "kill the attractive fake route with one cheap falsifier before the structural carrier thickens"
                            if supporting
                            else "kill decorative progress with one cheap falsifier"
                        ),
                        "backed_by": "control",
                        **(
                            {"supporting_skills_if_any": supporting}
                            if supporting
                            else {}
                        ),
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

    frontload = derive_problem_skill_frontload(
        state,
        primitive_field=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals=control_signals if isinstance(control_signals, dict) else None,
    )
    if isinstance(frontload, dict):
        frontload_skills = _normalize_skill_combo(frontload.get("candidate_skills"), limit=8)
        frontload_target = nonempty_text(frontload.get("touch_target")) or (
            nonempty_text(state.get("current_seam"))
            or nonempty_text(state.get("current_object"))
            or nonempty_text(state.get("current_debt"))
        )
        frontload_reason = nonempty_text(frontload.get("why_now"))
        for skill_name in frontload_skills:
            candidates.append(
                {
                    "skill": skill_name,
                    "touch_target": frontload_target,
                    "expected_local_gain": frontload_reason,
                    "why_now": frontload_reason,
                    "backed_by": "problem_frontload",
                    "supporting_skills_if_any": [
                        value for value in frontload_skills if value != skill_name
                    ][:3],
                }
            )

    function_图像_lane = bool(
        "f(" in current_object
        and any(
            token in current_debt.lower()
            for token in ["monotonic", "graph", "curve", "root", "zero", "inequality"]
        )
    )
    if function_图像_lane and not any(
        canonicalize_skill_token(candidate.get("skill")) == "图像"
        for candidate in candidates
        if isinstance(candidate, dict)
    ):
        图像_support = [
            value
            for value in ["投影", "极限边界", "状态拆分", "读出"]
            if any(
                canonicalize_skill_token(candidate.get("skill")) == value
                for candidate in candidates
                if isinstance(candidate, dict)
            )
        ]
        candidates.append(
            {
                "skill": "图像",
                "touch_target": current_seam or current_object,
                "expected_local_gain": "externalize the function carrier first and see whether the current layer almost collapses on the graph skeleton",
                "backed_by": "controller_trigger",
                **(
                    {"supporting_skills_if_any": 图像_support[:3]}
                    if 图像_support
                    else {}
                ),
            }
        )
    if function_图像_lane and not any(
        canonicalize_skill_token(candidate.get("skill")) == "赋值"
        for candidate in candidates
        if isinstance(candidate, dict)
    ):
        candidates.append(
            {
                "skill": "赋值",
                "touch_target": current_seam or current_object,
                "expected_local_gain": "rewrite or assign one thinner carrier first and test whether that already deletes enough burden",
                "backed_by": "semantic_coactivation",
                "supporting_skills_if_any": [
                    value for value in ["图像", "投影", "极限边界"] if value
                ][:3],
            }
        )

    lit_candidate_skills = _normalize_skill_combo(lit_candidate_override, limit=8)
    if not lit_candidate_skills:
        lightweight_skill_field = (
            dict(skill_field_override)
            if isinstance(skill_field_override, dict)
            else {
                "active_skills": [
                    canonicalize_skill_token(candidate.get("skill"))
                    for candidate in candidates
                    if isinstance(candidate, dict) and canonicalize_skill_token(candidate.get("skill"))
                ],
                "authority_skill_if_any": (
                    nonempty_text(primitive_competition.get("winner_if_any"))
                    if isinstance(primitive_competition, dict)
                    else ""
                ),
            }
        )
        lit_candidate_skills, _ = derive_frontloaded_skill_candidates(
            state,
            skill_field=lightweight_skill_field if isinstance(lightweight_skill_field, dict) else None,
            probe_discipline=probe_discipline_override if isinstance(probe_discipline_override, dict) else None,
            controller_trigger=controller_trigger if isinstance(controller_trigger, dict) else None,
        )
    if isinstance(controller_trigger, dict):
        favored_counter = _normalize_skill_combo(
            controller_trigger.get("favored_skills"),
            limit=4,
        )
        if (
                "反问" in favored_counter
                and problem_wants_hostile_falsifier(
                    current_object,
                    current_seam,
                current_debt,
                next_bite,
            )
                and "反问" not in lit_candidate_skills
            ):
                lit_candidate_skills = ["反问"] + lit_candidate_skills
    combo_active_primitives: list[str] = []
    if isinstance(primitive_field, dict):
        raw_combo_primitives = primitive_field.get("active_primitives")
        if isinstance(raw_combo_primitives, list):
            combo_active_primitives = [
                canonicalize_skill_token(value)
                for value in raw_combo_primitives
                if canonicalize_skill_token(value)
            ]
    combo_support_pool: list[str] = []
    for bucket in [
        lit_candidate_skills,
        [
            canonicalize_skill_token(candidate.get("skill"))
            for candidate in candidates
            if isinstance(candidate, dict) and canonicalize_skill_token(candidate.get("skill"))
        ],
        combo_active_primitives,
    ]:
        if not isinstance(bucket, list):
            continue
        for value in bucket:
            canonical = canonicalize_skill_token(value)
            if canonical and canonical not in combo_support_pool:
                combo_support_pool.append(canonical)
    candidates.extend(
        _build_generic_combo_candidates(
            candidates,
            support_pool=combo_support_pool[:8],
            default_target=(
                nonempty_text(state.get("current_seam"))
                or nonempty_text(state.get("current_object"))
                or nonempty_text(state.get("current_debt"))
                or nonempty_text(state.get("asked_medium_surface"))
            ),
        )
    )
    lit_candidate_set = set(lit_candidate_skills)

    deduped: list[dict] = []
    seen: set[tuple[str, str, tuple[str, ...], str]] = set()
    for candidate in candidates:
        key = (
            candidate.get("skill", ""),
            candidate.get("touch_target", ""),
            tuple(
                _normalize_skill_combo(
                    candidate.get("supporting_skills_if_any"),
                    limit=4,
                )
            ),
            nonempty_text(candidate.get("backed_by")),
        )
        if candidate.get("skill") and key not in seen:
            seen.add(key)
            deduped.append(candidate)
    candidates = deduped
    if not candidates:
        return None

    winning_skill = ""
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    current_seam = nonempty_text(state.get("current_seam"))
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))
    next_bite = nonempty_text(state.get("next_bite"))
    direct_closure_allowed = True
    layerwise_pressure = {}
    meta_controls = control_signals.get("meta_controls", {}) if isinstance(control_signals, dict) else {}
    composition_pressure = (
        control_signals.get("composition_pressure", {})
        if isinstance(control_signals, dict)
        else {}
    )
    if isinstance(control_signals, dict):
        layerwise_pressure = control_signals.get("layerwise_reselection_pressure", {})
        direct_closure_allowed = not (
            isinstance(layerwise_pressure, dict)
            and layerwise_pressure.get("active") is True
            and layerwise_pressure.get("direct_closure_allowed") is not True
        )
    反问 = meta_controls.get("反问", {}) if isinstance(meta_controls, dict) else {}
    counter_target = (
        nonempty_text(counter_surface.get("target"))
        or nonempty_text(反问.get("target"))
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
        or nonempty_text(反问.get("preferred_answer_kind"))
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
    closure_blocking_primitives = [
        primitive for primitive in active_primitives if primitive not in 读出_like_skills
    ]
    fresh_blind_pending_first_touch = fresh_blind_problem_first_touch_pending(
        state,
        asked_medium=asked_medium,
    )
    closure_first_shot_ready = closure_can_take_first_shot(
        closure_nucleus=closure_nucleus,
        direct_closure_allowed=direct_closure_allowed,
        asked_medium=asked_medium,
    ) and not _same_carrier_takeover_active(state) and not fresh_blind_pending_first_touch and (
        not closure_blocking_primitives
        or (asked_medium and current_debt == asked_medium and next_bite == asked_medium)
    )
    structural_primitives_live = [
        primitive for primitive in active_primitives if primitive not in PROBE_LIKE_PRIMITIVES
    ]
    counter_can_take_first_shot = (
        isinstance(反问, dict)
        and 反问.get("active") is True
        and counter_target
        and counter_kind in {"check", "见证"}
        and not explicit_primitive_winner
        and not structural_primitives_live
    )

    if closure_first_shot_ready:
        candidates.append(
            {
                "skill": "精确封口",
                "touch_target": asked_medium or current_debt or current_object,
                "expected_local_gain": "deny release drift and force exact asked-medium contact",
                "backed_by": "closure_readiness",
            }
        )
    if counter_can_take_first_shot:
        candidates.append(
            {
                "skill": "反问",
                "touch_target": counter_target,
                "expected_local_gain": "kill decorative progress with one cheap falsifier",
                "backed_by": "counter_readiness",
            }
        )
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        rank, reason = projected_gain_profile_for_skill(
            candidate.get("skill", ""),
            touch_target=nonempty_text(candidate.get("touch_target")),
            asked_medium=asked_medium,
            current_object=current_object,
            current_debt=current_debt,
            direct_closure_allowed=direct_closure_allowed,
            supporting_skills=(
                candidate.get("supporting_skills_if_any")
                if isinstance(candidate.get("supporting_skills_if_any"), list)
                else []
            ),
        )
        candidate["projected_gain_rank"] = rank
        candidate["projected_gain_reason"] = reason
        candidate["projected_progress_percent_if_selected"] = projected_progress_percent_for_gain_rank(rank)
    candidates = sorted(
        candidates,
        key=lambda candidate: (
            candidate.get("projected_gain_rank", 8),
            _candidate_support_rank(candidate),
            -len(
                _normalize_skill_combo(
                    candidate.get("supporting_skills_if_any"),
                    limit=4,
                )
            ),
            0
            if canonicalize_skill_token(candidate.get("skill")) == seeded_leading_skill
            else 1,
            0
            if canonicalize_skill_token(candidate.get("skill")) in lit_candidate_set
            else 1,
            candidate.get("skill", ""),
        ),
    )
    winning_candidate = candidates[0] if candidates else None
    if isinstance(winning_candidate, dict):
        winning_skill = canonicalize_skill_token(winning_candidate.get("skill")) or ""

    def _structural_candidate(candidate: dict) -> bool:
        candidate_skill = canonicalize_skill_token(candidate.get("skill"))
        return bool(
            candidate_skill
            and candidate_skill not in {
                "读出",
                "定义即直接读出",
                "投影读出",
                "主导机制读出",
                "向量差读出",
                "公共值压缩",
                "精确封口",
            }
        )

    if (
        isinstance(composition_pressure, dict)
        and composition_pressure.get("compression_without_support") is True
        and isinstance(winning_candidate, dict)
        and not _structural_candidate(winning_candidate)
    ):
        structural_alternative = next(
            (candidate for candidate in candidates if isinstance(candidate, dict) and _structural_candidate(candidate)),
            None,
        )
        if isinstance(structural_alternative, dict):
            winning_candidate = structural_alternative
            winning_skill = canonicalize_skill_token(winning_candidate.get("skill")) or winning_skill

    if (
        fresh_blind_problem_first_touch_pending(
            state,
            asked_medium=asked_medium,
        )
        and isinstance(winning_candidate, dict)
        and not _structural_candidate(winning_candidate)
    ):
        structural_alternative = next(
            (candidate for candidate in candidates if isinstance(candidate, dict) and _structural_candidate(candidate)),
            None,
        )
        if isinstance(structural_alternative, dict):
            winning_candidate = structural_alternative
            winning_skill = canonicalize_skill_token(winning_candidate.get("skill")) or winning_skill

    winning_combo = [winning_skill] if winning_skill else []
    if isinstance(winning_candidate, dict):
        for value in _normalize_skill_combo(
            winning_candidate.get("supporting_skills_if_any"),
            limit=GENERIC_COMBO_SUPPORT_LIMIT,
        ):
            if value and value not in winning_combo:
                winning_combo.append(value)

    coactive_skills: list[str] = []
    for skill_name in winning_combo:
        if skill_name and skill_name not in coactive_skills:
            coactive_skills.append(skill_name)
    for candidate in candidates:
        skill = canonicalize_skill_token(candidate.get("skill"))
        if skill and skill not in coactive_skills:
            coactive_skills.append(skill)
    if winning_skill and winning_skill not in coactive_skills:
        coactive_skills.insert(0, winning_skill)
    competition_basis = "projected_gain_first_takeover"
    arbitration_skill = ""
    counter_question = ""
    favored_combo = []
    if isinstance(controller_trigger, dict):
        arbitration_skill = canonicalize_skill_token(controller_trigger.get("arbitration_skill_if_any")) or ""
        counter_question = nonempty_text(controller_trigger.get("counter_question_if_any"))
        favored_combo = _normalize_skill_combo(controller_trigger.get("favored_combo"), limit=6)
        if arbitration_skill == "反问" and nonempty_text(controller_trigger.get("mode")) == "counter_question_arbitration":
            competition_basis = "counter_question_arbitrated_projected_gain"
    if not favored_combo and len(winning_combo) >= 2:
        favored_combo = winning_combo[:]

    return {
        "layer_object": nonempty_text(state.get("current_object")) or nonempty_text(state.get("current_debt")),
        "candidates": candidates[:10],
        "lit_candidate_skills_if_any": lit_candidate_skills[:8],
        "separating_check": (
            nonempty_text(closure_nucleus.get("separating_check_if_any"))
            if isinstance(closure_nucleus, dict)
            else nonempty_text(primitive_competition.get("separating_check")) if isinstance(primitive_competition, dict) else ""
        ),
        "winning_skill_if_any": winning_skill,
        "coactive_skills_if_any": coactive_skills[:8],
        "competition_basis": competition_basis,
        **({"winning_combo_if_any": winning_combo[:6]} if len(winning_combo) >= 2 else {}),
        **({"arbitration_skill_if_any": arbitration_skill} if arbitration_skill else {}),
        **({"counter_question_if_any": counter_question} if counter_question else {}),
        **({"favored_combo_if_any": favored_combo[:6]} if favored_combo else {}),
        **(
            {
                "winning_projected_gain_rank": best_projected_gain_for_skill(
                    winning_skill,
                    candidates,
                    asked_medium=asked_medium,
                    current_object=current_object,
                    current_debt=current_debt,
                    direct_closure_allowed=direct_closure_allowed,
                )[0],
                "winning_projected_gain_reason": best_projected_gain_for_skill(
                    winning_skill,
                    candidates,
                    asked_medium=asked_medium,
                    current_object=current_object,
                    current_debt=current_debt,
                    direct_closure_allowed=direct_closure_allowed,
                )[1],
                "winning_projected_progress_percent_if_selected": projected_progress_percent_for_gain_rank(
                    best_projected_gain_for_skill(
                        winning_skill,
                        candidates,
                        asked_medium=asked_medium,
                        current_object=current_object,
                        current_debt=current_debt,
                        direct_closure_allowed=direct_closure_allowed,
                    )[0]
                ),
            }
            if winning_skill
            else {}
        ),
        **(
            {
                "surface": "controller_trigger",
                "reason": nonempty_text(controller_trigger.get("why_now")),
            }
            if isinstance(controller_trigger, dict)
            else {}
        ),
        **(
            {
                "surface": "problem_frontload",
                "reason": nonempty_text(frontload.get("why_now")),
            }
            if not isinstance(controller_trigger, dict) and isinstance(frontload, dict)
            else {}
        ),
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
        "精确封口",
        "反问",
        "监督",
        "元认知",
        "中枢控制",
        "后脑守卫",
        "奖惩塑形",
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
        micro_control_surface.get("反问", {})
        if isinstance(micro_control_surface, dict)
        else {}
    )
    反问 = meta_controls.get("反问", {}) if isinstance(meta_controls, dict) else {}
    probe_like = bool(active_probe_primitives) or (
        isinstance(反问, dict) and 反问.get("active") is True
    )
    if not probe_like:
        return None

    preferred_probe_target = (
        nonempty_text(counter_surface.get("target"))
        or nonempty_text(反问.get("target"))
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
                gate_owner = "精确封口"
            elif gate_focus in {"seam", "rival"} and bound_kind in {"check", "见证"}:
                gate_owner = "反问"
    counter_kind = (
        nonempty_text(counter_surface.get("preferred_answer_kind"))
        or nonempty_text(反问.get("preferred_answer_kind"))
    )
    if gate_owner:
        winning_hypothesis = gate_owner
    if isinstance(skill_competition, dict):
        winning = canonicalize_skill_token(skill_competition.get("winning_skill_if_any"))
        if winning_hypothesis:
            pass
        elif (
            winning == "反问"
            and preferred_probe_target
            and counter_kind in {"check", "见证"}
        ):
            winning_hypothesis = winning
        elif winning and winning not in non_hypothesis_skills:
            winning_hypothesis = winning
        for candidate in skill_competition.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            skill = canonicalize_skill_token(candidate.get("skill"))
            if (
                skill
                and skill not in non_hypothesis_skills
                and not primitive_is_probe_like(skill)
                and skill not in candidate_hypotheses
            ):
                candidate_hypotheses.append(skill)

    if isinstance(skill_field, dict):
        for skill in skill_field.get("active_skills", []):
            canonical = canonicalize_skill_token(skill)
            if (
                canonical
                and canonical not in non_hypothesis_skills
                and canonical != "读出"
                and not primitive_is_probe_like(canonical)
                and canonical not in candidate_hypotheses
            ):
                candidate_hypotheses.append(canonical)

    if not winning_hypothesis and candidate_hypotheses:
        lead_primitive = active_primitives[0] if active_primitives else ""
        if lead_primitive and not primitive_is_probe_like(lead_primitive):
            winning_hypothesis = candidate_hypotheses[0]

    active_hypotheses: list[str] = []
    for skill in [winning_hypothesis, *candidate_hypotheses]:
        canonical = canonicalize_skill_token(skill)
        if canonical and canonical not in active_hypotheses:
            active_hypotheses.append(canonical)
    structural_skill = next(
        (
            skill for skill in active_hypotheses
            if skill not in {
                "读出",
                "定义即直接读出",
                "投影读出",
                "主导机制读出",
                "向量差读出",
            }
        ),
        "",
    )
    if structural_skill and winning_hypothesis and structural_skill != winning_hypothesis:
        active_hypotheses = [winning_hypothesis, structural_skill] + [
            skill for skill in active_hypotheses
            if skill not in {winning_hypothesis, structural_skill}
        ]

    binding_strength = "explicit_winner" if winning_hypothesis else "unbound"
    if winning_hypothesis and winning_hypothesis in candidate_hypotheses:
        binding_strength = "provisional_structural_lead"
    if len(active_hypotheses) >= 2:
        binding_strength = "plural_live_binding"

    allowed_probe_kinds = ["check", "见证"] if active_hypotheses else []
    if active_hypotheses and any(primitive in {"赋值", "特殊值探针"} for primitive in active_primitives):
        allowed_probe_kinds.append("write")
    check_methods = derive_check_methods(
        focus="seam",
        has_structural_lead=bool(active_hypotheses),
        has_tie_break_check=bool(
            nonempty_text(primitive_field.get("tie_break_check")) if isinstance(primitive_field, dict) else ""
        ),
        asked_medium_live=bool(nonempty_text(state.get("asked_medium_surface"))),
    )

    unbound = not active_hypotheses
    reason = (
        f"tiny probe work on {preferred_probe_target} should stay attached to the live skill set {', '.join(active_hypotheses[:3])}"
        if active_hypotheses
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
        "active_skill_hypotheses": active_hypotheses[:4],
        "hypothesis_binding_strength": binding_strength,
        "reason": reason,
        "check_skill_active": True,
        "allowed_check_methods": check_methods,
        "small_scale_enumeration_role": (
            "optional_post_compression_verifier"
            if active_hypotheses and "small_scale_enumeration_after_compression_only" in check_methods
            else "forbidden_before_structural_binding"
        ),
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
        if "ordinary_route_reconstruction" in text and "更薄载体重选" not in demoted_skills:
            demoted_skills.append("更薄载体重选")
        if "decorative_continuation_without_contact" in text and "精确封口" not in demoted_skills:
            demoted_skills.append("精确封口")
        if "better_wording_without_object_change" in text and "抓本质" not in demoted_skills:
            demoted_skills.append("抓本质")

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
                gate_owner = "精确封口"
            elif gate_focus in {"seam", "rival"} and bound_kind in {"check", "见证"}:
                gate_owner = "反问"
    if gate_owner:
        winning = gate_owner
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    same_carrier_takeover_active = _same_carrier_takeover_active(state)
    direct_closure_allowed = True
    if isinstance(closure_nucleus, dict):
        structural_bite = closure_nucleus.get("current_structural_bite_if_any")
        if isinstance(structural_bite, dict) and not program_is_direct_closure_like(
            structural_bite,
            asked_medium=asked_medium,
        ):
            direct_closure_allowed = False
    concrete_closure_ready = False
    if isinstance(closure_nucleus, dict):
        读出_bite = closure_nucleus.get("current_读出_bite_if_any")
        concrete_closure_ready = bool(
            isinstance(读出_bite, dict)
            and program_is_direct_closure_like(
                读出_bite,
                asked_medium=asked_medium,
            )
            and not is_generic_runtime_operation(读出_bite)
        )
    fresh_blind_pending_first_touch = fresh_blind_problem_first_touch_pending(
        state,
        asked_medium=asked_medium,
    )
    精确封口_gate_live = (
        not winning or winning in {"精确封口", "读出"}
    ) and (
        not same_carrier_takeover_active
        and
        nonempty_text(inhibition.get("gate_until"))
        == "asked_medium_contact_or_exact_executable_closure"
        and concrete_closure_ready
        and not fresh_blind_pending_first_touch
        and closure_can_take_first_shot(
            closure_nucleus=closure_nucleus,
            direct_closure_allowed=direct_closure_allowed,
            asked_medium=asked_medium,
        )
    )
    promoted = "精确封口" if 精确封口_gate_live else winning
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
    if _same_carrier_takeover_active(state):
        landed_touch = state.get("landed_next_touch_if_any")
        landed_combo = extract_explicit_skill_combo(landed_touch)
        if isinstance(landed_touch, dict) and landed_combo:
            controller_trigger = derive_controller_trigger_surface(
                state,
                primitive_field_override=(
                    primitive_field_override if isinstance(primitive_field_override, dict) else None
                ),
                control_signals_override=(
                    control_signals_override if isinstance(control_signals_override, dict) else None
                ),
            )
            leading_skill = canonicalize_skill_token(
                landed_touch.get("owner_skill_if_any")
            )
            promoted_touch, promoted_leading, promoted_combo = _derive_rewritten_layer_promoted_touch(
                state,
                landed_touch,
                leading_skill=leading_skill,
                controller_trigger=controller_trigger if isinstance(controller_trigger, dict) else None,
            )
            if (
                isinstance(promoted_touch, dict)
                and promoted_leading
                and promoted_combo
                and not is_generic_runtime_operation(promoted_touch)
            ):
                landed_touch = promoted_touch
                landed_combo = promoted_combo[:]
                leading_skill = promoted_leading
            payload = {
                "executable_local_touch_if_any": landed_touch,
                "silence_after_contact": True,
                "same_carrier_only": True,
                "active_skill_combo_if_any": landed_combo[:8],
            }
            if leading_skill:
                payload["winning_skill_if_any"] = leading_skill
            supporting = [
                skill_name for skill_name in landed_combo if skill_name and skill_name != leading_skill
            ]
            if supporting:
                payload["supporting_skills_if_any"] = supporting[:8]
            return payload

    explicit_layer = state.get("layer_composition_if_any")
    explicit_layer_surface_live = any(
        isinstance(state.get(key), dict)
        for key in [
            "bound_program",
            "carrier_handoff_if_any",
            "landed_next_touch_if_any",
        ]
    )
    if (
        isinstance(explicit_layer, dict)
        and explicit_layer.get("event_owned") is True
        and explicit_layer_surface_live
        and _event_owned_layer_matches_live_surface(state, explicit_layer)
        and not _same_carrier_takeover_active(state)
    ):
        raw_bite = explicit_layer.get("authorized_bite")
        authorized_bite = None
        if isinstance(raw_bite, dict):
            kind = nonempty_text(raw_bite.get("kind"))
            target = nonempty_text(raw_bite.get("target"))
            operation = nonempty_text(raw_bite.get("operation"))
            if kind and target and operation:
                authorized_bite = {
                    "kind": kind,
                    "target": target,
                    "operation": operation,
                }
                success_signal = nonempty_text(raw_bite.get("success_signal"))
                if success_signal:
                    authorized_bite["success_signal"] = success_signal
                owner_skill = canonicalize_skill_token(raw_bite.get("owner_skill_if_any"))
                if owner_skill:
                    authorized_bite["owner_skill_if_any"] = owner_skill
                owner_combo = extract_explicit_skill_combo(raw_bite)
                if owner_combo:
                    authorized_bite["owner_skill_combo_if_any"] = owner_combo[:6]
        explicit_combo = extract_explicit_skill_combo(authorized_bite)
        if isinstance(authorized_bite, dict) and explicit_combo:
            leading_skill = canonicalize_skill_token(
                explicit_layer.get("leading_skill_if_any")
                or authorized_bite.get("owner_skill_if_any")
            )
            executable_owner = canonicalize_skill_token(
                authorized_bite.get("owner_skill_if_any")
            )
            leading_skill, executable_owner = collapse_public_lit_skill_split(
                leading_skill,
                executable_owner,
            )
            payload = {
                "executable_local_touch_if_any": authorized_bite,
                "silence_after_contact": True,
                "same_carrier_only": explicit_layer.get("must_spend_handoff") is not True,
                "active_skill_combo_if_any": explicit_combo[:8],
            }
            if leading_skill:
                payload["winning_skill_if_any"] = leading_skill
            supporting = [
                skill_name
                for skill_name in explicit_combo
                if skill_name and skill_name != leading_skill
            ]
            if supporting:
                payload["supporting_skills_if_any"] = supporting[:8]
            if executable_owner and executable_owner != leading_skill:
                payload["executable_owner_skill_if_any"] = executable_owner
            return payload

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

    def executable_program_shape(payload: object) -> dict | None:
        if not isinstance(payload, dict):
            return None
        kind = nonempty_text(payload.get("kind"))
        target = nonempty_text(payload.get("target"))
        operation = nonempty_text(payload.get("operation"))
        if not kind or not target or not operation:
            return None
        touch = {
            "kind": kind,
            "target": target,
            "operation": operation,
        }
        success_signal = nonempty_text(payload.get("success_signal"))
        if success_signal:
            touch["success_signal"] = success_signal
        origin = nonempty_text(payload.get("origin"))
        if origin:
            touch["origin"] = origin
        owner_skill = nonempty_text(payload.get("owner_skill_if_any"))
        if owner_skill:
            touch["owner_skill_if_any"] = owner_skill
        raw_combo = payload.get("owner_skill_combo_if_any")
        if isinstance(raw_combo, list):
            owner_combo = []
            for value in raw_combo:
                canonical = canonicalize_skill_token(value)
                if canonical and canonical not in owner_combo:
                    owner_combo.append(canonical)
            if owner_combo:
                touch["owner_skill_combo_if_any"] = owner_combo[:6]
        return touch

    def combo_supports_winner(program: object, *, owner_hint: str = "") -> bool:
        shaped = executable_program_shape(program)
        if not isinstance(shaped, dict):
            return False
        explicit_combo = extract_explicit_skill_combo(shaped)
        explicit_owner = canonicalize_skill_token(shaped.get("owner_skill_if_any"))
        normalized_winner = canonicalize_skill_token(owner_hint or winning_skill)
        if not normalized_winner:
            return bool(explicit_owner or explicit_combo)
        if explicit_combo and normalized_winner not in explicit_combo:
            return False
        if explicit_owner and explicit_owner == normalized_winner:
            return True
        if explicit_owner and explicit_combo and normalized_winner in explicit_combo:
            return True
        if explicit_owner and explicit_owner != normalized_winner:
            return False
        return bool(explicit_combo and normalized_winner in explicit_combo)

    def with_control_skill_authority(
        program: object,
        *,
        control_skill: str,
        supporting_skills: list[str] | None = None,
    ) -> dict | None:
        shaped = executable_program_shape(program)
        control_skill = canonicalize_skill_token(control_skill)
        if not isinstance(shaped, dict) or not control_skill:
            return None
        owner_combo: list[str] = [control_skill]
        for value in extract_explicit_skill_combo(shaped):
            canonical = canonicalize_skill_token(value)
            if canonical and canonical not in owner_combo:
                owner_combo.append(canonical)
        for value in supporting_skills or []:
            canonical = canonicalize_skill_token(value)
            if canonical and canonical not in owner_combo:
                owner_combo.append(canonical)
        shaped["owner_skill_if_any"] = control_skill
        if owner_combo:
            shaped["owner_skill_combo_if_any"] = owner_combo[:6]
        return shaped

    def build_frontloaded_touch_for_skill(
        skill: str,
        *,
        target: str,
        supporting: list[str] | None = None,
    ) -> dict | None:
        return build_problem_born_touch_for_skill(
            state,
            skill,
            target=target,
            supporting=supporting,
        )

    def derive_problem_frontload_touch() -> dict | None:
        if not isinstance(skill_competition, dict) or not winning_skill:
            return None
        winning_candidate = next(
            (
                candidate
                for candidate in skill_competition.get("candidates", [])
                if isinstance(candidate, dict)
                and canonicalize_skill_token(candidate.get("skill")) == winning_skill
            ),
            None,
        )
        target = (
            nonempty_text((winning_candidate or {}).get("touch_target"))
            or nonempty_text(state.get("current_seam"))
            or nonempty_text(state.get("current_object"))
            or nonempty_text(state.get("current_debt"))
        )
        supporting = []
        if isinstance(winning_candidate, dict):
            supporting = _normalize_skill_combo(
                winning_candidate.get("supporting_skills_if_any"),
                limit=3,
            )
        if not supporting:
            supporting = [
                canonicalize_skill_token(value)
                for value in skill_competition.get("coactive_skills_if_any", [])
                if canonicalize_skill_token(value)
                and canonicalize_skill_token(value) != winning_skill
            ][:3]
        return build_frontloaded_touch_for_skill(
            winning_skill,
            target=target,
            supporting=supporting,
        )

    def derive_control_skill_touch() -> dict | None:
        control_skill = canonicalize_skill_token(winning_skill)
        if control_skill in {
            "外壳怀疑",
            "抓本质",
            "最终控制者",
            "元认知",
            "监督",
            "中枢控制",
            "后脑守卫",
            "奖惩塑形",
        }:
            return None
        return None

    def derive_specific_touch_for_skill(skill_name: str) -> dict | None:
        primitive_winner = canonicalize_primitive_token(skill_name)
        if not primitive_winner or not isinstance(primitive_field, dict):
            return None
        active_for_program = [primitive_winner]
        raw_active = primitive_field.get("active_primitives")
        composition_pressure = (
            control_signals.get("composition_pressure", {})
            if isinstance(control_signals, dict)
            else {}
        )
        explicit_multi_primitive = (
            isinstance(raw_active, list)
            and len(raw_active) > 1
            and nonempty_text(primitive_field.get("selection_basis")) == "explicit_hint"
        )
        if (
            explicit_multi_primitive
            or (
                isinstance(raw_active, list)
                and len(raw_active) > 1
                and isinstance(composition_pressure, dict)
                and composition_pressure.get("composition_ready") is True
            )
        ):
            ordered_active = [primitive_winner]
            for value in raw_active:
                canonical = canonicalize_primitive_token(value)
                if canonical and canonical not in ordered_active:
                    ordered_active.append(canonical)
            active_for_program = ordered_active[:3]
        single_field = {
            "layer_object": primitive_field.get("layer_object"),
            "active_primitives": active_for_program,
            "why_now": primitive_field.get("why_now"),
            "selection_basis": "explicit_hint",
            "evidence_basis": primitive_field.get("evidence_basis") or "state_见证",
        }
        tie_break_check = nonempty_text(primitive_field.get("tie_break_check"))
        if tie_break_check:
            single_field["tie_break_check"] = tie_break_check
        probe_state = dict(state)
        probe_state["primitive_competition_if_any"] = None
        program = derive_primitive_program_candidate(
            probe_state,
            problems,
            primitive_field_override=single_field,
        )
        if not isinstance(program, dict):
            return None
        return executable_program_shape(program)

    def derive_winner_specific_touch() -> dict | None:
        return derive_specific_touch_for_skill(winning_skill)

    def derive_non_counter_structural_followup() -> tuple[str, dict | None]:
        ordered_skills: list[str] = []
        if isinstance(skill_competition, dict):
            winning_candidate = next(
                (
                    candidate
                    for candidate in skill_competition.get("candidates", [])
                    if isinstance(candidate, dict)
                    and canonicalize_skill_token(candidate.get("skill")) == winning_skill
                ),
                None,
            )
            if isinstance(winning_candidate, dict):
                for value in winning_candidate.get("supporting_skills_if_any", []):
                    canonical = canonicalize_skill_token(value)
                    if canonical and canonical not in ordered_skills:
                        ordered_skills.append(canonical)
            for bucket in (
                skill_competition.get("lit_candidate_skills_if_any", []),
                skill_competition.get("coactive_skills_if_any", []),
            ):
                if isinstance(bucket, list):
                    for value in bucket:
                        canonical = canonicalize_skill_token(value)
                        if canonical and canonical not in ordered_skills:
                            ordered_skills.append(canonical)
        if isinstance(primitive_field, dict):
            raw_active = primitive_field.get("active_primitives")
            if isinstance(raw_active, list):
                for value in raw_active:
                    canonical = canonicalize_skill_token(value)
                    if canonical and canonical not in ordered_skills:
                        ordered_skills.append(canonical)

        excluded = {
            "",
            "反问",
            "精确封口",
            "外壳怀疑",
            "抓本质",
            "最终控制者",
            "元认知",
            "监督",
            "中枢控制",
            "后脑守卫",
            "奖惩塑形",
        }
        for skill_name in ordered_skills:
            if skill_name in excluded:
                continue
            specific_touch = derive_specific_touch_for_skill(skill_name)
            if combo_supports_winner(specific_touch, owner_hint=skill_name):
                return skill_name, specific_touch
            target = (
                nonempty_text(state.get("current_debt"))
                or nonempty_text(state.get("current_seam"))
                or nonempty_text(state.get("current_object"))
            )
            frontloaded_touch = build_frontloaded_touch_for_skill(
                skill_name,
                target=target,
                supporting=[],
            )
            if combo_supports_winner(frontloaded_touch, owner_hint=skill_name):
                return skill_name, frontloaded_touch
        return "", None

    bridge_touch = None
    executable_owner_skill = ""
    if isinstance(closure_nucleus, dict):
        structural = executable_program_shape(
            closure_nucleus.get("current_structural_bite_if_any")
        )
        读出 = executable_program_shape(
            closure_nucleus.get("current_读出_bite_if_any")
        )
        if (
            winning_skill == "精确封口"
            and not closure_waiting_on_structural_discharge
            and isinstance(读出, dict)
        ):
            bridge_touch = 读出
            executable_owner_skill = "精确封口"
        elif winning_skill == "反问":
            meta_controls = control_signals.get("meta_controls", {}) if isinstance(control_signals, dict) else {}
            micro_control_surface = (
                control_signals.get("micro_control_surface", {})
                if isinstance(control_signals, dict)
                else {}
            )
            counter_surface = (
                micro_control_surface.get("反问", {})
                if isinstance(micro_control_surface, dict)
                else {}
            )
            反问 = (
                meta_controls.get("反问", {}) if isinstance(meta_controls, dict) else {}
            )
            separating_check = nonempty_text(closure_nucleus.get("separating_check_if_any"))
            counter_target = (
                separating_check
                or nonempty_text(counter_surface.get("target"))
                or nonempty_text(反问.get("target"))
                or nonempty_text(state.get("current_seam"))
                or nonempty_text(state.get("current_object"))
            )
            counter_kind = (
                nonempty_text(counter_surface.get("preferred_answer_kind"))
                or nonempty_text(反问.get("preferred_answer_kind"))
            )
            if counter_kind not in {"check", "见证"}:
                counter_kind = "check"
            fresh_blind_first_touch_pending = fresh_blind_problem_first_touch_pending(
                state,
                asked_medium=asked_medium,
            )
            fallback_skill, fallback_touch = derive_non_counter_structural_followup()
            counter_must_hold_slot = (
                fresh_blind_first_touch_pending
                or not fallback_skill
                or not isinstance(fallback_touch, dict)
            )
            if counter_target and counter_must_hold_slot:
                bridge_touch = {
                    "kind": counter_kind,
                    "target": counter_target,
                    "operation": (
                        f"land one hostile 见证 on {counter_target}"
                        if counter_kind == "见证"
                        else f"land one hostile separating check on {counter_target}"
                    ),
                    "success_signal": (
                        f"hostile 见证 on {counter_target} killed decorative progress"
                        if counter_kind == "见证"
                        else f"separating check on {counter_target} killed decorative progress"
                    ),
                }
                executable_owner_skill = "反问"
            elif fallback_skill and isinstance(fallback_touch, dict):
                bridge_touch = fallback_touch
                executable_owner_skill = fallback_skill
        elif winning_skill:
            winner_specific_touch = derive_winner_specific_touch()
            if combo_supports_winner(winner_specific_touch, owner_hint=winning_skill):
                bridge_touch = winner_specific_touch
                executable_owner_skill = winning_skill
            else:
                frontloaded_touch = derive_problem_frontload_touch()
                if combo_supports_winner(frontloaded_touch, owner_hint=winning_skill):
                    bridge_touch = frontloaded_touch
                    executable_owner_skill = winning_skill
            if not bridge_touch:
                control_touch = derive_control_skill_touch()
                if combo_supports_winner(control_touch, owner_hint=winning_skill):
                    bridge_touch = control_touch
                    executable_owner_skill = winning_skill
            if not bridge_touch and (
                combo_supports_winner(structural, owner_hint=winning_skill)
            ):
                bridge_touch = structural
                executable_owner_skill = winning_skill
            elif not bridge_touch and combo_supports_winner(读出, owner_hint=winning_skill):
                bridge_touch = 读出
                executable_owner_skill = winning_skill

    if not bridge_touch and not winning_skill:
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
            lead_primitive = ""
            if isinstance(primitive_field, dict):
                primitives = primitive_field.get("active_primitives")
                if isinstance(primitives, list) and primitives:
                    lead_primitive = canonicalize_primitive_token(primitives[0])
            probe_like_unbound = (
                not winning_skill
                and primitive_is_probe_like(lead_primitive)
            )
            if probe_like_unbound:
                primitive_program = None
        if combo_supports_winner(primitive_program):
            bridge_touch = primitive_program
            # Only project-defined owner skills may surface here; program kind is an
            # operation channel, not a skill family.
            executable_owner_skill = canonicalize_skill_token(
                primitive_program.get("owner_skill_if_any")
            )
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
        for skill_name in skill_competition.get("coactive_skills_if_any", []):
            canonical = canonicalize_skill_token(skill_name)
            if canonical and canonical != winning_skill and canonical not in supporting_skills:
                supporting_skills.append(canonical)
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

    if (
        winning_skill
        and fresh_blind_problem_first_touch_pending(
            state,
            asked_medium=asked_medium,
        )
    ):
        _, focus_target, _, _ = _fresh_blind_problem_facing_target(state)
        if focus_target and nonempty_text(bridge_touch.get("target")) != focus_target:
            rebuilt_touch = build_problem_born_touch_for_skill(
                state,
                winning_skill,
                target=focus_target,
                supporting=supporting_skills[:4],
            )
            if isinstance(rebuilt_touch, dict):
                bridge_touch = rebuilt_touch

    explicit_touch_combo = extract_explicit_skill_combo(bridge_touch)
    if winning_skill:
        if winning_skill not in explicit_touch_combo:
            explicit_touch_combo = [winning_skill] + explicit_touch_combo
        for skill_name in supporting_skills:
            if skill_name and skill_name not in explicit_touch_combo:
                explicit_touch_combo.append(skill_name)
    if winning_skill and winning_skill not in explicit_touch_combo:
        return None
    active_skill_combo: list[str] = explicit_touch_combo[:]

    primitive_takeover_gate = state.get("primitive_takeover_gate_if_any")
    same_carrier_takeover_active = (
        isinstance(primitive_takeover_gate, dict)
        and nonempty_text(primitive_takeover_gate.get("trigger")) == "same_carrier_landing"
    )
    if same_carrier_takeover_active and isinstance(bridge_touch, dict):
        recomposed_program = derive_primitive_program_candidate(
            state,
            problems,
            primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        )
        if (
            isinstance(recomposed_program, dict)
            and not program_is_direct_closure_like(
                recomposed_program,
                asked_medium=asked_medium,
            )
            and program_is_direct_closure_like(
                bridge_touch,
                asked_medium=asked_medium,
            )
        ):
            bridge_touch = executable_program_shape(recomposed_program)
            if not winning_skill or winning_skill == "精确封口":
                winning_skill = canonicalize_skill_token(
                    primitive_field.get("active_primitives", [None])[0]
                    if isinstance(primitive_field, dict)
                    else ""
                )
            explicit_touch_combo = extract_explicit_skill_combo(bridge_touch)
            active_skill_combo = explicit_touch_combo[:]

    if isinstance(bridge_touch, dict) and active_skill_combo:
        effective_owner_skill = (
            executable_owner_skill
            or winning_skill
            or nonempty_text(bridge_touch.get("owner_skill_if_any"))
        )
        effective_combo = active_skill_combo[:]
        if effective_owner_skill and effective_owner_skill not in effective_combo:
            effective_combo = [effective_owner_skill] + [
                value for value in effective_combo if value != effective_owner_skill
            ]
        enriched_touch = _attach_skill_metadata(
            bridge_touch,
            owner_skill=effective_owner_skill,
            combo=effective_combo,
        )
        if isinstance(enriched_touch, dict):
            bridge_touch = enriched_touch
            executable_owner_skill = canonicalize_skill_token(effective_owner_skill)

    winning_skill, executable_owner_skill = collapse_public_lit_skill_split(
        winning_skill,
        executable_owner_skill or (
            canonicalize_skill_token(bridge_touch.get("owner_skill_if_any"))
            if isinstance(bridge_touch, dict)
            else ""
        ),
    )
    if (
        winning_skill
        and isinstance(bridge_touch, dict)
        and executable_owner_skill == ""
    ):
        bridge_touch = (
            _attach_skill_metadata(
                bridge_touch,
                owner_skill=winning_skill,
                combo=extract_explicit_skill_combo(bridge_touch),
            )
            or bridge_touch
        )

    payload = {
        "winning_skill_if_any": winning_skill,
        "executable_local_touch_if_any": bridge_touch,
        "silence_after_contact": True,
        "same_carrier_only": not isinstance(state.get("carrier_handoff_if_any"), dict),
    }
    if executable_owner_skill and executable_owner_skill != winning_skill:
        payload["executable_owner_skill_if_any"] = executable_owner_skill
    if supporting_skills:
        payload["supporting_skills_if_any"] = supporting_skills[:8]
    if active_skill_combo:
        payload["active_skill_combo_if_any"] = active_skill_combo[:8]
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
    if winning_skill != "精确封口" or not isinstance(skill_touch, dict):
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
    if meta_controls.get("后脑守卫", {}).get("active") is not True:
        return None
    if nonempty_text(meta_controls.get("中枢控制", {}).get("mode")) != "closure_gate":
        return None

    监督 = micro_surface.get("监督_pulse", {})
    closure_pull = micro_surface.get("closure_pull", {})
    if not (
        isinstance(监督, dict)
        and isinstance(closure_pull, dict)
        and 监督.get("active") is True
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
    读出_like = {
        "读出",
        "定义即直接读出",
        "投影读出",
        "主导机制读出",
        "向量差读出",
    }
    if not any(primitive not in 读出_like for primitive in structural_primitives):
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
            "thinner-carrier structural debt is still live, but 精确封口 should "
            "retake final authority immediately after one structural spend"
        ),
        "spend_first_program": primitive_program,
        "post_closure_touch_if_any": {
            "kind": skill_kind,
            "target": skill_target,
            "operation": nonempty_text(skill_touch.get("operation")),
            "success_signal": nonempty_text(skill_touch.get("success_signal")),
            "owner_skill_if_any": nonempty_text(skill_touch.get("owner_skill_if_any"))
            or "精确封口",
            "owner_skill_combo_if_any": extract_explicit_skill_combo(skill_touch)
            or ["精确封口"],
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
    skill_field_override: dict | None = None,
    skill_competition_override: dict | None = None,
    skill_authority_override: dict | None = None,
    first_layer_arena_override: dict | None = None,
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
    skill_field = (
        skill_field_override
        if skill_field_override is not None
        else derive_skill_field(
            state,
            problems,
            closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        )
    )
    skill_competition = (
        skill_competition_override
        if skill_competition_override is not None
        else derive_skill_competition(
            state,
            problems,
            closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        )
    )
    skill_authority = (
        skill_authority_override
        if skill_authority_override is not None
        else derive_skill_authority_bridge(
            state,
            problems,
            closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        )
    )
    first_layer_arena = (
        first_layer_arena_override
        if first_layer_arena_override is not None
        else derive_first_layer_arena(
            state,
            problems,
            skill_field_override=skill_field if isinstance(skill_field, dict) else None,
            skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
            skill_authority_override=skill_authority if isinstance(skill_authority, dict) else None,
        )
    )

    bound_program = state.get("bound_program")
    explicit_handoff = state.get("carrier_handoff_if_any")
    primitive_takeover_gate = state.get("primitive_takeover_gate_if_any")
    explicit_layer = state.get("layer_composition_if_any")
    gate_until = (
        nonempty_text(inhibition.get("gate_until"))
        if isinstance(inhibition, dict)
        else ""
    )
    current_object = nonempty_text(state.get("current_object"))
    current_debt = nonempty_text(state.get("current_debt"))
    asked_medium = nonempty_text(state.get("asked_medium_surface"))

    def project_program_shape(payload: object) -> dict | None:
        if not isinstance(payload, dict):
            return None
        kind = nonempty_text(payload.get("kind"))
        target = nonempty_text(payload.get("target"))
        operation = nonempty_text(payload.get("operation"))
        if not kind or not target or not operation:
            return None
        program = {
            "kind": kind,
            "target": target,
            "operation": operation,
        }
        success_signal = nonempty_text(payload.get("success_signal"))
        if success_signal:
            program["success_signal"] = success_signal
        owner_skill = canonicalize_skill_token(payload.get("owner_skill_if_any"))
        if owner_skill:
            program["owner_skill_if_any"] = owner_skill
        raw_combo = payload.get("owner_skill_combo_if_any")
        if isinstance(raw_combo, list):
            owner_combo: list[str] = []
            for value in raw_combo:
                canonical = canonicalize_skill_token(value)
                if canonical and canonical not in owner_combo:
                    owner_combo.append(canonical)
            if owner_combo:
                program["owner_skill_combo_if_any"] = owner_combo[:6]
        return attach_program_metadata_fields(program, payload)

    def combo_has_problem_facing_owner(combo: list[str]) -> bool:
        读出_like = {
            "读出",
            "定义即直接读出",
            "投影读出",
            "主导机制读出",
            "向量差读出",
        }
        return any(skill not in 读出_like for skill in combo)

    if isinstance(bound_program, dict):
        contract = {
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
        }
        active_skill_combo = extract_explicit_skill_combo(bound_program)
        if active_skill_combo:
            contract["active_skill_combo_if_any"] = active_skill_combo
        if isinstance(probe_discipline, dict) and probe_discipline.get("probe_must_bind") is True:
            contract["probe_must_bind_skill_hypothesis"] = True
            contract["active_skill_hypothesis"] = nonempty_text(
                probe_discipline.get("active_skill_hypothesis")
            )
        return contract

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

    if isinstance(primitive_takeover_gate, dict):
        gate_trigger = nonempty_text(primitive_takeover_gate.get("trigger"))
        if gate_trigger == "same_carrier_landing":
            authorized_bite = project_program_shape(state.get("landed_next_touch_if_any"))
            if not isinstance(authorized_bite, dict):
                authorized_bite = derive_primitive_program_candidate(state, problems)
            contract = {
                "active": True,
                "forbid_ordinary_regrowth": True,
                "must_bind_local_bite": True,
                "must_spend_handoff": False,
                "surface": "takeover_recomposition",
                "owner": "same_carrier",
                "current_object": current_object,
                "current_debt": current_debt,
                "authorized_bite": authorized_bite if isinstance(authorized_bite, dict) else primitive_takeover_gate,
                "reason": (
                    "the carrier just tightened; recompute and bind one fresh current-layer skill combo "
                    "before ordinary continuation regains value"
                ),
                "tears_on": gate_until or "fresh_skill_combo_bound_or_exact_refusal",
            }
            active_skill_combo = extract_explicit_skill_combo(authorized_bite)
            if active_skill_combo:
                contract["active_skill_combo_if_any"] = active_skill_combo[:5]
            if isinstance(authorized_bite, dict) and not program_is_direct_closure_like(
                authorized_bite,
                asked_medium=asked_medium,
            ):
                contract["structural_first"] = True
            if isinstance(probe_discipline, dict) and probe_discipline.get("probe_must_bind") is True:
                contract["probe_must_bind_skill_hypothesis"] = True
                contract["active_skill_hypothesis"] = nonempty_text(
                    probe_discipline.get("active_skill_hypothesis")
                )
            return contract

    if (
        isinstance(state.get("bootstrap_context"), dict)
        and nonempty_text(state.get("bootstrap_context", {}).get("mode"))
        == "fresh_blind_project_skills_on"
        and not isinstance(bound_program, dict)
        and not isinstance(explicit_handoff, dict)
        and not isinstance(primitive_takeover_gate, dict)
        and not isinstance(explicit_layer, dict)
    ):
        authorized_bite = None
        active_skill_combo: list[str] = []
        leading_skill = ""
        if isinstance(first_layer_arena, dict):
            leading_skill = canonicalize_skill_token(
                first_layer_arena.get("primary_skill_if_any")
            )
            arena_touch = project_program_shape(first_layer_arena.get("authorized_touch_if_any"))
            if isinstance(arena_touch, dict):
                authorized_bite = arena_touch
            arena_combo = first_layer_arena.get("active_skill_combo_if_any")
            if isinstance(arena_combo, list):
                active_skill_combo = [
                    canonicalize_skill_token(value)
                    for value in arena_combo
                    if canonicalize_skill_token(value)
                ][:6]
        if isinstance(skill_authority, dict):
            if not isinstance(authorized_bite, dict):
                authorized_bite = project_program_shape(
                    skill_authority.get("executable_local_touch_if_any")
                )
            if not active_skill_combo:
                active_skill_combo = extract_explicit_skill_combo(authorized_bite)
            if not leading_skill:
                leading_skill = canonicalize_skill_token(
                    skill_authority.get("winning_skill_if_any")
                )
        if (
            isinstance(skill_competition, dict)
            and not leading_skill
        ):
            leading_skill = canonicalize_skill_token(
                skill_competition.get("winning_skill_if_any")
            )
        if isinstance(skill_competition, dict) and len(active_skill_combo) < 2:
            enriched_combo: list[str] = []
            if leading_skill:
                enriched_combo.append(leading_skill)
            for value in skill_competition.get("coactive_skills_if_any", []):
                canonical = canonicalize_skill_token(value)
                if canonical and canonical not in enriched_combo:
                    enriched_combo.append(canonical)
            if len(enriched_combo) >= 2:
                active_skill_combo = enriched_combo[:6]
                if isinstance(authorized_bite, dict):
                    authorized_bite["owner_skill_combo_if_any"] = active_skill_combo[:6]
        frontload_target = choose_genuine_problem_facing_runtime_target(
            nonempty_text((first_layer_arena or {}).get("focus_target")),
            nonempty_text(authorized_bite.get("target")) if isinstance(authorized_bite, dict) else "",
            nonempty_text(state.get("current_seam")),
            current_object,
            current_debt,
            nonempty_text(state.get("next_bite")),
        )
        if (
            frontload_target and
            isinstance(authorized_bite, dict)
            and active_skill_combo
            and len(active_skill_combo) >= 2
            and combo_has_problem_facing_owner(active_skill_combo)
            and (not leading_skill or leading_skill in active_skill_combo)
        ):
            contract = {
                "active": True,
                "forbid_ordinary_regrowth": True,
                "must_bind_local_bite": True,
                "must_spend_handoff": False,
                "surface": "fresh_blind_first_touch",
                "owner": "same_carrier",
                "current_object": current_object,
                "current_debt": current_debt,
                "authorized_bite": authorized_bite,
                "reason": (
                    "fresh blind first layer must bind one explicit project skill combination "
                    "before ordinary continuation regains value"
                ),
                "tears_on": gate_until or "first_skill_combo_bound_or_exact_refusal",
                "active_skill_combo_if_any": active_skill_combo[:5],
            }
            if isinstance(skill_competition, dict):
                separating_check = nonempty_text(skill_competition.get("separating_check"))
                if separating_check:
                    contract["separating_check"] = separating_check
            if isinstance(probe_discipline, dict) and probe_discipline.get("probe_must_bind") is True:
                contract["probe_must_bind_skill_hypothesis"] = True
                contract["active_skill_hypothesis"] = nonempty_text(
                    probe_discipline.get("active_skill_hypothesis")
                )
            if not program_is_direct_closure_like(authorized_bite, asked_medium=asked_medium):
                contract["structural_first"] = True
            return contract

    return None


def derive_layer_composition(
    state: dict,
    *,
    discipline_contract: dict | None = None,
    skill_field: dict | None = None,
    skill_competition: dict | None = None,
    skill_authority_bridge: dict | None = None,
    skill_lighting_surface: dict | None = None,
    first_layer_arena: dict | None = None,
    primitive_field: dict | None = None,
    resume_bridge: dict | None = None,
    gap_object: dict | None = None,
) -> dict | None:
    def project_program_shape(payload: object) -> dict | None:
        if not isinstance(payload, dict):
            return None
        kind = nonempty_text(payload.get("kind"))
        target = nonempty_text(payload.get("target"))
        operation = nonempty_text(payload.get("operation"))
        if not kind or not target or not operation:
            return None
        program = {
            "kind": kind,
            "target": target,
            "operation": operation,
        }
        success_signal = nonempty_text(payload.get("success_signal"))
        if success_signal:
            program["success_signal"] = success_signal
        owner_skill = canonicalize_skill_token(payload.get("owner_skill_if_any"))
        if owner_skill:
            program["owner_skill_if_any"] = owner_skill
        raw_combo = payload.get("owner_skill_combo_if_any")
        if isinstance(raw_combo, list):
            owner_combo: list[str] = []
            for value in raw_combo:
                canonical = canonicalize_skill_token(value)
                if canonical and canonical not in owner_combo:
                    owner_combo.append(canonical)
            if owner_combo:
                program["owner_skill_combo_if_any"] = owner_combo[:6]
        return attach_program_metadata_fields(program, payload)

    explicit_layer = state.get("layer_composition_if_any")
    projected_from_contract = False
    if (
        isinstance(explicit_layer, dict)
        and explicit_layer.get("event_owned") is True
        and _event_owned_layer_matches_live_surface(state, explicit_layer)
    ):
        authorized_bite = project_program_shape(explicit_layer.get("authorized_bite"))
        combo = extract_explicit_skill_combo(authorized_bite)
        if not isinstance(authorized_bite, dict) or not combo:
            return None
    else:
        explicit_layer = {}
        contract = discipline_contract if isinstance(discipline_contract, dict) else {}
        authorized_bite = project_program_shape(contract.get("authorized_bite"))
        combo = extract_explicit_skill_combo(authorized_bite)
        if not (
            contract.get("active") is True
            and contract.get("must_bind_local_bite") is True
            and isinstance(authorized_bite, dict)
            and combo
        ):
            return None
        projected_from_contract = True

    layer_object = (
        nonempty_text(explicit_layer.get("layer_object"))
        or nonempty_text((discipline_contract or {}).get("current_object"))
        or nonempty_text(state.get("current_object"))
    )
    if isinstance(primitive_field, dict):
        candidate_layer = nonempty_text(primitive_field.get("layer_object"))
        if candidate_layer:
            layer_object = candidate_layer

    payload = {
        "active": True,
        "surface": nonempty_text(explicit_layer.get("surface"))
        or nonempty_text((discipline_contract or {}).get("surface"))
        or "unknown",
        "layer_object": layer_object,
        "current_seam": nonempty_text(explicit_layer.get("current_seam"))
        or nonempty_text(state.get("current_seam")),
        "current_debt": nonempty_text(explicit_layer.get("current_debt"))
        or nonempty_text((discipline_contract or {}).get("current_debt"))
        or nonempty_text(state.get("current_debt")),
        "active_skill_combo_if_any": combo,
        "event_owned": explicit_layer.get("event_owned") is True,
        "forbid_ordinary_regrowth": (
            explicit_layer.get("forbid_ordinary_regrowth") is True
            or (discipline_contract or {}).get("forbid_ordinary_regrowth") is True
        ),
        "must_bind_local_bite": (
            explicit_layer.get("must_bind_local_bite") is True
            or (discipline_contract or {}).get("must_bind_local_bite") is True
        ),
        "must_spend_handoff": (
            explicit_layer.get("must_spend_handoff") is True
            or (discipline_contract or {}).get("must_spend_handoff") is True
        ),
        "reason": nonempty_text(explicit_layer.get("reason"))
        or nonempty_text((discipline_contract or {}).get("reason")),
    }
    if isinstance(authorized_bite, dict):
        payload["authorized_bite"] = authorized_bite
        payload["controlled_object"] = (
            nonempty_text(explicit_layer.get("controlled_object"))
            or nonempty_text(authorized_bite.get("controlled_object_if_any"))
            or nonempty_text(authorized_bite.get("target"))
            or layer_object
        )
    else:
        payload["controlled_object"] = (
            nonempty_text(explicit_layer.get("controlled_object"))
            or layer_object
        )
    if isinstance(skill_field, dict):
        axes = skill_field.get("composition_axes")
        if isinstance(axes, list):
            composition_axes = [nonempty_text(value) for value in axes if nonempty_text(value)]
            if composition_axes:
                payload["composition_axes"] = composition_axes[:4]
        background = skill_field.get("background_skills_if_any")
        if isinstance(background, list):
            background_skills = [
                canonicalize_skill_token(value)
                for value in background
                if canonicalize_skill_token(value)
            ]
            if background_skills:
                payload["background_skills_if_any"] = background_skills[:6]
    if isinstance(primitive_field, dict):
        active_primitives = primitive_field.get("active_primitives")
        if isinstance(active_primitives, list):
            primitives = [nonempty_text(value) for value in active_primitives if nonempty_text(value)]
            if primitives:
                payload["active_primitives"] = primitives[:4]
    explicit_lighting = explicit_layer.get("lighting_if_any")
    if isinstance(explicit_lighting, dict):
        payload["lighting_if_any"] = {
            key: explicit_lighting.get(key)
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
            ]
            if explicit_lighting.get(key) not in (None, "", [], {})
        }
    elif isinstance(skill_lighting_surface, dict):
        payload["lighting_if_any"] = {
            key: skill_lighting_surface.get(key)
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
            ]
            if skill_lighting_surface.get(key) not in (None, "", [], {})
        }
    if (
        isinstance(first_layer_arena, dict)
        and not (
            isinstance(explicit_layer, dict)
            and explicit_layer.get("event_owned") is True
            and _event_owned_layer_matches_live_surface(state, explicit_layer)
        )
    ):
        arena_focus = nonempty_text(first_layer_arena.get("focus_target"))
        if arena_focus:
            payload["controlled_object"] = arena_focus
    next_choice = (
        nonempty_text(explicit_layer.get("next_local_choice"))
        or (nonempty_text(authorized_bite.get("next_object_if_any")) if isinstance(authorized_bite, dict) else "")
    )
    if not next_choice and isinstance(resume_bridge, dict):
        next_choice = nonempty_text(resume_bridge.get("next_local_choice"))
    controlled_object = nonempty_text(payload.get("controlled_object"))
    if controlled_object and next_choice and next_choice != controlled_object:
        next_choice = controlled_object
    elif controlled_object and not next_choice:
        next_choice = controlled_object
    if next_choice:
        payload["next_local_choice"] = next_choice
    gap_target = nonempty_text(explicit_layer.get("gap_object"))
    if not gap_target and isinstance(gap_object, dict):
        gap_target = nonempty_text(gap_object.get("object"))
    if gap_target:
        payload["gap_object"] = gap_target
    transition_change = nonempty_text(explicit_layer.get("transition_change"))
    if transition_change:
        payload["transition_change"] = transition_change
    if isinstance(authorized_bite, dict):
        for key in [
            "current_layer_object_if_any",
            "object_transform_if_any",
            "step_outline_if_any",
            "skill_phase_if_any",
        ]:
            value = nonempty_text(authorized_bite.get(key))
            if value:
                payload[key] = value
    leading_skill = canonicalize_skill_token(
        nonempty_text(explicit_layer.get("leading_skill_if_any"))
        or (authorized_bite.get("owner_skill_if_any") if isinstance(authorized_bite, dict) else "")
    ) or combo[0]
    if leading_skill:
        payload["leading_skill_if_any"] = leading_skill
    if projected_from_contract:
        separating_check = nonempty_text((discipline_contract or {}).get("separating_check"))
        if separating_check:
            payload["separating_check"] = separating_check
    return payload


def derive_explicit_layer_report_overrides(state: dict) -> dict | None:
    layer = state.get("layer_composition_if_any")
    if (
        not isinstance(layer, dict)
        or layer.get("event_owned") is not True
        or not _event_owned_layer_matches_live_surface(state, layer)
    ):
        return None

    def project_program_shape(payload: object) -> dict | None:
        if not isinstance(payload, dict):
            return None
        kind = nonempty_text(payload.get("kind"))
        target = nonempty_text(payload.get("target"))
        operation = nonempty_text(payload.get("operation"))
        if not kind or not target or not operation:
            return None
        program = {
            "kind": kind,
            "target": target,
            "operation": operation,
        }
        success_signal = nonempty_text(payload.get("success_signal"))
        if success_signal:
            program["success_signal"] = success_signal
        owner_skill = canonicalize_skill_token(payload.get("owner_skill_if_any"))
        if owner_skill:
            program["owner_skill_if_any"] = owner_skill
        owner_combo = extract_explicit_skill_combo(payload)
        if owner_combo:
            program["owner_skill_combo_if_any"] = owner_combo[:6]
        return attach_program_metadata_fields(program, payload)

    authorized_bite = project_program_shape(layer.get("authorized_bite"))
    combo = extract_explicit_skill_combo(authorized_bite)
    if not isinstance(authorized_bite, dict) or not combo:
        return None

    leading_skill = canonicalize_skill_token(layer.get("leading_skill_if_any"))
    if leading_skill and leading_skill not in combo:
        leading_skill = ""
    executable_owner_skill = canonicalize_skill_token(
        authorized_bite.get("owner_skill_if_any")
    )
    controlled_object = (
        nonempty_text(layer.get("controlled_object"))
        or nonempty_text(authorized_bite.get("target"))
        or nonempty_text(layer.get("gap_object"))
        or nonempty_text(layer.get("next_local_choice"))
        or nonempty_text(layer.get("layer_object"))
        or nonempty_text(state.get("current_object"))
    )
    seam_target = (
        nonempty_text(layer.get("current_seam"))
        or nonempty_text(state.get("current_seam"))
        or controlled_object
    )
    reason = (
        nonempty_text(layer.get("reason"))
        or "one explicit event-owned skill composition is currently live on this layer"
    )
    active_skills = combo[:]

    primitive_field = {
        "layer_object": controlled_object,
        "active_primitives": combo[:3],
        "why_now": reason,
        "selection_basis": "explicit_hint",
        "evidence_basis": "state_见证",
    }
    if seam_target:
        primitive_field["tie_break_check"] = seam_target

    skill_field = {
        "layer_object": controlled_object,
        "active_skills": active_skills[:8],
        "why_now": reason,
        "selection_basis": "explicit_hint",
        "evidence_basis": "state_见证",
        "full_active_skills": active_skills[:8],
        "composition_ready": len(combo) >= 2,
        "composition_reason": "the current layer already carries one explicit event-owned skill combination",
    }
    if leading_skill:
        skill_field["authority_skill_if_any"] = leading_skill
    if isinstance(state.get("bound_program"), dict):
        if leading_skill:
            skill_field["bound_skill_if_any"] = leading_skill
    if nonempty_text(state.get("asked_medium_surface")):
        skill_field["closure_authority_skill_if_any"] = "精确封口"

    skill_competition = {
        "layer_object": nonempty_text(layer.get("layer_object")) or nonempty_text(state.get("current_object")),
        "coactive_skills_if_any": combo[:6],
        "candidates": [
            {
                "skill": skill_name,
                "touch_target": seam_target or controlled_object,
                "expected_local_gain": reason,
                "backed_by": "event_owned_layer",
            }
            for skill_name in combo[:6]
        ],
    }
    if leading_skill:
        skill_competition["winning_skill_if_any"] = leading_skill
    explicit_lighting = layer.get("lighting_if_any")
    skill_lighting_surface = (
        {
            key: explicit_lighting.get(key)
            for key in [
                "lit_skill_if_any",
                "supporting_skills_if_any",
                "false_first_skill_if_any",
                "false_first_label_if_any",
                "false_skill_reason",
                "verify_touch_if_any",
                "accountability_nudge_if_any",
                "winning_projected_gain_reason",
                "ordinary_operations_are_not_skills",
                "anti_pipeline_note",
            ]
            if explicit_lighting.get(key) not in (None, "", [], {})
        }
        if isinstance(explicit_lighting, dict)
        else None
    )
    skill_authority_bridge = {
        "executable_local_touch_if_any": authorized_bite,
        "silence_after_contact": True,
        "same_carrier_only": not isinstance(state.get("carrier_handoff_if_any"), dict),
        "active_skill_combo_if_any": combo[:6],
    }
    leading_skill, executable_owner_skill = collapse_public_lit_skill_split(
        leading_skill,
        executable_owner_skill,
    )
    if leading_skill:
        skill_authority_bridge["winning_skill_if_any"] = leading_skill
    supporting_skills = [skill_name for skill_name in combo if skill_name != leading_skill]
    if supporting_skills:
        skill_authority_bridge["supporting_skills_if_any"] = supporting_skills[:8]
    if executable_owner_skill and executable_owner_skill != leading_skill:
        skill_authority_bridge["executable_owner_skill_if_any"] = executable_owner_skill

    layer_surface = nonempty_text(layer.get("surface"))
    must_spend_handoff = layer.get("must_spend_handoff") is True
    must_bind_local_bite = layer.get("must_bind_local_bite") is True
    resume_mode = "continue_same_carrier"
    same_carrier_preferred = True
    if must_spend_handoff:
        resume_mode = "reopen_on_thinner_carrier"
        same_carrier_preferred = False
    elif layer_surface == "takeover_recomposition" or must_bind_local_bite:
        resume_mode = "reopen_same_carrier_layer"

    resume_bridge = {
        "mode": resume_mode,
        "known_object": controlled_object or nonempty_text(state.get("current_object")),
        "explicit_gap": controlled_object,
        "next_local_choice": controlled_object,
        "same_carrier_preferred": same_carrier_preferred,
        "supporting_skills": combo[:6],
    }

    probe_discipline = {
        "active": True,
        "probe_must_bind": True,
        "unbound_probe_is_drift": True,
        "active_skill_hypothesis": leading_skill,
        "active_skill_hypotheses": combo[:6],
        "reason": reason,
    }

    return {
        "skill_lighting_surface": skill_lighting_surface,
        "skill_authority_bridge": skill_authority_bridge,
        "resume_bridge": resume_bridge,
    }


def build_report(state: dict, state_path: Path) -> dict:
    problems: list[str] = []
    warnings: list[str] = []

    persisted_derived_overlap = sorted(
        key for key in DERIVED_READOUT_ONLY_KEYS if key in state
    )
    for key in persisted_derived_overlap:
        problems.append(
            f"state contains derived readout-only field `{key}`; derived runtime surfaces must not be persisted"
        )

    validate_no_extra_keys(
        state,
        PERSISTED_STATE_KEYS,
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

    bootstrap_context = state.get("bootstrap_context")
    if bootstrap_context is not None:
        if not isinstance(bootstrap_context, dict):
            problems.append("bootstrap_context must be an object or null")
        else:
            validate_no_extra_keys(
                bootstrap_context,
                {
                    "mode",
                    "readset_manifest",
                    "requires_fresh_state_path",
                    "requires_new_runtime_transition",
                    "requires_qualified_layer_composition_for_skill_claims",
                    "auto_enter_local_action_when_concrete",
                    "auto_reselect_after_layer_change",
                    "selection_dynamics",
                    "first_runtime_transition_window_seconds",
                    "first_runtime_transition_window_started_at",
                },
                "bootstrap_context",
                problems,
            )

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
    validate_layer_composition(state, problems)
    validate_gate_binding(state, problems)
    validate_primitive_field(state, problems)
    validate_primitive_takeover_gate(state, problems)
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
            "bound_program",
            "layer_composition_if_any",
            "gate_binding_if_any",
            "carrier_handoff_if_any",
            "primitive_field_if_any",
            "primitive_competition_if_any",
            "primitive_takeover_gate_if_any",
            "secondary_rival_if_any",
            "landed_next_touch_if_any",
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
    effective_program_origin = ""
    missing_program_problem = "bound_program is required while release_veto is active"
    explicit_handoff_live = state.get("carrier_handoff_if_any") is not None
    landed_next_touch = state.get("landed_next_touch_if_any")
    if (
        effective_handoff is None
        and not explicit_handoff_live
        and state.get("release_veto") is True
        and state.get("bound_program") is None
        and isinstance(landed_next_touch, dict)
    ):
        projected_landed_touch = None
        landed_kind = nonempty_text(landed_next_touch.get("kind"))
        landed_target = nonempty_text(landed_next_touch.get("target"))
        landed_operation = nonempty_text(landed_next_touch.get("operation"))
        if landed_kind and landed_target and landed_operation:
            projected_landed_touch = dict(landed_next_touch)
            projected_landed_touch["kind"] = landed_kind
            projected_landed_touch["target"] = landed_target
            projected_landed_touch["operation"] = landed_operation
            landed_success = nonempty_text(landed_next_touch.get("success_signal"))
            if landed_success:
                projected_landed_touch["success_signal"] = landed_success
            elif "success_signal" in projected_landed_touch:
                projected_landed_touch.pop("success_signal", None)
            landed_owner = canonicalize_skill_token(landed_next_touch.get("owner_skill_if_any"))
            if landed_owner:
                projected_landed_touch["owner_skill_if_any"] = landed_owner
            elif "owner_skill_if_any" in projected_landed_touch:
                projected_landed_touch.pop("owner_skill_if_any", None)
            landed_combo = extract_explicit_skill_combo(landed_next_touch)
            if landed_combo:
                projected_landed_touch["owner_skill_combo_if_any"] = landed_combo
            elif "owner_skill_combo_if_any" in projected_landed_touch:
                projected_landed_touch.pop("owner_skill_combo_if_any", None)
        if isinstance(projected_landed_touch, dict):
            problems[:] = [problem for problem in problems if problem != missing_program_problem]
            warnings.append("bound_program missing; landed next_touch inherited")
            effective_program = projected_landed_touch
            effective_program_origin = "landed_inherited"
    if (
        effective_handoff is None
        and not explicit_handoff_live
        and state.get("release_veto") is True
        and state.get("bound_program") is None
        and effective_program is None
    ):
        candidate = derive_bound_program_candidate(state, [])
        if isinstance(candidate, dict):
            fresh_blind_pending_first_touch = fresh_blind_problem_first_touch_pending(
                state,
            )
            authority_bridge = derive_skill_authority_bridge(
                state,
                [],
                primitive_field_override=effective_primitive_field
                if isinstance(effective_primitive_field, dict)
                else None,
            )
            authority_touch = (
                authority_bridge.get("executable_local_touch_if_any")
                if isinstance(authority_bridge, dict)
                else None
            )
            authority_owner = (
                nonempty_text(authority_bridge.get("winning_skill_if_any"))
                if isinstance(authority_bridge, dict)
                else ""
            )
            authority_combo = (
                authority_bridge.get("active_skill_combo_if_any")
                if isinstance(authority_bridge, dict)
                else None
            )
            same_local_touch = (
                isinstance(authority_touch, dict)
                and nonempty_text(candidate.get("kind")) == nonempty_text(authority_touch.get("kind"))
                and nonempty_text(candidate.get("target")) == nonempty_text(authority_touch.get("target"))
                and nonempty_text(candidate.get("operation")) == nonempty_text(authority_touch.get("operation"))
            )
            if (
                same_local_touch
                and not _has_explicit_owner_combo(candidate)
            ):
                candidate = (
                    _attach_skill_metadata(
                        candidate,
                        owner_skill=authority_owner,
                        combo=authority_combo,
                    )
                    or candidate
                )
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
            elif not state_has_explicit_local_ownership_evidence(state):
                if fresh_blind_pending_first_touch and _has_explicit_owner_combo(candidate):
                    problems[:] = [problem for problem in problems if problem != missing_program_problem]
                    warnings.append(
                        "bound_program missing; fresh-blind first-touch bridge promoted one explicit local next_touch"
                    )
                    effective_program = candidate
                    effective_program_origin = "derived"
                else:
                    warnings.append(
                        "bound_program missing; derived next_touch stayed suppressed because explicit local ownership is still absent"
                    )
            else:
                problems[:] = [problem for problem in problems if problem != missing_program_problem]
                warnings.append("bound_program missing; derived next_touch used")
                effective_program = candidate
                effective_program_origin = "derived"

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

    primitive_takeover_gate = state.get("primitive_takeover_gate_if_any")
    if isinstance(primitive_takeover_gate, dict):
        gate_trigger = nonempty_text(primitive_takeover_gate.get("trigger"))
        gate_note = nonempty_text(primitive_takeover_gate.get("note"))
        gate_primitives = primitive_takeover_gate.get("active_primitives")
        if state.get("bound_program") is None:
            if gate_trigger == "same_carrier_landing":
                warnings.append(
                    "primitive takeover gate is active after same-carrier landing; ordinary continuation should stay illegal until one explicit primitive-bound next bite lands"
                )
            elif gate_trigger == "thinner_carrier_handoff":
                warnings.append(
                    "primitive takeover gate is active after thinner-carrier handoff; ordinary continuation should stay illegal until one explicit primitive-bound thinner-carrier bite lands"
                )
            if gate_note:
                warnings.append("primitive takeover note: " + gate_note)
            if isinstance(gate_primitives, list) and gate_primitives:
                warnings.append(
                    "primitive takeover live set: "
                    + ", ".join(
                        canonicalize_primitive_token(value) or str(value).strip()
                        for value in gate_primitives
                        if canonicalize_primitive_token(value) or str(value).strip()
                    )
                )

    release_allowed = True

    if state.get("release_veto") is True:
        release_allowed = False
        warnings.append("release_veto is active")

    for key in [
        "bound_program",
        "layer_composition_if_any",
        "gate_binding_if_any",
        "carrier_handoff_if_any",
        "primitive_field_if_any",
        "primitive_competition_if_any",
        "primitive_takeover_gate_if_any",
        "secondary_rival_if_any",
        "landed_next_touch_if_any",
    ]:
        if state.get(key) is not None and state.get("release_veto") is not True:
            release_allowed = False
            warnings.append(f"{key} is still live after release")

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

    asked_medium_hint = extract_markdown_artifact_hint(state.get("asked_medium_surface"))
    if asked_medium_hint:
        asked_medium_path = state_path.with_name(asked_medium_hint)
        evidence = state.get("materialization_evidence")
        evidence_location = (
            nonempty_text(evidence.get("location"))
            if isinstance(evidence, dict)
            else ""
        )
        evidence_points_at_asked_medium = bool(
            evidence_location and Path(evidence_location).name == asked_medium_hint
        )
        if (
            asked_medium_path.exists()
            and (
                output_status.get("final_artifact_materialized") is not True
                or evidence_points_at_asked_medium is not True
            )
        ):
            release_allowed = False
            warnings.append(
                "asked medium file already exists on disk before runtime-owned materialization; treat it as bypass/manual output"
            )

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
    frontload_problems = fresh_blind_frontload_problems(state, problems)
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
        bound_program_origin_override=effective_program_origin or None,
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
            "explicit"
            if isinstance(state.get("bound_program"), dict)
            else effective_program_origin or "derived"
        ) if isinstance(effective_program, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
    )
    gap_object = derive_gap_object(
        state,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
    )
    controller_trigger = derive_controller_trigger_surface(
        state,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
    )
    skill_field = derive_skill_field(
        state,
        frontload_problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        controller_trigger_override=controller_trigger if isinstance(controller_trigger, dict) else None,
    )
    skill_semantics = (
        summarize_skill_semantics(skill_field.get("active_skills"))
        if isinstance(skill_field, dict)
        else {}
    )
    skill_competition = derive_skill_competition(
        state,
        frontload_problems,
        primitive_competition_override=effective_competition if isinstance(effective_competition, dict) else None,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        controller_trigger_override=controller_trigger if isinstance(controller_trigger, dict) else None,
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
        frontload_problems,
        inhibition_override=inhibition_state if isinstance(inhibition_state, dict) else None,
        skill_field_override=skill_field if isinstance(skill_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
    )
    probe_discipline = derive_probe_discipline(
        state,
        frontload_problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        skill_field_override=skill_field if isinstance(skill_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
    )
    skill_coaching_surface = derive_local_skill_coaching_surface(
        state,
        frontload_problems,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        skill_field_override=skill_field if isinstance(skill_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
        probe_discipline_override=probe_discipline if isinstance(probe_discipline, dict) else None,
        self_check_agenda_override=self_check_agenda if isinstance(self_check_agenda, dict) else None,
    )
    skill_authority_bridge = derive_skill_authority_bridge(
        state,
        frontload_problems,
        primitive_field_override=primitive_field if isinstance(primitive_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
    )
    skill_lighting_surface = derive_skill_lighting_surface(
        state,
        frontload_problems,
        control_signals_override=control_signals if isinstance(control_signals, dict) else None,
        skill_field_override=skill_field if isinstance(skill_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
        probe_discipline_override=probe_discipline if isinstance(probe_discipline, dict) else None,
        self_check_agenda_override=self_check_agenda if isinstance(self_check_agenda, dict) else None,
    )
    asked_medium = nonempty_text(state.get("asked_medium_surface"))
    closure_读出_bite = (
        closure_nucleus.get("current_读出_bite_if_any")
        if isinstance(closure_nucleus, dict)
        else None
    )
    closure_phrase = " ".join(
        part
        for part in [
            nonempty_text(state.get("current_seam")),
            nonempty_text(state.get("current_debt")),
            nonempty_text(state.get("next_bite")),
        ]
        if part
    )
    closure_frontload_ready = bool(
        asked_medium
        and isinstance(closure_读出_bite, dict)
        and program_is_direct_closure_like(closure_读出_bite, asked_medium=asked_medium)
        and not is_generic_runtime_operation(closure_读出_bite)
        and asked_medium.lower() in closure_phrase.lower()
    )
    primitive_takeover_gate = state.get("primitive_takeover_gate_if_any")
    if (
        closure_frontload_ready
        and isinstance(primitive_takeover_gate, dict)
        and nonempty_text(primitive_takeover_gate.get("trigger")) == "same_carrier_landing"
    ):
        closure_frontload_ready = False
    if closure_frontload_ready:
        closure_combo = _closure_combo_from_sources(
            skill_authority_bridge.get("active_skill_combo_if_any")
            if isinstance(skill_authority_bridge, dict)
            else None,
            skill_competition.get("winning_combo_if_any")
            if isinstance(skill_competition, dict)
            else None,
            skill_competition.get("coactive_skills_if_any")
            if isinstance(skill_competition, dict)
            else None,
            skill_lighting_surface.get("supporting_skills_if_any")
            if isinstance(skill_lighting_surface, dict)
            else None,
            primitive_field.get("active_primitives")
            if isinstance(primitive_field, dict)
            else None,
            closure_读出_bite,
        )
        closure_owner = _closure_owner_from_combo(
            skill_authority_bridge.get("active_skill_combo_if_any")
            if isinstance(skill_authority_bridge, dict)
            else None,
            skill_competition.get("winning_combo_if_any")
            if isinstance(skill_competition, dict)
            else None,
            skill_competition.get("coactive_skills_if_any")
            if isinstance(skill_competition, dict)
            else None,
            skill_lighting_surface.get("supporting_skills_if_any")
            if isinstance(skill_lighting_surface, dict)
            else None,
            primitive_field.get("active_primitives")
            if isinstance(primitive_field, dict)
            else None,
            closure_读出_bite,
            preferred_owner=(
                skill_authority_bridge.get("executable_owner_skill_if_any")
                if isinstance(skill_authority_bridge, dict)
                else ""
            )
            or (
                skill_competition.get("winning_skill_if_any")
                if isinstance(skill_competition, dict)
                else ""
            )
            or (
                closure_读出_bite.get("owner_skill_if_any")
                if isinstance(closure_读出_bite, dict)
                else ""
            ),
        )
        if not closure_combo or not closure_owner:
            closure_frontload_ready = False
        closure_support = [skill for skill in closure_combo if skill != closure_owner]
        closure_touch_with_combo = (
            _attach_skill_metadata(
                closure_读出_bite,
                owner_skill=closure_owner,
                combo=closure_combo,
            )
            if isinstance(closure_读出_bite, dict)
            else None
        )
        if isinstance(closure_touch_with_combo, dict):
            closure_读出_bite = closure_touch_with_combo
        if closure_frontload_ready and isinstance(skill_competition, dict):
            skill_competition["winning_skill_if_any"] = closure_owner
            skill_competition["winning_combo_if_any"] = closure_combo[:6]
            skill_competition["coactive_skills_if_any"] = closure_combo[:6]
            candidates = skill_competition.get("candidates")
            if isinstance(candidates, list):
                closure_candidate = {
                    "skill": closure_owner,
                    "touch_target": asked_medium,
                    "expected_local_gain": "the structural carrier is already discharged; exact asked-medium closure should take the next shot",
                    "backed_by": "closure_readiness",
                    "supporting_skills_if_any": closure_support[:4],
                }
                filtered = [
                    candidate
                    for candidate in candidates
                    if not (
                        isinstance(candidate, dict)
                        and canonicalize_skill_token(candidate.get("skill")) == closure_owner
                    )
                ]
                skill_competition["candidates"] = [closure_candidate] + filtered[:5]
        if closure_frontload_ready and isinstance(skill_field, dict):
            skill_field["authority_skill_if_any"] = closure_owner
            if isinstance(state.get("bound_program"), dict):
                skill_field["bound_skill_if_any"] = closure_owner
        if closure_frontload_ready and isinstance(skill_authority_bridge, dict):
            skill_authority_bridge["winning_skill_if_any"] = closure_owner
            skill_authority_bridge["executable_local_touch_if_any"] = closure_读出_bite
            skill_authority_bridge["active_skill_combo_if_any"] = closure_combo[:6]
            if closure_support:
                skill_authority_bridge["supporting_skills_if_any"] = closure_support[:6]
            else:
                skill_authority_bridge.pop("supporting_skills_if_any", None)
            skill_authority_bridge["silence_after_contact"] = True
        if closure_frontload_ready and isinstance(skill_lighting_surface, dict):
            skill_lighting_surface["lit_skill_if_any"] = closure_owner
            skill_lighting_surface["candidate_skills_if_any"] = closure_combo[:6]
            skill_lighting_surface["supporting_skills_if_any"] = closure_support[:4]
            skill_lighting_surface["verify_touch_if_any"] = {
                "target": asked_medium,
                "kind": nonempty_text(closure_读出_bite.get("kind")) or "write",
            }
        if closure_frontload_ready and isinstance(probe_discipline, dict):
            probe_discipline["active_skill_hypothesis"] = closure_owner
            probe_discipline["active_skill_hypotheses"] = closure_combo[:6]
    layer_arena = derive_layer_arena(
        state,
        frontload_problems,
        skill_field_override=skill_field if isinstance(skill_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
        skill_authority_override=skill_authority_bridge if isinstance(skill_authority_bridge, dict) else None,
        skill_lighting_override=skill_lighting_surface if isinstance(skill_lighting_surface, dict) else None,
        probe_discipline_override=probe_discipline if isinstance(probe_discipline, dict) else None,
    )
    first_layer_arena = (
        dict(layer_arena, surface="first_layer_arena")
        if isinstance(layer_arena, dict)
        else None
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
        frontload_problems,
        control_bridge_override=control_bridge if isinstance(control_bridge, dict) else None,
        reselection_bridge_override=reselection_bridge if isinstance(reselection_bridge, dict) else None,
        closure_nucleus_override=closure_nucleus if isinstance(closure_nucleus, dict) else None,
        inhibition_override=inhibition_state if isinstance(inhibition_state, dict) else None,
        interlayer_override=interlayer_discharge_bridge if isinstance(interlayer_discharge_bridge, dict) else None,
        probe_discipline_override=probe_discipline if isinstance(probe_discipline, dict) else None,
        skill_field_override=skill_field if isinstance(skill_field, dict) else None,
        skill_competition_override=skill_competition if isinstance(skill_competition, dict) else None,
        skill_authority_override=skill_authority_bridge if isinstance(skill_authority_bridge, dict) else None,
        first_layer_arena_override=first_layer_arena if isinstance(first_layer_arena, dict) else None,
    )
    layer_composition = derive_layer_composition(
        state,
        discipline_contract=discipline_contract if isinstance(discipline_contract, dict) else None,
        skill_field=skill_field if isinstance(skill_field, dict) else None,
        skill_competition=skill_competition if isinstance(skill_competition, dict) else None,
        skill_authority_bridge=skill_authority_bridge if isinstance(skill_authority_bridge, dict) else None,
        skill_lighting_surface=skill_lighting_surface if isinstance(skill_lighting_surface, dict) else None,
        first_layer_arena=first_layer_arena if isinstance(first_layer_arena, dict) else None,
        primitive_field=primitive_field if isinstance(primitive_field, dict) else None,
        resume_bridge=resume_bridge if isinstance(resume_bridge, dict) else None,
        gap_object=gap_object if isinstance(gap_object, dict) else None,
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
            if isinstance(primitive_takeover_gate, dict):
                control_bridge["primitive_takeover_gate"] = primitive_takeover_gate
            if isinstance(control_signals, dict):
                control_bridge["control_signals"] = control_signals
            if isinstance(closure_nucleus, dict):
                control_bridge["closure_nucleus"] = closure_nucleus
            if isinstance(gap_object, dict):
                control_bridge["gap_object"] = gap_object
            if isinstance(resume_bridge, dict):
                control_bridge["resume_bridge"] = resume_bridge
            if isinstance(controller_trigger, dict):
                control_bridge["controller_trigger"] = controller_trigger
        if isinstance(reselection_bridge, dict):
            reselection_bridge["primitive_field"] = primitive_field
            reselection_bridge["primitive_semantics"] = primitive_semantics
            if isinstance(primitive_takeover_gate, dict):
                reselection_bridge["primitive_takeover_gate"] = primitive_takeover_gate
            if isinstance(control_signals, dict):
                reselection_bridge["control_signals"] = control_signals
            if isinstance(closure_nucleus, dict):
                reselection_bridge["closure_nucleus"] = closure_nucleus
            if isinstance(gap_object, dict):
                reselection_bridge["gap_object"] = gap_object
            if isinstance(resume_bridge, dict):
                reselection_bridge["resume_bridge"] = resume_bridge
            if isinstance(controller_trigger, dict):
                reselection_bridge["controller_trigger"] = controller_trigger
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

    explicit_layer_overrides = derive_explicit_layer_report_overrides(state)
    if isinstance(explicit_layer_overrides, dict):
        if not (
            isinstance(skill_authority_bridge, dict)
            and isinstance(skill_authority_bridge.get("executable_local_touch_if_any"), dict)
        ):
            skill_authority_bridge = explicit_layer_overrides.get(
                "skill_authority_bridge",
                skill_authority_bridge,
            )
        if not (isinstance(resume_bridge, dict) and nonempty_text(resume_bridge.get("mode"))):
            resume_bridge = explicit_layer_overrides.get("resume_bridge", resume_bridge)
        if not isinstance(skill_lighting_surface, dict):
            skill_lighting_surface = explicit_layer_overrides.get(
                "skill_lighting_surface",
                skill_lighting_surface,
            )
        layer_arena = derive_layer_arena(state, [])
        first_layer_arena = (
            dict(layer_arena, surface="first_layer_arena")
            if isinstance(layer_arena, dict)
            else None
        )

    closure_bridge_touch = None
    if isinstance(skill_authority_bridge, dict):
        raw_closure_bridge_touch = skill_authority_bridge.get("executable_local_touch_if_any")
        if isinstance(raw_closure_bridge_touch, dict):
            closure_kind = nonempty_text(raw_closure_bridge_touch.get("kind"))
            closure_target = nonempty_text(raw_closure_bridge_touch.get("target"))
            closure_operation = nonempty_text(raw_closure_bridge_touch.get("operation"))
            if closure_kind and closure_target and closure_operation:
                closure_bridge_touch = {
                    "kind": closure_kind,
                    "target": closure_target,
                    "operation": closure_operation,
                }
                closure_signal = nonempty_text(raw_closure_bridge_touch.get("success_signal"))
                if closure_signal:
                    closure_bridge_touch["success_signal"] = closure_signal
                closure_owner = canonicalize_skill_token(
                    raw_closure_bridge_touch.get("owner_skill_if_any")
                )
                if closure_owner:
                    closure_bridge_touch["owner_skill_if_any"] = closure_owner
                closure_combo = extract_explicit_skill_combo(raw_closure_bridge_touch)
                if closure_combo:
                    closure_bridge_touch["owner_skill_combo_if_any"] = closure_combo
    if (
        closure_frontload_ready
        and isinstance(closure_bridge_touch, dict)
        and program_is_direct_closure_like(closure_bridge_touch, asked_medium=asked_medium)
        and not is_generic_runtime_operation(closure_bridge_touch)
        and nonempty_text(skill_authority_bridge.get("winning_skill_if_any")) == "精确封口"
    ):
        closure_combo = _closure_combo_from_sources(
            skill_authority_bridge.get("active_skill_combo_if_any"),
            skill_competition.get("winning_combo_if_any")
            if isinstance(skill_competition, dict)
            else None,
            skill_competition.get("coactive_skills_if_any")
            if isinstance(skill_competition, dict)
            else None,
            closure_bridge_touch,
        )
        closure_owner = _closure_owner_from_combo(
            skill_authority_bridge.get("active_skill_combo_if_any"),
            skill_competition.get("winning_combo_if_any")
            if isinstance(skill_competition, dict)
            else None,
            skill_competition.get("coactive_skills_if_any")
            if isinstance(skill_competition, dict)
            else None,
            closure_bridge_touch,
            preferred_owner=skill_authority_bridge.get("winning_skill_if_any"),
        )
        if not closure_combo or not closure_owner:
            closure_frontload_ready = False
        closure_support = [skill for skill in closure_combo if skill != closure_owner]
        if isinstance(discipline_contract, dict):
            discipline_contract["authorized_bite"] = closure_bridge_touch
            discipline_contract["active_skill_combo_if_any"] = closure_combo[:6]
        if isinstance(layer_composition, dict):
            layer_composition["authorized_bite"] = closure_bridge_touch
            layer_composition["leading_skill_if_any"] = closure_owner
            layer_composition["active_skill_combo_if_any"] = closure_combo[:6]
            layer_composition["lit_control_skill_if_any"] = closure_owner
            layer_composition["controlled_object"] = asked_medium
            layer_composition["next_local_choice"] = asked_medium
            lighting = layer_composition.get("lighting_if_any")
            if isinstance(lighting, dict):
                lighting["lit_skill_if_any"] = closure_owner
                lighting["candidate_skills_if_any"] = closure_combo[:6]
                lighting["supporting_skills_if_any"] = closure_support[:6]
                role_split = lighting.get("role_split_if_any")
                if isinstance(role_split, dict):
                    role_split["primary_skill_if_any"] = closure_owner
                    role_split["supporting_skills_if_any"] = closure_support[:6]
                    role_split["check_kind_if_any"] = nonempty_text(
                        closure_bridge_touch.get("kind")
                    ) or "write"
                    role_split["check_target_if_any"] = asked_medium
                lighting["verify_touch_if_any"] = {
                    "target": asked_medium,
                    "kind": nonempty_text(closure_bridge_touch.get("kind")) or "write",
                }
        if isinstance(first_layer_arena, dict):
            first_layer_arena["primary_skill_if_any"] = closure_owner
            first_layer_arena["authorized_touch_if_any"] = closure_bridge_touch
            first_layer_arena["active_skill_combo_if_any"] = closure_combo[:6]
            first_layer_arena["supporting_skills_if_any"] = closure_support[:6]
            role_split = first_layer_arena.get("role_split_if_any")
            if isinstance(role_split, dict):
                role_split["primary_skill_if_any"] = closure_owner
                role_split["supporting_skills_if_any"] = closure_support[:6]
                role_split["check_kind_if_any"] = nonempty_text(
                    closure_bridge_touch.get("kind")
                ) or "write"
                role_split["check_target_if_any"] = asked_medium

    public_report_owned_surface_live = bool(
        (
            isinstance(discipline_contract, dict)
            and discipline_contract.get("active") is True
        )
        or (
            isinstance(layer_composition, dict)
            and isinstance(layer_composition.get("authorized_bite"), dict)
        )
        or (
            isinstance(skill_authority_bridge, dict)
            and isinstance(skill_authority_bridge.get("executable_local_touch_if_any"), dict)
        )
    )
    if public_report_owned_surface_live:
        if isinstance(control_bridge, dict):
            suppressed = [
                key
                for key in [
                    "next_touch",
                    "candidate_next_touch",
                    "candidate_authorized_bite",
                    "default_local_action",
                ]
                if key in control_bridge
            ]
            for key in suppressed:
                control_bridge.pop(key, None)
            if suppressed:
                control_bridge["public_shadow_suppressed"] = suppressed
        if isinstance(reselection_bridge, dict):
            suppressed = [
                key
                for key in ["next_primitive_touch", "default_local_action"]
                if key in reselection_bridge
            ]
            for key in suppressed:
                reselection_bridge.pop(key, None)
            if suppressed:
                reselection_bridge["public_shadow_suppressed"] = suppressed

    public_skill_field = _append_skill_labels_zh(_sanitize_public_skill_field(skill_field))
    public_skill_competition = _append_skill_labels_zh(
        _sanitize_public_skill_competition(skill_competition)
    )
    public_skill_lighting_surface = _append_skill_labels_zh(_sanitize_public_skill_lighting_surface(
        skill_lighting_surface
    ))
    public_skill_semantics = (
        summarize_skill_semantics(public_skill_field.get("active_skills"))
        if isinstance(public_skill_field, dict)
        else {}
    )
    public_skill_competition_semantics = (
        summarize_skill_semantics(
            [
                candidate.get("skill")
                for candidate in public_skill_competition.get("candidates", [])
                if isinstance(candidate, dict)
            ]
        )
        if isinstance(public_skill_competition, dict)
        else {}
    )
    return {
        "state_file": str(state_path),
        "valid_schema_shape": not problems,
        "release_allowed": release_allowed and not problems,
        "control_bridge": control_bridge,
        "reselection_bridge": reselection_bridge,
        "control_signals": control_signals,
        "controller_trigger": controller_trigger,
        "gap_object": gap_object,
        "resume_bridge": resume_bridge,
        "primitive_field": primitive_field,
        "primitive_takeover_gate": primitive_takeover_gate,
        "primitive_semantics": primitive_semantics,
        "primitive_competition": effective_competition,
        "primitive_competition_semantics": primitive_competition_semantics,
        "self_check_agenda": self_check_agenda,
        "closure_nucleus": closure_nucleus,
        "skill_field": public_skill_field,
        "skill_semantics": public_skill_semantics,
        "skill_competition": public_skill_competition,
        "skill_competition_semantics": public_skill_competition_semantics,
        "skill_inhibition": skill_inhibition,
        "skill_authority_bridge": skill_authority_bridge,
        "skill_lighting_surface": public_skill_lighting_surface,
        "_internal_skill_lighting_surface": skill_lighting_surface,
        "layer_arena": layer_arena,
        "first_layer_arena": first_layer_arena,
        "skill_coaching_surface": skill_coaching_surface,
        "interlayer_discharge_bridge": interlayer_discharge_bridge,
        "probe_discipline": probe_discipline,
        "discipline_contract": discipline_contract,
        "layer_composition": layer_composition,
        "event_layer_overrides_if_any": explicit_layer_overrides,
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
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")

    if report["problems"]:
        return 2
    if not report["release_allowed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

