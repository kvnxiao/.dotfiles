# Staff engineer delivery and evidence

Research date: 2026-10-25. Use this bundled synthesis during generation; do not reopen the source pages. It combines the user's live-interview constraints with the public level expectations in the 16 accessible breakdowns inventoried in [diagram research](diagram-research.md). Premium-gated designs were not inspected. This is generation guidance, not an official scoring rubric.

## Generate the live reasoning

Model a seasoned staff engineer constructing the answer at the whiteboard. Derive the design from workload, invariants, access patterns, and failure conditions. Use established technologies as known building blocks. Do not simulate discovering the answer through vendor API research. Reason from the problem's fundamentals without lecturing on familiar concepts.

Establish the central design tension during requirements. For example, fast hotel discovery and authoritative reservation have different freshness and failure contracts. Mark the hard questions early, establish a coherent baseline, then examine them deliberately. Let the prompt determine how soon the baseline appears; do not delay a supplied design review behind a generic requirements and API sequence.

Make a decision and justify it briefly. Select PostgreSQL for transactional inventory because the invariant needs atomic room-night claims; name the transaction boundary and contention risk. Do not leave the interviewer to choose from a catalog of databases.

Prioritize two or three consequential deep-dive threads as a planning default, not a quota. Adapt to scope and interviewer steering. For each chosen thread, explain the concrete mechanism, its principal failure case, and remaining or newly exposed bottlenecks, when relevant. Tie operating concerns to that path: for example, a retry queue needs bounded attempts, backlog visibility, and recovery ownership.

Use the existing deep-dive fields to show a limitation, chosen change, credible alternative, tradeoff, failure behavior, and diagram update. Add the condition that would change the decision to Notes. Do not add complexity merely to signal seniority; keep a single process or database when it meets the constraints.

Use first-person proposed decisions where natural in `lead`, such as “I would keep booking authoritative in PostgreSQL.” Do not invent incidents, employers, projects, or personal experience for the learner or the assistant. Express experience through concrete judgment and anticipated failures. Invite the learner to substitute a real example only in optional Notes.

## Cross-question patterns

The public breakdowns repeatedly distinguish senior candidates who complete the baseline efficiently and explain selected mechanisms from staff candidates who independently direct the discussion and explore consequences of their decisions. Exact depth counts vary by problem; do not enforce breadth/depth percentages or reproduce every sample deep dive.

| Public examples                                  | Recurring depth emphasis                                                                                 |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| Bitly; distributed rate limiter                  | Coordination, atomicity, hot state, failover, and operational consequences of a chosen scaling approach. |
| Dropbox; YouTube                                 | Large transfers, resumability, processing, and practical storage choices.                                |
| Ticketmaster; GoPuff                             | Inventory correctness alongside read throughput and contention.                                          |
| Facebook news feed; Tinder                       | Precomputation, fan-out or feed construction, freshness, and workload-sensitive alternatives.            |
| Facebook live comments; WhatsApp                 | Fan-out or message routing, recoverability, partition choices, and failures under load.                  |
| Facebook post search; Top K; ad click aggregator | Ingestion and query paths, aggregation or indexing choices, latency, and processing correctness.         |
| Uber; web crawler                                | Domain constraints such as matching contention or crawl politeness, followed by throughput and recovery. |
| LeetCode                                         | Execution isolation, concrete test-running behavior, latency, and a simple design with a growth path.    |

These are transferable discussion patterns, not mandatory infrastructure. A named technology is useful when its configuration or semantics explain the chosen mechanism; a box labeled Kafka or Redis alone does not demonstrate depth.

## Source interpretation

[Expectations at each level](https://www.hellointerview.com/blog/the-system-design-interview-what-is-expected-at-each-level) emphasizes increasing depth and proactive problem navigation. Senior candidates should explain concrete choices in selected areas. Staff candidates should anticipate limitations and direct the discussion with practical judgment.

[Staff-level interview guidance](https://www.hellointerview.com/blog/staff-level-system-design) emphasizes concise peer communication, early recognition of the hardest constraints, simple designs, transferable experience, and decisive recommendations. The rules above adapt those themes to a generated practice artifact; they do not authorize fabricated experience.

The per-question links and public-access boundaries are recorded in [the survey](diagram-research.md#public-evidence). The level sections were compared in addition to the diagrams. Their common pattern is constraint-driven depth, not one shared final architecture.
