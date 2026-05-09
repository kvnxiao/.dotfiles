---
name: linear-search
description: Search Linear issues and projects by text. Use when finding issues, looking up bugs, searching the backlog, querying "what tickets mention X", or finding issues by keyword like "find ENG-" or "search for login bug".
allowed-tools: Bash
---

# Linear Search

Search Linear.app issues and projects using `linear-cli`.

## Search Issues

```bash
# Search issues by text
linear-cli s issues "authentication bug"

# Limit results
linear-cli s issues "login" --limit 5

# Get JSON output
linear-cli s issues "error" --output ndjson
```

## Search Projects

```bash
# Search projects
linear-cli s projects "backend"

# Limit results
linear-cli s projects "api" --limit 10
```

## After Searching

For detailed issue operations (get details, add comments, update status), use the `linear-issues` skill.

## Tips

- Search is case-insensitive
- Searches issue titles and descriptions
- Use `--output ndjson` for programmatic access
