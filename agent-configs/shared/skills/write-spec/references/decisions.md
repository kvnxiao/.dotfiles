# Historical decision records

Preserve consequential historical evaluations that would otherwise be costly to repeat. Use this format when consulting, recording, compacting, pruning, or removing public decisions. Keep implementation attempts and execution history in private plans.

## Eligibility and retrieval

Record a direction only when it materially affects functional requirements, nonfunctional requirements, or their feasibility. Functional requirements include capabilities, business rules, behavior, and user experience. Nonfunctional requirements include scale, performance, reliability, privacy, compatibility, and architectural constraints needed for those guarantees.

Require an actual consequential evaluation and a reusable conclusion that current documentation does not already supply. If deleting the entry would lose only facts stated in the spec or architecture documents, omit it. Do not create entries merely to restate the selected design, enumerate hypothetical alternatives, or invent retrospective reasons for an existing choice. When the evaluation's basis is unavailable, ask the coordinator for evidence rather than reconstructing history from current code.

Describe the outcome and trade-off first. Include a mechanism only when necessary to explain the limitation or reevaluation condition. For example, rejecting offline editing is a product decision; choosing internal message types is ordinarily a plan detail. An experiment can support a qualifying decision without becoming a separate decision entry.

When selecting an approach or investigating a blocker, search relevant topics and identifiers in the existing record. Reuse a conclusion while its basis applies. Reconsider the changed assumption when its reevaluation condition is met; do not treat rejection as permanent. Do not load all decisions on every task.

## Location and format

Honor the repository's location; otherwise start with `docs/decisions.md`. Group entries by topic, not date. The document starts with a brief scope statement, followed by H2 topic headings and H3 entries:

```markdown
# Decisions

Evaluated directions that affect the product contract or its feasibility.

## Topic

### DEC-descriptive-slug — Evaluated direction

**Disposition:** Not selected | Deferred | Superseded

**Requirement impact:** The capability, behavior, experience, or system guarantee affected.

**Reason:** The consequential limitation or trade-off.

**Basis:** Relevant evidence, constraints, or explicit product preferences; link public sources where useful.

**Reevaluate when:** The changed condition that would justify reconsideration.
```

Select one disposition per entry. Distinguish measured failure from a deliberate trade-off or a deferral. Use a unique descriptive `DEC-` identifier and preserve it when editing or moving the entry. Link governing requirements when useful, but explain the impact in plain language. Keep the chosen contract in the spec rather than duplicating it here. If no useful reevaluation condition is known, say what would need new evidence instead of inventing a date.

Keep entries historical: describe the abandoned or deferred direction, why it was unsuitable, and what would justify reconsideration. An optional brief scope cue or link can orient the reader, but the historical conclusion must make sense without following it. Do not summarize current requirements or architecture. Link technical evidence rather than copying it.

When topic detail obscures the overview or needs independent maintenance, move it to `docs/decisions/<topic>.md`. Keep `docs/decisions.md` as a short `Topic | Scope` index linking those files. Each topic file has an H1 topic title, a brief scope, optional H2 subtopics, and the same H3 entry blocks. Repair affected links and preserve entry identifiers. Do not create one file per entry by default.

## Writing and maintenance

Record settled conclusions within the authorized documentation scope. During brainstorming, keep proposed entries in the conversation until the session concludes. Do not turn a documentation write into permission to publish private records or commit files.

Adding or revising an entry triggers maintenance of overlapping records: those evaluating the same direction, depending on the same governing constraint, or having conclusions changed by the new finding. Sharing a broad topic alone does not require reviewing every entry.

- Update an equivalent entry instead of appending a duplicate.
- Merge repeated conclusions and context where one coherent entry preserves their meaning.
- Remove entries whose useful content is already fully explained in current documentation; preserve unique reasons that would otherwise be lost.
- Update affected reasons and reevaluation conditions; remove superseded statements that no longer help.
- Preserve distinct, relevant limitations and trade-offs.
- Repair affected public references. Do not replace removed links with links to private plans.

Do not silently resolve conflicting product choices through compaction. Reconcile them against evidence and settled requirements; return an unresolved choice to the coordinating workflow.

Handle explicit maintenance requests according to their scope:

| Request           | Action                                                                                    |
| :---------------- | :---------------------------------------------------------------------------------------- |
| Review decisions  | Propose corrections or removals without editing.                                          |
| Compact decisions | Shorten and consolidate while preserving unique, relevant conclusions.                    |
| Prune decisions   | Assess the selected scope and remove entries that no longer prevent useful repeated work. |
| Remove a decision | Remove the specified entry and repair affected references.                                |

Do not require an archive, deletion ledger, or new approval for a deletion the user already requested. Git provides recovery. Broader cleanup happens on request; ordinary work does not trigger a scan of the entire record.
