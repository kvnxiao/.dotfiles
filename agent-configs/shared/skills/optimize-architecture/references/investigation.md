# Investigate architectural efficiency

Derive candidate approaches from the business result, workload, and requirements before treating the existing architecture as necessary. Identify which boundaries and responsibilities are required and which are implementation choices.

Explore relevant alternatives to:

- Where and when computation happens, including incremental computation and reusable derived state.
- Data ownership, representation, movement, and access paths.
- Component boundaries and coordination, including consolidation as well as decomposition.
- Execution and communication models, scheduling, and placement.

Follow the implications of materially different candidates. Compare the required result under representative conditions, such as bursts, skewed data, slow dependencies, and recovery. Select conditions that could distinguish the approaches rather than requiring every category in every review.

Explain the mechanism behind each proposed benefit. Track work removed, duplicated, or transferred between reads, writes, background processing, and recovery. Check whether reducing one cost exposes another limit.

Preserve functional and non-functional requirements, including relevant consistency, freshness, ordering, security, availability, and resource budgets. Flag an alternative that requires relaxing a requirement as incompatible with the current contract. Do not silently trade correctness or reliability for speed.

Compare each promising alternative with improvements to the current design. Include migration effort, temporary duplication during transition, operational cost, reversibility, and evidence that could reverse the recommendation. Prefer a design because it fits the workload rather than because it follows an architectural pattern.

Include current and credibly anticipated workloads. Explain the conditions under which an alternative becomes worthwhile and the evidence for anticipated demand. Avoid speculative scale requirements.

Return concrete alternatives and their trade-offs, with implementation dependencies and high-value validation questions. In default mode, propose experiments as further work. In deep mode, validate only uncertainties that could change the recommendation; an unavailable full-system environment does not justify an unrelated experiment.
