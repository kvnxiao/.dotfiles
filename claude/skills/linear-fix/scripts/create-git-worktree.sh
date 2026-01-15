#!/bin/bash
# Generate branch name from ticket ID (lowercase)
BRANCH_NAME=$(echo "$TICKET_ID" | tr '[:upper:]' '[:lower:]')
WORKTREE_PATH="./worktrees/$BRANCH_NAME"

# Get the default branch name
DEFAULT_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)

# Create worktree
echo "🌳 Creating worktree at $WORKTREE_PATH"
git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" "origin/$DEFAULT_BRANCH"

if [ $? -ne 0 ]; then
  echo "Error: Failed to create worktree"
  exit 1
fi

cd "$WORKTREE_PATH" || exit 1
echo "✅ Worktree created and switched to $WORKTREE_PATH"
