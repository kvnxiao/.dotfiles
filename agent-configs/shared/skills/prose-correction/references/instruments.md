# Full-audit instruments

Load this reference only for a full audit or recurring ambiguity in a smaller pass. After reading the prose, run the mechanical tripwires. A match prompts a decision; it does not establish a defect by itself.

## Mechanical tripwires

- **Trailing modifier:** Verify that `, which ...`, `, where ...`, or comma plus `-ing` has an immediate subject and a clear logical relation. If its scope or causal force is ambiguous, split it.
- **Condition placement:** If a trailing temporal or conditional clause frames a long or multi-branch main clause, move it before the main clause. If a short trailing condition is restrictive or focal, preserve it.
- **Signature restatement:** Delete internal documentation that synonyms for the name, parameters, and return type reproduce without adding a constraint. Preserve documentation required for public discovery or ecosystem completeness.
- **Dummy verb:** Replace an incidental carrier verb paired with a nominalization, such as `performs validation`, `handles serialization`, `implements the transformation`, or `provides configuration`. If the noun names a concrete object, keep it.
- **Ambiguous reference:** If `from there`, `at that point`, `in that case`, or a bare `this` or `it` lacks an immediate unambiguous referent, name the file, buffer, component, or operation.
- **Bundled rules:** If operational rules joined by `and`, a semicolon, or a colon are independent, split them. If the clauses share a subject, mechanism, or consequence, keep the coordination.
- **Negation scope:** Verify a negative statement against its semantic scope and pragmatic context. If a positive equivalent is shorter and equally precise, prefer it. Preserve negative quantifiers and prohibitions that state the contract directly.
- **Tally or position:** Delete counts used only to introduce prose. Replace mutable-code references such as `the first`, `the second`, or `the remaining` with the item or shared property.
- **Fragment:** Complete a comment that opens with `Before`, `After`, `Once`, `Under`, `Without`, `Only`, or `To` but never reaches a main clause. If the following sentence carries the fact, a noun-phrase label may remain.
- **Narrator framing:** Delete intensifiers, indefinite agents, prose self-reference, staged reveals, and comprehension verbs such as `the reader knows`. Name the component, operation, field, or result instead.
- **Unsupported quantifier:** Verify every path covered by `all`, `every`, `never`, `always`, or a case sweep before keeping the quantifier.

## Full-pass checks

### Semantic advance

Require each sentence to add a fact, constraint, consequence, or necessary example. Delete a sentence that only paraphrases its predecessor. If a worked example makes an instruction executable, keep it.

### Single-read clarity

Read each prose item once with its surrounding code or document. Rewrite an ambiguous referent, condition, or scope. If the text is already clear, do not manufacture syntactic variation.

### Bidirectional fidelity

Compare the result against both the original prose and the authority.

- Restore a verified invariant, number, term of art, boundary, or hazard that the rewrite dropped.
- Delete an assertion the rewrite introduced without support.
- Flag a contradiction between prose and implementation instead of preserving the old claim in smoother words.

### Deletion safety

For each deleted fact, identify the authoritative site that still states it. If no site remains, restore the fact. When duplicate sites serve the same audience, keep the statement nearest the decision it governs.

### Adversarial reread

Run one final pass over items ruled clean. Try to find a concrete semantic, convention, clarity, or diction defect. If the pass finds one, correct it and reread the affected item once. Do not restart an unbounded file-wide loop.

### Idempotence check

Apply the audit criteria mentally to the finished result once more. Unexplained wording churn indicates that the criteria do not identify a concrete defect. Unless the new pass finds a named violation or a verified fact to add, keep the current text.

## Full-audit record

Track each in-scope item as kept, rewritten, deleted, or flagged. A kept comment or docstring must have a named purpose: public discovery, an ecosystem requirement, a constraint, a hazard, required ordering, rationale, or another fact the adjacent code does not provide efficiently.

Report material changes and coverage. Unless the user requests a complete ledger, do not reproduce every clean sentence.
