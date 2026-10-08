# Spec review

Review a spec, its area files, and the research behind them adversarially: challenge the idea and approach as well as the text. Every finding names a concrete way an implementer or a conformance reviewer would go wrong. Follow [review-execution.md](review-execution.md) for scope, read-only execution, and reporting.

Read the format rules in `~/.agents/skills/write-spec/references/spec-format.md`. If it is missing, report the missing path and review against the checks below.

## Investigation

First read the spec top to bottom without following links; then read the linked research and area files.

- **Idea and approach:** Does the design solve the stated problem for the stated audience within its constraints? Name a simpler design that meets the same goals, an Explored alternative dismissed for a reason that does not hold, and a decision the linked research does not support.
- **Requirements:** Check that each requirement is necessary (its intent traces to a goal), singular, observable from outside the system, and complete in trigger, result, and failure behavior. Flag vague criteria such as "fast", "appropriate", "if possible", and "etc.". Report a scenario that a plausible wrong implementation passes.
- **The set:** Find contradictions between requirements, invariants, and non-goals. Find goals that no requirement serves, and failure, cancellation, recovery, or ordering behavior that the requirements leave out. Find requirements outside the goals.
- **Reading order:** Find terms, states, or approaches used before they are introduced, and terms that disagree with the terms table.
- **Spec–plan boundary:** Flag mechanism that belongs in a plan, such as internal signatures, module layout, algorithms, or libraries, unless an external party depends on it. Flag exact names, formats, or values an external party depends on that the spec leaves unstated.
- **Normative language:** Judge each lowercase "should" or "may" in requirement and invariant blocks. Report one that leaves an obligation optional or hides an unstated option. Report an uppercase SHOULD or MAY that does not state when the deviation applies.
- **Current state:** Report history, provenance, dates, ticket references, and figures that go stale.
- **Diagrams:** Report a diagram that disagrees with its prose, and a table that repeats a diagram that lists every transition.
- **Structure:** From the repository root, run `uv run "$HOME/.agents/skills/write-spec/scripts/check_spec.py" <path/to/SPEC.md>`, passing `--research <dir>` when research lives outside `docs/research/`, and report its errors. Do not repeat its checks by hand.

## Report

Report defects in the spec, such as a contradiction, an unverifiable requirement, or a gap with a concrete scenario, as correctness findings. Report a challenge to the idea or approach as an unresolved concern: it is a decision for the user, not a fix. Give the alternative and its trade-off.
