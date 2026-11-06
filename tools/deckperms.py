#!/usr/bin/env python3
"""Add the Claude Code permission rules the uw-slides skills need to a deck (stdlib only).

Usage:
  deckperms.py [<deck-dir>] [--check]

The skills run the same few commands on every deck (tools/deckparse.py, the
catalog resolver, the build scripts) and write briefs and slide fragments.
Without allow rules Claude Code asks about each one, which for a deck of 15
slides means dozens of prompts. This script writes the rules into the deck:

  .claude/settings.json        shared with everyone who clones the deck: Bash
                               rules for the deck's own scripts and tools, and
                               Edit rules for content/ and slides/
  .claude/settings.local.json  this computer only (kept out of git): a Read rule
                               for the plugin folder, whose files the skills read
                               (layouts, brand rules, schemas) and which lives
                               outside the deck

Existing settings are kept. Only rules that are missing are added, so running
it again changes nothing, and it never removes or reorders what is there. A
settings file that is not valid JSON is left alone and reported.

--check   print what would be added and write nothing

Exit status: 0 success (including nothing to add), 1 a settings file could not
be used, 2 usage error.
"""

import argparse
import json
import os
import re
import sys

# The plugin is the one this script lives in. Keep both spellings of its path:
# Claude Code matches an allow rule against the path a file is requested by and
# against the file it resolves to, so a plugin reached through a symlink needs
# a rule for each.
PLUGIN_DIR_LEXICAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_DIR = os.path.realpath(PLUGIN_DIR_LEXICAL)

SETTINGS = os.path.join(".claude", "settings.json")
SETTINGS_LOCAL = os.path.join(".claude", "settings.local.json")

# Rules that hold in every copy of the deck, so they are safe to commit.
# A trailing " *" also matches the bare command (./build.sh with no arguments).
# `/content/**` is anchored at the project root (Claude Code reads a single
# leading slash in a project settings file as relative to the project).
# resolve-catalog.py is allowed for `resolve` only: `eject` turns a slide into a
# locked layout slide, which the user should confirm.
SHARED_RULES = [
    "Bash(python3 tools/deckparse.py *)",
    "Bash(python3 tools/resolve-catalog.py resolve *)",
    "Bash(python3 tools/lint.py *)",
    "Bash(./build.sh *)",
    "Bash(./build-visuals.sh *)",
    "Bash(./outline.sh *)",
    "Bash(./lint.sh *)",
    "Bash(./status.sh *)",
    "Bash(printenv UW_SLIDES_HOME)",
    "Edit(/content/**)",
    "Edit(/slides/**)",
]

# Version-numbered plugin cache folders (0.6.2, v0.6.2, 0.6.2-rc.1) and the
# commit-hash folders some installers use.
_VERSION_DIR = re.compile(r"v?\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?|[0-9a-f]{7,40}")


class PermissionsError(Exception):
    """A settings file could not be used; the message is for the user."""


def plugin_read_rules(*plugin_dirs):
    """Read rules for the plugin folder, one per distinct spelling of its path.

    The plugin's folder is named after its version, so a rule for one version
    stops matching after the next update. When the folder looks like a version
    the rule covers its parent, which holds only that plugin's versions. Any
    other folder (a development checkout, the legacy symlink install) gets a
    rule for just that folder.
    """
    if os.name == "nt":  # Windows paths are matched in a different form
        return []
    rules = []
    for plugin_dir in plugin_dirs:
        path = os.path.abspath(plugin_dir).rstrip("/")
        if _VERSION_DIR.fullmatch(os.path.basename(path)):
            path = os.path.dirname(path)
        # "//" before an absolute path is Claude Code's filesystem-root anchor.
        rule = f"Read(/{path}/**)"
        if rule not in rules:
            rules.append(rule)
    return rules


