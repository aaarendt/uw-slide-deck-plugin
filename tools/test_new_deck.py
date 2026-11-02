#!/usr/bin/env python3
"""Tests for tools/new-deck.py (stdlib only; no network)."""

import datetime
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(PLUGIN_DIR, "tools")
NEW_DECK = os.path.join(TOOLS_DIR, "new-deck.py")

# new-deck.py has a hyphen so it cannot be imported normally; it imports
# deckparse from its own directory.
sys.path.insert(0, TOOLS_DIR)
_spec = importlib.util.spec_from_file_location("new_deck", NEW_DECK)
nd = importlib.util.module_from_spec(_spec)
sys.modules["new_deck"] = nd
_spec.loader.exec_module(nd)

import deckparse  # noqa: E402


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _fake_reveal(ok, reason=""):
    return lambda deck_dir: (ok, reason)


class ScaffoldCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="new-deck-test-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def scaffold(self, name="demo", brand="uw", **kw):
        kw.setdefault("skip_reveal", True)
        return nd.scaffold(name, brand, dest=self.tmp, **kw)

    def path(self, *parts):
        return os.path.join(self.tmp, *parts)


class TestFiles(ScaffoldCase):
    def test_expected_files_exist_for_both_brands(self):
        for brand in nd.BRANDS:
            with self.subTest(brand=brand):
                r = self.scaffold(f"deck-{brand}", brand)
                deck = r.deck_dir
                expected = [d for d, _, _ in nd.FILES] + [nd.HEADER[0]]
                expected += [d for d, _ in nd.TEXT_TEMPLATES]
                expected += ["deck.yml", "slides/title.md", ".gitignore", ".brand", ".uw-slides.json"]
                for rel in expected:
                    self.assertTrue(os.path.isfile(os.path.join(deck, rel)), rel)
                for d in nd.EMPTY_DIRS:
                    self.assertTrue(os.path.isdir(os.path.join(deck, d)), d)
                self.assertEqual(r.files, len(expected))

    def test_shell_scripts_are_executable(self):
        r = self.scaffold()
        scripts = [f for f in os.listdir(r.deck_dir) if f.endswith(".sh")]
        # Includes setup-reveal.sh and export.sh, which are not executable in git.
        self.assertIn("setup-reveal.sh", scripts)
        self.assertIn("export.sh", scripts)
        for f in scripts:
            mode = os.stat(os.path.join(r.deck_dir, f)).st_mode
            self.assertTrue(mode & stat.S_IXUSR, f)

    def test_vendored_tools_match_plugin(self):
        r = self.scaffold()
        for tool in ("deckparse.py", "lint.py", "resolve-catalog.py"):
            self.assertEqual(
                _read_bytes(os.path.join(r.deck_dir, "tools", tool)),
                _read_bytes(os.path.join(TOOLS_DIR, tool)),
                tool,
            )

    def test_header_is_brand_specific(self):
        headers = {}
        for brand in nd.BRANDS:
            r = self.scaffold(f"deck-{brand}", brand)
            src = os.path.join(PLUGIN_DIR, "design-systems", f"{brand}-brand", "shared", "header-reveal.html")
            headers[brand] = _read_bytes(os.path.join(r.deck_dir, "shared", "header.html"))
            self.assertEqual(headers[brand], _read_bytes(src))
        self.assertNotEqual(headers["uw"], headers["cloudbank"])

    def test_footer_is_the_reveal_footer(self):
        r = self.scaffold()
        footer = _read(os.path.join(r.deck_dir, "shared", "footer.html"))
        self.assertIn("Reveal.initialize", footer)

    def test_fonts_for_uw_only(self):
        fonts_src = os.path.join(PLUGIN_DIR, "design-systems", "uw-brand", "fonts")
        expected = sorted(os.listdir(fonts_src))
        uw = self.scaffold("deck-uw", "uw")
        self.assertEqual(sorted(os.listdir(os.path.join(uw.deck_dir, "assets", "fonts"))), expected)
        self.assertEqual(uw.fonts, len(expected))
        cb = self.scaffold("deck-cb", "cloudbank")
        self.assertFalse(os.path.exists(os.path.join(cb.deck_dir, "assets", "fonts")))
        self.assertEqual(cb.fonts, 0)

    def test_every_source_in_the_tables_exists(self):
        for brand in nd.BRANDS:
            sources = [s for _, s, _ in nd.FILES] + [nd.HEADER[1].format(brand=brand)]
            sources += [s for _, s in nd.TEXT_TEMPLATES] + ["templates/deck.yml", "plugin.json"]
            for s in sources:
                self.assertTrue(os.path.isfile(os.path.join(PLUGIN_DIR, s)), s)


