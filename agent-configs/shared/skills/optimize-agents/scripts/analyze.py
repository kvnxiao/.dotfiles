# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Measure a repository's agent-facing files per host and report limits and structural findings.

Token counts are estimates: bytes / 4, counting each run of four or more spaces, tabs, or dashes as four bytes. Exits 0 after reporting, including when it reports findings, and 1 when it cannot run.
"""

import argparse
import fnmatch
import functools
import io
import itertools
import json
import os
import re
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote as url_unquote

HOME = Path.home()
SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "target",
    "dist",
    "build",
    ".next",
    ".turbo",
}
SCRIPT_SUFFIXES = {
    ".py",
    ".sh",
    ".bash",
    ".fish",
    ".zsh",
    ".ps1",
    ".ts",
    ".mts",
    ".cts",
    ".js",
    ".mjs",
    ".cjs",
    ".toml",
    ".json",
    ".yaml",
    ".yml",
}
SCRIPT_NAMES = {"justfile", "Justfile", "Makefile"}
CLAUDE_MD_NAMES = ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md")

CODEX_PROJECT_DOC_MAX_BYTES = 32_768
CODEX_PLUGIN_SKILL_MAX_BYTES = 8_000
CODEX_DESCRIPTION_MAX_CHARS = 1_024
CODEX_LISTING_FALLBACK_CHARS = 8_000
CODEX_TOOL_OUTPUT_TOKENS = 10_000
CODEX_SHELL_OUTPUT_BYTES = CODEX_TOOL_OUTPUT_TOKENS * 4 * 6 // 5
CLAUDE_LISTING_MAX_CHARS = 1_536
CLAUDE_IMPORT_DEPTH = 4
GEMINI_IMPORT_DEPTH = 5
ANTIGRAVITY_RULE_MAX_BYTES = 24_000
ANTIGRAVITY_RULES_BUDGET_TOKENS = 20_000
ANTIGRAVITY_TRIGGERS = ("always_on", "model_decision", "glob", "manual")
ANTIGRAVITY_SKILL_FILTERS = ("include_only", "exclude", "inherits")
PAGE_LINES = 200
PI_READ_MAX_LINES = 2_000
PI_READ_MAX_BYTES = 51_200
MIN_REPEAT_WORDS = 12
MIN_IDENTICAL_CHARS = 200
MAX_ROWS = 30

HOSTS = ("claude", "codex", "pi", "gemini", "antigravity")
HOST_CODE = {"claude": "c", "codex": "x", "pi": "p", "gemini": "g", "antigravity": "a"}

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"(`+)(.+?)\1")
LINK = re.compile(
    r"(?<!!)\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^)]*[\"'])?\s*\)"
)
REF_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)>?")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
PATHLIKE = re.compile(
    r"^(?:~/|\.{1,2}/|/)?(?:[\w.@-]+/)*[\w.@-]+\.(?:md|toml|json|ya?ml|py|sh|fish|ps1|ts|mts|js|mjs)(?:#[\w-]+)?$"
)
STALE_CANDIDATE = re.compile(
    r"^(?:\.{1,2}/)+|^references/|^(?:\.agents|\.claude|\.codex|\.gemini|\.pi)/[^/]+/"
)
IMPORT = re.compile(r"(?:^|(?<=\s))@([~./\w][^\s,;)\]`'\"]*)")
LABELED_IMPORT = re.compile(r"@\[[^\]]*\]\(\s*<?([^)\s>]+)>?\s*\)")
FM_KEY = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
YAML_COMMENT = re.compile(r"(?:^|\s)#")
YAML_MAPPING = re.compile(r":(?:\s|$)")
YAML_QUOTED = ("'", '"', "|", ">", "[", "{")
INSTRUCTION_PATH = re.compile(
    r"~?[\w./-]*(?:(?:\.agents|\.claude|\.codex|\.gemini)/[\w./-]+\.(?:md|toml)|\.pi/(?:agent|skills|prompts)/[\w./-]+\.md|/(?:AGENTS|CLAUDE|GEMINI|SKILL)\.md)\b"
)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z`*\[(])")
BLOCK_START = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|#|>|\||<|```|~~~)")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|>)")
PADDING = re.compile(r"([ \t-])\1{3,}")
PLACEHOLDER = re.compile(r"^(?:[\w.@<>*-]+/)*[\w.@<>*-]+\.(?:md|toml|json|ya?ml|txt)$")

type Meta = dict[str, object]
type Listing = list[tuple[str, int, Path]]


def tokens(n_bytes: int) -> int:
    return (n_bytes + 3) // 4


def plural(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def weight(text: str) -> int:
    return len(PADDING.sub(r"\1\1\1\1", text).encode())


def line_count(text: str) -> int:
    return text.count("\n") + (text != "" and not text.endswith("\n"))


def home_path(raw: str) -> Path | None:
    return HOME / raw[2:] if raw.startswith("~/") else None


_text: dict[Path, str] = {}


def read(path: Path) -> str:
    key = path.resolve()
    if key not in _text:
        try:
            _text[key] = key.read_text(encoding="utf-8", errors="replace")
        except OSError:
            _text[key] = ""
    return _text[key]


def nbytes(path: Path) -> int:
    try:
        return path.resolve().stat().st_size
    except OSError:
        return 0


def cost(path: Path) -> int:
    return weight(read(path))


def unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str)]
    return []


def table(value: object) -> Meta:
    return {str(k): v for k, v in value.items()} if isinstance(value, dict) else {}


def merged(base: Meta, over: Meta) -> Meta:
    out = dict(base)
    for k, v in over.items():
        prev = out.get(k)
        both = isinstance(prev, dict) and isinstance(v, dict)
        out[k] = merged(table(prev), table(v)) if both else v
    return out


def strip_yaml_comment(value: str) -> str:
    quote = ""
    index = 0
    previous = ""
    while index < len(value):
        char = value[index]
        if quote:
            if quote == '"' and char == "\\":
                index += 2
                continue
            if char == quote:
                if quote == "'" and value[index : index + 2] == "''":
                    index += 2
                    continue
                quote = ""
        elif char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
        elif char in "\"'" and (not previous or previous in "[{,:"):
            quote = char
        if not char.isspace():
            previous = char
        index += 1
    return value.rstrip()


def frontmatter(text: str) -> tuple[Meta, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}, text
    entries: list[tuple[str, str, list[str]]] = []
    for line in lines[1:end]:
        m = FM_KEY.match(line)
        if m and not line[:1].isspace():
            entries.append((m.group(1), m.group(2).strip(), []))
        elif entries:
            entries[-1][2].append(line.strip())
    data: Meta = {}
    for key, inline, raw_block in entries:
        inline = strip_yaml_comment(inline)
        if inline[:1] in ("'", '"'):
            data[key] = unquote(strip_yaml_comment(" ".join([inline, *raw_block])))
            continue
        block_scalar = inline in ("|", "|-", "|+", ">", ">-", ">+")
        block = []
        for value in raw_block:
            if block_scalar:
                block.append(value)
            elif value.startswith("- "):
                block.append("- " + strip_yaml_comment(value[2:]))
            else:
                block.append(strip_yaml_comment(value))
        block = [b for b in block if b]
        if block and all(b.startswith("- ") for b in block) and inline == "":
            data[key] = [unquote(b[2:]) for b in block]
        elif inline.startswith("[") and inline.endswith("]"):
            data[key] = [unquote(s) for s in inline[1:-1].split(",") if s.strip()]
        elif inline in ("", "|", "|-", "|+", ">", ">-", ">+"):
            data[key] = " ".join(block)
        else:
            data[key] = unquote(" ".join([inline, *block]))
    return data, "\n".join(lines[end + 1 :])


def yaml_reserved(value: str) -> bool:
    return (
        value[:1] in ("@", "`", "*", "%", ",") or value[:2] in ("- ", "? ") or value in ("-", "?")
    )


def yaml_hazards(text: str) -> list[tuple[bool, str]]:
    """Return (fails_parsing, message) for each frontmatter construct strict YAML rejects or truncates."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return [(True, "frontmatter has no closing ---")]
    out: list[tuple[bool, str]] = []
    entries: list[tuple[int, str, str, list[str]]] = []
    for i, line in enumerate(lines[1:end], 2):
        indent = line[: len(line) - len(line.lstrip())]
        if "\t" in indent:
            out.append((True, f"line {i} indents with a tab"))
        m = FM_KEY.match(line)
        if m and not indent:
            entries.append((i, m.group(1), m.group(2).strip(), []))
        elif entries and not (not indent and line.startswith("#")):
            entries[-1][3].append(line.strip())
    keys: set[str] = set()
    for i, key, inline, block in entries:
        if key in keys:
            out.append((True, f"'{key}' (line {i}) repeats an earlier key"))
        keys.add(key)
        body = [b for b in block if b]
        if inline[:1] in YAML_QUOTED:
            continue
        comment_at = YAML_COMMENT.search(inline)
        head = (inline[: comment_at.start()] if comment_at else inline).strip()
        nested = [b for b in body if not b.startswith("#")]
        if not head and all(FM_KEY.match(b) or b == "-" or b.startswith("- ") for b in nested):
            for b in nested:
                m = FM_KEY.match(b)
                value = strip_yaml_comment((m.group(2) if m else b[1:]).strip())
                if value[:1] in YAML_QUOTED:
                    continue
                if yaml_reserved(value):
                    out.append(
                        (True, f"'{key}' (line {i}) has a nested value starting with '{value[0]}'")
                    )
                if m and YAML_MAPPING.search(value):
                    out.append((True, f"'{key}' (line {i}) has an unquoted ': ' in a nested value"))
            continue
        parts = [inline, *body] if head else body
        while parts and parts[0].startswith("#"):
            parts = parts[1:]
        while parts and parts[-1].startswith("#"):
            parts = parts[:-1]
        if not parts:
            continue
        if yaml_reserved(parts[0]):
            out.append((True, f"'{key}' (line {i}) starts with the reserved '{parts[0][0]}'"))
        comment = next((n for n, part in enumerate(parts) if YAML_COMMENT.search(part)), None)
        if comment is not None and comment < len(parts) - 1:
            out.append(
                (True, f"'{key}' (line {i}) has an unquoted ' #' before more lines of its value")
            )
        if any(YAML_MAPPING.search(strip_yaml_comment(part)) for part in parts):
            out.append((True, f"'{key}' (line {i}) has an unquoted ': ' inside a plain value"))
    return out


