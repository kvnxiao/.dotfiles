import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import analyze


class AntigravityChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "repo"
        (self.repo / ".git").mkdir(parents=True)
        home = patch.object(analyze, "HOME", self.root / "home")
        home.start()
        self.addCleanup(home.stop)

    def write(self, relative: str, text: str) -> Path:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_analysis(self) -> analyze.Analysis:
        result = analyze.Analysis(self.repo, [], [])
        result.walk()
        result.antigravity()
        return result

    def test_commented_triggers_load(self) -> None:
        for index, value in enumerate(
            ["always_on # apply everywhere", '"always_on" # apply everywhere']
        ):
            path = self.write(
                f".agents/rules/rule-{index}.md",
                f"---\ntrigger: {value}\n---\nUse stable defaults.\n",
            )
            result = self.run_analysis()
            self.assertIn(path, [p for p, _, _ in result.always["antigravity"]])
            self.assertEqual(result.limits, [])

    def test_description_comment_is_not_invalid_yaml(self) -> None:
        self.write(
            ".agents/skills/demo/SKILL.md",
            "---\nname: demo\ndescription: Read files # note: local only\n---\nRead files.\n",
        )
        result = self.run_analysis()
        self.assertEqual([name for name, _, _ in result.listing["antigravity"]["skills"]], ["demo"])
        self.assertEqual(result.limits, [])
        self.assertEqual(next(iter(result.skills.values())).description, "Read files")

    def test_agent_only_configuration_is_discovered(self) -> None:
        self.write(
            ".agents/agents/researcher.md",
            "---\nname: researcher\ndescription: Research facts.\n---\nResearch facts.\n",
        )
        result = self.run_analysis()
        self.assertEqual(
            [name for name, _, _ in result.listing["antigravity"]["agents"]], ["researcher"]
        )

    def test_legacy_rules_are_discovered(self) -> None:
        path = self.write(
            ".agent/rules/legacy.md", "---\ntrigger: always_on\n---\nUse stable defaults.\n"
        )
        result = self.run_analysis()
        self.assertIn(path, [p for p, _, _ in result.always["antigravity"]])

    def test_every_trigger_checks_expanded_size_without_loading_conditional_rules(self) -> None:
        for trigger in ["always_on", "glob", "manual", "model_decision"]:
            with self.subTest(trigger=trigger):
                path = self.write(
                    f".agents/rules/{trigger}.md",
                    f'---\ntrigger: {trigger}\nglobs: "*.py"\ndescription: Read this rule.\n---\n'
                    + f"@[Details](../../{trigger}.txt)\n",
                )
                included = self.write(f"{trigger}.txt", "x" * 25_000)
                result = self.run_analysis()
                self.assertTrue(
                    any(
                        trigger + ".md" in message and "24000" in message
                        for _, _, message in result.limits
                    ),
                    result.limits,
                )
                loaded = [p.resolve() for p, _, _ in result.always["antigravity"] if p]
                if trigger == "always_on":
                    self.assertIn(path, loaded)
                    self.assertIn(included, loaded)
                else:
                    self.assertNotIn(path, loaded)
                    self.assertNotIn(included, loaded)

    def test_actual_yaml_hazards_remain_errors(self) -> None:
        for value in ["Read files: local only", "@files", "Read files # comment\n  continued"]:
            with self.subTest(value=value):
                self.assertTrue(
                    any(
                        fatal
                        for fatal, _ in analyze.yaml_hazards(f"---\ndescription: {value}\n---\n")
                    )
                )

    def test_quoted_hash_and_block_scalar_content_are_preserved(self) -> None:
        for text in [
            '---\ndescription: "Read # files: locally" # note\n---\n',
            "---\ndescription: |\n  Read # files: locally\n---\n",
        ]:
            with self.subTest(text=text):
                meta, _ = analyze.frontmatter(text)
                self.assertEqual(meta["description"], "Read # files: locally")
                self.assertEqual(analyze.yaml_hazards(text), [])

    def test_multiline_quoted_scalar_preserves_hash(self) -> None:
        meta, _ = analyze.frontmatter('---\ndescription: "Read\n  # files carefully."\n---\n')
        self.assertEqual(meta["description"], "Read # files carefully.")

    def test_quoted_block_list_item_preserves_hash(self) -> None:
        meta, _ = analyze.frontmatter('---\nskills:\n  - "name # suffix" # note\n---\n')
        self.assertEqual(meta["skills"], ["name # suffix"])


class DelegateComparisonChecks(unittest.TestCase):
    def test_reports_first_difference_in_normalized_agent_bodies(self) -> None:
        cases = [
            ("abc", "xbc", 'researcher: claude and codex bodies differ at char 0: "abc" vs "xbc"'),
            ("ab", "abc", 'researcher: claude and codex bodies differ at char 2: "" vs "c"'),
            ("abc", "ab", 'researcher: claude and codex bodies differ at char 2: "c" vs ""'),
            ("", "a", 'researcher: claude and codex bodies differ at char 0: "" vs "a"'),
            ("a", "", 'researcher: claude and codex bodies differ at char 0: "a" vs ""'),
            ("猫犬", "猫鳥", 'researcher: claude and codex bodies differ at char 1: "犬" vs "鳥"'),
            ("**Read**   files.", "Read files.", "bodies match across hosts"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for left, right, expected in cases:
                with self.subTest(left=left, right=right):
                    result = analyze.Analysis(root, [], [])
                    result.agents = [
                        analyze.Agent("claude", "researcher", root / "claude.md", "", left, {}),
                        analyze.Agent("codex", "researcher", root / "codex.toml", "", right, {}),
                    ]
                    self.assertEqual(analyze.delegates_across(result), [expected])


if __name__ == "__main__":
    unittest.main()
