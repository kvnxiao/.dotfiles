---
name: prose-correction
description: Rewrite technical prose into its artifact's register and strict linear causality, then strip AI diction. Audits inline comments, docstrings, commit messages, PR titles and bodies, documentation, chat responses, or any draft text; with no target named, it audits the current change set. Use before opening a PR, during a completion check, or when the user says "prose correct this", "fix this writing", "remove the AI tells", or "make this linear".
---

# Prose Correction

Machine-written technical prose fails in three hierarchical layers. Repair a failure at the earliest law it breaks, then re-read the sentence from the top.

1. **Register:** Mood, tense, and voice belong to the artifact layer, not the narrator.
2. **Causality:** Anchor context and triggers precede actions; actions precede branch details.
3. **Substance:** Every sentence states a concrete fact the reader lacks, using the direct verb the code runs.

Diction ranks fourth. A passage clearing the word list still fails if it breaks a structural law; clean diction is the final polish, never the primary fix.

The ranking is not stylistic preference. Structural failures are stable across model generations and are the durable signal. Word-level tells decay: a flagged word collapses in usage within months while unflagged ones keep growing, and the same words have entered ordinary human writing. A clean word list is never a pass.

---

## Procedure

**Resolve the scope first. The scope the user names wins; the change set is only the default.** Everything below operates on the resolved scope, so settle it before step 0 and state it in the report's first line. A mismatch is then visible before the work rather than after it.

- **No target named** → the active change set: `git diff HEAD` and `git status --porcelain`, reading modified files in context. Edit only changed prose.
- **A directory, subtree, or path glob named** → every prose item under it, whether or not it appears in the diff. An untouched file inside the named target is in scope; its prose was written by the same process and carries the same defects. Enumerate the target's files and subtract the diff to find what a diff-only pass would have missed, then read that remainder too.
- **A file, symbol, or line range named** → that item only.
- **Outside the resolved scope** → report, never edit. Quote the defect and name the file so the user can widen the scope on the next run.

The failure this guards against runs one way: a named target gets silently narrowed to its changed files, because the diff is the habitual scope and every file in the target usually _is_ in the diff. The handful that are not are precisely the stale ones no recent pass has read. Never widen a scope the user did not name, and never narrow one they did.

_Instruction text:_ A `SKILL.md`, `AGENTS.md`, output style, agent definition, or system prompt is read by a model executing it, not by a person comprehending it. Apply Laws 1 through 3 and the no-exemption list. Skip the escape hatch and Canonical Construction: an unusual phrasing of an instruction is a parse risk, and canonical phrasing is what an instruction wants. Semantic Advance governs the prose around an example, never the worked examples themselves, which are how a rule becomes executable.

_Examples must survive removal from their source._ Drawing one from a real codebase is worth doing, because the prose is then verified rather than invented. But a term that codebase coined reads as jargon everywhere else, and Law 3.7 certifies it as consistent precisely because the source repo uses it throughout: `self-contend` passed that way. The test is parseability, not provenance. Naming a source system's commands, types, or flags is fine; a coined term the reader must reconstruct a definition for is not. Strip the local shorthand, or genericize the example. Correctness travels the same way — an example true only given the source system's internals becomes a false claim once quoted elsewhere.

**This is a reading pass, not a search.** Every comment, docstring, and prose block in scope is read and judged one sentence at a time against Laws 1 through 3. Most structural defects have no lexical signature — a tail trigger, a dangling pronoun, a rationale bolted on with `, so`, two invariants joined by `and` — so a search over known patterns cannot reach them and will report clean coverage it did not have. Grep is triage: it orders the work and catches the lexical minority. It never stands in for the read.

Under load this pass degrades into a search, silently, and the report still reads like coverage. The practices below keep that visible:

- **Hold the report to the resolved scope.** Every item in scope gets a verdict: kept, rewritten, deleted, or flagged. A skipped item is then a missing verdict rather than an invisible non-event.
- **Where the scope is too large to read, say so and narrow it.** Report the part that got a full pass and the part that got triage only. A truthful partial audit beats a whole-target claim backed by a word search.
- **Quote before ruling.** Reproduce the sentence, then judge it. A verdict on text you did not reproduce is a verdict from memory of the file, and memory is where a defect with no lexical signature disappears.
- **A `kept` verdict cites its reason, and keeping the fact is not keeping the sentence.** Name the fact the item carries that the code cannot, or the exemption that spares it. `Reads fine` is not a reason and converts to `delete`. Once the fact is named, read the sentence again and judge it like any other. A genuine ordering constraint stated by a subject-less fragment is a `rewrite`, not a `keep`. Naming the fact is what makes such a fragment feel finished, so this is where a `keep` gets waved through.
- **Zero findings is a claim, not a result.** Machine-written prose at density rarely audits clean. A file that yields nothing needs one line saying why — genuinely spare, already audited, or prose too thin to break. Absent that line, treat the file as under-read and re-run it.

**Regenerate, do not edit.** Correcting a sentence in place is the single largest source of surviving defects, because the old wording is still in front of you while you write the new one. Its clause order, its verbs, and its rhythm are the highest-probability continuation available, so they come back. The repair lands on the defect you came for and the sentence keeps everything else. Steps 2 through 4 therefore run through the facts, never through the text: extract what the item claims, check each claim against the code, then compose from the claim list with the old paragraph closed.

