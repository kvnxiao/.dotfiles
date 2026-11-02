---
name: update-docs
description: Update repository documentation to match a code, configuration, architecture, or behavior change. Use during review-changes or for requests to correct stale, missing, or contradictory documentation outside code comments and docstrings, or to review, compact, prune, or remove public decision records.
---

# Update docs

Before writing or delegating work, restore any brainstorm state from the conversation or continuation summary and follow [Brainstorming boundary and conclusion](../brainstorm/SKILL.md#brainstorming-boundary-and-conclusion). This rule also applies if brainstorming starts during this workflow.

Keep documentation accurate for its role under [documentation boundaries](../write-spec/references/document-boundaries.md). For decision-record maintenance, use [decisions.md](../write-spec/references/decisions.md) directly; the user's requested review or edit determines the mode, and unrelated implementation inspection is unnecessary.

## Select the mode

Honor explicit user constraints, then the caller's `mode=report` or `mode=apply`. Without a supplied mode, use report for assessment/review requests and apply for requests to update or fix docs.

- **Report:** Search and assess without editing. Return each required correction with its location, conflicting behavior, and proposed replacement. Run only checks that preserve source files.
- **Apply:** Make the scoped corrections, then verify and report them.

Keep scope and investigation the same in both modes. Report mode takes precedence over the editing steps below. A delegated report does not authorize edits.

## Scope

- Preserve the caller's resolved scope, including revisions and diff/snapshot boundaries. For a snapshot, assess selected artifacts against their authority without requiring a diff: code for implemented behavior, the approved spec for intended behavior, and stated evidence for research findings.
- If the caller names revisions, files, or a feature, use that boundary. Otherwise inspect the complete working-tree change set, including staged, unstaged, and untracked files.
- Read the repository instructions and the changed implementation before editing documentation.
- Treat hand-maintained prose outside code comments and docstrings as documentation. Include conventional documentation directories, Markdown, MDX, reStructuredText, AsciiDoc, Org, text guides, and extensionless files such as `README`, `CONTRIBUTING`, and `SECURITY`.
- Preserve necessary migration and release context and the stated conditions of empirical evidence. Maintain public records of evaluated alternatives through the decision-record format.
- Do not edit vendored or generated documentation. If generated output is stale and its documentation source is in scope, update the source. If the source is out of scope, report the required generation step.

## Determine documentation impact

Read the full scoped diff or snapshot and enough surrounding implementation to identify the behavior, interfaces, and constraints that the change adds, modifies, or removes. Check user-facing commands, flags, configuration keys, environment variables, defaults, outputs, APIs, schemas, setup procedures, compatibility boundaries, and workflows. When repository documentation describes maintainer-facing architecture, component relationships, extension points, or operational procedures, check those claims against the change. Do not infer documentation impact from filenames alone.

Do not rewrite an approved requirement to match incomplete code. Route an intentional contract change through `write-spec`; update research applicability without rewriting a valid bounded observation. Keep architecture documentation selective: correct known contradictions in scoped explanations, but do not create or synchronize detailed diagrams for every internal refactor.

## Find affected documentation

Start with the owning documents and their relevant links. Search for exact identifiers and descriptions of the affected concepts. Broaden searches when a rename, removal, cross-document contract, or other concrete dependency warrants it; do not enumerate and reread the whole corpus for every change. Follow old names and inbound links when moving or retiring content.

## Apply updates

In report mode, propose these corrections without applying them.

- Remove stale descriptions and references for removed implemented behavior; do not treat an unimplemented spec requirement as obsolete.
- When behavior changes, update descriptions, examples, defaults, prerequisites, and migration guidance.
- When new public behavior is in scope for the repository's documentation audience, document it within the existing structure.
- Keep documentation structure, terminology, and detail consistent with neighboring material.
- Limit edits to documentation affected by the target change set. Report unrelated documentation defects without changing them.
- If the implementation does not establish the correct replacement, report the conflict or unknown instead of guessing.

## Verify and report

After applying edits, verify affected claims and links. Repeat or broaden searches only where the changes could leave stale references. When the repository provides an existing documentation-specific validation command and the command fits the caller's verification workflow, run it.

Report the documentation files changed or proposed and the fact each correction describes. If no edit is needed, state the documentation-impact assessment and the documentation areas searched. List stale generated output, unresolved claims, and unrelated defects separately.
