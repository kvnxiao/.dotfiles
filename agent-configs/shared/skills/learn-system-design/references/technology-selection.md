# Select concrete technologies

Read this reference when selecting infrastructure for a solution. Use the bundled guidance during ordinary generation; research again only for a requested refresh or a selected infrastructure building block guarantee not covered here. Research date: 2026-10-25.

## Name the product and its relevant mode

Label infrastructure with its role and selected technology, such as `PostgreSQL inventory`, `Redis offer cache`, or `Kafka booking events`. Keep domain services logical, such as `Reservation app`. Select one defensible implementation per role; do not fill diagrams with competing product names.

State the feature or deployment mode when it changes the design. For example, distinguish `Redis Streams workers` from `Redis Pub/Sub updates`, and introduce `Redis Cluster cache` only when sharding is justified. Put longer configuration details in the accompanying explanation so labels remain readable.

For each consequential selection, explain:

- Which access pattern or requirement it serves.
- Which feature, key, partition, transaction, or acknowledgment boundary supplies the claimed behavior.
- Which relevant failure it does not solve, and one credible alternative when the choice merits discussion.

Prefer a small working baseline. Introduce additional products when a demonstrated limitation requires them. Keep answers stable by reusing established choices for the same input unless its constraints change. Do not teach standard concepts from first principles or add every technology below to every solution.