- **The code is the authority, and the old prose is only a witness.** An existing comment is a prior author's report about the code, not evidence of what the code does. Read the implementation before ruling on any claim. Where prose and code disagree, the prose is wrong — even when it has survived several passes.
- **A claim you cannot verify is not a fact.** Drop it, or mark it as unverified in the report. Do not carry it forward because it was already there.
- **Do not consult the old sentence while writing the replacement.** Work from the claim list. Compare the two only in step 5, and only to check for facts you dropped.

0. **Model the reader:** Decide who reads this artifact. Internal code maintained by its authors, or a public surface read by newcomers. Every gate below resolves against this answer, so settle it before Law 1 runs.
1. **Classify:** Identify the artifact layer for each item (docstring, commit, inline comment, architecture doc, PR copy).
2. **Extract the claims:** Reduce the item to a list of bare propositions — one invariant, condition, hazard, or ordering constraint each. Strip every adjective, connective, and framing device in the process. An item that reduces to zero propositions is deleted, and so is a proposition the signature or the adjacent line already proves.
3. **Verify each claim against the implementation:** Read the code the item describes and mark each proposition verified, refuted, or unverifiable. Delete the refuted ones. Add the constraint the code carries that the item never stated: this is where a missing hazard or ordering requirement gets found, and pruning alone never finds it.
4. **Compose from the surviving claims:** Write the item from the proposition list in causal order and in that artifact's register. Load `references/diction.md` now, not earlier, and check the new text against it. Fewer propositions than the original is the expected outcome, not a loss.
5. **Verify & Compare:** Read the new text against both the old text and the code. Confirm that no verified number, boundary condition, or constraint was dropped, and that nothing was invented. A fact the old text carried and the new one does not is either a deliberate delete you can name, or a regression.
6. **Re-audit everything you composed:** Text written during steps 2 through 5 is unjudged prose. Run it through Laws 1 through 3 and every tripwire, exactly as you ran the text it replaced. Your replacement is written under the pull of the defect you were fixing, so it is more likely to break a different law than the original was, not less.
   - **A one-phrase substitution is not a repair.** Swapping a word and moving on is how a defect survives a pass: the fix you came for lands, the sentence now reads as handled, and the clauses you never looked at ride into the next commit. If a sentence needs a fix, it goes back through steps 2 through 4 whole.
   - _Evidence this is the dominant failure:_ `git log -L <start>,<end>:<file>` on a defective line typically shows several prose commits in a row, each repairing the defect it was hunting and preserving the rest. One of them will have introduced a new defect while fixing an old one.
   - _Corollary:_ a line with a long prose-commit history is a suspect, not a settled item. Repeated rewriting means the defect survives rewriting.
7. **Adversarial re-read:** Over the items just ruled clean, run one pass whose only goal is to find a single violation. Assume the earlier verdict was wrong and look for the reason. Finding one voids the clean verdicts for that file, which returns to step 1. Finding none, after genuinely trying, is the first evidence the pass held. Run it as a read. A re-read driven by the tripwire greps inherits the main pass's blind spots and re-clears precisely what the main pass missed, because both are then matching the same phrases; the defects that survive to this step are the ones with no lexical signature at all.

**Escape hatch.** Where a sentence satisfies Laws 1 through 3 and still reads synthetic, the problem is that the phrasing sits at the model's mode. Do not swap synonyms. Generate five candidate rewrites with their estimated probabilities, then take a low-probability candidate that preserves every verified fact. Skip this on instruction text.

---

## Law 1: Register Contracts

Match grammatical mood, tense, and voice strictly to the artifact:

| Artifact                             | Grammatical Contract                                                                                                                                       | Example                                                               |
| :----------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| **Docstring / API Header**           | Imperative mood, present tense. Strip the narrator (`This function parses...` → `Parse...`). State constraints the signature cannot show.                  | `Parse incoming buffer and emit decode diagnostics.`                  |
| **Git Commit Subject**               | Imperative mood, present tense, no trailing period. Cause-before-effect body.                                                                              | `feat: log path and major versions on decode failure`                 |
| **Inline Code Comment**              | Clipped present-tense note on the _why_ or a non-obvious invariant. Drop the narrator and first person. Strip meta-transitions (`Basically`, `Note that`). | `// Declined prompt returns before acquiring lock to avoid deadlock.` |
| **Architecture Doc / RFC / PR Body** | Third-person indicative mood, present tense. Name the concrete component a pronoun points at.                                                              | `When the connection resets, the worker flushes the buffer.`          |
| **Chat / Direct Deliverable**        | Direct indicative or imperative verdict. No conversational preamble or trailing wrap-up summary.                                                           | `Applied migration. Added composite index on (user_id, created_at).`  |

### Gates on Law 1

Each rule below does harm when applied without its condition.

- **Imperative compression is for unfamiliar tasks.** Explicit action statements speed reading when the reader does not already know the procedure, and have no measurable effect when the task is familiar. On a public API surface, compress hard. On internal code whose authors wrote the procedure, a fuller sentence costs nothing and a clipped one can obscure.
  - _Reject (compressed past the fact):_ `// Validate pre-lock.`
  - _Apply:_ `// Validate the request before acquiring the lock to prevent a rejected request from mutating state.`
