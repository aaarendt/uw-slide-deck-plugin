#!/usr/bin/env python3
"""Tests for tools/validate_plugin.py (stdlib only)."""

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
