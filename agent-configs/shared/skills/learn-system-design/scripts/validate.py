# /// script
# dependencies = ["jsonschema==4.23.0"]
# ///
import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator  # ty: ignore[unresolved-import]

PHASES = ("requirements", "entities", "interfaces", "baseline", "deep-dive", "summary")


def validate(solution: dict[str, Any], schema: Path) -> None:
    validator = Draft202012Validator(json.loads(schema.read_text(encoding="utf-8")))
    errors = list(validator.iter_errors(solution))
    if errors:
        error = errors[0]
        raise ValueError(
            f"{'.'.join(map(str, error.absolute_path)) or 'solution'}: {error.message}"
        )
    groups = {}
    for key in ("requirements", "entities", "interfaces", "steps"):
        ids = [item["id"] for item in solution[key]]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate IDs in {key}")
        groups[key] = set(ids)
    requirements = groups["requirements"]
    functional = {r["id"] for r in solution["requirements"] if r["kind"] == "functional"}
    nonfunctional = requirements - functional
    interface_coverage = set()
    for interface in solution["interfaces"]:
        if not set(interface["requirements"]) <= functional:
            raise ValueError(
                f"{interface['id']}: interface requirement references must be known functional requirement IDs"
            )
        if not set(interface["entities"]) <= groups["entities"]:
            raise ValueError(f"{interface['id']}: interface references an unknown entity")
        interface_coverage.update(interface["requirements"])
    if solution["interfaces"] and interface_coverage != functional:
        raise ValueError(
            f"Functional requirements without interfaces: {sorted(functional - interface_coverage)}"
        )
    phases = [step["phase"] for step in solution["steps"]]
    if "baseline" not in phases or "summary" not in phases:
        raise ValueError("Include a baseline and a final summary")
    if phases[0] not in ("requirements", "baseline"):
        raise ValueError("Start with requirements or a baseline design")
    if any(phase != "summary" for phase in phases[phases.index("summary") :]):
        raise ValueError("Finish with summary steps after all other phases")
    if "deep-dive" in phases and phases.index("deep-dive") < phases.index("baseline"):
        raise ValueError("Introduce a baseline before its deep dives")
    sections = {
        "functional": functional,
        "nonfunctional": nonfunctional,
        "entities": groups["entities"],
        "interfaces": groups["interfaces"],
    }
    section_phases = {
        "functional": "requirements",
        "nonfunctional": "requirements",
        "entities": "entities",
        "interfaces": "interfaces",
    }
    revealed: dict[str, set[str]] = {name: set() for name in sections}
    entity_reveals: dict[str, int] = {}
    for index, step in enumerate(solution["steps"]):
        lines = [line for line in step["body"].splitlines() if line.strip()]
        if not lines or any(not line.startswith("- ") or not line[2:].strip() for line in lines):
            raise ValueError(f"{step['id']}: body must use one concise bullet per line")
        reveal = step["reveal"]
        if step["phase"] in ("requirements", "entities", "interfaces") and "diagram" in step:
            raise ValueError(f"{step['id']}: introduce diagrams in the baseline phase")
        if reveal is None:
            continue
        section = reveal["section"]
        if step["phase"] != section_phases[section]:
            raise ValueError(f"{step['id']}: reveal section does not match phase")
        ids = set(reveal["ids"])
        if not ids <= sections[section] or ids & revealed[section]:
            raise ValueError(f"{step['id']}: reveal needs known, previously unrevealed IDs")
        revealed[section].update(ids)
        if section == "entities":
            entity_reveals.update((identifier, index) for identifier in ids)
    for section, ids in sections.items():
        if revealed[section] != ids:
            raise ValueError(f"Unrevealed {section} records: {sorted(ids - revealed[section])}")
    entity_fields = {entity["id"]: entity.get("fields", []) for entity in solution["entities"]}
    for index, step in enumerate(solution["steps"]):
        if "entity_update" not in step:
            continue
        update = step["entity_update"]
        if step["phase"] not in ("baseline", "deep-dive", "summary") or step["reveal"]:
            raise ValueError(
                f"{step['id']}: evolve one entity in a design step without a simultaneous reveal"
            )
        if update["id"] not in entity_fields:
            raise ValueError(f"{step['id']}: entity_update references an unknown entity")
        if index <= entity_reveals[update["id"]]:
            raise ValueError(f"{step['id']}: reveal an entity before updating its fields")
        if update["fields"] == entity_fields[update["id"]]:
            raise ValueError(f"{step['id']}: entity_update must change the model")
        entity_fields[update["id"]] = update["fields"]
    baseline_coverage: set[str] = set()
    design_coverage: set[str] = set()
    positions: dict[tuple[str, str], tuple[int, int]] = {}
    current_diagram: dict[str, Any] = {}
    for step in solution["steps"]:
        covers = set(step["covers"])
        if not covers <= requirements:
            raise ValueError(f"{step['id']}: unknown requirement reference")
        if step["phase"] == "baseline":
            baseline_coverage.update(covers)
        if step["phase"] in ("baseline", "deep-dive"):
            design_coverage.update(covers)
        if step["phase"] == "deep-dive" and not covers:
            raise ValueError(f"{step['id']}: deep dive must identify its driving requirements")
        if "note_target" in step and step["phase"] in ("requirements", "entities", "interfaces"):
            raise ValueError(
                f"{step['id']}: note_target overrides are only supported in design steps"
            )
        diagram = step.get("diagram", {})
        if diagram:
            current_diagram = diagram
        if (
            "note_target" in step
            and step["note_target"] != "body"
            and (
                current_diagram.get("type") != "graph"
                or step["note_target"] not in {node["id"] for node in current_diagram["nodes"]}
            )
        ):
            raise ValueError(f"{step['id']}: note_target must be body or a node in this graph")
        if diagram.get("type") != "graph":
            continue
        nodes = diagram["nodes"]
        ids = {node["id"] for node in nodes}
        cells = {(node["column"], node["row"]) for node in nodes}
        if len(ids) != len(nodes) or len(cells) != len(nodes):
            raise ValueError(f"{step['id']}: duplicate graph node or occupied grid cell")
        lookup = {node["id"]: node for node in nodes}
        for node in nodes:
            if node.get("shape") == "diamond" and node.get("role") != "decision":
                raise ValueError(f"{step['id']}: diamonds require the decision role")
            if node.get("role") == "decision" and (
                node.get("bullets") or node.get("shape", "diamond") != "diamond"
            ):
                raise ValueError(
                    f"{step['id']}: use a short decision label without responsibility bullets"
                )
        for node in nodes:
            key = (diagram["family"], node["id"])
            cell = (node["column"], node["row"])
            if key in positions and positions[key] != cell:
                raise ValueError(f"{step['id']}: node {node['id']} moved within its diagram family")
            positions[key] = cell
        for edge in diagram["edges"]:
            if edge["from"] not in ids or edge["to"] not in ids or edge["from"] == edge["to"]:
                raise ValueError(f"{step['id']}: edge needs two distinct existing nodes")
        for edge in diagram["edges"]:
            source, target = lookup[edge["from"]], lookup[edge["to"]]
            if source.get("role") == "client" and target["column"] <= source["column"]:
                raise ValueError(f"{step['id']}: client request paths must flow left-to-right")
            if source.get("role") == "decision" and not edge["label"].strip():
                raise ValueError(f"{step['id']}: label decision outcomes")
    if not functional <= baseline_coverage:
        raise ValueError(
            f"Baseline misses functional requirements: {sorted(functional - baseline_coverage)}"
        )
    if not nonfunctional <= design_coverage:
        raise ValueError(
            f"Design misses nonfunctional requirements: {sorted(nonfunctional - design_coverage)}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("solution", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "assets/solution.schema.json",
    )
    args = parser.parse_args()
    try:
        validate(json.loads(args.solution.read_text(encoding="utf-8")), args.schema)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Invalid solution: {error}\n")
    print("Solution structure and references are valid; review technical claims separately.")


if __name__ == "__main__":
    main()
