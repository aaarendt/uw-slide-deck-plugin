#!/usr/bin/env python3
"""Tests for tools/resolve-catalog.py (stdlib only)."""

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest

# Locate plugin root relative to this file
PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_DIR = os.path.join(PLUGIN_DIR, "catalog")

# resolve-catalog.py has a hyphen so cannot be imported normally.
# Also ensure deckparse is importable (resolve-catalog.py does the same).
sys.path.insert(0, os.path.join(PLUGIN_DIR, "tools"))
_spec = importlib.util.spec_from_file_location(
    "resolve_catalog",
    os.path.join(PLUGIN_DIR, "tools", "resolve-catalog.py"),
)
rc = importlib.util.module_from_spec(_spec)
sys.modules["resolve_catalog"] = rc
_spec.loader.exec_module(rc)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _make_deck(root, slides_yaml, briefs):
    """Scaffold a minimal deck for testing.
    slides_yaml: list of IDs (strings)
    briefs: dict of id -> brief text (markdown)
    """
    _write(os.path.join(root, "deck.yml"),
           'title: "Test Deck"\n'
           'slides:\n' +
           "".join(f"  - {sid}\n" for sid in slides_yaml))
    for sid, text in briefs.items():
        _write(os.path.join(root, "slides", sid + ".md"), text)
    os.makedirs(os.path.join(root, "content"), exist_ok=True)


def _make_catalog(root):
    """Copy the plugin catalog into a temp directory and return its path."""
    dst = os.path.join(root, "catalog")
    shutil.copytree(CATALOG_DIR, dst)
    return dst


# ---------------------------------------------------------------------------
# Tests for _substitute_params
# ---------------------------------------------------------------------------

class TestSubstituteParams(unittest.TestCase):

    def test_simple_substitution(self):
        result = rc._substitute_params("Hello {{name}}!", {"name": "World"})
        self.assertEqual(result, "Hello World!")

    def test_html_escaping(self):
        result = rc._substitute_params("{{val}}", {"val": "<script>alert('x')</script>"})
        self.assertIn("&lt;script&gt;", result)
        self.assertNotIn("<script>", result)

    def test_missing_param_empty_string(self):
        result = rc._substitute_params("{{missing}}", {})
        self.assertEqual(result, "")

    def test_multiple_params(self):
        result = rc._substitute_params("{{a}} and {{b}}", {"a": "X", "b": "Y"})
        self.assertEqual(result, "X and Y")

    def test_ampersand_escaping(self):
        result = rc._substitute_params("{{val}}", {"val": "A & B"})
        self.assertEqual(result, "A &amp; B")


# ---------------------------------------------------------------------------
# Tests for _rewrite_data_slide
# ---------------------------------------------------------------------------

class TestRewriteDataSlide(unittest.TestCase):

    def test_rewrites_attribute(self):
        fragment = '<section data-slide="uw-title" class="slide">'
        result = rc._rewrite_data_slide(fragment, "uw-title", "my-title")
        self.assertIn('data-slide="my-title"', result)
        self.assertNotIn('data-slide="uw-title"', result)

    def test_rewrites_css_selector(self):
        fragment = 'section[data-slide="uw-title"] { color: red; }'
        result = rc._rewrite_data_slide(fragment, "uw-title", "my-title")
        self.assertIn('section[data-slide="my-title"]', result)
        self.assertNotIn('section[data-slide="uw-title"]', result)

    def test_rewrites_single_quoted_attribute(self):
        fragment = "<section data-slide='uw-title' class='slide'>"
        result = rc._rewrite_data_slide(fragment, "uw-title", "my-title")
        self.assertIn("my-title", result)


# ---------------------------------------------------------------------------
# Tests for _inject_data_catalog
# ---------------------------------------------------------------------------

class TestInjectDataCatalog(unittest.TestCase):

    def test_adds_attribute(self):
        fragment = '<section data-slide="s" class="slide">'
        result = rc._inject_data_catalog(fragment, "uw-title", "1.0.0")
        self.assertIn('data-catalog="uw-title@1.0.0"', result)

    def test_updates_existing_attribute(self):
        fragment = '<section data-slide="s" data-catalog="uw-title@0.9.0" class="slide">'
        result = rc._inject_data_catalog(fragment, "uw-title", "1.0.0")
        self.assertIn('data-catalog="uw-title@1.0.0"', result)
        self.assertNotIn("0.9.0", result)

    def test_only_patches_first_section(self):
        fragment = '<section data-slide="s1" class="slide"></section><section data-slide="s2">'
        result = rc._inject_data_catalog(fragment, "x", "1.0.0")
        # Only the first section should be patched
        count = result.count("data-catalog=")
        self.assertEqual(count, 1)


# ---------------------------------------------------------------------------
# Tests for _load_catalog_slide_meta
# ---------------------------------------------------------------------------

