import copy
import dataclasses
import importlib
import inspect
import sys
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

runtime_consume = importlib.import_module("runtime_consume")
runtime_state = importlib.import_module("runtime_state")

try:
    runtime_supervision = importlib.import_module("runtime_supervision")
except ModuleNotFoundError:
    runtime_supervision = None


DEFAULT_STATE = runtime_state.DEFAULT_STATE
IGNORED_FRONTLOAD_PROBLEM = "bound_program is required while release_veto is active"


def _coerce_mapping(value: object) -> dict:
    if isinstance(value, dict):
        return value
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if hasattr(value, "_asdict"):
        maybe = value._asdict()
        if isinstance(maybe, dict):
            return maybe
    if hasattr(value, "__dict__"):
        return {
            key: current
            for key, current in vars(value).items()
            if not key.startswith("_")
        }
    return {"value": value}


def _lookup_callable(module: object, names: list[str]) -> object | None:
    if module is None:
        return None
    for name in names:
        candidate = getattr(module, name, None)
        if callable(candidate):
            return candidate
    return None


def _invoke_helper(func: object, **available: object) -> object:
    signature = inspect.signature(func)
    positional: list[object] = []
    keyword: dict[str, object] = {}
    for parameter in signature.parameters.values():
        if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
            continue
        if parameter.kind == inspect.Parameter.VAR_KEYWORD:
            for key, value in available.items():
                if key not in keyword:
                    keyword[key] = value
            continue
        if parameter.name in available:
            if parameter.kind == inspect.Parameter.POSITIONAL_ONLY:
                positional.append(available[parameter.name])
            else:
                keyword[parameter.name] = available[parameter.name]
    return func(*positional, **keyword)


def _completion_snapshot(state: dict, report: dict) -> dict:
    helper = _lookup_callable(
        runtime_supervision,
        [
            "completion_gap_snapshot",
            "_completion_gap_snapshot",
            "build_completion_snapshot",
            "build_completion_gap_snapshot",
        ],
    )
    if helper is None:
        return runtime_consume._completion_gap_snapshot(state, report)
    result = _invoke_helper(
        helper,
        state=state,
        report=report,
        completion_report=report,
    )
    return _coerce_mapping(result)


def _classify_blocker(
    *,
    state: dict,
    report: dict,
    required_action: str,
    refusal_reason: str,
) -> dict:
    helper = _lookup_callable(
        runtime_supervision,
        [
            "classify_blocker",
            "classify_runtime_blocker",
            "classify_refusal_blocker",
            "build_blocker_classification",
        ],
    )
    if helper is not None:
        result = _invoke_helper(
            helper,
            state=state,
            report=report,
            required_action=required_action,
            action=required_action,
            refusal_reason=refusal_reason,
            reason=refusal_reason,
            problems=report.get("problems", []),
            transition_history=[],
        )
        return _coerce_mapping(result)

    normalized_reason = runtime_consume._normalize_refusal_reason(refusal_reason)
    problems = [
        problem
        for problem in report.get("problems", [])
        if problem != IGNORED_FRONTLOAD_PROBLEM
    ]
    retryable = runtime_consume._continuable_refusal_reason(normalized_reason) and not problems
    return {
        "required_action": required_action,
        "refusal_reason": normalized_reason,
        "retryable": retryable,
        "terminal": not retryable,
        "classification": "retryable_stall" if retryable else "terminal_invalid_state",
        "problems": problems,
    }


def _continuation_budget(state: dict, report: dict, *, required_action: str) -> int:
    helper = _lookup_callable(
        runtime_supervision,
        [
            "continuation_round_budget",
            "_continuation_round_budget",
            "continuation_budget",
            "build_continuation_budget",
        ],
    )
    if helper is None:
        result = runtime_consume._continuation_round_budget(
            state,
            report,
            required_action=required_action,
        )
    else:
        snapshot = _completion_snapshot(state, report)
        result = _invoke_helper(
            helper,
            state=state,
            report=report,
            completion_snapshot=snapshot,
            snapshot=snapshot,
            required_action=required_action,
            action=required_action,
        )

    if isinstance(result, int):
        return result
    mapped = _coerce_mapping(result)
    for key in [
        "budget",
        "round_budget",
        "continuation_budget",
        "max_rounds",
        "max_possible_continuation_rounds",
    ]:
        value = mapped.get(key)
        if isinstance(value, int):
            return value
    raise AssertionError(f"Could not read continuation budget from {mapped!r}")


def _is_retryable(classification: dict) -> bool:
    if classification.get("retryable") is True or classification.get("can_retry") is True:
        return True
    for key in ["classification", "kind", "mode", "disposition", "status"]:
        value = classification.get(key)
        if isinstance(value, str):
            normalized = value.lower()
            if any(marker in normalized for marker in ["retryable", "reopen", "continue"]):
                return True
    return False


def _is_terminal(classification: dict) -> bool:
    if classification.get("terminal") is True or classification.get("is_terminal") is True:
        return True
    for key in ["classification", "kind", "mode", "disposition", "status"]:
        value = classification.get(key)
        if isinstance(value, str):
            normalized = value.lower()
            if any(marker in normalized for marker in ["terminal", "invalid", "dead_end", "stop"]):
                return True
    return False


def _live_state() -> dict:
    state = copy.deepcopy(DEFAULT_STATE)
    state.update(
        {
            "current_object": "same carrier still owns the blocker",
            "current_seam": "the current layer has not closed yet",
            "current_debt": "the supervised gap is still live",
            "next_bite": "bind one sharper witness on the current layer",
            "asked_medium_surface": "answer.md",
            "release_veto": True,
        }
    )
    return state


