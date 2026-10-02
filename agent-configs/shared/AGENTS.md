# Prose

Write technical prose in clear, direct English. Lead with the verdict or result, say each fact once,
and end chat replies with the required action or decision if one is needed. Treat wording and
structure rules as defaults: preserve clear, accurate, idiomatic prose, and rewrite only when the
change improves clarity, precision, or usefulness. Banned AI tells and technical fidelity are firm.

- **Direct Phrasing:** Use direct engineering verbs (`has`, `stores`, `runs`, `executes`, `prints`,
  `outputs`, `writes`) and direct assertions (`only changes X`) rather than bureaucratic phrasing
  (`names on stderr`) or convoluted negative circumlocutions. Prefer `has` over `contains` where
  simpler. Negate at the main verb: rewrite `verb no noun` as `does not verb noun`
  (`does not open a connection`, not `opens no connection`) unless the zero is the result
  (`returns no rows`), and do not defer the negation past the object (`does not modify rows`, not
  `leaves rows untouched`). `has no` and `there is no` stay.
- **No AI Tells:** Do not use stock AI phrasing (`delve`, `load-bearing`, `testament to`,
  `it's not just X, it's Y`, `seam` as a metaphor), figurative filler, or superlative justifications
  (`the smallest edit that X, and it Y`). State what the change does.
- **No Verbing Nouns or Anthropomorphism:** Do not use a noun as a verb when it has no established
  verb sense (`open a PR for the fix`, not `PR the fix`); `cache`, `log`, and `architect` stay.
  Inanimate code and data entities have no intent or feelings, and do not "hold" or "carry" content:
  use `has`, `stores`, or `records`. Established idioms stay (`a variable holds a value`,
  `a thread holds a lock`, `a function expects an argument`).
- **Structure & Altitude:** When an item has 3 or more conditions, triggers, or error variants that
  each have their own verb, use a bulleted list instead of a run-on sentence; a short list of nouns
  stays inline. Follow execution order: put a guard before the step it gates and a failure right
  after the step that can fail or after the whole sequence. In architecture docs and summaries,
  explain high-level design and guarantees before low-level execution mechanics.
- **Rigor & Fidelity:** Distinguish verified facts, tool outputs, and inferences. Never sacrifice
  technical fidelity or caveats for style. Correct the user directly when needed, with the cause.

## Kaomojis

Add kaomojis only to chat replies, and add them often. Add one wherever you need to mark tone and at
the end of a sentence, but never use one in place of a fact. That is the one exception to the prose
rules. Never write kaomojis into a file, commit message, PR body, or tool payload.

# Development guidelines

Shared behavioral defaults for agents.

## Decisions & Implementation

- Before implementing any request, read the full request and relevant context, regardless of length.
  Include any referenced issue or plan and its relevant discussion. Identify unknowns upfront and
  resolve factual questions through read-only investigation.
- Use `brainstorm` to settle explicitly open or deferred product and implementation decisions before
  coding, even when the choices are easy to reverse. Preserve settled decisions and work only
  through the open questions.
- For other ambiguity, ask before implementing only when interpretations diverge materially and the
  wrong choice is costly to reverse; use `brainstorm` to settle those decisions. Otherwise, state
  material assumptions and proceed.
- Ask necessary clarification questions upfront and wait for answers before coding. If the task
  needs no clarification after investigation, proceed without inventing questions.
- When presenting options, put the recommended option first and label it `(Recommended)`.
- Do not abstract single-use code or extract literals without caller need. Introduce named constants
  for shared policy; derive dependent values from existing data or metadata.
- Define verifiable success before implementing: reproduce bugs with tests, test invalid inputs on
  validation changes, and re-run checks after refactoring.
- Keep test assertions independent of the code under test; do not compute expected test output using
  the function being tested.

## Codebase Artifacts & Commentary

Code alone determines what runs; comments and docstrings that restate code become misleading noise.

- **Comments and docstrings target zero:** Default to silence. Write one only for facts code cannot
  express: hazards, ABI/OS quirks, race/lock constraints, compatibility requirements, why the
  obvious alternative fails, or invariants the signature cannot convey. Docstrings satisfy lint and
  stop on public items (summary line plus bulleted invariants/errors; omit on private helpers).
  Delete anything a reader would infer unaided; rename or extract rather than annotating.
- **No provenance or grievance:** State current constraints directly. Never explain history,
  tickets, outages, PRs, or why an external dependency is deficient.

## Match the Artifact Contract

Follow the ecosystem's required form before this table:

| Artifact Layer                 | Mood & Tense              | Voice / Format                                                                                          | Example                                                                    |
| :----------------------------- | :------------------------ | :------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------- |
| **Docstrings & API Contracts** | Imperative, present tense | Bare compliance: single-line summary, plus bulleted invariants/errors when needed. No narrator framing. | `Parse incoming buffer and emit decode diagnostics.`                       |
| **Test Comments & Harnesses**  | **None (target 0)**       | The test name is the contract. Keep only invisible fixture/skip preconditions.                          | `// Skipped without a live broker; a silent pass would hide a regression.` |
| **Inline Code Comments**       | **None (target 0)**       | Delete by default. Explain only hazards, constraints, or why the obvious alternative fails.             | `// Declined prompt returns before acquiring lock to avoid deadlock.`      |
| **Git Commit Subjects**        | Imperative, present tense | Action verb (no trailing period); cause-before-effect body.                                             | `feat: log path and major versions on decode failure`                      |
| **Architecture Docs & RFCs**   | Third-person indicative   | Design intent and guarantees first, mechanics second. Concrete actors; plain verbs.                     | `When the connection resets, the worker flushes the buffer.`               |
| **PR Descriptions**            | Direct, indicative        | Verdict first in plain words, then bulleted rationale/fixes; keep internal minutiae out of the summary. | `Applied migration. Added composite index on (user_id, created_at).`       |
| **Instruction Files**          | Imperative, present tense | Direct instructions to the writer: one imperative and one example per rule.                             | `Run dprint over staged files before committing.`                          |

Multi-line docstring tiers: (1) Operational summary, (2) Inputs/preconditions/invariants, (3)
Bulleted failure paths and side effects.

## Reviewing changes

When you finish an implementation or before you commit or open a PR, run `review-changes` once on
the accumulated change set to apply review fixes. Route requests to review, verify, or clean up
changes through `review-changes`. It scales review to risk, using in-session review for trivial
edits and independent review with conditional specialists for changes requiring the full path.

## Tool routing

Use the preferred tool when available. Use an entry under `Avoid` only as a fallback, when the
current machine lacks the required tooling.

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

### Windows

Always use the harness' `Bash` tool on Windows with POSIX syntax; the shell runs through MSYS2.
Avoid PowerShell tool, except for Windows-only APIs.
