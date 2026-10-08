# Host loading

What each host loads and when, and the controls that change it. The analyzer applies these rules and the numeric limits; use this file to choose a control.

## Claude Code

- **Session start:** `~/.claude/CLAUDE.md`; `CLAUDE.md`, `.claude/CLAUDE.md`, and `CLAUDE.local.md` in the working directory and every directory above it, with `@path` imports expanded up to four hops; `.claude/rules/**/*.md` files without `paths` frontmatter, user-level and project; the output style; MCP tool names; skill and agent names and descriptions from `~/.claude/skills`, `.claude/skills`, `~/.claude/agents`, `.claude/agents`, and enabled plugins. Symlinked skill directories load; `rg --files` skips them unless given `-L`.
- **AGENTS.md:** read by default only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or above it. Then every `AGENTS.md` and `.claude/AGENTS.md` in those directories loads. `~/.claude/CLAUDE.md` does not count for this check, and there is no user-level `AGENTS.md`. A `CLAUDE.md` that imports `@AGENTS.md` loads it once.
- **On a trigger:** when Claude reads a file in a subdirectory, that directory's `CLAUDE.md` loads. Its `AGENTS.md` loads instead only when the subdirectory has no `CLAUDE.md` and Claude read `AGENTS.md` files at session start. Either file loads even when a session-start file is a symlink to it. Rules with `paths` load when Claude reads or edits a matching file, and MCP tool schemas load when searched.
- **On invocation:** the skill body. Other files load only when read.
- **Delegates:** the definition body as the system prompt, the instruction files above unless the definition sets `omitClaudeMd: true`, and the full bodies of skills named in `skills`. Output styles do not load.
- **Controls:** `disable-model-invocation: true` removes a skill from the model's listing and keeps `/name`; `user-invocable: false` hides it from the menu; `skillOverrides` in settings; `paths` frontmatter on rules.

## Codex

- **Session start:** `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md`; then, in each directory from the project root to the working directory, the first of `AGENTS.override.md`, `AGENTS.md`, and `project_doc_fallback_filenames`. It reads `CLAUDE.md` only when that setting lists it. It lists skills from `.agents/skills` in the same directories, `.codex/skills`, `~/.agents/skills`, and `~/.codex/skills`, and lists agent names and descriptions in the spawn tool. An untrusted project loads only the global file.
- **On invocation:** `$name` injects the body. Otherwise the model reads `SKILL.md` with a shell command. For the bundled models, Codex cuts an output over about 48 KB to its head and tail. Models page long files by line ranges and may stop after the first page. Only a skill installed from a plugin, which has `.codex-plugin/plugin.json`, is injected with a byte cap.
- **Delegates:** `developer_instructions`, plus `AGENTS.md` and the skill listing again. A role file in `.codex/agents/` can drop its delegate's listing with `[skills] include_instructions = false` and disable skills, but cannot turn on what the parent turned off.
- **Controls:** `policy.allow_implicit_invocation: false` in `agents/openai.yaml` hides a skill from the listing and keeps `$name`; `[skills] include_instructions = false` removes the listing; `project_doc_fallback_filenames`.

## pi

- **Session start:** one context file from `~/.pi/agent/`, then the first of `AGENTS.override.md`, `AGENTS.md`, and `CLAUDE.md` in each directory from the working directory up to the filesystem root, so a directory with both loads only `AGENTS.md`. `SYSTEM.md` replaces the system prompt and `APPEND_SYSTEM.md` extends it. Skills are listed from `~/.pi/agent/skills`, `~/.agents/skills`, `.pi/skills`, and `.agents/skills`.
- **On invocation:** the model reads `SKILL.md`; `/skill:name` inlines it. One read returns at most 2,000 lines or 50 KB and gives the offset to continue.
- **Delegates:** none built in.
- **Controls:** `disable-model-invocation: true`; prompt templates in `.pi/prompts/` cost nothing until invoked.

## Gemini CLI

Since June 18, 2026, Gemini CLI no longer serves individual Google AI Pro, Ultra, or free accounts, which use the Antigravity CLI instead. Gemini Code Assist Standard and Enterprise licenses and paid Gemini API keys keep Gemini CLI access.

- **Session start:** `~/.gemini/GEMINI.md` in the system prompt; `GEMINI.md` files from the workspace up to the git root in the first message, with a directory tree; skill listings from `~/.gemini/skills`, `~/.agents/skills`, `.gemini/skills`, and `.agents/skills`; agent names and descriptions; every MCP tool declaration.
- **Context files:** `context.fileName` in `settings.json` sets the names, `GEMINI.md` by default, so `AGENTS.md` loads only when listed. `@path` imports expand up to five levels, and Gemini parses any `@word` in prose as an import attempt.
- **On a trigger:** context files in directories that file tools touch.
- **On invocation:** `activate_skill` returns the body after the user consents. Headless runs deny it unless the approval mode allows it.
- **Delegates:** `.gemini/agents/*.md`, with a strict schema that rejects Claude Code agent files; the body, global and workspace memory, and the skill listing only when the agent may activate skills.
- **Controls:** no setting hides a skill from the model alone; `skills.disabled` hides it from both model and user. Custom commands in `.gemini/commands/` cost nothing until invoked.

