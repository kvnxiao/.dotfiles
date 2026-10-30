---
name: write-readme
description: Write or restructure repository READMEs around their primary audience, with a clear introduction, evidence of value, a first-use path, and links to deeper documentation. Use for README creation, rewrites, and requests to remove implementation detail from an introductory README.
---

# Write README

Make the README help a new reader understand what the project provides, why it may be useful, and how to start using it. Preserve the user's requested scope and established repository conventions.

## Establish the audience and facts

Identify the primary reader and their next action before drafting. Infer them from the project's purpose, distribution, existing documentation, and the request; ask when competing audiences would materially change the result. For example, write a desktop application's introduction for someone considering installing it, and a library's introduction for a developer considering using its API. A library consumer and a contributor changing its internals are different audiences.

Read the current README, repository instructions, relevant documentation, and the files that establish installation and usage. Verify availability, supported platforms, commands, and claims against current evidence. Treat a specification as intended behavior, not proof of implementation or release readiness. Report unresolved facts rather than inventing them.

For an existing README, identify information to retain, relocate, or remove before rewriting. Preserve useful current information in an appropriate destination; remove obsolete claims and notes about the agent conversation or completed editing steps without preserving them as new documentation. Honor a temporary-output or README-only scope: propose out-of-scope relocations instead of modifying their destinations, and report any information whose relocation remains pending.

## Arrange a linear introduction

Use this reading order as a default, adapting headings and emphasis to the project rather than imposing a fixed template:

1. **Identity and purpose.** State what the project does and who it serves. Use an existing logo or a plain title. Put adoption-relevant status, such as an unreleased application, near the opening.
2. **Features and benefits.** For desktop and web applications, use a dedicated Features section that gives the primary reader a coherent overview of the available capabilities. Explain what each feature lets the reader do. Cover the meaningful user-facing features without enumerating every setting or implementation component. Adapt this section for other project types.
3. **Evidence or demonstration.** Show representative behavior through a real screenshot, a short example, or a supported comparison. Combine this with the benefits when that reads more naturally.
4. **Getting started.** Give the primary reader a verified path to one normal first use. State prerequisites before commands. Keep alternative installations and advanced setup in linked documentation.
5. **Deeper resources.** Provide descriptive links to user guidance and secondary-audience documentation, followed by applicable support, contribution, and license information. Include only destinations that exist or are created within the authorized scope.

Keep the README understandable when read top-down. Define unfamiliar terms before using them, including in headings. State each fact once and connect adjacent paragraphs by explanation, sequence, condition, or consequence. Avoid a directory inventory or table of contents that overwhelms a short introduction; use navigation when the document's actual length warrants it.

Group related behavior together within the Features section. Include a feature's relevant exceptions and complementary controls beside its main behavior. For example, describe an automatic application override, exclusions that preserve normal operation, and a manual override together. Do not make readers assemble one feature from scattered benefits, setup steps, caveats, and help links. Keep a feature-specific limitation beside that feature; group application-wide requirements and system effects separately.

Give feature groups enough space to explain their practical value. Use short subsections and focused lists when a single bullet becomes dense; colocation does not require one paragraph. For example, an app can group automatic rules, exclusions, and manual control under one feature heading. Optimize for a complete introduction, not the shortest document.

Use progressive disclosure for depth and audience changes, not to reveal basic capabilities gradually. The feature overview should establish what is available before the reader follows setup or reference links. For example, explain both automatic and manual operation in the feature list, and put their button-by-button instructions in a user guide.

Adapt the demonstration and first-use path:

| Project                                 | Primary reader's question                                    | Useful evidence and next step                                                                                                           |
| --------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Consumer application                    | What will this help me do?                                   | Show a representative interface screenshot and explain useful behavior; provide requirements and download or installation instructions. |
| Command-line tool                       | What task can I complete with it?                            | Show a realistic command and its result; provide installation and one short usage example.                                              |
| Library or framework                    | Why would I adopt this in my project?                        | Show an idiomatic example and concrete developer-experience advantages; provide dependency setup and a minimal working use.             |
| Collection or infrastructure repository | What does this repository provide, and which part do I need? | Explain the collection or operational purpose, identify its users, and give a selective navigation or setup path.                       |

If no usable release exists, say so and link verified source-build instructions when available. Do not turn a consumer application's README into a developer setup manual to compensate for missing distribution.

## Keep details with their audience

Keep information when it helps the primary audience evaluate the project or complete an ordinary first use. Move it to linked documentation when it changes the audience or becomes a reference beyond those introductory needs. For example, installation instructions for a library user belong in its README; instructions for rebuilding that library's test fixtures belong in contributor documentation.

