#!/usr/bin/env python3
"""Parser and validator for deck.yml and slide briefs (stdlib only).

Implements the restricted YAML subset defined in references/slide-schema.md.
Everything accepted is valid YAML; anything outside the subset is rejected
with "<file>:<line>: <message>" and exit status 1.

Usage:
  deckparse.py deck  <deck.yml> [--format json|ids]
  deckparse.py brief <slides/id.md> [--format json|kv]
  deckparse.py hash  <slides/id.md>
  deckparse.py status  <deck-dir> [--format table|json]
  deckparse.py outline <deck-dir>

status reports, per slide in deck.yml order, whether content/<id>.html needs
generating (missing), is out of date (stale) or must be left alone (locked,
catalog). outline prints OUTLINE.md (read-only overview) to stdout.
"""

import hashlib
import json
import os
import re
import sys
import unicodedata

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
SLOT_RE = re.compile(r"^[a-z][a-z0-9-]*$")


class DeckParseError(Exception):
    def __init__(self, path, line, message):
        super().__init__(message)
        self.path, self.line, self.message = path, line, message

    def __str__(self):
        where = f"{self.path}:{self.line}" if self.line else str(self.path)
        return f"{where}: {self.message}"


# --------------------------------------------------------------------------
# Restricted YAML subset
# --------------------------------------------------------------------------

INT_RE = re.compile(r"^-?(0|[1-9][0-9]*)$")
AMBIGUOUS_NUMBER_RES = [
    re.compile(r"^[+-]?[0-9]+$"),
    re.compile(r"^[+-]?([0-9]+\.[0-9]*|\.[0-9]+)([eE][+-]?[0-9]+)?$"),
    re.compile(r"^[+-]?[0-9]+[eE][+-]?[0-9]+$"),
    re.compile(r"^[+-]?0[xXoObB][0-9a-fA-F_]+$"),
    re.compile(r"^[+-]?\.(inf|Inf|INF|nan|NaN|NAN)$"),
    re.compile(r"^[0-9]+(:[0-9]+)+(\.[0-9]*)?$"),  # YAML 1.1 sexagesimal
]
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}([Tt ].*)?$")
AMBIGUOUS_WORDS = {"Null", "NULL", "True", "TRUE", "False", "FALSE"}
RESERVED_START = {
    "&": "anchors and aliases are not supported",
    "*": "anchors and aliases are not supported",
    "!": "tags are not supported",
    "|": "multi-line block scalars are not supported",
    ">": "multi-line block scalars are not supported",
    "%": "directives are not supported; quote the value",
    "@": "reserved indicator; quote the value",
    "`": "reserved indicator; quote the value",
    ",": "reserved indicator; quote the value",
    "]": "reserved indicator; quote the value",
    "}": "reserved indicator; quote the value",
}
MULTILINE_MSG = "unexpected indentation (multi-line values are not supported)"


def _parse_quoted(s, path, line):
    quote = s[0]
    out, i = [], 1
    while i < len(s):
        c = s[i]
        if quote == '"' and c == "\\":
            if i + 1 >= len(s) or s[i + 1] not in '"\\':
                raise DeckParseError(
                    path, line, 'unsupported escape in double-quoted string (only \\" and \\\\)'
                )
            out.append(s[i + 1])
            i += 2
        elif c == quote:
            if quote == "'" and s[i + 1 : i + 2] == "'":
                out.append("'")
                i += 2
                continue
            rest = s[i + 1 :].strip()
            if rest.startswith("#"):
                raise DeckParseError(path, line, "trailing comments are not supported")
            if rest:
                raise DeckParseError(path, line, "unexpected text after closing quote")
            return "".join(out)
        else:
            out.append(c)
            i += 1
    raise DeckParseError(path, line, "unterminated quoted string (multi-line strings are not supported)")


