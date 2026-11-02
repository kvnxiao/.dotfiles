# Coordinate an optimization review

Use this procedure for the agent answering the user. Investigators receive a resolved assignment and the shared investigation contract, rather than this coordination procedure.

## Resolve scope once

Honor explicit targets and exclusions. Otherwise infer the relevant feature or operation from the active task; when no such context exists, inspect the repository to identify its principal operations. State the inferred scope.

Review the selected system as it exists, including unchanged code needed to understand its behavior and costs. A clean Git tree does not make the investigation empty. For a request specifically about a diff, focus findings on costs introduced or exposed by that diff.

Establish the shared requirements and workload context before dividing the investigation. Preserve existing authorization. Honor restrictions from an active brainstorm on experiments or writes that depend on unresolved decisions.

## Assign relevant work

Consider both architecture and implementation for a broad review. Use the selected scope for a focused entry point. Read only the applicable investigation references.

Delegate when independent investigation justifies its context and tool cost. Use available general-purpose investigators with the supplied contract; avoid profiles that impose a different workflow. Work in-session when delegation is unavailable or the assignment is small. Do not require installing plugins or custom agent profiles.

For each delegate, supply:

- The target, relevant paths, scope, selected mode, and exclusions.
- The business operation, requirements, workload evidence, and known uncertainties.
- The shared contract and assigned area reference paths.
- The specific question to investigate and any authorized experiment limits.

Require delegates to inspect the actual evidence, stay within their assignment, and return findings to the coordinator. Delegates must not start other skills or agents, ask the user questions, or apply changes to the target. Pass the experiment reference before a delegate performs authorized deep-mode validation. Keep concurrent experiments isolated and avoid measuring competing workloads on shared resources.

## Reconcile findings

Verify findings against the requirements and available evidence. Deduplicate by cause, and identify dependencies or incompatible alternatives. Do not add together the benefits of replacing a component and tuning the component being replaced.

Use cross-area findings to reassess affected conclusions. Share the new evidence with the relevant investigator instead of restarting unchanged work. For substantial redesigns, compare whether a simpler change achieves most of the same benefit.

Stop when remaining investigation is unlikely to change the recommendations within the selected effort and available evidence. Return the shared contract's findings and specific unresolved questions as follow-up investigations.
