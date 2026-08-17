---
name: prose-correction
description: Audit or rewrite technical prose to preserve verified meaning, follow ecosystem and artifact conventions, and remove synthetic diction. Supports quick rewrites, change-set audits, and full prose audits across comments, docstrings, commit messages, PR copy, documentation, instruction files, and chat. Use before a PR or completion check. Use for requests to correct prose, fix writing, remove AI tells, or make text more direct.
---

# Prose Correction

Apply these priorities in order. A lower priority never overrides a higher one.

1. **Semantic fidelity:** Preserve verified behavior, scope, numbers, boundaries, hazards, and ordering requirements. Do not invent facts.
2. **Artifact convention:** Follow the target ecosystem and artifact before applying a general house style.
3. **Reader clarity:** Order and phrase each claim for the intended reader and surrounding discourse.
4. **House diction:** After the first three priorities hold, remove synthetic phrasing.

House style binds prose composed during the task. During an audit, treat a generation-time ban as a tripwire for existing prose, not an automatic defect. When semantics, ecosystem convention, or context favors an existing construction, do not rewrite it solely to satisfy that ban. Apply house style to each replacement without weakening a higher priority.

Over-correction is itself a defect. Evading a banned construction with a syntactic crutch produces worse prose than the construction it replaced. These repair traps recur, and a rewrite that trades one for another has not improved the prose:

- A `That <verb>` bridge.
- A causal trailer: `, which keeps ...`, `, so the arm resolves ...`, appended to absorb a dropped `That <verb>` bridge or participle.
- A demonstrative noun-echo: one sentence ends on a noun, the next opens `That <same noun>`.
- A cleft that delays the verb, such as `X is what keeps ...` or `the rendered help is what this asserts against`. The locative and temporal variants belong to the same family: `the long help is where it appears`, `startup is when the lock is taken`.
- A reduced appositive left dangling off a noun: `..., absent from non-Windows release builds`, `..., unreadable on a fresh checkout`. Dropping the relative pronoun strands an adjective phrase whose subject the reader must reconstruct.
- Coordinator chaining: `and ... and ...` strung across independent facts to absorb a dropped participle.
- A placeholder referent sentence.
- An isolated trailing paragraph.
- Two clipped sentences where one coordinated sentence carried the relation.

Engineering prose reads as connected reasoning rather than a sequence of telegraphic assertions. When no available construction states the fact better than the original, keep the original.

## Resolve Scope and Mode

Honor the scope the user names.

- With prose supplied in the request, treat that prose as the target even without a named file path.
- With no named target, audit prose in `git diff HEAD` and files reported by `git status --porcelain`. Edit only changed prose.
- With a named directory, subtree, or glob, inspect every prose item inside it. Do not narrow the audit to changed files.
- With a named file, symbol, or line range, inspect only that item.
- Outside the resolved scope, report a defect without editing it.

If the target is too large for a complete read, state the fully audited boundary and any triage-only remainder. Do not claim full coverage for a search-only pass.

Choose the least expensive mode that satisfies the request.

- **Quick rewrite:** Use for a sentence, paragraph, commit message, PR draft, or small named file. Unless the user requests an audit ledger, return only the corrected artifact.
- **Change-set audit:** Use for an unnamed target, a completion check, or a normal review of changed prose. Read every changed prose item in context and report material findings.
- **Full audit:** Use for exhaustive coverage, broad public-documentation releases, or high-risk behavioral contracts. Before running this mode, read [references/instruments.md](references/instruments.md).

Grep and mechanical matches may order the work. They do not replace reading the prose in context.

### Run the verification pass inline

Every mode verifies in the same session and the same agent. Prose is cheaper to re-audit than code and a human reads the diff anyway, so one pass plus its audit is the whole budget. Do not spawn a subagent, a second review round, or a re-audit of an already-clean item.

Composing a rewrite anchors you to it, and the inline pass has to work against that anchor deliberately:

