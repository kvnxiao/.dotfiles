---
name: linear-issues
description: Manage Linear issues - list, create, update, start/stop work, assign, comment, set priority/labels. Use when working with Linear issues, viewing tasks, creating bugs, updating issue status, adding comments, or changing assignments.
allowed-tools: Bash
---

# Linear Issues

Manage Linear.app issues using the `linear-cli` command-line tool.

NOTE: **Always use `--output ndjson`** when querying data (e.g. listing, getting, viewing).

## List Issues

```bash
# List all issues
linear-cli i list --output ndjson

# Filter by team
linear-cli i list -t Engineering --output ndjson

# Filter by status
linear-cli i list -s "In Progress" --output ndjson
```

## View Issue Details

```bash
# View issue details
linear-cli i get LIN-123 --output ndjson

# Batch fetch multiple issues
linear-cli i get LIN-1 LIN-2 LIN-3 --output ndjson
```

## Create Issues

```bash
# Create issue (priority: 0=none, 1=urgent, 2=high, 3=normal, 4=low)
linear-cli i create "Bug: Login fails" -t Engineering -p 2

# Create with status
linear-cli i create "Feature request" -t ENG -s "Backlog"

# Create with labels (use label IDs, not names - look up IDs first)
linear-cli i create "Bug fix" -t ENG -l "uuid-1" -l "uuid-2"

# Preview without creating (dry run)
linear-cli i create "Test issue" -t ENG --dry-run

# Get just the created ID (for chaining)
linear-cli i create "Bug fix" -t ENG --id-only

# Read description from stdin
cat description.md | linear-cli i create "Title" -t ENG -d -
```

## Labels

**IMPORTANT**: Use label UUIDs, not names. Names cause validation errors.

```bash
# List issue labels (to find IDs) - default is project labels
linear-cli l list -t issue --output ndjson

# Filter labels by name pattern
linear-cli l list -t issue --filter "name~=Bug" --output ndjson

# Create with multiple labels (repeat -l flag)
linear-cli i create "Title" -t ENG -l "uuid-1" -l "uuid-2" -l "uuid-3"
```

## Update Issues

```bash
# Update status
linear-cli i update LIN-123 -s Done

# Update priority
linear-cli i update LIN-123 -p 1

# Get just the ID on success
linear-cli i update LIN-123 -s Done --id-only
```

## Start/Stop Work

**Note**: These commands do NOT support `--dry-run`.

```bash
# Start working (assigns to you, sets In Progress, creates git branch)
linear-cli i start LIN-123 --checkout

# Stop working (returns to backlog state)
linear-cli i stop LIN-123

# Stop and unassign
linear-cli i stop LIN-123 --unassign
```

## Comments

**Note**: `cm create` does NOT support `--dry-run`.

```bash
# List comments
linear-cli cm list LIN-123 --output ndjson

# Add comment (no dry-run available)
linear-cli cm create LIN-123 -b "Fixed in latest commit"
```

## Context Detection

```bash
# Get current issue from git branch name
linear-cli context --output ndjson
```

## Agent-Friendly Options

| Flag              | Purpose                            |
| ----------------- | ---------------------------------- |
| `--output ndjson` | One JSON object per line (queries) |
| `--quiet` / `-q`  | Suppress decorative output         |
| `--id-only`       | Only output created/updated ID     |
| `--dry-run`       | Preview (create/update only)       |

## Exit Codes

- `0` = Success
- `1` = General error
- `2` = Not found
- `3` = Auth error

## Tips

- **Always use `--output ndjson`** for queries (`list`, `get`, `context`)
- Short aliases: `i` for issues, `cm` for comments, `l` for labels, `ctx` for context
- Labels require UUIDs - look up with `linear-cli l list -t issue --output ndjson`
- Run `linear-cli <subcommand> --help` for all options
