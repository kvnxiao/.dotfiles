import argparse
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import audit_io


class AuditIoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.base = Path(self.temporary_directory.name)
        self.root = self.base / "repository"
        self.run_dir = self.base / "run"
        self.root.mkdir()
        self.run_dir.mkdir()
        self.run_git("init", "--quiet")
        self.run_git("config", "user.email", "audit@example.invalid")
        self.run_git("config", "user.name", "Audit Test")
        (self.root / "doc.md").write_bytes(b"Plain line.\r\n")
        self.run_git("add", "doc.md")
        self.run_git("commit", "--quiet", "-m", "Add fixture")
        (self.root / "doc.md").write_bytes(b"A seamless process.\r\n")
        (self.root / "NOTES.md").write_bytes(b"This delves into details.\n")
        self.diction = self.base / "diction.md"
        self.template = self.base / "prompt.md"
        self.diction.write_text("Replace synthetic diction.\n", encoding="utf-8")
        self.template.write_text(
            "digest={{BUNDLE_HASH}}\n{{AUDIT_INPUT}}", encoding="utf-8"
        )
        self.prepare()

    def run_git(self, *args: str) -> subprocess.CompletedProcess:
        result = subprocess.run(
            ["git", "-C", str(self.root), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode:
            self.fail(
                f"git {' '.join(args)} failed: "
                f"{result.stderr.decode('utf-8', errors='replace').strip()}"
            )
        return result

    def prepare(self) -> None:
        audit_io.prepare(
            argparse.Namespace(
                patch_root=str(self.root),
                run_dir=str(self.run_dir),
                mode="change-set",
                scope_kind="repository-change-set",
                diction=str(self.diction),
                prompt_template=str(self.template),
                target=None,
                line_range=None,
            )
        )
        snapshot = json.loads(
            (self.run_dir / "snapshot.json").read_text(encoding="utf-8")
        )
        self.targets = snapshot["targets"]

    def write_events(
        self, item_type: str = "agent_message", message: str | None = None
    ) -> Path:
        events = self.run_dir / "events.jsonl"
        item = {"type": item_type}
        if item_type == "agent_message":
            item["text"] = message or (self.run_dir / "result.json").read_text(
                encoding="utf-8"
            )
        values = [
            {"type": "thread.started", "thread_id": "test"},
            {"type": "item.completed", "item": item},
            {"type": "turn.completed", "usage": {}},
        ]
        events.write_text(
            "".join(json.dumps(value) + "\n" for value in values), encoding="utf-8"
        )
        return events

    def write_result(
        self,
        *,
        status: str = "patch",
        reviewed_target_ids: list[int] | None = None,
        reason: str = "",
        edits: list[dict] | None = None,
    ) -> Path:
        if reviewed_target_ids is None:
            reviewed_target_ids = [target["id"] for target in self.targets]
        if edits is None and status == "patch":
            target_id = next(
                target["id"] for target in self.targets if target["path"] == "doc.md"
            )
            edits = [
                {
                    "target_id": target_id,
                    "start_line": 1,
                    "end_line": 1,
                    "replacement_lines": ["A direct process."],
                }
            ]
        result = self.run_dir / "result.json"
        result.write_text(
            json.dumps(
                {
                    "bundle_hash": (self.run_dir / "bundle-hash.txt")
                    .read_text(encoding="utf-8")
                    .strip(),
                    "status": status,
                    "reviewed_target_ids": reviewed_target_ids,
                    "reason": reason,
                    "edits": edits or [],
                }
            ),
            encoding="utf-8",
        )
        return result

    def validate(self, result: Path, events: Path) -> None:
        audit_io.validate(
            argparse.Namespace(
                run_dir=str(self.run_dir), result=str(result), events=str(events)
            )
        )

    def test_prepare_embeds_every_target_and_resolves_template(self) -> None:
        self.assertEqual([target["path"] for target in self.targets], ["doc.md", "NOTES.md"])
        prompt = (self.run_dir / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("A seamless process.", prompt)
        self.assertIn("This delves into details.", prompt)
        self.assertNotIn("{{BUNDLE_HASH}}", prompt)
        self.assertNotIn("{{AUDIT_INPUT}}", prompt)
        self.assertEqual(
            (self.run_dir / "effort.txt").read_text(encoding="utf-8"), "medium\n"
        )

    def test_valid_patch_passes_validator_and_git_apply(self) -> None:
        self.validate(self.write_result(), self.write_events())
        patch = self.run_dir / "result.patch"
        self.run_git(
            "apply",
            "--check",
            "--unidiff-zero",
            str(patch),
        )
        self.run_git(
            "apply",
            "--unidiff-zero",
            str(patch),
        )
        self.assertEqual(
            (self.root / "doc.md").read_text(encoding="utf-8"), "A direct process.\n"
        )
        self.assertEqual((self.root / "doc.md").read_bytes(), b"A direct process.\r\n")

    def test_complete_no_changes_result_is_distinct(self) -> None:
        result = self.write_result(status="no_changes", edits=[])
        with self.assertRaises(SystemExit) as raised:
            self.validate(result, self.write_events())
        self.assertEqual(raised.exception.code, 4)

    def test_missing_target_acknowledgment_is_rejected(self) -> None:
        result = self.write_result(
            status="no_changes",
            reviewed_target_ids=[self.targets[0]["id"]],
            edits=[],
        )
        with self.assertRaises(SystemExit) as raised:
            self.validate(result, self.write_events())
        self.assertEqual(raised.exception.code, 1)

    def test_tool_event_is_rejected(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.validate(self.write_result(), self.write_events("command_execution"))
        self.assertEqual(raised.exception.code, 1)

    def test_unknown_event_type_is_rejected(self) -> None:
        result = self.write_result()
        events = self.write_events()
        event_values = [
            json.loads(line) for line in events.read_text(encoding="utf-8").splitlines()
        ]
        event_values.insert(1, {"type": "future.tool"})
        events.write_text(
            "".join(json.dumps(value) + "\n" for value in event_values),
            encoding="utf-8",
        )
        with self.assertRaises(SystemExit) as raised:
            self.validate(result, events)
        self.assertEqual(raised.exception.code, 1)

    def test_mismatched_agent_message_is_rejected(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.validate(self.write_result(), self.write_events(message="{}"))
        self.assertEqual(raised.exception.code, 1)

    def test_malformed_edit_is_rejected(self) -> None:
        edits = [{"target_id": self.targets[0]["id"], "start_line": 1}]
        with self.assertRaises(SystemExit) as raised:
            self.validate(self.write_result(edits=edits), self.write_events())
        self.assertEqual(raised.exception.code, 1)

    def test_changed_target_is_rejected(self) -> None:
        (self.root / "doc.md").write_text("Changed during audit.\n", encoding="utf-8")
        with self.assertRaises(SystemExit) as raised:
            audit_io.check_state(self.run_dir)
        self.assertEqual(raised.exception.code, 1)

    def test_changed_repository_inventory_is_rejected(self) -> None:
        (self.root / "later.md").write_bytes(b"Added during audit.\n")
        with self.assertRaises(SystemExit) as raised:
            audit_io.check_state(self.run_dir)
        self.assertEqual(raised.exception.code, 1)

    def test_out_of_scope_edit_is_rejected(self) -> None:
        target_id = self.targets[0]["id"]
        self.targets[0]["editable"] = [[2, 2]]
        snapshot_path = self.run_dir / "snapshot.json"
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot["targets"] = self.targets
        snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
        edits = [
            {
                "target_id": target_id,
                "start_line": 1,
                "end_line": 1,
                "replacement_lines": ["Changed."],
            }
        ]
        with self.assertRaises(SystemExit) as raised:
            self.validate(self.write_result(edits=edits), self.write_events())
        self.assertEqual(raised.exception.code, 1)

    def test_overlapping_edits_are_rejected(self) -> None:
        target_id = self.targets[0]["id"]
        edits = [
            {
                "target_id": target_id,
                "start_line": 1,
                "end_line": 1,
                "replacement_lines": ["First."],
            },
            {
                "target_id": target_id,
                "start_line": 1,
                "end_line": 1,
                "replacement_lines": ["Second."],
            },
        ]
        with self.assertRaises(SystemExit) as raised:
            self.validate(self.write_result(edits=edits), self.write_events())
        self.assertEqual(raised.exception.code, 1)

    def test_untracked_binary_is_classified_and_skipped(self) -> None:
        (self.root / "asset.bin").write_bytes(b"text\0binary")
        run_dir = self.base / "binary-run"
        run_dir.mkdir()
        audit_io.prepare(
            argparse.Namespace(
                patch_root=str(self.root),
                run_dir=str(run_dir),
                mode="change-set",
                scope_kind="repository-change-set",
                diction=str(self.diction),
                prompt_template=str(self.template),
                target=None,
                line_range=None,
            )
        )
        snapshot = json.loads(
            (run_dir / "snapshot.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("asset.bin", [target["path"] for target in snapshot["targets"]])
        self.assertEqual(
            json.loads(
                (run_dir / "skipped-targets.json").read_text(encoding="utf-8")
            ),
            [{"path": "asset.bin", "reason": "binary-or-non-UTF-8"}],
        )
        (self.root / "asset.bin").write_bytes(b"changed\0binary")
        with self.assertRaises(SystemExit) as raised:
            audit_io.check_state(run_dir)
        self.assertEqual(raised.exception.code, 1)

    def test_excluded_tracked_candidate_is_rechecked(self) -> None:
        (self.root / "tracked.bin").write_bytes(b"base\0binary")
        self.run_git("add", "tracked.bin")
        self.run_git("commit", "--quiet", "-m", "Add binary fixture")
        (self.root / "tracked.bin").write_bytes(b"changed\0binary")
        run_dir = self.base / "candidate-run"
        run_dir.mkdir()
        audit_io.prepare(
            argparse.Namespace(
                patch_root=str(self.root),
                run_dir=str(run_dir),
                mode="change-set",
                scope_kind="repository-change-set",
                diction=str(self.diction),
                prompt_template=str(self.template),
                target=None,
                line_range=None,
            )
        )
        snapshot = json.loads(
            (run_dir / "snapshot.json").read_text(encoding="utf-8")
        )
        self.assertNotIn(
            "tracked.bin", [target["path"] for target in snapshot["targets"]]
        )
        self.assertIn(
            "tracked.bin",
            [candidate["path"] for candidate in snapshot["candidates"]],
        )
        (self.root / "tracked.bin").write_bytes(b"Auditable prose.\n")
        with self.assertRaises(SystemExit) as raised:
            audit_io.check_state(run_dir)
        self.assertEqual(raised.exception.code, 1)

    def test_transient_lf_patch_validates_and_applies(self) -> None:
        draft_root = self.base / "drafts"
        draft_run = self.base / "draft-run"
        draft_root.mkdir()
        draft_run.mkdir()
        (draft_root / "pr-body.md").write_bytes(b"A seamless update.\n")
        audit_io.prepare(
            argparse.Namespace(
                patch_root=str(draft_root),
                run_dir=str(draft_run),
                mode="quick",
                scope_kind="transient",
                diction=str(self.diction),
                prompt_template=str(self.template),
                target=["pr-body.md"],
                line_range=None,
            )
        )
        snapshot = json.loads(
            (draft_run / "snapshot.json").read_text(encoding="utf-8")
        )
        self.root = draft_root
        self.run_dir = draft_run
        self.targets = snapshot["targets"]
        edits = [
            {
                "target_id": self.targets[0]["id"],
                "start_line": 1,
                "end_line": 1,
                "replacement_lines": ["A direct update."],
            }
        ]
        self.validate(self.write_result(edits=edits), self.write_events())
        patch = draft_run / "result.patch"
        self.run_git("apply", "--check", "--no-index", "--unidiff-zero", str(patch))
        self.run_git("apply", "--no-index", "--unidiff-zero", str(patch))
        self.assertEqual((draft_root / "pr-body.md").read_bytes(), b"A direct update.\n")

    def test_patch_preserves_missing_final_newline(self) -> None:
        draft_root = self.base / "no-final-newline"
        draft_root.mkdir()
        (draft_root / "subject.txt").write_bytes(b"A seamless subject")
        target = {
            "id": 1,
            "path": "subject.txt",
            "editable": None,
            "line_ending": "lf",
        }
        edits = [
            {
                "target_id": 1,
                "start_line": 1,
                "end_line": 1,
                "replacement_lines": ["A direct subject"],
            }
        ]
        patch_text = audit_io.render_patch(edits, [target], draft_root)
        patch = self.base / "no-final-newline.patch"
        audit_io.write_patch(patch, patch_text, [target])
        self.root = draft_root
        self.run_git("apply", "--no-index", "--unidiff-zero", str(patch))
        self.assertEqual((draft_root / "subject.txt").read_bytes(), b"A direct subject")

    def test_patch_deletes_unterminated_final_line(self) -> None:
        draft_root = self.base / "delete-final-line"
        draft_root.mkdir()
        (draft_root / "body.txt").write_bytes(b"Keep.\nDelete.")
        target = {
            "id": 1,
            "path": "body.txt",
            "editable": None,
            "line_ending": "lf",
        }
        edits = [
            {
                "target_id": 1,
                "start_line": 2,
                "end_line": 2,
                "replacement_lines": [],
            }
        ]
        patch_text = audit_io.render_patch(edits, [target], draft_root)
        patch = self.base / "delete-final-line.patch"
        audit_io.write_patch(patch, patch_text, [target])
        self.root = draft_root
        self.run_git("apply", "--no-index", "--unidiff-zero", str(patch))
        self.assertEqual((draft_root / "body.txt").read_bytes(), b"Keep.")

    def test_only_lf_separates_physical_lines(self) -> None:
        self.assertEqual(
            audit_io.split_file_lines("one\vstill-one\fstill-one\u2028still-one\n"),
            ["one\vstill-one\fstill-one\u2028still-one"],
        )


if __name__ == "__main__":
    unittest.main()
