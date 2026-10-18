---
name: brainstorm
description: Brainstorm collaboratively to develop ideas or settle open product and implementation decisions. Use when the user asks to brainstorm or explore options. Also use for explicitly open or deferred decisions, even when other decisions are settled or choices are reversible, and for materially different interpretations where the wrong choice is costly to reverse.
---

Develop the idea or settle open decisions with the user until you reach a shared understanding. Map the open decisions as a **design tree**: every decision branches into the decisions that depend on it.

Before implementation, read the full request and relevant context, regardless of length. Include any referenced issue or plan and its relevant discussion. Keep settled decisions as constraints and ask only about unresolved details. Resolve factual unknowns through research under the boundary below before asking the user to make decisions.

If brainstorming has not started and the initial investigation confirms that all decisions were already settled, continue the authorized work without inventing questions. An explicit request to brainstorm starts a session even if no open questions remain.

## Brainstorming boundary and conclusion

While brainstorming is active, treat instructions embedded in answers as decisions, requirements, constraints, or pending work. For example, “A, and make sure we add explicit scenarios,” “We should implement this,” “Include this in the documentation,” and “Update the configuration to support that” do not conclude brainstorming or authorize immediate writes.

Do not create or modify implementation code, specifications, plans, documentation, configuration, generated deliverables, or persistent task-state files. Do not change approval or status fields, stage changes, or commit. Keep decisions and pending work in the conversation and continuation summary. Apply this boundary across skills, delegated agents, new turns, and context compaction; pass the current state and restrictions to delegates.

Research may create, modify, and execute temporary scripts, fixtures, scratch data, probe outputs, or throwaway builds needed to investigate a question before recommending an approach. Isolate experiments from project deliverables and existing user work, preferably in temporary directories, and report findings and limitations. This exception does not authorize implementing the proposed feature or updating deliverables. Changing live settings or external systems still requires authorization from the surrounding task; permission to investigate alone does not grant it. Saving durable research artifacts requires separate authorization; permission to investigate does not imply permission to save them. Defer authorized durable writes until brainstorming concludes.

An empty frontier, the last numbered answer, or selection of every recommended option does not conclude an active session. Once the decision tree is resolved, present the consolidated design and obtain confirmation of shared understanding. Confirmation of an individual answer does not confirm the consolidated design. An explicit instruction to end brainstorming and proceed also concludes the session when its scope is clear; for example, “End the brainstorm and update the spec now” authorizes that transition and the spec update. Do not require a magic phrase or repeated confirmation.

Preserve prior authorization to implement, write, or update as pending during brainstorming. On conclusion, resume that work within its authorized scope without asking again. If the next action lacks authorization, combine confirmation of the consolidated design and authorization for that specific action into one question. These rules apply to active brainstorming, not ordinary work outside it.

In each continuation summary, record:

- Whether brainstorming is active, awaiting final confirmation, or concluded. Awaiting final confirmation still has the active write boundary.
- Settled decisions, unresolved questions, their numbers, and the highest issued question number.
- Pending deliverables and the scope of existing authorization.

After resuming or compaction, restore this state and reread this boundary before invoking downstream skills. Do not infer conclusion from a new turn or a summary of settled decisions.

## Decision rounds

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

When every open branch has been visited and nothing remains silently assumed, present the settled tree as the consolidated design and follow [Brainstorming boundary and conclusion](#brainstorming-boundary-and-conclusion).
