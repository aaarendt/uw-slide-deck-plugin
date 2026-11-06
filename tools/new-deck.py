#!/usr/bin/env python3
"""Scaffold a new uw-slides deck in one command (stdlib only).

Usage:
  new-deck.py <name> [--brand=uw|cloudbank] [--skip-reveal]

Creates ./<name>/ in the current directory with everything
/uw-slides:new-deck used to copy and write by hand: the build scripts and
templates, the brand's shared header and footer, the vendored tools, the
CI and collaboration files, fonts (uw brand only), .brand, .uw-slides.json,
deck.yml with the starter briefs, README.md, AGENTS.md, CLAUDE.md,
.gitignore and the Claude Code permission rules (.claude/, see deckperms.py).
It then validates deck.yml and the briefs and downloads reveal.js with
setup-reveal.sh.

The plugin is the one this script lives in (two directories above it), so no
plugin lookup is needed. The script refuses to touch an existing folder, and a
failed run removes the folder it created. A failed reveal.js download is a
warning, not a failure: the deck is complete and ./setup-reveal.sh can be run
later.

--skip-reveal   do not download reveal.js (offline use, tests)

Exit status: 0 success (including a reveal.js download that failed),
1 refused or failed, 2 usage error.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

# The plugin's path as this script was run (may go through a symlink) and with
# symlinks resolved; deckperms needs both to write its Read rules.
PLUGIN_DIR_LEXICAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_DIR = os.path.realpath(PLUGIN_DIR_LEXICAL)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import deckparse  # noqa: E402  (vendored alongside this file)
import deckperms  # noqa: E402  (writes .claude/settings.json; not copied into decks)

BRANDS = {"uw": "UW-branded", "cloudbank": "CloudBank-branded"}

REVEAL_TIMEOUT = 120  # seconds
REVEAL_FILES = ("reveal.min.js", "reveal.min.css", os.path.join("plugin", "notes", "notes.js"))

# Files copied verbatim from the plugin into every deck:
#   (path in the deck, source in the plugin, managed by /uw-slides:update-deck)
# The "managed" column is the list update-deck keeps in sync; a test checks it
# against skills/update-deck/SKILL.md so the two cannot drift apart.
FILES = [
    ("build.sh", "templates/build.sh", True),
    ("build-visuals.sh", "templates/build-visuals.sh", True),
    ("lint.sh", "templates/lint.sh", True),
    ("status.sh", "templates/status.sh", True),
    ("outline.sh", "templates/outline.sh", True),
    ("publish.sh", "templates/publish.sh", True),
    ("export.sh", "templates/export.sh", True),
    ("shared/footer.html", "templates/shared/footer-reveal.html", True),
    ("tools/deckparse.py", "tools/deckparse.py", True),
    ("tools/lint.py", "tools/lint.py", True),
    ("tools/resolve-catalog.py", "tools/resolve-catalog.py", True),
    ("setup-reveal.sh", "templates/setup-reveal.sh", False),
    ("VISUALS.md", "templates/VISUALS.md", False),
    ("CLAUDE.md", "templates/CLAUDE.md", False),
    (".github/CODEOWNERS", "templates/.github/CODEOWNERS", False),
    (".github/pull_request_template.md", "templates/.github/pull_request_template.md", False),
    (".github/workflows/deck.yml", "templates/.github/workflows/deck.yml", True),
    ("slides/example-slide.md", "templates/slides/_example.md", False),
]

# The shared header is the one brand-specific file.
HEADER = ("shared/header.html", "design-systems/{brand}-brand/shared/header-reveal.html", True)

# Templates with placeholders: (path in the deck, source in the plugin).
TEXT_TEMPLATES = [
    ("README.md", "templates/README.md"),
    ("AGENTS.md", "templates/AGENTS.md"),
]

EMPTY_DIRS = ["content", "content-with-visuals", "assets/images", "assets/diagrams"]

# .claude/settings.local.json holds this computer's plugin path (see deckperms.py).
GITIGNORE = "build/\n.DS_Store\n*.swp\n*~\n.claude/settings.local.json\n"

TITLE_BRIEF = """---
id: title
layout: title
status: draft
---

# Key message
{name}

