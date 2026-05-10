---
name: humanize-as-kevin-xiao
version: 1.0.0
description: |
  Rewrite AI-generated prose to match Kevin's own writing voice for software
  engineering blog posts. Use when Kevin says "myself-ize this", "make this
  sound like me", "rewrite in my voice", or after drafting prose for his blog.
  Distinct from the general `humanizer` skill: this one targets Kevin's
  specific cadence (methodical, trade-off-aware, Canadian/British spelling,
  no em-dashes, criteria-first reasoning, concession-then-claim structure)
  rather than generic AI-tell removal. Transforms voice/rhythm/vocabulary;
  does NOT change technical claims or restructure argument order.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
---

# Humanize as Kevin Xiao

Rewrite the supplied prose so it reads as something Kevin Xiao would have written. Preserve the technical content, argument structure, and section ordering. Transform voice, sentence rhythm, vocabulary, and remove AI-tells.

## Inputs

The user will supply a block of prose (usually AI-generated, sometimes hand-drafted). Treat it as the source draft.

If the user has not specified what register they want, ask once: is this for a **blog post** (semi-formal, first-person OK), an **engineering report / RFC** (formal, structured), or **casual prose** (looser, contractions OK)? The default is blog post — only ask if the source register is ambiguous.

## Process

### 1. Strip AI-tells (mechanical pass)

Do this first, before any voice work. These patterns are dead giveaways and the user does not write this way:

- **Replace every em-dash (—).** Use parentheses, commas, semicolons, or restructure into two sentences. The user does not use em-dashes in any document in the corpus. This alone removes the strongest AI signal.
- **Remove "It's not just X — it's Y" / "not merely X but Y" / "X transcends Y" rhetorical inversions.** Restate as a direct claim.
- **Remove "Here's the thing:" / "But here's the kicker:" / "The reality is:"** — punchy openers absent from the user's writing.
- **Remove single-sentence paragraphs used for emphasis.** Either fold them into the previous paragraph or expand them into a full paragraph.
- **Cut AI vocabulary**: delve, tapestry, navigate the complexities of, in today's fast-paced world, at the end of the day, journey (as metaphor), unlock, unleash, harness the power of, game-changer, paradigm shift, robust ecosystem, seamless integration (unless literally describing a seamless integration), revolutionize.
- **Cut "In summary," / "To wrap up," / "In conclusion," as transition phrases.** The user closes with substance, not signposting.
- **Cut listicle structure** (numbered three-word bullets, headings every two paragraphs). The user writes long paragraphs; if a list is genuinely the right shape, items should be full clauses.

### 2. Adjust sentence rhythm

The user's natural sentences are medium-to-long with embedded clauses, not punchy and short. AI prose tends toward staccato. Lengthen by:

- **Combining short consecutive sentences with subordinating connectives.** "X is fast. Y is slow." → "While X is fast, Y is slow due to its dependency on Z."
- **Adding adverbial transitions where the logical flow calls for one.** Pick from the user's high-frequency set: Effectively, Essentially, Evidently, Eventually, Ironically, Naturally, Distinctly, Likewise, Similarly, Consequently, Subsequently, Conversely, Correspondingly, Resultantly, Unfortunately, Luckily, Regardless, Nevertheless, Ultimately. Use them to mark the logical move (consequence vs. concession vs. restatement) — not as filler. Don't overdo it; one per two-to-three paragraphs in casual prose, more in formal contexts.
- **Adding embedded relative clauses.** Where the source has a bare noun phrase, consider a parenthetical-style qualification: "Cassandra would..." → "Cassandra, which is a NoSQL database known for high availability, would..."

### 3. Apply signature constructions

Where the rewrite naturally allows, fold in moves the user actually makes:

- **Concession-then-claim**: "While X may be [easier/faster/cheaper], Y offers [the more important property]." This is a signature paragraph move — use it once or twice per piece if the content supports it.
- **"With X being Y..."** to chain context into the next claim.
- **"It should be noted that..." / "It is important to note that..."** for hedged-but-load-bearing observations. Use sparingly — once or twice per piece.
- **"An ideal X would..."** when stating what the best-case outcome looks like.
- **Triadic enumerations** (three adjectives, three nouns) where the source has two or four. "scalable, timely, and configurable", not "scalable and configurable" or "scalable, timely, configurable, and maintainable".
- **Topic-first sentences** for paragraph openers: "The X service is responsible for...", "X is a Y company that..." Avoid leading with subordinate clauses or "While..." for paragraph openers (use those mid-paragraph).

### 4. Vocabulary swaps

Apply Canadian/British spelling and Latinate vocabulary:

| Replace                     | With                        |
| --------------------------- | --------------------------- |
| utilize, utilizes, utilized | utilise, utilises, utilised |
| favor, favorable            | favour, favourable          |
| behavior                    | behaviour                   |
| analyze, analyzed           | analyse, analysed           |
| -ize endings (most)         | -ise                        |
| labor, honor, rumor         | labour, honour, rumour      |
| use (formal)                | utilise                     |
| get (formal)                | obtain                      |
| then (logical)              | subsequently                |
| so (logical)                | consequently                |
| also                        | in addition                 |
| but (formal)                | however                     |
| also worth noting           | it should also be noted     |

The Latinate swaps are register-dependent — keep "use" and "get" in casual contexts; lean Latinate for formal blog posts and reports.

Words/phrases the user's writing actively contains and you can re-introduce: thereby, thereafter, hereby, non-trivial, non-ideal, aforementioned, evidently, effectively, consequently, ultimately, naturally, ironically.

### 5. Trade-off check

Scan every claim. If a positive assertion stands alone with no acknowledgment of cost or limit, add one. The user almost never makes an unqualified positive claim. Patterns to add:

- "...at the expense of [X]."
- "...this is at the expense of..."
- "While [chosen approach] may be [more difficult / more expensive], it offers..."
- "...although this is not without [X]."
- "However, [acknowledgment of limit]."

### 6. Structural check

For longer pieces, verify the skeleton matches the user's natural structure:

- **Opening grounds the topic** in a system, company, project, or concrete problem — not in an abstract claim.
- **Body develops one point per paragraph** with topic sentence → context → evidence → analysis → tie-back.
- **Criteria are named** when alternatives are evaluated. Don't say "Option A is better" without saying "better according to what".
- **Close projects forward** with implications, recommendations, or open questions — not a summary.

If the source draft has a "TL;DR" or "Summary" or "Conclusion: as we saw above..." block, consider rewriting it into a forward-looking close ("Recommendations" / "Where to go from here" / "What this means in practice").

### 7. Punctuation discipline

- No em-dashes (already covered, but verify).
- Semicolons OK for extending a thought.
- Parentheses OK for asides — the user uses them liberally with "e.g.,", "i.e.,", and short clarifications.
- No dashes between clauses for emphasis. Restructure to comma + adverbial connector.
- Default to no contractions in formal prose (do not, is not, cannot). Casual technical prose can use contractions.

### 8. Final pass — read the output as if you wrote it

Read the rewritten draft straight through. Ask:

- Does any sentence feel "performative" or punchy in a way the corpus doesn't support? Flatten it.
- Is there a paragraph that feels short and snappy? Lengthen it with the development pattern (topic → context → evidence → analysis → tie-back).
- Are there too many adverbial transitions? More than one per paragraph in casual prose feels stilted. Trim.
- Does the close end on a forward-looking note?

## Output format

Return:

1. **The rewritten prose** as the primary output.
2. **A short "what changed" note** — three to five bullet points naming the specific transformations applied (e.g., "Removed 4 em-dashes", "Restructured the close from summary to recommendations", "Swapped utilize→utilise throughout"). This helps the user calibrate trust in the rewrite and learn the pattern.

Do not return the original alongside the rewrite unless the user asks for a diff view.

## When NOT to apply this skill

- **Code comments and inline docstrings** — the user's coding style is terse, not literary. Defer to coding conventions.
- **Slack messages, casual chat, commit messages** — the corpus is long-form prose; short-form has a different register.
- **When the source is already clearly the user's voice** — verify by checking for em-dashes and listicle structure first. If the source already lacks AI-tells and matches the cadence, return it largely unchanged with a note saying so.
- **When technical accuracy is uncertain** — this skill transforms voice, not facts. If the rewrite would require restating a technical claim and you're unsure of the underlying truth, flag the sentence and ask before changing.

## Reference: voice signatures (high-confidence)

These are patterns lifted directly from the corpus. Reading them aloud calibrates the target voice:

> "From further investigations into the first solution, it was evident that this solution would be the fastest approach to getting [X] into a completed product. ... However, when considering the most important criterion valued by the team, this solution could potentially be the worst in terms of [scalability/maintenance]."

> "The main issue with this approach is that it is a risky choice to go with from the start since [the dependency] is still in development. ... Hence, it is very probable that if this approach was used, then the [outcome] will suffer."

> "While [chosen path] may be more difficult to implement, the benefits this solution provides far outweigh the implementation difficulties in the long run."

> "In the broader scheme of things, I hope to have helped [team/company] construct a robust, reliable, and performant product."

> "It is evident that those who attempted to defy [the system] lead to chaos, and as a result were met with [consequence]."

> "Effectively, X. Consequently, Y. Subsequently, Z."

The flatness and methodical-ness is the point. Don't try to make it sing; make it walk steadily.
