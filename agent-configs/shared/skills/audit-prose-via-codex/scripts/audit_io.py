import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
import textwrap
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
SINGLE_LINE_KINDS = {"commit-subject", "pr-title"}
COMMIT_LINE_LIMIT = 72
MIN_WRAP_WIDTH = 72
MIN_OVERRIDE_WIDTH = 20
UNWRAPPED_MAX_WIDTH = 120
INDENTED_CODE_DEPTH = 4
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s*#{1,6}\s")
LIST_RE = re.compile(r"^(\s*(?:[-*+]|\d+[.)])\s+)")
CONTEXT_BLOCK_RE = re.compile(
    r"^\s*(?:\||>|<|\[[^\]]+\]:|(?:-{3,}|_{3,}|\*{3,}|={3,})\s*$)"
)
SETEXT_RE = re.compile(r"^\s*(?:={2,}|-{2,})\s*$")
TABLE_DELIMITER_RE = re.compile(r"^\s*:?-{2,}:?(?:\s*\|\s*:?-{2,}:?)+\s*$")
THEMATIC_BREAK_RE = re.compile(r"^\s*(?:(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,})$")
SHEBANG_RE = re.compile(r"^#!")
PRAGMA_RE = re.compile(
    r"^(?:noqa|type:|pylint:|pyright:|mypy:|ruff:|fmt:|nolint|lint:|eslint-"
    r"|@ts-|prettier-ignore|biome-ignore|go:|cgo|SPDX-|-\*-|!)"
)
ABBREVIATION_RE = re.compile(
    r"\b(?:e\.g|i\.e|etc|cf|vs|al|approx|Dr|Mr|Ms|St|No|Fig|Sec)\.|\.\.\."
)
LOWERCASE_SENTENCE_RE = re.compile(r"[.!?][)\"'`\]]*\s+[a-z]")
CODE_SPAN_RE = re.compile(r"`[^`\n]+`")
URL_RE = re.compile(r"https?://[^\s<>()\[\]]+")
FLAG_RE = re.compile(r"(?<![\w-])--?[A-Za-z][\w-]*")
PATH_RE = re.compile(r"(?<![\w./-])[\w.-]*/[\w./-]+")
FILENAME_RE = re.compile(
    r"\b[\w-]+\.(?:md|markdown|mdx|json|jsonc|ya?ml|toml|lock|txt|rst|py|pyi|ts|tsx"
    r"|js|jsx|mjs|cjs|sh|bash|zsh|sql|rs|go|rb|java|kt|swift|c|h|cpp|cs|css|scss"
    r"|html|xml|ini|cfg|env|patch|diff)\b"
)
VERSION_RE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)*(?:-[\w.]+)?\b")
NUMBER_RE = re.compile(r"(?<![\w.])\d+(?:\.\d+)*\b")
IDENTIFIER_RE = re.compile(
    r"\b(?:[a-z]+(?:_[a-z0-9]+)+|[a-z]+[A-Z][A-Za-z0-9]*"
    r"|[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+|[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\b"
)
NUMBER_WORDS = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    "10": "ten",
    "11": "eleven",
    "12": "twelve",
}
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


def split_file_lines(text: str) -> list[str]:
    if not text:
        return []
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


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


def leading_indent(line: str) -> str:
    return line[: len(line) - len(line.lstrip())]


def closes_fence(stripped: str, fence: str) -> bool:
    run = len(stripped) - len(stripped.lstrip(fence[0]))
    return run >= len(fence) and not stripped[run:].strip()


def has_frontmatter(lines: list[str]) -> bool:
    if not lines or lines[0].strip() != "---" or len(lines) < 2 or not lines[1].strip():
        return False
    return any(line.strip() in {"---", "..."} for line in lines[1:])


