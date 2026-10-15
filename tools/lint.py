#!/usr/bin/env python3
"""Deterministic linter for uw-slides decks (stdlib only).

Usage:
  lint.py <deck-dir>                   # lint all slides; exit 1 on errors
  lint.py <deck-dir> --strict          # exit 1 on warnings too
  lint.py <deck-dir> --format json     # machine-readable output
  lint.py <deck-dir> --status          # print status table (id, state, brief-status, owner, locked, layout)
  lint.py --contrast <css-file>        # check design-system color-token contrast pairs

Exit codes: 0 = clean, 1 = errors found (or warnings with --strict), 2 = usage/parse error.
"""

import html.parser
import json
import os
import re
import sys

# Import deckparse from the same directory (vendored alongside lint.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deckparse


# ---------------------------------------------------------------------------
# Finding data type
# ---------------------------------------------------------------------------


class Finding:
    __slots__ = ("level", "check", "file", "line", "message")

    def __init__(self, level, check, file, line, message):
        self.level = level    # "ERROR" | "WARN"
        self.check = check    # machine-readable slug
        self.file = str(file)
        self.line = line      # int or None
        self.message = message

    def to_dict(self):
        return {
            "level": self.level,
            "check": self.check,
            "file": self.file,
            "line": self.line,
            "message": self.message,
        }

    def __str__(self):
        loc = f"{self.file}:{self.line}" if self.line else self.file
        return f"{self.level:<5}  {loc}: {self.message}"


def _err(check, file, message, line=None):
    return Finding("ERROR", check, file, line, message)


def _warn(check, file, message, line=None):
    return Finding("WARN", check, file, line, message)


# ---------------------------------------------------------------------------
# HTML parser
# ---------------------------------------------------------------------------


class _SlideParser(html.parser.HTMLParser):
    """Extract the root <section>, <img> elements and <style> blocks."""

    def __init__(self):
        super().__init__()
        self.root_section = None   # {"attrs": {...}, "line": int}
        self.images = []           # [{"attrs": {...}, "line": int}]
        self.styles = []           # [(start_line, css_text)]
        self._depth = 0
        self._in_style = False
        self._style_start = None
        self._style_buf = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        ln = self.getpos()[0]
        if tag == "section" and self._depth == 0:
            self.root_section = {"attrs": attrs_dict, "line": ln}
        if tag == "img":
            self.images.append({"attrs": attrs_dict, "line": ln})
        if tag == "style":
            self._in_style = True
            self._style_start = ln
            self._style_buf = []
        self._depth += 1

    def handle_endtag(self, tag):
        self._depth -= 1
        if tag == "style" and self._in_style:
            self._in_style = False
            self.styles.append((self._style_start, "".join(self._style_buf)))

    def handle_data(self, data):
        if self._in_style:
            self._style_buf.append(data)


# ---------------------------------------------------------------------------
# CSS analysis helpers
# ---------------------------------------------------------------------------

_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_AT_RULE_BLOCK_RE = re.compile(r"@[^{;]+\{[^{}]*\}", re.DOTALL)
_RULE_BLOCK_RE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.DOTALL)

_FONT_SIZE_RE = re.compile(r"font-size\s*:\s*([^;}{]+)", re.IGNORECASE)
_CLAMP_RE = re.compile(r"clamp\(\s*([^,]+),\s*([^,]+),\s*([^)]+)\s*\)", re.IGNORECASE)
_LENGTH_RE = re.compile(r"^([0-9]*\.?[0-9]+)(rem|px|em)$")

# Selectors for source/citation lines — exempt from the 1.5rem floor
_SOURCE_RE = re.compile(
    r"\.(source|citation|cite|footnote|source-line|caption|label|tag|eyebrow)",
    re.IGNORECASE,
)


def _to_rem(s: str):
    """Return the rem equivalent of a plain CSS length, or None if not parseable."""
    s = s.strip()
    m = _LENGTH_RE.match(s)
    if not m:
        return None
    val, unit = float(m.group(1)), m.group(2)
    if unit == "rem":
        return val
    if unit == "px":
        return val / 16.0
    # treat em ≈ rem for this check
    return val


