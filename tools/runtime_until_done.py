#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime_state import add_bool_argument, annotate_runtime_surface_payload
from runtime_supervision import run_until_done_supervisor as _run_until_done_supervisor


def _adapt_supervisor_result(
    result,
    *,
    auto_execute_local: bool,
    max_rounds: int | None,
) -> tuple[dict, int]:
    payload = dict(result.final_payload or {})
    if not payload:
        payload = {"state_file": result.state_file}

    if result.reason == "supervisor_stagnation_guard":
        payload["binding_action"] = "supervisor_stagnation_guard"

    payload["completion_supervisor"] = {
        "active": True,
        "rounds_used": result.executed_rounds,
        "auto_execute_local": auto_execute_local,
        "max_rounds": max_rounds,
        "layer_depth_ceiling": "none" if max_rounds is None else max_rounds,
        "history": list(result.step_history),
        "reason": result.reason,
    }
    if result.blocker is not None:
        payload["completion_supervisor"]["last_blocker"] = result.blocker.as_dict()
    if result.continuation_budget is not None:
        payload["completion_supervisor"]["continuation_budget"] = result.continuation_budget.as_dict()

    exit_code = result.final_exit_code
    if exit_code is None:
        exit_code = 0 if result.completed else 1
    return annotate_runtime_surface_payload(payload, exit_code=exit_code), exit_code


def run_until_done_supervisor(
    state_path: Path,
    *,
    allow_handoff: bool = False,
    spend_handoff: bool = False,
    allow_rival: bool = False,
    previous_state: str | None = None,
    worked_step: str | None = None,
    summary: str | None = None,
    output_file: str | None = None,
    cosmetic_only: bool | None = None,
    contains_unsupported: bool | None = None,
    contains_placeholder: bool | None = None,
    auto_execute_local: bool = True,
    max_rounds: int | None = None,
    stagnation_limit: int = 3,
) -> tuple[dict, int]:
    result = _run_until_done_supervisor(
        state_path,
        allow_handoff=allow_handoff,
        spend_handoff=spend_handoff,
        allow_rival=allow_rival,
        previous_state=previous_state,
        worked_step=worked_step,
        summary=summary,
        output_file=output_file,
        cosmetic_only=cosmetic_only,
        contains_unsupported=contains_unsupported,
        contains_placeholder=contains_placeholder,
        auto_execute_local=auto_execute_local,
        max_supervisor_rounds=max_rounds,
        stagnation_limit=stagnation_limit,
    )
    return _adapt_supervisor_result(
        result,
        auto_execute_local=auto_execute_local,
        max_rounds=max_rounds,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Thin adapter over the explicit runtime supervision entry point. "
            "Returns a payload-shaped surface for compatibility while preserving "
            "the single source of truth in runtime_supervision.py."
        )
    )
    parser.add_argument("state_file", help="Path to a runtime state json file")
    parser.add_argument("--previous-state", help="Compatibility pass-through for local bind loop", default=None)
    parser.add_argument("--worked-step", help="Optional first execute-local evidence step", default=None)
    parser.add_argument("--summary", help="Optional summary for the execute-local evidence", default=None)
    parser.add_argument("--output-file", help="Optional evidence output file", default=None)
    parser.add_argument("--max-rounds", type=int, default=None, help="Optional explicit cap for supervisor rounds")
    parser.add_argument(
        "--stagnation-limit",
        type=int,
        default=3,
        help="How many identical live-layer fingerprints are allowed before the supervisor stops",
    )
    parser.add_argument(
        "--no-auto-execute-local",
        action="store_true",
        help="Disable supervisor-owned execute-local synthesis and require explicit worked-step input",
    )
    add_bool_argument(parser, "--allow-handoff", "allow_handoff")
    add_bool_argument(parser, "--spend-handoff", "spend_handoff")
    add_bool_argument(parser, "--allow-rival", "allow_rival")
    parser.add_argument("--cosmetic-only", action="store_true", help="Mark the executed step as cosmetic-only")
    parser.add_argument("--contains-unsupported", action="store_true", help="Mark the executed step as unsupported")
    parser.add_argument("--contains-placeholder", action="store_true", help="Mark the executed step as containing placeholders")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    payload, exit_code = run_until_done_supervisor(
        Path(args.state_file),
        allow_handoff=args.allow_handoff is True,
        spend_handoff=args.spend_handoff is True,
        allow_rival=args.allow_rival is True,
        previous_state=args.previous_state,
        worked_step=args.worked_step,
        summary=args.summary,
        output_file=args.output_file,
        cosmetic_only=(True if args.cosmetic_only else None),
        contains_unsupported=(True if args.contains_unsupported else None),
        contains_placeholder=(True if args.contains_placeholder else None),
        auto_execute_local=not args.no_auto_execute_local,
        max_rounds=args.max_rounds,
        stagnation_limit=args.stagnation_limit,
    )
    json.dump(payload, sys.stdout, ensure_ascii=True, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
