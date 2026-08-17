# Full-audit instruments

Load this reference only for a full audit or recurring ambiguity in a smaller pass. After reading the prose, run the mechanical tripwires. A match prompts a decision; it does not establish a defect by itself.

## Mechanical tripwires

- **Trailing modifier:** Verify that `, which ...`, `, where ...`, or comma plus `-ing` has an immediate subject and a clear logical relation. If its scope or causal force is ambiguous, split it.
- **Condition placement:** If a trailing temporal or conditional clause frames a long or multi-branch main clause, move it before the main clause. If a short trailing condition is restrictive or focal, preserve it.
- **Signature restatement:** Delete internal documentation that synonyms for the name, parameters, and return type reproduce without adding a constraint. Preserve documentation required for public discovery or ecosystem completeness.
- **Dummy verb:** Replace an incidental carrier verb paired with a nominalization, such as `performs validation`, `handles serialization`, `implements the transformation`, or `provides configuration`. If the noun names a concrete object, keep it.
- **Ambiguous reference:** If `from there`, `at that point`, `in that case`, or a bare `this` or `it` lacks an immediate unambiguous referent, name the file, buffer, component, or operation.
- **Artificial causal connector:** Flag a sentence opening with `That <verb>`, such as `That raises`, `That keeps`, or `That becomes`, and a trailing `, so ...` that carries a result. Both usually bridge a split the prose did not need. Rejoin the halves with parallel predicates, or give the second fact its own named subject. Keep a trailing `so` for an immediate mechanical consequence.
- **Demonstrative noun-echo:** Flag a sentence ending on a noun where the next sentence opens `That <same noun>`, such as `... without the binary artifact. That artifact is absent from non-Windows release builds.` The echo re-announces a referent the reader has not lost. Fold the second sentence's modifier into the noun's first appearance with a restrictive relative or a prepositional phrase. Keep the split where the second sentence carries an independent operational rule rather than a modifier.
- **Cleft:** Flag `X is what <verb>`, `what X does is`, and `it is X that <verb>`. The copula and the empty head delay the predicate, such as `The existence check on disk is what keeps the spawn from panicking` or `the rendered long help is what this asserts against`. Promote the actor to subject and let it act. Keep a cleft that contrasts one candidate against a named alternative already in the discourse: `The re-read, not the exit code, is what the CLI trusts` earns its cleft because both candidates are live and the sentence exists to choose between them. A cleft with no competing alternative on the page is delay, not contrast.
- **Coordinator chaining:** Flag repeated `and` or `or` that joins facts of unlike kind, especially where a participle was just removed. Test the members, not their number: `downloads, unpacks, and links the binary` coordinates three predicates of one kind over one subject and is well-formed at any length, whereas `needs no elevation and no Defender and can run unattended` welds two requirements to a capability. Recast a heterogeneous chain as a compound object, a parallel list, or a purpose infinitive. A serial list of like predicates is not a defect.
- **Placeholder referent:** Flag a clause whose only content points back at a prior noun, such as `X is one of them`, `The CLI polls for that file`, or `it does this for that`. State the fact about the named component instead.
- **Over-fragmentation:** Flag consecutive short sentences that share a subject and were produced by splitting one clause. Recombine them unless each states an independent operational rule.
- **Bundled rules:** If operational rules joined by `and`, a semicolon, or a colon are independent, split them. If the clauses share a subject, mechanism, or consequence, keep the coordination.
- **Negation scope:** Verify a negative statement against its semantic scope and pragmatic context. If a positive equivalent is shorter and equally precise, prefer it. Preserve negative quantifiers and prohibitions that state the contract directly.
- **Tally or position:** Delete counts used only to introduce prose. Replace mutable-code references such as `the first`, `the second`, or `the remaining` with the item or shared property.
- **Fragment:** Complete a comment that opens with `Before`, `After`, `Once`, `Under`, `Without`, `Only`, or `To` but never reaches a main clause. If the following sentence carries the fact, a noun-phrase label may remain.
- **Narrator framing:** Delete intensifiers, indefinite agents, prose self-reference, staged reveals, and comprehension verbs such as `the reader knows`. Name the component, operation, field, or result instead.
- **Unsupported quantifier:** Verify every path covered by `all`, `every`, `never`, `always`, or a case sweep before keeping the quantifier.

## Full-pass checks

Bidirectional fidelity, deletion safety, the adversarial reread, and the idempotence check run in the delegated verification subagent. Semantic advance and single-read clarity run in the primary agent during composition. The sections below are written for whichever agent runs them.

### Semantic advance

Require each sentence to add a fact, constraint, consequence, or necessary example. Delete a sentence that only paraphrases its predecessor. If a worked example makes an instruction executable, keep it.

### Single-read clarity

Read each prose item once with its surrounding code or document. Rewrite an ambiguous referent, condition, or scope. If the text is already clear, do not manufacture syntactic variation.

### Bidirectional fidelity

Compare the result against both the original prose and the authority. Treat every claim as unverified until you open the authority and read it. A claim can be plausible, internally consistent, and false.

- Restore a verified invariant, number, term of art, boundary, or hazard that the rewrite dropped.
- Delete an assertion the rewrite introduced without support.
- Flag a contradiction between prose and implementation instead of preserving the old claim in smoother words.
- Follow a claim to the file that settles it, including files the prose never names. A claim about a sanctioned lint carve-out is settled by the lint config, a claim about what CI runs by the workflow, a claim about what enables a build feature by the build recipe. A claim whose authority you could not locate is reported as unverified, never as accepted.

### Deletion safety

For each deleted fact, identify the authoritative site that still states it. If no site remains, restore the fact. When duplicate sites serve the same audience, keep the statement nearest the decision it governs.

### Adversarial reread

Run one final pass over items ruled clean, both the rewritten items and the ones kept unedited. Try to find a concrete semantic, convention, clarity, or diction defect. Read each rewritten item as prose you did not write: check it against the repair traps in `SKILL.md`, since a rewrite that trades a bare `this` for a trailing relative, or a participle for a coordinator chain, has relocated its defect rather than removed it. For a kept item, argue against its recorded keep-reason rather than restating the tripwire that reason already answers. If the pass finds a defect, correct it and reread the affected item once. Do not restart an unbounded file-wide loop.

### Idempotence check

Apply the audit criteria mentally to the finished result once more. Unexplained wording churn indicates that the criteria do not identify a concrete defect. Unless the new pass finds a named violation or a verified fact to add, keep the current text.

## Delegated verification contract

`SKILL.md` sends the verification pass to a fresh subagent on change-set and full audits. Both sides hold to this contract.

The primary agent supplies the repository path and read tools, the candidate diff with both sides, the keep-reason ledger for unedited items, and this file with `references/diction.md`. It does not supply its drafting rationale, its candidate history, or its own assessment of the rewrite. Those are the anchors the delegation exists to remove.

The subagent runs bidirectional fidelity, deletion safety, the adversarial reread, and the idempotence check. It returns `ACCEPT`, or `REVISE` carrying, per item: the file and line, the named tripwire or refuted claim, the authority it read, and one minimal patch. Every patch names the rule behind it, and the subagent does not open a negotiation.

The primary agent applies each patch or rejects it with a named reason, then reports both. The exchange runs once. A second delegated round repeats the first at full cost.

## Full-audit record

Track each in-scope item as kept, rewritten, deleted, or flagged. A kept comment or docstring must have a named purpose: public discovery, an ecosystem requirement, a constraint, a hazard, required ordering, rationale, or another fact the adjacent code does not provide efficiently.

Report material changes and coverage. Unless the user requests a complete ledger, do not reproduce every clean sentence.