- Verify against the authority, not against your draft. Open the file that settles each claim, including files the prose never names: a lint config behind a claim about a sanctioned carve-out, a CI workflow behind a claim about what CI runs, a build recipe behind a claim about what enables a feature. A claim whose authority you could not locate is reported as unverified, never as accepted.
- Reread each rewritten item as text you did not write, against the repair traps above. A rewrite that swapped a `That <verb>` bridge for a `, which keeps` trailer relocated its defect.
- Reread each item you kept by arguing against your own keep-reason, not by restating the tripwire that reason already answers.

Delegate to a subagent only where the user asks for an independent pass, or where a wrong claim ships something irreversible. State the cost when you propose it. An audit that runs inline is complete, not provisional; report it as a verdict rather than as a pass awaiting review.

## Core Procedure

1. **Model the reader.** Identify whether the artifact serves maintainers, newcomers, API consumers, operators, or another named audience.
2. **Classify the artifact.** Identify its ecosystem and layer: inline comment, docstring, commit, PR, architecture document, instruction file, or direct response.
3. **Extract the claims.** Reduce the source to concrete propositions. Separate invariants, conditions, consequences, hazards, rationale, and examples.
4. **Verify the claims.** Read the implementation or authoritative source. Mark each claim as verified, refuted, or unverified. Treat existing prose as a witness, not as evidence. When no authority is available, preserve the source's claims without increasing their certainty.
5. **Compose.** Preserve verified claims and flag material unknowns. When the authority establishes a replacement, correct a refuted claim. Use the artifact contract and discourse heuristics below. For a structural rewrite, compose from the claim list instead of copying the old clause pattern. For a local typo or mechanical defect, edit locally.
6. **Audit diction.** After the structural rewrite, read [references/diction.md](references/diction.md). Keep literal technical uses.
7. **Re-audit replacements.** Run every changed sentence through all priorities and heuristics. Include rules unrelated to the original trigger. Check each replacement against the repair traps above: a rewrite that swaps a bare `this` for a trailing relative, or a participle for a coordinator chain, has moved the defect rather than fixed it. If a replacement invents a fact, weakens a quantifier, obscures a dependency, or adds an unrelated defect, return it once to claim extraction and verification. If the retry fails, flag the unresolved defect and stop rewriting that item.
8. **Verify.** Compare the result with the source and the authority: restore any verified fact that was dropped, delete any fact the rewrite introduced, then read the finished prose once in context and revise ambiguous dependencies. Run this inline under the contract above. Stop when the pass finds nothing; a second lap over clean prose is churn, not rigor.

If a correct sentence still reads synthetic, generate multiple candidates. Vary syntax or information order deliberately. Select against semantic fidelity, artifact convention, and single-read clarity. Do not estimate probabilities. A candidate's apparent rarity does not justify its selection.

## Artifact Contracts

Follow an ecosystem's required form before these defaults. For example, one ecosystem requires an imperative one-line summary, while another requires a complete declarative sentence that names the declared symbol. Read the target ecosystem's own convention rather than generalizing from another language.

