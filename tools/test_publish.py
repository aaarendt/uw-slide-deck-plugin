#!/usr/bin/env python3
"""Tests for templates/publish.sh (stdlib only; no network, no browser).

Each test builds a small fake deck in a temporary folder: a build/ page that
links reveal.js the way the shared header and footer do, plus stand-in
reveal.js files, then runs the real publish.sh on it.
"""

import base64
import os
import re
import shutil
import subprocess
import tempfile
import unittest

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISH = os.path.join(PLUGIN_DIR, "templates", "publish.sh")

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

# Backslashes, a regex escape and "\1" check that contents are copied as is
# (a replacement string in re.sub would reinterpret them). "</script>" and
# "</style>" check the end-tag guard.
REVEAL_JS = 'var Reveal={re:/\\d+\\/\\s*/g,s:"a\\\\b \\1 \\n",t:"</script>"};\n'
NOTES_JS = 'var RevealNotes=function(){return "<\\/div>"};\n'
REVEAL_CSS = ('.reveal{background:url(data:image/gif;base64,R0lGOD)}\n'
              '.reveal .x::before{content:"\\f101 </style>"}\n')

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>t</title>
  <link rel="stylesheet" href="../assets/reveal/reveal.min.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <style>@font-face { font-family: 'X'; src: url('../assets/fonts/X-400.ttf'); }</style>
</head><body><div class="reveal"><div class="slides">
<section data-slide="a"><h1>A</h1><img src="../assets/images/dot.png" alt="dot">
  <a href="https://example.org">link</a><a href="#/2">jump</a></section>
