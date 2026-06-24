# Development Guidelines

Behavioral guidelines for LLM agents. Bias toward caution over speed, and use judgment for trivial tasks.

## Think before coding

- State assumptions explicitly. If uncertain, always ask the user before implementing.
- Surface multiple interpretations rather than picking silently.
- Push back when a simpler approach exists or if the premise looks flawed.
- Don't hide confusion. Name what's unclear and ask the user.
- When providing multiple approaches, always label the recommendation and explain why it's the best choice.

## Simplicity first

- Write the minimum code that solves the problem. Nothing speculative.
- **Clear intent over clever code** - Keep things boring and obvious. If you need to explain it, it's too complex.
- No features, abstractions, configurability, or error handling for cases that weren't asked for.
- One responsibility per unit. Don't prematurely abstract single-use code.
- If 200 lines could be 50, rewrite it. Ask yourself: "Would a senior engineer say this is overcomplicated?". If yes, simplify.

## Surgical changes

- Touch only what the request requires. Every changed line should trace to it.
- Don't "improve" adjacent code, comments, or formatting. Match existing style even if you'd do it differently.
- Don't refactor things that aren't broken. Mention unrelated dead code; don't delete it.
- Clean up orphans your changes created (unused imports, variables, functions). Leave pre-existing dead code alone unless asked.

## Goal-driven execution

Turn tasks into verifiable goals BEFORE implementing:

- "Add validation" -> write tests for invalid inputs, then make them pass.
- "Fix the bug" -> write a test that reproduces it, then make it pass.
- "Refactor X" -> ensure tests pass before and after.

For multi-step work, state a brief plan with a verification check per step. Strong success criteria let you loop independently; weak ones ("make it work") cause rework and tech debt.

## Tooling and MCP use

- Always use `gh` CLI to access GitHub, never the GitHub MCP tool
- Always use `linear-cli` to interact with Linear, never the Linear MCP tool
- Use react-aria MCP to get latest documentation on React Aria Components
- Use Context7 MCP to validate current documentation about software libraries
- When working on TypeScript / JavaScript projects, always prefer `pnpm` and `pnpm exec` or `pnpm dlx` over `npm` and `npx`
