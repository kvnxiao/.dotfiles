import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_spec


class SpecChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.spec = self.root / "SPEC.md"
        self.document = (
            "---\nstatus: draft\n---\n# Export\n\n## Requirements\n\n"
            "### REQ-export-file - Export file\n\n"
            "The command writes UTF-8 CSV to an absent destination and exits 0.\n\n"
            "**Scenarios:**\n\n"
            "- Given one record and an absent destination, export: write that record and exit 0.\n"
        )
        self.spec.write_text(self.document, encoding="utf-8")

    def check(self, document: str | None = None) -> check_spec.Report:
        if document is not None:
            self.spec.write_text(document, encoding="utf-8")
        report = check_spec.Report()
        docs = check_spec.load_spec_set(self.spec, report)
        check_spec.check_spec_set(docs, report)
        return report

    def test_spec_with_scenario_is_valid(self) -> None:
        self.assertEqual(self.check().errors, [])

    def test_inline_scenario_is_valid(self) -> None:
        document = self.document.replace("**Scenarios:**\n\n- ", "**Scenarios:** ")
        self.assertEqual(self.check(document).errors, [])

    def test_scenarios_can_have_subheadings(self) -> None:
        document = self.document.replace("**Scenarios:**\n\n", "**Scenarios:**\n\n#### Success\n\n")
        self.assertEqual(self.check(document).errors, [])

    def test_scenarios_can_have_bold_labels(self) -> None:
        prefix = self.document.split("**Scenarios:**", 1)[0] + "**Scenarios:**\n\n"
        for scenario in (
            "**Absent destination:** Given one record, export to an absent destination: "
            "write the record and exit 0.\n",
            "**Given:** One record and an absent destination.\n\n"
            "**When:** Run export.\n\n**Then:** Write the record and exit 0.\n",
        ):
            with self.subTest(scenario=scenario):
                self.assertEqual(self.check(prefix + scenario).errors, [])

    def test_empty_scenario_field_is_rejected(self) -> None:
        prefix = self.document.split("**Scenarios:**", 1)[0] + "**Scenarios:**\n\n"
        for suffix in (
            "",
            "-\n",
            "1.\n",
            "## Non-goals\n\nThe command does not contact remote services.\n",
            "**Failure behavior:** Report write failures.\n",
            "### REQ-export-empty - Empty export\n\nThe command writes a header.\n\n"
            "**Scenarios:** Empty input; export: write a header and exit 0.\n",
            "```markdown\n**Scenarios:**\n\n- Example text.\n```\n",
        ):
            with self.subTest(suffix=suffix):
                errors = self.check(prefix + suffix).errors
                self.assertTrue(any("REQ-export-file" in error for error in errors), errors)

    def test_scenario_label_mentioned_in_prose_is_not_a_field(self) -> None:
        document = self.document.split("**Scenarios:**", 1)[0]
        document += "The help text prints **Scenarios:** before its examples.\n"
        errors = self.check(document).errors
        self.assertTrue(any("REQ-export-file" in error for error in errors), errors)

    def test_scenario_field_in_code_example_is_ignored(self) -> None:
        document = self.document.split("**Scenarios:**", 1)[0]
        document += "```markdown\n**Scenarios:**\n\n- Export succeeds.\n```\n"
        errors = self.check(document).errors
        self.assertTrue(any("REQ-export-file" in error for error in errors), errors)

    def test_invalid_status_is_rejected(self) -> None:
        errors = self.check(self.document.replace("status: draft", "status: ready")).errors
        self.assertTrue(any("status" in error for error in errors), errors)

    def test_missing_area_is_rejected(self) -> None:
        document = self.document.replace("status: draft", "status: draft\nareas: [missing.md]")
        errors = self.check(document).errors
        self.assertTrue(any("missing.md" in error for error in errors), errors)

    def test_duplicate_ids_across_areas_are_rejected(self) -> None:
        area = self.root / "export.md"
        area.write_text(self.document.replace("status: draft", "spec: SPEC.md"), encoding="utf-8")
        document = self.document.replace("status: draft", "status: draft\nareas: [export.md]")
        errors = self.check(document).errors
        self.assertTrue(
            any("REQ-export-file is already defined" in error for error in errors), errors
        )

    def test_area_dependency_cycle_is_rejected(self) -> None:
        (self.root / "a.md").write_text(
            "---\nspec: SPEC.md\ndepends-on: [b.md]\n---\n# Area A\n", encoding="utf-8"
        )
        (self.root / "b.md").write_text(
            "---\nspec: SPEC.md\ndepends-on: [a.md]\n---\n# Area B\n", encoding="utf-8"
        )
        document = self.document.replace("status: draft", "status: draft\nareas: [a.md, b.md]")
        errors = self.check(document).errors
        self.assertTrue(any("cycle" in error for error in errors), errors)

    def test_undefined_requirement_reference_is_rejected(self) -> None:
        errors = self.check(self.document + "\nSee REQ-export-missing.\n").errors
        self.assertTrue(
            any("REQ-export-missing is not defined" in error for error in errors), errors
        )

    def test_approved_spec_with_open_questions_is_rejected(self) -> None:
        document = self.document.replace("status: draft", "status: approved")
        document += "\n## Open questions\n\nWhich output format is required?\n"
        errors = self.check(document).errors
        self.assertTrue(any("open questions" in error for error in errors), errors)

    def test_draft_spec_with_open_questions_is_valid(self) -> None:
        document = self.document + "\n## Open questions\n\nWhich output format is required?\n"
        self.assertEqual(self.check(document).errors, [])

    def test_research_without_metadata_or_index_is_rejected(self) -> None:
        research = self.root / "research"
        research.mkdir()
        (research / "export.md").write_text("# Export\n\nA local observation.\n", encoding="utf-8")
        report = check_spec.Report()
        check_spec.check_research(research, report)
        self.assertTrue(any("README.md" in error for error in report.errors), report.errors)
        self.assertTrue(any("date" in error for error in report.errors), report.errors)
        self.assertTrue(any("questions" in error for error in report.errors), report.errors)


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

    def status_with_task_states(self, t1: str, t2: str) -> str:
        self.add_plan()
        child = self.plans / "export.md"
        child.write_text(
            child.read_text(encoding="utf-8")
            + "\n### T2 - Verify export\n\n**Requirements:** REQ-export-file\n",
            encoding="utf-8",
        )
        (self.plans / ".state" / "export.yaml").write_text(
            f"tasks:\n  T1: {t1}\n  T2: {t2}\nreview: pending\n", encoding="utf-8"
        )
        root, plans, report = self.load()
        self.assertEqual(report.errors, [])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            check_spec.print_status(root, plans)
        return output.getvalue()

    def test_resume_selects_first_unfinished_task(self) -> None:
        self.assertRegex(
            self.status_with_task_states("todo", "in-progress"), r"next: .*export\.md T1"
        )

    def test_tasks_before_a_blocked_task_stay_runnable(self) -> None:
        self.assertRegex(self.status_with_task_states("todo", "blocked"), r"next: .*export\.md T1")

    def test_blocked_first_unfinished_task_stops_the_plan(self) -> None:
        self.assertIn("next: none", self.status_with_task_states("blocked", "todo"))

    def test_done_tasks_before_a_blocked_task_do_not_make_the_plan_runnable(self) -> None:
        self.assertIn("next: none", self.status_with_task_states("done", "blocked"))

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