- **Pruning depth tracks reader expertise.** Explanation that helps a newcomer is dead weight to an expert, and forcing an expert to reconcile it against their own model adds load rather than removing it. Prune harder for the maintainer audience than for the newcomer audience.
  - _Delete at both depths:_ `// Acquire the exclusive lock.` above `acquire_lock(&path, Exclusive, timeout)`. The call says it.
  - _Keep at both depths:_ `// A timeout here exits 4 rather than propagating a panic.` The signature cannot show it.
- **Keep the pronoun when the antecedent is the previous sentence's subject.** Replacing a pronoun that already points at the discourse focus slows the reader down. Replace pronouns only where the antecedent is ambiguous, distant, or not the prior subject.
  - _Reject (needless replacement):_ `The parser reads the header. The parser also reports whether the header was truncated.`
  - _Apply:_ `The parser reads the header. It also reports whether the header was truncated.`
  - _Reject (antecedent is not the prior subject):_ `A request selects a retry policy. They differ only in the backoff curve.`
  - _Apply:_ `A request selects a retry policy. Linear and Exponential differ only in the backoff curve.`
- **Drop articles only in short comments over known referents.** Function words earn their place where the following material is dense or unexpected. A telegraphic comment packing three new nouns is harder, not tighter.
  - _Reject:_ `// Reaper drops expired session, rewrites index, warns caller.`
  - _Apply:_ `// The reaper drops the expired session, rewrites the index, and warns the caller.`
  - _Still correct (short, known referent):_ `// Declined prompt returns before acquiring lock to avoid deadlock.`

_Ecosystem Boundary:_ Where a language ecosystem standardizes a specific pattern (e.g., Go Doc starting with the function name, rustdoc third-person summaries, JSDoc `@param`), follow the ecosystem convention while stripping internal narrator fluff.

---

## Law 2: Causality & Dependency Order

Human working memory resolves sentences forward in a single pass. Order every sentence:\
`[Trigger / Condition / Anchor] → [Actor + Action] → [Secondary Branch Detail]`

- **Front-load triggers:** Never put `if`, `when`, `on [event]`, `under [state]`, `after`, `once`, `following`, or `upon` at the tail of a multi-branch clause or inline comment. Temporal triggers read as description rather than condition and are the ones most often missed.
  - _Tripwire:_ `after`, `once`, `following`, `subsequent to`, or `upon` appearing later in the sentence than the main verb.
  - _Reject:_ `The socket closes after the client sends EOF.`
  - _Apply:_ `When the client sends EOF, the socket closes.`
  - _Reject:_ `The summary line is omitted when the count is zero.`
  - _Apply:_ `When the count is zero, the summary line is omitted.`
  - _Also reject (front-loaded past the referent):_ `At zero the summary line is omitted.` Front-loading must not clip the noun the condition is about.
  - _Exception:_ A single-line docstring summary describing a fallback may state the primary return first (`Return fallback payload if header is missing.`).
  - _Bound:_ Keep the preposed clause short. A long condition that separates the subject from its verb costs more than the front-loading saves. Where the trigger runs long, give it its own sentence.
- **No dangling participial branches:** Never attach a secondary condition or consequence with a trailing participle (`..., adding ...`, `..., ensuring ...`, `..., along with ...`). Split them into distinct declarative sentences. This is the single largest measured divergence between machine and human technical prose, so treat a trailing `-ing` after a comma as a defect until proven otherwise.
  - _Reject:_ ``Copy the file at `src` into the cache at `dst`, leaving the original in place.``
  - _Apply:_ ``Copy the file at `src` into the cache at `dst`. The original at `src` is preserved.``
  - _The full cluster:_ `, ensuring`, `, allowing`, `, preventing`, `, avoiding`, `, causing`, `, creating`, `, yielding`, `, leaving`, `, resulting in`, `, thereby [verb]-ing`. The Latinate and adverbial forms do the same work and are missed more often than `, ensuring`.
  - _Bound, stated as a burden:_ a comma plus `-ing` is a violation **unless you name the front-loaded condition it is the direct result of**. `With the cache disabled every lookup goes to the database, leaving the in-memory index unused` passes because the condition is `With the cache disabled`. An exemption you cannot name in one phrase does not apply. A coordinate list (`parsing, validating, and writing`) is not this construction.
  - _Repair trap:_ This construction enters during the fix far more often than in the first draft. `, allowing`, `, preventing`, and `, ensuring` are what a writer reaches for when rebuilding a sentence around a defect they just found, and a reviewer hunting participles still writes them into their own replacement. Check every repair for one before accepting it.
- **No non-restrictive relative clauses:** `, which [verb]` and `, where [actor] [verb]` carry the identical backward dependency a participle does, and they are the reflex substitution once participles are banned. A restrictive clause with no comma (`the file that the writer opened`) is not this defect.
  - _Tripwire:_ `, which` or `, where` attached to an independent clause.
  - _Reject:_ `The worker drains the queue, which prevents memory starvation.`
  - _Apply:_ `The worker drains the queue to keep memory bounded.`