def _clamp_min(value: str):
    """Return the minimum (first) arg of a clamp() as rem, or None."""
    m = _CLAMP_RE.match(value.strip())
    if not m:
        return None
    return _to_rem(m.group(1))


def _strip_css(css: str) -> str:
    """Remove comments and simple @-rule blocks."""
    css = _COMMENT_RE.sub("", css)
    css = _AT_RULE_BLOCK_RE.sub("", css)
    return css


def check_css_scoping(css: str, slide_id: str, style_line: int, path: str) -> list:
    """Every rule must be scoped to section[data-slide='<slide_id>']."""
    findings = []
    scope = f'section[data-slide="{slide_id}"]'
    for m in _RULE_BLOCK_RE.finditer(_strip_css(css)):
        raw_selector = m.group(1).strip()
        for sel in raw_selector.split(","):
            sel = sel.strip()
            if sel and not sel.startswith(scope):
                findings.append(_err(
                    "css-not-scoped",
                    path,
                    f"CSS selector {sel!r} is not scoped to "
                    f'section[data-slide="{slide_id}"] — styles may leak to other slides',
                    style_line,
                ))
    return findings


_SKIP_FS_RE = re.compile(r"(var\s*\(|calc\s*\(|clamp\s*\()", re.IGNORECASE)
_KEYWORD_FS = {
    "inherit", "initial", "unset", "revert",
    "xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large",
    "smaller", "larger",
}


def check_css_font_sizes(css: str, slide_id: str, style_line: int, path: str) -> list:
    """Flag font-size values below the minimum thresholds."""
    findings = []
    for m in _RULE_BLOCK_RE.finditer(_strip_css(css)):
        selector = m.group(1).strip()
        block = m.group(0)
        is_source = bool(_SOURCE_RE.search(selector))
        floor = 1.0 if is_source else 1.5

        for fs_m in _FONT_SIZE_RE.finditer(block):
            raw = fs_m.group(1).strip()
            if not raw or raw == "0":
                continue
            if raw.lower() in _KEYWORD_FS:
                continue
            if _SKIP_FS_RE.search(raw):
                # clamp() — check the minimum arg only
                if raw.lower().startswith("clamp"):
                    min_rem = _clamp_min(raw)
                    if min_rem is not None:
                        if min_rem < 1.0:
                            findings.append(_err(
                                "font-size-too-small",
                                path,
                                f"font-size clamp minimum {min_rem}rem is below the 1rem floor "
                                f"(selector: {selector!r})",
                                style_line,
                            ))
                        elif min_rem < floor:
                            findings.append(_warn(
                                "font-size-below-minimum",
                                path,
                                f"font-size clamp minimum {min_rem}rem is below {floor}rem "
                                f"(selector: {selector!r}); allowed only for source/citation lines",
                                style_line,
                            ))
                continue
            rem = _to_rem(raw)
            if rem is None:
                continue
            if rem < 1.0:
                findings.append(_err(
                    "font-size-too-small",
                    path,
                    f"font-size {raw} is below the 1rem hard floor "
                    f"(selector: {selector!r})",
                    style_line,
                ))
            elif rem < floor:
                findings.append(_err(
                    "font-size-below-minimum",
                    path,
                    f"font-size {raw} is below the {floor}rem minimum "
                    f"(selector: {selector!r}); use clamp(1.5rem, ...) or larger",
                    style_line,
                ))
    return findings


# ---------------------------------------------------------------------------
# Fragment checks
# ---------------------------------------------------------------------------


