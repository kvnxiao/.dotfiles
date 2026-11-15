# Agent configuration

## Codex configuration

Patina symlinks [config.toml](codex/config.toml) to `~/.codex/config.toml` for shared preferences.
Codex uses the built-in `:read-only` permission profile by default. On Windows, the interactive fish
`codex` function adds `windows-msys2-read`, which extends read access to MSYS2, Cargo, Git for
Windows, pnpm's bin directory, and WinGet's portable package and command-link directories. This
includes WinGet-installed pnpm. Each machine keeps a regular, untracked `~/.codex/local.config.toml`
for local state and overrides. Do not deploy or symlink the local profile.

Interactive fish defines `codex` as `command codex --profile local`. The `astra`, `sol`, and `luna`
abbreviations, including their effort variants, expand through that function. Codex creates the
local profile when it first saves a setting. Local profile values override shared preferences;
remove a local override to use the shared value again.

Use `codex --profile local` when launching outside interactive fish. The Windows-only filesystem
grants are supplied by the fish function, so direct CLI launches, the desktop app, and the IDE
extension do not receive them. Codex does not support a default profile selector in `config.toml`.
Launches without the local profile can write local state into the shared base file.

## Reviewer agents

All three clients use the
[shared reviewer contract](shared/skills/review-changes/references/review-execution.md). The client
definitions set the model, effort, and available permissions:

| Client      | Standard profile                              | Deep profile                                            |
| ----------- | --------------------------------------------- | ------------------------------------------------------- |
| Codex       | [reviewer.toml](codex/agents/reviewer.toml)   | [reviewer-deep.toml](codex/agents/reviewer-deep.toml)   |
| Claude Code | [reviewer.md](claude-code/agents/reviewer.md) | [reviewer-deep.md](claude-code/agents/reviewer-deep.md) |
| Antigravity | [reviewer.md](agy/agents/reviewer.md)         | [reviewer-deep.md](agy/agents/reviewer-deep.md)         |

Patina symlinks the definitions into each client's user-level `agents` directory. All three clients
read the shared contract directly from
`~/.agents/skills/review-changes/references/review-execution.md`. See
[review-changes](shared/skills/review-changes/SKILL.md) for modes and scope, and the
[full workflow](shared/skills/review-changes/references/full-path.md) for delegation, effort, and
acceptance rules.

Codex uses the built-in `:read-only` profile by default. Claude Code excludes editing and delegation
tools but retains Bash for diff inspection, so its read-only behavior also depends on the shared
instructions. Parent runtime settings can override Codex permissions. Explicit Claude model
overrides can override the definition's model.

