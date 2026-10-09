#!/usr/bin/env python3
"""Tests for deckparse.py. Run: python3 tools/test_deckparse.py"""

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deckparse as dp  # noqa: E402

FIXTURES = os.path.join(HERE, "tests", "fixtures")
UPDATE = os.environ.get("UPDATE_FIXTURES") == "1"


def read(*parts):
    with open(os.path.join(FIXTURES, *parts), encoding="utf-8") as fh:
        return fh.read()


def load_cases(name):
    """Split a .cases file into (case_name, line, substring, content)."""
    cases, cur = [], None
    for row in read("invalid", name).split("\n"):
        if row.startswith("### "):
            cname, line, sub = [p.strip() for p in row[4:].split("|", 2)]
            cur = [cname, None if line == "-" else int(line), sub, []]
            cases.append(cur)
        elif cur is not None:
            cur[3].append(row)
    return [(c[0], c[1], c[2], "\n".join(c[3]) + "\n") for c in cases]


class ValidFixtures(unittest.TestCase):
    def check(self, fixture, actual):
        expected_path = os.path.join(FIXTURES, "valid", fixture.rsplit(".", 1)[0] + ".json")
        rendered = json.dumps(actual, indent=2, ensure_ascii=False) + "\n"
        if UPDATE:
            with open(expected_path, "w", encoding="utf-8") as fh:
                fh.write(rendered)
        self.assertEqual(rendered, read("valid", os.path.basename(expected_path)))

    def test_subset_edge_cases(self):
        data, _ = dp.parse_subset(read("valid", "subset-edge.yml"), "subset-edge.yml")
        self.check("subset-edge.yml", data)

    def test_deck_full(self):
        self.check("deck-full.yml", dp.parse_deck(read("valid", "deck-full.yml"), "deck-full.yml"))

    def test_deck_minimal(self):
        self.check("deck-minimal.yml", dp.parse_deck(read("valid", "deck-minimal.yml"), "deck-minimal.yml"))

    def test_brief_full(self):
        brief = dp.parse_brief(read("valid", "brief-full.md"), "brief-full.md")
        brief["hash"] = dp.brief_hash(brief)
        self.check("brief-full.md", brief)

    def test_brief_catalog(self):
        brief = dp.parse_brief(read("valid", "brief-catalog.md"), "brief-catalog.md")
        brief["hash"] = dp.brief_hash(brief)
        self.check("brief-catalog.md", brief)

    def test_types(self):
        data, _ = dp.parse_subset(read("valid", "subset-edge.yml"))
        for k in ("yes_string", "no_string", "on_string", "off_string"):
            self.assertIsInstance(data[k], str)
        self.assertEqual(data["quoted_number"], "007")
        self.assertIs(data["flag"], True)
        self.assertIsNone(data["empty_value"])
        self.assertEqual(data["empty_list"], [])
        self.assertEqual(data["tags"], ["first", "second: quoted", 3])

    def test_crlf_and_bom(self):
        text = "\ufefftitle: T\r\nslides:\r\n  - a\r\n"
        self.assertEqual(dp.parse_deck(text)["slides"], ["a"])


class InvalidCases(unittest.TestCase):
    def run_cases(self, filename, parse):
        for name, line, sub, content in load_cases(filename):
            with self.subTest(case=name):
                with self.assertRaises(dp.DeckParseError) as cm:
                    parse(content)
                err = cm.exception
                self.assertIn(sub, err.message)
                self.assertEqual(err.line, line, f"{err}")
                self.assertTrue(str(err).startswith("x"), str(err))

    def test_subset(self):
        self.run_cases("subset.cases", lambda t: dp.parse_subset(t, "x.yml"))

    def test_deck(self):
        self.run_cases("deck.cases", lambda t: dp.parse_deck(t, "x.yml"))

    def test_brief(self):
        self.run_cases("brief.cases", lambda t: dp.parse_brief(t, "x.md"))


