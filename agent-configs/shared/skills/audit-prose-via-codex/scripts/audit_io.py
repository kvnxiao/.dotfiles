import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


MODES = {
    "quick": ("Quick rewrite", "low"),
    "change-set": ("Change-set audit", "medium"),
    "full": ("Full audit", "high"),
}
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
ALLOWED_EVENT_TYPES = {
    "thread.started",
    "turn.started",
    "item.started",
    "item.updated",
    "item.completed",
    "turn.completed",
}
RETRYABLE_EVENT_RE = re.compile(
    r"reconnect|stream disconnected|websocket|connection reset|timed out|temporarily unavailable",
    re.IGNORECASE,
)
TRAILER_RE = re.compile(
    r"^(?:Co-Authored-By|Signed-off-by|Reviewed-by|Acked-by|Refs|Fixes|Closes|Linear|BREAKING CHANGE):\s",
)
GENERATED_LINE_RE = re.compile(r"^\s*(?:\U0001F916|Generated with)\s")
PROSE_SUFFIXES = {".md", ".markdown", ".txt", ".rst", ".adoc", ".mdx"}
PROSE_NAMES = {"README", "CHANGELOG", "LICENSE", "NOTICE", "AGENTS", "CLAUDE"}
COMMENT_SYNTAX = {
    ".sql": (("--",), (("/*", "*/"),)),
    ".ts": (("//",), (("/*", "*/"),)),
    ".tsx": (("//",), (("/*", "*/"),)),
    ".js": (("//",), (("/*", "*/"),)),
    ".jsx": (("//",), (("/*", "*/"),)),
    ".mjs": (("//",), (("/*", "*/"),)),
    ".cjs": (("//",), (("/*", "*/"),)),
    ".go": (("//",), (("/*", "*/"),)),
    ".rs": (("//",), (("/*", "*/"),)),
    ".java": (("//",), (("/*", "*/"),)),
    ".kt": (("//",), (("/*", "*/"),)),
    ".swift": (("//",), (("/*", "*/"),)),
    ".dart": (("//",), (("/*", "*/"),)),
    ".c": (("//",), (("/*", "*/"),)),
    ".h": (("//",), (("/*", "*/"),)),
    ".cpp": (("//",), (("/*", "*/"),)),
    ".cs": (("//",), (("/*", "*/"),)),
    ".css": ((), (("/*", "*/"),)),
    ".scss": (("//",), (("/*", "*/"),)),
    ".tf": (("#", "//"), (("/*", "*/"),)),
    ".hcl": (("#", "//"), (("/*", "*/"),)),
    ".py": (("#",), (('"""', '"""'), ("'''", "'''"))),
    ".sh": (("#",), ()),
    ".bash": (("#",), ()),
    ".zsh": (("#",), ()),
    ".fish": (("#",), ()),
    ".rb": (("#",), ()),
    ".pl": (("#",), ()),
    ".yaml": (("#",), ()),
    ".yml": (("#",), ()),
    ".toml": (("#",), ()),
    ".just": (("#",), ()),
    ".html": ((), (("<!--", "-->"),)),
    ".xml": ((), (("<!--", "-->"),)),
}
COMMENT_NAMES = {
    "Dockerfile": (("#",), ()),
    "Makefile": (("#",), ()),
    "justfile": (("#",), ()),
    "Justfile": (("#",), ()),
}
DRAFT_KINDS = {
    "commit-subject",
    "commit-message",
    "commit-body",
    "pr-title",
    "pr-body",
    "draft-prose",
}
WIDTH_LIMITED_KINDS = {"commit-subject", "commit-message", "commit-body"}
COMMIT_LINE_LIMIT = 72
WRAP_SLACK = 8
BLOCK_START_RE = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|>\s|\|)")
DUPLICATE_MIN_CHARS = 40
DEFAULT_MAX_INPUT_CHARS = 400_000


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        fail(f"Cannot read UTF-8 input {path}: {error}")


def write_text(path: Path, text: str) -> None:
    try:
        path.write_text(text, encoding="utf-8", newline="\n")
    except OSError as error:
        fail(f"Cannot write {path}: {error}")


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        fail(f"Cannot hash {path}: {error}")
    return digest.hexdigest()


def line_ending(path: Path) -> str:
    try:
        content = path.read_bytes()
    except OSError as error:
        fail(f"Cannot inspect line endings in {path}: {error}")
    without_crlf = content.replace(b"\r\n", b"")
    if b"\r" in without_crlf or (b"\r\n" in content and b"\n" in without_crlf):
        fail(f"Mixed or CR-only line endings are not supported: {path}")
    return "crlf" if b"\r\n" in content else "lf"


