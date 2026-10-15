#!/usr/bin/env python3
"""Catalog resolver for uw-slides decks (stdlib only).

Usage:
  resolve-catalog.py resolve <deck-dir> [--catalog=<path>]
  resolve-catalog.py eject   <deck-dir> <slide-id> [--catalog=<path>]

resolve
  For each slide in deck.yml with `use: catalog/<id>`, reads the catalog
  fragment, applies param substitution, rewrites data-slide / CSS selectors /
  aria-label to the deck slide ID, records data-catalog provenance, and writes
  the result to content/<deck-slide-id>.html.

eject
  Converts a catalog slide to a local locked slide: removes `use:` from the
  brief, sets `locked: true`, and adds a `# Key message` placeholder so the
  brief remains valid. The existing content/<id>.html is kept unchanged.

Catalog location (first match wins):
  --catalog=<path>                     explicit path to a catalog/ directory
  $UW_SLIDES_HOME/catalog/             if UW_SLIDES_HOME is set
  ~/.claude/plugins/local/uw-slides/catalog/  default fallback

Each catalog slide lives in <catalog>/slides/<id>/:
  slide.html   HTML fragment with {{param}} placeholders
  slide.md     Metadata front matter (restricted YAML subset) + documentation
  assets/      Optional images or other files used by this slide

Param substitution:
  {{param}}  is replaced with html.escape(params[param]) where params is
  the merge of catalog defaults (slide.md params:) and deck brief params:.
  Missing params use the catalog default; missing with no default → empty string.
  {{aria-label}} is special: resolved to "Slide N: <brief.title or params.title
  or catalog description>" where N is the 1-based position in deck.yml.

Derived slides (kind: derived):
  The agenda slide is the only built-in derived kind. Its {{agenda_items}}
  placeholder is replaced with <li> elements built from the deck's briefs.
"""

import html
import json
import os
import re
import shutil
import sys

# ---------------------------------------------------------------------------
# Import deckparse from the same directory (vendored alongside this file)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deckparse

# ---------------------------------------------------------------------------
# Catalog discovery
# ---------------------------------------------------------------------------

DEFAULT_CATALOG_PATH = os.path.expanduser(
    "~/.claude/plugins/local/uw-slides/catalog"
)


def _find_catalog(override=None):
    if override:
        # Explicit --catalog= flag: use it or fail; do not fall through.
        if os.path.isdir(override) and os.path.isfile(os.path.join(override, "catalog.yml")):
            return override
        return None
    candidates = []
    env = os.environ.get("UW_SLIDES_HOME")
    if env:
        candidates.append(os.path.join(env, "catalog"))
    candidates.append(DEFAULT_CATALOG_PATH)
    for c in candidates:
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "catalog.yml")):
            return c
    return None


# ---------------------------------------------------------------------------
# Load catalog slide metadata (slide.md front matter)
# ---------------------------------------------------------------------------

SLIDE_MD_FIELDS = {
    "id", "description", "kind", "brand", "version", "status", "owner", "params",
}
SLIDE_MD_KINDS = ("verbatim", "parameterized", "derived")


def _load_catalog_slide_meta(catalog_path, catalog_id):
    """Parse slides/<id>/slide.md front matter. Returns dict or raises."""
    meta_path = os.path.join(catalog_path, "slides", catalog_id, "slide.md")
    if not os.path.isfile(meta_path):
        raise FileNotFoundError(f"{meta_path}: catalog slide metadata not found")
    with open(meta_path, encoding="utf-8") as fh:
        text = fh.read()
    # Split front matter manually (same pattern as deckparse.split_front_matter)
    if text.startswith("﻿"):
        text = text[1:]
    rows = text.split("\n")
    if not rows or rows[0].rstrip() != "---":
        raise ValueError(f"{meta_path}: must start with a '---' front matter block")
    end = None
    for i in range(1, len(rows)):
        if rows[i].rstrip() == "---":
            end = i
            break
    if end is None:
        raise ValueError(f"{meta_path}: front matter is not closed with '---'")
    fm_text = "\n".join(rows[1:end])
    data, _ = deckparse.parse_subset(fm_text, meta_path, 2)
    # Validate required fields
    for req in ("id", "kind", "version", "status", "owner"):
        if req not in data:
            raise ValueError(f"{meta_path}: missing required field {req!r}")
    if data["kind"] not in SLIDE_MD_KINDS:
        raise ValueError(
            f"{meta_path}: kind must be one of {', '.join(SLIDE_MD_KINDS)}, got {data['kind']!r}"
        )
    return {
        "id": data["id"],
        "description": data.get("description", ""),
        "kind": data["kind"],
        "brand": data.get("brand", "any"),
        "version": data["version"],
        "status": data.get("status", "draft"),
        "owner": data.get("owner", ""),
        "params": data.get("params") or {},
    }


