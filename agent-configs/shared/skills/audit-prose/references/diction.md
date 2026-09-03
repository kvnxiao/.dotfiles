# Diction reference

After semantic fidelity, artifact convention, and discourse structure hold, load this reference. The entries are review signals, not a specification. If a match is the precise literal or technical term, it may remain.

This file is the sole authority for the skill's lexical tokens. `SKILL.md` carries procedure and discourse rules and names no words of its own, so a token added or retired here takes effect everywhere without a second edit.

## Never generate

These expressions have no legitimate technical use. Never write one into new prose. Encountering one in existing prose is a tripwire like any other: correct it where it carries no verified sense, and record a keep-reason where the surrounding artifact demands it.

`delve` · `load-bearing` · `steelman` / `steelmanning` · `tapestry` · `showcasing` · `seamless` · `testament to` · `at its core` / `at its heart` · `sits at the intersection of` · `underscores the importance` · false-dichotomy formulas such as `it is not just X, it is Y` or `less about X than about Y`

## Review categories

- **Structural and tactile metaphors:** Replace figurative `load-bearing`, `scaffolding`, `texture` or `adds texture`, `tapestry`, `throughline`, `linchpin`, `bedrock`, and `fractal` with the concrete relation.
- **Manufactured profundity and hype:** Unless the term is literal and verified, remove `delve`, `robust`, `seamless`, `leverage`, `nuance` or `nuanced`, `salient`, `poignant`, `elegant`, `compelling`, `trenchant`, `visceral`, `testament to`, `pivotal`, `crucial`, `underscores the importance`, `intricate`, `meticulous` or `meticulously`, `realm`, `encompassing`, `comprehensive`, `innovative`, `garnered`, `boasts`, and `aligns with`.
- **Thesis framing and debate posture:** Delete `At its core`, `At its heart`, `Crucially`, `It is worth noting that`, `The key insight here is`, `Sits at the intersection of`, `Speaks to [a broader pattern]`, `Fundamentally`, `Notably`, `steelman`, and `steelmanning`. State the claim or counterargument directly.
- **False dichotomies:** State the actual contrast instead of `It is not just X, it is Y` or `Less about X than about Y`.
- **Decorative triads:** If a member of a three-part sequence adds no fact, delete it.
- **Academic dynamic verbs:** Name the actual operation instead of using metaphorical `interrogate`, `unpack`, `illuminate`, `crystallize`, `resonate`, or `grapple with`.
- **Padding participles:** If `ensuring`, `highlighting`, `fostering`, `indicating`, `showcasing`, `emphasizing`, or `demonstrating` appends an unstated rationale or consequence, split or rewrite the clause.
- **Copula avoidance:** If `is`, `contains`, `is marked`, `preserves`, `executes`, or `reports success` states the fact more directly, use it instead of `serves as`, `stands as`, `represents`, `functions as`, `holds`, `carries`, `keeps`, `lives in`, `sits in`, `gains`, `admits`, `keeps acting as`, or `claims a success`. Review possession applied to data state: `keeps its rows`, `a workspace that has one keeps it`, `they hold a profile`. For current state, prefer `is null`, `is unchanged`, `remains`, or `they have a profile`. For a historical invariant such as `has never held a value`, preserve the time scope with an action predicate such as `no writer has ever stored a value`. Sweep a diff for these matches as a set and sweep each replacement too. A recurring shape prompts review but may remain when every use is precise.
- **Motion applied to static state:** If no motion occurs, replace `comes back unchanged`, `ends up empty`, and `comes out plain` with `is preserved`, `is empty`, or `is plain`.
- **Anthropomorphic verbs in mechanical contexts:** A dependency graph, file format, build gate, or test harness has no intent. Review `arrives`, `earns`, `wants`, `knows`, `decides`, `chooses`, and `agrees` when one of them is the subject. Prefer `the logging library is linked unconditionally` over `the logging library arrives unconditionally`, and `the format is tested on every host` over `the format earns a cross-platform test`. Keep the verb where a component performs the act literally, such as a server refusing a fetch or a scanner rejecting a write. Review the transfer verbs on the same test, since an API, format, or build tool bestows nothing on a caller: `hands`, `gives`, `offers`, `grants`, and `affords`. Name the operation the mechanism performs: `the spawn call does not return a process handle`, not `the spawn call hands the caller no process handle`. That sentence carries a displaced negation as well, so swapping `hands` for `returns` repairs only half of it; see the displaced-negation tripwire in `references/instruments.md`.
- **Unneeded emphasis:** If the plain tense carries the fact, remove `did bump`, `does hold`, `is in fact`, and a reflexive or possessive intensifier such as `itself` or `its own`. If emphasis establishes a contrast the reader could otherwise miss, keep it.
- **Conversational preambles:** If `Basically`, `Note that`, `Let's dive in`, `Here's what you need to know`, or `The reality is` delays the claim, remove it.
- **Unsupported case sweeps:** Verify the paths covered by `whichever`, `whatever`, `no matter how`, `regardless of`, and `in every case`. If the authority supports the sweep, keep it.
- **Open-ended list tails:** `and other X`, `and similar`, `and more`, `etc.`, and `such as ... and others` close a list with nothing the reader can check. Name the members or state the class. If the source asserts unnamed members whose identities cannot be verified, flag the claim instead of narrowing its scope.
- **Compliance verbs:** `obeys`, `respects`, `honors`, `follows`, `adheres to`, and `is subject to` before a mechanism name assert conformance without behavior. State the operation and any failure or effect that defines conformance.
- **Rule-standing adjectives:** `valid`, `proper`, `appropriate`, `applicable`, `correct`, `relevant`, and `existing` on a noun with no stated criterion defer the rule to the reader. State the criterion or delete the adjective.
- **Elliptical substitutes:** `with none`, `has one`, `the same`, and `such` standing for a noun from an earlier sentence. Repeat the noun.
- **Antithesis slogans:** A mirrored pair such as `X records what changed; Y records what happened` or `X is the how, Y is the what` is a slogan. Replace it with the concrete distinction between the components. If they write records, name each record and its write condition.

Do not replace a flagged word with a decorative synonym. Rebuild the sentence around its verified claim and the mechanism's direct verb.
