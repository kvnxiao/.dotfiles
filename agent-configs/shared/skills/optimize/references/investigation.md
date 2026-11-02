# Shared optimization contract

Optimize latency, successful throughput, resource consumption, and operating cost while preserving functional and non-functional requirements. Work autonomously and return recommendations. Use judgment when information is incomplete; state material assumptions and limitations without asking the user questions.

## Understand the operation

Establish the business result, the operation's useful completion point, and its relevant workload from the request and repository evidence. Read applicable instructions and the contracts, callers, tests, and documentation needed to understand the operation.

Distinguish required behavior from current design choices. Treat observable behavior as compatibility evidence; do not silently discard an uncertain requirement. For example, a cache proposal must preserve the required freshness of returned data.

Consider current and credibly anticipated demand. Support future demand with plans or evidence rather than invented growth. Examine relevant ordinary and exceptional conditions, such as startup, large inputs, skewed demand, bursts, or slow dependencies. Use these conditions to assess alternatives without requiring a formal scenario document.

## Choose investigation effort

Use default mode unless the user explicitly requests deep investigation. Keep scope and effort independent: architectural analysis can be inexpensive, and a local optimization can require extensive measurement.

- In default mode, prioritize inspection, existing measurements, and inexpensive checks that do not change the target. Propose new probes, benchmarks, and prototypes as follow-up work requiring explicit user direction.
- In deep mode, develop competing approaches more fully and follow their consequences. The request authorizes selective temporary experiments that could change the recommendation; the entry skill links to their validation rules.
- In either mode, return findings without applying production changes. Keep investigation state in the session. Persist findings only on explicit request, using the user's repository conventions as a separate writing task.

Keep experiments isolated from source files, user work, and live systems. Deep mode does not authorize deployments or other external mutations. If available permissions or resources prevent validation, report the specific gap and continue useful investigation.

## Explore and assess alternatives

Explore materially different approaches before choosing a recommendation. Follow their implications across the operation rather than stopping at the first plausible local improvement. Keep brief conclusions about investigated approaches in session context. Revisit an approach when new evidence or changed assumptions could alter its conclusion; avoid repeating unchanged investigations.

Explain the limiting mechanism and the work each proposal removes, adds, or transfers. Distinguish reduced work from reduced latency. For example, moving computation to writes can accelerate reads while increasing update and recovery costs.

Estimate whole-operation benefit when the evidence permits it. State assumptions and distinguish estimates from measurements. A faster component does not establish a faster complete operation.

Compare expected benefit with implementation effort, migration cost, and correctness risk. Identify important resource trade-offs rather than hiding them in a single score. Prefer the least expensive investigation that can resolve a consequential uncertainty.

Use applicable domain guidance selectively. Treat outside optimization recipes as candidate mechanisms; verify their conditions and retain this task's scope and authorization boundaries.

## Return findings

Return concise, prioritized, numbered opportunities. For each, explain the current cost and location, concrete alternative, expected or measured benefit, and material conditions or trade-offs. Distinguish facts established by inspection from hypotheses and measured outcomes. Do not invent speedups.

Separate worthwhile further investigations from supported recommendations. Specify the question, the missing evidence, and the next observation or experiment that could resolve it. A local result must retain its local scope.

Include rejected alternatives when they explain a recommendation. Report important coverage or evidence limitations without a mandatory coverage ledger. State when the investigation found no worthwhile improvements.
