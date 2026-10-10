---
name: audit-prose
description: Lightweight prose audit to remove AI tells, simplify diction into natural English, replace rhetorical phrasing with literal statements a cold reader understands, chunk dense multi-condition sentences into lists, and preserve semantic fidelity. Use for PR copy, commit messages, docs, comments, and instructions.
---

# Audit Prose

Audit technical prose to remove AI tells and stiff, bureaucratic phrasing, and leave clear, natural English.

## Select the mode

Honor explicit user constraints, then the caller's `mode=report` or `mode=apply`. Without a supplied mode, use report for review or suggestion requests and apply for rewrite, cleanup, or correction requests.

- **Report:** Do not edit. Return each correction with its location, violated rule, and proposed wording. State when no correction is needed.
- **Apply:** Rewrite only the scoped prose, or return the rewritten text when no file is targeted.

Apply the same lenses in both modes. In report mode, instructions below to delete, rewrite, or otherwise edit mean to propose that correction.

> **Meaning takes precedence over style.** Treat wording and structure rules as defaults: preserve clear, accurate, idiomatic prose, and rewrite only when the change improves clarity, precision, or usefulness. Banned AI tells and semantic fidelity are firm: never alter verified behavior, invent facts, or drop technical caveats. Preserve deliberately non-conforming or bad prose in quoted examples, error messages, test fixtures, and anti-pattern documentation.

After resolving scope and running any required cold-reader pass (both described below the lenses), apply these five review lenses in order:

## 1. Direct Diction & Simplicity

- **Purge AI Tells:** Remove the AI tells listed in section 1 of [references/diction.md](references/diction.md), and apply its substitution table.
- **No Conversational Preamble:** Cut `Basically`, `Note that`, `Here is what you need to know`, and `The reality is`. State the fact and stop.
- **Natural Engineering Verbs:** Use direct technical verbs (`has`, `stores`, `runs`, `executes`, `prints`, `outputs`, `writes`) rather than bureaucratic phrasing (`names on stderr`, `holds files`). Prefer `has` over `contains` where simpler (e.g., `has no files`), while keeping `contains` when describing collection membership or substrings. Use `skips` when an operation bypasses an item, and `does not modify` or `does not change` when an item is inspected without mutation.
- **Direct Phrasing Over Negative Evasions:** Say what happens directly. Reject convoluted circumlocutions invented to avoid restrictive adverbs such as `only`:
  - _Reject:_ `does not change any target other than the one it names`
  - _Apply:_ `only changes the named target`
  - _Reject:_ `a scenario in which the command rejects invalid arguments`
  - _Apply:_ `when the command rejects invalid arguments`
- **Negate at the Verb:** The reader should know a claim is negative by the time they reach its main verb or predicate. If `verb no noun` can be rewritten as `does not verb noun`, rewrite it, unless the zero quantity is the result (`the query returns no rows`, `the search finds no matches`). Do not defer the negation past the verb's object. Negative predicates (`existing rows are untouched`), `has no`, and `there is no` stay.
  - _Reject:_ `It opens no connection.`
  - _Apply:_ `It does not open a connection.`
  - _Reject:_ `The migration leaves existing rows untouched.`
  - _Apply:_ `The migration does not modify existing rows.`
  - _Reject:_ `makes no modifications to the database`
  - _Apply:_ `does not modify the database`
- **No Verbing Nouns Without a Verb Sense:** Reject a noun used as a verb when it has no established verb sense (`PR the fix`, `ticket the follow-up`, `mutex the map`); write the verb phrase instead. Words with an established verb sense stay (`cache`, `log`, `commit`, `transition`, `architect`, `impact`). If a reader would pause on the verb, use the verb phrase.
- **No Inanimate Intent or Possession:** Code, files, records, and data structures have no feelings or intent. Reject verbs of intent or perception: `code wants`, `test decides`, `file prefers`, `build earns its keep`, and `the scheduler cannot see paused jobs`. Reject `holds`, `carries`, and `gains` as stand-ins for `has` when a file, record, message, or change possesses content (`the record holds five fields`, `this PR carries the fix`), and `lives in` as a stand-in for `is stored in`; use `has`, `stores`, `records`, `includes`, or `is stored in`. Established technical idioms stay where they fit: a variable holds a value, a thread holds a lock, an invariant holds, a function expects or accepts an argument, and a parser sees a token. Stative descriptions (`has no timeout`, `needs credentials`) are natural and standard.

## 2. Literal Over Rhetorical

