# Full review workflow

## Assign review coverage

Assign one reviewer both [correctness-review.md](correctness-review.md) and [simplify-review.md](simplify-review.md), or only simplification for a cleanup request. When the scope has only a spec, its area files, and its research, assign [spec-review.md](spec-review.md) alone; when it has them alongside other changes, also assign spec-review.md to that reviewer. When the scope includes a plan set under `.plans/`, pass `~/.agents/skills/plan-from-spec/references/plan-format.md` as a rule file. Add a specialist only for a distinct contract or repository rule requiring separate investigation; name that concern and the reviewer assigned to it. Run independent assignments in parallel when available.

Pass the resolved assignment from [SKILL.md](../SKILL.md#resolve-the-assignment), the selected profile, and the assigned contract paths. Include intended behavior and known uncertainties without copying the conversation or presenting the author's conclusions as evidence. Require inspection of the actual artifacts.

Use `reviewer` by default. Use `reviewer-deep` upfront only when the caller explicitly requests it. Select named profiles; model IDs and effort settings belong in the client definitions. If a named profile is unavailable, read its definition and use explicit model/effort arguments when supported, with [review-execution.md](review-execution.md) as the contract. Otherwise use an available read-only reviewer and report the configuration limitation. If delegation is unavailable, review in-session and report the lack of independent review. Stop retrying an unavailable configuration after its fallback fails.

Keep each running review at its selected effort. After reports return, allow at most one focused `reviewer-deep` follow-up per workflow for unresolved correctness concerns that:

- Are marked reasoning-limited and have the needed evidence available.
- Have a concrete potential P0 or P1 consequence.
- Have not already been reviewed at the deep profile.

Pass the first reviewer's evidence and competing explanations; require an independent conclusion. Do not escalate a concern that is blocked on a missing requirement, test, log, or runtime observation. Reuse existing reviewers for ordinary clarifications. Report remaining uncertainty when a follow-up is unavailable or does not resolve it.

## Reconcile and apply

Wait for assigned reviews before changing reviewed files. Deduplicate findings by mechanism and location, keeping unresolved concerns separate from confirmed findings. Verify each finding against the target and applicable contracts; a reviewer's verdict alone does not establish acceptance.

In report mode, return verified findings without edits. In apply mode:

- Apply confirmed correctness corrections within the authorized scope.
- Apply confirmed simplifications only within the scoped files, with equivalent behavior, unchanged public interfaces, and settled design decisions.
- Do not apply unresolved or refuted items. Record every confirmed item skipped and its reason.

Correctness takes precedence over cleanup. Inspect fixes in-session with affected callers and contracts. Reassess changed behavior and invalidate stale evidence, including for edits to prompts or instructions. Do not repeat review of unchanged work or spawn another reviewer for routine fixes. If a correction requires an unsettled product or compatibility decision, report it and obtain that decision before applying the dependent change.

## Documentation and prose

Use `update-docs` with the selected mode to assess documented public behavior and internal design. Search the relevant documentation corpus; report the assessment even when no update is needed. Skip this assessment only for cleanup-only work that preserves documented behavior and design, and state that reason.

Use `audit-prose` with the selected mode on added or modified prose and requested prose-cleanup targets; for a reader-facing deliverable, as `audit-prose` defines it, it audits the whole artifact. A cleanup request does not skip this step when prose is in scope. In snapshot reviews, audit the selected prose. Skip only when no prose is in scope. Finish documentation before auditing prose; preserve meaning. After a prose correction to a prompt or instruction, recheck that it still directs the same behavior.

The coordinator applies edits. If documentation or prose investigation is delegated, require `mode=report` and apply accepted corrections in-session. Before delegating a prose audit that needs a cold-reader pass, run that pass in-session and pass its flags to the delegate.

## Validate and finish

Run relevant formatting, linting, type-checking, and tests after the final edits. Follow the mode's side-effect boundary in [SKILL.md](../SKILL.md). Reuse passed checks only while their inputs remain unchanged. For suggestion-only cleanup, run a check only when needed to establish a proposal.

For a failure, establish its cause before changing code. Classify it as pre-existing only when a baseline run or other evidence establishes that; a failure on a line the change did not touch does not prove the failure is pre-existing. Fix in-scope causes in apply mode and rerun affected checks. Do not repeat an unchanged failing command without new evidence. After two attempts with no new evidence or progress, stop that retry loop, report the blocker and failing command, and continue independent work. Report mode records the failure without repairing it.

Check that every assigned assessment returned or has a recorded limitation. Use the completion format in [SKILL.md](../SKILL.md); include remaining issues and verification gaps without repeating the reviewer reports.
