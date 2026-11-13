import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check


class CheckerTests(unittest.TestCase):
    def test_solution_crash_after_pass_is_rejected(self) -> None:
        results = [
            subprocess.CompletedProcess(
                [], 1, "FAIL test_set_1_example NotImplementedError\nSUMMARY 1 1\n", ""
            ),
            subprocess.CompletedProcess(
                [], 1, "PASS test_set_1_example\nSUMMARY 1 0\n", "Traceback: crash"
            ),
        ]
        with patch.object(check.subprocess, "run", side_effect=results):
            problems = check.test_problems(Path("."), 1)
        self.assertTrue(any("solution.py" in problem and "exit" in problem for problem in problems))

    def test_starter_crash_before_completion_is_rejected(self) -> None:
        result = subprocess.CompletedProcess(
            [], 1, "FAIL test_set_1_example NotImplementedError\n", "Traceback: crash"
        )
        with patch.object(check.subprocess, "run", return_value=result):
            outcome = check.outcomes(Path("."), ["question.py", "--all"], 1)
        self.assertIsInstance(outcome, str)

    def test_starter_abnormal_exit_is_rejected(self) -> None:
        result = subprocess.CompletedProcess(
            [], 2, "FAIL test_set_1_example NotImplementedError\nSUMMARY 1 1\n", ""
        )
        with patch.object(check.subprocess, "run", return_value=result):
            outcome = check.outcomes(Path("."), ["question.py", "--all"], 1)
        self.assertIsInstance(outcome, str)

    def test_timeout_is_reported(self) -> None:
        with patch.object(
            check.subprocess, "run", side_effect=subprocess.TimeoutExpired("question.py", 1)
        ):
            self.assertEqual(
                check.outcomes(Path("."), ["question.py"], 1),
                "question.py timed out after 1 seconds",
            )

    def test_malformed_and_incomplete_results_are_rejected(self) -> None:
        for output in (
            "",
            "FAIL test_set_1_example\nSUMMARY 1 1\n",
            "PASS test_set_1_example\nSUMMARY 2 0\n",
            "PASS test_set_1_example\nPASS test_set_1_example\nSUMMARY 2 0\n",
        ):
            with (
                self.subTest(output=output),
                patch.object(
                    check.subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess([], 0, output, ""),
                ),
            ):
                self.assertIsInstance(check.outcomes(Path("."), ["solution.py"], 1), str)

    def test_runner_accepts_starter_and_solution_and_detects_missing_sets(self) -> None:
        runner = (Path(__file__).resolve().parent.parent / "assets/runner.py.txt").read_text(
            encoding="utf-8"
        )
        tests = (
            """from __future__ import annotations

def test_set_1_example(candidate):
    assert candidate.answer() == 42

def test_set_2_example(candidate):
    assert candidate.answer() == 42

"""
            + runner
        )
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "tests.py").write_text(tests, encoding="utf-8")
            entry = """
import sys
import tests
candidate = sys.modules[__name__]
tests._run_set(candidate, 1)
{second}
raise SystemExit(tests.finish_tests(candidate))
"""
            (project / "question.py").write_text(
                "def answer():\n    raise NotImplementedError\n" + entry.format(second=""),
                encoding="utf-8",
            )
            (project / "solution.py").write_text(
                "def answer():\n    return 42\n"
                + entry.format(second="tests._run_set(candidate, 2)"),
                encoding="utf-8",
            )
            self.assertEqual(check.test_problems(project, 10), [])
            (project / "solution.py").write_text(
                "def answer():\n    return 42\n" + entry.format(second=""), encoding="utf-8"
            )
            self.assertEqual(
                check.test_problems(project, 10),
                ["solution.py does not run every test case; enable every set in it"],
            )


if __name__ == "__main__":
    unittest.main()
