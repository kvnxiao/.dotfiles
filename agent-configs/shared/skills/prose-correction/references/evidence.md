# Evidence for maintaining prose-correction

When changing the skill's rules, read this reference. During a normal prose audit, do not load it.

Research describes tendencies under particular models, genres, readers, and tasks. Unless the evidence establishes that a construction is harmful across the artifacts this skill audits, treat a replicated tendency as a heuristic. House preferences do not need scientific framing. They must remain labeled as preferences.

## Discourse order

- When given information precedes new information, it can reduce integration cost. Syntax and discourse context moderate the effect. Haviland and Clark, “What's new? Acquiring new information as a process in comprehension” (1974): <https://doi.org/10.1016/S0022-5371(74)80003-4>.
- Main-clause order, event order, and givenness exert competing effects during adult reading. Scholman et al., “Discourse rules: the effects of clause order principles on the reading process” (2022): <https://doi.org/10.1080/23273798.2022.2077971>.
- Conditional clauses tend to precede the main clause, temporal clauses occur in both positions, and causal clauses tend to follow it. Processing, semantics, and discourse function compete. Diessel, “Competing motivations for the ordering of main and adverbial clauses” (2005): <https://doi.org/10.1515/ling.2005.43.3.449>.

Maintenance inference: prefer early framing context without banning short trailing conditions, temporal clauses, or causal clauses.

## Reader expertise

- Instructional assistance helps low-knowledge readers and can hinder high-knowledge readers. The effect varies by domain and is stronger for helping novices than for withholding help from experts. Tetzlaff et al., “A cornerstone of adaptivity—A meta-analysis of the expertise reversal effect” (2025): <https://doi.org/10.1016/j.learninstruc.2025.102142>.

Maintenance inference: model the reader before pruning explanation. Do not equate shorter prose with clearer prose for every audience.

## LLM style markers

- In a broad parallel corpus, instruction-tuned models used present-participial clauses about two to five times as often as human writers. GPT-4o used agentless passive voice at roughly half the human rate. Model family and register changed the results. Reinhart et al., “Do LLMs write like humans? Variation in grammatical and rhetorical styles” (2025): <https://doi.org/10.1073/pnas.2422455122>.
- Biomedical abstracts showed abrupt post-2022 increases in several style words associated with LLM assistance. The method measures corpus-level excess vocabulary; it does not prove authorship or establish that a word is defective. Kobak et al., “Delving into LLM-assisted writing in biomedical publications through excess vocabulary” (2025): <https://doi.org/10.1126/sciadv.adt3813>.

Maintenance inference: use participles and lexical markers as review signals. Judge the local construction and genre instead of banning a grammatical form because models overproduce it.

## Comments and documentation

- Comment-update practices improved models of future bugs, but inconsistent updates were not uniformly risky. Sudden deviations from a component's normal update practice carried the strongest signal. Ibrahim et al., “On the relationship between comment update practices and software bugs” (2012): <https://doi.org/10.1016/j.jss.2011.09.019>.
- An eye-tracking study found that comments changed comprehension performance from a decrease on some snippets to an improvement on others. Comment effect depended on code, comment quality, and reader background. Abdelsalam et al., “The Effect of Comments on Program Comprehension: An Eye-tracking Study” (2026): <https://doi.org/10.1007/s10664-025-10721-2>.

Maintenance inference: verify comment fidelity and usefulness. Do not make deletion or retention unconditional.

## Instruction load

- As instruction complexity rises, constraint satisfaction declines. Jiang et al., “FollowBench: A Multi-level Fine-grained Constraints Following Benchmark for Large Language Models” (2024): <https://aclanthology.org/2024.acl-long.257/>.
- Models can underuse relevant information in the middle of long contexts. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts” (2024): <https://doi.org/10.1162/tacl_a_00638>.

Maintenance inference: keep the operational skill concise and load detailed instruments only for the mode that needs them.

## Candidate generation

- Low-probability distribution tails contain unreliable tokens; controlled truncation improved diversity without accepting the full tail. Holtzman et al., “The Curious Case of Neural Text Degeneration” (2020): <https://arxiv.org/abs/1904.09751>.

Maintenance inference: compare candidates against explicit criteria. Do not ask a model to estimate sentence probabilities or select a candidate for being low probability.

## Ecosystem conventions

- Python one-line function docstrings prescribe the effect as a command: <https://peps.python.org/pep-0257/>.
- Go doc comments use complete declarative sentences that name exported symbols: <https://go.dev/doc/comment>.
- Git recommends imperative commit subjects: <https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project.html>.

Maintenance inference: ecosystem requirements override general artifact defaults.
