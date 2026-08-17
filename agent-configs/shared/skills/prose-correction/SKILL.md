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
- A demonstrative noun-echo: one sentence ends on a noun, the next opens `That <same noun>`.
- A cleft that delays the verb, such as `X is what keeps ...` or `the rendered help is what this asserts against`.
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

- **Quick rewrite:** Use for a sentence, paragraph, commit message, PR draft, or small named file. Unless the user requests an audit ledger, return only the corrected artifact. Do not delegate the verification pass; the orchestration costs more than the pass returns.
- **Change-set audit:** Use for an unnamed target, a completion check, or a normal review of changed prose. Read every changed prose item in context and report material findings. Delegate the verification pass.
- **Full audit:** Use for exhaustive coverage, broad public-documentation releases, or high-risk behavioral contracts. Before running this mode, read [references/instruments.md](references/instruments.md). Delegate the verification pass.

Grep and mechanical matches may order the work. They do not replace reading the prose in context.

### Delegate the verification pass

Composing a rewrite anchors you to it. A reviewer that holds the drafting history discounts its own repair traps and re-accepts its own unverified claims, so the verification pass runs in a fresh subagent with no drafting context.

Hand the subagent:

- The repository path and read tools. Do not hand it a frozen text bundle. Bidirectional fidelity means opening the authority, and the authority is often a file the prose never names: a lint config behind a claim about a sanctioned carve-out, a CI workflow behind a claim about what CI runs, a build recipe behind a claim about what enables a feature.
- The candidate diff, both sides. Fidelity runs against the original prose as well as the authority.
- The keep-reason ledger for items ruled clean without an edit. A full audit keeps far more than it rewrites, and a keep decision carries the same anchoring as a rewrite. Given the reasons, the subagent disputes a reason instead of regenerating churn.
- [references/instruments.md](references/instruments.md) and [references/diction.md](references/diction.md).

The subagent runs bidirectional fidelity, repair-trap detection, and the naturalness and idempotence checks, then returns `ACCEPT`, or `REVISE` with the named tripwire and one minimal patch per item. It does not open a negotiation. Apply each patch, or reject it with a named reason and report the rejection. Run this exchange once. A second delegated round only repeats the first.

## Core Procedure

1. **Model the reader.** Identify whether the artifact serves maintainers, newcomers, API consumers, operators, or another named audience.
2. **Classify the artifact.** Identify its ecosystem and layer: inline comment, docstring, commit, PR, architecture document, instruction file, or direct response.
3. **Extract the claims.** Reduce the source to concrete propositions. Separate invariants, conditions, consequences, hazards, rationale, and examples.
4. **Verify the claims.** Read the implementation or authoritative source. Mark each claim as verified, refuted, or unverified. Treat existing prose as a witness, not as evidence. When no authority is available, preserve the source's claims without increasing their certainty.
5. **Compose.** Preserve verified claims and flag material unknowns. When the authority establishes a replacement, correct a refuted claim. Use the artifact contract and discourse heuristics below. For a structural rewrite, compose from the claim list instead of copying the old clause pattern. For a local typo or mechanical defect, edit locally.
6. **Audit diction.** After the structural rewrite, read [references/diction.md](references/diction.md). Keep literal technical uses.
7. **Re-audit replacements.** Run every changed sentence through all priorities and heuristics. Include rules unrelated to the original trigger. Check each replacement against the repair traps above: a rewrite that swaps a bare `this` for a trailing relative, or a participle for a coordinator chain, has moved the defect rather than fixed it. If a replacement invents a fact, weakens a quantifier, obscures a dependency, or adds an unrelated defect, return it once to claim extraction and verification. If the retry fails, flag the unresolved defect and stop rewriting that item.
8. **Verify.** In a quick rewrite, compare the result with the source and authority yourself: restore any verified fact that was dropped, delete any fact the rewrite introduced, then read the finished prose once in context and revise ambiguous dependencies. In a change-set or full audit, delegate this pass to a fresh subagent under the contract above, then apply or reject its patches.

If a correct sentence still reads synthetic, generate multiple candidates. Vary syntax or information order deliberately. Select against semantic fidelity, artifact convention, and single-read clarity. Do not estimate probabilities. A candidate's apparent rarity does not justify its selection.

## Artifact Contracts

