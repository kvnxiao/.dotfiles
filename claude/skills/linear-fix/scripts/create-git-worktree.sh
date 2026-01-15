#!/bin/bash
# =============================================================================
# create-git-worktree.sh
# =============================================================================
# Creates a git worktree for working on a Linear ticket in isolation.
#
# Usage:
#   TICKET_ID="ENG-123" ./create-git-worktree.sh
#
# Required environment variables:
#   TICKET_ID - The Linear ticket ID (e.g., "ENG-123")
#
# Outputs (to stdout, one per line):
#   BRANCH_NAME=<branch>       - Branch name in format "[username]/[ticket-lowercase]"
#   WORKTREE_PATH=<path>       - Absolute path to created worktree
#   DEFAULT_BRANCH=<branch>    - The repository's default branch (e.g., "main")
#
# Exit codes:
#   0 - Success (worktree created)
#   1 - Failed to create worktree
#
# Note: Caller must cd to WORKTREE_PATH after running this script
#
# Example:
#   TICKET_ID="ENG-123" ./create-git-worktree.sh
#   # Creates worktree, outputs:
#   # BRANCH_NAME=kevin/eng-123
#   # WORKTREE_PATH=/path/to/repo/worktrees/eng-123
#   # DEFAULT_BRANCH=main
# =============================================================================

# Generate branch name: [username]/[ticket-id-lowercase]
OS_USER=$(whoami)
TICKET_LOWER=$(echo "$TICKET_ID" | tr '[:upper:]' '[:lower:]')
BRANCH_NAME="${OS_USER}/${TICKET_LOWER}"
WORKTREE_PATH="$(pwd)/worktrees/$TICKET_LOWER"

# Get the default branch name
DEFAULT_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)

# Create worktree
echo "🌳 Creating worktree at $WORKTREE_PATH" >&2
if ! git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" "origin/$DEFAULT_BRANCH"; then
  echo "Error: Failed to create worktree" >&2
  exit 1
fi

echo "✅ Worktree created at $WORKTREE_PATH" >&2

# Output variables for caller to capture
echo "BRANCH_NAME=$BRANCH_NAME"
echo "WORKTREE_PATH=$WORKTREE_PATH"
echo "DEFAULT_BRANCH=$DEFAULT_BRANCH"