- **Subject belongs to the entity:** Make the primary thing the subject, never its transient attribute, count, color, or flag.
  - _Reject:_ `A red border indicates the failing container.`
  - _Apply:_ `The failing container is marked with a red border.`
  - _Passive voice is correct here._ Machine prose under-uses the agentless passive relative to human writing, so a passive that serves topic continuity is not a defect and must not be "fixed."
- **Premise before judgment:** Place the mechanism before the evaluation or error state.
  - _Reject:_ `Invalid config occurs when declaring exclude on a file.`
  - _Apply:_ `Declaring exclude on a file is a parse error.`
- **Direct negation on the verb:** Negate the verb, never the object or the subject it applies to. This is a causality rule, not a style preference: on `writes no output` the reader resolves `writes`, builds the expectation of written bytes, then hits `no` and undoes it. The negation arrives after the expectation it cancels, which is a backward dependency inside one clause. Negating the verb puts it first, so no wrong expectation forms.
  - _Tripwire:_ `[verb] no [noun]`, `[verb] nothing`, `[verb] neither X nor Y`, or a sentence opening `No [noun] [verb]s`.
  - **Action verbs only.** The defect needs a verb that builds an expectation for the negation to cancel: `writes`, `prints`, `emits`, `reads`, `creates`, `sends`. A stative verb builds none, so a negated object after one is correct and shorter — keep `has no timeout`, `contains no timestamps`, `leaves no borrow outstanding`. `does not have a timeout` is longer, adds `do`-support, and reads as denying a claim rather than describing a state. Run the parse test on the verb; do not match the string.
  - _Reject (object):_ `The dry run compares every entry and writes no output.`
  - _Apply:_ `The dry run compares every entry and does not write output.`
  - _Reject (subject):_ `No caller can supply one.` / `No reader mistakes the one for the other.`
  - _Apply:_ `A caller cannot supply one.` / `A reader cannot mistake the one for the other.`
  - Where a single plain verb carries the meaning, use it (`skips`, not `makes no change to`; `does not write`, not `writes nothing`).
  - _Gate:_ A negation must deny something a reader would otherwise expect. Where nothing is being denied, delete the negation and state the positive fact.
  - _Exempt:_ a lexicalized compound (`no-op`); `no longer`, an adverb on the verb rather than a negated object; and any negator that lands before the expectation it cancels — clause-initial `Neither is added`, post-copula `is neither absent nor text`, or a front-loaded `With neither flag, the command …`. The test is position, not the word: nothing is undone if the reader meets the negation first.
- **One invariant per sentence:** Two independent invariants joined by `and` make the reader hold the first while parsing the second, and a later edit to one silently strands the other. Split them.
  - _Reject:_ ``Stripping only one dot leaves `..` as `.`, and a name that is exactly `.` comes back unchanged.``
  - _Apply:_ ``Stripping a single leading dot reduces `..` to `.`. An exact `.` is preserved.``
  - **A semicolon or colon does not dissolve the rule.** Either may join a mechanism to its consequence (`the buffer is flushed on every write; a reader never observes a partial record`). Neither may join two unrelated operational rules.
  - _Reject:_ `// Writes flush to disk immediately; eviction removes orphaned entries.`
  - _Apply:_ `// Writes flush to disk immediately. Eviction removes orphaned entries.`
- **No deictics for system state:** `from there`, `at that point`, `in that case`, `thereafter`, and a bare `this` as subject name no object. They appear most often when a passive is converted to an active and a bridge is needed. Name the disk, buffer, file, or subsystem.
  - _Reject:_ `The index is written to disk. The loader reads it from there.`
  - _Apply:_ `The index is written to disk before the loader reads it.`
- **No intent clauses on a mechanism:** `so that it can`, `in order to`, and `so as to` frame a mechanical action as an actor's purpose, and they push the goal to the tail. Front-load the goal as a purpose infinitive.
  - _Reject:_ `The daemon re-reads the configuration file so that it can pick up modified port bindings.`
  - _Apply:_ `To apply updated port bindings, the daemon re-reads the configuration file.`
- **`, so` is not a rationale slot:** A trailing `, so [goal]` appends the design reason as an afterthought and buries the constraint that governs the code. Lead with the constraint, or hang the reason off an imperative as a purpose clause.
  - _Reject:_ ``The path is stored as the user wrote it (e.g. `~/.config/app.toml`), so the config stays portable across machines.``
  - _Apply:_ ``Store the unexpanded path (e.g. `~/.config/app.toml`) to keep the config portable across machines.``
  - _Bound:_ `, so` is correct where the second clause is a mechanical consequence rather than a design goal (`the lock is already held, so the nested call does not block`).

| Source / Broken Form                                                                                                                                      | Corrected Linear Form                                                                                                                 |
| :-------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| The decoder names the path, and adds both majors on a version mismatch.                                                                                   | On decode failure, the decoder logs the path. If a version mismatch caused the failure, the decoder also appends both major versions. |
| `return null; // Returns null if the buffer is empty`                                                                                                     | `// If the buffer is empty, return null.`                                                                                             |
| The engine re-derives the same set under the lock.                                                                                                        | Under the lock, the engine re-derives the same set.                                                                                   |
| An empty change set short-circuits ahead of the confirmation branch, so a run with nothing to do neither shows the prompt nor has a line read from input. | An empty change set proceeds without reading a line from the input stream.                                                            |
| Whatever entries the pass did update are already written, so the run that follows sees them.                                                              | The update pass writes changed entries to disk before the next run reads them.                                                        |
| The loader's own read raises the parse error when one does.                                                                                               | If the config does not parse, the loader raises that error on its own read.                                                           |
| Both the refresh pass and the cleanup sweep write that file, so a run that must not write holds both back.                                                | Both the refresh pass and the cleanup sweep write that file. A read-only run skips both.                                              |

