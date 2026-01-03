---
name: planning-with-persistent-files
description: >
  Manages multi-phase tasks using persistent markdown files as cross-session memory.
  Syncs plan state to TodoWrite for UI visibility.
  Triggers: 3+ phase tasks, research, multi-session work, refactors, or keywords like
  "plan", "track progress", "resume", "continue", "break this down", "organize".
---

# Planning with Persistent Files

Uses persistent markdown files as cross-session memory and source of truth. Syncs with the TodoWrite tool for UI visibility.

## When to Use

**Use this pattern for:**

- Multi-step tasks (3+ phases)
- Research tasks
- Work spanning multiple sessions
- Tasks needing error history
- Large migrations or refactors

**Skip for:**

- Simple questions
- Single-file edits
- Quick lookups

## Architecture

```
[task].plan.md (filesystem) ←── SOURCE OF TRUTH
            ↓
         TodoWrite ←── UI mirror (session-only)
```

| Layer   | Tool             | Persistence | Purpose              |
| ------- | ---------------- | ----------- | -------------------- |
| Storage | `[task].plan.md` | Disk        | Cross-session memory |
| UI      | TodoWrite        | Session     | User visibility      |

**Rule:** Update plan file FIRST, then sync TodoWrite.

## File Naming and Frontmatter

Use descriptive names—never generic `[task].plan.md`:

| Task Type | Filename                      | Task Name (frontmatter) |
| --------- | ----------------------------- | ----------------------- |
| Feature   | `auth-feature.plan.md`        | `auth-feature`          |
| Bug fix   | `fix-login-timeout.plan.md`   | `fix-login-timeout`     |
| Refactor  | `refactor-api-client.plan.md` | `refactor-api-client`   |
| Research  | `research-caching.plan.md`    | `research-caching`      |

**Example:** `auth-feature.plan.md`
**Pattern:** `[action]-[subject].plan.md`

### Subtask Naming

For complex phases requiring their own plan, use triple-hyphen separator:

| Type    | Pattern                      | Example                                        |
| ------- | ---------------------------- | ---------------------------------------------- |
| Parent  | `[task].plan.md`             | `dashboard-feature.plan.md`                    |
| Subtask | `[task]---[subtask].plan.md` | `dashboard-feature---data-aggregation.plan.md` |

**When to create a subtask plan:**

- Subtask has 3+ phases of its own
- Subtask could be reused independently
- Parent plan would exceed 10 phases without nesting

**Otherwise:** Expand parent plan phases instead of creating subtasks.

### Frontmatter Requirements

All persistent markdown files **must** include YAML frontmatter:

**Plan files (`*.plan.md`):**

```yaml
---
name: [task-name]
status: planning | in-progress | completed
---
```

**Notes and output files:**

```yaml
---
name: [task-name]
---
```

**Status lifecycle for plan files:**

- `planning` → Initial design, defining phases
- `in-progress` → Executing plan, completing phases
- `completed` → All phases done

**Subtask plans** include a `Parent` section referencing the parent plan:

```markdown
## Parent

dashboard-feature.plan.md (Phase 2)
```

Update `status:` field when transitioning between stages.

## **CRITICAL**: Sync Loop

Every iteration: Read plan → Sync TodoWrite → Work → Write plan → Update TodoWrite.

See [examples.md](examples.md) for detailed sync patterns including initialization, phase completion, and context recovery.

## Quick Start

1. Create `[task].plan.md` with goal and phases
2. Call TodoWrite to mirror phases in UI
3. Read plan before each decision
4. Update plan file first, then TodoWrite
5. Log errors in plan file

## Resuming Tasks

On session start or context reset:

1. `Glob "*.plan.md"` → find existing plans
2. Read plan file → get current state
3. **Rebuild TodoWrite from plan phases**
4. Continue from Status section

## Verification

After each sync iteration:

1. **Confirm plan file updated**: `head -20 [task].plan.md` to verify phases/status
2. **Confirm TodoWrite reflects state**: Visual check that UI matches plan
3. **If mismatch detected**: Re-read plan file and rebuild TodoWrite from scratch

## The 3-File Pattern

For complex tasks, use three files working together:

| File               | Purpose                         | Update When      | Sync?                 |
| ------------------ | ------------------------------- | ---------------- | --------------------- |
| `[task].plan.md`   | Track phases, decisions, errors | After each phase | ✅ Yes (to TodoWrite) |
| `[task].notes.md`  | Store research/findings         | During research  | ❌ No                 |
| `[task].output.md` | Final output/deliverable        | At completion    | ❌ No                 |

**Only `[task].plan.md` syncs to TodoWrite.** Notes and output files are referenced in the plan but don't need UI representation.

**Workflow:**

1. Read `[task].plan.md` → know current phase
2. If research phase → write findings to `[task].notes.md`
3. Update `[task].plan.md` → phase complete, reference notes
4. Sync TodoWrite → UI reflects progress
5. If final phase → create `[task].output.md` with deliverable
6. Update `[task].plan.md` → task complete

## Critical Rules

1. **Plan file is source of truth** — TodoWrite is just UI
2. **Read before decide** — every loop, refresh goals
3. **Write plan first** — then sync TodoWrite
4. **Log all errors** — builds knowledge for recovery
5. **Sync on resume** — rebuild TodoWrite from plan

## Edge Cases

| Situation                                | Action                                                          |
| ---------------------------------------- | --------------------------------------------------------------- |
| Multiple `*.plan.md` found               | Ask user which task to resume or list all                       |
| Plan file corrupted/unreadable           | Recreate from scratch, log incident in new plan                 |
| TodoWrite fails to sync                  | Continue with plan file only, warn user UI may be stale         |
| User manually edited plan during session | Re-read plan file before next action to pick up changes         |
| Overlapping plan files for similar work  | Clarify scope with user, potentially merge or archive old plans |

## Anti-Patterns

| Don't                              | Do Instead                         |
| ---------------------------------- | ---------------------------------- |
| Trust TodoWrite as source of truth | Read plan file, sync TodoWrite     |
| Update TodoWrite without plan file | Write plan file first              |
| Skip sync on resume                | Always rebuild TodoWrite from plan |
| Use generic `plan.md` filename     | Use descriptive `[task].plan.md`   |
| State goals once and forget        | Re-read plan every loop            |

## References

- [templates.md](templates.md) — Plan and notes file templates
- [examples.md](examples.md) — Workflow examples including sync patterns
- [reference.md](reference.md) — Manus context engineering principles