def truthy(value: object) -> bool:
    return str(value).strip().lower() == "true"


def prose_lines(text: str) -> list[str]:
    out: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        m = FENCE.match(line)
        if fence:
            out.append("")
            if m and m.group(1) == fence:
                fence = None
        elif m:
            fence = m.group(1)
            out.append("")
        else:
            out.append(line)
    return out


def load_toml(path: Path) -> Meta:
    if not path.is_file():
        return {}
    try:
        return tomllib.loads(read(path))
    except tomllib.TOMLDecodeError:
        return {}


def strip_jsonc(text: str) -> str:
    out: list[str] = []
    i, in_string = 0, False
    while i < len(text):
        c = text[i]
        if in_string:
            out.append(text[i : i + 2] if c == "\\" else c)
            in_string = c != '"'
            i += 2 if c == "\\" else 1
        elif c == '"':
            out.append(c)
            in_string = True
            i += 1
        elif text.startswith("//", i):
            end = text.find("\n", i)
            i = len(text) if end == -1 else end
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = len(text) if end == -1 else end + 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def load_json(path: Path, jsonc: bool = True) -> Meta:
    if not path.is_file():
        return {}
    text = read(path)
    try:
        return table(json.loads(strip_jsonc(text) if jsonc else text))
    except json.JSONDecodeError:
        return {}


def can_activate_skills(meta: Meta) -> bool:
    tools = [
        t.strip() for value in strings(meta.get("tools")) for t in value.split(",") if t.strip()
    ]
    return not tools or any(fnmatch.fnmatch("activate_skill", t) for t in tools)


@dataclass
class Skill:
    name: str
    path: Path
    description: str
    when_to_use: str
    meta: Meta
    hosts: set[str] = field(default_factory=set)


@dataclass
class Agent:
    host: str
    name: str
    path: Path
    description: str
    body: str
    meta: Meta