---

## Law 3: Substance & Verification

Delete before rewriting. Keep only what provides information the reader cannot obtain from the code itself.

**The burden is on keeping, not on cutting.** A comment is redundant until you can name, in one phrase, the fact it carries that the signature and body cannot: an external constraint, an ordering requirement, a hazard, a benchmarked number, a reason a wrong-looking choice is right. Where no such phrase can be written, delete it. "It reads fine" and "it adds context" are not facts and do not keep a comment alive. This default matters more than any rule below, because the common failure is not a bad rewrite — it is a redundant comment waved through.

**The Information Subtraction Test.** Take the function name, parameter names, and return type. Substitute synonyms freely. If that mechanical exercise reproduces the docstring, the docstring states nothing and gets deleted. Synonym churn is what makes a restatement read as substantive: `fn create_user(...) -> User` documented as `/// Instantiates a new user account.` passes a keyword-overlap check and fails this one.

**Over-cutting check.** A deletion is safe only when the fact it removed still appears somewhere. After cutting, name the surviving site that states the fact, then read that site and confirm it does. Where no site survives, restore the cut. Where two survive, keep the one nearest the decision it governs. Run this on every deletion, including deletions that cleared every rule below.

1. **Prune redundant prose:** Delete comments that merely restate the line below them, docstrings that mechanically unfold the function name, step-by-step narrations of self-evident code, meta-announcements (`Here is a breakdown of...`), and summary closes (`In summary...`). A comment that restates its line is also the highest-risk staleness surface: code and comment drift apart, and inconsistent pairs correlate with bug-introducing commits.
   - _Reject:_ `/// A single lint finding. Carries a stable code, a severity, a human message, and the path the finding concerns.` — over a struct whose fields each carry their own doc comment.
   - _Apply:_ `/// A single lint finding.` The field docs below already state the rest.
2. **Preserve mechanical rigor:** Never cut an ordering requirement, external constraint, concurrency hazard, benchmarked threshold, or non-obvious trade-off to satisfy brevity.
   - _Reject (rigor cut as verbosity):_ `/// Read the inventory under the shared lock.`
   - _Apply:_ ``/// Read the inventory under the shared lock, then release it before the network call. Holding the lock across an untimed `fetch` blocks every later writer.``
   - _Bound:_ restore the constraint, not a paragraph. One sentence of hazard beats three of context.
3. **Use the verb the code executes:** Use direct operational verbs (`logs`, `writes`, `appends`, `skips`, `returns`) instead of vague processing verbs (`handles`, `processes`, `surfaces`, `manages`, `deals with`). A comment verb that contradicts the code raises measured reader load.
   - _Reject:_ `// Handles incoming websocket handshakes and manages TLS termination.`
   - _Apply:_ `// Terminates TLS and upgrades incoming connections to WebSockets.`
   - The concrete verbs also expose the real order: TLS terminates first, and the upgrade runs on the decrypted stream. `handles ... and manages ...` hid that.
   - **Dummy verb plus action noun is the disguised form.** An active-looking verb paired with a `-tion` / `-sion` / `-ment` noun passes a weak-verb check while saying the same nothing. _Tripwire:_ `performs`, `provides`, `conducts`, `initiates`, `facilitates`, `carries out`, `undertakes`, followed by an abstract noun.
   - **`names` is the literary form.** `the logger names the path`, `an error naming the flag`, `a row names its target` stand in for whatever the layer actually does. Pick the verb by layer: writing to a stream is `prints` / `writes` / `logs`; putting a value into a rendered string is `includes` / `formats` / `interpolates`; setting a key or field is `sets` / `identifies`; selecting a declared thing by its name is `selects` / `references`. The noun `name` is untouched by this — `the names as written` and `file_name` are both correct.
   - **Layer picks the verb; the verb then repeats.** Specificity resolves against the mechanism, never against a wish for variety, so two sites doing the same thing take the same verb and Law 3.7 keeps them identical. Rotating `logs` / `emits` / `prints` across one operation is the synonym-churn Law 4 bans. A codebase that already assigns one of these a meaning binds you to it: where `logs` is reserved for the logging framework and a separate printer owns user-facing output, the printer's sites cannot say `logs`.
   - _Reject:_ `The service performs validation of the token.`
   - _Apply:_ `The service validates the token.`
4. **Transaction verbs require physical objects:** Replace abstract possession verbs (`carries a state field`, `holds a lock`, `keeps its terminator`) with direct state descriptions (`has a state field`, `ends with a newline`, `is marked`).
   - **No possessive on the object either.** A possession verb smuggles in ownership that does not hold: a row does not own its newline, a cell does not own its padding, a path does not own its prefix. Write `alignment preserves every terminator`, not `alignment keeps every terminator`; write `the key cell ends with a colon`, not `the key keeps its trailing colon`. The negated forms take the same fix: `must not write past the cell`, not `must not keep its padding`.
