#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from runtime_guard import (
    ALLOWED_SKILLS,
    ALLOWED_PRIMITIVES,
    CONTROL_SKILL_SEMANTICS,
    PUBLIC_CONTROL_SKILLS,
    PUBLIC_LIT_SKILLS,
    PRIMITIVE_ALIAS_GROUPS,
    SKILL_ALIAS_GROUPS,
    get_skill_display_name_zh,
    get_primitive_semantics,
    get_skill_semantics,
    normalize_primitive_token,
)

PUBLIC_KERNEL_PRIMITIVES = sorted(PUBLIC_LIT_SKILLS)


def main() -> int:
    payload = {
        "project_skill_only_contract": {
            "active": True,
            "rule": "only project-defined skill families may enter skill competition, ownership, coaching, state, or trace surfaces",
            "ordinary_operations_are_not_skills": True,
        },
        "public_kernel_primitives": PUBLIC_KERNEL_PRIMITIVES,
        "public_kernel_primitives_zh": [
            get_skill_display_name_zh(primitive) for primitive in PUBLIC_KERNEL_PRIMITIVES
        ],
        "public_control_skills": sorted(PUBLIC_CONTROL_SKILLS),
        "public_control_skills_zh": [
            get_skill_display_name_zh(skill) for skill in sorted(PUBLIC_CONTROL_SKILLS)
        ],
        "executable_primitive_families": sorted(ALLOWED_PRIMITIVES),
        "executable_primitive_families_zh": [
            get_skill_display_name_zh(skill) for skill in sorted(ALLOWED_PRIMITIVES)
        ],
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
        "executable_skill_families_zh": [
            get_skill_display_name_zh(skill) for skill in sorted(ALLOWED_SKILLS)
        ],
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
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

