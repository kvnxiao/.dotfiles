---
name: brainstorm
description: Brainstorm collaboratively with the user to develop an idea, plan, or design from scratch. Use when the user wants to explore options, ideate, or uses any 'brainstorm' trigger phrases (e.g. "let's brainstorm").
---

Develop the idea with the user until you reach a shared understanding. Map it as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision you can present to the user now without guessing. A decision waiting on an open question stays off the frontier. Ask the whole frontier in one round. Number each question, offer 2–4 genuinely different options with their trade-offs, and mark your recommendation. Make at least one option unconventional. Then wait for the user's answers.

Format each question like this:

```
  ❓ **1.** - **<question title>**: <question body, might be multiple paragraphs, laying out the candidate options and their trade-offs>

     A. <option 1>
     B. <option 2>
     C. <option 3>
     ... (more options, if needed)

  ➡️ <your recommended option and why>
```

Diverge before you converge: widen the option space instead of defending each recommendation. Once the user picks a direction, build on top of that to generate the next options _inside_ it.

Each round of answers reshapes the tree. The decisions picked may push the frontier outward and unblock questions that depended on them, or close questions that are no longer relevant. Recompute the frontier, then ask the next round. A question whose answer depends on another open question is deferred to a _later_ round, not the current one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, web search, installed tools), dispatch a sub-agent rather than asking the user. Always wait for the sub-agent to finish before asking the rest of the frontier in the current round, as the exploration may reveal information that affects the option space and recommendations. The _decisions_ are always the user's - put each to them and wait.

The session is done when the frontier is empty with every branch of the design tree visited and nothing left silently assumed. Close by writing up the settled tree as a concise summary the user can act on. Do not act on it until the user confirms you have reached a shared understanding.
