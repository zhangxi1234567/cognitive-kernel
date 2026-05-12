#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from runtime_guard import (
    ALLOWED_SKILLS,
    ALLOWED_PRIMITIVES,
    CONTROL_SKILL_SEMANTICS,
    PRIMITIVE_ALIAS_GROUPS,
    SKILL_ALIAS_GROUPS,
    get_primitive_semantics,
    get_skill_semantics,
    normalize_primitive_token,
)

PUBLIC_KERNEL_PRIMITIVES = [
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
]

PUBLIC_CONTROL_SKILLS = [
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
]


def main() -> int:
    payload = {
        "public_kernel_primitives": PUBLIC_KERNEL_PRIMITIVES,
        "public_control_skills": PUBLIC_CONTROL_SKILLS,
        "executable_primitive_families": sorted(ALLOWED_PRIMITIVES),
        "alias_groups": {
            primitive: sorted(
                {
                    alias
                    for alias in aliases
                    if normalize_primitive_token(alias) != normalize_primitive_token(primitive)
                }
            )
            for primitive, aliases in sorted(PRIMITIVE_ALIAS_GROUPS.items())
        },
        "primitive_semantics": {
            primitive: get_primitive_semantics(primitive)
            for primitive in sorted(ALLOWED_PRIMITIVES)
        },
        "executable_skill_families": sorted(ALLOWED_SKILLS),
        "skill_alias_groups": {
            skill: sorted(
                {
                    alias
                    for alias in aliases
                    if normalize_primitive_token(alias) != normalize_primitive_token(skill)
                }
            )
            for skill, aliases in sorted(SKILL_ALIAS_GROUPS.items())
        },
        "skill_semantics": {
            skill: get_skill_semantics(skill)
            for skill in sorted(ALLOWED_SKILLS)
        },
        "control_skill_families": sorted(CONTROL_SKILL_SEMANTICS),
        "direct_or_alias_families": [
            primitive
            for primitive in sorted(ALLOWED_PRIMITIVES)
            if primitive not in PUBLIC_KERNEL_PRIMITIVES
        ],
    }
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
