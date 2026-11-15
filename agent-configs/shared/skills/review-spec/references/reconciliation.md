# Reconcile requirements with evidence

Use these rules when an amendment or reconstruction compares intended requirements with existing implementation. Apply the [spec format](spec-format.md) for requirement identity, scenarios, and approval. Use `brainstorm` for unsettled contract decisions; investigation establishes facts, while the user settles intent.

## Establish what the evidence supports

Distinguish the approved contract, documented claims, source inspection, runtime observations, and inferred intent. Pin repository evidence to a commit or release and identify relevant working changes. Record the configuration and conditions of runtime observations. A passing test supports its assertions under those conditions; it does not establish behavior outside them.

Use source, tests, documentation, and relevant decisions together. Trace a disagreement to its actual conditions before proposing a requirement change. Do not select a winner solely because one source is newer or executable. Identify which behavior runs; separately establish whether it is intended, a compatibility obligation, or a defect.

Keep evidence, discrepancies, and investigation limits in supporting research, with links from requirements where needed. Keep findings in the conversation during active brainstorming. Write the approved intended contract in the spec without narrating implementation gaps beside its rules.

## Decide the requirement change

| Finding                                                                              | Action                                                                                                       |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| Implementation satisfies the requirement, or chooses an explicitly permitted option  | Keep the requirement and its slug.                                                                           |
| Implementation violates a still-intended requirement                                 | Report the implementation defect; do not change the contract to excuse it.                                   |
| The user selects a changed contract, including an accepted implementation difference | Amend the affected requirement and scenarios; preserve its slug when the behavior identity remains the same. |
| An intended behavior has no requirement                                              | Propose a new requirement with observable scenarios.                                                         |
| A requirement is unimplemented but still wanted                                      | Preserve it. Missing implementation does not retire a requirement.                                           |
| The user abandons a requirement                                                      | Retire it and resolve its references under the format's identifier rules.                                    |
| Evidence conflicts or intent remains uncertain                                       | Investigate the factual gap, then ask the user for any remaining decision.                                   |

Obtain the user's decision on new and retired requirements and changed obligations. Cohesive groups can be decided together; individual approval of every identifier is unnecessary. Preserve settled decisions and reuse confirmation already obtained for the consolidated design.

For a code-first amendment, compare the relevant diff, tests, requirements, and compatibility obligations. For a proposed feature, inspect existing behavior where the new contract depends on it. The amount of investigation does not determine which skill applies: `write-spec` starts from a known change or contract question; `reconstruct-spec` discovers the contract of a system that is not yet sufficiently understood.

Do not infer business motives, reliability guarantees, or performance targets from implementation structure alone. Mark an inference and seek corroborating evidence. If it materially affects the contract and cannot be established, settle it with the user or explicitly defer it.