def is_utf8_text(path: Path) -> bool:
    try:
        content = path.read_bytes()
    except OSError as error:
        fail(f"Cannot classify {path}: {error}")
    if b"\0" in content:
        return False
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def bytes_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", b"").decode("utf-8", errors="replace").strip()
        fail(f"git {' '.join(args)} failed: {detail or error}")
    return result.stdout


def split_nul(value: bytes) -> list[str]:
    try:
        return [part.decode("utf-8") for part in value.split(b"\0") if part]
    except UnicodeDecodeError as error:
        fail(f"Git returned a path that is not UTF-8: {error}")


def resolve_target(root: Path, relative: str) -> Path:
    if not relative or any(character in relative for character in "\n\r\t"):
        fail("Target paths must be nonempty and contain no control separators")
    path = Path(relative)
    if path.is_absolute():
        fail(f"Target path must be patch-root-relative: {relative}")
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        fail(f"Target escapes the patch root: {relative}")
    if not resolved.is_file():
        fail(f"Target is not a file: {relative}")
    return resolved


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(ranges):
        if start < 1 or end < start:
            fail(f"Invalid editable range: {start}-{end}")
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def changed_ranges(diff: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for line in diff.splitlines():
        match = HUNK_RE.match(line)
        if not match:
            continue
        start = int(match.group(3))
        count = int(match.group(4) or "1")
        if count:
            ranges.append((start, start + count - 1))
    return merge_ranges(ranges)


def format_ranges(ranges: list[tuple[int, int]] | None) -> str:
    if ranges is None:
        return "full"
    return ",".join(f"{start}-{end}" for start, end in ranges)


def split_file_lines(text: str) -> list[str]:
    if not text:
        return []
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def numbered_source(text: str, ranges: list[tuple[int, int]] | None) -> str:
    lines = split_file_lines(text)
    if ranges is None:
        windows = [(1, len(lines))] if lines else []
    else:
        windows = merge_ranges(
            [(max(1, start - 3), min(len(lines), end + 3)) for start, end in ranges]
        )
    rendered: list[str] = []
    for index, (start, end) in enumerate(windows):
        if index:
            rendered.append("...")
        rendered.extend(f"{line_number}\t{lines[line_number - 1]}" for line_number in range(start, end + 1))
    return "\n".join(rendered)


def intersect_ranges(
    left: list[tuple[int, int]], right: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    overlaps: list[tuple[int, int]] = []
    for left_start, left_end in left:
        for right_start, right_end in right:
            start = max(left_start, right_start)
            end = min(left_end, right_end)
            if start <= end:
                overlaps.append((start, end))
    return merge_ranges(overlaps) if overlaps else []


def invert_ranges(excluded: set[int], line_count: int) -> list[tuple[int, int]]:
    kept = [number for number in range(1, line_count + 1) if number not in excluded]
    return merge_ranges([(number, number) for number in kept]) if kept else []


def comment_syntax(relative: str) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]] | None:
    path = Path(relative)
    if path.name in COMMENT_NAMES:
        return COMMENT_NAMES[path.name]
    return COMMENT_SYNTAX.get(path.suffix.lower())


def classify_path(relative: str) -> str:
    path = Path(relative)
    if path.suffix.lower() in PROSE_SUFFIXES or path.name in PROSE_NAMES:
        return "prose"
    if comment_syntax(relative) is not None:
        return "code"
    return "excluded"


def comment_ranges(text: str, relative: str) -> list[tuple[int, int]]:
    syntax = comment_syntax(relative)
    if syntax is None:
        return []
    line_prefixes, block_pairs = syntax
    ranges: list[tuple[int, int]] = []
    open_close: tuple[str, str] | None = None
    for number, line in enumerate(split_file_lines(text), start=1):
        stripped = line.strip()
        if open_close is not None:
            ranges.append((number, number))
            if open_close[1] in line:
                open_close = None
            continue
        opened = next(
            (pair for pair in block_pairs if stripped.startswith(pair[0])), None
        )
        if opened is not None:
            ranges.append((number, number))
            remainder = stripped[len(opened[0]) :]
            if opened[1] not in remainder:
                open_close = opened
            continue
        if line_prefixes and stripped.startswith(line_prefixes):
            ranges.append((number, number))
    return merge_ranges(ranges) if ranges else []


