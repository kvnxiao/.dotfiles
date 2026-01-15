#!/bin/bash
# =============================================================================
# create-github-pr.sh
# =============================================================================
# Creates a GitHub pull request with Linear ticket details and planning reasoning.
#
# Usage:
#   ./create-github-pr.sh  (with required env vars set)
#
# Required environment variables:
#   TICKET_ID      - The Linear ticket ID (e.g., "ENG-123")
#   TITLE          - Short description for PR title
#   BRANCH_NAME    - Source branch for the PR
#   DEFAULT_BRANCH - Target branch (e.g., "main")
#
# Optional environment variables (ticket metadata):
#   COMMIT_TYPE    - Conventional commit type (default: "fix")
#   TICKET_URL     - Linear ticket URL (from linear-cli JSON output)
#   DESCRIPTION    - Ticket description
#   STATE          - Ticket state (e.g., "In Progress")
#   PRIORITY       - Ticket priority (e.g., "High")
#   WORKTREE_PATH  - Path to worktree (for success message)
#
# Optional environment variables (autonomous planning):
#   SELECTED_APPROACH  - Name of the selected implementation approach
#   REVIEW_REASONING   - Why this approach was selected
#   TRADEOFFS_ACCEPTED - Trade-offs accepted in this approach
#   EDGE_CASES         - Edge cases handled
#   ITERATION_COUNT    - Number of planning iterations
#
# PR body includes:
#   - Overview and description
#   - Linear ticket link with status/priority
#   - Collapsible planning reasoning section
#   - Repository PR template (if exists)
#
# Exit codes:
#   0 - Success (PR created)
#   1 - Missing required env vars or gh pr create failed
#
# Example:
#   TICKET_ID="ENG-123" TITLE="Fix bug" BRANCH_NAME="kevin/eng-123" \
#   DEFAULT_BRANCH="main" ./create-github-pr.sh
# =============================================================================

if [ -z "$TICKET_ID" ] || [ -z "$TITLE" ] || [ -z "$BRANCH_NAME" ] || [ -z "$DEFAULT_BRANCH" ]; then
  echo "Error: TICKET_ID, TITLE, BRANCH_NAME, and DEFAULT_BRANCH must be set" >&2
  exit 1
fi

# Default commit type to "fix" if not specified
COMMIT_TYPE="${COMMIT_TYPE:-fix}"
PR_TITLE="$COMMIT_TYPE($TICKET_ID): $TITLE"

# Check if PR template exists
PR_TEMPLATE=""
if [ -f ".github/pull_request_template.md" ]; then
  PR_TEMPLATE=".github/pull_request_template.md"
elif [ -f ".github/PULL_REQUEST_TEMPLATE.md" ]; then
  PR_TEMPLATE=".github/PULL_REQUEST_TEMPLATE.md"
fi

# Generate PR body with planning reasoning
PR_BODY="## Overview
Fixes Linear ticket: $TICKET_ID

## Description
$DESCRIPTION

## Changes
- Implemented fix for $TICKET_ID

## Linear Ticket
- [$TICKET_ID](${TICKET_URL:-https://linear.app/issue/$TICKET_ID})
- Status: $STATE
- Priority: $PRIORITY

<details>
<summary>🤖 Autonomous Planning Reasoning</summary>

### Selected Approach
$SELECTED_APPROACH

### Why This Approach
$REVIEW_REASONING

### Trade-offs Accepted
$TRADEOFFS_ACCEPTED

### Edge Cases Handled
$EDGE_CASES

### Planning Iterations
$ITERATION_COUNT iteration(s) before approval

</details>"

# If template exists, append it
if [ -n "$PR_TEMPLATE" ]; then
  TEMPLATE_CONTENT=$(cat "$PR_TEMPLATE")
  PR_BODY="$PR_BODY

---

$TEMPLATE_CONTENT"
fi

# Create PR
echo "🚀 Creating pull request"
if gh pr create --title "$PR_TITLE" --body "$PR_BODY" --base "$DEFAULT_BRANCH" --head "$BRANCH_NAME"; then
  PR_URL=$(gh pr view --json url -q .url)
  echo ""
  echo "✅ Success! PR created: $PR_URL"
  echo ""
  echo "Next steps:"
  echo "1. Review the PR: $PR_URL"
  echo "2. Update Linear ticket: ${TICKET_URL:-$TICKET_ID}"
  echo "3. Worktree location: $WORKTREE_PATH"
else
  echo "Error: Failed to create PR"
  exit 1
fi