class TestContents(ScaffoldCase):
    def test_stamp(self):
        r = self.scaffold("demo", "cloudbank")
        stamp = json.loads(_read(os.path.join(r.deck_dir, ".uw-slides.json")))
        version = json.loads(_read(os.path.join(PLUGIN_DIR, "plugin.json")))["version"]
        self.assertEqual(
            stamp,
            {
                "plugin_version": version,
                "brand": "cloudbank",
                "scaffolded_at": datetime.date.today().isoformat(),
                "catalog": None,
                "plugin_dir": os.path.realpath(PLUGIN_DIR),
            },
        )

    def test_brand_file(self):
        for brand in nd.BRANDS:
            r = self.scaffold(f"deck-{brand}", brand)
            self.assertEqual(_read(os.path.join(r.deck_dir, ".brand")), brand + "\n")

    def test_placeholders_are_substituted(self):
        r = self.scaffold("Cloud Intro", "cloudbank")
        readme = _read(os.path.join(r.deck_dir, "README.md"))
        agents = _read(os.path.join(r.deck_dir, "AGENTS.md"))
        self.assertTrue(readme.startswith("# Cloud Intro\n"))
        self.assertIn("CloudBank-branded presentation", readme)
        self.assertIn("design-systems/cloudbank-brand/DESIGN.md", agents)
        for text in (readme, agents):
            self.assertNotIn("[Presentation Name]", text)
            self.assertNotIn("[BRAND_NAME]", text)
            self.assertNotIn("[BRAND]", text)

    def test_deck_yml_title_and_slides(self):
        r = self.scaffold("cloudbank-intro")
        deck = deckparse.parse_deck(_read(os.path.join(r.deck_dir, "deck.yml")))
        self.assertEqual(deck["title"], "cloudbank-intro")
        self.assertEqual(deck["slides"], ["title", "example-slide"])

    def test_title_with_quotes_round_trips(self):
        name = 'My "Deck" intro'
        r = self.scaffold(name)
        deck = deckparse.parse_deck(_read(os.path.join(r.deck_dir, "deck.yml")))
        self.assertEqual(deck["title"], name)
        brief_path = os.path.join(r.deck_dir, "slides", "title.md")
        brief = deckparse.parse_brief(_read(brief_path), brief_path)
        self.assertEqual(brief["body"]["key_message"], name)

    def test_yaml_quote_escapes_backslash_and_quote(self):
        # Names cannot contain a backslash (it is a path separator), but the
        # quoting helper must still produce valid, round-tripping YAML.
        for text in ('plain', 'a"b', 'a\\b', 'a\\"b"\\'):
            with self.subTest(text=text):
                deck = deckparse.parse_deck(f"title: {nd._yaml_quote(text)}\nslides:\n  - title\n")
                self.assertEqual(deck["title"], text)

    def test_starter_briefs(self):
        r = self.scaffold()
        title_path = os.path.join(r.deck_dir, "slides", "title.md")
        title = deckparse.parse_brief(_read(title_path), title_path)
        self.assertEqual(title["front_matter"]["layout"], "title")
        self.assertEqual(
            _read(os.path.join(r.deck_dir, "slides", "example-slide.md")),
            _read(os.path.join(PLUGIN_DIR, "templates", "slides", "_example.md")),
        )

    def test_gitignore(self):
        r = self.scaffold()
        self.assertEqual(_read(os.path.join(r.deck_dir, ".gitignore")), "build/\n.DS_Store\n*.swp\n*~\n")

    def test_vendored_deckparse_validates_the_deck(self):
        r = self.scaffold()
        for cmd in (["deck", "deck.yml"], ["status", "."]):
            proc = subprocess.run(
                [sys.executable, "-I", "tools/deckparse.py"] + cmd,
                cwd=r.deck_dir, capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_no_slides_md_or_content_fragments(self):
        r = self.scaffold()
        self.assertFalse(os.path.exists(os.path.join(r.deck_dir, "SLIDES.md")))
        self.assertEqual(os.listdir(os.path.join(r.deck_dir, "content")), [])


class TestRefusals(ScaffoldCase):
    def test_existing_folder_is_refused_and_untouched(self):
        existing = self.path("demo")
        os.mkdir(existing)
        keep = os.path.join(existing, "keep.txt")
        with open(keep, "w") as fh:
            fh.write("mine")
        with self.assertRaises(nd.ScaffoldError) as cm:
            self.scaffold("demo")
        self.assertIn("already exists", str(cm.exception))
        self.assertEqual(os.listdir(existing), ["keep.txt"])
        self.assertEqual(_read(keep), "mine")

    def test_empty_existing_folder_is_refused(self):
        os.mkdir(self.path("demo"))
        with self.assertRaises(nd.ScaffoldError):
            self.scaffold("demo")

    def test_existing_file_is_refused(self):
        with open(self.path("demo"), "w") as fh:
            fh.write("x")
        with self.assertRaises(nd.ScaffoldError):
            self.scaffold("demo")

    def test_invalid_names(self):
        bad = ["", " x", "x ", "-x", ".hidden", "#title", "a/b", "a\\b", "..", "a..b", "x\ny", "x" * 101]
        for name in bad:
            with self.subTest(name=name):
                with self.assertRaises(nd.ScaffoldError):
                    self.scaffold(name)
        self.assertEqual(os.listdir(self.tmp), [])

    def test_valid_names(self):
        for name in ("cloudbank-intro", "2026 kickoff", "UW_intro.v2"):
            with self.subTest(name=name):
                self.assertTrue(os.path.isdir(self.scaffold(name).deck_dir))

    def test_unknown_brand(self):
        with self.assertRaises(nd.ScaffoldError):
            self.scaffold("demo", "purple")
        self.assertEqual(os.listdir(self.tmp), [])

    def test_incomplete_plugin_is_refused_before_creating_anything(self):
        plugin = os.path.join(self.tmp, "plugin")
        shutil.copytree(
            PLUGIN_DIR, plugin,
            ignore=shutil.ignore_patterns(".git", "catalog", "fonts", "docs"),
        )
        os.remove(os.path.join(plugin, "templates", "build.sh"))
        dest = os.path.join(self.tmp, "out")
        os.mkdir(dest)
        with self.assertRaises(nd.ScaffoldError) as cm:
            nd.scaffold("demo", "cloudbank", dest=dest, plugin_dir=plugin, skip_reveal=True)
        self.assertIn("templates/build.sh", str(cm.exception))
        self.assertEqual(os.listdir(dest), [])

    def test_failure_midway_removes_the_partial_folder(self):
        def boom(deck_dir):
            raise RuntimeError("disk on fire")
        with self.assertRaises(nd.ScaffoldError) as cm:
            self.scaffold("demo", skip_reveal=False, reveal_runner=boom)
        self.assertIn("disk on fire", str(cm.exception))
        self.assertFalse(os.path.exists(self.path("demo")))

    def test_a_failure_does_not_remove_a_pre_existing_folder(self):
        os.mkdir(self.path("other"))
        with self.assertRaises(nd.ScaffoldError):
            self.scaffold("demo", skip_reveal=False, reveal_runner=lambda d: 1 / 0)
        self.assertTrue(os.path.isdir(self.path("other")))


class TestReveal(ScaffoldCase):
    def test_skip_reveal_does_not_run_it(self):
        runner = mock.Mock()
        r = self.scaffold(skip_reveal=True, reveal_runner=runner)
        runner.assert_not_called()
        self.assertIsNone(r.reveal)
        self.assertEqual(r.warnings, [])

    def test_reveal_success(self):
        r = self.scaffold(skip_reveal=False, reveal_runner=_fake_reveal(True))
        self.assertTrue(r.reveal)
        self.assertEqual(r.warnings, [])

    def test_reveal_failure_is_a_warning_not_a_failure(self):
        def failing(deck_dir):
            os.makedirs(os.path.join(deck_dir, "assets", "reveal"))  # a partial download
            return False, "Could not resolve host"
        r = self.scaffold(skip_reveal=False, reveal_runner=failing)
        self.assertFalse(r.reveal)
        self.assertTrue(os.path.isdir(r.deck_dir))
        self.assertEqual(len(r.warnings), 1)
        self.assertIn("./setup-reveal.sh", r.warnings[0])
        self.assertIn("Could not resolve host", r.warnings[0])
        self.assertFalse(os.path.exists(os.path.join(r.deck_dir, "assets", "reveal")))

    def test_default_runner_is_used_when_not_skipped(self):
        with mock.patch.object(nd, "_run_setup_reveal", return_value=(True, "")) as run:
            r = self.scaffold(skip_reveal=False)
        run.assert_called_once_with(r.deck_dir)
        self.assertTrue(r.reveal)

    def _deck_with_script(self, body):
        deck = self.path("fake-deck")
        os.mkdir(deck)
        with open(os.path.join(deck, "setup-reveal.sh"), "w") as fh:
            fh.write(body)
        return deck

    def test_runner_reports_a_failing_script(self):
        deck = self._deck_with_script("#!/bin/bash\necho 'curl: (6) Could not resolve host' >&2\nexit 6\n")
        ok, reason = nd._run_setup_reveal(deck)
        self.assertFalse(ok)
        self.assertIn("Could not resolve host", reason)

    def test_runner_reports_a_missing_script(self):
        deck = self.path("empty-deck")
        os.mkdir(deck)
        ok, _ = nd._run_setup_reveal(deck)
        self.assertFalse(ok)

    def test_runner_checks_the_downloaded_files(self):
        deck = self._deck_with_script("#!/bin/bash\nexit 0\n")
        ok, reason = nd._run_setup_reveal(deck)
        self.assertFalse(ok)
        self.assertIn("reveal.min.js", reason)

    def test_runner_success(self):
        script = (
            "#!/bin/bash\nmkdir -p assets/reveal/plugin/notes\n"
            "touch assets/reveal/reveal.min.js assets/reveal/reveal.min.css "
            "assets/reveal/plugin/notes/notes.js\n"
        )
        ok, reason = nd._run_setup_reveal(self._deck_with_script(script))
        self.assertTrue(ok, reason)

    def test_runner_timeout(self):
        deck = self._deck_with_script("#!/bin/bash\nsleep 5\n")
        with mock.patch.object(nd, "REVEAL_TIMEOUT", 0.2):
            ok, reason = nd._run_setup_reveal(deck)
        self.assertFalse(ok)
        self.assertIn("timed out", reason)


class TestManagedFilesStayInSync(unittest.TestCase):
    def test_matches_update_deck_skill(self):
        """update-deck's "Managed files" list must equal the scaffold's table."""
        text = _read(os.path.join(PLUGIN_DIR, "skills", "update-deck", "SKILL.md"))
        lines = text.split("\n")
        start = next(i for i, l in enumerate(lines) if l.startswith("**Managed files**"))
        listed = []
        for line in lines[start + 1:]:
            m = re.match(r"^- `([^`]+)`", line)
            if m:
                listed.append(m.group(1))
            elif listed and not line.strip():
                break
        self.assertEqual(sorted(listed), nd.managed_files())


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="new-deck-cli-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-I", NEW_DECK, *args],
            cwd=self.tmp, capture_output=True, text=True,
        )

    def test_scaffold_then_refuse(self):
        first = self.run_cli("demo", "--brand=cloudbank", "--skip-reveal")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("Created cloudbank deck", first.stdout)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "demo", "deck.yml")))
        second = self.run_cli("demo", "--skip-reveal")
        self.assertEqual(second.returncode, 1)
        self.assertIn("already exists", second.stderr)

    def test_default_brand_is_uw(self):
        self.assertEqual(self.run_cli("demo", "--skip-reveal").returncode, 0)
        self.assertEqual(_read(os.path.join(self.tmp, "demo", ".brand")), "uw\n")

    def test_long_brand_name_is_accepted(self):
        self.assertEqual(self.run_cli("demo", "--brand=cloudbank-brand", "--skip-reveal").returncode, 0)
        self.assertEqual(_read(os.path.join(self.tmp, "demo", ".brand")), "cloudbank\n")

    def test_usage_errors_exit_2(self):
        self.assertEqual(self.run_cli().returncode, 2)
        self.assertEqual(self.run_cli("demo", "--brand=purple").returncode, 2)
        self.assertEqual(os.listdir(self.tmp), [])

    def test_invalid_name_exits_1(self):
        proc = self.run_cli("a/b", "--skip-reveal")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("✗", proc.stderr)


if __name__ == "__main__":
    unittest.main()
