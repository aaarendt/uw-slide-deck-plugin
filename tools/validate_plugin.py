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
    directory and a non-empty `description` (folded `>` and literal `|`
    block scalars are read too)
  - every skill that uses `<PLUGIN>/` paths says how to resolve PLUGIN
  - both marketplaces (.claude-plugin/ for Claude Code and Copilot CLI,
    .agents/plugins/ for Codex) list this plugin at the repository root,
    the Codex entry has the `policy` and `category` Codex requires, and both
    entries use the same category (case-insensitive)

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
BLOCK_SCALAR_RE = re.compile(r"^[>|][+-]?$")
CODEX_INSTALLATION = ("AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE")
CLAUDE_MARKETPLACE = ".claude-plugin/marketplace.json"
CODEX_MARKETPLACE = ".agents/plugins/marketplace.json"


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
    # Stricter than the spec on purpose: Agent Plugins clients report an
    # unknown top-level field and ignore it, so a typo such as "keyword" would
    # be silently dropped at install time. Fail here instead.
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
    lines = text[4:end].splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        i += 1
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if BLOCK_SCALAR_RE.match(value):
            # A `>` or `|` block scalar: the value is the indented lines below.
            block = []
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in " \t"):
                block.append(lines[i].strip())
                i += 1
            if value.startswith(">"):
                fields[key] = " ".join(b for b in block if b)
            else:
                fields[key] = "\n".join(block).strip()
        else:
            fields[key] = value.strip('"\'')
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
    """Check one marketplace file and return this plugin's entry, or None."""
    data = _load_json(root, label, errors)
    if data is None:
        return None
    if not isinstance(data.get("name"), str) or not data["name"]:
        errors.append(f"{label}: name is missing")
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        errors.append(f"{label}: plugins must be an array")
        return None
    entries = [p for p in plugins if isinstance(p, dict)]
    matches = [p for p in entries if p.get("name") == plugin_name]
    if not matches:
        errors.append(f"{label}: no entry for plugin {plugin_name!r}")
        return None
    entry = matches[0]
    if not _source_is_root(entry.get("source")):
        errors.append(f"{label}: {plugin_name!r} source must point at the repository root")
    return entry


def check_codex_entry(entry, plugin_name, errors):
    """Fields Codex requires on every marketplace entry."""
    label = CODEX_MARKETPLACE
    policy = entry.get("policy")
    if not isinstance(policy, dict):
        errors.append(f"{label}: {plugin_name!r} needs a policy object")
    else:
        if policy.get("installation") not in CODEX_INSTALLATION:
            errors.append(
                f"{label}: {plugin_name!r} policy.installation must be one of "
                + ", ".join(CODEX_INSTALLATION)
            )
        auth = policy.get("authentication")
        if not isinstance(auth, str) or not auth:
            errors.append(f"{label}: {plugin_name!r} policy.authentication must be a string")
    category = entry.get("category")
    if not isinstance(category, str) or not category:
        errors.append(f"{label}: {plugin_name!r} category must be a non-empty string")


def check_categories(claude_entry, codex_entry, plugin_name, errors):
    """Both marketplaces should file the plugin under the same category."""
    a, b = claude_entry.get("category"), codex_entry.get("category")
    if isinstance(a, str) and isinstance(b, str) and a.lower() != b.lower():
        errors.append(
            f"{plugin_name!r} category differs between marketplaces: "
            f"{a!r} in {CLAUDE_MARKETPLACE}, {b!r} in {CODEX_MARKETPLACE}"
        )


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
    claude_entry = check_marketplace(root, CLAUDE_MARKETPLACE, name, errors)
    codex_entry = check_marketplace(root, CODEX_MARKETPLACE, name, errors)
    if codex_entry is not None:
        check_codex_entry(codex_entry, name, errors)
        if claude_entry is not None:
            check_categories(claude_entry, codex_entry, name, errors)
    return errors


def _usage():
    lines = __doc__.strip().splitlines()
    start = lines.index("Usage:")
    end = lines.index("", start)
    return "\n".join(lines[start:end])


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) > 1 or set(flags) - {"--claude"}:
        print(_usage(), file=sys.stderr)
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
