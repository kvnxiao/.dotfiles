# Experimental validation

Use this guidance for temporary experiments authorized by a deep request or by explicit direction to investigate a particular hypothesis.

## Select a consequential experiment

Identify the uncertainty and the competing outcomes that could change the recommendation. Reuse suitable benchmarks or fixtures before building a new probe. Choose a bounded experiment proportional to the potential benefit, available resources, and any user-supplied limits.

Before execution, establish:

- The hypothesis and the result that would support or weaken it.
- A comparable baseline and candidate, with representative input and execution conditions.
- Correctness checks derived from the required behavior, independently of the candidate.
- The target metric and relevant trade-off metrics, such as memory, errors, or write cost.

When requirements or the environment prevent a meaningful comparison, report that limitation instead of substituting an unrelated benchmark.

## Run and interpret

Use disposable copies or fixtures outside the target's working files. Changes made to a candidate are experimental; do not apply or commit them to the target.

Keep baseline and candidate conditions comparable. Account for relevant warmup, cache state, startup, workload distribution, and measurement overhead. Repeat or interleave trials when variation could change the conclusion; choose sampling effort from the workload rather than a universal count or percentage threshold.

A candidate that fails required behavior is not an improvement. Treat noise or an unsuitable workload as an inconclusive result. Diagnose unexpected outcomes when doing so could change the assessment.

State exactly what the result establishes. Validate the complete operation when necessary and feasible; otherwise retain the local conclusion and identify the missing end-to-end evidence. For example, a faster parser does not establish lower request latency when requests mostly wait for a database.

## Conclude the investigation

Stop experimenting when:

- The consequential uncertainty is resolved.
- Further trials are unlikely to change the recommendation.
- Noise, missing requirements, or unavailable resources prevent a defensible conclusion.
- A supplied resource or time limit is reached.

Retain useful conclusions, failed hypotheses, and conditions for revisiting them in session context. Return findings, evidence limits, and worthwhile follow-ups. Do not create a permanent experiment log or benchmark suite unless the user separately requests it.
