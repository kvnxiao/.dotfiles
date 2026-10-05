# Diction Reference

Lookup data for the `audit-prose` diction lens: banned AI tells and plain-English substitutions.

## 1. Never Generate (Synthetic AI Tells)

Delete or rewrite these phrases. An entry with a stated sense applies only in that sense:

`delve` · `load-bearing` · `seam` / `seams` (as a metaphor) · `steelman` / `steelmanning` · `tapestry` · `showcasing` · `seamless` · `testament to` · `at its core` / `at its heart` · `sits at the intersection of` · `underscores the importance` · `it's not just X, it's Y` / `less about X than about Y` · `plethora` · `crucial` / `pivotal` · `leverage` (as a verb) · `fostering` · `unpacks` (meaning explains) · `interrogates` (meaning examines)

Cut every false profundity, thesis-framing formula, synthetic contrast formula, and superlative justification. Cut a figure of speech when a literal phrase of similar length says the same thing. Established technical terms stay: words the field uses as the name of a mechanism in APIs, commands, or reference docs, such as `pipeline`, `handshake`, `heap`, `fork`, `sandbox`, and `deadlock`. State what the change does and stop.

## 2. Diction Upgrades: Natural Programmer English

Replace stiff, formal, or Latinate substitutes with everyday, natural words **when the meaning is equivalent**:

| Avoid (Stiff / Compliance Slop)                              | Prefer (Plain & Natural)                             | Context / Condition                                                          |
| :----------------------------------------------------------- | :--------------------------------------------------- | :--------------------------------------------------------------------------- |
| `contains no` (where simpler), `holds no`                    | `has no`                                             | Checking absence or count (keep `contains` for set/string membership)        |
| `holds [content]`, `carries [content]`                       | `has`, `stores`, `records`                           | A file, record, or change with content (keep variable and lock idiom)        |
| `names on stderr`                                            | `prints to stderr`, `outputs to X`                   | Emitting diagnostic or log lines                                             |
| `is newer in timestamp order than`                           | `is newer than`                                      | Strictly when comparing timestamps/dates                                     |
| `leaves X untouched`, `leaves X alone`, `leaves X unchanged` | `does not modify X`, `X is untouched`, `skips X`     | Negate at the verb; use `skips` only when the operation bypasses X           |
| `does not change any target other than X`                    | `only changes X`                                     | Restrictive scope without double-negative evasion                            |
| `opens no connection`                                        | `does not open a connection`                         | Rewrite `verb no noun` as `does not verb noun`; keep `has no`, `there is no` |
| `does not return rows` (for an empty result)                 | `returns no rows`                                    | The zero quantity is the result; keep `verb no noun`                         |
| `makes no modifications to`                                  | `does not modify`                                    | Negated light-verb nominalization                                            |
| `provides configuration for`                                 | `configures`                                         | Avoiding light-verb nominalizations                                          |
| `performs validation on`                                     | `validates`                                          | Avoiding light-verb nominalizations                                          |
| `a scenario in which the command fails`                      | `when the command fails`                             | Avoiding clumsy prepositional relative clauses                               |
| `reverses the transaction that the latest record describes`  | `reverses the latest transaction`                    | Clear referent without pedantic clutter                                      |
| `the smallest edit that X, and it Y`                         | What the option changes (`only changes three lines`) | Justifying a recommendation                                                  |