| Artifact                                     | Default contract                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| :------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Docstring or API documentation**           | Follow ecosystem conventions. State behavior, side effects, errors, constraints, and usage information that callers need. Limit an implementation docstring to what the code does, what it expects, and what it returns or raises; strip commentary on how a third-party library is deficient, and compress a rationale a maintainer needs into one clause. Public discovery requirements may justify a concise summary that resembles the signature. |
| **Git commit subject**                       | Use imperative mood and present tense with no trailing period. In the body, state the motivation and relevant behavior change.                                                                                                                                                                                                                                                                                                                        |
| **Inline comment**                           | State the mechanical constraint, invariant, hazard, or non-obvious ordering requirement in clipped present tense. Omit narrator framing, first person, and explanatory scaffolding: prefer `Accepts an explicit denylist so tests can inject arbitrary directories on any host` over `Taking the system-directory denylist as a parameter makes the denylist rule testable with injected directories on any platform`.                                |
| **Test comment, docstring, or harness code** | State the assertion or failure contract directly in indicative or imperative form: name the input, the expected outcome, and the regression it catches. Do not reduce a test to a truncated noun-phrase header. For a harness helper, state the skip condition and what a silent no-op would hide.                                                                                                                                                    |
| **Architecture document or RFC**             | Use third-person indicative prose. Use present tense for current behavior, past tense for completed work, and future or conditional forms for proposals. Name ambiguous actors.                                                                                                                                                                                                                                                                       |
| **PR title and body**                        | State the change and its cause directly. Distinguish verified results from risks, skipped checks, and planned work.                                                                                                                                                                                                                                                                                                                                   |
| **Instruction file**                         | Use direct imperative or infinitive instructions. Favor conventional, easily parsed phrasing over stylistic variation. Keep worked examples executable outside their original source.                                                                                                                                                                                                                                                                 |
| **Chat or direct deliverable**               | Lead with the verdict or result. Omit conversational preambles and redundant closing summaries.                                                                                                                                                                                                                                                                                                                                                       |

### Multi-line docstring order

Where the ecosystem does not dictate otherwise, order a multi-line docstring:

1. **Operational summary.** The primary action, in the ecosystem's required mood.
2. **Inputs, invariants, and preconditions.** What the caller must supply, what must hold on entry, and what the function refuses to recompute or assume.
3. **Failure paths, error mappings, and side effects.** Which condition maps to which terminal error, and what the call writes outside its return value.

A docstring that interleaves these — an authoritativeness constraint dropped between two execution steps, a side effect stated before the operation that causes it — forces the reader to reorder it. An ecosystem's own error section already sits at position 3; keep it there.

## Discourse and Dependency Heuristics

Treat these as decisions, not phrase bans.

