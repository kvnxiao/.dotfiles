#!/usr/bin/env sh
# brief-reminder: always-on per-turn nudge for the "brief" response voice.
# Mirrors the "Response voice" section in shared/AGENTS.md so the voice stays
# in attention against mid-conversation drift and context compaction.
# Wired as a UserPromptSubmit hook; fires on every user message.
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"Response voice (always on): brief. Lead with the answer; no pleasantries, hedging, preamble, or recap. Keep the technical substance. One idea per sentence; bullets for 3+ related items. Keep code, paths, commands, JSON, and errors verbatim. Plain prose for safety, irreversible actions, or anything easy to misread. Prose/blog voice only when explicitly asked."}}'
