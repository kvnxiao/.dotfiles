---
name: implement-spec-plan
description: Implement or resume a plan set under .plans/ that plan-from-spec wrote from an approved spec, plan by plan through one implementer subagent per plan, tracking progress in agent-only state and reviewing each plan's result against the plan and spec. Use when asked to implement, continue, or resume a spec-derived plan; not for plans from host plan mode.
---

# Implement a spec plan

Before writing or delegating work, restore any brainstorm state from the conversation or continuation summary and follow [Brainstorming boundary and conclusion](../brainstorm/SKILL.md#brainstorming-boundary-and-conclusion). This rule also applies if brainstorming starts during this workflow.

This skill executes an approved plan set from `plan-from-spec`. The session that runs it coordinates:

- It picks the next plan and runs its tasks inline or through one `implementer` subagent.
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

4. Select the next plan with an unfinished task or a pending review within the requested scope. A named child must still wait for its dependencies' tasks and reviews. When all its tasks are done but its review is pending, resume section 3 directly. Recheck a recorded blocker before retrying a blocked task; keep it blocked until the cause is resolved. Resume at the plan's first unfinished task, inspecting any partial edits before continuing.

## 2. Run the plan's tasks

Complete the implementation and acceptance checks assigned by the plan. Missing features and failing checks against clear requirements are work to implement or fix; they do not by themselves invalidate spec approval. Use the outcome rules below to distinguish changes within the approved contract from decisions that require a spec amendment.

Run one plan at a time, and give all of its unfinished tasks to one implementer, which runs them in order. Tasks in the same plan share files and context, so a new implementer for each task would reread the same instructions, plan, spec, and code.

1. Select the plan's unfinished tasks that come before the first task whose recorded blocker is unresolved; the tasks after a blocked task depend on it. If no task is selected, return `Blocked`. Otherwise, set the selected tasks to `in-progress` and the plan's review to `pending` in its [state file](../plan-from-spec/references/plan-format.md#state-file).
2. Run the selected tasks under [implementer.md](references/implementer.md). For a plan with a few small tasks, or a host without an `implementer` agent, follow that contract's steps inline. Otherwise, start one `implementer` with the plan path, the selected task IDs in order, the spec path, and the `discovered` entries of this plan and the plans it is blocked by.
3. When the implementer returns, append to `discovered` what a later task needs to know. Then process each task's outcome in order with the table below, and keep a task incomplete until it returns Done and passes coordinator validation. The implementer stops at the first task it cannot finish:

   - To resume the stopped task, continue the same implementer with the answer when the host supports it, so it keeps its context. Otherwise, start a new implementer with the remaining tasks and the updated `discovered` entries.
   - When an outcome returns from this workflow, leave the outcomes after it unprocessed. Set each later task that the implementer reports as not started back to `todo`, and keep each other later task `in-progress`.

   | Outcome                                                                                                | Action                                                                                                                                                                                                                                                                         |
   | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
   | Done                                                                                                   | Validate it with the other Done tasks in step 4.                                                                                                                                                                                                                               |
   | A routine choice within the spec that was not explicitly left open or deferred                         | Choose the recommended option, record it in the plan's Approach, and resume the same task.                                                                                                                                                                                     |
   | A decision within the approved spec that was explicitly left open or deferred, or needs human judgment | Settle it through `brainstorm`. Defer plan and state writes until that session concludes. If the confirmed decision requires a spec change, set the task to `blocked`, record the decision, and return `Needs spec`. Otherwise record it in the plan and resume the same task. |
   | A change the spec does not settle                                                                      | Set the task to `blocked`, record the decision, and return `Needs spec`.                                                                                                                                                                                                       |
   | A fix outside the task but within the approved plan's scope                                            | Add a task with the next unused ID and `todo` state, tell the user, and resume the current task if it can finish independently. Otherwise return `Needs plan` to reorder the work.                                                                                             |
   | A fix outside the approved plan, or an answer that invalidates later tasks                             | Set the task to `blocked`, record the reason, and return `Needs plan`.                                                                                                                                                                                                         |
   | Blocked                                                                                                | Set the task to `blocked`, record the blocker in `discovered`, and return `Blocked`; later tasks in the plan depend on it.                                                                                                                                                     |

4. Validate when the implementer has finished every assigned task, and before returning from this workflow:

   - Run each Done task's validate command yourself, in task order; run a command that several tasks share once. When a command produces each task's expected result, set those tasks to `done`.
   - When a command fails, give the earliest failing task a single retry with the failing output, through the same implementer when possible. Then rerun the validation of that task and the tasks after it. If that task's validation fails again, set it to `blocked`, record the failure, and return `Blocked`.
   - When a stopped task's partial edits break an earlier task's validation, keep the earlier task `in-progress` and validate it after the stopped task finishes.

5. While the plan has unfinished tasks, repeat from step 1 with them.

If the implementer stops without an outcome for an assigned task, for example because it ran out of context or was interrupted, inspect the partial edits and start a new implementer with the remaining tasks, or continue the same one when it still has its context.

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
