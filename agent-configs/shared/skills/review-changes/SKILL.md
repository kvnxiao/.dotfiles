---
name: review-changes
description: Review, verify, or clean up a diff, commit, branch, pull request, or selected files. Review and cleanup-suggestion requests report findings without editing; explicit cleanup or fix requests apply changes. Also run after implementation or before a commit or PR to review and apply fixes.
---

# Review changes

## Select mode and coverage

Honor explicit user constraints first, then a supplied `mode=report` or `mode=apply`. Otherwise use
this table. A self-run after implementation uses `mode=apply` explicitly.

| Request                                             | Mode   | Assessments                    |
| --------------------------------------------------- | ------ | ------------------------------ |
| Review, check, or verify a target                   | report | Correctness and simplification |
| Suggest cleanups                                    | report | Simplification                 |
| Clean up a target                                   | apply  | Simplification                 |
| Review and fix; implement and verify                | apply  | Correctness and simplification |
| Self-run after implementation or before a commit/PR | apply  | Correctness and simplification |

Run `audit-prose` whenever prose cleanup is requested, including cleanup in report mode. Mode
controls editing, not assessment coverage. Pass it explicitly to `update-docs` and `audit-prose`.

In report mode, do not edit source files, stage, commit, push, or post comments. Checks may create
disposable generated outputs in known locations; they must not rewrite source, snapshots, or
lockfiles, or mutate external services. If a check cannot meet this boundary, report it as pending.

In apply mode, only the coordinator edits files during this workflow. Subagents return findings or
proposed corrections. Commit, push, and publishing require authorization from the surrounding task;
apply mode alone does not authorize them.

## Resolve the assignment

Resolve the scope once and reuse it in every downstream call. Read applicable repository
instructions and relevant local `*-rules` skills on both paths; pass their paths with delegated
assignments.

Use this procedure for the coordinator and standalone reviews. Delegated reviewers use the supplied
assignment without resolving a different scope.

### Select the target

Honor explicit revisions, paths, and exclusions. Distinguish these two scope kinds:

- **Diff:** Review defects or costs introduced or exposed by the selected changes. Read unchanged
  code as context; keep unrelated pre-existing issues separate.
- **Snapshot:** For a request to review or clean up existing files, functions, or a design, inspect
  the complete selected artifacts. Existing defects and cleanup opportunities are in scope. A clean
  Git tree does not make a snapshot scope empty.

For a diff, use the first matching row. Resolve revision names to commit IDs before delegation.

| Target                                                 | Comparison                                                                                                                                  |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Explicit base and target                               | Use the requested endpoints or range semantics.                                                                                             |
| Commit                                                 | Compare its first parent with that commit; treat a root commit as additions.                                                                |
| Pull request                                           | Use `gh` to resolve the PR's base/head and compare their merge base with the head.                                                          |
| Branch                                                 | Compare its merge base with the requested integration branch, or the repository default branch, against its head.                           |
| Working tree, or unspecified target with local changes | Compare `HEAD` with working contents and inspect untracked files separately. Without commits, inspect index and working files as additions. |
| Unspecified target with a clean tree                   | Use an open PR's base if identifiable; otherwise use the repository default branch. Compare its merge base with `HEAD` against `HEAD`.      |

Resolve the default branch from the remote's symbolic `HEAD` or repository metadata; do not assume
the tracking upstream is the integration branch. If the base cannot be established, report the
missing base rather than selecting a historical commit. Report an empty diff only after resolving
the requested comparison. `git diff HEAD` omits untracked files; enumerate them with Git status and
read them separately. Keep unrelated working changes out of revision-based reviews.

### Record the assignment

Record the repository/worktree, scope kind, base/target IDs or working contents, selected paths,
intent, mode, assessments, applicable rule paths, and known uncertainties. Label inferred intent;
report unknown requirements instead of inventing them. Include governing `AGENTS.md`/`CLAUDE.md`
paths from the repository root through the scoped directories, plus relevant `*-rules` skills.

Keep the reviewed contents stable until reviewers return. If the user or another process changes
them, reconcile the changed scope and invalidate affected findings/checks before applying fixes.

### Choose the apply worktree

Use the current worktree for its branch or working contents. For another branch, inspect
`git worktree list` before selecting an existing worktree or creating one outside the repository.
Use `git worktree add <path> <branch>` for an available branch. For a PR, create a detached worktree
at its resolved head so another checkout is not disturbed.

Inspect status before writing in an existing worktree. Preserve unrelated edits and never reset,
stash, or overwrite them. If overlapping edits prevent applying the reviewed correction safely, use
an isolated worktree when that preserves the requested target; otherwise explain the conflict and
ask for the needed decision. Report the worktree path when fixes are applied outside the original
worktree. Do not commit or push unless the surrounding task authorizes it.

## Fast path

Choose the full path when the caller requests a comprehensive review or when any fast-path condition
is uncertain. A request to avoid subagents changes delegation, not coverage.

Use this path only for a diff where every hunk is one of:

- A typo, wording, or formatting correction in prose, comments, or docstrings that preserves meaning
  and does not change executable examples or directives.
- Documentation outside skills, prompts, agent definitions, and other instruction files, with no
  change to the behavior it describes.

Changes to test assertions, configuration, runtime code, or behavioral instructions use the full
path. Snapshot reviews also use the full path.

Perform these steps in-session without loading the full-path or reviewer contract references:

1. Inspect every scoped hunk and relevant context. For correctness, require a concrete trigger or
   conflicting repository rule. For simplification, require a specific replacement with a concrete
   benefit and preserved behavior. Check both unless this is a cleanup-only request.
2. Apply confirmed, in-scope corrections only in apply mode. Report unresolved concerns separately.
3. Run `audit-prose` with the selected mode when prose is the deliverable or prose cleanup was
   requested. For incidental wording and typo fixes, inspect the prose directly.
4. Run relevant checks as the mode permits. Report failures and checks that could not run.

If inspection reveals changed behavioral contracts, continue through the full path with the same
scope and completed work.

## Full path

Read [references/full-path.md](references/full-path.md). Cover the assigned correctness and
simplification assessments, repository rules, documentation impact, prose, and validation. Use one
independent reviewer by default; perform the same work in-session when delegation is unavailable or
the user requests it, and report that limitation.

## Finish

Finish when:

- Every required assessment is complete or has an explicit limitation.
- Findings are reconciled.
- Required checks have results or recorded blockers.

Do not describe incomplete coverage as a clean review.

Number actionable findings and retain their IDs for follow-ups. Keep unresolved concerns and check
results separate; successful checks are not findings. In apply mode, report fixes and any confirmed
findings skipped, with reasons. End with a compact scope/mode/path statement and the status of
review, fixes, documentation, prose, and validation. Mark a skipped step with its reason; omit
detailed logs unless they explain a failure.

On `fix them` or `fix 1 and 3`, switch to apply mode for the selected findings. Verify that their
evidence still matches the target, reuse the report, and review only the corrections and affected
contracts. Complete documentation, prose, and validation for those fixes without restarting
unchanged review work.