Write every sentence, caption, and tooltip so that a reader who has only the document understands it, without the session, the codebase, or the project's shorthand. Write every heading, label, table cell, status chip, and aria-label so that it makes sense read alone. A term the document has already defined is not shorthand. Prefer the literal statement of what happens over a phrase chosen for rhythm, wit, or memorability, even when the literal phrase is longer. Test each phrase with these questions. A yes means rewrite it; when the rewrite needs an action or fact the text does not state, report the phrase and ask the caller for that fact instead of supplying one:

- **Effect Without Action:** Does it name only the property a change guarantees, or a mechanism without its behavior (`writes obey the lock`)? State what changes, runs, waits, or fails.
- **Context-Dependent Heading or Opener:** Does a heading or a section's first sentence need the section body to make sense, or use a term the text has not yet defined?
- **Judging or Teasing Label:** Does a heading, title, or status label judge (`Easy wins`) or tease (`Where the bytes go`) instead of naming the subject or state?
- **Figure of Speech:** Does it use wordplay, a slogan, personification of anything other than a code entity (lens 1 judges code entities and their idioms), metaphor, or a contrast built for effect? Keep a contrast with an option the reader is weighing. Keep established technical terms: words the field uses as the name of a mechanism in APIs, commands, or reference docs, such as `pipeline`, `handshake`, `heap`, `fork`, `sandbox`, and `deadlock`.
- **Undefined Shorthand:** Does it use a coined term or nickname that is not defined at first use, a qualifier with no defined meaning (`valid existing record`), or an elliptical stand-in for an earlier noun (`a project with none`)?
- **Audience Jargon:** Does it use in-house jargon, an in-house status word, or a narrow-specialty term the audience may not share? Terms common across software engineering and tech stay (`egress`, `idempotent`, `p99`). When the text does not name its audience, assume an engineer outside the project. Replace the term with its plain meaning.

[references/diction.md](references/diction.md) lists a before-and-after example for each pattern.

## 3. Structural Chunking (The 3+ Rule)

- **Lists Over Run-ons:** When a sentence describes 3 or more conditions, failure modes, error variants, or exit reasons that each have their own verb, do not pack them into a compound sentence with chained `and` / `or` clauses. Format them as a bulleted list or table. A short list of nouns stays inline (`accepts JSON, TOML, or YAML`).
  - _Reject:_ `Returns a ConfigError when path is not a directory or cannot be canonicalized, or when its config.toml is absent, cannot be read or parsed, or is missing root = true.`
  - _Apply:_
    ```markdown
    Returns a `ConfigError` if:

    - `path` is not a directory or cannot be canonicalized.
    - `config.toml` is missing, unreadable, or unparseable.
    - The manifest is missing `root = true`.
    ```
- **Sentence Length as Review Cue:** Sentences should rarely exceed 30 words. When a sentence passes ~30 words, check whether it is packing multiple distinct claims or conditions; if so, split it or convert the cases to a list. Repeating a subject to start a new clear sentence is clean writing, not a defect.
- **Group by Outcome:** Group multiple triggers under their shared outcome rather than bouncing between outcomes (e.g., avoid jumping from exit 2 to exit 0 and back to exit 2).

## 4. Sequential Narrative Flow

- **Chronological Order:** State prerequisites, causes, and guard conditions before the actions they govern, as readable pseudocode does (`If the key is missing, generate one. Then deploy.`).
- **Failures as Branches:** State a failure as a branch right after the step that can fail (`Fetch the configuration. If fetching fails, stop. Otherwise, deploy.`), or collect failures after the whole sequence. Reject a failure stated as a detached fact the reader must attach to a step:
  - _Reject:_ `The client requests an auth token and user profile from the server; the request fails when the server rejects either credential. After obtaining both, it saves the session.`
  - _Apply:_ `The client requests an auth token and user profile from the server. Once both are obtained, it saves the session. If the server rejects either credential, the client returns an error.`
- **Keep Clauses Connected:** Each clause follows from the one before it. Cut a trailing clause that does not, such as a speculative benefit (`..., ensuring that`, `..., thereby preventing`) or a non-sequitur. A factual chain whose every link follows stays:
  - _Reject:_ `The hook appends one record per command, which keeps the codebase maintainable.`
  - _Apply:_ `The hook appends one record per command.`
