# Correctness review

Review for defects introduced or exposed by the selected changes. Every correctness finding must
identify a concrete input, state, or ordering that produces incorrect behavior; cite the conflicting
instruction and artifact for a repository-rule violation.

Follow [review-execution.md](review-execution.md) for scope, read-only execution, and reporting.

## Investigation

Read every in-scope hunk, including tests and configuration, and open enclosing functions and
relevant contracts. Scale investigation depth to the behavior and risk of the change, without quotas
for findings.

- **Changed behavior:** Check boundary values, invalid inputs, error paths, resource lifetimes,
  state transitions, and ordering. Follow language-specific semantics and supported platforms rather
  than assuming a generic pitfall applies.
- **Removed behavior:** For deleted or replaced guards, validation, cleanup, and tests, identify the
  protected invariant and locate its replacement. Confirm whether the intended change removes that
  requirement before reporting a defect.
- **Callers and callees:** Trace changed preconditions, return values, exceptions, and side effects
  through relevant call sites. For wrappers and adapters, check delegation targets and the methods
  callers use.
- **Tests and contracts:** Check whether changed tests still exercise the intended behavior. Tie a
  missing regression test to a concrete failure mode; do not report generic requests for more
  coverage. For a rule violation, cite the applicable rule and the conflicting code.
- **Repository rules:** Apply the repository instructions and relevant rule skills supplied by the
  coordinator. Report gaps that require specialized investigation rather than assuming compliance.

Read unchanged code to establish reachability and existing guards. Separate pre-existing defects
from change-induced findings; a touched function alone does not put all of its old defects in scope.
Leave simplification to [simplify-review.md](simplify-review.md), and specialized rule checks to the
reviewers assigned them, without excluding correctness defects in the same code from your review.

## Verify and report

Deduplicate candidates by defect and mechanism. Before keeping each candidate, trace its trigger
through the actual code and check for guards, type constraints, and intentional behavior that
disprove it.

- **Confirmed:** The code establishes a reachable trigger and incorrect result. State whether
  evidence comes from inspection or an observed execution.
- **Unresolved:** A credible mechanism depends on an unverified environment, configuration, or
  runtime condition. State the missing evidence and the check needed to resolve it; keep these
  concerns separate from confirmed findings.
- **Refuted:** A guard, invariant, or intended contract disproves the candidate. Exclude it from
  findings.

Use this severity scale, independently of the verdict:

- **P0:** Immediate action required for widespread outage, data loss, or security exposure under
  normal operation.
- **P1:** High-impact failure of a supported path; correct before merge.
- **P2:** Bounded functional or performance regression; correct in normal work.
- **P3:** Minor impact or maintenance cost; low-priority correction or cleanup.

Return confirmed findings ranked by severity, separate unresolved concerns, and verification limits.
Use a compact paragraph or bullet per finding with its location, severity, concrete trigger or rule
violation, evidence, and suggested correction. Distinguish inspection from observed execution. For
unresolved concerns, state the missing evidence and required check; do not imply a confirmed defect.
