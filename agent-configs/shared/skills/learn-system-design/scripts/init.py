# /// script
# dependencies = ["jsonschema==4.23.0"]
# ///
import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from validate import PHASES  # ty: ignore[unresolved-import]


def initialize(output: Path, title: str) -> None:
    root = Path(__file__).resolve().parent.parent
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Use an empty output directory; existing files are not overwritten")
    (output / "src").mkdir()
    shutil.copytree(root / "assets", output / "assets")
    for name in ("render.py", "validate.py", "board.py", "diagrams.cjs"):
        shutil.copyfile(root / "scripts" / name, output / "src" / name)
    steps = []
    for phase in PHASES:
        step: dict[str, Any] = {
            "id": phase,
            "phase": phase,
            "title": "",
            "lead": "",
            "body": "",
            "notes": "",
            "covers": [],
            "reveal": None,
        }
        if phase == "deep-dive":
            step["deep_dive"] = dict.fromkeys(
                ("limitation", "change", "alternative", "tradeoff", "failure", "diagram_update"), ""
            )
        steps.append(step)
    solution = {
        "format_version": 2,
        "title": title,
        "subtitle": "System design interview walkthrough",
        "mark": "SD",
        "scope": "",
        "assumptions": [],
        "exclusions": [],
        "requirements": [
            {"id": "fr-core", "kind": "functional", "text": "", "basis": "given"},
            {"id": "nfr-core", "kind": "nonfunctional", "text": "", "basis": "assumed"},
        ],
        "entities": [{"id": "entity-core", "name": "", "description": "", "fields": [""]}],
        "interfaces": [
            {
                "id": "api-core",
                "name": "",
                "contract": "",
                "requirements": ["fr-core"],
                "entities": ["entity-core"],
            }
        ],
        "steps": steps,
        "sources": [],
    }
    (output / "solution.json").write_text(json.dumps(solution, indent=2) + "\n", encoding="utf-8")
    print(f"Created {output / 'solution.json'}; fill empty fields before validation and rendering.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    try:
        initialize(args.output, args.title)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Initialization failed: {error}\n")


if __name__ == "__main__":
    main()
