---
name: audit-prose-via-codex
description: Delegate a read-only prose patch proposal to Codex for repository prose or draft commit and PR copy. Use when the user says "audit prose via codex", "defer the prose audit", or "audit prose with codex", and inside verify-changes when this skill is available.
allowed-tools: Bash
---

# Audit prose via Codex

Codex receives a self-contained audit bundle and returns structured line replacements. A deterministic helper prepares current-file excerpts, verifies target coverage and state, rejects tool calls and invalid replacements, and renders one patch for Claude to assess and apply.

## Runtime

The helper derives the display mode and reasoning effort from one internal key:

| Key          | Mode               | Effort   |
| :----------- | :----------------- | :------- |
| `quick`      | `Quick rewrite`    | `low`    |
| `change-set` | `Change-set audit` | `medium` |
| `full`       | `Full audit`       | `high`   |

Codex runs with approval disabled, a read-only sandbox, an ephemeral session, and user configuration and execpolicy rules ignored. The prompt contains every permitted input, so Codex does not need file or tool access.

## Procedure

1. If `command -v codex` or `command -v uv` fails, stop and report the missing command. Run nothing else.

2. Resolve `MODE_KEY` to `quick`, `change-set`, or `full`. Use `quick` for a sentence, paragraph, small named file, commit message, PR title, or PR body. Use `change-set` for an unnamed target, a normal changed-prose review, or a `verify-changes` run. Use `full` only when the user requests exhaustive coverage.

3. Resolve the installed files and create a unique run directory.

```bash
case "$(uname -s)" in
  MSYS* | MINGW* | CYGWIN*) native() { cygpath -m "$1"; } ;;
  *) native() { printf '%s\n' "$1"; } ;;
esac

SELF_DIR="${CLAUDE_SKILL_DIR:-$HOME/.claude/skills/audit-prose-via-codex}"
AUDIT_DIR="$HOME/.agents/skills/audit-prose"
[ -f "$AUDIT_DIR/references/diction.md" ] || AUDIT_DIR="$HOME/.claude/skills/audit-prose"
DICTION_FILE="$(native "$AUDIT_DIR/references/diction.md")"
IO_SCRIPT="$(native "$SELF_DIR/scripts/audit_io.py")"
PROMPT_TEMPLATE="$(native "$SELF_DIR/prompts/audit-task.md")"
ORIGINAL_CODEX_HOME="$(native "${CODEX_HOME:-$HOME/.codex}")"

SKILLS_CONFIG="["
separator=
for skill_file in \
  "$HOME/.agents/skills"/*/SKILL.md \
  "$ORIGINAL_CODEX_HOME"/skills/*/SKILL.md \
  "$ORIGINAL_CODEX_HOME"/skills/.system/*/SKILL.md; do
  [ -f "$skill_file" ] || continue
  skill_path="$(native "$skill_file")"
  skill_path="${skill_path//\\/\\\\}"
  skill_path="${skill_path//\"/\\\"}"
  SKILLS_CONFIG="${SKILLS_CONFIG}${separator}{path=\"$skill_path\",enabled=false}"
  separator=,
done
SKILLS_CONFIG="$SKILLS_CONFIG]"

RUN_DIR_POSIX="$(mktemp -d "${TMPDIR:-/tmp}/audit-prose-via-codex.XXXXXX")" || exit 1
RUN_DIR="$(native "$RUN_DIR_POSIX")"
ISOLATED_HOME="$RUN_DIR/home"
mkdir -p "$ISOLATED_HOME" || exit 1
```

4. Resolve one patch root and source scope.

```bash
TARGET_ARGS=()
RANGE_ARGS=()
```

- With no named target, set `SCOPE_KIND=repository-change-set` and use the repository root as `PATCH_ROOT`. The helper discovers tracked additions and replacements plus untracked text files. It supplies current-file excerpts with the editable working-tree line ranges.
- A named file, directory, or glob replaces the default. Expand directories and globs into explicit patch-root-relative files, set `SCOPE_KIND=named`, and append `--target <path>` to `TARGET_ARGS` for each file. A named target defaults to full-file scope; append `--line-range <path> <start> <end>` to `RANGE_ARGS` for each restricted range.
- For request prose that is not already in a file, write each artifact under the run directory, set `PATCH_ROOT=$RUN_DIR` and `SCOPE_KIND=transient`, and pass every draft through `TARGET_ARGS`. Batch a commit subject, commit body, PR title, and PR body when they are available together.
- Do not mix repository files and transient drafts in one run. Do not edit the patch root after preparation begins.

