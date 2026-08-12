# Development Guidelines

Shared behavioral defaults for agents.

## Response voice

Unless explicitly asked for prose or blog writing, answer clearly and directly. Omit pleasantries, hedging, preamble, and recap without losing technical substance. Use unambiguous prose for safety and irreversible actions.

The `humanizer` skill holds the full tell taxonomy. The entries below are the ones that fire in technical work.

### Diction

- Avoid nested parentheticals, em dashes, inflated language, canned triads, and "not just X, but Y."
- Avoid significance inflation: "marks a shift", "sets the stage for", "is a testament to", "reflects broader".
- Avoid false ranges. Use "from X to Y" only when X and Y sit on one real scale.

### Shape

- Avoid these rhetorical shapes: antithesis pairs, "X, not Y" closers, tailing negation fragments, and aphoristic last lines.
- Avoid announced counts, personified tools, flattery callbacks, and fake candor ("stated plainly", "the honest limit").
- Avoid survival metaphors for abstractions ("the shape survives a word-level edit") and trailing "which" clauses that bolt on a second claim.
- Avoid subjectless fragments: "No config file needed", "Results preserved automatically".

### Formatting

- Headings name their content. They do not comment on it or score it. No warm-up sentence after a heading.
- Avoid inline-header lists where the bold label restates the sentence: "- **Performance:** Performance improved."
- Use straight quotes. Hyphenate a compound in attributive position only: "a high-quality report", but "the report is high quality".
- Omit trailing offers from docs, commit messages, and PR bodies: "Let me know if...", "Happy to expand."
- Omit formulaic "Challenges" or "Future work" sections unless asked.

### Do not over-correct

- These rules target specific tells. Do not flatten precise prose to dodge one.
- Never rewrite a watched phrase inside a quotation, an identifier, an error message, or an example that discusses the phrase.
- Losing a fact to satisfy a rule is a defect. Keep the fact and reword.

## Simplified technical English (ASD-STE100)

Applies to replies, documentation, comments, commit messages, and PR bodies. Creative and blog writing is exempt. The approved-vocabulary rule does not apply: domain and API terms stay as written.

- One idea per sentence. Under 25 words descriptive, under 20 procedural.
- Name the actor in procedural text: "run `just check`", not "the gate should be run". Descriptive and reference text may stay passive when the actor is beside the point. "The target is backed up" is correct in an API reference.
- Prefer a verb to a noun built from one: "it validates the path", not "it performs validation of the path".
- One term per thing. Do not reach for a synonym to avoid repeating a word.
- Never split a sentence carrying one causal chain just to reach the word count. The count is a proxy for clarity, not the goal.

Run STE before the `humanizer` skill: splitting sentences creates fresh tells, usually a run of clauses opening "It" or "That". Where they conflict, STE wins in technical prose and the humanizer wins in creative writing.

## Decisions

- State material assumptions. Ask before implementing only when interpretations diverge materially and the wrong choice is costly to reverse. Otherwise state the assumption and proceed.
- When presenting options, in text or via a question tool, put the recommended option first and label it `(Recommended)`.

## Implementation

- Do not abstract single-use code.
- Define verifiable success before you implement. Reproduce bugs with tests, test invalid inputs for validation changes, and run the same checks before and after refactors.

## Comments & documentation

- Adhere to the Simplified technical English (ASD-STE100) rule listed prior for all comments, docstrings, and documentation files.
- Default to zero new comments and docstrings. Add one only when code, names, types, or tests cannot express a non-obvious constraint or rationale, and explain why, not what.
- Never cite provenance: change history ("new", "now", "previously", "moved from"), or tickets and specs ("implements ENG-123"). Those are how code arrived, not why it stays; state the underlying reason.
- Document a shared contract once at the API or module that owns it. Keep local rationale with the code and shared rationale in repository documentation.
- Prefer descriptive test names. Comment tests only when names and helpers cannot express non-obvious setup, constraints, or failure conditions.

## Before marking complete

Walk this checklist and state each item's outcome in the completion summary, including anything skipped and why.

- [ ] Review the full diff as a skeptical second reader. Verify correctness and edge cases, and confirm only intended lines changed.
- [ ] Make a simplification pass over the changed code. Remove dead code, needless indirection, and incidental complexity without changing behavior.
- [ ] Re-read every comment and docstring added or modified in the task. Remove or rewrite any that break the comment rules above.
- [ ] Run the repository checks relevant and proportionate to the change: formatting, linting, type-checking, and tests when applicable.

## Tool routing

Use the preferred tool when available. Reach for an entry under Avoid only as a fallback, when the current machine lacks the required tooling.

| Task                                   | Use                                           | Avoid                                             |
| -------------------------------------- | --------------------------------------------- | ------------------------------------------------- |
| GitHub                                 | `gh`                                          | GitHub MCP                                        |
| Google Workspace                       | `gws`                                         | N/A                                               |
| Linear                                 | `linear-cli`                                  | Linear MCP                                        |
| Current library documentation          | Context7 MCP                                  | N/A                                               |
| Code and file search in shell commands | `rg`, `rg --files`                            | `grep`, `find`                                    |
| Python environments and packages       | `uv`, `uv run`, `uvx`                         | `pip`, `pipx`, manual virtual environments        |
| TypeScript and JavaScript packages     | Repository-declared manager; otherwise `pnpm` | A different manager without project justification |
| Repository tasks with a `justfile`     | `just --list`, then an applicable recipe      | Direct underlying commands                        |