class Analysis:
    def __init__(self, root: Path, only: list[str], exclude: list[str]) -> None:
        self.root = root.resolve()
        self.only = [(self.root / p).resolve() for p in only]
        self.exclude = exclude
        self.always: dict[str, list[tuple[Path | None, str, int]]] = defaultdict(list)
        self.conditional: dict[str, list[tuple[Path, str]]] = defaultdict(list)
        self.listing: dict[str, dict[str, Listing]] = {
            h: {"skills": [], "agents": []} for h in HOSTS
        }
        self.delegates: list[tuple[str, str, int, str, bool]] = []
        self.limits: list[tuple[str, str, str]] = []
        self.unmeasured: list[str] = []
        self.codex_plugins: list[Path] = []
        self.max_rows = MAX_ROWS
        self.skills: dict[Path, Skill] = {}
        self.agents: list[Agent] = []
        self.repo_context: list[Path] = []
        self.repo_scripts: list[Path] = []
        self.gemini_names = ["GEMINI.md"]
        self.claude_reads_agents_md = True
        self.codex_home = Path(os.environ.get("CODEX_HOME", HOME / ".codex"))

    def in_repo(self, p: Path) -> bool:
        return p.resolve().is_relative_to(self.root)

    def rel(self, p: Path) -> str:
        rp = p.resolve()
        if rp.is_relative_to(self.root):
            return rp.relative_to(self.root).as_posix() or "."
        return self.tilde(rp)

    def tilde(self, p: Path) -> str:
        return "~/" + p.relative_to(HOME).as_posix() if p.is_relative_to(HOME) else p.as_posix()

    def show(self, p: Path) -> str:
        absolute = p if p.is_absolute() else self.root / p
        rp = absolute.resolve()
        if absolute.is_relative_to(self.root) or absolute == rp:
            return self.rel(absolute)
        shown = self.tilde(absolute)
        return f"{shown} -> {self.rel(rp)}" if rp.is_relative_to(self.root) else shown

    def excluded(self, p: Path) -> bool:
        if not self.in_repo(p):
            return True
        rel = self.rel(p)
        return any(
            fnmatch.fnmatch(rel, g) or rel.startswith(g.rstrip("/*") + "/") for g in self.exclude
        )

    def selected(self, *paths: Path) -> bool:
        repo = [p for p in paths if self.in_repo(p) and not self.excluded(p)]
        if not repo:
            return False
        return not self.only or any(p.resolve().is_relative_to(o) for p in repo for o in self.only)

    def limit(self, severity: str, host: str, message: str, *paths: Path) -> None:
        entry = (severity, host, message)
        if (not paths or self.selected(*paths)) and entry not in self.limits:
            self.limits.append(entry)

    def walk(self) -> None:
        names = {
            "AGENTS.md",
            "AGENTS.override.md",
            "CLAUDE.md",
            "CLAUDE.local.md",
            *self.gemini_names,
        }
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            base = Path(dirpath)
            for f in filenames:
                p = base / f
                if f in names:
                    self.repo_context.append(p)
                if f == "SKILL.md":
                    self.add_skill(p)
                if base.name == "agents" and f.endswith(".md") and ".agents" not in p.parts:
                    self.add_md_agent(p, "gemini" if ".gemini" in p.parts else "claude")
                if base.name == "agents" and f.endswith(".toml"):
                    self.add_codex_agent(p)
                if base.name == ".codex-plugin" and f == "plugin.json":
                    self.codex_plugins.append(base.parent.resolve())
                if (
                    not f.endswith(".md")
                    and (p.suffix in SCRIPT_SUFFIXES or f in SCRIPT_NAMES)
                    and nbytes(p) < 512_000
                ):
                    self.repo_scripts.append(p)

    def add_skill(self, skill_md: Path) -> Skill:
        key = skill_md.parent.resolve()
        skill = self.skills.get(key)
        if skill is None:
            meta, _ = frontmatter(read(skill_md))
            skill = Skill(
                name=str(meta.get("name") or skill_md.parent.name),
                path=skill_md,
                description=str(meta.get("description") or ""),
                when_to_use=str(meta.get("when_to_use") or ""),
                meta=meta,
            )
            self.skills[key] = skill
        return skill

    def add_md_agent(self, p: Path, host: str) -> Agent | None:
        key = p.resolve()
        existing = next(
            (ag for ag in self.agents if ag.host == host and ag.path.resolve() == key), None
        )
        if existing:
            return existing
        meta, body = frontmatter(read(p))
        if not (meta.get("name") and meta.get("description")) or p.name.startswith("_"):
            return None
        agent = Agent(host, str(meta["name"]), p, str(meta["description"]), body, meta)
        self.agents.append(agent)
        return agent

    def add_codex_agent(self, p: Path) -> Agent | None:
        key = p.resolve()
        existing = next((ag for ag in self.agents if ag.path.resolve() == key), None)
        if existing:
            return existing
        data = load_toml(p)
        name, instructions = data.get("name"), data.get("developer_instructions")
        if not isinstance(name, str) or not name.strip():
            return None
        if not isinstance(instructions, str) or not instructions:
            return None
        agent = Agent(
            "codex",
            name.strip(),
            p,
            str(data.get("description") or ""),
            instructions,
            data,
        )
        self.agents.append(agent)
        return agent

    def skill_dirs(self, root: Path) -> list[Path]:
        if not root.is_dir():
            return []
        return sorted(
            d / "SKILL.md"
            for d in root.iterdir()
            if (d / "SKILL.md").is_file() and d.name != ".system"
        )

    def list_agent(self, host: str, agent: Agent) -> None:
        self.listing[host]["agents"].append(
            (agent.name, len(agent.name) + len(agent.description) + 20, agent.path)
        )

    def load(self, host: str, p: Path, note: str = "") -> None:
        self.always[host].append((p, note, cost(p)))

    def imports(
        self,
        host: str,
        p: Path,
        depth: int,
        boundary: Path | None,
        seen: set[Path],
        misses: list[tuple[Path, int, str]] | None = None,
    ) -> None:
        if depth == 0:
            return
        for i, line in enumerate(prose_lines(read(p)), 1):
            for m in IMPORT.finditer(INLINE_CODE.sub(" ", line)):
                raw = m.group(1).rstrip(".")
                target = home_path(raw) if raw.startswith("~") else p.parent / raw
                if target is None or not target.is_file():
                    if misses is not None:
                        misses.append((p, i, raw))
                    continue
                rt = target.resolve()
                if rt in seen or (boundary and not rt.is_relative_to(boundary)):
                    continue
                seen.add(rt)
                self.load(host, target, f"import from {self.rel(p)}")
                self.imports(host, target, depth - 1, boundary, seen, misses)

    def git_boundary(self) -> Path | None:
        return next((d for d in (self.root, *self.root.parents) if (d / ".git").exists()), None)

    def claude(self) -> None:
        host = "claude"
        dirs = list(reversed((self.root, *self.root.parents)))
        candidates = [
            d / rel
            for d in dirs
            for rel in CLAUDE_MD_NAMES
            if (d / rel).is_file() and not (d == HOME and rel.startswith(".claude/"))
        ]
        self.claude_reads_agents_md = not candidates
        user = HOME / ".claude/CLAUDE.md"
        loaded = [user] if user.is_file() else []
        if candidates:
            loaded += candidates
        else:
            loaded += [
                d / rel
                for d in dirs
                for rel in ("AGENTS.md", ".claude/AGENTS.md")
                if (d / rel).is_file() and not (d == HOME and rel.startswith(".claude/"))
            ]
        seen = {p.resolve() for p in loaded}
        for p in loaded:
            self.load(host, p)
            self.imports(host, p, CLAUDE_IMPORT_DEPTH, None, seen)
        agents_md = self.root / "AGENTS.md"
        loaded_text = {read(p) for p, _, _ in self.always[host] if p}
        if (
            candidates
            and agents_md.is_file()
            and agents_md.resolve() not in seen
            and read(agents_md) not in loaded_text
        ):
            self.limit(
                "truncates",
                host,
                "AGENTS.md is not loaded: a CLAUDE.md exists, so Claude Code reads CLAUDE.md files only; import @AGENTS.md from it",
                agents_md,
            )
        settings = [
            load_json(HOME / ".claude/settings.json"),
            load_json(self.root / ".claude/settings.json"),
            load_json(self.root / ".claude/settings.local.json"),
        ]
        for rules_dir, scope in (
            (HOME / ".claude/rules", "user"),
            (self.root / ".claude/rules", "repo"),
        ):
            for p in sorted(walk_files(rules_dir, ".md")):
                paths = strings(frontmatter(read(p))[0].get("paths"))
                if paths:
                    self.conditional[host].append((p, "paths: " + ", ".join(paths)))
                else:
                    self.load(host, p, f"{scope} rule")
        style = next(
            (str(s["outputStyle"]) for s in reversed(settings) if s.get("outputStyle")), None
        )
        if style and style.lower() != "default":
            files = [
                *walk_files(self.root / ".claude/output-styles", ".md"),
                *walk_files(HOME / ".claude/output-styles", ".md"),
            ]
            match = next(
                (
                    p
                    for p in files
                    if str(frontmatter(read(p))[0].get("name", "")).lower() == style.lower()
                    or p.stem.lower() == style.lower()
                ),
                None,
            )
            if match:
                self.load(host, match, f"output style {style}")
            else:
                self.always[host].append(
                    (None, f"output style {style}: built-in or not found, not measured", 0)
                )
        enabled: Meta = {}
        for s in settings:
            enabled.update(table(s.get("enabledPlugins")))
        plugins = sorted(k for k, v in enabled.items() if v is True)
        if plugins:
            self.unmeasured.append(
                f"claude: {plural(len(plugins), 'enabled plugin')} ({', '.join(plugins)}): their skills, agents, commands, and MCP tools"
            )
        state = load_json(HOME / ".claude.json", jsonc=False)
        project = table(table(state.get("projects")).get(self.root.as_posix()))
        servers = {
            *table(state.get("mcpServers")),
            *table(project.get("mcpServers")),
            *table(load_json(self.root / ".mcp.json").get("mcpServers")),
        }
        if servers:
            self.unmeasured.append(
                f"claude: MCP servers ({', '.join(sorted(servers))}): their tool names and schemas"
            )
        overrides: dict[str, str] = {}
        for s in settings:
            overrides.update({k: str(v) for k, v in table(s.get("skillOverrides")).items()})
        by_name: dict[str, Skill] = {}
        for root in (self.root / ".claude/skills", HOME / ".claude/skills"):
            for p in self.skill_dirs(root):
                skill = self.add_skill(p)
                by_name[skill.name] = skill
        for root in (self.root / ".claude/skills", HOME / ".claude/skills"):
            for d in sorted(root.iterdir()) if root.is_dir() else []:
                nested = (
                    []
                    if not d.is_dir() or (d / "SKILL.md").is_file()
                    else [f for f in walk_files(d, ".md") if f.name == "SKILL.md"]
                )
                if nested:
                    self.unmeasured.append(
                        f"claude: {plural(len(nested), 'skill')} nested under {self.show(d)}"
                    )
        for skill in by_name.values():
            if truthy(skill.meta.get("disable-model-invocation")) or overrides.get(
                skill.name, ""
            ).lower() in ("user-invocable-only", "off", "disabled"):
                continue
            skill.hosts.add(host)
            text_len = len(skill.description) + len(skill.when_to_use)
            if text_len > CLAUDE_LISTING_MAX_CHARS:
                self.limit(
                    "truncates",
                    host,
                    f"{skill.name}: description and when_to_use are {text_len} chars; the listing keeps {CLAUDE_LISTING_MAX_CHARS}",
                    skill.path,
                )
            self.listing[host]["skills"].append(
                (
                    skill.name,
                    len(skill.name) + min(text_len, CLAUDE_LISTING_MAX_CHARS) + 4,
                    skill.path,
                )
            )
        agents: dict[str, Agent] = {}
        for root in (HOME / ".claude/agents", self.root / ".claude/agents"):
            for p in sorted(walk_files(root, ".md", recurse=False)):
                agent = self.add_md_agent(p, host)
                if agent:
                    agents[agent.name] = agent
        instructions = sum(
            n for p, note, n in self.always[host] if p and not note.startswith("output style")
        )
        for agent in agents.values():
            self.list_agent(host, agent)
            base = 0 if truthy(agent.meta.get("omitClaudeMd")) else instructions
            preload = strings(agent.meta.get("skills"))
            skill_bytes = sum(cost(by_name[n].path) for n in set(preload) if n in by_name)
            body = weight(agent.body)
            self.delegates.append(
                (
                    host,
                    agent.name,
                    body + base + skill_bytes,
                    f"body {tokens(body)} + instructions {tokens(base)} + preloaded skills {tokens(skill_bytes)}",
                    self.in_repo(agent.path),
                )
            )

    def codex(self) -> None:
        host = "codex"
        home = self.codex_home
        config = merged(
            load_toml(home / "config.toml"), load_toml(self.root / ".codex/config.toml")
        )
        fallbacks = strings(config.get("project_doc_fallback_filenames"))
        max_value = config.get("project_doc_max_bytes")
        max_bytes = (
            max_value
            if isinstance(max_value, int) and not isinstance(max_value, bool)
            else CODEX_PROJECT_DOC_MAX_BYTES
        )
        listed = table(config.get("skills")).get("include_instructions", True) is not False
        servers = sorted(table(config.get("mcp_servers")))
        if servers:
            self.unmeasured.append(
                f"codex: MCP servers ({', '.join(servers)}): their tool definitions"
            )
        user = next(
            (
                home / n
                for n in ("AGENTS.override.md", "AGENTS.md")
                if (home / n).is_file() and read(home / n).strip()
            ),
            None,
        )
        if user:
            self.load(host, user, "global")
        boundary = self.git_boundary() or self.root
        chain = [d for d in reversed((self.root, *self.root.parents)) if d.is_relative_to(boundary)]
        project_total, project_files = 0, []
        for d in chain:
            doc = next(
                (
                    d / n
                    for n in ("AGENTS.override.md", "AGENTS.md", *fallbacks)
                    if (d / n).is_file()
                ),
                None,
            )
            if doc:
                self.load(host, doc)
                project_total += nbytes(doc)
                project_files.append(doc)
        if project_total > max_bytes:
            self.limit(
                "truncates",
                host,
                f"project AGENTS.md files total {project_total} B; Codex keeps the first {max_bytes} B and drops the rest",
                *project_files,
            )
        loaded = {p.resolve() for p in project_files}
        for p in self.repo_context:
            if (
                p.name in ("AGENTS.md", "AGENTS.override.md", *fallbacks)
                and p.resolve() not in loaded
                and p.parent.resolve() != self.root
            ):
                self.conditional[host].append(
                    (p, f"when the working directory is under {self.rel(p.parent)}")
                )
        roots = [
            *(d / ".agents/skills" for d in chain),
            self.root / ".codex/skills",
            HOME / ".agents/skills",
            home / "skills",
        ]
        seen: set[Path] = set()
        total = 0
        for root in roots:
            for p in self.skill_dirs(root):
                if p.parent.resolve() in seen:
                    continue
                seen.add(p.parent.resolve())
                skill = self.add_skill(p)
                policy = p.parent / "agents/openai.yaml"
                if not listed or (
                    policy.is_file()
                    and re.search(r"allow_implicit_invocation:\s*false", read(policy))
                ):
                    continue
                skill.hosts.add(host)
                if len(skill.description) > CODEX_DESCRIPTION_MAX_CHARS:
                    self.limit(
                        "truncates",
                        host,
                        f"{skill.name}: description is {len(skill.description)} chars; Codex caps it at {CODEX_DESCRIPTION_MAX_CHARS}",
                        p,
                    )
                chars = (
                    len(
                        f"- {skill.name}: {skill.description[:CODEX_DESCRIPTION_MAX_CHARS]} (file: r0/{skill.name}/SKILL.md)"
                    )
                    + 1
                )
                total += chars
                self.listing[host]["skills"].append((skill.name, chars, skill.path))
        if total > CODEX_LISTING_FALLBACK_CHARS:
            self.limit(
                "risk",
                host,
                f"skill listing is {total} chars, over the {CODEX_LISTING_FALLBACK_CHARS}-char fallback budget. With a known context window the budget is 2% of it; over budget, Codex shortens descriptions, then drops skills",
            )
        agents: dict[str, Agent] = {}
        for root in (home / "agents", self.root / ".codex/agents"):
            for p in sorted(walk_files(root, ".toml")):
                agent = self.add_codex_agent(p)
                if agent:
                    agents[agent.name] = agent
        instructions = sum(n for p, _, n in self.always[host] if p)
        for agent in agents.values():
            self.list_agent(host, agent)
            body = weight(agent.body)
            role_skills = table(agent.meta.get("skills"))
            listing = total if role_skills.get("include_instructions", True) is not False else 0
            self.delegates.append(
                (
                    host,
                    agent.name,
                    body + instructions + listing,
                    f"developer_instructions {tokens(body)} + AGENTS.md {tokens(instructions)} + skill listing {tokens(listing)}",
                    self.in_repo(agent.path),
                )
            )

    def pi(self) -> None:
        host = "pi"
        agent_dir = HOME / ".pi/agent"
        names = ("AGENTS.override.md", "AGENTS.md", "AGENTS.MD", "CLAUDE.md", "CLAUDE.MD")
        user = next((agent_dir / n for n in names if (agent_dir / n).is_file()), None)
        if user:
            self.load(host, user, "global")
        for d in reversed((self.root, *self.root.parents)):
            doc = next((d / n for n in names if (d / n).is_file()), None)
            if not doc:
                continue
            self.load(host, doc)
            other = d / "CLAUDE.md"
            if (
                doc.name != "CLAUDE.md"
                and other.is_file()
                and other.resolve() != doc.resolve()
                and read(other) != read(doc)
            ):
                self.limit(
                    "truncates",
                    host,
                    f"{self.rel(other)} is not loaded: pi reads only the first context file per directory and picks {doc.name}",
                    other,
                )
        for n in ("SYSTEM.md", "APPEND_SYSTEM.md"):
            p = next((d / n for d in (self.root / ".pi", agent_dir) if (d / n).is_file()), None)
            if p:
                self.load(
                    host,
                    p,
                    "replaces the system prompt"
                    if n == "SYSTEM.md"
                    else "appended to the system prompt",
                )
        seen: set[Path] = set()
        for root in (
            agent_dir / "skills",
            HOME / ".agents/skills",
            self.root / ".pi/skills",
            self.root / ".agents/skills",
        ):
            for p in self.skill_dirs(root):
                if p.parent.resolve() in seen:
                    continue
                seen.add(p.parent.resolve())
                skill = self.add_skill(p)
                if truthy(skill.meta.get("disable-model-invocation")):
                    continue
                skill.hosts.add(host)
                self.listing[host]["skills"].append(
                    (
                        skill.name,
                        len(skill.name) + len(skill.description) + len(str(p.resolve())) + 70,
                        skill.path,
                    )
                )

    def gemini(self) -> None:
        host = "gemini"
        home = HOME / ".gemini"
        user_settings, repo_settings = (
            load_json(home / "settings.json"),
            load_json(self.root / ".gemini/settings.json"),
        )
        names: list[str] = []
        for s in (repo_settings, user_settings):
            names = strings(table(s.get("context")).get("fileName"))
            if names:
                break
        self.gemini_names = names or ["GEMINI.md"]
        disabled: set[str] = set()
        for s in (user_settings, repo_settings):
            disabled.update(strings(table(s.get("skills")).get("disabled")))
        boundary = self.git_boundary() or self.root
        dirs = [d for d in reversed((self.root, *self.root.parents)) if d.is_relative_to(boundary)]
        loaded = [home / n for n in self.gemini_names if (home / n).is_file()]
        loaded += [d / n for d in dirs for n in self.gemini_names if (d / n).is_file()]
        seen = {p.resolve() for p in loaded}
        misses: list[tuple[Path, int, str]] = []
        for p in loaded:
            self.load(host, p, "global" if p.parent == home else "")
            self.imports(
                host, p, GEMINI_IMPORT_DEPTH, boundary if self.in_repo(p) else None, seen, misses
            )
        servers = sorted(
            {k for s in (user_settings, repo_settings) for k in table(s.get("mcpServers"))}
        )
        if servers:
            self.unmeasured.append(
                f"gemini: MCP servers ({', '.join(servers)}): every tool declaration loads at session start"
            )
        configured = home.is_dir() or (self.root / ".gemini").exists() or len(loaded) > 0
        agents_md = self.root / "AGENTS.md"
        if configured and agents_md.is_file() and agents_md.resolve() not in seen:
            self.limit(
                "truncates",
                host,
                f"AGENTS.md is not loaded: context.fileName is {self.gemini_names}; add AGENTS.md to it or import it with @AGENTS.md",
                agents_md,
            )
        for p, i, raw in misses:
            if self.in_repo(p):
                self.limit(
                    "risk",
                    host,
                    f"{self.rel(p)}:{i}: '@{raw}' is parsed as an import that does not resolve",
                    p,
                )
        by_name: dict[str, Skill] = {}
        for root in (
            home / "skills",
            HOME / ".agents/skills",
            self.root / ".gemini/skills",
            self.root / ".agents/skills",
        ):
            for p in self.skill_dirs(root):
                skill = self.add_skill(p)
                by_name[skill.name] = skill
        for skill in by_name.values():
            if skill.name in disabled:
                continue
            skill.hosts.add(host)
            self.listing[host]["skills"].append(
                (
                    skill.name,
                    len(skill.name) + len(skill.description) + len(str(skill.path.resolve())) + 60,
                    skill.path,
                )
            )
        memory = sum(n for p, _, n in self.always[host] if p)
        listing = sum(chars for _, chars, _ in self.listing[host]["skills"])
        for root in (home / "agents", self.root / ".gemini/agents"):
            for p in sorted(walk_files(root, ".md", recurse=False)):
                agent = self.add_md_agent(p, host)
                if not agent:
                    continue
                self.list_agent(host, agent)
                body = weight(agent.body)
                skills = listing if can_activate_skills(agent.meta) else 0
                self.delegates.append(
                    (
                        host,
                        agent.name,
                        body + memory + skills,
                        f"body {tokens(body)} + memory {tokens(memory)} + skill listing {tokens(skills)}",
                        self.in_repo(agent.path),
                    )
                )

    def antigravity(self) -> None:
        host = "antigravity"
        home = HOME / ".gemini"
        config = home / "config"
        cli = home / "antigravity-cli"
        boundary = self.git_boundary() or self.root
        chain = [d for d in reversed((self.root, *self.root.parents)) if d.is_relative_to(boundary)]
        dots = [d / dot for d in chain for dot in (".agents", ".agent")]
        candidates = [
            *((d / n, "global") for d in (home, config) for n in ("AGENTS.md", "GEMINI.md")),
            *(
                (p, "global rule")
                for rules in (config / "rules", cli / "rules")
                for p in sorted(walk_files(rules, ".md", False))
            ),
            *((d / n, "") for d in chain for n in ("AGENTS.md", "GEMINI.md")),
            *((d / ".agents" / n, "") for d in chain for n in ("AGENTS.md", "GEMINI.md")),
            *((p, "rule") for dot in dots for p in sorted(walk_files(dot / "rules", ".md", False))),
        ]
        seen: set[Path] = set()
        documents: list[tuple[Path, str, bool]] = []
        for p, note in candidates:
            if not p.is_file() or p.resolve() in seen:
                continue
            active = True
            if note.endswith("rule"):
                trigger = str(frontmatter(read(p))[0].get("trigger") or "")
                if trigger not in ANTIGRAVITY_TRIGGERS or any(
                    fatal for fatal, _ in yaml_hazards(read(p))
                ):
                    self.limit(
                        "truncates",
                        host,
                        f"{self.rel(p)} is discarded: Antigravity drops a rule whose frontmatter fails strict YAML or lacks a trigger of {', '.join(ANTIGRAVITY_TRIGGERS)}",
                        p,
                    )
                    continue
                if trigger != "always_on":
                    self.conditional[host].append((p, f"trigger: {trigger}"))
                    active = False
                else:
                    note = f"always-on {note}"
            if active:
                seen.add(p.resolve())
            documents.append((p, note, active))
        shared_bytes = 0
        for p, note, active in documents:
            if active:
                self.load(host, p, note)
            inlined = self.antigravity_imports(host, p, seen, load_includes=active)
            if note.endswith("rule"):
                size = nbytes(p) + sum(nbytes(t) for t in inlined)
                if size > ANTIGRAVITY_RULE_MAX_BYTES:
                    self.limit(
                        "truncates",
                        host,
                        f"{self.rel(p)} is {size} B with its includes; Antigravity truncates each rule at {ANTIGRAVITY_RULE_MAX_BYTES} B",
                        p,
                    )
                if active:
                    shared_bytes += min(
                        cost(p) + sum(cost(t) for t in inlined), ANTIGRAVITY_RULE_MAX_BYTES
                    )
            elif note == "global":
                shared_bytes += cost(p)
        if tokens(shared_bytes) > ANTIGRAVITY_RULES_BUDGET_TOKENS:
            self.limit(
                "risk",
                host,
                f"global files and always-on rules total {tokens(shared_bytes)} tokens, over the {ANTIGRAVITY_RULES_BUDGET_TOKENS}-token budget they share; Antigravity demotes the largest rules to path-and-description pointers",
            )
        for p in self.repo_context:
            directory = p.parent.parent if p.parent.name == ".agents" else p.parent
            if (
                p.name in ("AGENTS.md", "GEMINI.md")
                and p.resolve() not in seen
                and directory.resolve() != self.root
            ):
                self.conditional[host].append(
                    (p, f"when a file under {self.rel(directory)} is read or edited")
                )
        mcp_files = (config / "mcp_config.json", *(d / ".agents/mcp_config.json" for d in chain))
        servers = sorted({s for f in mcp_files for s in table(load_json(f).get("mcpServers"))})
        if servers:
            self.unmeasured.append(
                f"antigravity: MCP servers ({', '.join(servers)}): their tool declarations"
            )
        roots = [
            *(dot / "skills" for dot in dots),
            config / "skills",
            cli / "skills",
            home / "antigravity/skills",
        ]
        filtered = False
        manifests = [
            (config / "skills.json", HOME),
            *((d / ".agents/skills.json", d) for d in chain),
        ]
        for manifest, base in manifests:
            data = load_json(manifest)
            entries = data.get("entries")
            filtered = filtered or any(k in data for k in ANTIGRAVITY_SKILL_FILTERS)
            for entry in entries if isinstance(entries, list) else []:
                item = table(entry)
                filtered = filtered or any(k in item for k in ANTIGRAVITY_SKILL_FILTERS)
                raw = str(item.get("path") or "")
                if raw.startswith("~"):
                    path = home_path(raw)
                elif raw:
                    path = base / raw if (base / raw).is_dir() else boundary / raw
                else:
                    path = None
                if path:
                    roots.append(path)
        if filtered:
            self.unmeasured.append(
                "antigravity: skills.json include_only, exclude, or inherits filters are not applied to the listing"
            )
        listed: set[Path] = set()
        for root in roots:
            for p in self.skill_dirs(root):
                if p.parent.resolve() in listed:
                    continue
                listed.add(p.parent.resolve())
                skill = self.add_skill(p)
                hazards = yaml_hazards(read(p))
                for fatal, message in hazards:
                    self.limit(
                        "truncates",
                        host,
                        f"{skill.name}: {message}"
                        + (
                            "; Antigravity likely drops a skill whose frontmatter fails strict YAML"
                            if fatal
                            else ""
                        ),
                        p,
                    )
                if any(fatal for fatal, _ in hazards):
                    continue
                skill.hosts.add(host)
                self.listing[host]["skills"].append(
                    (
                        skill.name,
                        len(skill.name)
                        + len(skill.description)
                        + len(str(skill.path.resolve()))
                        + 6,
                        skill.path,
                    )
                )
        if listed:
            self.unmeasured.append(
                "antigravity: skills, subagents, and MCP tools share a customization budget of unverified size; items over it are left out of the listing"
            )
        for root in (*(d / ".agents/agents" for d in chain), config / "agents"):
            files = walk_files(root, ".md", recurse=False)
            if root.is_dir():
                files += [d / "agent.md" for d in root.iterdir() if (d / "agent.md").is_file()]
            for p in sorted(files):
                agent = self.add_md_agent(p, host)
                if not agent or str(agent.meta.get("subagent")).strip().lower() == "false":
                    continue
                self.list_agent(host, agent)
                body = weight(agent.body)
                self.delegates.append(
                    (
                        host,
                        agent.name,
                        body,
                        f"body {tokens(body)}; inherits skills, rules, and subagents unless inheritCustomizations is off (not verified)",
                        self.in_repo(agent.path),
                    )
                )

    def antigravity_imports(
        self, host: str, p: Path, seen: set[Path], *, load_includes: bool
    ) -> list[Path]:
        inlined: list[Path] = []
        for i, line in enumerate(prose_lines(read(p)), 1):
            text = INLINE_CODE.sub(" ", line)
            for m in LABELED_IMPORT.finditer(text):
                raw = m.group(1)
                target = home_path(raw) if raw.startswith("~") else p.parent / raw
                if not (target and target.is_file()):
                    continue
                inlined.append(target)
                if load_includes and target.resolve() not in seen:
                    seen.add(target.resolve())
                    self.load(host, target, f"inlined from {self.rel(p)}")
            for m in IMPORT.finditer(text):
                raw = m.group(1).rstrip(".")
                target = home_path(raw) if raw.startswith("~") else p.parent / raw
                if target and target.is_file() and target.resolve() not in seen:
                    self.limit(
                        "risk",
                        host,
                        f"{self.rel(p)}:{i}: '@{raw}' is a path reference in Antigravity, not an import; write @[{raw}]({raw}) to inline it",
                        p,
                    )
        return inlined

    def nested_context(self) -> None:
        loaded = {
            p.resolve(): p for h in HOSTS if h != "antigravity" for p, _, _ in self.always[h] if p
        }
        claude_real = {p.resolve(): p for p, _, _ in self.always["claude"] if p}
        claude_paths = {Path(os.path.normpath(p)) for p, _, _ in self.always["claude"] if p}
        for p in self.repo_context:
            directory = p.parent.parent if p.parent.name == ".claude" else p.parent
            if directory.resolve() == self.root:
                continue
            twin = loaded.get(p.resolve())
            has_claude_md = any((directory / n).is_file() for n in CLAUDE_MD_NAMES)
            if Path(os.path.normpath(p)) not in claude_paths and (
                p.name in ("CLAUDE.md", "CLAUDE.local.md")
                or (p.name == "AGENTS.md" and self.claude_reads_agents_md and not has_claude_md)
            ):
                note = f"when Claude reads a file under {self.rel(directory)}"
                if p.resolve() in claude_real:
                    note += f"; same file as {self.show(claude_real[p.resolve()])}, loaded again"
                self.conditional["claude"].append((p, note))
            if twin:
                continue
            if p.name in self.gemini_names:
                self.conditional["gemini"].append(
                    (p, f"when a file tool touches {self.rel(p.parent)}")
                )