## Slot: subtitle
Subtitle
"""


class ScaffoldError(Exception):
    """The scaffold was refused or failed; the message is for the user."""


class Result:
    def __init__(self, deck_dir, brand, plugin_version):
        self.deck_dir = deck_dir
        self.brand = brand
        self.plugin_version = plugin_version
        self.files = 0
        self.fonts = 0
        self.permission_rules = 0  # Claude Code allow rules written to .claude/
        self.reveal = None  # True downloaded, False failed, None skipped
        self.warnings = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def managed_files():
    """Deck paths that /uw-slides:update-deck manages (brand-independent)."""
    return sorted([d for d, _, m in FILES if m] + ([HEADER[0]] if HEADER[2] else []))


def validate_name(name):
    if not name or name != name.strip():
        raise ScaffoldError("the presentation name must not be empty or start or end with spaces")
    if not name[0].isalnum():
        raise ScaffoldError(f"{name!r}: the name must start with a letter or digit")
    if "/" in name or "\\" in name or ".." in name:
        raise ScaffoldError(f"{name!r}: the name must not contain slashes or '..'")
    if any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise ScaffoldError(f"{name!r}: the name must not contain control characters")
    if len(name) > 100:
        raise ScaffoldError("the presentation name is longer than 100 characters")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _copy(src, dst):
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    shutil.copyfile(src, dst)
    # Set the mode explicitly: a plugin cache may not preserve it, and two
    # shell templates are not executable in git.
    os.chmod(dst, 0o755 if dst.endswith(".sh") else 0o644)


def _plugin_version(plugin_dir):
    try:
        return json.loads(_read(os.path.join(plugin_dir, "plugin.json")))["version"]
    except (OSError, ValueError, KeyError) as e:
        raise ScaffoldError(f"{plugin_dir}/plugin.json: cannot read the plugin version ({e})")


def _yaml_quote(text):
    """Double-quoted scalar in the restricted YAML subset (escapes \\ and ")."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _run_setup_reveal(deck_dir):
    """Run setup-reveal.sh in the deck. Returns (ok, reason)."""
    try:
        proc = subprocess.run(
            ["bash", "setup-reveal.sh", "."],
            cwd=deck_dir, capture_output=True, text=True, timeout=REVEAL_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return False, f"timed out after {REVEAL_TIMEOUT} seconds"
    except OSError as e:
        return False, str(e)
    if proc.returncode != 0:
        lines = (proc.stderr or proc.stdout or "").strip().splitlines()
        return False, lines[-1] if lines else f"setup-reveal.sh exited with status {proc.returncode}"
    missing = [f for f in REVEAL_FILES if not os.path.isfile(os.path.join(deck_dir, "assets", "reveal", f))]
    if missing:
        return False, "missing after download: " + ", ".join(missing)
    return True, ""


# ---------------------------------------------------------------------------
# Scaffold
# ---------------------------------------------------------------------------


def scaffold(name, brand="uw", dest=".", plugin_dir=PLUGIN_DIR_LEXICAL, skip_reveal=False, reveal_runner=None):
    """Create <dest>/<name>/ and return a Result. Raises ScaffoldError."""
    if brand not in BRANDS:
        raise ScaffoldError(f"unknown brand {brand!r} (use {' or '.join(BRANDS)})")
    validate_name(name)
    lexical_plugin_dir = os.path.abspath(plugin_dir)
    plugin_dir = os.path.realpath(plugin_dir)
    version = _plugin_version(plugin_dir)

    header = (HEADER[0], HEADER[1].format(brand=brand), HEADER[2])
    copies = [(d, s) for d, s, _ in FILES] + [(header[0], header[1])]
    fonts_src = os.path.join(plugin_dir, "design-systems", "uw-brand", "fonts")

    # Check the plugin is complete before creating anything.
    sources = [s for _, s in copies + TEXT_TEMPLATES] + ["templates/deck.yml"]
    missing = [s for s in sources if not os.path.isfile(os.path.join(plugin_dir, s))]
    if brand == "uw" and not os.path.isdir(fonts_src):
        missing.append("design-systems/uw-brand/fonts/")
    if missing:
        raise ScaffoldError(f"the plugin at {plugin_dir} is incomplete; missing: " + ", ".join(missing))

    deck_dir = os.path.join(os.path.abspath(dest), name)
    try:
        os.mkdir(deck_dir)
    except FileExistsError:
        raise ScaffoldError(f"{deck_dir} already exists; choose another name or remove it")
    except OSError as e:
        raise ScaffoldError(f"cannot create {deck_dir}: {e.strerror}")

    result = Result(deck_dir, brand, version)
    try:
        _populate(result, name, brand, plugin_dir, copies, fonts_src, lexical_plugin_dir)
        deckparse.load_deck_dir(deck_dir)  # validates deck.yml and the briefs
        if skip_reveal:
            result.reveal = None
        else:
            ok, reason = (reveal_runner or _run_setup_reveal)(deck_dir)
            result.reveal = ok
            if not ok:
                shutil.rmtree(os.path.join(deck_dir, "assets", "reveal"), ignore_errors=True)
                result.warnings.append(
                    f"reveal.js assets could not be downloaded ({reason}). Run ./setup-reveal.sh "
                    "when you have internet access. Until then the deck will not load reveal.js; "
                    "a manually installed copy at assets/reveal/ also works."
                )
    except deckparse.DeckParseError as e:
        shutil.rmtree(deck_dir, ignore_errors=True)
        raise ScaffoldError(f"the scaffolded deck did not validate (plugin bug): {e}")
    except deckperms.PermissionsError as e:
        shutil.rmtree(deck_dir, ignore_errors=True)
        raise ScaffoldError(f"could not write the Claude Code permission rules (plugin bug): {e}")
    except BaseException as e:
        shutil.rmtree(deck_dir, ignore_errors=True)
        if isinstance(e, (ScaffoldError, KeyboardInterrupt)):
            raise
        raise ScaffoldError(f"scaffold failed and {deck_dir} was removed: {e}")
    return result


def _populate(result, name, brand, plugin_dir, copies, fonts_src, lexical_plugin_dir=None):
    deck_dir = result.deck_dir

    for dst, src in copies:
        _copy(os.path.join(plugin_dir, src), os.path.join(deck_dir, dst))
        result.files += 1

    # README.md and AGENTS.md: fill in the placeholders.
    subs = {"[Presentation Name]": name, "[BRAND_NAME]": BRANDS[brand], "[BRAND]": brand}
    for dst, src in TEXT_TEMPLATES:
        text = _read(os.path.join(plugin_dir, src))
        for key, value in subs.items():
            text = text.replace(key, value)
        _write(os.path.join(deck_dir, dst), text)
        result.files += 1

    if brand == "uw":
        fonts_dst = os.path.join(deck_dir, "assets", "fonts")
        os.makedirs(fonts_dst)
        for f in sorted(os.listdir(fonts_src)):
            if os.path.isfile(os.path.join(fonts_src, f)):
                _copy(os.path.join(fonts_src, f), os.path.join(fonts_dst, f))
                result.fonts += 1

    for d in EMPTY_DIRS:
        os.makedirs(os.path.join(deck_dir, d), exist_ok=True)
        # git does not keep empty folders; without this a fresh clone (CI)
        # would be missing them.
        with open(os.path.join(deck_dir, d, ".gitkeep"), "w", encoding="utf-8"):
            pass

    write_deck_yml(deck_dir, plugin_dir, name)
    write_starter_briefs(deck_dir, name)
    result.files += 2  # deck.yml and slides/title.md (slides/example-slide.md is in FILES)

    _write(os.path.join(deck_dir, ".gitignore"), GITIGNORE)
    _write(os.path.join(deck_dir, ".brand"), brand + "\n")
    stamp = {
        "plugin_version": result.plugin_version,
        "brand": brand,
        "scaffolded_at": datetime.date.today().isoformat(),
        "catalog": None,
        "plugin_dir": plugin_dir,
    }
    _write(os.path.join(deck_dir, ".uw-slides.json"), json.dumps(stamp, indent=2) + "\n")
    result.files += 3  # .gitignore, .brand, .uw-slides.json

    # Claude Code permission rules, so the skills do not ask about every command.
    perms = deckperms.apply(deck_dir, plugin_dir, lexical_plugin_dir)
    result.files += perms.files
    result.permission_rules = len(perms.shared) + len(perms.local)


def write_deck_yml(deck_dir, plugin_dir, name):
    """deck.yml from the template, with title set to the presentation name."""
    text = _read(os.path.join(plugin_dir, "templates", "deck.yml"))
    text, n = re.subn(r"(?m)^title:.*$", lambda m: "title: " + _yaml_quote(name), text, count=1)
    if n != 1:
        raise ScaffoldError("templates/deck.yml has no title: line to set")
    _write(os.path.join(deck_dir, "deck.yml"), text)


def write_starter_briefs(deck_dir, name):
    """slides/title.md (slides/example-slide.md is copied from the template).

    Kept separate so a later --slides option can replace the starter slides."""
    _write(os.path.join(deck_dir, "slides", "title.md"), TITLE_BRIEF.format(name=name))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _brand_arg(value):
    return value.strip().removesuffix("-brand")


def main(argv):
    parser = argparse.ArgumentParser(
        prog="new-deck.py",
        description="Scaffold a new uw-slides deck in ./<name>/.",
    )
    parser.add_argument("name", help="presentation name (also the folder name)")
    parser.add_argument("--brand", type=_brand_arg, choices=sorted(BRANDS), default="uw",
                        help="design system (default: uw)")
    parser.add_argument("--skip-reveal", action="store_true",
                        help="do not download reveal.js")
    args = parser.parse_args(argv[1:])

    try:
        r = scaffold(args.name, args.brand, skip_reveal=args.skip_reveal)
    except ScaffoldError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1

    print(f"✓ Created {r.brand} deck: {r.deck_dir}")
    print(f"  Plugin: v{r.plugin_version} ({PLUGIN_DIR}), recorded in .uw-slides.json")
    fonts = f", {r.fonts} fonts" if r.fonts else ""
    print(f"  Files: {r.files} written{fonts}; deck.yml and the starter briefs validate")
    print(f"  Permissions: {r.permission_rules} Claude Code allow rules in .claude/ so the skills don't ask for each command")
    if r.reveal is True:
        print("  reveal.js: downloaded to assets/reveal/")
    elif r.reveal is None:
        print("  reveal.js: skipped (--skip-reveal); run ./setup-reveal.sh to download it")
    for w in r.warnings:
        print(f"  ⚠ {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