# ---------------------------------------------------------------------------
# HTML rewriting helpers
# ---------------------------------------------------------------------------

DATA_SLIDE_ATTR_RE = re.compile(
    r'(\bdata-slide\s*=\s*["\'])([^"\']+)(["\'])'
)
CSS_SELECTOR_RE = re.compile(
    r'section\[data-slide\s*=\s*"([^"]+)"\]'
)
ARIA_LABEL_RE = re.compile(
    r'(\baria-label\s*=\s*["\'])([^"\']+)(["\'])'
)
DATA_CATALOG_ATTR_RE = re.compile(
    r'\bdata-catalog\s*=\s*["\'][^"\']*["\']'
)
SECTION_TAG_RE = re.compile(r"(<section\b[^>]*>)", re.S)
PARAM_RE = re.compile(r"\{\{([^}]+)\}\}")


def _substitute_params(template, params, raw_keys=()):
    """Replace {{key}} with html.escape(params[key]). Unknown keys → ''.
    Keys in raw_keys are inserted verbatim (already trusted HTML)."""
    def replace(m):
        key = m.group(1).strip()
        val = params.get(key, "")
        if key in raw_keys:
            return str(val)
        return html.escape(str(val), quote=True)
    return PARAM_RE.sub(replace, template)


def _warn_empty_params(template, catalog_defaults, merged_params, slide_id):
    """Warn when a {{key}} resolves to '' and the catalog default was also ''."""
    internal = {"aria-label", "agenda_items"}
    warned = []
    seen = set()
    for m in PARAM_RE.finditer(template):
        key = m.group(1).strip()
        if key in internal or key in seen:
            continue
        seen.add(key)
        if merged_params.get(key, "") == "" and catalog_defaults.get(key, "") == "":
            warned.append(key)
    if warned:
        keys = ", ".join(warned)
        print(
            f"  ⚠ {slide_id}: param(s) {keys} are empty — "
            "add them to the brief's params: map if needed",
            file=sys.stderr,
        )


def _rewrite_data_slide(fragment, old_id, new_id):
    """Rewrite data-slide attribute and all CSS selectors."""
    fragment = DATA_SLIDE_ATTR_RE.sub(
        lambda m: m.group(1) + new_id + m.group(3), fragment
    )
    fragment = CSS_SELECTOR_RE.sub(
        lambda m: f'section[data-slide="{new_id}"]', fragment
    )
    return fragment


def _rewrite_aria_label(fragment, aria_label):
    """Replace the aria-label attribute value."""
    return ARIA_LABEL_RE.sub(
        lambda m: m.group(1) + aria_label + m.group(3), fragment
    )


def _inject_data_catalog(fragment, catalog_id, catalog_version):
    """Add or update data-catalog on the root <section> element."""
    catalog_value = f"{catalog_id}@{catalog_version}"
    # Remove existing data-catalog if present
    def patch_section(m):
        tag = m.group(1)
        tag = DATA_CATALOG_ATTR_RE.sub("", tag)
        # Insert after the first attribute or before the closing >
        insert = f' data-catalog="{catalog_value}"'
        if tag.endswith(">"):
            tag = tag[:-1] + insert + ">"
        else:
            tag = tag + insert
        return tag
    return SECTION_TAG_RE.sub(patch_section, fragment, count=1)


# ---------------------------------------------------------------------------
# Derived slide generators
# ---------------------------------------------------------------------------


_AGENDA_EXCLUDED_LAYOUTS = {"title", "section-divider", "closing"}


def _build_agenda_items(deck_dir, deck, briefs, self_id):
    """Build <li> elements for the agenda slide. Excludes structural slides and self."""
    items = []
    for sid in deck["slides"]:
        if sid == self_id:
            continue
        b = briefs.get(sid)
        if b is None or isinstance(b, deckparse.DeckParseError):
            continue
        f = b["front_matter"]
        if f.get("layout") in _AGENDA_EXCLUDED_LAYOUTS:
            continue
        label = f.get("title") or b["body"].get("key_message") or sid
        # Truncate key message to first line only
        label = label.split("\n")[0].strip()
        label_esc = html.escape(label)
        duration = f.get("duration")
        if duration:
            dur_html = f'<span class="duration">{html.escape(str(duration))} min</span>'
        else:
            dur_html = ""
        items.append(f"      <li>{label_esc}{dur_html}</li>")
    return "\n".join(items) if items else "      <li>(no slides found)</li>"


# ---------------------------------------------------------------------------
# Main resolution logic
# ---------------------------------------------------------------------------


