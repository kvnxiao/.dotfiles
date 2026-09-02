import argparse
import contextlib
import io
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
        self.base = Path(self.temporary_directory.name).resolve()
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

    def prepare(self, **overrides) -> None:
        if "run_dir" in overrides:
            self.run_dir = Path(overrides["run_dir"])
            self.run_dir.mkdir(exist_ok=True)
        namespace = {
            "patch_root": str(self.root),
            "run_dir": str(self.run_dir),
            "mode": "change-set",
            "scope_kind": "repository-change-set",
            "diction": str(self.diction),
            "prompt_template": str(self.template),
            "target": None,
            "line_range": None,
            "target_kind": None,
            "max_input_chars": audit_io.DEFAULT_MAX_INPUT_CHARS,
            "batch": None,
        }
        namespace.update(overrides)
        audit_io.prepare(argparse.Namespace(**namespace))
        snapshot = json.loads(
            (self.run_dir / "snapshot.json").read_text(encoding="utf-8")
        )
        self.targets = snapshot["targets"]

    def target_id(self, path: str) -> int:
        return next(target["id"] for target in self.targets if target["path"] == path)

    def expect_rejection(self, edits: list[dict], code: int = 1) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.validate(self.write_result(edits=edits), self.write_events())
        self.assertEqual(raised.exception.code, code)

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
            "kind": "draft-prose",
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
        patch_text = "\n".join(
            section
            for _, section in audit_io.render_patch(edits, [target], draft_root)[0]
        ) + "\n"
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
            "kind": "draft-prose",
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
        patch_text = "\n".join(
            section
            for _, section in audit_io.render_patch(edits, [target], draft_root)[0]
        ) + "\n"
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


    def prepare_drafts(self, label: str, name: str, text: str, kind: str) -> None:
        drafts = self.base / f"drafts-{label}"
        drafts.mkdir(exist_ok=True)
        (drafts / name).write_text(text, encoding="utf-8")
        self.prepare(
            run_dir=str(self.base / f"run-{label}"),
            patch_root=str(drafts),
            scope_kind="transient",
            mode="quick",
            target=[name],
            target_kind=[[name, kind]],
        )

    def test_sql_code_lines_stay_out_of_editable_scope(self) -> None:
        change = self.root / "change.sql"
        change.write_text("-- Old note.\nSELECT 1;\n", encoding="utf-8")
        self.run_git("add", "change.sql")
        self.run_git("commit", "--quiet", "-m", "Add sql fixture")
        change.write_text("-- A seamless note.\nSELECT 2;\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "sql-run"))
        target = next(item for item in self.targets if item["path"] == "change.sql")
        self.assertEqual(target["kind"], "code-comment")
        self.assertEqual(target["editable"], [[1, 1]])
        self.expect_rejection(
            [
                {
                    "target_id": target["id"],
                    "start_line": 2,
                    "end_line": 2,
                    "replacement_lines": ["SELECT 3;"],
                }
            ]
        )

    def test_code_file_without_changed_comments_is_skipped(self) -> None:
        change = self.root / "only-code.sql"
        change.write_text("SELECT 1;\n", encoding="utf-8")
        self.run_git("add", "only-code.sql")
        self.run_git("commit", "--quiet", "-m", "Add code-only fixture")
        change.write_text("SELECT 2;\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "code-only-run"))
        self.assertNotIn("only-code.sql", [item["path"] for item in self.targets])
        skipped = json.loads(
            (self.run_dir / "skipped-targets.json").read_text(encoding="utf-8")
        )
        self.assertIn(
            {"path": "only-code.sql", "reason": "no-changed-comment-lines"}, skipped
        )

    def test_machine_parsed_file_is_not_audited(self) -> None:
        (self.root / "plan.json").write_text('{"change": "one"}\n', encoding="utf-8")
        self.prepare(run_dir=str(self.base / "json-run"))
        self.assertNotIn("plan.json", [item["path"] for item in self.targets])
        skipped = json.loads(
            (self.run_dir / "skipped-targets.json").read_text(encoding="utf-8")
        )
        self.assertIn({"path": "plan.json", "reason": "non-prose-file"}, skipped)

    def test_cross_target_copy_is_rejected(self) -> None:
        shared = "The backfill mints one singleton enterprise per soft-deleted workspace."
        (self.root / "NOTES.md").write_text(shared + "\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "copy-run"))
        self.expect_rejection(
            [
                {
                    "target_id": self.target_id("doc.md"),
                    "start_line": 1,
                    "end_line": 1,
                    "replacement_lines": [shared],
                }
            ]
        )

    def test_duplicate_line_is_rejected(self) -> None:
        repeated = "The coordinator retries the shadow write once before it gives up."
        guide = self.root / "guide.md"
        guide.write_text(f"Old opening line.\n{repeated}\n", encoding="utf-8")
        self.run_git("add", "guide.md")
        self.run_git("commit", "--quiet", "-m", "Add guide fixture")
        guide.write_text(f"A seamless opening line.\n{repeated}\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "duplicate-run"))
        self.expect_rejection(
            [
                {
                    "target_id": self.target_id("guide.md"),
                    "start_line": 1,
                    "end_line": 1,
                    "replacement_lines": [repeated],
                }
            ]
        )

    def test_commit_trailer_and_blank_lines_are_protected(self) -> None:
        self.prepare_drafts(
            "trailer",
            "commit-message.txt",
            "[COR-1] Add the thing\n"
            "\n"
            "A seamless body line worth rewriting.\n"
            "\n"
            "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\n",
            "commit-message",
        )
        target = self.targets[0]
        self.assertEqual(target["kind"], "commit-message")
        self.assertEqual(target["editable"], [[1, 1], [3, 3]])
        self.expect_rejection(
            [
                {
                    "target_id": target["id"],
                    "start_line": 5,
                    "end_line": 5,
                    "replacement_lines": [],
                }
            ]
        )

    def test_commit_body_rewrap_is_rejected(self) -> None:
        self.prepare_drafts(
            "rewrap",
            "commit-message.txt",
            "[COR-1] Add the thing\n\nA seamless body line worth rewriting.\n",
            "commit-message",
        )
        target = self.targets[0]
        self.expect_rejection(
            [
                {
                    "target_id": target["id"],
                    "start_line": 3,
                    "end_line": 3,
                    "replacement_lines": ["A direct body line worth rewriting " * 3],
                }
            ]
        )

    def test_retryable_transport_error_is_distinct(self) -> None:
        result = self.write_result()
        events = self.run_dir / "events.jsonl"
        events.write_text(
            json.dumps(
                {
                    "type": "error",
                    "message": "Reconnecting... 2/5 (stream disconnected before completion)",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        with self.assertRaises(SystemExit) as raised:
            self.validate(result, events)
        self.assertEqual(raised.exception.code, 6)

    def test_oversized_bundle_prepares_batches(self) -> None:
        for index in range(3):
            (self.root / f"extra{index}.md").write_text(
                "A seamless body line.\n" * 40, encoding="utf-8"
            )
        run_dir = self.base / "batch-run"
        with self.assertRaises(SystemExit) as raised:
            self.prepare(run_dir=str(run_dir), max_input_chars=2000)
        self.assertEqual(raised.exception.code, 5)
        batches = json.loads((run_dir / "batches.json").read_text(encoding="utf-8"))
        self.assertGreater(len(batches), 1)
        self.prepare(run_dir=str(run_dir), max_input_chars=2000, batch=1)
        self.assertEqual(
            [item["path"] for item in self.targets], batches[0]["targets"]
        )

    def test_validate_writes_one_patch_per_target(self) -> None:
        self.validate(self.write_result(), self.write_events())
        target_id = self.target_id("doc.md")
        self.assertTrue((self.run_dir / "result.patch").is_file())
        self.assertTrue((self.run_dir / f"result-{target_id}.patch").is_file())


    def test_changed_comment_line_expands_to_its_block(self) -> None:
        block = self.root / "block.sql"
        block.write_text(
            "-- First line of the note.\n-- Second line of the note.\nSELECT 1;\n",
            encoding="utf-8",
        )
        self.run_git("add", "block.sql")
        self.run_git("commit", "--quiet", "-m", "Add block fixture")
        block.write_text(
            "-- First line of the note.\n-- A seamless second line.\nSELECT 1;\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "block-run"))
        target = next(item for item in self.targets if item["path"] == "block.sql")
        self.assertEqual(target["editable"], [[1, 2]])

    def test_changed_prose_line_expands_to_its_paragraph(self) -> None:
        page = self.root / "page.md"
        page.write_text("One.\nTwo.\nThree.\n\nApart.\n", encoding="utf-8")
        self.run_git("add", "page.md")
        self.run_git("commit", "--quiet", "-m", "Add page fixture")
        page.write_text(
            "One.\nA seamless two.\nThree.\n\nApart.\n", encoding="utf-8"
        )
        self.prepare(run_dir=str(self.base / "paragraph-run"))
        target = next(item for item in self.targets if item["path"] == "page.md")
        self.assertEqual(target["editable"], [[1, 3]])

    def test_out_of_scope_edit_drops_only_its_target(self) -> None:
        doc_id = self.target_id("doc.md")
        notes_id = self.target_id("NOTES.md")
        snapshot_path = self.run_dir / "snapshot.json"
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        for target in snapshot["targets"]:
            if target["path"] == "doc.md":
                target["editable"] = [[2, 2]]
        snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
        edits = [
            {
                "target_id": doc_id,
                "start_line": 1,
                "end_line": 1,
                "replacement_lines": ["A direct process."],
            },
            {
                "target_id": notes_id,
                "start_line": 1,
                "end_line": 1,
                "replacement_lines": ["This states the details."],
            },
        ]
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            self.validate(self.write_result(edits=edits), self.write_events())
        self.assertIn("DROPPED", printed.getvalue())
        self.assertTrue((self.run_dir / f"result-{notes_id}.patch").is_file())
        self.assertFalse((self.run_dir / f"result-{doc_id}.patch").is_file())


    def test_list_items_are_separate_prose_blocks(self) -> None:
        page = self.root / "list.md"
        page.write_text(
            "- First bullet.\n- Second bullet\n  continued here.\n- Third bullet.\n",
            encoding="utf-8",
        )
        self.run_git("add", "list.md")
        self.run_git("commit", "--quiet", "-m", "Add list fixture")
        page.write_text(
            "- First bullet.\n- A seamless second bullet\n  continued here.\n"
            "- Third bullet.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "list-run"))
        target = next(item for item in self.targets if item["path"] == "list.md")
        self.assertEqual(target["editable"], [[2, 3]])


if __name__ == "__main__":
    unittest.main()
