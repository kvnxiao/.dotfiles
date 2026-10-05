# Patterns

Each pattern names its signal, an analyzer section or a cue to look for, and the reconstruction it suggests. A signal marks a candidate; the user decides.

## Structure

- **Agent procedures in a human doc.** Signal: instruction files or skills link to sections of a doc, and its size far exceeds the linked sections. Reconstruction: move each procedure into an agent-facing file read at its step, and keep a human overview that agents do not read. Leave content that humans also follow where humans look for it.
- **Always-loaded file used as the contributor guide.** Signal: the README or contributor docs send humans to `AGENTS.md` or `CLAUDE.md`. Reconstruction: keep the rules both follow there, move agent procedures to files read at their step, and move human-only setup to a contributor doc. Ask before changing where humans look.
- **Cycles and upward links.** Signal: link cycles, upward links. Reconstruction: a tree read top-down. Always-loaded files link to entry skills, entry skills link to their own references and to shared files, and references and shared files link nowhere else.
- **Specialists that start each other.** Signal: skills that name other skills, especially mutual pairs; review or delivery steps in several skills. Reconstruction: one coordinator routes, and each specialist ends by returning one named outcome. The coordinator owns review and delivery, so nothing runs twice. A repository whose skills do not hand work to each other needs no router.
- **Dual entry points.** Signal: branches on who started the work, such as "if X did not start this", or the same preamble repeated across skills. Reconstruction: one entry point for every request of that kind, including requests that name a specialist.
- **Overlapping skills.** Signal: two skills with shared steps whose outcomes route to each other. Reconstruction: merge them, and move a rare sub-procedure into a reference. Ask before merging when the workloads may diverge.
- **Restated files.** Signal: repeated sentences; identical files; files with the same set of referrers; a template that restates a guide section by section. Reconstruction: one home per rule, merging files that the same steps read and deleting restatements. Replace an identical copy with a symlink when the host follows it. Keep copies across hosts when their formats differ, and keep their meaning identical.
- **Overloaded terms.** Signal: one word names two gates, such as approving a document and authorizing work, or one gate has two names. Reconstruction: one term per gate, defined once in the always-loaded file.
- **Steps out of order.** Signal: a guard, definition, or failure branch after the step it governs; a term used before it is defined. Reconstruction: order each file as it runs, the way pseudocode reads.

## Placement

- **Rules read before they are needed.** Signal: links in a first step or under "before any edit"; trace reads that no step uses, such as an index or wiki fetched at the start of every session. Reconstruction: read each file at the step that applies it, and name the trigger there. A rule that must hold even when an agent misses a trigger stays in an always-loaded file.
- **Role-specific rules in an always-loaded file.** Signal: an always-loaded section, sized in the analyzer's section list, that the traces apply only for some roles or workflows. Delegates on Claude Code and Codex reload the always-loaded files. Reconstruction: move the section into a file those roles read at their step.
- **Delegates that load a coordinator's procedure.** Signal: an agent definition names a skill whose steps do what the delegate must not, such as starting agents, editing, or running reviews. Reconstruction: give the delegate a role contract file and load only that.
- **Delegates that ask the user.** Signal: a delegate's steps ask the user, run a decision skill such as `brainstorm`, or wait for approval. Reconstruction: only the coordinator talks to the user, and delegates return open decisions as an outcome.
- **Descriptions without a trigger.** Signal: a listed description that restates the skill's name or omits when to use it. Reconstruction: state what the skill does and when to use it, so the model chooses from the listing without reading bodies.
- **Rarely used skills listed upfront.** Signal: the listing column of the analyzer's skills table. Reconstruction: when only users start the skill, use a host control that hides it from the model and keeps it user-invocable.
- **Listings a delegate does not use.** Signal: a delegate start that includes a skill listing while the delegate's definition names the files it reads. Reconstruction: turn the listing off for that delegate with a host control.

## Records and retrieval

- **Records without a reader.** Signal: a record field from step 4 with no reading step or person, or one its reader could derive from other state, such as PR status, labels, or files present. Reconstruction: drop fields and records that no later step or human reads, give each kind of record one home, and keep history separate from current state. A human reader counts; ask the user.
- **Writes more often than reads.** Signal: a record rewritten at every transition while readers read it only when work resumes or ends. Reconstruction: write it at the points a reader needs it.
- **Lookups for facts in context.** Signal: steps that search transcripts, logs, or settings for a fact the host already gives the model, such as its model name, the date, or the working directory. Reconstruction: take the fact from context.
- **Broad retrieval.** Signal: list or search commands where a recorded pointer exists, fetching every comment or page, cloning a repository to read it. Reconstruction: a targeted query with explicit fields, or a fetch by the recorded ID.
- **Large files read whole.** Signal: placeholder paths with large matches, or traces in which several agents read the same large file in full for work that touches part of it. Reconstruction: read the sections the work touches, found by heading or by an index script, and keep full reads for work on the whole file.
- **Undated evidence.** Signal: research or notes without the date or version they were observed in, or a directory of them without an index. Readers cannot tell when to recheck a finding, and they read every file to find one. Reconstruction: dated evidence with an observed-in marker and an index per directory, and a recheck only when a step depends on a finding. Reorganize expensive reference material instead of deleting it.

## Scripts and tooling

- **Rules a command could enforce.** Signal: "do X before Y" where Y runs a command or script; a template that tells the reader to replace it. Reconstruction: make the command refuse or check, and delete the prose.
- **Deterministic loops.** Signal: steps that loop over files, records, or command output, or repeat a fixed command sequence. Reconstruction: a script that prints only what the next step needs.
- **Hard-wrapped Markdown.** Signal: a Codex line-paging risk whose unwrapped count is under the limit. Codex models page through files by line ranges. Reconstruction: when the target supports Codex, turn off hard wrapping for agent-facing Markdown. Check the formatter's documentation for per-path settings, and say so when you cannot verify them.
- **Long files.** Signal: a line-paging or tool-output risk that unwrapping does not fix. Reconstruction: split the file by the steps that read it, or put what most readers need first.

### Proposing a script

Place each script beside its only user, in `<skill>/scripts/`, or in the repository's existing scripts directory or task runner when several skills or humans use it. Write it in the language of the target's scripts that run on the same platforms, preferring the one its task runner calls. When the target has no such scripts, or the script belongs to a user-level skill, write typed Python run through `uv`, and check it with `ruff` and `ty`. The calling step names the command, its output, and its failure branch:

- When a script that gates a rule fails, print its stderr and stop.
- When an informational script fails, continue and report the gap.
- Never reimplement a script's logic as a fallback.

## After applying

- **First-pass output.** A restructure can create its own repeated text, caller branches, and stale paths in scripts. Step 7 reruns the analyzer to catch them.
