---
name: linear-fix
description: Autonomously completes Linear tickets via git worktrees. Use when user says "fix ENG-123", "complete LIN-456", "work on linear ticket", provides a linear.app URL, or mentions a ticket ID pattern like ABC-123. Creates git worktree, implements fix via autonomous planning/review loop, opens GitHub PR with full reasoning.
allowed-tools: Read, Bash(), Task
---

# Linear Fix

This skill provides the full workflow for autonomously completing a Linear ticket ID or Linear issue URL. The workflow runs sequentially and unsupervised: fetch issue details, create git worktree, implement the fix via autonomous planning and review, then open a GitHub PR with the changes.

**CRITICAL**:

- This skill operates **autonomously** - make judgment calls and document reasoning instead of asking user questions.
- ALWAYS create a git worktree BEFORE working on the task. Use the ID of the linear ticket as the worktree folder name and branch name.
- ALWAYS use `linear-cli` for Linear CLI, never Linear MCP tool. Use `linear-cli --help` to see all commands.
- ALWAYS use `gh` for GitHub CLI, never GitHub MCP tool. Use `gh --help` to see all commands.

## Usage

### As a command

```
/linear-fix <ticket-id-or-url>
```

## Workflow

ALWAYS follow this 6 step process:

### Step 1: Gather Context

Extract ticket ID and fetch details:

```bash
TICKET_ID=$(./scripts/extract-linear-issue-id.sh "<user-input>")
TICKET_JSON=$(linear-cli issues get "$TICKET_ID" --output json)
TICKET_COMMENTS=$(linear-cli comments list "$TICKET_ID")
```

Extract from TICKET_JSON: `TITLE`, `DESCRIPTION`, `STATE`, `PRIORITY`

### Step 2: Create Git Worktree

Ensure `.worktrees` is gitignored (if not already):

```bash
grep -qxF '.worktrees' .gitignore || echo '.worktrees' >> .gitignore
```

Run @./scripts/create-git-worktree.sh and capture output variables:

```bash
eval $(TICKET_ID="$TICKET_ID" ./scripts/create-git-worktree.sh)
cd "$WORKTREE_PATH"
```

This sets: `BRANCH_NAME`, `WORKTREE_PATH`, `DEFAULT_BRANCH`

### Step 3: Autonomous Planning Phase

Use the Task tool with `subagent_type=Plan` to create a comprehensive implementation plan.

The planner MUST:
1. Explore codebase to understand patterns and architecture
2. Propose 2-3 implementation approaches with trade-offs
3. Identify risks and edge cases
4. Recommend one approach with justification

Use prompt template from @./references/planner-prompt.md, substituting `$TICKET_ID`, `$TICKET_JSON`, `$TICKET_COMMENTS`.

### Step 4: Autonomous Plan Review (Multi-Round)

Use the Task tool with `subagent_type=feature-dev:code-architect` to review the plan.

**Review Criteria:** Alignment with requirements, codebase consistency, edge case coverage, risk mitigation.

Use prompt template from @./references/reviewer-prompt.md, substituting `$TICKET_ID`, `$TICKET_JSON`, `$PLANNER_OUTPUT`.

**Multi-Round Loop:**
- If `## Review Decision: REVISION REQUESTED` → pass feedback back to planner (Step 3)
- If `## Review Decision: APPROVED` → proceed to implementation
- Max 3 iterations; after 3, reviewer MUST select best available with caveats

**Extract from approved review** (parse from reviewer output text):
- `SELECTED_APPROACH` ← value after "## Selected Approach"
- `REVIEW_REASONING` ← content under "## Reasoning"
- `TRADEOFFS_ACCEPTED` ← content under "## Additional Considerations"
- `EDGE_CASES` ← edge cases mentioned in plan
- `ITERATION_COUNT` ← number of planning rounds completed

### Step 5: Implement and Validate

Implement according to the approved plan. Follow repository coding standards. Handle documented edge cases.

**Before committing, validate:**
1. Run existing tests if present (`just test`, `pnpm test`, etc.)
2. Run linter/formatter if configured
3. Verify build succeeds if applicable

If validation fails, fix issues before proceeding.

### Step 6: Commit, Push, and Create PR

1. Determine `COMMIT_TYPE` based on ticket type: `fix` (bug), `feat` (feature), `chore` (maintenance), `refactor`, `docs`, `test`
2. Commit and push using @./scripts/commit-and-push.sh
3. Create PR using @./scripts/create-github-pr.sh

Required env vars: `TICKET_ID`, `TITLE`, `BRANCH_NAME`, `DEFAULT_BRANCH`
Optional: `COMMIT_TYPE` (default: fix), `DESCRIPTION`, `STATE`, `PRIORITY`, planning variables

## Requirements

- `linear-cli` installed and authenticated
- `gh` (GitHub CLI) installed and authenticated
- `jq` for JSON parsing
- Repository must have `origin` remote configured

## Notes

- Worktrees are created in a subfolder relative to repo root `./.worktrees/`
- Branch names use format `[username]/[ticket-lowercase]` (e.g., `kevin/eng-123`)
- Commit messages follow conventional format: `fix(TICKET-ID): Title`
- PR automatically includes Linear ticket link and details
- If a PR template exists, it's appended to the generated body

## Autonomous Behavior

This skill operates **without user interaction**:

- Make judgment calls based on ticket context and codebase analysis
- Document all reasoning in PR body under collapsible section
- Planner and reviewer iterate until consensus (max 3 rounds)
- If max iterations reached, select best available with caveats documented

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Worktree already exists | `git worktree remove ./.worktrees/<ticket>` then retry |
| Branch already exists | `git branch -D <branch>` or use existing branch |
| `linear-cli` auth expired | `linear-cli auth login` |
| Merge conflicts | Resolve manually, then continue workflow |
| Tests fail | Fix issues before committing |

## Cleanup

After PR is merged, clean up worktree:

```bash
git worktree remove ./.worktrees/<ticket-lowercase>
git branch -D <branch-name>  # if not auto-deleted
```

List existing worktrees: `git worktree list`
