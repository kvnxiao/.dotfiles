---
name: docs-review
description: Review and improve repository documentation including both human-readable docs (`docs/`), `README.md`, and AI agent memory context files (`CLAUDE.md`, `.claude/rules/*`, `AGENTS.md`, `.cursorrules`, etc.) for clarity, minimal duplication, and modularity. Use when asked to review, audit, refactor, or improve documentation structure, consolidate rules, reduce redundancy, establish shared standards, or modularize monolithic instruction files.
---

# Documentation Review Skill

Review and improve repository documentation for both human-readable docs and AI agent context files to ensure clarity, minimal duplication, and modularity.

## Target Files

### Human Documentation
- `docs/*.md` — Numbered human-readable docs (`01-overview.md`, etc.)
- `docs/standards/` — Shared actionable patterns (humans + agents)
- `README.md` — Project introduction

### Agent Context Files
- `CLAUDE.md` — Claude Code project context
- `.claude/rules/*.md` — Modular Claude rules
- `AGENTS.md` — Multi-agent context (Cursor, etc.)
- `.cursor/rules/*.md` or `.cursorrules` — Cursor-specific rules
- `.github/copilot-instructions.md` — GitHub Copilot context

## Docs vs Rules Separation

Many repositories have both human-readable documentation (`docs/`) and agent context files (`.claude/rules/`). Avoid duplication by establishing clear boundaries.

### Recommended Structure

```
repo/
├── docs/
│   ├── standards/                  # Shared source of truth (humans + agents)
│   │   ├── frontend/
│   │   │   ├── typescript.md
│   │   │   ├── react.md
│   │   │   └── styling.md
│   │   │   └── state.md
│   │   ├── backend/
│   │   │   ├── api.md
│   │   │   └── database.md
│   │   └── git.md
│   │
│   ├── 01-overview.md              # Human-only (numbered for reading order)
│   ├── 02-getting-started.md
│   ├── 03-architecture.md
│   └── 04-debugging.md
│
├── CLAUDE.md                      # Project context (root-level)
└── .claude/
    ├── rules/                      # Agent-only (behavioral)
    │   └── workflow/
    │       ├── testing.md
    │       └── pr-process.md
    └── settings.json
```

### Content Boundaries

| Location | Purpose | Audience | Content Type |
|----------|---------|----------|--------------|
| `docs/standards/` | Actionable patterns | Both | Do's/don'ts, code examples |
| `docs/*.md` | Onboarding, context | Humans | Explanatory, diagrams, rationale |
| `.claude/rules/` | Agent behavior | Agents | Workflow, constraints, pointers |

### Naming Conventions

**Human docs:** Numbered prefix, zero-padded for sort order
- `01-overview.md`, `02-getting-started.md`, ... `12-advanced-topics.md`

**Standards:** No prefix, organized by domain subfolder
- `docs/standards/frontend/react.md`, `docs/standards/backend/api.md`

**Agent context:** Root-level CLAUDE.md for project overview
- `CLAUDE.md` at repository root provides project context

**General rules:**
- Folders: lowercase, single word when possible (`frontend/`, `backend/`)
- Files: kebab-case, descriptive (`typescript-patterns.md` not `ts.md`)
- Avoid generic names: `firebase-auth.md` not `auth.md`

### How Each Layer References Standards

**In `docs/03-architecture.md` (human doc):**
```markdown
# Architecture

[Diagrams, rationale, history]

For specific coding patterns, see `docs/standards/`.
```

**In `CLAUDE.md` (project context at repo root):**
```markdown
# Project Context

Brief project summary.

## Before You Start

**CRITICAL**: Before making any changes or answering questions about this project, **ALWAYS consult the `docs/` folder first** as it is the source of truth for architectural decisions, conventions, patterns, standards, and project specific workflows

## Standards

Follow all patterns in `docs/standards/`:
- `docs/standards/frontend/` — example: React, TypeScript, Tailwind
- `docs/standards/backend/` — example: API and database patterns
- `docs/standards/git.md` — example: Commit and branching

## Before Marking Complete

- Run linter and test commands and apply any necessary fixes to ensure they pass.
```

### Avoid Auto-Importing Docs

Do not use `@` imports to pull docs into rules:

```markdown
<!-- Avoid: Auto-imports entire doc, bloats context -->
See @docs/standards/frontend/react.md for details.

<!-- Prefer: Explicit reference, agent reads if needed -->
For React patterns, consult `docs/standards/frontend/react.md`.
```

**Why:**
- Hidden dependencies are hard to audit
- Full doc imported even when only a section is relevant
- Doc changes may unintentionally affect agent behavior

## Review Workflow

### 1. Discovery

Scan the repository for all documentation and agent context files:

```bash
# Find human docs
ls -la README.md 2>/dev/null
ls -la docs/ 2>/dev/null
ls -la docs/standards/ 2>/dev/null

# Find agent context files
find . -type f \( \
  -name "CLAUDE.md" -o \
  -name "AGENTS.md" -o \
  -name ".cursorrules" -o \
  -name "copilot-instructions.md" -o \
  -name "*.mdc" \
\) 2>/dev/null

# Check for rules directories
ls -la .claude/rules/ 2>/dev/null
ls -la .cursor/rules/ 2>/dev/null
```