Reuse existing destinations before creating new ones. Choose filenames to fit the repository; the following are examples, not required files:

| Information                                            | Possible destination                                    |
| ------------------------------------------------------ | ------------------------------------------------------- |
| Local contributor setup, builds, tests, and debugging  | `DEVELOPMENT.md` or an existing development guide       |
| Contribution process and review expectations           | `CONTRIBUTING.md`                                       |
| Internal components and architectural decisions        | Existing architecture or design documentation           |
| Complete settings, advanced usage, and troubleshooting | User guide or configuration reference                   |
| Benchmark methodology, environments, and limitations   | Benchmark or research documentation                     |
| Plans and implementation acceptance criteria           | Existing roadmap, specification, or implementation plan |

Link each relocated topic from the README with a label that explains its destination. Preserve useful content without copying it into several documents. Do not create empty scaffolding, a file for every paragraph, or a second authoritative copy of an existing guide. Check relocated links relative to their new location and update affected inbound links within scope.

Keep limitations that affect adoption visible beside the relevant claim or step, even when their explanation moves elsewhere. For example, retain an application's supported operating system and significant changes it makes to system settings. Separate planned capabilities from available ones. Remove notes about the editing session, temporary verification notes, implementation-only names or tracking IDs, and exhaustive edge cases from introductory prose; retain their relevant facts in the appropriate documentation.

Apply the same audience test during later edits. A new feature does not automatically require a new README paragraph, and an implementation fix does not automatically require a README update. Choose content by its usefulness to the primary reader, not by the amount of work that produced it. Do not impose an arbitrary word limit.

## Demonstrate value honestly

Persuade through concrete benefits and evidence. For example, show how a framework reduces the setup needed for a common task rather than calling it effortless. Use comparisons that address choices the reader might actually make; state their scope and link supporting details. Keep benchmark conditions and caveats available, and do not generalize a narrow measurement into an unconditional performance claim. Do not invent benchmarks or launch a benchmarking project merely to complete a README.

Use authentic, relevant assets when available. Reuse the project's existing logo or icon for identity. Select demonstrations by the audience's questions: a desktop or web app benefits from a representative interface screenshot or short workflow recording; a CLI from a terminal example; a library from an idiomatic code example or a supported benchmark; infrastructure from a diagram when relationships help readers understand it. A logo establishes identity but does not demonstrate behavior. Do not add every media type or generate a mock interface and present it as the application.

When the user requests media placeholders or a layout draft, reserve appropriate positions with visibly labeled text blocks that name the proposed medium, what it should show, and what the reader should learn. For example: `Screenshot placeholder: Show the schedule graph and its wake/bedtime controls so readers can connect their inputs to the daily curve.` Keep placeholders beside the relevant introduction or feature group. Use real assets where available and placeholders only for missing media that adds value. Do not use broken image links, invented measurements, or mock screenshots as evidence. Before treating the document as ready to publish, replace or remove visible placeholders unless the user explicitly wants them retained.

Without a request for placeholders, finish the text and report missing assets. Creating a logo or capturing a running application is separate work unless authorized by the task.

Keep visuals understandable with descriptive alternative text and readable presentation on light and dark backgrounds. Keep essential meaning in text as well. Add badges only when they answer a relevant reader question and point to real information; do not use decorative status claims or fabricated download links.

## Review the complete result

Check the README as a whole after drafting or restructuring:

- Can the intended reader explain what the project provides, why they might use it, and what to do next from this document alone?
- Does every introductory section serve that reader, with secondary audiences directed to deeper documentation?
- Are related capabilities, exceptions, and controls grouped so the reader can understand a complete feature in one place?
- What information is missing for an adoption decision, and what operational detail is premature? Do linked guides actually serve the audience their labels promise?
- Are commands, links, image paths, availability claims, and significant limitations supported by the inspected sources?
- Does each visual or requested placeholder answer a relevant reader question, and are missing assets clearly distinguished from real evidence?
- Has useful relocated material been preserved, with links that work from its new location?
- Does the prose make sense without session history, repository shorthand, or explanations outside the document?

Use the available `audit-prose` skill on the completed prose, passing the intended audience explicitly and reusing any existing cold-reader findings. Its independent reader receives only the artifact and audience. If that skill is unavailable, perform the checks above directly and report that an independent cold-reader pass did not run. Keep the README workflow usable without installing another skill.

Report the files changed, substantive relocations, validation results, and unresolved facts or missing assets. For a proposed README saved separately for comparison with the current README, identify its location and any steps needed before it can replace the repository README. Do not describe a draft as installed or published.
