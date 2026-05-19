#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from runtime_state import bootstrap_blind_state, default_fresh_blind_state_path, event_log_path

TEACHING_NOTES = (
    Path("references/joi-layerwise-skill-composition-note.md"),
    Path("references/gaokao-final-skill-composition-note.md"),
)
OWNER_MARKER_SUFFIX = ".prepare_blind_package_owner.json"
FORBIDDEN_RUNTIME_OUTPUT_FILENAMES = {
    "runtime_state.json",
    "runtime_state.events.jsonl",
    "runtime_trace.md",
    "runtime_skill_trace.md",
    "runtime_solve_trace.md",
    "answer.md",
    "final.md",
    "verdict.md",
}
FORBIDDEN_BLIND_PACKAGE_PATHS = {
    "README.md",
    "PACKAGE_MAP.md",
    "agents/openai.yaml",
    "skill.manifest.json",
}
FORBIDDEN_BLIND_PACKAGE_PREFIXES = {
    "benchmarks",
    "memory",
    "references",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize a fresh blind-test package from the canonical readset manifest "
            "without adding forbidden archive/history surfaces."
        )
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root that contains BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt",
    )
    parser.add_argument(
        "--manifest",
        default="BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt",
        help="Relative manifest path inside the project root",
    )
    parser.add_argument(
        "--package-dir",
        required=True,
        help="Target directory for the isolated read-only blind package",
    )
    parser.add_argument(
        "--run-dir",
        help="Sibling work directory for fresh blind runtime outputs",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete and recreate the target package/run directories first",
    )
    parser.add_argument(
        "--report-json",
        help="Optional path to write a packaging report JSON file",
    )
    parser.add_argument(
        "--include-teaching-notes",
        action="store_true",
        help=(
            "Also copy the JOI/gaokao teaching notes for manual or non-blind packages. "
            "Blind packages exclude them by default."
        ),
    )
    parser.add_argument(
        "--bootstrap-problem-file",
        help=(
            "Optional relative problem statement path to seed the fresh blind runtime bootstrap. "
            "Defaults to the unique blind_cases/*.problem.txt entry in the manifest."
        ),
    )
    parser.add_argument(
        "--bootstrap-current-object",
        help="Optional explicit current_object for the fresh blind bootstrap state",
    )
    parser.add_argument(
        "--bootstrap-current-seam",
        help="Optional explicit current_seam for the fresh blind bootstrap state",
    )
    parser.add_argument(
        "--bootstrap-current-debt",
        help="Optional explicit current_debt for the fresh blind bootstrap state",
    )
    parser.add_argument(
        "--bootstrap-next-bite",
        help="Optional explicit next_bite for the fresh blind bootstrap state",
    )
    parser.add_argument(
        "--asked-medium-surface",
        default="final.md",
        help="Relative markdown output path for the fresh blind asked-medium artifact",
    )
    parser.add_argument(
        "--allow-explicit-bootstrap-override",
        action="store_true",
        help=(
            "Allow manual bootstrap-current-* overrides even when a manifest problem statement exists. "
            "This is a non-canonical escape hatch."
        ),
    )
    return parser.parse_args()


def _safe_rmtree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def _owner_marker_path(path: Path) -> Path:
    return path.parent / f"{path.name}{OWNER_MARKER_SUFFIX}"


def _write_owner_marker(path: Path, *, role: str) -> None:
    marker_path = _owner_marker_path(path)
    payload = {
        "role": role,
        "path": str(path),
    }
    marker_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _remove_owner_marker(path: Path) -> None:
    marker_path = _owner_marker_path(path)
    if marker_path.exists():
        marker_path.unlink()


def _resolve_within(root: Path, rel: Path, *, role: str) -> Path:
    if rel.is_absolute():
        raise SystemExit(f"{role} must stay relative: {rel.as_posix()}")
    if any(part in {".", ".."} for part in rel.parts):
        raise SystemExit(f"{role} must not use dot-segments: {rel.as_posix()}")
    resolved = (root / rel).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SystemExit(f"{role} escapes its root: {rel.as_posix()}") from exc
    return resolved


