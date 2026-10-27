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
        self.assertIn('<li><span class="label">Introduction</span>', out)
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
# Tests for _strip_empty_para_elements
# ---------------------------------------------------------------------------

class TestStripEmptyParaElements(unittest.TestCase):

    def test_removes_empty_href_link(self):
        html = '<p class="url"><a href=""></a></p>'
        self.assertEqual(rc._strip_empty_para_elements(html), "")

    def test_removes_empty_href_link_with_text(self):
        # href="" is a broken link regardless of label text
        html = '<p class="url-line"><a href="" class="survey-link">feedback survey</a></p>'
        self.assertEqual(rc._strip_empty_para_elements(html), "")

    def test_removes_bare_mailto_with_no_text(self):
        html = '<p class="email"><a href="mailto:"></a></p>'
        self.assertEqual(rc._strip_empty_para_elements(html), "")

    def test_keeps_mailto_with_address(self):
        html = '<p class="email"><a href="mailto:a@b.com">a@b.com</a></p>'
        result = rc._strip_empty_para_elements(html)
        self.assertIn("a@b.com", result)

    def test_keeps_real_url(self):
        html = '<p class="url"><a href="https://example.com">https://example.com</a></p>'
        result = rc._strip_empty_para_elements(html)
        self.assertIn("example.com", result)

    def test_removes_whitespace_only_para(self):
        html = '<p class="url-text">   </p>'
        self.assertEqual(rc._strip_empty_para_elements(html).strip(), "")

    def test_removes_truly_empty_para(self):
        html = '<p class="url-text"></p>'
        self.assertEqual(rc._strip_empty_para_elements(html), "")

    def test_leaves_para_with_content(self):
        html = '<p class="presenter">Jane Doe</p>'
        self.assertEqual(rc._strip_empty_para_elements(html), html)


# ---------------------------------------------------------------------------
# Integration: thank-you empty params strip links
# ---------------------------------------------------------------------------

