---
name: completion-check
description: Run a completion checklist over the current change set when work is considered done and ready to commit. Checks for correctness, simplification candidates, comment and prose audits, and repository-specific checks. Use before marking a task complete, e.g. before committing or pushing to open a PR, or when the user says "commit for me", "open a PR", "are we done".
---

# Completion check

Consider the proportionality of the changes and run the following checklist over the working-tree change set.

1. [ ] Gather read-only review reports in parallel:
   - [ ] 1a. Review the full diff as a skeptical second reader. Verify correctness and edge cases, and confirm only intended lines changed. Use the `code-review` skill (if available) in a subagent.
   - [ ] 1b. Find dead code, needless indirection, and incidental complexity that can be removed without changing behavior. Use the `simplify` skill (if available) in a subagent.
2. [ ] Deduplicate the reports, resolve overlaps, and apply accepted changes in one edit pass. Review the resulting full diff.
3. [ ] Audit every comment, docstring, and documentation line the change set added or modified, including prose written during step 2. Use the `prose-check` skill in a subagent.
4. [ ] Run the repository checks relevant and proportionate to the change: formatting, linting, type-checking, and tests when applicable.

Parallel subagents used for Step 1's review coverage must be restricted to read-only access. Reviewers must report findings without editing files or running mutating commands. Only the coordinating agent may edit the working tree. Step 3's prose audits also use subagents, but these are allowed to directly apply changes.

List anything you found but did not fix, with the reason. State what you could not verify.

## Proportionality

| Change class            | Steps to run                                              |
| ----------------------- | --------------------------------------------------------- |
| Code                    | 1a, 1b, 2, 3, 4                                           |
| Prose and documentation | 3, and the formatter from 4                               |
| Config and dotfiles     | 3 and 4, plus 1a and 2 when the config controls behaviour |
| Dependency bump         | 4                                                         |

A three-line documentation edit does not need a correctness review. Say what you skipped and why.

## Boundaries

- Do not repair problems outside the change set. List them for the user instead.
- Do not repeat a passed review or check when its inputs have not changed.
- Commit the changes only if the original intent was to mark a task complete and commit / push to a PR.