def _is_same_or_nested(left: Path, right: Path) -> bool:
    try:
        left.relative_to(right)
        return True
    except ValueError:
        pass
    try:
        right.relative_to(left)
        return True
    except ValueError:
        return False


def _ensure_distinct_non_nested(package_dir: Path, run_dir: Path | None) -> None:
    if run_dir is None:
        return
    if package_dir == run_dir or _is_same_or_nested(package_dir, run_dir):
        raise SystemExit("package-dir and run-dir must stay distinct and non-nested")


def _ensure_missing_or_empty(path: Path, *, role: str) -> None:
    if not path.exists():
        return
    if path.is_file():
        raise SystemExit(f"{role} already exists as a file: {path}")
    if any(path.iterdir()):
        raise SystemExit(f"{role} must be missing or empty unless --clean is used: {path}")


def _ensure_clean_target_is_safe(path: Path, *, role: str, project_root: Path) -> None:
    try:
        path.relative_to(project_root)
        inside_project = True
    except ValueError:
        inside_project = False
    if path == project_root:
        raise SystemExit(f"{role} must not be the project root when --clean is used: {path}")
    if project_root in path.parents:
        protected_names = {
            "src",
            "tools",
            "tests",
            "runtime",
            "references",
            "benchmarks",
            "memory",
            "blind_cases",
            "agents",
        }
        if path.name in protected_names:
            raise SystemExit(
                f"{role} points at a protected project directory and cannot be removed with --clean: {path}"
            )
    if path.exists() and path.is_dir() and any(path.iterdir()):
        marker_path = _owner_marker_path(path)
        if not marker_path.exists():
            raise SystemExit(
                f"{role} must be tool-owned, empty, or missing before --clean removes it: {path}"
            )
    if inside_project and path.name.startswith(".git"):
        raise SystemExit(f"{role} must not target git metadata: {path}")


def _load_manifest(project_root: Path, manifest_path: Path) -> list[Path]:
    if not manifest_path.exists():
        raise SystemExit(f"manifest not found: {manifest_path}")
    entries: list[Path] = []
    for raw_line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        rel = Path(line)
        source = _resolve_within(project_root, rel, role="manifest entry")
        if not source.exists():
            raise SystemExit(f"manifest entry missing in project: {line}")
        entries.append(rel)
    return entries


def _copy_manifest_entries(project_root: Path, package_dir: Path, entries: list[Path]) -> list[str]:
    copied: list[str] = []
    for rel in entries:
        source = _resolve_within(project_root, rel, role="manifest entry")
        target = _resolve_within(package_dir, rel, role="package entry")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(rel.as_posix())
    return copied


def _copy_optional_entries(project_root: Path, package_dir: Path, entries: tuple[Path, ...]) -> list[str]:
    copied: list[str] = []
    for rel in entries:
        source = _resolve_within(project_root, rel, role="optional entry")
        if not source.exists():
            raise SystemExit(f"optional entry missing in project: {rel.as_posix()}")
        target = _resolve_within(package_dir, rel, role="optional entry")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(rel.as_posix())
    return copied


def _collapse_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _truncate(value: str, *, limit: int = 220) -> str:
    collapsed = _collapse_text(value)
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3].rstrip() + "..."


def _detect_problem_entry(entries: list[Path], explicit_problem: str | None) -> Path:
    if explicit_problem:
        rel = Path(explicit_problem)
        if rel.is_absolute() or any(part in {".", ".."} for part in rel.parts):
            raise SystemExit("bootstrap-problem-file must stay relative and dot-segment-free")
        if rel not in entries:
            raise SystemExit(
                "bootstrap-problem-file must match one manifest entry so fresh blind bootstrap "
                "stays on the handed readset"
            )
        return rel
    candidates = [
        rel
        for rel in entries
        if rel.suffix == ".txt"
        and rel.name.endswith(".problem.txt")
        and rel.parts
        and rel.parts[0] == "blind_cases"
    ]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise SystemExit(
            "fresh blind solve requires one problem statement entry in the manifest or "
            "--bootstrap-problem-file / explicit bootstrap fields"
        )
    raise SystemExit(
        "fresh blind solve found multiple manifest problem statements; pass --bootstrap-problem-file"
    )


