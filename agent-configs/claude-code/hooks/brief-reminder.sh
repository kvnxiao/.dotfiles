#!/usr/bin/env sh
# brief-reminder: always-on per-turn nudge for the "brief" response voice.
# Reinforces the canonical "Response voice" section in shared/AGENTS.md against
# mid-conversation drift and context compaction.
# Wired as a UserPromptSubmit hook; fires on every user message.
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"Apply the Response voice in CLAUDE.md: answer first; be brief, clear, technically complete, and natural; preserve literals; use unambiguous prose for risky actions."}}'
