#!/usr/bin/env python3
"""Tests for tools/deckperms.py (stdlib only; no network)."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
DECKPERMS = os.path.join(TOOLS_DIR, "deckperms.py")
sys.path.insert(0, TOOLS_DIR)

import deckperms as dp  # noqa: E402


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class DeckCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="deckperms-test-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.deck = os.path.join(self.tmp, "deck")
        os.mkdir(self.deck)
        _write(os.path.join(self.deck, "deck.yml"), "title: x\nslides:\n  - a\n")

    def path(self, *parts):
        return os.path.join(self.deck, *parts)


class TestPluginReadRules(unittest.TestCase):
    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_version_folder_covers_its_parent(self):
        rules = dp.plugin_read_rules("/home/u/.claude/plugins/cache/mp/uw-slides/0.6.2")
        self.assertEqual(rules, ["Read(//home/u/.claude/plugins/cache/mp/uw-slides/**)"])

    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_v_prefix_prerelease_and_hash_folders(self):
        for folder in ("v0.6.2", "0.7.0-rc.1", "0.7.0+build5", "9f3c2ab41d7e"):
            with self.subTest(folder=folder):
                rules = dp.plugin_read_rules(f"/p/uw-slides/{folder}")
                self.assertEqual(rules, ["Read(//p/uw-slides/**)"])

    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_other_folders_get_a_rule_for_just_that_folder(self):
        # A development checkout must not widen the rule to its parent.
        self.assertEqual(dp.plugin_read_rules("/home/u/src/uw-slide-deck-plugin"),
                         ["Read(//home/u/src/uw-slide-deck-plugin/**)"])
        self.assertEqual(dp.plugin_read_rules("/home/u/.claude/plugins/local/uw-slides"),
                         ["Read(//home/u/.claude/plugins/local/uw-slides/**)"])

    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_symlinked_and_resolved_spellings_both_get_a_rule(self):
        rules = dp.plugin_read_rules("/home/u/.claude/plugins/local/uw-slides", "/home/u/src/plugin")
        self.assertEqual(rules, ["Read(//home/u/.claude/plugins/local/uw-slides/**)",
                                 "Read(//home/u/src/plugin/**)"])

    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_same_spelling_twice_is_one_rule(self):
        self.assertEqual(len(dp.plugin_read_rules("/a/b", "/a/b")), 1)


class TestMergeAllow(DeckCase):
    def test_creates_the_file(self):
        p = self.path(".claude", "settings.json")
        added = dp.merge_allow(p, ["Bash(x *)", "Edit(/y/**)"])
        self.assertEqual(added, ["Bash(x *)", "Edit(/y/**)"])
        self.assertEqual(json.loads(_read(p)), {"permissions": {"allow": ["Bash(x *)", "Edit(/y/**)"]}})
        self.assertTrue(_read(p).endswith("\n"))

    def test_keeps_existing_settings_and_rules(self):
        p = self.path(".claude", "settings.json")
        before = {
            "model": "opus",
            "permissions": {"allow": ["Bash(git status)"], "deny": ["Read(./.env)"], "defaultMode": "plan"},
            "hooks": {"x": []},
        }
        _write(p, json.dumps(before))
        added = dp.merge_allow(p, ["Bash(git status)", "Bash(x *)"])
        self.assertEqual(added, ["Bash(x *)"])
        after = json.loads(_read(p))
        self.assertEqual(after["permissions"]["allow"], ["Bash(git status)", "Bash(x *)"])
        for key in ("model", "hooks"):
            self.assertEqual(after[key], before[key])
        self.assertEqual(after["permissions"]["deny"], ["Read(./.env)"])
        self.assertEqual(after["permissions"]["defaultMode"], "plan")

    def test_second_run_changes_nothing(self):
        p = self.path(".claude", "settings.json")
        dp.merge_allow(p, ["Bash(x *)"])
        before = _read(p)
        self.assertEqual(dp.merge_allow(p, ["Bash(x *)"]), [])
        self.assertEqual(_read(p), before)

    def test_check_mode_writes_nothing(self):
        p = self.path(".claude", "settings.json")
        self.assertEqual(dp.merge_allow(p, ["Bash(x *)"], write=False), ["Bash(x *)"])
        self.assertFalse(os.path.exists(p))
        self.assertFalse(os.path.exists(self.path(".claude")))

    def test_invalid_json_is_left_alone(self):
        p = self.path(".claude", "settings.json")
        _write(p, "{ not json")
        with self.assertRaises(dp.PermissionsError) as cm:
            dp.merge_allow(p, ["Bash(x *)"])
        self.assertIn("not valid JSON", str(cm.exception))
        self.assertEqual(_read(p), "{ not json")

    def test_wrong_shapes_are_refused_and_left_alone(self):
        for text in ('[]', '{"permissions": []}', '{"permissions": {"allow": "Bash(x)"}}'):
            with self.subTest(text=text):
                p = self.path(".claude", "settings.json")
                _write(p, text)
                with self.assertRaises(dp.PermissionsError):
                    dp.merge_allow(p, ["Bash(x *)"])
                self.assertEqual(_read(p), text)


class TestEnsureIgnored(DeckCase):
    def test_adds_the_line(self):
        _write(self.path(".gitignore"), "build/\n")
        self.assertTrue(dp.ensure_ignored(self.deck))
        self.assertEqual(_read(self.path(".gitignore")), "build/\n.claude/settings.local.json\n")

    def test_adds_a_newline_first_when_the_file_lacks_one(self):
        _write(self.path(".gitignore"), "build/")
        dp.ensure_ignored(self.deck)
        self.assertEqual(_read(self.path(".gitignore")), "build/\n.claude/settings.local.json\n")

    def test_creates_the_file(self):
        self.assertTrue(dp.ensure_ignored(self.deck))
        self.assertEqual(_read(self.path(".gitignore")), ".claude/settings.local.json\n")

    def test_already_listed_is_not_repeated(self):
        _write(self.path(".gitignore"), "a\n.claude/settings.local.json\n")
        self.assertFalse(dp.ensure_ignored(self.deck))
        self.assertEqual(_read(self.path(".gitignore")), "a\n.claude/settings.local.json\n")


class TestApply(DeckCase):
    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_writes_shared_and_local_files(self):
        r = dp.apply(self.deck, "/p/uw-slides/0.6.2")
        self.assertEqual(r.shared, dp.SHARED_RULES)
        self.assertEqual(r.local, ["Read(//p/uw-slides/**)"])
        self.assertTrue(r.ignored)
        self.assertEqual(r.files, 2)
        shared = json.loads(_read(self.path(".claude", "settings.json")))
        local = json.loads(_read(self.path(".claude", "settings.local.json")))
        self.assertEqual(shared["permissions"]["allow"], dp.SHARED_RULES)
        self.assertEqual(local["permissions"]["allow"], ["Read(//p/uw-slides/**)"])

    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_shared_file_has_no_machine_specific_paths(self):
        dp.apply(self.deck, "/home/someone/.claude/plugins/cache/mp/uw-slides/0.6.2")
        self.assertNotIn("someone", _read(self.path(".claude", "settings.json")))

    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_second_run_is_a_no_op(self):
        dp.apply(self.deck, "/p/uw-slides/0.6.2")
        files = {f: _read(self.path(f)) for f in (".claude/settings.json", ".claude/settings.local.json", ".gitignore")}
        again = dp.apply(self.deck, "/p/uw-slides/0.6.2")
        self.assertFalse(again.changed)
        for f, text in files.items():
            self.assertEqual(_read(self.path(f)), text, f)

    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_a_new_plugin_version_needs_no_new_rule(self):
        dp.apply(self.deck, "/p/uw-slides/0.6.2")
        newer = dp.apply(self.deck, "/p/uw-slides/0.7.0")
        self.assertFalse(newer.changed)

    @unittest.skipIf(os.name == "nt", "POSIX paths")
    def test_check_writes_nothing(self):
        r = dp.apply(self.deck, "/p/uw-slides/0.6.2", write=False)
        self.assertTrue(r.changed)
        self.assertEqual(sorted(os.listdir(self.deck)), ["deck.yml"])


class TestRules(unittest.TestCase):
    def test_rules_have_a_known_form_and_no_duplicates(self):
        self.assertEqual(len(dp.SHARED_RULES), len(set(dp.SHARED_RULES)))
        for rule in dp.SHARED_RULES:
            with self.subTest(rule=rule):
                self.assertRegex(rule, r"^(Bash|Edit)\(.+\)$")

    def test_rules_are_literal_text_not_shell_expansions(self):
        # Claude Code cannot match a rule against $VAR, ${...} or $(...).
        for rule in dp.SHARED_RULES:
            self.assertNotIn("$", rule)

    def test_resolve_catalog_is_allowed_for_resolve_only(self):
        rules = [r for r in dp.SHARED_RULES if "resolve-catalog" in r]
        self.assertEqual(rules, ["Bash(python3 tools/resolve-catalog.py resolve *)"])

    def test_edit_rules_cover_only_content_and_slides(self):
        self.assertEqual([r for r in dp.SHARED_RULES if r.startswith("Edit(")],
                         ["Edit(/content/**)", "Edit(/slides/**)"])


class TestCli(DeckCase):
    def run_cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, "-I", DECKPERMS, *args],
                              cwd=cwd or self.tmp, capture_output=True, text=True)

    def test_adds_rules_then_reports_up_to_date(self):
        first = self.run_cli(self.deck)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("Added Claude Code permission rules", first.stdout)
        self.assertTrue(os.path.isfile(self.path(".claude", "settings.json")))
        second = self.run_cli(self.deck)
        self.assertEqual(second.returncode, 0)
        self.assertIn("nothing to add", second.stdout)

    def test_defaults_to_the_current_folder(self):
        proc = self.run_cli(cwd=self.deck)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(os.path.isfile(self.path(".claude", "settings.json")))

    def test_check_flag(self):
        proc = self.run_cli(self.deck, "--check")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Would add", proc.stdout)
        self.assertFalse(os.path.exists(self.path(".claude")))

    def test_not_a_deck_exits_1(self):
        proc = self.run_cli(self.tmp)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no deck.yml", proc.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, ".claude")))

    def test_bad_settings_file_exits_1_and_is_untouched(self):
        _write(self.path(".claude", "settings.json"), "{oops")
        proc = self.run_cli(self.deck)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not valid JSON", proc.stderr)
        self.assertEqual(_read(self.path(".claude", "settings.json")), "{oops")


if __name__ == "__main__":
    unittest.main()