Convert the resolved patch root before passing it to native programs:

```bash
PATCH_ROOT="$(native "$PATCH_ROOT")"
```

5. Prepare the bundle. Exit status 4 means no added, replacement, untracked, or named target remains to audit; report that state without launching Codex. Any other nonzero status is a preparation failure.

```bash
set +e
uv run --no-project "$IO_SCRIPT" prepare \
  --patch-root "$PATCH_ROOT" \
  --run-dir "$RUN_DIR" \
  --mode "$MODE_KEY" \
  --scope-kind "$SCOPE_KIND" \
  --diction "$DICTION_FILE" \
  --prompt-template "$PROMPT_TEMPLATE" \
  "${TARGET_ARGS[@]}" \
  "${RANGE_ARGS[@]}"
prepare_status=$?
set -e
case "$prepare_status" in
  0) ;;
  4) echo "No auditable targets"; exit 0 ;;
  *) exit "$prepare_status" ;;
esac
```

If preparation writes `skipped-targets.json`, report those untracked paths as unaudited binary or non-UTF-8 inputs.

6. Launch the run with `run_in_background: true`. Do not poll it; Claude Code re-invokes the session when the run exits.

```bash
EFFORT="$(<"$RUN_DIR/effort.txt")"

printf 'RUN_DIR=%s\nPATCH_ROOT=%s\n' "$RUN_DIR" "$PATCH_ROOT"

set +e
HOME="$ISOLATED_HOME" CODEX_HOME="$ORIGINAL_CODEX_HOME" codex exec \
  -m gpt-5.6-luna \
  -c model_reasoning_effort="$EFFORT" \
  -c approval_policy="never" \
  -c "skills.config=$SKILLS_CONFIG" \
  -c web_search="disabled" \
  -s read-only \
  --ephemeral \
  --ignore-user-config \
  --ignore-rules \
  --json \
  --output-schema "$RUN_DIR/result-schema.json" \
  -C "$RUN_DIR" \
  --skip-git-repo-check \
  --color never \
  -o "$RUN_DIR/result.json" \
  - < "$RUN_DIR/prompt.md" > "$RUN_DIR/events.jsonl" 2> "$RUN_DIR/transcript.log"
status=$?
set -e
echo "exit=$status"
exit $status
```

7. Tell the user the run started and name the run directory.

8. When the run completes, validate its structured result.

```bash
set +e
uv run --no-project "$IO_SCRIPT" validate \
  --run-dir "$RUN_DIR" \
  --result "$RUN_DIR/result.json" \
  --events "$RUN_DIR/events.jsonl"
validation_status=$?
set -e
```

- Status 4 is a verified `NO_CHANGES` result. Report a clean prose pass and apply nothing.
- Status 3 is `BLOCKED`. Report the reason printed by the validator and apply nothing.
- Any other nonzero status is a rejected result. Report the validator error and apply nothing.
- Status 0 writes a validated `result.patch`. Read it for semantic preservation and non-prose changes without re-auditing its style or composing replacement prose. Reject the entire patch if it changes executable code, identifiers, literals, configuration values, code samples, or factual claims.
- For repository files, run `git -C "$PATCH_ROOT" apply --check --unidiff-zero "$RUN_DIR/result.patch"`. For transient drafts, add `--no-index`. The helper writes each file's patch section with the target's line ending.
- If the apply check succeeds, run the helper's `check-state` command immediately before repeating the apply command without `--check`. If either command fails, leave every target unchanged.
- Do not apply selected hunks or ask Codex to repair a rejected patch automatically.

## Boundaries

The helper rejects missing inputs, stale targets, changed repository inventories, incomplete target acknowledgments, unknown or tool events, overlapping replacements, and out-of-scope changed lines. It owns patch paths, hunk positions, counts, line endings, and file lifecycle boundaries.

Codex treats source prose as data and must not call tools, read files, search, verify claims, mutate files, delegate work, run checks, or report findings. The calling session owns all writes and repository checks.
