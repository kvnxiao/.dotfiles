# Reservation-system applicability review

Read this reference for booking, inventory, ticketing, appointment, or capacity-allocation questions. Use it before authoring the baseline and revisit it during the mandatory coverage pass. The [public diagram survey](diagram-research.md) records the comparison sources. Apply the target prompt's requirements; a similar product name does not establish an identical workload.

## Evaluate the mechanisms

For each relevant row, choose include, defer, or exclude and state a problem-specific reason. Record the disposition in `coverage-review.md`; expose consequential choices and interviewer follow-ups in Notes. A deferred mechanism needs a trigger, not just a statement that it is unnecessary.

| Concern                      | Required design question                                                                                                                                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Public ingress and replicas  | Who calls the API? When application instances scale, how are requests distributed and unhealthy instances removed? Show workload-appropriate ingress and explain traffic distribution for the scaled public backend, including a replicated monolith. |
| Discovery versus inventory   | Which data can be stale? Separate catalogue/candidate discovery from authoritative selection and purchase. A search index or cache cannot allocate scarce capacity.                                                                                   |
| Search implementation        | Which queries need indexes, full-text relevance, geospatial filtering or facets? Start with a justified query plan; name a search-engine trigger and its update path if deferred.                                                                     |
| Cache scope                  | Define separate keys and freshness for static metadata, candidates, prices and volatile inventory. Explain misses, invalidation, stampedes and authoritative revalidation.                                                                            |
| Temporary reservation        | Use a durable state and expiry contract across checkout. Keep database transactions short; do not keep a row lock open while a user enters payment details.                                                                                           |
| Expired capacity             | Explain reclamation lag and how stale held counters recover. If reclaiming on demand, use the same state predicates and atomic capacity updates as the expiry worker. Never reclaim ambiguous external bookings solely because a timer elapsed.       |
| Payment and external effects | Identify durable intent, stable identities, callback/retry handling, and compensation after partial success. A provider timeout does not prove failure.                                                                                               |
| Hot inventory and overload   | Distinguish normal throughput from concentration on one resource. Explain bounded admission; consider a waiting room only when measured or assumed bursts justify its queueing and fairness costs.                                                    |
| Live updates                 | Decide whether polling suffices or whether SSE/WebSockets materially improve an explicitly required experience. Faster updates do not reserve capacity.                                                                                               |
| Edge caching                 | Separate public static content from personalized or volatile availability. Introduce a CDN only for an applicable delivery path and freshness contract.                                                                                               |
| Inventory ownership          | Identify who can sell each unit. An aggregator needs provider contracts, holds or confirmation; transactions in its own database cannot prevent another seller's independent sale.                                                                    |

## Reflect the chosen deployment in the drawing

Check every statement about replicas, sharding, caches, workers or service extraction against the diagram at that step. Add the necessary ingress, routing, state owner and update path, or annotate an existing node when only deployment changes. Do not describe a scaled backend while leaving a single-instance request path unexplained.

For example, annotate an application node with stateless replicas and show the chosen load balancer, reverse proxy, or gateway on the request path. Keep one logical node per replica group; drawing every instance is unnecessary. Keep a monolith when domain-service extraction adds no needed isolation or scaling benefit.

Explain differences from the nearest known pattern. Multi-night hotel inventory needs atomic claims across all nights; a ticket example's individual-seat mechanism does not automatically establish that guarantee. Prefer one transactional authority unless another mechanism has a demonstrated benefit and a complete failure protocol.