def parse_scalar(s, path, line, allow_empty_list=False):
    s = s.strip()
    if s[0] in "\"'":
        return _parse_quoted(s, path, line)
    if s[0] == "[":
        if allow_empty_list and s == "[]":
            return []
        raise DeckParseError(path, line, "flow-style collections are not supported (only [] for an empty list)")
    if s[0] == "{":
        raise DeckParseError(path, line, "flow-style collections are not supported")
    if s[0] in RESERVED_START:
        raise DeckParseError(path, line, RESERVED_START[s[0]])
    if s[0] == "#":
        raise DeckParseError(path, line, "comments after a key are not supported")
    if s.startswith(("? ", ": ", "- ")) or s in ("?", ":", "-"):
        raise DeckParseError(path, line, "unsupported YAML construct; quote the value")
    if "\t" in s:
        raise DeckParseError(path, line, "tabs are not allowed in unquoted values")
    if " #" in s:
        raise DeckParseError(path, line, "trailing comments are not supported; quote the value if it contains ' #'")
    if ": " in s or s.endswith(":"):
        raise DeckParseError(path, line, "unquoted value contains ':'; quote it (maps inside values or lists are not supported)")
    if s == "true":
        return True
    if s == "false":
        return False
    if s in ("null", "~"):
        return None
    if s in AMBIGUOUS_WORDS:
        raise DeckParseError(path, line, f"ambiguous value {s!r}; use lowercase true/false/null or quote it")
    if INT_RE.match(s):
        return int(s)
    if DATE_RE.match(s) or any(r.match(s) for r in AMBIGUOUS_NUMBER_RES):
        raise DeckParseError(path, line, f"ambiguous number or date {s!r}; quote it to keep it a string")
    return s


def _tokenize(text, path, first_line):
    toks = []
    for i, raw in enumerate(text.split("\n")):
        line = first_line + i
        raw = raw.rstrip("\r")
        stripped = raw.lstrip(" ")
        if not stripped.strip():
            continue
        if stripped.startswith("\t"):
            raise DeckParseError(path, line, "tabs are not allowed for indentation")
        if stripped.startswith("#"):
            continue
        if raw.rstrip() in ("---", "...") or raw.startswith(("--- ", "... ")):
            raise DeckParseError(path, line, "document markers are not supported")
        toks.append((line, len(raw) - len(stripped), stripped.rstrip()))
    return toks


KEY_LINE_RE = re.compile(r"^([^:]*):(?:\s+(.*))?$")


def _split_key(content, path, line):
    m = KEY_LINE_RE.match(content)
    if not m:
        raise DeckParseError(path, line, "expected 'key: value' (a space must follow the colon)")
    key, rest = m.group(1).rstrip(), (m.group(2) or "").strip()
    if not KEY_RE.match(key):
        raise DeckParseError(
            path, line, f"invalid key {key!r} (letters, digits, '_' and '-', starting with a letter or '_')"
        )
    return key, rest


def _is_item(content):
    return content == "-" or content.startswith("- ")


