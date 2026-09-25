---
name: verify-changes
description: Verify changes before a commit or PR with review and checks proportional to risk. Use when an implementation is finished, or when the user says "commit for me", "open a PR", "push this", or "are we done".
---

# Verify changes

Resolve the review scope once. Honor caller-supplied revisions and paths; otherwise:

- Review staged and unstaged changes against `HEAD`, plus untracked files reported by
  `git status --porcelain`.
- In a repository without commits, inspect the index and working files as additions.
- When the working tree is clean, review commits ahead of the upstream branch, or the default branch
  when no upstream exists. If no commits are ahead, report an empty scope.

Pass the resolved repository, base revision, file scope, and intended change to every downstream
skill and reviewer. Keep unrelated changes outside that scope.

Choose the verification path by potential consequences and unresolved uncertainty, not file or line
counts. Escalate when investigation reveals broader effects.

## 1. Fast-Path (Lightweight & Trivial Edits)

**Criteria:** Low-risk, localized edits with no architectural or runtime impact—such as fixing
typos, editing comments or docstrings, updating isolated test assertions, narrow documentation
fixes, or adding/removing an isolated configuration field.

**Action:** Complete verification directly in the main session without subagents:

1. **Review Diff:** Check the scoped diff directly for correctness, unintended edits, and clear
   prose.
2. **Focused Checks:** Run relevant formatters, linters, or the affected test in the main session.
3. **Finish:** Report the result and material verification gaps, then continue the authorized task.
   Do not spawn subagents or load full-review instructions unless the risk assessment changes.

## 2. Full Review

**Criteria:** Changes affecting behavioral contracts or requiring broader investigation, including:

- Execution flow, runtime state, or persisted data.
- Public APIs, security, compatibility, or shared configuration.
- Structural refactors or unresolved design choices.

**Action:** Read [references/full-review.md](references/full-review.md). Preserve coverage of
correctness, simplification, repository rules, documentation, prose, and validation; scale
delegation and investigation to the risk.
