# /// script
# dependencies = ["ruff==0.16.10", "ty==0.0.84"]
# ///
"""Check a generated interview practice package and print each problem."""

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

MODULES = ("question.py", "solution.py", "tests.py")
RUFF_RULES = "E4,E7,E9,F,I,UP,B,BLE"
RESULT = re.compile(r"^(PASS|FAIL) (test_set_\w+)(?: ([\w.]+))?")


def tool_problems(project: Path) -> list[str]:
    files = [str(project / name) for name in MODULES]
    search_paths = [
        arg
        for path in (str(project), *(p for p in sys.path if p.endswith("site-packages")))
        for arg in ("--extra-search-path", path)
    ]
    ruff = ["--isolated", "--target-version", "py313"]
    commands = {
        "ruff check": ["ruff", "check", *ruff, "--select", RUFF_RULES, *files],
        "ruff format": ["ruff", "format", *ruff, "--check", *files],
        "ty": [
            "ty",
            "check",
            "--python-version",
            "3.13",
            *search_paths,
            "--error-on-warning",
            *files,
        ],
    }
    problems = []
    for label, command in commands.items():
        result = subprocess.run(
            [sys.executable, "-m", *command],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            problems.append(f"{label} failed:\n{(result.stdout + result.stderr).strip()}")
    return problems


def outcomes(project: Path, command: list[str], timeout: float) -> dict[str, str | None] | str:
    module = command[0]
    try:
        result = subprocess.run(
            [sys.executable, *command],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return f"{module} timed out after {timeout} seconds"
    found: dict[str, str | None] = {}
    lines = result.stdout.splitlines()
    for line in lines:
        if match := RESULT.match(line):
            if match[2] in found or (match[1] == "FAIL" and match[3] is None):
                return f"{module} reported a duplicate or malformed result: {line}"
            found[match[2]] = None if match[1] == "PASS" else match[3]
    if not found:
        return f"{module} reported no test results:\n{result.stdout}{result.stderr}".strip()
    failures = sum(error is not None for error in found.values())
    if lines[-1] != f"SUMMARY {len(found)} {failures}":
        return f"{module} did not report a complete test summary:\n{result.stderr}".strip()
    expected_exit = int(failures > 0)
    if result.returncode != expected_exit:
        return f"{module} exited with {result.returncode}, expected {expected_exit}:\n{result.stderr}".strip()
    return found


def test_problems(project: Path, timeout: float) -> list[str]:
    starter = outcomes(project, ["question.py", "--all"], timeout)
    solution = outcomes(project, ["solution.py"], timeout)
    if isinstance(starter, str) or isinstance(solution, str):
        return [result for result in (starter, solution) if isinstance(result, str)]
    problems = []
    if set(starter) != set(solution):
        problems.append("solution.py does not run every test case; enable every set in it")
    problems += [f"solution fails {name}: {error}" for name, error in solution.items() if error]
    problems += [
        f"starter {name} should fail with NotImplementedError, got {error or 'a pass'}"
        for name, error in starter.items()
        if error != "NotImplementedError"
    ]
    return problems


def outline(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            node.body = []
    return [
        ast.dump(node)
        for node in tree.body
        if not isinstance(node, ast.Import | ast.ImportFrom)
        and not (isinstance(node, ast.If) and "__name__" in ast.unparse(node.test))
    ]


def starter_kept(starter: list[str], solution: list[str]) -> bool:
    remaining = iter(solution)
    return all(node in remaining for node in starter)


def readme_problems(project: Path) -> list[str]:
    prompt = project.parent / f"{project.name}.md"
    if not prompt.is_file():
        return [f"prompt file not found: {prompt}"]
    if not (project / "README.md").read_bytes().startswith(prompt.read_bytes()):
        return [f"README.md does not start with the exact bytes of {prompt.name}"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    project: Path = args.project.resolve()
    missing = [name for name in (*MODULES, "README.md") if not (project / name).is_file()]
    if missing:
        print(f"missing files: {', '.join(missing)}")
        return 1
    problems = [*tool_problems(project), *readme_problems(project)]
    try:
        if not starter_kept(outline(project / "question.py"), outline(project / "solution.py")):
            problems.append("solution.py changes, drops, or reorders a definition from question.py")
    except SyntaxError as error:
        problems.append(f"{error.filename or 'a module'} has a syntax error: {error}")
    problems += test_problems(project, args.timeout)
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print("OK: every solution case passes and every starter case raises NotImplementedError")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
