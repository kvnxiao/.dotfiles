import base64
import copy
import json
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from board import figure
from init import initialize
from render import render
from validate import PHASES, validate


def example() -> dict[str, Any]:
    steps: list[dict[str, Any]] = [
        {
            "id": phase,
            "phase": phase,
            "title": phase.title(),
            "lead": "Explain the operation.",
            "body": "- Atomic save",
            "notes": "If asked about retries, discuss idempotency.",
            "covers": ["fr-save", "nfr-safe"],
            "reveal": None,
        }
        for phase in PHASES
    ]
    steps.insert(1, {**copy.deepcopy(steps[0]), "id": "nonfunctional"})
    for index, section, identifier in (
        (0, "functional", "fr-save"),
        (1, "nonfunctional", "nfr-safe"),
        (2, "entities", "record"),
        (3, "interfaces", "save"),
    ):
        steps[index]["reveal"] = {"section": section, "ids": [identifier]}
    steps[5]["deep_dive"] = dict.fromkeys(
        ("limitation", "change", "alternative", "tradeoff", "failure", "diagram_update"),
        "Explain this design decision.",
    )
    return {
        "format_version": 2,
        "title": "A < B",
        "subtitle": "Practice",
        "mark": "AB",
        "scope": "Save records.",
        "assumptions": [],
        "exclusions": [],
        "requirements": [
            {"id": "fr-save", "kind": "functional", "text": "Save records.", "basis": "given"},
            {
                "id": "nfr-safe",
                "kind": "nonfunctional",
                "text": "Do not lose acknowledged writes.",
                "basis": "assumed",
            },
        ],
        "entities": [{"id": "record", "name": "Record", "description": "Stored value."}],
        "interfaces": [
            {
                "id": "save",
                "name": "PUT /records/{id}",
                "contract": "Return the saved revision.",
                "requirements": ["fr-save"],
                "entities": ["record"],
            }
        ],
        "steps": steps,
        "sources": [],
    }


class RendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.assets = Path(__file__).resolve().parent.parent / "assets"
        self.solution = self.root / "solution.json"
        self.data = example()
        self.question = self.root / "question.md"
        self.question.write_text("# Original\n<script>alert(1)</script>", encoding="utf-8")
        self.output = self.root / "index.html"

    def build(self) -> None:
        self.solution.write_text(json.dumps(self.data), encoding="utf-8")
        render(
            self.solution,
            self.question,
            self.output,
            self.assets / "viewer",
            self.assets / "solution.schema.json",
        )

    def test_rebuild_is_identical_and_embeds_fonts(self) -> None:
        self.build()
        first = self.output.read_bytes()
        self.build()
        self.assertEqual(first, self.output.read_bytes())
        html = first.decode()
        self.assertIn("A &lt; B", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("font-family:Nunito", html)
        self.assertIn("font-family:Excalifont", html)
        self.assertEqual(html.count("data:font/woff2;base64,"), 2)
        self.assertEqual(html.count("data-step="), 8)

    def test_invalid_inputs_fail_before_output(self) -> None:
        mutations = [
            lambda d: d.update(scope="   "),
            lambda d: d["steps"].reverse(),
            lambda d: d["interfaces"][0].update(entities=["missing"]),
            lambda d: d["interfaces"][0].update(requirements=[]),
            lambda d: d["steps"][4].update(covers=[]),
            lambda d: d["steps"][5].pop("deep_dive"),
            lambda d: d["steps"][0].update(script="alert(1)"),
            lambda d: d["requirements"].append(copy.deepcopy(d["requirements"][0])),
            lambda d: d["steps"][5].update(covers=["missing"]),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.data = example()
                mutate(self.data)
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())

    def test_reveals_require_one_matching_section_and_complete_coverage(self) -> None:
        mutations = [
            lambda d: d["steps"][0].update(reveal=None),
            lambda d: d["steps"][0]["reveal"].update(ids=["fr-save", "nfr-safe"]),
            lambda d: d["steps"][1].update(reveal={"section": "functional", "ids": ["fr-save"]}),
            lambda d: d["steps"][2].update(reveal=None),
            lambda d: d["steps"][4].update(reveal={"section": "interfaces", "ids": ["save"]}),
            lambda d: d["steps"][0].update(body="A paragraph instead of bullets."),
            lambda d: d["steps"][0].update(
                reveal=[
                    {"section": "functional", "ids": ["fr-save"]},
                    {"section": "nonfunctional", "ids": ["nfr-safe"]},
                ]
            ),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.data = example()
                mutate(self.data)
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())

    def test_interleaved_reveals_retain_the_latest_diagram(self) -> None:
        self.data["steps"][4]["diagram"] = {
            "type": "graph",
            "family": "early-design",
            "description": "Save through the application.",
            "nodes": [{"id": "app", "label": "App", "column": 0, "row": 0}],
            "edges": [],
        }
        self.data["steps"] = [self.data["steps"][i] for i in (0, 4, 1, 2, 3, 5, 6)]
        self.build()
        html = self.output.read_text(encoding="utf-8")
        stages = re.findall(r'<section id="step-\d+".*?</section>', html, re.S)
        self.assertNotIn('data-node-id="app"', stages[0])
        for stage in stages[1:7]:
            self.assertIn('data-node-id="app"', stage)
            self.assertNotIn("pre-design", stage)
        self.assertIn('data-note-target="reveal"', stages[2])
        self.assertIn('data-section="entities" data-from="3"', html)
        self.assertIn('data-section="interfaces" data-from="4"', html)

    def test_design_review_can_start_with_a_baseline(self) -> None:
        self.data["steps"].insert(0, self.data["steps"].pop(4))
        self.build()

    def test_interleaving_keeps_dependency_and_summary_guards(self) -> None:
        for order in ((0, 5, 1, 2, 3, 4, 6), (0, 4, 6, 1, 2, 3, 5)):
            with self.subTest(order=order):
                self.data = example()
                self.data["steps"] = [self.data["steps"][i] for i in order]
                with self.assertRaises(ValueError):
                    validate(self.data, self.assets / "solution.schema.json")

    def test_baseline_without_deep_dive_renders(self) -> None:
        self.data["steps"].pop(5)
        self.build()
        self.assertNotIn(" / deep-dive</div>", self.output.read_text(encoding="utf-8"))

    def test_focused_question_renders_without_entities_or_interfaces(self) -> None:
        self.data["entities"] = []
        self.data["interfaces"] = []
        self.data["requirements"] = [self.data["requirements"][1]]
        self.data["steps"] = [self.data["steps"][i] for i in (1, 4, 6)]
        for step in self.data["steps"]:
            step["covers"] = ["nfr-safe"]
        self.build()
        html = self.output.read_text(encoding="utf-8")
        self.assertIn("Non-functional requirements", html)
        self.assertNotIn('<section class="board-item left-card" data-section="entities"', html)
        self.assertNotIn('<section class="board-item left-card" data-section="interfaces"', html)
        self.assertNotIn('<section class="board-item left-card" data-section="functional"', html)

    def test_grouped_requirement_reveal_renders(self) -> None:
        self.data["requirements"].append(
            {"id": "fr-read", "kind": "functional", "text": "Read records.", "basis": "given"}
        )
        self.data["interfaces"][0]["requirements"].append("fr-read")
        self.data["steps"][0]["reveal"]["ids"].append("fr-read")
        self.data["steps"][4]["covers"].append("fr-read")
        self.build()
        html = self.output.read_text(encoding="utf-8")
        self.assertIn('<li data-reveal="0">Save records. (given)</li>', html)
        self.assertIn('<li data-reveal="0">Read records. (given)</li>', html)

    def test_flexible_phases_still_require_baseline_summary_and_coverage(self) -> None:
        for omitted in (4, 6):
            with self.subTest(omitted=omitted):
                data = example()
                data["steps"].pop(omitted)
                with self.assertRaisesRegex(ValueError, "baseline.*summary"):
                    validate(data, self.assets / "solution.schema.json")
        self.data["steps"].pop(5)
        self.data["steps"][4]["covers"] = ["fr-save"]
        with self.assertRaisesRegex(ValueError, "Design misses nonfunctional"):
            validate(self.data, self.assets / "solution.schema.json")

    def test_entity_update_requires_an_earlier_reveal(self) -> None:
        self.data["steps"][4]["entity_update"] = {
            "id": "record",
            "fields": ["recordId", "revision"],
            "reason": "Detect conflicting writes.",
        }
        self.data["steps"] = [self.data["steps"][i] for i in (0, 4, 1, 2, 3, 5, 6)]
        with self.assertRaisesRegex(ValueError, "before.*reveal|reveal.*before"):
            validate(self.data, self.assets / "solution.schema.json")

    def test_board_separates_sections_and_assigns_item_reveal_times(self) -> None:
        self.build()
        html = self.output.read_text(encoding="utf-8")
        for section, start in (
            ("functional", 0),
            ("nonfunctional", 1),
            ("entities", 2),
            ("interfaces", 3),
        ):
            self.assertIn(f'data-section="{section}" data-from="{start}"', html)
            self.assertRegex(html, rf'<li[^>]* data-reveal="{start}"[^>]*>')
        self.assertIn("Functional requirements", html)
        self.assertIn("Non-functional requirements", html)
        self.assertIn("Core entities / data models", html)
        self.assertIn("API / system interface", html)
        self.assertNotIn('<p class="lead">', html)

    def test_graph_references_and_positions_are_checked(self) -> None:
        graph: dict[str, Any] = {
            "type": "graph",
            "family": "architecture",
            "description": "Client writes to storage.",
            "nodes": [
                {"id": "client", "label": "Client", "column": 0, "row": 0},
                {"id": "store", "label": "Storage", "column": 1, "row": 0},
            ],
            "edges": [{"from": "client", "to": "store", "label": "write", "kind": "sync"}],
        }
        self.data["steps"][4]["diagram"] = graph
        self.data["steps"][5]["diagram"] = copy.deepcopy(graph)
        self.build()
        self.assertIn('data-arrow="end"', self.output.read_text(encoding="utf-8"))
        self.data["steps"][5]["diagram"]["nodes"][1]["row"] = 1
        with self.assertRaises(ValueError):
            validate(self.data, self.assets / "solution.schema.json")
        self.data["steps"][5]["diagram"] = copy.deepcopy(graph)
        self.data["steps"][5]["diagram"]["edges"][0]["to"] = "missing"
        with self.assertRaises(ValueError):
            validate(self.data, self.assets / "solution.schema.json")

    def test_evolving_graphs_keep_the_same_viewbox(self) -> None:
        graph: dict[str, Any] = {
            "type": "graph",
            "family": "architecture",
            "description": "Growing design",
            "nodes": [{"id": "app", "label": "App", "column": 1, "row": 0}],
            "edges": [],
        }
        self.data["steps"][4]["diagram"] = graph
        self.data["steps"][5]["diagram"] = copy.deepcopy(graph)
        self.data["steps"][5]["diagram"]["nodes"].append(
            {"id": "worker", "label": "Worker", "column": 1, "row": 3}
        )
        self.build()
        html = self.output.read_text(encoding="utf-8")
        views = re.findall(r'viewBox="([^"]+)" role="img"', html)
        self.assertEqual(views, ["0 0 960 1192"] * 3)
        self.assertIn('data-note-target="node:worker"', html)
        self.data["steps"][5]["note_target"] = "app"
        self.build()
        html = self.output.read_text(encoding="utf-8")
        self.assertRegex(html, r'id="step-5"[^>]*data-note-target="node:app"')

    def test_long_edge_label_is_outside_node_bounds(self) -> None:
        diagram = {
            "type": "graph",
            "family": "design",
            "description": "Read a published prompt.",
            "nodes": [
                {"id": "a", "label": "Client", "column": 0, "row": 0},
                {"id": "b", "label": "Server", "column": 1, "row": 0},
            ],
            "edges": [
                {"from": "a", "to": "b", "label": "load latest published prompt", "kind": "sync"}
            ],
        }
        tree = ET.fromstring(figure(diagram, "read"))
        mask = tree.find(".//{http://www.w3.org/2000/svg}rect")
        assert mask is not None
        self.assertGreaterEqual(float(mask.attrib["y"]), 0)
        self.assertLess(float(mask.attrib["y"]) + float(mask.attrib["height"]), 64)
        labels = [
            node.text or ""
            for node in tree.findall(".//{http://www.w3.org/2000/svg}text")
            if node.attrib.get("font-size") == "16"
        ]
        self.assertEqual(" ".join(labels), "load latest published prompt")

    def test_parallel_vertical_edge_labels_do_not_overlap(self) -> None:
        diagram = {
            "type": "graph",
            "family": "design",
            "description": "Two independent paths",
            "nodes": [
                {"id": "app", "label": "App", "column": 1, "row": 0},
                {"id": "db", "label": "DB", "column": 2, "row": 0},
                {"id": "adapter", "label": "Adapter", "column": 1, "row": 1},
                {"id": "worker", "label": "Worker", "column": 2, "row": 1},
            ],
            "edges": [
                {"from": "app", "to": "adapter", "label": "external offers", "kind": "sync"},
                {"from": "db", "to": "worker", "label": "poll durable work", "kind": "async"},
            ],
        }
        tree = ET.fromstring(figure(diagram, "parallel"))
        masks = tree.findall(".//{http://www.w3.org/2000/svg}rect")
        self.assertEqual(len(masks), 2)
        self.assertLess(
            float(masks[0].attrib["x"]) + float(masks[0].attrib["width"]),
            float(masks[1].attrib["x"]),
        )

    def test_shapes_annotations_and_bidirectional_arrows_are_escaped_and_stable(self) -> None:
        graph: dict[str, Any] = {
            "type": "graph",
            "family": "shapes",
            "description": "A read path",
            "nodes": [
                {
                    "id": "app",
                    "label": "Service",
                    "role": "service",
                    "column": 0,
                    "row": 0,
                    "bullets": ["Serve reads"],
                },
                {
                    "id": "db",
                    "label": "PostgreSQL",
                    "role": "store",
                    "column": 1,
                    "row": 0,
                    "annotation": ["id < revision"],
                },
                {"id": "choice", "label": "Allowed?", "role": "decision", "column": 2, "row": 0},
            ],
            "edges": [
                {"from": "app", "to": "db", "kind": "sync", "label": "read", "direction": "both"}
            ],
        }
        first = figure(graph, "shapes")
        self.assertEqual(first, figure(graph, "shapes"))
        for shape in ("rectangle", "ellipse", "diamond"):
            self.assertIn(f'data-shape="{shape}"', first)
        self.assertIn('data-arrow="start"', first)
        self.assertIn('data-arrow="end"', first)
        self.assertIn("id &lt; revision", first)
        ET.fromstring(first)

    def test_ingress_choices_preserve_graph_validation(self) -> None:
        nodes: list[dict[str, Any]] = [
            {"id": "app", "label": "App", "role": "service", "column": 1, "row": 0}
        ]
        graph: dict[str, Any] = {
            "type": "graph",
            "family": "architecture",
            "description": "Ingress",
            "architecture": {
                "deployment": "microservices",
                "entry": "external-api",
                "rationale": "Public APIs",
                "replicated": False,
            },
            "nodes": nodes,
            "edges": [],
        }
        self.data["steps"][4]["diagram"] = graph
        validate(self.data, self.assets / "solution.schema.json")
        graph["nodes"].append(
            {
                "id": "gateway",
                "label": "Envoy",
                "role": "gateway",
                "bullets": ["health checks"],
                "column": 0,
                "row": 0,
            }
        )
        validate(self.data, self.assets / "solution.schema.json")
        graph["nodes"].pop()
        graph["architecture"].update(deployment="monolith", replicated=True)
        validate(self.data, self.assets / "solution.schema.json")
        graph["architecture"].update(deployment="pipeline", entry="queue")
        validate(self.data, self.assets / "solution.schema.json")
        graph["nodes"].append(
            {"id": "client", "label": "Client", "role": "client", "column": 2, "row": 0}
        )
        graph["edges"].append({"from": "client", "to": "app", "kind": "sync", "label": "call"})
        with self.assertRaisesRegex(ValueError, "left-to-right"):
            validate(self.data, self.assets / "solution.schema.json")

    def test_dense_labels_and_annotations_stay_inside_reserved_bounds(self) -> None:
        diagram = {
            "type": "graph",
            "family": "dense",
            "description": "Dense labels",
            "nodes": [
                {
                    "id": "db",
                    "label": "x" * 60,
                    "role": "store",
                    "column": 0,
                    "row": 0,
                    "bullets": ["A responsibility detail", "Another responsibility"],
                    "annotation": ["a" * 27, "b" * 27, "c" * 27],
                }
            ],
            "edges": [],
        }
        tree = ET.fromstring(figure(diagram, "dense"))
        svg = tree.find("{http://www.w3.org/2000/svg}svg")
        assert svg is not None
        height = float(svg.attrib["viewBox"].split()[3])
        texts = tree.findall(".//{http://www.w3.org/2000/svg}text")
        for text in texts:
            self.assertLessEqual(len(text.text or ""), 27)
            self.assertLess(float(text.attrib["y"]) + 5, height)
        node = tree.find('.//{http://www.w3.org/2000/svg}g[@data-node-id="db"]')
        assert node is not None
        for text in node.findall("{http://www.w3.org/2000/svg}text"):
            self.assertGreater(float(text.attrib["y"]) - float(text.attrib["font-size"]), 64)
            self.assertLess(float(text.attrib["y"]) + 5, 214)

    def test_fanout_edge_label_masks_do_not_overlap(self) -> None:
        diagram = {
            "type": "graph",
            "family": "fanout",
            "description": "Fanout",
            "nodes": [
                {"id": "app", "label": "App", "column": 0, "row": 0},
                {"id": "db", "label": "DB", "column": 1, "row": 0},
                {"id": "cache", "label": "Cache", "column": 1, "row": 1},
            ],
            "edges": [
                {"from": "app", "to": "db", "label": "read / transact", "kind": "sync"},
                {"from": "app", "to": "cache", "label": "candidate offers", "kind": "sync"},
            ],
        }
        tree = ET.fromstring(figure(diagram, "fanout"))
        masks = tree.findall(".//{http://www.w3.org/2000/svg}rect")
        self.assertEqual(len(masks), 2)
        a, b = [{k: float(m.attrib[k]) for k in ("x", "y", "width", "height")} for m in masks]
        self.assertFalse(
            a["x"] < b["x"] + b["width"]
            and a["x"] + a["width"] > b["x"]
            and a["y"] < b["y"] + b["height"]
            and a["y"] + a["height"] > b["y"]
        )

    def test_alternate_viewer_does_not_need_a_vendor_sibling(self) -> None:
        alternate = self.root / "alternate-viewer"
        shutil.copytree(self.assets / "viewer", alternate)
        self.solution.write_text(json.dumps(self.data), encoding="utf-8")
        render(
            self.solution,
            self.question,
            self.output,
            alternate,
            self.assets / "solution.schema.json",
        )
        self.assertIn("Rough.js 4.6.6 license", self.output.read_text(encoding="utf-8"))

    def test_diagonal_edges_are_independent_straight_shape_boundary_connections(self) -> None:
        diagram = {
            "type": "graph",
            "family": "diagonals",
            "description": "Independent fanout",
            "nodes": [
                {"id": "app", "label": "App", "column": 0, "row": 1},
                {"id": "db", "label": "DB", "role": "store", "column": 1, "row": 0},
                {"id": "cache", "label": "Cache", "role": "cache", "column": 1, "row": 2},
            ],
            "edges": [
                {"from": "app", "to": target, "label": "", "kind": "sync"}
                for target in ("db", "cache")
            ],
        }
        tree = ET.fromstring(figure(diagram, "fanout"))
        edges = tree.findall('.//{http://www.w3.org/2000/svg}g[@data-edge-from="app"]')
        self.assertEqual(len(edges), 2)
        starts = []
        for index, edge in enumerate(edges):
            start = list(map(float, edge.attrib["data-start"].split(",")))
            end = list(map(float, edge.attrib["data-end"].split(",")))
            starts.append(start)
            self.assertAlmostEqual(
                (end[1] - start[1]) / (end[0] - start[0]), -0.875 if index == 0 else 0.875
            )
            path = edge.find("{http://www.w3.org/2000/svg}path")
            assert path is not None
            self.assertEqual(path.attrib["d"].count("C"), 2)
        self.assertLess(starts[0][1], 344)
        self.assertGreater(starts[1][1], 494)

    def test_replica_stacks_have_opaque_layers_and_one_label(self) -> None:
        for role in ("service", "store", "decision"):
            with self.subTest(role=role):
                diagram = {
                    "type": "graph",
                    "family": "replicas",
                    "description": "Replicated group",
                    "nodes": [
                        {
                            "id": "group",
                            "label": "Group",
                            "role": role,
                            "replicated": True,
                            "column": 0,
                            "row": 0,
                        }
                    ],
                    "edges": [],
                }
                tree = ET.fromstring(figure(diagram, "replicas"))
                layers = tree.findall(".//{http://www.w3.org/2000/svg}g[@data-replica-layer]")
                self.assertEqual(
                    [layer.attrib["data-replica-layer"] for layer in layers], ["16", "8", "0"]
                )
                for layer in layers:
                    self.assertIsNotNone(
                        layer.find('{http://www.w3.org/2000/svg}path[@fill="white"]')
                    )
                self.assertEqual(
                    [text.text for text in tree.findall(".//{http://www.w3.org/2000/svg}text")],
                    ["Group"],
                )

    def test_top_row_replica_labels_and_tall_gateway_fit(self) -> None:
        for role in ("service", "gateway"):
            with self.subTest(role=role):
                diagram = {
                    "type": "graph",
                    "family": "replicas",
                    "description": "Ingress replicas",
                    "nodes": [
                        {
                            "id": "a",
                            "label": "API Gateway",
                            "role": role,
                            "replicated": True,
                            "column": 0,
                            "row": 0,
                        },
                        {
                            "id": "b",
                            "label": "Application",
                            "role": "service",
                            "replicated": True,
                            "column": 1,
                            "row": 0,
                        },
                    ],
                    "edges": [{"from": "a", "to": "b", "label": "requests", "kind": "sync"}],
                }
                tree = ET.fromstring(figure(diagram, "replicas"))
                edge = tree.find('.//{http://www.w3.org/2000/svg}g[@data-edge-from="a"]')
                assert edge is not None
                self.assertAlmostEqual(float(edge.attrib["data-start"].split(",")[1]), 139)
                self.assertAlmostEqual(float(edge.attrib["data-end"].split(",")[1]), 139)
                self.assertIn(
                    "requests",
                    [text.text for text in tree.findall(".//{http://www.w3.org/2000/svg}text")],
                )

    def test_note_targets_reference_existing_graph_nodes(self) -> None:
        self.data["steps"][0]["note_target"] = "body"
        with self.assertRaises(ValueError):
            self.build()
        del self.data["steps"][0]["note_target"]
        self.data["steps"][4]["note_target"] = "missing"
        with self.assertRaises(ValueError):
            self.build()
        self.data["steps"][4]["note_target"] = "body"
        self.build()
        self.assertIn('data-note-target="body"', self.output.read_text(encoding="utf-8"))
        self.assertIn('class="note-connector"', self.output.read_text(encoding="utf-8"))
        self.assertNotIn(">Study notes<", self.output.read_text(encoding="utf-8"))

    def test_note_target_uses_the_retained_or_replacement_diagram(self) -> None:
        graph: dict[str, Any] = {
            "type": "graph",
            "family": "storage",
            "description": "Store the result.",
            "nodes": [{"id": "db", "label": "DB", "column": 1, "row": 0}],
            "edges": [],
        }
        self.data["steps"][4]["diagram"] = graph
        self.data["steps"][5]["note_target"] = "db"
        self.build()
        html = self.output.read_text(encoding="utf-8")
        self.assertRegex(html, r'id="step-5"[^>]*data-note-target="node:db"')
        replacement = copy.deepcopy(graph)
        replacement["nodes"][0]["id"] = "archive"
        self.data["steps"][5]["diagram"] = replacement
        with self.assertRaisesRegex(ValueError, "note_target"):
            validate(self.data, self.assets / "solution.schema.json")
        self.data["steps"][5]["note_target"] = "archive"
        validate(self.data, self.assets / "solution.schema.json")

    def test_talking_points_render_only_in_notes(self) -> None:
        self.data["steps"][4]["body"] = "- Durable booking intent"
        self.build()
        html = self.output.read_text(encoding="utf-8")
        self.assertNotIn('class="body-copy"', html)
        self.assertEqual(html.count("Durable booking intent"), 1)
        notes = re.findall(r'<div class="study-content"[^>]*>(.*?)</aside>', html, re.S)
        self.assertTrue(any("Durable booking intent" in note for note in notes))
        self.assertIn('marker-start="url(#note-arrow-4)"', html)

    def test_entity_fields_render_as_nested_list(self) -> None:
        self.data["entities"][0]["fields"] = ["recordId (PK)", "revision: int", "<unsafe>"]
        self.build()
        html = self.output.read_text(encoding="utf-8")
        self.assertIn('<ul class="entity-list">', html)
        self.assertIn("<strong>Record</strong>", html)
        self.assertIn("<li>recordId (PK)</li>", html)
        self.assertIn("<li>&lt;unsafe&gt;</li>", html)
        for invalid in (
            [],
            [""],
            ["same", "same"],
            ["field" + chr(10) + "- extra"],
            ["field" + chr(13) + "next"],
            "not an array",
        ):
            self.data["entities"][0]["fields"] = invalid
            with self.assertRaises(ValueError):
                self.build()

    def test_entity_evolution_requires_valid_explicit_changes(self) -> None:
        self.data["entities"][0]["fields"] = ["recordId"]
        update = {
            "id": "record",
            "fields": ["recordId", "revision"],
            "reason": "Detect conflicting edits.",
        }
        self.data["steps"][5]["entity_update"] = update
        self.build()
        html = self.output.read_text(encoding="utf-8")
        self.assertIn('data-model-from="2" data-model-until="5"', html)
        self.assertIn('data-model-from="5" data-model-until="8"', html)
        self.assertIn('data-note-target="entity:record"', html)
        self.assertIn("Detect conflicting edits.", html)
        for invalid in (
            {**update, "id": "unknown"},
            {**update, "fields": ["recordId"]},
            {**update, "reason": ""},
        ):
            self.data["steps"][5]["entity_update"] = invalid
            with self.assertRaises(ValueError):
                self.build()
        del self.data["steps"][5]["entity_update"]
        self.data["steps"][2]["entity_update"] = update
        with self.assertRaises(ValueError):
            self.build()

    def test_content_html_is_escaped(self) -> None:
        self.data["steps"][0]["body"] = '- <img src=x onerror="alert(1)">'
        self.build()
        self.assertIn("&lt;img src=x", self.output.read_text(encoding="utf-8"))

    def test_local_question_image_is_embedded(self) -> None:
        data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/l9sAAAAASUVORK5CYII="
        )
        (self.root / "figure.png").write_bytes(data)
        self.question.write_text("![Supplied diagram](figure.png)", encoding="utf-8")
        self.build()
        self.assertIn('src="data:image/png;base64,', self.output.read_text(encoding="utf-8"))
        self.assertIn('alt="Supplied diagram"', self.output.read_text(encoding="utf-8"))

    def test_remote_image_fails_before_output(self) -> None:
        self.question.write_text("![Diagram](https://example.org/diagram.png)", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.build()
        self.assertFalse(self.output.exists())

    def test_initializer_preserves_existing_files_and_rejects_empty_answers(self) -> None:
        bundle = self.root / "new-question"
        initialize(bundle, "Practice")
        self.assertTrue((bundle / "src/render.py").exists())
        self.assertTrue((bundle / "assets/viewer/NunitoVariable.woff2").exists())
        with self.assertRaises(ValueError):
            validate(
                json.loads((bundle / "solution.json").read_text()),
                self.assets / "solution.schema.json",
            )
        with self.assertRaises(ValueError):
            initialize(bundle, "Replacement")
        self.assertEqual(json.loads((bundle / "solution.json").read_text())["title"], "Practice")


if __name__ == "__main__":
    unittest.main()