def structural_context(lines: list[str]) -> set[int]:
    marked: set[int] = set()
    fence: str | None = None
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if fence is not None:
            if closes_fence(stripped, fence):
                fence = None
            continue
        opened = FENCE_RE.match(line)
        if opened:
            fence = opened.group(1)
            continue
        if TABLE_DELIMITER_RE.match(line):
            marked.add(number)
            if number > 1 and lines[number - 2].strip():
                marked.add(number - 1)
            for following in range(number + 1, len(lines) + 1):
                if not lines[following - 1].strip():
                    break
                marked.add(following)
            continue
        if SETEXT_RE.match(line) and number > 1 and lines[number - 2].strip():
            marked.update({number - 1, number})
            continue
        if THEMATIC_BREAK_RE.match(line):
            marked.add(number)
    return marked


def prose_spans(
    lines: list[str], excluded: set[int], allow_headings: bool
) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    current: list[int] = []

    def flush() -> None:
        nonlocal current
        if current:
            spans.append((current[0], current[-1]))
            current = []

    fence: str | None = None
    frontmatter = has_frontmatter(lines)
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        verbatim = False
        if frontmatter:
            if number > 1 and stripped in {"---", "..."}:
                frontmatter = False
            verbatim = True
        elif fence is not None:
            if closes_fence(stripped, fence):
                fence = None
            verbatim = True
        else:
            opened = FENCE_RE.match(line)
            if opened:
                fence = opened.group(1)
                verbatim = True
        if verbatim or number in excluded or not stripped or CONTEXT_BLOCK_RE.match(line):
            flush()
            continue
        if HEADING_RE.match(line):
            flush()
            if allow_headings:
                spans.append((number, number))
            continue
        if LIST_RE.match(line):
            flush()
        elif current:
            base = len(block_prefixes(lines[current[0] - 1])[1])
            if len(leading_indent(line)) >= base + INDENTED_CODE_DEPTH:
                flush()
                continue
        elif line.startswith(" " * INDENTED_CODE_DEPTH):
            continue
        current.append(number)
    flush()
    return spans


def comment_spans(
    lines: list[str], relative: str, excluded: set[int]
) -> list[tuple[int, int]]:
    syntax = comment_syntax(relative)
    if syntax is None:
        return []
    line_prefixes, block_pairs = syntax
    spans: list[tuple[int, int]] = []
    current: list[int] = []

    def flush() -> None:
        nonlocal current
        if current:
            spans.append((current[0], current[-1]))
            current = []

    open_close: tuple[str, str] | None = None
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if open_close is not None:
            if open_close[1] in line:
                open_close = None
            flush()
            continue
        opened = next(
            (pair for pair in block_pairs if stripped.startswith(pair[0])), None
        )
        if opened is not None:
            if opened[1] not in stripped[len(opened[0]) :]:
                open_close = opened
            flush()
            continue
        marker = next(
            (prefix for prefix in line_prefixes if stripped.startswith(prefix)), None
        )
        body = stripped[len(marker) :].strip() if marker is not None else ""
        if (
            marker is None
            or number in excluded
            or not body
            or (number == 1 and SHEBANG_RE.match(stripped))
            or PRAGMA_RE.match(body)
            or LIST_RE.match(body)
        ):
            flush()
            continue
        current.append(number)
    flush()
    return spans


def comment_prefix(line: str, line_prefixes: tuple[str, ...]) -> str:
    indent = leading_indent(line)
    body = line[len(indent) :]
    marker = next(prefix for prefix in line_prefixes if body.startswith(prefix))
    rest = body[len(marker) :]
    return indent + marker + rest[: len(rest) - len(rest.lstrip(" "))]


def strip_comment_marker(line: str, line_prefixes: tuple[str, ...]) -> str:
    stripped = line.strip()
    marker = next(
        (prefix for prefix in line_prefixes if stripped.startswith(prefix)), None
    )
    return stripped[len(marker) :].strip() if marker else stripped


def block_prefixes(line: str) -> tuple[str, str]:
    heading = HEADING_RE.match(line)
    if heading:
        return heading.group(0), heading.group(0)
    marker = LIST_RE.match(line)
    if marker:
        return marker.group(1), " " * len(marker.group(1))
    indent = leading_indent(line)
    return indent, indent


