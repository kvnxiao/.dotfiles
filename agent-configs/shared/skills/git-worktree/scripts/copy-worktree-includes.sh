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

cd "$SOURCE_REPO"

# Convert glob pattern to find arguments
find_matches() {
  local pattern="$1"

  if [[ "$pattern" == *"**"* ]]; then
    # Recursive glob: **/*.local -> -name "*.local"
    local name_pattern="${pattern##**/}"
    find . -name "$name_pattern" -type f 2>/dev/null | sed 's|^\./||'
  elif [[ "$pattern" == *"*"* ]]; then
    # Simple glob in current dir or specific path
    local dir_part=$(dirname "$pattern")
    local name_part=$(basename "$pattern")
    if [[ "$dir_part" == "." ]]; then
      find . -maxdepth 1 -name "$name_part" -type f 2>/dev/null | sed 's|^\./||'
    else
      find "$dir_part" -maxdepth 1 -name "$name_part" -type f 2>/dev/null | sed 's|^\./||'
    fi
  elif [[ -f "$pattern" ]]; then
    # Exact file match
    echo "$pattern"
  elif [[ -d "$pattern" ]]; then
    # Directory - mark with trailing slash
    echo "$pattern/"
  fi
}

while IFS= read -r pattern || [[ -n "$pattern" ]]; do
  # Skip empty lines and comments
  [[ -z "$pattern" || "$pattern" =~ ^[[:space:]]*# ]] && continue

  # Trim whitespace
  pattern=$(echo "$pattern" | xargs)

  # Find matching items
  find_matches "$pattern" | while IFS= read -r item; do
    [[ -z "$item" ]] && continue

    if [[ "$item" == */ ]]; then
      # Directory (trailing slash)
      item="${item%/}"
      mkdir -p "$WORKTREE_PATH/$item"
      cp -r "$item/." "$WORKTREE_PATH/$item/"
      echo "  Copied: $item/ (directory)" >&2
    else
      # File
      dir=$(dirname "$item")
      if [[ "$dir" != "." ]]; then
        mkdir -p "$WORKTREE_PATH/$dir"
      fi
      cp "$item" "$WORKTREE_PATH/$item"
      echo "  Copied: $item" >&2
    fi
  done
done < "$INCLUDE_FILE"
