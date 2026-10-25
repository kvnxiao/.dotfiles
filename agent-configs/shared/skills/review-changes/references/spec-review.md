# Spec review

Review a spec, its area files, and the research behind them adversarially: challenge the idea and approach as well as the text. Every finding names a concrete way an implementer or a conformance reviewer would go wrong. Follow [review-execution.md](review-execution.md) for scope, read-only execution, and reporting.

Read the format rules in `~/.agents/skills/write-spec/references/spec-format.md`. If it is missing, report the missing path and review against the checks below.

## Investigation

For a snapshot, first read the spec top to bottom without following links; then read the linked research and area files. For a diff:

1. Read the root spec and each changed file top to bottom.
2. Read the requirement blocks of each area file that a changed area file lists directly in its `depends-on` frontmatter, and of each area file that lists a changed one there. A change to the root spec alone does not make an area file changed.
3. Search the remaining area files and research for the added, changed, and retired requirement IDs and defined terms, including the old names of renamed terms. Read each paragraph, requirement block, or table row that mentions them.

Apply the checks below to the changed text and its interactions with the passages you read. State in the report that cross-area consistency was checked only for those passages.

- **Idea and approach:** Does the design solve the stated problem for the stated audience within its constraints? Name a simpler design that meets the same goals, an Explored alternative dismissed for a reason that does not hold, and a decision the linked research does not support.
- **Requirements:** Check that each requirement is necessary (its intent traces to a goal), singular, observable from outside the system, and complete in trigger, result, and failure behavior. Flag vague criteria such as "fast", "appropriate", "if possible", and "etc.". Report a scenario that a plausible wrong implementation passes.
- **The set:** Find contradictions between requirements, invariants, and non-goals. Find goals that no requirement serves, and failure, cancellation, recovery, or ordering behavior that the requirements leave out. Find requirements outside the goals.
- **Reading order:** Find terms, states, or approaches used before they are introduced, and terms that disagree with the terms table.
- **Spec–plan boundary:** Preserve required languages, frameworks, libraries, observable behavior, and acceptance scenarios. Flag internal signatures, module layout, code snippets, and algorithms unless an external contract requires them. Keep detailed feasibility evidence, API mechanics, experimental setup, and measurements in linked research or probes. Flag exact names, formats, or values an external party depends on that the spec leaves unstated.
- **Approval readiness:** Apply the format's readiness criteria. Flag an approval prerequisite that only asks for completed features or passing implementation tests, unless the user explicitly required it. Allow optional prototypes and validation that strengthen confidence without making them default approval prerequisites. For a genuine feasibility concern, name the assumption, its design consequence, and the bounded evidence needed. Keep pending conformance and release checks distinct from unresolved product decisions; do not waive those checks when removing an approval prerequisite.
- **Normative language:** Judge each lowercase "should" or "may" in requirement and invariant blocks. Report one that leaves an obligation optional or hides an unstated option. Report an uppercase SHOULD or MAY that does not state when the deviation applies.
- **Current state:** Report history, provenance, dates, ticket references, and figures that go stale.
- **Diagrams:** Report a diagram that disagrees with its prose, and a table that repeats a diagram that lists every transition.
- **Structure:** From the repository root, run `uv run "$HOME/.agents/skills/write-spec/scripts/check_spec.py" <path/to/SPEC.md>`, passing `--research <dir>` when research lives outside `docs/research/`, and report its errors. Do not repeat its checks by hand.

## Report

Report defects in the spec, such as a contradiction, an unverifiable requirement, or a gap with a concrete scenario, as correctness findings. Report a challenge to the idea or approach as an unresolved concern: it is a decision for the user, not a fix. Give the alternative and its trade-off.