def _load(path):
    """The settings object in path ({} if the file does not exist)."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except ValueError as e:
        raise PermissionsError(f"{path}: not valid JSON ({e}); fix or remove it, then run this again")
    except OSError as e:
        raise PermissionsError(f"{path}: cannot read it ({e.strerror})")
    if not isinstance(data, dict):
        raise PermissionsError(f"{path}: expected a JSON object at the top level")
    return data


def merge_allow(path, rules, write=True):
    """Add the rules missing from permissions.allow in the settings file at path.

    Returns the rules that were (or, with write=False, would be) added.
    Everything else in the file is kept as it is.
    """
    data = _load(path)
    permissions = data.setdefault("permissions", {})
    if not isinstance(permissions, dict):
        raise PermissionsError(f"{path}: \"permissions\" must be an object")
    allow = permissions.setdefault("allow", [])
    if not isinstance(allow, list):
        raise PermissionsError(f"{path}: \"permissions.allow\" must be a list")
    added = [r for r in rules if r not in allow]
    if added and write:
        allow.extend(added)
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
                fh.write("\n")
        except OSError as e:
            raise PermissionsError(f"{path}: cannot write it ({e.strerror})")
    return added


def ensure_ignored(deck_dir, pattern=SETTINGS_LOCAL.replace(os.sep, "/"), write=True):
    """Make sure .gitignore lists the machine-specific settings file.

    Returns True if the line was (or would be) added. The file holds this
    computer's plugin path, which must not be committed.
    """
    path = os.path.join(deck_dir, ".gitignore")
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        text = ""
    except OSError as e:
        raise PermissionsError(f"{path}: cannot read it ({e.strerror})")
    if pattern in (line.strip() for line in text.splitlines()):
        return False
    if write:
        sep = "" if not text or text.endswith("\n") else "\n"
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text + sep + pattern + "\n")
        except OSError as e:
            raise PermissionsError(f"{path}: cannot write it ({e.strerror})")
    return True


class Result:
    def __init__(self):
        self.shared = []  # rules added to .claude/settings.json
        self.local = []  # rules added to .claude/settings.local.json
        self.ignored = False  # .gitignore line added
        self.files = 0  # settings files that exist after the run (or would, with --check)

    @property
    def changed(self):
        return bool(self.shared or self.local or self.ignored)


def apply(deck_dir, plugin_dir=PLUGIN_DIR, lexical_dir=None, write=True):
    """Merge the rules into <deck_dir>/.claude/ and return a Result."""
    lexical_dir = lexical_dir or plugin_dir
    result = Result()
    shared_path = os.path.join(deck_dir, SETTINGS)
    result.shared = merge_allow(shared_path, SHARED_RULES, write=write)
    result.files = 1
    local_rules = plugin_read_rules(lexical_dir, plugin_dir)
    if local_rules:
        local_path = os.path.join(deck_dir, SETTINGS_LOCAL)
        result.local = merge_allow(local_path, local_rules, write=write)
        result.ignored = ensure_ignored(deck_dir, write=write)
        result.files = 2
    return result


def main(argv):
    parser = argparse.ArgumentParser(
        prog="deckperms.py",
        description="Add the Claude Code permission rules the uw-slides skills need to a deck.",
    )
    parser.add_argument("deck_dir", nargs="?", default=".", help="deck folder (default: .)")
    parser.add_argument("--check", action="store_true", help="show what would be added; write nothing")
    args = parser.parse_args(argv[1:])

    if not os.path.isfile(os.path.join(args.deck_dir, "deck.yml")):
        print(f"✗ {args.deck_dir}: no deck.yml here; run this from a deck folder", file=sys.stderr)
        return 1
    try:
        r = apply(args.deck_dir, PLUGIN_DIR, PLUGIN_DIR_LEXICAL, write=not args.check)
    except PermissionsError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1

    verb = "Would add" if args.check else "Added"
    if not r.changed:
        print("✓ Permission rules are up to date: nothing to add")
        return 0
    print(f"✓ {verb} Claude Code permission rules")
    if r.shared:
        print(f"  {SETTINGS}: {len(r.shared)} rule(s)")
    if r.local:
        print(f"  {SETTINGS_LOCAL}: {len(r.local)} rule(s), this computer only")
    if r.ignored:
        print(f"  .gitignore: {verb.lower()} {SETTINGS_LOCAL.replace(os.sep, '/')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
