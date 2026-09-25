# Agent configuration

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

Codex sets a read-only sandbox default. Claude Code excludes editing and delegation tools but
retains Bash for diff inspection, so its read-only behavior also depends on the shared instructions.
Parent runtime settings can override Codex sandbox defaults. Explicit Claude model overrides can
override the definition's model.

Run `patina apply` to inspect deployment, then `patina apply --yes` to apply it. Start a new client
session after the first deployment so it discovers the agent definitions. Opus 5.5 requires Claude
Code 2.1.280 or later.

Definition formats follow the official
[Codex subagent documentation](https://developers.openai.com/codex/subagents) and
[Claude Code subagent documentation](https://code.claude.com/docs/en/sub-agents).