- **Place framing context early.** When given information, prerequisites, or short conditions frame an action, place them before it.
- **Preserve event order.** When sequence matters, state prerequisite operations before dependent operations. If a short trailing temporal or conditional clause is restrictive, focal, or easier to parse in that position, it may remain.
- **Keep dependencies local.** If the subject, scope, or causal relation of a trailing participial phrase or non-restrictive relative clause is ambiguous, review the clause. If the relation is local and clearer than a split sentence, keep it.
- **Use topic continuity.** Give the grammatical subject to the current discourse topic. When the affected entity matters more than the actor, use agentless passive voice.
- **Coordinate related facts.** When predicates share a subject, condition, or mechanism, keep them together. Split independent operational rules.
- **Preserve negation scope.** If a positive verb states the same fact more directly, prefer it. If a negative quantifier such as `no`, `none`, or `neither` expresses the contract precisely, keep it. Do not rewrite `No caller can supply one` merely to move the negation.
- **Name ambiguous references.** If the referent of a pronoun or deictic such as `from there`, `at that point`, or a bare `this` is not immediate and unambiguous, name it.
- **State the referent, do not point at it.** Delete a clause whose only work is pointing back at a prior noun, such as `X is one of them`, `The CLI polls for that file`, or `it does this for that`. Naming a referent means stating the fact about the named component once, not adding a sentence that reintroduces the noun. Prefer `the parser already renders the empty-input path with the command listing` over `The empty-input path is one of them; the parser already renders it`.
- **State rationale where the artifact needs it.** If a purpose infinitive preserves the actor and goal, use it instead of `so that it can`, `in order to`, `so as to`, or a trailing `, which keeps` / `, so it keeps`. Front-load the purpose: prefer `To keep the parser exercisable on every host, the stub returns Unsupported without opening the device` over `the stub returns Unsupported without opening the device, which keeps the parser exercisable on every host`. Keep a trailing `so` only for an immediate mechanical consequence.
- **Cap a front-loaded purpose at one clause the reader can hold.** Front-loading establishes context quickly, and past roughly 10 to 12 words it postpones the subject behind a predicate stack instead. When the purpose carries a coordinated goal, a platform list, or its own relative clause, state the mechanism first and attach the purpose as a trailing infinitive or a second sentence. Reject `To keep the write arm compiling on every platform and exercisable by the integration suite, the device write is gated behind a platform check: on an unsupported platform the call returns Unsupported.` Apply `The device write is gated behind a platform check. On an unsupported platform the call returns Unsupported, to keep the integration suite compiling.` A colon splice after a long front-loaded purpose is the same defect wearing punctuation.
- **Do not document the documentation.** Prose states the code's behavior, never its own editorial mechanics. Delete a clause explaining why a symbol is not a cross-reference link, why a fact sits in this comment rather than another, or what a reader or caller notices, discovers, or is told by the output. Reject `The Retry mention above is deliberately not a cross-reference link, since a link to a platform-gated variant does not resolve when the docs are built for another platform` and `The verbose flag is where the tool lists its subcommands, so a caller who mis-invokes discovers the right one there`. Apply `Not cross-referenced: Retry is platform-gated` and `The tool lists subcommands under the verbose flag, not in the unknown-subcommand error`. Keep the constraint a maintainer would otherwise undo, in one clause, without the rationale for the wording.
- **Do not restate third-party behavior as a general rule.** A comment documents this repository, not the build tool, compiler, runtime, or shell it invokes. Delete abstract mechanism lectures such as `the build tool silently skips a target whose required features are not enabled`, `the shell wraps a thrown message in its own error rendering`, or `the operating system returns ENOENT for a missing path`, and state the local configuration rule instead. Keep the mechanism only where the reader cannot act on the local rule without it, and attach it to the concrete artifact rather than to the tool in general.
- **Do not stage a contract as narrative.** Name the branches and the action taken on each. Do not build contrastive drama around the problem first: `X reports only A, and does not enumerate B, while the contract requires B, so this function does C` sets a scene the reader must hold before reaching the behavior. Lead with what the function does on each input.
- **Coordinate instead of fragmenting.** Removing a trailing participle or relative clause rarely requires two sentences. When the facts share a subject or mechanism, join them with parallel predicates or one compound sentence. Two back-to-back short sentences that force the reader to reassemble a relation are worse than the trailing clause they replaced.
- **Consolidate, do not chain.** Coordination is a structure, not a rescue. Judge a chain by whether its members are of one kind, never by how many there are: `downloads, unpacks, and links the binary` is three like predicates over one subject and stands as written, while `needs no root and no network and can run unattended` welds two requirements to a capability and should become `needs no root or network access to run unattended`.
- **Give the verb its subject.** A cleft delays the predicate behind a copula and an empty head: `the rendered help text is what this asserts against`, `The existence check is what keeps the spawn from failing`. Name the actor and let it act: `this test asserts against the rendered help text`, `Guarding on file existence keeps the test from spawning a path that does not exist`. The empty head has locative and temporal forms too, and swapping one for another repairs nothing: `the long help is where it appears` and `the long help is what carries it` both want `the long help lists it`. Keep a cleft only where the sentence contrasts one candidate against a named alternative.
- **Give a reduced modifier its pronoun.** A trailing adjective or participial phrase with no relative pronoun leaves its subject to inference: `without the binary artifact, absent from non-Windows release builds`. Restore the pronoun and a finite verb (`, which non-Windows release builds omit`), or state the fact in its own predicate. Keep the reduced form for a short, adjacent modifier whose subject is the immediately preceding noun and nothing else.
- **Keep docstring flow continuous.** Progress from operational behavior to the constraints and invariants that govern it within the existing paragraph structure. Do not isolate a single explanatory sentence as a trailing paragraph, and do not promote a subordinate constraint into a standalone assertion that loses the operation it constrains.

Use these pairs to calibrate the audit boundary:

| Existing prose                                                                                                                                                              | Audit result                                                                                                             | Reason                                                                         |
| :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| `The socket closes after the client sends EOF.`                                                                                                                             | `After the client sends EOF, the socket closes.`                                                                         | The event order frames the entire action.                                      |
| `Return the fallback payload if the header is missing.`                                                                                                                     | Keep.                                                                                                                    | The short restriction is clear in a one-line docstring summary.                |
| `No caller can supply one.`                                                                                                                                                 | Keep.                                                                                                                    | The verified negative universal defines the API boundary precisely.            |
| `The command writes no cached entries.`                                                                                                                                     | `The command does not write cached entries.`                                                                             | The verb-position negation preserves the write-only scope.                     |
| `The supervisor restarts the worker, dropping every queued job.`                                                                                                            | `The supervisor restarts the worker and drops every queued job.`                                                         | Co-predication drops the participle without splitting the sentence.            |
| `The supervisor restarts the worker. That drops every queued job.`                                                                                                          | Rejoin the halves.                                                                                                       | `That <verb>` bridges a split the prose did not need.                          |
| `...without the schema file. That file is absent from fresh checkouts.`                                                                                                     | `...without the schema file, which fresh checkouts omit.`                                                                | Demonstrative noun-echo. Fold the modifier into the noun's first appearance.   |
| `The existence check is what keeps the spawn from failing.`                                                                                                                 | `Guarding on file existence keeps the spawn from failing.`                                                               | The cleft buries the verb behind a copula and an empty head.                   |
| `clap lists subcommands in the long help, so the long help is where the flag appears.`                                                                                      | `clap lists subcommands in the long help, not in the unknown-subcommand error.`                                          | A locative empty head is the same cleft; `is where` does not repair `is what`. |
| `...testable without the binary artifact, absent from non-Windows release builds.`                                                                                          | `...testable without the binary artifact, which non-Windows release builds omit.`                                        | The reduced appositive strands an adjective phrase without its subject.        |
| `It needs no root and no network and can run unattended.`                                                                                                                   | `It needs no root or network access to run unattended.`                                                                  | Three coordinators signal facts that were never parallel.                      |
| `The cache entry is dropped, which forces one refetch.`                                                                                                                     | Keep.                                                                                                                    | The relative clause has an immediate subject and one clear relation.           |
| `The build tool skips a bin whose required features are off, so a default build produces no artifact.`                                                                      | `Gated behind an off-by-default feature so default builds omit the binary.`                                              | Third-party mechanism restated as a general rule before the local one.         |
| `The stub returns Unsupported, which keeps the parser testable on every host.`                                                                                              | `To keep the parser testable on every host, the stub returns Unsupported.`                                               | The purpose belongs in front, not on a causal trailer.                         |
| `The parser reports only the bad token and omits the listing, while the contract requires the listing, so this function appends it.`                                        | `On an unknown subcommand, prints the parser's error and appends the supported commands.`                                | Staged contrast delays the behavior behind a problem statement.                |
| `The scanner rejects a write silently under its tamper policy.`                                                                                                             | Keep.                                                                                                                    | External behavior the reader cannot act on the local rule without.             |
| `To keep the write arm compiling on every platform and exercisable by the integration suite, the device write is gated: on an unsupported platform it returns Unsupported.` | `The device write is gated. On an unsupported platform it returns Unsupported, to keep the integration suite compiling.` | A front-loaded purpose past 10 to 12 words postpones the subject.              |
| `The Retry mention above is deliberately not a cross-reference link, since a link to a platform-gated variant does not resolve on another platform.`                        | `Not cross-referenced: Retry is platform-gated.`                                                                         | Editorial mechanics of the docstring, compressed to the constraint.            |
| `The verbose flag is where the tool lists its subcommands, so a mis-invoking caller discovers the right one there.`                                                         | `The tool lists subcommands under the verbose flag, not in the unknown-subcommand error.`                                | Reader-experience narration replaced by the mechanical fact.                   |

## Substance and Verification

