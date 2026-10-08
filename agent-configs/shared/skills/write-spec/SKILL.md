---
name: write-spec
description: Write, amend, or reconcile a technical specification (SPEC.md and any area files) for spec-driven development, backed by dated research. Use when starting a spec for a new project or feature, changing specified behavior, turning settled decisions from a brainstorm into a spec, or reconciling a spec with code that changed first or never had one.
---

# Write a spec

This skill produces an approved spec: `SPEC.md`, area files when the spec outgrows one file, and the research behind its decisions. Approval does not authorize planning or implementation; `plan-from-spec` plans an approved spec.

## 1. Establish the baseline

1. Read the repository's instructions for where specs and research live and for spec conventions. Unless they or the user name other locations, use `SPEC.md` at the repository root, area files in `specs/`, and research in `docs/research/`.
2. Treat decisions already settled in the conversation, such as a brainstorm's outcome, as constraints. Work only through what remains open.
3. Select the mode:

   | Mode      | When                                                         |
   | --------- | ------------------------------------------------------------ |
   | New       | No spec covers the subject.                                  |
   | Amend     | The request changes specified behavior.                      |
   | Reconcile | Code changed before its spec, or code exists without a spec. |

4. For Amend and Reconcile, read the root spec, the affected area files, Explored alternatives, and the source and tests the request touches. In Reconcile mode, section 3 classifies each behavior. In Amend mode, map the request to the affected requirement IDs and classify it:

   | Finding                                                                                 | Action                                                        |
   | --------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
   | Code violates a requirement                                                             | Return `No spec change` with the fix the requirement implies. |
   | The change stays within a permitted choice                                              | Return `No spec change`.                                      |
   | The change alters what a user, an integrator, another component, or stored data notices | Amend through sections 2–5.                                   |
   | The spec is missing, conflicting, or ambiguous                                          | Settle the gap through sections 2–5.                          |

## 2. Research the facts

Research when a decision depends on facts the session lacks, such as external APIs, versions, comparable products, or published evidence. Skip research for a small or settled spec. Finish research before the decision rounds, so the user is asked for preferences, not facts.

1. Split the facts into independent questions, one per research document.
2. If the host has no `spec-researcher` agent, research each question in-session under [research.md](references/research.md). Otherwise, start one `spec-researcher` per question, at most three at a time, and queue the rest. Give each the question, the decision it informs, its output path, and today's date.
3. Read each returned summary. Open a research document only where a decision needs its detail.
4. Add each new document to the research directory's `README.md`, a `Document | Question it answers` table. When a new document replaces an old one, delete the old one and its row in the same change.

If online research is unavailable, report the gap and defer the decisions that need the missing evidence.

## 3. Reconcile code with the spec

Skip this section unless the mode is Reconcile. List the public behavior in the source, tests, and documentation: commands, APIs, configuration, events, persisted data, and user-visible failures. Map each behavior to its requirements and propose one action for each:

| Finding                                                 | Proposal                                 |
| ------------------------------------------------------- | ---------------------------------------- |
| Code implements the requirement as written              | Keep the slug.                           |
| Code differs, and the user approves the difference      | Amend the requirement and keep the slug. |
| Code implements behavior that no requirement covers     | Mint a requirement with scenarios.       |
| No code implements it, and the behavior is abandoned    | Retire the slug.                         |
| No code implements it, and the behavior is still wanted | Keep the slug.                           |

A spec for existing code reconciles against an empty spec, so every behavior starts as a mint proposal. Minting and retiring need the user's decision; missing code does not retire a requirement.

## 4. Settle the decisions

Use `brainstorm` for every decision round, including proposed mints and retirements and content that sits on the spec–plan boundary in [spec-format.md](references/spec-format.md#spec-or-plan). When no decision remains, present the integrated design: scope, invariants, requirements by area, failure behavior, security, and explicit deferrals. Wait for the user to confirm it.

## 5. Write the spec

1. Read [spec-format.md](references/spec-format.md) and write the spec under it, ordering sections and terms by prerequisite knowledge. Follow the repository's layout and section headings; report a convention that conflicts with a format invariant instead of migrating it. For an amendment, also apply the format's status, identifier, and informative-section rules, and update each requirement with its scenarios.
2. Include each optional section whose condition holds. Explain relevant omissions when presenting the spec, and ask only when an omission reflects an unresolved decision.
3. Run the structural check from the repository root, passing `--research <dir>` when research lives outside `docs/research/`:

   ```sh
   uv run <skill-dir>/scripts/check_spec.py <path/to/SPEC.md>
   ```

   If the script cannot run, print its stderr and stop. Otherwise, fix every error.
4. Run `review-changes mode=apply` on the spec, its area files, and the changed research. Bring each finding that needs a decision back to the user through `brainstorm`.
5. Present the spec for approval. When the user approves the complete spec, set `status: approved`. After an amendment, report which existing plan sets need reconciliation through `plan-from-spec`; do not refresh their baselines or completed task states here.

## Return

- `Done`: the spec is saved, and its status matches the user's approval. Report the paths, the minted, amended, and retired requirement IDs, the research documents, and explicit deferrals.
- `No spec change`: the request is a fix or a permitted choice. Report the requirement that governs it.
- `Blocked`: a decision, the approval, or evidence is outstanding. Report what resolves it.
