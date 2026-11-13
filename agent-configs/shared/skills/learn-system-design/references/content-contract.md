# Structured solution content

Author `solution.json`; the renderer owns HTML, typography, canvas coordinates, controls, and notes placement. Use the [bundled JSON Schema](../assets/solution.schema.json) as the field contract. Start from the [initializer's skeleton](renderer.md#new-question), whose empty fields deliberately fail validation until completed.

## Canonical modules

| Field                       | What to generate                                                                                                                                                 |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `format_version`            | Keep `2` for this schema.                                                                                                                                        |
| `title`, `subtitle`, `mark` | Question name, interview focus, and short header initials.                                                                                                       |
| `scope`                     | A concise description of the system and supplied deployment constraints.                                                                                         |
| `assumptions`, `exclusions` | Explicit decisions to confirm and features outside the interview.                                                                                                |
| `requirements`              | Records with stable `id`, `kind` (`functional` or `nonfunctional`), `text`, and `basis` (`given` or `assumed`).                                                  |
| `entities`                  | Stable `id`, domain `name`, and concise `description` stating the entity's role or invariant.                                                                    |
| `interfaces`                | Stable `id`, operation `name`, Markdown `contract`, and lists of functional requirement IDs and entity IDs.                                                      |
| `steps`                     | Ordered presentation states using the fields below.                                                                                                              |
| `sources`                   | Actual source title, HTTPS URL, retrieval date, and the claim supported. Identify bundled framework references as bundled research, not freshly retrieved pages. |

Use lowercase hyphenated IDs, such as `fr-publish`, `nfr-revocation`, and `publish-version`. Keep IDs when revising content. Requirement IDs in `covers` describe what the step addresses; interfaces reference only functional requirement IDs, while their entity IDs describe what the operation exchanges or changes. Discuss non-functional guarantees in the contract text and reference them through step `covers` lists.

The renderer derives the first-column requirements and second-column entities and interfaces from these modules. Do not maintain a second copy of those summaries. Write canonical text as terse whiteboard fragments, preferably 6–12 words per bullet. Use concise signatures and input/output fragments for APIs; put detailed schema and error behavior in the relevant steps.

## Entity fields

Supply `fields` for each newly authored entity: an ordered list of concise field declarations, such as `reservationId: UUID (PK)` or `state: BookingState`. Render a bold entity name above an indented bullet list, one field per line. Keep `description` for the entity purpose or invariant in Notes. Existing records without `fields` retain their compact description rendering.

Show identifiers, relationships, and the state required by the core operations. Use a compact conceptual projection, not exhaustive production DDL. Put detailed indexes, uniqueness constraints, and transaction semantics in Notes. Keep API field names consistent with these declarations. The renderer uses two compact columns within the middle-column entity section and reserves their largest version size before revealing them.

## Step contract

Every step has `id`, `phase`, `title`, `lead`, Markdown `body`, Markdown `notes`, `reveal`, and a `covers` list. Notes may be empty. Plain strings and Markdown are content, never HTML or scripts. Use one `-` bullet per nonblank body line. Keep body bullets as short fragments; put prose, tables, and code blocks in study notes.

Use `phase` to describe a step's purpose: `requirements`, `entities`, `interfaces`, `baseline`, `deep-dive` or `summary`. Include the phases relevant to the prompt and let them recur as the explanation develops. A baseline and final summary are required; deep dives are optional. Keep entities or interfaces empty when outside the prompt's scope, and explain these omissions in the opening Notes. Include every in-scope requirement; do not omit requirements to shorten the presentation. Start with requirements or a baseline design; introduce a baseline before any deep dive; finish with summary steps. A baseline may show architecture, schema, product flows or state transitions. The phase does not require new infrastructure.

Choose the progression from the prompt. A general blank-page answer may establish requirements, entities and interfaces before its baseline. A design review may start with the supplied baseline; a depth-focused answer may establish the main constraint, show a minimal working path, then introduce contracts alongside the mechanism that needs them. Preserve complete coverage in each case and explain the chosen progression in the opening Notes.

Set `reveal` to `{"section":"functional","ids":["fr-search"]}` or the corresponding `nonfunctional`, `entities` or `interfaces` section. Reveal each canonical record exactly once within its matching phase. Reveal at most one section per step. Group related requirements, entities, or interfaces when they can be explained together; split groups when they become difficult to follow. Use `null` for discussion-only or design steps. Sections may interleave across steps. For example, reveal a latency requirement after a baseline reveals the reason for it.

Introduce or replace diagrams in baseline, deep-dive or summary steps. Steps without `diagram` retain the most recent diagram, including later requirement, entity and interface reveals. The renderer uses each step's own ID for the retained figure's accessible identifiers. New reveals remain the Notes target while the diagram stays visible. Preserve graph positions across snapshots.

The renderer keeps prior records at stable board locations, reserves space for future records and restores the matching state on backward navigation. Canonical modules determine the board regions, not presentation order. All step bodies appear only in Notes. Do not add introductory steps merely to complete a template before reaching the prompt's main constraint.

Write each `lead` as the point the candidate would make aloud. Put terse per-step talking points in `body`; the body, lead, and full explanation appear only in Notes. Put durable mechanisms in canonical board records or diagram annotations, and retain them in subsequent snapshots unless the step explicitly explains their removal or replacement in Notes. Never render a changing per-step bullet block beneath the diagram. Use `notes` for interviewer probes, alternatives, and additional failure cases. Avoid teaching familiar concepts from first principles unless the mechanism is central to this question.

For every `deep-dive` step, add `deep_dive` with these Markdown fields:

| Field            | Required reasoning                                                                        |
| ---------------- | ----------------------------------------------------------------------------------------- |
| `limitation`     | The concrete workload, failure, or invariant that the baseline cannot handle adequately.  |
| `change`         | The selected mechanism and why it addresses that limitation.                              |
| `alternative`    | A credible alternative and why it is not selected under these assumptions.                |
| `tradeoff`       | The resulting latency, consistency, complexity, cost, or operational compromise.          |
| `failure`        | What happens under the most relevant partial failure or concurrency case.                 |
| `diagram_update` | What changes in the shown design; say when a behavior changes without adding a component. |

The renderer labels these fields inside study notes. Do not repeat the same paragraphs in `body`; use the body for the concrete operation being examined. Connect `covers` to the requirements that motivate the dive.

## Contextual notes

Use the label Notes. The renderer anchors each slide's note to its newly revealed bullet. During early discussion-only steps, reuse the most recently revealed bullet. For graph steps, compare nodes with the preceding snapshot in the same family and select the last added or changed node in the current `nodes` array. If no node changed, target the diagram. In baseline, deep-dive, or summary steps, an explicit target overrides automatic selection. For a behavior change involving an existing graph node, set optional `note_target` to that node ID; the legacy `body` value targets the diagram or step title. For example, use `"note_target":"db"` for a transaction-isolation deep dive. Use an explicit target for edge-only changes when a particular node is relevant. Resolve graph targets against the displayed snapshot, including a retained diagram. The validator rejects targets missing from that snapshot and overrides in requirements, entities or interfaces steps.

Choose the semantic target, not pixel coordinates. The viewer places the note near that target without covering visible content and draws an annotation connector. Notes can move between steps; main content and the camera cannot. Preserve detailed notes and scroll long content within the note. Fit all includes the visible note; print presents notes beneath their associated step.

## Diagrams

An optional `diagram` uses one of two data formats:

- `flow`: `labels` has two to four short strings; `description` states the sequence's meaning. The renderer draws a left-to-right flow.
- `graph`: `family` identifies an evolving diagram; `nodes`, `edges`, and `description` define its current snapshot. Each node has `id`, `label`, `column` (0–4), and `row` (0–4). Each edge has `from`, `to`, `label` (possibly empty), and `kind` (`sync` or `async`).

For architecture graphs, supply `architecture` with `deployment` (`monolith`, `microservices`, or `pipeline`), `entry` (`external-api`, `persistent`, `internal`, or `queue`), a `replicated` boolean for multiple public application instances, and a concise `rationale`. Omit this metadata only for non-architecture diagrams. Supply a semantic node `role`: `client`, `gateway`, `service`, `worker`, `queue`, `store`, `cache`, `counter`, `decision`, or `external`. Choose ingress appropriate to the workload and describe traffic distribution when applications are replicated. The validator checks graph references and rejects client-originating edges that do not advance rightward; it does not prescribe an ingress product or prove routing correctness. Trace actual ingress connections during self-review.

Set node `replicated: true` when it represents multiple instances or a cluster. The renderer draws three layered outlines without duplicating labels; this is a multiplicity symbol, not an exact instance count. Leave it false or omit it for single instances.

The gateway role uses a tall, narrow box centered in its grid cell. Other rectangular nodes use a wider rounded box; ellipse and diamond shapes retain their geometry.

Node `shape` optionally overrides the default with `rectangle`, `ellipse`, or `diamond`. Only decisions may use diamonds. Decisions use a short label and labeled outgoing outcomes; put their explanation outside the diamond. Optional `bullets` adds at most two responsibility fragments of 24 characters each. Optional `annotation` adds up to three floating bullet fragments of 27 characters each below that node. Keep annotations clear of edges; use Notes for longer explanations. Optional edge `direction` is `forward` (default) or `both`; the latter draws an arrowhead at each end. Follow [architecture diagram rules](diagram-patterns.md) for semantics and ingress exceptions.

Keep at most nine nodes and twelve edges in a focused graph. Keep node labels under 60 characters and edge labels under 28. `sync` produces a solid arrow and `async` a dashed arrow; explain operation semantics in the body. For entity graphs, state cardinality in edge labels rather than implying call semantics.

Place the main client/gateway/application path on a middle row, with dependencies above and below where the topology permits. The renderer draws independent straight connectors clipped to each shape boundary; use positions that keep those paths clear of unrelated nodes.

Reuse the same `family`, node IDs, and grid positions across architecture snapshots. Include every node and edge visible at that step; snapshots do not depend on replaying earlier steps. The renderer reserves one viewBox size per graph family so later nodes cannot rescale earlier ones. For a separate close-up, choose a distinct family. Inspect routing and label placement: schema validity does not establish diagram readability. Split a dense graph into focused states if connectors cross unrelated nodes or labels overlap.

Do not force a specialized visual into an ambiguous graph. Use focused flows with terse bullets when the primitives cannot express the relationship clearly; put detailed tables and prose in study notes. Extend shared primitives only when required, following the [viewer-change route](../SKILL.md#change-the-viewer).

## Consistency review

The validator checks fields, phase coverage, baseline-before-dive and final-summary ordering, unique reveals, entity-update prerequisites, references, coverage declarations and stable node positions. It cannot establish that a declared guarantee follows from the design. Review these relationships yourself:

- Main-board text uses concise bullet fragments; detailed prose stays in notes. The three-region layout fits a horizontal overview.
- Each reveal adds at most one section with a manageable group of related records; the sequence follows the prompt while keeping future records hidden.
- Every functional requirement has an end-to-end baseline explanation and, when interfaces are in scope, a matching interface.
- Entity identities and API fields agree with diagrams and notes.
- Deep dives address prioritized requirements and modify the baseline coherently.
- Infrastructure labels identify concrete products and relevant modes; explanations justify the choice using the [technology selection rules](technology-selection.md).
- Consistency decisions follow the solution guide: identify operations with different invariants or staleness tolerance, and state their behavior when the relevant authority cannot be reached. Explain a uniform choice when the workload genuinely has one; do not force a mixed answer.
- Each claimed consistency guarantee follows from a concrete authority, transaction, replication, or reconciliation mechanism. Separate CAP partition behavior from normal-operation latency and uptime targets.
- Failure handling matches the consistency, acknowledgment, and durability claims.
- The summary describes the final design, including unresolved compromises.

Complete the mandatory [coverage pass](coverage-pass.md) and save its evidence in the package. Before delivery, evaluate the generated answer against the [solution guide](solution-guide.md) and technology-selection rules, not only the JSON validator. Check the progression, assumptions, requirement coverage, technology choices, consistency decisions, and deep-dive tradeoffs against the actual prose and diagrams. Fix omissions before rendering the final package. Treat coverage IDs as declarations, not proof of compliance; do not add unsupported guarantees just to satisfy a checklist.

For the same question, preserve the same prioritized scope, chosen progression and established decisions unless the user requests a revision. Fresh generation may vary in wording and defensible choices; exact reproduction uses saved JSON and a fixed renderer bundle.

## Progressive entity modeling

Start with the minimum identities and fields needed to discuss the functional requirements, usually two to four fields per entity. Defer recovery identities, versions, indexes, and operational fields until a baseline operation or deep dive needs them. Keep invariants in Notes.

Use optional step `entity_update: {"id": "reservation", "fields": ["reservationId", "state", "idempotencyKey"], "reason": "Persist retry identity before retrying ambiguous writes."}` to replace one entity's field list explicitly. Include all fields that remain; explain additions, renames, and removals in `reason`, which appears in Notes. Use updates only after that entity has been revealed on an earlier step, with `reveal: null` in a baseline, deep-dive or summary step. Keep the same entity ID and board location. The renderer reserves the largest version's space, restores earlier versions on Previous, and anchors Notes to the changed entity. Print and no-JavaScript views show final fields; per-step Notes explain evolution. Do not reveal the final production schema at the start.