5. **No ambiguous shorthand:** Brevity cuts filler, not technical nouns. Expand ambiguous shorthand (`both major versions`, not `both majors`; `configuration parameter`, not `the config`).
   - **An example must show a form or a transformation.** A concrete value earns its place where it shows something the prose cannot state as compactly — an unexpanded path (`e.g. ~/.config/app.toml`), or a mapping (`` a leading dot is dropped, so `.apprc` is stored as `apprc` ``). It does not earn its place where it merely re-instantiates a noun the sentence already named, which renames the referent mid-sentence and breaks rule 7.
   - _Reject:_ ``The file at `src` is preserved: until the next sync runs, `~/.config/app.toml` is still a regular file.`` — `~/.config/app.toml` is a second name for `src`, and the function is not specific to that file.
   - _Apply:_ ``The source file at `src` remains an untouched regular file until the next sync replaces it.``
6. **No tallies in prose:** Do not count the things you are about to list or point at (`fixes two things`, `four of the invariants`, `the three checks below`, `the two differ only in`). A tally is a second copy of a fact the list already carries, and it goes stale the moment anyone adds or removes an item. Name the items, or name the property they share.
   - _Reject:_ `Each variant fixes two things: the mode recorded, and which section the entry is written to.`
   - _Apply:_ `Each variant fixes the mode recorded and the section the entry is written to.`
   - **Positional references rot the same way.** `the first two arms`, `the second field`, `the remaining arm`, and `the three checks below` all break on the next insertion. Name the variant, field, or condition.
   - _Reject:_ `// The first two arms handle existing records. The remaining arm inserts a new row.`
   - _Apply:_ ``// Update the matched record on `Exact` and `Prefix`. Insert a new row on `NotFound`.``
   - _Exempt:_ a number that is itself the fact, not a count of prose (a benchmarked threshold, a protocol constant, an exit code, a byte width, a version major).
7. **Repeat the exact term:** Name the same identifier, component, or concept with the same words every time. Varying the wording across mentions is not style; in technical prose it reads as a second thing.
   - _Reject:_ a module table listing `version mismatch` while the variant it documents says `schema version mismatch`, and three spellings of one deprecation notice across four call sites.
   - _Apply:_ `schema version mismatch` at both sites; one spelling of the deprecation notice everywhere.
8. **Zero speculation:** Do not invent facts, unverified constants, or hypothetical behaviors. Unknowns remain unknown; verified facts, tool outputs, and inferences must remain distinct.
   - _Reject:_ `Every command's error document uses these keys.` — written while most commands did, and one keyed its subject `target` rather than `path`.
   - _Apply:_ `` `init` and `remove` emit the same error keys. `` Check each site before generalizing across them.
9. **Add the missing rationale:** Pruning alone leaves the most common documentation defect in place. Where a choice looks wrong and is right, where an ordering is required, or where a hazard is not visible from the signature, the reason is missing and belongs in the file. Report what you added.
   - _Before:_ `/// Discard an IO result.`
   - _After:_ `/// Discard an IO result. A broken stdout/stderr pipe must not abort the run.`

---

## Law 4: Diction & Rhetorical Traps

Apply this audit last, over prose that already satisfies the first three laws.

**This list is dated and incomplete by construction.** Its contents track a 2024 corpus of machine-written text; flagged words fall out of use once they are named, and unflagged ones take their place. Treat the list as a sample of a moving target. Clearing it proves nothing about Laws 1 through 3.

**Do not grow this list as maintenance.** Most of its entries are cached instances of Law 3.3 (use the verb the code executes) and Law 3.4 (transaction verbs require physical objects). `serves as`, `holds`, `carries`, `keeps`, `comes back`, `ends up` are one defect — reaching for a verb the mechanism does not perform — and the reading pass derives every one of them without a lookup. The list buys recall speed, not coverage. On finding a new tell, first check whether Law 3.3 or 3.4 already generates it; where it does, the entry is optional and adding it changes nothing. Only the _No exemption_ list is irreducibly lexical: register violations with no technical use, which no mechanical rule predicts.

**The enumerated categories live in `references/diction.md`.** Load that file at step 4, never before. It is the one part of this skill that can be mistaken for the audit, and holding it out of context until the structural laws have run is what stops a reading pass from collapsing into a word search.

_No exemption, and never generated in the first place:_ `delve`, `load-bearing`, `steelman` / `steelmanning`, `tapestry`, `showcasing`, `seamless`, `testament to`, `at its core` / `at its heart`, `sits at the intersection of`, `underscores the importance`, and the false-dichotomy frames. These have no legitimate technical use. This list stays here rather than in the reference file because it binds at generation time: the words must be absent when prose is written, not caught when it is reviewed.

---

## Read-Back Instruments

Steps 4 through 7 draw on this section. The tripwires are triage; the full-pass instruments below them are reads.

### Mechanical tripwires

**These do not constitute the audit.** They are fail-closed triage over text the reading pass has already covered, and clearing them proves nothing — most Law 1–3 defects have no lexical signature. A pass that runs only these has not run.

Each is fail-closed: **a match is a violation until you name the exemption that applies.** Naming it is a claim you can be wrong about, which is the point; a silent exemption is how a violation gets waved through.

