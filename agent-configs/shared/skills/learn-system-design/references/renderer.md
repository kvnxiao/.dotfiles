# Build and rebuild a presentation

Use the packaged scripts rather than generating viewer code. Commands below use `uv`; follow a target repository's Python-runner requirements when they differ. Install Node.js for build-time Rough.js SVG generation. Rough.js 4.6.6 and its MIT license are bundled under `assets/vendor/`; no package installation is needed. Build-time Python dependencies are pinned in script metadata. The resulting page needs no Python, server, installation, or network connection.

## New question

For a Markdown input, derive the output directory by removing the final `.md` extension from the full input path. For example, `/practice/question-name.md` produces `/practice/question-name/index.html`. Create that sibling folder even when the working directory is elsewhere; do not place package files directly in the input directory. For a text-only prompt, choose a descriptive folder name in the working directory.

Initialize that empty output directory:

```sh
uv run <skill-dir>/scripts/init.py <question-name> --title "Question title"
```

The initializer copies the viewer, fonts, licenses, schema, and rendering scripts. It creates `solution.json` with module placeholders and empty content fields. Remove irrelevant optional phases and leave out-of-scope entity or interface arrays empty; explain those omissions in the opening Notes. It refuses a nonempty destination instead of overwriting another presentation. It does not invent a solution or copy the question.

Save the full original question as `question.md` in that bundle. Preserve supplied figures as local PNG, JPEG, GIF, or WebP files and use relative Markdown image paths. Convert unsupported figures or save remote figures locally before rendering. Do not remove question content to make validation pass.

Fill `solution.json` according to the content contract. Then run:

```sh
uv run <question-name>/src/validate.py <question-name>/solution.json
uv run <question-name>/src/render.py --solution <question-name>/solution.json --question <question-name>/question.md --output <question-name>/index.html
```

Validation checks the JSON Schema and semantic references. Rendering repeats validation before writing output. On failure, read the reported field or relationship and repair it; do not bypass the checks. Both commands exit unsuccessfully for invalid inputs.

The renderer produces `index.html` and `index.manifest.json`. The page embeds CSS, JavaScript, fonts, licenses, diagrams, and the question. Open `index.html#19` to start at slide 19; refreshing retains that numeric position. Local question images are embedded. No runtime fetch is needed.

## Format compatibility

The current version 2 schema supports optional entity `fields` for indented data models; use them for newly authored entities. It also adds optional diagram roles, shapes, annotations, directions, and architecture metadata. Version 2 content without architecture metadata remains structurally valid. If an existing graph has `architecture`, add its required `replicated` boolean when adopting the current schema. New generation follows the current diagram rules. Refresh scripts, vendor assets, schema and viewer together when adopting the entity-field and architecture-metadata features.

Adaptive phase ordering keeps the version 2 schema: refresh only `validate.py` and `board.py` together to allow interleaved reveals, retain the most recent diagram and resolve Notes targets against it. Existing saved bundles keep their original behavior until explicitly refreshed; this change does not require runtime viewer asset updates.

New bundles use format version 2 with explicit per-step `reveal` schedules and bullet-only bodies. Keep older bundles on their saved renderer for exact rebuilds. To adopt this layout, migrate their content to version 2, then explicitly refresh the schema, rendering scripts, and viewer together. Do not relabel version 1 content without adding the schedule and revising its board text.

Flexible phase coverage and ingress choices retain format version 2. To use them in an existing bundle, explicitly refresh the schema, validate.py and board.py together. Older bundles keep their saved renderer until refreshed.

## Content revision or exact rebuild

Edit only `solution.json` for content changes, preserving stable IDs and diagram positions. Run the same validation and render commands. The manifest records hashes of the source question, solution, schema, image files, renderer modules, viewer files, and resulting HTML. Compare hashes when checking which inputs changed.

Keep the bundle's renderer and dependency versions fixed for exact rebuilding. Fresh model-generated reasoning is not byte-reproducible; saved inputs and a fixed build environment are. A content edit must not require changing runtime JavaScript or CSS.

## Viewer changes

The shared source is `assets/viewer/` in this skill. Its HTML template, CSS, JavaScript, fonts, and licenses define the application shell. `scripts/board.py` assembles the fixed content modules and invokes `scripts/diagrams.cjs` to generate seeded Rough.js SVG shapes, arrows, and Notes outlines. Python does not draw diagram shapes. The build manifest hashes the JavaScript generator and vendored dependency as well as the viewer.

After an authorized shared viewer change, refresh the matching bundle files explicitly and rebuild. Do not silently update older bundles during content-only edits. The renderer accepts `--viewer` and `--schema` for explicitly selected alternatives; its defaults resolve under the bundle's `assets/` directory.

## Validation boundaries

The schema rejects unknown fields and missing required content. Structural checks cannot prove technical correctness or readable diagram routing. Inspect the content and use the canvas acceptance checks when repository rules permit them.

To check the packaged renderer with disposable fixtures, run from the skill directory:

```sh
uv run --with markdown-it-py==4.0.0 --with jsonschema==4.23.0 python -m unittest discover -s scripts -p 'test_*.py'
```

These tests check assembly and invalid-input behavior. Browser checks and visual inspection remain separate. Do not present a successful build as proof that all interactions were tested.

The viewer embeds Nunito Variable (Latin, weights 200–1000), vendored from `@fontsource-variable/nunito@5.2.7`, and its SIL Open Font License. Keep both font families offline.