def parse_subset(text, path="<string>", first_line=1):
    """Parse the subset. Returns (data, lines); lines maps key tuples to line numbers."""
    if text.startswith("\ufeff"):
        text = text[1:]
    toks = _tokenize(text, path, first_line)
    data, lines = {}, {}
    i = 0
    while i < len(toks):
        line, indent, content = toks[i]
        if indent != 0:
            raise DeckParseError(path, line, MULTILINE_MSG)
        if _is_item(content):
            raise DeckParseError(path, line, "top level must be 'key: value' pairs, not a list")
        key, rest = _split_key(content, path, line)
        if key in data:
            raise DeckParseError(path, line, f"duplicate key {key!r}")
        lines[(key,)] = line
        i += 1
        if rest:
            data[key] = parse_scalar(rest, path, line, allow_empty_list=True)
            if i < len(toks) and toks[i][1] > 0:
                raise DeckParseError(path, toks[i][0], MULTILINE_MSG)
            continue
        nxt = toks[i] if i < len(toks) else None
        if not nxt or (nxt[1] == 0 and not _is_item(nxt[2])):
            data[key] = None
            continue
        block_indent = nxt[1]
        is_list = _is_item(nxt[2])
        block = [] if is_list else {}
        while i < len(toks):
            bline, bindent, bcontent = toks[i]
            if bindent == 0 and not (is_list and block_indent == 0 and _is_item(bcontent)):
                break
            if bindent != block_indent:
                raise DeckParseError(path, bline, "inconsistent indentation or nesting deeper than one level")
            if _is_item(bcontent) != is_list:
                raise DeckParseError(path, bline, "cannot mix list items and 'key: value' pairs")
            if is_list:
                item = bcontent[1:].strip()
                if not item:
                    raise DeckParseError(path, bline, "empty list item")
                lines[(key, len(block))] = bline
                block.append(parse_scalar(item, path, bline))
            else:
                sub, srest = _split_key(bcontent, path, bline)
                if sub in block:
                    raise DeckParseError(path, bline, f"duplicate key {sub!r}")
                lines[(key, sub)] = bline
                if srest:
                    block[sub] = parse_scalar(srest, path, bline)
                else:
                    if i + 1 < len(toks) and toks[i + 1][1] > block_indent:
                        raise DeckParseError(path, toks[i + 1][0], "nesting deeper than one level is not supported")
                    block[sub] = None
            i += 1
            if i < len(toks) and toks[i][1] > block_indent:
                raise DeckParseError(path, toks[i][0], "nested values or multi-line values are not supported")
        data[key] = block
    return data, lines


# --------------------------------------------------------------------------
# Validation helpers
# --------------------------------------------------------------------------


def _check_keys(data, lines, path, allowed, required):
    for k in data:
        if k not in allowed:
            raise DeckParseError(path, lines[(k,)], f"unknown field {k!r} (allowed: {', '.join(sorted(allowed))})")
    for k in required:
        if k not in data:
            raise DeckParseError(path, None, f"missing required field {k!r}")


def _expect(data, lines, path, key, kind):
    if key not in data:
        return
    v = data[key]
    if kind == "map" and v is None:
        return
    ok = {
        "str": isinstance(v, str) and v != "",
        "int": isinstance(v, int) and not isinstance(v, bool) and v > 0,
        "bool": isinstance(v, bool),
        "map": isinstance(v, dict),
        "list": isinstance(v, list),
    }[kind]
    if not ok:
        names = {"str": "a non-empty string", "int": "a positive integer", "bool": "true or false",
                 "map": "a map", "list": "a list"}
        raise DeckParseError(path, lines[(key,)], f"{key!r} must be {names[kind]}")


# --------------------------------------------------------------------------
# deck.yml
# --------------------------------------------------------------------------

DECK_FIELDS = {"title", "audience", "duration", "presenter", "date", "catalog", "objectives", "slides"}


def parse_deck(text, path="deck.yml"):
    data, lines = parse_subset(text, path)
    _check_keys(data, lines, path, DECK_FIELDS, ["title", "slides"])
    for k in ("title", "audience", "presenter", "date", "catalog"):
        _expect(data, lines, path, k, "str")
    _expect(data, lines, path, "duration", "int")
    _expect(data, lines, path, "slides", "list")
    if "objectives" in data:
        _expect(data, lines, path, "objectives", "map")
        data["objectives"] = data["objectives"] or {}
        for k, v in data["objectives"].items():
            if not isinstance(v, str) or not v:
                raise DeckParseError(path, lines[("objectives", k)], f"objective {k!r} needs a text value")
    seen = set()
    for n, sid in enumerate(data["slides"]):
        ln = lines[("slides", n)]
        if not isinstance(sid, str) or not ID_RE.match(sid):
            raise DeckParseError(path, ln, f"invalid slide ID {sid!r} (lowercase letters, digits and single hyphens)")
        if sid in seen:
            raise DeckParseError(path, ln, f"duplicate slide ID {sid!r}")
        seen.add(sid)
    return data


