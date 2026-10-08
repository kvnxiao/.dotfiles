---
name: implement-spec-plan
description: Implement or resume a plan set under .plans/ that plan-from-spec wrote from an approved spec, task by task through implementer subagents, tracking progress in agent-only state and reviewing the result against the plan and spec. Use when asked to implement, continue, or resume a spec-derived plan; not for plans from host plan mode.
---

# Implement a spec plan

This skill executes an approved plan set from `plan-from-spec`. The session that runs it coordinates:

- It picks tasks and runs each inline or through an `implementer` subagent.
- It records progress in the state files.
- It is the only session that talks to the user.

A request to implement authorizes edits within the plan's scope; commits, pushes, and PRs need separate authorization.

## 1. Load the plan set

1. Find the plan set: a path the user names, or the only `.plans/*/README.md`.
   - If the user names a child plan, load its root and keep execution limited to that child.
   - If several sets exist and none was named, ask which.
   - If none exists, return `Needs plan`.
2. If the root plan is not `status: ready`, return `Needs plan`.
3. Print the progress and the next task from the repository root, resolving the root plan's `spec` path relative to the root plan:

   ```sh
   uv run "$HOME/.agents/skills/write-spec/scripts/check_spec.py" <path/to/SPEC.md> --plans .plans/<spec-slug> --status
   ```

   If the script cannot run, print its stderr and stop. If it reports errors in the spec or its area files, including an unapproved spec, return `Needs spec`. If it reports errors only in the plan files, including a missing or mismatched `spec-baseline`, return `Needs plan`. Never update the baseline here to bypass reconciliation.

4. Select the next task or pending review within the requested scope. A named child must still wait for its dependencies' tasks and reviews. When all its tasks are done but its review is pending, resume section 3 directly. Recheck a recorded blocker before retrying a blocked task; keep it blocked until the cause is resolved. Resume the first unfinished task, inspecting any partial edits before continuing.

## 2. Run the tasks

Run the tasks of one plan in order, one at a time; tasks in the same plan share files. For each task:

1. Set the task to `in-progress` and the plan's review to `pending` in its state file.
2. Run the task under [implementer.md](references/implementer.md). For a plan with a few small tasks, or a host without an `implementer` agent, follow that contract's steps inline. Otherwise, start an `implementer` with the plan path, task ID, spec path, the task's requirement IDs, and the `discovered` entries of this plan and the plans it is blocked by.
3. Append to `discovered` what a later task needs to know, and process the outcome before recording completion. Keep the task incomplete until it returns Done and passes coordinator validation:

   | Outcome                                                                                                | Action                                                                                                                                                                                                   |
   | ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | Done                                                                                                   | Run the coordinator validation in step 4.                                                                                                                                                                |
   | A routine choice within the spec that was not explicitly left open or deferred                         | Choose the recommended option, record it in the plan's Approach, and resume the same task.                                                                                                               |
   | A decision within the approved spec that was explicitly left open or deferred, or needs human judgment | Settle it through `brainstorm`. If the answer requires a spec change, set the task to `blocked`, record the decision, and return `Needs spec`. Otherwise record it in the plan and resume the same task. |
   | A change the spec does not settle                                                                      | Set the task to `blocked`, record the decision, and return `Needs spec`.                                                                                                                                 |
   | A fix outside the task but within the approved plan's scope                                            | Add a task with the next unused ID and `todo` state, tell the user, and resume the current task if it can finish independently. Otherwise return `Needs plan` to reorder the work.                       |
   | A fix outside the approved plan, or an answer that invalidates later tasks                             | Set the task to `blocked`, record the reason, and return `Needs plan`.                                                                                                                                   |
   | Blocked                                                                                                | Set the task to `blocked`, record the blocker in `discovered`, and return `Blocked`; later tasks in the plan depend on it.                                                                               |

4. After a Done outcome, run the task's validate command yourself. If it produces the expected result, set the task to `done` and continue. Otherwise, give the same task one more attempt with the failing output and process its outcome again. If validation still fails, set it to `blocked`, record the failure, and return `Blocked`.

Whether a task runs inline or through an `implementer`, the coordinator keeps the state file and the plans current; the implementer contract's boundaries bind subagents only.

Plans marked parallel-safe can run at the same time only in separate sessions the user starts, each implementing one plan.

## 3. Review the plan's result

After a plan's last task, complete the root plan's Definition of done, including one `review-changes mode=apply` on the files this plan's tasks changed. Name the plan and the spec as the governing artifacts. Keep `review: pending` until the checks and review fixes are complete. If interrupted or blocked, resume this phase before reporting the plan done or starting a dependent plan. Then set `review: done` and rerun the status check.

Continue with the next plan only when the user asked for more than one plan. Without authorization to commit each plan first, the next plan's review also covers this plan's changes in files both plans touch.

## Return

- `Done`: report the completed tasks, the validate results, the review outcome, and the next unblocked plan.
- `Needs plan`: the plan set is missing, not ready, or disagrees with the spec. Report the errors for `plan-from-spec`.
- `Needs spec`: the spec has check errors, or a task requires a change the spec does not settle. Report the error lines, or the requirement IDs and the proposed change, for `write-spec`.
- `Blocked`: report the blocker and the tasks it holds back.