class TestThankYouEmptyParams(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="uw-test-thankyou-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _resolve(self):
        return rc.cmd_resolve(self.tmpdir, CATALOG_DIR)

    def test_empty_email_strips_link_element(self):
        _make_deck(self.tmpdir, ["ty"], {
            "ty": (
                "---\n"
                "id: ty\n"
                "use: catalog/thank-you\n"
                "params:\n"
                "  message: Thank you\n"
                "  presenter: Jane Doe\n"
                "  email: \"\"\n"
                "  url: https://example.com\n"
                "---\n"
            ),
        })
        self.assertEqual(self._resolve(), 0)
        out = _read(os.path.join(self.tmpdir, "content", "ty.html"))
        # The <p class="email"> element must be absent — check for the HTML tag,
        # not the string "mailto:" which also appears inside the CSS :has() selector.
        self.assertNotIn('<p class="email">', out)

    def test_empty_url_strips_link_element(self):
        _make_deck(self.tmpdir, ["ty"], {
            "ty": (
                "---\n"
                "id: ty\n"
                "use: catalog/thank-you\n"
                "params:\n"
                "  message: Thank you\n"
                "  presenter: Jane Doe\n"
                "  email: user@example.com\n"
                "  url: \"\"\n"
                "---\n"
            ),
        })
        self.assertEqual(self._resolve(), 0)
        out = _read(os.path.join(self.tmpdir, "content", "ty.html"))
        # The <p class="url"> element must be absent — check for the HTML tag,
        # not 'href=""' which also appears inside the CSS :has() selector.
        self.assertNotIn('<p class="url">', out)
        # Provided email must survive
        self.assertIn("user@example.com", out)


# ---------------------------------------------------------------------------
# Integration: feedback empty url strips link and text
# ---------------------------------------------------------------------------

class TestFeedbackEmptyUrl(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="uw-test-feedback-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_empty_url_strips_link_and_text_paras(self):
        _make_deck(self.tmpdir, ["fb"], {
            "fb": (
                "---\n"
                "id: fb\n"
                "use: catalog/feedback\n"
                "params:\n"
                '  url: ""\n'
                "---\n"
            ),
        })
        self.assertEqual(rc.cmd_resolve(self.tmpdir, CATALOG_DIR), 0)
        out = _read(os.path.join(self.tmpdir, "content", "fb.html"))
        # Check for the HTML elements, not 'href=""' which also appears in the
        # CSS :has() selector.  Both <p> wrappers must be stripped by the resolver.
        self.assertNotIn('<p class="url-line">', out)
        self.assertNotIn('<p class="url-text">', out)


# ---------------------------------------------------------------------------
# Tests for asset path rewrite (fix 3)
# ---------------------------------------------------------------------------

class TestAssetPathRewrite(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="uw-test-assets-")
        # Build a minimal catalog with an assets/ dir
        self.catalog_dir = os.path.join(self.tmpdir, "catalog")
        slide_dir = os.path.join(self.catalog_dir, "slides", "mock-asset")
        os.makedirs(slide_dir, exist_ok=True)
        # Write catalog.yml
        _write(os.path.join(self.catalog_dir, "catalog.yml"),
               "slides:\n  - id: mock-asset\n")
        # Write slide.md
        _write(os.path.join(slide_dir, "slide.md"),
               "---\n"
               "id: mock-asset\n"
               "description: Test slide with assets\n"
               "kind: parameterized\n"
               "brand: any\n"
               "version: 1.0.0\n"
               "status: stable\n"
               "owner: test\n"
               "params:\n"
               "  logo_url: https://example.com/assets/logo.png\n"
               "---\n")
        # Write slide.html — one real asset ref + one param that contains "assets/"
        _write(os.path.join(slide_dir, "slide.html"),
               '<section data-slide="mock-asset" aria-label="{{aria-label}}" class="slide">\n'
               '  <img src="assets/logo.png" alt="logo">\n'
               '  <a href="{{logo_url}}">link</a>\n'
               '  <style>\n'
               '    section[data-slide="mock-asset"] { background: url(\'assets/bg.png\'); }\n'
               '  </style>\n'
               '</section>\n')
        # Create actual assets dir so the copy branch runs
        assets_src = os.path.join(slide_dir, "assets")
        os.makedirs(assets_src)
        _write(os.path.join(assets_src, "logo.png"), "PNG")
        # Create deck
        self.deck_dir = os.path.join(self.tmpdir, "deck")
        _make_deck(self.deck_dir, ["mock"], {
            "mock": "---\nid: mock\nuse: catalog/mock-asset\n---\n",
        })

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_src_and_css_url_are_rewritten(self):
        rc.cmd_resolve(self.deck_dir, self.catalog_dir)
        out = _read(os.path.join(self.deck_dir, "content", "mock.html"))
        self.assertIn('src="../assets/images/catalog-mock-asset/logo.png"', out)
        self.assertIn("url('../assets/images/catalog-mock-asset/bg.png')", out)

    def test_param_url_containing_assets_is_not_mangled(self):
        rc.cmd_resolve(self.deck_dir, self.catalog_dir)
        out = _read(os.path.join(self.deck_dir, "content", "mock.html"))
        # The logo_url param value "https://example.com/assets/logo.png"
        # must arrive verbatim — not rewritten
        self.assertIn("https://example.com/assets/logo.png", out)


# ---------------------------------------------------------------------------
# Tests for brand compatibility check (fix 4)
# ---------------------------------------------------------------------------

class TestBrandCompatibility(unittest.TestCase):

    def test_norm_brand_strips_suffix(self):
        self.assertEqual(rc._norm_brand("uw-brand"), "uw")
        self.assertEqual(rc._norm_brand("cloudbank-brand"), "cloudbank")
        self.assertEqual(rc._norm_brand("uw"), "uw")
        self.assertEqual(rc._norm_brand("cloudbank"), "cloudbank")
        self.assertEqual(rc._norm_brand(""), "")
        self.assertEqual(rc._norm_brand(None), "")

    def test_brands_match_any(self):
        self.assertTrue(rc._brands_match("any", "uw"))
        self.assertTrue(rc._brands_match("any", "uw-brand"))
        self.assertTrue(rc._brands_match("any", "cloudbank"))

    def test_brands_match_short_form(self):
        # new-deck writes short form in both .uw-slides.json and .brand
        self.assertTrue(rc._brands_match("uw", "uw"))
        self.assertFalse(rc._brands_match("uw", "cloudbank"))
        self.assertTrue(rc._brands_match("cloudbank", "cloudbank"))
        self.assertFalse(rc._brands_match("cloudbank", "uw"))

    def test_brands_match_long_form(self):
        # older .uw-slides.json may write the long form
        self.assertTrue(rc._brands_match("uw-brand", "uw-brand"))
        self.assertFalse(rc._brands_match("uw-brand", "cloudbank-brand"))

    def test_brands_match_mixed_forms(self):
        # short catalog brand vs long deck brand and vice versa must both work
        self.assertTrue(rc._brands_match("uw", "uw-brand"))
        self.assertTrue(rc._brands_match("uw-brand", "uw"))
        self.assertFalse(rc._brands_match("uw", "cloudbank-brand"))
        self.assertFalse(rc._brands_match("uw-brand", "cloudbank"))


class TestBrandMismatchWarning(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="uw-test-brand-")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_uw_slide_in_cloudbank_deck_warns(self):
        _make_deck(self.tmpdir, ["title"], {
            "title": "---\nid: title\nuse: catalog/uw-title\n---\n",
        })
        # new-deck writes the short form in .uw-slides.json
        _write(os.path.join(self.tmpdir, ".uw-slides.json"),
               '{"plugin_version": "0.2.0", "brand": "cloudbank", '
               '"scaffolded_at": "2026-01-01", "catalog": null}')
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc.cmd_resolve(self.tmpdir, CATALOG_DIR)
        self.assertIn("may render incorrectly", buf.getvalue())

    def test_uw_slide_in_uw_deck_no_brand_warning(self):
        _make_deck(self.tmpdir, ["title"], {
            "title": "---\nid: title\nuse: catalog/uw-title\n---\n",
        })
        # Short form stamp — what new-deck actually writes
        _write(os.path.join(self.tmpdir, ".uw-slides.json"),
               '{"plugin_version": "0.2.0", "brand": "uw", '
               '"scaffolded_at": "2026-01-01", "catalog": null}')
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc.cmd_resolve(self.tmpdir, CATALOG_DIR)
        self.assertNotIn("may render incorrectly", buf.getvalue())

    def test_uw_slide_in_uw_deck_long_form_no_warning(self):
        # Older decks may have the long form in .uw-slides.json — must not warn
        _make_deck(self.tmpdir, ["title"], {
            "title": "---\nid: title\nuse: catalog/uw-title\n---\n",
        })
        _write(os.path.join(self.tmpdir, ".uw-slides.json"),
               '{"plugin_version": "0.2.0", "brand": "uw-brand", '
               '"scaffolded_at": "2026-01-01", "catalog": null}')
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc.cmd_resolve(self.tmpdir, CATALOG_DIR)
        self.assertNotIn("may render incorrectly", buf.getvalue())

    def test_brand_read_from_dot_brand_file(self):
        # Older decks have a .brand file but no .uw-slides.json
        _make_deck(self.tmpdir, ["title"], {
            "title": "---\nid: title\nuse: catalog/uw-title\n---\n",
        })
        _write(os.path.join(self.tmpdir, ".brand"), "cloudbank\n")
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc.cmd_resolve(self.tmpdir, CATALOG_DIR)
        self.assertIn("may render incorrectly", buf.getvalue())

    def test_no_brand_files_defaults_to_uw_no_warning(self):
        # Deck with no .uw-slides.json and no .brand defaults to uw — no spurious warning
        _make_deck(self.tmpdir, ["title"], {
            "title": "---\nid: title\nuse: catalog/uw-title\n---\n",
        })
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc.cmd_resolve(self.tmpdir, CATALOG_DIR)
        self.assertNotIn("may render incorrectly", buf.getvalue())


# ---------------------------------------------------------------------------
# Tests for the derived agenda: exclusions, grouping, labels, fit
# ---------------------------------------------------------------------------

def _brief(sid, fm="", key_message="x"):
    """A minimal valid brief; fm is extra front matter lines."""
    body = f"\n# Key message\n{key_message}\n" if key_message else ""
    return f"---\nid: {sid}\n{fm}---\n{body}"


class TestAgenda(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _agenda(self, order, briefs):
        """Resolve a deck whose first slide is the agenda.

        Returns (labels, list_class, stderr, html)."""
        import contextlib
        import io
        import re
        briefs = dict(briefs)
        briefs["agenda"] = "---\nid: agenda\nuse: catalog/agenda\n---\n"
        _make_deck(self.tmpdir, ["agenda"] + order, briefs)
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf), contextlib.redirect_stdout(io.StringIO()):
            rc.cmd_resolve(self.tmpdir, CATALOG_DIR)
        out = _read(os.path.join(self.tmpdir, "content", "agenda.html"))
        labels = re.findall(r'<span class="label">(.*?)</span>', out)
        list_class = re.search(r'<ol class="([^"]*)"', out).group(1)
        return labels, list_class, buf.getvalue(), out

    def test_framing_catalog_slides_left_out(self):
        order = ["title", "land-ack", "intro", "funding", "feedback", "thanks"]
        labels, _, _, _ = self._agenda(order, {
            "title": "---\nid: title\nuse: catalog/uw-title\n---\n",
            "land-ack": "---\nid: land-ack\nuse: catalog/land-ack\n---\n",
            "intro": _brief("intro", "layout: key-message\ntitle: Introduction\n"),
            "funding": "---\nid: funding\nuse: catalog/funding\n---\n",
            "feedback": "---\nid: feedback\nuse: catalog/feedback\n---\n",
            "thanks": "---\nid: thanks\nuse: catalog/thank-you\n---\n",
        })
        self.assertEqual(labels, ["Introduction"])

    def test_program_catalog_slide_uses_its_heading(self):
        labels, _, _, _ = self._agenda(["eligibility"], {
            "eligibility": "---\nid: eligibility\nuse: catalog/cb-eligibility\n---\n",
        })
        self.assertEqual(labels, ["Eligibility and recommended uses"])

    def test_hidden_section_left_out(self):
        labels, _, _, _ = self._agenda(["a", "b"], {
            "a": _brief("a", "layout: bullets\ntitle: Shown\n"),
            "b": _brief("b", "layout: bullets\ntitle: Backup\nsection: hidden\n"),
        })
        self.assertEqual(labels, ["Shown"])

    def test_groups_by_section_and_sums_minutes(self):
        labels, _, _, out = self._agenda(["a", "b", "c", "d"], {
            "a": _brief("a", "layout: bullets\nsection: Why cloud\nduration: 2\n"),
            "b": _brief("b", "layout: bullets\nsection: Why cloud\nduration: 3\n"),
            "c": _brief("c", "layout: bullets\nsection: Getting access\n"),
            "d": _brief("d", "layout: bullets\ntitle: Loose slide\nduration: 1\n"),
        })
        self.assertEqual(labels, ["Why cloud", "Getting access", "Loose slide"])
        self.assertIn('<span class="label">Why cloud</span><span class="duration">5 min</span>', out)
        self.assertIn('<span class="label">Getting access</span></li>', out)

    def test_groups_by_section_divider(self):
        labels, _, _, out = self._agenda(["opener", "d1", "a", "b", "d2", "c"], {
            "opener": _brief("opener", "layout: key-message\ntitle: Opening\n"),
            "d1": _brief("d1", "layout: section-divider\n", "Part one"),
            "a": _brief("a", "layout: bullets\nduration: 2\n"),
            "b": _brief("b", "layout: bullets\nduration: 2\n"),
            "d2": _brief("d2", "layout: section-divider\ntitle: Part two\n"),
            "c": _brief("c", "layout: bullets\n"),
        })
        self.assertEqual(labels, ["Opening", "Part one", "Part two"])
        self.assertIn('<span class="label">Part one</span><span class="duration">4 min</span>', out)

    def test_sections_win_over_dividers(self):
        labels, _, _, _ = self._agenda(["d1", "a"], {
            "d1": _brief("d1", "layout: section-divider\n", "Divider"),
            "a": _brief("a", "layout: bullets\nsection: Named section\n"),
        })
        self.assertEqual(labels, ["Named section"])

    def _flat(self, n):
        ids = [f"s{i}" for i in range(n)]
        return ids, {sid: _brief(sid, f"layout: bullets\ntitle: Item {i}\n")
                     for i, sid in enumerate(ids)}

    def test_seven_items_one_column(self):
        labels, cls, err, _ = self._agenda(*self._flat(7))
        self.assertEqual(len(labels), 7)
        self.assertEqual(cls, "agenda-list")
        self.assertNotIn("agenda has", err)

    def test_eight_items_two_columns(self):
        labels, cls, _, _ = self._agenda(*self._flat(8))
        self.assertEqual(len(labels), 8)
        self.assertEqual(cls, "agenda-list two-columns")

    def test_twelve_items_fit_without_warning(self):
        labels, cls, err, _ = self._agenda(*self._flat(12))
        self.assertEqual(len(labels), 12)
        self.assertNotIn("agenda has", err)

    def test_over_twelve_items_cut_with_warning(self):
        labels, cls, err, _ = self._agenda(*self._flat(20))
        self.assertEqual(len(labels), 12)
        self.assertEqual(labels[-1], "and 9 more")
        self.assertEqual(labels[-2], "Item 10")
        self.assertIn("agenda has 20 items", err)
        self.assertIn("section:", err)

    def test_aria_label_uses_heading_param(self):
        _, _, _, out = self._agenda(["a"], {"a": _brief("a", "layout: bullets\n")})
        self.assertIn('aria-label="Slide 1: Agenda"', out)

    def test_in_agenda_must_be_boolean(self):
        cat = _make_catalog(self.tmpdir)
        md = os.path.join(cat, "slides", "agenda", "slide.md")
        _write(md, _read(md).replace("in_agenda: false", 'in_agenda: "no"'))
        with self.assertRaises(ValueError):
            rc._load_catalog_slide_meta(cat, "agenda")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