class TestLoadCatalogSlideMeta(unittest.TestCase):

    def test_loads_uw_title(self):
        meta = rc._load_catalog_slide_meta(CATALOG_DIR, "uw-title")
        self.assertEqual(meta["id"], "uw-title")
        self.assertEqual(meta["kind"], "parameterized")
        self.assertIn("title", meta["params"])

    def test_loads_land_ack(self):
        meta = rc._load_catalog_slide_meta(CATALOG_DIR, "land-ack")
        self.assertEqual(meta["kind"], "verbatim")

    def test_loads_agenda(self):
        meta = rc._load_catalog_slide_meta(CATALOG_DIR, "agenda")
        self.assertEqual(meta["kind"], "derived")

    def test_missing_slide_raises(self):
        with self.assertRaises(FileNotFoundError):
            rc._load_catalog_slide_meta(CATALOG_DIR, "nonexistent-slide")


# ---------------------------------------------------------------------------
# Integration: resolve
# ---------------------------------------------------------------------------

class TestResolveIntegration(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="uw-test-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _resolve(self):
        return rc.cmd_resolve(self.tmpdir, CATALOG_DIR)

    def test_no_catalog_slides_exits_zero(self):
        _make_deck(self.tmpdir, ["title"], {
            "title": "---\nid: title\nlayout: title\n---\n\n# Key message\nHello\n",
        })
        result = self._resolve()
        self.assertEqual(result, 0)

    def test_resolves_uw_title(self):
        _make_deck(self.tmpdir, ["title"], {
            "title": (
                "---\n"
                "id: title\n"
                "use: catalog/uw-title\n"
                "params:\n"
                "  title: My Great Talk\n"
                "  presenter: Jane Doe\n"
                "---\n"
            ),
        })
        result = self._resolve()
        self.assertEqual(result, 0)
        out = _read(os.path.join(self.tmpdir, "content", "title.html"))
        self.assertIn('data-slide="title"', out)
        self.assertIn("My Great Talk", out)
        self.assertIn("Jane Doe", out)
        self.assertIn('data-catalog="uw-title@1.0.0"', out)
        # catalog ID must NOT appear as data-slide
        self.assertNotIn('data-slide="uw-title"', out)
        # aria-label should include slide number
        self.assertIn("Slide 1:", out)

    def test_resolves_verbatim_land_ack(self):
        _make_deck(self.tmpdir, ["land-ack"], {
            "land-ack": "---\nid: land-ack\nuse: catalog/land-ack\n---\n",
        })
        result = self._resolve()
        self.assertEqual(result, 0)
        out = _read(os.path.join(self.tmpdir, "content", "land-ack.html"))
        self.assertIn('data-slide="land-ack"', out)
        self.assertIn('data-catalog="land-ack@1.0.0"', out)

    def test_param_html_escaping(self):
        _make_deck(self.tmpdir, ["title"], {
            "title": (
                "---\n"
                "id: title\n"
                "use: catalog/uw-title\n"
                "params:\n"
                '  title: "A & B <test>"\n'
                "---\n"
            ),
        })
        self._resolve()
        out = _read(os.path.join(self.tmpdir, "content", "title.html"))
        self.assertIn("A &amp; B", out)
        self.assertNotIn("<test>", out)

    def test_resolves_agenda_derived(self):
        _make_deck(self.tmpdir, ["agenda", "intro", "closing"], {
            "agenda": "---\nid: agenda\nuse: catalog/agenda\n---\n",
            "intro": (
                "---\nid: intro\nlayout: key-message\ntitle: Introduction\nduration: 5\n---\n\n"
                "# Key message\nWelcome\n"
            ),
            "closing": (
                "---\nid: closing\nlayout: closing\ntitle: Wrap up\nduration: 2\n---\n\n"
                "# Key message\nThanks\n"
            ),
        })
        result = self._resolve()
        self.assertEqual(result, 0)
        out = _read(os.path.join(self.tmpdir, "content", "agenda.html"))
        # Content slide appears; agenda_items must be raw HTML (not escaped)
        self.assertIn("<li>Introduction", out)
        self.assertIn("5 min", out)
        self.assertNotIn("&lt;li&gt;", out)
        # Structural slides are excluded: closing should not appear
        self.assertNotIn("Wrap up", out)

    def test_resolves_funding_with_defaults(self):
        _make_deck(self.tmpdir, ["funding"], {
            "funding": "---\nid: funding\nuse: catalog/funding\n---\n",
        })
        result = self._resolve()
        self.assertEqual(result, 0)
        out = _read(os.path.join(self.tmpdir, "content", "funding.html"))
        self.assertIn("PLACEHOLDER AGENCY", out)

    def test_resolves_multiple_catalog_slides(self):
        _make_deck(self.tmpdir, ["title", "land-ack", "thank-you"], {
            "title": "---\nid: title\nuse: catalog/uw-title\n---\n",
            "land-ack": "---\nid: land-ack\nuse: catalog/land-ack\n---\n",
            "thank-you": "---\nid: thank-you\nuse: catalog/thank-you\n---\n",
        })
        result = self._resolve()
        self.assertEqual(result, 0)
        for sid in ("title", "land-ack", "thank-you"):
            out_path = os.path.join(self.tmpdir, "content", sid + ".html")
            self.assertTrue(os.path.isfile(out_path), f"content/{sid}.html not created")
            out = _read(out_path)
            self.assertIn(f'data-slide="{sid}"', out)

    def test_css_selectors_rewritten(self):
        _make_deck(self.tmpdir, ["title"], {
            "title": "---\nid: title\nuse: catalog/uw-title\n---\n",
        })
        self._resolve()
        out = _read(os.path.join(self.tmpdir, "content", "title.html"))
        # CSS selectors must use deck slide ID, not catalog ID
        self.assertIn('section[data-slide="title"]', out)
        self.assertNotIn('section[data-slide="uw-title"]', out)

    def test_missing_catalog_returns_nonzero(self):
        _make_deck(self.tmpdir, ["title"], {
            "title": "---\nid: title\nuse: catalog/uw-title\n---\n",
        })
        result = rc.cmd_resolve(self.tmpdir, "/nonexistent/catalog/path")
        self.assertNotEqual(result, 0)

    def test_unknown_catalog_slide_id_fails(self):
        _make_deck(self.tmpdir, ["mystery"], {
            "mystery": "---\nid: mystery\nuse: catalog/does-not-exist\n---\n",
        })
        result = rc.cmd_resolve(self.tmpdir, CATALOG_DIR)
        self.assertNotEqual(result, 0)


# ---------------------------------------------------------------------------
# Integration: eject
# ---------------------------------------------------------------------------

class TestEjectIntegration(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="uw-test-eject-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _eject(self, sid):
        return rc.cmd_eject(self.tmpdir, sid, CATALOG_DIR)

    def _setup_slide(self, sid, brief_text):
        _write(os.path.join(self.tmpdir, "slides", sid + ".md"), brief_text)
        _write(os.path.join(self.tmpdir, "content", sid + ".html"),
               f'<section data-slide="{sid}" class="slide"><p>content</p></section>')

    def test_eject_removes_use_and_adds_locked(self):
        self._setup_slide("title",
            "---\nid: title\nuse: catalog/uw-title\nparams:\n  presenter: Jane\n---\n")
        result = self._eject("title")
        self.assertEqual(result, 0)
        brief = _read(os.path.join(self.tmpdir, "slides", "title.md"))
        self.assertNotIn("use:", brief)
        self.assertIn("locked: true", brief)
        self.assertIn("# Key message", brief)

    def test_eject_keeps_html_unchanged(self):
        original_html = '<section data-slide="title" class="slide"><p>original</p></section>'
        self._setup_slide("title",
            "---\nid: title\nuse: catalog/uw-title\n---\n")
        _write(os.path.join(self.tmpdir, "content", "title.html"), original_html)
        self._eject("title")
        out = _read(os.path.join(self.tmpdir, "content", "title.html"))
        self.assertEqual(out, original_html)

    def test_eject_no_use_field_errors(self):
        self._setup_slide("title",
            "---\nid: title\nlayout: title\n---\n\n# Key message\nHello\n")
        result = self._eject("title")
        self.assertNotEqual(result, 0)

    def test_eject_missing_brief_errors(self):
        result = self._eject("nonexistent")
        self.assertNotEqual(result, 0)

    def test_eject_removes_params_block(self):
        self._setup_slide("title",
            "---\nid: title\nuse: catalog/uw-title\nparams:\n  title: Hello\n  presenter: Jane\n---\n")
        self._eject("title")
        brief = _read(os.path.join(self.tmpdir, "slides", "title.md"))
        self.assertNotIn("params:", brief)


# ---------------------------------------------------------------------------
# Tests for catalog slide HTML validity
# ---------------------------------------------------------------------------

class TestCatalogSlideHtml(unittest.TestCase):
    """Sanity-check the catalog slide HTML files."""

    def _load(self, catalog_id):
        path = os.path.join(CATALOG_DIR, "slides", catalog_id, "slide.html")
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    def _check_slide(self, catalog_id):
        content = self._load(catalog_id)
        self.assertIn(f'data-slide="{catalog_id}"', content,
                      f"{catalog_id}: data-slide must equal catalog ID in template")
        self.assertIn(f'section[data-slide="{catalog_id}"]', content,
                      f"{catalog_id}: CSS selector must use catalog ID")
        self.assertIn("class=\"slide\"", content,
                      f"{catalog_id}: must have class='slide'")
        self.assertIn("::before", content,
                      f"{catalog_id}: must have gold accent bar (::before)")

    def test_uw_title_html(self):
        self._check_slide("uw-title")

    def test_land_ack_html(self):
        self._check_slide("land-ack")

    def test_funding_html(self):
        self._check_slide("funding")

    def test_agenda_html(self):
        self._check_slide("agenda")

    def test_feedback_html(self):
        self._check_slide("feedback")

    def test_thank_you_html(self):
        self._check_slide("thank-you")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
