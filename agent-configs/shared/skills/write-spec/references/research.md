# Topic research

Research a user-directed topic to support understanding or a decision. Follow [documentation boundaries](document-boundaries.md). Research is informative and does not add requirements; a recommendation is optional when the objective is exploration.

## Assignment and boundaries

The assignment names the topic, objective, relevant questions, requested depth, today's date, and either an authorized output path or conversation-only output. Clarification belongs to the coordinator when the user's interests admit materially different scopes. Reuse an existing topic document where appropriate; an assignment does not require a new file.

Include any active brainstorm state and follow [Brainstorming boundary and conclusion](../../brainstorm/SKILL.md#brainstorming-boundary-and-conclusion). During active brainstorming, return findings and sources without saving reports or updating indexes. Defer durable documents even when an output path was assigned.

- For authorized durable output, write only the assigned document. Return any needed index, related-document, or public-decision updates to the coordinator.
- Do not ask the user, start agents, or run workflow skills such as `review-changes`.
- Run bounded probes only within the authorized scope, in temporary directories outside the repository. Report changes to active settings or external systems that need further authorization instead of assuming an investigation permits them.

## Evidence

- Gather evidence from primary sources: official documentation, source code, standards, and papers. Do not substitute memory for investigation.
- Pin sources to a version, tag, commit, or retrieval date. Distinguish shipped behavior from examples and proposals, and source inspection from runtime verification.
- State a paper's publication status and evaluation limits. Treat popularity measures as dated adoption signals, not evidence of quality.
- Retain findings, including negative results, when they serve the research objective, distinguish options, affect confidence, or establish meaningful limitations. Do not collect incidental measurements merely because a probe exposes them.
- Match depth to the user's objective. For a bounded feasibility question, stop requiring evidence once the decision is sufficiently supported; a requested deep dive can explore further relevant questions without becoming an approval gate.

## Document

Lead with a synthesis answering the questions and the important applicability limits. Introduce enough context to understand it without the session. Put deeper explanations, relevant findings, methods, and sources after the synthesis; do not substitute raw output or a link list. Write each paragraph on one line.

Use this frontmatter, retaining the actual conditions of observations:

```yaml
---
date: 2026-01-15
questions:
  - Which session stores support atomic compare-and-set?
observed-in: [Redis 7.4.2, PostgreSQL 17.2]
recheck-when: A store releases a major version or changes its transaction semantics.
---
```

Choose headings for the topic. Include:

- Scope and current applicability, followed by findings that answer the questions.
- Evidence labels such as `**Observed in <version or conditions>:**` for inspected documentation or source, bounded probes, and measurements. Distinguish inference and external claims.
- Methods and reproduction conditions needed to assess retained evidence.
- Alternatives and a recommendation when the objective calls for a choice; use a table when comparing three or more.
- Uncertainty and limitations, including what evidence would settle a material unknown.
- Sources.

Keep assigned work, pending acceptance checklists, routine validation commands and results, and project-direction history out of research. Explain an untested boundary when it limits a finding; let plans assign and track the work. Return qualifying requirement-level conclusions to the coordinator for the public decision record.

On a recheck, update the synthesis, applicability, and frontmatter to reflect the evidence actually refreshed. Preserve dates and conditions for retained older observations; do not relabel them as tested on the new version. Remove obsolete advice and irrelevant material without adding a historical correction section.

## Return

Return at most 300 words: the synthesis, consequential findings, limitations, and the saved path if any. For conversation-only output, include sources needed to assess the evidence. The summary limit does not constrain an authorized deep-dive document.