def target_blocks(
    lines: list[str],
    relative: str,
    kind: str,
    changed: list[tuple[int, int]] | None,
    excluded: set[int],
    allow_headings: bool,
) -> list[dict]:
    if kind == "code-comment":
        spans = comment_spans(lines, relative, excluded)
    else:
        spans = prose_spans(
            lines, excluded | structural_context(lines), allow_headings
        )
    if changed is not None:
        spans = [
            span
            for span in spans
            if any(start <= span[1] and span[0] <= end for start, end in changed)
        ]
    blocks: list[dict] = []
    for index, (start, end) in enumerate(spans, start=1):
        first_line = lines[start - 1]
        if kind == "code-comment":
            prefix = comment_prefix(first_line, comment_syntax(relative)[0])
            first_prefix, continuation, single = prefix, prefix, False
        else:
            first_prefix, continuation = block_prefixes(first_line)
            single = bool(HEADING_RE.match(first_line)) or (
                kind == "commit-message" and start == 1
            )
        blocks.append(
            {
                "id": index,
                "start": start,
                "end": end,
                "first_prefix": first_prefix,
                "prefix": continuation,
                "single": single,
            }
        )
    return blocks


def derive_wrap(lines: list[str], blocks: list[dict], kind: str) -> tuple[str, int]:
    if kind in SINGLE_LINE_KINDS:
        return "single-line", COMMIT_LINE_LIMIT
    if kind in WIDTH_LIMITED_KINDS:
        return "hard-wrap", COMMIT_LINE_LIMIT
    continued = [
        len(lines[number - 1])
        for block in blocks
        for number in range(block["start"], block["end"])
    ]
    if continued and max(continued) <= UNWRAPPED_MAX_WIDTH:
        return "hard-wrap", max(max(continued), MIN_WRAP_WIDTH)
    longest = max(
        (
            len(lines[number - 1])
            for block in blocks
            for number in range(block["start"], block["end"] + 1)
        ),
        default=0,
    )
    if longest > UNWRAPPED_MAX_WIDTH:
        return "single-line", 0
    return "hard-wrap", max(longest, MIN_WRAP_WIDTH)


def strip_marker(body: str, first_prefix: str) -> str:
    marker = first_prefix.strip()
    if not marker:
        return body
    if body == marker:
        return ""
    if body.startswith(marker + " "):
        return body[len(marker) + 1 :].lstrip()
    return body


def block_source_body(lines: list[str], block: dict, kind: str, relative: str) -> str:
    parts: list[str] = []
    for number in range(block["start"], block["end"] + 1):
        line = lines[number - 1]
        if kind == "code-comment":
            parts.append(strip_comment_marker(line, comment_syntax(relative)[0]))
        else:
            parts.append(line.strip())
    joined = " ".join(part for part in parts if part)
    return strip_marker(" ".join(joined.split()), block["first_prefix"])


def protected_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for pattern in (
        CODE_SPAN_RE,
        URL_RE,
        FLAG_RE,
        FILENAME_RE,
        VERSION_RE,
        NUMBER_RE,
        IDENTIFIER_RE,
    ):
        tokens.update(pattern.findall(text))
    for candidate in PATH_RE.findall(text):
        if "." in candidate or "-" in candidate or candidate.count("/") > 1:
            tokens.add(candidate)
    return tokens


def sentence_fragments(text: str) -> int:
    return len(LOWERCASE_SENTENCE_RE.findall(ABBREVIATION_RE.sub(" ", text)))


def lost_tokens(source_body: str, body: str) -> list[str]:
    spelled = set(re.findall(r"[a-z]+", body.lower()))
    return sorted(
        token
        for token in protected_tokens(source_body) - protected_tokens(body)
        if NUMBER_WORDS.get(token) not in spelled
    )