- **Paragraph Pass:** After the sentence-level fixes, reread each paragraph whole. Name the relation between each pair of adjacent sentences (cause, condition, consequence, contrast, sequence, or elaboration); when none fits, reorder the sentences or convert them to a list. Keep at most one causal link per sentence.
- **Verdict First, Said Once:** In a document, PR description, or reply, open on the result or conclusion. Cut restatements, closing recaps, and sign-offs. When the reader must act or decide, end on that action.

## 5. Design Before Mechanics & Semantic Fidelity

- **Concept Before Mechanics:** In architecture documents, RFCs, and PR summaries, explain design intent and user-visible behavior before detailing internal algorithmic loops, variable traces, or polling loops.
- **Comments and Docstrings Target Zero:** Delete inline comments and docstrings that merely paraphrase code, statements, or signatures. Retain comments only for non-obvious hazards, ABI/OS quirks, race or lock constraints, compatibility requirements, why the obvious alternative fails, or invariants the signature cannot convey. On public items, write only the docstring the linter requires (a summary line plus invariants and failure contracts); omit docstrings on private helpers.
- **No Provenance or Grievance:** Remove commentary on history, tickets, PRs, or outages (`added after outage`, `historically this was`), or complaints about dependency defaults (`workaround for upstream bug`). State the current constraint directly.
- **Design Intent as a Rule:** Rewrite a contract stated as an observed absence (`No other service writes the sessions table`) as a rule about the component that enforces it (`The auth service is the only writer of the sessions table`). An observed absence describes the current code, not the rule a future change must keep.
- **Zero Semantic Drift:** Preserve verified facts, numbers, boundaries, and error codes. Never invent facts or drop technical caveats.
- **Behavior Over Identifiers:** In prose outside code, describe what the code does in plain words, adding backtick identifiers only where needed to locate the symbol. Never use an identifier name as an English verb.

---

## Resolve scope and output

Resolve scope before auditing:

- Preserve a caller-supplied scope, including revisions and diff/snapshot boundaries. In a diff, audit only added or modified prose; in a snapshot (the selected files as they are now), audit the selected prose in full.
- With an explicitly named file, path, or text snippet, audit only that target.
- With no named target, audit staged changes, unstaged changes, and untracked files (the union of `git diff HEAD` and untracked files reported by `git status --porcelain`). Audit and rewrite only the prose lines added or modified within that resolved scope.
- For a reader-facing deliverable (a document, page, proposal, README, or PR description written for people to read as a whole, not agent instructions or code comments), audit the whole artifact each time this skill runs, even when the caller supplies a diff scope, unless the user explicitly limits the scope. Earlier passes may have missed violations in unchanged lines.

For commit messages, PR drafts, and small snippets, keep the output to corrections or the rewritten artifact as the selected mode requires.

## Run a cold-reader pass with a fresh subagent

The writer knows its own shorthand, so it cannot judge what a reader without that context understands. Run a cold-reader pass before applying the lenses when both of these hold:

- The prose is a reader-facing deliverable or an instruction file (a skill, prompt, agent definition, or repository instruction file).
- The agent running this audit, or the agent that delegated it, wrote the prose, or authorship is unknown.

Skip the pass for commit messages, code comments, docstrings, and other short snippets. When the delegating agent already ran the pass and supplied its flags, use those flags instead of spawning another reader.

1. Spawn a fresh subagent and give it only the text: the whole artifact that contains the scoped prose, and the intended audience when known. Give it no session history, other project files, or explanations of terms beyond what the artifact states.
2. Ask it to quote every word, phrase, heading, and label whose meaning it cannot determine from the text alone, and to give its best guess at what each one means. Tell it not to judge style.
3. Treat each flag inside the resolved scope as a Literal Over Rhetorical violation. Dismiss a flag only when the artifact defines the term, the term is common across software engineering, or the stated audience (by default, an engineer outside the project) already knows it. Never dismiss a flag because the session context explains it. Rewrite each violation in apply mode or report it in report mode.

If the harness cannot spawn a subagent or the user forbids subagents, state that the cold-reader pass did not run.

## Operational Constraints

- Rewrite a line only when you can name the rule it violates and what the rewrite improves; otherwise leave it unchanged. Literal Over Rhetorical is a nameable rule: a phrase that fails one of its tests, or a cold-reader flag that step 3 does not dismiss, violates it.
- Touch only prose lines (comments, docstrings, docs, markdown, commit messages).
- Never modify code logic, string literals (except docstrings that a CLI prints as usage text), identifiers, or test assertions.
- Do not enforce arbitrary line wrapping or column limits; let deterministic formatters handle layout.
- Do not run formatters, linters, tests, or build commands. Do not spawn subagents other than the cold reader.
