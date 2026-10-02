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