Delete prose that carries no useful claim, subject to ecosystem and public-documentation requirements.

- **Apply the information-subtraction test.** If synonyms for the name, parameters, and return type reproduce a comment or docstring, look for a missing constraint or delete the restatement. When documentation tooling or reader discovery requires a concise API summary, keep it.
- **Delete provenance.** Prose states the constraint, not where the constraint came from. Cut the audit, incident, ticket, PR, release, or conversation that produced a rule or a value: `added after the August outage`, `per the migration audit`, `observed during the parser rewrite`, `historically this was`. Version control holds that history. Keep an external citation a reader must open to verify a claim, and keep a date the reader must act on, such as a deprecation deadline.
- **Run the over-cutting check.** Before deleting a fact, name the surviving site that states it. If no authoritative site remains, restore the fact. When distinct audiences or generated documentation require duplicate statements, keep them.
- **Preserve rigorous nouns.** Keep the noun that gives a number or term its meaning: `200 concurrent requests`, not `200`; `atomic`, not an imprecise paraphrase.
- **Use the verb the mechanism executes.** Prefer `logs`, `writes`, `appends`, `skips`, and `returns` over `handles`, `manages`, or a carrier verb plus a nominalization. When `names` stands in for an operation, review the verb. Choose `logs`, `prints`, `includes`, `sets`, or `references` by layer. Keep `names` for literal naming operations. Respect established codebase distinctions between terms such as `logs`, `prints`, and `emits`.
- **Describe state as state.** When no transfer or ownership occurs, prefer `has`, `contains`, `ends with`, `is marked`, or `is preserved`.
- **Use stable technical terms.** Repeat the same name for the same component or concept. If a reader could interpret shorthand more than one way, expand it.
- **Avoid stale references.** Name variants, fields, and conditions instead of referring to `the first two arms` or `the remaining check`. Do not count items merely to introduce a list.
- **Keep examples transferable.** Use an example to show a concrete form or transformation. Remove source-local jargon and assumptions that fail outside the original codebase.
- **Separate evidence states.** Keep verified facts, tool output, inferences, and unknowns distinct. Flag a contradiction instead of smoothing it into plausible prose.
- **Add missing rationale.** When the code cannot carry an external constraint, required ordering, concurrency hazard, benchmarked threshold, or reason a wrong-looking choice is correct, document that fact.

## Diction

Apply diction last. A clean word list does not establish clear or correct prose.

[references/diction.md](references/diction.md) holds every lexical token this skill governs, including the never-generate list. Load it before composing replacement prose and before auditing diction. Treat its entries as model- and genre-sensitive review aids: when a listed word is the precise literal or technical term, keep it.

## Reporting

For a quick rewrite, return the corrected artifact. If a material ambiguity, factual conflict, or preserved uncertainty affects the result, explain it.

For an audit, lead with the resolved scope, selected mode, and material result.

Report outcome-affecting rewrites, deletions, restored facts, added rationale, contradictions, and unverified claims. State partial coverage, skipped checks, and untouched out-of-scope defects. If the audit finds no defect, say so without forcing another pass.

A clean verdict requires a named keep-or-change reason for every matched tripwire or suspected construction. Track the reasons during the audit. If a judgment is material or the user requests a full ledger, report the relevant reasons. Do not invent a defect to avoid a clean verdict.

For a full audit, also report which named-target files were absent from the diff but read, whether the adversarial reread found a defect, and whether the over-cutting check restored a deletion. When counts help the user assess coverage, report them.

Report each corrected claim with the authority you opened to settle it, and each claim you could not settle as unverified. Where a pass was delegated, report what the subagent returned, which patches you applied, and which you rejected with the reason for each; a delegated `ACCEPT` is reported as an accept, not as your own clean verdict.

## Maintenance

Before changing a rule or promoting a heuristic to an invariant, read [references/evidence.md](references/evidence.md). Do not attach an empirical claim to a rule without evidence that covers the same audience, artifact, and outcome.