def check_fragment(path: str, slide_id: str, expected_hash=None) -> list:
    """Check a single HTML fragment file for structural and style errors."""
    findings = []
    try:
        with open(path, encoding="utf-8") as f:
            html_text = f.read()
    except OSError as e:
        return [_err("fragment-unreadable", path, str(e))]

    parser = _SlideParser()
    try:
        parser.feed(html_text)
    except Exception as e:
        return [_err("fragment-parse-error", path, f"HTML parse error: {e}")]

    sec = parser.root_section
    if sec is None:
        return [_err("no-section", path, "no root <section> element found")]

    attrs = sec["attrs"]
    sec_line = sec["line"]

    # data-slide matches filename
    ds = attrs.get("data-slide", "")
    if ds != slide_id:
        findings.append(_err(
            "data-slide-mismatch",
            path,
            f'data-slide="{ds}" does not match slide ID "{slide_id}"',
            sec_line,
        ))

    # class="slide"
    if "slide" not in attrs.get("class", "").split():
        findings.append(_err(
            "missing-class-slide",
            path,
            'root <section> is missing class="slide"',
            sec_line,
        ))

    # aria-label
    if "aria-label" not in attrs:
        findings.append(_err(
            "missing-aria-label",
            path,
            "root <section> is missing aria-label",
            sec_line,
        ))

    # <img> alt text
    for img in parser.images:
        if "alt" not in img["attrs"]:
            findings.append(_err(
                "img-missing-alt",
                path,
                "<img> is missing alt attribute",
                img["line"],
            ))

    # CSS: scoping and font sizes
    for style_line, css_text in parser.styles:
        findings.extend(check_css_scoping(css_text, slide_id, style_line, path))
        findings.extend(check_css_font_sizes(css_text, slide_id, style_line, path))

    # Staleness
    if expected_hash is not None:
        html_hash = attrs.get("data-brief-hash", "")
        if html_hash and html_hash != expected_hash:
            findings.append(_warn(
                "stale-brief",
                path,
                f"brief changed since HTML was generated "
                f"(html={html_hash!r}, current={expected_hash!r}); "
                "run /uw-slides:generate-slides",
            ))

    return findings


# ---------------------------------------------------------------------------
# Deck lint
# ---------------------------------------------------------------------------


def lint_deck(deck_dir: str) -> list:
    """Run all lint checks on a deck directory. Returns a list of Finding objects."""
    findings = []
    deck_dir = os.path.abspath(deck_dir)
    deck_yml = os.path.join(deck_dir, "deck.yml")

    if not os.path.isfile(deck_yml):
        if os.path.isfile(os.path.join(deck_dir, "SLIDES.md")):
            findings.append(_warn(
                "slides-md-deprecated",
                os.path.join(deck_dir, "SLIDES.md"),
                "SLIDES.md is deprecated; migrate to deck.yml "
                "(references/slide-schema.md §6); lint skipped",
            ))
            return findings
        return [_err("no-deck-yml", deck_yml, "deck.yml not found")]

    # Load deck and briefs via deckparse
    try:
        deck, briefs = deckparse.load_deck_dir(deck_dir)
    except deckparse.DeckParseError as e:
        return [_err("deck-parse-error", deck_yml, str(e))]
    except OSError as e:
        return [_err("deck-unreadable", deck_yml, f"{e.strerror}: {e.filename}")]

    slide_ids = deck.get("slides", [])
    objectives_in_deck = set((deck.get("objectives") or {}).keys())
    objectives_used = set()
    content_dir = os.path.join(deck_dir, "content")

    # Use deck_status for stale hashes + orphan info
    try:
        status_report = deckparse.deck_status(deck_dir)
    except (deckparse.DeckParseError, OSError):
        status_report = {"slides": [], "orphan_briefs": [], "orphan_fragments": []}

    hash_by_id = {r["id"]: r["brief_hash"] for r in status_report["slides"]}

    for sid in slide_ids:
        brief = briefs.get(sid)
        brief_path = os.path.join(deck_dir, "slides", f"{sid}.md")
        frag_path = os.path.join(content_dir, f"{sid}.html")

        # Missing brief
        if brief is None:
            findings.append(_warn(
                "no-brief",
                brief_path,
                f'slides/{sid}.md not found for slide "{sid}"',
            ))
            # Still check the fragment if present
            if os.path.isfile(frag_path):
                findings.extend(check_fragment(frag_path, sid, None))
            elif not isinstance(brief, deckparse.DeckParseError):
                findings.append(_err(
                    "missing-fragment",
                    frag_path,
                    f'content/{sid}.html not found; run /uw-slides:generate-slides',
                ))
            continue

        # Invalid brief
        if isinstance(brief, deckparse.DeckParseError):
            findings.append(_err("brief-parse-error", brief_path, str(brief)))
            continue

        fm = brief["front_matter"]

        # Objective cross-file check
        for o in fm.get("objective", []):
            objectives_used.add(o)
            if objectives_in_deck and o not in objectives_in_deck:
                findings.append(_err(
                    "unknown-objective",
                    brief_path,
                    f'objective "{o}" is not defined in deck.yml objectives',
                ))

        # Catalog slides: skip fragment checks
        if fm.get("use"):
            continue

        # Fragment missing (non-catalog)
        if not os.path.isfile(frag_path):
            findings.append(_err(
                "missing-fragment",
                frag_path,
                f'content/{sid}.html not found; run /uw-slides:generate-slides',
            ))
            continue

        findings.extend(check_fragment(frag_path, sid, hash_by_id.get(sid)))

    # Objective coverage
    for obj_key in objectives_in_deck:
        if obj_key not in objectives_used:
            findings.append(_warn(
                "objective-uncovered",
                deck_yml,
                f'objective "{obj_key}" is not referenced by any slide',
            ))

    # Orphan fragments
    for sid in status_report.get("orphan_fragments", []):
        findings.append(_warn(
            "orphan-fragment",
            os.path.join(content_dir, f"{sid}.html"),
            f'content/{sid}.html is not listed in deck.yml',
        ))

    return findings


