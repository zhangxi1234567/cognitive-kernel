import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "prepare_blind_package.py"
CANONICAL_ICPC_APC_PROBLEM = "blind_cases/icpc_apc/2026_icpc_apc_m_deformed_balance.problem.txt"


class PrepareBlindPackageTests(unittest.TestCase):
    def _make_project_root(self, root: Path, *, include_teaching_notes: bool = False) -> None:
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "src" / "a.txt").write_text("alpha\n", encoding="utf-8")
        (root / "src" / "b.txt").write_text("beta\n", encoding="utf-8")
        (root / "BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt").write_text(
            "src/a.txt\nsrc/b.txt\n",
            encoding="utf-8",
        )
        if include_teaching_notes:
            for rel in (
                Path("references/joi-layerwise-skill-composition-note.md"),
                Path("references/gaokao-final-skill-composition-note.md"),
            ):
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(f"{rel.name}\n", encoding="utf-8")

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def _bootstrap_args(self) -> tuple[str, ...]:
        return (
            "--allow-explicit-bootstrap-override",
            "--bootstrap-current-object",
            "fresh blind package run in isolated directory",
            "--bootstrap-current-debt",
            "bind one honest local runtime layer before ordinary continuation regrows",
            "--bootstrap-next-bite",
            "draw one minimal problem diagram for the live controller and rewrite the governing relation there",
            "--asked-medium-surface",
            "final.md",
        )

    def test_prepare_blind_package_rejects_nonempty_package_without_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            package_dir = Path(tmpdir) / "pkg"
            run_dir = Path(tmpdir) / "run"
            package_dir.mkdir()
            (package_dir / "stale.txt").write_text("stale\n", encoding="utf-8")

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                *self._bootstrap_args(),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("package-dir must be missing or empty", result.stderr or result.stdout)

    def test_prepare_blind_package_rejects_nonempty_run_without_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            package_dir = Path(tmpdir) / "pkg"
            run_dir = Path(tmpdir) / "run"
            run_dir.mkdir()
            (run_dir / "runtime_state.json").write_text("{}", encoding="utf-8")

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                *self._bootstrap_args(),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("run-dir must be missing or empty", result.stderr or result.stdout)

    def test_prepare_blind_package_rejects_nested_package_and_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            package_dir = Path(tmpdir) / "pkg"
            run_dir = package_dir / "run"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                *self._bootstrap_args(),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("distinct and non-nested", result.stderr or result.stdout)

    def test_prepare_blind_package_clean_run_bootstraps_runtime_and_excludes_teaching_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root, include_teaching_notes=True)
            package_dir = Path(tmpdir) / "pkg"
            run_dir = Path(tmpdir) / "run"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                "--clean",
                *self._bootstrap_args(),
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertFalse(report["teaching_notes_included"])
            self.assertEqual(report["unexpected_count"], 0)
            self.assertEqual(report["forbidden_count"], 0)
            self.assertTrue(report["runtime_bootstrapped"])
            state_path = run_dir / "runtime_state.json"
            log_path = run_dir / "runtime_state.events.jsonl"
            self.assertEqual(report["runtime_state_path"], str(state_path.resolve()))
            self.assertEqual(report["runtime_event_log_path"], str(log_path.resolve()))
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state.get("bootstrap_context", {}).get("mode"), "fresh_blind_project_skills_on")
            events = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].get("command"), "bootstrap-blind")
            self.assertTrue((package_dir / "src" / "a.txt").exists())
            self.assertFalse(
                (package_dir / "references" / "joi-layerwise-skill-composition-note.md").exists()
            )

    def test_prepare_blind_package_fresh_blind_requires_run_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            package_dir = Path(tmpdir) / "pkg"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                *self._bootstrap_args(),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fresh blind solve requires --run-dir", result.stderr or result.stdout)

    def test_prepare_blind_package_copies_problem_statement_entry_from_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            problem_path = root / CANONICAL_ICPC_APC_PROBLEM
            problem_path.parent.mkdir(parents=True, exist_ok=True)
            problem_path.write_text("problem\n", encoding="utf-8")
            (root / "BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt").write_text(
                f"src/a.txt\n{CANONICAL_ICPC_APC_PROBLEM}\n",
                encoding="utf-8",
            )
            package_dir = Path(tmpdir) / "pkg"
            run_dir = Path(tmpdir) / "run"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                "--clean",
                *self._bootstrap_args(),
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue((package_dir / CANONICAL_ICPC_APC_PROBLEM).exists())

    def test_prepare_blind_package_bootstraps_from_manifest_problem_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            problem_path = root / CANONICAL_ICPC_APC_PROBLEM
            problem_path.parent.mkdir(parents=True, exist_ok=True)
            problem_path.write_text(
                "Deformed Balance\n\nTask\nGiven a parenthesis string, reason about balance via prefix and suffix structure.\n",
                encoding="utf-8",
            )
            (root / "BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt").write_text(
                f"src/a.txt\n{CANONICAL_ICPC_APC_PROBLEM}\n",
                encoding="utf-8",
            )
            package_dir = Path(tmpdir) / "pkg"
            run_dir = Path(tmpdir) / "run"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                "--clean",
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["bootstrap_seed_source"], CANONICAL_ICPC_APC_PROBLEM)
            state = json.loads((run_dir / "runtime_state.json").read_text(encoding="utf-8"))
            self.assertIn("Deformed Balance", state.get("current_object", ""))
            self.assertIn("prefix/suffix", state.get("current_seam", ""))
            self.assertIn("balance-state controller", state.get("current_debt", ""))
            self.assertIn("state-graph or split witness", state.get("next_bite", ""))

    def test_prepare_blind_package_rejects_off_manifest_bootstrap_problem(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            hidden_problem = root / "hidden" / "secret.problem.txt"
            hidden_problem.parent.mkdir(parents=True, exist_ok=True)
            hidden_problem.write_text("secret\n", encoding="utf-8")
            package_dir = Path(tmpdir) / "pkg"
            run_dir = Path(tmpdir) / "run"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                "--clean",
                "--bootstrap-problem-file",
                "hidden/secret.problem.txt",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("bootstrap-problem-file must match one manifest entry", result.stderr or result.stdout)

    def test_prepare_blind_package_rejects_final_md_in_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            (root / "final.md").write_text("stale final\n", encoding="utf-8")
            (root / "BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt").write_text(
                "src/a.txt\nfinal.md\n",
                encoding="utf-8",
            )
            package_dir = Path(tmpdir) / "pkg"
            run_dir = Path(tmpdir) / "run"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                "--clean",
                *self._bootstrap_args(),
            )

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertEqual(report["forbidden_count"], 1)
            self.assertIn("final.md", report["forbidden"])
            self.assertFalse(package_dir.exists())
            self.assertFalse(run_dir.exists())

    def test_prepare_blind_package_rejects_manifest_dotdot_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            root.mkdir(parents=True, exist_ok=True)
            secret = Path(tmpdir) / "secret.txt"
            secret.write_text("secret\n", encoding="utf-8")
            (root / "BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt").write_text(
                "../secret.txt\n",
                encoding="utf-8",
            )
            package_dir = Path(tmpdir) / "pkg"
            run_dir = Path(tmpdir) / "run"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manifest entry must not use dot-segments", result.stderr or result.stdout)

    def test_prepare_blind_package_clean_refuses_unowned_nonempty_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            package_dir = Path(tmpdir) / "pkg"
            package_dir.mkdir()
            (package_dir / "user.txt").write_text("keep\n", encoding="utf-8")
            run_dir = Path(tmpdir) / "run"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                "--clean",
                *self._bootstrap_args(),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be tool-owned, empty, or missing", result.stderr or result.stdout)

    def test_prepare_blind_package_rejects_forbidden_blind_surface_manifest_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root)
            agents_dir = root / "agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            (agents_dir / "openai.yaml").write_text("secret: no\n", encoding="utf-8")
            (root / "BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt").write_text(
                "src/a.txt\nagents/openai.yaml\n",
                encoding="utf-8",
            )
            package_dir = Path(tmpdir) / "pkg"
            run_dir = Path(tmpdir) / "run"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--run-dir",
                str(run_dir),
                "--clean",
            )

            self.assertNotEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertIn("agents/openai.yaml", report["forbidden"])
            self.assertFalse(package_dir.exists())
            self.assertFalse(run_dir.exists())

    def test_prepare_blind_package_manual_mode_labels_surface_as_manual(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            self._make_project_root(root, include_teaching_notes=True)
            package_dir = Path(tmpdir) / "pkg"

            result = self._run(
                "--project-root",
                str(root),
                "--package-dir",
                str(package_dir),
                "--include-teaching-notes",
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["mode"], "manual/non-blind package")
            self.assertEqual(report["project_skills"], "manual/non-blind")
            self.assertEqual(report["project_skills_surface"], "manual/non-blind")

    def test_canonical_manifest_includes_icpc_problem_statement_and_excludes_teaching_note(self) -> None:
        manifest = (REPO_ROOT / "BLIND_TEST_READSET_PROJECT_SKILLS_ON.txt").read_text(
            encoding="utf-8"
        ).splitlines()

        self.assertIn(CANONICAL_ICPC_APC_PROBLEM, manifest)
        self.assertNotIn("references/gaokao-final-skill-composition-note.md", manifest)
        self.assertTrue((REPO_ROOT / CANONICAL_ICPC_APC_PROBLEM).exists())


if __name__ == "__main__":
    unittest.main()