# --------------------------------------------------------------------------
# slide briefs
# --------------------------------------------------------------------------

BRIEF_FIELDS = {
    "id", "title", "layout", "layout_rationale", "layout_intent", "objective", "owner",
    "status", "duration", "locked", "use", "params", "section",
}
STATUSES = ("draft", "review", "done")
USE_RE = re.compile(r"^catalog/[a-z0-9]+(-[a-z0-9]+)*$")
SECTION_NAMES = {"Talking points": "talking_points", "Source": "source", "Notes": "notes"}
FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,2}) +(\S.*?)\s*$")


def normalize_text(lines):
    """NFC, no trailing whitespace, collapsed blank runs, trimmed ends."""
    out, blank = [], False
    for ln in lines:
        ln = unicodedata.normalize("NFC", ln.rstrip())
        if not ln:
            blank = True
            continue
        if blank and out:
            out.append("")
        blank = False
        out.append(ln)
    return "\n".join(out)


def parse_body(text, path, first_line):
    sections, seen = {}, set()
    cur, fence = None, None
    for i, raw in enumerate(text.split("\n")):
        line = first_line + i
        raw = raw.rstrip("\r")
        m_fence = FENCE_RE.match(raw)
        if fence:
            if m_fence and m_fence.group(1) == fence:
                fence = None
        elif m_fence:
            fence = m_fence.group(1)
        else:
            m = HEADING_RE.match(raw)
            if m:
                level, name = len(m.group(1)), m.group(2)
                if level == 1:
                    if name != "Key message":
                        raise DeckParseError(
                            path, line, f"unknown heading '# {name}' (only '# Key message' is allowed at level 1)"
                        )
                    key = "key_message"
                elif name in SECTION_NAMES:
                    key = SECTION_NAMES[name]
                elif name.startswith("Slot:") and SLOT_RE.match(name[5:].strip()):
                    key = "slot:" + name[5:].strip()
                else:
                    raise DeckParseError(
                        path, line,
                        f"unknown section '## {name}' (allowed: Talking points, Source, Notes, Slot: <name>)",
                    )
                if key in seen:
                    raise DeckParseError(path, line, f"duplicate section {name!r}")
                seen.add(key)
                cur = key
                sections[cur] = []
                continue
        if cur is None:
            if raw.strip():
                raise DeckParseError(path, line, "content before the first heading (start with '# Key message')")
            continue
        sections[cur].append(raw)
    body = {"key_message": None, "talking_points": None, "source": None, "notes": None, "slots": {}}
    for key, content in sections.items():
        norm = normalize_text(content)
        if key.startswith("slot:"):
            body["slots"][key[5:]] = norm
        else:
            body[key] = norm
    return body


def split_front_matter(text, path):
    if text.startswith("\ufeff"):
        text = text[1:]
    rows = text.split("\n")
    if rows[0].rstrip() != "---":
        raise DeckParseError(path, 1, "brief must start with a '---' front matter block")
    for i in range(1, len(rows)):
        if rows[i].rstrip() == "---":
            return "\n".join(rows[1:i]), 2, "\n".join(rows[i + 1 :]), i + 2
    raise DeckParseError(path, 1, "front matter is not closed with '---'")


