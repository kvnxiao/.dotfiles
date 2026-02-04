# Linear Fix Workflow

## Contents

1. [Gather Context](#step-1-gather-context) - Fetch ticket details, download attachments, prepare visual baselines (if `[visual-test]` marker present)
2. [Create Git Worktree](#step-2-create-git-worktree) - Isolated workspace for implementation
3. [Autonomous Planning](#step-3-autonomous-planning) - Generate implementation approaches
4. [Autonomous Plan Review](#step-4-autonomous-plan-review) - Architect approval loop, extract variables
5. [Implement and Review](#step-5-implement-and-review) - Code implementation and review loop
6. [Commit, Push, and Create PR](#step-6-commit-push-and-create-pr) - PR with planning reasoning

---

## Step 1: Gather Context

Extract ticket ID and fetch details:

```bash
TICKET_ID=$(./scripts/extract-linear-issue-id.sh "<user-input>")
TICKET_JSON=$(linear-cli i get "$TICKET_ID" --output json)
TICKET_COMMENTS=$(linear-cli cm list "$TICKET_ID" --output json)
```

**Always use `--output json`** for all Linear CLI commands.

Extract from TICKET_JSON: `TITLE`, `DESCRIPTION`, `STATE`, `PRIORITY`, `TICKET_URL` (the `url` field)

**IMPORTANT**: Check BOTH `TICKET_JSON` (issue description) AND `TICKET_COMMENTS` for uploaded files/attachments. If any uploads exist (images, screenshots, files), ALWAYS download them via `/linear-uploads` skill for additional context before planning.

**Visual Testing Baseline Preparation (opt-in):**

Visual testing is **off by default**. Only set up baselines if explicitly requested.

Enable visual testing if ANY of these are true:

1. **User prompt**: User includes `--visual`, `with visual testing`, or similar in their request
2. **Ticket label**: `visual-test` label on the ticket (check `TICKET_JSON.labels`)
3. **Ticket description**: `[visual-test]` marker in `DESCRIPTION`
4. **Ticket comment**: `[visual-test]` marker in any `TICKET_COMMENTS`

If none found, skip this section.

If visual testing enabled:

1. Set `HAS_VISUAL_BASELINE=true`
2. Create baselines directory:
   ```bash
   mkdir -p .visual-testing/baselines
   ```
3. Build `VISUAL_BASELINES` list from design assets in ticket:
   - **Figma URLs**: store URL directly
   - **Uploaded images**: copy to `.visual-testing/baselines/<ticket-id>-<index>.png`

Example structure:
```
VISUAL_BASELINES:
  - name: homepage
    baseline: .visual-testing/baselines/ENG-123-1.png
    url: http://localhost:3000/
  - name: settings-mobile
    baseline: https://figma.com/file/abc123
    url: http://localhost:3000/settings
    viewport: 375x812
```

Infer URL and viewport from image filename/context when possible.

## Step 2: Create Git Worktree

Use the `/git-worktree` skill to create an isolated worktree. First generate branch name from ticket URL:

```bash
OS_USER=$(whoami)
BRANCH_SUFFIX=$(echo "$TICKET_URL" | sed -n 's|.*/issue/||p' | tr '[:upper:]' '[:lower:]')
BRANCH_NAME="${OS_USER}/${BRANCH_SUFFIX}"
```

Pass `BRANCH_NAME` to the `/git-worktree` skill. The skill outputs `WORKTREE_PATH` and `DEFAULT_BRANCH`. After creation, cd into `$WORKTREE_PATH` and install dependencies.

## Step 3: Autonomous Planning

Use Task tool with `subagent_type=Plan`.

Read `./planner-prompt.md` for prompt template. Substitute `$TICKET_ID`, `$TICKET_JSON`, `$TICKET_COMMENTS`.

## Step 4: Autonomous Plan Review

Use Task tool with `subagent_type=feature-dev:code-architect`.

Read `./reviewer-prompt.md` for prompt template. Substitute `$TICKET_ID`, `$TICKET_JSON`, `$PLANNER_OUTPUT`.

**Multi-Round Loop:**

- `## Review Decision: REVISION REQUESTED` → pass feedback back to planner (Step 3)
- `## Review Decision: APPROVED` → proceed to implementation
- Max 3 iterations; after 3, reviewer MUST select best available with caveats

**Extract from approved review:**

- `SELECTED_APPROACH` ← value after "## Selected Approach"
- `REVIEW_REASONING` ← content under "## Reasoning"
- `TRADEOFFS_ACCEPTED` ← content under "## Additional Considerations"
- `EDGE_CASES` ← edge cases mentioned in plan
- `ITERATION_COUNT` ← number of planning rounds completed

## Step 5: Implement and Review

### 5a: Implement

Implement approved plan. Validate (tests, lint, build) pass before review.

### 5b: Code Review and Visual Validation

Run code review and visual validation **in parallel** when design assets exist.

**Code Review** (always runs):

Use Task tool with `subagent_type=feature-dev:code-reviewer`.

Read `./code-reviewer-prompt.md` for prompt template. Substitute `$TICKET_ID`, `$TICKET_JSON`, `$SELECTED_APPROACH`.

**Visual Validation** (conditional):

If `HAS_VISUAL_BASELINE=true` (set in Step 1), invoke visual validator agent with all baselines.

Agent handles script generation, capture, and comparison for each test case:

```yaml
Use Task tool with:
  subagent_type: squint:playwright-visual-validator
  prompt: |
    Capture and validate visual consistency for multiple screens:

    Auth: <if-needed>
    Context: Implementing $TICKET_ID - $TITLE

    Test 1:
      URL: <url-from-VISUAL_BASELINES>
      Baseline: <baseline-from-VISUAL_BASELINES>
      Viewport: <viewport-or-default-1920x1080>
      Name: <name-from-VISUAL_BASELINES>

    Test 2:
      ...
```

**Parallel Execution:**

Spawn BOTH agents in the same Task tool message:

- `subagent_type=feature-dev:code-reviewer`
- `subagent_type=squint:playwright-visual-validator` (if enabled)

**Review Loop:**

- Code review: `## Code Review: CHANGES REQUESTED` → fix issues (5a) and re-review
- Visual validation: Overall verdict `FAIL` or `WARNING` → address differences, re-capture, re-validate
- Both must pass: Code review `APPROVED` AND visual validation `PASS` (or `WARNING` with documented justification)
- Max 2 iterations; then proceed with documented caveats

**IMPORTANT**: Do NOT proceed to Step 6 until code review is APPROVED (or max iterations reached with caveats documented).

## Step 6: Commit, Push, and Create PR

### 6a: Commit and Push

1. Determine `COMMIT_TYPE`: `fix` (bug), `feat` (feature), `chore`, `refactor`, `docs`, `test`
2. Run `../scripts/commit-and-push.sh`

### 6b: Prepare PR Body

Check for PR template and fill it out:

1. Look for `.github/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE.md`
2. **If template exists**: Read it and fill each section with ticket details and implementation info
3. **If no template**: Create body with: Overview (link to Linear ticket), Description, Changes summary

**IMPORTANT**: ALWAYS APPEND collapsible planning section to PR body:

```markdown
<details>
<summary>🤖 Autonomous Planning Reasoning</summary>

### Selected Approach
$SELECTED_APPROACH

### Why This Approach
$REVIEW_REASONING

### Trade-offs Accepted
$TRADEOFFS_ACCEPTED

### Edge Cases Handled
$EDGE_CASES

### Planning Iterations
$ITERATION_COUNT iteration(s) before approval

</details>
```

### 6c: Create PR

Run `../scripts/create-github-pr.sh` with env vars:

- Required: `TICKET_ID`, `TITLE`, `BRANCH_NAME`, `DEFAULT_BRANCH`, `PR_BODY`
- Optional: `COMMIT_TYPE` (default: fix), `TICKET_URL`, `WORKTREE_PATH`
