# Reference: Manus Context Engineering Principles

Based on Manus's context engineering documentation.

## The 6 Principles

### 1. Filesystem as External Memory

**Problem:** Context windows have limits.

**Solution:** Store large content in files, keep only paths in context.

### 2. Attention Manipulation Through Repetition

**Problem:** After ~50 tool calls, models forget original goals ("lost in the middle").

**Solution:** Re-read plan file before each decision. Recent reads get attention.

```
Start of context: [Original goal - forgotten]
...many tool calls...
End of context: [Recently read plan file - gets ATTENTION!]
```

### 3. Keep Failure Traces

**Problem:** Hiding errors wastes tokens and loses learning.

**Solution:** Log errors in plan file:

```markdown
## Errors

- FileNotFoundError: config.json → Created default config
- API timeout → Retried with backoff, succeeded
```

### 4. Avoid Few-Shot Overfitting

**Problem:** Repetitive patterns cause drift.

**Solution:** Vary phrasings slightly, don't copy-paste blindly.

### 5. Stable Prefixes for Cache Optimization

**Problem:** Agents are input-heavy (100:1 ratio).

**Solution:** Put static content first, use append-only context.

### 6. Append-Only Context

**Problem:** Modifying previous messages invalidates KV-cache.

**Solution:** Never modify previous messages. Always append.

## File Operations

| Operation | When                        |
| --------- | --------------------------- |
| `write`   | New files                   |
| `append`  | Adding sections             |
| `edit`    | Updating checkboxes, status |
| `read`    | Before decisions            |
