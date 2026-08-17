# Read-back instruments (Law 4)

Load this at step 5 of the procedure, never before. Laws 1 through 3 run first, as a read over the full text, without it.

The tripwires below are triage; the full-pass instruments after them are reads. Both are held out of `SKILL.md` for the reason `references/diction.md` is: a list of matchable phrases sitting in context during the reading pass is what turns the read into a search.

---

## Mechanical tripwires

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

---

## Full-pass instruments

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