def wrap_block(target: dict, block: dict, body: str) -> list[str]:
    if not body:
        return []
    if block["single"] or target["wrap_mode"] == "single-line":
        return [block["first_prefix"] + body]
    wrapped = textwrap.wrap(
        body,
        width=target["wrap_width"],
        initial_indent=block["first_prefix"],
        subsequent_indent=block["prefix"],
        break_long_words=False,
        break_on_hyphens=False,
    )
    return wrapped or [block["first_prefix"] + body]


def plan_replacement(
    target: dict,
    block: dict,
    lines: list[str],
    replacement: str,
    owners: dict[str, set[int]],
) -> tuple[list[str] | None, str | None]:
    if any(character in replacement for character in "\r\n\0"):
        return None, "replacement contains a line separator"
    body = strip_marker(" ".join(replacement.split()), block["first_prefix"])
    source_body = block_source_body(lines, block, target["kind"], target["path"])
    if not body:
        if target["kind"] != "code-comment":
            return None, "replacement is empty"
        return [], None
    missing = lost_tokens(source_body, body)
    if missing:
        return None, "drops protected token " + ", ".join(missing)
    if sentence_fragments(body) > sentence_fragments(source_body):
        return None, "replacement splits a sentence"
    replacement_lines = wrap_block(target, block, body)
    width = target["wrap_width"]
    longest = max((len(line) for line in replacement_lines), default=0)
    if width and longest > width:
        return None, f"replacement runs {longest - width} columns past {width}"
    replaced = {
        normalized(line) for line in lines[block["start"] - 1 : block["end"]]
    }
    for line in replacement_lines:
        text = normalized(line)
        if len(text) < DUPLICATE_MIN_CHARS or text in replaced:
            continue
        line_owners = owners.get(text, set())
        if line_owners - {target["id"]}:
            return None, "replacement copies a line from another target"
        if target["id"] in line_owners:
            return None, "replacement duplicates a line the target already holds"
    return replacement_lines, None


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
                        "block_id": {"type": "integer"},
                        "replacement": {"type": "string"},
                    },
                    "required": ["target_id", "block_id", "replacement"],
                    "additionalProperties": False,
                },
            },
            "out_of_scope_notes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "target_id": {"type": "integer"},
                        "note": {"type": "string"},
                    },
                    "required": ["target_id", "note"],
                    "additionalProperties": False,
                },
            },
        },
        "required": [
            "bundle_hash",
            "status",
            "reviewed_target_ids",
            "reason",
            "edits",
            "out_of_scope_notes",
        ],
        "additionalProperties": False,
    }


def render_source(lines: list[str], blocks: list[dict], context: int = 2) -> str:
    if not blocks:
        return ""
    rendered: list[str] = []
    previous_end = 0
    for index, block in enumerate(blocks):
        next_start = (
            blocks[index + 1]["start"] if index + 1 < len(blocks) else len(lines) + 1
        )
        window_start = max(1, block["start"] - context)
        if previous_end and window_start > previous_end + 1:
            rendered.append("...")
        window_start = max(window_start, previous_end + 1)
        for number in range(window_start, block["start"]):
            rendered.append(f"ctx| {lines[number - 1]}")
        attributes = [f"block {block['id']}"]
        if block["first_prefix"]:
            attributes.append(f'prefix="{block["first_prefix"]}"')
        if block["single"]:
            attributes.append("single-line")
        rendered.append(f"[[{' '.join(attributes)}]]")
        rendered.extend(lines[block["start"] - 1 : block["end"]])
        rendered.append(f"[[/block {block['id']}]]")
        window_end = min(len(lines), block["end"] + context, next_start - 1)
        for number in range(block["end"] + 1, window_end + 1):
            rendered.append(f"ctx| {lines[number - 1]}")
        previous_end = max(block["end"], window_end)
    return "\n".join(rendered)


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


def draft_excluded(lines: list[str]) -> set[int]:
    return {
        number
        for number, line in enumerate(lines, start=1)
        if TRAILER_RE.match(line) or GENERATED_LINE_RE.match(line)
    }