Hello Interview recommends knowing representative technologies and explaining their application instead of relying on broad SQL-versus-NoSQL claims. This rulebook adapts that approach to explicit diagram labels. [Key technologies](https://www.hellointerview.com/learn/system-design/in-a-hurry/key-technologies).

## Redis features and deployment choices

| Selection                            | Use when                                                              | Explain the boundary                                                                                                                                                                                                                                                                                                       |
| ------------------------------------ | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Redis cache with TTL                 | Repeated reads tolerate stale or missing entries                      | Define keys, expiry, invalidation, miss behavior, and stampede protection. TTL limits cache age; it does not establish source-of-truth correctness.                                                                                                                                                                        |
| Redis sorted sets                    | Ranking or ordered lookup matches the access pattern                  | Define score, tie handling, retention, and hot-key limits.                                                                                                                                                                                                                                                                 |
| Redis atomic commands or Lua         | A counter or conditional operation needs atomic execution             | Define the keys and operation; atomic execution does not imply durable consensus across failover.                                                                                                                                                                                                                          |
| Redis Pub/Sub                        | Live fan-out can tolerate missed messages                             | Disconnected subscribers miss messages; use a recoverable source when replay is required. [Pub/Sub](https://redis.io/docs/latest/develop/use-cases/pub-sub/).                                                                                                                                                              |
| Redis Streams with consumer groups   | Workers need retained entries, independent groups, and acknowledgment | Explain XADD, XREADGROUP, XACK, pending-entry recovery, and idempotent effects. Reclaim abandoned work with XAUTOCLAIM; trimming, persistence, replication, and consumer lag bound recovery. One stream key is not automatically split across shards. [Streams](https://redis.io/docs/latest/develop/data-types/streams/). |
| Redis Sentinel with primary/replicas | A non-sharded Redis deployment needs monitored failover               | Sentinel manages failover, not horizontal partitioning. [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/).                                                                                                                                                                               |
| Redis Cluster                        | Memory or throughput requires multiple shards                         | Explain hash slots, cluster-aware clients, and hot keys. Multi-key operations require compatible same-slot keys; a single hot key still needs redesign. Acknowledged writes can be lost during failover. [Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/).              |

Redis replication is asynchronous by default; WAIT does not turn Redis into a strongly consistent consensus store. Do not use a replicated cache counter as the sole proof of strict inventory or payment correctness. [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/).

Redis Streams is a data structure and messaging feature; Redis Cluster is a sharded deployment. They can coexist. Do not present them as competing products. For work queues that retain jobs until processing completes, compare Streams with a managed queue; for long retained logs and multiple replaying consumers, consider Kafka. Make the selection from workload, recovery, and operational requirements.

## Other technology choices

Use this table as a selection aid, not a required component list. These are design recommendations; verify a particular deployment's guarantees when the answer depends on them.

| Role                            | Concrete candidate          | Reasoning to include                                                                                                                                                                                                                                                                                                    |
| ------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Transactional state             | PostgreSQL                  | Access-path indexes, transaction boundaries, row locks or conditional writes, and retry behavior. Specify replication and failover policy for durability claims.                                                                                                                                                        |
| Key-oriented managed storage    | DynamoDB                    | Partition/sort keys, hot partitions, conditional writes, and the consistency required by each read path.                                                                                                                                                                                                                |
| Partitioned wide-column storage | Cassandra                   | Query-shaped tables, partition size, write distribution, and chosen consistency levels; do not infer linearizability from quorum terminology alone.                                                                                                                                                                     |
| Search index                    | Elasticsearch               | Indexed fields and query needs; describe refresh lag and how authoritative state is checked before a consequential action.                                                                                                                                                                                              |
| Durable event log               | Apache Kafka                | Partition key, ordering scope, retention, consumer groups, replay, and idempotent effects. Kafka transactions do not automatically make an external API call exactly once. [Kafka design](https://kafka.apache.org/40/design/design/).                                                                                  |
| Stateful stream computation     | Apache Flink                | Justify continuous event-time processing, windows, watermarks, and checkpoints. Keep broker and processor roles separate. End-to-end exactly-once behavior depends on participating sources and sinks. [Flink guarantees](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/datastream/guarantees/). |
| Durable workflows               | Temporal                    | Use when long-running retries and recovery justify an orchestrator. Define idempotent activities and compensation; workflow durability does not make external effects atomic.                                                                                                                                           |
| Background delivery             | Amazon SQS                  | Choose queue mode and explain visibility timeout, redelivery, dead-letter handling, and consumer idempotency.                                                                                                                                                                                                           |
| Request ingress                 | Envoy or Amazon API Gateway | Choose according to deployment constraints; identify routing, authentication, throttling, and deadline responsibilities.                                                                                                                                                                                                |
| Blob storage                    | Amazon S3                   | Separate bytes from transactional metadata; explain upload completion, access control, and cleanup of partial or orphaned objects.                                                                                                                                                                                      |

## Coordination and ZooKeeper alternatives

Keep ZooKeeper in the vocabulary, but prefer a suitable contemporary deployment choice for a new solution. When ZooKeeper is relevant to a selection, explain the role-specific alternative once in the decision notes. Keep diagram labels concise; do not append replacement advice to each mention. Preserve an original question's wording in the question panel. Consider these alternatives:

- etcd for small coordination state, leases, and leader election.
- Consul when service registration and health-based discovery are the actual requirement.
- KRaft when discussing Kafka metadata. Kafka 4.0 removed ZooKeeper mode; KRaft is Kafka's metadata mechanism, not a general application coordination service. [Kafka upgrade guide](https://kafka.apache.org/40/getting-started/upgrade/).

These are alternatives for a role, not drop-in protocol replacements. Preserve explicit legacy constraints and explain migration separately. Do not replace a system merely because it is older. When an existing platform already supplies discovery or leader election, consider that facility before deploying another coordination cluster.

For etcd, distinguish linearizable KV operations from optional stale serializable reads and watch delivery. Use leases and transactions where appropriate; require fencing at the protected resource when a paused former leader could still write. Do not use coordination storage as the application's bulk data store. [etcd API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/). For discovery, Consul provides service registration and health information; that role differs from transactional inventory ownership. [Consul discovery](https://docs.hashicorp.com/consul/docs/discover).

## Research scope and maintenance

The Hello Interview index and publicly accessible deep-dive material informed the categories and interview emphasis. Restricted deep-dive sections were not read; do not describe this reference as a complete reproduction or an official Hello Interview technology prescription. Product-specific correctness limits above use primary documentation. The recommendations connecting them to interview answers are this skill's synthesis.

Relevant Hello Interview reading, consulted 2026-10-25:

- [Redis](https://www.hellointerview.com/learn/system-design/deep-dives/redis): representative features and interview tradeoffs.
- [Kafka](https://www.hellointerview.com/learn/system-design/deep-dives/kafka): messaging and retained-stream roles.
- [Flink](https://www.hellointerview.com/learn/system-design/deep-dives/flink): justify real-time processing before selecting it; stateful processing concerns.
- [ZooKeeper](https://www.hellointerview.com/learn/system-design/deep-dives/zookeeper): coordination use cases; public introduction and outline only.

Review generated content for named technologies, justified features, and accurate guarantee boundaries. Keep this review semantic: a fixed brand-name allowlist cannot establish that a component is appropriate. Use saved solution JSON for deterministic rebuilds; do not change technology choices during rendering.