### 2. Analysis

For each file, evaluate against these criteria:

| Criterion | Check |
|-----------|-------|
| **Clarity** | Instructions are unambiguous and actionable |
| **Scope** | Each file/section has a single, clear purpose |
| **Audience** | Content matches intended audience (human vs agent vs shared) |
| **Duplication** | No repeated content across files |
| **Three-layer separation** | Standards, human docs, and agent rules clearly separated |
| **Modularity** | Related content grouped; unrelated content separated |
| **Naming** | Human docs numbered in-order; standards by domain; CLAUDE.md at root |
| **Discoverability** | File/section names reflect content |
| **Maintainability** | Easy to update without side effects |
| **No auto-imports** | Rules reference docs explicitly, not via `@` |

### 3. Report Format

Generate findings using this structure:

```markdown
## Documentation Review Report

### Files Analyzed
- [list of files with line counts]

### Issues Found

#### Critical (Blocks Agent Effectiveness)
- Issue description → Recommended fix

#### Moderate (Reduces Clarity)
- Issue description → Recommended fix

#### Minor (Optimization Opportunity)
- Issue description → Recommended fix

### Recommendations
1. Prioritized action items
```

## Common Anti-Patterns

### Duplication

**Problem:** Same instruction appears in multiple files.
```
# In CLAUDE.md
Use TypeScript strict mode for all files.

# In .claude/rules/typescript.md  
Always enable TypeScript strict mode.
```

**Solution:** Single source of truth, reference from other locations if needed.

### Monolithic Files

**Problem:** Single file covers unrelated domains.
```
# CLAUDE.md (500+ lines)
## TypeScript Rules
## Database Conventions
## API Design
## Testing Strategy
## Git Workflow
## Deployment
```

**Solution:** Extract to `.claude/rules/` with domain subfolders:
```
.claude/rules/
├── frontend/
│   └── typescript.md
├── backend/
│   ├── database.md
│   └── api.md
└── workflow/
    ├── testing.md
    └── git.md
```

### Vague Instructions

**Problem:** Non-actionable guidance.
```
Write good code.
Follow best practices.
Keep things clean.
```

**Solution:** Specific, verifiable instructions.
```
Limit functions to 50 lines. Extract helpers for complex logic.
Name boolean variables with is/has/should prefix.
```

### Contradictions

**Problem:** Conflicting rules across files.
```
# In typescript.md
Prefer interfaces over types.

# In api.md
Use type aliases for API response shapes.
```

**Solution:** Resolve conflicts, document exceptions with rationale.

### Stale Context

**Problem:** Outdated instructions that no longer apply.
```
Use moment.js for date handling.  # Project now uses date-fns
```

**Solution:** Regular audits, tie instructions to current dependencies.

## Modularization Strategy

### When to Modularize

Modularize when CLAUDE.md exceeds ~200 lines or covers 3+ unrelated domains. See "Recommended Structure" above for the target organization.

**Flat structure** is acceptable for smaller projects (<10 rule files):
```
.claude/rules/
├── code-style.md
├── api.md
├── testing.md
└── git.md
```

### Cross-References

When rules in one file depend on another:
```markdown
<!-- In workflow/testing.md -->
Follow component naming from `frontend/react.md` for test files.
```

## Writing Effective Rules

### Rule Structure

```markdown
## [Category]: [Specific Topic]

[1-2 sentence context if needed]

**Do:**
- Specific actionable instruction
- Another instruction with example

**Don't:**
- Anti-pattern to avoid

**Example:**
[code block or concrete example]
```

### Characteristics of Good Rules

- **Atomic:** One concept per rule
- **Testable:** Can verify compliance
- **Contextual:** Explains "why" when non-obvious
- **Current:** Reflects actual project state

## Refactoring Checklist

When improving existing documentation:

### 1. Discovery
- [ ] Locate all docs (`docs/`, `README.md`) and agent context files (`CLAUDE.md`, `.claude/rules/`, etc.)
- [ ] Identify actionable patterns that belong in `docs/standards/`

### 2. Audit
- [ ] Map content overlap and flag contradictions
- [ ] Flag stale instructions and `@` imports

### 3. Restructure
- [ ] Modularize monolithic files (>200 lines or 3+ domains)
- [ ] Apply naming conventions (numbered human docs, domain-organized standards)
- [ ] Ensure three-layer separation (standards / human docs / agent rules)

### 4. Validate
- [ ] Check for orphaned references and broken links
- [ ] Verify CLAUDE.md includes pre-session requirements and post-session checks

### 5. Final Audit Pass
- [ ] Re-run analysis criteria from §2 against all changed files
- [ ] Confirm no new duplication, contradictions, or anti-patterns introduced
- [ ] Verify changes maintain clarity, scope, and discoverability

## Output

After review, provide:

1. **Summary:** Current state assessment (1-2 paragraphs)
2. **Issues:** Categorized list with severity
3. **Proposed Structure:** Directory tree if reorganizing
4. **Migration Plan:** Steps to implement changes safely
5. **Updated Files:** Refactored content (if requested)
