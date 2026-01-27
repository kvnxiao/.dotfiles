---
name: git-worktree
description: Create isolated git worktrees in ~/.claude-worktrees/. Use when user says "create an isolated copy", "worktree", "create worktree", "isolated workspace", or needs to work on a branch without affecting the main working directory.
allowed-tools: Bash, Read
---

# Git Worktree

Create isolated git worktrees in `~/.claude-worktrees/<repo>/<branch>/`.

Supports `.worktreeinclude` file for copying untracked files (e.g., `.env.local`) to new worktrees.

## Usage

### Create Worktree

```bash
BRANCH_NAME="feature/my-feature" ./scripts/create-worktree.sh
# Or with ticket URL for branch naming:
BRANCH_NAME="eng-123/fix-bug" TICKET_URL="https://linear.app/team/issue/ENG-123/fix-bug" ./scripts/create-worktree.sh
# Or with custom base branch:
BRANCH_NAME="feature/my-feature" BASE_BRANCH="develop" ./scripts/create-worktree.sh
```

**Outputs** (to stdout):
- `BRANCH_NAME=<branch>` - The created branch name
- `WORKTREE_PATH=<path>` - Absolute path to worktree
- `DEFAULT_BRANCH=<branch>` - Repository's default branch

### Remove Worktree

```bash
WORKTREE_PATH="$HOME/.claude-worktrees/my-repo/my-branch" ./scripts/remove-worktree.sh
```

## .worktreeinclude

Create a `.worktreeinclude` file in your repo root to specify files that should be copied to new worktrees:

```
# Environment files
.env.local
.env.development

# Local config
config/local.json
```

Supports glob patterns via bash globbing (`**/*.local`).

## Scripts

- `create-worktree.sh` - Create worktree, copy includes
- `copy-worktree-includes.sh` - Copy files from .worktreeinclude
- `remove-worktree.sh` - Remove worktree and clean up
