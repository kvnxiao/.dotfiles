---
name: reconstruct-spec
description: Deeply investigate an existing repository or subsystem and reconstruct its intended specification from code, tests, documentation, and observed behavior. Use for brownfield discovery, contributor onboarding that needs a spec, or recovering an undocumented contract through an active brainstorm with the user. Use write-spec for a known proposed change or amendment.
---

# Reconstruct a spec

Produce the same intended-contract `SPEC.md` and area files as `write-spec`, supported by traceable repository research. Recover purpose, functional requirements, business rules, invariants, edge cases, and conformance scenarios. Write a contract that a new implementation can satisfy without copying internal module structure.

Start or continue an active `brainstorm` with the user during reconstruction. Restore its state before research or delegation and follow [Brainstorming boundary and conclusion](../brainstorm/SKILL.md#brainstorming-boundary-and-conclusion). Keep findings and proposed requirements in the conversation until the consolidated design is confirmed. Do not save reports, specs, or persistent investigation state during active brainstorming.

Use the shared [spec format](../review-spec/references/spec-format.md) and [reconciliation rules](../review-spec/references/reconciliation.md). Apply [documentation boundaries](../write-spec/references/document-boundaries.md) and consult relevant [public decisions](../write-spec/references/decisions.md). A reconstruction request authorizes the spec and its supporting research; approval does not authorize planning or implementation.

## 1. Establish the subject and evidence baseline

Read repository instructions, the existing spec if any, and enough product documentation and entrypoints to explain the subject. Honor the requested repository or subsystem boundary. Use the repository's destinations, defaulting to root `SPEC.md`, area files in `specs/`, and research in `docs/research/`.

Note the inspected revision and relevant working changes in the session. If existing spec files are committed, record `git rev-parse HEAD` as the amendment base for review. Identify the relevant configurations and supported versions; do not assume one local setup represents every deployment.

Present the initial understanding of the purpose, audience, major workflows, and investigation scope. Label inferred purpose. Use `brainstorm` for the currently answerable decisions before the detailed investigation; resolve factual questions through inspection first. Preserve settled scope and avoid inventing questions when the user has already supplied the answer.

## 2. Investigate the contract

Read [investigation.md](references/investigation.md) and investigate by user workflow and area of responsibility. Trace observable behavior through source, tests, schemas, configuration, and relevant documentation. Use bounded, isolated probes when source inspection cannot settle a consequential fact. Record untested conditions explicitly.

Keep a conversation-level coverage map of the in-scope capabilities, inspected evidence, candidate requirements, conflicting claims, and remaining unknowns. Revisit it as findings change the investigation. Do not claim completeness from a file inventory, passing tests, or an overview alone.

For independent topics, use one `spec-researcher` research agent per cohesive area, at most three concurrently. If the named profile is unavailable, assign an available agent the same research contract; research in-session when delegation is unavailable. Pass the repository baseline, relevant questions, depth, today's date, the active brainstorm state, and the [research contract](../write-spec/references/research.md). During brainstorming, require conversation-only findings. Include the investigation guidance and require evidence locations, applicability limits, and decisions needed from the user. Researchers return facts to the coordinator; the coordinator owns the cross-area synthesis and questions.

## 3. Resolve intent with the user as research proceeds

Alternate investigation with `brainstorm` rounds. Present supported behavior and its implications, inferred intent, conflicting evidence, and the decisions that can now be made. Explain enough of each workflow for the user to assess it; do not ask the user to supply facts available in the repository.

Apply the shared reconciliation rules to existing requirements and proposed additions. Group related requirements for discussion. Preserve approved future behavior when implementation is missing, and ask before adopting a defect or accidental behavior as a compatibility obligation. Reconstruction does not authorize redesigning the product.

Follow dependent questions into later rounds. Investigate contradictions across areas and check uncovered boundaries before concluding. Once the in-scope investigation supports a coherent contract, present the consolidated design, including:

- Purpose, audience, scope, and explicit deferrals.
- Core workflows, business rules, and requirements by area.
- Invariants, ownership boundaries, and relevant quality and security guarantees.
- Interfaces, failure behavior, edge cases, and conformance scenarios.
- Consequential evidence limits and any uncertainty the user must accept.

Obtain confirmation under the brainstorm conclusion rule before writing. Preserve the settled design and research state in continuation summaries; a new turn does not end the brainstorm. If evidence remains unavailable, narrow or defer the affected claim explicitly instead of presenting it as established.

## 4. Write and review the spec

After brainstorming concludes, write the spec under the shared format. Preserve existing requirement IDs when their identity remains unchanged and apply the format's amendment rules. Describe observable contracts and required system responsibilities; keep implementation navigation, source citations, and observed discrepancies in supporting research.

Write cohesive topic research under the research contract, including the relevant baseline, evidence, and limitations. Maintain a concise research `README.md` index. Link consequential reconstructed requirements to their supporting evidence. Record qualifying evaluated directions under the public decision rules without inventing historical rationale.

Run `review-spec mode=apply` on the spec, its area files, and affected research and public decisions. For an amendment, use the diff from the recorded base to working contents, including untracked files in scope. Without a base, use a snapshot of the spec set and supporting documents this run wrote or changed. Return findings that require decisions to `brainstorm`.

Present the complete spec for approval when the shared readiness criteria are met. Set `status: approved` only after the user approves that spec. Report existing plan sets that need reconciliation through `plan-from-spec`; do not refresh their fingerprints or completed task states here.

## Return

- **Done:** Report the saved spec and research paths, new/amended/retired requirement IDs, approval status, investigation limits, and explicit deferrals.
- **No spec change:** Report the governing requirements and the evidence supporting them, including implementation defects that do not justify changing the contract.
- **Blocked:** Report the missing evidence, unresolved decision, or approval needed to finish. Do not describe an incomplete investigation as a complete reconstruction.