def skip_reason(kind: str, changed: list[tuple[int, int]] | None) -> str:
    if kind == "code-comment":
        return "no-changed-comment-lines" if changed is not None else "no-comment-lines"
    return "no-changed-prose-blocks" if changed is not None else "no-reflowable-prose"


def prepare(args: argparse.Namespace) -> None:
    root = Path(args.patch_root).resolve()
    run_dir = Path(args.run_dir).resolve()
    if not root.is_dir() or not run_dir.is_dir():
        fail("Patch root and run directory must exist")
    mode_text, effort = MODES[args.mode]
    paths: list[str] = []
    changed_map: dict[str, list[tuple[int, int]] | None] = {}
    kind_map: dict[str, str] = {}
    skipped: list[dict[str, str]] = []
    inventory_before = inventory_hash(root, args.scope_kind)
    candidate_resolved: dict[str, Path] = {}
    candidate_hashes_before: dict[str, str] = {}
    notes = list(args.note or [])
    width_overrides: dict[str, int] = {}
    for relative, columns in args.wrap_width or []:
        if not columns.isdigit() or int(columns) < MIN_OVERRIDE_WIDTH:
            fail(
                f"--wrap-width columns must be an integer of at least "
                f"{MIN_OVERRIDE_WIDTH}: {columns}"
            )
        width_overrides[relative.replace("\\", "/")] = int(columns)
    heading_targets = {
        relative.replace("\\", "/") for relative in args.allow_headings or []
    }

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
            paths.append(relative)
            changed_map[relative] = ranges
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
            paths.append(relative)
            changed_map[relative] = None
            kind_map[relative] = (
                "code-comment" if file_kind == "code" else "documentation"
            )
    else:
        paths = list(args.target or [])
        for relative, start, end in args.line_range or []:
            if relative not in paths:
                paths.append(relative)
            changed_map.setdefault(relative, []).append((int(start), int(end)))
        for relative, declared_kind in args.target_kind or []:
            if declared_kind not in DRAFT_KINDS:
                fail(f"Unknown target kind: {declared_kind}")
            if args.scope_kind != "transient":
                fail("Target kinds apply to transient drafts only")
            if relative not in paths:
                paths.append(relative)
            kind_map[relative.replace("\\", "/")] = declared_kind

    paths = list(dict.fromkeys(path.replace("\\", "/") for path in paths))
    changed_map = {
        path.replace("\\", "/"): ranges for path, ranges in changed_map.items()
    }
    kind_map = {path.replace("\\", "/"): kind for path, kind in kind_map.items()}

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

    plan: dict[str, dict] = {}
    planned: list[str] = []
    for relative in paths:
        text = read_utf8(resolved[relative])
        lines = split_file_lines(text)
        changed = changed_map.get(relative)
        if changed:
            changed = merge_ranges(changed)
            if any(end > len(lines) for _, end in changed):
                fail(f"Editable range exceeds {relative}'s {len(lines)} lines")
        else:
            changed = None
        kind = kind_map.get(relative)
        excluded: set[int] = set()
        if args.scope_kind == "transient":
            kind = kind or "draft-prose"
            excluded = draft_excluded(lines)
        elif args.scope_kind == "named":
            file_kind = classify_path(relative)
            if file_kind == "excluded":
                fail(f"Named target is not auditable prose: {relative}")
            kind = "code-comment" if file_kind == "code" else "documentation"
        kind = kind or "documentation"
        allow_headings = relative in heading_targets
        every_block = target_blocks(
            lines, relative, kind, None, excluded, allow_headings
        )
        blocks = target_blocks(
            lines, relative, kind, changed, excluded, allow_headings
        )
        if not blocks:
            reason = skip_reason(kind, changed)
            if args.scope_kind == "repository-change-set":
                skipped.append(
                    {
                        "path": relative,
                        "reason": reason,
                        "sha256": hashes_before[relative],
                    }
                )
                continue
            fail(f"Named target has no auditable prose block: {relative} ({reason})")
        wrap_mode, wrap_width = derive_wrap(lines, every_block, kind)
        if relative in width_overrides:
            wrap_width = width_overrides[relative]
        plan[relative] = {
            "lines": lines,
            "kind": kind,
            "blocks": blocks,
            "wrap_mode": wrap_mode,
            "wrap_width": wrap_width,
        }
        planned.append(relative)
    paths = planned
    unmatched = sorted((set(width_overrides) | heading_targets) - set(paths))
    if unmatched:
        fail("No prepared target matches: " + ", ".join(unmatched))

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

    endings = {relative: line_ending(resolved[relative]) for relative in paths}

    def build(selected: list[str]) -> tuple[list[dict], list[str]]:
        targets: list[dict] = []
        source_sections: list[str] = []
        for target_id, relative in enumerate(selected, start=1):
            entry = plan[relative]
            target = {
                "id": target_id,
                "path": relative,
                "kind": entry["kind"],
                "blocks": entry["blocks"],
                "wrap_mode": entry["wrap_mode"],
                "wrap_width": entry["wrap_width"],
                "line_ending": endings[relative],
                "sha256": hashes_before[relative],
            }
            targets.append(target)
            if entry["wrap_mode"] == "hard-wrap":
                wrap_note = f"wrap: rewrapped to {entry['wrap_width']} columns"
            elif entry["wrap_width"]:
                wrap_note = (
                    f"wrap: one line per block, at most {entry['wrap_width']} columns"
                )
            else:
                wrap_note = "wrap: one line per block"
            source_sections.append(
                "\n".join(
                    [
                        f"===== TARGET {target_id} BEGIN =====",
                        f"path: {relative}",
                        f"artifact-kind: {entry['kind']}",
                        wrap_note,
                        f"editable-blocks: {len(entry['blocks'])}",
                        f"line-ending: {target['line_ending']}",
                        "content-lines:",
                        render_source(entry["lines"], entry["blocks"]),
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
        constraints = (
            ["<caller_constraints>", *notes, "</caller_constraints>"] if notes else []
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
                *constraints,
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
    batch_index = args.batch
    budget = args.max_input_chars or DEFAULT_MAX_INPUT_CHARS
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


def render_patch(
    edits: list, targets: list[dict], root: Path
) -> tuple[list[tuple[dict, str]], list[tuple[dict, int, str]]]:
    target_by_id = {target["id"]: target for target in targets}
    sources: dict[int, list[str]] = {}
    final_newlines: dict[int, bool] = {}
    for target in targets:
        text = read_utf8(resolve_target(root, target["path"]))
        sources[target["id"]] = split_file_lines(text)
        final_newlines[target["id"]] = text.endswith("\n")
    owners: dict[str, set[int]] = {}
    for owner_id, owner_lines in sources.items():
        for owner_line in owner_lines:
            text = normalized(owner_line)
            if len(text) >= DUPLICATE_MIN_CHARS:
                owners.setdefault(text, set()).add(owner_id)
    grouped: dict[int, list[dict]] = {}
    required_edit_keys = {"target_id", "block_id", "replacement"}
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != required_edit_keys:
            fail("Each edit must contain the exact replacement fields")
        if type(edit["target_id"]) is not int or edit["target_id"] not in target_by_id:
            fail(f"Edit references an unknown target ID: {edit['target_id']}")
        if type(edit["block_id"]) is not int:
            fail("Edit block IDs must be integers")
        if not isinstance(edit["replacement"], str):
            fail("Edit replacements must be strings")
        grouped.setdefault(edit["target_id"], []).append(edit)

    sections: list[tuple[dict, str]] = []
    dropped: list[tuple[dict, int, str]] = []
    accepted_any = False
    for target_id, target_edits in grouped.items():
        target = target_by_id[target_id]
        source_lines = sources[target_id]
        blocks = {block["id"]: block for block in target["blocks"]}
        accepted: dict[int, list[str]] = {}
        for edit in target_edits:
            block_id = edit["block_id"]
            block = blocks.get(block_id)
            if block is None:
                dropped.append((target, block_id, "unknown block id"))
                continue
            if block_id in accepted:
                dropped.append((target, block_id, "repeated block id"))
                continue
            if block["end"] > len(source_lines):
                dropped.append((target, block_id, "block exceeds the current file"))
                continue
            replacement_lines, reason = plan_replacement(
                target, block, source_lines, edit["replacement"], owners
            )
            if reason is not None:
                dropped.append((target, block_id, reason))
                continue
            accepted[block_id] = replacement_lines

        if not accepted:
            continue
        accepted_any = True
        updated_lines = list(source_lines)
        for block_id in sorted(
            accepted, key=lambda value: blocks[value]["start"], reverse=True
        ):
            block = blocks[block_id]
            updated_lines[block["start"] - 1 : block["end"]] = accepted[block_id]
        if updated_lines == source_lines:
            continue
        final_newline = final_newlines[target_id]
        last_line_deleted = any(
            blocks[block_id]["end"] == len(source_lines) and not accepted[block_id]
            for block_id in accepted
        )
        updated_final_newline = bool(updated_lines) and (
            final_newline or last_line_deleted
        )
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
                f"{target['path']} block {block_id} ({reason})"
                for target, block_id, reason in dropped
            )
            if accepted_any:
                fail(f"Surviving edits change nothing; dropped: {detail}")
            fail(f"Every proposed edit was dropped: {detail}")
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
    required_keys = {
        "bundle_hash",
        "status",
        "reviewed_target_ids",
        "reason",
        "edits",
        "out_of_scope_notes",
    }
    if not isinstance(result, dict) or set(result) != required_keys:
        fail("Result JSON has unexpected or missing fields")
    expected_hash = read_utf8(run_dir / "bundle-hash.txt").strip()
    target_by_id = {target["id"]: target for target in snapshot["targets"]}
    expected_ids = sorted(target_by_id)
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
    notes = result["out_of_scope_notes"]
    if not isinstance(status, str) or not isinstance(reason, str) or not isinstance(edits, list):
        fail("Result status and reason must be strings, and edits must be an array")
    if not isinstance(notes, list) or any(
        not isinstance(note, dict)
        or set(note) != {"target_id", "note"}
        or type(note["target_id"]) is not int
        or note["target_id"] not in target_by_id
        or not isinstance(note["note"], str)
        for note in notes
    ):
        fail("Out-of-scope notes must name a reviewed target and carry note text")

    def print_notes() -> None:
        for note in notes:
            target = target_by_id[note["target_id"]]
            print(f"NOTE\t{target['id']}\t{target['path']}\t{normalized(note['note'])}")

    if status == "blocked":
        if not reason or edits:
            fail("Blocked result must contain one reason and no edits")
        print(f"BLOCKED: {reason}")
        print_notes()
        raise SystemExit(3)
    if status == "no_changes":
        if reason or edits:
            fail("No-changes result must contain no reason or edits")
        print("NO_CHANGES")
        print_notes()
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
    patched_ids = {target["id"] for target, _ in sections}
    drops_by_target: dict[int, list[str]] = {}
    for target, block_id, drop_reason in dropped:
        drops_by_target.setdefault(target["id"], []).append(
            f"block {block_id}: {drop_reason}"
        )
    for target_id, reasons in drops_by_target.items():
        target = target_by_id[target_id]
        label = "PARTIAL" if target_id in patched_ids else "DROPPED"
        print(f"{label}\t{target_id}\t{target['path']}\t{'; '.join(reasons)}")
    print_notes()
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
    prepare_parser.add_argument("--note", action="append", metavar="TEXT")
    prepare_parser.add_argument("--wrap-width", action="append", nargs=2, metavar=("PATH", "COLUMNS"))
    prepare_parser.add_argument("--allow-headings", action="append", metavar="PATH")
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