# ---------------------------------------------------------------------------
# Status table
# ---------------------------------------------------------------------------


def status_table(deck_dir: str) -> str:
    """Return a human-readable status table: id | state | brief-status | owner | locked | layout."""
    deck_dir = os.path.abspath(deck_dir)

    try:
        status_report = deckparse.deck_status(deck_dir)
        _, briefs = deckparse.load_deck_dir(deck_dir)
    except deckparse.DeckParseError as e:
        return f"Error: {e}\n"
    except OSError as e:
        return f"Error: {e.strerror}: {e.filename}\n"

    headers = ["ID", "state", "brief-status", "owner", "locked", "layout"]
    rows = []
    for row in status_report["slides"]:
        sid = row["id"]
        state = row["state"]
        brief = briefs.get(sid)
        if isinstance(brief, dict):
            fm = brief["front_matter"]
            b_status = fm.get("status") or "—"
            owner = fm.get("owner") or "—"
            locked = "yes" if fm.get("locked") else "no"
            layout = fm.get("use") or fm.get("layout") or "—"
        else:
            b_status = owner = locked = layout = "—"
        rows.append([sid, state, b_status, owner, locked, layout])

    if not rows:
        return "(no slides)\n"

    widths = [
        max(len(headers[i]), max(len(str(r[i])) for r in rows))
        for i in range(len(headers))
    ]
    sep = "  "
    lines = [
        sep.join(h.ljust(widths[i]) for i, h in enumerate(headers)),
        sep.join("-" * w for w in widths),
    ]
    for row in rows:
        lines.append(sep.join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Contrast check (design-system tokens)
# ---------------------------------------------------------------------------

_CSS_VAR_HEX_RE = re.compile(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\b")


def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    if len(h) != 6:
        return None
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return None


def _luminance(r, g, b) -> float:
    def ch(c):
        s = c / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast_ratio(hex1: str, hex2: str):
    c1, c2 = _hex_to_rgb(hex1), _hex_to_rgb(hex2)
    if not c1 or not c2:
        return None
    l1, l2 = _luminance(*c1), _luminance(*c2)
    light, dark = max(l1, l2), min(l1, l2)
    return (light + 0.05) / (dark + 0.05)


# Required contrast pairs for each brand.
# Format: (token-fg, token-bg, min-ratio, description)
_UW_PAIRS = [
    ("uw-spirit-purple", "uw-white",       4.5, "spirit-purple on white (body text)"),
    ("uw-husky-purple",  "uw-white",       4.5, "husky-purple on white (body text)"),
    ("uw-white",         "uw-spirit-purple", 4.5, "white on spirit-purple"),
    ("uw-white",         "uw-husky-purple",  4.5, "white on husky-purple"),
    ("uw-black",         "uw-spirit-gold",   4.5, "black on spirit-gold (body text)"),
    ("uw-spirit-purple", "uw-spirit-gold",   3.0, "spirit-purple on spirit-gold (large/display text)"),
]

_CB_PAIRS = [
    ("cb-white", "cb-deep-navy", 4.5, "white on deep-navy (body text)"),
    ("cb-ink",   "cb-white",     4.5, "ink on white (body text)"),
    ("cb-mist",  "cb-deep-navy", 4.5, "mist on deep-navy"),
]


def check_contrast(css_file: str) -> list:
    """Check WCAG AA contrast for known token pairs in a design-system CSS file."""
    findings = []
    try:
        with open(css_file, encoding="utf-8") as f:
            css_text = f.read()
    except OSError as e:
        return [_err("contrast-unreadable", css_file, str(e))]

    tokens = {m.group(1): m.group(2) for m in _CSS_VAR_HEX_RE.finditer(css_text)}

    pairs = []
    if any(k.startswith("uw-") for k in tokens):
        pairs.extend(_UW_PAIRS)
    if any(k.startswith("cb-") for k in tokens):
        pairs.extend(_CB_PAIRS)

    if not pairs:
        findings.append(_warn(
            "contrast-no-pairs",
            css_file,
            "no recognised UW or CloudBank color tokens found",
        ))
        return findings

    for t_fg, t_bg, min_ratio, desc in pairs:
        h_fg = tokens.get(t_fg)
        h_bg = tokens.get(t_bg)
        if not h_fg or not h_bg:
            findings.append(_warn(
                "contrast-token-missing",
                css_file,
                f"cannot check '{desc}': --{t_fg} or --{t_bg} not found",
            ))
            continue
        ratio = contrast_ratio(h_fg, h_bg)
        if ratio is None:
            continue
        if ratio < min_ratio:
            findings.append(_err(
                "contrast-fail",
                css_file,
                f"{desc}: --{t_fg}={h_fg} on --{t_bg}={h_bg} "
                f"has contrast {ratio:.2f}:1 (minimum {min_ratio}:1 WCAG AA)",
            ))

    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _output(findings: list, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps([f.to_dict() for f in findings], indent=2))
    else:
        for f in findings:
            print(f)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    # --contrast mode
    if argv[0] == "--contrast":
        if len(argv) < 2:
            print("Usage: lint.py --contrast <css-file>", file=sys.stderr)
            sys.exit(2)
        css_file = argv[1]
        fmt = "json" if "--format" in argv[2:] else "table"
        findings = check_contrast(css_file)
        _output(findings, fmt)
        if any(f.level == "ERROR" for f in findings):
            sys.exit(1)
        sys.exit(0)

    deck_dir = argv[0]
    strict = "--strict" in argv
    status_mode = "--status" in argv
    fmt = "table"
    if "--format" in argv:
        i = argv.index("--format")
        if i + 1 < len(argv):
            fmt = argv[i + 1]

    if not os.path.isdir(deck_dir):
        print(f"lint.py: not a directory: {deck_dir!r}", file=sys.stderr)
        sys.exit(2)

    if status_mode:
        print(status_table(deck_dir), end="")
        sys.exit(0)

    findings = lint_deck(deck_dir)
    _output(findings, fmt)

    errors = [f for f in findings if f.level == "ERROR"]
    warnings = [f for f in findings if f.level == "WARN"]

    if fmt != "json":
        if not findings:
            print("✓ lint passed")
        else:
            parts = []
            if errors:
                parts.append(f"{len(errors)} error(s)")
            if warnings:
                parts.append(f"{len(warnings)} warning(s)")
            print(f"{'✗' if errors else '⚠'} {', '.join(parts)}")

    if errors:
        sys.exit(1)
    if strict and warnings:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
