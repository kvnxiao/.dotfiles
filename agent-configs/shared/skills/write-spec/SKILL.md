---
name: write-spec
description: Write or amend a technical specification (SPEC.md and any area files) from a known proposed change or contract question, backed by dated research. Use for new projects or features, settled brainstorm designs, and amendments that need reconciliation with existing code. Use reconstruct-spec to discover an existing system's insufficiently understood contract.
---

# Write a spec

Before writing or delegating work, restore any brainstorm state from the conversation or continuation summary and follow [Brainstorming boundary and conclusion](../brainstorm/SKILL.md#brainstorming-boundary-and-conclusion). This rule also applies if brainstorming starts during this workflow.

Apply [documentation boundaries](references/document-boundaries.md) when writing the spec or supporting documents. Consult [public decisions](references/decisions.md) when selecting a direction; record qualifying settled conclusions within the authorized scope.

This skill produces an approved spec: `SPEC.md`, area files when the spec outgrows one file, and the research behind its decisions. Use the shared [format](../review-spec/references/spec-format.md) and [reconciliation rules](../review-spec/references/reconciliation.md). Approval does not authorize planning or implementation; `plan-from-spec` plans an approved spec.

## 1. Establish the baseline

1. Read the repository's instructions for where specs and research live and for spec conventions. Unless they or the user name other locations, use `SPEC.md` at the repository root, area files in `specs/`, and research in `docs/research/`.
2. Treat decisions already settled in the conversation, such as a brainstorm's outcome, as constraints. Work only through what remains open.
3. Select the mode:

   | Mode  | When                                                                                                                 |
   | ----- | -------------------------------------------------------------------------------------------------------------------- |
   | New   | A proposed project or capability needs its first spec.                                                               |
   | Amend | A known change or contract question affects an existing spec, including a change implemented before its spec update. |

   When the task is to discover the contract of existing software, use `reconstruct-spec`. Repository age and investigation size do not determine the skill: a cross-cutting amendment can require substantial research, and one undocumented subsystem can need reconstruction.

4. For Amend, when the spec files are committed in Git, note the current commit (`git rev-parse HEAD`) in the session as the amendment base for section 4's review. Read the root spec, the affected area files, and relevant source and tests. Compare current behavior, intended guarantees, and the requested change under the shared reconciliation rules. Include compatibility obligations and related invariants, even when the implementation changed first. Map the request to affected requirement IDs and classify it:

   | Finding                                                                                 | Action                                                  |
   | --------------------------------------------------------------------------------------- | ------------------------------------------------------- |
   | Code violates a still-intended requirement                                              | Keep the requirement and report the implementation fix. |
   | The change stays within a permitted choice                                              | Keep the requirement.                                   |
   | The change alters what a user, an integrator, another component, or stored data notices | Amend through sections 2–4.                             |
   | The affected contract is missing, conflicting, or ambiguous                             | Settle the gap through sections 2–4.                    |

   Classify each affected behavior separately. Return `No spec change` only when none requires a contract change. A proposed or selected change that was implemented first still proceeds through reconciliation and the decision workflow.

## 2. Research the facts

Research when the user requests a topic investigation or a decision depends on facts the session lacks, such as existing behavior, compatibility constraints, external APIs, versions, or published evidence. A small or settled spec does not require new research. Optional prototyping and validation can still strengthen confidence under [Approval readiness](../review-spec/references/spec-format.md#approval-readiness). Resolve factual questions before each decision round, so the user is asked for preferences, not facts.

During active brainstorming, use conversation-only research assignments under [research.md](references/research.md), with the brainstorm state and temporary-probe restrictions. Return findings to the conversation; defer research documents and index updates until conclusion and authorization to save them. A request to write a spec includes its supporting research; an investigation request alone does not.

Outside active brainstorming, when durable research is authorized:

1. Scope cohesive topics from the user's interests, objective, and requested depth. Clarify materially different interpretations; do not require an interview when the request is clear. Group related questions and reuse existing topic documents.
2. Assign one `spec-researcher` research agent per independent topic, at most three at a time. If the named profile is unavailable, assign an available agent the same [research contract](references/research.md); research in-session when delegation is unavailable. Give each the objective, relevant questions, requested depth, output path, and today's date. Do not assign concurrent writers to the same document.
3. Read each returned synthesis; open detail only where the research objective or a decision needs it.
4. Keep the research directory's `README.md` as a concise topic index. When consolidating or replacing documents, preserve relevant evidence and repair affected links in the same change; do not create a historical correction index.

If online research is unavailable, report the gap and defer the decisions that need the missing evidence.

## 3. Settle the decisions

Use `brainstorm` for every decision round, including proposed new and retired requirements and content that sits on the spec–plan boundary in [spec-format.md](../review-spec/references/spec-format.md#spec-or-plan). Apply the shared reconciliation rules to evidence conflicts and code-first amendments. Assess readiness under [Approval readiness](../review-spec/references/spec-format.md#approval-readiness); do not substitute completed implementation tests for settled design decisions. When no decision remains, include scope, invariants, requirements by area, failure behavior, security, and explicit deferrals in the consolidated design. Follow brainstorm's conclusion rule before writing; reuse confirmation already obtained for that design rather than asking again.

## 4. Write the spec

1. Read [spec-format.md](../review-spec/references/spec-format.md) and write the spec under it, ordering sections and terms by prerequisite knowledge. Follow the repository's layout and section headings; report a convention that conflicts with a format invariant instead of migrating it. For an amendment, also apply the format's status, identifier, and informative-section rules, and update each requirement with its scenarios.
2. Include each optional section whose condition holds. Explain relevant omissions when presenting the spec, and ask only when an omission reflects an unresolved decision.
3. Run `review-spec mode=apply` on the spec, its area files, affected research, and affected public decisions, as the diff from the amendment base to the working contents, including untracked files in those paths. Supply the research directory when it differs from `docs/research/`. When no amendment base was noted, review the spec, its area files, and the research and decision documents this run wrote or changed as a snapshot instead. The shared review runs structural and semantic checks; resolve its errors and bring each finding that needs a decision back to the user through `brainstorm`.
4. Present the spec for approval once the readiness criteria are met. Keep pending implementation and release verification in plans or the conversation until planning is authorized, without treating it as an unresolved product decision. When the user approves the complete spec, set `status: approved`. After an amendment, report which existing plan sets need reconciliation through `plan-from-spec`; do not refresh their recorded spec fingerprints or completed task states here.

## Return

- `Done`: the spec is saved, and its status matches the user's approval. Report the paths, the new, amended, and retired requirement IDs, the research documents, and explicit deferrals.
- `No spec change`: the request is a fix or a permitted choice. Report the requirement that governs it.
- `Blocked`: a decision, the approval, or evidence is outstanding. Report what resolves it.
