# Spec format

Define the intended end state for human review and implementation. Apply [documentation boundaries](document-boundaries.md); these format rules govern `SPEC.md` and its area files.

## Invariants

These hold in every repository, whatever its layout or heading conventions:

- **Intended end state.** State durable functional and nonfunctional requirements. Code may lag behind the contract; do not weaken it to match incomplete implementation. Keep engineering choices open within explicit constraints and amend related requirements consistently when findings require a changed contract.
- **No development history.** Amend the spec in place. Keep concise current rationale beside a constraint; put evaluated alternatives that affect requirements or feasibility in public decisions and implementation history in private plans. Leave out changelogs, update dates, ticket references, and counts that go stale.
- **Normative text is declared.** The conformance clause states which text binds; examples and notes are labeled.
- **Proportionate.** Leave out a section or field that has nothing to say. Never write "N/A" or "None".
- **Unwrapped.** Write each paragraph and list item on one line, so a read returns more content per line range.

## Spec or plan

Decide where content belongs with one test: would a user, an integrator, another component, or stored data notice if two implementations chose differently? If so, the content belongs in the spec. If only this implementation's own code depends on it, it belongs in the plan. Detailed edge cases and failure behavior belong in the spec when they change observable outcomes; length alone does not make them an implementation plan.

| Concern                                       | Spec                                                                                                                          | Plan                                 |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| Goals, non-goals, constraints, invariants     | States them                                                                                                                   | Cites them                           |
| System design                                 | Components, responsibilities, state ownership, data flow                                                                      | Module and file layout               |
| Names and formats                             | Exact only when an external party depends on the exact form: CLI flags, configuration keys, file and wire formats, exit codes | Everything else                      |
| Signatures, internal types, unexposed schemas | Leaves them out                                                                                                               | Defines them                         |
| Languages, frameworks, and libraries          | States the required technology choices and compatibility constraints                                                          | Selects details the spec leaves open |
| Algorithms and task order                     | Leaves them out unless an external contract requires one                                                                      | Selects them                         |
| Undecided details                             | Open questions in a draft; Permitted choices once approved                                                                    | Resolves them                        |

Keep the spec concise by stating the required technology choices and a brief rationale, then linking to the supporting research and probes. Put implementation code, internal API call sequences, experimental setup, and measured results in those supporting artifacts or implementation plans. Keep examples in the spec when they define the system's public interfaces, configuration, or other compatibility contract. For example, require a chosen UI framework in the spec; link to the capability assessment and runnable probe for evidence that it supports the intended interactions.

## Approval readiness

A draft is ready for user approval when it defines a feasible design for its stated scope. For an MVP, establish that its required experience is achievable with the chosen architecture and technology stack. Keep approval separate from implementation acceptance, which requires evidence that the code conforms, and release readiness, which includes deployment and operational checks.

Present a spec for approval when:

- Product choices, scope, and important failure behavior are settled.
- Requirements are consistent and have observable acceptance scenarios.
- Evidence supports the design's material feasibility assumptions, or the user explicitly accepts the remaining uncertainty.
- Remaining engineering choices have clear permitted boundaries.

Require a preapproval investigation only for a concrete uncertainty whose answer could change required behavior, architecture, or an essential dependency. Identify the assumption and the design consequence before proposing more research. Use documentation, source inspection, or a bounded probe in proportion to that risk, and stop when the decision has enough support. Honor an explicitly requested prototype or approval condition.

