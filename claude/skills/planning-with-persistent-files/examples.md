# Examples

## Example 1: Sync Loop in Action

**Task:** Implement auth feature (3 phases)

### Loop 1: Initialize

```
Write auth-feature.plan.md:
  ---
  task: auth-feature
  status: planning
  ---

  # Auth Feature Plan
  ## Goal
  Add JWT-based authentication to the API.
  ## Phases
  - [ ] Phase 1: Design auth flow
  - [ ] Phase 2: Implement JWT
  - [ ] Phase 3: Add tests
  ## Status
  **Phase:** 1
  **Current:** Designing auth flow

TodoWrite:
  - [in_progress] Design auth flow
  - [pending] Implement JWT
  - [pending] Add tests
```

### Loop 2: Complete Phase 1

```
Read auth-feature.plan.md     # Refresh goals
# Do design work...

Edit auth-feature.plan.md:    # UPDATE SOURCE FIRST
  ---
  status: in-progress         # CHANGED from planning
  ---

  - [x] Phase 1: Design auth flow
  - [ ] Phase 2: Implement JWT
  ## Status
  **Phase:** 2
  **Current:** Implementing JWT handler

TodoWrite:                    # THEN SYNC UI
  - [completed] Design auth flow
  - [in_progress] Implement JWT
  - [pending] Add tests
```

### Loop 3: Context Reset Recovery

```
# New session, context lost

Glob "*.plan.md"              # Find: auth-feature.plan.md
Read auth-feature.plan.md     # Phase 1 done, Phase 2 in progress

TodoWrite:                    # REBUILD FROM PLAN
  - [completed] Design auth flow
  - [in_progress] Implement JWT
  - [pending] Add tests

# Continue Phase 2...
```

---

## Example 2: Research Task

**Task:** Research caching strategies and write summary

### Initialize

```
Write research-caching.plan.md:
  ---
  task: research-caching
  status: planning
  ---

  # Caching Research Plan
  ## Goal
  Create summary of caching strategies for our API.
  ## Phases
  - [ ] Phase 1: Gather sources
  - [ ] Phase 2: Synthesize findings
  - [ ] Phase 3: Write summary
  ## Status
  **Phase:** 1

TodoWrite:
  - [in_progress] Gather sources
  - [pending] Synthesize findings
  - [pending] Write summary
```

### Research Loop

```
Read research-caching.plan.md   # Refresh goals
WebSearch "API caching strategies 2025"

Write research-caching.notes.md:
  ---
  task: research-caching
  ---

  # Caching Research Notes
  ## Sources
  ### Redis Documentation
  - URL: https://redis.io/docs
  - Key points:
    - In-memory store
    - TTL-based expiration

Edit research-caching.plan.md:
  ---
  status: in-progress           # CHANGED from planning
  ---

  - [x] Phase 1: Gather sources
  ## Status: **Phase:** 2

TodoWrite:
  - [completed] Gather sources
  - [in_progress] Synthesize findings
  - [pending] Write summary
```

---

## Example 3: Bug Fix with Error Logging

**Task:** Fix login timeout bug

### Initialize

```
Write fix-login-timeout.plan.md:
  ---
  task: fix-login-timeout
  status: planning
  ---

  # Fix Login Timeout Plan
  ## Goal
  Resolve timeout errors on login endpoint.
  ## Phases
  - [ ] Phase 1: Reproduce and diagnose
  - [ ] Phase 2: Implement fix
  - [ ] Phase 3: Verify fix
  ## Errors
  (none yet)
  ## Status
  **Phase:** 1
```

### Error Encountered

```
Read fix-login-timeout.plan.md
# Attempt fix...
# Error: Database connection pool exhausted

Edit fix-login-timeout.plan.md:
  ## Errors
  - Connection pool exhausted → Need to increase pool size
  ## Status
  **Phase:** 2
  **Current:** Increasing connection pool size
```

---

## Example 4: Nested Tasks

**Task:** Feature with complex subtask

### Parent Plan

```
Write dashboard-feature.plan.md:
  ---
  task: dashboard-feature
  status: in-progress
  ---

  # Dashboard Feature Plan
  ## Goal
  Add analytics dashboard to admin panel.
  ## Phases
  - [ ] Phase 1: Design dashboard layout
  - [ ] Phase 2: Implement data aggregation (complex—see subtask)
  - [ ] Phase 3: Build UI components
  ## Status
  **Phase:** 2
  **Subtask:** dashboard-feature---data-aggregation.plan.md
```

