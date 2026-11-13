# Architecture diagram rules

Apply these rules when authoring diagrams. The [research inventory](diagram-research.md) records the public examples examined on 2026-10-25; ordinary generation does not require browsing them again. These are this skill's conventions, informed by those examples, not a claim that Hello Interview enforces a universal notation.

## Composition and notation

- Place the request initiator at the left, ingress next, application work next, and state or external dependencies toward the right. For backend pipelines, start with the producer, queue, or scheduler. Keep the primary request or processing path left-to-right; return traffic, callbacks, and feedback loops may point back or vertically.
- Place the primary request path near the vertical middle of the full diagram family, with dependencies and workers above and below it. Reserve the final family bounds upfront and preserve those positions across steps; never recenter each snapshot from its visible nodes.
- Prefer independent straight, angled arrows between shape boundaries. Fan-out connections leave the source separately toward their targets; do not merge them into a right-angle trunk. Arrange nodes to avoid crossing unrelated shapes and keep labels near their own arrows.
- Use rectangles for clients, gateways, services, workers, and queues; use ellipses for databases, object stores, caches, indexes, and shared counters. Use diamonds for actual decisions with labeled outcomes. Do not add a decision just to vary shapes. Label external providers explicitly in rectangles.
- Mark every horizontally scaled node with `replicated: true`. Draw three copies of the selected shape with rear layers offset above-left behind one label. Round rectangular corners; preserve ellipse and diamond geometry for that replica group or cluster, for both rectangles and ellipses. The layers indicate multiple instances, not an exact count or a replication guarantee. Explain replicas versus shards and their authority separately. Use opaque white fills on every layer and draw back-to-front so rear strokes and arrows cannot bleed through. Keep single-instance nodes unstacked.
- Draw API Gateway as a tall, narrow rounded rectangle centered on the primary request path. Keep other service boxes wider than they are tall.
- Use pointed directional arrows for calls, writes, publications, and deliveries. Use two arrowheads only for a genuinely bidirectional interaction; do not use them to conceal distinct operations. Label important edges with operation or payload fragments. Distinguish asynchronous paths with dashed lines and name their transport.
- Put up to two short responsibility bullets below a node label. Put schema fields, cache keys and values, partition keys, TTLs, and invariants in nearby floating bullet annotations. Keep annotations distinct from ephemeral slide Notes. Include only details needed to explain the design.
- Keep stable node IDs and positions as the architecture evolves. Reserve space for planned additions. Use a separate focused diagram when a composite becomes unreadable. Prefer horizontal layouts; allow zoom for detail without turning the overview into a long vertical page.
- Generate SVG outlines with bundled, pinned Rough.js and stable seeds. Keep text as selectable SVG text. Never generate diagram shapes in Python or fetch drawing dependencies at page runtime.

## Ingress decision

Choose ingress from the workload and deployment. Classify a reservation API consumed by web/mobile clients as client-facing even when the interview asks only for its backend. State the choice and rationale in Notes.

| Workload                                                                                    | Required treatment                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| External API backend with multiple application services or replicated application instances | Show the ingress appropriate to the workload, such as a load balancer, reverse proxy, or API gateway. Explain routing, health checks, and traffic distribution; add authentication or rate limiting where required. Label the selected component by its actual role or product. |
| Monolithic application                                                                      | Show the application entry point; add a load balancer or gateway only when its responsibility is needed. When the public backend scales to multiple instances, explain how traffic reaches healthy instances. A worker does not by itself make the design microservices.        |
| Backend pipeline or internal infrastructure                                                 | Show its actual queue, stream, scheduler, or internal RPC entry point. Do not add a gateway without an external API requirement.                                                                                                                                                |
| Persistent connections                                                                      | Show connection-aware ingress, such as an L4 load balancer for WebSockets. Explain any separate HTTP API gateway path.                                                                                                                                                          |
| Large objects                                                                               | Separate the authorization/metadata API from direct signed object-storage transfers and CDN delivery. The data path can bypass the gateway.                                                                                                                                     |

Combine gateway and load-balancing responsibilities in one node only when the selected deployment does so. Replication needs traffic distribution, but an API gateway is not a universal technical prerequisite for replication. In particular, replicating only internal consumers does not create an external API.

Select HTTP, gRPC, or asynchronous messaging for internal communication from the operation's needs. Do not infer gRPC or a service mesh merely because services communicate internally. Add a mesh only for a concrete operational requirement.

## Conditional scaling patterns

Select only patterns motivated by requirements and the current baseline's limitations. Name concrete technologies and modes using [technology selection](technology-selection.md).

| Trigger                          | Diagram additions and explanation                                                                                                                       |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read-heavy hot data              | Cache or materialized read model; key, freshness/invalidation policy, miss path, authoritative store.                                                   |
| Search or discovery              | Dedicated search index; update path such as CDC; indexing lag and behavior when the index is stale.                                                     |
| Bursty or expensive work         | Queue or log and independently scalable workers; acknowledgment, retry, deduplication, backlog and failure handling.                                    |
| Continuous aggregation           | Partitioned log, stream processor, serving store; partition key, window, late events, replay and repair where relevant.                                 |
| High fan-out or live delivery    | Fan-out workers or routing/pub-sub; connection ownership, delivery/reconnect behavior, durable history if required.                                     |
| Large files or video             | Object storage, direct transfers, CDN; metadata authority and asynchronous processing/completion state.                                                 |
| Contended scarce inventory       | Authoritative transaction or conditional write; explicit hold/expiry/confirmation transitions. A Redis box or lock alone does not prove no overselling. |
| State capacity or hot partitions | Concrete shard key and routing/replication choice; hot-key handling and cross-partition operations. Replica stacks alone do not establish consistency.  |

Do not prescribe Redis, Kafka, microservices, a gateway, or a service mesh for every scaled system. Explain why each selected addition solves this question's bottleneck and which guarantee it weakens or complicates.

State whether a network-accessed cache is a single instance, replicated deployment, or sharded cluster. An arrow denotes communication, not replication or sharding. Use stacked shapes only when the selected deployment has multiple instances.
