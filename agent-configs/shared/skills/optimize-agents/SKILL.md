---
name: optimize-agents
description: Restructure a repository's agent instructions, skills, and agent definitions to cut upfront tokens and tool calls without losing what they enforce. Use when asked to optimize, slim, simplify, or restructure a repo's agents, skills, AGENTS.md, CLAUDE.md, or GEMINI.md.
---

# Optimize agents

Restructure a repository's agent-facing files so that sessions load less upfront and spend fewer reads, writes, and tool calls per request, while every rule still applies where an agent needs it. The user steers every decision. Edit files only after the user approves the complete design.

## 1. Select the mode

- **Report:** `mode=report`, or a request to assess, measure, or suggest. Run steps 2–4, then reply with the step 6 report. Do not run `brainstorm` or write files.
- **Interactive (default):** run every step. When the user answers a report with a selection such as "apply 1 and 3", start step 5 with those items.

## 2. Resolve the scope

1. Read the target's always-loaded instruction files first. Follow its conventions where they differ from this skill: layout, supported hosts, generated files, who edits which files, branch and approval rules, required tools, and its policy on scripts.
2. Treat a host as supported when the target has files only that host reads, such as `.claude/`, `.codex/`, `.pi/`, `.agents/rules/`, or `GEMINI.md`, or its docs tell people to use it. For a repository that deploys user-level files, use the hosts the user has configured. Report costs and findings only for supported hosts, and note what a host cannot run, such as delegates on pi.
3. Cover every agent-facing surface in the repository: always-loaded instruction files, rules files, skills and their files, agent definitions, docs that agents read, templates and commands that agents fill in or run, host configuration that changes what loads, and the records agents write, such as issue bodies, checkpoints, and research notes.
4. When the user names a subset, recommend and edit only within it. Read other files only to learn how the subset is invoked and what it depends on, and report problems outside the subset separately.
5. Measure surfaces outside the repository, such as user-level instructions and skills, as part of the baseline. Report them separately and never edit them. Read records stored outside the clone, such as issues and wiki pages, only with read-only commands the target allows. When you cannot, describe them from the steps that write them and state the gap.

## 3. Measure

Run the analyzer from this skill's directory; it prints to stdout:

```sh
uv run <skill-dir>/scripts/analyze.py <repo-root> [--exclude <glob>]... [--only <path>]... [--all]
```

Pass `--exclude` for each generated path the target names; globs match resolved paths, detectors skip excluded files, and costs still count them. Pass `--only` for a named subset and `--all` to print every row. Rerun with other flags when a section needs them.

A `truncates` finding means a host loses content. A `risk` finding depends on how a model reads a file or how a skill ships.

For each surface the analyzer lists as not measured, estimate bytes / 4 of what the host loads, such as listed names and descriptions, and label the figure as your measurement. If the analyzer fails, report its stderr, continue without its findings, and state the gap. Do not repeat its checks by hand.

## 4. Break down each workflow

A workflow is one kind of request the instructions handle, such as starting work, reviewing a change, or cutting a release.

1. Read the entry skills and each workflow's skills in full. Read a reference or doc only when a finding or trace points to it. For generated files, read only the listing and the entry file, and measure the rest by size.
2. For each workflow, state its purpose and atomic invariants, marked inferred:
   - **Outcome and inputs.**
   - **Gates:** each approval or authorization, named with one term. Flag a term that names two gates, or a gate with two names.
   - **Actors:** who acts at each step, and who talks to the user.
   - **Records:** each field the workflow writes, how often it writes it, and the step or person that reads it. Count a field as unread when its reader could derive it from other state.
3. Trace two or three requests from the target's own triggers that together reach the workflows with the most reads and record writes. Trace on one supported host, and note what differs on the others. For each trace:
   - List the files read and the step that uses each one. A read that no step uses is a finding.
   - Mark the always-loaded sections the request applies.
   - Include each delegate's start and reads, and the files outside the repository that the workflow reads.
   - Sum instruction tokens. Report reads that vary by request, such as contracts, issue bodies, source, and diffs, separately. Estimate tool calls from the instructions, one per command, read, or write.
4. Read [references/patterns.md](references/patterns.md) and match its signals against the analyzer output, the invariants, and the traces. Before proposing a change that depends on how a host loads files, read [references/hosts.md](references/hosts.md).
5. Mark script candidates. A step is a candidate when all of these hold:
   - Its logic is deterministic.
   - Its input is structured, such as files, JSON, or command output.
   - It repeats within a run, across skills, or across runs.
   - A later step uses its output.

   Keep a step in prose when it needs judgment or when a script would cost more to maintain than it saves. Drop a candidate the target's policy forbids. Before scripting a write, confirm the record has a reader.

Restructure before rewording: a simpler workflow saves more than shorter sentences.

## 5. Settle the design with the user

Invoke `brainstorm` with the design tree. Order rounds by dependency, and skip questions that earlier answers make moot:

1. **Structure:** entry points and routing, merges, deletions, and separating human docs from agent procedures. Group related workflows in one round. For each workflow, show its inferred invariants and two to four reconstructions built from them, including one radical option such as deleting the workflow or merging it into another. A corrected invariant reopens only that workflow's question.
2. **Placement:** what leaves the always-loaded files, and which step reads each rule with which trigger.
3. **Records and writes:** fields and records without a reader, how often each is written, and the one home for each kind of record.
4. **Scripts:** each candidate's location, language, command, output, and failure branch, proposed as patterns.md describes.
5. **Host settings:** skill visibility, delegate loading, and formatter settings.

Put behavior-preserving fixes, such as broken links, repeated text, and restated files, into the design as one batch without a question. Give each behavior-changing recommendation its own question with its estimated saving; moving a rule counts as behavior-changing. When the target states no policy on scripts, treat each script as behavior-changing.

## 6. Present the complete design

Present the design in the format that [references/report.md](references/report.md) describes. In interactive mode, wait for the user to approve the complete design. An answer to one question does not approve it.

## 7. Apply and recheck

1. Apply the approved design in this session, following the target's rules for who edits which files and on which branch.
2. Run the analyzer and the traces once more. Put new findings in changed files into one follow-up round, and apply them only after the user approves them. Report findings elsewhere for a later run.

## 8. Review and report

Run `review-changes mode=apply` once on the accumulated change set. Do not commit, push, or publish without separate authorization.

Report the cost per host before and after, the change summary, the review results, and the separate findings.