### Subtask Plan

```
Write dashboard-feature---data-aggregation.plan.md:  # NOTE: Triple-hyphen separator
  ---
  task: dashboard-feature---data-aggregation
  status: planning
  ---

  # Data Aggregation Plan
  ## Goal
  Build efficient data aggregation for dashboard metrics.
  ## Parent
  dashboard-feature.plan.md (Phase 2)
  ## Phases
  - [ ] Phase 1: Design query strategy
  - [ ] Phase 2: Implement aggregation
  - [ ] Phase 3: Optimize performance
  ## Status
  **Phase:** 1
```

### Subtask Completion

```
# After completing subtask...

Edit dashboard-feature---data-aggregation.plan.md:
  ---
  status: completed               # CHANGED from in-progress
  ---

  - [x] Phase 3: Optimize performance
  ## Status: Complete

Edit dashboard-feature.plan.md:
  - [x] Phase 2: Implement data aggregation
  ## Status
  **Phase:** 3
  **Current:** Building UI components
```

---

## Key Patterns

| Pattern                         | When to Use          |
| ------------------------------- | -------------------- |
| Read → Work → Write → Sync      | Every loop iteration |
| Glob → Read → Rebuild TodoWrite | Session resume       |
| Log error → Continue            | Error recovery       |
| Parent + Subtask plans          | Complex nested work  |

---

## Evaluation Scenarios

### Scenario 1: Fresh Task

**Input:** "Help me implement a caching layer for the API"

**Expected behavior:**

1. Creates `caching-layer.plan.md` with goal and phases
2. Calls TodoWrite to mirror phases in UI
3. Begins Phase 1 work
4. Updates plan file after each phase completion
5. Syncs TodoWrite after each plan update

**Success criteria:**

- Plan file exists and is properly structured
- TodoWrite reflects current phase status
- Phase checkboxes update as work progresses

### Scenario 2: Resume Existing Task

**Input:** "Continue where I left off" or "What was I working on?"

**Expected behavior:**

1. Runs `Glob "*.plan.md"` to find existing plans
2. If multiple found, lists them and asks which to resume
3. Reads selected plan file to get current state
4. Rebuilds TodoWrite from plan phases (completed, in_progress, pending)
5. Resumes work from Status section's current phase

**Success criteria:**

- Finds existing plan file(s) correctly
- Rebuilds TodoWrite to match plan state exactly
- Continues from correct phase without repeating completed work

### Scenario 3: Error Handling

**Input:** Task encounters error (e.g., API timeout, file not found)

**Expected behavior:**

1. Logs error in plan file's Errors section with resolution strategy
2. Attempts recovery based on error type
3. Updates Status section with current recovery action
4. Continues work after resolution
5. Does not lose track of original goal despite error

**Success criteria:**

- Error logged in plan file with context
- Recovery action documented
- Work continues without abandoning task
- Error history preserved for learning

### Scenario 4: Complex Multi-Session Research

**Input:** "Research authentication strategies and write a summary"

**Expected behavior:**

1. Creates `research-auth.plan.md` with research phases
2. Creates `research-auth.notes.md` for findings as research progresses
3. Updates plan file after each research phase
4. At completion, creates `research-auth.output.md` with final summary
5. Handles session breaks by resuming from plan file

**Success criteria:**

- All three files created (plan, notes, output)
- Notes file contains structured findings from sources
- Plan file tracks research phases
- Output file contains synthesized summary
- Can resume research across multiple sessions

### Scenario 5: Nested Complex Task

**Input:** "Build a dashboard feature with data aggregation, caching, and UI components"

**Expected behavior:**

1. Creates parent `dashboard-feature.plan.md` with high-level phases
2. When hitting complex subtask (data aggregation), creates `dashboard-feature---data-aggregation.plan.md`
3. Links subtask plan to parent plan using `## Parent` section
4. Completes subtask plan fully before returning to parent
5. Updates parent plan when subtask completes
6. Both TodoWrite and plan files stay synchronized

**Success criteria:**

- Subtask filename uses triple-hyphen separator: `[parent]---[subtask].plan.md`
- Parent plan references subtask plan with full filename
- Subtask plan includes `## Parent` section referencing parent
- Subtask `task:` frontmatter includes full name with triple-hyphen
- Subtask completion updates parent plan
- TodoWrite reflects nested structure appropriately
- No loss of context when switching between parent and subtask
