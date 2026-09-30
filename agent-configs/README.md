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

The reviewer uses one [shared contract](shared/agents/reviewer.md) with two effort profiles per
client:

| Client      | Definition                                              | Model             | Effort  |
| ----------- | ------------------------------------------------------- | ----------------- | ------- |
| Codex       | [reviewer.toml](codex/agents/reviewer.toml)             | `gpt-6-astra`     | `high`  |
| Codex       | [reviewer-deep.toml](codex/agents/reviewer-deep.toml)   | `gpt-6-astra`     | `xhigh` |
| Claude Code | [reviewer.md](claude-code/agents/reviewer.md)           | `claude-opus-5-5` | `high`  |
| Claude Code | [reviewer-deep.md](claude-code/agents/reviewer-deep.md) | `claude-opus-5-5` | `xhigh` |

Patina symlinks the definitions into each client's user-level `agents` directory and the shared
contract to `~/.agents/instructions/reviewer.md`. Both clients read review procedures from the
shared skills deployed under `~/.agents/skills/`.

Ask either client to use the `reviewer` agent for a diff or selected files. The full
`verify-changes` workflow defaults to `reviewer` and selects `reviewer-deep` when a specific
reasoning difficulty warrants it. Both profiles support correctness and focused simplification
review. The coordinator chooses effort before spawning and keeps it fixed for the assignment.
Follow-ups reuse the existing reviewer; unresolved questions do not trigger a replacement at higher
effort. The coordinator supplies scope and applies accepted fixes. See the
[effort routing criteria](shared/skills/verify-changes/references/full-review.md#select-review-effort).

The profiles set effort in client configuration; prompt text alone does not change it. The routing
criteria are provisional and require evaluation on actual reviews. OpenAI recommends using `xhigh`
when evaluations justify its added cost and latency. Anthropic recommends evaluating effort levels
on the workload for Opus 5.5, whose default is `medium`. Choosing `high` for ordinary reviews is a
local policy. See
[OpenAI reasoning guidance](https://developers.openai.com/api/docs/guides/reasoning) and
[Anthropic effort guidance](https://platform.claude.com/docs/en/build-with-claude/effort).

Codex uses the built-in `:read-only` profile by default. Claude Code excludes editing and delegation
tools but retains Bash for diff inspection, so its read-only behavior also depends on the shared
instructions. Parent runtime settings can override Codex permissions. Explicit Claude model
overrides can override the definition's model.

Run `patina apply` to inspect deployment, then `patina apply --yes` to apply it. Start a new client
session after the first deployment so it discovers the agent definitions. Opus 5.5 requires Claude
Code 2.1.280 or later.

Definition formats follow the official
[Codex subagent documentation](https://developers.openai.com/codex/subagents) and
[Claude Code subagent documentation](https://code.claude.com/docs/en/sub-agents).
