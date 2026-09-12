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
            "note": None,
            "wrap_width": None,
            "allow_headings": None,
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

    def target_for(self, path: str) -> dict:
        return next(target for target in self.targets if target["path"] == path)

    def spans(self, path: str) -> list[list[int]]:
        return [
            [block["start"], block["end"]] for block in self.target_for(path)["blocks"]
        ]

    def edit(self, path: str, block_id: int, replacement: str) -> dict:
        return {
            "target_id": self.target_id(path),
            "block_id": block_id,
            "replacement": replacement,
        }

    def expect_rejection(self, edits: list[dict]) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.validate(self.write_result(edits=edits), self.write_events())
        self.assertEqual(raised.exception.code, 1)

    def run_validate(self, **result_overrides) -> str:
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            self.validate(self.write_result(**result_overrides), self.write_events())
        return printed.getvalue()

    def added_lines(self, patch: Path) -> list[str]:
        return [
            line[1:]
            for line in patch.read_text(encoding="utf-8").splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]

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
        out_of_scope_notes: list[dict] | None = None,
    ) -> Path:
        if reviewed_target_ids is None:
            reviewed_target_ids = [target["id"] for target in self.targets]
        if edits is None and status == "patch":
            edits = [self.edit("doc.md", 1, "A direct process.")]
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
                    "out_of_scope_notes": out_of_scope_notes or [],
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
        edits = [{"target_id": self.targets[0]["id"], "block_id": 1}]
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

    def test_only_unknown_block_edit_rejects_the_run(self) -> None:
        self.expect_rejection([self.edit("doc.md", 9, "Changed.")])

    def test_repeated_block_id_drops_the_second_edit(self) -> None:
        printed = self.run_validate(
            edits=[
                self.edit("doc.md", 1, "A direct process."),
                self.edit("doc.md", 1, "Another direct process."),
            ]
        )
        self.assertIn("PARTIAL", printed)
        self.assertIn("repeated block id", printed)
        self.assertEqual(
            self.added_lines(self.run_dir / "result.patch"), ["A direct process."]
        )

    def test_untracked_binary_is_classified_and_skipped(self) -> None:
        (self.root / "asset.bin").write_bytes(b"text\0binary")
        run_dir = self.base / "binary-run"
        self.prepare(run_dir=str(run_dir))
        self.assertNotIn("asset.bin", [target["path"] for target in self.targets])
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
        self.prepare(run_dir=str(run_dir))
        snapshot = json.loads(
            (run_dir / "snapshot.json").read_text(encoding="utf-8")
        )
        self.assertNotIn(
            "tracked.bin", [target["path"] for target in self.targets]
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
        self.prepare(
            run_dir=str(draft_run),
            patch_root=str(draft_root),
            scope_kind="transient",
            mode="quick",
            target=["pr-body.md"],
        )
        self.root = draft_root
        edits = [self.edit("pr-body.md", 1, "A direct update.")]
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
            "blocks": [
                {
                    "id": 1,
                    "start": 1,
                    "end": 1,
                    "first_prefix": "",
                    "prefix": "",
                    "single": False,
                }
            ],
            "wrap_mode": "hard-wrap",
            "wrap_width": 72,
            "line_ending": "lf",
        }
        edits = [{"target_id": 1, "block_id": 1, "replacement": "A direct subject"}]
        patch_text = "\n".join(
            section
            for _, section in audit_io.render_patch(edits, [target], draft_root)[0]
        ) + "\n"
        patch = self.base / "no-final-newline.patch"
        audit_io.write_patch(patch, patch_text, [target])
        self.root = draft_root
        self.run_git("apply", "--no-index", "--unidiff-zero", str(patch))
        self.assertEqual((draft_root / "subject.txt").read_bytes(), b"A direct subject")

    def test_deleting_the_final_block_keeps_the_preceding_newline(self) -> None:
        draft_root = self.base / "delete-final-line"
        draft_root.mkdir()
        (draft_root / "body.sql").write_bytes(b"SELECT 1;\n-- Delete.")
        target = {
            "id": 1,
            "path": "body.sql",
            "kind": "code-comment",
            "blocks": [
                {
                    "id": 1,
                    "start": 2,
                    "end": 2,
                    "first_prefix": "-- ",
                    "prefix": "-- ",
                    "single": False,
                }
            ],
            "wrap_mode": "hard-wrap",
            "wrap_width": 72,
            "line_ending": "lf",
        }
        edits = [{"target_id": 1, "block_id": 1, "replacement": ""}]
        patch_text = "\n".join(
            section
            for _, section in audit_io.render_patch(edits, [target], draft_root)[0]
        ) + "\n"
        patch = self.base / "delete-final-line.patch"
        audit_io.write_patch(patch, patch_text, [target])
        self.root = draft_root
        self.run_git("apply", "--no-index", "--unidiff-zero", str(patch))
        self.assertEqual((draft_root / "body.sql").read_bytes(), b"SELECT 1;\n")

    def test_only_lf_separates_physical_lines(self) -> None:
        self.assertEqual(
            audit_io.split_file_lines("one\vstill-one\fstill-one still-one\n"),
            ["one\vstill-one\fstill-one still-one"],
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
        self.root = drafts

    def test_sql_code_lines_stay_out_of_editable_scope(self) -> None:
        change = self.root / "change.sql"
        change.write_text("-- Old note.\nSELECT 1;\n", encoding="utf-8")
        self.run_git("add", "change.sql")
        self.run_git("commit", "--quiet", "-m", "Add sql fixture")
        change.write_text("-- A seamless note.\nSELECT 2;\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "sql-run"))
        target = self.target_for("change.sql")
        self.assertEqual(target["kind"], "code-comment")
        self.assertEqual(self.spans("change.sql"), [[1, 1]])

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
        self.expect_rejection([self.edit("doc.md", 1, shared)])

    def test_duplicate_line_is_rejected(self) -> None:
        repeated = "The coordinator retries the shadow write once before it gives up."
        guide = self.root / "guide.md"
        guide.write_text(f"Old opening line.\n\n{repeated}\n", encoding="utf-8")
        self.run_git("add", "guide.md")
        self.run_git("commit", "--quiet", "-m", "Add guide fixture")
        guide.write_text(
            f"A seamless opening line.\n\n{repeated}\n", encoding="utf-8"
        )
        self.prepare(run_dir=str(self.base / "duplicate-run"))
        self.expect_rejection([self.edit("guide.md", 1, repeated)])

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
        self.assertEqual(self.spans("commit-message.txt"), [[1, 1], [3, 3]])
        self.expect_rejection(
            [self.edit("commit-message.txt", 3, "A trailer rewrite.")]
        )

    def test_commit_body_is_rewrapped_to_the_commit_width(self) -> None:
        self.prepare_drafts(
            "rewrap",
            "commit-message.txt",
            "[COR-1] Add the thing\n\nA seamless body line worth rewriting.\n",
            "commit-message",
        )
        self.run_validate(
            edits=[
                self.edit(
                    "commit-message.txt",
                    2,
                    "A direct body line worth rewriting " * 4,
                )
            ]
        )
        added = self.added_lines(self.run_dir / "result.patch")
        self.assertGreater(len(added), 1)
        self.assertLessEqual(max(len(line) for line in added), 72)

    def test_over_width_subject_replacement_is_dropped(self) -> None:
        self.prepare_drafts(
            "subject", "subject.txt", "Add a seamless thing\n", "commit-subject"
        )
        self.expect_rejection(
            [self.edit("subject.txt", 1, "Add a direct thing that keeps going " * 3)]
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
                "A seamless body line.\n\n" * 40, encoding="utf-8"
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
        self.assertEqual(self.spans("block.sql"), [[1, 2]])

    def test_changed_prose_line_expands_to_its_paragraph(self) -> None:
        page = self.root / "page.md"
        page.write_text("One.\nTwo.\nThree.\n\nApart.\n", encoding="utf-8")
        self.run_git("add", "page.md")
        self.run_git("commit", "--quiet", "-m", "Add page fixture")
        page.write_text(
            "One.\nA seamless two.\nThree.\n\nApart.\n", encoding="utf-8"
        )
        self.prepare(run_dir=str(self.base / "paragraph-run"))
        self.assertEqual(self.spans("page.md"), [[1, 3]])

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
        self.assertEqual(self.spans("list.md"), [[2, 3]])

    def test_out_of_range_edit_keeps_its_targets_other_edits(self) -> None:
        page = self.root / "two.md"
        page.write_text("First paragraph.\n\nSecond paragraph.\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "salvage-run"))
        target = self.target_for("two.md")
        self.assertEqual(self.spans("two.md"), [[1, 1], [3, 3]])
        printed = self.run_validate(
            edits=[
                self.edit("two.md", 1, "A direct first paragraph."),
                self.edit("two.md", 7, "An adjacent paragraph the model also fixed."),
            ]
        )
        self.assertIn("PARTIAL", printed)
        self.assertIn("unknown block id", printed)
        self.assertTrue(
            (self.run_dir / f"result-{target['id']}.patch").is_file()
        )
        self.assertEqual(
            self.added_lines(self.run_dir / f"result-{target['id']}.patch"),
            ["A direct first paragraph."],
        )

    def test_out_of_range_edit_leaves_other_targets_intact(self) -> None:
        printed = self.run_validate(
            edits=[
                self.edit("doc.md", 9, "A direct process."),
                self.edit("NOTES.md", 1, "This states the details."),
            ]
        )
        self.assertIn("DROPPED", printed)
        self.assertTrue(
            (self.run_dir / f"result-{self.target_id('NOTES.md')}.patch").is_file()
        )
        self.assertFalse(
            (self.run_dir / f"result-{self.target_id('doc.md')}.patch").is_file()
        )

    def test_replacement_dropping_a_protected_token_is_dropped(self) -> None:
        page = self.root / "tokens.md"
        page.write_text(
            "The helper reads `--unidiff-zero` before it applies the patch.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "token-run"))
        self.expect_rejection(
            [
                self.edit(
                    "tokens.md",
                    1,
                    "The helper reads the flag before it applies the patch.",
                )
            ]
        )

    def test_replacement_that_splits_a_sentence_is_dropped(self) -> None:
        page = self.root / "fragment.md"
        page.write_text(
            "Link every requirement to a conformance check with observable "
            "expected results.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "fragment-run"))
        self.expect_rejection(
            [
                self.edit(
                    "fragment.md",
                    1,
                    "Names remain separate. requirement to a conformance check "
                    "with observable expected results.",
                )
            ]
        )

    def test_replacement_rewraps_to_the_files_own_width(self) -> None:
        page = self.root / "wrapped.md"
        widest = "Column " * 13 + "ends here at one hundred."
        self.assertEqual(len(widest), 116)
        page.write_text(widest[:100] + "\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "wrap-run"))
        target = self.target_for("wrapped.md")
        self.assertEqual(target["wrap_mode"], "hard-wrap")
        self.assertEqual(target["wrap_width"], 100)
        self.run_validate(
            edits=[
                self.edit("wrapped.md", 1, "The rewritten column ends here. " * 12)
            ]
        )
        added = self.added_lines(self.run_dir / f"result-{target['id']}.patch")
        self.assertGreater(len(added), 1)
        self.assertLessEqual(max(len(line) for line in added), 100)

    def test_wrap_width_comes_from_the_whole_file_not_the_changed_block(self) -> None:
        page = self.root / "mixed.md"
        wide = ("Column " * 13 + "ends here.")[:100]
        page.write_text(f"Short paragraph.\n\n{wide}\n", encoding="utf-8")
        self.run_git("add", "mixed.md")
        self.run_git("commit", "--quiet", "-m", "Add mixed-width fixture")
        page.write_text(f"A seamless paragraph.\n\n{wide}\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "mixed-run"))
        target = self.target_for("mixed.md")
        self.assertEqual(self.spans("mixed.md"), [[1, 1]])
        self.assertEqual(target["wrap_width"], 100)

    def test_unwrapped_file_keeps_one_line_per_block(self) -> None:
        page = self.root / "unwrapped.md"
        page.write_text("A seamless sentence. " * 12 + "\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "unwrapped-run"))
        target = self.target_for("unwrapped.md")
        self.assertEqual(target["wrap_mode"], "single-line")
        self.run_validate(
            edits=[self.edit("unwrapped.md", 1, "A direct sentence. " * 12)]
        )
        self.assertEqual(
            len(self.added_lines(self.run_dir / f"result-{target['id']}.patch")), 1
        )

    def test_caller_note_reaches_the_rendered_prompt(self) -> None:
        note = "docs/ is formatter-managed; wrap it at 100 columns."
        self.prepare(run_dir=str(self.base / "note-run"), note=[note])
        prompt = (self.run_dir / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("<caller_constraints>", prompt)
        self.assertIn(note, prompt)

    def test_caller_wrap_width_overrides_the_derived_width(self) -> None:
        page = self.root / "narrow.md"
        page.write_text("Short line.\n", encoding="utf-8")
        self.prepare(
            run_dir=str(self.base / "override-run"),
            wrap_width=[["narrow.md", "40"]],
        )
        self.assertEqual(self.target_for("narrow.md")["wrap_width"], 40)

    def test_fenced_code_is_context_not_an_editable_block(self) -> None:
        page = self.root / "fenced.md"
        page.write_text(
            "A seamless intro.\n\n```bash\nset -e\nrun_thing --flag\n```\n\nAfter.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "fence-run"))
        self.assertEqual(self.spans("fenced.md"), [[1, 1], [8, 8]])

    def test_table_and_frontmatter_lines_are_context(self) -> None:
        page = self.root / "table.md"
        page.write_text(
            "---\nname: fixture\n---\n\n| Column | Other |\n| --- | --- |\n"
            "| a | b |\n\nA seamless closing paragraph.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "table-run"))
        self.assertEqual(self.spans("table.md"), [[9, 9]])

    def test_heading_is_context_unless_the_caller_allows_it(self) -> None:
        page = self.root / "headed.md"
        page.write_text("## Mirrored heading\n\nA seamless body.\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "heading-run"))
        self.assertEqual(self.spans("headed.md"), [[3, 3]])
        self.prepare(
            run_dir=str(self.base / "heading-allowed-run"),
            allow_headings=["headed.md"],
        )
        self.assertEqual(self.spans("headed.md"), [[1, 1], [3, 3]])

    def test_context_lines_render_distinctly_from_editable_blocks(self) -> None:
        page = self.root / "excerpt.md"
        page.write_text("## Heading\n\nA seamless body.\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "excerpt-run"))
        audit_input = (self.run_dir / "audit-input.md").read_text(encoding="utf-8")
        self.assertIn("ctx| ## Heading", audit_input)
        self.assertIn("[[block 1]]\nA seamless body.\n[[/block 1]]", audit_input)

    def test_context_never_repeats_an_editable_block_line(self) -> None:
        page = self.root / "adjacent.md"
        page.write_text(
            "A seamless first paragraph.\n\nA seamless second paragraph.\n"
            "\nA seamless third paragraph.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "adjacent-run"))
        audit_input = (self.run_dir / "audit-input.md").read_text(encoding="utf-8")
        for paragraph in ("first", "second", "third"):
            self.assertNotIn(f"ctx| A seamless {paragraph} paragraph.", audit_input)

    def test_out_of_scope_note_is_reported(self) -> None:
        printed = self.run_validate(
            out_of_scope_notes=[
                {
                    "target_id": self.target_id("NOTES.md"),
                    "note": "The paragraph below the editable block repeats itself.",
                }
            ]
        )
        self.assertIn("NOTE\t", printed)
        self.assertIn("repeats itself", printed)

    def test_out_of_scope_note_for_an_unknown_target_is_rejected(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.validate(
                self.write_result(
                    out_of_scope_notes=[{"target_id": 99, "note": "Elsewhere."}]
                ),
                self.write_events(),
            )
        self.assertEqual(raised.exception.code, 1)

    def test_a_fence_closes_only_on_its_own_length(self) -> None:
        page = self.root / "nested.md"
        page.write_text(
            "A seamless intro.\n\n````md\n```sh\necho build the artifact\n```\n"
            "````\n\nAfter.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "nested-run"))
        self.assertEqual(self.spans("nested.md"), [[1, 1], [9, 9]])

    def test_a_leading_thematic_break_is_not_frontmatter(self) -> None:
        page = self.root / "rule.md"
        page.write_text(
            "---\n\nA seamless first paragraph.\n\n---\n\nA second paragraph.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "rule-run"))
        self.assertEqual(self.spans("rule.md"), [[3, 3], [7, 7]])

    def test_setext_headings_and_their_underlines_are_context(self) -> None:
        page = self.root / "setext.md"
        page.write_text(
            "Section Title\n=============\n\nA seamless body.\n\n"
            "Other Title\n-----------\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "setext-run"))
        self.assertEqual(self.spans("setext.md"), [[4, 4]])

    def test_pipe_less_table_rows_are_context(self) -> None:
        page = self.root / "bare-table.md"
        page.write_text(
            "A seamless intro.\n\nColumn A | Column B\n-------- | --------\n"
            "first    | second\n\nAfter.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "bare-table-run"))
        self.assertEqual(self.spans("bare-table.md"), [[1, 1], [7, 7]])

    def test_indented_code_after_a_paragraph_line_is_context(self) -> None:
        page = self.root / "indented.md"
        page.write_text(
            "Run the helper as shown:\n    uv run audit_io.py prepare\n"
            "    uv run audit_io.py validate\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "indented-run"))
        self.assertEqual(self.spans("indented.md"), [[1, 1]])

    def test_spaced_thematic_break_is_not_a_list_item(self) -> None:
        page = self.root / "spaced.md"
        page.write_text("A seamless intro.\n\n- - -\n\nAfter.\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "spaced-run"))
        self.assertEqual(self.spans("spaced.md"), [[1, 1], [5, 5]])

    def test_a_shebang_never_joins_a_comment_block(self) -> None:
        script = self.root / "run.sh"
        script.write_text(
            "#!/usr/bin/env bash\n# A seamless setup of the run directory.\n"
            "set -euo pipefail\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "shebang-run"))
        self.assertEqual(self.spans("run.sh"), [[2, 2]])

    def test_lint_pragmas_and_comment_lists_break_the_run(self) -> None:
        script = self.root / "pragma.py"
        script.write_text(
            "# A seamless note about the helper.\n# noqa: E501\n"
            "# Steps to run the audit:\n#   - prepare the bundle\n"
            "#   - validate the result\n"
            "value = 1\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "pragma-run"))
        self.assertEqual(self.spans("pragma.py"), [[1, 1], [3, 3]])

    def test_a_marker_is_stripped_only_when_a_space_follows(self) -> None:
        page = self.root / "marker.md"
        page.write_text("* The glob matches every file it walks.\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "marker-run"))
        target = self.target_for("marker.md")
        self.run_validate(
            edits=[
                self.edit("marker.md", 1, "*.md sources are the ones the glob walks.")
            ]
        )
        self.assertEqual(
            self.added_lines(self.run_dir / f"result-{target['id']}.patch"),
            ["* *.md sources are the ones the glob walks."],
        )

    def test_one_long_line_does_not_unwrap_a_wrapped_file(self) -> None:
        page = self.root / "outlier.md"
        wrapped = "A seamless first line of about seventy-eight columns in this file.\n"
        page.write_text(
            wrapped + "Its continuation line completes the paragraph.\n\n"
            + "x" * 136 + "\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "outlier-run"))
        self.assertEqual(self.target_for("outlier.md")["wrap_mode"], "hard-wrap")

    def test_a_single_line_outlier_does_not_widen_the_derived_width(self) -> None:
        page = self.root / "bullet.md"
        page.write_text(
            "A seamless paragraph line that runs to about seventy columns here.\n"
            "Its continuation completes the paragraph.\n\n"
            "- " + "y" * 109 + "\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "bullet-run"))
        self.assertEqual(self.target_for("bullet.md")["wrap_width"], 72)

    def test_adjacent_long_lines_do_not_read_as_a_wrap_column(self) -> None:
        page = self.root / "sentences.md"
        page.write_text(
            "A seamless opening sentence that runs well past any wrap column "
            + "and keeps going for a while. " * 4
            + "\n"
            + "A second sentence sharing the block on the next line, also long. "
            + "It continues past the threshold too. " * 3
            + "\n\nA closing paragraph.\n",
            encoding="utf-8",
        )
        self.prepare(run_dir=str(self.base / "sentences-run"))
        target = self.target_for("sentences.md")
        self.assertEqual(target["wrap_mode"], "single-line")
        self.assertEqual(target["wrap_width"], 0)

    def test_wrap_width_override_keeps_a_subject_on_one_line(self) -> None:
        self.prepare_drafts(
            "override-subject", "subject.txt", "Add a seamless thing\n", "commit-subject"
        )
        self.prepare(
            run_dir=str(self.base / "run-override-subject-again"),
            patch_root=str(self.root),
            scope_kind="transient",
            mode="quick",
            target=["subject.txt"],
            target_kind=[["subject.txt", "commit-subject"]],
            wrap_width=[["subject.txt", "20"]],
        )
        self.assertEqual(self.target_for("subject.txt")["wrap_mode"], "single-line")
        self.expect_rejection([self.edit("subject.txt", 1, "Add a direct thing here")])

    def test_wrap_width_rejects_a_nonnumeric_or_tiny_value(self) -> None:
        for columns in ("abc", "0", "5"):
            with self.assertRaises(SystemExit) as raised:
                self.prepare(
                    run_dir=str(self.base / f"bad-width-{columns}"),
                    wrap_width=[["doc.md", columns]],
                )
            self.assertEqual(raised.exception.code, 1)

    def test_an_override_naming_no_prepared_target_is_rejected(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.prepare(
                run_dir=str(self.base / "typo-run"),
                wrap_width=[["typo.md", "100"]],
            )
        self.assertEqual(raised.exception.code, 1)

    def test_spelling_a_number_out_keeps_the_edit(self) -> None:
        page = self.root / "count.md"
        page.write_text("The parser runs 2 passes over the buffer.\n", encoding="utf-8")
        self.prepare(run_dir=str(self.base / "count-run"))
        target = self.target_for("count.md")
        self.run_validate(
            edits=[
                self.edit("count.md", 1, "The parser runs two passes over the buffer.")
            ]
        )
        self.assertEqual(
            self.added_lines(self.run_dir / f"result-{target['id']}.patch"),
            ["The parser runs two passes over the buffer."],
        )

    def test_an_abbreviation_is_not_a_sentence_fragment(self) -> None:
        page = self.root / "abbrev.md"
        page.write_text(
            "The helper wraps a seamless run of prose blocks.\n", encoding="utf-8"
        )
        self.prepare(run_dir=str(self.base / "abbrev-run"))
        target = self.target_for("abbrev.md")
        self.run_validate(
            edits=[
                self.edit(
                    "abbrev.md", 1, "The helper wraps prose, e.g. paragraphs and items."
                )
            ]
        )
        self.assertEqual(
            self.added_lines(self.run_dir / f"result-{target['id']}.patch"),
            ["The helper wraps prose, e.g. paragraphs and items."],
        )

    def test_pascal_case_and_dotted_filenames_are_protected(self) -> None:
        self.assertEqual(
            audit_io.protected_tokens("The SystemExit path reads package.json at v1.2.3"),
            {"SystemExit", "package.json", "v1.2.3"},
        )

    def test_a_commit_message_subject_stays_on_one_line(self) -> None:
        self.prepare_drafts(
            "subject-line",
            "commit-message.txt",
            "feat: add a seamless mode\n\nA body line worth keeping.\n",
            "commit-message",
        )
        self.assertTrue(self.target_for("commit-message.txt")["blocks"][0]["single"])
        subject = (
            "feat: add the direct block addressing mode that finally replaces "
            "every line range"
        )
        self.assertGreater(len(subject), 72)
        self.expect_rejection([self.edit("commit-message.txt", 1, subject)])


if __name__ == "__main__":
    unittest.main()
