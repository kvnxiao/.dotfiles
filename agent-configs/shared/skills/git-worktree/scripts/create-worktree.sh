#!/bin/bash
# =============================================================================
# create-worktree.sh
# =============================================================================
# Creates a git worktree in ~/.claude-worktrees/<repo>/<branch>/ for isolated work.
#
# Usage:
#   BRANCH_NAME="feature/my-feature" ./create-worktree.sh
#   BRANCH_NAME="eng-123/fix-bug" TICKET_URL="https://linear.app/..." ./create-worktree.sh
#   BRANCH_NAME="feature/x" BASE_BRANCH="develop" ./create-worktree.sh
#
# Environment Variables:
#   BRANCH_NAME  - (Required) The branch name to create
#   TICKET_URL   - (Optional) Linear ticket URL; extracts slug for branch suffix
#   BASE_BRANCH  - (Optional) Base branch to branch from; defaults to origin HEAD
#
# Outputs (to stdout, one per line):
#   BRANCH_NAME=<branch>       - Branch name created
#   WORKTREE_PATH=<path>       - Absolute path to created worktree
#   DEFAULT_BRANCH=<branch>    - The repository's default branch
#
# Exit codes:
#   0 - Success
#   1 - Error (missing BRANCH_NAME, not in git repo, worktree creation failed)
#
# Note: If .worktreeinclude exists, files listed will be copied to worktree
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "$BRANCH_NAME" ]]; then
  echo "Error: BRANCH_NAME is required" >&2
  exit 1
fi

# Get repo root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [[ -z "$REPO_ROOT" ]]; then
  echo "Error: Not in a git repository" >&2
  exit 1
fi

# Extract repo name from remote URL
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [[ -z "$REMOTE_URL" ]]; then
  # Fallback to directory name if no remote
  REPO_NAME=$(basename "$REPO_ROOT")
else
  # Extract repo name from URL (handles both HTTPS and SSH formats)
  REPO_NAME=$(basename -s .git "$REMOTE_URL")
fi

# Get default branch
DEFAULT_BRANCH="${BASE_BRANCH:-$(git remote show origin 2>/dev/null | grep 'HEAD branch' | cut -d' ' -f5)}"
if [[ -z "$DEFAULT_BRANCH" ]]; then
  DEFAULT_BRANCH="main"
fi

# Compute worktree path: ~/.claude-worktrees/<repo>/<branch>
# Replace slashes in branch name with dashes for directory name
BRANCH_DIR=$(echo "$BRANCH_NAME" | tr '/' '-')
WORKTREE_PATH="$HOME/.claude-worktrees/$REPO_NAME/$BRANCH_DIR"

# Create worktree
echo "🌳 Creating worktree at $WORKTREE_PATH" >&2
if ! git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" "origin/$DEFAULT_BRANCH" >&2 2>&1; then
  echo "Error: Failed to create worktree" >&2
  exit 1
fi

# Copy .worktreeinclude files if present
if [[ -f "$REPO_ROOT/.worktreeinclude" ]]; then
  echo "📦 Copying files from .worktreeinclude..." >&2
  SOURCE_REPO="$REPO_ROOT" WORKTREE_PATH="$WORKTREE_PATH" "$SCRIPT_DIR/copy-worktree-includes.sh"
fi

echo "✅ Worktree created at $WORKTREE_PATH" >&2
echo "" >&2
echo "📦 Remember to install dependencies in the new worktree:" >&2
echo "   cd $WORKTREE_PATH && <package-manager> install" >&2

# Output variables for caller to capture
echo "BRANCH_NAME=$BRANCH_NAME"
echo "WORKTREE_PATH=$WORKTREE_PATH"
echo "DEFAULT_BRANCH=$DEFAULT_BRANCH"