<section data-slide="b"><h1>B é ✓</h1><img src="https://example.org/remote.png" alt="r"></section>
</div></div>
<script src="../assets/reveal/reveal.min.js"></script>
<script src="../assets/reveal/plugin/notes/notes.js"></script>
<script>Reveal.initialize({ plugins: [ RevealNotes ] });</script>
</body></html>
"""


def _write(path, text, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as fh:
        fh.write(text)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class PublishCase(unittest.TestCase):
    def setUp(self):
        self.deck = tempfile.mkdtemp(prefix="publish-test-")
        self.addCleanup(shutil.rmtree, self.deck, ignore_errors=True)
        a = os.path.join(self.deck, "assets")
        _write(os.path.join(a, "reveal", "reveal.min.js"), REVEAL_JS)
        _write(os.path.join(a, "reveal", "reveal.min.css"), REVEAL_CSS)
        _write(os.path.join(a, "reveal", "plugin", "notes", "notes.js"), NOTES_JS)
        _write(os.path.join(a, "images", "dot.png"), PNG, "wb")
        _write(os.path.join(a, "fonts", "X-400.ttf"), b"\0", "wb")
        self.out = os.path.join(self.deck, "build", "index-published.html")

    def build(self, name="index-with-visuals.html", page=PAGE):
        _write(os.path.join(self.deck, "build", name), page)

    def publish(self, expect_ok=True, *args):
        proc = subprocess.run(["bash", PUBLISH, *args, self.deck], capture_output=True, text=True)
        if expect_ok:
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return proc

    # --- reveal.js inlining -------------------------------------------------

    def test_no_relative_asset_links_remain(self):
        self.build()
        self.publish()
        html = _read(self.out)
        self.assertEqual(re.findall(r'(?:src|href)="\.\./assets[^"]*"', html), [])
        self.assertNotIn('rel="stylesheet"', html)

    def test_contents_are_copied_exactly(self):
        self.build()
        self.publish()
        html = _read(self.out)
        self.assertIn(REVEAL_JS.replace("</script", "<\\/script"), html)
        self.assertIn(NOTES_JS, html)
        self.assertIn(REVEAL_CSS.replace("</style", "<\\/style"), html)

    def test_end_tags_inside_assets_are_guarded(self):
        self.build()
        self.publish()
        html = _read(self.out)
        # Exactly the page's own three scripts and one stylesheet close.
        self.assertEqual(len(re.findall(r"</script>", html)), 3)
        self.assertEqual(len(re.findall(r"<style\b", html)), len(re.findall(r"</style>", html)))

    def test_no_unknown_type_warning_for_scripts(self):
        self.build()
        out = self.publish().stdout
        self.assertNotIn("unknown type", out)
        for path in ("reveal.min.css", "reveal.min.js", "notes/notes.js"):
            self.assertRegex(out, r"Inlined: \S*" + re.escape(path))

    def test_script_inlining_does_not_touch_strings_inside_reveal(self):
        # A src="..." string inside reveal.js must not be treated as an image.
        _write(os.path.join(self.deck, "assets", "reveal", "reveal.min.js"),
               'var Reveal={h:\'<img src="../assets/images/dot.png">\'};\n')
        self.build()
        self.publish()
        self.assertIn('<img src="../assets/images/dot.png">', _read(self.out))

    # --- unchanged behaviour ------------------------------------------------

    def test_images_are_inlined_and_external_urls_kept(self):
        self.build()
        self.publish()
        html = _read(self.out)
        self.assertIn('src="data:image/png;base64,', html)
        self.assertIn('src="https://example.org/remote.png"', html)
        self.assertIn('href="https://example.org"', html)

    def test_output_is_utf8(self):
        self.build()
        self.publish()
        self.assertIn("B é ✓", _read(self.out))

    def test_missing_asset_warns_and_keeps_link(self):
        os.remove(os.path.join(self.deck, "assets", "reveal", "plugin", "notes", "notes.js"))
        self.build()
        out = self.publish().stdout
        self.assertIn("Warning: not found — ../assets/reveal/plugin/notes/notes.js", out)
        self.assertIn('<script src="../assets/reveal/plugin/notes/notes.js"></script>', _read(self.out))

    def test_legacy_page_without_reveal(self):
        page = re.sub(r'\s*<link rel="stylesheet"[^>]*>', "", PAGE)
        page = re.sub(r'\s*<script src="[^"]*"></script>', "", page)
        self.build(page=page)
        out = self.publish().stdout
        self.assertNotIn("Warning", out)
        self.assertEqual(_read(self.out).count("<section"), 2)

    # --- input selection and reporting --------------------------------------

    def test_falls_back_to_index_html(self):
        self.build("index.html")
        out = self.publish().stdout
        self.assertIn("publishing build/index.html", out)
        self.assertTrue(os.path.isfile(self.out))

    def test_prefers_index_with_visuals(self):
        self.build("index.html", PAGE.replace("<h1>A</h1>", "<h1>PASS1</h1>"))
        self.build("index-with-visuals.html")
        self.publish()
        self.assertNotIn("PASS1", _read(self.out))

    def test_fails_without_any_build(self):
        proc = self.publish(expect_ok=False)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Run ./build.sh", proc.stdout)

    def test_reports_what_is_still_linked(self):
        self.build()
        out = self.publish().stdout
        self.assertIn("Not inlined: 1 local file(s)", out)
        self.assertIn("../assets/fonts/", out)
        self.assertIn("Needs internet for: example.org, fonts.googleapis.com", out)

    def test_no_site_without_flag(self):
        self.build()
        self.publish()
        self.assertFalse(os.path.exists(os.path.join(self.deck, "build", "site")))

    def test_unknown_option_is_refused(self):
        self.build()
        proc = self.publish(False, "--sitee")
        self.assertEqual(proc.returncode, 2)

    # --- --site: build/site/ for GitHub Pages --------------------------------

    def site(self, *rel):
        return os.path.join(self.deck, "build", "site", *rel)

    def test_site_copies_linked_files_and_rewrites_paths(self):
        self.build()
        out = self.publish(True, "--site").stdout
        html = _read(self.site("index.html"))
        self.assertIn("url('assets/fonts/X-400.ttf')", html)
        self.assertNotIn("../assets/", html)
        self.assertTrue(os.path.isfile(self.site("assets", "fonts", "X-400.ttf")))
        self.assertIn("Site:", out)

    def test_site_copies_only_what_is_still_linked(self):
        # Images and reveal.js are inlined, so the site needs no copy of them.
        self.build()
        self.publish(True, "--site")
        copied = sorted(os.path.relpath(os.path.join(d, f), self.site())
                        for d, _, files in os.walk(self.site()) for f in files)
        self.assertEqual(copied, ["assets/fonts/X-400.ttf", "index.html"])

    def test_site_index_matches_published_file_apart_from_paths(self):
        self.build()
        self.publish(True, "--site")
        published = _read(self.out)
        site = _read(self.site("index.html"))
        self.assertEqual(site.replace("assets/fonts/", "../assets/fonts/"), published)

    def test_site_leaves_inlined_scripts_alone(self):
        _write(os.path.join(self.deck, "assets", "reveal", "reveal.min.js"),
               'var Reveal={f:"url(\'../assets/fonts/X-400.ttf\')"};\n')
        self.build()
        self.publish(True, "--site")
        self.assertIn('var Reveal={f:"url(\'../assets/fonts/X-400.ttf\')"}', _read(self.site("index.html")))

    def test_site_is_rebuilt_from_scratch(self):
        self.build()
        os.makedirs(self.site(), exist_ok=True)
        _write(self.site("stale.txt"), "old")
        self.publish(True, "--site")
        self.assertFalse(os.path.exists(self.site("stale.txt")))

    def test_site_warns_for_missing_linked_file(self):
        os.remove(os.path.join(self.deck, "assets", "fonts", "X-400.ttf"))
        self.build()
        out = self.publish(True, "--site").stdout
        self.assertIn("not copied to the site", out)
        self.assertIn("1 missing", out)


if __name__ == "__main__":
    unittest.main()
