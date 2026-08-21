---
name: verify-changes
description: Verify the working-tree change set before a commit or PR. Reviews the full diff for correctness, finds simplification candidates, checks compliance against repo-local `*-rules` skills, audits every comment and doc line through audit-prose, and runs repo format, lint, type-check, and test commands. Use when an implementation is finished, or when the user says "commit for me", "open a PR", "push this", "are we done".
---

# Verify changes

Consider the proportionality of the changes and run the following checklist over the working-tree change set.

1. [ ] Gather read-only review reports in parallel:
   - [ ] 1a. Review the full diff as a skeptical second reader. Verify correctness and edge cases, and confirm only intended lines changed. Use the `code-review` skill (if available) in a subagent.
   - [ ] 1b. Find dead code, needless indirection, and incidental complexity that can be removed without changing behavior. Use the `simplify` skill (if available) in a subagent.
   - [ ] 1c. **Check compliance against repo-specific rules and standards:**
     - Inspect available local skills with names matching `*-rules` (e.g., `python-rules`, `react-rules`, `architecture-rules`).
     - If matching rules exist for the languages, frameworks, or layers touched by the diff, invoke them in a read-only subagent to verify adherence to local conventions.
2. [ ] Deduplicate the reports (from 1a, 1b, and 1c), resolve overlaps, and apply accepted changes in one edit pass. Review the resulting full diff.
3. [ ] Audit every comment, docstring, and documentation line the change set added or modified, including prose written during step 2. Use the `audit-prose` skill in a subagent.
4. [ ] Run the repository checks relevant and proportionate to the change: formatting, linting, type-checking, and tests when applicable.

Parallel subagents used for Step 1's review coverage (1a, 1b, 1c) must be restricted to read-only access. Reviewers must report findings without editing files or running mutating commands. Only the coordinating agent may edit the working tree. Step 3's prose audits also use subagents, but these are allowed to directly apply changes.

List anything you found but did not fix, with the reason. State what you could not verify.

## Proportionality

Scale the review steps to the scope, risk, and runtime blast radius of the diff. Do not run full semantic or correctness reviews on changes that cannot alter execution behavior.

| Change Scope                      | Required Steps                                            | Bypassed Steps                           | Bypass Criteria                                                                      |
| :-------------------------------- | :-------------------------------------------------------- | :--------------------------------------- | :----------------------------------------------------------------------------------- |
| **Logic & Runtime Code**          | `1a`, `1b`, `1c` (if matching rules exist), `2`, `3`, `4` | None                                     | Edits modifying execution flow, state, schemas, APIs, or business logic.             |
| **Prose & Documentation**         | `3`, and formatter from `4`                               | `1a`, `1b`, `1c`, `2`, type-check, tests | Markdown, text files, or standalone docs that do not affect build or execution.      |
| **Cosmetic & Trivial Fixes**      | `3`, lint & format from `4`                               | `1a`, `1b`, `1c`, `2`, tests             | Variable renames, comments, or typos with zero semantic or behavioral impact.        |
| **Declarative Config & Dotfiles** | `3`, format & lint from `4`                               | `1a`, `1b`, `1c`, `2`, tests             | Linter configs, `.gitignore`, or tooling presets that do not alter runtime behavior. |
| **Behavioral Config & CI/CD**     | `1a`, `1c` (if applicable), `2`, `3`, `4`                 | `1b`                                     | Build pipelines, routing, infra manifests, or runtime environment configs.           |
| **Dependency Updates**            | `4` (build, types, tests)                                 | `1a`, `1b`, `1c`, `2`, `3`               | Package updates or lockfile changes without manual application logic edits.          |

### Bypass Rules

- **Silent Rule Skips:** If no local `*-rules` skills match the touched languages, frameworks, or ideas, skip `1c` silently.
- **Reporting Requirement:** If any non-silent step is bypassed based on the matrix above, explicitly state which step was skipped and why in your final summary.

## Boundaries

- Do not repair problems outside the change set. List them for the user instead.
- Do not repeat a passed review or check when its inputs have not changed.
- Commit the changes only if the original intent was to mark a task complete and commit / push to a PR.
