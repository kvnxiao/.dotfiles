# Linear Fix Workflow

## Step 1: Gather Context

Extract ticket ID and fetch details:

```bash
TICKET_ID=$(./scripts/extract-linear-issue-id.sh "<user-input>")
TICKET_JSON=$(linear-cli issues get "$TICKET_ID" --output json)
TICKET_COMMENTS=$(linear-cli comments list "$TICKET_ID")
```

Extract from TICKET_JSON: `TITLE`, `DESCRIPTION`, `STATE`, `PRIORITY`, `TICKET_URL` (the `url` field)

**IMPORTANT**: If description or comments contain uploads (images, files), ALWAYS download them via `/linear-uploads` skill for additional context before planning.

## Step 2: Create Git Worktree

Ensure `.worktrees` is gitignored:

```bash
grep -qxF '.worktrees' .gitignore || echo '.worktrees' >> .gitignore
```

Run worktree script and cd into it:

```bash
eval $(TICKET_ID="$TICKET_ID" ./scripts/create-git-worktree.sh)
cd "$WORKTREE_PATH"
```

This sets: `BRANCH_NAME`, `WORKTREE_PATH`, `DEFAULT_BRANCH`

Install dependencies (`just install`, `pnpm install`, etc.)

## Step 3: Autonomous Planning

Use Task tool with `subagent_type=Plan`.

Use prompt template from @./planner-prompt.md, substituting `$TICKET_ID`, `$TICKET_JSON`, `$TICKET_COMMENTS`.

## Step 4: Autonomous Plan Review

Use Task tool with `subagent_type=feature-dev:code-architect`.

Use prompt template from @./reviewer-prompt.md, substituting `$TICKET_ID`, `$TICKET_JSON`, `$PLANNER_OUTPUT`.

**Multi-Round Loop:**
- `## Review Decision: REVISION REQUESTED` → pass feedback back to planner (Step 3)
- `## Review Decision: APPROVED` → proceed to implementation
- Max 3 iterations; after 3, reviewer MUST select best available with caveats

**Extract from approved review:**
- `SELECTED_APPROACH` ← value after "## Selected Approach"
- `REVIEW_REASONING` ← content under "## Reasoning"
- `TRADEOFFS_ACCEPTED` ← content under "## Additional Considerations"
- `EDGE_CASES` ← edge cases mentioned in plan
- `ITERATION_COUNT` ← number of planning rounds completed

## Step 5: Implement and Review

### 5a: Implement

Implement approved plan. Validate (tests, lint, build) pass before review.

### 5b: Code Review

Use Task tool with `subagent_type=feature-dev:code-reviewer`.

Use prompt template from @./code-reviewer-prompt.md, substituting `$TICKET_ID`, `$TICKET_JSON`, `$SELECTED_APPROACH`.

**Review Loop:**

- `## Code Review: CHANGES REQUESTED` → fix issues (5a) and re-review (5b)
- `## Code Review: APPROVED` → proceed to Step 6
- Max 2 iterations; then proceed with documented caveats

**IMPORTANT**: Do NOT proceed to Step 6 until code review is APPROVED (or max iterations reached with caveats documented).

## Step 6: Commit, Push, and Create PR

1. Determine `COMMIT_TYPE`: `fix` (bug), `feat` (feature), `chore`, `refactor`, `docs`, `test`
2. Commit and push: @../scripts/commit-and-push.sh
3. Create PR: @../scripts/create-github-pr.sh

Required env vars: `TICKET_ID`, `TITLE`, `BRANCH_NAME`, `DEFAULT_BRANCH`
Optional: `COMMIT_TYPE` (default: fix), `TICKET_URL`, `DESCRIPTION`, `STATE`, `PRIORITY`, planning variables
