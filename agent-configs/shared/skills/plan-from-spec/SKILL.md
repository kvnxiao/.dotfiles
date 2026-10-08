---
name: plan-from-spec
description: Break an approved spec (SPEC.md and its area files) into a tree of implementation plans under .plans/, with tasks that cite requirement IDs, fixed shared interfaces, and acceptance checks. Use when planning the implementation of an approved spec or part of one; not for one-off plans without a spec, which host plan mode covers.
---

# Plan from a spec

This skill writes a plan set that implementer sessions can execute without the conversation: a root plan, one child plan per vertical slice, and agent-only state files. Approving a plan does not authorize implementing it; `implement-spec-plan` implements an approved plan set.

## 1. Establish the baseline

1. Find the spec, using the first that applies: a path the user names, a location in the repository's instructions, or `SPEC.md` at the repository root. Read the root and every area file the requested scope touches, including Explored alternatives.
2. Act on the spec's state:

   | State                                       | Action               |
   | ------------------------------------------- | -------------------- |
   | No spec, `status: draft`, or open questions | Return `Needs spec`. |
   | `status: approved`                          | Continue.            |

3. Read the research findings the planned behavior depends on. Recheck an `Observed in` finding against the installed version when the plan relies on it.

## 2. Inspect the repository

Inspect the source, tests, dependencies, and build setup the scope touches. Separate requirements the code already satisfies from those it lacks or satisfies in part; do not assume existing code conforms. A repository with only a spec is a valid starting point.

## 3. Map the scope

List the requirement IDs in scope, the ones already satisfied, and the ones out of scope with the reason. Never invent, rename, or retire a requirement; a change to a requirement goes through `write-spec`.

## 4. Settle the approach

Choose files, internal types, algorithms, libraries, and slice boundaries within the spec's permitted choices. Settle the interfaces between slices, module boundaries, and persisted formats the spec leaves open before dividing the work, and drop any mechanism that no requirement forces. Resolve each open question by its kind:

| Question                                                                                                                | Resolution                                                                             |
| ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| A routine implementation detail was not explicitly left open or deferred, and the spec permits the recommended approach | Choose it and record it in Shared decisions.                                           |
| An implementation decision was explicitly left open or deferred                                                         | Settle it with the user through `brainstorm`, even when the spec permits every option. |
| It needs a human's judgment, such as a trade-off between products or costs                                              | Settle it with the user through `brainstorm`.                                          |
| A user, an integrator, another component, or stored data would notice the answer, and the spec leaves it open           | Return `Needs spec` with the proposed change.                                          |
| An API or runtime behavior is unconfirmed                                                                               | Plan an investigation task and block the work that depends on it.                      |

## 5. Write the plan set

If the plan set already exists, amend it under the format's amendment rules instead of replanning from scratch.

1. Read [plan-format.md](references/plan-format.md), and divide the work and write the plans under it in `.plans/<spec-slug>/`. For a spec set, give each area its own slices.
2. Create a state file, with every task `todo` and `review: pending`, for each child plan that has none. Maintain existing state under the format's amendment rules.
3. After reconciling the plan's obligations with the approved spec, run the checker with `--fingerprint` and copy its `spec-baseline` field into the root plan:

   ```sh
   uv run "$HOME/.agents/skills/write-spec/scripts/check_spec.py" <path/to/SPEC.md> --fingerprint
   ```

   If the check fails, fix the errors before recording a baseline. Then check the plans against the spec from the repository root:

   ```sh
   uv run "$HOME/.agents/skills/write-spec/scripts/check_spec.py" <path/to/SPEC.md> --plans .plans/<spec-slug>
   ```

   If the script cannot run, print its stderr and stop. Otherwise, fix every error, and add each requirement the coverage warning names to a plan or to the root plan's `out-of-scope` list with the reason.
4. Run `review-changes mode=apply` on the plan files as a snapshot, naming the spec as the governing spec. Bring each finding that needs a decision to the user through `brainstorm`.
5. Present the plan set. When no question is open and the user approves it, set the root plan's `status: ready` and rerun the plan check. For wording-only reconciliation that preserves the approved plan, retain approval under the format's amendment rules. A missing or mismatched baseline requires reconciliation before implementation.

## Return

- `Done`: the plan set is saved. Report its path, the plan tree with blocked-by links, coverage gaps, the root status, and the first unblocked task.
- `Needs spec`: the spec is missing, unapproved, or needs a change. Report the requirement IDs and the proposed change.
- `Blocked`: a decision that changes acceptance is unanswered. Report it and the planning already done.
