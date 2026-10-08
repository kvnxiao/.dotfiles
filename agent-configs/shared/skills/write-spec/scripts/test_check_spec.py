import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_spec


class PlanChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.spec = self.root / "SPEC.md"
        self.spec.write_text(
            "---\nstatus: approved\n---\n# Export\n\n## Requirements\n\n"
            "### REQ-export-file - Export file\n\nThe command exports UTF-8 CSV.\n\n"
            "**Scenarios:**\n\n- Run export; the file is UTF-8 CSV.\n",
            encoding="utf-8",
        )
        self.plans = self.root / ".plans" / "export"
        (self.plans / ".state").mkdir(parents=True)
        self.plan_root = self.plans / "README.md"
        self.plan_root.write_text(
            "---\nspec: ../../SPEC.md\nstatus: draft\n---\n# Export\n\n## Plans\n\n"
            "| Plan | Outcome | Blocked by | Parallel-safe |\n"
            "| --- | --- | --- | --- |\n"
            "| [Export](export.md) | Export | | No |\n",
            encoding="utf-8",
        )

    def add_plan(self, name: str = "export", blocked_by: str = "") -> None:
        (self.plans / f"{name}.md").write_text(
            "---\nspec: ../../SPEC.md\nparent: README.md\n"
            "requirements: [REQ-export-file]\n"
            + (f"blocked-by: [{blocked_by}.md]\n" if blocked_by else "")
            + "---\n# Export\n\n## Tasks\n\n### T1 - Export a file\n\n"
            "**Requirements:** REQ-export-file\n\n1. Validate: export passes.\n",
            encoding="utf-8",
        )
        (self.plans / ".state" / f"{name}.yaml").write_text(
            "tasks:\n  T1: done\nreview: pending\n", encoding="utf-8"
        )

    def load(self) -> tuple[check_spec.Doc, list[check_spec.Plan], check_spec.Report]:
        report = check_spec.Report()
        docs = check_spec.load_spec_set(self.spec, report)
        requirements = check_spec.check_spec_set(docs, report)
        root, plans = check_spec.load_plans(
            self.plans, docs, {requirement.slug for requirement in requirements}, report
        )
        assert root is not None
        check_spec.check_plan_set(root, plans, ["REQ-export-file"], report)
        return root, plans, report

    def test_missing_child_plan_is_an_error(self) -> None:
        _, _, report = self.load()
        self.assertTrue(any("export.md" in error for error in report.errors), report.errors)
        self.assertTrue(any("REQ-export-file" in warning for warning in report.warnings))

    def test_plan_outcome_can_link_to_the_spec(self) -> None:
        self.add_plan()
        self.plan_root.write_text(
            self.plan_root.read_text(encoding="utf-8").replace(
                "| Export |", "| Implements [REQ-export-file](../../SPEC.md#req-export-file) |"
            ),
            encoding="utf-8",
        )
        _, _, report = self.load()
        self.assertEqual(report.errors, [])

    def test_resume_selects_first_unfinished_task(self) -> None:
        self.add_plan()
        child = self.plans / "export.md"
        child.write_text(
            child.read_text(encoding="utf-8")
            + "\n### T2 - Verify export\n\n**Requirements:** REQ-export-file\n",
            encoding="utf-8",
        )
        (self.plans / ".state" / "export.yaml").write_text(
            "tasks:\n  T1: todo\n  T2: in-progress\nreview: pending\n", encoding="utf-8"
        )
        root, plans, report = self.load()
        self.assertEqual(report.errors, [])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            check_spec.print_status(root, plans)
        self.assertRegex(output.getvalue(), r"next: .*export\.md T1")

    def test_empty_plan_set_reports_uncovered_requirements(self) -> None:
        self.plan_root.write_text(
            "---\nspec: ../../SPEC.md\nstatus: draft\n---\n# Export\n", encoding="utf-8"
        )
        _, _, report = self.load()
        self.assertTrue(any("REQ-export-file" in warning for warning in report.warnings))

    def test_explicitly_out_of_scope_empty_set_has_no_coverage_warning(self) -> None:
        self.plan_root.write_text(
            "---\nspec: ../../SPEC.md\nstatus: draft\n"
            "out-of-scope: [REQ-export-file]\n---\n# Export\n",
            encoding="utf-8",
        )
        _, _, report = self.load()
        self.assertFalse(any("not covered" in warning for warning in report.warnings))

    def test_completed_tasks_still_schedule_review(self) -> None:
        self.add_plan()
        root, plans, report = self.load()
        self.assertEqual(report.errors, [])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            check_spec.print_status(root, plans)
        self.assertRegex(output.getvalue(), r"next: .*export\.md review")
        self.assertFalse(check_spec.is_complete(plans[0]))

    def test_review_blocks_dependent_plan(self) -> None:
        self.add_plan()
        self.add_plan("consumer", "export")
        (self.plans / ".state" / "consumer.yaml").write_text(
            "tasks:\n  T1: todo\nreview: pending\n", encoding="utf-8"
        )
        root, plans, report = self.load()
        self.assertEqual(report.errors, [])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            check_spec.print_status(root, plans)
        self.assertIn("blocked by:", output.getvalue())
        self.assertRegex(output.getvalue(), r"next: .*export\.md review")

    def test_review_done_releases_dependent_plan(self) -> None:
        self.add_plan()
        self.add_plan("consumer", "export")
        (self.plans / ".state" / "export.yaml").write_text(
            "tasks:\n  T1: done\nreview: done\n", encoding="utf-8"
        )
        (self.plans / ".state" / "consumer.yaml").write_text(
            "tasks:\n  T1: todo\nreview: pending\n", encoding="utf-8"
        )
        root, plans, report = self.load()
        self.assertEqual(report.errors, [])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            check_spec.print_status(root, plans)
        self.assertRegex(output.getvalue(), r"next: .*consumer\.md T1")

    def test_review_cannot_be_done_with_unfinished_tasks(self) -> None:
        self.add_plan()
        (self.plans / ".state" / "export.yaml").write_text(
            "tasks:\n  T1: todo\nreview: done\n", encoding="utf-8"
        )
        _, _, report = self.load()
        self.assertTrue(any("review" in error for error in report.errors), report.errors)

    def test_legacy_state_requires_review(self) -> None:
        self.add_plan()
        (self.plans / ".state" / "export.yaml").write_text("tasks:\n  T1: done\n", encoding="utf-8")
        _, plans, _ = self.load()
        self.assertFalse(check_spec.is_complete(plans[0]))

    def approve(self) -> None:
        self.plan_root.write_text(
            self.plan_root.read_text(encoding="utf-8").replace(
                "status: draft",
                "status: ready\nspec-baseline: sha256:808f63a0e08f1aa51de5d076c2933eee3c16ae17497a3829abad1f0e2ebce895",
            ),
            encoding="utf-8",
        )

    def test_matching_baseline_accepts_ready_plan(self) -> None:
        self.add_plan()
        self.approve()
        _, _, report = self.load()
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_same_slug_spec_amendment_invalidates_ready_plan(self) -> None:
        self.add_plan()
        self.approve()
        self.spec.write_text(
            self.spec.read_text(encoding="utf-8").replace("UTF-8", "UTF-16"), encoding="utf-8"
        )
        _, _, report = self.load()
        self.assertTrue(any("spec-baseline" in error for error in report.errors), report.errors)

    def test_ready_plan_without_baseline_is_rejected(self) -> None:
        self.add_plan()
        self.plan_root.write_text(
            self.plan_root.read_text(encoding="utf-8").replace("status: draft", "status: ready"),
            encoding="utf-8",
        )
        _, _, report = self.load()
        self.assertTrue(any("spec-baseline" in error for error in report.errors), report.errors)

    def test_line_endings_do_not_invalidate_baseline(self) -> None:
        self.add_plan()
        self.approve()
        self.spec.write_bytes(
            self.spec.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        )
        _, _, report = self.load()
        self.assertEqual(report.errors, [])

    def test_fingerprint_covers_area_contents(self) -> None:
        area = self.root / "area.md"
        area.write_text("---\nspec: SPEC.md\n---\n# Area\n\nOriginal content.\n", encoding="utf-8")
        self.spec.write_text(
            self.spec.read_text(encoding="utf-8").replace(
                "status: approved", "status: approved\nareas: [area.md]"
            ),
            encoding="utf-8",
        )
        self.add_plan()
        docs = check_spec.load_spec_set(self.spec, check_spec.Report())
        baseline = check_spec.spec_fingerprint(docs)
        self.plan_root.write_text(
            self.plan_root.read_text(encoding="utf-8").replace(
                "status: draft", f"status: ready\nspec-baseline: {baseline}"
            ),
            encoding="utf-8",
        )
        area.write_text("---\nspec: SPEC.md\n---\n# Area\n\nChanged content.\n", encoding="utf-8")
        _, _, report = self.load()
        self.assertTrue(any("spec-baseline" in error for error in report.errors), report.errors)

    def test_fingerprint_cli_prints_expected_field(self) -> None:
        output = io.StringIO()
        with (
            patch("sys.argv", ["check_spec.py", str(self.spec), "--fingerprint"]),
            contextlib.redirect_stdout(output),
        ):
            code = check_spec.main()
        self.assertEqual(code, 0)
        self.assertIn(
            "spec-baseline: sha256:808f63a0e08f1aa51de5d076c2933eee3c16ae17497a3829abad1f0e2ebce895",
            output.getvalue(),
        )

    def test_invalid_baseline_does_not_print_next_task(self) -> None:
        self.add_plan()
        self.approve()
        self.spec.write_text(
            self.spec.read_text(encoding="utf-8").replace("UTF-8", "UTF-16"), encoding="utf-8"
        )
        output = io.StringIO()
        with (
            patch(
                "sys.argv",
                ["check_spec.py", str(self.spec), "--plans", str(self.plans), "--status"],
            ),
            contextlib.redirect_stdout(output),
        ):
            code = check_spec.main()
        self.assertEqual(code, 1)
        self.assertNotIn("next:", output.getvalue())

    def test_invalid_review_value_is_rejected(self) -> None:
        self.add_plan()
        (self.plans / ".state" / "export.yaml").write_text(
            "tasks:\n  T1: done\nreview: skipped\n", encoding="utf-8"
        )
        _, _, report = self.load()
        self.assertTrue(any("review must be" in error for error in report.errors), report.errors)


if __name__ == "__main__":
    unittest.main()