Allow optional prototyping and validation within the authorized scope to test claims, compare approaches, or strengthen confidence in the direction. These experiments can be useful before approval even when the design is already feasible. Do not turn optional validation into an approval prerequisite merely because it remains possible or incomplete. Record its evidence and limitations under [the research output boundary](research.md#assignment-and-boundaries), using conversation-only findings during active brainstorming.

Treat missing features, unrun integration tests, and ordinary implementation defects as implementation work. Do not require a complete feature prototype merely to approve its requirements. For example, a spec can require cancellation to restore the current target while the implementation plan assigns the cancellation code and tests.

Keep acceptance outcomes and necessary validation conditions in the spec. Put files, internal types, algorithms, task order, test commands, and concrete verification assignments in plans. Record pending implementation and release checks in plans, or in the conversation until planning is authorized; moving a check does not waive it. When a bounded investigation remains necessary within an approved design, assign it to the plan and block only dependent work.

## Sections

Use this reading order, adapting headings to repository conventions:

1. **Purpose and context:** the problem, audience, and goals.
2. **Functional requirements:** capabilities, business rules, behavior, workflows, and user experience.
3. **Nonfunctional requirements:** measurable performance, target scale, reliability, security, privacy, compatibility, and other required guarantees.
4. **Non-goals and out-of-scope behavior:** what the system deliberately does not solve.
5. **Constraints and assumptions:** required choices, dependencies, and conditions shaping the solution.
6. **High-level system design:** responsibilities, state ownership, boundaries, and interactions needed to explain the contract.
7. **Detailed contracts and behavior:** exact interfaces, lifecycle transitions, failure outcomes, compatibility, and migration where needed.
8. **Conformance and supporting evidence:** what binds and the evidence supporting feasibility.

Keep functional requirements, nonfunctional requirements, and scope boundaries near the top, before design mechanics. Introduce terms before use; add a shared glossary only when it helps. State security obligations with the relevant requirements; add a threat model when its scope needs further explanation. Leave out detailed sections that have nothing to add.

For a small spec, the early requirement sections can contain complete blocks and scenarios. For a spec set, use concise overviews linked to authoritative blocks in the areas. Overviews do not introduce separate obligations or repeat complete rules. Place invariant requirement blocks under an H2 heading containing `Invariants`, which the checker uses to distinguish them from requirements that need plan coverage. Keep cross-cutting invariants in the root; detailed areas follow prerequisite order.

An implementation choice is not a nonfunctional requirement merely because it is technical. Require a framework or algorithm only when deliberately constrained to establish the intended contract. Approval does not imply that all implementation mechanisms or runtime behavior have been discovered.

Add **Open questions** only for unresolved behavior or material feasibility assumptions that prevent approval. Link supporting research and public decisions when relevant; do not reproduce their findings or rejected directions in the spec.

## Requirements

Write each requirement as a block under an H3 heading. Its first paragraph is the statement: the trigger or precondition and the observable result. Labeled fields follow. Every block, invariants included, has `**Scenarios:**`; add each other field only when it has content:

- `**Intent:**` the goal the requirement serves, in one line. A reviewer uses it to judge whether an implementation meets the purpose and not only the wording.
- `**Failure behavior:**` what happens when the trigger occurs and the result cannot be produced.
- `**Permitted choices:**` the variation an implementation may choose; the implementation documents its choice.
- `**Scenarios:**` one or more checks, each giving the initial state or input, the action, and the observable result. Cover failure, cancellation, recovery, and ordering where the behavior depends on them.

```markdown
### REQ-export-overwrite — Export overwrite protection

When the export target file exists and the user does not pass `--force`, the export command writes nothing and exits with status 3.

**Intent:** Serves the goal that exports never destroy user data silently.

**Failure behavior:** If the target exists but cannot be read, the command exits with status 4 and does not modify the file.

**Scenarios:**

- Target `out.csv` exists; run `export out.csv`: the command exits 3 and `out.csv` is unchanged.
- Target `out.csv` exists; run `export --force out.csv`: the command exits 0 and `out.csv` has the new export.
```

- Keep one behavior per requirement, stated at the boundary an outside observer sees.
- Define exact values and formats when compatibility depends on them.
- Never use an adjective such as "fast", "intuitive", or "appropriate" as the only acceptance criterion; state the measurable condition.
- Write a scenario that a plausible wrong implementation fails, not one that every implementation passes.
- An invariant applies to every change, so reviewers check all invariants and only the requirements a change affects. Plans cite invariants but do not own them.

### Identifiers

Name each requirement `REQ-<behavior-slug>`:

- Use two to four kebab-case words that name the behavior, not its mechanism, and match the heading title.
- Do not use ordinals or numeric segments, obligation verbs such as `must-`, library or product names, or the project's own name: `REQ-session-restore`, not `REQ-012` or `REQ-must-restore-redis`.
- Add an area prefix only to tell siblings apart: `REQ-review-cancellation` beside `REQ-round-cancellation`.
- Keep each slug unique across the spec and its area files, and distinct from plan task names.

Every amendment resolves to one of these operations. Do not add retirement ledgers, redirect tables, or rename notes to the spec.

| Operation                     | Rule                                                                          |
| ----------------------------- | ----------------------------------------------------------------------------- |
| Meaning unchanged or refined  | Keep the slug; change only the text.                                          |
| Behavior split                | Keep the slug for the dominant part; give each separated behavior a new slug. |
| Behaviors merged              | Keep the slug that still describes the merged behavior; retire the other.     |
| Behavior defunct              | Retire the slug and delete its block and references.                          |
| Slug contradicts its behavior | Rename it. Rename for a wrong name, never for tidiness.                       |

After a retirement or rename, run `rg -i 'req-<old-slug>'` over the spec, its area files, and `.plans/`, and resolve every hit in the same change. Name `.plans/` explicitly: `rg` skips hidden directories. Never reuse a retired slug for different behavior.

## Normative language

Open the Conformance section with the clause, adapted to the spec:

> A conforming implementation satisfies every requirement and invariant in this spec and its area files, the stated constraints and non-goals, the exact names and formats in external contracts, and the transitions in each state or flow diagram that lists every transition. Present-tense statements in these parts are mandatory. Uppercase SHOULD marks a recommendation an implementation may decline with a documented reason; uppercase MAY marks an allowed option. Text labeled Example or Note, background, requirements overviews linking authoritative blocks, supporting evidence, other diagrams, linked research, and public decisions are informative.

State obligations in plain present tense: "The command exits with status 3", not "The command should exit with status 3". Use uppercase SHOULD or MAY only for a real exception or option, and state its condition. A lowercase "should" or "may" in a requirement block leaves its force unclear; the `review-changes` spec review judges each one.

## Size and spec sets

Keep each spec file under 40 KB. That is about one 10,000-token tool output and about thirty minutes of reading, so one file fits one reading session for an agent or a human. When the core spec exceeds the budget, split it into a spec set:

- **Root `SPEC.md`:** purpose, functional and nonfunctional requirements overviews, non-goals, constraints, shared terms, high-level design, cross-area invariants, conformance, and an area index. The index lists each area file in prerequisite order with one line on what it covers and when to read it.
- **Area files `specs/<area>.md`:** one per area of responsibility, drawn along state ownership: each requirement belongs to exactly one area. An area assumes only the root and the areas it lists in `depends-on`; the dependencies do not form a cycle. Terms that only one area uses live in that area.
- **Transitional area:** current-state description, migration rules, and compatibility paths that end at a cutover go in one area, retired when the cutover completes. The rest of the set describes the intended end state.

Split along areas of responsibility, never by section type. A spec under budget stays one file, with its diagrams inline.

## Diagrams

- Add a Mermaid diagram where a flow branches, loops, or has several states. Place it after the prose that introduces its terms. Write a linear sequence as a numbered list instead.
- A state or flow diagram that lists every transition with its trigger is the statement of those transitions; do not repeat them in a table. The surrounding prose states guards, failure behavior, and anything a label cannot express.
- Other diagrams, such as component maps, illustrate the prose and do not add requirements.
- Do not use ASCII art.

## Frontmatter

Start each spec file with YAML frontmatter:

```yaml
---
status: draft # or approved; root SPEC.md only
areas: [specs/sessions.md, specs/storage.md] # root of a spec set only
---
```

```yaml
---
spec: ../SPEC.md # area files only
depends-on: [sessions.md]
---
```

Write each path relative to the file that declares it. A spec is `draft` from its first draft or an amendment until the user approves the complete spec. An `approved` spec has no Open questions section.

## Informative sections

- **Open questions:** list undecided behavior and material feasibility assumptions that prevent design approval, with the requirements they block. Remove a question when resolved or when the user accepts the remaining uncertainty. Do not list ordinary implementation or release checks here.
- **Supporting evidence:** link the research index. Add a row for a requirement when readers need to trace it: the requirement, its research links, and the outcome the research does not establish. Keep findings in the research documents.
