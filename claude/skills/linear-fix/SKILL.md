---
name: linear-fix
description: Automated Linear ticket workflow - creates git worktrees in current repository, fixes the ticket / issue, and opens a GitHub PR
allowed-tools: Read, Bash(gh:*), Bash(linear-cli:*), Bash()
---

# Context

Automates the complete workflow for a Linear ticket ID or Linear issue URL: fetch details, create worktree, implement fix, and open PR.

**IMPORTANT**:

- ALWAYS use `linear-cli` for Linear CLI, never Linear MCP tool. Use `linear-cli --help` to see all commands.
- ALWAYS use `gh` GitHub CLI, never GitHub MCP tool. Use `gh --help` to see all commands.
- ALWAYS create a git worktree BEFORE working on the task. Use the id of the linear ticket as the worktree folder name and branch name.

# Usage

## As a command

```
/linear-fix <ticket-id-or-url>
```

## Implementation

ALWAYS follow this 4 step process:

1. Extract the ticket ID from the input (handles both formats) using @./scripts/extract-linear-issue-id.sh . Then, fetch ticket details using `linear-cli`, on both the issue fields and additional comments:
   - Issue JSON: `linear-cli issues get "$TICKET_ID" --output json`
   - Issue comments: `linear-cli comments list "$TICKET_ID"`

2. Create git worktree with ticket-based branch using @./scripts/create-git-worktree.sh . Ensure the working directory is in the worktree folder directory.

3. Implement the fix, adhering to the repository's docs and coding standards. NEVER implement the fix before creating the worktree.

4. Commit and push changes:

```bash
# Stage all changes
git add -A

# Generate commit message
COMMIT_MSG="fix($TICKET_ID): $TITLE"

# Commit
git commit -m "$COMMIT_MSG"

if [ $? -ne 0 ]; then
  echo "Error: Nothing to commit or commit failed"
  exit 1
fi

# Push to origin
echo "📤 Pushing to origin/$BRANCH_NAME"
git push -u origin "$BRANCH_NAME"
```

Create PR using GitHub CLI:

```bash
# Check if PR template exists
PR_TEMPLATE=""
if [ -f ".github/pull_request_template.md" ]; then
  PR_TEMPLATE=".github/pull_request_template.md"
elif [ -f ".github/PULL_REQUEST_TEMPLATE.md" ]; then
  PR_TEMPLATE=".github/PULL_REQUEST_TEMPLATE.md"
fi

# Generate PR body
PR_BODY="## Overview
Fixes Linear ticket: $TICKET_ID

## Description
$DESCRIPTION

## Changes
- Implemented fix for $TICKET_ID

## Linear Ticket
- [$TICKET_ID](https://linear.app/issue/$TICKET_ID)
- Status: $STATE
- Priority: $PRIORITY"

# If template exists, append it
if [ -n "$PR_TEMPLATE" ]; then
  TEMPLATE_CONTENT=$(cat "$PR_TEMPLATE")
  PR_BODY="$PR_BODY

---

$TEMPLATE_CONTENT"
fi

# Create PR
echo "🚀 Creating pull request"
gh pr create \
  --title "$COMMIT_MSG" \
  --body "$PR_BODY" \
  --base "$DEFAULT_BRANCH" \
  --head "$BRANCH_NAME"

if [ $? -eq 0 ]; then
  PR_URL=$(gh pr view --json url -q .url)
  echo ""
  echo "✅ Success! PR created: $PR_URL"
  echo ""
  echo "Next steps:"
  echo "1. Review the PR: $PR_URL"
  echo "2. Update Linear ticket: https://linear.app/issue/$TICKET_ID"
  echo "3. Worktree location: $WORKTREE_PATH"
else
  echo "Error: Failed to create PR"
  exit 1
fi
```

## Requirements

- `linear-cli` installed and authenticated
- `gh` (GitHub CLI) installed and authenticated
- `jq` for JSON parsing
- Repository must have `origin` remote configured

## Notes

- Worktrees are created in a subfolder relative to repo root `./worktrees/`
- Branch names use lowercase ticket IDs (e.g., `eng-123`)
- Commit messages follow conventional format: `fix(TICKET-ID): Title`
- PR automatically includes Linear ticket link and details
- If a PR template exists, it's appended to the generated body