class Hash(unittest.TestCase):
    BASE = "---\nid: x\nlayout: two-column\nparams:\n  eyebrow: A\n---\n# Key message\nHello\n\n## Talking points\n- a\n- b\n"

    def h(self, text):
        return dp.brief_hash(dp.parse_brief(text, "x.md"))

    def test_stable_across_whitespace_and_defaults(self):
        base = self.h(self.BASE)
        noisy = self.BASE.replace("Hello", "Hello   ").replace("\n\n## Talking", "\n\n\n\n## Talking")
        noisy = noisy.replace("\n", "\r\n")
        self.assertEqual(base, self.h(noisy))
        self.assertEqual(self.h("---\nid: x\n---\n# Key message\nHi\n"),
                         self.h("---\nid: x\nlayout: auto\nparams:\n---\n# Key message\nHi\n"))

    def test_ignores_workflow_fields_and_notes(self):
        base = self.h(self.BASE)
        edited = self.BASE.replace("id: x\n", "id: x\nowner: sam\nstatus: done\nlocked: true\nduration: 3\n"
                                   "section: S\nlayout_rationale: why\nobjective: o1\n") + "\n## Notes\nnew\n"
        self.assertEqual(base, self.h(edited))

    def test_changes_with_content(self):
        base = self.h(self.BASE)
        for old, new in [("Hello", "Hullo"), ("- b", "- c"), ("eyebrow: A", "eyebrow: B"),
                         ("two-column", "title")]:
            self.assertNotEqual(base, self.h(self.BASE.replace(old, new)), old)
        self.assertNotEqual(base, self.h(self.BASE + "\n## Source\ns\n"))
        self.assertNotEqual(base, self.h(self.BASE + "\n## Slot: left\ns\n"))

    def test_format(self):
        h = self.h(self.BASE)
        self.assertRegex(h, r"^[0-9a-f]{12}$")


class Templates(unittest.TestCase):
    ROOT = os.path.dirname(HERE)

    def test_templates_parse(self):
        with open(os.path.join(self.ROOT, "templates", "deck.yml"), encoding="utf-8") as fh:
            deck = dp.parse_deck(fh.read(), "deck.yml")
        self.assertEqual(deck["slides"], ["title", "example-slide"])
        path = os.path.join(self.ROOT, "templates", "slides", "_example.md")
        with open(path, encoding="utf-8") as fh:
            brief = dp.parse_brief(fh.read(), path)
        self.assertEqual(brief["front_matter"]["id"], "example-slide")

    def test_underscore_files_skip_name_check(self):
        text = "---\nid: other\n---\n# Key message\nHi\n"
        dp.parse_brief(text, "slides/_tmpl.md")
        with self.assertRaises(dp.DeckParseError):
            dp.parse_brief(text, "slides/tmpl.md")


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(HERE, "deckparse.py"), *args],
                              capture_output=True, text=True)

    def test_ids(self):
        r = self.run_cli("deck", os.path.join(FIXTURES, "valid", "deck-full.yml"), "--format", "ids")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.split(), ["title", "02-what-is-cloud", "demo"])

    def test_kv(self):
        r = self.run_cli("brief", os.path.join(FIXTURES, "valid", "brief-full.md"), "--format", "kv")
        self.assertEqual(r.returncode, 0)
        self.assertIn("params.eyebrow=WHY", r.stdout.split("\n"))
        self.assertIn("objective=obj-1,obj-2", r.stdout.split("\n"))
        self.assertIn("locked=false", r.stdout.split("\n"))

    def test_hash_matches_json(self):
        path = os.path.join(FIXTURES, "valid", "brief-full.md")
        h = self.run_cli("hash", path).stdout.strip()
        self.assertEqual(h, json.loads(self.run_cli("brief", path).stdout)["hash"])

    def test_error_exit_code_and_message(self):
        with self.subTest("parse error"):
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, "deck.yml")
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write("title: T\nslides:\n  - a\n  - a\n")
                r = self.run_cli("deck", p)
                self.assertEqual(r.returncode, 1)
                self.assertEqual(r.stderr.strip(), f"{p}:4: duplicate slide ID 'a'")
        with self.subTest("missing file"):
            self.assertEqual(self.run_cli("deck", "/nonexistent/deck.yml").returncode, 1)
        with self.subTest("usage"):
            self.assertEqual(self.run_cli("deck").returncode, 2)
            self.assertEqual(self.run_cli("deck", "f", "--format", "kv").returncode, 2)


if __name__ == "__main__":
    unittest.main()
