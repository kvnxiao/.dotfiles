# Development Guidelines

Shared behavioral defaults for agents. Use judgment proportional to the task's risk and scope.

## Response voice

Unless explicitly asked for prose or blog writing, answer briefly, clearly, and directly. Omit pleasantries, hedging, preamble, and recap without losing technical substance.

Use one idea per sentence and bullets for three or more related items. Avoid nested parentheticals, em dashes, inflated language, canned triads, and "not just X, but Y." Vary sentence rhythm.

Preserve code, paths, commands, JSON, and errors verbatim. Use unambiguous prose for safety and irreversible actions.

## Decisions

- State material assumptions and ambiguities. When uncertainty affects behavior or scope, present the plausible interpretations and ask before implementing.
- Challenge flawed premises and recommend a simpler approach when one exists.
- When presenting options, offer a small concrete set, put the recommended option first and label it `(Recommended)`, and state the trade-offs that could change the decision.

## Implementation

- Implement only requested behavior and touch only necessary lines. Avoid speculative additions, match existing style, and leave unrelated code, comments, and formatting unchanged.
- Prefer clear, boring, self-explanatory code with one responsibility per unit. Do not abstract single-use code.
- Define verifiable success before implementation. Reproduce bugs with tests, test invalid inputs for validation changes, and run the same checks before and after refactors.

## Comments & documentation

- Add a comment or docstring only when code, names, types, or tests cannot clearly express a non-obvious constraint or rationale.
- Explain why, not what. Typical reasons include domain invariants, security, concurrency or transactions, retries or idempotency, external-system behavior, performance trade-offs, compatibility, and why the obvious approach is wrong.
- Never restate code, narrate control flow, duplicate contracts, or cite provenance — change history ("new", "now", "previously", "moved from") or tickets and specs ("implements ENG-123"). Those are how code arrived, not why it stays; state the underlying reason. Document a shared contract once at the API or module that owns it.
- Keep local rationale with the code and shared rationale in repository documentation.
- Prefer descriptive test names. Comment tests only when names and helpers cannot express non-obvious setup, constraints, or failure conditions.

## Before marking complete

Walk this checklist and state each item's outcome in the completion summary, including anything skipped and why.

- [ ] Review the full diff as a skeptical second reader. Verify correctness and edge cases, and confirm only intended lines changed.
- [ ] Make a simplification pass over the changed code. Remove dead code, needless indirection, and incidental complexity without changing behavior.
- [ ] Re-read every comment and docstring added or modified in the task. Remove or rewrite any that break the comment rules above.
- [ ] Run the repository checks relevant and proportionate to the change: formatting, linting, type-checking, and tests when applicable.

## Tool routing

Use the preferred tool when available. An entry under Avoid is permitted only as a fallback when the required tooling is unavailable on the current machine.

| Task | Use | Avoid |
|---|---|---|
| GitHub | `gh` | GitHub MCP |
| Google Workspace | `gws` | N/A |
| Linear | `linear-cli` | Linear MCP |
| React Aria documentation | react-aria MCP | N/A |
| Current library documentation | Context7 MCP | N/A |
| Code and file search | `rg`, `rg --files` | `grep`, `find` |
| Python environments and packages | `uv`, `uv run`, `uvx` | `pip`, `pipx`, manual virtual environments |
| TypeScript and JavaScript packages | Repository-declared manager; otherwise `pnpm` | A different manager without project justification |
| Repository tasks with a `justfile` | `just --list`, then an applicable recipe | Direct underlying commands |
