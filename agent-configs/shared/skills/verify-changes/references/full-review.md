# Full Verification Workflow

Keep one independent correctness reviewer for the full path. Add reviewers for concrete uncertainty
or specialized investigation, not diff size. For example, inspect an authorization change deeply
even when it changes one line; check a mechanical rename across all references without requiring a
separate design review.

The coordinator owns delegation. Give each reviewer a focused task with the repository, revisions,
file scope, intended behavior, applicable rules, constraints, and known uncertainties. Avoid copying
the full conversation or supplying the author's conclusions as evidence. Require reviewers to read
the actual diff and relevant code. When delegation is unavailable, perform the assigned checks
in-session and report the lack of an independent review.

## Select Review Effort

Honor an explicit caller choice. Otherwise use `reviewer` at `high` on both clients. Select effort
per assignment before spawning; full review and large diffs do not automatically require `xhigh`.
Use the coordinator's scope assessment and targeted inspection of uncertain contracts to choose; do
not perform a duplicate review just to route effort. Keep the same coverage and evidence standard at
either effort.

Use `reviewer-deep` at `xhigh` when deeper reasoning has a concrete expected benefit, for example:

- Several interacting state transitions or concurrency orderings make a failure difficult to trace.
- An authorization boundary or irreversible migration has a subtle invariant whose failure has
  serious consequences.
- Contracts across components support competing explanations that require a long chain of reasoning
  to distinguish from the available evidence.

Treat these as judgment criteria, not keyword triggers. A straightforward authorization edit can
remain at `high`; a small change with a difficult race can warrant `xhigh` immediately. Do not
select `xhigh` solely for missing logs, unavailable tests, or unclear requirements. Obtain the
missing evidence or report the verification gap.

Include the chosen effort and a short reason in the assignment. Use the client-specific profiles:

| Profile         | Codex         | Claude Code       | Effort  |
| --------------- | ------------- | ----------------- | ------- |
| `reviewer`      | `gpt-6-astra` | `claude-opus-5-5` | `high`  |
| `reviewer-deep` | `gpt-6-astra` | `claude-opus-5-5` | `xhigh` |

Select the named profile rather than asking a pinned agent to change effort in its prompt. If named
profiles are unavailable, use explicit model and effort arguments when the spawning tool supports
them, and supply the shared reviewer contract. Otherwise use the available read-only reviewer and
report that the requested configuration could not be enforced. Do not claim a model or effort was
verified from the reviewer's self-description.

Keep the effort choice fixed once the reviewer starts. Do not interrupt or replace a `high` reviewer
with `reviewer-deep`, or spawn an `xhigh` follow-up for the same assignment. Reuse the existing
reviewer at its selected effort for clarifications and corrections, preserving its context. Report
unresolved questions with the evidence needed to decide them. Additional specialists must cover
distinct concerns, not repeat an assignment at higher effort. Apply lessons from difficult reviews
to future upfront choices.

Treat this routing as provisional. When comparable reviews provide evidence, tune it using valid
defects found, false positives, unresolved questions, latency, and token usage where available. Do
not add comparison runs to every verification or claim an unmeasured quality or cost benefit.

## Review Pipeline

1. [ ] **Assign review coverage:** Select the effort profile above and assign `review-changes` for
       correctness, applicable repository rules, and a simplification assessment. Inspect relevant
       local `*-rules` skills and supply them to that reviewer. Assign each specialist a specific
       concern and tell the general reviewer which assessments are assigned elsewhere. Run
       independent reviews in parallel. Delegate focused work separately when:
   - Structural changes or competing designs warrant a reviewer assigned `simplify-changes`.
   - Specialized rules require investigation beyond the general review.
   - An unresolved contract or unexpected dependency requires additional expertise.
2. [ ] **Apply fixes:** Deduplicate findings by mechanism and location, keeping unresolved concerns
       distinct. Correctness governs over cleanup. Apply accepted fixes and inspect the corrections
       with their affected callers and contracts. Broaden review when a fix changes shared behavior
       or invalidates earlier evidence; do not restart unchanged review work.
3. [ ] **Assess and update documentation:** Use `update-docs` in the main session to search the
       documentation corpus and assess public behavior and documented internal design. Make small
       edits in-session; delegate substantial writing or investigation with the relevant search
       results. Report the assessment when no update is needed.
4. [ ] **Audit changed prose:** After documentation updates, use `audit-prose` on all added or
       modified prose in the resolved change set, including comments and follow-up edits. Keep
       modest audits in-session; delegate when writing is a substantial deliverable. Check that
       prose edits preserve meaning and stay within scope.
5. [ ] **Validate:** Run relevant formatting, linting, type-checking, and tests after the final
       edits. Choose checks that establish the changed contracts; broaden them for shared behavior
       or uncertain dependencies. Reuse passed results only while their inputs remain unchanged.

## Operational Constraints

- **Read-Only Reviewers:** Review subagents must not edit files, stage changes, mutate external
  services, spawn children, or invoke another verification workflow. Keep reviewed files unchanged
  until their reports return.
- **Tree Mutation Scope:** Only the coordinator, `update-docs` subagent, and `audit-prose` subagent
  may edit the working tree.
- **Boundaries:** Do not repair problems outside the scoped change set; list them for the user
  instead. Review delegated edits before continuing; finish documentation before auditing prose.
- **Reporting:** Keep findings compact and evidence-based. Report remaining issues, checks run, and
  verification gaps without repeating reviewer reports or adding empty sections. Do not claim
  measured token savings or equivalent defect detection without comparative results.
