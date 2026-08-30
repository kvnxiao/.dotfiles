---
name: update-docs
description: Update repository documentation to match a code, configuration, architecture, or behavior change. Use for documentation maintenance delegated by `verify-changes`, and for requests to find and correct stale, missing, or contradictory documentation outside code comments and docstrings.
---

# Update docs

Keep the repository's documentation accurate for the target change set.

## Scope

- If the caller names revisions, files, or a feature, use that boundary. Otherwise inspect the complete working-tree change set, including staged, unstaged, and untracked files.
- Read the repository instructions and the changed implementation before editing documentation.
- Treat hand-maintained prose outside code comments and docstrings as documentation. Include conventional documentation directories, Markdown, MDX, reStructuredText, AsciiDoc, Org, text guides, and extensionless files such as `README`, `CONTRIBUTING`, and `SECURITY`.
- When historical release notes or migration records claim to describe current behavior, update them; otherwise preserve them.
- Do not edit vendored or generated documentation. If generated output is stale and its documentation source is in scope, update the source. If the source is out of scope, report the required generation step.

## Determine documentation impact

Read the full diff and enough surrounding implementation to identify the behavior, interfaces, and constraints that the change adds, modifies, or removes. Check user-facing commands, flags, configuration keys, environment variables, defaults, outputs, APIs, schemas, setup procedures, compatibility boundaries, and workflows. When repository documentation describes maintainer-facing architecture, component relationships, extension points, or operational procedures, check those claims against the change. Do not infer documentation impact from filenames alone.

Unless standalone documentation describes the changed design or mechanism, an internal refactor does not require a documentation edit.

## Search the documentation corpus

Enumerate the entire repository documentation corpus before selecting files to edit. Search every candidate rather than limiting the search to changed files or documentation beside the implementation.

Search for exact identifiers and for prose that describes the affected concepts without naming them. For removed or renamed behavior, search for former names, examples, defaults, output text, and conceptual descriptions that can remain stale after exact-name matches are gone. Read each match in context and follow local links to related documentation.

## Apply updates

- Remove claims, examples, navigation entries, and cross-references for behavior that no longer exists.
- When behavior changes, update descriptions, examples, defaults, prerequisites, and migration guidance.
- When new public behavior is in scope for the repository's documentation audience, document it within the existing structure.
- Keep documentation structure, terminology, and detail consistent with neighboring material.
- Limit edits to documentation affected by the target change set. Report unrelated documentation defects without changing them.
- If the implementation does not establish the correct replacement, report the conflict or unknown instead of guessing.

## Verify and report

After editing, search the full documentation corpus again for stale names and conceptual descriptions. When the repository provides an existing documentation-specific validation command and the command fits the caller's verification workflow, run it.

Report the documentation files changed and the fact each edit now describes. If no edit is needed, state the documentation-impact assessment and the documentation areas searched. List stale generated output, unresolved claims, and unrelated defects separately.
