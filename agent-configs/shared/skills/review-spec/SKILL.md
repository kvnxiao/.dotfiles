---
name: review-spec
description: Review a technical specification for shared format, completeness, consistency, conformance scenarios, and supporting evidence. Use directly for spec reviews or from write-spec and reconstruct-spec before approval. Report findings by default; apply settled corrections when requested.
---

# Review a spec

Own the shared [spec format](references/spec-format.md), [structural checker](scripts/check_spec.py), and [semantic review contract](references/spec-review.md). Both `write-spec` and `reconstruct-spec` produce specs under these rules.

Before writing or delegating, restore any brainstorm state and follow [Brainstorming boundary and conclusion](../brainstorm/SKILL.md#brainstorming-boundary-and-conclusion). A review does not approve a spec or authorize planning, implementation, commits, or publication.

## 1. Resolve mode and scope

Honor explicit user constraints, then a supplied `mode=report` or `mode=apply`. Default to report for review or validation requests; use apply for an explicit fix request or a writer's preapproval review.

- **Report:** Return findings without editing.
- **Apply:** Correct confirmed defects within the authorized scope. Resolve product decisions through the calling workflow's `brainstorm` before changing the contract.

Preserve a caller's diff or snapshot scope, amendment base, and exclusions. Otherwise, review the current spec as a snapshot: use the named root spec or the repository's configured location, defaulting to `SPEC.md`. Include its area files and explicitly scoped research and public decisions. Read linked supporting documents as needed under the semantic review contract; a link alone does not authorize editing that document.

Record the root spec, research directory, scope, mode, applicable repository rules, and any supplied reconstruction evidence. Check repository conventions against format invariants; report a conflict instead of silently changing the repository's layout or headings.

## 2. Check structure

From the repository root, run:

```sh
uv run <review-spec-dir>/scripts/check_spec.py <path/to/SPEC.md>
```

Pass `--research <dir>` when research lives outside `docs/research/`. If the checker cannot run, report its stderr and stop with validation incomplete. Otherwise, include its errors and warnings in the review assignment. A successful check establishes only the checks the script performs; it does not establish complete requirements, useful scenarios, or fidelity to repository behavior.

## 3. Review meaning and apply corrections

Run `review-changes` once with the resolved scope and explicit mode. Supply the checker results and [spec-review.md](references/spec-review.md) as the spec assessment contract. Use its full workflow for independent review, confirmed fixes, documentation, prose, and validation. `review-changes` reads the assessment contract directly; it does not invoke this entrypoint again.

Review the spec's purpose, requirements, invariants, interfaces, failure behavior, and conformance scenarios. For reconstructed requirements, check the supplied evidence and uncertainty under [reconciliation.md](references/reconciliation.md). Report an unsupported claim with the evidence needed to resolve it. Do not infer completeness from passing implementation tests or start a new repository-wide reconstruction without a scoped reason.

In apply mode, preserve requirement identity and settled intent. Return findings that require a product decision to the calling workflow, or use `brainstorm` when invoked directly. Keep ordinary implementation defects and release checks separate from spec defects. Do not weaken requirements to match incomplete code or set `status: approved`.

After corrections, rerun the structural checker if its inputs changed. Fix all confirmed, in-scope errors whose resolution is settled; report any remaining decision or evidence gap.

## Return

Report the reviewed scope and mode, confirmed findings or applied fixes, unresolved decisions, and validation results. State limitations in evidence and cross-area coverage. A clean structural result is not a clean semantic review, and a clean review is not user approval.
