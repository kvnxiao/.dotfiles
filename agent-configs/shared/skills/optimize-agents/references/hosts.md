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

- **Session start:** `~/.gemini/GEMINI.md` in the system prompt; `GEMINI.md` files from the workspace up to the git root in the first message, with a directory tree; skill listings from `~/.gemini/skills`, `~/.agents/skills`, `.gemini/skills`, and `.agents/skills`; agent names and descriptions; every MCP tool declaration.
- **Context files:** `context.fileName` in `settings.json` sets the names, `GEMINI.md` by default, so `AGENTS.md` loads only when listed. `@path` imports expand up to five levels, and Gemini parses any `@word` in prose as an import attempt.
- **On a trigger:** context files in directories that file tools touch.
- **On invocation:** `activate_skill` returns the body after the user consents. Headless runs deny it unless the approval mode allows it.
- **Delegates:** `.gemini/agents/*.md`, with a strict schema that rejects Claude Code agent files; the body, global and workspace memory, and the skill listing only when the agent may activate skills.
- **Controls:** no setting hides a skill from the model alone; `skills.disabled` hides it from both model and user. Custom commands in `.gemini/commands/` cost nothing until invoked.
