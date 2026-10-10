# Diction Reference

Lookup data for the `audit-prose` diction and literal-over-rhetorical lenses: banned AI tells, plain-English substitutions, and rhetorical patterns.

## 1. Never Generate (Synthetic AI Tells)

Delete or rewrite these phrases. An entry with a stated sense applies only in that sense:

`delve` · `load-bearing` · `seam` / `seams` (as a metaphor) · `steelman` / `steelmanning` · `tapestry` · `showcasing` · `seamless` · `testament to` · `at its core` / `at its heart` · `sits at the intersection of` · `underscores the importance` · `it's not just X, it's Y` / `less about X than about Y` · `plethora` · `crucial` / `pivotal` · `leverage` (as a verb) · `fostering` · `unpacks` (meaning explains) · `interrogates` (meaning examines)

Cut every false profundity (a sentence that sounds deep but states nothing), thesis-framing opener (`The key insight is`), and superlative justification. Contrasts other than the listed formulas fall under the Literal Over Rhetorical lens. A trailing clause that justifies a step with an absence (`the migration drops the column, which no code reads`) is a tell: state the cause first (`Because no code reads the column, the migration drops it`) or drop the justification. Do not repair it by joining the clauses with `and` (`no code reads the column, and the migration drops it`). State what the change does and stop. The Literal Over Rhetorical lens covers figures of speech; section 3 lists examples.

## 2. Diction Upgrades: Natural Programmer English

Replace stiff, formal, or Latinate substitutes with everyday, natural words **when the meaning is equivalent**:

| Avoid (Stiff or Bureaucratic)                                | Prefer (Plain & Natural)                             | Context / Condition                                                          |
| :----------------------------------------------------------- | :--------------------------------------------------- | :--------------------------------------------------------------------------- |
| `contains no` (where simpler), `holds no`                    | `has no`                                             | Checking absence or count (keep `contains` for set/string membership)        |
| `holds [content]`, `carries [content]`, `gains [content]`    | `has`, `stores`, `records`; `the migration adds`     | A file, record, or change with content (keep variable and lock idiom)        |
| `lives in [path]`                                            | `is stored in`, `is in`                              | A file or setting at a location                                              |
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
| `reverses the transaction that the record describes`         | `reverses the recorded transaction`                  | Clear referent without pedantic clutter                                      |
| `the smallest edit that X, and it Y`                         | What the option changes (`only changes three lines`) | Justifying a recommendation                                                  |

## 3. Rhetorical Patterns: Literal Over Rhetorical

Each row fails the named test, which belongs to the Literal Over Rhetorical lens unless the row names lens 1. The rewrites assume the writer knows the facts they add; an auditor without those facts asks for them.

| Pattern                        | Test                                | Reject                                         | Apply                                                                                       |
| :----------------------------- | :---------------------------------- | :--------------------------------------------- | :------------------------------------------------------------------------------------------ |
| Effect named instead of action | Effect Without Action               | `Uploads that never get lost`                  | `Retry failed uploads once`                                                                 |
| Mechanism without behavior     | Effect Without Action               | `Writes obey the lock`                         | `Each write waits for the table lock`                                                       |
| Evaluative title               | Judging or Teasing Label            | `Easy wins`                                    | `Cache dependencies and remove the unused lint step`                                        |
| Teaser title                   | Judging or Teasing Label            | `Where the bytes go`                           | `Storage use by table`                                                                      |
| Context-dependent heading      | Context-Dependent Heading or Opener | `Why it matters`                               | `Why uploads retry only once`                                                               |
| Wordplay                       | Figure of Speech                    | `the safe bet is to stop betting on the cache` | `the fix is to read from the database when the cache misses`                                |
| Contrast for effect            | Figure of Speech                    | `a timeout costs a retry instead of a page`    | `a timeout retries the request and does not page the on-call engineer`                      |
| Personification                | Lens 1: No Inanimate Intent         | `the queue forgets stale jobs`                 | `the queue drops jobs older than one hour`                                                  |
| Figurative verb                | Figure of Speech                    | `batching first buries the regression`         | `if batching ships before profiling, the benchmark cannot show which change slowed queries` |
| Metaphor as a name             | Figure of Speech                    | `the heavy lifter`                             | `the job that does the most work`                                                           |
| Undefined nickname             | Undefined Shorthand                 | `the short loop`                               | `the edit, build, and test loop`                                                            |
| Undefined qualifier            | Undefined Shorthand                 | `a valid existing record`                      | `a record that passed schema validation`                                                    |
| Elliptical stand-in            | Undefined Shorthand                 | `a project with none`                          | `a project with no members`                                                                 |
| Narrow-specialty jargon        | Audience Jargon                     | `NRE cost`                                     | `one-time engineering cost`                                                                 |
| In-house status word           | Audience Jargon                     | `Parked`                                       | `Postponed`                                                                                 |
