import argparse
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

from runtime_guard import (  # noqa: E402
    build_problem_born_touch_for_skill,
    _sanitize_public_skill_competition,
    _sanitize_public_skill_field,
    _sanitize_public_skill_lighting_surface,
    build_report,
    canonicalize_skill_token,
    derive_control_bridge,
    derive_controller_trigger_surface,
    derive_first_layer_arena,
    derive_layer_arena,
    derive_bound_program_candidate,
    derive_interlayer_discharge_bridge,
    derive_local_skill_coaching_surface,
    derive_problem_skill_frontload,
    infer_primitives_from_text,
    derive_primitive_field_candidate,
    derive_primitive_program_candidate,
    derive_self_check_agenda,
    derive_skill_authority_bridge,
    derive_skill_competition,
    derive_skill_lighting_surface,
    program_has_meta_narration,
    projected_gain_profile_for_skill,
    program_is_direct_closure_like,
    state_has_explicit_local_ownership_evidence,
    expected_layer_object,
)
from runtime_state import (  # noqa: E402
    _display_supporting_skills,
    _explicit_layer_composition_from_event,
    _skill_composition_step_refusals,
    _solve_trace_export_allowed,
    bootstrap_blind_state,
    canonical_asked_medium_materialization_text,
    DEFAULT_STATE,
    append_runtime_event,
    apply_same_carrier_landing,
    build_layer_composition_state_payload,
    build_parser,
    build_runtime_evidence,
    build_runtime_evidence_refusal_payload,
    command_bind_local,
    command_bootstrap_blind,
    command_check,
    command_competition,
    command_evidence,
    command_land_local,
    command_execute_local,
    command_materialize_asked_medium,
    command_init,
    command_program,
    command_set_core,
    command_set_output,
    command_trace,
    first_entry_asked_medium_short_circuit_refusal,
    finalize_materialized_closure,
    fresh_blind_same_carrier_first_entry,
    is_generic_runtime_operation,
    load_runtime_events,
    materialize_asked_medium_if_ready,
    mutate_state,
    normalize_direct_asked_medium_closure_owner,
    same_carrier_landing_is_ready,
    has_runtime_owned_asked_medium_materialization,
    pending_runtime_execution_contract,
    promote_report_derived_exact_closure,
    read_skill_authority_program,
    render_runtime_skill_trace_markdown,
    render_runtime_solve_steps_markdown,
    solve_trace_markdown_path,
)
from runtime_consume import (  # noqa: E402
    autonomous_transition_pressure,
    build_inspect_surface,
    cool_shortcut_fields,
    run_bind_local_once,
    stalled_runtime_continuation,
    write_trace_output,
)
from runtime_next_touch import build_consumption as build_next_touch_consumption  # noqa: E402
from runtime_controller import build_controller_读出  # noqa: E402