def parse_brief(text, path="brief.md"):
    fm_text, fm_line, body_text, body_line = split_front_matter(text, path)
    data, lines = parse_subset(fm_text, path, fm_line)
    _check_keys(data, lines, path, BRIEF_FIELDS, ["id"])
    for k in ("title", "layout", "layout_rationale", "layout_intent", "owner", "section", "use", "status"):
        _expect(data, lines, path, k, "str")
    _expect(data, lines, path, "duration", "int")
    _expect(data, lines, path, "locked", "bool")
    _expect(data, lines, path, "params", "map")
    if "objective" in data:
        obj = data["objective"]
        if isinstance(obj, str) and obj:
            data["objective"] = [obj]
        elif not (isinstance(obj, list) and obj and all(isinstance(o, str) and o for o in obj)):
            raise DeckParseError(path, lines[("objective",)], "'objective' must be an objective ID or a list of IDs")

    sid = data["id"]
    if not isinstance(sid, str) or not ID_RE.match(sid):
        raise DeckParseError(path, lines[("id",)], f"invalid id {sid!r} (lowercase letters, digits and single hyphens)")
    stem = os.path.basename(str(path))
    if stem.endswith(".md") and not stem.startswith("_") and stem[:-3] != sid:
        raise DeckParseError(path, lines[("id",)], f"id {sid!r} does not match the file name {stem!r}")
    if data.get("status", "draft") not in STATUSES:
        raise DeckParseError(path, lines.get(("status",)), f"status must be one of {', '.join(STATUSES)}")
    layout = data.get("layout")
    if layout is not None and layout not in ("auto", "custom") and not ID_RE.match(layout):
        raise DeckParseError(path, lines[("layout",)], f"invalid layout {layout!r} (auto, custom or a layout ID)")
    if layout == "custom" and not data.get("layout_intent"):
        raise DeckParseError(path, lines[("layout",)], "layout 'custom' requires 'layout_intent'")
    if "layout_intent" in data and layout != "custom":
        raise DeckParseError(path, lines[("layout_intent",)], "'layout_intent' is only allowed with layout: custom")
    use = data.get("use")
    if use is not None:
        if not USE_RE.match(use):
            raise DeckParseError(path, lines[("use",)], f"invalid use {use!r} (expected catalog/<id>)")
        if "layout" in data or "layout_intent" in data:
            raise DeckParseError(
                path, lines[("use",)], "'use' cannot be combined with 'layout'; catalog slides bring their own layout"
            )

    body = parse_body(body_text, path, body_line)
    if use is None and not body["key_message"]:
        raise DeckParseError(path, None, "missing or empty '# Key message' (required unless 'use' is set)")

    front = {
        "id": sid,
        "title": data.get("title"),
        "layout": layout or "auto",
        "layout_rationale": data.get("layout_rationale"),
        "layout_intent": data.get("layout_intent"),
        "objective": data.get("objective", []),
        "owner": data.get("owner"),
        "status": data.get("status", "draft"),
        "duration": data.get("duration"),
        "locked": data.get("locked", False),
        "use": use,
        "params": data.get("params") or {},
        "section": data.get("section"),
    }
    return {"front_matter": front, "body": body}


def brief_hash(brief):
    """Staleness hash (data-brief-hash); see references/slide-schema.md."""
    f, b = brief["front_matter"], brief["body"]
    material = {
        "id": f["id"], "title": f["title"], "layout": f["layout"],
        "layout_intent": f["layout_intent"], "use": f["use"], "params": f["params"],
        "key_message": b["key_message"], "talking_points": b["talking_points"],
        "source": b["source"], "slots": b["slots"],
    }
    canon = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------
# whole-deck operations: status and outline
# --------------------------------------------------------------------------

SECTION_TAG_RE = re.compile(r"<section\b([^>]*)>", re.S)
HASH_ATTR_RE = re.compile(r"""\bdata-brief-hash\s*=\s*["']([^"']*)["']""")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _fragment_hash(path):
    """data-brief-hash of the first <section> in a fragment, or None."""
    m = SECTION_TAG_RE.search(_read(path))
    if not m:
        return None
    h = HASH_ATTR_RE.search(m.group(1))
    return h.group(1) if h else None


def load_deck_dir(deck_dir):
    """Parse deck.yml and every listed brief. Returns (deck, {id: brief|DeckParseError|None})."""
    deck = parse_deck(_read(os.path.join(deck_dir, "deck.yml")), os.path.join(deck_dir, "deck.yml"))
    briefs = {}
    for sid in deck["slides"]:
        path = os.path.join(deck_dir, "slides", sid + ".md")
        if not os.path.isfile(path):
            briefs[sid] = None
            continue
        try:
            briefs[sid] = parse_brief(_read(path), path)
        except DeckParseError as e:
            briefs[sid] = e
    return deck, briefs


