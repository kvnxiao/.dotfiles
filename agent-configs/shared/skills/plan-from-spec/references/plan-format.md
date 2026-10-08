# Plan format

A plan set turns an approved spec into work that implementer sessions execute one task at a time. Humans review the plan files; agents track progress in state files that nobody else reads. Plans tie to the spec more strictly than host plan-mode plans: every task cites the requirements it serves, and a reviewer checks the plans and the resulting code against the spec.

## Layout

```text
.plans/<spec-slug>/
  README.md              root plan
  <slice>.md             one child plan per vertical slice
  .state/<slice>.yaml    agent-only progress for that child plan
```

Name the directory with a kebab-case slug of the spec's subject. Do not create, edit, or recommend a `.gitignore` entry for `.plans/`; whether plans are tracked is the user's choice. Keep each plan file under 40 KB, write each paragraph and list item on one line, and leave out a step or section that has nothing to say.

## Root plan

```yaml
---
spec: ../../SPEC.md
status: draft # or ready
spec-baseline: sha256:<digest> # copy the checker's --fingerprint output
out-of-scope: [REQ-legacy-import] # requirements no plan covers
---
```

Record `spec-baseline` only after reconciling the plan with the approved spec. The checker fingerprints the root spec and every declared area file, normalizing line endings. Any text change requires reconciliation; a wording-only change can preserve all tasks and review results. A missing or mismatched baseline prevents a ready plan from running. Never refresh it merely to clear a checker error.

The root plan has these sections:

- **Outcome and scope:** the observable result when every plan is done, the requirement IDs in scope, and the reason for each `out-of-scope` requirement.
- **Shared decisions:** what every child plan builds on, fixed before any of them runs: interfaces between slices, module boundaries, and persisted formats the spec leaves open. Give each mechanism the requirement that forces it and the simpler mechanism that fails that requirement. Write a multi-step lifecycle as a state table.
- **Coverage:** a `Requirement | Owner | Contributors` table. Exactly one plan owns each requirement's full check; contributors implement parts of it. Leave invariants out: every task reads them, and review checks them.
- **Plans:** a `Plan | Outcome | Blocked by | Parallel-safe` table in execution order, with each plan linked. `check_spec.py --status` picks the next task or pending plan review in this order. Dependencies remain blocked until the prerequisite's tasks and review are done.
- **Definition of done:** the checks every plan meets, stated once: formatter, linter, tests, and `review-changes`.

## Child plan

```yaml
---
spec: ../../SPEC.md
parent: README.md
requirements: [REQ-export-overwrite, REQ-session-restore]
blocked-by: [storage.md]
---
```

A child plan has:

- **Outcome:** the behavior a user observes after this plan merges, the requirements it contributes to, and the obligations it leaves to other plans.
- **Approach:** the files and symbols it changes, the interfaces it consumes and produces, and existing behavior it reuses. Label proposed files and interfaces as new. For an edit that repeats across files, describe the pattern once and list representative paths.
- **Tasks:** one block per task, in prerequisite order.

For example, a task in a TypeScript repository:

```markdown
### T1 - Refuse to overwrite an existing export

**Requirements:** REQ-export-overwrite

1. Locate: `src/export/writer.ts` (`writeExport`), `tests/export.test.ts`.
2. Failing check: add a test that exports to an existing file without `--force` and expects exit status 3 with the file unchanged.
3. Change: check for the target before opening it, and return status 3 unless `force` is set.
4. Validate: run `pnpm test tests/export.test.ts` in the repository root; every test passes.
```

- Give tasks IDs `T1`, `T2`, … that stay fixed; a new task takes the next unused number, and no task is renumbered.
- Cite requirement IDs; never copy requirement text or the implementer contract's mandatory reading steps into each task.
- Give each validate step its working directory, the repository's command, and the expected result.
- Leave out the failing check when the task has no natural one, such as wiring or configuration.
- Write an investigation task as the question, a bounded experiment, and a validate step that states the result that unblocks the dependent tasks. Those tasks stay blocked until it completes.

## Dividing the work

- **Plan:** one vertical slice that ships as one PR and changes behavior a user can observe. Never make a plan for a single layer, except a walking skeleton or enabling slice that names the behavior it unblocks.
- **Split a plan** when it:
  - has more than one independently mergeable behavior.
  - has a grab-bag name.
  - mixes investigation with routine work.

  Prefer the split that lets a piece be dropped.
- **Task:** a contiguous set of edits that one implementer session finishes, with one observable acceptance check. A candidate without its own check becomes a step in another task.
- **Unknowns:** an API or runtime behavior the plan cannot confirm becomes an investigation task, not a finer split.
- **Integration:** give the work that joins slices, such as wiring, migration, or end-to-end checks, its own task. It is the work most often left out.
- **Order:** investigations first, then the walking skeleton and the riskiest core, then variations, then the rest. Order by prerequisites, never by requirement ID.
- **Parallel-safe:** mark a plan parallel-safe only when no plan that can run at the same time edits the same files, and every interface the plan consumes is fixed in Shared decisions.

## State file

```yaml
tasks:
  T1: done
  T2: in-progress
  T3: todo
review: pending
discovered:
  - "T2: the lock file must exist before T3 reads it"
```

A task is `todo`, `in-progress`, `blocked`, or `done`. `review` is `pending` or `done`; a missing value means `pending`. A plan is complete only when every task and its review are done.

`plan-from-spec` creates state files, adds new tasks as `todo`, removes deleted task entries, and resets review to `pending` for affected plans. `implement-spec-plan` records task execution, review completion, and `discovered`. Before changing a plan's implementation, reset its review to `pending`. Record `review: done` only after the plan's Definition of done and final review pass.

Record in `discovered` only what a later task needs to know, including an investigation's answer. A discovery that changes behavior goes to the spec, and one that changes the plan goes to the plan.

## Amending a plan set

Before amending a plan set, return the root to `status: draft`. Compare the current spec and implementation with the plan's obligations, including completed tasks. Revise only affected plans and coverage; preserve valid completed work and add tasks for new or changed obligations. Reset review to `pending` for affected plans and dependents whose acceptance is invalidated. A task marked done does not establish a changed requirement.

After reconciliation, record the current spec fingerprint. Present changed plans for approval before returning the root to `status: ready`. When only wording changed and the approved plan still applies, record that conclusion and retain its approval, tasks, and review results. For a plan without a baseline, establish conformance before recording one.