def walk_files(root: Path, suffix: str, recurse: bool = True) -> list[Path]:
    if not root.is_dir():
        return []
    if not recurse:
        return [p for p in root.iterdir() if p.is_file() and p.name.endswith(suffix)]
    out: list[Path] = []
    visited: set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=True):
        real = Path(dirpath).resolve()
        if real in visited:
            dirnames[:] = []
            continue
        visited.add(real)
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        out += [Path(dirpath) / f for f in filenames if f.endswith(suffix)]
    return out


@functools.cache
def anchors(path: Path) -> set[str]:
    seen: dict[str, int] = defaultdict(int)
    out: set[str] = set()
    for line in prose_lines(read(path)):
        m = HEADING.match(line)
        if not m:
            continue
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", m.group(1).replace("`", ""))
        slug = re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")
        n = seen[slug]
        seen[slug] += 1
        out.add(slug if n == 0 else f"{slug}-{n}")
    out.update(re.findall(r"<a\s+(?:name|id)=\"([^\"]+)\"", read(path)))
    return out


def resolve(base: Path, raw: str, root: Path) -> Path | None:
    raw = url_unquote(raw)
    if raw.startswith("~"):
        p = home_path(raw)
        return p if p and p.exists() else None
    for candidate in [Path(raw)] if raw.startswith("/") else [base / raw, root / raw]:
        if candidate.exists():
            return candidate
    return None


@dataclass
class Edge:
    src: Path
    line: int
    dst: Path | None
    raw: str
    anchor: str | None
    kind: str


@functools.cache
def edges_of(a: Analysis, p: Path) -> list[Edge]:
    out: list[Edge] = []
    for i, line in enumerate(prose_lines(read(p)), 1):
        stripped = INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line)
        for raw in [*LINK.findall(stripped), *REF_DEF.findall(stripped)]:
            if "://" in raw or raw.startswith(("mailto:", "data:")):
                continue
            target, _, anchor = raw.partition("#")
            dst = p if not target else resolve(p.parent, target, p.parent)
            out.append(Edge(p, i, dst, raw, anchor or None, "link"))
        for m in INLINE_CODE.finditer(line):
            token = m.group(2).strip()
            if PATHLIKE.match(token):
                target, _, anchor = token.partition("#")
                dst = resolve(p.parent, target, a.root)
                out.append(
                    Edge(
                        p,
                        i,
                        dst,
                        token,
                        anchor or None,
                        "mention"
                        if dst or (target.endswith(".md") and STALE_CANDIDATE.match(target))
                        else "name",
                    )
                )
    return out


def sentences(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in prose_lines(text):
        if not line.strip() or HEADING.match(line) or line.lstrip().startswith("|"):
            if current:
                blocks.append(" ".join(current))
            current = []
            continue
        if BLOCK_START.match(line) and current:
            blocks.append(" ".join(current))
            current = []
        current.append(re.sub(r"^\s*(?:[-*+]|\d+[.)]|>)\s+", "", line).strip())
    if current:
        blocks.append(" ".join(current))
    return [s for b in blocks for s in SENTENCE_SPLIT.split(b)]


def normalize(sentence: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*_]", "", sentence)).strip().rstrip(".:;").lower()


def unwrapped_lines(text: str) -> int:
    count, prev_prose = 0, False
    fence: str | None = None
    for line in text.splitlines():
        m = FENCE.match(line)
        if fence or m:
            count += 1
            prev_prose = False
            if not fence and m:
                fence = m.group(1)
            elif fence and m and m.group(1) == fence:
                fence = None
            continue
        is_prose = bool(line.strip()) and not BLOCK_START.match(line)
        if not (is_prose and prev_prose):
            count += 1
        prev_prose = is_prose or bool(LIST_ITEM.match(line))
    return count


def tarjan(graph: dict[Path, set[Path]]) -> list[list[Path]]:
    index: dict[Path, int] = {}
    low: dict[Path, int] = {}
    stack: list[Path] = []
    on_stack: set[Path] = set()
    out: list[list[Path]] = []
    counter = 0
    for start in graph:
        if start in index:
            continue
        work = [(start, iter(sorted(graph.get(start, ()))))]
        index[start] = low[start] = counter
        counter += 1
        stack.append(start)
        on_stack.add(start)
        while work:
            node, children = work[-1]
            child = next(children, None)
            if child is not None:
                if child not in index:
                    index[child] = low[child] = counter
                    counter += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(sorted(graph.get(child, ())))))
                elif child in on_stack:
                    low[node] = min(low[node], index[child])
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                component: list[Path] = []
                while True:
                    item = stack.pop()
                    on_stack.discard(item)
                    component.append(item)
                    if item == node:
                        break
                if len(component) > 1:
                    out.append(sorted(component))
    return out


def capped(a: Analysis, rows: list[str], noun: str = "more") -> list[str]:
    if not a.max_rows or len(rows) <= a.max_rows:
        return rows
    return [*rows[: a.max_rows], f"... {len(rows) - a.max_rows} {noun} (--all prints them)"]


def sections(text: str) -> list[tuple[str, int, int]]:
    parts: list[tuple[str, int, list[str]]] = [("(before the first heading)", 1, [])]
    for i, (raw, prose) in enumerate(
        zip(text.splitlines(keepends=True), prose_lines(text), strict=True), 1
    ):
        if HEADING.match(prose):
            parts.append((prose.strip(), i, []))
        parts[-1][2].append(raw)
    return [(h, line, weight("".join(body))) for h, line, body in parts if "".join(body).strip()]


def read_limits(a: Analysis, p: Path) -> None:
    text = read(p)
    lines, size = line_count(text), nbytes(p)
    if size > CODEX_SHELL_OUTPUT_BYTES:
        a.limit(
            "risk",
            "codex",
            f"{a.rel(p)} is {size} B; Codex cuts a shell output over about {CODEX_SHELL_OUTPUT_BYTES} B to its head and tail",
            p,
        )
    if lines > PAGE_LINES:
        a.limit(
            "risk",
            "codex",
            f"{a.rel(p)} has {lines} lines (~{unwrapped_lines(text)} unwrapped); Codex models page by line ranges of about {PAGE_LINES}",
            p,
        )
    if lines > PI_READ_MAX_LINES or size > PI_READ_MAX_BYTES:
        a.limit(
            "risk",
            "pi",
            f"{a.rel(p)} has {lines} lines and {size} B; one pi read returns at most {PI_READ_MAX_LINES} lines or {PI_READ_MAX_BYTES // 1024} KB and gives the offset to continue",
            p,
        )


def placeholders(a: Analysis, nodes: set[Path]) -> list[str]:
    found: dict[str, tuple[set[Path], set[Path], list[str]]] = {}
    for p in sorted(nodes):
        if not a.selected(p):
            continue
        for i, line in enumerate(prose_lines(read(p)), 1):
            for m in INLINE_CODE.finditer(line):
                token = m.group(2).strip()
                if not ("<" in token or "*" in token) or not PLACEHOLDER.match(token):
                    continue
                pattern = re.sub(r"<[^<>/]+>", "*", token)
                if ".." in pattern or "**" in pattern or "<" in pattern or ">" in pattern:
                    continue
                matches, bases, refs = found.setdefault(pattern, (set(), set(), []))
                for base in {a.root, p.parent} - bases:
                    bases.add(base)
                    matches.update(
                        q.resolve()
                        for q in base.glob(pattern)
                        if q.is_file()
                        and not a.excluded(q)
                        and SKIP_DIRS.isdisjoint(a.rel(q).split("/"))
                    )
                refs.append(f"{a.rel(p)}:{i}")
    rows: list[str] = []
    for pattern, (matches, _, refs) in sorted(found.items()):
        where = ", ".join(refs[:3]) + (f" and {len(refs) - 3} more" if len(refs) > 3 else "")
        if not matches:
            rows.append(f"{pattern}  no files  <- {where}")
            continue
        sized = sorted(((tokens(cost(q)), q) for q in matches), key=lambda r: -r[0])
        top, largest = sized[0]
        rows.append(
            f"{pattern}  {plural(len(matches), 'file')}, {sum(t for t, _ in sized)} tokens; largest {a.rel(largest)} ({top} tokens, {line_count(read(largest))} lines)  <- {where}"
        )
        for q in sorted(matches):
            read_limits(a, q)
    return capped(a, rows)


def report(a: Analysis) -> list[str]:
    out = [
        f"# optimize-agents analyzer: {a.root.as_posix()}",
        "Tokens are estimates: bytes / 4, counting each run of four or more spaces, tabs, or dashes as four bytes. Scope: repo = editable here; user = outside the repository.",
        "",
    ]
    if a.exclude:
        out.append(f"Excluded from detectors, still counted in costs: {', '.join(a.exclude)}")
    if a.only:
        out.append(f"Findings limited to: {', '.join(a.rel(p) for p in a.only)}")
    present = [
        d
        for d in (".claude", ".codex", ".agents", ".agent", ".gemini", ".pi")
        if (a.root / d).exists()
    ]
    present += [n for n in ("AGENTS.md", "CLAUDE.md", "GEMINI.md") if (a.root / n).is_file()]
    user_dirs = [
        a.tilde(d)
        for d in (
            HOME / ".claude",
            a.codex_home,
            HOME / ".pi/agent",
            HOME / ".gemini",
        )
        if d.is_dir()
    ]
    out += [
        f"Host files at the root: {', '.join(present) or 'none'}",
        f"User host directories: {', '.join(user_dirs) or 'none'}",
        "",
        "## Session start per host",
        "host          total    repo    user   skills listed  agents listed",
    ]
    for h in HOSTS:
        repo = sum(n for p, _, n in a.always[h] if p and a.in_repo(p))
        user = sum(n for p, _, n in a.always[h] if p and not a.in_repo(p))
        for kind in ("skills", "agents"):
            for _, chars, path in a.listing[h][kind]:
                if a.in_repo(path):
                    repo += chars
                else:
                    user += chars
        out.append(
            f"{h:<13}{tokens(repo + user):>6}{tokens(repo):>8}{tokens(user):>8}   {len(a.listing[h]['skills']):>13}  {len(a.listing[h]['agents']):>13}"
        )
    out += ["", "## Not measured", *(a.unmeasured or ["none"])]
    out += ["", "## Always loaded", "hosts  tokens  file"]
    rows: dict[tuple[str, str], set[str]] = defaultdict(set)
    sizes: dict[tuple[str, str], int] = {}
    for h in HOSTS:
        for p, note, n in a.always[h]:
            key = (a.show(p) if p else "-", note)
            rows[key].add(HOST_CODE[h])
            sizes[key] = n
    for (shown, note), hosts in sorted(rows.items(), key=lambda kv: -sizes[kv[0]]):
        out.append(
            f"{''.join(sorted(hosts)):<5}{tokens(sizes[(shown, note)]):>8}  {shown}{'  (' + note + ')' if note else ''}"
        )
    out += ["", "## Sections of always-loaded repository files", "tokens  line  heading"]
    shown_files: set[Path] = set()
    section_rows: list[str] = []
    for h in HOSTS:
        for p, _, _ in a.always[h]:
            if not p or not a.in_repo(p) or p.resolve() in shown_files or not a.selected(p):
                continue
            shown_files.add(p.resolve())
            parts = sections(read(p))
            if len(parts) > 1:
                section_rows.append(a.rel(p))
                section_rows += capped(
                    a, [f"{tokens(n):>6}  {line:>4}  {head}" for head, line, n in parts]
                )
    out += section_rows or ["none"]
    out += ["", "## Loaded on a trigger"]
    cond = [(h, p, note) for h in HOSTS for p, note in a.conditional[h]]
    out += [
        f"{HOST_CODE[h]}  {tokens(cost(p)):>6}  {a.show(p)}  ({note})" for h, p, note in cond
    ] or ["none"]
    out += ["", "## Delegate start", "host         tokens  scope  agent  (parts)"]
    out += [
        f"{h:<13}{tokens(n):>6}  {'repo' if in_repo else 'user':<5}  {name}  ({parts})"
        for h, name, n, parts, in_repo in a.delegates
    ] or ["none"]
    listing_chars: dict[Path, int] = defaultdict(int)
    for h in HOSTS:
        for _, chars, path in a.listing[h]["skills"]:
            listing_chars[path.resolve()] = max(listing_chars[path.resolve()], chars)
    out += [
        "",
        "## Skills (c=claude x=codex p=pi g=gemini a=antigravity listed for the model; listing = its largest listing entry; linked = files its SKILL.md links)",
        "listed  listing   body  linked (n)  scope  skill",
    ]
    for skill in sorted(a.skills.values(), key=lambda s: (not a.in_repo(s.path), s.name)):
        linked = {
            e.dst.resolve()
            for e in edges_of(a, skill.path)
            if e.kind == "link"
            and e.dst
            and e.dst.is_file()
            and e.dst.resolve() != skill.path.resolve()
        }
        hosts = "".join(HOST_CODE[h] for h in HOSTS if h in skill.hosts) or "-"
        listing = tokens(listing_chars[skill.path.resolve()])
        out.append(
            f"{hosts:<6}{listing:>9}{tokens(cost(skill.path)):>7}{tokens(sum(cost(p) for p in linked)):>8} ({len(linked):>2})  {'repo' if a.in_repo(skill.path) else 'user'}  {skill.name}  {a.show(skill.path)}"
        )
    always = {p.resolve() for h in HOSTS for p, _, _ in a.always[h] if p and a.in_repo(p)}
    nodes, graph, edges = collect_nodes(a, always)
    for p in sorted(nodes - always):
        if not a.selected(p):
            continue
        if (
            p.name == "SKILL.md"
            and nbytes(p) > CODEX_PLUGIN_SKILL_MAX_BYTES
            and any(p.is_relative_to(r) for r in a.codex_plugins)
        ):
            a.limit(
                "truncates",
                "codex",
                f"{a.rel(p)} is {nbytes(p)} B; Codex injects the first {CODEX_PLUGIN_SKILL_MAX_BYTES} B of a plugin skill",
                p,
            )
        read_limits(a, p)
    out += ["", "## Files named by placeholder paths", *(placeholders(a, nodes) or ["none"])]
    out += ["", "## Limits"]
    out += [
        f"{sev:<10}{host:<13}{msg}"
        for sev, host, msg in sorted(a.limits, key=lambda r: r[0] != "truncates")
    ] or ["none"]
    out += structure(a, always, nodes, graph, edges)
    return out


def collect_nodes(
    a: Analysis, always: set[Path]
) -> tuple[set[Path], dict[Path, set[Path]], list[Edge]]:
    seeds = set(always)
    seeds |= {p.resolve() for h in HOSTS for p, _ in a.conditional[h] if a.in_repo(p)}
    for skill in a.skills.values():
        if a.in_repo(skill.path):
            seeds |= {p.resolve() for p in walk_files(skill.path.parent, ".md")}
    seeds |= {
        ag.path.resolve() for ag in a.agents if a.in_repo(ag.path) and ag.path.suffix == ".md"
    }
    seeds |= {p.resolve() for p in walk_files(a.root / ".claude/output-styles", ".md")}
    nodes = set(seeds)
    for p in seeds:
        for e in edges_of(a, p):
            if e.dst and e.dst.is_file() and e.dst.suffix == ".md" and a.in_repo(e.dst):
                nodes.add(e.dst.resolve())
    edges = [e for p in sorted(nodes) for e in edges_of(a, p)]
    graph: dict[Path, set[Path]] = defaultdict(set)
    for e in edges:
        if e.kind == "link" and e.dst and e.dst.is_file():
            dst = e.dst.resolve()
            if dst in nodes and dst != e.src:
                graph[e.src].add(dst)
    return nodes, graph, edges


def structure(
    a: Analysis,
    always: set[Path],
    nodes: set[Path],
    graph: dict[Path, set[Path]],
    edges: list[Edge],
) -> list[str]:
    entries = {s.path.resolve() for s in a.skills.values()} | {ag.path.resolve() for ag in a.agents}
    skill_dirs = sorted(
        (s.path.parent.resolve() for s in a.skills.values()), key=lambda d: -len(d.parts)
    )

    def depth(p: Path) -> int:
        return 0 if p in always else 1 if p in entries else 2

    def owner(p: Path) -> Path | None:
        return next((d for d in skill_dirs if p.is_relative_to(d)), None)

    out = ["", "## Link cycles (each line is one set of files that reach each other through links)"]
    cycles = [c for c in tarjan(graph) if a.selected(*c)]
    out += [f"{len(c)} files: " + ", ".join(a.rel(p) for p in c) for c in cycles] or ["none"]
    upward: list[str] = []
    reach: list[str] = []
    broken: list[str] = []
    unresolved: list[str] = []
    for e in edges:
        src = e.src.resolve()
        if not a.selected(src):
            continue
        where = f"{a.rel(src)}:{e.line}"
        if e.kind == "link" and not e.dst:
            broken.append(f"{where}  {e.raw}  (missing file)")
            continue
        if e.kind == "mention" and not e.dst:
            unresolved.append(f"{where}  {e.raw}")
            continue
        if not e.dst:
            continue
        dst = e.dst.resolve()
        if e.anchor and dst.suffix == ".md" and e.anchor not in anchors(dst):
            broken.append(f"{where}  {e.raw}  (missing anchor)")
        if e.kind == "link" and dst != src and depth(src) > depth(dst):
            upward.append(f"{where}  -> {a.rel(dst)}")
        so, do = owner(src), owner(dst)
        if do and so != do and dst.name != "SKILL.md" and e.kind in ("link", "mention"):
            reach.append(f"{where}  -> {a.rel(dst)}  ({e.kind})")
    for title, rows in (
        ("Upward links", upward),
        ("Reach-ins to another skill's files", reach),
        ("Broken links and anchors", broken),
        ("Unresolved backtick paths", unresolved),
    ):
        out += ["", f"## {title}", *(capped(a, rows) or ["none"])]
    out += ["", "## Identical files (copies, not links)"]
    by_text: dict[str, list[Path]] = defaultdict(list)
    for p in sorted(nodes):
        if a.in_repo(p) and not a.excluded(p) and len(read(p)) >= MIN_IDENTICAL_CHARS:
            by_text[read(p)].append(p)
    mirrors: dict[tuple[str, ...], list[tuple[str, int]]] = defaultdict(list)
    for g in by_text.values():
        if len(g) < 2 or not a.selected(*g):
            continue
        parts = [a.rel(p).split("/") for p in g]
        n = 1
        while all(len(r) > n for r in parts) and len({tuple(r[-n - 1 :]) for r in parts}) == 1:
            n += 1
        same_name = len({r[-1] for r in parts}) == 1
        key = tuple("/".join(r[:-n] if same_name else r) or "." for r in parts)
        mirrors[key].append(("/".join(parts[0][-n:]) if same_name else "", tokens(cost(g[0]))))
    copies: list[str] = []
    for key, files in mirrors.items():
        names = [name for name, _ in files if name]
        listed = ", ".join(names[:8]) + (f" and {len(names) - 8} more" if len(names) > 8 else "")
        copies.append(
            f"{' = '.join(key)}: {plural(len(files), 'identical file')}, ~{sum(t for _, t in files)} tokens per copy"
            + (f": {listed}" if listed else "")
        )
    out += capped(a, copies) or ["none"]
    out += [
        "",
        "## Repeated sentences (each set of identical files counts once)",
        *repeated(a, nodes),
    ]
    out += ["", "## Files with the same set of referrers"]
    referrers: dict[Path, set[Path]] = defaultdict(set)
    for src, dsts in graph.items():
        for dst in dsts:
            referrers[dst].add(src)
    groups: dict[frozenset[Path], list[Path]] = defaultdict(list)
    for dst, refs in referrers.items():
        if len(refs) >= 2 and dst not in always and dst not in entries and a.selected(dst):
            groups[frozenset(refs)].append(dst)
    rows = [
        f"{', '.join(a.rel(p) for p in sorted(g))}  <- {len(refs)} files: {', '.join(a.rel(p) for p in sorted(refs))}"
        for refs, g in groups.items()
        if len(g) >= 2
    ]
    out += rows or ["none"]
    out += ["", "## Skills that name other skills"]
    names = {s.name for s in a.skills.values()}
    mentions: dict[str, set[str]] = defaultdict(set)
    for skill in a.skills.values():
        if not a.selected(skill.path):
            continue
        text = "\n".join(read(p) for p in walk_files(skill.path.parent, ".md"))
        for other in names - {skill.name}:
            if re.search(rf"(?:`|\$|/)({re.escape(other)})(?:`|\b)", text):
                mentions[skill.name].add(other)
    out += [
        f"{name} -> "
        + ", ".join(
            sorted(o + (" (mutual)" if name in mentions.get(o, set()) else "") for o in others)
        )
        for name, others in sorted(mentions.items())
    ] or ["none"]
    out += ["", "## Delegates across hosts", *delegates_across(a)]
    out += ["", "## Instruction paths in scripts and config", *script_paths(a)]
    return out


def repeated(a: Analysis, nodes: set[Path]) -> list[str]:
    texts: dict[Path, str] = {}
    seen: set[str] = set()
    for p in sorted(nodes):
        if not a.in_repo(p) or a.excluded(p) or read(p) in seen:
            continue
        if len(read(p)) >= MIN_IDENTICAL_CHARS:
            seen.add(read(p))
        texts[p] = read(p)
    for ag in a.agents:
        if ag.host == "codex" and a.in_repo(ag.path) and not a.excluded(ag.path):
            texts[ag.path.resolve()] = ag.body
    agent_names = {ag.path.resolve(): ag.name for ag in a.agents}
    found: dict[str, tuple[str, set[Path]]] = {}
    for p, text in texts.items():
        for s in sentences(text):
            if len(s.split()) >= MIN_REPEAT_WORDS:
                found.setdefault(normalize(s), (s, set()))[1].add(p)
    ranked: list[tuple[int, int, str]] = []
    for s, files in found.values():
        if len(files) < 2 or not a.selected(*files):
            continue
        if all(f in agent_names for f in files) and len({agent_names[f] for f in files}) == 1:
            continue
        excerpt = s[:110] + ("..." if len(s) > 110 else "")
        ranked.append(
            (
                len(files),
                len(s),
                f'{len(files)} files  "{excerpt}"  {", ".join(a.rel(f) for f in sorted(files))}',
            )
        )
    ranked.sort(key=lambda r: (-r[0], -r[1]))
    return capped(a, [r[2] for r in ranked]) or ["none"]


def delegates_across(a: Analysis) -> list[str]:
    repo_agents = [ag for ag in a.agents if a.in_repo(ag.path) and a.selected(ag.path)]
    hosts_with_defs = {ag.host for ag in repo_agents}
    by_name: dict[str, dict[str, Agent]] = defaultdict(dict)
    for ag in repo_agents:
        by_name[ag.name][ag.host] = ag
    rows: list[str] = []
    for name, defs in sorted(by_name.items()):
        missing = sorted(hosts_with_defs - set(defs))
        if missing:
            rows.append(
                f"{name}: defined for {', '.join(sorted(defs))}; missing for {', '.join(missing)}"
            )
        for (h1, d1), (h2, d2) in itertools.pairwise(sorted(defs.items())):
            t1, t2 = (re.sub(r"\s+", " ", re.sub(r"[`*_]", "", d.body)).strip() for d in (d1, d2))
            if t1 != t2:
                i = len(os.path.commonprefix([t1, t2]))
                rows.append(
                    f'{name}: {h1} and {h2} bodies differ at char {i}: "{t1[i : i + 50]}" vs "{t2[i : i + 50]}"'
                )
    if len(hosts_with_defs) < 2 and not rows:
        return [f"agent definitions for {', '.join(sorted(hosts_with_defs)) or 'no host'} only"]
    return rows or ["bodies match across hosts"]


