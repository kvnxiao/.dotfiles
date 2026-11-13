# /// script
# dependencies = ["markdown-it-py==4.0.0", "jsonschema==4.23.0"]
# ///
import argparse
import base64
import hashlib
import json
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import unquote, urlsplit

from board import make_board  # ty: ignore[unresolved-import]
from markdown_it import MarkdownIt  # ty: ignore[unresolved-import]
from markdown_it.token import Token  # ty: ignore[unresolved-import]
from validate import validate  # ty: ignore[unresolved-import]


def embed_images(tokens: list[Token], directory: Path, inputs: dict[str, Path]) -> None:
    for token in tokens:
        if token.type == "image":
            source = token.attrGet("src") or ""
            parsed = urlsplit(source)
            if parsed.scheme or parsed.netloc:
                raise ValueError(f"Save question image locally before rendering: {source}")
            path = (directory / unquote(parsed.path)).resolve()
            types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }
            if path.suffix.lower() not in types:
                raise ValueError(f"Question image needs PNG, JPEG, GIF, or WebP: {source}")
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            token.attrSet("src", f"data:{types[path.suffix.lower()]};base64,{data}")
            inputs[f"question-image/{source}"] = path
        if token.children:
            embed_images(token.children, directory, inputs)


def render(
    solution_path: Path, question_path: Path, output_path: Path, viewer: Path, schema: Path
) -> None:
    solution = json.loads(solution_path.read_text(encoding="utf-8"))
    validate(solution, schema)
    board, steps = make_board(solution)
    metadata = solution
    shell = (viewer / "shell.template").read_text(encoding="utf-8")
    licenses = "".join(
        f"<details><summary>{name} license</summary><pre>"
        f"{escape(((Path(__file__).resolve().parent.parent / 'assets/vendor/rough-LICENSE.txt') if name.startswith('Rough.js') else viewer / filename).read_text(encoding='utf-8'))}</pre></details>"
        for name, filename in [
            ("Excalifont", "Excalifont-OFL.txt"),
            ("Nunito", "Nunito-OFL.txt"),
            ("Rough.js 4.6.6", "../vendor/rough-LICENSE.txt"),
        ]
    )
    style = ""
    for name, filename, weight in [
        ("Excalifont", "Excalifont-Latin.woff2", "400"),
        ("Nunito", "NunitoVariable.woff2", "200 1000"),
    ]:
        font = base64.b64encode((viewer / filename).read_bytes()).decode("ascii")
        style += (
            f"@font-face{{font-family:{name};src:url(data:font/woff2;base64,{font}) "
            f'format("woff2");font-weight:{weight};font-style:normal;font-display:block;}}'
        )
    style += (viewer / "style.css").read_text(encoding="utf-8")
    options = "".join(
        f'<option value="{i}">{i + 1:02d} · {escape(step["section"])} — '
        f"{escape(step['title'])}</option>"
        for i, step in enumerate(steps)
    )
    markdown = MarkdownIt("commonmark", {"html": False}).enable("table")
    image_inputs: dict[str, Path] = {}
    tokens = markdown.parse(question_path.read_text(encoding="utf-8"))
    embed_images(tokens, question_path.parent, image_inputs)
    question = markdown.renderer.render(tokens, markdown.options, {})
    page = Template(shell).substitute(
        title=escape(metadata["title"]),
        subtitle=escape(metadata["subtitle"]),
        mark=escape(metadata["mark"]),
        board=board.replace("<!-- FONT_LICENSES -->", licenses),
        style=style,
        script=(viewer / "app.js").read_text(encoding="utf-8"),
        options=options,
        question=question,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page, encoding="utf-8", newline="\n")
    inputs = {
        "solution": solution_path,
        "schema": schema,
        "question": question_path,
        "renderer": Path(__file__),
    }
    for name in ("board.py", "diagrams.cjs", "validate.py"):
        inputs[name] = Path(__file__).parent / name
    inputs.update(
        {
            f"vendor/{p.name}": p
            for p in sorted((Path(__file__).resolve().parent.parent / "assets/vendor").iterdir())
            if p.is_file()
        }
    )
    inputs.update(image_inputs)
    inputs.update({f"viewer/{p.name}": p for p in sorted(viewer.iterdir()) if p.is_file()})
    manifest = {
        "format_version": 1,
        "inputs": {
            key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in inputs.items()
        },
        "output_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
    }
    output_path.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Built {len(steps)} steps: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", type=Path, required=True)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "assets/solution.schema.json",
    )
    parser.add_argument("--question", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--viewer", type=Path, default=Path(__file__).resolve().parent.parent / "assets/viewer"
    )
    args = parser.parse_args()
    try:
        render(args.solution, args.question, args.output, args.viewer, args.schema)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Render failed: {error}" + chr(10))


if __name__ == "__main__":
    main()