def _orphans(deck_dir, listed, sub, ext):
    folder = os.path.join(deck_dir, sub)
    if not os.path.isdir(folder):
        return []
    found = {n[: -len(ext)] for n in os.listdir(folder) if n.endswith(ext) and not n.startswith("_")}
    return sorted(found - set(listed))


def deck_status(deck_dir):
    """Per-slide generation state. States:

    no-brief   listed in deck.yml but slides/<id>.md is missing
    invalid    the brief does not parse (see "error")
    catalog    brief has `use:`; copied by the catalog resolver, never generated
    locked     brief has `locked: true`; the HTML is hand-edited, never overwritten
    missing    no content/<id>.html yet
    untracked  HTML exists but has no data-brief-hash (hand-written or legacy)
    stale      HTML was generated from a different version of the brief
    fresh      HTML matches the brief
    """
    deck, briefs = load_deck_dir(deck_dir)
    slides = []
    for sid in deck["slides"]:
        b = briefs[sid]
        html = os.path.join(deck_dir, "content", sid + ".html")
        row = {"id": sid, "state": None, "layout": None, "brief_hash": None, "html_hash": None}
        if b is None:
            row["state"] = "no-brief"
        elif isinstance(b, DeckParseError):
            row["state"], row["error"] = "invalid", str(b)
        else:
            f = b["front_matter"]
            row["layout"] = f["use"] or f["layout"]
            row["brief_hash"] = brief_hash(b)
            has_html = os.path.isfile(html)
            if has_html:
                row["html_hash"] = _fragment_hash(html)
            if f["use"]:
                row["state"] = "catalog"
            elif f["locked"]:
                row["state"] = "locked"
            elif not has_html:
                row["state"] = "missing"
            elif row["html_hash"] is None:
                row["state"] = "untracked"
            else:
                row["state"] = "fresh" if row["html_hash"] == row["brief_hash"] else "stale"
        slides.append(row)
    listed = deck["slides"]
    return {
        "slides": slides,
        "orphan_briefs": _orphans(deck_dir, listed, "slides", ".md"),
        "orphan_fragments": _orphans(deck_dir, listed, "content", ".html"),
    }


def _cell(text):
    return " ".join(str(text).split()).replace("|", "\\|") if text else ""


def render_outline(deck_dir):
    """Read-only Markdown overview. Deterministic: the same inputs give the same bytes."""
    deck, briefs = load_deck_dir(deck_dir)
    out = [
        "<!-- GENERATED by tools/deckparse.py outline from deck.yml and slides/*.md. -->",
        "<!-- Do not edit: changes are overwritten. Edit deck.yml or the briefs instead. -->",
        "",
        f"# Outline: {deck['title']}",
        "",
    ]
    if deck.get("audience"):
        out.append(f"- Audience: {deck['audience']}")
    if deck.get("presenter"):
        out.append(f"- Presenter: {deck['presenter']}")
    planned, unknown = 0, 0
    for sid in deck["slides"]:
        b = briefs[sid]
        d = b["front_matter"]["duration"] if isinstance(b, dict) else None
        if d is None:
            unknown += 1
        else:
            planned += d
    target = f" of {deck['duration']}" if deck.get("duration") is not None else ""
    note = f" ({unknown} slide(s) without a duration)" if unknown else ""
    out += [f"- Slides: {len(deck['slides'])}", f"- Planned minutes: {planned}{target}{note}", ""]
    out += [
        "| # | ID | Key message | Layout | Min | Owner | Status | Objective |",
        "|---|----|-------------|--------|-----|-------|--------|-----------|",
    ]
    covered = {}
    for n, sid in enumerate(deck["slides"], 1):
        b = briefs[sid]
        if b is None:
            out.append(f"| {n} | {sid} | (missing brief) | | | | | |")
            continue
        if isinstance(b, DeckParseError):
            out.append(f"| {n} | {sid} | (invalid brief) | | | | | |")
            continue
        f, body = b["front_matter"], b["body"]
        msg = body["key_message"] or ("(catalog slide)" if f["use"] else "")
        layout = f["use"] or f["layout"]
        out.append(
            "| " + " | ".join([
                str(n), sid, _cell(msg), _cell(layout), _fmt(f["duration"]),
                _cell(f["owner"]), f["status"] + (" (locked)" if f["locked"] else ""),
                _cell(", ".join(f["objective"])),
            ]) + " |"
        )
        for o in f["objective"]:
            covered.setdefault(o, []).append(sid)
    if deck.get("objectives"):
        out += ["", "## Objectives", ""]
        for oid, text in deck["objectives"].items():
            ids = covered.get(oid)
            out.append(f"- {oid}: {text} ({', '.join(ids) if ids else 'NOT COVERED'})")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def _kv(brief):
    out = []
    for k, v in brief["front_matter"].items():
        if k == "params":
            out.extend(f"params.{pk}={_fmt(pv)}" for pk, pv in v.items())
        elif k == "objective":
            out.append(f"objective={','.join(v)}")
        else:
            out.append(f"{k}={_fmt(v)}")
    return out