Follow an ecosystem's required form before these defaults. For example, Python one-line function docstrings use imperative summaries, while Go documentation names the declared symbol and uses a complete declarative sentence.

| Artifact                                     | Default contract                                                                                                                                                                                                                                                                                                                                                                                                       |
| :------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Docstring or API documentation**           | Follow ecosystem conventions. State behavior, side effects, errors, constraints, and usage information that callers need. Public discovery requirements may justify a concise summary that resembles the signature.                                                                                                                                                                                                    |
| **Git commit subject**                       | Use imperative mood and present tense with no trailing period. In the body, state the motivation and relevant behavior change.                                                                                                                                                                                                                                                                                         |
| **Inline comment**                           | State the mechanical constraint, invariant, hazard, or non-obvious ordering requirement in clipped present tense. Omit narrator framing, first person, and explanatory scaffolding: prefer `Accepts an explicit denylist so tests can inject arbitrary directories on any host` over `Taking the system-directory denylist as a parameter makes the denylist rule testable with injected directories on any platform`. |
| **Test comment, docstring, or harness code** | State the assertion or failure contract directly in indicative or imperative form: name the input, the expected outcome, and the regression it catches. Do not reduce a test to a truncated noun-phrase header. For a harness helper, state the skip condition and what a silent no-op would hide.                                                                                                                     |
| **Architecture document or RFC**             | Use third-person indicative prose. Use present tense for current behavior, past tense for completed work, and future or conditional forms for proposals. Name ambiguous actors.                                                                                                                                                                                                                                        |
| **PR title and body**                        | State the change and its cause directly. Distinguish verified results from risks, skipped checks, and planned work.                                                                                                                                                                                                                                                                                                    |
| **Instruction file**                         | Use direct imperative or infinitive instructions. Favor conventional, easily parsed phrasing over stylistic variation. Keep worked examples executable outside their original source.                                                                                                                                                                                                                                  |
| **Chat or direct deliverable**               | Lead with the verdict or result. Omit conversational preambles and redundant closing summaries.                                                                                                                                                                                                                                                                                                                        |

### Multi-line docstring order

Where the ecosystem does not dictate otherwise, order a multi-line docstring:

1. **Operational summary.** The primary action, in the ecosystem's required mood.
2. **Inputs, invariants, and preconditions.** What the caller must supply, what must hold on entry, and what the function refuses to recompute or assume.
3. **Failure paths, error mappings, and side effects.** Which condition maps to which terminal error, and what the call writes outside its return value.

A docstring that interleaves these — an authoritativeness constraint dropped between two execution steps, a side effect stated before the operation that causes it — forces the reader to reorder it. Rustdoc `# Errors`, Python `Raises:`, and Go's trailing error sentence already sit at position 3; keep them there.

## Discourse and Dependency Heuristics

Treat these as decisions, not phrase bans.