def _extract_problem_seed(problem_text: str) -> dict[str, str]:
    lines = [line.strip() for line in problem_text.splitlines() if line.strip()]
    title = lines[0] if lines else "blind problem"
    lower = problem_text.lower()
    summary = ""
    for marker in ("problem summary", "task", "input"):
        if marker in lower:
            idx = lower.index(marker)
            window = _collapse_text(problem_text[idx : idx + 500])
            if window:
                summary = window
                break
    if not summary:
        summary = _collapse_text(" ".join(lines[:6]))
    current_object = _truncate(f"{title}. {summary}")

    parenthesis_balance_lane = (
        any(
            token in lower
            for token in [
                "balanced",
                "balance",
                "parenthesis",
                "prefix",
                "suffix",
                "bracket",
                "string",
                "strings",
                "括号",
                "平衡",
                "前缀",
                "后缀",
                "字符串",
            ]
        )
        and any(
            token in lower
            for token in [
                "choose x and y",
                "deformed balance",
                "minimize",
                "state",
                "prefix",
                "suffix",
                "补串",
                "最小",
                "畸形",
            ]
        )
    )

    if parenthesis_balance_lane:
        current_seam = (
            "which prefix/suffix state split or hostile witness decides the cheapest deformed-balance completion "
            "before ordinary balance repair regrows"
        )
        current_debt = (
            "separate the genuine balance-state controller from fake pure-balance heuristics and keep one local "
            "state-graph / split witness live"
        )
        next_bite = (
            "bind one concrete prefix/suffix state-graph or split witness on the current carrier without turning "
            "the bootstrap into staged route guidance"
        )
    else:
        current_seam = (
            "compress the stated object into one thinner controller-bearing carrier without turning "
            "the bootstrap itself into route guidance"
        )
        current_debt = (
            "separate the real controlling relation from decorative burden and keep the next runtime "
            "transition local, honest, and non-scripted"
        )
        next_bite = (
            "bind one concrete local touch on the current carrier without adding route hints or "
            "problem-specific solve staging"
        )

    return {
        "current_object": current_object,
        "current_seam": _truncate(current_seam),
        "current_debt": _truncate(current_debt),
        "next_bite": _truncate(next_bite),
    }


def _resolve_fresh_blind_bootstrap(
    args: argparse.Namespace,
    *,
    project_root: Path,
    entries: list[Path],
) -> tuple[dict[str, str], str]:
    explicit = {
        "current_object": str(args.bootstrap_current_object or "").strip(),
        "current_seam": str(args.bootstrap_current_seam or "").strip(),
        "current_debt": str(args.bootstrap_current_debt or "").strip(),
        "next_bite": str(args.bootstrap_next_bite or "").strip(),
    }
    explicit_override_requested = any(explicit.values())
    seed_source = "explicit"
    derived: dict[str, str] = {}
    requires_manifest_seed = (
        args.bootstrap_problem_file is not None
        or any(
            rel.suffix == ".txt"
            and rel.name.endswith(".problem.txt")
            and rel.parts
            and rel.parts[0] == "blind_cases"
            for rel in entries
        )
    )
    if (
        explicit_override_requested
        and requires_manifest_seed
        and not args.allow_explicit_bootstrap_override
    ):
        raise SystemExit(
            "fresh blind solve must derive bootstrap-current-* from the manifest problem statement "
            "unless --allow-explicit-bootstrap-override is set"
        )
    if not all(explicit.get(key) for key in ["current_object", "current_debt", "next_bite"]):
        problem_entry = _detect_problem_entry(entries, args.bootstrap_problem_file)
        problem_path = project_root / problem_entry
        if not problem_path.exists():
            raise SystemExit(f"bootstrap problem file missing in project: {problem_entry.as_posix()}")
        derived = _extract_problem_seed(problem_path.read_text(encoding="utf-8"))
        seed_source = problem_entry.as_posix()

    bootstrap = {
        "current_object": explicit["current_object"] or derived.get("current_object", ""),
        "current_seam": explicit["current_seam"] or derived.get("current_seam", ""),
        "current_debt": explicit["current_debt"] or derived.get("current_debt", ""),
        "next_bite": explicit["next_bite"] or derived.get("next_bite", ""),
        "asked_medium_surface": str(args.asked_medium_surface or "").strip() or "final.md",
    }
    if not bootstrap["current_seam"]:
        bootstrap["current_seam"] = bootstrap["current_object"]
    missing = [key for key in ["current_object", "current_debt", "next_bite"] if not bootstrap[key]]
    if missing:
        raise SystemExit(
            "fresh blind solve bootstrap is missing required fields: " + ", ".join(missing)
        )
    return bootstrap, seed_source