BLOCKING_STATES = ("no-brief", "invalid")


def _deck_command(cmd, deck_dir, fmt):
    if fmt is not None and not (cmd == "status" and fmt in ("table", "json")):
        print(f"unknown format {fmt!r} for {cmd}", file=sys.stderr)
        return 2
    if not os.path.isfile(os.path.join(deck_dir, "deck.yml")):
        print(f"{deck_dir}: no deck.yml (legacy SLIDES.md decks are not supported by {cmd})", file=sys.stderr)
        return 1
    try:
        if cmd == "outline":
            sys.stdout.write(render_outline(deck_dir))
            return 0
        report = deck_status(deck_dir)
    except DeckParseError as e:
        print(e, file=sys.stderr)
        return 1
    except OSError as e:
        print(f"{e.filename}: {e.strerror}", file=sys.stderr)
        return 1
    if fmt == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for r in report["slides"]:
            detail = r.get("error") or r["layout"] or ""
            print(f"{r['state']:<10} {r['id']:<30} {detail}")
        for label, key in (("orphan-brief", "orphan_briefs"), ("orphan-fragment", "orphan_fragments")):
            for sid in report[key]:
                print(f"{label:<10} {sid}")
    return 1 if any(r["state"] in BLOCKING_STATES for r in report["slides"]) else 0


def main(argv):
    args = argv[1:]
    fmt = None
    if "--format" in args:
        i = args.index("--format")
        if i + 1 >= len(args):
            print(__doc__, file=sys.stderr)
            return 2
        fmt = args[i + 1]
        del args[i : i + 2]
    if len(args) == 2 and args[0] in ("status", "outline"):
        return _deck_command(args[0], args[1], fmt)
    if len(args) != 2 or args[0] not in ("deck", "brief", "hash"):
        print(__doc__, file=sys.stderr)
        return 2
    cmd, path = args
    allowed = {"deck": ("json", "ids"), "brief": ("json", "kv"), "hash": ()}[cmd]
    if fmt is not None and fmt not in allowed:
        print(f"unknown format {fmt!r} for {cmd}", file=sys.stderr)
        return 2
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        print(f"{path}: {e.strerror}", file=sys.stderr)
        return 1
    try:
        if cmd == "deck":
            deck = parse_deck(text, path)
            if fmt == "ids":
                print("\n".join(deck["slides"]))
            else:
                print(json.dumps(deck, indent=2, ensure_ascii=False))
        else:
            brief = parse_brief(text, path)
            if cmd == "hash":
                print(brief_hash(brief))
            elif fmt == "kv":
                print("\n".join(_kv(brief)))
            else:
                brief["hash"] = brief_hash(brief)
                print(json.dumps(brief, indent=2, ensure_ascii=False))
    except DeckParseError as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
