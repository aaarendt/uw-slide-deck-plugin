#!/usr/bin/env python3
"""Check the download URLs in templates/setup-reveal.sh (stdlib only).

The other tests stub the download, so a wrong CDN path goes unnoticed (reveal.js
6.x moved the notes plugin and the script 404'd). The offline checks always run;
the network check is skipped when jsDelivr cannot be reached.

Usage: python3 tools/test_setup_reveal_urls.py
"""

import os
import re
import unittest
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "templates", "setup-reveal.sh")


def _script():
    with open(SCRIPT, encoding="utf-8") as fh:
        return fh.read()


def _variable(text, name):
    m = re.search(r'^%s="([^"]+)"' % name, text, re.M)
    assert m, "%s not set in setup-reveal.sh" % name
    return m.group(1)


def download_urls():
    """Return {local path under assets/reveal: URL} for the curl lines."""
    text = _script()
    version = _variable(text, "REVEAL_VERSION")
    bases = {
        "DIST_URL": _variable(text, "DIST_URL").replace("${REVEAL_VERSION}", version),
        "PLUGIN_URL": _variable(text, "PLUGIN_URL").replace("${REVEAL_VERSION}", version),
    }
    urls = {}
    for m in re.finditer(
        r'curl -fsSL -o "\$TARGET/([^"]+)"\s+"\$(DIST_URL|PLUGIN_URL)/([^"]+)"', text
    ):
        local, base, name = m.groups()
        urls[local] = "%s/%s" % (bases[base + ""], name)
    return urls


class TestSetupRevealUrls(unittest.TestCase):
    def test_three_files_and_local_paths(self):
        urls = download_urls()
        self.assertEqual(
            sorted(urls),
            ["plugin/notes/notes.js", "reveal.min.css", "reveal.min.js"],
        )

    def test_notes_plugin_uses_the_6x_path(self):
        # 6.x ships dist/plugin/notes.js; plugin/notes/notes.js is the 5.x path (404).
        self.assertTrue(download_urls()["plugin/notes/notes.js"].endswith("/dist/plugin/notes.js"))

    def test_urls_exist_on_the_cdn(self):
        for local, url in sorted(download_urls().items()):
            req = urllib.request.Request(url, method="HEAD")
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    status = resp.status
            except urllib.error.HTTPError as err:
                if err.code in (403, 407, 429):  # proxy or rate limit, not a missing file
                    self.skipTest("CDN not reachable (HTTP %d)" % err.code)
                status = err.code
            except (urllib.error.URLError, OSError) as err:
                self.skipTest("CDN not reachable (%s)" % err)
            self.assertEqual(status, 200, "%s -> HTTP %s (%s)" % (local, status, url))


if __name__ == "__main__":
    unittest.main()