class RuntimeGuardTests(unittest.TestCase):
    def _append_bind_step_event(
        self,
        state_path: Path,
        *,
        combo: list[str],
        materialized: bool = False,
        target: str = "focus seam",
        debt: str = "tighten the current layer",
    ) -> None:
        after = copy.deepcopy(DEFAULT_STATE)
        before = copy.deepcopy(DEFAULT_STATE)
        before.update(
            {
                "current_object": "broad carrier",
                "current_seam": "broad carrier",
                "current_debt": "separate one honest seam from the carrier",
                "next_bite": "bind one local bite",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )
        after.update(
            {
                "current_object": "focused seam object",
                "current_seam": target,
                "current_debt": debt,
                "next_bite": "bind one local bite",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": target,
                    "operation": "check the current seam directly",
                    "success_signal": "the seam is narrowed",
                    "owner_skill_if_any": combo[0] if combo else "",
                    "owner_skill_combo_if_any": combo[:],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "focused seam object",
                    "controlled_object": target,
                    "current_seam": target,
                    "current_debt": debt,
                    "reason": "one local bite is explicitly bound on the live layer",
                    "leading_skill_if_any": combo[0] if combo else "",
                    "event_owned": True,
                    "transition_change": "bound one local runtime bite",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": combo[:],
                    "authorized_bite": {
                        "kind": "check",
                        "target": target,
                        "operation": "check the current seam directly",
                        "success_signal": "the seam is narrowed",
                        "owner_skill_if_any": combo[0] if combo else "",
                        "owner_skill_combo_if_any": combo[:],
                    },
                    "next_local_choice": "next exact relation",
                    "gap_object": debt,
                    "lighting_if_any": {
                        "lit_skill_if_any": combo[0] if combo else "",
                        "candidate_skills_if_any": combo[:],
                        "supporting_skills_if_any": combo[1:],
                        "verify_touch_if_any": {"target": target, "kind": "check"},
                        "role_split_if_any": {
                            "primary_skill_if_any": combo[0] if combo else "",
                            "supporting_skills_if_any": combo[1:],
                            "check_kind_if_any": "check",
                            "check_target_if_any": target,
                            "ordinary_operations_are_not_skills": True,
                        },
                    },
                },
            }
        )
        if materialized:
            after["output_status"] = {
                "touched": True,
                "cosmetic_only": False,
                "contains_unsupported": False,
                "contains_placeholder": False,
                "final_artifact_materialized": True,
            }
            after["materialization_evidence"] = {
                "kind": "artifact",
                "location": "answer.md",
                "summary": "answer.md is materialized",
            }
        append_runtime_event(
            state_path,
            command_name="bind-local",
            before=before,
            after=after,
        )

    def test_handoff_candidate_does_not_require_probe_secondary_binding(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "carrier",
                "current_debt": "debt",
                "next_bite": "bite",
                "asked_medium_surface": "medium",
                "release_veto": True,
            }
        )
        handoff = {
            "trigger": "same_carrier_change",
            "from_slot": "solve",
            "to_object": "thinner",
            "winning_pressure": "pressure",
            "why_local": "why",
            "warm_field": {
                "active_pressures": ["check"],
                "cheap_check": "touch thinner",
                "evidence_basis": "cheap_check",
            },
        }

        candidate = derive_primitive_field_candidate(state, [], handoff_override=handoff)

        self.assertIsInstance(candidate, dict)
        self.assertEqual(candidate.get("layer_object"), "thinner")
        self.assertTrue(candidate.get("active_primitives"))

    def test_skill_lighting_surface_tracks_first_takeover_and_verification(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "f(x)",
                "asked_medium_surface": "single_variable_function",
            }
        )

        lighting = derive_skill_lighting_surface(
            state,
            [],
            skill_field_override={
                "active_skills": ["图像", "见证", "读出"],
            },
            skill_competition_override={
                "winning_skill_if_any": "图像",
                "winning_projected_gain_reason": "it gets closest to the current-layer target fastest",
                "candidates": [
                    {
                        "skill": "图像",
                        "projected_gain_rank": 1,
                        "projected_gain_reason": "it gets closest to the current-layer target fastest",
                    },
                    {
                        "skill": "读出",
                        "projected_gain_rank": 4,
                        "projected_gain_reason": "it is downstream of the 图像 rather than first takeover",
                    },
                ],
            },
            probe_discipline_override={
                "probe_must_bind": True,
                "preferred_probe_target": "f(x)",
                "allowed_probe_kinds": ["check"],
            },
            self_check_agenda_override={
                "touch_target": "f(x)",
                "preferred_kinds": ["check"],
            },
        )

        self.assertIsInstance(lighting, dict)
        self.assertEqual(lighting.get("lit_skill_if_any"), "图像")
        self.assertIn("见证", lighting.get("supporting_skills_if_any", []))
        self.assertEqual(lighting.get("false_first_skill_if_any"), "读出")
        self.assertEqual(lighting.get("verify_touch_if_any", {}).get("kind"), "check")
        self.assertTrue(lighting.get("ordinary_operations_are_not_skills"))

    def test_skill_lighting_role_split_exposes_explicit_check_skill(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "函数图像",
                "current_seam": "比较边界方向是否翻转",
                "current_debt": "先让图像接管，再用边界检查稳住判断",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        lighting = derive_skill_lighting_surface(
            state,
            [],
            skill_field_override={
                "active_skills": ["图像", "极限边界", "对称"],
                "authority_skill_if_any": "图像",
            },
            skill_competition_override={
                "winning_skill_if_any": "图像",
                "winning_projected_gain_reason": "图像最接近当前层目标",
                "candidates": [
                    {
                        "skill": "图像",
                        "projected_gain_rank": 1,
                        "projected_gain_reason": "图像最接近当前层目标",
                    },
                    {
                        "skill": "极限边界",
                        "projected_gain_rank": 2,
                        "projected_gain_reason": "边界检查用来稳住图像判断",
                    },
                ],
            },
            probe_discipline_override={
                "preferred_probe_target": "比较边界方向是否翻转",
                "allowed_probe_kinds": ["check"],
            },
            self_check_agenda_override={
                "touch_target": "比较边界方向是否翻转",
                "preferred_kinds": ["check"],
            },
        )

        role_split = lighting.get("role_split_if_any", {})
        self.assertEqual(role_split.get("primary_skill_if_any"), "图像")
        self.assertEqual(role_split.get("check_skill_if_any"), "极限边界")
        self.assertEqual(role_split.get("check_kind_if_any"), "check")

    def test_skill_lighting_keeps_broad_candidate_field_after_open_competition(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "f(x)",
                "current_seam": "graph skeleton",
                "current_debt": "decide the honest first layer",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        lighting = derive_skill_lighting_surface(
            state,
            [],
            skill_field_override={
                "active_skills": ["图像", "投影", "读出"],
                "authority_skill_if_any": "图像",
            },
            skill_competition_override={
                "winning_skill_if_any": "见证",
                "winning_projected_gain_reason": "cheap probe can touch the seam",
                "candidates": [
                    {
                        "skill": "见证",
                        "projected_gain_rank": 1,
                        "projected_gain_reason": "cheap probe can touch the seam",
                    },
                    {
                        "skill": "图像",
                        "projected_gain_rank": 2,
                        "projected_gain_reason": "graph skeleton carries the real layer",
                    },
                ],
            },
            probe_discipline_override={
                "active_skill_hypothesis": "图像",
                "active_skill_hypotheses": ["图像", "投影"],
                "preferred_probe_target": "f(x)",
                "allowed_probe_kinds": ["check"],
            },
            self_check_agenda_override={
                "touch_target": "f(x)",
                "preferred_kinds": ["check"],
            },
        )

        self.assertIsInstance(lighting, dict)
        self.assertEqual(lighting.get("lit_skill_if_any"), "图像")
        self.assertIn("图像", lighting.get("candidate_skills_if_any", []))
        self.assertIn("投影", lighting.get("candidate_skills_if_any", []))
        self.assertIn("见证", lighting.get("candidate_skills_if_any", []))
        self.assertGreaterEqual(len(lighting.get("candidate_skills_if_any", [])), 4)
        self.assertEqual(lighting.get("supporting_skills_if_any"), ["投影", "读出", "见证"])
        self.assertEqual(lighting.get("comparison_skill_if_any"), "投影")
        self.assertIn("not a required order", lighting.get("anti_pipeline_note", ""))

    def test_skill_competition_preserves_open_candidates_beyond_lit_shortlist(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "function carrier",
                "current_seam": "graph skeleton",
                "current_debt": "decide the live graph route",
                "next_bite": "draw before 读出",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        competition = derive_skill_competition(
            state,
            [],
            primitive_field_override={
                "layer_object": "function carrier",
                "active_primitives": ["见证"],
                "why_now": "cheap probe pressure is live",
                "selection_basis": "lexical_hint",
                "evidence_basis": "lexical_hint",
            },
            control_signals_override={
                "meta_controls": {},
                "micro_control_surface": {},
                "layerwise_reselection_pressure": {
                    "active": True,
                    "wake_skills": ["图像", "赋值"],
                    "reason": "the layer is still too thick to let a probe own it",
                    "direct_closure_allowed": False,
                },
                "composition_pressure": {},
            },
            skill_field_override={
                "active_skills": ["图像", "赋值"],
                "authority_skill_if_any": "图像",
            },
            lit_candidate_override=["图像", "赋值"],
        )

        self.assertIsInstance(competition, dict)
        self.assertEqual(competition.get("lit_candidate_skills_if_any"), ["图像", "赋值"])
        self.assertIn(competition.get("winning_skill_if_any"), {"图像", "赋值"})
        self.assertEqual(competition.get("competition_basis"), "projected_gain_first_takeover")
        self.assertGreater(len(competition.get("coactive_skills_if_any", [])), 2)
        self.assertIn("读出", competition.get("coactive_skills_if_any", []))
        self.assertIn("极限边界", competition.get("coactive_skills_if_any", []))
        candidate_skills = [
            canonicalize_skill_token(candidate.get("skill"))
            for candidate in competition.get("candidates", [])
            if isinstance(candidate, dict)
        ]
        self.assertIn("图像", candidate_skills)
        self.assertIn("赋值", candidate_skills)
        self.assertGreaterEqual(len(set(candidate_skills)), 2)

    def test_layer_composition_persists_minimal_lighting_surface(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state["current_object"] = "f(x)"

        payload = build_layer_composition_state_payload(
            state,
            surface="bound_program",
            authorized_bite={
                "kind": "check",
                "target": "f(x)",
                "operation": "sketch the monotonic 图像",
                "owner_skill_if_any": "图像",
                "owner_skill_combo_if_any": ["图像", "见证"],
            },
            skill_winner="图像",
            skill_combo=["图像", "见证"],
            lighting_if_any={
                "lit_skill_if_any": "图像",
                "candidate_skills_if_any": ["图像", "见证"],
                "supporting_skills_if_any": ["check"],
                "verify_touch_if_any": {"target": "f(x)", "kind": "check"},
                "role_split_if_any": {
                    "primary_skill_if_any": "图像",
                    "supporting_skills_if_any": ["见证"],
                    "check_kind_if_any": "check",
                    "check_target_if_any": "f(x)",
                    "ordinary_operations_are_not_skills": True,
                },
            },
        )

        self.assertIsInstance(payload, dict)
        self.assertEqual(payload.get("lighting_if_any", {}).get("lit_skill_if_any"), "图像")
        self.assertEqual(
            payload.get("lighting_if_any", {}).get("candidate_skills_if_any"),
            ["图像", "见证"],
        )
        self.assertEqual(
            payload.get("lighting_if_any", {}).get("supporting_skills_if_any"),
            ["见证"],
        )
        self.assertEqual(
            payload.get("lighting_if_any", {}).get("role_split_if_any", {}).get("check_target_if_any"),
            "f(x)",
        )
        self.assertEqual(
            payload.get("lighting_if_any", {}).get("verify_touch_if_any", {}).get("kind"),
            "check",
        )
        self.assertTrue(
            payload.get("lighting_if_any", {}).get("ordinary_operations_are_not_skills")
        )

    def test_layer_composition_uses_program_metadata_for_object_transition(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "thick carrier",
                "current_seam": "compressed parity ledger",
                "current_debt": "compare three front-prefix families",
            }
        )

        payload = build_layer_composition_state_payload(
            state,
            surface="bound_program",
            authorized_bite={
                "kind": "write",
                "target": "compressed parity ledger",
                "operation": "project thick carrier onto one compressed parity ledger",
                "owner_skill_if_any": "投影",
                "owner_skill_combo_if_any": ["投影", "状态拆分"],
                "current_layer_object_if_any": "thick carrier",
                "controlled_object_if_any": "compressed parity ledger",
                "object_transform_if_any": "投影 rewrites `thick carrier` toward `compressed parity ledger`",
                "next_object_if_any": "compare three front-prefix families",
                "step_outline_if_any": "use `投影` on `compressed parity ledger` to move from `thick carrier` to `compressed parity ledger`, then continue on `compare three front-prefix families`",
                "skill_phase_if_any": "structural_rewrite",
            },
            skill_winner="投影",
            skill_combo=["投影", "状态拆分"],
        )

        self.assertIsInstance(payload, dict)
        self.assertEqual(payload.get("controlled_object"), "compressed parity ledger")
        self.assertEqual(payload.get("next_local_choice"), "compare three front-prefix families")
        self.assertNotIn("current_layer_object_if_any", payload)
        authorized = payload.get("authorized_bite", {})
        self.assertEqual(authorized.get("current_layer_object_if_any"), "thick carrier")
        self.assertIn("投影 rewrites", authorized.get("object_transform_if_any", ""))
        self.assertEqual(authorized.get("skill_phase_if_any"), "structural_rewrite")

    def test_same_carrier_landing_persists_takeover_layer_composition(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "carrier",
                "current_seam": "carrier",
                "current_debt": "tighten seam",
                "next_bite": "make one same-carrier structural move",
                "asked_medium_surface": "answer",
                "bound_program": {
                    "kind": "check",
                    "target": "carrier",
                    "operation": "take the 对称-revealing slice",
                    "success_signal": "carrier changes shape",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            apply_same_carrier_landing(
                state,
                state_path,
                next_object="carrier_thinner",
                next_seam="carrier_thinner",
                next_debt="new local seam",
                next_bite="bind the thinner carrier",
            )

        layer = state.get("layer_composition_if_any")
        self.assertIsInstance(layer, dict)
        self.assertEqual(layer.get("surface"), "takeover_recomposition")
        self.assertTrue(layer.get("leading_skill_if_any"))
        self.assertEqual(
            layer.get("authorized_bite", {}).get("owner_skill_if_any"),
            layer.get("leading_skill_if_any"),
        )

    def test_same_carrier_landing_can_rebuild_owned_touch_from_current_layer_skill_bridge(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "old object",
                "current_seam": "old seam",
                "current_debt": "old debt",
                "next_bite": "old bite",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": "old seam",
                    "operation": "use one structural move",
                    "success_signal": "object changes",
                    "owner_skill_if_any": "状态拆分",
                    "owner_skill_combo_if_any": ["状态拆分", "相容", "投影"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            apply_same_carrier_landing(
                state,
                state_path,
                next_object="已知函数 f_a(x)=x+lnx-ax 的零点结构",
                next_seam="先把参数 a 赋到一条单独载体上再看峰值奇点",
                next_debt="不要先做普通导数分类；先看 a=1+(lnx)/x 这条载体上的峰值和端点奇点",
                next_bite="先赋值成 a=1+(lnx)/x 再画出载体骨架",
            )

        layer = state.get("layer_composition_if_any")
        landed_touch = state.get("landed_next_touch_if_any")
        self.assertIsInstance(layer, dict)
        self.assertIsInstance(landed_touch, dict)
        self.assertEqual(layer.get("surface"), "takeover_recomposition")
        self.assertTrue(layer.get("leading_skill_if_any"))
        self.assertNotEqual(layer.get("leading_skill_if_any"), "状态拆分")
        self.assertEqual(
            layer.get("authorized_bite", {}).get("owner_skill_if_any"),
            layer.get("leading_skill_if_any"),
        )
        self.assertEqual(
            landed_touch.get("owner_skill_if_any"),
            layer.get("leading_skill_if_any"),
        )
        self.assertTrue(layer.get("active_skill_combo_if_any"))
        self.assertNotEqual(layer.get("authorized_bite", {}).get("target"), "answer.md")

    def test_event_layer_reads_missing_next_choice_from_after_state(self) -> None:
        event = {
            "report_excerpt": {
                "layer_composition": {
                    "event_owned": True,
                    "surface": "takeover_recomposition",
                    "layer_object": "thin carrier",
                    "controlled_object": "thin carrier",
                    "current_debt": "close the remaining local gap",
                    "reason": "same-carrier landing tightened the object",
                    "transition_change": "landed one touch and reopened the next local layer",
                    "active_skill_combo_if_any": ["图像", "投影"],
                }
            },
            "after": {
                "asked_medium_surface": "answer.md",
                "layer_composition_if_any": {
                    "event_owned": True,
                    "surface": "takeover_recomposition",
                    "layer_object": "thin carrier",
                    "controlled_object": "thin carrier",
                    "current_debt": "close the remaining local gap",
                    "reason": "same-carrier landing tightened the object",
                    "transition_change": "landed one touch and reopened the next local layer",
                    "next_local_choice": "remaining local gap on thin carrier",
                    "active_skill_combo_if_any": ["图像", "投影"],
                },
            },
        }

        layer = _explicit_layer_composition_from_event(event)

        self.assertIsInstance(layer, dict)
        self.assertEqual(
            layer.get("next_local_choice"),
            "remaining local gap on thin carrier",
        )
        self.assertNotIn(
            "recomposition did not expose the next local object or gap",
            _skill_composition_step_refusals(event),
        )

    def test_append_runtime_event_rewrites_official_solve_trace(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "carrier",
                "current_seam": "carrier",
                "current_debt": "find the first controlled slice",
                "next_bite": "bind the first local bite",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            solve_path = solve_trace_markdown_path(state_path)
            solve_path.write_text("handwritten ordinary solve trace\n", encoding="utf-8")

            append_runtime_event(
                state_path,
                command_name="bootstrap-blind",
                before=None,
                after=state,
                note="fresh blind bootstrap",
            )

            self.assertEqual(
                solve_path.read_text(encoding="utf-8"),
                render_runtime_solve_steps_markdown(state_path),
            )
            self.assertNotIn(
                "handwritten ordinary solve trace",
                solve_path.read_text(encoding="utf-8"),
            )

    def test_solve_trace_refuses_materialized_answer_with_mixed_runtime_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(DEFAULT_STATE, ensure_ascii=True, indent=2), encoding="utf-8")
            self._append_bind_step_event(state_path, combo=["图像"], materialized=False, target="premature seam")
            self._append_bind_step_event(
                state_path,
                combo=["图像", "见证"],
                materialized=True,
                target="stable seam",
                debt="cash the stable seam into answer.md",
            )
            final_state = copy.deepcopy(DEFAULT_STATE)
            final_state["output_status"] = {
                "touched": True,
                "cosmetic_only": False,
                "contains_unsupported": False,
                "contains_placeholder": False,
                "final_artifact_materialized": True,
            }
            final_state["materialization_evidence"] = {
                "kind": "artifact",
                "location": "answer.md",
                "summary": "answer.md is materialized",
            }
            state_path.write_text(json.dumps(final_state, ensure_ascii=True, indent=2), encoding="utf-8")

            output_path = Path(tmpdir) / "solve.md"
            rc = command_trace(
                argparse.Namespace(
                    state_file=str(state_path),
                    format="solve-markdown",
                    output=str(output_path),
                )
            )
            rendered = render_runtime_solve_steps_markdown(state_path)

            self.assertEqual(rc, 1)
            self.assertIn(
                "Runtime refusal: existing runtime skill/layer evidence does not justify exporting solve-markdown.",
                rendered,
            )

    def test_skill_trace_refuses_mixed_runtime_steps_even_if_answer_is_materialized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(DEFAULT_STATE, ensure_ascii=True, indent=2), encoding="utf-8")
            self._append_bind_step_event(state_path, combo=["图像"], materialized=False, target="premature seam")
            self._append_bind_step_event(
                state_path,
                combo=["图像", "见证"],
                materialized=True,
                target="stable seam",
                debt="cash the stable seam into answer.md",
            )
            final_state = copy.deepcopy(DEFAULT_STATE)
            final_state["output_status"] = {
                "touched": True,
                "cosmetic_only": False,
                "contains_unsupported": False,
                "contains_placeholder": False,
                "final_artifact_materialized": True,
            }
            final_state["materialization_evidence"] = {
                "kind": "artifact",
                "location": "answer.md",
                "summary": "answer.md is materialized",
            }
            state_path.write_text(json.dumps(final_state, ensure_ascii=True, indent=2), encoding="utf-8")

            output_path = Path(tmpdir) / "skill.md"
            rc = command_trace(
                argparse.Namespace(
                    state_file=str(state_path),
                    format="skill-markdown",
                    output=str(output_path),
                )
            )
            rendered = render_runtime_skill_trace_markdown(state_path)

        self.assertEqual(rc, 1)
        self.assertIn(
            "Runtime refusal: this event did not qualify as a genuine skill-owned runtime step.",
            rendered,
        )

    def test_solve_trace_refuses_mixed_runtime_steps_without_materialized_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(DEFAULT_STATE, ensure_ascii=True, indent=2), encoding="utf-8")
            self._append_bind_step_event(state_path, combo=["图像"], materialized=False, target="premature seam")
            self._append_bind_step_event(
                state_path,
                combo=["图像", "见证"],
                materialized=False,
                target="stable seam",
                debt="cash the stable seam into answer.md",
            )
            state_path.write_text(json.dumps(DEFAULT_STATE, ensure_ascii=True, indent=2), encoding="utf-8")

            output_path = Path(tmpdir) / "solve.md"
            rc = command_trace(
                argparse.Namespace(
                    state_file=str(state_path),
                    format="solve-markdown",
                    output=str(output_path),
                )
            )
            rendered = render_runtime_solve_steps_markdown(state_path)

            self.assertEqual(rc, 1)
            self.assertIn(
                "Runtime refusal: existing runtime skill/layer evidence does not justify exporting solve-markdown.",
                rendered,
            )
            self.assertIn("Qualified runtime step count: `1`.", rendered)

    def test_solve_trace_export_refuses_when_asked_medium_closure_is_still_pending(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "three solved subresults now only need exact closure",
                "current_seam": "write the already-solved proof into final.md without reopening ordinary derivation",
                "current_debt": "materialize the exact asked medium honestly",
                "next_bite": "seal final.md from the live closure carrier",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "final.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by the solved carrier",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "图像", "见证"],
                },
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": False,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "精确封口",
                    "reason": "exact closure now owns one local touch and should keep foreground authority until asked-medium contact changes",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "final.md",
                        "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by the solved carrier",
                        "success_signal": "asked_medium_is_exact_and_executable",
                        "owner_skill_if_any": "精确封口",
                        "owner_skill_combo_if_any": ["精确封口", "图像", "见证"],
                    },
                    "layer_object": "three solved subresults now only need exact closure",
                    "controlled_object": "final.md",
                    "current_seam": "write the already-solved proof into final.md without reopening ordinary derivation",
                    "current_debt": "materialize the exact asked medium honestly",
                    "next_local_choice": "final.md",
                    "transition_change": "bound write on final.md",
                    "active_skill_combo_if_any": ["精确封口", "图像", "见证"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            self._append_bind_step_event(
                state_path,
                combo=["图像", "见证"],
                materialized=False,
                target="already solved seam",
                debt="the old structural layer already landed",
            )

            self.assertFalse(
                _solve_trace_export_allowed(state_path, load_runtime_events(state_path))
            )

    def test_solve_trace_refuses_without_runtime_events_even_if_answer_is_materialized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state["output_status"] = {
                "touched": True,
                "cosmetic_only": False,
                "contains_unsupported": False,
                "contains_placeholder": False,
                "final_artifact_materialized": True,
            }
            state["materialization_evidence"] = {
                "kind": "artifact",
                "location": "answer.md",
                "summary": "answer.md is materialized",
            }
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            output_path = Path(tmpdir) / "solve.md"
            rc = command_trace(
                argparse.Namespace(
                    state_file=str(state_path),
                    format="solve-markdown",
                    output=str(output_path),
                )
            )
            rendered = render_runtime_solve_steps_markdown(state_path)

            self.assertEqual(rc, 1)
            self.assertEqual(
                rendered,
                "# Runtime Solve Steps\n\nNo runtime events were captured for this state file.\n",
            )

    def test_bootstrap_blind_refuses_non_pathlike_asked_medium_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"

            with self.assertRaises(SystemExit) as ctx:
                command_bootstrap_blind(
                    argparse.Namespace(
                        state_file=str(state_path),
                        current_object="solve object",
                        current_seam="solve object",
                        current_debt="close the final answer",
                        next_bite="materialize the final answer",
                        asked_medium_surface="在 run 目录 materialize 为 answer.md 与 verdict.md，并保留 runtime sidecars",
                        revocation_handle="runtime_state",
                        uncertainty_mode="local_competition",
                        primary_slot="solve",
                    )
                )

            self.assertIn(
                "asked-medium surface must name one concrete markdown artifact",
                str(ctx.exception),
            )
            self.assertFalse(state_path.exists())

    def test_trace_refuses_json_output_to_asked_medium_in_fresh_blind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "asked_medium_surface": "answer.md",
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_trace(
                    argparse.Namespace(
                        state_file=str(state_path),
                        format="json",
                        output="answer.md",
                    )
                )

            self.assertIn(
                "fresh blind asked medium may only be written from canonical solve-markdown export",
                str(ctx.exception),
            )
            self.assertFalse((Path(tmpdir) / "answer.md").exists())

    def test_trace_refuses_unexportable_solve_markdown_to_asked_medium_in_fresh_blind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "asked_medium_surface": "answer.md",
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_trace(
                    argparse.Namespace(
                        state_file=str(state_path),
                        format="solve-markdown",
                        output="answer.md",
                    )
                )

            self.assertIn(
                "fresh blind asked medium still lacks exact closure ownership",
                str(ctx.exception),
            )
            self.assertFalse((Path(tmpdir) / "answer.md").exists())

    def test_trace_allows_canonical_solve_markdown_to_asked_medium_in_fresh_blind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "asked_medium_surface": "answer.md",
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                    "bound_program": {
                        "kind": "write",
                        "target": "answer.md",
                        "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by the live closure",
                        "success_signal": "asked_medium_is_exact_and_executable",
                        "owner_skill_if_any": "见证",
                        "owner_skill_combo_if_any": ["见证", "读出"],
                    },
                    "output_status": {
                        "touched": True,
                        "cosmetic_only": False,
                        "contains_unsupported": False,
                        "contains_placeholder": False,
                        "final_artifact_materialized": False,
                    },
                    "release_veto": True,
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            canonical_text = "# Runtime Solve Steps\n\n1. canonical.\n"
            with (
                patch("runtime_state._solve_trace_export_allowed", return_value=True),
                patch("runtime_state.render_runtime_solve_steps_markdown", return_value=canonical_text),
            ):
                rc = command_trace(
                    argparse.Namespace(
                        state_file=str(state_path),
                        format="solve-markdown",
                        output="answer.md",
                    )
                )

            self.assertEqual(rc, 0)
            self.assertEqual(
                (Path(tmpdir) / "answer.md").read_text(encoding="utf-8"),
                canonical_text,
            )
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertTrue(
                loaded_state.get("output_status", {}).get("final_artifact_materialized")
            )
            self.assertTrue(
                loaded_state.get("materialization_evidence", {}).get("skill_serialized")
            )

    def test_trace_solve_markdown_to_asked_medium_refuses_without_exact_closure_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "current_object": "blind package handoff completeness for gaokao 2026 math final",
                    "current_seam": "missing math prompt inside the packaged readset",
                    "current_debt": "the allowed blind readset contains runtime/docs/tools but no problem statement",
                    "next_bite": "check the readset boundary exactly once",
                    "asked_medium_surface": "final.md",
                    "release_veto": True,
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                    "bound_program": {
                        "kind": "check",
                        "target": "missing math prompt inside the packaged readset",
                        "operation": "push the blocker to one honest boundary case",
                        "success_signal": "the blocker is decided there",
                        "owner_skill_if_any": "极限边界",
                        "owner_skill_combo_if_any": ["极限边界", "图像"],
                    },
                    "output_status": {
                        "touched": True,
                        "cosmetic_only": False,
                        "contains_unsupported": False,
                        "contains_placeholder": False,
                        "final_artifact_materialized": False,
                    },
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            append_runtime_event(
                state_path,
                command_name="execute-local",
                before=copy.deepcopy(DEFAULT_STATE),
                after=state,
            )

            canonical_text = "# Runtime Solve Steps\n\n1. blocker.\n"
            with (
                patch("runtime_state._solve_trace_export_allowed", return_value=True),
                patch("runtime_state.render_runtime_solve_steps_markdown", return_value=canonical_text),
            ):
                with self.assertRaises(SystemExit) as ctx:
                    command_trace(
                        argparse.Namespace(
                            state_file=str(state_path),
                            format="solve-markdown",
                            output="final.md",
                        )
                    )

            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertIn("fresh blind asked medium still lacks exact closure ownership", str(ctx.exception))
            self.assertFalse((Path(tmpdir) / "final.md").exists())
            self.assertFalse(has_runtime_owned_asked_medium_materialization(loaded_state))
            self.assertFalse(loaded_state.get("output_status", {}).get("final_artifact_materialized"))
            self.assertEqual(load_runtime_events(state_path)[-1].get("command"), "execute-local")

    def test_runtime_evidence_refusal_payload_keeps_skill_lighting_surface(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            payload = build_runtime_evidence_refusal_payload(
                state_path,
                discipline_contract={},
                resume_bridge={},
                warnings=[],
                surface_payload={
                    "skill_lighting_surface": {
                        "lit_skill_if_any": "图像",
                        "verify_touch_if_any": {"target": "f(x)", "kind": "check"},
                    }
                },
            )

        self.assertEqual(
            payload.get("skill_lighting_surface", {}).get("lit_skill_if_any"),
            "图像",
        )
        self.assertIs(payload.get("ok"), False)
        self.assertIs(payload.get("refused"), True)
        self.assertIs(payload.get("delivery_veto"), True)

    def test_trace_refuses_verdict_output_in_fresh_blind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "asked_medium_surface": "answer.md",
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_trace(
                    argparse.Namespace(
                        state_file=str(state_path),
                        format="markdown",
                        output="verdict.md",
                    )
                )

            self.assertIn(
                "fresh blind final deliverable `verdict.md` must stay runtime-derived",
                str(ctx.exception),
            )
            self.assertFalse((Path(tmpdir) / "verdict.md").exists())

    def test_execute_local_refuses_verdict_output_in_fresh_blind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "asked_medium_surface": "answer.md",
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                    "bound_program": {
                        "kind": "check",
                        "target": "focus seam",
                        "operation": "check the focus seam",
                    },
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_execute_local(
                    argparse.Namespace(
                        state_file=str(state_path),
                        worked_step="图像：先固定当前局部对象。\n",
                        summary="sealed one local step",
                        output_file="verdict.md",
                        cosmetic_only=None,
                        contains_unsupported=None,
                        contains_placeholder=None,
                    )
                )

            self.assertIn(
                "fresh blind final deliverable `verdict.md` must stay runtime-derived",
                str(ctx.exception),
            )
            self.assertFalse((Path(tmpdir) / "verdict.md").exists())

    def test_execute_local_refuses_custom_markdown_output_in_fresh_blind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "asked_medium_surface": "final.md",
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                    "bound_program": {
                        "kind": "check",
                        "target": "focus seam",
                        "operation": "check the focus seam",
                    },
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_execute_local(
                    argparse.Namespace(
                        state_file=str(state_path),
                        worked_step="图像：先固定当前局部对象。\n",
                        summary="sealed one local step",
                        output_file="custom.md",
                        cosmetic_only=None,
                        contains_unsupported=None,
                        contains_placeholder=None,
                    )
                )

            self.assertIn(
                "fresh blind generic markdown outputs must stay on the canonical asked-medium",
                str(ctx.exception),
            )
            self.assertFalse((Path(tmpdir) / "custom.md").exists())

    def test_trace_refuses_custom_markdown_output_in_fresh_blind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "asked_medium_surface": "final.md",
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_trace(
                    argparse.Namespace(
                        state_file=str(state_path),
                        format="markdown",
                        output="custom.md",
                    )
                )

            self.assertIn(
                "fresh blind generic markdown outputs must stay on the canonical asked-medium",
                str(ctx.exception),
            )
            self.assertFalse((Path(tmpdir) / "custom.md").exists())

    def test_runtime_consume_trace_output_refuses_custom_markdown_in_fresh_blind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "asked_medium_surface": "final.md",
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                write_trace_output(state_path, "custom.md")

            self.assertIn(
                "fresh blind generic markdown outputs must stay on the canonical asked-medium",
                str(ctx.exception),
            )
            self.assertFalse((Path(tmpdir) / "custom.md").exists())

    def test_runtime_consume_trace_output_allows_canonical_trace_sidecar_in_fresh_blind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "asked_medium_surface": "final.md",
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            output_path = state_path.with_name("runtime_trace.md")
            write_trace_output(state_path, output_path.name)

            self.assertTrue(output_path.exists())
            self.assertIn("No runtime events were captured", output_path.read_text(encoding="utf-8"))

    def test_next_touch_invalid_state_payload_marks_delivery_veto(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(
                json.dumps(copy.deepcopy(DEFAULT_STATE), ensure_ascii=True, indent=2),
                encoding="utf-8",
            )

            payload, exit_code = build_next_touch_consumption(state_path)

        self.assertEqual(exit_code, 2)
        self.assertEqual(payload.get("reason"), "invalid_state")
        self.assertIs(payload.get("ok"), False)
        self.assertIs(payload.get("refused"), True)
        self.assertIs(payload.get("delivery_veto"), True)

    def test_controller_invalid_state_payload_marks_delivery_veto(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(
                json.dumps(copy.deepcopy(DEFAULT_STATE), ensure_ascii=True, indent=2),
                encoding="utf-8",
            )

            payload, exit_code = build_controller_读出(state_path)

        self.assertEqual(exit_code, 2)
        self.assertEqual(payload.get("reason"), "invalid_state")
        self.assertIs(payload.get("ok"), False)
        self.assertIs(payload.get("refused"), True)
        self.assertIs(payload.get("delivery_veto"), True)

    def test_layer_composition_payload_preserves_lighting_candidates_and_roles(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state["current_object"] = "carrier"
        payload = build_layer_composition_state_payload(
            state,
            surface="bound_program",
            authorized_bite={
                "kind": "check",
                "target": "thinner carrier",
                "operation": "project the solid into the controlling section",
                "success_signal": "the controlling section is explicit",
                "owner_skill_if_any": "投影",
                "owner_skill_combo_if_any": ["投影", "见证"],
            },
            skill_winner="投影",
            skill_combo=["投影", "见证"],
            layer_object="carrier",
            controlled_object="thinner carrier",
            current_seam="controlling section",
            current_debt="cut to the honest slice",
            next_local_choice="projected center geometry",
            gap_object="projected center geometry",
            transition_change="bound one section-owned touch",
            lighting_if_any={
                "lit_skill_if_any": "投影",
                "candidate_skills_if_any": ["投影", "见证", "读出"],
                "comparison_skill_if_any": "见证",
                "supporting_skills_if_any": ["见证"],
                "verify_touch_if_any": {"target": "thinner carrier", "kind": "check"},
                "role_split_if_any": {
                    "primary_skill_if_any": "投影",
                    "supporting_skills_if_any": ["见证"],
                    "check_kind_if_any": "check",
                    "check_target_if_any": "thinner carrier",
                    "ordinary_operations_are_not_skills": True,
                },
                "ability_branch_if_any": {
                    "support_operation_is_subordinate": True,
                },
                "competition_basis": "projected_gain_first_takeover",
            },
        )

        lighting = payload.get("lighting_if_any", {})
        self.assertEqual(payload.get("active_skill_combo_if_any"), ["投影", "见证"])
        self.assertEqual(lighting.get("candidate_skills_if_any"), ["投影", "见证", "读出"])
        self.assertEqual(lighting.get("comparison_skill_if_any"), "见证")
        self.assertEqual(
            lighting.get("role_split_if_any", {}).get("primary_skill_if_any"),
            "投影",
        )
        self.assertEqual(
            lighting.get("role_split_if_any", {}).get("check_target_if_any"),
            "thinner carrier",
        )
        self.assertTrue(lighting.get("ordinary_operations_are_not_skills"))

    def test_layer_composition_promotes_supporting_skills_from_lighting_when_owner_combo_is_singleton(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state["current_object"] = "ball-center carrier"

        payload = build_layer_composition_state_payload(
            state,
            surface="bound_program",
            authorized_bite={
                "kind": "check",
                "target": "joint feasibility window",
                "operation": "check whether the local constraints are jointly compatible",
                "owner_skill_if_any": "相容",
                "owner_skill_combo_if_any": ["相容"],
            },
            skill_winner="相容",
            skill_combo=["相容"],
            lighting_if_any={
                "lit_skill_if_any": "相容",
                "candidate_skills_if_any": ["极限边界", "状态拆分", "相容", "见证", "对称"],
                "supporting_skills_if_any": ["状态拆分", "见证", "对称"],
                "verify_touch_if_any": {"target": "joint feasibility window", "kind": "check"},
                "role_split_if_any": {
                    "primary_skill_if_any": "相容",
                    "supporting_skills_if_any": ["状态拆分", "见证", "对称"],
                    "check_kind_if_any": "check",
                    "check_target_if_any": "joint feasibility window",
                    "ordinary_operations_are_not_skills": True,
                },
            },
        )

        self.assertIsInstance(payload, dict)
        self.assertEqual(
            payload.get("active_skill_combo_if_any"),
            ["相容", "状态拆分", "见证", "对称"],
        )
        self.assertEqual(
            payload.get("lighting_if_any", {}).get("supporting_skills_if_any"),
            ["状态拆分", "见证", "对称"],
        )

    def test_skill_refusal_requires_lit_candidates_and_verification_roles(self) -> None:
        event = {
            "command": "bind-local",
            "before": {
                "current_object": "thick carrier",
                "asked_medium_surface": "answer.md",
            },
            "after": {
                "current_object": "thinner carrier",
                "asked_medium_surface": "answer.md",
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "active_skill_combo_if_any": ["投影", "见证"],
                    "event_owned": True,
                    "leading_skill_if_any": "投影",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "projected center geometry",
                        "operation": "project to the controlling slice",
                        "success_signal": "the slice owns the decisive distance",
                        "owner_skill_if_any": "投影",
                        "owner_skill_combo_if_any": ["投影", "见证"],
                    },
                    "layer_object": "thinner carrier",
                    "controlled_object": "projected center geometry",
                    "current_seam": "projected center geometry",
                    "current_debt": "cut to the honest slice",
                    "next_local_choice": "projected center geometry",
                    "gap_object": "projected center geometry",
                    "transition_change": "bound one section-owned touch",
                    "lighting_if_any": {
                        "lit_skill_if_any": "投影",
                        "supporting_skills_if_any": ["见证"],
                    },
                },
            },
            "report_excerpt": {},
        }

        refusals = _skill_composition_step_refusals(event)

        self.assertIn("no candidate skill field was ever lit before the owned bite", refusals)
        self.assertIn("current-layer roles never exposed any supporting skills", refusals)
        self.assertIn("current-layer roles never exposed a concrete verification touch", refusals)

    def test_skill_refusal_blocks_generic_write_answer_without_closure_owner(self) -> None:
        event = {
            "command": "bind-local",
            "before": {
                "current_object": "equation carrier",
                "asked_medium_surface": "answer.md",
            },
            "after": {
                "current_object": "equation carrier",
                "asked_medium_surface": "answer.md",
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "active_skill_combo_if_any": ["图像", "读出"],
                    "event_owned": True,
                    "leading_skill_if_any": "图像",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "answer.md",
                        "operation": "write the final answer directly",
                        "success_signal": "answer is present",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "读出"],
                    },
                    "layer_object": "equation carrier",
                    "controlled_object": "answer.md",
                    "current_seam": "final write",
                    "current_debt": "close the argument",
                    "next_local_choice": "answer.md",
                    "gap_object": "close the argument",
                    "transition_change": "bound the final write",
                    "lighting_if_any": {
                        "lit_skill_if_any": "图像",
                        "candidate_skills_if_any": ["图像", "读出"],
                        "supporting_skills_if_any": ["读出"],
                        "role_split_if_any": {
                            "primary_skill_if_any": "图像",
                            "supporting_skills_if_any": ["读出"],
                            "check_kind_if_any": "check",
                            "check_target_if_any": "answer.md",
                            "ordinary_operations_are_not_skills": True,
                        },
                    },
                },
            },
            "report_excerpt": {},
        }

        refusals = _skill_composition_step_refusals(event)

        self.assertIn(
            "write reached the asked medium before a real closure owner took control",
            refusals,
        )

    def test_skill_refusal_allows_asked_medium_write_when_real_combo_contains_readout(self) -> None:
        event = {
            "command": "bind-local",
            "before": {
                "current_object": "mirror-witness carrier",
                "asked_medium_surface": "final.md",
            },
            "after": {
                "current_object": "mirror-witness carrier",
                "asked_medium_surface": "final.md",
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "active_skill_combo_if_any": ["见证", "读出", "图像"],
                    "event_owned": True,
                    "leading_skill_if_any": "见证",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "final.md",
                        "operation": "seal the exact answer from the mirror-witness layer",
                        "success_signal": "asked_medium_is_exact_and_executable",
                        "owner_skill_if_any": "见证",
                        "owner_skill_combo_if_any": ["见证", "读出", "图像"],
                    },
                    "layer_object": "mirror-witness carrier",
                    "controlled_object": "final.md",
                    "current_seam": "the right same-height point must lie beyond the log mirror",
                    "current_debt": "finish the mirror witness and close the answer",
                    "next_local_choice": "final.md",
                    "gap_object": "finish the mirror witness and close the answer",
                    "transition_change": "bound the final write",
                    "lighting_if_any": {
                        "lit_skill_if_any": "见证",
                        "candidate_skills_if_any": ["见证", "图像", "投影", "读出"],
                        "supporting_skills_if_any": ["图像", "投影"],
                        "role_split_if_any": {
                            "primary_skill_if_any": "见证",
                            "supporting_skills_if_any": ["图像", "投影"],
                            "check_kind_if_any": "check",
                            "check_target_if_any": "the right same-height point must lie beyond the log mirror",
                            "ordinary_operations_are_not_skills": True,
                        },
                    },
                },
            },
            "report_excerpt": {},
        }

        refusals = _skill_composition_step_refusals(event)

        self.assertNotIn(
            "write reached the asked medium before a real closure owner took control",
            refusals,
        )

    def test_skill_refusal_blocks_图像_led_closure_decision_lane(self) -> None:
        event = {
            "command": "bind-local",
            "before": {
                "current_object": "quadratic carrier",
                "asked_medium_surface": "answer.md",
            },
            "after": {
                "current_object": "quadratic carrier",
                "asked_medium_surface": "answer.md",
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "active_skill_combo_if_any": ["图像", "极限边界", "读出"],
                    "event_owned": True,
                    "leading_skill_if_any": "图像",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "the feasible root must satisfy 0<r<=4 and exclude the oversized root",
                        "operation": "draw the final root-selection 图像",
                        "success_signal": "the admissible root is fixed",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "极限边界", "读出"],
                    },
                    "layer_object": "quadratic carrier",
                    "controlled_object": "feasible root selection",
                    "current_seam": "exclude the oversized root",
                    "current_debt": "select the admissible root and close the answer",
                    "next_local_choice": "feasible root selection",
                    "gap_object": "select the admissible root and close the answer",
                    "transition_change": "bound the closure decision lane",
                    "lighting_if_any": {
                        "lit_skill_if_any": "精确封口",
                        "candidate_skills_if_any": ["精确封口", "图像", "极限边界", "读出"],
                        "supporting_skills_if_any": ["图像", "极限边界", "读出"],
                        "role_split_if_any": {
                            "primary_skill_if_any": "精确封口",
                            "supporting_skills_if_any": ["图像", "极限边界", "读出"],
                            "check_kind_if_any": "check",
                            "check_target_if_any": "feasible root selection",
                            "ordinary_operations_are_not_skills": True,
                        },
                    },
                },
            },
            "report_excerpt": {},
        }

        refusals = _skill_composition_step_refusals(event)

        self.assertIn(
            "closure-decision layer kept a carrier or 读出 skill in front after a real closure skill was already lit",
            refusals,
        )

    def test_skill_refusal_blocks_reopened_layer_closure_before_object_change(self) -> None:
        event = {
            "command": "land-local",
            "before": {
                "current_object": "thin ledger",
                "asked_medium_surface": "answer.md",
                "bound_program": {
                    "kind": "check",
                    "target": "thin ledger",
                    "operation": "spend one exact local bite on the thin ledger",
                    "success_signal": "thin ledger changed",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "精确封口"],
                },
            },
            "after": {
                "current_object": "thinner local seam",
                "asked_medium_surface": "answer.md",
                "layer_composition_if_any": {
                    "surface": "takeover_recomposition",
                    "active_skill_combo_if_any": ["精确封口", "极限边界"],
                    "event_owned": True,
                    "leading_skill_if_any": "精确封口",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "answer.md",
                        "operation": "seal the answer immediately",
                        "success_signal": "answer closed",
                        "owner_skill_if_any": "精确封口",
                        "owner_skill_combo_if_any": ["精确封口", "极限边界"],
                    },
                    "layer_object": "thinner local seam",
                    "controlled_object": "remaining gap on thin ledger",
                    "current_seam": "remaining gap on thin ledger",
                    "current_debt": "close one remaining gap before final writeout",
                    "reason": "the current object changed but still exposes one unresolved thin-layer gap",
                    "next_local_choice": "remaining gap on thin ledger",
                    "gap_object": "close one remaining gap before final writeout",
                    "transition_change": "reopened one thinner local layer",
                    "lighting_if_any": {
                        "lit_skill_if_any": "精确封口",
                        "candidate_skills_if_any": ["精确封口", "极限边界"],
                        "supporting_skills_if_any": ["极限边界"],
                        "role_split_if_any": {
                            "primary_skill_if_any": "精确封口",
                            "supporting_skills_if_any": ["极限边界"],
                            "check_kind_if_any": "check",
                            "check_target_if_any": "remaining gap on thin ledger",
                            "ordinary_operations_are_not_skills": True,
                        },
                    },
                },
            },
            "report_excerpt": {},
        }

        refusals = _skill_composition_step_refusals(event)

        self.assertIn(
            "reopened layer tried to close on the asked medium before the new current object was spent",
            refusals,
        )

    def test_land_local_same_carrier_tightening_is_a_qualified_reopened_change(self) -> None:
        event = {
            "command": "land-local",
            "before": {
                "current_object": "thin ledger",
                "current_seam": "thin ledger",
                "current_debt": "old local debt",
                "next_bite": "old local bite",
                "asked_medium_surface": "answer.md",
                "bound_program": {
                    "kind": "check",
                    "target": "thin ledger",
                    "operation": "push one exact boundary on the thin ledger",
                    "success_signal": "the live seam tightens",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "见证"],
                },
            },
            "after": {
                "current_object": "thin ledger",
                "current_seam": "remaining exact seam on thin ledger",
                "current_debt": "bind the remaining exact seam before final closure",
                "next_bite": "rebind the remaining exact seam on thin ledger",
                "asked_medium_surface": "answer.md",
                "layer_composition_if_any": {
                    "surface": "takeover_recomposition",
                    "active_skill_combo_if_any": ["极限边界", "见证"],
                    "event_owned": True,
                    "leading_skill_if_any": "极限边界",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "thin ledger",
                        "operation": "push one exact boundary on the reopened seam",
                        "success_signal": "the remaining seam becomes explicit",
                        "owner_skill_if_any": "极限边界",
                        "owner_skill_combo_if_any": ["极限边界", "见证"],
                    },
                    "layer_object": "thin ledger",
                    "controlled_object": "thin ledger",
                    "current_seam": "remaining exact seam on thin ledger",
                    "current_debt": "bind the remaining exact seam before final closure",
                    "reason": "same-carrier landing tightened the live seam without changing the outer carrier name",
                    "next_local_choice": "thin ledger",
                    "gap_object": "bind the remaining exact seam before final closure",
                    "transition_change": "landed one exact boundary and reopened the remaining seam on the same carrier",
                    "lighting_if_any": {
                        "lit_skill_if_any": "极限边界",
                        "candidate_skills_if_any": ["极限边界", "见证"],
                        "supporting_skills_if_any": ["见证"],
                        "verify_touch_if_any": {
                            "target": "thin ledger",
                            "kind": "check",
                        },
                        "role_split_if_any": {
                            "primary_skill_if_any": "极限边界",
                            "supporting_skills_if_any": ["见证"],
                            "check_kind_if_any": "check",
                            "check_target_if_any": "thin ledger",
                            "ordinary_operations_are_not_skills": True,
                        },
                    },
                },
            },
            "report_excerpt": {},
        }

        refusals = _skill_composition_step_refusals(event)

        self.assertNotIn("land-local never changed the current mathematical object", refusals)
        self.assertNotIn(
            "recomposition never emitted a controller beyond the previous object",
            refusals,
        )

    def test_program_direct_closure_like_requires_exact_operation_and_owner(self) -> None:
        self.assertFalse(
            program_is_direct_closure_like(
                {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "write the final answer directly",
                    "owner_skill_if_any": "图像",
                },
                asked_medium="answer.md",
            )
        )
        self.assertTrue(
            program_is_direct_closure_like(
                {
                    "kind": "读出",
                    "target": "answer.md",
                    "operation": "materialize_exact_asked_medium_读出",
                    "owner_skill_if_any": "读出",
                },
                asked_medium="answer.md",
            )
        )

    def test_fresh_blind_first_touch_keeps_agenda_on_problem_layer(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes",
                "next_bite": "draw the carrier before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        agenda = derive_self_check_agenda(state, [])

        self.assertIsInstance(agenda, dict)
        self.assertNotEqual(agenda.get("focus"), "asked_medium")
        self.assertEqual(agenda.get("touch_target"), "equation ln x=(a-1)x on x>0")

    def test_fresh_blind_expected_layer_object_ignores_asked_medium_short_circuit(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes",
                "next_bite": "draw the carrier before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        layer_object = expected_layer_object(
            state,
            agenda_override={
                "focus": "asked_medium",
                "touch_target": "solve_writeup.md",
                "preferred_kinds": ["write", "读出"],
            },
        )

        self.assertEqual(layer_object, "equation ln x=(a-1)x on x>0")

    def test_fresh_blind_primitive_field_does_not_collapse_to_artifact(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        primitive_field = derive_primitive_field_candidate(state, [])

        self.assertIsInstance(primitive_field, dict)
        self.assertEqual(
            primitive_field.get("layer_object"),
            "equation ln x=(a-1)x on x>0",
        )
        self.assertNotEqual(primitive_field.get("tie_break_check"), "solve_writeup.md")

    def test_fresh_blind_bound_program_stays_off_asked_medium_on_first_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        program = derive_bound_program_candidate(state, [])

        self.assertIsInstance(program, dict)
        self.assertNotEqual(program.get("target"), "solve_writeup.md")

    def test_first_entry_refuses_probe_bound_on_asked_medium(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes",
                "next_bite": "draw the carrier before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        refusal = first_entry_asked_medium_short_circuit_refusal(
            {
                "kind": "check",
                "target": "solve_writeup.md",
                "operation": "run one separating 见证 on solve_writeup.md",
                "owner_skill_if_any": "见证",
                "owner_skill_combo_if_any": ["见证", "读出"],
            },
            {},
            state=state,
            winning_skill="见证",
        )

        self.assertIn("problem-facing probe/check tried to bind directly on the asked medium", refusal)

    def test_pending_bound_program_refuses_runtime_consume_inspect_surface(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            command_bind_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "previous_state": None,
                        "allow_handoff": False,
                        "allow_rival": False,
                    },
                )()
            )
            payload, exit_code = build_inspect_surface(state_path)

        self.assertIn(exit_code, {1, 2})
        if payload.get("pending_transition"):
            self.assertEqual(payload.get("reason"), "active_discipline_contract_requires_runtime_consumption")
            authorized_target = payload.get("authorized_bite_if_any", {}).get("target")
        elif isinstance(payload.get("bound_program"), dict):
            authorized_target = payload.get("bound_program", {}).get("target")
            self.assertEqual(authorized_target, "equation ln x=(a-1)x on x>0")
        self.assertNotIn("resume_bridge", payload)
        self.assertNotIn("closure_nucleus", payload)

    def test_fresh_blind_initial_report_projects_first_touch_contract_and_layer(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "fresh_blind_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {
                    "mode": "fresh_blind_project_skills_on",
                    "auto_enter_local_action_when_concrete": False,
                },
            }
        )

        report = build_report(state, Path("dummy_state.json"))
        contract = report.get("discipline_contract", {})
        layer = report.get("layer_composition", {})

        self.assertTrue(contract.get("active"))
        self.assertEqual(contract.get("surface"), "fresh_blind_first_touch")
        self.assertEqual(contract.get("must_bind_local_bite"), True)
        self.assertIsInstance(contract.get("authorized_bite"), dict)
        self.assertTrue(layer.get("active"))
        self.assertEqual(layer.get("surface"), "fresh_blind_first_touch")
        self.assertEqual(layer.get("event_owned"), False)
        self.assertGreaterEqual(len(layer.get("active_skill_combo_if_any", [])), 2)

    def test_fresh_blind_initial_report_keeps_broad_lighting_and_same_carrier_ownership(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "IOI 2024 Hieroglyphs: universal common subsequence under subsequence order",
                "current_seam": "all common subsequences must fit inside one common super-container U that is itself common",
                "current_debt": "find a thinner carrier that decides whether one universal common subsequence exists or non-existence is forced",
                "next_bite": "externalize the structure that controls all common subsequences without route leakage",
                "asked_medium_surface": "final.md",
                "revocation_handle": "fresh_blind_hieroglyphs_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {
                    "mode": "fresh_blind_project_skills_on",
                    "auto_enter_local_action_when_concrete": False,
                },
            }
        )

        with patch(
            "runtime_guard._sanitize_public_skill_competition",
            side_effect=lambda payload: payload,
        ):
            report = build_report(state, Path("dummy_state.json"))
        contract = report.get("discipline_contract", {})
        layer = report.get("layer_composition", {})
        lighting = report.get("skill_lighting_surface", {})

        self.assertIn(
            "bound_program is required while release_veto is active",
            report.get("problems", []),
        )
        self.assertTrue(contract.get("active"))
        self.assertEqual(contract.get("surface"), "fresh_blind_first_touch")
        self.assertEqual(contract.get("must_bind_local_bite"), True)
        self.assertIsInstance(contract.get("authorized_bite"), dict)
        self.assertTrue(layer.get("active"))
        self.assertEqual(layer.get("surface"), "fresh_blind_first_touch")
        self.assertEqual(layer.get("event_owned"), False)
        self.assertGreaterEqual(len(layer.get("active_skill_combo_if_any", [])), 2)
        self.assertIsInstance(lighting, dict)
        self.assertIn(lighting.get("lit_skill_if_any"), lighting.get("candidate_skills_if_any", []))
        self.assertGreaterEqual(len(lighting.get("candidate_skills_if_any", [])), 4)
        self.assertGreaterEqual(len(lighting.get("supporting_skills_if_any", [])), 3)
        self.assertEqual(
            contract.get("authorized_bite", {}).get("owner_skill_combo_if_any"),
            layer.get("active_skill_combo_if_any"),
        )
        self.assertIn("not a required order", lighting.get("anti_pipeline_note", ""))

    def test_fresh_blind_initial_report_does_not_frontload_generic_runtime_shell(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "fresh blind package run in isolated directory",
                "current_seam": "fresh blind package run in isolated directory",
                "current_debt": "produce one honest runtime transition and validate the current contract surface without reading forbidden package history",
                "next_bite": "bind one local runtime-owned verification bite inside this run directory",
                "asked_medium_surface": "final.md",
                "revocation_handle": "runtime_shell_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {
                    "mode": "fresh_blind_project_skills_on",
                    "auto_enter_local_action_when_concrete": False,
                },
            }
        )

        report = build_report(state, Path("dummy_state.json"))

        self.assertEqual(report.get("problems"), ["bound_program is required while release_veto is active"])
        self.assertFalse(report.get("discipline_contract"))
        self.assertFalse(report.get("skill_lighting_surface"))
        self.assertFalse(report.get("first_layer_arena"))

    def test_fresh_blind_initial_report_does_not_frontload_meta_process_narration(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "need a thinner carrier before ordinary continuation",
                "current_seam": "rewrite the live burden on one thinner carrier",
                "current_debt": "need an exact structural criterion before ordinary continuation regrows",
                "next_bite": "stay on the thinner carrier and do not close early",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "meta_process_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {
                    "mode": "fresh_blind_project_skills_on",
                    "auto_enter_local_action_when_concrete": False,
                },
            }
        )

        report = build_report(state, Path("dummy_state.json"))

        self.assertEqual(report.get("problems"), ["bound_program is required while release_veto is active"])
        self.assertFalse(report.get("discipline_contract"))
        self.assertFalse(report.get("skill_lighting_surface"))
        self.assertFalse(report.get("first_layer_arena"))

    def test_chinese_function_text_frontloads_multiple_project_skills(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "已知 f(x)=ln((x^2-x+ax+b)/(x-1)^3)，且 b=0, f'(x)≥0，求 a 的最小值",
                "current_seam": "参数下界是不是来自导数符号核的边界刚好饱和",
                "current_debt": "不要先把整道导数题完全铺开；只找真正控制单调性的符号核，并盯住参数 a 的下界是否由刚好饱和的边界条件决定",
                "next_bite": "先压缩出控制 f'(x) 符号的核心表达式，检查最小 a 是否对应某个边界刚好取到，而不是先做整套求导化简",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        competition = derive_skill_competition(state, [])

        self.assertIsInstance(competition, dict)
        candidate_skills = [
            canonicalize_skill_token(candidate.get("skill"))
            for candidate in competition.get("candidates", [])
            if isinstance(candidate, dict)
        ]
        self.assertIn("图像", candidate_skills)
        self.assertIn("极限边界", candidate_skills)
        self.assertGreaterEqual(len(set(candidate_skills)), 4)
        self.assertNotEqual(competition.get("winning_skill_if_any"), "读出")

    def test_chinese_grouping_text_frontloads_structure_skills(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "2024新高考I卷第19题：可分数列里删去两项后还能分组",
                "current_seam": "删去两项后可分性是否等价于一个精确覆盖约束",
                "current_debt": "不要先暴力枚举所有删法和分组；先看删去两项后可分条件是否形成一一覆盖或精确覆盖结构",
                "next_bite": "先把元素与分组约束画成覆盖关系，检查是不是每个位置只会被一种删法和一种配对结构解释",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        competition = derive_skill_competition(state, [])

        self.assertIsInstance(competition, dict)
        candidate_skills = [
            canonicalize_skill_token(candidate.get("skill"))
            for candidate in competition.get("candidates", [])
            if isinstance(candidate, dict)
        ]
        self.assertIn("状态拆分", candidate_skills)
        self.assertIn("相容", candidate_skills)
        self.assertIn("投影", candidate_skills)

    def test_public_skill_competition_exposes_projected_progress_percent(self) -> None:
        payload = {
            "winning_skill_if_any": "守恒",
            "winning_projected_gain_rank": 1,
            "candidates": [
                {
                    "skill": "守恒",
                    "projected_gain_rank": 1,
                    "projected_gain_reason": "it gets closest to the current-layer target fastest",
                },
                {
                    "skill": "对称",
                    "projected_gain_rank": 4,
                    "projected_gain_reason": "it can simplify the layer, but not as decisively",
                },
            ],
        }

        sanitized = _sanitize_public_skill_competition(payload)

        self.assertEqual(
            sanitized.get("winning_projected_progress_percent_if_selected"),
            10,
        )
        candidates = sanitized.get("candidates", [])
        self.assertEqual(candidates[0].get("projected_progress_percent_if_selected"), 10)
        self.assertEqual(candidates[1].get("projected_progress_percent_if_selected"), 5)

    def test_wake_skills_enter_skill_competition_candidates(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "function carrier",
                "current_seam": "graph skeleton",
                "current_debt": "decide the live graph route",
                "next_bite": "draw before 读出",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        competition = derive_skill_competition(
            state,
            [],
            primitive_field_override={
                "layer_object": "function carrier",
                "active_primitives": ["见证"],
                "why_now": "cheap probe pressure is live",
                "selection_basis": "lexical_hint",
                "evidence_basis": "lexical_hint",
            },
            control_signals_override={
                "meta_controls": {},
                "micro_control_surface": {},
                "layerwise_reselection_pressure": {
                    "active": True,
                    "wake_skills": ["图像", "赋值"],
                    "reason": "the current layer still looks thick enough to require a structural wake-up",
                    "direct_closure_allowed": False,
                },
                "composition_pressure": {},
            },
        )

        self.assertIsInstance(competition, dict)
        candidate_skills = [
            canonicalize_skill_token(candidate.get("skill"))
            for candidate in competition.get("candidates", [])
            if isinstance(candidate, dict)
        ]
        self.assertIn("图像", candidate_skills)
        self.assertIn("赋值", candidate_skills)

    def test_frontloaded_winner_can_materialize_problem_born_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "已知 (x+a)ln(x+b)≥0，求 a^2+b^2 的最小值",
                "current_seam": "a^2+b^2 的最小值是否由某个刚好压线的边界见证决定",
                "current_debt": "不要先做通法分类铺开；先猜参数下界由哪个边界值或见证点卡住，再做最小验证",
                "next_bite": "先找最可能卡出最小值的边界点或见证值，检查参数是否在该处刚好饱和，而不是先把全部区间分类做满",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        bridge = derive_skill_authority_bridge(state, [])

        self.assertIsInstance(bridge, dict)
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertIsInstance(touch, dict)
        self.assertNotEqual(touch.get("target"), "answer.md")
        self.assertIn(touch.get("kind"), {"check", "write", "见证"})
        self.assertTrue(touch.get("operation"))
        self.assertGreaterEqual(len(touch.get("owner_skill_combo_if_any", [])), 2)

    def test_structure_first_winner_rewrites_object_before_ordinary_writeout(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "carrier",
                "current_seam": "carrier gap",
                "current_debt": "rewrite to a thinner object before closure",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "carrier_handoff_if_any": {
                    "trigger": "same_carrier_change",
                    "from_slot": "solve",
                    "to_object": "thin ledger",
                    "winning_pressure": "structure survives more honestly on the thinner ledger",
                    "why_local": "the governing gap becomes visible there",
                    "warm_field": {
                        "active_pressures": ["状态拆分"],
                        "cheap_check": "split the ledger once",
                        "evidence_basis": "cheap_check",
                    },
                },
            }
        )

        bridge = derive_skill_authority_bridge(
            state,
            [],
            primitive_field_override={
                "layer_object": "thin ledger",
                "active_primitives": ["状态拆分"],
                "why_now": "the thinner object exposes the remaining gap",
                "selection_basis": "explicit_hint",
                "evidence_basis": "cheap_check",
                "tie_break_check": "split the ledger once",
            },
            skill_competition_override={
                "winning_skill_if_any": "状态拆分",
                "candidates": [
                    {
                        "skill": "状态拆分",
                        "touch_target": "thin ledger",
                        "supporting_skills_if_any": ["投影"],
                    },
                    {
                        "skill": "投影",
                        "touch_target": "thin ledger",
                        "supporting_skills_if_any": ["状态拆分"],
                    },
                ],
                "coactive_skills_if_any": ["状态拆分", "投影"],
            },
        )

        self.assertIsInstance(bridge, dict)
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertEqual(bridge.get("winning_skill_if_any"), "状态拆分")
        self.assertEqual(touch.get("target"), "thin ledger")
        self.assertEqual(touch.get("owner_skill_if_any"), "状态拆分")
        self.assertEqual(
            touch.get("owner_skill_combo_if_any"),
            ["状态拆分", "投影"],
        )
        self.assertNotEqual(touch.get("target"), "answer.md")

    def test_post_land_arena_keeps_next_local_gap_visible_after_rewrite(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "rewritten thin graph",
                "current_seam": "remaining signed gap on thin graph",
                "current_debt": "close one visible remaining gap",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "rewritten thin graph",
                    "operation": "rewrite the carrier onto one thin graph",
                    "success_signal": "thin graph explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "投影"],
                },
                "layer_composition_if_any": {
                    "event_owned": True,
                    "surface": "takeover_recomposition",
                    "layer_object": "rewritten thin graph",
                    "current_seam": "remaining signed gap on thin graph",
                    "controlled_object": "remaining signed gap on thin graph",
                    "next_local_choice": "remaining signed gap on thin graph",
                    "leading_skill_if_any": "图像",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "remaining signed gap on thin graph",
                        "operation": "check the remaining signed gap directly on the thin graph",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "投影"],
                    },
                },
            }
        )

        arena = derive_first_layer_arena(state, [])

        self.assertIsInstance(arena, dict)
        self.assertEqual(
            arena.get("focus_target"),
            "remaining signed gap on thin graph",
        )
        self.assertEqual(
            arena.get("verify_touch_if_any", {}).get("target"),
            "remaining signed gap on thin graph",
        )
        self.assertEqual(
            arena.get("authorized_touch_if_any", {}).get("target"),
            "remaining signed gap on thin graph",
        )

    def test_reopened_layer_arena_keeps_asked_medium_out_even_if_next_bite_mentions_writeup(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "rewritten thin graph",
                "current_seam": "remaining signed gap on thin graph",
                "current_debt": "close one visible gap before final writeout",
                "next_bite": "once this gap is closed, write answer.md immediately",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "rewritten thin graph",
                    "operation": "rewrite the carrier onto one thin graph",
                    "success_signal": "thin graph explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "投影"],
                },
                "layer_composition_if_any": {
                    "event_owned": True,
                    "surface": "takeover_recomposition",
                    "layer_object": "rewritten thin graph",
                    "current_seam": "remaining signed gap on thin graph",
                    "controlled_object": "remaining signed gap on thin graph",
                    "next_local_choice": "remaining signed gap on thin graph",
                    "leading_skill_if_any": "图像",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "remaining signed gap on thin graph",
                        "operation": "check the remaining signed gap directly on the thin graph",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "投影"],
                    },
                },
            }
        )

        arena = derive_first_layer_arena(state, [])

        self.assertIsInstance(arena, dict)
        self.assertNotEqual(arena.get("authorized_touch_if_any", {}).get("target"), "answer.md")
        self.assertNotEqual(arena.get("verify_touch_if_any", {}).get("target"), "answer.md")

    def test_same_carrier_takeover_promotes_natural_followup_skill(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "薄载体上只剩固定横坐标的局部读数",
                "current_seam": "固定线 x=-1 是否就是交点的横坐标",
                "current_debt": "在 x=-1 这条锚线上比较两条线的高度是否重合",
                "next_bite": "先盯住这条固定线，再决定是否直接读出结论",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "primitive_takeover_gate_if_any": {
                    "trigger": "same_carrier_landing",
                    "current_object": "薄载体上只剩固定横坐标的局部读数",
                },
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "薄载体上只剩固定横坐标的局部读数",
                    "operation": "图像已经把问题压到固定线读数上",
                    "success_signal": "薄载体显式化",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": [
                        "图像",
                        "极限边界",
                        "赋值",
                        "读出",
                    ],
                },
            }
        )

        bridge = derive_skill_authority_bridge(state, [])

        self.assertIsInstance(bridge, dict)
        self.assertEqual(bridge.get("winning_skill_if_any"), "极限边界")
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertEqual(touch.get("owner_skill_if_any"), "极限边界")
        self.assertEqual(
            touch.get("target"),
            "固定线 x=-1 是否就是交点的横坐标",
        )
        self.assertNotEqual(touch.get("target"), "answer.md")

    def test_same_carrier_takeover_ignores_generic_rewritten_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "thin graph controller",
                "current_seam": "one remaining local split",
                "current_debt": "bind the real current-layer split instead of a generic runtime instruction",
                "next_bite": "let the same-carrier followup stay local",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "landed_next_touch_if_any": {
                    "kind": "check",
                    "target": "one remaining local split",
                    "operation": "separate the live split directly on the current carrier",
                    "success_signal": "the local split is explicit",
                    "owner_skill_if_any": "状态拆分",
                    "owner_skill_combo_if_any": ["状态拆分", "见证"],
                },
            }
        )

        with patch("runtime_guard._same_carrier_takeover_active", return_value=True), patch(
            "runtime_guard._derive_rewritten_layer_promoted_touch",
            return_value=(
                {
                    "kind": "write",
                    "target": "one remaining local split",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on one remaining local split",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
                "图像",
                ["图像", "见证"],
            ),
        ):
            bridge = derive_skill_authority_bridge(state, [])

        self.assertIsInstance(bridge, dict)
        self.assertEqual(bridge.get("winning_skill_if_any"), "状态拆分")
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertEqual(touch.get("owner_skill_if_any"), "状态拆分")
        self.assertEqual(touch.get("operation"), "separate the live split directly on the current carrier")

    def test_skill_authority_bridge_collapses_public_lit_split_on_same_layer(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "a=1+(lnx)/x 这条值载体图像已经显式化",
                "current_seam": "峰值 x=e 与左右同高双点是否接管",
                "current_debt": "先锁定峰值和同高双点，不回到普通导数分类",
                "next_bite": "先在同一张图上读峰值和同高双点",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "draw the carrier",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "event_owned": True,
                    "must_bind_local_bite": True,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "极限边界",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "峰值 x=e 与左右同高双点是否接管",
                        "operation": "先锁定峰值 1+1/e 与左右同高双点",
                        "success_signal": "同一张图上的统一控制骨架显式化",
                        "owner_skill_if_any": "赋值",
                        "owner_skill_combo_if_any": ["赋值", "极限边界", "图像"],
                    },
                },
                "bound_program": {
                    "kind": "write",
                    "target": "峰值 x=e 与左右同高双点是否接管",
                    "operation": "先锁定峰值 1+1/e 与左右同高双点",
                    "success_signal": "同一张图上的统一控制骨架显式化",
                    "owner_skill_if_any": "赋值",
                    "owner_skill_combo_if_any": ["赋值", "极限边界", "图像"],
                },
            }
        )

        bridge = derive_skill_authority_bridge(state, [])

        self.assertIsInstance(bridge, dict)
        self.assertEqual(bridge.get("winning_skill_if_any"), "赋值")
        self.assertNotIn("executable_owner_skill_if_any", bridge)
        self.assertEqual(
            bridge.get("executable_local_touch_if_any", {}).get("owner_skill_if_any"),
            "赋值",
        )

    def test_first_layer_arena_aligns_focus_and_authorized_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "圆锥曲线问题中证明两条相关直线的交点落在定直线 x=-1 上",
                "current_seam": "固定线 x=-1 是否就是交点的横坐标",
                "current_debt": "目标只问固定横坐标，不先回收完整交点坐标；在 x=-1 这条锚线比较两条线的高度是否重合",
                "next_bite": "盯住定直线 x=-1 做目标式证明，先比较两条线在这条竖线上的读数，不先解全坐标",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        arena = derive_first_layer_arena(state, [])

        self.assertIsInstance(arena, dict)
        self.assertEqual(arena.get("focus_target"), "固定线 x=-1 是否就是交点的横坐标")
        self.assertEqual(
            arena.get("authorized_touch_if_any", {}).get("target"),
            "固定线 x=-1 是否就是交点的横坐标",
        )
        self.assertEqual(
            arena.get("verify_touch_if_any", {}).get("target"),
            "固定线 x=-1 是否就是交点的横坐标",
        )
        self.assertTrue(arena.get("active_skill_combo_if_any"))

    def test_first_layer_arena_skips_bootstrap_meta_target_and_stays_problem_facing(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "2026 ICPC APC M Deformed Balance problem summary",
                "current_seam": "compress the stated object into one thinner controller-bearing carrier without turning the bootstrap itself into route guidance",
                "current_debt": "separate the real controller from decorative burden and keep the next runtime transition local, honest, and non-scripted",
                "next_bite": "bind one concrete local touch on the current carrier without adding route hints or problem-specific solve staging",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        arena = derive_first_layer_arena(state, [])

        self.assertIsInstance(arena, dict)
        self.assertEqual(arena.get("focus_target"), "2026 ICPC APC M Deformed Balance problem summary")
        self.assertNotEqual(arena.get("authorized_touch_if_any", {}).get("target"), "final.md")
        self.assertNotIn("route guidance", arena.get("authorized_touch_if_any", {}).get("target", ""))

    def test_first_layer_arena_rebuilds_generic_authority_touch_during_fresh_blind_first_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "2026 ICPC APC M Deformed Balance problem summary",
                "current_seam": "compress the stated object into one thinner controller-bearing carrier without turning the bootstrap itself into route guidance",
                "current_debt": "separate the real controller from decorative burden and keep the next runtime transition local, honest, and non-scripted",
                "next_bite": "bind one concrete local touch on the current carrier without adding route hints or problem-specific solve staging",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        arena = derive_first_layer_arena(
            state,
            [],
            skill_authority_override={
                "winning_skill_if_any": "图像",
                "same_carrier_only": True,
                "executable_local_touch_if_any": {
                    "kind": "write",
                    "target": "2026 ICPC APC M Deformed Balance problem summary",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on 2026 ICPC APC M Deformed Balance problem summary",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "状态拆分", "见证"],
                },
            },
            skill_lighting_override={
                "lit_skill_if_any": "图像",
                "candidate_skills_if_any": ["图像", "状态拆分", "见证"],
                "supporting_skills_if_any": ["状态拆分", "见证"],
                "verify_touch_if_any": {
                    "target": "2026 ICPC APC M Deformed Balance problem summary",
                    "kind": "write",
                },
            },
        )

        touch = arena.get("authorized_touch_if_any", {})
        self.assertIsInstance(arena, dict)
        self.assertEqual(touch.get("target"), "2026 ICPC APC M Deformed Balance problem summary")
        self.assertNotEqual(
            touch.get("operation"),
            "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
        )
        self.assertFalse(is_generic_runtime_operation(touch))
        self.assertTrue(
            any(
                marker in str(touch.get("operation", ""))
                for marker in ["problem diagram", "state graph"]
            )
        )

    def test_problem_frontload_keeps_counter_question_for_hostile_falsifier_lane(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                "current_seam": "ordinary balanced-prefix heuristics explain some samples but fail on (() and other class-+1 counterexamples",
                "current_debt": "separate the real tree-weight invariant from ordinary bracket-prefix repair",
                "next_bite": "use one hostile counterexample before the structural carrier thickens",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        frontload = derive_problem_skill_frontload(state)

        self.assertIsInstance(frontload, dict)
        skills = frontload.get("candidate_skills", [])
        self.assertIn("反问", skills)
        self.assertIn("守恒", skills)
        self.assertIn("对称", skills)

    def test_controller_trigger_surface_can_frontload_counter_question_with_structure(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                "current_seam": "ordinary balanced-prefix heuristics explain some samples but fail on (() and other class-+1 counterexamples",
                "current_debt": "separate the real tree-weight invariant from ordinary bracket-prefix repair",
                "next_bite": "kill the fake main line first",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        trigger = derive_controller_trigger_surface(
            state,
            primitive_field_override={
                "layer_object": state["current_object"],
                "active_primitives": ["守恒", "对称", "见证", "状态拆分"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
            },
            control_signals_override={"current_controller_view": {}},
        )

        self.assertIsInstance(trigger, dict)
        self.assertIn("hostile_falsifier_first", trigger.get("trigger_names", []))
        self.assertEqual(trigger.get("favored_skills", [None])[0], "反问")
        self.assertIn("守恒", trigger.get("favored_skills", []))

    def test_controller_trigger_surface_uses_counter_question_to_arbitrate_structural_combo(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "parameter monotonicity for f(x)=ln((x^2-x+ax)/(x-1)^3)",
                "current_seam": "which first-layer carrier really controls the lower bound on a",
                "current_debt": "let 图像, 赋值, and 极限边界 compete before ordinary derivation",
                "next_bite": "choose the strongest first-layer combo",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        trigger = derive_controller_trigger_surface(
            state,
            primitive_field_override={
                "layer_object": state["current_object"],
                "active_primitives": ["图像", "赋值", "极限边界"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
            },
            control_signals_override={
                "current_controller_view": {},
                "meta_controls": {
                    "反问": {
                        "active": True,
                        "target": state["current_seam"],
                        "question": "这一步先看图像、赋值还是边界，谁对参数下界推进最深？",
                    }
                },
                "micro_control_surface": {
                    "反问": {
                        "target": state["current_seam"],
                        "question": "这一步先看图像、赋值还是边界，谁对参数下界推进最深？",
                    }
                },
            },
        )

        self.assertIsInstance(trigger, dict)
        self.assertEqual(trigger.get("mode"), "counter_question_arbitration")
        self.assertEqual(trigger.get("arbitration_skill_if_any"), "反问")
        self.assertIn("counter_question_arbitration", trigger.get("trigger_names", []))
        self.assertIn("图像", trigger.get("favored_combo", []))
        self.assertIn("赋值", trigger.get("favored_combo", []))
        self.assertNotEqual(trigger.get("favored_skills", [None])[0], "反问")

    def test_skill_competition_keeps_counter_question_inside_open_competition_field(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                "current_seam": "ordinary balanced-prefix heuristics explain some samples but fail on (() and other class-+1 counterexamples",
                "current_debt": "separate the real tree-weight invariant from ordinary bracket-prefix repair",
                "next_bite": "use one hostile counterexample before the structural carrier thickens",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        competition = derive_skill_competition(
            state,
            [],
            primitive_field_override={
                "layer_object": state["current_object"],
                "active_primitives": ["守恒", "对称", "见证", "状态拆分"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
            },
            control_signals_override={
                "current_controller_view": {},
                "meta_controls": {
                    "反问": {
                        "active": True,
                        "target": state["current_seam"],
                    }
                },
                "micro_control_surface": {
                    "反问": {
                        "target": state["current_seam"],
                    }
                },
                "layerwise_reselection_pressure": {"active": False},
            },
        )

        self.assertIsInstance(competition, dict)
        self.assertEqual(competition.get("competition_basis"), "projected_gain_first_takeover")
        self.assertEqual(competition.get("arbitration_skill_if_any"), "反问")
        self.assertIn("守恒", competition.get("favored_combo_if_any", []))
        self.assertIn("对称", competition.get("favored_combo_if_any", []))
        self.assertIn("见证", competition.get("favored_combo_if_any", []))
        self.assertGreaterEqual(len(competition.get("lit_candidate_skills_if_any", [])), 5)
        counter_candidate = next(
            candidate
            for candidate in competition.get("candidates", [])
            if candidate.get("skill") == "反问"
        )
        self.assertIn("守恒", counter_candidate.get("supporting_skills_if_any", []))
        self.assertNotEqual(competition.get("favored_combo_if_any", [None])[0], "反问")

    def test_skill_competition_can_use_counter_question_as_arbitration_without_making_it_owner(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "parameter monotonicity for f(x)=ln((x^2-x+ax)/(x-1)^3)",
                "current_seam": "which first-layer carrier really controls the lower bound on a",
                "current_debt": "let 图像, 赋值, and 极限边界 compete before ordinary derivation",
                "next_bite": "choose the strongest first-layer combo",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        competition = derive_skill_competition(
            state,
            [],
            primitive_field_override={
                "layer_object": state["current_object"],
                "active_primitives": ["图像", "赋值", "极限边界"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
            },
            control_signals_override={
                "current_controller_view": {},
                "meta_controls": {
                    "反问": {
                        "active": True,
                        "target": state["current_seam"],
                        "question": "这一步先看图像、赋值还是边界，谁对参数下界推进最深？",
                    }
                },
                "micro_control_surface": {
                    "反问": {
                        "target": state["current_seam"],
                        "question": "这一步先看图像、赋值还是边界，谁对参数下界推进最深？",
                    }
                },
                "layerwise_reselection_pressure": {"active": False},
            },
        )

        self.assertIsInstance(competition, dict)
        self.assertEqual(competition.get("competition_basis"), "counter_question_arbitrated_projected_gain")
        self.assertEqual(competition.get("arbitration_skill_if_any"), "反问")
        self.assertIn("图像", competition.get("favored_combo_if_any", []))
        self.assertIn(competition.get("winning_skill_if_any"), {"图像", "赋值", "极限边界"})
        self.assertNotEqual(competition.get("winning_skill_if_any"), "反问")

    def test_skill_authority_bridge_keeps_first_touch_semantically_owned_by_live_combo(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                "current_seam": "ordinary balanced-prefix heuristics explain some samples but fail on (() and other class-+1 counterexamples",
                "current_debt": "separate the real tree-weight invariant from ordinary bracket-prefix repair",
                "next_bite": "kill the fake main line first",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        bridge = derive_skill_authority_bridge(
            state,
            [],
            primitive_field_override={
                "layer_object": state["current_object"],
                "active_primitives": ["守恒", "对称", "见证", "状态拆分"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
            },
            control_signals_override={
                "current_controller_view": {},
                "meta_controls": {"反问": {"active": True, "target": state["current_seam"]}},
                "micro_control_surface": {"反问": {"target": state["current_seam"]}},
            },
            closure_nucleus_override={"separating_check_if_any": state["current_seam"]},
            skill_competition_override={
                "winning_skill_if_any": "反问",
                "candidates": [
                    {
                        "skill": "反问",
                        "touch_target": state["current_seam"],
                        "supporting_skills_if_any": ["守恒", "对称"],
                    }
                ],
                "coactive_skills_if_any": ["反问", "守恒", "对称"],
                "lit_candidate_skills_if_any": ["反问", "守恒", "对称"],
            },
        )

        self.assertIsInstance(bridge, dict)
        self.assertEqual(bridge.get("winning_skill_if_any"), "反问")
        self.assertTrue(bridge.get("same_carrier_only"))
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertEqual(touch.get("target"), state["current_seam"])
        self.assertTrue(touch.get("owner_skill_if_any"))
        self.assertIn(touch.get("owner_skill_if_any"), touch.get("owner_skill_combo_if_any", []))
        for skill in ["反问", "守恒", "对称", "见证", "状态拆分"]:
            self.assertIn(skill, touch.get("owner_skill_combo_if_any", []))

    def test_skill_authority_bridge_returns_execution_to_structural_skill_after_counter_check(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                "current_seam": "derive the surviving tree-weight invariant after the counterexample killed the fake prefix heuristic",
                "current_debt": "compress the real invariant instead of repeating the hostile falsifier",
                "next_bite": "return to the live structural carrier",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        bridge = derive_skill_authority_bridge(
            state,
            [],
            primitive_field_override={
                "layer_object": state["current_object"],
                "active_primitives": ["守恒", "对称", "见证", "状态拆分"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
                "tie_break_check": state["current_seam"],
            },
            control_signals_override={
                "current_controller_view": {},
                "meta_controls": {"反问": {"active": True, "target": "(() killed the fake prefix heuristic"}},
                "micro_control_surface": {"反问": {"target": "(() killed the fake prefix heuristic"}},
            },
            closure_nucleus_override={"separating_check_if_any": "(() killed the fake prefix heuristic"},
            skill_competition_override={
                "winning_skill_if_any": "反问",
                "candidates": [
                    {
                        "skill": "反问",
                        "touch_target": "(() killed the fake prefix heuristic",
                        "supporting_skills_if_any": ["守恒", "对称"],
                    }
                ],
                "coactive_skills_if_any": ["反问", "守恒", "对称"],
                "lit_candidate_skills_if_any": ["反问", "守恒", "对称"],
            },
        )

        self.assertIsInstance(bridge, dict)
        self.assertEqual(bridge.get("winning_skill_if_any"), "反问")
        self.assertEqual(bridge.get("executable_owner_skill_if_any"), "守恒")
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertEqual(touch.get("owner_skill_if_any"), "守恒")
        self.assertNotEqual(touch.get("target"), "(() killed the fake prefix heuristic")
        self.assertIn(
            touch.get("target"),
            {state["current_object"], state["current_seam"], state["current_debt"]},
        )

    def test_reopened_layer_bridge_drops_stale_counterexample_authority(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "surviving tree-weight ledger",
                "current_seam": "compress the surviving invariant after (() was already used",
                "current_debt": "return to the structural invariant instead of repeating the falsifier",
                "next_bite": "bind the surviving invariant on the reopened thin layer",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "surviving tree-weight ledger",
                    "operation": "reopen the thin ledger after the hostile falsifier landed",
                    "success_signal": "the thin ledger is explicit",
                    "owner_skill_if_any": "守恒",
                    "owner_skill_combo_if_any": ["守恒", "状态拆分", "对称"],
                },
                "layer_composition_if_any": {
                    "event_owned": True,
                    "surface": "takeover_recomposition",
                    "layer_object": "surviving tree-weight ledger",
                    "current_seam": "compress the surviving invariant after (() was already used",
                    "controlled_object": "compress the surviving invariant after (() was already used",
                    "next_local_choice": "compress the surviving invariant after (() was already used",
                    "leading_skill_if_any": "守恒",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "compress the surviving invariant after (() was already used",
                        "operation": "compress the surviving invariant on the reopened thin ledger",
                        "owner_skill_if_any": "守恒",
                        "owner_skill_combo_if_any": ["守恒", "状态拆分", "对称"],
                    },
                },
            }
        )

        bridge = derive_skill_authority_bridge(
            state,
            [],
            primitive_field_override={
                "layer_object": "surviving tree-weight ledger",
                "active_primitives": ["守恒", "状态拆分", "对称"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
                "tie_break_check": state["current_seam"],
            },
            control_signals_override={
                "current_controller_view": {},
                "meta_controls": {"反问": {"active": True, "target": "(() killed the fake prefix heuristic"}},
                "micro_control_surface": {"反问": {"target": "(() killed the fake prefix heuristic"}},
            },
            closure_nucleus_override={"separating_check_if_any": "(() killed the fake prefix heuristic"},
            skill_competition_override={
                "winning_skill_if_any": "反问",
                "candidates": [
                    {
                        "skill": "反问",
                        "touch_target": "(() killed the fake prefix heuristic",
                        "supporting_skills_if_any": ["守恒", "对称"],
                    }
                ],
                "coactive_skills_if_any": ["反问", "守恒", "对称"],
                "lit_candidate_skills_if_any": ["反问", "守恒", "对称"],
            },
        )

        self.assertIsInstance(bridge, dict)
        self.assertEqual(bridge.get("winning_skill_if_any"), "守恒")
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertEqual(touch.get("owner_skill_if_any"), "守恒")
        self.assertNotEqual(touch.get("target"), "(() killed the fake prefix heuristic")
        self.assertNotEqual(touch.get("owner_skill_combo_if_any"), ["反问", "守恒", "对称"])

    def test_skill_authority_bridge_uses_supported_structural_followup_not_hardcoded_skill(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "thin graph already killed the fake path and only the ledger split remains",
                "current_seam": "split the surviving ledger instead of repeating the falsifier",
                "current_debt": "compress the remaining ledger by state split",
                "next_bite": "return to the strongest structural followup",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        bridge = derive_skill_authority_bridge(
            state,
            [],
            primitive_field_override={
                "layer_object": state["current_object"],
                "active_primitives": ["状态拆分", "图像", "见证"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "cheap_check",
                "tie_break_check": state["current_seam"],
            },
            control_signals_override={
                "current_controller_view": {},
                "meta_controls": {"反问": {"active": True, "target": "one cheap falsifier already landed"}},
                "micro_control_surface": {"反问": {"target": "one cheap falsifier already landed"}},
            },
            closure_nucleus_override={"separating_check_if_any": "one cheap falsifier already landed"},
            skill_competition_override={
                "winning_skill_if_any": "反问",
                "candidates": [
                    {
                        "skill": "反问",
                        "touch_target": "one cheap falsifier already landed",
                        "supporting_skills_if_any": ["状态拆分", "图像"],
                    }
                ],
                "coactive_skills_if_any": ["反问", "状态拆分", "图像"],
                "lit_candidate_skills_if_any": ["反问", "状态拆分", "图像"],
            },
        )

        self.assertIsInstance(bridge, dict)
        self.assertEqual(bridge.get("winning_skill_if_any"), "反问")
        self.assertEqual(bridge.get("executable_owner_skill_if_any"), "状态拆分")
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertEqual(touch.get("owner_skill_if_any"), "状态拆分")
        self.assertIn("状态拆分", touch.get("owner_skill_combo_if_any", []))
        self.assertNotIn("守恒", touch.get("owner_skill_combo_if_any", []))

    def test_generic_layer_arena_matches_first_layer_shape_on_fresh_first_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        generic = derive_layer_arena(state, [])
        first = derive_first_layer_arena(state, [])

        self.assertIsInstance(generic, dict)
        self.assertIsInstance(first, dict)
        self.assertEqual(generic.get("focus_target"), first.get("focus_target"))
        self.assertEqual(
            generic.get("authorized_touch_if_any", {}).get("target"),
            first.get("authorized_touch_if_any", {}).get("target"),
        )
        self.assertEqual(
            generic.get("active_skill_combo_if_any"),
            first.get("active_skill_combo_if_any"),
        )
        self.assertEqual(generic.get("surface"), "layer_arena")
        self.assertEqual(first.get("surface"), "first_layer_arena")

    def test_generic_layer_arena_relights_post_land_layer_without_asked_medium_drift(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "rewritten thin graph",
                "current_seam": "remaining signed gap on thin graph",
                "current_debt": "close one visible remaining gap",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "rewritten thin graph",
                    "operation": "rewrite the carrier onto one thin graph",
                    "success_signal": "thin graph explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "投影"],
                },
                "layer_composition_if_any": {
                    "event_owned": True,
                    "surface": "takeover_recomposition",
                    "layer_object": "rewritten thin graph",
                    "current_seam": "remaining signed gap on thin graph",
                    "controlled_object": "remaining signed gap on thin graph",
                    "next_local_choice": "remaining signed gap on thin graph",
                    "leading_skill_if_any": "图像",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "remaining signed gap on thin graph",
                        "operation": "check the remaining signed gap directly on the thin graph",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "投影"],
                    },
                },
            }
        )

        arena = derive_layer_arena(state, [])

        self.assertIsInstance(arena, dict)
        self.assertEqual(arena.get("surface"), "layer_arena")
        self.assertEqual(arena.get("focus_target"), "remaining signed gap on thin graph")
        self.assertEqual(
            arena.get("authorized_touch_if_any", {}).get("target"),
            "remaining signed gap on thin graph",
        )
        self.assertNotEqual(arena.get("focus_target"), "answer.md")
        self.assertEqual(
            arena.get("anti_pipeline_note"),
            "these prompts are current-layer pressure surfaces, not a required order",
        )
        self.assertEqual(
            arena.get("primary_skill_if_any"),
            arena.get("authorized_touch_if_any", {}).get("owner_skill_if_any"),
        )

    def test_event_owned_relight_reuses_arena_style_surface_on_later_layer(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "rewritten thin graph",
                "current_seam": "remaining signed gap on thin graph",
                "current_debt": "close one visible remaining gap",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "rewritten thin graph",
                    "operation": "rewrite the carrier onto one thin graph",
                    "success_signal": "thin graph explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "投影"],
                },
                "layer_composition_if_any": {
                    "event_owned": True,
                    "surface": "takeover_recomposition",
                    "layer_object": "rewritten thin graph",
                    "current_seam": "remaining signed gap on thin graph",
                    "controlled_object": "remaining signed gap on thin graph",
                    "next_local_choice": "remaining signed gap on thin graph",
                    "leading_skill_if_any": "图像",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "remaining signed gap on thin graph",
                        "operation": "check the remaining signed gap directly on the thin graph",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "投影"],
                    },
                    "lighting_if_any": {
                        "lit_skill_if_any": "图像",
                        "supporting_skills_if_any": ["投影"],
                        "verify_touch_if_any": {
                            "target": "remaining signed gap on thin graph",
                            "kind": "check",
                        },
                        "ordinary_operations_are_not_skills": True,
                        "anti_pipeline_note": "these prompts are current-layer pressure surfaces, not a required order",
                    },
                },
            }
        )

        arena = derive_first_layer_arena(state, [])

        self.assertIsInstance(arena, dict)
        self.assertEqual(arena.get("focus_target"), "remaining signed gap on thin graph")
        self.assertEqual(arena.get("primary_skill_if_any"), "图像")
        self.assertEqual(
            arena.get("authorized_touch_if_any", {}).get("target"),
            "remaining signed gap on thin graph",
        )
        self.assertIn("图像", arena.get("active_skill_combo_if_any", []))
        self.assertIn("投影", arena.get("active_skill_combo_if_any", []))
        self.assertEqual(
            arena.get("anti_pipeline_note"),
            "these prompts are current-layer pressure surfaces, not a required order",
        )
        self.assertEqual(
            arena.get("authorized_touch_if_any", {}).get("owner_skill_if_any"),
            arena.get("primary_skill_if_any"),
        )

    def test_report_projects_event_owned_relight_through_same_arena_surface(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "rewritten thin graph",
                "current_seam": "remaining signed gap on thin graph",
                "current_debt": "close one visible remaining gap",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "rewritten thin graph",
                    "operation": "rewrite the carrier onto one thin graph",
                    "success_signal": "thin graph explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "投影"],
                },
                "layer_composition_if_any": {
                    "event_owned": True,
                    "surface": "takeover_recomposition",
                    "layer_object": "rewritten thin graph",
                    "current_seam": "remaining signed gap on thin graph",
                    "controlled_object": "remaining signed gap on thin graph",
                    "next_local_choice": "remaining signed gap on thin graph",
                    "leading_skill_if_any": "图像",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "remaining signed gap on thin graph",
                        "operation": "check the remaining signed gap directly on the thin graph",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "投影"],
                    },
                    "lighting_if_any": {
                        "lit_skill_if_any": "图像",
                        "supporting_skills_if_any": ["投影"],
                        "verify_touch_if_any": {
                            "target": "remaining signed gap on thin graph",
                            "kind": "check",
                        },
                        "ordinary_operations_are_not_skills": True,
                        "anti_pipeline_note": "these prompts are current-layer pressure surfaces, not a required order",
                    },
                },
            }
        )

        report = build_report(state, Path("dummy_state.json"))
        arena = report.get("first_layer_arena")

        self.assertIsInstance(arena, dict)
        self.assertEqual(arena.get("focus_target"), "remaining signed gap on thin graph")
        self.assertEqual(arena.get("primary_skill_if_any"), "图像")
        self.assertEqual(
            arena.get("authorized_touch_if_any", {}).get("target"),
            "remaining signed gap on thin graph",
        )
        self.assertIn("投影", arena.get("active_skill_combo_if_any", []))
        self.assertEqual(
            arena.get("anti_pipeline_note"),
            "these prompts are current-layer pressure surfaces, not a required order",
        )

    def test_interlayer_bridge_promotes_supporting_closure_after_thinner_spend(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "original carrier",
                "current_seam": "need one structural spend before final equation",
                "current_debt": "structural gap still live",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "carrier_handoff_if_any": {
                    "trigger": "same_carrier_change",
                    "from_slot": "solve",
                    "to_object": "thin object",
                    "winning_pressure": "投影 made the governing gap legible",
                    "why_local": "the thin object exposes one remaining gap",
                    "warm_field": {
                        "active_pressures": ["状态拆分"],
                        "cheap_check": "write the split on the thin object",
                        "evidence_basis": "cheap_check",
                    },
                },
            }
        )

        bridge = derive_interlayer_discharge_bridge(
            state,
            [],
            primitive_field_override={
                "layer_object": "thin object",
                "active_primitives": ["状态拆分"],
                "why_now": "the thin object still needs one structural split",
                "selection_basis": "explicit_hint",
                "evidence_basis": "cheap_check",
            },
            control_signals_override={
                "current_controller_view": {"carrier_status": "thinning"},
                "meta_controls": {
                    "后脑守卫": {"active": True},
                    "中枢控制": {"mode": "closure_gate"},
                },
                "micro_control_surface": {
                    "监督_pulse": {"active": True},
                    "closure_pull": {"active": True, "blocks_release": True},
                },
            },
            skill_authority_override={
                "winning_skill_if_any": "精确封口",
                "executable_local_touch_if_any": {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "write the forced final equality",
                    "success_signal": "final answer stated",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口"],
                },
            },
        )

        self.assertIsInstance(bridge, dict)
        self.assertEqual(bridge.get("mode"), "primitive_then_closure")
        self.assertEqual(bridge.get("handoff_target"), "thin object")
        self.assertEqual(
            bridge.get("spend_first_program", {}).get("target"),
            "thin object",
        )
        self.assertEqual(
            bridge.get("post_closure_touch_if_any", {}).get("owner_skill_if_any"),
            "精确封口",
        )
        self.assertEqual(
            bridge.get("post_closure_touch_if_any", {}).get("target"),
            "answer.md",
        )
        self.assertTrue(bridge.get("keep_closure_authority"))

    def test_fresh_blind_initial_inspect_refusal_keeps_layer_but_hides_读出(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "fresh_blind_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {
                    "mode": "fresh_blind_project_skills_on",
                    "auto_enter_local_action_when_concrete": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            payload, exit_code = build_inspect_surface(state_path)

        self.assertEqual(exit_code, 1)
        self.assertTrue(payload.get("pending_transition"))
        self.assertEqual(payload.get("reason"), "active_discipline_contract_requires_runtime_consumption")
        self.assertEqual(payload.get("layer_composition", {}).get("surface"), "fresh_blind_first_touch")
        self.assertTrue(payload.get("layer_composition", {}).get("qualified_claims_pending"))
        self.assertGreaterEqual(
            len(payload.get("layer_composition", {}).get("active_skill_combo_if_any", [])),
            2,
        )
        self.assertNotIn("skill_field", payload)
        self.assertNotIn("skill_competition", payload)
        self.assertNotIn("skill_authority_bridge", payload)
        self.assertNotIn(
            "lit_skill_if_any",
            payload.get("layer_composition", {}).get("lighting_if_any", {}),
        )
        self.assertNotIn("读出", payload)
        self.assertNotIn("available_authority_touches", payload)

    def test_fresh_blind_default_inspect_attempts_autonomous_transition(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "fresh_blind_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with patch(
                "runtime_consume.maybe_run_autonomous_transition",
                return_value=({"autonomous_transition": True, "inspect_only": False}, 0),
            ) as transition_mock:
                payload, exit_code = build_inspect_surface(state_path)

        self.assertEqual(exit_code, 0)
        self.assertTrue(payload.get("autonomous_transition"))
        self.assertFalse(payload.get("inspect_only"))
        transition_mock.assert_called_once()

    def test_fresh_blind_default_inspect_autobinds_report_derived_first_touch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            bootstrap_blind_state(
                state_path,
                current_object="equation ln x=(a-1)x on x>0",
                current_seam="equation ln x=(a-1)x on x>0",
                current_debt="separate root-count regimes and bind the two-root product gap",
                next_bite="use the carrier 图像 before asked-medium writeout",
                asked_medium_surface="solve_writeup.md",
                revocation_handle="fresh_blind_case",
                primary_slot="solve",
            )

            payload, exit_code = build_inspect_surface(state_path)
            rebound_state = json.loads(state_path.read_text(encoding="utf-8"))
            runtime_evidence = build_runtime_evidence(state_path)

        self.assertIn(exit_code, {1, 2})
        self.assertEqual(payload.get("binding_action"), "pending_execute_local")
        self.assertTrue(payload.get("consumed"))
        self.assertFalse(payload.get("inspect_only"))
        self.assertEqual(payload.get("transition_history"), ["bind_local"])
        self.assertEqual(payload.get("allowed_transition_surfaces"), ["execute_local"])
        self.assertTrue(payload.get("autonomous_transition"))
        self.assertEqual(
            rebound_state.get("bound_program", {}).get("target"),
            "equation ln x=(a-1)x on x>0",
        )
        self.assertEqual(
            rebound_state.get("layer_composition_if_any", {}).get("surface"),
            "bound_program",
        )
        self.assertTrue(runtime_evidence.get("has_real_runtime_transition"))
        self.assertEqual(
            runtime_evidence.get("latest_real_runtime_transition_command"),
            "bind-local",
        )

    def test_fresh_blind_default_inspect_autobinds_generic_sequence_first_touch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            bootstrap_blind_state(
                state_path,
                current_object="IOI 2024 Hieroglyphs: universal common subsequence under subsequence order",
                current_seam="all common subsequences must fit inside one common super-container U that is itself common",
                current_debt="find a thinner carrier that decides whether one universal common subsequence exists or non-existence is forced",
                next_bite="externalize the structure that controls all common subsequences without route leakage",
                asked_medium_surface="final.md",
                revocation_handle="fresh_blind_hieroglyphs_case",
                primary_slot="solve",
            )

            payload, exit_code = build_inspect_surface(state_path)
            rebound_state = json.loads(state_path.read_text(encoding="utf-8"))
            runtime_evidence = build_runtime_evidence(state_path)

        self.assertIn(exit_code, {1, 2})
        self.assertEqual(payload.get("binding_action"), "pending_execute_local")
        self.assertTrue(payload.get("consumed"))
        self.assertFalse(payload.get("inspect_only"))
        self.assertEqual(payload.get("transition_history"), ["bind_local"])
        self.assertEqual(payload.get("allowed_transition_surfaces"), ["execute_local"])
        self.assertTrue(payload.get("autonomous_transition"))
        self.assertEqual(
            rebound_state.get("bound_program", {}).get("target"),
            "all common subsequences must fit inside one common super-container U that is itself common",
        )
        self.assertEqual(
            rebound_state.get("bound_program", {}).get("owner_skill_if_any"),
            "极限边界",
        )
        self.assertEqual(
            rebound_state.get("layer_composition_if_any", {}).get("surface"),
            "bound_program",
        )
        self.assertTrue(runtime_evidence.get("has_real_runtime_transition"))
        self.assertEqual(
            runtime_evidence.get("latest_real_runtime_transition_command"),
            "bind-local",
        )

    def test_non_fresh_blind_default_inspect_stays_read_only_without_auto_transition(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "non_fresh_blind_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with patch("runtime_consume.maybe_run_autonomous_transition") as transition_mock:
                payload, exit_code = build_inspect_surface(state_path)

        self.assertIn(exit_code, {1, 2})
        self.assertTrue(payload.get("inspect_only"))
        transition_mock.assert_not_called()

    def test_bootstrap_event_excerpt_does_not_claim_lit_skill_before_transition(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "fresh_blind_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {
                    "mode": "fresh_blind_project_skills_on",
                    "requires_qualified_layer_composition_for_skill_claims": True,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            append_runtime_event(
                state_path,
                command_name="bootstrap-blind",
                before=None,
                after=state,
            )
            events = load_runtime_events(state_path)

        self.assertEqual(len(events), 1)
        excerpt = events[0].get("report_excerpt", {})
        self.assertNotIn("skill_field", excerpt)
        self.assertNotIn("skill_competition", excerpt)
        self.assertNotIn("skill_authority_bridge", excerpt)
        self.assertTrue(excerpt.get("layer_composition", {}).get("qualified_claims_pending"))
        self.assertNotIn(
            "lit_skill_if_any",
            excerpt.get("layer_composition", {}).get("lighting_if_any", {}),
        )

    def test_bootstrap_helper_creates_run_local_state_but_not_runtime_participation_yet(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "run"
            run_dir.mkdir()
            state_path = run_dir / "runtime_state.json"
            state = bootstrap_blind_state(
                state_path,
                current_object="Characterize strings T with deformed balance and minimize additions around S",
                current_seam="ordinary balanced-prefix repair may be fake; isolate the exact structural criterion",
                current_debt="find the thinner exact carrier that separates structural validity from ordinary balanced-prefix repair",
                next_bite="draw one minimal problem diagram for deformed balance and rewrite the governing relation",
                asked_medium_surface="final.md",
            )
            runtime_evidence = build_runtime_evidence(state_path)
            payload, exit_code = build_inspect_surface(state_path)

        self.assertEqual(state_path.name, "runtime_state.json")
        self.assertEqual(state.get("bootstrap_context", {}).get("mode"), "fresh_blind_project_skills_on")
        self.assertFalse(runtime_evidence.get("has_real_runtime_transition"))
        self.assertEqual(runtime_evidence.get("real_runtime_transition_count"), 0)
        self.assertEqual(runtime_evidence.get("event_count"), 1)
        self.assertEqual(runtime_evidence.get("latest_event_command"), "bootstrap-blind")
        self.assertEqual(exit_code, 1)
        self.assertTrue(payload.get("pending_transition"))
        if "runtime_transition_required" in payload:
            self.assertTrue(payload.get("runtime_transition_required"))
        self.assertIn(
            payload.get("reason"),
            {
                "active_discipline_contract_requires_runtime_consumption",
                "fresh_blind_project_skills_on_requires_new_runtime_transition",
            },
        )

    def test_expired_bootstrap_watchdog_surfaces_in_inspect_and_controller(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "fresh_blind_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {
                    "mode": "fresh_blind_project_skills_on",
                    "requires_new_runtime_transition": True,
                    "requires_qualified_layer_composition_for_skill_claims": True,
                    "first_runtime_transition_window_seconds": 1,
                    "first_runtime_transition_window_started_at": "2000-01-01T00:00:00+00:00",
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            inspect_payload, inspect_exit = build_inspect_surface(state_path)
            controller_payload, controller_exit = build_controller_读出(state_path)

        self.assertEqual(inspect_exit, 1)
        self.assertEqual(inspect_payload.get("reason"), "bootstrap_runtime_window_expired")
        self.assertTrue(
            inspect_payload.get("runtime_transition_watchdog", {}).get("expired")
        )
        self.assertEqual(controller_exit, 1)
        self.assertEqual(controller_payload.get("reason"), "bootstrap_runtime_window_expired")
        self.assertTrue(
            controller_payload.get("runtime_transition_watchdog", {}).get("expired")
        )

    def test_check_command_refuses_fresh_blind_first_touch_before_bind(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "fresh_blind_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            exit_code = command_check(type("Args", (), {"state_file": str(state_path)})())

        self.assertEqual(exit_code, 1)

    def test_execute_local_refuses_state_backed_blind_worked_step_when_equation_solving_leaks_in(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "矩形8x9截面内两个相同圆与上下边、左右边及彼此外切",
                "current_seam": "由两圆心距离等于2r读出最大半径",
                "current_debt": "在二维截面上把横向距离 8-2r 与纵向距离 9-2r 写进外切方程",
                "next_bite": "在矩形截面中列出外切方程并解出 r",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "check",
                    "target": "由两圆心距离等于2r读出最大半径",
                    "operation": "push the center-distance relation to one decisive boundary check",
                    "success_signal": "the decisive center-distance equation is explicit",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "对称", "投影", "读出"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "矩形8x9截面内两个相同圆与上下边、左右边及彼此外切",
                    "controlled_object": "由两圆心距离等于2r读出最大半径",
                    "current_seam": "由两圆心距离等于2r读出最大半径",
                    "current_debt": "在二维截面上把横向距离 8-2r 与纵向距离 9-2r 写进外切方程",
                    "reason": "the current layer must visibly cash the live skill combination into the solution text",
                    "leading_skill_if_any": "极限边界",
                    "event_owned": True,
                    "transition_change": "bound one geometry-owned touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["极限边界", "对称", "投影", "读出"],
                    "authorized_bite": {
                        "kind": "check",
                        "target": "由两圆心距离等于2r读出最大半径",
                        "operation": "push the center-distance relation to one decisive boundary check",
                        "success_signal": "the decisive center-distance equation is explicit",
                        "owner_skill_if_any": "极限边界",
                        "owner_skill_combo_if_any": ["极限边界", "对称", "投影", "读出"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": (
                                "在控制截面上，两圆心横向距离为 8-2r，纵向距离为 9-2r，且两圆外切给出圆心距 2r，"
                                "因此有 (8-2r)^2+(9-2r)^2=(2r)^2，解得 r=5/2。"
                            ),
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("当前应先由 `极限边界` 接管", str(exc.exception))

    def test_execute_local_refuses_second_touch_on_same_bound_program(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "thin graph",
                "current_seam": "remaining signed gap",
                "current_debt": "close one visible local gap",
                "next_bite": "check the remaining signed gap directly",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": "remaining signed gap",
                    "operation": "use 图像 to check the remaining signed gap directly",
                    "success_signal": "the remaining gap is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "投影"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "图像 在 remaining signed gap 上完成了一次当前层检查",
                            "summary": "",
                            "output_file": None,
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("already touched once", str(exc.exception))

    def test_execute_local_refuses_semantic_owner_wording_when_equation_solving_leaks_in(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "矩形8x9截面内两个相同圆与上下边、左右边及彼此外切",
                "current_seam": "由两圆心距离等于2r读出最大半径",
                "current_debt": "在二维截面上把横向距离 8-2r 与纵向距离 9-2r 写进外切方程",
                "next_bite": "在矩形截面中列出外切方程并解出 r",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "check",
                    "target": "由两圆心距离等于2r读出最大半径",
                    "operation": "push the center-distance relation to one decisive boundary check",
                    "success_signal": "the decisive center-distance equation is explicit",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "对称", "投影", "读出"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "矩形8x9截面内两个相同圆与上下边、左右边及彼此外切",
                    "controlled_object": "由两圆心距离等于2r读出最大半径",
                    "current_seam": "由两圆心距离等于2r读出最大半径",
                    "current_debt": "在二维截面上把横向距离 8-2r 与纵向距离 9-2r 写进外切方程",
                    "reason": "the current layer must visibly cash the live skill combination into the solution text",
                    "leading_skill_if_any": "极限边界",
                    "event_owned": True,
                    "transition_change": "bound one geometry-owned touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["极限边界", "对称", "投影", "读出"],
                    "authorized_bite": {
                        "kind": "check",
                        "target": "由两圆心距离等于2r读出最大半径",
                        "operation": "push the center-distance relation to one decisive boundary check",
                        "success_signal": "the decisive center-distance equation is explicit",
                        "owner_skill_if_any": "极限边界",
                        "owner_skill_combo_if_any": ["极限边界", "对称", "投影", "读出"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": (
                                "极限边界：在控制截面里把相切条件全部取满，所以圆心横向距离为 8-2r，纵向距离为 9-2r，"
                                "再由两圆外切得到 (8-2r)^2+(9-2r)^2=(2r)^2，解得 r=5/2。"
                            ),
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("当前应先由 `极限边界` 接管", str(exc.exception))

    def test_execute_local_accepts_blind_worked_step_with_only_leading_skill_explicit_when_only_one_problem_facing_skill_is_live(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "索引层模型：删去两点后剩余下标能否拆成四项等差组",
                "current_seam": "先做局部模板再统计合法删对",
                "current_debt": "把三问都压到索引层的删对结构里",
                "next_bite": "完成模板构造与下界计数",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "先做局部模板再统计合法删对",
                    "operation": "split the live object into template blocks and count one rigid lower bound",
                    "success_signal": "the local template family and lower bound are explicit",
                    "owner_skill_if_any": "状态拆分",
                    "owner_skill_combo_if_any": ["状态拆分", "读出"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "索引层模型：删去两点后剩余下标能否拆成四项等差组",
                    "controlled_object": "先做局部模板再统计合法删对",
                    "current_seam": "先做局部模板再统计合法删对",
                    "current_debt": "把三问都压到索引层的删对结构里",
                    "reason": "the current layer must visibly cash the live skill combination into the solution text",
                    "leading_skill_if_any": "状态拆分",
                    "event_owned": True,
                    "transition_change": "bound one structure-owned touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["状态拆分", "读出"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "先做局部模板再统计合法删对",
                        "operation": "split the live object into template blocks and count one rigid lower bound",
                        "success_signal": "the local template family and lower bound are explicit",
                        "owner_skill_if_any": "状态拆分",
                        "owner_skill_combo_if_any": ["状态拆分", "读出"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            exit_code = command_execute_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "worked_step": (
                            "状态拆分：先把整题压成索引层模板问题，再在各个模板块里组织合法删对，"
                            "最后把概率层改成下界计数。"
                        ),
                        "summary": "",
                        "output_file": "evidence.md",
                        "cosmetic_only": None,
                        "contains_unsupported": None,
                        "contains_placeholder": None,
                    },
                )()
            )
            saved_state = json.loads(state_path.read_text(encoding="utf-8"))

            self.assertEqual(exit_code, 0)
            self.assertTrue((Path(tmpdir) / "evidence.md").exists())
            self.assertEqual(saved_state.get("materialization_evidence", {}).get("kind"), "file")
            self.assertFalse(
                [
                    problem
                    for problem in build_report(saved_state, state_path).get("problems", [])
                    if "materialization_evidence" in problem
                ]
            )

    def test_execute_local_refuses_state_backed_foreign_problem_skill_relabeling(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "双根层：同一高度截到两根后要把乘积压成标准不等式",
                "current_seam": "先把双根同高结构压成单参数，再完成最终比较",
                "current_debt": "不能只靠图像主线伪装成多技能组合",
                "next_bite": "在当前层完成一次真实 execute-local",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "先把双根同高结构压成单参数，再完成最终比较",
                    "operation": "rewrite the same-height double-root layer into one parameter and one decisive inequality",
                    "success_signal": "the ratio carrier and decisive inequality are explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "读出", "见证", "极限边界", "对称"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "双根层：同一高度截到两根后要把乘积压成标准不等式",
                    "controlled_object": "先把双根同高结构压成单参数，再完成最终比较",
                    "current_seam": "先把双根同高结构压成单参数，再完成最终比较",
                    "current_debt": "不能只靠图像主线伪装成多技能组合",
                    "reason": "the current layer must visibly cash the live skill combination into the solution text",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one double-root touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "读出", "见证", "极限边界", "对称"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "先把双根同高结构压成单参数，再完成最终比较",
                        "operation": "rewrite the same-height double-root layer into one parameter and one decisive inequality",
                        "success_signal": "the ratio carrier and decisive inequality are explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "读出", "见证", "极限边界", "对称"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": (
                                "赋值：先取一个代表参数把双根压到同一层。\n"
                                "图像：再从同高结构读出比较骨架。"
                            ),
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("non-active skill labels", str(exc.exception))
        self.assertIn("Current explicit combo", str(exc.exception))

    def test_execute_local_persists_full_worked_step_text(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "a=1+(lnx)/x 这条值载体图像",
                "current_seam": "同一条值载体上统一三问",
                "current_debt": "不要回到普通导数分类，要先把值载体真的立起来",
                "next_bite": "先把参数题改写到同一条值载体图像上",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "同一条值载体上统一三问",
                    "operation": "use 图像 to externalize one shared value carrier before ordinary continuation",
                    "success_signal": "the shared value carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "a=1+(lnx)/x 这条值载体图像",
                    "controlled_object": "同一条值载体上统一三问",
                    "current_seam": "同一条值载体上统一三问",
                    "current_debt": "不要回到普通导数分类，要先把值载体真的立起来",
                    "reason": "当前层必须先把共享值载体真的画出来",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one graph-owned touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "同一条值载体上统一三问",
                        "operation": "use 图像 to externalize one shared value carrier before ordinary continuation",
                        "success_signal": "the shared value carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    },
                },
            }
        )

        worked_step = (
            "赋值：先把原方程改写成 a=1+(lnx)/x。\n"
            "图像：把三问统一压到这条值载体 y=1+(lnx)/x 上，先看横线截点、峰值和左端奇点。\n"
            "极限边界：记录 x->0+ 时左端下冲，和 x=e 处峰值 1+1/e。"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            exit_code = command_execute_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "worked_step": worked_step,
                        "summary": "",
                        "output_file": None,
                        "cosmetic_only": None,
                        "contains_unsupported": None,
                        "contains_placeholder": None,
                    },
                )()
            )
            saved_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            saved_state.get("materialization_evidence", {}).get("worked_step"),
            worked_step,
        )
        self.assertFalse(
            [
                problem
                for problem in build_report(saved_state, state_path).get("problems", [])
                if "materialization_evidence" in problem
            ]
        )

    def test_execute_local_refuses_partial_multi_skill_expression(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "共享值载体",
                "current_seam": "共享值载体图像",
                "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                "next_bite": "在统一值载体上画图并压出边界与锚点",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "共享值载体图像",
                    "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                    "success_signal": "the shared carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "共享值载体",
                    "controlled_object": "共享值载体图像",
                    "current_seam": "共享值载体图像",
                    "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                    "reason": "the current layer already belongs to one multi-skill carrier-building combination",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one carrier-building touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "共享值载体图像",
                        "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                        "success_signal": "the shared carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": (
                                "图像：先把函数大致画出来。\n"
                                "然后设新变量并直接分类计算，把三问分别算完。"
                            ),
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))

    def test_execute_local_refuses_ordinary_action_without_counter_question_handoff(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "共享值载体",
                "current_seam": "共享值载体图像",
                "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                "next_bite": "在统一值载体上画图并压出边界与锚点",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "共享值载体图像",
                    "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                    "success_signal": "the shared carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "共享值载体",
                    "controlled_object": "共享值载体图像",
                    "current_seam": "共享值载体图像",
                    "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                    "reason": "the current layer already belongs to one multi-skill carrier-building combination",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one carrier-building touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "共享值载体图像",
                        "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                        "success_signal": "the shared carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "设一个辅助函数 g(x)，再求导分类，最后回去整理答案。",
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))

    def test_execute_local_accepts_counter_question_denial_and_skill_handoff(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "共享值载体",
                "current_seam": "共享值载体图像",
                "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                "next_bite": "在统一值载体上画图并压出边界与锚点",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "共享值载体图像",
                    "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                    "success_signal": "the shared carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "共享值载体",
                    "controlled_object": "共享值载体图像",
                    "current_seam": "共享值载体图像",
                    "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                    "reason": "the current layer already belongs to one multi-skill carrier-building combination",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one carrier-building touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "共享值载体图像",
                        "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                        "success_signal": "the shared carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            exit_code = command_execute_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "worked_step": (
                            "这一步真的需要先设辅助函数吗？其实并不需要设，也不需要先求导分类。\n"
                            "应该先图像：把三问统一压到共享值载体上，再钉住边界与锚点。"
                        ),
                        "summary": "",
                        "output_file": "evidence.md",
                        "cosmetic_only": None,
                        "contains_unsupported": None,
                        "contains_placeholder": None,
                    },
                )()
            )
            saved_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(saved_state.get("materialization_evidence", {}).get("kind"), "file")

    def test_execute_local_refuses_counter_question_handoff_that_reverts_to_auxiliary_assignment(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "共享值载体",
                "current_seam": "共享值载体图像",
                "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                "next_bite": "在统一值载体上画图并压出边界与锚点",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "共享值载体图像",
                    "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                    "success_signal": "the shared carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "共享值载体",
                    "controlled_object": "共享值载体图像",
                    "current_seam": "共享值载体图像",
                    "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                    "reason": "the current layer already belongs to one multi-skill carrier-building combination",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one carrier-building touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "共享值载体图像",
                        "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                        "success_signal": "the shared carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": (
                                "这一步真的需要先设辅助函数吗？其实并不需要设，也不需要先求导分类。\n"
                                "应该先图像：把三问统一压到共享值载体上。\n"
                                "图像：u=\\ln x，把等值条件直接压到新变量上再继续。"
                            ),
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("live skill-owned layer", str(exc.exception))
        self.assertIn("当前应先由 `图像` 接管", str(exc.exception))

    def test_execute_local_refuses_explanation_without_touch_on_live_skill_layer(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "共享值载体",
                "current_seam": "共享值载体图像",
                "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                "next_bite": "在统一值载体上画图并压出边界与锚点",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "共享值载体图像",
                    "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                    "success_signal": "the shared carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "共享值载体",
                    "controlled_object": "共享值载体图像",
                    "current_seam": "共享值载体图像",
                    "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                    "reason": "the current layer already belongs to one multi-skill carrier-building combination",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one carrier-building touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "共享值载体图像",
                        "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                        "success_signal": "the shared carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "图像：先继续解释这条值载体为什么统一三问，补充说明之后自然就都清楚了。",
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("explanation without touch", str(exc.exception))

    def test_execute_local_refuses_asked_medium_rush_before_closure(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "共享值载体",
                "current_seam": "共享值载体图像",
                "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                "next_bite": "在统一值载体上画图并压出边界与锚点",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "共享值载体图像",
                    "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                    "success_signal": "the shared carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "共享值载体",
                    "controlled_object": "共享值载体图像",
                    "current_seam": "共享值载体图像",
                    "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                    "reason": "the current layer already belongs to one multi-skill carrier-building combination",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one carrier-building touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "共享值载体图像",
                        "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                        "success_signal": "the shared carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "图像：先把值载体立起来，然后直接把最终答案写进 answer.md。",
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("asked medium", str(exc.exception))

    def test_execute_local_refuses_stale_counterexample_continuation_after_structural_return(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                "current_seam": "derive the surviving tree-weight invariant after the counterexample killed the fake prefix heuristic",
                "current_debt": "compress the real invariant instead of repeating the hostile falsifier",
                "next_bite": "return to the live structural carrier",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "derive the surviving tree-weight invariant after the counterexample killed the fake prefix heuristic",
                    "operation": "compress the surviving invariant on the current thinner carrier",
                    "success_signal": "the real invariant is explicit",
                    "owner_skill_if_any": "守恒",
                    "owner_skill_combo_if_any": ["守恒", "状态拆分", "对称"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                    "controlled_object": "derive the surviving tree-weight invariant after the counterexample killed the fake prefix heuristic",
                    "current_seam": "derive the surviving tree-weight invariant after the counterexample killed the fake prefix heuristic",
                    "current_debt": "compress the real invariant instead of repeating the hostile falsifier",
                    "reason": "authority has already returned to the structural carrier",
                    "leading_skill_if_any": "守恒",
                    "event_owned": True,
                    "transition_change": "bound one structural followup after the hostile falsifier",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["守恒", "状态拆分", "对称"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "derive the surviving tree-weight invariant after the counterexample killed the fake prefix heuristic",
                        "operation": "compress the surviving invariant on the current thinner carrier",
                        "success_signal": "the real invariant is explicit",
                        "owner_skill_if_any": "守恒",
                        "owner_skill_combo_if_any": ["守恒", "状态拆分", "对称"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "反问：继续拿 (() 这个反例说事，看看普通 balanced-prefix heuristic 为什么还不行。",
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("old counterexample thread", str(exc.exception))

    def test_execute_local_refuses_derivative_notation_as_ordinary_regrowth(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "函数 D(u)=ln((1+u)/(1-u))-2u（0<u<1） 的符号",
                "current_seam": "比较 t=1 两侧等距点时，右侧函数值更大",
                "current_debt": "证明对 0<u<1 恒有 D(u)>0",
                "next_bite": "让图像与极限边界接管",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "比较 t=1 两侧等距点时，右侧函数值更大",
                    "operation": "draw one minimal problem diagram and expose the decisive ordering feature",
                    "success_signal": "the decisive controller is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "极限边界", "对称"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "函数 D(u)=ln((1+u)/(1-u))-2u（0<u<1） 的符号",
                    "controlled_object": "比较 t=1 两侧等距点时，右侧函数值更大",
                    "current_seam": "比较 t=1 两侧等距点时，右侧函数值更大",
                    "current_debt": "证明对 0<u<1 恒有 D(u)>0",
                    "reason": "图像与极限边界已经接管这一层",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one structural followup",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "极限边界", "对称"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "比较 t=1 两侧等距点时，右侧函数值更大",
                        "operation": "draw one minimal problem diagram and expose the decisive ordering feature",
                        "success_signal": "the decisive controller is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "极限边界", "对称"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "图像：把峰顶图像立起来，然后算 D'(u)=2u^2/(1-u^2)>0，所以 D(u)>0。",
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("live skill-owned layer", str(exc.exception))
        self.assertIn("当前应先由 `图像` 接管", str(exc.exception))

    def test_execute_local_refuses_skill_labeled_subscript_prime_case_split_regrowth(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "方程 f_a(x)=0 的零点个数",
                "current_seam": "同一条横线与单峰图像的交点结构",
                "current_debt": "先在图像上统一参数与零点个数，不回到普通导数分类",
                "next_bite": "让图像与状态拆分接管",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "同一条横线与单峰图像的交点结构",
                    "operation": "use 图像 to externalize the single-peak intersection carrier",
                    "success_signal": "the single-peak carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "方程 f_a(x)=0 的零点个数",
                    "controlled_object": "同一条横线与单峰图像的交点结构",
                    "current_seam": "同一条横线与单峰图像的交点结构",
                    "current_debt": "先在图像上统一参数与零点个数，不回到普通导数分类",
                    "reason": "图像与状态拆分已经接管这一层",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one graph-skeleton touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "同一条横线与单峰图像的交点结构",
                        "operation": "use 图像 to externalize the single-peak intersection carrier",
                        "success_signal": "the single-peak carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                    },
                    "lighting_if_any": {
                        "lit_skill_if_any": "图像",
                        "candidate_skills_if_any": ["图像", "状态拆分", "投影"],
                        "supporting_skills_if_any": ["状态拆分", "投影"],
                        "verify_touch_if_any": {
                            "target": "同一条横线与单峰图像的交点结构",
                            "kind": "write",
                        },
                        "role_split_if_any": {
                            "primary_skill_if_any": "图像",
                            "supporting_skills_if_any": ["状态拆分", "投影"],
                            "check_skill_if_any": "投影",
                            "check_kind_if_any": "write",
                            "check_target_if_any": "同一条横线与单峰图像的交点结构",
                            "ordinary_operations_are_not_skills": True,
                        },
                        "ordinary_operations_are_not_skills": True,
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": (
                                "图像：先把单峰交点图像立起来。\n"
                                "状态拆分：再看 f'_a(x)=\\frac{1-\\ln x}{x^2}，分两种情形讨论 a\\le 1 和 a>1。"
                            ),
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("live skill-owned layer", str(exc.exception))
        self.assertIn("当前应先由 `图像` 接管", str(exc.exception))

    def test_execute_local_refuses_case_split_when_ordinary_helper_claims_live_layer(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "方程 f_a(x)=0 的零点个数",
                "current_seam": "同一条横线与单峰图像的交点结构",
                "current_debt": "先在图像上统一参数与零点个数，不回到普通导数分类",
                "next_bite": "让图像与状态拆分接管",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "同一条横线与单峰图像的交点结构",
                    "operation": "use 图像 to externalize the single-peak intersection carrier",
                    "success_signal": "the single-peak carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "方程 f_a(x)=0 的零点个数",
                    "controlled_object": "同一条横线与单峰图像的交点结构",
                    "current_seam": "同一条横线与单峰图像的交点结构",
                    "current_debt": "先在图像上统一参数与零点个数，不回到普通导数分类",
                    "reason": "图像与状态拆分已经接管这一层",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one graph-skeleton touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "同一条横线与单峰图像的交点结构",
                        "operation": "use 图像 to externalize the single-peak intersection carrier",
                        "success_signal": "the single-peak carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                    },
                    "lighting_if_any": {
                        "lit_skill_if_any": "图像",
                        "candidate_skills_if_any": ["图像", "状态拆分", "投影"],
                        "supporting_skills_if_any": ["状态拆分", "投影"],
                        "verify_touch_if_any": {
                            "target": "同一条横线与单峰图像的交点结构",
                            "kind": "write",
                        },
                        "role_split_if_any": {
                            "primary_skill_if_any": "图像",
                            "supporting_skills_if_any": ["状态拆分", "投影"],
                            "check_skill_if_any": "投影",
                            "check_kind_if_any": "write",
                            "check_target_if_any": "同一条横线与单峰图像的交点结构",
                            "ordinary_operations_are_not_skills": True,
                        },
                        "ordinary_operations_are_not_skills": True,
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": (
                                "图像：先把单峰交点图像立起来。\n"
                                "分类：再把 a<=1 和 a>1 分成两档，分别算每档的交点个数。"
                            ),
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("live skill-owned layer", str(exc.exception))
        self.assertIn("当前应先由 `图像` 接管", str(exc.exception))

    def test_execute_local_refuses_subordinate_derivative_even_when_skill_layer_is_live(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "函数 D(u)=ln((1+u)/(1-u))-2u（0<u<1） 的符号",
                "current_seam": "比较 t=1 两侧等距点时，右侧函数值更大",
                "current_debt": "证明对 0<u<1 恒有 D(u)>0",
                "next_bite": "让图像与极限边界接管",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "比较 t=1 两侧等距点时，右侧函数值更大",
                    "operation": "draw one minimal problem diagram and expose the decisive ordering feature",
                    "success_signal": "the decisive controller is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "极限边界", "对称"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "函数 D(u)=ln((1+u)/(1-u))-2u（0<u<1） 的符号",
                    "controlled_object": "比较 t=1 两侧等距点时，右侧函数值更大",
                    "current_seam": "比较 t=1 两侧等距点时，右侧函数值更大",
                    "current_debt": "证明对 0<u<1 恒有 D(u)>0",
                    "reason": "图像与极限边界已经接管这一层",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one structural followup",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "极限边界", "对称"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "比较 t=1 两侧等距点时，右侧函数值更大",
                        "operation": "draw one minimal problem diagram and expose the decisive ordering feature",
                        "success_signal": "the decisive controller is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "极限边界", "对称"],
                    },
                    "lighting_if_any": {
                        "lit_skill_if_any": "图像",
                        "candidate_skills_if_any": ["图像", "极限边界", "对称"],
                        "supporting_skills_if_any": ["极限边界", "对称"],
                        "verify_touch_if_any": {
                            "target": "比较 t=1 两侧等距点时，右侧函数值更大",
                            "kind": "check",
                        },
                        "role_split_if_any": {
                            "primary_skill_if_any": "图像",
                            "supporting_skills_if_any": ["极限边界", "对称"],
                            "check_skill_if_any": "极限边界",
                            "check_kind_if_any": "check",
                            "check_target_if_any": "比较 t=1 两侧等距点时，右侧函数值更大",
                            "ordinary_operations_are_not_skills": True,
                        },
                        "ordinary_operations_are_not_skills": True,
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "图像：先把比较图像立起来，再借导数只做检查，验证极限边界方向没有翻转。",
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("当前应先由 `图像` 接管", str(exc.exception))

    def test_execute_local_refuses_subordinate_case_split_when_skill_layer_stays_owner(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "方程 f_a(x)=0 的零点个数",
                "current_seam": "同一条横线与单峰图像的交点结构",
                "current_debt": "先在图像上统一参数与零点个数，不回到普通导数分类",
                "next_bite": "让图像与状态拆分接管",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "同一条横线与单峰图像的交点结构",
                    "operation": "use 图像 to externalize the single-peak intersection carrier",
                    "success_signal": "the single-peak carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "方程 f_a(x)=0 的零点个数",
                    "controlled_object": "同一条横线与单峰图像的交点结构",
                    "current_seam": "同一条横线与单峰图像的交点结构",
                    "current_debt": "先在图像上统一参数与零点个数，不回到普通导数分类",
                    "reason": "图像与状态拆分已经接管这一层",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one graph-skeleton touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "同一条横线与单峰图像的交点结构",
                        "operation": "use 图像 to externalize the single-peak intersection carrier",
                        "success_signal": "the single-peak carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                    },
                    "lighting_if_any": {
                        "lit_skill_if_any": "图像",
                        "candidate_skills_if_any": ["图像", "状态拆分", "投影"],
                        "supporting_skills_if_any": ["状态拆分", "投影"],
                        "verify_touch_if_any": {
                            "target": "同一条横线与单峰图像的交点结构",
                            "kind": "write",
                        },
                        "role_split_if_any": {
                            "primary_skill_if_any": "图像",
                            "supporting_skills_if_any": ["状态拆分", "投影"],
                            "check_skill_if_any": "投影",
                            "check_kind_if_any": "write",
                            "check_target_if_any": "同一条横线与单峰图像的交点结构",
                            "ordinary_operations_are_not_skills": True,
                        },
                        "ordinary_operations_are_not_skills": True,
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": (
                                "图像：先把单峰交点图像立起来，再让分类只做辅助检查，"
                                "验证同一条横线与单峰图像的交点结构在 a<=1 和 a>1 两侧都没有换层。"
                            ),
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("当前应先由 `图像` 接管", str(exc.exception))

    def test_execute_local_refuses_subordinate_equation_solving_when_skill_layer_stays_owner(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "方程 f_a(x)=0 的零点个数",
                "current_seam": "同一条横线与单峰图像的交点结构",
                "current_debt": "先在图像上统一参数与零点个数，不回到普通方程求解",
                "next_bite": "让图像与状态拆分接管",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "同一条横线与单峰图像的交点结构",
                    "operation": "use 图像 to externalize the single-peak intersection carrier",
                    "success_signal": "the single-peak carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "方程 f_a(x)=0 的零点个数",
                    "controlled_object": "同一条横线与单峰图像的交点结构",
                    "current_seam": "同一条横线与单峰图像的交点结构",
                    "current_debt": "先在图像上统一参数与零点个数，不回到普通方程求解",
                    "reason": "图像与状态拆分已经接管这一层",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one graph-skeleton touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "同一条横线与单峰图像的交点结构",
                        "operation": "use 图像 to externalize the single-peak intersection carrier",
                        "success_signal": "the single-peak carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "状态拆分", "投影"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": (
                                "图像：先把单峰交点图像立起来，再联立等值关系解方程，"
                                "把两个交点直接算出来。"
                            ),
                            "summary": "",
                            "output_file": "evidence.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("当前应先由 `图像` 接管", str(exc.exception))

    def test_set_core_refuses_ordinary_next_bite_inside_live_skill_layer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state = copy.deepcopy(DEFAULT_STATE)
            state.update(
                {
                    "current_object": "函数 D(u)=ln((1+u)/(1-u))-2u（0<u<1） 的符号",
                    "current_seam": "比较 t=1 两侧等距点时，右侧函数值更大",
                    "current_debt": "让图像与极限边界一起接管这一层",
                    "next_bite": "让图像与极限边界一起接管这一层",
                    "asked_medium_surface": "final.md",
                    "release_veto": True,
                    "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                    "layer_composition_if_any": {
                        "active": True,
                        "surface": "fresh_blind_first_touch",
                        "layer_object": "函数 D(u)=ln((1+u)/(1-u))-2u（0<u<1） 的符号",
                        "controlled_object": "比较 t=1 两侧等距点时，右侧函数值更大",
                        "current_seam": "比较 t=1 两侧等距点时，右侧函数值更大",
                        "current_debt": "让图像与极限边界一起接管这一层",
                        "reason": "fresh blind first layer must bind one explicit project skill combination before ordinary continuation regains value",
                        "leading_skill_if_any": "图像",
                        "event_owned": False,
                        "forbid_ordinary_regrowth": True,
                        "must_bind_local_bite": True,
                        "must_spend_handoff": False,
                        "active_skill_combo_if_any": ["图像", "极限边界", "对称"],
                    },
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as exc:
                command_set_core(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "current_object": "函数 D(u)=ln((1+u)/(1-u))-2u（0<u<1） 的符号",
                            "current_seam": "比较 t=1 两侧等距点时，右侧函数值更大",
                            "current_debt": "证明对 0<u<1 恒有 D(u)>0",
                            "next_bite": "对 D(u) 求导并用 D'(u)>0 判定单调性",
                            "asked_medium_surface": None,
                            "revocation_handle": None,
                            "uncertainty_mode": None,
                            "primary_slot": None,
                            "release_veto": None,
                        },
                    )()
                )

        self.assertIn("set-core refused", str(exc.exception))
        self.assertIn("ordinary fallback action", str(exc.exception))
        self.assertIn("freshly narrowed live layer", str(exc.exception))

    def test_build_report_warns_when_asked_medium_exists_before_runtime_materialization(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "local layer still open",
                "current_seam": "same local layer",
                "current_debt": "still unpaid",
                "next_bite": "bind one honest local bite",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "output_status": {
                    "touched": False,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            (Path(tmpdir) / "final.md").write_text("普通题解：先求导分类。\n", encoding="utf-8")

            report = build_report(state, state_path)

        self.assertIn(
            "asked medium file already exists on disk before runtime-owned materialization; treat it as bypass/manual output",
            report.get("warnings", []),
        )

    def test_reopened_layer_bridge_does_not_return_to_previous_thick_object(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "thin ledger",
                "current_seam": "remaining signed gap on thin ledger",
                "current_debt": "close the visible gap without rebuilding the original carrier",
                "next_bite": "return to the original thick carrier and explain it globally",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "carrier_handoff_if_any": {
                    "trigger": "same_carrier_change",
                    "from_slot": "solve",
                    "to_object": "thin ledger",
                    "winning_pressure": "structure survives more honestly on the thinner ledger",
                    "why_local": "the governing gap becomes visible there",
                    "warm_field": {
                        "active_pressures": ["状态拆分", "投影"],
                        "cheap_check": "split the thin ledger once",
                        "evidence_basis": "cheap_check",
                    },
                },
            }
        )

        bridge = derive_skill_authority_bridge(
            state,
            [],
            primitive_field_override={
                "layer_object": "thin ledger",
                "active_primitives": ["状态拆分", "投影"],
                "why_now": "the thinner object exposes the remaining gap",
                "selection_basis": "explicit_hint",
                "evidence_basis": "cheap_check",
                "tie_break_check": "split the thin ledger once",
            },
            skill_competition_override={
                "winning_skill_if_any": "状态拆分",
                "candidates": [
                    {
                        "skill": "状态拆分",
                        "touch_target": "thin ledger",
                        "supporting_skills_if_any": ["投影"],
                    },
                    {
                        "skill": "投影",
                        "touch_target": "thin ledger",
                        "supporting_skills_if_any": ["状态拆分"],
                    },
                ],
                "coactive_skills_if_any": ["状态拆分", "投影"],
            },
        )

        self.assertIsInstance(bridge, dict)
        self.assertEqual(bridge.get("winning_skill_if_any"), "状态拆分")
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertEqual(touch.get("target"), "thin ledger")
        self.assertNotEqual(touch.get("target"), "original thick carrier")
        self.assertNotEqual(touch.get("owner_skill_if_any"), "读出")

    def test_skill_coaching_surface_exposes_counter_question_denial_and_handoff(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "共享值载体",
                "current_seam": "共享值载体图像",
                "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                "next_bite": "在统一值载体上画图并压出边界与锚点",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "共享值载体图像",
                    "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                    "success_signal": "the shared carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "共享值载体",
                    "controlled_object": "共享值载体图像",
                    "current_seam": "共享值载体图像",
                    "current_debt": "把三问压到同一个值载体后再读边界与锚点",
                    "reason": "the current layer already belongs to one multi-skill carrier-building combination",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one carrier-building touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "共享值载体图像",
                        "operation": "draw one minimal carrier picture, anchor one decisive value, and expose the boundary controller",
                        "success_signal": "the shared carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "赋值", "极限边界"],
                    },
                },
            }
        )

        surface = derive_local_skill_coaching_surface(state, [])
        self.assertIsInstance(surface, dict)
        self.assertIn("真的需要", surface.get("ordinary_action_counter_question_if_any", ""))
        self.assertIn("不需要", surface.get("ordinary_action_denial_if_any", ""))
        self.assertIn("图像", surface.get("skill_positive_handoff_if_any", ""))
        self.assertIn("ordinary_counter_question", surface.get("speech_acts", {}))

    def test_execute_local_refuses_skill_named_result_only_summary(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "h(x)=ln x / x 的单峰图像",
                "current_seam": "同一条横线与单峰图像的交点结构",
                "current_debt": "先在图像上统一零点个数和双根区域",
                "next_bite": "先做图像层统一读出",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "同一条横线与单峰图像的交点结构",
                    "operation": "use 图像 to externalize the single-peak intersection carrier",
                    "success_signal": "the single-peak carrier is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "读出", "见证"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "h(x)=ln x / x 的单峰图像",
                    "controlled_object": "同一条横线与单峰图像的交点结构",
                    "current_seam": "同一条横线与单峰图像的交点结构",
                    "current_debt": "先在图像上统一零点个数和双根区域",
                    "reason": "当前层必须把图像层真的做出来",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one graph-owned touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "读出", "见证"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "同一条横线与单峰图像的交点结构",
                        "operation": "use 图像 to externalize the single-peak intersection carrier",
                        "success_signal": "the single-peak carrier is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "读出", "见证"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "图像+读出 统一解决了第一问，并锁定了第二问只发生在 1<a<1+1/e。",
                            "summary": "",
                            "output_file": None,
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("only reported that something was solved", str(exc.exception))

    def test_execute_local_refuses_direct_write_to_asked_medium_even_with_skill_expression(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "薄对象",
                "current_seam": "当前层局部缺口",
                "current_debt": "把当前层缺口做成可验证文本",
                "next_bite": "在当前层完成一次真实 execute-local",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "check",
                    "target": "当前层局部缺口",
                    "operation": "use 图像 and 极限边界 to cash the current layer into one visible step",
                    "success_signal": "the current-layer gap is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "极限边界", "对称"],
                },
                "layer_composition_if_any": {
                    "active": True,
                    "surface": "bound_program",
                    "layer_object": "薄对象",
                    "controlled_object": "当前层局部缺口",
                    "current_seam": "当前层局部缺口",
                    "current_debt": "把当前层缺口做成可验证文本",
                    "reason": "当前层必须先留下真实 skill-owned touch",
                    "leading_skill_if_any": "图像",
                    "event_owned": True,
                    "transition_change": "bound one current-layer touch",
                    "forbid_ordinary_regrowth": True,
                    "active_skill_combo_if_any": ["图像", "极限边界", "对称"],
                    "authorized_bite": {
                        "kind": "check",
                        "target": "当前层局部缺口",
                        "operation": "use 图像 and 极限边界 to cash the current layer into one visible step",
                        "success_signal": "the current-layer gap is explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "极限边界", "对称"],
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "图像：先画控制骨架。极限边界：再把当前层缺口压成可验证边界。",
                            "summary": "",
                            "output_file": "answer.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("direct writes to the asked medium bypass skill-serialized closure", str(exc.exception))

    def test_execute_local_refuses_output_path_escape_outside_state_directory(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "薄对象",
                "current_seam": "当前层局部缺口",
                "current_debt": "把当前层缺口做成可验证文本",
                "next_bite": "在当前层完成一次真实 execute-local",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": "当前层局部缺口",
                    "operation": "use 图像 to cash the current layer into one visible step",
                    "success_signal": "the current-layer gap is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "极限边界"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "图像：先画控制骨架。",
                            "summary": "",
                            "output_file": "..\\outside.md",
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("output path refused", str(exc.exception))

    def test_execute_local_refuses_absolute_output_path_outside_state_directory(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "薄对象",
                "current_seam": "当前层局部缺口",
                "current_debt": "把当前层缺口做成可验证文本",
                "next_bite": "在当前层完成一次真实 execute-local",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": "当前层局部缺口",
                    "operation": "use 图像 to cash the current layer into one visible step",
                    "success_signal": "the current-layer gap is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "极限边界"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            outside_path = Path(tmpdir).parent / "outside.md"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_execute_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "worked_step": "图像：先画控制骨架。",
                            "summary": "",
                            "output_file": str(outside_path),
                            "cosmetic_only": None,
                            "contains_unsupported": None,
                            "contains_placeholder": None,
                        },
                    )()
                )

        self.assertIn("output path refused", str(exc.exception))

    def test_execute_then_land_local_reopens_new_layer_without_asked_medium_hijack(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "Characterize strings T with deformed balance and minimize additions around S",
                "current_seam": "compress deformed-balance definition into a direct prefix/suffix balance condition",
                "current_debt": "find the thinner exact carrier that separates structural validity from ordinary balanced-prefix repair",
                "next_bite": "draw one minimal problem diagram for deformed balance and rewrite the governing relation",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "compress deformed-balance definition into a direct prefix/suffix balance condition",
                    "operation": "draw one minimal problem diagram for compress deformed-balance definition into a direct prefix/suffix balance condition and rewrite the governing relation there",
                    "success_signal": "one thinner carrier became explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "对称", "见证", "极限边界", "状态拆分", "守恒"],
                },
                "output_status": {
                    "touched": False,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            command_execute_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "worked_step": "图像：把 deformed balance 看成比普通 balanced 更细的结构筛子。",
                        "summary": "压成更薄结构对象",
                        "output_file": None,
                        "cosmetic_only": False,
                        "contains_unsupported": False,
                        "contains_placeholder": False,
                    },
                )()
            )
            command_land_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "current_object": "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                        "current_seam": "ordinary balanced-prefix repair is not the controller; isolate the exact structural criterion",
                        "current_debt": "compress the real controller into a smaller family that can drive minimal prefix/suffix repair",
                        "next_bite": "compare the candidate prefix families on the thinner structural carrier",
                    },
                )()
            )
            landed_state = json.loads(state_path.read_text(encoding="utf-8"))

        layer = landed_state.get("layer_composition_if_any", {})
        self.assertEqual(landed_state.get("current_object"), "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes")
        self.assertIsNone(landed_state.get("bound_program"))
        self.assertFalse(landed_state.get("output_status", {}).get("touched"))
        self.assertEqual(layer.get("surface"), "takeover_recomposition")
        self.assertTrue(layer.get("must_bind_local_bite"))
        self.assertNotEqual(layer.get("authorized_bite", {}).get("target"), "answer.md")
        self.assertEqual(
            layer.get("authorized_bite", {}).get("target"),
            "ordinary balanced-prefix repair is not the controller; isolate the exact structural criterion",
        )
        self.assertNotEqual(layer.get("leading_skill_if_any"), "图像")
        self.assertIn("compress deformed-balance definition", layer.get("transition_change", ""))
        self.assertIn("ordinary balanced-prefix repair", layer.get("transition_change", ""))

    def test_post_land_pending_runtime_contract_requires_bind_local_on_reopened_layer(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "Characterize strings T with deformed balance and minimize additions around S",
                "current_seam": "compress deformed-balance definition into a direct prefix/suffix balance condition",
                "current_debt": "find the thinner exact carrier that separates structural validity from ordinary balanced-prefix repair",
                "next_bite": "draw one minimal problem diagram for deformed balance and rewrite the governing relation",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "compress deformed-balance definition into a direct prefix/suffix balance condition",
                    "operation": "draw one minimal problem diagram for compress deformed-balance definition into a direct prefix/suffix balance condition and rewrite the governing relation there",
                    "success_signal": "one thinner carrier became explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "对称", "见证", "极限边界", "状态拆分", "守恒"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            apply_same_carrier_landing(
                loaded_state,
                state_path,
                next_object="deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                next_seam="ordinary balanced-prefix repair is not the controller; isolate the exact structural criterion",
                next_debt="compress the real controller into a smaller family that can drive minimal prefix/suffix repair",
                next_bite="compare the candidate prefix families on the thinner structural carrier",
            )

        contract = pending_runtime_execution_contract(loaded_state)
        self.assertIsInstance(contract, dict)
        self.assertEqual(contract.get("required_action"), "bind_local")
        self.assertEqual(contract.get("allowed_transition_surfaces"), ["bind_local"])
        self.assertEqual(contract.get("surface"), "takeover_recomposition")

    def test_post_land_reopened_layer_exposes_current_semantic_owner_before_next_spend(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "第一层对象",
                "current_seam": "第一层 seam",
                "current_debt": "第一层 debt",
                "next_bite": "第一层 bite",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "rebind_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": "第一层 seam",
                    "operation": "use 图像 to touch the first layer",
                    "success_signal": "the first-layer gap is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "极限边界"],
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "summary": "skill-expressive answer already written",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "landed_next_touch_if_any": {
                    "kind": "check",
                    "target": "第二层 seam",
                    "operation": "use 对称 to touch the second layer",
                    "success_signal": "the second-layer gap is explicit",
                    "owner_skill_if_any": "对称",
                    "owner_skill_combo_if_any": ["对称", "图像"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("画图：...\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(answer_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            with patch(
                "runtime_guard._sanitize_public_skill_competition",
                side_effect=lambda payload: payload,
            ):
                apply_same_carrier_landing(
                    loaded_state,
                    state_path,
                    next_object="第二层对象",
                    next_seam="第二层 seam",
                    next_debt="第二层 debt",
                    next_bite="第二层 bite",
                )

        pending = pending_runtime_execution_contract(loaded_state)
        reopened_layer = loaded_state.get("layer_composition_if_any", {})
        reopened_bite = reopened_layer.get("authorized_bite", {})
        self.assertEqual(loaded_state.get("bound_program"), None)
        self.assertTrue(reopened_layer.get("event_owned"))
        self.assertEqual(reopened_layer.get("leading_skill_if_any"), reopened_bite.get("owner_skill_if_any"))
        self.assertIn(reopened_bite.get("owner_skill_if_any"), reopened_bite.get("owner_skill_combo_if_any", []))
        self.assertEqual(pending.get("required_action"), "bind_local")
        self.assertEqual(pending.get("surface"), "takeover_recomposition")

    def test_post_land_closure_bind_preserves_real_project_owner_on_asked_medium_closure(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "two synchronized one-dimensional walks: ordinary balance b and deformed-parser walk t with a 1-bit phase",
                "current_seam": "prefix/suffix additions only move the start and end states of the same automaton; the middle S contributes one ordinary summary and one mirrored transformed summary",
                "current_debt": "package the solved carrier into the asked medium with a concise proof and submit-ready C++",
                "next_bite": "finalize final.md and solution.cpp around the two-walk carrier",
                "asked_medium_surface": "final.md",
                "revocation_handle": "runtime_state",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "final.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by the two-walk carrier",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_combo_if_any": ["见证", "状态拆分", "对称"],
                },
                "layer_composition_if_any": {
                    "surface": "takeover_recomposition",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": True,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "对称",
                    "reason": "the previous same-carrier bite really changed the live object, so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "final.md",
                        "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by the two-walk carrier",
                        "success_signal": "asked_medium_is_exact_and_executable",
                        "owner_skill_if_any": "对称",
                        "owner_skill_combo_if_any": ["见证", "状态拆分", "对称"],
                    },
                    "layer_object": "two synchronized one-dimensional walks: ordinary balance b and deformed-parser walk t with a 1-bit phase",
                    "controlled_object": "final.md",
                    "current_seam": "prefix/suffix additions only move the start and end states of the same automaton; the middle S contributes one ordinary summary and one mirrored transformed summary",
                    "current_debt": "package the solved carrier into the asked medium with a concise proof and submit-ready C++",
                    "next_local_choice": "final.md",
                    "transition_change": "landed write on closure layer",
                    "active_skill_combo_if_any": ["见证", "状态拆分", "对称"],
                },
                "primitive_field_if_any": {
                    "layer_object": "final.md",
                    "active_primitives": ["对称", "状态拆分"],
                    "why_now": "the previous same-carrier bite really changed the live object, so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes",
                    "selection_basis": "explicit_hint",
                    "evidence_basis": "state_见证",
                    "tie_break_check": "final.md",
                },
                "primitive_takeover_gate_if_any": {
                    "trigger": "same_carrier_landing",
                    "current_object": "two synchronized one-dimensional walks: ordinary balance b and deformed-parser walk t with a 1-bit phase",
                    "current_seam": "prefix/suffix additions only move the start and end states of the same automaton; the middle S contributes one ordinary summary and one mirrored transformed summary",
                    "current_debt": "package the solved carrier into the asked medium with a concise proof and submit-ready C++",
                    "next_bite": "finalize final.md and solution.cpp around the two-walk carrier",
                    "note": "the live carrier just tightened; rebind one primitive-owned next bite before ordinary continuation resumes",
                },
                "output_status": {
                    "touched": False,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )
        structural_closure_touch = {
            "kind": "write",
            "target": "final.md",
            "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by the two-walk carrier",
            "success_signal": "asked_medium_is_exact_and_executable",
            "owner_skill_if_any": "对称",
            "owner_skill_combo_if_any": ["见证", "状态拆分", "对称"],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with patch(
                "runtime_state.read_skill_authority_program",
                return_value=(
                    "对称",
                    ["见证", "状态拆分", "对称"],
                    structural_closure_touch,
                    False,
                ),
            ):
                command_bind_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "previous_state": None,
                            "allow_handoff": False,
                            "allow_rival": False,
                        },
                    )()
                )

            rebound_state = json.loads(state_path.read_text(encoding="utf-8"))

        rebound_program = rebound_state.get("bound_program", {})
        rebound_layer = rebound_state.get("layer_composition_if_any", {})
        rebound_combo = rebound_program.get("owner_skill_combo_if_any", [])
        self.assertEqual(rebound_program.get("owner_skill_if_any"), "对称")
        self.assertIn("对称", rebound_combo)
        self.assertNotIn("精确封口", rebound_combo)
        self.assertTrue({"对称", "见证", "状态拆分"}.issubset(set(rebound_combo)))
        self.assertEqual(rebound_layer.get("leading_skill_if_any"), "对称")
        self.assertEqual(
            rebound_layer.get("authorized_bite", {}).get("owner_skill_if_any"),
            "对称",
        )

    def test_post_land_closure_bind_promotes_seam_targeted_close_onto_final_md(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        seam_targeted_closure = {
            "kind": "write",
            "target": "only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
            "operation": "attach the equal-height pairing argument and close onto final.md",
            "success_signal": "the next local layer became explicit on only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
            "owner_skill_if_any": "读出",
            "owner_skill_combo_if_any": ["读出", "见证"],
            "current_layer_object_if_any": "final answer object: root-count ranges, the two-root bound x1x2>e^2",
            "controlled_object_if_any": "only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
            "object_transform_if_any": "seal the two-root product inequality and align the written final.md artifact with the runtime-owned closure state",
            "next_object_if_any": "only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
            "step_outline_if_any": "attach the equal-height pairing argument and close onto final.md",
            "skill_phase_if_any": "same_carrier_reopened_layer",
        }
        state.update(
            {
                "current_object": "final answer object: root-count ranges, the two-root bound x1x2>e^2",
                "current_seam": "only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
                "current_debt": "seal the two-root product inequality and align the written final.md artifact with the runtime-owned closure state",
                "next_bite": "attach the equal-height pairing argument and close onto final.md",
                "asked_medium_surface": "final.md",
                "revocation_handle": "runtime_state",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "landed_next_touch_if_any": seam_targeted_closure,
                "layer_composition_if_any": {
                    "surface": "takeover_recomposition",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": True,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "读出",
                    "reason": "the previous same-carrier bite really changed the live object, so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes",
                    "authorized_bite": seam_targeted_closure,
                    "layer_object": "final answer object: root-count ranges, the two-root bound x1x2>e^2",
                    "controlled_object": "only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
                    "current_seam": "only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
                    "current_debt": "seal the two-root product inequality and align the written final.md artifact with the runtime-owned closure state",
                    "next_local_choice": "final.md",
                    "transition_change": "bound write on the final answer object and reopened final closure",
                    "active_skill_combo_if_any": ["读出", "见证"],
                },
                "primitive_field_if_any": {
                    "layer_object": "only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
                    "active_primitives": ["读出", "见证"],
                    "why_now": "the previous same-carrier bite really changed the live object, so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes",
                    "selection_basis": "explicit_hint",
                    "evidence_basis": "state_见证",
                    "tie_break_check": "only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
                },
                "primitive_takeover_gate_if_any": {
                    "trigger": "same_carrier_landing",
                    "current_object": "final answer object: root-count ranges, the two-root bound x1x2>e^2",
                    "current_seam": "only the equal-height two-point pairing remains to justify the product bound inside the final answer object",
                    "current_debt": "seal the two-root product inequality and align the written final.md artifact with the runtime-owned closure state",
                    "next_bite": "attach the equal-height pairing argument and close onto final.md",
                    "note": "the live carrier just tightened; rebind one primitive-owned next bite before ordinary continuation resumes",
                    "active_primitives": ["读出", "见证"],
                },
                "output_status": {
                    "touched": False,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with patch(
                "runtime_state.read_skill_authority_program",
                return_value=("读出", ["读出", "见证"], seam_targeted_closure, False),
            ):
                command_bind_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "previous_state": None,
                            "allow_handoff": False,
                            "allow_rival": False,
                        },
                    )()
                )

            rebound_state = json.loads(state_path.read_text(encoding="utf-8"))

        rebound_program = rebound_state.get("bound_program", {})
        rebound_layer = rebound_state.get("layer_composition_if_any", {})
        self.assertEqual(rebound_program.get("target"), "final.md")
        self.assertEqual(
            rebound_program.get("success_signal"),
            "asked_medium_is_exact_and_executable",
        )
        self.assertEqual(rebound_program.get("owner_skill_if_any"), "读出")
        self.assertEqual(rebound_layer.get("controlled_object"), "final.md")
        self.assertEqual(
            rebound_layer.get("authorized_bite", {}).get("target"),
            "final.md",
        )

    def test_same_carrier_landing_preserves_last_explicit_combo_when_refresh_is_lexical_only(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "thick carrier",
                "current_seam": "thick carrier",
                "current_debt": "make one structural cut",
                "next_bite": "land one structural cut",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "thick carrier",
                    "operation": "图像已经把对象压到更薄的局部读数上",
                    "success_signal": "thinner layer becomes explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "极限边界", "赋值"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            def fake_refresh(runtime_state: dict, *, agenda_override=None, handoff_override=None, force=False):
                runtime_state["primitive_field_if_any"] = {
                    "layer_object": "opaque new layer",
                    "active_primitives": ["读出"],
                    "why_now": "only lexical residue survived",
                    "selection_basis": "text_fallback",
                    "evidence_basis": "lexical_hint",
                }

            with patch("runtime_state.refresh_primitive_field_for_current_layer", new=fake_refresh):
                apply_same_carrier_landing(
                    state,
                    state_path,
                    next_object="opaque new layer",
                    next_seam="opaque new layer seam",
                    next_debt="recover the honest structural owner",
                    next_bite="do not fall back to a generic readout",
                )

        primitive_field = state.get("primitive_field_if_any", {})
        self.assertEqual(primitive_field.get("selection_basis"), "explicit_hint")
        self.assertEqual(primitive_field.get("evidence_basis"), "state_见证")
        self.assertEqual(
            primitive_field.get("active_primitives"),
            ["图像", "极限边界", "赋值"],
        )
        layer = state.get("layer_composition_if_any", {})
        self.assertEqual(layer.get("leading_skill_if_any"), "图像")

    def test_same_carrier_landing_seeds_only_allowed_primitives_from_closure_combo(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "三问都已求完；剩余唯一债务是把完整最终解答封进 final.md",
                "current_seam": "数学内容已经闭合，当前只差 asked medium 的精确读出与封口",
                "current_debt": "把完整最终答案封进 final.md",
                "next_bite": "按题号 materialize 完整解答",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "reopened closure seam before final materialization",
                    "operation": "seal the thinner carrier before exact asked-medium contact",
                    "success_signal": "the closure layer is now ready",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "投影", "状态拆分", "对称"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            def fake_refresh(runtime_state: dict, *, agenda_override=None, handoff_override=None, force=False):
                runtime_state["primitive_field_if_any"] = {
                    "layer_object": "closure seam",
                    "active_primitives": ["读出"],
                    "why_now": "only lexical residue survived",
                    "selection_basis": "text_fallback",
                    "evidence_basis": "lexical_hint",
                }

            with patch("runtime_state.refresh_primitive_field_for_current_layer", new=fake_refresh):
                apply_same_carrier_landing(
                    state,
                    state_path,
                    next_object="closure-ready layer that should bind final.md without leaking control skills into primitives",
                    next_seam="asked medium closure is the only live seam",
                    next_debt="seal the exact final answer into final.md",
                    next_bite="materialize the exact asked medium",
                )

        primitive_field = state.get("primitive_field_if_any", {})
        self.assertEqual(primitive_field.get("selection_basis"), "explicit_hint")
        self.assertCountEqual(
            primitive_field.get("active_primitives"),
            ["投影", "状态拆分", "对称"],
        )
        self.assertNotIn("精确封口", primitive_field.get("active_primitives", []))

    def test_normalize_direct_asked_medium_closure_owner_keeps_real_project_owner_combo(self) -> None:
        normalized = normalize_direct_asked_medium_closure_owner(
            {
                "kind": "write",
                "target": "final.md",
                "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by the two-walk carrier",
                "success_signal": "asked_medium_is_exact_and_executable",
                "owner_skill_if_any": "对称",
                "owner_skill_combo_if_any": ["对称", "见证", "状态拆分"],
            },
            asked_medium="final.md",
            preferred_owner="精确封口",
        )

        self.assertIsInstance(normalized, dict)
        normalized_combo = normalized.get("owner_skill_combo_if_any", [])
        self.assertEqual(normalized.get("owner_skill_if_any"), "对称")
        self.assertIn("对称", normalized_combo)
        self.assertNotIn("精确封口", normalized_combo)
        self.assertTrue({"对称", "见证", "状态拆分"}.issubset(set(normalized_combo)))

    def test_promote_report_derived_asked_medium_closure_preserves_real_project_owner_combo(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "三问的数学内容已经齐备，只剩 asked-medium 证明成稿",
                "current_seam": "final.md 还不存在，运行仍未完成合法释放",
                "current_debt": "需要把前两层得到的内容写成一份完整、无占位、可直接提交的 final.md",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )
        expected_combo = ["极限边界", "见证", "读出"]

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with patch(
                "runtime_state.build_report",
                return_value={
                    "skill_authority_bridge": {
                        "winning_skill_if_any": "极限边界",
                        "active_skill_combo_if_any": expected_combo,
                        "executable_local_touch_if_any": {
                            "kind": "write",
                            "target": "final.md",
                            "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 三问的数学内容已经齐备，只剩 asked-medium 证明成稿",
                            "success_signal": "asked_medium_is_exact_and_executable",
                            "owner_skill_if_any": "极限边界",
                            "owner_skill_combo_if_any": expected_combo,
                        },
                    },
                    "skill_lighting_surface": {
                        "lit_skill_if_any": "极限边界",
                        "candidate_skills_if_any": expected_combo,
                        "supporting_skills_if_any": expected_combo[1:],
                        "role_split_if_any": {
                            "primary_skill_if_any": "极限边界",
                            "supporting_skills_if_any": expected_combo[1:],
                            "ordinary_operations_are_not_skills": True,
                        },
                    },
                },
            ):
                changed = promote_report_derived_exact_closure(state, state_path=state_path)

        self.assertTrue(changed)
        self.assertEqual(state.get("bound_program", {}).get("owner_skill_if_any"), "极限边界")
        self.assertEqual(state.get("bound_program", {}).get("owner_skill_combo_if_any"), expected_combo)
        self.assertEqual(
            state.get("layer_composition_if_any", {}).get("leading_skill_if_any"),
            "极限边界",
        )
        self.assertEqual(
            state.get("layer_composition_if_any", {}).get("active_skill_combo_if_any"),
            expected_combo,
        )
        self.assertEqual(
            state.get("layer_composition_if_any", {})
            .get("authorized_bite", {})
            .get("owner_skill_combo_if_any"),
            expected_combo,
        )
        self.assertEqual(
            state.get("layer_composition_if_any", {})
            .get("lighting_if_any", {})
            .get("supporting_skills_if_any"),
            expected_combo[1:],
        )

    def test_materialize_asked_medium_refuses_singleton_exact_closure_style(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "asked_medium_surface": "final.md",
                "bound_program": {
                    "kind": "write",
                    "target": "final.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by peak value threshold already settled",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "release_veto": True,
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            final_path = Path(tmpdir) / "final.md"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 精确封口。\n",
            ):
                changed = materialize_asked_medium_if_ready(loaded_state, state_path=state_path)

        self.assertFalse(changed)
        self.assertFalse(final_path.exists())
        self.assertTrue(loaded_state.get("release_veto"))
        self.assertFalse(loaded_state.get("output_status", {}).get("final_artifact_materialized"))
        self.assertEqual(
            loaded_state.get("bound_program", {}).get("owner_skill_combo_if_any"),
            ["精确封口"],
        )

    def test_finalize_materialized_closure_refuses_singleton_exact_closure_style(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "asked_medium_surface": "final.md",
                "bound_program": {
                    "kind": "write",
                    "target": "final.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by peak value threshold already settled",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口"],
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "skill_serialized": True,
                    "summary": "runtime materialized the exact asked-medium 读出 from solve-step serialization",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": True,
                },
                "release_veto": True,
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            final_path = Path(tmpdir) / "final.md"
            final_path.write_text("# Runtime Solve Steps\n\n1. 精确封口。\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(final_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 精确封口。\n",
            ):
                changed = finalize_materialized_closure(loaded_state, state_path=state_path)

        self.assertFalse(changed)
        self.assertTrue(loaded_state.get("release_veto"))
        self.assertEqual(
            loaded_state.get("bound_program", {}).get("owner_skill_combo_if_any"),
            ["精确封口"],
        )

    def test_materialize_asked_medium_falls_back_to_closure_program_without_solve_step_export(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "asked_medium_surface": "answer.md",
                "bound_program": {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 最大半径 r = 5/2 已确定",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "极限边界", "对称"],
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "summary": "skill-expressive answer already written",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "release_veto": True,
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("画图：...\n对称：...\n极限边界：r=5/2。\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(answer_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            changed = materialize_asked_medium_if_ready(loaded_state, state_path=state_path)

            self.assertTrue(changed)
            self.assertIn("Runtime Solve Steps", answer_path.read_text(encoding="utf-8"))
            self.assertIn("极限边界", answer_path.read_text(encoding="utf-8"))
            self.assertTrue(loaded_state.get("output_status", {}).get("final_artifact_materialized"))
            self.assertFalse(loaded_state.get("materialization_evidence", {}).get("skill_serialized"))

    def test_materialize_asked_medium_writes_canonical_skill_text_once_solve_step_export_is_available(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "asked_medium_surface": "answer.md",
                "bound_program": {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 最大半径 r = 5/2 已确定",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "极限边界", "对称"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "release_veto": True,
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            answer_path = Path(tmpdir) / "answer.md"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 画图。\n2. 极限边界。\n",
            ):
                changed = materialize_asked_medium_if_ready(loaded_state, state_path=state_path)

            self.assertTrue(changed)
            self.assertEqual(
                answer_path.read_text(encoding="utf-8"),
                "# Runtime Solve Steps\n\n1. 画图。\n2. 极限边界。\n",
            )
            self.assertTrue(loaded_state.get("materialization_evidence", {}).get("skill_serialized"))

    def test_materialize_asked_medium_accepts_descriptive_surface_that_embeds_markdown_artifact(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "proof body established",
                "current_seam": "asked-medium closure in final.md",
                "current_debt": "seal the exact final answer into final.md and release the veto honestly",
                "next_bite": "touch the asked medium with the exact final solution",
                "asked_medium_surface": "seal the full solution in final.md",
                "bound_program": {
                    "kind": "write",
                    "target": "asked-medium closure in final.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by proof body established",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "图像", "读出"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "release_veto": True,
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 封口。\n",
            ):
                changed = materialize_asked_medium_if_ready(loaded_state, state_path=state_path)

            self.assertTrue(changed)
            self.assertEqual((Path(tmpdir) / "final.md").read_text(encoding="utf-8"), "# Runtime Solve Steps\n\n1. 封口。\n")
            self.assertFalse(loaded_state.get("release_veto"))
            self.assertIsNone(loaded_state.get("bound_program"))
            self.assertTrue(loaded_state.get("output_status", {}).get("final_artifact_materialized"))
            self.assertTrue(loaded_state.get("materialization_evidence", {}).get("skill_serialized"))

    def test_materialize_asked_medium_does_not_promote_report_derived_closure_while_object_side_layer_is_live(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "三问的数学内容已经齐备，只剩 asked-medium 证明成稿",
                "current_seam": "final.md 还不存在，运行仍未完成合法释放",
                "current_debt": "需要把前两层得到的内容写成一份完整、无占位、可直接提交的 final.md",
                "next_bite": "用 [读出, 状态拆分, 见证] 把三问证明按题面顺序写入 final.md",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": "final.md 还不存在，运行仍未完成合法释放",
                    "operation": "push the stale release seam to one separating check",
                    "success_signal": "the stale release seam is explicit",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "见证", "读出"],
                },
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": False,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "极限边界",
                    "reason": "the carrier just tightened; recompute and bind one fresh current-layer skill combo before ordinary continuation regains value",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "final.md 还不存在，运行仍未完成合法释放",
                        "operation": "push the stale release seam to one separating check",
                        "success_signal": "the stale release seam is explicit",
                        "owner_skill_if_any": "极限边界",
                        "owner_skill_combo_if_any": ["极限边界", "见证", "读出"],
                    },
                    "layer_object": "三问的数学内容已经齐备，只剩 asked-medium 证明成稿",
                    "controlled_object": "final.md 还不存在，运行仍未完成合法释放",
                    "current_seam": "final.md 还不存在，运行仍未完成合法释放",
                    "current_debt": "需要把前两层得到的内容写成一份完整、无占位、可直接提交的 final.md",
                    "next_local_choice": "final.md 还不存在，运行仍未完成合法释放",
                    "gap_object": "需要把前两层得到的内容写成一份完整、无占位、可直接提交的 final.md",
                    "transition_change": "bound stale release check",
                    "active_skill_combo_if_any": ["极限边界", "见证", "读出"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            with patch(
                "runtime_state.build_report",
                return_value={
                    "skill_authority_bridge": {
                        "winning_skill_if_any": "极限边界",
                        "active_skill_combo_if_any": ["极限边界", "见证", "读出"],
                        "executable_local_touch_if_any": {
                            "kind": "write",
                            "target": "final.md",
                            "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 三问的数学内容已经齐备，只剩 asked-medium 证明成稿",
                            "success_signal": "asked_medium_is_exact_and_executable",
                            "owner_skill_if_any": "极限边界",
                            "owner_skill_combo_if_any": ["极限边界", "见证", "读出"],
                        },
                    }
                },
            ), patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 封口。\n",
            ):
                changed = materialize_asked_medium_if_ready(loaded_state, state_path=state_path)

            self.assertFalse(changed)
            self.assertFalse((Path(tmpdir) / "final.md").exists())
            self.assertTrue(loaded_state.get("release_veto"))
            self.assertIsInstance(loaded_state.get("bound_program"), dict)
            self.assertFalse(loaded_state.get("output_status", {}).get("final_artifact_materialized"))

    def test_bind_local_refuses_direct_closure_touch_while_takeover_recomposition_is_still_live(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "Final answer assembled",
                "current_seam": "Seal the proved result into the canonical asked medium final.md",
                "current_debt": "Materialize the exact proved answer without reopening ordinary derivation",
                "next_bite": "Write the canonical solve-markdown artifact to final.md and clear release_veto.",
                "asked_medium_surface": "Write the complete solution to final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "revocation_handle": "runtime_state",
                "primary_slot": "solve",
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "final.md",
                    "operation": "seal the proved result into final.md without reopening ordinary derivation",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "图像", "读出", "见证"],
                },
                "layer_composition_if_any": {
                    "surface": "takeover_recomposition",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": True,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "图像",
                    "reason": "the previous same-carrier bite really changed the live object, so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "closure ledger that still orders the proved pieces before final serialization",
                        "operation": "use 状态拆分 to keep the proved pieces on one explicit closure ledger",
                        "success_signal": "the closure ledger is explicit",
                        "owner_skill_if_any": "状态拆分",
                        "owner_skill_combo_if_any": ["状态拆分", "见证", "图像"],
                    },
                    "layer_object": "Final answer assembled",
                    "controlled_object": "closure ledger that still orders the proved pieces before final serialization",
                    "current_seam": "closure ledger that still orders the proved pieces before final serialization",
                    "current_debt": "Materialize the exact proved answer without reopening ordinary derivation",
                    "next_local_choice": "closure ledger that still orders the proved pieces before final serialization",
                    "transition_change": "landed write on closure layer",
                    "active_skill_combo_if_any": ["状态拆分", "见证", "图像"],
                },
                "primitive_field_if_any": {
                    "layer_object": "closure ledger that still orders the proved pieces before final serialization",
                    "active_primitives": ["状态拆分", "见证", "图像"],
                    "why_now": "the previous same-carrier bite really changed the live object, so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes",
                    "selection_basis": "explicit_hint",
                    "evidence_basis": "state_见证",
                    "tie_break_check": "closure ledger that still orders the proved pieces before final serialization",
                },
                "primitive_takeover_gate_if_any": {
                    "trigger": "same_carrier_landing",
                    "current_object": "Final answer assembled",
                    "current_seam": "Seal the proved result into the canonical asked medium final.md",
                    "current_debt": "Materialize the exact proved answer without reopening ordinary derivation",
                    "next_bite": "Write the canonical solve-markdown artifact to final.md and clear release_veto.",
                    "note": "the live carrier just tightened; rebind one primitive-owned next bite before ordinary continuation resumes",
                    "active_primitives": ["读出"],
                },
                "output_status": {
                    "touched": False,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as exc:
                command_bind_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "previous_state": None,
                            "allow_handoff": False,
                            "allow_rival": False,
                        },
                    )()
                )

        self.assertIn("primitive takeover gate refused", str(exc.exception))

    def test_land_local_release_ready_layer_does_not_auto_materialize_final_md(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "第(2)问已经压到同值双点载体，只剩第(3)问与成稿封口",
                "current_seam": "先把 x1x2>e^2 在同值双点图上封口",
                "current_debt": "第(3)问还没有真实写成 solve text",
                "next_bite": "先完成第(2)问，再把第(3)问读回峰值阈值并写入 final.md",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "先把 x1x2>e^2 在同值双点图上封口",
                    "operation": "draw one minimal problem diagram for the same-height double-root layer and rewrite the governing relation there",
                    "success_signal": "one thinner carrier became explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "读出", "见证", "状态拆分"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            command_land_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "current_object": "第(3)问要把 a 的范围读回峰值阈值并并入 final.md",
                        "current_seam": "第(3)问还没有被真实写进 final.md",
                        "current_debt": "必须先用读出+见证把峰值阈值对应的 a 范围写成 solve text",
                        "next_bite": "先把第(3)问的峰值阈值范围真实写出来，再封口到 final.md",
                    },
                )()
            )

            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertTrue(loaded_state.get("release_veto"))
        self.assertIsNone(loaded_state.get("bound_program"))
        self.assertFalse(loaded_state.get("output_status", {}).get("final_artifact_materialized"))
        self.assertFalse((Path(tmpdir) / "final.md").exists())
        contract = pending_runtime_execution_contract(loaded_state)
        self.assertIsInstance(contract, dict)
        self.assertEqual(contract.get("required_action"), "bind_local")
        self.assertEqual(contract.get("allowed_transition_surfaces"), ["bind_local"])
        self.assertEqual(
            loaded_state.get("layer_composition_if_any", {}).get("surface"),
            "takeover_recomposition",
        )
        self.assertTrue(
            loaded_state.get("layer_composition_if_any", {}).get("must_bind_local_bite")
        )

    def test_materialize_asked_medium_command_finalizes_project_owned_closure_ready_state(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "asked_medium_surface": "final.md",
                "bound_program": {
                    "kind": "write",
                    "target": "final.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by peak value threshold already settled",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "读出", "见证"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "release_veto": True,
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            final_path = Path(tmpdir) / "final.md"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 封口。\n",
            ):
                exit_code = command_materialize_asked_medium(
                    type("Args", (), {"state_file": str(state_path)})()
                )

            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))
            final_text = final_path.read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertEqual(final_text, "# Runtime Solve Steps\n\n1. 封口。\n")
        self.assertFalse(loaded_state.get("release_veto"))
        self.assertIsNone(loaded_state.get("bound_program"))
        self.assertTrue(loaded_state.get("output_status", {}).get("final_artifact_materialized"))

    def test_bind_local_clears_stale_materialization_flags_when_new_program_binds(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "Final answer assembled",
                "current_seam": "Seal the proved result into the canonical asked medium final.md",
                "current_debt": "Materialize the exact proved answer without reopening ordinary derivation",
                "next_bite": "Write the canonical solve-markdown artifact to final.md and clear release_veto.",
                "asked_medium_surface": "Write the complete solution to final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "revocation_handle": "runtime_state",
                "primary_slot": "solve",
                "landed_next_touch_if_any": {
                    "kind": "check",
                    "target": "closure ledger that still orders the proved pieces before final serialization",
                    "operation": "use 状态拆分 to keep the proved pieces on one explicit closure ledger",
                    "success_signal": "the closure ledger is explicit",
                    "owner_skill_if_any": "状态拆分",
                    "owner_skill_combo_if_any": ["状态拆分", "见证", "图像"],
                },
                "layer_composition_if_any": {
                    "surface": "takeover_recomposition",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": True,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "图像",
                    "reason": "the previous same-carrier bite really changed the live object, so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "closure ledger that still orders the proved pieces before final serialization",
                        "operation": "use 状态拆分 to keep the proved pieces on one explicit closure ledger",
                        "success_signal": "the closure ledger is explicit",
                        "owner_skill_if_any": "状态拆分",
                        "owner_skill_combo_if_any": ["状态拆分", "见证", "图像"],
                    },
                    "layer_object": "Final answer assembled",
                    "controlled_object": "closure ledger that still orders the proved pieces before final serialization",
                    "current_seam": "closure ledger that still orders the proved pieces before final serialization",
                    "current_debt": "Materialize the exact proved answer without reopening ordinary derivation",
                    "next_local_choice": "closure ledger that still orders the proved pieces before final serialization",
                    "transition_change": "landed write on closure layer",
                    "active_skill_combo_if_any": ["状态拆分", "见证", "图像"],
                },
                "primitive_field_if_any": {
                    "layer_object": "closure ledger that still orders the proved pieces before final serialization",
                    "active_primitives": ["状态拆分", "见证", "图像"],
                    "why_now": "the previous same-carrier bite really changed the live object, so the newly exposed layer must bind one fresh local combination before ordinary continuation resumes",
                    "selection_basis": "explicit_hint",
                    "evidence_basis": "state_见证",
                    "tie_break_check": "closure ledger that still orders the proved pieces before final serialization",
                },
                "primitive_takeover_gate_if_any": {
                    "trigger": "same_carrier_landing",
                    "current_object": "Final answer assembled",
                    "current_seam": "Seal the proved result into the canonical asked medium final.md",
                    "current_debt": "Materialize the exact proved answer without reopening ordinary derivation",
                    "next_bite": "Write the canonical solve-markdown artifact to final.md and clear release_veto.",
                    "note": "the live carrier just tightened; rebind one primitive-owned next bite before ordinary continuation resumes",
                    "active_primitives": ["读出"],
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "final.md",
                    "summary": "stale earlier materialization",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": True,
                    "contains_unsupported": True,
                    "contains_placeholder": True,
                    "final_artifact_materialized": True,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            command_bind_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "previous_state": None,
                        "allow_handoff": False,
                        "allow_rival": False,
                    },
                )()
            )

            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertIsNone(loaded_state.get("materialization_evidence"))
        self.assertFalse(loaded_state.get("output_status", {}).get("touched"))
        self.assertFalse(loaded_state.get("output_status", {}).get("cosmetic_only"))
        self.assertFalse(loaded_state.get("output_status", {}).get("contains_unsupported"))
        self.assertFalse(loaded_state.get("output_status", {}).get("contains_placeholder"))
        self.assertFalse(loaded_state.get("output_status", {}).get("final_artifact_materialized"))

    def test_runtime_solve_steps_markdown_uses_persisted_execute_local_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            command_bootstrap_blind(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "current_object": "参数 a 可能是假主角",
                        "current_debt": "先把三问统一压到一条更薄的值载体上",
                        "next_bite": "先试把方程改写成 a 关于 x 的表达式，再看图像与峰值能否接管",
                        "asked_medium_surface": "answer.md",
                        "current_seam": "不要先回到普通导数分类",
                        "revocation_handle": None,
                        "uncertainty_mode": None,
                        "primary_slot": None,
                    },
                )()
            )
            command_bind_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "previous_state": None,
                        "allow_handoff": False,
                        "allow_rival": False,
                    },
                )()
            )
            worked_step = (
                "赋值：先把原方程改写成 a=1+(lnx)/x。\n"
                "图像：把三问统一压到值载体 y=1+(lnx)/x 上，先看横线截点与峰值。\n"
                "极限边界：记录 x->0+ 的左端下冲，以及 x=e 处峰值 1+1/e。"
            )
            command_execute_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "worked_step": worked_step,
                        "summary": "把参数题统一压到值载体图像上",
                        "output_file": None,
                        "cosmetic_only": False,
                        "contains_unsupported": False,
                        "contains_placeholder": False,
                    },
                )()
            )

            solve_trace = render_runtime_solve_steps_markdown(state_path)

        self.assertIn("实际做题文本", solve_trace)
        self.assertIn("赋值：先把原方程改写成 a=1+(lnx)/x。", solve_trace)
        self.assertIn("图像：把三问统一压到值载体 y=1+(lnx)/x 上", solve_trace)

    def test_execute_local_keeps_state_backed_combo_authoritative(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "fresh blind package run in isolated directory",
                "current_seam": "fresh blind package run in isolated directory",
                "current_debt": "produce one honest runtime transition and validate the current contract surface without reading forbidden package history",
                "next_bite": "bind one local runtime-owned verification bite inside this run directory",
                "asked_medium_surface": "final.md",
                "revocation_handle": "runtime_state",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            command_bind_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "previous_state": None,
                        "allow_handoff": False,
                        "allow_rival": False,
                    },
                )()
            )
            command_execute_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "worked_step": (
                            "见证：把这个结论钉在同一 run 目录内的 events 上，"
                            "现在事件里已经存在 bind-local，所以真实 transition 已经被当前层见证到。\n"
                            "精确封口：把验证面收束到同一 run 目录内的 runtime_state.json 与 "
                            "runtime_state.events.jsonl，并确认这次真实 transition 就是 bind-local。"
                        ),
                        "summary": "见证：确认这次 run 已有真实 transition",
                        "output_file": "evidence.md",
                        "cosmetic_only": False,
                        "contains_unsupported": False,
                        "contains_placeholder": False,
                    },
                )()
            )
            runtime_evidence = build_runtime_evidence(state_path)

        self.assertTrue(runtime_evidence.get("latest_consumption_authority_aligned"))
        self.assertTrue(runtime_evidence.get("latest_consumption_layer_composition_qualified"))
        self.assertEqual(runtime_evidence.get("latest_real_runtime_transition_command"), "execute-local")
        combo = runtime_evidence.get("latest_consumption_skill_combo") or []
        self.assertEqual(combo, ["见证", "精确封口"])

    def test_runtime_evidence_treats_rebind_local_as_qualified_runtime_transition(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            before = copy.deepcopy(DEFAULT_STATE)
            before.update(
                {
                    "current_object": "thick carrier",
                    "current_seam": "thick carrier",
                    "current_debt": "let the thinner carrier take local authority",
                    "next_bite": "rebind once",
                    "asked_medium_surface": "final.md",
                    "release_veto": True,
                }
            )
            after = copy.deepcopy(before)
            after["carrier_handoff_if_any"] = {
                "to_object": "thinner carrier seam",
                "reason": "one thinner carrier now owns the next bite",
            }
            authorized_bite = {
                "kind": "check",
                "target": "thinner carrier seam",
                "operation": "spend the thinner carrier seam directly",
                "success_signal": "the thinner seam is explicit",
                "owner_skill_if_any": "投影",
                "owner_skill_combo_if_any": ["投影", "状态拆分"],
            }
            after["layer_composition_if_any"] = build_layer_composition_state_payload(
                after,
                surface="carrier_handoff",
                authorized_bite=authorized_bite,
                skill_winner="投影",
                skill_combo=["投影", "状态拆分"],
                reason="the thinner carrier now owns one explicit spend-side bite",
                must_bind_local_bite=False,
                must_spend_handoff=True,
                layer_object="thinner carrier seam",
                controlled_object="thinner carrier seam",
                current_seam="thinner carrier seam",
                current_debt="spend the thinner seam before ordinary continuation resumes",
                next_local_choice="spend the thinner seam directly",
                gap_object="thinner carrier seam",
                transition_change="carrier authority moved onto the thinner seam",
                lighting_if_any={
                    "lit_skill_if_any": "投影",
                    "candidate_skills_if_any": ["投影", "状态拆分"],
                    "supporting_skills_if_any": ["状态拆分"],
                    "verify_touch_if_any": {"target": "thinner carrier seam", "kind": "check"},
                },
            )
            state_path.write_text(json.dumps(after, ensure_ascii=True, indent=2), encoding="utf-8")
            append_runtime_event(
                state_path,
                command_name="rebind-local",
                before=before,
                after=after,
            )

            runtime_evidence = build_runtime_evidence(state_path)

        self.assertTrue(runtime_evidence.get("has_runtime_consumption"))
        self.assertTrue(runtime_evidence.get("has_real_runtime_transition"))
        self.assertTrue(runtime_evidence.get("latest_consumption_authority_aligned"))
        self.assertTrue(runtime_evidence.get("latest_consumption_layer_composition_qualified"))
        self.assertEqual(runtime_evidence.get("latest_consumption_command"), "rebind-local")
        self.assertEqual(runtime_evidence.get("latest_consumption_skill_combo"), ["投影", "状态拆分"])

    def test_set_output_refuses_while_live_runtime_contract_still_requires_land_local(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "sphere centers in one axial cross-section",
                "current_seam": "sphere centers in one axial cross-section",
                "current_debt": "turn the geometry into one exact center-distance equation for r",
                "next_bite": "set the center distance equal to 2r",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "sphere centers in one axial cross-section",
                    "operation": "redraw the axial cross-section and pin the extremal center positions",
                    "success_signal": "the cross-section controller is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "投影", "极限边界"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as ctx:
                command_set_output(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "touched": True,
                            "cosmetic_only": False,
                            "contains_unsupported": False,
                            "contains_placeholder": False,
                            "final_artifact_materialized": True,
                        },
                    )()
                )

        self.assertIn("still requires land_local", str(ctx.exception))

    def test_evidence_set_refuses_while_live_runtime_contract_still_requires_land_local(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "sphere centers in one axial cross-section",
                "current_seam": "sphere centers in one axial cross-section",
                "current_debt": "turn the geometry into one exact center-distance equation for r",
                "next_bite": "set the center distance equal to 2r",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "sphere centers in one axial cross-section",
                    "operation": "redraw the axial cross-section and pin the extremal center positions",
                    "success_signal": "the cross-section controller is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "投影", "极限边界"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as ctx:
                command_evidence(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "mode": "set",
                            "kind": "file",
                            "location": str(Path(tmpdir) / "answer.md"),
                            "summary": "manual answer",
                        },
                    )()
                )

        self.assertIn("still requires land_local", str(ctx.exception))

    def test_set_output_refuses_noncanonical_asked_medium_materialization(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "skill_serialized": True,
                    "summary": "ordinary answer already exists",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("普通解法：先求导分类。\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(answer_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_set_output(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "touched": True,
                            "cosmetic_only": False,
                            "contains_unsupported": False,
                            "contains_placeholder": False,
                            "final_artifact_materialized": True,
                        },
                    )()
                )

        self.assertIn("set-output refused", str(ctx.exception))
        self.assertIn("runtime solve-step serialization is not exportable yet", str(ctx.exception))

    def test_evidence_set_refuses_manual_asked_medium_without_skill_serialization(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("普通解法：先求导分类。\n", encoding="utf-8")
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_evidence(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "mode": "set",
                            "evidence_kind": "file",
                            "evidence_location": str(answer_path),
                            "evidence_summary": "manual answer",
                        },
                    )()
                )

        self.assertIn("evidence set refused", str(ctx.exception))
        self.assertIn("asked medium artifact is not marked as skill-serialized", str(ctx.exception))

    def test_set_core_refuses_release_on_noncanonical_asked_medium_materialization(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "skill_serialized": True,
                    "summary": "ordinary answer already exists",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": True,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("普通解法：先求导分类。\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(answer_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_set_core(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "current_object": None,
                            "current_seam": None,
                            "current_debt": None,
                            "next_bite": None,
                            "asked_medium_surface": None,
                            "revocation_handle": None,
                            "uncertainty_mode": None,
                            "primary_slot": None,
                            "release_veto": False,
                        },
                    )()
                )

        self.assertIn("release refused", str(ctx.exception))
        self.assertIn("runtime solve-step serialization is not exportable yet", str(ctx.exception))

    def test_set_core_refuses_release_with_live_asked_medium_closure_without_solve_step_export(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "最大半径 r = 5/2 已确定",
                "current_seam": "把最终作答写入 answer.md",
                "current_debt": "把最终作答写入 answer.md",
                "next_bite": "把最终作答写入 answer.md",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 最大半径 r = 5/2 已确定",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "极限边界", "对称"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_set_core(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "current_object": None,
                            "current_seam": None,
                            "current_debt": None,
                            "next_bite": None,
                            "asked_medium_surface": None,
                            "revocation_handle": None,
                            "uncertainty_mode": None,
                            "primary_slot": None,
                            "release_veto": False,
                        },
                    )()
                )

        self.assertIn("cannot clear release_veto while active control artifacts remain", str(ctx.exception))
        self.assertIn("bound_program", str(ctx.exception))

    def test_init_allow_release_refuses_manual_asked_medium_without_skill_serialization(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("普通解法：先求导分类。\n", encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                command_init(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "current_object": "薄对象",
                            "current_seam": "薄对象",
                            "current_debt": "把答案写进 answer.md",
                            "next_bite": "把答案写进 answer.md",
                            "asked_medium_surface": "answer.md",
                            "revocation_handle": "revocable",
                            "uncertainty_mode": None,
                            "primary_slot": "main",
                            "touched": True,
                            "cosmetic_only": False,
                            "contains_unsupported": False,
                            "contains_placeholder": False,
                            "final_artifact_materialized": True,
                            "fresh_blind_project_skills_on": False,
                            "allow_release": True,
                            "evidence_kind": "file",
                            "evidence_location": str(answer_path),
                            "evidence_summary": "manual answer",
                            "kind": None,
                            "target": None,
                            "operation": None,
                            "success_signal": None,
                        },
                    )()
                )

        self.assertIn(
            "cannot clear release_veto without a bound_program unless the asked medium has already been touched",
            str(ctx.exception),
        )

    def test_materialize_event_keeps_previous_layer_composition_in_excerpt(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "最大半径 r = 5/2 已确定",
                "current_seam": "把最终作答写入 answer.md",
                "current_debt": "把最终作答写入 answer.md",
                "next_bite": "把最终作答写入 answer.md",
                "asked_medium_surface": "answer.md",
                "bound_program": {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 最大半径 r = 5/2 已确定",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "极限边界", "对称"],
                },
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "active_skill_combo_if_any": ["精确封口", "极限边界", "对称"],
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": False,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "精确封口",
                    "reason": "答案已经被压到 asked-medium 封口层",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "answer.md",
                        "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 最大半径 r = 5/2 已确定",
                        "success_signal": "asked_medium_is_exact_and_executable",
                        "owner_skill_if_any": "精确封口",
                        "owner_skill_combo_if_any": ["精确封口", "极限边界", "对称"],
                    },
                    "layer_object": "最大半径 r = 5/2 已确定",
                    "controlled_object": "answer.md",
                    "current_seam": "把最终作答写入 answer.md",
                    "current_debt": "把最终作答写入 answer.md",
                    "next_local_choice": "answer.md",
                    "gap_object": "把最终作答写入 answer.md",
                    "transition_change": "bound write on answer.md",
                    "lighting_if_any": {
                        "lit_skill_if_any": "精确封口",
                        "candidate_skills_if_any": ["精确封口", "极限边界", "对称"],
                        "supporting_skills_if_any": ["极限边界", "对称"],
                        "ordinary_operations_are_not_skills": True,
                    },
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "summary": "skill-expressive answer already written",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("画图：...\n对称：...\n极限边界：r=5/2。\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(answer_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            def _materialize(loaded_state: dict) -> None:
                materialize_asked_medium_if_ready(loaded_state, state_path=state_path)

            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 赋值换对象。\n2. 精确封口。\n",
            ):
                mutate_state(
                    state_path,
                    _materialize,
                    command_name="materialize-asked-medium",
                )
            events = load_runtime_events(state_path)

        self.assertTrue(events)
        latest = events[-1]
        layer = latest.get("report_excerpt", {}).get("layer_composition", {})
        self.assertEqual(latest.get("command"), "materialize-asked-medium")
        self.assertEqual(layer.get("leading_skill_if_any"), "精确封口")
        self.assertIn("精确封口", layer.get("active_skill_combo_if_any", []))
        self.assertEqual(
            layer.get("lighting_if_any", {}).get("lit_skill_if_any"),
            "精确封口",
        )
        self.assertIn(
            "精确封口",
            layer.get("lighting_if_any", {}).get("candidate_skills_if_any", []),
        )
        self.assertEqual(
            layer.get("lighting_if_any", {}).get("role_split_if_any", {}).get("primary_skill_if_any"),
            "精确封口",
        )

    def test_materialize_event_is_rendered_as_runtime_skill_and_solve_step(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "最大半径 r = 5/2 已确定",
                "current_seam": "把最终作答写入 answer.md",
                "current_debt": "把最终作答写入 answer.md",
                "next_bite": "把最终作答写入 answer.md",
                "asked_medium_surface": "answer.md",
                "bound_program": {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 最大半径 r = 5/2 已确定",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "极限边界", "对称"],
                },
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "active_skill_combo_if_any": ["精确封口", "极限边界", "对称"],
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "leading_skill_if_any": "精确封口",
                    "reason": "答案已经被压到 asked-medium 封口层",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "answer.md",
                        "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 最大半径 r = 5/2 已确定",
                        "success_signal": "asked_medium_is_exact_and_executable",
                        "owner_skill_if_any": "精确封口",
                        "owner_skill_combo_if_any": ["精确封口", "极限边界", "对称"],
                        "current_layer_object_if_any": "最大半径 r = 5/2 已确定",
                        "controlled_object_if_any": "answer.md",
                        "object_transform_if_any": "精确封口 rewrites `最大半径 r = 5/2 已确定` toward `answer.md`",
                        "next_object_if_any": "answer.md",
                        "step_outline_if_any": "use `精确封口` on `answer.md` to move from `最大半径 r = 5/2 已确定` to `answer.md`, then continue on `answer.md`",
                        "skill_phase_if_any": "structural_rewrite",
                    },
                    "layer_object": "最大半径 r = 5/2 已确定",
                    "controlled_object": "answer.md",
                    "current_seam": "把最终作答写入 answer.md",
                    "current_debt": "把最终作答写入 answer.md",
                    "next_local_choice": "answer.md",
                    "gap_object": "把最终作答写入 answer.md",
                    "transition_change": "bound write on answer.md",
                    "lighting_if_any": {
                        "lit_skill_if_any": "精确封口",
                        "candidate_skills_if_any": ["精确封口", "极限边界", "对称"],
                        "supporting_skills_if_any": ["极限边界", "对称"],
                        "role_split_if_any": {
                            "primary_skill_if_any": "精确封口",
                            "supporting_skills_if_any": ["极限边界", "对称"],
                            "check_kind_if_any": "write",
                            "check_target_if_any": "answer.md",
                            "ordinary_operations_are_not_skills": True,
                        },
                        "ordinary_operations_are_not_skills": True,
                    },
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "summary": "skill-expressive answer already written",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("画图：...\n对称：...\n极限边界：r=5/2。\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(answer_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            def _materialize(loaded_state: dict) -> None:
                materialize_asked_medium_if_ready(loaded_state, state_path=state_path)

            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 图像。\n2. 精确封口。\n",
            ):
                mutate_state(
                    state_path,
                    _materialize,
                    command_name="materialize-asked-medium",
                )

            skill_trace = render_runtime_skill_trace_markdown(state_path)
            solve_trace = render_runtime_solve_steps_markdown(state_path)

        self.assertIn("materialize-asked-medium", skill_trace)
        self.assertIn("精确封口", skill_trace)
        self.assertIn("Materialized closure", skill_trace)
        self.assertIn("asked medium", solve_trace)
        self.assertIn("最终层步骤", solve_trace)

    def test_canonical_asked_medium_materialization_prefers_runtime_solve_steps(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state["asked_medium_surface"] = "answer.md"
        program = {
            "kind": "write",
            "target": "answer.md",
            "operation": "ordinary fallback prose",
            "success_signal": "asked_medium_is_exact_and_executable",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 赋值换对象。\n2. 图像定骨架。\n",
            ):
                text = canonical_asked_medium_materialization_text(
                    state,
                    state_path=state_path,
                    program=program,
                )

        self.assertEqual(
            text,
            "# Runtime Solve Steps\n\n1. 赋值换对象。\n2. 图像定骨架。\n",
        )

    def test_materialize_asked_medium_overwrites_noncanonical_existing_answer_with_skill_steps(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "asked_medium_surface": "answer.md",
                "bound_program": {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "ordinary fallback prose",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "赋值", "图像"],
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "summary": "generic answer already written",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "release_veto": True,
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("普通解法：先求导分类。\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(answer_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 赋值换对象。\n2. 图像定骨架。\n",
            ):
                materialize_asked_medium_if_ready(state, state_path=state_path)

            self.assertEqual(
                answer_path.read_text(encoding="utf-8"),
                "# Runtime Solve Steps\n\n1. 赋值换对象。\n2. 图像定骨架。\n",
            )
            self.assertTrue(state.get("materialization_evidence", {}).get("skill_serialized"))

    def test_canonical_asked_medium_materialization_text_falls_back_to_closure_program(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update({"asked_medium_surface": "answer.md"})
        program = {
            "kind": "write",
            "target": "answer.md",
            "operation": "seal the exact answer forced by the current thin carrier",
            "success_signal": "asked_medium_is_exact_and_executable",
            "owner_skill_if_any": "精确封口",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with patch("runtime_state._solve_trace_export_allowed", return_value=False):
                text = canonical_asked_medium_materialization_text(
                    state,
                    state_path=state_path,
                    program=program,
                )

        self.assertIn("Runtime Solve Steps", text)
        self.assertIn("精确封口", text)
        self.assertIn("seal the exact answer", text)

    def test_attach_skill_authority_bridge_preserves_real_project_owner_combo(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "最大半径 r = 5/2 已确定",
                "current_seam": "把最终作答写入 answer.md",
                "current_debt": "把最终作答写入 answer.md",
                "next_bite": "把最终作答写入 answer.md",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "primitive_field_if_any": {
                    "layer_object": "把最终作答写入 answer.md",
                    "active_primitives": ["极限边界", "状态拆分", "读出"],
                    "why_now": "答案已经压到最后封口层",
                    "selection_basis": "explicit_hint",
                    "evidence_basis": "state_见证",
                    "tie_break_check": "answer.md",
                },
            }
        )

        bridge = derive_skill_authority_bridge(
            state,
            [],
            skill_competition_override={
                "winning_skill_if_any": "极限边界",
                "coactive_skills_if_any": ["极限边界", "状态拆分", "读出"],
                "candidates": [
                    {"skill": "极限边界"},
                    {"skill": "状态拆分"},
                    {"skill": "读出"},
                ],
            },
            closure_nucleus_override={
                "closure_gate_active": True,
                "current_读出_bite_if_any": {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by 最大半径 r = 5/2 已确定",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "状态拆分", "读出"],
                },
            },
        )

        self.assertIsInstance(bridge, dict)
        touch = bridge.get("executable_local_touch_if_any", {})
        self.assertEqual(touch.get("owner_skill_if_any"), "极限边界")
        self.assertEqual(
            touch.get("owner_skill_combo_if_any"),
            ["极限边界", "状态拆分", "读出"],
        )

    def test_read_skill_authority_program_keeps_real_project_owner_combo(self) -> None:
        winning_skill, skill_combo, touch, _ = read_skill_authority_program(
            {
                "skill_authority_bridge": {
                    "winning_skill_if_any": "对称",
                    "same_carrier_only": True,
                    "silence_after_contact": True,
                    "executable_local_touch_if_any": {
                        "kind": "write",
                        "target": "answer.md",
                        "operation": "seal the current thinner carrier into the asked medium",
                        "success_signal": "asked_medium_is_exact_and_executable",
                        "owner_skill_if_any": "对称",
                        "owner_skill_combo_if_any": ["对称", "投影", "读出"],
                    },
                }
            },
            require_same_carrier=True,
        )

        self.assertEqual(winning_skill, "对称")
        self.assertEqual(skill_combo, ["对称", "投影", "读出"])
        self.assertEqual(touch.get("owner_skill_if_any"), "对称")
        self.assertEqual(touch.get("owner_skill_combo_if_any"), ["对称", "投影", "读出"])

    def test_land_local_preserves_existing_asked_medium_evidence_for_final_closure(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "矩形8x9截面内两个相同圆与上下边、左右边及彼此外切",
                "current_seam": "由两圆心距离等于2r读出最大半径",
                "current_debt": "在二维截面上把横向距离 8-2r 与纵向距离 9-2r 写进外切方程",
                "next_bite": "在控制截面上把对称与极限边界一起写成圆心距离方程",
                "asked_medium_surface": "answer.md",
                "bound_program": {
                    "kind": "check",
                    "target": "由两圆心距离等于2r读出最大半径",
                    "operation": "push one decisive geometry check",
                    "success_signal": "the decisive center-distance equation is explicit",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "对称", "投影", "见证"],
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "summary": "skill-expressive answer already written",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("画图：...\n对称：...\n极限边界：r=5/2。\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(answer_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            apply_same_carrier_landing(
                loaded_state,
                state_path,
                next_object="最大半径 r = 5/2 已确定",
                next_seam="把最终作答写入 answer.md",
                next_debt="把最终作答写入 answer.md",
                next_bite="把最终作答写入 answer.md",
            )

            self.assertFalse(loaded_state.get("output_status", {}).get("touched"))
            self.assertEqual(
                loaded_state.get("materialization_evidence", {}).get("location"),
                str(answer_path),
            )

    def test_reopened_layer_rebind_turns_preserved_output_into_fresh_execute_local_contract(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "第一层对象",
                "current_seam": "第一层 seam",
                "current_debt": "第一层 debt",
                "next_bite": "第一层 bite",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "rebind_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": "第一层 seam",
                    "operation": "use 图像 to touch the first layer",
                    "success_signal": "the first-layer gap is explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "极限边界"],
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "",
                    "summary": "skill-expressive answer already written",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
                "landed_next_touch_if_any": {
                    "kind": "check",
                    "target": "第二层 seam",
                    "operation": "use 对称 to touch the second layer",
                    "success_signal": "the second-layer gap is explicit",
                    "owner_skill_if_any": "对称",
                    "owner_skill_combo_if_any": ["对称", "图像"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            answer_path = Path(tmpdir) / "answer.md"
            answer_path.write_text("画图：...\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(answer_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            with patch(
                "runtime_guard._sanitize_public_skill_competition",
                side_effect=lambda payload: payload,
            ):
                apply_same_carrier_landing(
                    loaded_state,
                    state_path,
                    next_object="第二层对象",
                    next_seam="第二层 seam",
                    next_debt="第二层 debt",
                    next_bite="第二层 bite",
                )
            rebound_state = copy.deepcopy(loaded_state)
            rebound_layer = copy.deepcopy(rebound_state.get("layer_composition_if_any", {}))
            rebound_bite = copy.deepcopy(rebound_layer.get("authorized_bite", {}))
            rebound_state["bound_program"] = rebound_bite
            rebound_layer["surface"] = "bound_program"
            rebound_layer["leading_skill_if_any"] = rebound_bite.get("owner_skill_if_any")
            rebound_layer["authorized_bite"] = rebound_bite
            rebound_state["layer_composition_if_any"] = rebound_layer
            rebound_state["output_status"]["touched"] = False
            pending = pending_runtime_execution_contract(
                rebound_state,
                layer_composition=rebound_state.get("layer_composition_if_any"),
            )

        self.assertIsInstance(pending, dict)
        self.assertEqual(pending.get("required_action"), "execute_local")
        self.assertEqual(
            rebound_state.get("bound_program", {}).get("owner_skill_if_any"),
            rebound_state.get("layer_composition_if_any", {}).get("leading_skill_if_any"),
        )
        self.assertFalse(rebound_state.get("output_status", {}).get("touched"))

    def test_apply_same_carrier_landing_seeds_reopened_layer_touch_metadata(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "旧层对象",
                "current_seam": "旧层缝",
                "current_debt": "把旧层压到新层",
                "next_bite": "旧层先做一刀",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "primary_slot": "solve",
                "bound_program": {
                    "kind": "check",
                    "target": "旧层缝",
                    "operation": "use 图像 to touch the old layer",
                    "success_signal": "old layer became explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "对称"],
                },
                "materialization_evidence": {
                    "kind": "inline_text",
                    "location": "inline",
                    "summary": "旧层已实际落地",
                    "worked_step": "图像：先把旧层看薄。",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            apply_same_carrier_landing(
                loaded_state,
                state_path,
                next_object="新层对象",
                next_seam="新层缝",
                next_debt="把新层继续压到更薄对象",
                next_bite="在新层上画图并压出边界锚点",
            )

        touch = loaded_state.get("landed_next_touch_if_any", {})
        self.assertEqual(touch.get("current_layer_object_if_any"), "新层对象")
        self.assertEqual(touch.get("controlled_object_if_any"), "新层缝")
        self.assertEqual(touch.get("object_transform_if_any"), "把新层继续压到更薄对象")
        self.assertEqual(touch.get("step_outline_if_any"), "在新层上画图并压出边界锚点")
        self.assertEqual(touch.get("skill_phase_if_any"), "same_carrier_reopened_layer")

    def test_apply_same_carrier_landing_prefers_direct_closure_over_seeded_final_check(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "整体上界与下界问题：1+ln x/x",
                "current_seam": "求对所有 x>0 的全局上确界，并检查下界是否可能被统一抬到 0 以上",
                "current_debt": "完成第(3)问并把三问封口到最终答案",
                "next_bite": "求 1+ln x/x 的最大值，并用 x->0+ 的边界排除全局非负可能",
                "asked_medium_surface": "Write the complete solution to final.md",
                "release_veto": True,
                "revocation_handle": "runtime_state",
                "primary_slot": "solve",
                "bound_program": {
                    "kind": "check",
                    "target": "求对所有 x>0 的全局上确界，并检查下界是否可能被统一抬到 0 以上",
                    "operation": "push the global upper-bound seam to one honest boundary case",
                    "success_signal": "the sign-range layer is settled",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "见证", "对称"],
                },
                "materialization_evidence": {
                    "kind": "inline_text",
                    "location": "inline",
                    "summary": "三问都已完成",
                    "worked_step": "极限边界：第(3)问完成。",
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            loaded_state = json.loads(state_path.read_text(encoding="utf-8"))

            compiled_closure_touch = {
                "kind": "write",
                "target": "final.md",
                "operation": "seal the existing solved layer into final.md",
                "success_signal": "asked_medium_is_exact_and_executable",
                "owner_skill_if_any": "极限边界",
                "owner_skill_combo_if_any": ["极限边界", "见证", "对称"],
            }
            closure_report = {
                "closure_nucleus": {
                    "current_structural_bite_if_any": {},
                    "current_读出_bite_if_any": compiled_closure_touch,
                },
                "gap_object": {"object": "final.md"},
            }

            with patch("runtime_state.closure_can_take_first_shot", return_value=True), patch(
                "runtime_state.build_report",
                return_value=closure_report,
            ), patch(
                "runtime_state.read_skill_authority_program",
                return_value=("", [], None, False),
            ), patch(
                "runtime_state.derive_bound_program_candidate",
                return_value=None,
            ):
                apply_same_carrier_landing(
                    loaded_state,
                    state_path,
                    next_object="最终封口：将已完成三问序列化到 final.md",
                    next_seam="把已完成的 runtime solve steps 与 asked medium 完全对齐",
                    next_debt="生成 final.md 并清除 release_veto",
                    next_bite="绑定 exact closure 读出并以 canonical solve-markdown materialize final.md",
                )

        touch = loaded_state.get("landed_next_touch_if_any", {})
        self.assertEqual(touch.get("target"), "final.md")
        self.assertEqual(touch.get("success_signal"), "asked_medium_is_exact_and_executable")
        self.assertIn("final.md", str(touch.get("operation", "")))

    def test_apply_same_carrier_landing_rejects_generic_asked_medium_touch_before_object_side_discharge(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "第(1)问已完成，ask2/ask3 仍未 discharge",
                "current_seam": "先把双根与峰值关系压到同一层",
                "current_debt": "ask2/ask3 还没有在对象侧收束",
                "next_bite": "先把双根关系压到更薄载体，再谈 final.md",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "primary_slot": "solve",
                "bound_program": {
                    "kind": "check",
                    "target": "先把双根与峰值关系压到同一层",
                    "operation": "use 图像 to finish ask1 and reopen the structural layer",
                    "success_signal": "ask1 is settled",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "读出", "见证"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            def fake_refresh(runtime_state: dict, *, agenda_override=None, handoff_override=None, force=False):
                runtime_state["primitive_field_if_any"] = {
                    "layer_object": "x=e 两侧的双根如何压成同一等值关系",
                    "active_primitives": ["读出", "见证"],
                    "why_now": "lexical reopen residue",
                    "selection_basis": "explicit_hint",
                    "evidence_basis": "state_见证",
                    "tie_break_check": "x=e 两侧的双根如何压成同一等值关系",
                }

            leaked_touch = {
                "kind": "write",
                "target": "final.md",
                "operation": "Write one explicit answer/读出 dependency, field set, or certificate surface.",
                "success_signal": "asked_medium_is_exact_and_executable",
                "owner_skill_if_any": "读出",
                "owner_skill_combo_if_any": ["读出", "见证"],
            }
            recomposed_touch = {
                "kind": "check",
                "target": "x=e 两侧的双根如何压成同一等值关系",
                "operation": "compare the same-height roots before any asked-medium serialization",
                "success_signal": "the structural ask2 layer is explicit",
                "owner_skill_if_any": "见证",
                "owner_skill_combo_if_any": ["见证", "读出"],
            }

            with patch("runtime_state.refresh_primitive_field_for_current_layer", new=fake_refresh), patch(
                "runtime_state.read_skill_authority_program",
                return_value=("读出", ["读出", "见证"], leaked_touch, False),
            ), patch(
                "runtime_state.derive_bound_program_candidate",
                return_value=recomposed_touch,
            ):
                loaded_state = json.loads(state_path.read_text(encoding="utf-8"))
                apply_same_carrier_landing(
                    loaded_state,
                    state_path,
                    next_object="h(x)=lnx/x 的双交点与峰值结构",
                    next_seam="x=e 两侧的双根如何压成同一等值关系",
                    next_debt="ask2/ask3 还没有在对象侧收束",
                    next_bite="先把双根关系压到更薄载体，再谈 final.md",
                )

        touch = loaded_state.get("landed_next_touch_if_any", {})
        layer = loaded_state.get("layer_composition_if_any", {})
        self.assertNotEqual(touch.get("target"), "final.md")
        self.assertEqual(touch.get("target"), "x=e 两侧的双根如何压成同一等值关系")
        self.assertNotEqual(layer.get("controlled_object"), "final.md")

    def test_apply_same_carrier_landing_keeps_object_side_when_closure_words_appear_but_gate_says_not_yet(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "第(1)问已完成，ask2/ask3 仍未 discharge",
                "current_seam": "先把双根与峰值关系压到同一层",
                "current_debt": "ask2/ask3 还没有在对象侧收束",
                "next_bite": "先把双根关系压到更薄载体，再谈 final.md",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "primary_slot": "solve",
                "bound_program": {
                    "kind": "check",
                    "target": "先把双根与峰值关系压到同一层",
                    "operation": "use 图像 to finish ask1 and reopen the structural layer",
                    "success_signal": "ask1 is settled",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "读出", "见证"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            def fake_refresh(runtime_state: dict, *, agenda_override=None, handoff_override=None, force=False):
                runtime_state["primitive_field_if_any"] = {
                    "layer_object": "x=e 两侧的双根如何压成同一等值关系",
                    "active_primitives": ["读出", "见证"],
                    "why_now": "lexical reopen residue",
                    "selection_basis": "explicit_hint",
                    "evidence_basis": "state_见证",
                    "tie_break_check": "x=e 两侧的双根如何压成同一等值关系",
                }

            leaked_touch = {
                "kind": "write",
                "target": "final.md",
                "operation": "Write one explicit answer/读出 dependency, field set, or certificate surface.",
                "success_signal": "asked_medium_is_exact_and_executable",
                "owner_skill_if_any": "读出",
                "owner_skill_combo_if_any": ["读出", "见证"],
            }
            recomposed_touch = {
                "kind": "check",
                "target": "x=e 两侧的双根如何压成同一等值关系",
                "operation": "compare the same-height roots before any asked-medium serialization",
                "success_signal": "the structural ask2 layer is explicit",
                "owner_skill_if_any": "见证",
                "owner_skill_combo_if_any": ["见证", "读出"],
            }

            with patch("runtime_state.refresh_primitive_field_for_current_layer", new=fake_refresh), patch(
                "runtime_state.read_skill_authority_program",
                return_value=("读出", ["读出", "见证"], leaked_touch, False),
            ), patch(
                "runtime_state.derive_bound_program_candidate",
                return_value=recomposed_touch,
            ), patch(
                "runtime_state.closure_can_take_first_shot",
                return_value=False,
            ):
                loaded_state = json.loads(state_path.read_text(encoding="utf-8"))
                apply_same_carrier_landing(
                    loaded_state,
                    state_path,
                    next_object="最终封口前的双根对象层",
                    next_seam="x=e 两侧的双根如何压成同一等值关系",
                    next_debt="虽然 final.md 已被提到，但 ask2/ask3 仍需先完成后再 materialize final.md",
                    next_bite="先把双根关系压到更薄载体，再谈 final.md 和封口",
                )

        touch = loaded_state.get("landed_next_touch_if_any", {})
        layer = loaded_state.get("layer_composition_if_any", {})
        self.assertNotEqual(touch.get("target"), "final.md")
        self.assertEqual(touch.get("target"), "x=e 两侧的双根如何压成同一等值关系")
        self.assertEqual(layer.get("surface"), "takeover_recomposition")
        self.assertNotEqual(layer.get("authorized_bite", {}).get("target"), "final.md")

    def test_competition_refreshes_live_handoff_into_concrete_spend_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "h(x)=lnx/x 的双交点与峰值结构",
                "current_seam": "x=e 两侧的双根如何压成同一等值关系",
                "current_debt": "证明双根时 x1x2>e^2，并给出第(3)问的范围结论",
                "next_bite": "把 q(u) 与 q(2-u) 的比较真正花到 ask2/ask3 上",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "carrier_handoff_if_any": {
                    "trigger": "same_carrier_change",
                    "from_slot": "parameter-root-structure",
                    "to_object": "u=ln x 上的等值函数 q(u)=u-ln u",
                    "winning_pressure": "u-重编码让双根乘积与峰值同载体闭合",
                    "why_local": "ask2/ask3 还未对象侧收束",
                    "warm_field": {
                        "active_pressures": ["重编码", "见证"],
                        "cheap_check": "比较 q(u) 与 q(2-u)",
                        "primitive_hints": ["重编码", "见证"],
                        "evidence_basis": "cheap_check",
                    },
                },
                "primitive_field_if_any": {
                    "layer_object": "u=ln x 上的等值函数 q(u)=u-ln u",
                    "active_primitives": ["重编码", "见证"],
                    "why_now": "ask2/ask3 还未对象侧收束",
                    "selection_basis": "tie_break",
                    "evidence_basis": "mixed",
                    "tie_break_check": "比较 q(u) 与 q(2-u)",
                },
                "layer_composition_if_any": {
                    "surface": "carrier_handoff",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": False,
                    "must_spend_handoff": True,
                    "leading_skill_if_any": "投影",
                    "reason": "the thinner carrier is already explicit, so one current-layer combination now owns the next local bite",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "u=ln x 上的等值函数 q(u)=u-ln u",
                        "operation": "Project onto one axis, section, or interface value and test whether exact closure survives there.",
                        "success_signal": "投影 became explicit on u=ln x 上的等值函数 q(u)=u-ln u",
                        "owner_skill_if_any": "投影",
                        "owner_skill_combo_if_any": ["投影", "重编码", "见证"],
                    },
                    "controlled_object": "u=ln x 上的等值函数 q(u)=u-ln u",
                },
                "output_status": {
                    "touched": False,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        skill_touch = {
            "kind": "write",
            "target": "u=ln x 上的等值函数 q(u)=u-ln u",
            "operation": "Project onto one axis, section, or interface value and test whether exact closure survives there.",
            "success_signal": "投影 became explicit on u=ln x 上的等值函数 q(u)=u-ln u",
            "owner_skill_if_any": "投影",
            "owner_skill_combo_if_any": ["投影", "重编码", "见证"],
        }
        primitive_touch = {
            "kind": "check",
            "target": "比较 q(u) 与 q(2-u)",
            "operation": "compare q(u) against q(2-u) to separate the double-root layer before closure",
            "success_signal": "the double-root witness is explicit",
            "owner_skill_if_any": "见证",
            "owner_skill_combo_if_any": ["见证", "重编码"],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with patch("runtime_state.read_skill_authority_program", return_value=("投影", ["投影", "重编码", "见证"], skill_touch, False)), patch(
                "runtime_state.derive_primitive_program_candidate",
                return_value=primitive_touch,
            ):
                command_competition(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "mode": "set",
                            "layer_object": "u=ln x 上的等值函数 q(u)=u-ln u",
                            "candidate": [
                                "重编码|u=ln x 上的等值函数 q(u)=u-ln u|把双根关系压到同一等值函数",
                                "见证|比较 q(u) 与 q(2-u)|分离 u1+u2 是否大于 2",
                            ],
                            "separating_check": "比较 q(u) 与 q(2-u)",
                            "winner_if_any": "见证",
                        },
                    )()
                )

            refreshed_state = json.loads(state_path.read_text(encoding="utf-8"))

        layer = refreshed_state.get("layer_composition_if_any", {})
        bite = layer.get("authorized_bite", {})
        self.assertEqual(bite.get("kind"), "check")
        self.assertEqual(bite.get("target"), "比较 q(u) 与 q(2-u)")
        self.assertEqual(layer.get("controlled_object"), "比较 q(u) 与 q(2-u)")
        pending = pending_runtime_execution_contract(refreshed_state, layer_composition=layer)
        self.assertEqual(pending.get("required_action"), "spend_local")
        self.assertEqual(pending.get("authorized_bite", {}).get("target"), "比较 q(u) 与 q(2-u)")

    def test_primitive_program_prefers_explicit_handoff_target_even_when_text_looks_meta(self) -> None:
        handoff_target = "compress the stated object into one thinner controller-bearing carrier for the q(u)=q(2-u) comparison"
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "the original thick double-root object",
                "current_seam": handoff_target,
                "current_debt": "spend the thinner carrier before commentary regrows",
                "next_bite": "land one symmetric separating check on the thinner carrier",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "carrier_handoff_if_any": {
                    "to_object": handoff_target,
                    "reason": "the thinner carrier is already explicit",
                },
                "layer_composition_if_any": {
                    "surface": "carrier_handoff",
                    "must_spend_handoff": True,
                },
            }
        )

        touch = derive_primitive_program_candidate(
            state,
            [],
            primitive_field_override={
                "layer_object": handoff_target,
                "active_primitives": ["对称"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
            },
        )

        self.assertIsInstance(touch, dict)
        self.assertEqual(touch.get("target"), handoff_target)

    def test_validate_state_accepts_inline_text_materialization_evidence(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "图像层对象",
                "current_seam": "图像层对象",
                "current_debt": "先在当前层留下一个真实触点",
                "next_bite": "图像先落一刀",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "图像层对象",
                    "operation": "用图像先把当前层落成一个可检查的触点",
                    "success_signal": "当前层被图像真实改写",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "对称"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            exit_code = command_execute_local(
                argparse.Namespace(
                    state_file=str(state_path),
                    worked_step="图像：先在当前层留下一个可执行触点。",
                    summary="图像层已经真实落地",
                    output_file=None,
                    cosmetic_only=False,
                    contains_unsupported=False,
                    contains_placeholder=False,
                )
            )

            saved_state = json.loads(state_path.read_text(encoding="utf-8"))
            report = build_report(saved_state, state_path)

        self.assertEqual(exit_code, 0)
        self.assertEqual(saved_state.get("materialization_evidence", {}).get("kind"), "inline_text")
        self.assertFalse(
            any(
                "materialization_evidence" in problem
                for problem in report.get("problems", [])
            )
        )

    def test_materialization_evidence_cli_accepts_inline_text_kind(self) -> None:
        parser = build_parser()

        args = parser.parse_args(
            [
                "evidence",
                "set",
                "state.json",
                "--evidence-kind",
                "inline_text",
                "--evidence-location",
                "inline",
                "--evidence-summary",
                "图像层已接管",
            ]
        )

        self.assertEqual(args.evidence_kind, "inline_text")

    def test_parser_accepts_materialize_asked_medium_command(self) -> None:
        parser = build_parser()

        args = parser.parse_args(["materialize-asked-medium", "state.json"])

        self.assertEqual(args.state_file, "state.json")
        self.assertIs(args.func, command_materialize_asked_medium)

    def test_pending_bound_program_refuses_next_touch_and_controller_readers(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            command_bind_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "previous_state": None,
                        "allow_handoff": False,
                        "allow_rival": False,
                    },
                )()
            )
            next_touch_payload, next_touch_exit = build_next_touch_consumption(state_path)
            controller_payload, controller_exit = build_controller_读出(state_path)

        self.assertIn(next_touch_exit, {1, 2})
        if next_touch_payload.get("pending_transition"):
            self.assertEqual(
                next_touch_payload.get("allowed_transition_surfaces"),
                ["execute_local"],
            )
        self.assertNotIn("closure_nucleus", next_touch_payload)

        self.assertIn(controller_exit, {1, 2})
        if controller_payload.get("pending_transition"):
            self.assertEqual(
                controller_payload.get("allowed_transition_surfaces"),
                ["execute_local"],
            )
        self.assertNotIn("closure_nucleus", controller_payload)

    def test_bind_local_keeps_conic_first_touch_on_problem_facing_target(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "圆锥曲线问题中证明两条相关直线的交点落在定直线 x=-1 上",
                "current_seam": "固定线 x=-1 是否就是交点的横坐标",
                "current_debt": "目标只问固定横坐标，不先回收完整交点坐标；在 x=-1 这条锚线比较两条线的高度是否重合",
                "next_bite": "盯住定直线 x=-1 做目标式证明，先比较两条线在这条竖线上的读数，不先解全坐标",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "conic_fixed_line_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            command_bind_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "previous_state": None,
                        "allow_handoff": False,
                        "allow_rival": False,
                    },
                )()
            )
            bound_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertEqual(
            bound_state.get("bound_program", {}).get("target"),
            "固定线 x=-1 是否就是交点的横坐标",
        )
        self.assertEqual(
            bound_state.get("layer_composition_if_any", {}).get("controlled_object"),
            "固定线 x=-1 是否就是交点的横坐标",
        )

    def test_bind_local_keeps_container_first_touch_on_problem_facing_target(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "2025新高考II卷第14题：圆柱内放置两个相同球，求相关长度或半径关系",
                "current_seam": "决定量是不是完全由那个中心截面里的两圆心距离和容器宽高关系控制",
                "current_debt": "不要把三维立体几何整体硬做；先找真正控制两个球与圆柱壁接触关系的那个二维截面",
                "next_bite": "先切出同时经过两个球心和关键接触方向的截面，把问题压成长方形里两个圆怎么挤，再看是否一条勾股就闭合",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "container_slice_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            command_bind_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "previous_state": None,
                        "allow_handoff": False,
                        "allow_rival": False,
                    },
                )()
            )
            bound_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertEqual(
            bound_state.get("bound_program", {}).get("target"),
            "决定量是不是完全由那个中心截面里的两圆心距离和容器宽高关系控制",
        )
        self.assertEqual(
            bound_state.get("layer_composition_if_any", {}).get("controlled_object"),
            "决定量是不是完全由那个中心截面里的两圆心距离和容器宽高关系控制",
        )

    def test_program_has_meta_narration_detects_apc_style_structural_complaint(self) -> None:
        self.assertTrue(
            program_has_meta_narration(
                {
                    "kind": "write",
                    "target": "Deformed recursion is awkward; need a thinner carrier that supports exact minimization",
                    "operation": "rewrite the live burden on one thinner carrier",
                }
            )
        )
        self.assertFalse(
            program_has_meta_narration(
                {
                    "kind": "write",
                    "target": "固定线 x=-1 是否就是交点的横坐标",
                    "operation": "draw one minimal problem diagram for 固定线 x=-1 是否就是交点的横坐标",
                }
            )
        )

    def test_bind_local_prefers_problem_facing_target_over_meta_structural_complaint(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "Characterize strings T with deformed balance and minimize additions around S",
                "current_seam": "Deformed recursion is awkward; need a thinner carrier that supports exact minimization",
                "current_debt": "Need an exact structural criterion for T such that T+) is balanced, then minimize edits by adding a prefix and suffix around S",
                "next_bite": "Compress deformed-balance definition into a direct prefix/suffix balance condition",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "apc_m_meta_seam_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            command_bind_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "previous_state": None,
                        "allow_handoff": False,
                        "allow_rival": False,
                    },
                )()
            )
            bound_state = json.loads(state_path.read_text(encoding="utf-8"))

        bound_program = bound_state.get("bound_program", {})
        target = bound_program.get("target", "")
        self.assertTrue(target)
        self.assertNotIn("awkward", target.lower())
        self.assertNotIn("need a thinner carrier", target.lower())
        self.assertFalse(is_generic_runtime_operation(bound_program))

    def test_fresh_blind_same_carrier_first_entry_rejects_generic_skill_template(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "2026 ICPC APC M Deformed Balance problem summary",
                "current_seam": "compress the stated object into one thinner controller-bearing carrier without turning the bootstrap itself into route guidance",
                "current_debt": "separate the real controller from decorative burden and keep the next runtime transition local, honest, and non-scripted",
                "next_bite": "bind one concrete local touch on the current carrier without adding route hints or problem-specific solve staging",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )
        program = {
            "kind": "write",
            "target": "2026 ICPC APC M Deformed Balance problem summary",
            "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
            "success_signal": "external 图像 became explicit on 2026 ICPC APC M Deformed Balance problem summary",
            "owner_skill_if_any": "图像",
            "owner_skill_combo_if_any": ["图像", "状态拆分", "见证"],
        }

        self.assertTrue(is_generic_runtime_operation(program))
        self.assertFalse(fresh_blind_same_carrier_first_entry(program, state=state))

    def test_fresh_blind_same_carrier_first_entry_rejects_write_self_rewrite_on_whole_problem(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "整道参数题的厚对象",
                "current_seam": "同一条值载体上的交点结构",
                "current_debt": "先把整题压到同一条值载体，不回到厚对象",
                "next_bite": "bind one fresh touch",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )
        program = {
            "kind": "write",
            "target": "整道参数题的厚对象",
            "operation": "draw one minimal problem diagram on the whole problem object",
            "success_signal": "the controller is explicit",
            "current_layer_object_if_any": "整道参数题的厚对象",
            "controlled_object_if_any": "整道参数题的厚对象",
            "owner_skill_if_any": "图像",
            "owner_skill_combo_if_any": ["图像", "状态拆分", "投影"],
        }

        self.assertFalse(fresh_blind_same_carrier_first_entry(program, state=state))

    def test_bind_local_refuses_pure_meta_structural_complaint_as_problem_born_bite(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "Need a thinner carrier before ordinary continuation",
                "current_seam": "Deformed recursion is awkward; need a thinner carrier that supports exact minimization",
                "current_debt": "Need an exact structural criterion before ordinary continuation regrows",
                "next_bite": "rewrite the live burden on one thinner carrier",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "pure_meta_structural_complaint_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as exc:
                command_bind_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "previous_state": None,
                            "allow_handoff": False,
                            "allow_rival": False,
                        },
                    )()
                )

        self.assertIn("control/meta narration", str(exc.exception))

    def test_bind_local_keeps_fresh_blind_counter_touch_semantically_owned_by_open_combo(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "deformed strings as unary-binary tree encodings with target class +1 and nonnegative prefixes",
                "current_seam": "ordinary balanced-prefix heuristics explain some samples but fail on (() and other class-+1 counterexamples",
                "current_debt": "separate the real tree-weight invariant from ordinary bracket-prefix repair",
                "next_bite": "kill the fake main line first",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "fresh_blind_counter_touch_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            with patch(
                "runtime_guard._sanitize_public_skill_competition",
                side_effect=lambda payload: payload,
            ):
                command_bind_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "previous_state": None,
                            "allow_handoff": False,
                            "allow_rival": False,
                        },
                    )()
                )

            bound_state = json.loads(state_path.read_text(encoding="utf-8"))

        bound_program = bound_state.get("bound_program") or {}
        layer = bound_state.get("layer_composition_if_any", {})
        lighting = layer.get("lighting_if_any", {})
        self.assertTrue(bound_program.get("owner_skill_if_any"))
        self.assertIn(
            bound_program.get("owner_skill_if_any"),
            bound_program.get("owner_skill_combo_if_any", []),
        )
        self.assertEqual(bound_program.get("kind"), "check")
        self.assertEqual(bound_program.get("target"), state["current_seam"])
        for skill in ["反问", "对称", "见证", "守恒"]:
            self.assertIn(skill, bound_program.get("owner_skill_combo_if_any", []))
        self.assertGreaterEqual(len(lighting.get("candidate_skills_if_any", [])), 5)
        self.assertIn("反问", lighting.get("candidate_skills_if_any", []))
        self.assertIn("守恒", lighting.get("supporting_skills_if_any", []))
        self.assertIn("not a required order", lighting.get("anti_pipeline_note", ""))

    def test_bind_local_rebuilds_non_meta_first_touch_when_authorized_write_stays_meta(self) -> None:
        gaokao_problem = (
            Path(__file__).resolve().parents[1]
            / "blind_cases"
            / "gaokao"
            / "gaokao_2026_math_final.problem.txt"
        ).read_text(encoding="utf-8")
        gaokao_object = " ".join(line.strip() for line in gaokao_problem.splitlines() if line.strip())
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": gaokao_object,
                "current_seam": "compress the stated object into one thinner controller-bearing carrier without turning the bootstrap itself into route guidance",
                "current_debt": "separate the real controlling relation from decorative burden and keep the next runtime transition local, honest, and non-scripted",
                "next_bite": "bind one concrete local touch on the current carrier without adding route hints or problem-specific solve staging",
                "asked_medium_surface": "final.md",
                "revocation_handle": "gaokao_fresh_blind_meta_write_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")

            command_bind_local(
                type(
                    "Args",
                    (),
                    {
                        "state_file": str(state_path),
                        "previous_state": None,
                        "allow_handoff": False,
                        "allow_rival": False,
                    },
                )()
            )

            bound_state = json.loads(state_path.read_text(encoding="utf-8"))

        bound_program = bound_state.get("bound_program") or {}
        self.assertTrue(bound_program)
        self.assertFalse(program_has_meta_narration(bound_program))
        self.assertTrue(bound_program.get("owner_skill_if_any"))
        self.assertTrue(bound_program.get("owner_skill_combo_if_any"))

    def test_explicit_bound_program_control_bridge_is_execution_required_not_next_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
            }
        )

        bridge = derive_control_bridge(state, [])
        self.assertTrue(bridge.get("execution_required"))
        self.assertEqual(bridge.get("required_action"), "execute_local")
        self.assertEqual(bridge.get("authorized_bite", {}).get("target"), "equation ln x=(a-1)x on x>0")
        self.assertNotIn("next_touch", bridge)
        self.assertNotIn("default_local_action", bridge)

    def test_pending_runtime_execution_contract_only_allows_execute_local_before_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
            }
        )

        contract = pending_runtime_execution_contract(state)
        self.assertIsInstance(contract, dict)
        self.assertEqual(contract.get("required_action"), "execute_local")
        self.assertEqual(contract.get("allowed_transition_surfaces"), ["execute_local"])

    def test_pending_runtime_execution_contract_keeps_execute_local_when_touched_but_landing_not_ready(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "still the same live blocker layer",
                "current_seam": "still the same live blocker layer",
                "current_debt": "the requirement is still unmet on this same carrier",
                "next_bite": "keep compressing this blocker before any real landing",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "still the same live blocker layer",
                    "operation": "keep compressing the blocker on the same carrier",
                    "success_signal": "a genuinely thinner next layer becomes explicit",
                    "owner_skill_if_any": "守恒",
                    "owner_skill_combo_if_any": ["守恒", "状态拆分", "见证"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with patch("runtime_state.same_carrier_landing_is_ready", return_value=False):
            contract = pending_runtime_execution_contract(state)

        self.assertIsInstance(contract, dict)
        self.assertEqual(contract.get("required_action"), "execute_local")
        self.assertEqual(contract.get("allowed_transition_surfaces"), ["execute_local"])
        self.assertEqual(
            contract.get("reason"),
            "non_closure_bound_program_touched_but_layer_not_done",
        )

    def test_pending_contract_stops_for_blocked_nonclosure_after_runtime_owned_asked_medium_materialization(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "blind package handoff completeness for gaokao 2026 math final",
                "current_seam": "missing math prompt inside the packaged readset",
                "current_debt": "the allowed blind readset contains runtime/docs/tools but no problem statement",
                "next_bite": "check the readset boundary exactly once",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": "missing math prompt inside the packaged readset",
                    "operation": "push the blocker to one honest boundary case",
                    "success_signal": "the blocker is decided there",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "图像"],
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "final.md",
                    "summary": "runtime materialized the canonical asked-medium solve-markdown export",
                    "skill_serialized": True,
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": True,
                },
            }
        )

        contract = pending_runtime_execution_contract(state)
        self.assertIsNone(contract)

    def test_build_report_refuses_released_state_that_still_keeps_live_control_artifacts(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "双根层：a in (1,1+1/e) 时从同高两点压出乘积不等式",
                "current_seam": "要从同一高度的两点读出 x1x2>e^2",
                "current_debt": "把同高双根压成单参数不等式",
                "next_bite": "引入比值 t=x2/x1>1 并完成最终比较",
                "asked_medium_surface": "final.md",
                "release_veto": False,
                "bound_program": {
                    "kind": "write",
                    "target": "要从同一高度的两点读出 x1x2>e^2",
                    "operation": "rewrite the same-height double-root layer into one parameter and one decisive inequality",
                    "success_signal": "the ratio carrier and decisive inequality are explicit",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "读出", "见证", "极限边界"],
                },
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": False,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "图像",
                    "reason": "the carrier just tightened; recompute and bind one fresh current-layer skill combo before ordinary continuation regains value",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "要从同一高度的两点读出 x1x2>e^2",
                        "operation": "rewrite the same-height double-root layer into one parameter and one decisive inequality",
                        "success_signal": "the ratio carrier and decisive inequality are explicit",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "读出", "见证", "极限边界"],
                    },
                    "layer_object": "双根层：a in (1,1+1/e) 时从同高两点压出乘积不等式",
                    "controlled_object": "要从同一高度的两点读出 x1x2>e^2",
                    "current_seam": "要从同一高度的两点读出 x1x2>e^2",
                    "current_debt": "把同高双根压成单参数不等式",
                    "next_local_choice": "要从同一高度的两点读出 x1x2>e^2",
                    "gap_object": "把同高双根压成单参数不等式",
                    "transition_change": "bound write on same-height double-root layer",
                    "active_skill_combo_if_any": ["图像", "读出", "见证", "极限边界"],
                },
                "materialization_evidence": {
                    "kind": "file",
                    "location": "final.md",
                    "summary": "runtime materialized the canonical asked-medium solve-markdown export",
                    "skill_serialized": True,
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": True,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            report = build_report(state, state_path)

        self.assertIn("bound_program requires release_veto to stay active", report.get("problems", []))
        self.assertIn("layer_composition_if_any requires release_veto to stay active", report.get("problems", []))
        self.assertFalse(report.get("release_allowed"))

    def test_build_report_suppresses_resume_bridge_after_honest_release(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "把第(3)问直接读回峰值阈值并封口到 final.md",
                "current_seam": "第(3)问已经写完，只保留历史描述字段",
                "current_debt": "历史描述不应再导出成 resume bridge",
                "next_bite": "none",
                "asked_medium_surface": "final.md",
                "release_veto": False,
                "revocation_handle": "runtime_state",
                "uncertainty_mode": "classification",
                "primary_slot": "solve",
                "materialization_evidence": {
                    "kind": "file",
                    "location": "final.md",
                    "summary": "runtime materialized the exact asked-medium 读出 from solve-step serialization",
                    "skill_serialized": True,
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": True,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            final_path = Path(tmpdir) / "final.md"
            final_path.write_text("# Runtime Solve Steps\n\n1. 完成。\n", encoding="utf-8")
            state["materialization_evidence"]["location"] = str(final_path)
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            report = build_report(state, state_path)

        self.assertTrue(report.get("release_allowed"))
        self.assertEqual(report.get("problems"), [])
        self.assertIsNone(report.get("resume_bridge"))

    def test_build_report_keeps_resume_bridge_while_release_veto_is_active(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "把第(3)问直接读回峰值阈值并封口到 final.md",
                "current_seam": "第(3)问还没有写完",
                "current_debt": "还需要一个真实 final-layer worked step",
                "next_bite": "先写第(3)问再封口",
                "asked_medium_surface": "final.md",
                "release_veto": True,
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "runtime_state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            report = build_report(state, state_path)

        self.assertIsInstance(report.get("resume_bridge"), dict)

    def test_run_bind_once_stops_at_pending_execute_local_for_untouched_bound_program(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            payload, exit_code = run_bind_local_once(
                state_path,
                allow_handoff=False,
                spend_handoff=False,
                allow_rival=False,
                previous_state=None,
            )
            rebound_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertIn(exit_code, {1, 2})
        self.assertTrue(payload.get("pending_transition"))
        self.assertEqual(payload.get("allowed_transition_surfaces"), ["execute_local"])
        self.assertEqual(payload.get("binding_action"), "pending_execute_local")
        self.assertEqual(
            rebound_state.get("bound_program", {}).get("target"),
            "equation ln x=(a-1)x on x>0",
        )

    def test_run_bind_once_consumes_one_explicit_execute_step_then_rebinds_next_layer(self) -> None:
        first_bite = {
            "kind": "write",
            "target": "equation ln x=(a-1)x on x>0",
            "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
            "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
            "owner_skill_if_any": "图像",
            "owner_skill_combo_if_any": ["图像", "见证"],
        }
        rebound_bite = {
            "kind": "write",
            "target": "two-root product gap on ln x=(a-1)x",
            "operation": "见证 one thinner current-layer product relation before asked-medium closure",
            "success_signal": "the reopened layer is explicit on the two-root product gap",
            "owner_skill_if_any": "见证",
            "owner_skill_combo_if_any": ["见证", "图像"],
        }
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": copy.deepcopy(first_bite),
                "output_status": {
                    "touched": False,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        calls = {
            "execute": 0,
            "land": 0,
            "bind": 0,
            "worked_step": "",
            "summary": "",
        }

        def fake_execute_local(args: object) -> int:
            calls["execute"] += 1
            calls["worked_step"] = getattr(args, "worked_step")
            calls["summary"] = getattr(args, "summary")
            state_path = Path(getattr(args, "state_file"))
            rebound = json.loads(state_path.read_text(encoding="utf-8"))
            rebound["materialization_evidence"] = {
                "kind": "inline_text",
                "location": "inline",
                "summary": getattr(args, "summary"),
                "worked_step": getattr(args, "worked_step"),
            }
            rebound["output_status"] = {
                "touched": True,
                "cosmetic_only": False,
                "contains_unsupported": False,
                "contains_placeholder": False,
                "final_artifact_materialized": False,
            }
            state_path.write_text(json.dumps(rebound, ensure_ascii=True, indent=2), encoding="utf-8")
            return 0

        def fake_land_local(args: object) -> int:
            calls["land"] += 1
            state_path = Path(getattr(args, "state_file"))
            rebound = json.loads(state_path.read_text(encoding="utf-8"))
            rebound["bound_program"] = None
            rebound["landed_next_touch_if_any"] = copy.deepcopy(rebound_bite)
            rebound["layer_composition_if_any"] = {
                "surface": "takeover_recomposition",
                "event_owned": True,
                "must_bind_local_bite": True,
                "authorized_bite": copy.deepcopy(rebound_bite),
                "leading_skill_if_any": rebound_bite["owner_skill_if_any"],
            }
            rebound["materialization_evidence"] = None
            rebound["output_status"] = {
                "touched": False,
                "cosmetic_only": False,
                "contains_unsupported": False,
                "contains_placeholder": False,
                "final_artifact_materialized": False,
            }
            state_path.write_text(json.dumps(rebound, ensure_ascii=True, indent=2), encoding="utf-8")
            return 0

        def fake_bind_local(args: object) -> int:
            calls["bind"] += 1
            state_path = Path(getattr(args, "state_file"))
            rebound = json.loads(state_path.read_text(encoding="utf-8"))
            rebound["bound_program"] = copy.deepcopy(rebound_bite)
            rebound["landed_next_touch_if_any"] = None
            rebound["layer_composition_if_any"] = {
                "surface": "bound_program",
                "event_owned": True,
                "must_bind_local_bite": False,
                "authorized_bite": copy.deepcopy(rebound_bite),
                "leading_skill_if_any": rebound_bite["owner_skill_if_any"],
            }
            state_path.write_text(json.dumps(rebound, ensure_ascii=True, indent=2), encoding="utf-8")
            return 0

        def fake_pending_contract(state_obj: dict, *, layer_composition: object = None) -> dict | None:
            output = state_obj.get("output_status") or {}
            if isinstance(state_obj.get("bound_program"), dict):
                if output.get("touched") is True:
                    return {
                        "reason": "non_closure_bound_program_touched_and_ready_to_land",
                        "required_action": "land_local",
                        "surface": "bound_program",
                        "authorized_bite": state_obj.get("bound_program"),
                        "allowed_transition_surfaces": ["land_local"],
                    }
                return {
                    "reason": "non_closure_bound_program_still_needs_execution",
                    "required_action": "execute_local",
                    "surface": "bound_program",
                    "authorized_bite": state_obj.get("bound_program"),
                    "allowed_transition_surfaces": ["execute_local"],
                }
            if isinstance(state_obj.get("landed_next_touch_if_any"), dict):
                return {
                    "reason": "rebound_local_touch_still_live",
                    "required_action": "bind_local",
                    "surface": "takeover_recomposition",
                    "authorized_bite": state_obj.get("landed_next_touch_if_any"),
                    "allowed_transition_surfaces": ["bind_local"],
                }
            return None

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with patch("runtime_consume.command_execute_local", side_effect=fake_execute_local), patch(
                "runtime_consume.command_land_local",
                side_effect=fake_land_local,
            ), patch(
                "runtime_consume.command_bind_local",
                side_effect=fake_bind_local,
            ), patch(
                "runtime_consume.pending_runtime_execution_contract",
                side_effect=fake_pending_contract,
            ):
                payload, exit_code = run_bind_local_once(
                    state_path,
                    allow_handoff=False,
                    spend_handoff=False,
                    allow_rival=False,
                    previous_state=None,
                    worked_step="图像：先把控制骨架压出来，再把两根的乘积缺口放到同层对象上。",
                    summary="图像：压出同层控制骨架",
                )
            rebound_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertIn(exit_code, {1, 2})
        self.assertEqual(calls["execute"], 1)
        self.assertEqual(calls["land"], 1)
        self.assertEqual(calls["bind"], 1)
        self.assertEqual(
            calls["worked_step"],
            "图像：先把控制骨架压出来，再把两根的乘积缺口放到同层对象上。",
        )
        self.assertEqual(calls["summary"], "图像：压出同层控制骨架")
        self.assertTrue(payload.get("consumed"))
        self.assertEqual(payload.get("binding_action"), "pending_execute_local")
        self.assertEqual(
            payload.get("transition_history"),
            ["execute_local", "land_local", "bind_local"],
        )
        self.assertEqual(
            rebound_state.get("bound_program", {}).get("target"),
            "two-root product gap on ln x=(a-1)x",
        )
        self.assertFalse(rebound_state.get("output_status", {}).get("touched"))

    def test_run_bind_once_reports_execute_local_refusal_for_explicit_worked_step(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
                "output_status": {
                    "touched": False,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        def fake_pending_contract(state_obj: dict, *, layer_composition: object = None) -> dict:
            return {
                "reason": "non_closure_bound_program_still_needs_execution",
                "required_action": "execute_local",
                "surface": "bound_program",
                "authorized_bite": state_obj.get("bound_program"),
                "allowed_transition_surfaces": ["execute_local"],
            }

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with patch(
                "runtime_consume.pending_runtime_execution_contract",
                side_effect=fake_pending_contract,
            ), patch(
                "runtime_consume.command_execute_local",
                side_effect=SystemExit(
                    "execute-local refused: visible skill expression is required on the live layer"
                ),
            ):
                payload, exit_code = run_bind_local_once(
                    state_path,
                    allow_handoff=False,
                    spend_handoff=False,
                    allow_rival=False,
                    previous_state=None,
                    worked_step="普通解释：先继续做题。",
                    summary="普通解释",
                )
            rebound_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 1)
        self.assertEqual(payload.get("binding_action"), "execute_local_refused")
        self.assertIn("visible skill expression", payload.get("reason", ""))
        self.assertEqual(payload.get("transition_history"), None)
        self.assertFalse(rebound_state.get("output_status", {}).get("touched"))

    def test_stalled_runtime_continuation_only_triggers_for_unfinished_live_runtime(self) -> None:
        live_state = copy.deepcopy(DEFAULT_STATE)
        live_state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "runtime_state",
                "primary_slot": "solve",
                "release_veto": True,
            }
        )

        continuation = stalled_runtime_continuation(
            live_state,
            {"problems": [], "control_signals": {}},
            required_action="bind_local",
            refusal_reason="bind-local refused: no unique local bite became concrete enough to bind",
            transition_history=[],
        )
        self.assertIsInstance(continuation, dict)
        self.assertIn("unfinished_current_layer", continuation.get("trigger_signals", []))
        self.assertIn("bind_local", continuation.get("allowed_transition_surfaces", []))

        finished_state = copy.deepcopy(live_state)
        finished_state["release_veto"] = False
        self.assertIsNone(
            stalled_runtime_continuation(
                finished_state,
                {"problems": [], "control_signals": {}},
                required_action="bind_local",
                refusal_reason="bind-local refused: no unique local bite became concrete enough to bind",
                transition_history=[],
            )
        )

    def test_stalled_runtime_continuation_allows_unfinished_land_local_failure_under_god_view(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "same carrier still owns the blocker",
                "current_seam": "landing tried to reopen the same layer again",
                "current_debt": "the requirement gap is still live",
                "next_bite": "keep compressing this blocker",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )
        report = {
            "problems": [],
            "layer_composition": {
                "active": True,
                "surface": "bound_program",
            },
            "control_signals": {
                "meta_controls": {
                    "god_view": {"active": True},
                    "supervisory_pulse": {"active": True},
                },
                "micro_control_surface": {},
            },
        }

        continuation = stalled_runtime_continuation(
            state,
            report,
            required_action="land_local",
            refusal_reason="land-local refused: next same-carrier layer is identical to the current one",
            transition_history=["execute_local"],
        )

        self.assertIsInstance(continuation, dict)
        self.assertEqual(continuation.get("required_action"), "land_local")
        self.assertIn("god_view", continuation.get("trigger_signals", []))

    def test_run_bind_once_reopens_competition_once_after_stalled_bind_refusal(self) -> None:
        authorized_bite = {
            "kind": "write",
            "target": "equation ln x=(a-1)x on x>0",
            "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
            "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
            "owner_skill_if_any": "图像",
            "owner_skill_combo_if_any": ["图像", "见证"],
        }
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "runtime_state",
                "primary_slot": "solve",
                "release_veto": True,
            }
        )

        calls = {"count": 0}

        def fake_bind_local(args: object) -> int:
            calls["count"] += 1
            state_path = Path(getattr(args, "state_file"))
            rebound = json.loads(state_path.read_text(encoding="utf-8"))
            if calls["count"] == 1:
                raise SystemExit("bind-local refused: no unique local bite became concrete enough to bind")
            rebound["bound_program"] = copy.deepcopy(authorized_bite)
            state_path.write_text(json.dumps(rebound, ensure_ascii=True, indent=2), encoding="utf-8")
            return 0

        def fake_pending_contract(state_obj: dict, *, layer_composition: object = None) -> dict:
            if isinstance(state_obj.get("bound_program"), dict):
                return {
                    "reason": "non_closure_bound_program_still_needs_execution",
                    "required_action": "execute_local",
                    "surface": "bound_program",
                    "authorized_bite": state_obj.get("bound_program"),
                    "allowed_transition_surfaces": ["execute_local"],
                }
            return {
                "reason": "fresh_blind_first_touch_still_pending",
                "required_action": "bind_local",
                "surface": "current_layer",
                "authorized_bite": copy.deepcopy(authorized_bite),
                "allowed_transition_surfaces": ["bind_local"],
            }

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with patch("runtime_consume.command_bind_local", side_effect=fake_bind_local), patch(
                "runtime_consume.pending_runtime_execution_contract",
                side_effect=fake_pending_contract,
            ):
                payload, exit_code = run_bind_local_once(
                    state_path,
                    allow_handoff=False,
                    spend_handoff=False,
                    allow_rival=False,
                    previous_state=None,
                )

        self.assertIn(exit_code, {1, 2})
        self.assertEqual(calls["count"], 2)
        self.assertEqual(payload.get("binding_action"), "pending_execute_local")
        self.assertEqual(payload.get("allowed_transition_surfaces"), ["execute_local"])
        continuation_loop = payload.get("continuation_loop", {})
        self.assertTrue(continuation_loop.get("active"))
        self.assertEqual(continuation_loop.get("rounds_used"), 1)
        self.assertIn("continue_competing", continuation_loop.get("transition_history", []))

    def test_run_bind_once_can_reopen_competition_more_than_once_while_gap_remains(self) -> None:
        authorized_bite = {
            "kind": "write",
            "target": "equation ln x=(a-1)x on x>0",
            "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
            "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
            "owner_skill_if_any": "图像",
            "owner_skill_combo_if_any": ["图像", "见证"],
        }
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "runtime_state",
                "primary_slot": "solve",
                "release_veto": True,
            }
        )

        calls = {"count": 0}

        def fake_bind_local(args: object) -> int:
            calls["count"] += 1
            state_path = Path(getattr(args, "state_file"))
            rebound = json.loads(state_path.read_text(encoding="utf-8"))
            if calls["count"] < 3:
                raise SystemExit("bind-local refused: no unique local bite became concrete enough to bind")
            rebound["bound_program"] = copy.deepcopy(authorized_bite)
            state_path.write_text(json.dumps(rebound, ensure_ascii=True, indent=2), encoding="utf-8")
            return 0

        def fake_pending_contract(state_obj: dict, *, layer_composition: object = None) -> dict:
            if isinstance(state_obj.get("bound_program"), dict):
                return {
                    "reason": "non_closure_bound_program_still_needs_execution",
                    "required_action": "execute_local",
                    "surface": "bound_program",
                    "authorized_bite": state_obj.get("bound_program"),
                    "allowed_transition_surfaces": ["execute_local"],
                }
            return {
                "reason": "fresh_blind_first_touch_still_pending",
                "required_action": "bind_local",
                "surface": "current_layer",
                "authorized_bite": copy.deepcopy(authorized_bite),
                "allowed_transition_surfaces": ["bind_local"],
            }

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with patch("runtime_consume.command_bind_local", side_effect=fake_bind_local), patch(
                "runtime_consume.pending_runtime_execution_contract",
                side_effect=fake_pending_contract,
            ):
                payload, exit_code = run_bind_local_once(
                    state_path,
                    allow_handoff=False,
                    spend_handoff=False,
                    allow_rival=False,
                    previous_state=None,
                )

        self.assertIn(exit_code, {1, 2})
        self.assertEqual(calls["count"], 3)
        self.assertEqual(payload.get("binding_action"), "pending_execute_local")
        self.assertEqual(payload.get("allowed_transition_surfaces"), ["execute_local"])
        continuation_loop = payload.get("continuation_loop", {})
        self.assertTrue(continuation_loop.get("active"))
        self.assertEqual(continuation_loop.get("rounds_used"), 2)
        self.assertEqual(
            continuation_loop.get("transition_history", []).count("continue_competing"),
            2,
        )

    def test_run_bind_once_reopens_after_land_local_refusal_when_gap_is_still_live(self) -> None:
        rebound_bite = {
            "kind": "check",
            "target": "remaining signed gap",
            "operation": "rebind one stronger local check on the still-live blocker",
            "success_signal": "the remaining gap is explicit again",
            "owner_skill_if_any": "见证",
            "owner_skill_combo_if_any": ["见证", "图像"],
        }
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "same carrier still owns the blocker",
                "current_seam": "landing tried to reopen the same layer again",
                "current_debt": "the requirement gap is still live",
                "next_bite": "keep compressing this blocker",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "land_retry_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "check",
                    "target": "same carrier still owns the blocker",
                    "operation": "push the blocker to one honest boundary case",
                    "success_signal": "the blocker is decided there",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "见证"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": False,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        calls = {"land": 0, "bind": 0}

        def fake_land_local(args: object) -> int:
            calls["land"] += 1
            raise SystemExit("land-local refused: next same-carrier layer is identical to the current one")

        def fake_bind_local(args: object) -> int:
            calls["bind"] += 1
            state_path = Path(getattr(args, "state_file"))
            rebound = json.loads(state_path.read_text(encoding="utf-8"))
            rebound["primitive_takeover_gate_if_any"] = None
            rebound["bound_program"] = copy.deepcopy(rebound_bite)
            state_path.write_text(json.dumps(rebound, ensure_ascii=True, indent=2), encoding="utf-8")
            return 0

        def fake_pending_contract(state_obj: dict, *, layer_composition: object = None) -> dict | None:
            if isinstance(state_obj.get("bound_program"), dict):
                if state_obj.get("output_status", {}).get("touched") is True:
                    return {
                        "reason": "non_closure_bound_program_touched_and_ready_to_land",
                        "required_action": "land_local",
                        "surface": "bound_program",
                        "authorized_bite": state_obj.get("bound_program"),
                        "allowed_transition_surfaces": ["land_local"],
                    }
                return {
                    "reason": "non_closure_bound_program_still_needs_execution",
                    "required_action": "execute_local",
                    "surface": "bound_program",
                    "authorized_bite": state_obj.get("bound_program"),
                    "allowed_transition_surfaces": ["execute_local"],
                }
            if isinstance(state_obj.get("primitive_takeover_gate_if_any"), dict):
                return {
                    "reason": "primitive_takeover_gate_still_live",
                    "required_action": "bind_local",
                    "surface": "takeover_recomposition",
                    "authorized_bite": copy.deepcopy(rebound_bite),
                    "allowed_transition_surfaces": ["bind_local"],
                }
            return None

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with patch("runtime_consume.command_land_local", side_effect=fake_land_local), patch(
                "runtime_consume.command_bind_local",
                side_effect=fake_bind_local,
            ), patch(
                "runtime_consume.pending_runtime_execution_contract",
                side_effect=fake_pending_contract,
            ):
                payload, exit_code = run_bind_local_once(
                    state_path,
                    allow_handoff=False,
                    spend_handoff=False,
                    allow_rival=False,
                    previous_state=None,
                )
            rebound_state = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertIn(exit_code, {1, 2})
        self.assertEqual(calls["land"], 1)
        self.assertEqual(calls["bind"], 1)
        self.assertEqual(payload.get("binding_action"), "pending_execute_local")
        self.assertEqual(payload.get("allowed_transition_surfaces"), ["execute_local"])
        self.assertFalse(rebound_state.get("output_status", {}).get("touched"))
        continuation_loop = payload.get("continuation_loop", {})
        self.assertTrue(continuation_loop.get("active"))
        self.assertEqual(continuation_loop.get("rounds_used"), 1)
        self.assertIn("continue_competing", continuation_loop.get("transition_history", []))

    def test_run_bind_once_materializes_pending_asked_medium_closure(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "three solved subresults now only need exact closure",
                "current_seam": "write the already-solved proof into final.md without reopening ordinary derivation",
                "current_debt": "materialize the exact asked medium honestly",
                "next_bite": "seal final.md from the live closure carrier",
                "asked_medium_surface": "final.md",
                "revocation_handle": "materialize_pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "final.md",
                    "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by the solved carrier",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "图像", "见证"],
                },
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": False,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "精确封口",
                    "reason": "exact closure now owns one local touch and should keep foreground authority until asked-medium contact changes",
                    "authorized_bite": {
                        "kind": "write",
                        "target": "final.md",
                        "operation": "seal the current thinner carrier into the asked medium by writing the exact answer forced by the solved carrier",
                        "success_signal": "asked_medium_is_exact_and_executable",
                        "owner_skill_if_any": "精确封口",
                        "owner_skill_combo_if_any": ["精确封口", "图像", "见证"],
                    },
                    "layer_object": "three solved subresults now only need exact closure",
                    "controlled_object": "final.md",
                    "current_seam": "write the already-solved proof into final.md without reopening ordinary derivation",
                    "current_debt": "materialize the exact asked medium honestly",
                    "next_local_choice": "final.md",
                    "transition_change": "bound write on final.md",
                    "active_skill_combo_if_any": ["精确封口", "图像", "见证"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with patch("runtime_state._solve_trace_export_allowed", return_value=True), patch(
                "runtime_state.render_runtime_solve_steps_markdown",
                return_value="# Runtime Solve Steps\n\n1. 封口。\n",
            ):
                payload, exit_code = run_bind_local_once(
                    state_path,
                    allow_handoff=False,
                    spend_handoff=False,
                    allow_rival=False,
                    previous_state=None,
                )
            rebound_state = json.loads(state_path.read_text(encoding="utf-8"))
            final_exists = (state_path.parent / "final.md").exists()

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload.get("binding_action"), "materialize_asked_medium")
        self.assertFalse(rebound_state.get("release_veto"))
        self.assertTrue(rebound_state.get("output_status", {}).get("final_artifact_materialized"))
        self.assertTrue(final_exists)

    def test_autonomous_transition_pressure_prefers_execute_local_for_untouched_bound_program(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            report = build_report(state, state_path)
            pressure = autonomous_transition_pressure(
                state,
                report,
                bootstrap_context=state["bootstrap_context"],
                runtime_evidence=build_runtime_evidence(state_path),
            )

        self.assertIsInstance(pressure, dict)
        self.assertEqual(pressure.get("selected_action"), "execute_local")
        self.assertIn(
            "execute_local",
            [candidate.get("action") for candidate in pressure.get("candidate_actions", [])],
        )

    def test_autonomous_transition_pressure_ignores_asked_medium_closure_bound_program(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "最大半径 r = 5/2 已确定",
                "current_seam": "把最终作答写入 answer.md",
                "current_debt": "把最终作答写入 answer.md",
                "next_bite": "把最终作答写入 answer.md",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "bound_program": {
                    "kind": "write",
                    "target": "answer.md",
                    "operation": "seal the exact answer",
                    "success_signal": "asked_medium_is_exact_and_executable",
                    "owner_skill_if_any": "精确封口",
                    "owner_skill_combo_if_any": ["精确封口", "极限边界"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            report = build_report(state, state_path)
            pressure = autonomous_transition_pressure(
                state,
                report,
                bootstrap_context=state["bootstrap_context"],
                runtime_evidence=build_runtime_evidence(state_path),
            )

        self.assertIsNone(pressure)

    def test_land_local_refuses_untouched_bound_program(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            with self.assertRaises(SystemExit) as land_ctx:
                command_land_local(
                    type(
                        "Args",
                        (),
                        {
                            "state_file": str(state_path),
                            "current_object": "",
                            "current_seam": "",
                            "current_debt": "",
                            "next_bite": "",
                        },
                    )()
                )

        self.assertIn("still needs one real execute-local touch", str(land_ctx.exception))

    def test_land_local_clears_contains_unsupported_for_reopened_layer(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "carrier",
                "current_seam": "carrier",
                "current_debt": "tighten seam",
                "next_bite": "make one same-carrier structural move",
                "asked_medium_surface": "answer.md",
                "bound_program": {
                    "kind": "check",
                    "target": "carrier",
                    "operation": "take the 对称-revealing slice",
                    "success_signal": "carrier changes shape",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
                "output_status": {
                    "touched": True,
                    "cosmetic_only": False,
                    "contains_unsupported": True,
                    "contains_placeholder": False,
                    "final_artifact_materialized": False,
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            apply_same_carrier_landing(
                state,
                state_path,
                next_object="carrier_thinner",
                next_seam="carrier_thinner",
                next_debt="new local seam",
                next_bite="bind the thinner carrier",
            )

        self.assertFalse(state.get("output_status", {}).get("contains_unsupported"))

    def test_derived_bound_program_control_bridge_stays_candidate_surface(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
            }
        )
        bridge = derive_control_bridge(
            state,
            [],
            bound_program_override={
                "kind": "write",
                "target": "equation ln x=(a-1)x on x>0",
                "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
                "owner_skill_if_any": "图像",
                "owner_skill_combo_if_any": ["图像", "见证"],
            },
            bound_program_origin_override="derived",
        )
        self.assertEqual(bridge.get("program_origin"), "derived")
        self.assertIn("candidate_next_touch", bridge)
        self.assertIn("candidate_authorized_bite", bridge)
        self.assertNotIn("execution_required", bridge)

    def test_public_report_suppresses_generic_bridge_actions_under_owned_surface(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "Draw one minimal object whose forbidden adjacencies or crossings are easier to see than to narrate.",
                    "success_signal": "external 图像 became explicit on equation ln x=(a-1)x on x>0",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
            }
        )

        report = build_report(state, Path("dummy_state.json"))
        bridge = report.get("control_bridge", {})
        self.assertNotIn("next_touch", bridge)
        self.assertNotIn("candidate_next_touch", bridge)
        self.assertNotIn("default_local_action", bridge)
        self.assertNotIn("public_shadow_suppressed", bridge)

    def test_public_report_suppresses_candidate_authorized_bite_under_owned_surface(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "equation ln x=(a-1)x on x>0",
                "current_seam": "equation ln x=(a-1)x on x>0",
                "current_debt": "separate root-count regimes and bind the two-root product gap",
                "next_bite": "use the carrier 图像 before asked-medium writeout",
                "asked_medium_surface": "solve_writeup.md",
                "revocation_handle": "pending_contract_case",
                "primary_slot": "solve",
                "release_veto": True,
                "bound_program": {
                    "kind": "write",
                    "target": "equation ln x=(a-1)x on x>0",
                    "operation": "draw the carrier",
                    "owner_skill_if_any": "图像",
                    "owner_skill_combo_if_any": ["图像", "见证"],
                },
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "event_owned": True,
                    "current_seam": "equation ln x=(a-1)x on x>0",
                    "current_debt": "separate root-count regimes and bind the two-root product gap",
                    "transition_change": "bound write on equation ln x=(a-1)x on x>0",
                    "next_local_choice": "equation ln x=(a-1)x on x>0",
                    "active_skill_combo_if_any": ["图像", "见证"],
                    "authorized_bite": {
                        "kind": "write",
                        "target": "equation ln x=(a-1)x on x>0",
                        "operation": "draw the carrier",
                        "owner_skill_if_any": "图像",
                        "owner_skill_combo_if_any": ["图像", "见证"],
                    },
                },
            }
        )

        report = build_report(state, Path("dummy_state.json"))
        bridge = report.get("control_bridge", {})
        self.assertNotIn("candidate_authorized_bite", bridge)
        self.assertNotIn("candidate_authorized_bite", bridge.get("public_shadow_suppressed", []))

    def test_event_owned_layer_without_explicit_authorized_bite_does_not_count_as_ownership(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "carrier",
                "current_seam": "carrier seam",
                "current_debt": "bind one explicit local bite",
                "next_bite": "draw the carrier",
                "asked_medium_surface": "solve_writeup.md",
                "release_veto": True,
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "event_owned": True,
                    "authorized_bite": {
                        "kind": "write",
                        "target": "carrier seam",
                        "operation": "draw the carrier",
                    },
                },
            }
        )

        report = build_report(state, Path("dummy_state.json"))
        self.assertFalse(state_has_explicit_local_ownership_evidence(state))
        self.assertIn(
            "bound_program missing; derived next_touch stayed suppressed because explicit local ownership is still absent",
            report.get("warnings", []),
        )
        self.assertNotIn(
            "bound_program missing; derived next_touch used",
            report.get("warnings", []),
        )

    def test_stale_event_owned_layer_does_not_count_as_live_ownership(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "2026 ICPC APC M Deformed Balance problem summary",
                "current_seam": "compress the stated object into one thinner controller-bearing carrier without turning the bootstrap itself into route guidance",
                "current_debt": "separate the real controller from decorative burden and keep the next runtime transition local, honest, and non-scripted",
                "next_bite": "bind one concrete local touch on the current carrier without adding route hints or problem-specific solve staging",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
                "layer_composition_if_any": {
                    "surface": "bound_program",
                    "event_owned": True,
                    "authorized_bite": {
                        "kind": "write",
                        "target": "stale closure seam",
                        "operation": "seal stale output",
                        "owner_skill_if_any": "精确封口",
                        "owner_skill_combo_if_any": ["精确封口", "读出"],
                    },
                    "controlled_object": "stale closure seam",
                    "next_local_choice": "stale closure seam",
                },
            }
        )

        report = build_report(state, Path("dummy_state.json"))
        arena = derive_first_layer_arena(state, [])

        self.assertFalse(state_has_explicit_local_ownership_evidence(state))
        self.assertIn(
            "bound_program missing; derived next_touch stayed suppressed because explicit local ownership is still absent",
            report.get("warnings", []),
        )
        self.assertNotEqual(arena.get("focus_target"), "stale closure seam")
        self.assertNotEqual(
            arena.get("authorized_touch_if_any", {}).get("target"),
            "stale closure seam",
        )

    def test_non_authoritative_bridge_shadow_is_summary_only(self) -> None:
        payload = {
            "control_bridge": {
                "program_origin": "derived",
                "next_touch": {
                    "kind": "write",
                    "target": "carrier",
                    "operation": "draw the carrier",
                },
            },
            "skill_authority_bridge": {
                "executable_local_touch_if_any": {
                    "kind": "write",
                        "target": "different object",
                        "operation": "do something else",
                    }
            },
        }
        cool_shortcut_fields(payload)
        shadow = payload.get("non_authoritative_control_bridge", {})
        self.assertEqual(shadow.get("suppressed_action_keys"), ["next_touch"])
        self.assertNotIn("next_touch", shadow)

    def test_non_authoritative_bridge_shadow_summarizes_candidate_authorized_bite(self) -> None:
        payload = {
            "control_bridge": {
                "program_origin": "derived",
                "candidate_authorized_bite": {
                    "kind": "write",
                    "target": "carrier",
                    "operation": "draw the carrier",
                },
            },
            "skill_authority_bridge": {
                "executable_local_touch_if_any": {
                    "kind": "write",
                    "target": "different object",
                    "operation": "do something else",
                }
            },
        }
        cool_shortcut_fields(payload)
        shadow = payload.get("non_authoritative_control_bridge", {})
        self.assertEqual(shadow.get("suppressed_action_keys"), ["candidate_authorized_bite"])
        self.assertNotIn("candidate_authorized_bite", shadow)

    def test_public_skill_field_filters_control_meta_skills_out_of_lit_surface(self) -> None:
        payload = {
            "active_skills": ["图像", "特殊值探针", "抓本质", "精确封口"],
            "full_active_skills": ["图像", "特殊值探针", "抓本质", "精确封口"],
            "background_skills_if_any": ["抓本质", "精确封口"],
            "authority_skill_if_any": "抓本质",
            "closure_authority_skill_if_any": "精确封口",
        }

        sanitized = _sanitize_public_skill_field(payload)
        self.assertEqual(sanitized.get("active_skills"), ["图像", "特殊值探针"])
        self.assertEqual(sanitized.get("full_active_skills"), ["图像", "特殊值探针"])
        self.assertEqual(
            sanitized.get("background_control_skills_if_any"),
            ["抓本质", "精确封口"],
        )
        self.assertNotIn("authority_skill_if_any", sanitized)
        self.assertEqual(sanitized.get("closure_authority_skill_if_any"), "精确封口")
        self.assertEqual(sanitized.get("active_skills_zh"), ["图像", "特殊值探针"])
        self.assertEqual(
            sanitized.get("background_control_skills_if_any_zh"),
            ["抓本质", "精确封口"],
        )

    def test_public_skill_competition_filters_control_winner_into_control_slot(self) -> None:
        payload = {
            "candidates": [
                {"skill": "图像", "supporting_skills_if_any": ["见证", "抓本质"]},
                {"skill": "精确封口", "supporting_skills_if_any": ["图像"]},
                {"skill": "函数原型匹配", "supporting_skills_if_any": ["图像"]},
            ],
            "coactive_skills_if_any": ["图像", "精确封口", "见证"],
            "winning_skill_if_any": "精确封口",
        }

        sanitized = _sanitize_public_skill_competition(payload)
        self.assertEqual(len(sanitized.get("candidates", [])), 2)
        self.assertEqual(sanitized.get("candidates", [])[0].get("skill"), "图像")
        self.assertEqual(
            sanitized.get("candidates", [])[0].get("supporting_skills_if_any"),
            ["见证"],
        )
        self.assertEqual(sanitized.get("candidates", [])[1].get("skill"), "函数原型匹配")
        self.assertEqual(sanitized.get("coactive_skills_if_any"), ["图像", "见证"])
        self.assertNotIn("winning_skill_if_any", sanitized)
        self.assertEqual(sanitized.get("winning_control_skill_if_any"), "精确封口")
        self.assertEqual(sanitized.get("winning_control_skill_if_any_zh"), "精确封口")
        self.assertEqual(sanitized.get("coactive_skills_if_any_zh"), ["图像", "见证"])
        self.assertEqual(sanitized.get("candidates", [])[0].get("skill_zh"), "图像")

    def test_public_skill_lighting_surface_filters_control_labels(self) -> None:
        payload = {
            "lit_skill_if_any": "抓本质",
            "candidate_skills_if_any": ["图像", "抓本质", "见证", "函数原型匹配"],
            "supporting_skills_if_any": ["见证", "精确封口"],
            "false_first_skill_if_any": "精确封口",
            "comparison_skill_if_any": "抓本质",
            "role_split_if_any": {
                "primary_skill_if_any": "抓本质",
                "supporting_skills_if_any": ["图像", "精确封口", "见证"],
            },
            "competing_routes_if_any": [
                {"skill": "图像"},
                {"skill": "抓本质"},
                {"skill": "见证"},
            ],
        }

        sanitized = _sanitize_public_skill_lighting_surface(payload)
        self.assertEqual(sanitized.get("lit_control_skill_if_any"), "抓本质")
        self.assertNotIn("lit_skill_if_any", sanitized)
        self.assertEqual(sanitized.get("candidate_skills_if_any"), ["图像", "见证", "函数原型匹配"])
        self.assertEqual(sanitized.get("supporting_skills_if_any"), ["见证"])
        self.assertNotIn("false_first_skill_if_any", sanitized)
        self.assertNotIn("comparison_skill_if_any", sanitized)
        self.assertEqual(
            sanitized.get("role_split_if_any", {}).get("supporting_skills_if_any"),
            ["图像", "见证"],
        )
        self.assertNotIn("primary_skill_if_any", sanitized.get("role_split_if_any", {}))
        self.assertEqual(
            [route.get("skill") for route in sanitized.get("competing_routes_if_any", [])],
            ["图像", "见证"],
        )
        self.assertEqual(sanitized.get("lit_control_skill_if_any_zh"), "抓本质")
        self.assertEqual(
            sanitized.get("candidate_skills_if_any_zh"),
            ["图像", "见证", "函数原型匹配"],
        )

    def test_infer_primitives_from_text_keeps_broad_candidate_field(self) -> None:
        hits = infer_primitives_from_text(
            (
                "symmetric mirror balance limit boundary degeneration invariant total flow "
                "project shadow slice representative anchor graph quotient compatibility "
                "special value compare exact cover"
            )
        )

        self.assertGreaterEqual(len(hits), 6)
        for primitive in ["对称", "极限边界", "守恒", "投影", "赋值", "图像"]:
            self.assertIn(primitive, hits)

    def test_skill_competition_synthesizes_generic_combo_candidates(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "two mirrored candidates on both sides of one threshold",
                "current_seam": "equal-height comparison seam",
                "current_debt": "compare the mirrored sides before thick derivation regrows",
                "next_bite": "pick the strongest current-layer combo",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        competition = derive_skill_competition(
            state,
            [],
            primitive_field_override={
                "layer_object": state["current_object"],
                "active_primitives": ["对称", "见证", "极限边界", "投影", "特殊值探针"],
                "why_now": state["current_debt"],
                "selection_basis": "explicit_hint",
                "evidence_basis": "state_见证",
            },
            control_signals_override={
                "current_controller_view": {},
                "layerwise_reselection_pressure": {"active": False},
            },
        )

        self.assertIsInstance(competition, dict)
        self.assertTrue(
            any(
                isinstance(candidate, dict)
                and candidate.get("backed_by") == "generic_combo_competition"
                and len(candidate.get("supporting_skills_if_any", [])) >= 2
                for candidate in competition.get("candidates", [])
            )
        )
        self.assertGreaterEqual(len(competition.get("winning_combo_if_any", [])), 2)

    def test_build_report_rejects_persisted_derived_readout_fields(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "carrier",
                "current_debt": "debt",
                "next_bite": "bite",
                "asked_medium_surface": "answer.md",
                "revocation_handle": "handle",
                "uncertainty_mode": "low",
                "primary_slot": "solve",
                "release_veto": True,
                "skill_field": {"active_skills": ["图像"]},
            }
        )

        report = build_report(state, Path("state.json"))
        self.assertTrue(
            any(
                "derived readout-only field `skill_field`" in problem
                for problem in report.get("problems", [])
            )
        )

    def test_build_report_preserves_full_explicit_lighting_round_trip(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "carrier",
                "current_seam": "tight seam",
                "current_debt": "tighten local object",
                "next_bite": "bind local bite",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "landed_next_touch_if_any": {
                    "kind": "write",
                    "target": "carrier",
                    "operation": "land one current-layer rewrite",
                    "owner_skill_if_any": "极限边界",
                    "owner_skill_combo_if_any": ["极限边界", "见证", "对称"],
                },
                "layer_composition_if_any": {
                    "surface": "takeover_recomposition",
                    "event_owned": True,
                    "forbid_ordinary_regrowth": True,
                    "must_bind_local_bite": True,
                    "must_spend_handoff": False,
                    "leading_skill_if_any": "极限边界",
                    "authorized_bite": {
                        "kind": "check",
                        "target": "tight seam",
                        "operation": "check one exact boundary",
                        "owner_skill_if_any": "极限边界",
                        "owner_skill_combo_if_any": ["极限边界", "见证", "对称"],
                    },
                    "layer_object": "carrier",
                    "controlled_object": "tight seam",
                    "current_seam": "tight seam",
                    "current_debt": "tighten local object",
                    "next_local_choice": "tight seam",
                    "gap_object": "tighten local object",
                    "transition_change": "reopened exact boundary",
                    "active_skill_combo_if_any": ["极限边界", "见证", "对称"],
                    "lighting_if_any": {
                        "lit_control_skill_if_any": "抓本质",
                        "candidate_skills_if_any": ["极限边界", "见证", "对称"],
                        "comparison_skill_if_any": "见证",
                        "supporting_skills_if_any": ["见证", "对称"],
                        "verify_touch_if_any": {"target": "tight seam", "kind": "check"},
                        "competition_basis": "projected_gain_first_takeover",
                        "role_split_if_any": {
                            "primary_skill_if_any": "极限边界",
                            "supporting_skills_if_any": ["见证", "对称"],
                            "check_kind_if_any": "check",
                            "check_target_if_any": "tight seam",
                            "ordinary_operations_are_not_skills": True,
                        },
                        "ability_branch_if_any": {
                            "support_operation_is_subordinate": True,
                        },
                        "ordinary_operations_are_not_skills": True,
                    },
                },
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
            report = build_report(state, state_path)

        layer_lighting = report.get("layer_composition", {}).get("lighting_if_any", {})
        self.assertEqual(layer_lighting.get("lit_control_skill_if_any"), "抓本质")
        self.assertEqual(layer_lighting.get("comparison_skill_if_any"), "见证")
        self.assertEqual(
            layer_lighting.get("role_split_if_any", {}).get("supporting_skills_if_any"),
            ["见证", "对称"],
        )
        self.assertTrue(
            layer_lighting.get("ability_branch_if_any", {}).get("support_operation_is_subordinate")
        )

    def test_display_supporting_skills_stay_on_current_combo(self) -> None:
        layer = {
            "leading_skill_if_any": "相容",
            "active_skill_combo_if_any": ["相容", "见证", "状态拆分", "对称"],
            "supporting_skills_if_any": ["见证", "精确封口"],
            "lighting_if_any": {
                "lit_skill_if_any": "相容",
                "supporting_skills_if_any": ["状态拆分", "见证", "对称"],
                "role_split_if_any": {
                    "primary_skill_if_any": "相容",
                    "supporting_skills_if_any": ["状态拆分", "见证", "对称"],
                    "ordinary_operations_are_not_skills": True,
                },
            },
        }

        self.assertEqual(
            _display_supporting_skills(
                layer,
                combo=layer["active_skill_combo_if_any"],
                leading_skill=layer["leading_skill_if_any"],
            ),
            ["见证", "状态拆分", "对称"],
        )

    def test_build_problem_born_touch_for_skill_uses_generic_state_graph_lane(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "balanced string carrier with local state transitions",
                "current_seam": "prefix/suffix balance layer",
                "current_debt": "need one exact local-state criterion before ordinary repair regrows",
                "next_bite": "draw the live state graph before any ordinary continuation",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        touch = build_problem_born_touch_for_skill(
            state,
            "图像",
            target="prefix/suffix balance layer",
            supporting=["状态拆分", "见证"],
        )

        self.assertIsInstance(touch, dict)
        self.assertIn("two-lane state graph", str(touch.get("operation", "")))
        self.assertIn("prefix/suffix balance criterion", str(touch.get("operation", "")))
        self.assertEqual(touch.get("owner_skill_if_any"), "图像")
        self.assertEqual(touch.get("owner_skill_combo_if_any"), ["图像", "状态拆分", "见证"])

    def test_build_problem_born_touch_for_skill_prefers_live_seam_on_fresh_blind_first_touch(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "整道参数题的厚对象",
                "current_seam": "同一条值载体上的交点结构",
                "current_debt": "先把整题压到同一条值载体，不回到厚对象",
                "next_bite": "bind one fresh touch",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        touch = build_problem_born_touch_for_skill(
            state,
            "图像",
            target="整道参数题的厚对象",
            supporting=["状态拆分", "投影"],
        )

        self.assertIsInstance(touch, dict)
        self.assertEqual(touch.get("target"), "同一条值载体上的交点结构")
        self.assertNotEqual(touch.get("controlled_object_if_any"), "整道参数题的厚对象")

    def test_build_problem_born_touch_for_skill_drops_meta_only_rewrite_on_fresh_blind_first_touch(self) -> None:
        gaokao_problem = (
            Path(__file__).resolve().parents[1]
            / "blind_cases"
            / "gaokao"
            / "gaokao_2026_math_final.problem.txt"
        ).read_text(encoding="utf-8")
        gaokao_object = " ".join(line.strip() for line in gaokao_problem.splitlines() if line.strip())
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": gaokao_object,
                "current_seam": "compress the stated object into one thinner controller-bearing carrier without turning the bootstrap itself into route guidance",
                "current_debt": "separate the real controlling relation from decorative burden and keep the next runtime transition local, honest, and non-scripted",
                "next_bite": "bind one concrete local touch on the current carrier without adding route hints or problem-specific solve staging",
                "asked_medium_surface": "final.md",
                "release_veto": True,
                "bootstrap_context": {"mode": "fresh_blind_project_skills_on"},
            }
        )

        touch = build_problem_born_touch_for_skill(
            state,
            "图像",
            target=gaokao_object,
            supporting=["状态拆分", "投影", "见证"],
        )

        self.assertIsInstance(touch, dict)
        self.assertFalse(program_has_meta_narration(touch))
        self.assertNotEqual(
            touch.get("controlled_object_if_any"),
            "separate the real controlling relation from decorative burden and keep the next runtime transition local, honest, and non-scripted",
        )

    def test_projected_gain_profile_promotes_generic_symmetry_comparison_lane(self) -> None:
        rank, reason = projected_gain_profile_for_skill(
            "对称",
            touch_target="equal-height comparison seam",
            current_object="two mirrored candidates on both sides of one threshold",
            current_debt="compare the mirrored sides before thick derivation regrows",
            direct_closure_allowed=False,
        )

        self.assertEqual(rank, 0)
        self.assertIn("mirrored", reason.lower())

    def test_read_skill_authority_program_recovers_combo_from_bridge_when_touch_is_thin(self) -> None:
        report = {
            "skill_authority_bridge": {
                "same_carrier_only": True,
                "winning_skill_if_any": "对称",
                "active_skill_combo_if_any": ["对称", "见证", "状态拆分"],
                "supporting_skills_if_any": ["见证", "状态拆分"],
                "executable_local_touch_if_any": {
                    "kind": "check",
                    "target": "equal-height comparison seam",
                    "operation": "compare the mirrored sides directly",
                },
            }
        }

        winning_skill, combo, touch, silence = read_skill_authority_program(
            report,
            require_same_carrier=True,
        )

        self.assertEqual(winning_skill, "对称")
        self.assertEqual(combo, ["对称", "见证", "状态拆分"])
        self.assertFalse(silence)
        self.assertEqual(touch.get("owner_skill_if_any"), "对称")
        self.assertEqual(touch.get("owner_skill_combo_if_any"), ["对称", "见证", "状态拆分"])

    def test_build_layer_composition_state_payload_inherits_owner_combo_from_live_layer(self) -> None:
        state = copy.deepcopy(DEFAULT_STATE)
        state.update(
            {
                "current_object": "mirrored comparison layer",
                "current_seam": "equal-height comparison seam",
                "current_debt": "turn the mirrored sides into one decisive inequality",
                "next_bite": "compare the mirrored sides directly",
                "asked_medium_surface": "answer.md",
                "release_veto": True,
            }
        )

        payload = build_layer_composition_state_payload(
            state,
            surface="bound_program",
            authorized_bite={
                "kind": "check",
                "target": "equal-height comparison seam",
                "operation": "compare the mirrored sides directly",
            },
            skill_winner="对称",
            skill_combo=["对称", "见证", "状态拆分"],
        )

        self.assertIsInstance(payload, dict)
        self.assertEqual(
            payload.get("authorized_bite", {}).get("owner_skill_if_any"),
            "对称",
        )
        self.assertEqual(
            payload.get("authorized_bite", {}).get("owner_skill_combo_if_any"),
            ["对称", "见证", "状态拆分"],
        )
        self.assertEqual(
            payload.get("active_skill_combo_if_any"),
            ["对称", "见证", "状态拆分"],
        )

    def test_chinese_skill_aliases_canonicalize_to_project_tokens(self) -> None:
        self.assertEqual(canonicalize_skill_token("图像"), "图像")
        self.assertEqual(canonicalize_skill_token("画图"), "图像")
        self.assertEqual(canonicalize_skill_token("对称"), "对称")
        self.assertEqual(canonicalize_skill_token("极限边界"), "极限边界")
        self.assertEqual(canonicalize_skill_token("奇点爆破"), "第一裂缝")
        self.assertEqual(canonicalize_skill_token("直接读出"), "读出")


if __name__ == "__main__":
    unittest.main()

