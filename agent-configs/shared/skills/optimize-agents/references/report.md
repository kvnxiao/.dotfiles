# Report format

Use this format for the step 6 design and for a report-mode reply.

## Ranking

Estimate each saving as the tokens a change removes from a load times the loads per traced request, and label it an estimate. Rank recommendations by severity, then by saving times how often the workflow runs. When nothing records how often, infer it from the triggers and say so.

- **High:** a `truncates` finding, a broken reference, contradictory rules, or a gate a workflow can skip.
- **Medium:** a `risk` finding on a file a trace reads, or a saving on every session, on every delegate, or on a frequent request.
- **Low:** everything else.

## Report mode

Apply step 5's rules without `brainstorm`: put behavior-preserving fixes in one batch, give each behavior-changing recommendation its options, and state each question for the user in its recommendation.

## Sections

- **Baseline:** session start and delegate start per supported host from the analyzer, with your own measurements labeled.
- **Workflows and traces:** each workflow's inferred invariants, and each trace's reads, records written, estimated tokens, and estimated tool calls.
- **Recommendations:** each with its severity, whether it changes behavior, and its estimated saving. In report mode, list each one's options with the recommended option first.
- **Change summary:** each file added, deleted, or modified, and how each modified file changes: trimmed, amended to fix a behavior, moved, or merged. In report mode, summarize the recommended options.
- **Scripts:** each new script's command and failure branch.
- **Savings:** the baseline and the estimated cost per host after the change, and each traced request before and after.
- **Separate findings:** problems outside the scope or outside the repository, and analyzer findings you dismissed, with the reason.
