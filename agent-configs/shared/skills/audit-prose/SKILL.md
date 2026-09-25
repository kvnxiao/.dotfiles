---
name: audit-prose
description: Lightweight prose audit to remove AI tells, simplify diction into natural English, chunk dense multi-condition sentences into lists, and preserve semantic fidelity. Use for PR copy, commit messages, docs, comments, and instructions.
---

# Audit Prose

Audit technical prose to remove machine tells, eliminate compliance slop, and ensure clean, natural
English. Nudge prose toward direct, human-written clarity rather than rigid, bureaucratic evasions.

> **Semantic fidelity trumps style.** Never alter verified behavior, invent facts, or drop technical
> caveats. If existing prose is already clear and idiomatic, leave it alone. Preserve deliberately
> non-conforming or bad prose in quoted examples, error messages, test fixtures, and anti-pattern
> documentation.

Apply these four review lenses in order:

## 1. Direct Diction & Simplicity (The Anti-Slop Check)

- **Purge AI Tells:** Remove synthetic framing formulas and buzzwords (`delve`, `load-bearing`,
  `seam`, `testament to`, `at its core`, `showcasing`, `it's not just X, it's Y`). See
  [references/diction.md](references/diction.md).
- **Natural Engineering Verbs:** Use direct technical verbs (`has`, `stores`, `runs`, `executes`,
  `prints`, `outputs`, `writes`) rather than bureaucratic phrasing (`names on stderr`,
  `holds files`). Prefer `has` over `contains` where simpler (e.g., `has no files`), while keeping
  `contains` when describing collection membership or substrings. Use `skips` when an operation
  bypasses an item, and `does not modify` or `does not change` when an item is inspected without
  mutation.
- **Direct Phrasing Over Negative Evasions:** Say what happens directly. Reject convoluted
  circumlocutions invented to avoid restrictive adverbs:
  - _Reject:_ `does not change any target other than the one it names`
  - _Apply:_ `only changes the named target`
  - _Reject:_ `a scenario in which the command rejects invalid arguments`
  - _Apply:_ `when the command rejects invalid arguments`
- **No Verbing Nouns:** Reject awkward verb coinages (`actioning`, `architecting`, `impact` as a
  verb).
- **No Inanimate Intent or Possession:** Code, files, records, and data structures do not possess
  feelings, intent, or consciousness, and do not "hold" things like physical containers. Reject
  `code wants`, `test decides`, and `directory/record holds X`. Use `has`, `stores`, or `records`
  instead (reserve `holds` strictly for synchronization locks or logical invariants). Stative
  descriptions (`has no timeout`, `needs credentials`) are natural and standard.

## 2. Structural Chunking (The 3+ Rule)

- **Lists Over Run-ons:** When a sentence describes 3 or more conditions, failure modes, error
  variants, or exit reasons, do not pack them into a compound sentence with chained `and` / `or`
  clauses. Format them as a bulleted list or table.
  - _Reject:_
    `Returns a ConfigError when path is not a directory or cannot be canonicalized, or when its config.toml is absent, cannot be read or parsed, or is missing root = true.`
  - _Apply:_
    ```markdown
    Returns a `ConfigError` if:

    - `path` is not a directory or cannot be canonicalized.
    - `config.toml` is missing, unreadable, or unparseable.
    - The manifest is missing `root = true`.
    ```
- **Sentence Length as Review Cue:** Sentences should rarely exceed 30 words. When a sentence passes
  ~30 words, check whether it is packing multiple distinct claims or conditions; if so, split it or
  convert the cases to a list. Repeating a subject to start a new clear sentence is clean writing,
  not a defect.
- **Group by Outcome:** Group multiple triggers under their shared outcome rather than bouncing
  between outcomes (e.g., avoid jumping between exit 2 $\to$ exit 0 $\to$ exit 2).

## 3. Sequential Narrative Flow

- **Chronological Order:** State prerequisites and causes before the actions they govern.
- **No Mid-Sequence Interruptions:** Do not break a happy-path sequence by wedging early-exit
  failure conditions into the middle of a prerequisite flow:
  - _Reject:_
    `The client requests an auth token and user profile from the server; the request fails when the server rejects either credential. After obtaining both, it saves the session.`
  - _Apply:_
    `The client requests an auth token and user profile from the server. Once both are obtained, it saves the session. If the server rejects either credential, the client returns an error.`

## 4. Conceptual Altitude & Semantic Fidelity

- **Concept Before Mechanics:** In architecture documents, RFCs, and PR summaries, explain design
  intent and user-visible behavior before detailing internal algorithmic loops, variable traces, or
  timestamp sleep loops.
- **Comments and Docstrings Target Zero:** Delete inline comments and docstrings that merely
  paraphrase code, statements, or signatures. Retain comments only for non-obvious hazards, lock
  ordering, or OS quirks. Docstrings satisfy the lint and stop (invariants and failure contracts
  only; omit on private helpers).
- **No Provenance or Grievance:** Remove commentary on history, tickets, PRs, or outages
  (`added after outage`), or complaints about dependency defaults. State the current constraint
  directly.
- **Zero Semantic Drift:** Preserve verified facts, numbers, boundaries, and error codes. Never
  invent facts or drop technical caveats.
- **Behavior Over Identifiers:** In prose outside code, describe what the code does in plain words,
  adding backtick identifiers only where needed to locate the symbol. Never use an identifier name
  as an English verb.

---

## Scope Gate & Audit Modes

Resolve scope before auditing:

- With an explicitly named file, path, or text snippet, audit only that target.
- With no named target, audit staged changes, unstaged changes, and untracked files (the union of
  `git diff HEAD` and untracked files reported by `git status --porcelain`). Audit and rewrite only
  the prose lines added or modified within that resolved scope.

Choose the mode matching the request:

- **Quick Rewrite:** Use for commit messages, PR drafts, or small text snippets. Directly rewrite
  the target in place or return the corrected artifact without verbose audit ledgers.
- **Change-Set Audit:** Use for reviewing a change set. Directly rewrite only the added or modified
  prose lines within the resolved scope.

## Operational Constraints

- Touch only prose lines (comments, docstrings, docs, markdown, commit messages).
- Never modify code logic, string literals (other than CLI usage docstrings), identifiers, or test
  assertions.
- Do not enforce arbitrary line wrapping or column limits; let deterministic formatters handle
  layout.
- Do not run formatters, linters, tests, or build commands. Do not spawn subagents.
