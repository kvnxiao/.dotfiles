# Diction Reference

This reference catalogs high-signal AI tells, corporate fluff, and unnatural diction patterns. Use
these entries as review signals to strip machine tells and restore direct, natural English.

> **Semantic fidelity always overrides diction upgrades.** A substitution applies only when it
> preserves the exact verified meaning in context. If existing text is already clear, direct, and
> technically accurate, leave it alone. Preserve deliberately bad or non-conforming prose in quoted
> examples, test fixtures, and anti-pattern documentation.

## 1. Never Generate (Synthetic AI Tells)

These phrases have no legitimate use in technical engineering prose. Delete or rewrite them
directly:

`delve` · `load-bearing` · `seam` / `seams` · `steelman` / `steelmanning` · `tapestry` ·
`showcasing` · `seamless` · `testament to` · `at its core` / `at its heart` ·
`sits at the intersection of` · `underscores the importance` · `it's not just X, it's Y` /
`less about X than about Y` · `plethora` · `crucial` / `pivotal` · `leverage` (as a verb) ·
`fostering` · `unpacks` · `interrogates`

## 2. Diction Upgrades: Natural Programmer English

Replace stiff, formal, or Latinate substitutes with everyday, natural words **when the meaning is
equivalent**:

| Avoid (Stiff / Compliance Slop)                             | Prefer (Plain & Natural)             | Context / Condition                                                   |
| :---------------------------------------------------------- | :----------------------------------- | :-------------------------------------------------------------------- |
| `contains no` (where simpler), `holds no`                   | `has no`                             | Checking absence or count (keep `contains` for set/string membership) |
| `holds [data/file/record]`, `holding`                       | `has`, `stores`, `records`           | Inanimate data entities (reserve `holds` for mutexes/locks)           |
| `names on stderr`                                           | `prints to stderr`, `outputs to X`   | Emitting diagnostic or log lines                                      |
| `is newer in timestamp order than`                          | `is newer than`                      | Strictly when comparing timestamps/dates                              |
| `leaves untouched`, `leaves alone`                          | `skips`                              | When the operation bypasses the item completely                       |
| `leaves untouched`, `leaves alone`, `leaves unchanged`      | `does not modify`, `does not change` | When the item is inspected, validated, or read without mutation       |
| `does not change any target other than X`                   | `only changes X`                     | Restrictive scope without double-negative evasion                     |
| `provides configuration for`                                | `configures`                         | Avoiding light-verb nominalizations                                   |
| `performs validation on`                                    | `validates`                          | Avoiding light-verb nominalizations                                   |
| `a scenario in which the command fails`                     | `when the command fails`             | Avoiding clumsy prepositional relative clauses                        |
| `reverses the transaction that the latest record describes` | `reverses the latest transaction`    | Clear referent without pedantic clutter                               |

## 3. Grammar Anti-Patterns

- **No Verbing Nouns:** Reject coining verbs from nouns (`actioning`, `architecting`,
  `transitioning` when `moving` applies, `impact` as a verb when `affect` applies).
- **No Anthropomorphic Intent or Inanimate Possession:** Code, files, tests, and data structures
  have no emotions, will, or hands. Reject `code wants`, `test decides`, `file prefers`,
  `build earns its
  keep`, and `the directory/struct holds X`. Use plain verbs (`has`, `stores`,
  `records`, `needs`, `requires`). Reserve `holds` strictly for synchronization locks
  (`holds the mutex`) or logical invariants (`the property holds`).
- **No Causal Padding:** Cut trailing participial appendages (`..., ensuring that`,
  `..., thereby preventing`). State the consequence directly with a coordinating verb or separate
  sentence.
- **No Conversational Preamble:** Cut `Basically`, `Note that`, `Here is what you need to know`, and
  `The reality is`. State the fact and stop.
- **No Provenance or Grievance:** Cut historical commentary (`added after outage`,
  `historically this was`, `workaround for upstream bug`). State the current constraint directly.
