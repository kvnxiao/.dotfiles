#!/bin/bash
# =============================================================================
# remove-worktree.sh
# =============================================================================
# Removes a git worktree and cleans up empty parent directories.
#
# Usage:
#   WORKTREE_PATH="$HOME/.claude-worktrees/my-repo/my-branch" ./remove-worktree.sh
#
# Environment Variables:
#   WORKTREE_PATH - (Required) Path to the worktree to remove
#
# Exit codes:
#   0 - Success
#   1 - Error (missing WORKTREE_PATH, removal failed)
# =============================================================================

set -e

if [[ -z "$WORKTREE_PATH" ]]; then
  echo "Error: WORKTREE_PATH is required" >&2
  exit 1
fi

if [[ ! -d "$WORKTREE_PATH" ]]; then
  echo "Error: Worktree path does not exist: $WORKTREE_PATH" >&2
  exit 1
fi

echo "🗑️  Removing worktree at $WORKTREE_PATH" >&2

# Remove the worktree
git worktree remove "$WORKTREE_PATH" --force

echo "✅ Worktree removed" >&2

# Clean up empty parent directories in ~/.claude-worktrees/
PARENT_DIR=$(dirname "$WORKTREE_PATH")
WORKTREES_BASE="$HOME/.claude-worktrees"

# Remove empty parent directories up to (but not including) ~/.claude-worktrees
while [[ "$PARENT_DIR" != "$WORKTREES_BASE" && "$PARENT_DIR" != "$HOME" && "$PARENT_DIR" != "/" ]]; do
  if [[ -d "$PARENT_DIR" ]] && [[ -z "$(ls -A "$PARENT_DIR")" ]]; then
    rmdir "$PARENT_DIR"
    echo "  Removed empty directory: $PARENT_DIR" >&2
    PARENT_DIR=$(dirname "$PARENT_DIR")
  else
    break
  fi
done
