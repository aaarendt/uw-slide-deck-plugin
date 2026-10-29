#!/usr/bin/env python3
"""Validate the uw-slides plugin packaging (stdlib only).

Usage:
  validate_plugin.py [<plugin-dir>]            # default: the directory above tools/
  validate_plugin.py [<plugin-dir>] --claude   # also run `claude plugin validate`

Checks:
  - plugin.json follows the Agent Plugins v1.0.0 manifest rules
    (https://agent-plugins.org/plugin-authors/manifest)
  - .claude-plugin/plugin.json carries the same metadata (Claude Code does not
    read the portable manifest, so both must exist and agree)
  - every skills/<name>/SKILL.md has front matter whose `name` matches its
    directory and a non-empty `description`
  - every skill that uses `<PLUGIN>/` paths says how to resolve PLUGIN
  - both marketplaces (.claude-plugin/ for Claude Code and Copilot CLI,
    .agents/plugins/ for Codex) list this plugin at the repository root

Exit codes: 0 = valid, 1 = problems found, 2 = usage error.
"""

import json
import os
import re
import shutil
import subprocess
import sys

SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MANIFEST_FIELDS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}
STRING_FIELDS = ("version", "description", "homepage", "repository", "license")
SHARED_FIELDS = (
    "name", "version", "description", "author", "homepage", "repository",
    "license", "keywords",
)
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,62}[a-z0-9])?$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
ROOT_SOURCES = (".", "./")


def _load_json(root, rel, errors):
    path = os.path.join(root, rel)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        errors.append(f"{rel}: missing")
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: invalid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{rel}: must be a JSON object")
        return None
    return data


def check_manifest(manifest, errors):
    """Agent Plugins v1.0.0 manifest rules for the root plugin.json."""
    if manifest.get("$schema") != SCHEMA:
        errors.append(f"plugin.json: $schema must be {SCHEMA}")
    name = manifest.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name) or ".." in name or "--" in name:
        errors.append(f"plugin.json: invalid name {name!r}")
    for key in sorted(set(manifest) - MANIFEST_FIELDS):
        errors.append(f"plugin.json: unknown field {key!r} (client data goes under extensions)")
    for key in STRING_FIELDS:
        if key in manifest and not isinstance(manifest[key], str):
            errors.append(f"plugin.json: {key} must be a string")
    if "author" in manifest:
        author = manifest["author"]
        if not isinstance(author, dict) or not all(
            isinstance(author.get(k), str) for k in author
        ) or set(author) - {"name", "email", "url"}:
            errors.append("plugin.json: author must be an object of name/email/url strings")
    keywords = manifest.get("keywords")
    if "keywords" in manifest and not (
        isinstance(keywords, list) and all(isinstance(k, str) for k in keywords)
    ):
        errors.append("plugin.json: keywords must be an array of strings")
    if "extensions" in manifest and not isinstance(manifest["extensions"], dict):
        errors.append("plugin.json: extensions must be an object")


def check_claude_manifest(manifest, claude, errors):
    for key in SHARED_FIELDS:
        if manifest.get(key) != claude.get(key):
            errors.append(
                f".claude-plugin/plugin.json: {key} differs from plugin.json"
            )


def _front_matter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"\'')
    return fields


def check_skills(root, errors):
    skills_dir = os.path.join(root, "skills")
    names = sorted(
        d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))
    ) if os.path.isdir(skills_dir) else []
    if not names:
        errors.append("skills/: no skills found")
    for name in names:
        rel = f"skills/{name}/SKILL.md"
        path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(path):
            errors.append(f"{rel}: missing")
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        fm = _front_matter(text)
        if fm is None:
            errors.append(f"{rel}: no YAML front matter")
            continue
        if fm.get("name") != name:
            errors.append(f"{rel}: name {fm.get('name')!r} does not match directory {name!r}")
        if not SKILL_NAME_RE.match(name) or "--" in name:
            errors.append(f"{rel}: invalid skill name {name!r}")
        desc = fm.get("description", "")
        if not desc:
            errors.append(f"{rel}: description is empty")
        elif len(desc) > 1024:
            errors.append(f"{rel}: description is longer than 1024 characters")
        if "<PLUGIN>/" in text and "two directories above this `SKILL.md`" not in text:
            errors.append(f"{rel}: uses <PLUGIN>/ paths but does not say how to find the plugin")
    return names


def _source_is_root(source):
    if isinstance(source, str):
        return source in ROOT_SOURCES
    if isinstance(source, dict):
        return source.get("source") == "local" and source.get("path") in ROOT_SOURCES
    return False


def check_marketplace(root, label, plugin_name, errors):
    data = _load_json(root, label, errors)
    if data is None:
        return
    if not isinstance(data.get("name"), str) or not data["name"]:
        errors.append(f"{label}: name is missing")
    entries = [p for p in data.get("plugins", []) if isinstance(p, dict)]
    matches = [p for p in entries if p.get("name") == plugin_name]
    if not matches:
        errors.append(f"{label}: no entry for plugin {plugin_name!r}")
        return
    if not _source_is_root(matches[0].get("source")):
        errors.append(f"{label}: {plugin_name!r} source must point at the repository root")


def run_claude(root, errors):
    exe = shutil.which("claude")
    if not exe:
        errors.append("--claude: claude CLI not found on PATH")
        return
    for target in (root, os.path.join(root, ".claude-plugin", "marketplace.json")):
        proc = subprocess.run(
            [exe, "plugin", "validate", target], capture_output=True, text=True
        )
        out = (proc.stdout + proc.stderr).strip()
        print(out)
        if proc.returncode != 0:
            errors.append(f"claude plugin validate {target}: exit {proc.returncode}")


def validate(root):
    """Return a list of problems with the packaging under `root`."""
    errors = []
    manifest = _load_json(root, "plugin.json", errors)
    if manifest is not None:
        check_manifest(manifest, errors)
        claude = _load_json(root, ".claude-plugin/plugin.json", errors)
        if claude is not None:
            check_claude_manifest(manifest, claude, errors)
    check_skills(root, errors)
    name = (manifest or {}).get("name", "uw-slides")
    check_marketplace(root, ".claude-plugin/marketplace.json", name, errors)
    check_marketplace(root, ".agents/plugins/marketplace.json", name, errors)
    return errors


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) > 1 or set(flags) - {"--claude"}:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    root = args[0] if args else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errors = validate(root)
    if "--claude" in flags:
        run_claude(root, errors)
    for e in errors:
        print(f"error: {e}")
    if errors:
        return 1
    print("plugin packaging OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
