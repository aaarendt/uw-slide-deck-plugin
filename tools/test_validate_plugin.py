#!/usr/bin/env python3
"""Tests for tools/validate_plugin.py (stdlib only)."""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PLUGIN_DIR, "tools"))
import validate_plugin as vp  # noqa: E402


def _copy_packaging(dest):
    """Copy only the files the validator reads into `dest`."""
    for rel in (
        "plugin.json",
        os.path.join(".claude-plugin", "plugin.json"),
        os.path.join(".claude-plugin", "marketplace.json"),
        os.path.join(".agents", "plugins", "marketplace.json"),
    ):
        os.makedirs(os.path.dirname(os.path.join(dest, rel)), exist_ok=True)
        shutil.copy(os.path.join(PLUGIN_DIR, rel), os.path.join(dest, rel))
    shutil.copytree(os.path.join(PLUGIN_DIR, "skills"), os.path.join(dest, "skills"))


def _restore_manifests(dest):
    """Restore both plugin manifests in `dest` from the repository."""
    for rel in ("plugin.json", os.path.join(".claude-plugin", "plugin.json")):
        shutil.copy(os.path.join(PLUGIN_DIR, rel), os.path.join(dest, rel))


def _edit_json(path, fn):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    fn(data)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


class TestRepository(unittest.TestCase):
    def test_repository_is_valid(self):
        self.assertEqual(vp.validate(PLUGIN_DIR), [])


class TestBreakage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        _copy_packaging(self.tmpdir)
        self.assertEqual(vp.validate(self.tmpdir), [])

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _path(self, *parts):
        return os.path.join(self.tmpdir, *parts)

    def _assert_error(self, fragment):
        errors = vp.validate(self.tmpdir)
        self.assertTrue(
            any(fragment in e for e in errors), f"{fragment!r} not in {errors}"
        )

    def test_missing_portable_manifest(self):
        os.remove(self._path("plugin.json"))
        self._assert_error("plugin.json: missing")

    def test_wrong_schema(self):
        _edit_json(self._path("plugin.json"), lambda d: d.update({"$schema": "x"}))
        self._assert_error("$schema must be")

    def test_invalid_name(self):
        for bad in ("UW-Slides", "-uw", "uw--slides", "uw..slides"):
            _edit_json(self._path("plugin.json"), lambda d: d.update({"name": bad}))
            self._assert_error("invalid name")

    def test_unknown_field(self):
        _edit_json(self._path("plugin.json"), lambda d: d.update({"skills": "./skills"}))
        self._assert_error("unknown field 'skills'")

    def test_keywords_must_be_strings(self):
        _edit_json(self._path("plugin.json"), lambda d: d.update({"keywords": [1]}))
        self._assert_error("keywords must be")

    def test_null_fields_are_rejected(self):
        for key, fragment in (
            ("author", "author must be"),
            ("keywords", "keywords must be"),
            ("version", "version must be a string"),
        ):
            for rel in (("plugin.json",), (".claude-plugin", "plugin.json")):
                _edit_json(self._path(*rel), lambda d: d.update({key: None}))
            self._assert_error(fragment)
            _restore_manifests(self.tmpdir)

    def test_manifests_must_agree(self):
        _edit_json(
            self._path(".claude-plugin", "plugin.json"),
            lambda d: d.update({"version": "9.9.9"}),
        )
        self._assert_error("version differs")

    def test_skill_name_must_match_directory(self):
        os.rename(self._path("skills", "new-deck"), self._path("skills", "newdeck"))
        self._assert_error("does not match directory 'newdeck'")

    def test_skill_needs_description(self):
        path = self._path("skills", "design-review", "SKILL.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        lines = [l for l in text.splitlines() if not l.startswith("description:")]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        self._assert_error("description is empty")

    def test_skill_using_plugin_paths_must_resolve_them(self):
        path = self._path("skills", "design-review", "SKILL.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text.replace("two directories above this `SKILL.md`", "somewhere"))
        self._assert_error("does not say how to find the plugin")

    def test_codex_marketplace_required(self):
        os.remove(self._path(".agents", "plugins", "marketplace.json"))
        self._assert_error(".agents/plugins/marketplace.json: missing")

    def test_marketplace_source_must_be_root(self):
        _edit_json(
            self._path(".claude-plugin", "marketplace.json"),
            lambda d: d["plugins"][0].update({"source": "./plugins/uw-slides"}),
        )
        self._assert_error("source must point at the repository root")

    def test_marketplace_must_list_plugin(self):
        _edit_json(
            self._path(".agents", "plugins", "marketplace.json"),
            lambda d: d.update({"plugins": []}),
        )
        self._assert_error("no entry for plugin 'uw-slides'")

    def test_marketplace_plugins_must_be_array(self):
        rel = (".agents", "plugins", "marketplace.json")
        for bad in (None, {}, "uw-slides"):
            _edit_json(self._path(*rel), lambda d: d.update({"plugins": bad}))
            self._assert_error("plugins must be an array")

    def _edit_codex_entry(self, fn):
        _edit_json(
            self._path(".agents", "plugins", "marketplace.json"),
            lambda d: fn(d["plugins"][0]),
        )

    def test_codex_entry_needs_policy(self):
        self._edit_codex_entry(lambda e: e.pop("policy"))
        self._assert_error("needs a policy object")

    def test_codex_policy_installation_value(self):
        self._edit_codex_entry(lambda e: e["policy"].update({"installation": "available"}))
        self._assert_error("policy.installation must be one of")

    def test_codex_policy_needs_authentication(self):
        self._edit_codex_entry(lambda e: e["policy"].pop("authentication"))
        self._assert_error("policy.authentication must be a string")

    def test_codex_entry_needs_category(self):
        self._edit_codex_entry(lambda e: e.pop("category"))
        self._assert_error("category must be a non-empty string")

    def test_categories_must_agree(self):
        self._edit_codex_entry(lambda e: e.update({"category": "Education"}))
        self._assert_error("category differs between marketplaces")

    def test_category_case_is_ignored(self):
        self._edit_codex_entry(lambda e: e.update({"category": "PRODUCTIVITY"}))
        self.assertEqual(vp.validate(self.tmpdir), [])

    def _set_description(self, skill, lines):
        """Replace the `description:` line of a skill's front matter."""
        path = self._path("skills", skill, "SKILL.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        out = []
        for line in text.splitlines():
            if line.startswith("description:"):
                out.extend(lines)
            else:
                out.append(line)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(out) + "\n")

    def test_folded_description_is_read(self):
        self._set_description(
            "design-review",
            ["description: >", "  Validate UW brand compliance", "  for a slide deck."],
        )
        self.assertEqual(vp.validate(self.tmpdir), [])

    def test_empty_block_description_is_rejected(self):
        self._set_description("design-review", ["description: >"])
        self._assert_error("description is empty")

    def test_long_literal_description_is_rejected(self):
        self._set_description(
            "design-review", ["description: |"] + ["  " + "x" * 100] * 11
        )
        self._assert_error("longer than 1024 characters")


class TestMain(unittest.TestCase):
    def test_usage_error_prints_both_usage_lines(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(vp.main(["--bogus"]), 2)
        self.assertIn("Usage:", err.getvalue())
        self.assertIn("--claude", err.getvalue())
        self.assertIn("default: the directory above tools/", err.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