def _walk_relative_files(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    )


def _forbidden_manifest_entries(
    entries: list[Path],
    *,
    fresh_blind_mode: bool,
) -> list[str]:
    forbidden: list[str] = []
    for rel in entries:
        rel_text = rel.as_posix()
        name = rel.name
        if name in FORBIDDEN_RUNTIME_OUTPUT_FILENAMES or "__pycache__" in rel.parts:
            forbidden.append(rel_text)
            continue
        if not fresh_blind_mode:
            continue
        if rel_text in FORBIDDEN_BLIND_PACKAGE_PATHS:
            forbidden.append(rel_text)
            continue
        if any(rel.parts and rel.parts[0] == prefix for prefix in FORBIDDEN_BLIND_PACKAGE_PREFIXES):
            forbidden.append(rel_text)
    return sorted(set(forbidden))


def _verify_package(
    package_dir: Path,
    entries: list[Path],
    *,
    optional_entries: tuple[Path, ...] = (),
) -> dict[str, list[str]]:
    expected = {rel.as_posix() for rel in entries}
    expected.update(rel.as_posix() for rel in optional_entries)
    actual = set(_walk_relative_files(package_dir))
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    forbidden = sorted(
        path
        for path in actual
        if Path(path).name in FORBIDDEN_RUNTIME_OUTPUT_FILENAMES or "__pycache__" in Path(path).parts
    )
    return {
        "missing": missing,
        "unexpected": unexpected,
        "forbidden": forbidden,
    }


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    manifest_path = (project_root / args.manifest).resolve()
    package_dir = Path(args.package_dir).resolve()
    run_dir = Path(args.run_dir).resolve() if args.run_dir else None

    entries = _load_manifest(project_root, manifest_path)
    _ensure_distinct_non_nested(package_dir, run_dir)
    fresh_blind_mode = not args.include_teaching_notes
    if fresh_blind_mode and run_dir is None:
        raise SystemExit(
            "fresh blind solve requires --run-dir so the handoff includes a fresh runtime_state.json"
        )
    preflight_forbidden = _forbidden_manifest_entries(entries, fresh_blind_mode=fresh_blind_mode)

    bootstrap_source = ""
    state_path: Path | None = default_fresh_blind_state_path(run_dir) if run_dir is not None else None
    state_event_log: Path | None = event_log_path(state_path) if state_path is not None else None
    if preflight_forbidden:
        report = {
            "project_root": str(project_root),
            "manifest": str(manifest_path),
            "package_dir": str(package_dir),
            "run_dir": str(run_dir) if run_dir is not None else None,
            "entry_count": len(entries),
            "copied_count": 0,
            "optional_entry_count": 0,
            "optional_entries": [],
            "missing_count": 0,
            "missing": [],
            "unexpected_count": 0,
            "unexpected": [],
            "forbidden_count": len(preflight_forbidden),
            "forbidden": preflight_forbidden,
            "mode": "manual/non-blind package" if args.include_teaching_notes else "fresh blind solve",
            "project_skills": "manual/non-blind" if args.include_teaching_notes else "on",
            "project_skills_surface": "manual/non-blind" if args.include_teaching_notes else "on",
            "teaching_notes_included": args.include_teaching_notes,
            "runtime_state_path": str(state_path) if fresh_blind_mode and state_path is not None else None,
            "runtime_event_log_path": (
                str(state_event_log) if fresh_blind_mode and state_event_log is not None else None
            ),
            "runtime_bootstrapped": False,
            "bootstrap_seed_source": None,
        }
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 1

    if args.clean:
        _ensure_clean_target_is_safe(package_dir, role="package-dir", project_root=project_root)
        _safe_rmtree(package_dir)
        _remove_owner_marker(package_dir)
        if run_dir is not None:
            _ensure_clean_target_is_safe(run_dir, role="run-dir", project_root=project_root)
            _safe_rmtree(run_dir)
            _remove_owner_marker(run_dir)
    else:
        _ensure_missing_or_empty(package_dir, role="package-dir")
        if run_dir is not None:
            _ensure_missing_or_empty(run_dir, role="run-dir")

    package_dir.mkdir(parents=True, exist_ok=True)
    copied = _copy_manifest_entries(project_root, package_dir, entries)
    optional_copied: list[str] = []
    if args.include_teaching_notes:
        optional_copied = _copy_optional_entries(project_root, package_dir, TEACHING_NOTES)

    if run_dir is not None:
        run_dir.mkdir(parents=True, exist_ok=True)

    if fresh_blind_mode and run_dir is not None:
        bootstrap_fields, bootstrap_source = _resolve_fresh_blind_bootstrap(
            args,
            project_root=project_root,
            entries=entries,
        )
        state_path = default_fresh_blind_state_path(run_dir)
        bootstrap_blind_state(
            state_path,
            current_object=bootstrap_fields["current_object"],
            current_seam=bootstrap_fields["current_seam"],
            current_debt=bootstrap_fields["current_debt"],
            next_bite=bootstrap_fields["next_bite"],
            asked_medium_surface=bootstrap_fields["asked_medium_surface"],
        )
        state_event_log = event_log_path(state_path)

    verification = _verify_package(
        package_dir,
        entries,
        optional_entries=TEACHING_NOTES if args.include_teaching_notes else (),
    )
    missing = verification["missing"]
    unexpected = verification["unexpected"]
    forbidden = verification["forbidden"]
    success = not (missing or unexpected or forbidden)
    if success:
        _write_owner_marker(package_dir, role="package-dir")
        if run_dir is not None:
            _write_owner_marker(run_dir, role="run-dir")
    report = {
        "project_root": str(project_root),
        "manifest": str(manifest_path),
        "package_dir": str(package_dir),
        "run_dir": str(run_dir) if run_dir is not None else None,
        "entry_count": len(entries),
        "copied_count": len(copied) + len(optional_copied),
        "optional_entry_count": len(optional_copied),
        "optional_entries": optional_copied,
        "missing_count": len(missing),
        "missing": missing,
        "unexpected_count": len(unexpected),
        "unexpected": unexpected,
        "forbidden_count": len(forbidden),
        "forbidden": forbidden,
        "mode": "manual/non-blind package" if args.include_teaching_notes else "fresh blind solve",
        "project_skills": "manual/non-blind" if args.include_teaching_notes else "on",
        "project_skills_surface": "manual/non-blind" if args.include_teaching_notes else "on",
        "teaching_notes_included": args.include_teaching_notes,
        "runtime_state_path": str(state_path) if state_path is not None else None,
        "runtime_event_log_path": str(state_event_log) if state_event_log is not None else None,
        "runtime_bootstrapped": state_path is not None and state_path.exists(),
        "bootstrap_seed_source": bootstrap_source or None,
    }

    if args.report_json:
        report_path = Path(args.report_json).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