def _resolve_one(deck_dir, deck, briefs, sid, slide_pos, catalog_path):
    """Resolve a single catalog slide. Returns (ok, message)."""
    b = briefs.get(sid)
    if b is None or isinstance(b, deckparse.DeckParseError):
        return False, f"  ✗ {sid}: brief missing or invalid — skipping"

    f = b["front_matter"]
    use = f.get("use")
    if not use or not use.startswith("catalog/"):
        return False, f"  ✗ {sid}: not a catalog slide"

    catalog_id = use[len("catalog/"):]

    # Load catalog slide metadata
    try:
        meta = _load_catalog_slide_meta(catalog_path, catalog_id)
    except (FileNotFoundError, ValueError) as e:
        return False, f"  ✗ {sid}: {e}"

    # Load the HTML template
    html_path = os.path.join(catalog_path, "slides", catalog_id, "slide.html")
    if not os.path.isfile(html_path):
        return False, f"  ✗ {sid}: {html_path}: HTML template not found"
    with open(html_path, encoding="utf-8") as fh:
        fragment = fh.read()

    # Merge params: catalog defaults first, brief params override
    catalog_defaults = dict(meta["params"])
    params = dict(catalog_defaults)
    params.update(f.get("params") or {})

    # Resolve aria-label
    aria_title = (
        f.get("title")
        or params.get("title")
        or meta.get("description", catalog_id)
    )
    aria_label = f"Slide {slide_pos}: {aria_title}"
    params["aria-label"] = aria_label

    # Derived slides: populate generated params (inserted raw — trusted HTML)
    raw_keys = set()
    if meta["kind"] == "derived":
        if catalog_id == "agenda":
            params["agenda_items"] = _build_agenda_items(
                deck_dir, deck, briefs, sid
            )
            raw_keys.add("agenda_items")
        else:
            return False, f"  ✗ {sid}: unknown derived kind for catalog/{catalog_id}"

    # Warn about empty params before substituting
    _warn_empty_params(fragment, catalog_defaults, params, sid)

    # Param substitution
    fragment = _substitute_params(fragment, params, raw_keys=raw_keys)

    # Rewrite data-slide and CSS selectors
    fragment = _rewrite_data_slide(fragment, catalog_id, sid)

    # Rewrite aria-label (in case the template's aria-label was substituted above,
    # this is now a no-op; but keeps us safe if {{aria-label}} was not in the template)
    fragment = _rewrite_aria_label(fragment, html.escape(aria_label))

    # Inject/update data-catalog provenance
    fragment = _inject_data_catalog(fragment, catalog_id, meta["version"])

    # Copy assets if the catalog slide has any
    assets_src = os.path.join(catalog_path, "slides", catalog_id, "assets")
    if os.path.isdir(assets_src):
        assets_dst = os.path.join(deck_dir, "assets", "images", f"catalog-{catalog_id}")
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
        # Rewrite relative asset paths from catalog/slides/<id>/assets/ to
        # the build-relative path ../assets/images/catalog-<id>/
        fragment = fragment.replace(
            "assets/",
            f"../assets/images/catalog-{catalog_id}/",
        )

    # Write to content/<deck-slide-id>.html
    content_dir = os.path.join(deck_dir, "content")
    os.makedirs(content_dir, exist_ok=True)
    out_path = os.path.join(content_dir, sid + ".html")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(fragment)

    return True, f"  ✓ {sid} ← catalog/{catalog_id}@{meta['version']}"


def cmd_resolve(deck_dir, catalog_override=None):
    """Resolve all catalog slides in deck_dir."""
    deck_yml = os.path.join(deck_dir, "deck.yml")
    if not os.path.isfile(deck_yml):
        print(f"{deck_yml}: not found", file=sys.stderr)
        return 1

    catalog_path = _find_catalog(catalog_override)
    if not catalog_path:
        print(
            "Catalog not found. Set $UW_SLIDES_HOME or pass --catalog=<path>.",
            file=sys.stderr,
        )
        return 1

    try:
        deck, briefs = deckparse.load_deck_dir(deck_dir)
    except deckparse.DeckParseError as e:
        print(str(e), file=sys.stderr)
        return 1
    except OSError as e:
        print(f"{e.filename}: {e.strerror}", file=sys.stderr)
        return 1

    def _is_catalog_slide(b):
        return (
            isinstance(b, dict)
            and (b["front_matter"].get("use") or "").startswith("catalog/")
        )

    catalog_slides = [sid for sid in deck["slides"] if _is_catalog_slide(briefs.get(sid))]

    if not catalog_slides:
        print("No catalog slides to resolve.")
        return 0

    print(f"Resolving catalog slides (catalog: {catalog_path})...")
    ok_count = 0
    for sid in deck["slides"]:
        if not _is_catalog_slide(briefs.get(sid)):
            continue
        pos = deck["slides"].index(sid) + 1
        ok, msg = _resolve_one(deck_dir, deck, briefs, sid, pos, catalog_path)
        print(msg)
        if ok:
            ok_count += 1

    print(f"\nResolved {ok_count} of {len(catalog_slides)} catalog slide(s).")
    return 0 if ok_count == len(catalog_slides) else 1


