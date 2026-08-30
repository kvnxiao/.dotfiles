---
name: verify-changes
description: Verify the working-tree change set before a commit or PR. Reviews the full diff for correctness, finds simplification candidates, checks repository rules, updates affected documentation, audits prose, and runs repository checks. Use when an implementation is finished, or when the user says "commit for me", "open a PR", "push this", "are we done".
---

# Verify changes

Consider the proportionality of the changes and run the following checklist over the working-tree change set.

1. [ ] Gather read-only review reports in parallel:
   - [ ] 1a. Review the full diff as a skeptical second reader. Verify correctness and edge cases, and confirm only intended lines changed. Use the `code-review` skill (if available) in a subagent.
   - [ ] 1b. Find dead code, needless indirection, and incidental complexity that can be removed without changing behavior. Use the `simplify` skill (if available) in a subagent.
   - [ ] 1c. **Check compliance against repo-specific rules and standards:**
     - Inspect available local skills with names matching `*-rules` (e.g., `python-rules`, `react-rules`, `architecture-rules`).
     - If matching rules exist for the languages, frameworks, or layers touched by the diff, invoke them in a read-only subagent to verify adherence to local conventions.
2. [ ] Deduplicate the reports from step 1, resolve overlaps, and apply accepted changes in one edit pass. Review the resulting full diff.
3. [ ] Update repository documentation for the accumulated change set. Use the `update-docs` skill in a subagent with write access limited to documentation files. The subagent must determine the change's documentation impact, search the full documentation corpus, apply required documentation edits directly, and report any unresolved or out-of-scope findings. Review its edits before continuing.
4. [ ] Audit every comment, docstring, and documentation line the change set added or modified, including prose written during steps 2 and 3. If your skill list offers `audit-prose-via-codex`, invoke it; it is already an independent pass, so do not wrap it in a subagent. Otherwise use the `audit-prose` skill in a subagent.
5. [ ] Run the formatting, linting, type-checking, and test commands that are relevant and proportionate to the change. Step 4 runs none of them.

Parallel subagents used for step 1's review coverage must be restricted to read-only access. Reviewers must report findings without editing files or running mutating commands. Only the coordinating agent may edit the working tree except for the `update-docs` subagent in step 3 and the prose audit in step 4. Run the mutating subagents sequentially: `update-docs` applies documentation changes before the prose audit reviews the accumulated prose.

List anything you found but did not fix, with the reason. State what you could not verify.

## Proportionality

Scale the review steps to the scope, risk, and runtime blast radius of the diff. Do not run full semantic or correctness reviews on changes that cannot alter execution behavior.

| Change Scope                      | Required Steps                                                 | Bypassed Steps                                | Bypass Criteria                                                                      |
| :-------------------------------- | :------------------------------------------------------------- | :-------------------------------------------- | :----------------------------------------------------------------------------------- |
| **Logic & Runtime Code**          | `1a`, `1b`, `1c` (if matching rules exist), `2`, `3`, `4`, `5` | None                                          | Edits modifying execution flow, state, schemas, APIs, or business logic.             |
| **Prose & Documentation**         | `4` and formatter from `5`                                     | `1a`, `1b`, `1c`, `2`, `3`, type-check, tests | Markdown, text files, or standalone docs that do not affect build or execution.      |
| **Cosmetic & Trivial Fixes**      | `4`, lint and format from `5`                                  | `1a`, `1b`, `1c`, `2`, `3`, tests             | Variable renames, comments, or typos with zero semantic or behavioral impact.        |
| **Declarative Config & Dotfiles** | `3`, `4`, format and lint from `5`                             | `1a`, `1b`, `1c`, `2`, tests                  | Linter configs, `.gitignore`, or tooling presets that do not alter runtime behavior. |
| **Behavioral Config & CI/CD**     | `1a`, `1c` (if applicable), `2`, `3`, `4`, `5`                 | `1b`                                          | Build pipelines, routing, infra manifests, or runtime environment configs.           |
| **Dependency Updates**            | `3`, `5` (build, types, tests)                                 | `1a`, `1b`, `1c`, `2`, `4`                    | Package updates or lockfile changes without manual application logic edits.          |

### Bypass Rules

- **Silent Rule Skips:** If no local `*-rules` skills match the touched languages, frameworks, or ideas, skip `1c` silently.
- **Reporting Requirement:** If any non-silent step is bypassed based on the matrix above, explicitly state which step was skipped and why in your final summary.

## Boundaries

- Do not repair problems outside the change set. List them for the user instead.
- Do not repeat a passed review or check when its inputs have not changed.
- Commit the changes only if the original intent was to mark a task complete and commit / push to a PR.
