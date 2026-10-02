---
name: review-changes
description: Review, verify, or clean up changes with review and checks proportional to risk. Use when the user asks to review, check, or verify a diff, commit, branch, pull request, or files, or asks for cleanup suggestions; these requests report findings without editing. Also run it when an implementation is finished or before committing or opening a PR, to apply fixes.
---

# Review changes

## Select the mode

Select the mode before resolving scope. A `mode=report` or `mode=apply` argument overrides the
request; otherwise:

- **Report:** The user's request asks to review, check, or verify changes, or asks for cleanup
  suggestions, even when you implemented those changes. Do not edit the working tree, stage, or
  commit.
- **Apply:** You run this skill when you finish an implementation or before you commit or open a PR,
  or the user explicitly asks for fixes (`review and fix PR #12`). Apply fixes, documentation
  updates, and prose corrections, then validate, in the same pass. A verification step inside a
  request to implement (`implement X and verify it works`) runs in apply mode.

The mode changes only each step's action and the final output. Choose the verification path the same
way in both modes.

Use [references/correctness-review.md](references/correctness-review.md) for reviews and
verification, and [references/simplify-review.md](references/simplify-review.md) instead for a
cleanup request. The full review assigns the selected contract to a reviewer; the fast path applies
it through the diff review.

## Resolve the scope

Resolve the review scope once. Honor caller-supplied revisions and paths; otherwise:

- Review staged and unstaged changes against `HEAD`, plus untracked files reported by
  `git status --porcelain`.
- In a repository without commits, inspect the index and working files as additions.
- When the working tree is clean, review commits ahead of the upstream branch, or the default branch
  when no upstream exists. If no commits are ahead, report an empty scope.

In apply mode, apply fixes in place when the target is the current branch or working tree. When
another worktree already has the target branch checked out, apply the fixes there. Otherwise, check
out the target in a new worktree outside the repository, then apply and validate there:

- For a branch, run `git worktree add <path> <branch>`.
- For a pull request, run `git worktree add --detach <path>`, then `gh pr checkout <number>` inside
  it.

Report the worktree path, its branch, and whether the fixes are committed.

Pass the resolved repository, base revision, file scope, mode, and intended change to every
downstream skill and reviewer. Keep unrelated changes outside that scope.

Choose the verification path by potential consequences and unresolved uncertainty, not file or line
counts. Escalate when investigation reveals broader effects. Use the full review when the user asks
for a full or comprehensive review. When the caller asks to review in-session or without subagents,
perform the assigned checks in the main session and report the lack of an independent review.

## 1. Fast-Path (Lightweight & Trivial Edits)

**Criteria:** Low-risk, localized edits with no architectural or runtime impact—such as fixing
typos, editing comments or docstrings, updating isolated test assertions, narrow documentation
fixes, or adding/removing an isolated configuration field. A document rewrite with no runtime impact
also stays on this path, with the prose audit below.

**Action:** Complete verification directly in the main session without subagents:

1. **Review Diff:** Check the scoped diff directly for correctness, unintended edits, and clear
   prose. For a cleanup request, check it against the simplification contract instead.
2. **Audit Prose When It Is the Deliverable:** Run `audit-prose` when the requested output is prose:
   the user asked to write, rewrite, or restructure a document, or the change adds a new document or
   section. Skip it when prose edits accompany a code change or are typo, wording, or
   single-sentence fixes; the diff review covers those. In report mode, list its corrections as
   findings instead of applying them.
3. **Focused Checks:** Run relevant formatters, linters, or the affected test in the main session.
   In report mode, run only checks that do not modify tracked or source files, such as tests and
   formatters in check mode.
4. **Finish:** Report the result and material verification gaps. In apply mode, continue the
   authorized task. Do not spawn subagents or load full-review instructions unless the risk
   assessment changes.

## 2. Full Review

**Criteria:** Changes affecting behavioral contracts or requiring broader investigation, including:

- Execution flow, runtime state, or persisted data.
- Public APIs, security, compatibility, or shared configuration.
- Structural refactors or unresolved design choices.

**Action:** Read [references/full-review.md](references/full-review.md). Preserve coverage of
correctness, simplification, repository rules, documentation, prose, and validation; scale
delegation and investigation to the risk.

## Report Findings

In report mode, number each finding, including documentation, prose, and check results, so the user
can reply `fix them` or `fix 1 and 3`. On that reply, switch to apply mode for the selected findings
and reuse the report instead of repeating the review. Re-review only the code the fixes touch, then
run the remaining apply-mode steps on those fixes.
