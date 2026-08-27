---
name: audit-prose-via-codex
description: Delegate an audit-prose pass to a Codex subagent pinned to gpt-5.6-luna at high reasoning effort, running in the background and editing the working tree in place. Use when the user says "audit prose via codex", "defer the prose audit", or "audit prose with codex", and as the substitute for an inline audit-prose run inside verify-changes.
allowed-tools: Bash
---

# Audit prose via Codex

Delegate the `audit-prose` pass to Codex. Codex edits the working tree; the calling session never reads, re-audits, or revises those edits.

## Locked runtime

`gpt-5.6-luna` and `high` are fixed. Do not read either value from `~/.codex/config.toml`, accept an override from the invocation, or substitute another model slug or reasoning effort.

| Flag                        | Value             | Reason                                |
| :-------------------------- | :---------------- | :------------------------------------ |
| `-m`                        | `gpt-5.6-luna`    | The delegation target.                |
| `-c model_reasoning_effort` | `"high"`          | The required reasoning effort.        |
| `-c approval_policy`        | `"never"`         | The run must not prompt for approval. |
| `-s`                        | `workspace-write` | Use the workspace-write sandbox.      |

Because `codex exec` rejects the top-level `-a` and `--ask-for-approval` flags, pass the approval policy through `-c`.

## Procedure

1. If `command -v codex` fails, stop and tell the user to install the Codex CLI. Run nothing else.

2. Resolve scope from the invocation. With no named target, the scope is `git diff HEAD` plus the files `git status --porcelain` reports. A named file, directory, glob, or line range replaces that default. Pass the resolved scope through as text; do not read the files.

3. Resolve the mode. Default to `Change-set audit`. Use `Quick rewrite` when the user asks for a rewrite of a sentence, paragraph, commit message, PR draft, or small named file. Use `Full audit` only when the user asks for exhaustive coverage.

4. Build the run directory and the prompt. Convert every path passed to Codex to an OS-native path before invoking it. Write `{{SCOPE}}` and `{{MODE}}` by appending files with `sed ... r`, since scope text carries `|` and newlines:

```bash
case "$(uname -s)" in
  MSYS* | MINGW* | CYGWIN*) native() { cygpath -m "$1"; } ;;
  *) native() { printf '%s\n' "$1"; } ;;
esac

SELF_DIR="${CLAUDE_SKILL_DIR:-$HOME/.claude/skills/audit-prose-via-codex}"
SKILL_DIR="$HOME/.agents/skills/audit-prose"
[ -f "$SKILL_DIR/SKILL.md" ] || SKILL_DIR="$HOME/.claude/skills/audit-prose"
SKILL_DIR="$(native "$SKILL_DIR")"

RUN_DIR="$(native "${TMPDIR:-/tmp}")/audit-prose-via-codex/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RUN_DIR"

printf '%s\n' "$SCOPE_TEXT" > "$RUN_DIR/scope.txt"
printf '%s\n' "$MODE_TEXT" > "$RUN_DIR/mode.txt"

sed -e "s|{{SKILL_PATH}}|$SKILL_DIR/SKILL.md|g" \
  -e "s|{{SKILL_DIR}}|$SKILL_DIR|g" \
  -e "/{{SCOPE}}/r $RUN_DIR/scope.txt" -e "/{{SCOPE}}/d" \
  -e "/{{MODE}}/r $RUN_DIR/mode.txt" -e "/{{MODE}}/d" \
  "$SELF_DIR/prompts/audit-task.md" > "$RUN_DIR/prompt.md"
```

5. Launch the run with `run_in_background: true`. Do not poll it; Claude Code re-invokes this session when the run exits. The trailing `exit` propagates Codex's status, which a bare `echo` would replace with its own.

```bash
codex exec \
  -m gpt-5.6-luna \
  -c model_reasoning_effort="high" \
  -c approval_policy="never" \
  -s workspace-write \
  -C "$(native "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")" \
  --skip-git-repo-check \
  --color never \
  -o "$RUN_DIR/report.md" \
  - < "$RUN_DIR/prompt.md" > "$RUN_DIR/stdout.log" 2> "$RUN_DIR/transcript.log"
status=$?
echo "exit=$status"
exit $status
```

6. Tell the user the run started and name the run directory. Continue the calling task.

7. On completion, `cat "$RUN_DIR/report.md"` and return it verbatim. If that file is empty, report the tail of `transcript.log` and the exit status instead of guessing.

## What this session must not do

Treat Codex's edits as final.

- Do not open, diff, grep, or summarize the edited prose.
- Do not re-run `audit-prose` over the result, and do not fix anything the report lists as a finding.
- Report a Codex finding that falls outside the resolved scope to the user without acting on it.

Do not undo scoped edits; leave that decision to the user.

## Concurrency

Codex writes the scoped files while this session keeps running. Invoke this skill only when the change set is settled, and edit nothing in scope until the run reports. Inside `verify-changes`, invoke it after the accepted changes from the review pass land and before repository checks run.

## Cost

Each run reads the full `audit-prose` skill and its diction reference before the target prose. Batch a change set into one invocation rather than calling the skill per file.