1. **Trailing modifier.** Does a clause end in `, which …`, `, where it …`, or comma plus `-ing`? Exemption: the participle is the direct result of a condition you can name in the same sentence.
2. **Temporal inversion.** Does `after`, `once`, `following`, or `upon` sit later than the main verb? Exemption: none for a two-clause sentence; front-load it.
3. **Signature restatement.** Can the docstring be reproduced by substituting synonyms into the name, parameters, and return type? Exemption: it also states a constraint, hazard, or ordering.
4. **Dummy verb.** Any verb paired with a `-tion` / `-sion` / `-ment` / `-ance` noun that has a plain verb form — `performs validation`, `handles serialization`, `implements the transformation`, `provides configuration`. The carrier verb is incidental, so match the noun, not a list of verbs. Exemption: the noun is a named object rather than a nominalized verb (`executes the migration script`, `provides the TLS certificate`).
   - Also flag `names` / `naming` where the subject is code, output, or a document — the literary stand-in Law 3.3 covers. Exemptions: the noun `name` (`the names as written`, `file_name`), and the instruction sense addressed to a reader or auditor (`name the fact it carries`), which is a request to state something rather than a claim about behaviour.
5. **Deictic.** `from there`, `at that point`, `in that case`, or a bare `this` / `it` whose antecedent is not the previous sentence's subject? Exemption: the antecedent _is_ that subject.
6. **Bundling.** Do two unrelated operational rules share one sentence via `and`, `;`, or `:`? Exemption: the second clause is the first one's consequence.
7. **Displaced negation.** `[verb] no [noun]`, `[verb] nothing`, `[verb] neither … nor`, or a sentence opening `No [noun] [verb]s`? Exemption: `no-op`, `no longer`, and a stative verb that builds no expectation for the negation to cancel — `has no timeout`, `contains no timestamps`. Run Law 2's parse test on the verb before claiming this one.
8. **Tally or position.** Any count of listed items, or `the first`/`second`/`remaining` pointing at code? Exemption: the number is the fact (threshold, exit code, byte width).
9. **Missing subject.** Does the item open on a subordinate clause (`Before …`, `After …`, `Once …`, `Under …`, `Without …`, `Only …`, `To …`) and never reach a main clause? Exemption: a noun-phrase label whose next sentence carries the fact. Alone among these, this one fires on an absence, so it reads the opener instead of matching a phrase. A comment that states a real constraint is where the defect hides, because stating the constraint is what makes the fragment feel finished.
   - _Reject:_ `// Before any lock or mutation, so a missing-input refusal costs nothing.`
   - _Apply:_ `// Mode and module resolve before the lock and before any mutation, so a missing-input refusal costs nothing.`
10. **Narrating instead of stating.** Is a narrator commenting on the system rather than describing what it does? Every signature below is repaired the same way, by naming the component and its operation:
    - _Intensifier on a mechanism:_ `really`, `actually`, `genuinely`, `truly`, `simply`, `just`, `in fact`. A mechanism either happens or does not, so the intensifier adds emphasis where the reader wanted a fact. `a rejection message means the service really rejected the write` → `a rejection message reports a rejection the verifier observed`.
    - _Indefinite agent:_ `nobody`, `no one`, `anyone`, `someone`, `whoever`. These stand in for the component that did or did not act. `an apply whose outcome nobody observed` → `an apply whose verdict never arrived before the deadline`.
    - _Self-reference by the prose:_ `says exactly that`, `says so`, `says which`, `means just that`, `is the whole point`. The sentence describes its own adequacy instead of stating the fact. Delete the clause and state the fact.
    - _Staged absence:_ `share X but never Y`, `has X yet no Y`, `does A without ever B`. The contrast frames what is missing as a reveal. State the positive fact: `share one exit code` and `the error message is the only thing separating them` are two sentences, not one contrast.
    - _Comprehension verb on a consumer:_ `tells a script`, `a caller learns`, `the reader knows`, `a consumer sees`, `leaves the user wondering`. A field, code, or message has content; it does not inform an audience. Name the field and its value instead: ``the `result` field alone tells a script only that the run failed`` → ``the failing results share one exit code, so `result` is what separates them``.
    - Exemption: `just` as a quantity or time adverb (`just under 4 KiB`, `just-written file`), and `simply` inside a quoted user-facing string.
    - This tripwire fires on repairs more than on first drafts. The worked examples above were all written to fix a different defect in the same paragraph, and the comprehension-verb one was written into the fix for this very tripwire. Re-run this item over your own replacement text before accepting it.

### Full-pass instruments

Each is a read over the finished text, not a phrase match.

- **Semantic Advance:** Every sentence must move the reader's state with a new fact, constraint, or consequence. A sentence that re-describes its predecessor in different words gets deleted, not rephrased. Rewording in place is the characteristic machine failure: the vocabulary churns while the content stands still. On instruction text, a set of worked examples is exempt.
  - _Reject:_ `The cache is invalidated on every write. After a write the cached value is no longer used.`
  - _Apply:_ `The cache is invalidated on every write; a reader after a write always hits the backing store.`
