# Example Patterns

Well-structured agent context file examples for reference.

## Example: Docs vs Rules Separation

A repository with shared standards, human docs, and agent rules:

```
repo/
├── docs/
│   ├── standards/                  # Shared (humans + agents)
│   │   ├── frontend/
│   │   │   ├── typescript.md
│   │   │   ├── react.md
│   │   │   └── tailwindcss.md
│   │   ├── backend/
│   │   │   ├── api.md
│   │   │   └── database.md
│   │   └── git.md
│   │
│   ├── 01-overview.md              # Human-only (numbered)
│   ├── 02-getting-started.md
│   ├── 03-architecture.md
│   └── 04-debugging.md
│
└── .claude/
    ├── rules/
    │   ├── _overview.md            # Agent-only
    │   └── workflow/
    │       └── testing.md
    └── settings.json
```

**In `docs/standards/frontend/react.md`** (shared):
```markdown
# React Patterns

## Component Structure

**Do:**
- One component per file
- Create folder: `ComponentName/`
- Required files: `index.tsx`, `styles.ts`, `types.ts`
- Use named exports, not default exports

**Don't:**
- Create components directly in `src/components/` root
- Mix multiple components in one file
- Use `any` for props

## Naming

| Element | Convention | Example |
|---------|------------|---------|
| Component | PascalCase | `UserProfile` |
| Props interface | `{Name}Props` | `UserProfileProps` |
| Styled component | `Styled` prefix | `StyledContainer` |

## Example

```tsx
// Good
export const UserCard = ({ user }: UserCardProps) => {
  return <StyledContainer>{user.name}</StyledContainer>;
};
```
```

**In `docs/03-architecture.md`** (human-only):
```markdown
# Architecture

## Why We Structure Things This Way

Our frontend architecture evolved from scaling challenges in 2023...

[Diagrams, history, context]

## Component Philosophy

We chose folder-per-component because:
1. Co-location simplifies refactoring
2. Clear boundaries for ownership
3. Simpler imports via barrel files

For specific patterns, see `docs/standards/frontend/react.md`.
```

**In `.claude/rules/_overview.md`** (agent-only):
```markdown
# Project Context

Enterprise guidance platform. TypeScript + React frontend, Firebase backend.

## Standards

Follow all patterns in `docs/standards/`:
- `docs/standards/frontend/` — React, TypeScript, Tailwind
- `docs/standards/backend/` — API and database patterns
- `docs/standards/git.md` — Commit and branching

## Agent-Specific Rules

- Run `pnpm lint && pnpm test` before marking complete
- Don't modify files in `src/generated/`
- Reference `src/components/Button/` as exemplar for new components
```

**Key principles:**
- `docs/standards/` = Single source for actionable do's/don'ts
- `docs/*.md` = Numbered, human-focused (rationale, diagrams, onboarding)
- `.claude/rules/` = Agent-focused (workflow, constraints, pointers to standards)

## Example: Modular CLAUDE.md

A lean root file that references modular rules:

```markdown
# Project Context

Brief 2-3 sentence project overview.

## Quick Reference

- **Stack:** TypeScript, React, Firebase, PostgreSQL
- **Package Manager:** pnpm
- **Test Command:** `pnpm test`

## Rules

Detailed rules organized by domain in `.claude/rules/`:

- **Frontend:** `frontend/react.md`, `frontend/typescript.md`, `frontend/tailwindcss.md`
- **Backend:** `backend/api.md`, `backend/database.md`, `backend/firebase-auth.md`
- **Workflow:** `workflow/git.md`, `workflow/testing.md`
```

## Example: Focused Rule File

`.claude/rules/frontend/typescript.md`:

```markdown
# Code Style

## TypeScript

Use strict mode. Prefer `type` for unions/intersections, `interface` for object shapes.

```typescript
// Prefer
type Status = 'pending' | 'active' | 'done';
interface User { id: string; name: string; }

// Avoid
type User = { id: string; name: string };
```

## Naming

| Element | Convention | Example |
|---------|------------|---------|
| Files | kebab-case | `user-service.ts` |
| Components | PascalCase | `UserCard.tsx` |
| Functions | camelCase | `getUserById` |
| Constants | SCREAMING_SNAKE | `MAX_RETRIES` |
| Booleans | is/has/should prefix | `isLoading`, `hasAccess` |

## Functions

Limit to 40 lines. Extract when:
- Logic is reused
- Nested callbacks exceed 2 levels
- Multiple unrelated operations in sequence
```

## Example: Domain-Specific Rule File

`.claude/rules/backend/firebase-auth.md`:

```markdown
# Firebase Authentication

## Multi-tenant SSO

Each workspace has isolated auth configuration. Workspace ID determines OIDC provider.

```typescript
// Correct: Workspace-scoped provider
const provider = getOIDCProvider(workspaceId);
await signInWithPopup(auth, provider);

// Wrong: Global provider
await signInWithPopup(auth, globalOktaProvider);
```

## User Provisioning

Users may lack company email. Use Global Platform ID as fallback identifier.

```typescript
const identifier = user.email || user.globalPlatformId;
if (!identifier) throw new Error('No valid identifier');
```

## Custom Claims

Set workspace access via custom claims, not database lookups per request.

```typescript
// In Cloud Function after SSO
await auth.setCustomUserClaims(uid, { 
  workspaces: ['ws_123', 'ws_456'],
  role: 'member'
});
```
```

## Example: Git Workflow Rules

`.claude/rules/workflow/git.md`:

```markdown
# Git Workflow

## Commits

Format: `type(scope): description`

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

```
feat(auth): add Okta SSO provider configuration
fix(api): handle null response in user lookup
refactor(db): extract connection pooling logic
```

Keep commits atomic. One logical change per commit.

## Branches

- `main` - Production, protected
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `release/*` - Release prep

## Pull Requests

Required before merge to `main`:
- Passing CI
- 1+ approval
- No unresolved threads
- Linear ticket linked
```

## Anti-Pattern Examples

### Before: Monolithic File

```markdown
# CLAUDE.md (400 lines)

## About
[50 lines of company history nobody needs]

## Code Style
[100 lines mixing TypeScript, React, CSS]

## Database
[80 lines of schema + query patterns]

## Testing
[70 lines]

## Deployment
[50 lines]

## Random Tips
[50 lines of accumulated tribal knowledge]
```

### After: Modular Structure

```
docs/
├── standards/                 # Shared (humans + agents)
│   ├── frontend/
│   │   ├── react.md
│   │   ├── typescript.md
│   │   └── tailwindcss.md
│   └── backend/
│       ├── database.md
│       └── api.md
├── 01-overview.md             # Human-only (numbered)
├── 02-getting-started.md
├── 03-architecture.md
└── 04-debugging.md

.claude/rules/
├── _overview.md               # Agent-only
└── workflow/
    ├── testing.md
    └── git.md
```

Benefits:
- `docs/standards/` = single source for actionable patterns
- Human docs numbered for reading order
- Agent rules focus on behavior, reference standards
- No duplication across layers
- Scales with project growth