Claude Code's bundled `code-review` and `simplify` skills are set to `user-invocable-only` in
[settings.json](claude-code/settings.json). They remain available as slash commands and are hidden
from automatic selection. See
[skill visibility overrides](https://code.claude.com/docs/en/skills#override-skill-visibility-from-settings).

Run `patina apply` to inspect deployment, then `patina apply --yes` to apply it. Start a new client
session after changing the agent definitions so it discovers the updated profiles.

Definition formats follow the official
[Codex subagent documentation](https://developers.openai.com/codex/subagents) and
[Claude Code subagent documentation](https://code.claude.com/docs/en/sub-agents).

## Prose audit reader agent

Before [audit-prose](shared/skills/audit-prose/SKILL.md) audits a document or instruction file that
the current agent session wrote, it starts a `cold-prose-reader` subagent. The reader gets the file,
the line ranges in scope, and the intended audience. It does not get the session history or
explanations of terms. It reads the file and the local files the file links to, and returns a flag
for each word, phrase, heading, and label whose meaning that text does not make clear. The session
that started the reader decides which flags to fix. When the reader flags wording in a linked file,
the session lists it for the user and does not edit that file.

The reader follows the instructions in
[cold-prose-reader.md](shared/skills/audit-prose/references/cold-prose-reader.md) and runs on fast
models:

| Client      | Definition                                                      | Model                                     |
| ----------- | --------------------------------------------------------------- | ----------------------------------------- |
| Claude Code | [cold-prose-reader.md](claude-code/agents/cold-prose-reader.md) | `claude-haiku-5-5`, high reasoning effort |
| Codex       | [cold-prose-reader.toml](codex/agents/cold-prose-reader.toml)   | `gpt-6-luna`, high reasoning effort       |
| Antigravity | [cold-prose-reader.md](agy/agents/cold-prose-reader.md)         | `flash` model tier, no effort setting     |

Antigravity agent files accept a model tier (`inherit`, `flash`, or `pro`) in place of a model ID.
Antigravity 1.5.9 does not load an agent file whose `model` is a model ID such as
`gemini-4-hydrogen-high`, so the reader cannot be pinned to a specific Gemini model.

## Spec workflow agents

The [write-spec](shared/skills/write-spec/SKILL.md),
[reconstruct-spec](shared/skills/reconstruct-spec/SKILL.md), and
[implement-spec-plan](shared/skills/implement-spec-plan/SKILL.md) skills use researcher and
implementer agents. Each definition sets the model and permissions and points at a shared contract:

| Client      | Researcher                                                  | Implementer                                         |
| ----------- | ----------------------------------------------------------- | --------------------------------------------------- |
| Codex       | [spec-researcher.toml](codex/agents/spec-researcher.toml)   | [implementer.toml](codex/agents/implementer.toml)   |
| Claude Code | [spec-researcher.md](claude-code/agents/spec-researcher.md) | [implementer.md](claude-code/agents/implementer.md) |
| Antigravity | [spec-researcher.md](agy/agents/spec-researcher.md)         | [implementer.md](agy/agents/implementer.md)         |

The researcher investigates one cohesive topic and its relevant questions under the
[research contract](shared/skills/write-spec/references/research.md). The implementer edits code for
the assigned tasks of one plan under the
[implementer contract](shared/skills/implement-spec-plan/references/implementer.md). Both write
files, so Codex runs them in the `workspace-write` sandbox and Claude Code grants them `Write` and
`Edit`. The Codex researcher also has network access for package and API probes. As with the
reviewers, the parent session's runtime permissions can override the Codex sandbox.

Use `write-spec` for a proposed project, capability, or known contract change. Amendments can
reconcile existing code, compatibility obligations, and changes implemented before their spec
updates. Use `reconstruct-spec` when an existing repository or subsystem needs investigation to
establish its intended contract. Reconstruction alternates repository research with an active
brainstorm, then writes the spec and supporting research after the consolidated design is confirmed.

Both writers use [review-spec](shared/skills/review-spec/SKILL.md) for the shared format, structural
checker, and substantive review before approval. Invoke it directly to review an existing spec; it
reports findings by default and applies corrections when requested. It uses the independent
`review-changes` workflow and does not grant spec approval. The spec review contract is stored in
`review-spec`; general change reviews use that contract directly for spec changes.

Patina deploys `reconstruct-spec` and `review-spec` to the Claude Code and Antigravity skill
directories and to `~/.agents/skills/` for Codex and the pi coding agent.

After spec approval, use [plan-from-spec](shared/skills/plan-from-spec/SKILL.md), then
`implement-spec-plan`. A ready plan records a fingerprint of its approved spec and area files. When
those files change, planning must reconcile the affected obligations before implementation can
resume. Completed tasks stay recorded, and new obligations get new tasks. Each child plan also
records whether its final checks and review are complete; dependent plans remain blocked until then.

Run `just test-agent-skills` for the spec checker, agent analyzer, coding practice checker, and
system design renderer regression tests. `just check` includes these suites. Coding checker tests
use subprocess test doubles for failure paths and run disposable practice packages with the bundled
runner. Renderer tests use temporary bundles and require Node.js; they do not test browser
interactions.

## Optimization reviews

Use [optimize](shared/skills/optimize/SKILL.md) to find performance and resource-efficiency
opportunities across a system. Use
[optimize-implementation](shared/skills/optimize-implementation/SKILL.md) for algorithms and
resource use within existing system responsibilities, or
[optimize-architecture](shared/skills/optimize-architecture/SKILL.md) to reconsider those
responsibilities, boundaries, and data ownership.

All three skills preserve requirements and return recommendations without applying production
changes. Default mode uses inexpensive inspection and existing evidence. Add `deep` or `mode=deep`
to authorize more extensive investigation and selective temporary experiments. For example,
`/optimize deep` examines both scopes, while `/optimize-architecture` uses default effort on the
architecture alone. Use the client's skill invocation syntax; Codex also accepts `$optimize`.

Patina deploys the three skills together to the Claude Code and Antigravity skill directories, and
to `~/.agents/skills/` for Codex and the pi coding agent. Their references share investigation rules
and load area-specific and experimental guidance when needed. Investigations run in-session when
delegation is unavailable.

## Repository README writing

The [write-readme](shared/skills/write-readme/SKILL.md) skill writes repository introductions for
their primary audience. It adapts the reading order to applications, command-line tools, libraries,
and collections, and moves detailed guidance into linked documents when the audience or level of
detail changes. It checks claims against current evidence and uses `audit-prose` for a
[cold-prose-reader pass](#prose-audit-reader-agent). It groups related app features and supports
audience-appropriate media placeholders when requested. Patina deploys it to the shared skill
directories for Codex, Claude Code, and Antigravity.

## Interactive system design tutoring

Use [tutor-system-design](shared/skills/tutor-system-design/SKILL.md) to study a Markdown question
or an existing `learn-system-design` package in conversation. Invoke `$tutor-system-design` in the
question directory, or pass a question file or package path. Use the host's equivalent skill syntax
where needed.

The tutor asks about familiar technologies and offers explain-first or try-first practice. It
develops a baseline with ASCII diagrams (or Mermaid when appropriate), and evolves the design
through discussion. When you are ready, it asks one practice scenario at a time and gives specific
feedback. You can ask for clarification, change the explanation depth, or pause quizzes. It does not
write files unless requested.

Patina deploys the skill to the Claude Code and Antigravity skill directories and to
`~/.agents/skills/` for Codex and the pi coding agent.

## Coding practice modes

Use [learn-coding-dsa](shared/skills/learn-coding-dsa/SKILL.md) with a Markdown prompt or folder of
prompts. Guided practice includes approach hints in the starter and follow-up answers in the README.
Request independent practice to put hints and answers in separate files. Both modes include shared
tests and a reference solution; contract assumptions remain visible in the starter.

## Codebase summaries

Use [summarize-codebase](shared/skills/summarize-codebase/SKILL.md) to get a high-level summary of
how a repository works before writing focused prompts about one part of it. Without arguments, it
summarizes the repository as it is. Text after the command adds instructions, such as an area to
focus on, a task description to check against the code, or a request to run the tests.

The skill writes a Markdown file of about 150 lines to the session's temporary directory, never to
the repository. The file has the run and test commands, an annotated file tree, a table of core
modules, a diagram of the main flow, and the `TODO` comments, stubs, and skipped tests it found. It
does not run code unless asked.

For repositories with more than 40 source files or 7,000 lines, the skill starts `codebase-scanner`
subagents in parallel, one per group of about 7,000 lines. The scanners follow the
[scanner contract](shared/skills/summarize-codebase/references/scanner.md) and run on fast models:

| Client      | Definition                                                    | Model              |
| ----------- | ------------------------------------------------------------- | ------------------ |
| Claude Code | [codebase-scanner.md](claude-code/agents/codebase-scanner.md) | `claude-haiku-5-5` |
| Codex       | [codebase-scanner.toml](codex/agents/codebase-scanner.toml)   | `gpt-6-luna`       |
| Antigravity | [codebase-scanner.md](agy/agents/codebase-scanner.md)         | inherited          |

The main session writes the overview sections and checks two cited definitions from each scanner
report. Patina deploys the skill to the Claude Code and Antigravity skill directories and to
`~/.agents/skills/` for Codex and the pi coding agent.