- **Canonical Construction:** Read a run of consecutive sentences and check whether each resolves on the first structure a reader tries. Uniformly frictionless syntax is the signature of prose sitting at the model's mode, and it reads fast while leaving nothing behind. Where a run is uniform, apply the escape hatch to the weakest sentence. Skip this on instruction text.
  - _Reject (one frame, three times):_ `The writer emits the record. The encoder frames the payload. The sender flushes the socket.`
  - _Apply:_ vary the frame, not the words — `The writer emits the record. Each payload is framed before it is sent. Transmission ends with a socket flush.`
  - Three frames, three subjects, no connective doing the work: `therefore`, `thus`, and `hence` mark an inference the sentence order already carries.
- **Shape as Diagnostic, Not Target:** After the rewrite, look at sentence length and opening variety. Flat shape means the content did not vary, so return to Semantic Advance. Never manufacture variance directly; forced jitter and synonym-swapping both make the passage worse.
- **Single-Pass Check:** Read each comment and the associated code line once. If a second read is required to understand what noun a pronoun refers to or what condition applies, rewrite it.
  - _Reject:_ `Some content cannot be line-diffed: a binary source or target, or an unreadable file. It renders as a placeholder.` — `It` points at the list, not at a noun.
  - _Apply:_ `A binary source or target, or an unreadable file, renders as a placeholder instead of a line diff.`
- **Bi-Directional Fidelity:** Compare the rewrite against the original source. If a verified invariant or edge-case warning was dropped, restore it. If an unverified assertion was added, delete it.
  - _Reject:_ tightening `refuses up front with exit 1 before acquiring any lock or mutating anything` to `refuses with exit 1`. The ordering guarantee was the fact worth keeping.
- **Code Fidelity:** Read each surviving comment and docstring against the code it annotates. Where the prose contradicts the code, the prose is wrong until the code proves otherwise. Flag the contradiction rather than smoothing the wording over it. A faithful rewrite of a false comment is still false.
  - _Contradiction:_ `all findings go to stderr regardless of format`, where the `--json` branch writes its whole document to stdout.
  - _Reject (smoothed, still false):_ `every finding is written to stderr in both formats.`
  - _Apply (claim corrected):_ ``findings go to stderr in human mode; `--json` writes its entire document to stdout.``

---

## Re-Auditing Your Own Sentences

A repair lands at the same place the original did. It was written by the same process, under pressure to fill the space a deletion left, and no pass has judged it.

**Re-enter the procedure; do not run a shorter checklist.** Every sentence the audit wrote goes back through Laws 1, 2, and 3 in full, exactly as the source text did. The Invention and Abstraction checks below are _additional_, not a substitute — running only them is the characteristic way this step fails, because a repair's usual defects are ordinary Law 2 and Law 3 breaks that the writer was too close to see:

- A rewrite fixing a trailing participle that lands an inverted condition and a possession verb: `Both the refresh pass and the cleanup sweep write that file, so a run that must not write holds both back.`
- A rewrite fixing a false claim that joins two invariants with `and` and reaches for a motion verb: ``Stripping only one dot leaves `..` as `.`, and a name that is exactly `.` comes back unchanged.``

Each clears the Invention and Abstraction checks below. Neither survives Law 2. A repair that fails returns to Law 1, and its replacement returns to this section.

**A repair characteristically imports a violation of a law other than the one it fixes.** The writer's attention is on the defect they found, so the replacement satisfies that rule and breaks a different one: a fix for a case sweep arrives with a trailing participle, a fix for a possession verb arrives with a tally, a fix for a positional count arrives with `handles`. Checking the repair against only the rule that triggered it is therefore worthless. Run all three laws over every replacement, including replacements proposed by a reviewer.

Then check the same sentences for the failures the laws above do not catch:

- **Invention.** Redrafting rebuilds a sentence instead of editing it, and rebuilding is the one move in this procedure that can manufacture a claim. Ask whether the redraft states a fact, name, number, limit, or behavior the source does not. A fabrication is a defect even where it reads better than the text it replaced. Restore the original claim, or cut the sentence.
- **Abstraction handling.** A redraft with no fact left to state reaches for a verb of transaction. Run Law 3's transaction-verb rule over every sentence written here: point at the object, and where you cannot, name the plain verb for what the code does.

Record that this pass ran and what it found. Skipping it is how a repair ships the defect it was written to remove.

---

## Reporting

Report structural findings and diction findings under separate counts.

- **Structural** covers Laws 1 through 3, plus the Semantic Advance and Canonical Construction instruments. These are the durable signal.
- **Diction** covers Law 4. These decay and recur.

For each group, list items deleted, items rewritten, facts restored, rationale added, contradictions flagged, and code cleanups that removed the need for a comment. If a group had no findings, state that plainly.

Report these outcomes separately from the counts, since each records work the audit did on itself:

- The resolved scope, and for a named target, which of its files were absent from the diff and read anyway.
- The adversarial re-read: that it ran, what it found in already-passed text, and which files it sent back to step 1. A report claiming clean without it has not earned the claim.
- Deletions the over-cutting check restored, and the surviving site named for each deletion that stood.
- The re-audit pass over the audit's own sentences: that it ran, how many it re-audited, and what it found. A report omitting this has not run it.

The split is diagnostic. Structural findings near zero with diction findings accumulating means the generation-time voice is holding and only the decaying layer is slipping. Structural findings rising means the voice is no longer reaching the generator.
