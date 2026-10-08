# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Check the structure of a spec set and, optionally, the plans derived from it.

Exits 0 without errors, 1 with errors, and 2 when it cannot run.
"""

import argparse
import hashlib
import io
import json
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

BUDGET_BYTES = 40 * 1024
SPEC_STATUSES = ("draft", "approved")
PLAN_STATUSES = ("draft", "ready")
TASK_STATUSES = ("todo", "in-progress", "blocked", "done")
REVIEW_STATUSES = ("pending", "done")
LIST_KEYS = ("areas", "depends-on", "requirements", "blocked-by", "out-of-scope", "questions")

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
REQ_HEADING = re.compile(
    r"^(#{3,4})\s+(REQ-[^\s\u2013\u2014:]+)\s*(?:[\u2013\u2014:-]+\s*)?(.*?)(?:\s+#+)?\s*$"
)
SLUG = re.compile(r"^REQ-[a-z0-9]+(?:-[a-z0-9]+)*$")
REQ_REF = re.compile(r"(?<![\w/#-])REQ-[a-z0-9]+(?:-[a-z0-9]+)*")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
LINK = re.compile(r"\[([^\]]*)\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")
SCENARIOS = re.compile(r"\*\*Scenarios?:\*\*", re.IGNORECASE)
OPEN_QUESTIONS = re.compile(r"^##\s+Open questions\s*$", re.IGNORECASE)
TASK_HEADING = re.compile(r"^###\s+(T\d+)\b")
TASK_REQUIREMENTS = re.compile(r"^\*\*Requirements:\*\*", re.IGNORECASE)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

type Value = str | list[str] | dict[str, str]


class FrontmatterError(ValueError):
    pass


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, path: Path, line: int, message: str) -> None:
        self.errors.append(f"error: {display(path)}:{line}: {message}")

    def warn(self, path: Path, line: int, message: str) -> None:
        self.warnings.append(f"warning: {display(path)}:{line}: {message}")


@dataclass
class Doc:
    path: Path
    lines: list[str]
    meta: dict[str, Value]
    body_start: int
    size: int


@dataclass
class Requirement:
    slug: str
    title: str
    path: Path
    line: int
    has_scenarios: bool
    invariant: bool


@dataclass
class Plan:
    doc: Doc
    tasks: list[str]
    blocked_by: list[Path]
    requirements: list[str]
    state: dict[str, str]
    review: str


def display(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def strip_scalar(raw: str) -> str:
    value = raw.strip()
    if value[:1] in {'"', "'"}:
        quote = value[0]
        end = value.find(quote, 1)
        return value[1:end] if end > 0 else value[1:]
    comment = value.find(" #")
    return (value[:comment] if comment >= 0 else value).strip()


def parse_inline_list(raw: str) -> list[str]:
    inner = raw.strip()[1 : raw.strip().rfind("]")]
    return [strip_scalar(item) for item in inner.split(",") if item.strip()]


def is_item(text: str) -> bool:
    return text.startswith("- ") or text.rstrip() == "-"


def parse_yaml_subset(lines: list[str]) -> dict[str, Value]:
    """Parse the YAML subset that specs, plans, and state files use.

    - Supports scalars, inline or block lists, one-level mappings, block scalars, and comments.
    - Raises FrontmatterError for a top-level line that is not `key: value`.
    """
    result: dict[str, Value] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0].isspace() or ":" not in line:
            raise FrontmatterError(f"unsupported line: {line.strip()}")
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest.startswith("#"):
            rest = ""
        nested: list[str] = []
        while index < len(lines) and (
            not lines[index].strip()
            or lines[index][0].isspace()
            or (not rest and is_item(lines[index]))
        ):
            item = lines[index].strip()
            if item and not item.startswith("#"):
                nested.append(item)
            index += 1
        if rest.startswith("["):
            result[key] = parse_inline_list(rest)
        elif rest in {"|", "|-", ">", ">-"}:
            result[key] = " ".join(nested)
        elif rest:
            result[key] = strip_scalar(rest)
        elif nested and is_item(nested[0]):
            items: list[str] = []
            for item in nested:
                if is_item(item):
                    items.append(item[1:].strip())
                else:
                    items[-1] = f"{items[-1]} {item}"
            result[key] = [strip_scalar(item) for item in items]
        elif nested:
            mapping: dict[str, str] = {}
            for item in nested:
                sub_key, _, sub_value = item.partition(":")
                mapping[sub_key.strip()] = strip_scalar(sub_value)
            result[key] = mapping
        else:
            result[key] = ""
    return result


def load_doc(path: Path) -> Doc:
    """Read a Markdown file and parse its frontmatter.

    - Raises OSError when the file cannot be read, UnicodeDecodeError when it is not UTF-8, and FrontmatterError when its frontmatter is unterminated or unsupported.
    - Measures size with LF line endings, so a CRLF checkout gets the same budget verdict.
    """
    text = path.read_bytes().decode("utf-8-sig")
    lines = text.splitlines()
    size = len(text.replace("\r\n", "\n").encode("utf-8"))
    if not lines or lines[0].strip() != "---":
        return Doc(path, lines, {}, 0, size)
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            return Doc(path, lines, parse_yaml_subset(lines[1:end]), end + 1, size)
    raise FrontmatterError("frontmatter has no closing ---")


def content_lines(doc: Doc) -> Iterator[tuple[int, str]]:
    fence = ""
    for index in range(doc.body_start, len(doc.lines)):
        line = doc.lines[index]
        match = FENCE.match(line)
        if match:
            run, info = match.group(1), match.group(2).strip()
            if not fence:
                fence = run
                continue
            if run[0] == fence[0] and len(run) >= len(fence) and not info:
                fence = ""
                continue
        if not fence:
            yield index + 1, line


def as_list(value: Value | None) -> list[str]:
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value:
        return [value]
    return []


def resolve(base: Path, target: str) -> Path:
    return (base.parent / target).resolve()


def load_or_report(path: Path, report: Report) -> Doc | None:
    try:
        doc = load_doc(path)
    except OSError as error:
        report.error(path, 1, f"cannot read: {error.strerror}")
        return None
    except UnicodeDecodeError:
        report.error(path, 1, "not valid UTF-8")
        return None
    except FrontmatterError as error:
        report.error(path, 1, f"invalid frontmatter: {error}")
        return None
    for key in LIST_KEYS:
        if isinstance(doc.meta.get(key), dict):
            report.error(path, 1, f"frontmatter {key} must be a list")
    return doc


def extract_requirements(doc: Doc, report: Report) -> list[Requirement]:
    found: list[Requirement] = []
    current: Requirement | None = None
    current_level = 0
    section = ""
    for number, line in content_lines(doc):
        heading = HEADING.match(line)
        if heading and len(heading.group(1)) <= 2:
            section = heading.group(2).lower()
        if heading and current and len(heading.group(1)) <= current_level:
            current = None
        match = REQ_HEADING.match(line)
        if match:
            slug = match.group(2)
            if not SLUG.match(slug):
                report.error(doc.path, number, f"{slug} is not a lowercase kebab-case slug")
                continue
            if any(segment.isdigit() for segment in slug.split("-")[1:]):
                report.error(
                    doc.path, number, f"{slug} has a numeric segment; name the behavior instead"
                )
            current = Requirement(
                slug, match.group(3), doc.path, number, False, "invariant" in section
            )
            current_level = len(match.group(1))
            found.append(current)
        elif current and SCENARIOS.search(line):
            current.has_scenarios = True
    return found


def external_spans(line: str, doc: Doc, internal: set[Path]) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for link in LINK.finditer(line):
        target = link.group(2)
        if target.startswith("#"):
            continue
        local = target.split("#", 1)[0]
        if "://" not in target and local and resolve(doc.path, local) in internal:
            continue
        spans.append(link.span())
    return spans


def undefined_refs(line: str, doc: Doc, internal: set[Path], defined: set[str]) -> Iterator[str]:
    spans = external_spans(line, doc, internal)
    for ref in REQ_REF.finditer(line):
        if ref.group(0) in defined or any(start <= ref.start() < end for start, end in spans):
            continue
        yield ref.group(0)


def find_cycle(graph: dict[Path, list[Path]]) -> list[Path] | None:
    visiting: list[Path] = []
    done: set[Path] = set()

    def visit(node: Path) -> list[Path] | None:
        if node in visiting:
            return [*visiting[visiting.index(node) :], node]
        if node in done:
            return None
        visiting.append(node)
        for neighbor in graph.get(node, []):
            cycle = visit(neighbor)
            if cycle:
                return cycle
        visiting.pop()
        done.add(node)
        return None

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def load_spec_set(root_path: Path, report: Report) -> list[Doc]:
    root = load_or_report(root_path, report)
    if root is None:
        return []
    status = root.meta.get("status")
    if status not in SPEC_STATUSES:
        report.error(root.path, 1, f"frontmatter status must be one of {', '.join(SPEC_STATUSES)}")
    docs = [root]
    areas: dict[Path, Doc] = {}
    seen = {root.path.resolve()}
    for entry in as_list(root.meta.get("areas")):
        area_path = resolve(root.path, entry)
        if area_path in seen:
            report.error(root.path, 1, f"area {entry} is the root or is listed twice")
            continue
        seen.add(area_path)
        if not area_path.is_file():
            report.error(root.path, 1, f"area {entry} does not exist")
            continue
        area = load_or_report(area_path, report)
        if area is None:
            continue
        areas[area_path] = area
        docs.append(area)
        spec_ref = area.meta.get("spec")
        if not isinstance(spec_ref, str) or resolve(area.path, spec_ref) != root.path.resolve():
            report.error(area.path, 1, "frontmatter spec must point to the root SPEC.md")
    graph: dict[Path, list[Path]] = {}
    for area_path, area in areas.items():
        graph[area_path] = []
        for entry in as_list(area.meta.get("depends-on")):
            target = resolve(area.path, entry)
            if target not in areas:
                report.error(area.path, 1, f"depends-on {entry} is not an area of this spec")
            else:
                graph[area_path].append(target)
    cycle = find_cycle(graph)
    if cycle:
        names = " -> ".join(display(path) for path in cycle)
        report.error(cycle[0], 1, f"depends-on forms a cycle: {names}")
    return docs


def check_spec_set(docs: list[Doc], report: Report) -> list[Requirement]:
    requirements: list[Requirement] = []
    for doc in docs:
        requirements.extend(extract_requirements(doc, report))
        if doc.size > BUDGET_BYTES:
            report.error(
                doc.path,
                1,
                f"{doc.size / 1024:.1f} KB exceeds the {BUDGET_BYTES // 1024} KB budget; split along areas of responsibility",
            )
    if docs and not requirements:
        report.error(docs[0].path, 1, "the spec has no requirement blocks such as ### REQ-<slug>")
    seen: dict[str, Requirement] = {}
    for requirement in requirements:
        if requirement.slug in seen:
            first = seen[requirement.slug]
            report.error(
                requirement.path,
                requirement.line,
                f"{requirement.slug} is already defined at {display(first.path)}:{first.line}",
            )
        else:
            seen[requirement.slug] = requirement
        if not requirement.has_scenarios:
            report.error(
                requirement.path,
                requirement.line,
                f"{requirement.slug} has no **Scenarios:** field",
            )
    internal = {doc.path.resolve() for doc in docs}
    defined = set(seen)
    for doc in docs:
        for number, line in content_lines(doc):
            for ref in undefined_refs(line, doc, internal, defined):
                report.error(doc.path, number, f"{ref} is not defined in this spec")
    if docs and docs[0].meta.get("status") == "approved":
        for doc in docs:
            check_open_questions(doc, report)
    return requirements


def check_open_questions(doc: Doc, report: Report) -> None:
    section_line = 0
    for number, line in content_lines(doc):
        if OPEN_QUESTIONS.match(line):
            section_line = number
        elif section_line and line.startswith("## "):
            section_line = 0
        elif section_line and line.strip():
            report.error(doc.path, section_line, "an approved spec has unresolved open questions")
            return


def check_research(directory: Path, report: Report) -> None:
    documents = sorted(path for path in directory.glob("*.md") if path.name != "README.md")
    index_path = directory / "README.md"
    if not documents:
        return
    index = None
    if index_path.is_file():
        index = load_or_report(index_path, report)
    else:
        report.error(index_path, 1, "research directory has no README.md index")
    linked: set[Path] = set()
    if index is not None:
        for number, line in content_lines(index):
            for link in LINK.finditer(line):
                local = link.group(2).split("#", 1)[0]
                if local.endswith(".md") and "://" not in local:
                    target = resolve(index.path, local)
                    linked.add(target)
                    if not target.is_file():
                        report.error(index.path, number, f"index links missing document {local}")
    for path in documents:
        doc = load_or_report(path, report)
        if doc is None:
            continue
        date = doc.meta.get("date")
        if not isinstance(date, str) or not DATE.match(date):
            report.error(path, 1, "frontmatter date must be YYYY-MM-DD")
        if not as_list(doc.meta.get("questions")):
            report.error(path, 1, "frontmatter questions is empty")
        if index is not None and path.resolve() not in linked:
            report.error(index.path, 1, f"index does not list {path.name}")


def spec_fingerprint(docs: list[Doc]) -> str:
    text = json.dumps([doc.lines for doc in docs], ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_state(path: Path, report: Report) -> tuple[dict[str, str], str]:
    if not path.is_file():
        return {}, "pending"
    try:
        parsed = parse_yaml_subset(path.read_text(encoding="utf-8-sig").splitlines())
    except UnicodeDecodeError:
        report.error(path, 1, "not valid UTF-8")
        return {}, "pending"
    except (OSError, FrontmatterError) as error:
        report.error(path, 1, f"invalid state file: {error}")
        return {}, "pending"
    tasks = parsed.get("tasks", {})
    if not isinstance(tasks, dict):
        report.error(path, 1, "tasks must be a mapping of task ID to status")
        return {}, "pending"
    review = parsed.get("review", "pending")
    if not isinstance(review, str) or review not in REVIEW_STATUSES:
        report.error(path, 1, f"review must be one of {', '.join(REVIEW_STATUSES)}")
        review = "pending"
    return tasks, review


def load_plans(
    plans_dir: Path, spec_docs: list[Doc], slugs: set[str], report: Report
) -> tuple[Doc | None, list[Plan]]:
    root_path = plans_dir / "README.md"
    if not root_path.is_file():
        report.error(root_path, 1, "plan set has no root README.md")
        return None, []
    root = load_or_report(root_path, report)
    if root is None:
        return None, []
    spec_root = spec_docs[0].path
    spec_ref = root.meta.get("spec")
    if not isinstance(spec_ref, str) or resolve(root.path, spec_ref) != spec_root.resolve():
        report.error(root.path, 1, f"frontmatter spec must point to {display(spec_root)}")
    if root.meta.get("status") not in PLAN_STATUSES:
        report.error(root.path, 1, f"frontmatter status must be one of {', '.join(PLAN_STATUSES)}")
    if root.meta.get("spec-baseline") != spec_fingerprint(spec_docs):
        message = "spec-baseline is missing or differs from the spec; reconcile the plan set with plan-from-spec before recording a new baseline"
        if root.meta.get("status") == "ready":
            report.error(root.path, 1, message)
        else:
            report.warn(root.path, 1, message)
    for slug in as_list(root.meta.get("out-of-scope")):
        if slug not in slugs:
            report.error(root.path, 1, f"out-of-scope lists {slug}, which the spec does not define")
    paths = sorted(
        path
        for path in plans_dir.rglob("*.md")
        if path != root_path and ".state" not in path.relative_to(plans_dir).parts
    )
    children = {path.resolve() for path in paths}
    plan_paths = children | {root_path.resolve()}
    internal = plan_paths | {doc.path.resolve() for doc in spec_docs}
    order: dict[Path, int] = {}
    in_plans_section = False
    for number, line in content_lines(root):
        heading = HEADING.match(line)
        if heading and len(heading.group(1)) <= 2:
            in_plans_section = heading.group(2).lower() == "plans"
        elif in_plans_section and line.lstrip().startswith("|"):
            plan_cell = line.strip().strip("|").split("|", 1)[0]
            for link in LINK.finditer(plan_cell):
                local = link.group(2).split("#", 1)[0]
                if not local.endswith(".md") or "://" in local:
                    continue
                target = resolve(root.path, local)
                if target not in children:
                    report.error(
                        root.path,
                        number,
                        f"Plans links {local}, which is not a child plan in this set",
                    )
                else:
                    order.setdefault(target, len(order))
        for ref in undefined_refs(line, root, internal, slugs):
            report.error(root.path, number, f"{ref} is not defined in the spec")
    for path in paths:
        if path.resolve() not in order:
            report.warn(root.path, 1, f"the ## Plans section does not link {display(path)}")
    paths.sort(key=lambda path: order.get(path.resolve(), len(order)))
    plans: list[Plan] = []
    for path in paths:
        doc = load_or_report(path, report)
        if doc is None:
            continue
        meta = doc.meta
        spec_ref = meta.get("spec")
        if not isinstance(spec_ref, str) or resolve(doc.path, spec_ref) != spec_root.resolve():
            report.error(doc.path, 1, f"frontmatter spec must point to {display(spec_root)}")
        parent = meta.get("parent")
        if not isinstance(parent, str) or resolve(doc.path, parent) not in plan_paths:
            report.error(doc.path, 1, "frontmatter parent must point to a plan in this set")
        requirements = as_list(meta.get("requirements"))
        for slug in requirements:
            if slug not in slugs:
                report.error(
                    doc.path, 1, f"requirements lists {slug}, which the spec does not define"
                )
        blocked_by: list[Path] = []
        for entry in as_list(meta.get("blocked-by")):
            target = resolve(doc.path, entry)
            if target not in children:
                report.error(doc.path, 1, f"blocked-by {entry} is not a child plan in this set")
            else:
                blocked_by.append(target)
        tasks = check_tasks(doc, internal, slugs, report)
        state_file = plans_dir / ".state" / doc.path.relative_to(plans_dir).with_suffix(".yaml")
        state, review = load_state(state_file, report)
        if not state_file.is_file():
            report.warn(doc.path, 1, f"no state file at {display(state_file)}")
        for task, status in state.items():
            if task not in tasks:
                report.error(state_file, 1, f"task {task} does not exist in {doc.path.name}")
            if status not in TASK_STATUSES:
                report.error(
                    state_file, 1, f"task {task} status must be one of {', '.join(TASK_STATUSES)}"
                )
        if review == "done" and any(state.get(task) != "done" for task in tasks):
            report.error(state_file, 1, "review cannot be done while tasks are unfinished")
        plans.append(Plan(doc, tasks, blocked_by, requirements, state, review))
    return root, plans


def check_tasks(doc: Doc, internal: set[Path], slugs: set[str], report: Report) -> list[str]:
    tasks: list[str] = []
    uncited: list[tuple[str, int]] = []
    current: tuple[str, int] | None = None
    for number, line in content_lines(doc):
        heading = TASK_HEADING.match(line)
        other = HEADING.match(line)
        if heading:
            task = heading.group(1)
            if task in tasks:
                report.error(doc.path, number, f"task {task} is defined twice")
            tasks.append(task)
            current = (task, number)
            uncited.append(current)
        elif other and len(other.group(1)) <= 3:
            current = None
        if current in uncited and TASK_REQUIREMENTS.match(line) and REQ_REF.search(line):
            uncited.remove(current)
        for ref in undefined_refs(line, doc, internal, slugs):
            report.error(doc.path, number, f"{ref} is not defined in the spec")
    if not tasks:
        report.error(doc.path, 1, "plan has no task headings such as ### T1 - <title>")
    for task, number in uncited:
        report.error(doc.path, number, f"task {task} has no **Requirements:** line with an ID")
    return tasks


def check_plan_set(root: Doc, plans: list[Plan], coverable: list[str], report: Report) -> None:
    graph = {plan.doc.path.resolve(): plan.blocked_by for plan in plans}
    cycle = find_cycle(graph)
    if cycle:
        names = " -> ".join(display(path) for path in cycle)
        report.error(cycle[0], 1, f"blocked-by forms a cycle: {names}")
    covered = {slug for plan in plans for slug in plan.requirements}
    covered.update(as_list(root.meta.get("out-of-scope")))
    uncovered = [slug for slug in coverable if slug not in covered]
    if uncovered:
        report.warn(
            root.path,
            1,
            f"not covered by any plan or listed in out-of-scope: {', '.join(uncovered)}",
        )


def is_complete(plan: Plan) -> bool:
    return plan.review == "done" and all(plan.state.get(task) == "done" for task in plan.tasks)


def print_status(root: Doc, plans: list[Plan]) -> None:
    title = next(
        (
            line.lstrip("# ").strip()
            for line in root.lines[root.body_start :]
            if line.startswith("# ")
        ),
        root.path.parent.name,
    )
    print(f"{title} ({root.meta.get('status', 'draft')})")
    by_path = {plan.doc.path.resolve(): plan for plan in plans}
    next_task = ""
    for plan in plans:
        done = sum(1 for task in plan.tasks if plan.state.get(task) == "done")
        active = [task for task in plan.tasks if plan.state.get(task) == "in-progress"]
        stuck = [task for task in plan.tasks if plan.state.get(task) == "blocked"]
        blockers = [
            path for path in plan.blocked_by if path in by_path and not is_complete(by_path[path])
        ]
        notes = [f"in progress: {', '.join(active)}"] if active else []
        if stuck:
            notes.append(f"blocked tasks: {', '.join(stuck)}")
        if blockers:
            notes.append(f"blocked by: {', '.join(display(path) for path in blockers)}")
        notes.append(f"review: {plan.review}")
        print(
            f"  {display(plan.doc.path)}  {done}/{len(plan.tasks)} done"
            + (f"  {'; '.join(notes)}" if notes else "")
        )
        if not next_task and not blockers and not stuck and not is_complete(plan):
            pending = [task for task in plan.tasks if plan.state.get(task, "todo") != "done"]
            next_task = f"{display(plan.doc.path)} {pending[0] if pending else 'review'}"
    print(f"next: {next_task or 'none'}")


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("spec", type=Path, help="root SPEC.md of the spec set")
    parser.add_argument(
        "--research",
        type=Path,
        help="research directory (default: the nearest docs/research at or above the spec, up to the repository root; skipped with --plans)",
    )
    parser.add_argument("--plans", type=Path, help="plan set directory to check against the spec")
    parser.add_argument("--list", action="store_true", help="print the requirement index")
    parser.add_argument(
        "--fingerprint",
        action="store_true",
        help="print the spec-baseline field for a reconciled plan set",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="print plan progress and the next task (needs --plans)",
    )
    args = parser.parse_args()
    if not args.spec.is_file():
        print(f"check_spec: {args.spec} is not a file", file=sys.stderr)
        return 2
    if args.status and not args.plans:
        print("check_spec: --status needs --plans", file=sys.stderr)
        return 2
    for directory in (args.plans, args.research):
        if directory and not directory.is_dir():
            print(f"check_spec: {directory} is not a directory", file=sys.stderr)
            return 2
    report = Report()
    docs = load_spec_set(args.spec, report)
    requirements = check_spec_set(docs, report)
    research = args.research
    if research is None:
        for directory in (args.spec.resolve().parent, *args.spec.resolve().parents):
            if (directory / "docs" / "research").is_dir():
                research = directory / "docs" / "research"
                break
            if (directory / ".git").exists():
                break
    if not args.plans and research is not None:
        check_research(research, report)
    slugs = {requirement.slug for requirement in requirements}
    root: Doc | None = None
    plans: list[Plan] = []
    if args.plans and docs:
        if docs[0].meta.get("status") != "approved":
            report.error(docs[0].path, 1, "plans need an approved spec")
        root, plans = load_plans(args.plans, docs, slugs, report)
        if root is not None:
            coverable = [r.slug for r in requirements if not r.invariant]
            check_plan_set(root, plans, coverable, report)
    if args.list:
        for requirement in requirements:
            flag = "" if requirement.has_scenarios else "  [no scenarios]"
            print(
                f"{requirement.slug}  {display(requirement.path)}:{requirement.line}  {requirement.title}{flag}"
            )
    if args.fingerprint and docs and not report.errors:
        print(f"spec-baseline: {spec_fingerprint(docs)}")
    if args.status and root is not None and not report.errors:
        print_status(root, plans)
    for line in [*report.errors, *report.warnings]:
        print(line)
    print(f"check_spec: {len(report.errors)} errors, {len(report.warnings)} warnings")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
