# Templates

## Plan File Template

```markdown
---
name: [task-name]
status: planning
---

# [Task Name] Plan

## Goal

[One sentence: what does "done" look like?]

## Phases

- [ ] Phase 1: [Description]
- [ ] Phase 2: [Description]
- [ ] Phase 3: [Description]

## Decisions

- [Decision]: [Rationale]

## Errors

- [Error]: [Resolution]

## Status

**Phase:** 1
**Current:** [What I'm doing now]
**Updated:** [timestamp]
```

### Plan File Status Values

| Status        | Meaning                                       |
| ------------- | --------------------------------------------- |
| `planning`    | Initial design phase, phases being defined    |
| `in-progress` | Executing on the plan, phases being completed |
| `completed`   | All phases done, task finished                |

**Update frontmatter `status:` field as task progresses.**

## Notes File Template

```markdown
---
name: [task-name]
---

# [Topic] Notes

## Sources

### [Source Name]

- URL: [link]
- Key points:
  - [Finding]

## Findings

### [Category]

- [Finding]
```

## Output File Template

```markdown
---
name: [task-name]
---

# [Task Name] Output

[Final deliverable content]
```

## Subtask Plan Template

For complex phases requiring separate plans:

```markdown
---
name: [parent-task]---[subtask-name]
status: planning
---

# [Subtask Name] Plan

## Parent

[parent-task].plan.md (Phase N)

## Goal

[One sentence: what does "done" look like?]

## Phases

- [ ] Phase 1: [Description]
- [ ] Phase 2: [Description]
- [ ] Phase 3: [Description]

## Status

**Phase:** 1
**Current:** [What I'm doing now]
**Updated:** [timestamp]
```

## Naming Examples

| Task Type   | Task Name                              | Plan File                                      | Notes File                                      | Output File                     |
| ----------- | -------------------------------------- | ---------------------------------------------- | ----------------------------------------------- | ------------------------------- |
| New feature | `auth-feature`                         | `auth-feature.plan.md`                         | `auth-feature.notes.md`                         | `auth-feature.output.md`        |
| Bug fix     | `fix-login-timeout`                    | `fix-login-timeout.plan.md`                    | `fix-login-timeout.notes.md`                    | `fix-login-timeout.output.md`   |
| Refactor    | `refactor-api-client`                  | `refactor-api-client.plan.md`                  | `refactor-api-client.notes.md`                  | `refactor-api-client.output.md` |
| Research    | `research-caching`                     | `research-caching.plan.md`                     | `research-caching.notes.md`                     | `research-caching.output.md`    |
| **Subtask** | `dashboard-feature---data-aggregation` | `dashboard-feature---data-aggregation.plan.md` | `dashboard-feature---data-aggregation.notes.md` | N/A                             |

**All files for a task share the same `task:` value in frontmatter.**

**Subtask naming:** Use triple-hyphen `---` to separate parent from subtask name.
