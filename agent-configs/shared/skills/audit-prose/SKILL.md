---
name: audit-prose
description: Lightweight prose audit to remove AI tells, simplify diction into natural English, chunk dense multi-condition sentences into lists, and preserve semantic fidelity. Use for PR copy, commit messages, docs, comments, and instructions.
---

# Audit Prose

Audit technical prose to remove machine tells, eliminate compliance slop, and ensure clean, natural
English. Nudge prose toward direct, human-written clarity rather than rigid, bureaucratic evasions.

## Select the mode

Honor explicit user constraints, then the caller's `mode=report` or `mode=apply`. Without a supplied
mode, use report for review or suggestion requests and apply for rewrite, cleanup, or correction
requests.

- **Report:** Do not edit. Return each correction with its location, violated rule, and proposed
  wording. State when no correction is needed.
- **Apply:** Rewrite only the scoped prose, or return the rewritten text when no file is targeted.

Apply the same lenses in both modes. In report mode, instructions below to delete, rewrite, or
otherwise edit mean to propose that correction.

> **Semantic fidelity trumps style.** Treat wording and structure rules as defaults: preserve clear,
> accurate, idiomatic prose, and rewrite only when the change improves clarity, precision, or
> usefulness. Banned AI tells and semantic fidelity are firm: never alter verified behavior, invent
> facts, or drop technical caveats. Preserve deliberately non-conforming or bad prose in quoted
> examples, error messages, test fixtures, and anti-pattern documentation.

Apply these four review lenses in order:

## 1. Direct Diction & Simplicity (The Anti-Slop Check)

- **Purge AI Tells:** Remove the banned phrases, framing formulas, and superlative justifications
  listed in [references/diction.md](references/diction.md), and apply its substitution table.
- **No Conversational Preamble:** Cut `Basically`, `Note that`, `Here is what you need to know`, and
  `The reality is`. State the fact and stop.
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
- **Negate at the Verb:** The reader should know a claim is negative by the time they reach its main
  verb or predicate. If `verb no noun` can be rewritten as `does not verb noun`, rewrite it, unless
  the zero quantity is the result (`the query returns no rows`, `the search finds no matches`). Do
  not defer the negation past the verb's object. Negative predicates
  (`existing rows are untouched`), `has no`, and `there is no` stay.
  - _Reject:_ `It opens no connection.`
  - _Apply:_ `It does not open a connection.`
  - _Reject:_ `The migration leaves existing rows untouched.`
  - _Apply:_ `The migration does not modify existing rows.`
  - _Reject:_ `makes no modifications to the database`
  - _Apply:_ `does not modify the database`
- **No Verbing Nouns Without a Verb Sense:** Reject a noun used as a verb when it has no established
  verb sense (`PR the fix`, `ticket the follow-up`, `mutex the map`); write the verb phrase instead.
  Words with an established verb sense stay (`cache`, `log`, `commit`, `transition`, `architect`,
  `impact`). If a reader would pause on the verb, use the verb phrase.
- **No Inanimate Intent or Possession:** Code, files, records, and data structures have no feelings
  or intent. Reject `code wants`, `test decides`, `file prefers`, and `build earns its keep`. Reject
  `holds` and `carries` as stand-ins for `has` when a file, record, message, or change possesses
  content (`the record holds five fields`, `this PR carries the fix`); use `has`, `stores`,
  `records`, or `includes`. Established technical idioms stay where they fit: a variable holds a
  value, a thread holds a lock, an invariant holds, a function expects or accepts an argument, and a
  parser sees a token. Stative descriptions (`has no timeout`, `needs credentials`) are natural and
  standard.

## 2. Structural Chunking (The 3+ Rule)

- **Lists Over Run-ons:** When a sentence describes 3 or more conditions, failure modes, error
  variants, or exit reasons that each have their own verb, do not pack them into a compound sentence
  with chained `and` / `or` clauses. Format them as a bulleted list or table. A short list of nouns
  stays inline (`accepts JSON, TOML, or YAML`).
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

- **Chronological Order:** State prerequisites, causes, and guard conditions before the actions they
  govern, as readable pseudocode does (`If the key is missing, generate one. Then deploy.`).
- **Failures as Branches:** State a failure as a branch right after the step that can fail
  (`Fetch the configuration. If fetching fails, stop. Otherwise, deploy.`), or collect failures
  after the whole sequence. Reject a failure stated as a detached fact the reader must attach to a
  step:
  - _Reject:_
    `The client requests an auth token and user profile from the server; the request fails when the server rejects either credential. After obtaining both, it saves the session.`
  - _Apply:_
    `The client requests an auth token and user profile from the server. Once both are obtained, it saves the session. If the server rejects either credential, the client returns an error.`
- **Keep Clauses Connected:** Each clause follows from the one before it. Cut a trailing clause that
  does not, such as a speculative benefit (`..., ensuring that`, `..., thereby preventing`) or a
  non-sequitur. A factual chain whose every link follows stays:
  - _Reject:_ `The hook appends one record per command, which keeps the codebase maintainable.`
  - _Apply:_ `The hook appends one record per command.`

## 4. Conceptual Altitude & Semantic Fidelity

- **Concept Before Mechanics:** In architecture documents, RFCs, and PR summaries, explain design
  intent and user-visible behavior before detailing internal algorithmic loops, variable traces, or
  timestamp sleep loops.
- **Comments and Docstrings Target Zero:** Delete inline comments and docstrings that merely
  paraphrase code, statements, or signatures. Retain comments only for non-obvious hazards, ABI/OS
  quirks, race or lock constraints, compatibility requirements, why the obvious alternative fails,
  or invariants the signature cannot convey. Docstrings satisfy the lint and stop (invariants and
  failure contracts only; omit on private helpers).
- **No Provenance or Grievance:** Remove commentary on history, tickets, PRs, or outages
  (`added after outage`, `historically this was`), or complaints about dependency defaults
  (`workaround for upstream bug`). State the current constraint directly.
- **Zero Semantic Drift:** Preserve verified facts, numbers, boundaries, and error codes. Never
  invent facts or drop technical caveats.
- **Behavior Over Identifiers:** In prose outside code, describe what the code does in plain words,
  adding backtick identifiers only where needed to locate the symbol. Never use an identifier name
  as an English verb.

---

## Resolve scope and output

Resolve scope before auditing:

- Preserve a caller-supplied scope, including revisions and diff/snapshot boundaries. In a diff,
  audit only added or modified prose; in a snapshot, audit the selected prose in full.
- With an explicitly named file, path, or text snippet, audit only that target.
- With no named target, audit staged changes, unstaged changes, and untracked files (the union of
  `git diff HEAD` and untracked files reported by `git status --porcelain`). Audit and rewrite only
  the prose lines added or modified within that resolved scope.

For commit messages, PR drafts, and small snippets, keep the output to corrections or the rewritten
artifact as the selected mode requires. For change sets, preserve the resolved line scope.

## Operational Constraints

- Rewrite a line only when you can name the rule it violates and what the rewrite improves;
  otherwise leave it unchanged.
- Touch only prose lines (comments, docstrings, docs, markdown, commit messages).
- Never modify code logic, string literals (other than CLI usage docstrings), identifiers, or test
  assertions.
- Do not enforce arbitrary line wrapping or column limits; let deterministic formatters handle
  layout.
- Do not run formatters, linters, tests, or build commands. Do not spawn subagents.
