---
name: optimize
description: Find software optimization opportunities across implementation and architecture. Use for broad requests to make a system faster, reduce resource use or operating cost, or find wasted work.
---

# Optimize

Coordinate an optimization review of both implementation and architecture. Return prioritized findings and further investigations.

Read [the shared investigation contract](references/investigation.md) and [the coordination procedure](references/coordinate.md). Use both scopes unless the user narrows the request.

Select the relevant investigation guidance for each assignment:

- [Implementation](../optimize-implementation/references/investigation.md): algorithms, data access, computation, and resource use within existing system responsibilities.
- [Architecture](../optimize-architecture/references/investigation.md): alternatives to system responsibilities, boundaries, data ownership, and execution models.

Default mode uses inexpensive evidence. An explicit `deep` or `mode=deep` request permits more extensive investigation. Before running a deep-mode experiment, read [experimental validation](references/experiments.md).
