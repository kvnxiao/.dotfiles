#!/bin/bash
# =============================================================================
# copy-worktree-includes.sh
# =============================================================================
# Copies files listed in .worktreeinclude from source repo to worktree.
#
# Usage:
#   SOURCE_REPO="/path/to/repo" WORKTREE_PATH="/path/to/worktree" ./copy-worktree-includes.sh
#
# Environment Variables:
#   SOURCE_REPO   - (Required) Path to original repository
#   WORKTREE_PATH - (Required) Path to destination worktree
#
# .worktreeinclude format:
#   - One pattern per line
#   - Empty lines and lines starting with # are ignored
#   - Supports glob patterns (e.g., **/*.local, config/*.json)
#
# Exit codes:
#   0 - Success (all files copied)
#   1 - Error (missing env vars, .worktreeinclude not found)
# =============================================================================

set -e

if [[ -z "$SOURCE_REPO" ]]; then
  echo "Error: SOURCE_REPO is required" >&2
  exit 1
fi

if [[ -z "$WORKTREE_PATH" ]]; then
  echo "Error: WORKTREE_PATH is required" >&2
  exit 1
fi

INCLUDE_FILE="$SOURCE_REPO/.worktreeinclude"

if [[ ! -f "$INCLUDE_FILE" ]]; then
  echo "Error: .worktreeinclude not found at $INCLUDE_FILE" >&2
  exit 1
fi

# Enable extended globbing
shopt -s globstar nullglob

cd "$SOURCE_REPO"

while IFS= read -r pattern || [[ -n "$pattern" ]]; do
  # Skip empty lines and comments
  [[ -z "$pattern" || "$pattern" =~ ^[[:space:]]*# ]] && continue

  # Trim whitespace
  pattern=$(echo "$pattern" | xargs)

  # Expand glob pattern
  for file in $pattern; do
    if [[ -f "$file" ]]; then
      # Get directory part of the file path
      dir=$(dirname "$file")

      # Create destination directory if needed
      if [[ "$dir" != "." ]]; then
        mkdir -p "$WORKTREE_PATH/$dir"
      fi

      # Copy file preserving relative path
      cp "$file" "$WORKTREE_PATH/$file"
      echo "  Copied: $file" >&2
    fi
  done
done < "$INCLUDE_FILE"
