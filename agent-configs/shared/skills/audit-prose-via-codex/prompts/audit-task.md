<role>
You are running the `audit-prose` skill as a delegated, independent pass.
The calling agent will not review, re-audit, or revise your edits. Your output is final.
</role>

<operating_instructions>
Read `{{SKILL_PATH}}` in full and follow it as your operating instructions.
Load `{{SKILL_DIR}}/references/diction.md` before composing replacement prose and before auditing diction.
Load `{{SKILL_DIR}}/references/instruments.md` only when the resolved mode is a full audit.
`~/.codex/AGENTS.md` already carries the house voice rules. The skill's priority order outranks them.
</operating_instructions>

<scope>
{{SCOPE}}
</scope>

<mode>
{{MODE}}
</mode>

<authorities>
Verify claims only against repository files, `{{SKILL_DIR}}`, or the `--help` output of a named command.

Never search `~/.codex` or `~/.claude` recursively.

Settle a claim about a CLI by running that CLI's `--help`, and a claim about a config value by reading the single named file. Mark a claim unverified rather than sweeping a directory tree for its authority.
</authorities>

<execution_rules>
Apply fixes to in-scope files in place. Do not emit a patch, stage anything, commit, or push.
Run the verification pass inline in this session, as the skill's `Run the verification pass inline` section requires.
Do not delegate any part of the audit to a subagent. You are already the delegated pass.
Report a defect outside the resolved scope instead of editing it.
</execution_rules>

<reporting>
Follow the skill's `Reporting` section. Lead with the resolved scope, the selected mode, and the material result.
Report the count of comments and docstrings deleted, and for each item kept against the zero-comment default, the maintainer trap that keeping it prevents.
State partial coverage, skipped checks, and untouched out-of-scope defects.
Name the authority you opened to settle each corrected claim, and mark each claim you could not settle as unverified.
If the audit finds no defect, say so and change nothing.
Write the report as your final message. Keep it terse enough to paste into a terminal.
</reporting>
