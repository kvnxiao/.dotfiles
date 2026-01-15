---
name: linear-fix
description: Autonomously completes Linear tickets via git worktrees. Use when user says "fix ENG-123", "complete LIN-456", "work on linear ticket", provides a linear.app URL, or mentions a ticket ID pattern like ABC-1234. Creates git worktree, implements fix via autonomous planning/review loop, opens GitHub PR with full reasoning.
allowed-tools: Read, Bash, Grep, Glob, Task
---

# Linear Fix

Autonomous Linear ticket completion: fetch issue → create worktree → plan → review → implement → PR.

**CRITICAL**: Create git worktree BEFORE implementation. Use ticket ID as worktree folder/branch name.

## Usage

```bash
/linear-fix <ticket-id-or-url>
```

## Workflow

Follow 6 steps in @./references/workflow.md:

1. **Gather Context** - Extract ticket ID, fetch details via `linear-cli`. Use the other Linear CLI skills for additional context:
   - `/linear-issues` - fetch issue details
   - `/linear-search` - search issues
   - `/linear-uploads` - download attachments (images, files)
2. **Create Worktree** - Run @./scripts/create-git-worktree.sh, cd into it, install deps
3. **Plan** - Task tool with `subagent_type=Plan`, use @./references/planner-prompt.md
4. **Review** - Task tool with `subagent_type=feature-dev:code-architect`, use @./references/reviewer-prompt.md
5. **Implement & Review** - Execute approved plan, then `subagent_type=feature-dev:code-reviewer` with @./references/code-reviewer-prompt.md
6. **Create PR** - Run @./scripts/commit-and-push.sh then @./scripts/create-github-pr.sh

## Autonomous Loops

**Planning Loop (Steps 3-4):**

- Planner proposes 2-3 approaches → Architect reviews → revise if needed
- Max 3 iterations; then select best available with caveats

**Implementation Loop (Step 5):**

- Implement → Code reviewer reviews → fix if needed
- Max 2 iterations; then proceed with caveats

**IMPORTANT**: Only proceed to Step 6 (Create PR) after code review is APPROVED. All reasoning captured in PR body under collapsible section.