def paragraph_ranges(text: str) -> list[tuple[int, int]]:
    blocks: list[tuple[int, int]] = []
    current: list[int] = []
    for number, line in enumerate(split_file_lines(text), start=1):
        if not line.strip() or BLOCK_START_RE.match(line):
            if current:
                blocks.append((current[0], current[-1]))
                current = []
            if not line.strip():
                continue
        current.append(number)
    if current:
        blocks.append((current[0], current[-1]))
    return blocks


def expand_to_blocks(
    changed: list[tuple[int, int]], blocks: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    touched = [
        block
        for block in blocks
        if any(
            start <= block[1] and block[0] <= end for start, end in changed
        )
    ]
    return merge_ranges(touched) if touched else []


def draft_ranges(text: str) -> list[tuple[int, int]]:
    lines = split_file_lines(text)
    protected = {
        number
        for number, line in enumerate(lines, start=1)
        if not line.strip() or TRAILER_RE.match(line) or GENERATED_LINE_RE.match(line)
    }
    return invert_ranges(protected, len(lines))


def normalized(line: str) -> str:
    return " ".join(line.split())


def inventory_hash(root: Path, scope_kind: str) -> str | None:
    if scope_kind != "repository-change-set":
        return None
    return bytes_hash(git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all"))


def make_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "bundle_hash": {"type": "string"},
            "status": {"enum": ["patch", "no_changes", "blocked"]},
            "reviewed_target_ids": {
                "type": "array",
                "items": {"type": "integer"},
            },
            "reason": {"type": "string"},
            "edits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "target_id": {"type": "integer"},
                        "start_line": {"type": "integer"},
                        "end_line": {"type": "integer"},
                        "replacement_lines": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "target_id",
                        "start_line",
                        "end_line",
                        "replacement_lines",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["bundle_hash", "status", "reviewed_target_ids", "reason", "edits"],
        "additionalProperties": False,
    }


def split_batches(
    paths: list[str], sections: list[str], budget: int
) -> list[list[str]]:
    if budget < 1:
        fail("Input budget leaves no room for source content")
    batches: list[list[str]] = []
    current: list[str] = []
    used = 0
    for relative, section in zip(paths, sections):
        size = len(section) + 1
        if current and used + size > budget:
            batches.append(current)
            current = []
            used = 0
        current.append(relative)
        used += size
    if current:
        batches.append(current)
    return batches


def prepare(args: argparse.Namespace) -> None:
    root = Path(args.patch_root).resolve()
    run_dir = Path(args.run_dir).resolve()
    if not root.is_dir() or not run_dir.is_dir():
        fail("Patch root and run directory must exist")
    mode_text, effort = MODES[args.mode]
    paths: list[str] = []
    range_map: dict[str, list[tuple[int, int]]] = {}
    kind_map: dict[str, str] = {}
    skipped: list[dict[str, str]] = []
    inventory_before = inventory_hash(root, args.scope_kind)
    candidate_resolved: dict[str, Path] = {}
    candidate_hashes_before: dict[str, str] = {}

    if args.scope_kind == "repository-change-set":
        if args.target or args.line_range:
            fail("Repository change-set scope discovers its own targets")
        tracked = [
            path.replace("\\", "/")
            for path in split_nul(
                git(
                    root,
                    "diff",
                    "--name-only",
                    "--diff-filter=ACMRTUXB",
                    "-z",
                    "HEAD",
                )
            )
        ]
        untracked = [
            path.replace("\\", "/")
            for path in split_nul(
                git(root, "ls-files", "--others", "--exclude-standard", "-z")
            )
        ]
        candidates = list(dict.fromkeys([*tracked, *untracked]))
        candidate_resolved = {
            relative: resolve_target(root, relative) for relative in candidates
        }
        candidate_hashes_before = {
            relative: file_hash(path) for relative, path in candidate_resolved.items()
        }
        if inventory_hash(root, args.scope_kind) != inventory_before:
            fail("The repository change inventory changed during discovery")
        for relative in tracked:
            file_kind = classify_path(relative)
            if file_kind == "excluded":
                skipped.append(
                    {
                        "path": relative,
                        "reason": "non-prose-file",
                        "sha256": candidate_hashes_before[relative],
                    }
                )
                continue
            try:
                diff = git(root, "diff", "--unified=0", "HEAD", "--", relative).decode(
                    "utf-8"
                )
            except UnicodeDecodeError as error:
                fail(f"Git returned a non-UTF-8 diff for {relative}: {error}")
            ranges = changed_ranges(diff)
            if not ranges:
                continue
            text = read_utf8(candidate_resolved[relative])
            if file_kind == "code":
                ranges = expand_to_blocks(ranges, comment_ranges(text, relative))
                if not ranges:
                    skipped.append(
                        {
                            "path": relative,
                            "reason": "no-changed-comment-lines",
                            "sha256": candidate_hashes_before[relative],
                        }
                    )
                    continue
            else:
                ranges = expand_to_blocks(ranges, paragraph_ranges(text))
            paths.append(relative)
            range_map[relative] = ranges
            kind_map[relative] = (
                "code-comment" if file_kind == "code" else "documentation"
            )
        for relative in untracked:
            if relative in paths:
                continue
            resolved_path = resolve_target(root, relative)
            if not is_utf8_text(resolved_path):
                skipped.append(
                    {
                        "path": relative,
                        "reason": "binary-or-non-UTF-8",
                        "sha256": candidate_hashes_before[relative],
                    }
                )
                continue
            file_kind = classify_path(relative)
            if file_kind == "excluded":
                skipped.append(
                    {
                        "path": relative,
                        "reason": "non-prose-file",
                        "sha256": candidate_hashes_before[relative],
                    }
                )
                continue
            if file_kind == "code":
                ranges = comment_ranges(read_utf8(resolved_path), relative)
                if not ranges:
                    skipped.append(
                        {
                            "path": relative,
                            "reason": "no-comment-lines",
                            "sha256": candidate_hashes_before[relative],
                        }
                    )
                    continue
                range_map[relative] = ranges
                kind_map[relative] = "code-comment"
            else:
                range_map[relative] = []
                kind_map[relative] = "documentation"
            paths.append(relative)
    else:
        paths = list(args.target or [])
        for relative, start, end in args.line_range or []:
            if relative not in paths:
                paths.append(relative)
            range_map.setdefault(relative, []).append((int(start), int(end)))
        for relative, declared_kind in getattr(args, "target_kind", None) or []:
            if declared_kind not in DRAFT_KINDS:
                fail(f"Unknown target kind: {declared_kind}")
            if args.scope_kind != "transient":
                fail("Target kinds apply to transient drafts only")
            if relative not in paths:
                paths.append(relative)
            kind_map[relative.replace("\\", "/")] = declared_kind

    paths = list(dict.fromkeys(path.replace("\\", "/") for path in paths))
    range_map = {
        path.replace("\\", "/"): ranges for path, ranges in range_map.items()
    }
    kind_map = {path.replace("\\", "/"): kind for path, kind in kind_map.items()}
    if skipped:
        write_text(
            run_dir / "skipped-targets.json",
            json.dumps(
                [
                    {"path": item["path"], "reason": item["reason"]}
                    for item in skipped
                ],
                indent=2,
            )
            + "\n",
        )
    if not paths:
        fail("No auditable targets", 4)

    if args.scope_kind == "repository-change-set":
        resolved = {relative: candidate_resolved[relative] for relative in paths}
        hashes_before = {
            relative: candidate_hashes_before[relative] for relative in paths
        }
    else:
        resolved = {relative: resolve_target(root, relative) for relative in paths}
        hashes_before = {
            relative: file_hash(path) for relative, path in resolved.items()
        }
    def build(selected: list[str]) -> tuple[list[dict], list[str]]:
        targets: list[dict] = []
        source_sections: list[str] = []
        for target_id, relative in enumerate(selected, start=1):
            text = read_utf8(resolved[relative])
            raw_ranges = range_map.get(relative)
            if args.scope_kind == "repository-change-set" and raw_ranges == []:
                ranges = None
            elif raw_ranges:
                ranges = merge_ranges(raw_ranges)
            else:
                ranges = None
            kind = kind_map.get(relative)
            if args.scope_kind == "transient":
                kind = kind or "draft-prose"
                allowed = draft_ranges(text)
                ranges = intersect_ranges(ranges, allowed) if ranges else allowed
                if not ranges:
                    fail(f"No editable draft line remains in {relative}")
            elif args.scope_kind == "named":
                file_kind = classify_path(relative)
                if file_kind == "excluded":
                    fail(f"Named target is not auditable prose: {relative}")
                if file_kind == "code":
                    kind = "code-comment"
                    allowed = comment_ranges(text, relative)
                    ranges = intersect_ranges(ranges, allowed) if ranges else allowed
                    if not ranges:
                        fail(f"Named target has no comment line to audit: {relative}")
                else:
                    kind = "documentation"
            kind = kind or "documentation"
            line_count = len(split_file_lines(text))
            if ranges and any(end > line_count for _, end in ranges):
                fail(f"Editable range exceeds {relative}'s {line_count} lines")
            target = {
                "id": target_id,
                "path": relative,
                "kind": kind,
                "editable": ranges,
                "line_ending": line_ending(resolved[relative]),
                "sha256": hashes_before[relative],
            }
            targets.append(target)
            width_note = (
                [f"max-line-width: {COMMIT_LINE_LIMIT}"]
                if kind in WIDTH_LIMITED_KINDS
                else []
            )
            source_sections.append(
                "\n".join(
                    [
                        f"===== TARGET {target_id} BEGIN =====",
                        f"path: {relative}",
                        f"artifact-kind: {kind}",
                        *width_note,
                        "source-kind: current-lines",
                        f"editable: {format_ranges(ranges)}",
                        f"line-ending: {target['line_ending']}",
                        f"final-newline: {'yes' if text.endswith(chr(10)) else 'no'}",
                        "content-lines:",
                        numbered_source(text, ranges),
                        f"===== TARGET {target_id} END =====",
                    ]
                )
            )
        return targets, source_sections

    targets, source_sections = build(paths)

    if args.scope_kind == "repository-change-set":
        hashes_after = {
            relative: file_hash(path) for relative, path in candidate_resolved.items()
        }
        expected_hashes = candidate_hashes_before
    else:
        hashes_after = {relative: file_hash(path) for relative, path in resolved.items()}
        expected_hashes = hashes_before
    inventory_after = inventory_hash(root, args.scope_kind)
    if expected_hashes != hashes_after or inventory_before != inventory_after:
        fail("Targets changed while the audit input was prepared")

    diction = read_utf8(Path(args.diction))
    template = read_utf8(Path(args.prompt_template))
    if not diction.strip() or "{{AUDIT_INPUT}}" not in template or "{{BUNDLE_HASH}}" not in template:
        fail("Diction and prompt template inputs must be complete")

    def render_input(built: list[dict], sections: list[str]) -> str:
        target_list = "\n".join(
            f"{target['id']}\t{target['kind']}\t{target['path']}" for target in built
        )
        return "\n".join(
            [
                "<mode>",
                mode_text,
                "</mode>",
                "<patch_root>",
                str(root),
                "</patch_root>",
                "<targets>",
                target_list,
                "</targets>",
                "<diction_reference>",
                diction.rstrip("\n"),
                "</diction_reference>",
                "<source>",
                "\n".join(sections),
                "</source>",
                "",
            ]
        )

    audit_input = render_input(targets, source_sections)
    batch_index = getattr(args, "batch", None)
    budget = getattr(args, "max_input_chars", None) or DEFAULT_MAX_INPUT_CHARS
    overhead = len(audit_input) - sum(len(section) for section in source_sections)
    batches = split_batches(paths, source_sections, budget - overhead)
    if len(batches) > 1:
        if batch_index is None:
            write_text(
                run_dir / "batches.json",
                json.dumps(
                    [
                        {"batch": index, "targets": group}
                        for index, group in enumerate(batches, start=1)
                    ],
                    indent=2,
                )
                + "\n",
            )
            fail(
                f"Bundle of {len(audit_input)} characters exceeds the {budget}-character "
                f"input budget; prepared {len(batches)} batches in batches.json",
                5,
            )
        if batch_index < 1 or batch_index > len(batches):
            fail(f"Batch index must fall between 1 and {len(batches)}")
        targets, source_sections = build(batches[batch_index - 1])
        audit_input = render_input(targets, source_sections)
    elif batch_index is not None and batch_index != 1:
        fail("This bundle needs no batching; omit --batch or pass 1")
    bundle_hash = hashlib.sha256(audit_input.encode("utf-8")).hexdigest()
    prompt = template.replace("{{BUNDLE_HASH}}", bundle_hash).replace("{{AUDIT_INPUT}}", audit_input)

    snapshot = {
        "patch_root": str(root),
        "scope_kind": args.scope_kind,
        "inventory_sha256": inventory_after,
        "candidates": [
            {"path": relative, "sha256": sha256}
            for relative, sha256 in candidate_hashes_before.items()
        ],
        "skipped": skipped,
        "targets": targets,
    }
    write_text(run_dir / "audit-input.md", audit_input)
    write_text(run_dir / "bundle-hash.txt", bundle_hash + "\n")
    write_text(run_dir / "effort.txt", effort + "\n")
    write_text(run_dir / "prompt.md", prompt)
    write_text(run_dir / "result-schema.json", json.dumps(make_schema(), indent=2) + "\n")
    write_text(run_dir / "snapshot.json", json.dumps(snapshot, indent=2) + "\n")
    print(f"Prepared {len(targets)} targets at {effort} reasoning effort")


def load_snapshot(run_dir: Path) -> dict:
    try:
        snapshot = json.loads(read_utf8(run_dir / "snapshot.json"))
    except json.JSONDecodeError as error:
        fail(f"Invalid snapshot: {error}")
    if not isinstance(snapshot, dict) or not snapshot.get("targets"):
        fail("Snapshot contains no targets")
    return snapshot


def check_state(run_dir: Path) -> dict:
    snapshot = load_snapshot(run_dir)
    root = Path(snapshot["patch_root"])
    for candidate in snapshot.get("candidates", []):
        path = resolve_target(root, candidate["path"])
        if file_hash(path) != candidate["sha256"]:
            fail(f"Stale discovered candidate: {candidate['path']}")
    for target in snapshot["targets"]:
        path = resolve_target(root, target["path"])
        if file_hash(path) != target["sha256"]:
            fail(f"Stale target: {target['path']}")
    if inventory_hash(root, snapshot["scope_kind"]) != snapshot["inventory_sha256"]:
        fail("The repository change inventory is stale")
    return snapshot


def validate_events(path: Path) -> str:
    completed = False
    final_message: str | None = None
    for line_number, line in enumerate(read_utf8(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            fail(f"Invalid JSONL event at line {line_number}: {error}")
        if not isinstance(event, dict):
            fail(f"Invalid JSONL event object at line {line_number}")
        event_type = event.get("type")
        if event_type in {"error", "turn.failed"}:
            message = event.get("message")
            if isinstance(message, str) and RETRYABLE_EVENT_RE.search(message):
                fail(f"Transient Codex transport failure: {message.strip()}", 6)
            fail(f"Codex event stream reports {event_type}")
        if event_type not in ALLOWED_EVENT_TYPES:
            fail(f"Codex event stream contains an unknown event: {event_type}")
        if event_type == "turn.completed":
            completed = True
        if isinstance(event_type, str) and event_type.startswith("item."):
            item = event.get("item")
            if not isinstance(item, dict):
                fail(f"Codex event at line {line_number} has no item object")
            item_type = item.get("type")
            if item_type not in {"agent_message", "reasoning"}:
                fail(f"Codex attempted a disallowed tool item: {item_type}")
            if event_type == "item.completed" and item_type == "agent_message":
                message = item.get("text")
                if not isinstance(message, str):
                    fail("Completed agent message has no text")
                final_message = message
    if not completed:
        fail("Codex event stream has no completed turn")
    if final_message is None:
        fail("Codex event stream has no completed agent message")
    return final_message


def is_allowed(line_number: int, ranges: list[list[int]] | None) -> bool:
    return ranges is None or any(start <= line_number <= end for start, end in ranges)


def add_line_terminators(lines: list[str], final_newline: bool) -> list[str]:
    return [
        line + "\n" if index < len(lines) - 1 or final_newline else line
        for index, line in enumerate(lines)
    ]


def render_diff_lines(lines: list[str]) -> list[str]:
    rendered: list[str] = []
    in_hunk = False
    for line in lines:
        if HUNK_RE.match(line):
            in_hunk = True
            rendered.append(line)
        elif not in_hunk:
            rendered.append(line)
        elif line.endswith("\n"):
            rendered.append(line[:-1])
        else:
            rendered.append(line)
            rendered.append("\\ No newline at end of file")
    return rendered


class TargetRejected(Exception):
    pass


def render_patch(
    edits: list, targets: list[dict], root: Path
) -> tuple[list[tuple[dict, str]], list[tuple[dict, str]]]:
    target_by_id = {target["id"]: target for target in targets}
    sources = {
        target["id"]: split_file_lines(read_utf8(resolve_target(root, target["path"])))
        for target in targets
    }
    owners: dict[str, set[int]] = {}
    for owner_id, owner_lines in sources.items():
        for owner_line in owner_lines:
            text = normalized(owner_line)
            if len(text) >= DUPLICATE_MIN_CHARS:
                owners.setdefault(text, set()).add(owner_id)
    grouped: dict[int, list[dict]] = {}
    required_edit_keys = {
        "target_id",
        "start_line",
        "end_line",
        "replacement_lines",
    }
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != required_edit_keys:
            fail("Each edit must contain the exact replacement fields")
        target_id = edit["target_id"]
        start_line = edit["start_line"]
        end_line = edit["end_line"]
        replacement_lines = edit["replacement_lines"]
        if type(target_id) is not int or target_id not in target_by_id:
            fail(f"Edit references an unknown target ID: {target_id}")
        if type(start_line) is not int or type(end_line) is not int:
            fail("Edit line bounds must be integers")
        if start_line < 1 or end_line < start_line:
            fail(f"Invalid edit range: {start_line}-{end_line}")
        if not isinstance(replacement_lines, list) or any(
            not isinstance(line, str) or any(character in line for character in "\r\n\0")
            for line in replacement_lines
        ):
            fail("Replacement lines must be strings without line separators or NUL bytes")
        grouped.setdefault(target_id, []).append(edit)

    sections: list[tuple[dict, str]] = []
    dropped: list[tuple[dict, str]] = []
    for target_id, target_edits in grouped.items():
        target = target_by_id[target_id]
        source_text = read_utf8(resolve_target(root, target["path"]))
        source_lines = sources[target_id]
        width_limit = (
            COMMIT_LINE_LIMIT
            if target["kind"] == "commit-subject"
            else max(
                COMMIT_LINE_LIMIT, max((len(line) for line in source_lines), default=0)
            )
            + WRAP_SLACK
        )
        previous_end = 0
        try:
            for edit in sorted(target_edits, key=lambda value: value["start_line"]):
                if edit["end_line"] > len(source_lines):
                    fail(f"Edit exceeds {target['path']}'s {len(source_lines)} lines")
                if edit["start_line"] <= previous_end:
                    fail(f"Edits overlap in {target['path']}")
                outside = [
                    line_number
                    for line_number in range(edit["start_line"], edit["end_line"] + 1)
                    if not is_allowed(line_number, target["editable"])
                ]
                if outside:
                    raise TargetRejected(
                        "edit touches line(s) "
                        f"{','.join(str(number) for number in outside)} outside "
                        f"{format_ranges(target['editable'])}"
                    )
                if target["kind"] in WIDTH_LIMITED_KINDS and any(
                    len(line) > width_limit for line in edit["replacement_lines"]
                ):
                    raise TargetRejected(
                        f"replacement rewraps past {width_limit} characters"
                    )
                if target["kind"] == "commit-subject" and len(
                    edit["replacement_lines"]
                ) != edit["end_line"] - edit["start_line"] + 1:
                    raise TargetRejected("replacement changes the subject line count")
                replaced = {
                    normalized(line)
                    for line in source_lines[edit["start_line"] - 1 : edit["end_line"]]
                }
                for line in edit["replacement_lines"]:
                    text = normalized(line)
                    if len(text) < DUPLICATE_MIN_CHARS or text in replaced:
                        continue
                    line_owners = owners.get(text, set())
                    if line_owners - {target_id}:
                        raise TargetRejected("replacement copies a line from another target")
                    if target_id in line_owners:
                        raise TargetRejected(
                            "replacement duplicates a line the target already holds"
                        )
                previous_end = edit["end_line"]
        except TargetRejected as rejection:
            dropped.append((target, str(rejection)))
            continue

        updated_lines = list(source_lines)
        for edit in sorted(
            target_edits, key=lambda value: value["start_line"], reverse=True
        ):
            updated_lines[edit["start_line"] - 1 : edit["end_line"]] = edit[
                "replacement_lines"
            ]
        if updated_lines == source_lines:
            continue
        final_newline = source_text.endswith("\n")
        updated_final_newline = final_newline and bool(updated_lines)
        diff_lines = render_diff_lines(
            list(
                difflib.unified_diff(
                    add_line_terminators(source_lines, final_newline),
                    add_line_terminators(updated_lines, updated_final_newline),
                    fromfile=f"a/{target['path']}",
                    tofile=f"b/{target['path']}",
                    n=3,
                    lineterm="",
                )
            )
        )
        sections.append(
            (
                target,
                "\n".join(
                    [f"diff --git a/{target['path']} b/{target['path']}", *diff_lines]
                ),
            )
        )
    if not sections:
        if dropped:
            detail = "; ".join(
                f"{target['path']} ({reason})" for target, reason in dropped
            )
            fail(f"Every edited target was rejected: {detail}")
        fail("Patch edits produce no changes")
    return sections, dropped


def write_patch(path: Path, patch: str, targets: list[dict]) -> None:
    target_by_header = {
        f"diff --git a/{target['path']} b/{target['path']}": target
        for target in targets
    }
    output = bytearray()
    separator = b"\n"
    lines = patch.split("\n")
    if lines[-1] == "":
        lines.pop()
    for line in lines:
        if line.startswith("diff --git "):
            separator = (
                b"\r\n"
                if target_by_header[line]["line_ending"] == "crlf"
                else b"\n"
            )
        output.extend(line.encode("utf-8"))
        output.extend(separator)
    try:
        path.write_bytes(output)
    except OSError as error:
        fail(f"Cannot write {path}: {error}")


def validate(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir).resolve()
    snapshot = check_state(run_dir)
    final_message = validate_events(Path(args.events))
    try:
        result = json.loads(read_utf8(Path(args.result)))
    except json.JSONDecodeError as error:
        fail(f"Invalid result JSON: {error}")
    try:
        event_result = json.loads(final_message)
    except json.JSONDecodeError as error:
        fail(f"Invalid JSON in the completed agent message: {error}")
    if event_result != result:
        fail("Completed agent message does not match the result file")
    required_keys = {"bundle_hash", "status", "reviewed_target_ids", "reason", "edits"}
    if not isinstance(result, dict) or set(result) != required_keys:
        fail("Result JSON has unexpected or missing fields")
    expected_hash = read_utf8(run_dir / "bundle-hash.txt").strip()
    expected_ids = [target["id"] for target in snapshot["targets"]]
    if result["bundle_hash"] != expected_hash:
        fail("Result bundle hash does not match the prepared input")
    reviewed_ids = result["reviewed_target_ids"]
    if not isinstance(reviewed_ids, list) or any(type(value) is not int for value in reviewed_ids):
        fail("Reviewed target IDs must be integers")
    if sorted(reviewed_ids) != expected_ids or len(set(reviewed_ids)) != len(expected_ids):
        fail("Result does not acknowledge every target exactly once")
    status = result["status"]
    reason = result["reason"]
    edits = result["edits"]
    if not isinstance(status, str) or not isinstance(reason, str) or not isinstance(edits, list):
        fail("Result status and reason must be strings, and edits must be an array")
    if status == "blocked":
        if not reason or edits:
            fail("Blocked result must contain one reason and no edits")
        print(f"BLOCKED: {reason}")
        raise SystemExit(3)
    if status == "no_changes":
        if reason or edits:
            fail("No-changes result must contain no reason or edits")
        print("NO_CHANGES")
        raise SystemExit(4)
    if status != "patch" or reason or not edits:
        fail(f"Invalid result status: {status}")
    sections, dropped = render_patch(
        edits, snapshot["targets"], Path(snapshot["patch_root"])
    )
    patch = "\n".join(section for _, section in sections) + "\n"
    write_patch(run_dir / "result.patch", patch, snapshot["targets"])
    for target, section in sections:
        write_patch(
            run_dir / f"result-{target['id']}.patch", section + "\n", snapshot["targets"]
        )
    print("PATCH")
    for target, reason in dropped:
        print(f"DROPPED\t{target['id']}\t{target['path']}\t{reason}")
    for target, _ in sections:
        print(f"{target['id']}\t{target['kind']}\t{target['path']}\tresult-{target['id']}.patch")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    subparsers = root.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--patch-root", required=True)
    prepare_parser.add_argument("--run-dir", required=True)
    prepare_parser.add_argument("--mode", choices=MODES, required=True)
    prepare_parser.add_argument(
        "--scope-kind",
        choices=["repository-change-set", "named", "transient"],
        required=True,
    )
    prepare_parser.add_argument("--diction", required=True)
    prepare_parser.add_argument("--prompt-template", required=True)
    prepare_parser.add_argument("--target", action="append")
    prepare_parser.add_argument("--line-range", action="append", nargs=3, metavar=("PATH", "START", "END"))
    prepare_parser.add_argument("--target-kind", action="append", nargs=2, metavar=("PATH", "KIND"))
    prepare_parser.add_argument("--max-input-chars", type=int, default=DEFAULT_MAX_INPUT_CHARS)
    prepare_parser.add_argument("--batch", type=int)
    prepare_parser.set_defaults(handler=prepare)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--run-dir", required=True)
    validate_parser.add_argument("--result", required=True)
    validate_parser.add_argument("--events", required=True)
    validate_parser.set_defaults(handler=validate)

    state_parser = subparsers.add_parser("check-state")
    state_parser.add_argument("--run-dir", required=True)
    state_parser.set_defaults(handler=lambda args: check_state(Path(args.run_dir).resolve()))
    return root


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.handler(arguments)