def script_paths(a: Analysis) -> list[str]:
    missing: list[str] = []
    existing: dict[str, int] = defaultdict(int)
    for p in sorted(a.repo_scripts):
        if not a.selected(p) or p.resolve() == Path(__file__).resolve():
            continue
        for i, line in enumerate(read(p).splitlines(), 1):
            for m in INSTRUCTION_PATH.finditer(line):
                token = m.group(0).rstrip(".")
                if resolve(p.parent, token, a.root):
                    existing[a.rel(p)] += 1
                else:
                    missing.append(f"{a.rel(p)}:{i}  {token}  (missing)")
    rows = capped(a, missing, "more missing")
    if existing:
        rows.append(
            f"{sum(existing.values())} paths that exist, in: "
            + ", ".join(f"{f} ({n})" for f, n in sorted(existing.items()))
        )
    return rows or ["none"]


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0] if __doc__ else None)
    parser.add_argument(
        "root", nargs="?", default=".", help="repository root (default: current directory)"
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="PATH",
        help="limit findings to files under PATH, relative to the root (repeatable)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="skip repo-relative paths matching GLOB in detectors, such as generated files; costs still count them (repeatable)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help=f"print every row instead of the first {MAX_ROWS} per section",
    )
    args = parser.parse_args()
    root = Path(args.root)
    if not root.is_dir():
        print(f"analyze.py: {root} is not a directory", file=sys.stderr)
        return 1
    for only in args.only:
        target = (root.resolve() / only).resolve()
        if not target.exists() or not target.is_relative_to(root.resolve()):
            print(
                f"analyze.py: --only {only} does not exist under {root.resolve().as_posix()}",
                file=sys.stderr,
            )
            return 1
    a = Analysis(root, args.only, args.exclude)
    if args.all:
        a.max_rows = 0
    a.gemini()
    a.walk()
    a.claude()
    a.codex()
    a.pi()
    a.antigravity()
    a.nested_context()
    print("\n".join(report(a)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