## Antigravity

Antigravity is Google's agent host: the `agy` CLI, the Antigravity IDE, and the 2.0 desktop app. Its customizations live under `~/.gemini/config/`, and each surface keeps its own app data, such as `~/.gemini/antigravity-cli/`.

- **Session start:** `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.gemini/config/AGENTS.md`, `~/.gemini/config/GEMINI.md`, and the rules in `~/.gemini/config/rules/` and, for the CLI, `~/.gemini/antigravity-cli/rules/`. Then, in each directory from the working directory up to the repository root: `AGENTS.md`, `GEMINI.md`, `.agents/AGENTS.md`, `.agents/GEMINI.md`, and the rules in `.agents/rules/` and the legacy `.agent/rules/`. Then skill names and descriptions.
- **On a trigger:** the same files in a subdirectory load when Antigravity reads or edits a file under it. A `model_decision` rule puts only its path and description in the prompt; `glob` and `manual` rules load when their condition applies.
- **Rules:** every rule file, global or workspace, needs frontmatter with a `trigger` of `always_on`, `model_decision`, `glob`, or `manual`. Antigravity discards a rule with a missing or invalid trigger, such as camelCase `alwaysOn`, without a warning. Each rule is capped at 24,000 bytes after its `@[label](path)` includes expand and is truncated on a line boundary. Global rules and always-on rules share a 20,000-token budget; over it, Antigravity demotes the largest rules to path-and-description pointers. Whether workspace `AGENTS.md` and `GEMINI.md` count toward that budget is unverified. A bare `@file` is only a path reference.
- **Skills:** listed one level deep from these roots:
  - `.agents/skills` and the legacy `.agent/skills` in each directory from the working directory up to the repository root.
  - `~/.gemini/config/skills/`.
  - each directory that a `skills.json` entry names. Antigravity reads `skills.json` from `~/.gemini/config/` and from each `.agents/` directory in that range. A relative entry resolves against the directory that holds the declaring dot-directory, falling back to the repository root, and `include_only` and `exclude` filter entries.

  The docs also name `~/.gemini/antigravity-cli/skills/` for the CLI and `~/.gemini/antigravity/skills/` for the IDE; the shipped CLI binary does not contain the CLI path. `~/.agents/skills` is not a global path, so its skills load only when that scan reaches `~`: in a workspace under `~` with no repository root between them. Where the scan stops outside a repository is not verified. Skills, subagents, and MCP tools share a customization budget of unverified size, and items over it are left out of the listing. Whether symlinked skill directories load is unverified.
- **Frontmatter:** the binary parses frontmatter with a strict YAML parser and has a "failed to parse frontmatter yaml" message, so a skill whose frontmatter fails strict YAML likely does not load. These constructs fail: an unquoted colon followed by a space, an unquoted `#` after a space when more lines of the value follow it, a plain value that starts with `@`, `` ` ``, `*`, `%`, `,`, `-`, or `?`, and a repeated key. The binary has no `.gemini/skills`, `.gemini/agents`, or `.gemini/commands` strings, so Antigravity likely does not read them.
- **On invocation:** the skill body; files under `references/`, `scripts/`, `examples/`, and `resources/` load when read. Each skill is also a `/name` command.
- **Reads:** `view_file` takes a line range, caps the lines per call, and truncates by bytes, then gives the byte offset to continue. Both limits are runtime settings.
- **Delegates:** the model starts concurrent subagents with `invoke_subagent` and creates temporary ones with `define_subagent`. Built-in subagents are `research`, `self`, `browser`, and `image-generator`; `browser` starts only from `/browser`. Custom agents live in `.agents/agents/<name>.md`, `.agents/agents/<name>/agent.md`, or the same forms under `~/.gemini/config/agents/`, and require `name` and `description`; `subagent: false` makes one uninvocable. A subagent starts with a clean context, but per the changelog, custom Markdown agents inherit skills, rules, and subagents unless `inheritCustomizations` turns that off. The docs cover delegates for the CLI and the 2.0 app only.
- **Controls:** `disable-slash-command: true` removes a skill's `/name` command and keeps it model-invocable; `skills.json` adds and filters skill directories; `trigger` frontmatter sets when a rule loads. MCP servers come from `~/.gemini/config/mcp_config.json` and the workspace `.agents/mcp_config.json`. No verified setting hides a skill from the model.
