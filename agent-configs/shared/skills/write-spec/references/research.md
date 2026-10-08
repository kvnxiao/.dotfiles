# Research for a spec

Research records the evidence behind a spec's decisions as dated documents. It is informative: it never adds requirements, and it is not edited to follow later spec changes. A `spec-researcher` agent follows this file for one assigned question; the coordinating session follows it when it researches in-session.

## Assignment and boundaries

The assignment names one question, the decision it informs, the output path, and today's date.

- Write only the assigned document. Do not edit the spec, other research, or code.
- Do not ask the user, start agents, or run workflow skills such as `review-changes`. Return unresolved points to the coordinator.
- Run bounded probes, such as installing a package or calling an API, only in a temporary directory outside the repository.

## Research

- Gather the evidence fresh from primary sources: official documentation, source code, standards, and papers. Never write from memory.
- Pin each source to a version, tag, commit, or retrieval date.
- Distinguish a shipped feature from an example or proposal, and source inspection from runtime verification.
- State a paper's publication status and evaluation limits: `Preprint; evaluated on Python repositories only.`
- Treat download counts and stars as adoption signals dated to their retrieval, not as evidence of quality.
- Stop at the evidence the decision needs. A design does not need an exhaustive market survey.

## Document

Save the document at the assigned path. It stands alone: a reader understands it without the spec, the session, or other research. Synthesize the evidence; never substitute a link list or raw tool output. Write each paragraph on one line.

Start with frontmatter:

```yaml
---
date: 2026-01-15
questions:
  - Which session stores support atomic compare-and-set?
observed-in: [Redis 7.4.2, PostgreSQL 17.2]
recheck-when: A store releases a major version or changes its transaction semantics.
---
```

Choose headings that fit the topic. The body has:

1. A one-paragraph verdict that answers the questions.
2. Why the research started: the decision it informs.
3. Findings. Mark a claim, table cell, or section `**Observed in <version or conditions>:**` when you:
   - inspected source or documentation at that version.
   - ran a bounded probe.
   - measured an outcome under stated conditions.

   Leave reasoning and others' claims unmarked.
4. The alternatives compared, as a table when there are three or more, with the criteria that separate them.
5. A recommendation for the decision.
6. Gaps: what remains unobserved or unmeasured, and what would settle it.
7. Sources.

Do not record provenance about the session, such as who asked or which tools ran.

When the assignment rechecks an existing document, rewrite it in place with the new date and versions.

## Return

Return at most 300 words: the verdict, the findings that change the decision's options, the gaps, and the document path.
