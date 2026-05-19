import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import runtime_supervision  # noqa: E402
import runtime_consume  # noqa: E402
import runtime_until_done  # noqa: E402
from runtime_state import DEFAULT_STATE  # noqa: E402


class RuntimeUntilDoneTests(unittest.TestCase):
    def _base_state(self) -> dict:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "initial live carrier",
                "current_seam": "initial seam",
                "current_debt": "the current layer is still unfinished",
                "next_bite": "bind the next live bite",
                "asked_medium_surface": "final.md",
                "release_veto": True,
            }
        )
        return state

    def test_until_done_supervisor_can_survive_beyond_small_local_ceiling(self) -> None:
        state = self._base_state()

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            final_path = Path(tmpdir) / "final.md"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            call_count = {"value": 0}

            def fake_run_bind_local_once(
                current_state_path: Path,
                *,
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
                call_count["value"] += 1
                current = json.loads(current_state_path.read_text(encoding="utf-8"))
                if call_count["value"] >= 12:
                    final_path.write_text("# Runtime Solve Steps\n\n1. 完成。\n", encoding="utf-8")
                    current["release_veto"] = False
                    current["bound_program"] = None
                    current["layer_composition_if_any"] = None
                    current["gate_binding_if_any"] = None
                    current["carrier_handoff_if_any"] = None
                    current["primitive_field_if_any"] = None
                    current["primitive_competition_if_any"] = None
                    current["primitive_takeover_gate_if_any"] = None
                    current["landed_next_touch_if_any"] = None
                    current["materialization_evidence"] = {
                        "kind": "file",
                        "location": str(final_path),
                        "summary": "runtime supervisor sealed the asked medium",
                        "skill_serialized": True,
                    }
                    current["output_status"] = {
                        "touched": True,
                        "cosmetic_only": False,
                        "contains_unsupported": False,
                        "contains_placeholder": False,
                        "final_artifact_materialized": True,
                    }
                    current_state_path.write_text(
                        json.dumps(current, ensure_ascii=True, indent=2),
                        encoding="utf-8",
                    )
                    return {"binding_action": "materialize_asked_medium"}, 0

                current["current_object"] = f"carrier_layer_{call_count['value']}"
                current["current_seam"] = f"seam_layer_{call_count['value']}"
                current["current_debt"] = f"debt_layer_{call_count['value']}"
                current["next_bite"] = f"bite_layer_{call_count['value']}"
                current_state_path.write_text(
                    json.dumps(current, ensure_ascii=True, indent=2),
                    encoding="utf-8",
                )
                return {"binding_action": "land_local"}, 0

            def fake_build_inspect_surface(
                current_state_path: Path,
                *,
                allow_autonomous_transition: bool,
            ) -> tuple[dict, int]:
                current = json.loads(current_state_path.read_text(encoding="utf-8"))
                if current.get("release_veto") is False:
                    return {"required_action": "", "binding_action": "release_allowed"}, 0
                return {"required_action": "bind_local", "binding_action": "inspect"}, 1

            with patch(
                "runtime_supervision._load_runtime_consume_entrypoints",
                return_value=(
                    fake_build_inspect_surface,
                    fake_run_bind_local_once,
                    lambda *args, **kwargs: None,
                    lambda *args, **kwargs: ("", ""),
                ),
            ):
                result = runtime_supervision.run_until_done_supervisor(
                    state_path,
                    auto_execute_local=False,
                )

        self.assertTrue(result.completed)
        self.assertEqual(call_count["value"], 12)
        self.assertEqual(result.executed_rounds, 12)
        self.assertEqual(result.reason, "supervisor_completed")

    def test_until_done_supervisor_auto_synthesizes_execute_local_step(self) -> None:
        state = self._base_state()
        state["bound_program"] = {
            "kind": "write",
            "target": "equation ln x=(a-1)x on x>0",
            "operation": "draw the carrier and mark the peak singularity",
            "success_signal": "the peak-controlled carrier is explicit",
            "owner_skill_if_any": "图像",
            "owner_skill_combo_if_any": ["图像", "见证"],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            final_path = Path(tmpdir) / "final.md"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            captured: dict[str, str] = {}

            def fake_run_bind_local_once(
                current_state_path: Path,
                *,
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
                captured["worked_step"] = worked_step or ""
                captured["summary"] = summary or ""
                current = json.loads(current_state_path.read_text(encoding="utf-8"))
                final_path.write_text("# Runtime Solve Steps\n\n1. 完成。\n", encoding="utf-8")
                current["release_veto"] = False
                current["bound_program"] = None
                current["layer_composition_if_any"] = None
                current["materialization_evidence"] = {
                    "kind": "file",
                    "location": str(final_path),
                    "summary": "runtime supervisor sealed the asked medium",
                    "skill_serialized": True,
                }
                current["output_status"] = {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": True,
                }
                current_state_path.write_text(
                    json.dumps(current, ensure_ascii=True, indent=2),
                    encoding="utf-8",
                )
                return {"binding_action": "execute_local"}, 0

            def fake_build_inspect_surface(
                current_state_path: Path,
                *,
                allow_autonomous_transition: bool,
            ) -> tuple[dict, int]:
                current = json.loads(current_state_path.read_text(encoding="utf-8"))
                if current.get("release_veto") is False:
                    return {"required_action": "", "binding_action": "release_allowed"}, 0
                return {"required_action": "execute_local", "binding_action": "inspect"}, 1

            def fake_synthesize_execute_local_worked_step(
                current_state: dict,
                current_report: dict,
                *,
                strict: bool = False,
                prior_refusal_reason: str = "",
            ) -> tuple[str, str]:
                return (
                    "使用 图像 + 见证 在 equation ln x=(a-1)x on x>0 上画出 carrier 并标出峰值奇点。",
                    "图像 接管当前层。",
                )

            with patch(
                "runtime_supervision._load_runtime_consume_entrypoints",
                return_value=(
                    fake_build_inspect_surface,
                    fake_run_bind_local_once,
                    lambda *args, **kwargs: None,
                    fake_synthesize_execute_local_worked_step,
                ),
            ):
                result = runtime_supervision.run_until_done_supervisor(state_path)

        self.assertTrue(result.completed)
        self.assertIn("图像", captured.get("worked_step", ""))
        self.assertIn("equation ln x=(a-1)x on x>0", captured.get("worked_step", ""))
        self.assertIn("图像", captured.get("summary", ""))
        self.assertEqual(result.executed_rounds, 1)

    def test_until_done_supervisor_uses_stagnation_guard_instead_of_small_hard_stop(self) -> None:
        state = self._base_state()

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            def fake_run_bind_local_once(
                current_state_path: Path,
                *,
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
                return {
                    "binding_action": "structural_hop_limit",
                    "reason": "bind_once_structural_hop_limit_reached",
                }, 1

            def fake_build_inspect_surface(
                current_state_path: Path,
                *,
                allow_autonomous_transition: bool,
            ) -> tuple[dict, int]:
                return {"required_action": "bind_local", "binding_action": "inspect"}, 1

            with patch(
                "runtime_supervision._load_runtime_consume_entrypoints",
                return_value=(
                    fake_build_inspect_surface,
                    fake_run_bind_local_once,
                    lambda *args, **kwargs: None,
                    lambda *args, **kwargs: ("", ""),
                ),
            ), patch(
                "runtime_supervision.classify_runtime_blocker",
                side_effect=lambda current_state, current_report, *, required_action, refusal_reason: runtime_supervision.BlockerAssessment(
                    disposition="retryable",
                    code=runtime_supervision.BLOCKER_STRUCTURAL_HOP_LIMIT,
                    refusal_reason=runtime_supervision.normalize_refusal_reason(refusal_reason),
                    snapshot=runtime_supervision.completion_gap_snapshot(current_state, current_report),
                ),
            ):
                result = runtime_supervision.run_until_done_supervisor(
                    state_path,
                    auto_execute_local=False,
                    stagnation_limit=3,
                )

        self.assertFalse(result.completed)
        self.assertIsNotNone(result.blocker)
        self.assertEqual(
            result.blocker.code,
            runtime_supervision.BLOCKER_SUPERVISOR_STAGNATION_GUARD,
        )
        self.assertEqual(result.executed_rounds, 3)

    def test_until_done_supervisor_continues_after_pending_transition_action_payload(self) -> None:
        state = self._base_state()

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            final_path = Path(tmpdir) / "final.md"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            phase = {"value": 0}

            def fake_run_bind_local_once(
                current_state_path: Path,
                *,
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
                current = json.loads(current_state_path.read_text(encoding="utf-8"))

                if phase["value"] == 0:
                    phase["value"] = 1
                    current["current_object"] = "carrier_after_rebind"
                    current["current_seam"] = "execute the rebound bite"
                    current["current_debt"] = "the rebound bite still needs execution"
                    current["next_bite"] = "execute rebound bite"
                    current_state_path.write_text(
                        json.dumps(current, ensure_ascii=True, indent=2),
                        encoding="utf-8",
                    )
                    return {
                        "binding_action": "pending_execute_local",
                        "pending_transition": True,
                        "allowed_transition_surfaces": ["execute_local"],
                        "reason": "active_discipline_contract_requires_runtime_consumption",
                    }, 1

                if phase["value"] == 1:
                    phase["value"] = 2
                    current["current_object"] = "carrier_after_execute"
                    current["current_seam"] = "land the rebound bite"
                    current["current_debt"] = "the executed bite still needs landing"
                    current["next_bite"] = "land rebound bite"
                    current_state_path.write_text(
                        json.dumps(current, ensure_ascii=True, indent=2),
                        encoding="utf-8",
                    )
                    return {
                        "binding_action": "pending_land_local",
                        "pending_transition": True,
                        "allowed_transition_surfaces": ["land_local"],
                        "reason": "active_discipline_contract_requires_runtime_consumption",
                    }, 1

                phase["value"] = 3
                final_path.write_text("# Runtime Solve Steps\n\n1. 完成。\n", encoding="utf-8")
                current["release_veto"] = False
                current["bound_program"] = None
                current["layer_composition_if_any"] = None
                current["gate_binding_if_any"] = None
                current["carrier_handoff_if_any"] = None
                current["primitive_field_if_any"] = None
                current["primitive_competition_if_any"] = None
                current["primitive_takeover_gate_if_any"] = None
                current["landed_next_touch_if_any"] = None
                current["materialization_evidence"] = {
                    "kind": "file",
                    "location": str(final_path),
                    "summary": "runtime supervisor sealed the asked medium",
                    "skill_serialized": True,
                }
                current["output_status"] = {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": True,
                }
                current_state_path.write_text(
                    json.dumps(current, ensure_ascii=True, indent=2),
                    encoding="utf-8",
                )
                return {"binding_action": "materialize_asked_medium"}, 0

            def fake_build_inspect_surface(
                current_state_path: Path,
                *,
                allow_autonomous_transition: bool,
            ) -> tuple[dict, int]:
                current = json.loads(current_state_path.read_text(encoding="utf-8"))
                if current.get("release_veto") is False:
                    return {"required_action": "", "binding_action": "release_allowed"}, 0
                if phase["value"] == 0:
                    return {"required_action": "bind_local", "binding_action": "inspect"}, 1
                if phase["value"] == 1:
                    return {
                        "binding_action": "inspect",
                        "pending_transition": True,
                        "allowed_transition_surfaces": ["execute_local"],
                        "reason": "active_discipline_contract_requires_runtime_consumption",
                    }, 1
                return {
                    "binding_action": "inspect",
                    "pending_transition": True,
                    "allowed_transition_surfaces": ["land_local"],
                    "reason": "active_discipline_contract_requires_runtime_consumption",
                }, 1

            def fake_synthesize_execute_local_worked_step(
                current_state: dict,
                current_report: dict,
                *,
                strict: bool = False,
                prior_refusal_reason: str = "",
            ) -> tuple[str, str]:
                return (
                    "使用 见证 在当前层执行 rebound bite。",
                    "见证层继续向下一 pending action 推进。",
                )

            with patch(
                "runtime_supervision._load_runtime_consume_entrypoints",
                return_value=(
                    fake_build_inspect_surface,
                    fake_run_bind_local_once,
                    lambda *args, **kwargs: None,
                    fake_synthesize_execute_local_worked_step,
                ),
            ):
                result = runtime_supervision.run_until_done_supervisor(state_path)

        self.assertTrue(result.completed)
        self.assertEqual(result.executed_rounds, 3)
        self.assertEqual(result.reason, "supervisor_completed")

    def test_runtime_until_done_parser_accepts_supervisor_bool_flags(self) -> None:
        parser = runtime_until_done.build_parser()
        args = parser.parse_args(
            [
                "state.json",
                "--allow-handoff",
                "--spend-handoff",
                "--allow-rival",
            ]
        )

        self.assertTrue(args.allow_handoff)
        self.assertTrue(args.spend_handoff)
        self.assertTrue(args.allow_rival)

    def test_until_done_supervisor_retries_execute_local_with_strict_step_after_ordinary_fallback_refusal(self) -> None:
        state = self._base_state()

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            final_path = Path(tmpdir) / "final.md"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            phase = {"value": 0}
            strict_flags: list[bool] = []
            refusal_reasons: list[str] = []
            worked_steps: list[str | None] = []

            def fake_run_bind_local_once(
                current_state_path: Path,
                *,
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
                worked_steps.append(worked_step)
                current = json.loads(current_state_path.read_text(encoding="utf-8"))

                if phase["value"] == 0:
                    phase["value"] = 1
                    current_state_path.write_text(
                        json.dumps(current, ensure_ascii=True, indent=2),
                        encoding="utf-8",
                    )
                    return {
                        "binding_action": "execute_local_refused",
                        "reason": (
                            "execute-local refused: ordinary fallback action `分情况` "
                            "regrew inside a live skill-owned layer before the worked step "
                            "challenged it. 当前应先由 `见证` 接管。"
                        ),
                    }, 1

                phase["value"] = 2
                final_path.write_text("# Runtime Solve Steps\n\n1. 严格层成功。\n", encoding="utf-8")
                current["release_veto"] = False
                current["bound_program"] = None
                current["layer_composition_if_any"] = None
                current["gate_binding_if_any"] = None
                current["carrier_handoff_if_any"] = None
                current["primitive_field_if_any"] = None
                current["primitive_competition_if_any"] = None
                current["primitive_takeover_gate_if_any"] = None
                current["landed_next_touch_if_any"] = None
                current["materialization_evidence"] = {
                    "kind": "file",
                    "location": str(final_path),
                    "summary": "strict execute-local sealed the layer",
                    "skill_serialized": True,
                }
                current["output_status"] = {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": True,
                }
                current_state_path.write_text(
                    json.dumps(current, ensure_ascii=True, indent=2),
                    encoding="utf-8",
                )
                return {"binding_action": "materialize_asked_medium"}, 0

            def fake_build_inspect_surface(
                current_state_path: Path,
                *,
                allow_autonomous_transition: bool,
            ) -> tuple[dict, int]:
                current = json.loads(current_state_path.read_text(encoding="utf-8"))
                if current.get("release_veto") is False:
                    return {"required_action": "", "binding_action": "release_allowed"}, 0
                return {"required_action": "execute_local", "binding_action": "inspect"}, 1

            def fake_synthesize_execute_local_worked_step(
                current_state: dict,
                current_report: dict,
                *,
                strict: bool = False,
                prior_refusal_reason: str = "",
            ) -> tuple[str, str]:
                strict_flags.append(strict)
                refusal_reasons.append(prior_refusal_reason)
                if strict:
                    return ("strict current-layer execute step", "strict")
                return ("ordinary execute step", "ordinary")

            with patch(
                "runtime_supervision._load_runtime_consume_entrypoints",
                return_value=(
                    fake_build_inspect_surface,
                    fake_run_bind_local_once,
                    lambda *args, **kwargs: None,
                    fake_synthesize_execute_local_worked_step,
                ),
            ):
                result = runtime_supervision.run_until_done_supervisor(state_path)

        self.assertTrue(result.completed)
        self.assertEqual(strict_flags, [False, True])
        self.assertEqual(
            refusal_reasons,
            [
                "",
                (
                    "execute-local refused: ordinary fallback action `分情况` "
                    "regrew inside a live skill-owned layer before the worked step "
                    "challenged it. 当前应先由 `见证` 接管。"
                ),
            ],
        )
        self.assertEqual(worked_steps, ["ordinary execute step", "strict current-layer execute step"])

    def test_strict_execute_local_synthesis_uses_refusal_reason_to_deny_ordinary_action_and_restore_skill_handoff(self) -> None:
        state = self._base_state()
        state["current_seam"] = "需要给出足够大的可分对族并完成计数下界。"
        state["current_debt"] = "核心是构造两族可分对，并完成当前层计数下界。"
        state["bound_program"] = {
            "kind": "check",
            "target": "需要给出足够大的可分对族并完成计数下界。",
            "operation": "Construct one case, check, or counter-pressure that one route survives and another fails.",
            "success_signal": "见证 on 当前层 changed the current line",
            "owner_skill_if_any": "见证",
            "owner_skill_combo_if_any": ["见证", "状态拆分", "相容"],
        }

        worked_step, summary = runtime_consume.synthesize_execute_local_worked_step(
            state,
            {},
            strict=True,
            prior_refusal_reason=(
                "execute-local refused: ordinary fallback action `分情况` regrew inside a "
                "live skill-owned layer before the worked step challenged it. 应该先让 `状态拆分` "
                "在当前授权触点上真的接管，再决定是否需要后续从属检查。 当前应先由 `见证` 接管。"
            ),
        )

        self.assertIn("先不要 `分情况`", worked_step)
        self.assertIn("先让 `见证`", worked_step)
        self.assertIn("`状态拆分`", worked_step)
        self.assertIn("不单独接管", worked_step)
        self.assertIn("见证 接管", summary)


if __name__ == "__main__":
    unittest.main()
