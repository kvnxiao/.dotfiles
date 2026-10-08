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

Both clients use the
[shared reviewer contract](shared/skills/review-changes/references/review-execution.md). The client
definitions set the model, effort, and available permissions:

| Client      | Standard profile                              | Deep profile                                            |
| ----------- | --------------------------------------------- | ------------------------------------------------------- |
| Codex       | [reviewer.toml](codex/agents/reviewer.toml)   | [reviewer-deep.toml](codex/agents/reviewer-deep.toml)   |
| Claude Code | [reviewer.md](claude-code/agents/reviewer.md) | [reviewer-deep.md](claude-code/agents/reviewer-deep.md) |

Patina symlinks the definitions into each client's user-level `agents` directory. Both clients read
the shared contract directly from `~/.agents/skills/review-changes/references/review-execution.md`.
See [review-changes](shared/skills/review-changes/SKILL.md) for modes and scope, and the
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

## Spec workflow agents

The [write-spec](shared/skills/write-spec/SKILL.md) and
[implement-spec-plan](shared/skills/implement-spec-plan/SKILL.md) skills delegate to two more
agents. Each definition sets the model and permissions and points at a contract in its skill:

| Client      | Researcher                                                  | Implementer                                         |
| ----------- | ----------------------------------------------------------- | --------------------------------------------------- |
| Codex       | [spec-researcher.toml](codex/agents/spec-researcher.toml)   | [implementer.toml](codex/agents/implementer.toml)   |
| Claude Code | [spec-researcher.md](claude-code/agents/spec-researcher.md) | [implementer.md](claude-code/agents/implementer.md) |

The researcher writes one dated research document under the
[research contract](shared/skills/write-spec/references/research.md). The implementer edits code for
one plan task under the
[implementer contract](shared/skills/implement-spec-plan/references/implementer.md). Both write
files, so Codex runs them in the `workspace-write` sandbox and Claude Code grants them `Write` and
`Edit`. The Codex researcher also has network access for package and API probes. As with the
reviewers, the parent session's runtime permissions can override the Codex sandbox.

The workflow runs through `write-spec`, [plan-from-spec](shared/skills/plan-from-spec/SKILL.md), and
`implement-spec-plan`. A ready plan records a fingerprint of its approved spec and area files. When
those files change, planning must reconcile the affected obligations before implementation can
resume. Completed tasks stay recorded, and new obligations get new tasks. Each child plan also
records whether its final checks and review are complete; dependent plans remain blocked until then.

Run `just test-agent-skills` for the checker and analyzer regression tests. `just check` includes
these tests.