# ---------------------------------------------------------------------------
# Eject
# ---------------------------------------------------------------------------


def cmd_eject(deck_dir, slide_id, catalog_override=None):
    """Eject a catalog slide: remove use:, set locked: true."""
    brief_path = os.path.join(deck_dir, "slides", slide_id + ".md")
    if not os.path.isfile(brief_path):
        print(f"{brief_path}: not found", file=sys.stderr)
        return 1

    with open(brief_path, encoding="utf-8") as fh:
        original = fh.read()

    try:
        brief = deckparse.parse_brief(original, brief_path)
    except deckparse.DeckParseError as e:
        print(str(e), file=sys.stderr)
        return 1

    use = brief["front_matter"].get("use")
    if not use:
        print(f"{brief_path}: slide does not have a 'use:' field; nothing to eject", file=sys.stderr)
        return 1

    catalog_id = use[len("catalog/"):] if use.startswith("catalog/") else use

    # Find catalog to get description for key message
    catalog_path = _find_catalog(catalog_override)
    description = f"Ejected from {use}"
    if catalog_path:
        try:
            meta = _load_catalog_slide_meta(catalog_path, catalog_id)
            description = meta.get("description", description)
        except (FileNotFoundError, ValueError):
            pass

    # Rewrite the brief: remove use:, set locked: true, add key message
    new_brief = _eject_rewrite(original, brief_path, slide_id, use, description)
    if new_brief is None:
        return 1

    with open(brief_path, "w", encoding="utf-8") as fh:
        fh.write(new_brief)

    # Validate the rewritten brief
    try:
        deckparse.parse_brief(new_brief, brief_path)
    except deckparse.DeckParseError as e:
        print(f"Warning: ejected brief does not validate: {e}", file=sys.stderr)
        print(f"Edit {brief_path} manually to fix.", file=sys.stderr)

    print(f"✓ Ejected {slide_id} from {use}")
    print(f"  Brief: {brief_path}")
    print(f"  The HTML in content/{slide_id}.html is unchanged (locked: true).")
    print(f"  Edit the brief and set locked: false to regenerate.")
    return 0


def _eject_rewrite(text, path, slide_id, use_value, description):
    """Rewrite brief text for eject: remove use:, add locked: true, add # Key message."""
    if text.startswith("﻿"):
        text = text[1:]
    rows = text.split("\n")
    if not rows or rows[0].rstrip() != "---":
        print(f"{path}: cannot parse front matter", file=sys.stderr)
        return None
    end = None
    for i in range(1, len(rows)):
        if rows[i].rstrip() == "---":
            end = i
            break
    if end is None:
        print(f"{path}: front matter not closed", file=sys.stderr)
        return None

    fm_lines = rows[1:end]
    body_lines = rows[end + 1:]

    # Remove use: line and params: block from front matter
    new_fm = []
    skip_block = False
    for line in fm_lines:
        stripped = line.lstrip()
        if stripped.startswith("use:"):
            continue  # drop it
        if stripped.startswith("params:"):
            skip_block = True
            continue
        if skip_block:
            # Skip indented lines belonging to params block
            if line and (line[0] == " " or line[0] == "\t"):
                continue
            else:
                skip_block = False
        new_fm.append(line)

    # Add locked: true
    new_fm.append("locked: true")

    # Check if body already has # Key message
    body_text = "\n".join(body_lines)
    if "# Key message" not in body_text:
        # Prepend key message to body
        km_line = f"# Key message\n{description}\n\n## Notes\nEjected from {use_value}. Edit this brief and set locked: false to regenerate.\n"
        body_text = km_line + body_text.lstrip("\n")

    fm_text = "\n".join(new_fm)
    return "---\n" + fm_text + "\n---\n" + body_text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv):
    args = argv[1:]

    # Extract --catalog= flag
    catalog_override = None
    remaining = []
    for a in args:
        if a.startswith("--catalog="):
            catalog_override = a[len("--catalog="):]
        else:
            remaining.append(a)
    args = remaining

    if not args or args[0] not in ("resolve", "eject"):
        print(__doc__, file=sys.stderr)
        return 2

    cmd = args[0]

    if cmd == "resolve":
        if len(args) != 2:
            print("Usage: resolve-catalog.py resolve <deck-dir> [--catalog=<path>]", file=sys.stderr)
            return 2
        return cmd_resolve(args[1], catalog_override)

    if cmd == "eject":
        if len(args) != 3:
            print("Usage: resolve-catalog.py eject <deck-dir> <slide-id> [--catalog=<path>]", file=sys.stderr)
            return 2
        return cmd_eject(args[1], args[2], catalog_override)

    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
