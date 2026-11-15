# Investigate an existing system's contract

Investigate enough of the requested scope to explain its purpose and define observable requirements. Adapt depth to the project and the user's questions. Use this guidance with the [research contract](../../write-spec/references/research.md) and [reconciliation rules](../../review-spec/references/reconciliation.md).

## Establish purpose and boundaries

Read product documentation, examples, public interfaces, and relevant existing decisions. Identify the users, the problem being solved, and the outcomes the system supports. Treat business purpose inferred from names or implementation structure as a hypothesis until evidence or the user establishes it. Do not invent historical reasons for existing choices.

Identify entrypoints, external integrations, state owners, and deployment or configuration variants that affect behavior. Use generated and vendored code only when needed to understand an actual contract. A repository summary can orient the investigation, but does not establish requirements or completeness.

## Trace representative workflows and their boundaries

Start from an observable action and follow validation, authorization, state transitions, persistence, external effects, and the returned result. Read tests and fixtures alongside the relevant implementation. Expand into exceptional paths where the outcome differs. Follow cross-area dependencies until the contract can be explained without guessing.

Trace each declaration syntax or data format through the operations that create, inspect, modify, remove, or restore its contents. Acceptance by one operation does not establish support in another. For example, a manifest can accept several targets while its removal command only handles a single-target declaration.

Check option combinations that select different execution paths, such as structured output with automatic confirmation. Inspect their side effects, warnings, and failure results; testing each option separately does not establish their combined behavior.

Check failures while reporting the result of an operation that has already saved data or completed an external action. Define the resulting state, failure reporting, and retry outcome separately from failures before those effects. For example, a command can save data successfully and then fail to write its result to a closed stdout pipe.

Use the following questions where they apply; omit irrelevant topics instead of manufacturing requirements:

| Area                                  | Investigate                                                                                                           |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Core functionality and business rules | Actors, preconditions, decisions, permissions, successful outcomes, and deliberate exclusions.                        |
| State and invariants                  | Ownership, lifecycle transitions, uniqueness, ordering, atomicity, and behavior under concurrent actions.             |
| Interfaces and compatibility          | Commands, APIs, configuration precedence, defaults, events, file formats, persisted schemas, and migration behavior.  |
| Failures and recovery                 | Invalid or boundary inputs, partial success, cancellation, retries, duplication, timeouts, interruption, and restart. |
| Security and privacy                  | Trust boundaries, access restrictions, secret handling, data visibility, and retention or deletion guarantees.        |
| Quality guarantees                    | Evidence for performance, scale, availability, resource limits, platform support, and dependency constraints.         |

Separate intended guarantees from incidental mechanisms. For example, a transaction may establish an atomicity guarantee; its internal helper names do not become requirements. Preserve exact names and values when callers or stored data depend on them.

## Resolve conflicting evidence

For a disagreement, locate the relevant source branch, test assertion, documented claim, and any applicable decision. Establish version and configuration differences before deciding that the claims conflict. A test can preserve accidental behavior; documentation can be stale; runtime observations cover only the executed conditions.

Use a temporary probe when inspection cannot distinguish plausible outcomes. Isolate it from project deliverables and existing user work. Do not mutate live data or settings merely to investigate behavior. Record the inputs, environment, observation, and remaining limits; do not equate an unrun test with a passing one.

Return the factual result separately from the proposed contract. Identify whether the remaining issue is missing evidence, unclear intent, an implementation defect, or an explicit compatibility choice. The coordinator resolves the decision with the user through `brainstorm`.

## Synthesize requirements and scenarios

For each cohesive behavior, retain enough evidence to trace a candidate requirement to source, test assertions, documentation, observations, or an explicit user decision. Cite repository paths and symbols at the inspected revision; include line locations where useful. Distinguish code inspection from execution and inference.

Derive scenarios from the behavior's preconditions, action, and observable outcome. Include the consequential boundaries discovered during tracing. Write expected results from the settled contract, independently of the code under test. A useful scenario rejects a plausible wrong implementation.

Check the investigation in both directions: every in-scope capability has a requirement or an explicit exclusion, and every proposed requirement has evidence or an explicit decision. Check cross-area invariants and contradictions. Record consequential unexamined conditions as limitations; do not turn unknown behavior into a guarantee or demand exhaustive path enumeration.

Keep the investigation map and candidate requirements in the conversation while brainstorming is active. Once writing is authorized and brainstorming has concluded, synthesize durable findings by topic in research. Preserve evidence and applicability limits; leave task progress, file-reading checklists, and routine validation logs out of those documents.
