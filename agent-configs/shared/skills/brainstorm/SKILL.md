---
name: brainstorm
description: Brainstorm collaboratively to develop ideas or settle open product and implementation decisions. Use when the user asks to brainstorm or explore options. Also use for explicitly open or deferred decisions, even when other decisions are settled or choices are reversible, and for materially different interpretations where the wrong choice is costly to reverse.
---

Develop the idea or settle open decisions with the user until you reach a shared understanding. Map the open decisions as a **design tree**: every decision branches into the decisions that depend on it.

Before implementation, read the full request and relevant context, regardless of length. Include any referenced issue or plan and its relevant discussion. Keep settled decisions as constraints and ask only about unresolved details. Resolve factual unknowns through read-only investigation before asking the user to make decisions.

If the initial investigation confirms that all decisions were already settled, continue the authorized work without inventing questions.

Work the tree in **rounds**. The **frontier** is every decision you can present to the user now without guessing. A decision waiting on an open question stays off the frontier. Ask the whole frontier in one round. Offer 2–4 genuinely different options with their trade-offs, and mark your recommendation. Make at least one option unconventional. Then wait for the user's answers.

Number questions in one consecutive sequence across the entire conversation, starting at 1. Assign each new question the next unused number, including follow-up questions. Never restart numbering when the frontier changes or a new round begins. For example, after questions 1–3, number the next frontier's questions 4–6. Keep the original numbers when referring to earlier questions. Preserve the highest issued number in continuation summaries and resume from the next number.

Start every round, including the first, with a brief summary before the questions:

- State what this round focuses on and what its questions will decide.
- Connect the questions to the user's goal and relevant settled decisions, explaining why they come next.
- Name the priorities and constraints guiding the recommendations, including the main trade-off they favor.

Distinguish settled constraints from priorities you are proposing. When the frontier spans unrelated topics, name those topics without forcing a shared focus.

Keep shared reasoning in the round summary. State each question directly. For an unusual or complex decision, explain the relevant context before the options. Use connected paragraphs, a concrete example, or a small diagram when it helps explain the consequences. Make relevant assumptions and uncertainty explicit. Vary the depth with the decision, including within option descriptions; keep straightforward choices brief and avoid repeating context already explained.

Put each option's benefit and cost in clear, complete sentences beneath its bold label. Always put the recommended option first and mark it `(Recommended)`. Put ➡️ after its option letter and before its title so all option letters align. Explain why it fits the round's priorities in its description. Add a separate recommendation sentence only when it contributes reasoning not already stated.

Format options as one Markdown bulleted list with a blank line before the list and between items. Use a hard line break after each bold option label. Indent every continuation line and additional paragraph by two spaces to keep the explanation inside its list item. Use list indentation instead of tabs or padding characters for alignment. Format each round like this, repeating question and option blocks as needed:

```markdown
**Round <R> focus:** <what this round will decide and why it comes next> <priorities and constraints guiding the recommendations, and the main trade-off>

❓ **<N>. <question>**

<optional explanation, example, or diagram needed to understand this decision; omit when unnecessary>

- **A. ➡️ <recommended option> (Recommended).**\
  <why this choice fits the round's priorities and its main cost>

- **B. <alternative option>.**\
  <benefit and cost>

- **C. <alternative option>.**\
  <benefit and cost>
```

Diverge before you converge: widen the option space instead of defending each recommendation. Once the user picks a direction, build on top of that to generate the next options _inside_ it.

Each round of answers reshapes the tree. The decisions picked may push the frontier outward and unblock questions that depended on them, or close questions that are no longer relevant. Recompute the frontier, then ask the next round. A question whose answer depends on another open question is deferred to a _later_ round, not the current one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, web search, installed tools), dispatch a sub-agent rather than asking the user. Always wait for the sub-agent to finish before asking the rest of the frontier in the current round, as the exploration may reveal information that affects the option space and recommendations. The _decisions_ are always the user's - put each to them and wait.

The session is done when the frontier is empty with every open branch of the design tree visited and nothing left silently assumed. Close by writing up the settled tree as a concise summary the user can act on. Do not act on it until the user confirms you have reached a shared understanding.
