# Investigate implementation efficiency

Start from the required operation and workload established under the shared contract. Reconsider algorithms and data representation within existing system responsibilities; the current algorithm and code structure are not requirements. Classify a proposal by the decisions it changes rather than the size of its diff.

Investigate relevant causes of cost:

- **Unnecessary or repeated work:** repeated scans, parsing, serialization, queries, conversions, or computation. Determine execution frequency and whether results remain reusable.
- **Algorithms and data structures:** growth with input size, repeated lookup cost, redundant passes, and representation choices. Compare realistic inputs; asymptotic complexity alone does not determine the useful improvement.
- **Data movement and access:** transferred data volume, round trips, copying, locality, query shape, and unused results. Trace effects on the whole operation.
- **Memory and resource lifetime:** allocation frequency, retained state, peak memory, buffers, and delayed release. Account for both transient and sustained costs.
- **Waiting and contention:** dependency order, locks, blocking operations, queueing, and downstream limits. Establish what can proceed independently before proposing concurrency.

Check conditions of proposed mechanisms rather than applying a fixed catalogue:

- For caching, establish reuse, complete key inputs, freshness or invalidation, memory bounds, and concurrent-miss behavior.
- For batching, compare amortized overhead with added waiting, memory, failure handling, and required ordering.
- For concurrency or larger pools, check independent work, downstream capacity, bounded queues, cancellation, and synchronization costs.
- For precomputation or indexing, account for construction, updates, storage, and recovery.

Consider eliminating work or reducing its frequency before increasing machinery, while retaining alternatives that fit the actual constraints. Startup and infrequent operations can matter when their cost affects the required outcome.

Report a specific replacement and its conditions. Mark alternatives that require different component responsibilities or data ownership as architectural opportunities for the coordinator or a later focused investigation. Do not invoke another skill to pursue them automatically.
