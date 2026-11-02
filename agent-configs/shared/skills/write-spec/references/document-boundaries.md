# Documentation boundaries

Apply these rules when writing or maintaining project documents. Reuse rules already loaded in the current context; read linked formats only for the work that needs them.

## Information ownership

| Artifact                | Owns                                                                                                                           |
| :---------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| Spec                    | The intended end state: functional and nonfunctional requirements, durable constraints, and observable acceptance scenarios.   |
| Research                | User-directed topic knowledge, relevant evidence, conclusions, methods, and limitations.                                       |
| Public decision record  | Consequential evaluated directions, their requirement impact, reasons, and reevaluation conditions.                            |
| Plans, tasks, and state | Implementation approaches, experiments, technical dead ends, execution history, progress, and validation commands and results. |
| README and guides       | Project introduction, available behavior, first use, and supported user or contributor procedures.                             |
| Developer documentation | Selective explanations of important, stable aspects of implemented code that source and contracts do not adequately explain.   |

Keep the spec present-to-future-facing. Code can lag behind it; missing implementation does not justify weakening a requirement. Leave mechanisms open unless they are required to establish the contract. Findings can require a new decision: amend affected requirements, scenarios, and constraints together after that decision is settled. Approval does not establish that every implementation detail is known.

Keep plans, tasks, handoffs, scratch experiments, and spikes private and Git-ignored by default. Use repository ignore files for new private paths. Do not untrack existing files or publish private material without an explicit user choice. Treat existing tracking as context to report, not permission to publish more private records. Writing public documentation does not authorize committing or pushing it.

Keep public documents useful for current readers and intended goals. Exclude execution bookkeeping and development chronology. Retain history only for a current reader need, such as migration, interpreting relevant evidence, or avoiding a consequential repeated investigation through the public decision record. Public explanations must not depend on ignored plans or session history.

## Relevance and structure

Give each claim one authoritative home. Allow concise summaries and links, but do not copy complete contracts into multiple documents. Lead with the conclusion, scope, and important limits before detail. Introduce prerequisite concepts locally; a link supplies depth, not the explanation needed to understand the current passage.

Organize by cohesive topic and reader need, not assignment, session, or date. Reuse an appropriate destination before creating another file. Keep indexes navigational; update applicability beside the affected claim instead of adding correction tables elsewhere.

Research can support a decision or a deep understanding of a topic before next steps are known. Retain evidence when it contributes to that objective, distinguishes options, changes confidence, or establishes a meaningful limitation. Preserve the conditions of retained observations; do not turn an old result into evidence about an untested version. Update applicability and conclusions, and remove obsolete advice and irrelevant material.

Retain probes and tools for a relevant experiment, reproducibility need, or ongoing operational purpose. Deliberately select and document reusable experimental artifacts before making them public; do not publish every spike or routine run output.

## Proportionate maintenance

Avoid detailed architecture inventories and diagrams during rapid implementation change. Document stable ownership, important interactions, or operational constraints when useful. Correct known contradictions in scoped documents, without requiring continuous synchronization or a sweep after every code edit.

Apply these boundaries while writing and flag concrete violations encountered during existing review. Do not add a separate relevance audit, reviewer, mandatory report, or recurring full-corpus scan. Broaden an investigation only when the requested scope or a concrete dependency warrants it.
