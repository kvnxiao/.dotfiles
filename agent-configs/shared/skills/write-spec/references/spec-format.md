# Spec format

A spec states what a system must do and why, for humans who review it at a high level and for agents that implement and check against it. It owns behavior and system design; plans own mechanism. Every rule here applies to `SPEC.md` and its area files; research has its own format in [research.md](research.md).

## Invariants

These hold in every repository, whatever its layout or heading conventions:

- **Readable top-down.** Introduce each term, actor, state, and approach before or at its first use. Put concepts that several sections share in Background and terms, and define a term used in one section at its first use there. Before drafting a section, list the concepts it assumes and place their introductions earlier. A link to a later section may offer optional detail; it never replaces an explanation the current passage needs.
- **Current state only.** Amend the spec in place, as if writing it for the first time. Leave out history, changelogs, "last updated" dates, ticket links, and phrases such as "previously" or "now"; git records history. Explored alternatives is the one record of rejected ideas. Leave out figures that go stale, such as requirement or word counts.
- **One home per fact.** Link research, other spec files, and external contracts instead of restating them.
- **Normative text is declared.** The conformance clause states which text binds; examples and notes are labeled.
- **Proportionate.** Leave out a section or field that has nothing to say. Never write "N/A" or "None".
- **Unwrapped.** Write each paragraph and list item on one line, so a read returns more content per line range.

## Spec or plan

Decide where content belongs with one test: would a user, an integrator, another component, or stored data notice if two implementations chose differently? If so, the content belongs in the spec. If only this implementation's own code depends on it, it belongs in the plan.

| Concern                                       | Spec                                                                                                                          | Plan                   |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| Goals, non-goals, constraints, invariants     | States them                                                                                                                   | Cites them             |
| System design                                 | Components, responsibilities, state ownership, data flow                                                                      | Module and file layout |
| Names and formats                             | Exact only when an external party depends on the exact form: CLI flags, configuration keys, file and wire formats, exit codes | Everything else        |
| Signatures, internal types, unexposed schemas | Leaves them out                                                                                                               | Defines them           |
| Algorithms, libraries, task order             | Leaves them out unless an external contract forces one                                                                        | Selects them           |
| Undecided details                             | Open questions in a draft; Permitted choices once approved                                                                    | Resolves them          |

## Sections

Write the core sections in this order:

1. **Purpose and scope:** the problem, the audience, goals, non-goals, constraints, assumptions, and dependencies.
2. **Background and terms:** the context a reader needs, and a `Term | Meaning` table for terms that more than one section uses.
3. **Invariants:** properties every change must preserve, written as requirement blocks.
4. **Requirements:** functional and quality requirements, grouped under H2 headings by area of responsibility and ordered by prerequisite knowledge.
5. **Security:** the threats in and out of scope and the requirements that address them. When the system does not add attack surface, write one sentence that says why.
6. **Conformance:** the conformance clause.

Add an optional section only when its condition holds:

| Section                     | Include when                                                                                                                                                           |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Architecture overview       | The system has more than one component, or state ownership or data flow crosses component boundaries. Place it after Background and terms.                             |
| External contracts          | An external party depends on exact names, formats, or values.                                                                                                          |
| State and lifecycle         | An entity moves through several states with distinct transitions.                                                                                                      |
| Compatibility and migration | Existing users, stored data, or versions must keep working during a change. A spec set puts it in a transitional area (see [Size and spec sets](#size-and-spec-sets)). |
| Open questions              | The spec is a draft with undecided behavior.                                                                                                                           |
| Explored alternatives       | The design rejected or abandoned an option.                                                                                                                            |
| Supporting evidence         | Research documents back the spec's decisions.                                                                                                                          |
| References                  | The spec cites external contracts, standards, or API documentation.                                                                                                    |

Place optional sections where their prerequisites allow: shared concepts before the workflow, states before their transitions, behavior before its exceptions.

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

> A conforming implementation satisfies every requirement and invariant in this spec and its area files, the constraints and non-goals in Purpose and scope, the exact names and formats in External contracts, and the transitions in each state or flow diagram that lists every transition. Present-tense statements in these parts are mandatory. Uppercase SHOULD marks a recommendation an implementation may decline with a documented reason; uppercase MAY marks an allowed option. Text labeled Example or Note, Background, Explored alternatives, Supporting evidence, other diagrams, and linked research are informative.

State obligations in plain present tense: "The command exits with status 3", not "The command should exit with status 3". Use uppercase SHOULD or MAY only for a real exception or option, and state its condition. A lowercase "should" or "may" in a requirement block leaves its force unclear; the `review-changes` spec review judges each one.

## Size and spec sets

Keep each spec file under 40 KB. That is about one 10,000-token tool output and about thirty minutes of reading, so one file fits one reading session for an agent or a human. When the core spec exceeds the budget, split it into a spec set:

- **Root `SPEC.md`:** purpose and scope, shared terms, the architecture overview, invariants that span areas, Security, Conformance, and an area index. The index lists each area file in prerequisite order with one line on what it covers and when to read it.
- **Area files `specs/<area>.md`:** one per area of responsibility, drawn along state ownership: each requirement belongs to exactly one area. An area assumes only the root and the areas it lists in `depends-on`; the dependencies do not form a cycle. Terms that only one area uses live in that area.
- **Transitional area:** current-state description, migration rules, and compatibility paths that end at a cutover go in one area, retired when the cutover completes. The rest of the set then stays current-state only.

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

- **Open questions:** list each undecided behavior with the requirements it blocks. Remove a question in the change that resolves it.
- **Explored alternatives:** give one entry per rejected or abandoned idea, with the reason it was dropped. Reconsider an entry only when new evidence or changed constraints invalidate that reason, and name what changed.
- **Supporting evidence:** link the research index. Add a row for a requirement when readers need to trace it: the requirement, its research links, and the outcome the research does not establish. Keep findings in the research documents.
