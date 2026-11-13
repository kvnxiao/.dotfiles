import json
import subprocess
from html import escape
from pathlib import Path
from typing import Any

from markdown_it import MarkdownIt  # ty: ignore[unresolved-import]


def drawing(payload: dict[str, Any]) -> str:
    try:
        result = subprocess.run(
            ["node", str(Path(__file__).with_name("diagrams.cjs"))],
            input=json.dumps(payload),
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        )
    except FileNotFoundError as error:
        raise ValueError("Install Node.js to build Rough.js SVG diagrams") from error
    except subprocess.CalledProcessError as error:
        raise ValueError(f"Diagram generation failed: {error.stderr}") from error
    return result.stdout


def figure(
    diagram: dict[str, Any], step_id: str, graph_height: int | None = None, graph_width: int = 960
) -> str:
    return drawing(
        {
            "diagram": diagram,
            "id": step_id,
            "extent": {"width": graph_width, "height": graph_height} if graph_height else None,
        }
    )


def make_board(solution: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
    md = MarkdownIt("commonmark", {"html": False}).enable("table").disable("image")
    steps = solution["steps"]
    starts = {
        (step["reveal"]["section"], identifier): index
        for index, step in enumerate(steps)
        if step["reveal"]
        for identifier in step["reveal"]["ids"]
    }
    cards = [
        (
            "functional",
            "Functional requirements",
            [
                (r["id"], f"{r['text']} ({r['basis']})")
                for r in solution["requirements"]
                if r["kind"] == "functional"
            ],
        ),
        (
            "nonfunctional",
            "Non-functional requirements",
            [
                (r["id"], f"{r['text']} ({r['basis']})")
                for r in solution["requirements"]
                if r["kind"] == "nonfunctional"
            ],
        ),
        (
            "entities",
            "Core entities / data models",
            [(item["id"], "") for item in solution["entities"]],
        ),
        (
            "interfaces",
            "API / system interface",
            [
                (item["id"], f"**{item['name']}** — {item['contract']}")
                for item in solution["interfaces"]
            ],
        ),
    ]
    parts = []
    for section, title, items in cards:
        if not items:
            continue
        first = min(starts[(section, identifier)] for identifier, _ in items)
        if section == "entities":
            entity_parts = []
            for entity in solution["entities"]:
                identifier = entity["id"]
                first_step = starts[(section, identifier)]
                versions = [(first_step, entity.get("fields", []))] + [
                    (index, step["entity_update"]["fields"])
                    for index, step in enumerate(steps)
                    if step.get("entity_update", {}).get("id") == identifier
                ]
                rendered = []
                for version, (begin, fields) in enumerate(versions):
                    end = (
                        versions[version + 1][0] if version + 1 < len(versions) else len(steps) + 1
                    )
                    content = (
                        "<ul>" + "".join(f"<li>{escape(field)}</li>" for field in fields) + "</ul>"
                        if fields
                        else md.render(entity["description"])
                    )
                    rendered.append(
                        f'<div class="entity-version" data-model-from="{begin}" data-model-until="{end}">{content}</div>'
                    )
                entity_parts.append(
                    f'<li data-entity-id="{identifier}" data-reveal="{first_step}"><p><strong>{escape(entity["name"])}</strong></p><div class="entity-versions">{"".join(rendered)}</div></li>'
                )
            bullets = "".join(entity_parts)
        else:
            bullets = "".join(
                f'<li data-reveal="{starts[(section, identifier)]}">{md.renderInline(text)}</li>'
                for identifier, text in items
            )
        parts.append(
            f'<section class="board-item left-card" data-section="{section}" data-from="{first}"><h2>{title}</h2><ul class="{"entity-list" if section == "entities" else "record-list"}">{bullets}</ul></section>'
        )
    graph_heights: dict[str, int] = {}
    graph_widths: dict[str, int] = {}
    for step in steps:
        diagram = step.get("diagram", {})
        if diagram.get("type") == "graph":
            family = diagram["family"]
            height = max(
                352 + node["row"] * 280 + (35 if node.get("role") == "gateway" else 0)
                for node in diagram["nodes"]
            )
            graph_heights[family] = max(graph_heights.get(family, 0), height)
            graph_widths[family] = max(
                graph_widths.get(family, 960),
                320 * (1 + max(node["column"] for node in diagram["nodes"])),
            )
    previous_nodes: dict[str, dict[str, Any]] = {}
    metadata = []
    current_diagram: dict[str, Any] = {}
    for i, step in enumerate(steps):
        if "diagram" in step:
            current_diagram = step["diagram"]
        diagram = (
            figure(
                current_diagram,
                step["id"],
                graph_heights.get(current_diagram.get("family")),
                graph_widths.get(current_diagram.get("family"), 960),
            )
            if current_diagram
            else ""
        )
        body = md.render(step["body"])
        notes = body + f"<p>{escape(step['lead'])}</p>" + md.render(step["notes"])
        if step["reveal"] and step["reveal"]["section"] == "entities":
            for entity in solution["entities"]:
                if entity["id"] in step["reveal"]["ids"] and entity.get("fields"):
                    notes += f"<p>{escape(entity['description'])}</p>"
        if "entity_update" in step:
            notes += "<h3>Model change</h3>" + md.render(step["entity_update"]["reason"])
        if i == 0:
            notes += "<h3>Scope and assumptions</h3>" + md.render(solution["scope"])
            notes += md.render("\n".join(f"- {item}" for item in solution["assumptions"]))
            notes += "<h3>Out of scope</h3>" + md.render(
                "\n".join(f"- {item}" for item in solution["exclusions"])
            )
        if "deep_dive" in step:
            names = {
                "limitation": "Baseline limitation",
                "change": "Chosen change",
                "alternative": "Alternative",
                "tradeoff": "Tradeoff",
                "failure": "Failure behavior",
                "diagram_update": "Design update",
            }
            notes += (
                '<dl class="decision">'
                + "".join(
                    f"<dt>{label}</dt><dd>{md.render(step['deep_dive'][key])}</dd>"
                    for key, label in names.items()
                )
                + "</dl>"
            )
        early = (
            " pre-design"
            if not current_diagram and step["phase"] in ("requirements", "entities", "interfaces")
            else ""
        )
        target = step["reveal"]["section"] if step["reveal"] else ""
        anchor = "reveal" if step["reveal"] else "body"
        graph = step.get("diagram", {})
        if graph.get("type") == "graph":
            current = {node["id"]: node for node in graph["nodes"]}
            previous = previous_nodes.get(graph["family"], {})
            changed = [
                identifier
                for identifier, node in current.items()
                if previous.get(identifier) != node
            ]
            if changed and not step["reveal"]:
                anchor = "node:" + changed[-1]
            previous_nodes[graph["family"]] = current
        if "note_target" in step:
            anchor = "body" if step["note_target"] == "body" else "node:" + step["note_target"]
        if "entity_update" in step:
            anchor = "entity:" + step["entity_update"]["id"]
            target = "entities"
        outline = drawing({"kind": "outline", "id": step["id"]})
        parts.append(
            f'<section id="step-{i}" class="board-item stage{early}" data-focus="{target}" data-note-target="{anchor}" data-step="{i}" aria-labelledby="step-title-{i}"><div class="stage-main"><div class="eyebrow">{i + 1:02d} / {escape(step["phase"])}</div><h2 id="step-title-{i}">{escape(step["title"])}</h2>{diagram}</div><svg class="note-connector" aria-hidden="true"><defs><marker id="note-arrow-{i}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10" fill="none" stroke="#7197ad" stroke-width="1.5"/></marker></defs><path class="note-shaft" marker-start="url(#note-arrow-{i})"/></svg><aside class="study"><svg class="study-outline" viewBox="0 0 500 600" preserveAspectRatio="none" aria-hidden="true">{outline}</svg><h3>Notes</h3><div class="study-content" tabindex="0" aria-label="Notes for {escape(step["title"])}">{notes}</div></aside></section>'
        )
        metadata.append({"section": step["phase"], "title": step["title"]})
    sources = "".join(
        f'<li><a href="{escape(source["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(source["title"])}</a> — {escape(source["note"])} (retrieved {escape(source["retrieved"])})</li>'
        for source in solution["sources"]
    )
    parts.append(
        f'<section id="step-{len(steps)}" class="board-item stage source-block" data-step="{len(steps)}"><h2>Sources and assumptions</h2><ul><li>Reference solution · assumptions in notes</li><li>Full prompt in Question panel</li></ul><ul>{sources}</ul><ul><li>Offline presentation · external links require connectivity</li></ul><!-- FONT_LICENSES --></section>'
    )
    metadata.append({"section": "Sources", "title": "Sources and assumptions"})
    return "".join(parts), metadata