def _live_report(*, supervisory_pressure: bool = False, thinner_reopen: bool = False) -> dict:
    report = {
        "problems": [],
        "resume_bridge": {
            "explicit_gap": "the supervised gap is still live",
            "next_local_choice": "bind one sharper witness on the current layer",
            "known_object": "same carrier still owns the blocker",
            "ask_surface": "answer.md",
            "same_carrier_preferred": not thinner_reopen,
        },
        "control_signals": {
            "meta_controls": {},
            "micro_control_surface": {},
        },
        "layer_composition": {
            "active": True,
            "surface": "current_layer",
        },
    }
    if thinner_reopen:
        report["resume_bridge"]["mode"] = "reopen_on_thinner_carrier"
    if supervisory_pressure:
        report["control_signals"]["meta_controls"] = {
            "god_view": {"active": True},
            "supervisory_pulse": {"active": True},
        }
    return report


def _blocker_context(required_action: str, *, problems: list[str] | None = None) -> tuple[dict, dict]:
    state = _live_state()
    report = _live_report()
    report["problems"] = list(problems or [])

    if required_action == "land_local":
        state["bound_program"] = {
            "kind": "check",
            "target": "same carrier still owns the blocker",
            "operation": "push the blocker to one honest boundary case",
            "success_signal": "the blocker is decided there",
            "owner_skill_if_any": "极限边界",
            "owner_skill_combo_if_any": ["极限边界", "见证"],
        }
        state["output_status"] = {
            "touched": True,
            "cosmetic_only": False,
            "contains_unsupported": False,
            "contains_placeholder": False,
            "final_artifact_materialized": False,
        }
        report["layer_composition"] = {
            "active": True,
            "surface": "bound_program",
        }
    elif required_action == "spend_local":
        state["carrier_handoff_if_any"] = {
            "trigger": "thinner_carrier_handoff",
            "to_object": "thinner signed-gap seam",
            "winning_pressure": "the thinner carrier now owns the next bite",
            "why_local": "same-carrier continuation stays too thick",
            "warm_field": {
                "active_pressures": ["projection"],
                "cheap_check": "touch the thinner carrier directly",
                "evidence_basis": "cheap_check",
            },
        }
        report["layer_composition"] = {
            "active": True,
            "surface": "carrier_handoff",
        }

    return state, report


class RuntimeSupervisionTests(unittest.TestCase):
    def test_completion_snapshot_detects_unfinished_live_gap(self) -> None:
        state = _live_state()
        state["output_status"] = {
            "touched": True,
            "cosmetic_only": False,
            "contains_unsupported": False,
            "contains_placeholder": False,
            "final_artifact_materialized": False,
        }
        snapshot = _completion_snapshot(
            state,
            _live_report(supervisory_pressure=True),
        )

        self.assertTrue(snapshot.get("task_incomplete"))
        self.assertEqual(snapshot.get("explicit_gap"), "the supervised gap is still live")
        self.assertEqual(
            snapshot.get("next_local_choice"),
            "bind one sharper witness on the current layer",
        )
        self.assertTrue(snapshot.get("supervisor_active"))

    def test_blocker_classifier_marks_bind_spend_and_land_stalls_as_retryable(self) -> None:
        cases = [
            (
                "bind_local",
                "bind-local refused: no unique local bite became concrete enough to bind",
            ),
            (
                "spend_local",
                "spend-local refused: no unique thinner-carrier handoff is concrete enough",
            ),
            (
                "land_local",
                "land-local refused: next same-carrier layer is identical to the current one",
            ),
        ]

        for required_action, refusal_reason in cases:
            with self.subTest(required_action=required_action):
                state, report = _blocker_context(required_action)
                classification = _classify_blocker(
                    state=state,
                    report=report,
                    required_action=required_action,
                    refusal_reason=refusal_reason,
                )

                self.assertTrue(classification, msg=required_action)
                self.assertTrue(_is_retryable(classification), msg=classification)
                self.assertFalse(_is_terminal(classification), msg=classification)

    def test_blocker_classifier_treats_invalid_state_problems_as_terminal(self) -> None:
        invalid_problem = "gate_binding_if_any requires a bound_program on the same carrier"
        state, report = _blocker_context("bind_local", problems=[invalid_problem])
        classification = _classify_blocker(
            state=state,
            report=report,
            required_action="bind_local",
            refusal_reason=(
                "bind-local refused: state has blocking problems: "
                + invalid_problem
            ),
        )

        self.assertTrue(_is_terminal(classification), msg=classification)
        self.assertFalse(_is_retryable(classification), msg=classification)

    def test_continuation_budget_grows_with_supervisory_pressure_land_local_and_thinner_reopen(self) -> None:
        baseline_state = _live_state()
        baseline_report = _live_report()
        baseline_budget = _continuation_budget(
            baseline_state,
            baseline_report,
            required_action="bind_local",
        )

        supervisory_budget = _continuation_budget(
            baseline_state,
            _live_report(supervisory_pressure=True),
            required_action="bind_local",
        )
        land_state, land_report = _blocker_context("land_local")
        land_budget = _continuation_budget(
            land_state,
            land_report,
            required_action="land_local",
        )
        thinner_budget = _continuation_budget(
            baseline_state,
            _live_report(thinner_reopen=True),
            required_action="bind_local",
        )

        self.assertGreater(supervisory_budget, baseline_budget)
        self.assertGreater(land_budget, baseline_budget)
        self.assertGreater(thinner_budget, baseline_budget)


if __name__ == "__main__":
    unittest.main()