- **Place framing context early.** When given information, prerequisites, or short conditions frame an action, place them before it.
- **Preserve event order.** When sequence matters, state prerequisite operations before dependent operations. If a short trailing temporal or conditional clause is restrictive, focal, or easier to parse in that position, it may remain.
- **Keep dependencies local.** If the subject, scope, or causal relation of a trailing participial phrase or non-restrictive relative clause is ambiguous, review the clause. If the relation is local and clearer than a split sentence, keep it.
- **Use topic continuity.** Give the grammatical subject to the current discourse topic. When the affected entity matters more than the actor, use agentless passive voice.
- **Coordinate related facts.** When predicates share a subject, condition, or mechanism, keep them together. Split independent operational rules.
- **Preserve negation scope.** If a positive verb states the same fact more directly, prefer it. If a negative quantifier such as `no`, `none`, or `neither` expresses the contract precisely, keep it. Do not rewrite `No caller can supply one` merely to move the negation.
- **Name ambiguous references.** If the referent of a pronoun or deictic such as `from there`, `at that point`, or a bare `this` is not immediate and unambiguous, name it.
- **State the referent, do not point at it.** Delete a clause whose only work is pointing back at a prior noun, such as `X is one of them`, `The CLI polls for that file`, or `it does this for that`. Naming a referent means stating the fact about the named component once, not adding a sentence that reintroduces the noun. Prefer `clap already renders the no-subcommand path with the subcommand listing` over `The no-subcommand path is one of them; clap already renders it`.
- **State rationale where the artifact needs it.** If a purpose infinitive preserves the actor and goal, use it instead of `so that it can`, `in order to`, or `so as to`. Keep a trailing `so` only for an immediate mechanical consequence.
- **Coordinate instead of fragmenting.** Removing a trailing participle or relative clause rarely requires two sentences. When the facts share a subject or mechanism, join them with parallel predicates or one compound sentence. Two back-to-back short sentences that force the reader to reassemble a relation are worse than the trailing clause they replaced.
- **Consolidate, do not chain.** Coordination is a structure, not a rescue. Judge a chain by whether its members are of one kind, never by how many there are: `downloads, unpacks, and links the binary` is three like predicates over one subject and stands as written, while `needs no elevation and no Defender and can run unattended` welds two requirements to a capability and should become `needs no elevation or Defender to run unattended`.
- **Give the verb its subject.** A cleft delays the predicate behind a copula and an empty head: `the rendered long help is what this asserts against`, `The existence check on disk is what keeps the spawn from panicking`. Name the actor and let it act: `this test asserts against the rendered long help`, `Guarding on disk existence keeps a plain cargo test from spawning a path that does not exist`. Keep a cleft only where the sentence contrasts one candidate against a named alternative.
- **Keep docstring flow continuous.** Progress from operational behavior to the constraints and invariants that govern it within the existing paragraph structure. Do not isolate a single explanatory sentence as a trailing paragraph, and do not promote a subordinate constraint into a standalone assertion that loses the operation it constrains.

Use these pairs to calibrate the audit boundary:

| Existing prose                                                                             | Audit result                                                             | Reason                                                                       |
| :----------------------------------------------------------------------------------------- | :----------------------------------------------------------------------- | :--------------------------------------------------------------------------- |
| `The socket closes after the client sends EOF.`                                            | `After the client sends EOF, the socket closes.`                         | The event order frames the entire action.                                    |
| `Return the fallback payload if the header is missing.`                                    | Keep.                                                                    | The short restriction is clear in a one-line docstring summary.              |
| `No caller can supply one.`                                                                | Keep.                                                                    | The verified negative universal defines the API boundary precisely.          |
| `The command writes no cached entries.`                                                    | `The command does not write cached entries.`                             | The verb-position negation preserves the write-only scope.                   |
| `The launcher re-invokes the helper, triggering one UAC prompt.`                           | `The launcher re-invokes the helper and raises one UAC prompt.`          | Co-predication drops the participle without splitting the sentence.          |
| `The launcher re-invokes the helper. That raises one UAC prompt.`                          | Rejoin the halves.                                                       | `That <verb>` bridges a split the prose did not need.                        |
| `...without the binary artifact. That artifact is absent from non-Windows release builds.` | `...without the binary artifact, which non-Windows release builds omit.` | Demonstrative noun-echo. Fold the modifier into the noun's first appearance. |
| `The existence check on disk is what keeps the spawn from panicking.`                      | `Guarding on disk existence keeps the spawn from panicking.`             | The cleft buries the verb behind a copula and an empty head.                 |
| `It needs no elevation and no Defender and can run unattended.`                            | `It needs no elevation or Defender to run unattended.`                   | Three coordinators signal facts that were never parallel.                    |
| `The bin is skipped, which keeps the artifact off macOS.`                                  | Keep.                                                                    | The relative clause has an immediate subject and one clear relation.         |

## Substance and Verification

Delete prose that carries no useful claim, subject to ecosystem and public-documentation requirements.

- **Apply the information-subtraction test.** If synonyms for the name, parameters, and return type reproduce a comment or docstring, look for a missing constraint or delete the restatement. When documentation tooling or reader discovery requires a concise API summary, keep it.
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

Where the verification pass was delegated, report what the subagent returned and what you did with it: patches applied, patches rejected with the reason for each, and any claim it could not verify. A delegated `ACCEPT` is reported as an accept, not as your own clean verdict. If the pass was skipped, say so and say why.

## Maintenance

Before changing a rule or promoting a heuristic to an invariant, read [references/evidence.md](references/evidence.md). Keep house preferences labeled as preferences. Do not attach empirical claims to them without evidence that covers the same audience, artifact, and outcome.
