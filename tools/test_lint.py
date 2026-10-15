#!/usr/bin/env python3
"""Tests for tools/lint.py.

Run: python3 tools/test_lint.py
Exit 0 = all passed, 1 = one or more failed.
"""

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deckparse
import lint

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _make_deck(tmp, deck_yml_text, slides=None, fragments=None):
    """Create a minimal deck in tmp for testing.

    slides: {id: brief_text}
    fragments: {id: html_text}  (None = don't create the file)
    """
    os.makedirs(os.path.join(tmp, "slides"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "content"), exist_ok=True)
    with open(os.path.join(tmp, "deck.yml"), "w") as f:
        f.write(deck_yml_text)
    for sid, text in (slides or {}).items():
        with open(os.path.join(tmp, "slides", f"{sid}.md"), "w") as f:
            f.write(text)
    for sid, text in (fragments or {}).items():
        if text is not None:
            with open(os.path.join(tmp, "content", f"{sid}.html"), "w") as f:
                f.write(text)


def _brief(sid, layout="key-message", extra_fm="", key_message="A message"):
    return (
        f"---\nid: {sid}\nlayout: {layout}\nstatus: draft\n{extra_fm}\n---\n\n"
        f"# Key message\n{key_message}\n"
    )


def _fragment(sid, *, data_slide=None, classes="slide", aria_label="Slide 1: Test",
              extra="", font_size="clamp(1.5rem, 2vw, 2rem)", style_extra=""):
    ds = data_slide if data_slide is not None else sid
    style = (
        f'section[data-slide="{sid}"] h1 {{ font-size: {font_size}; }}\n'
        + style_extra
    )
    return (
        f'<section data-slide="{ds}" aria-label="{aria_label}" class="{classes}">\n'
        f'  <h1>Test</h1>\n'
        f'  {extra}\n'
        f'  <style>\n    {style}\n  </style>\n'
        f'</section>\n'
    )


def _hashed_fragment(sid, brief_text, **kwargs):
    """Create a fragment that has data-brief-hash matching the brief."""
    parsed = deckparse.parse_brief(brief_text, f"slides/{sid}.md")
    h = deckparse.brief_hash(parsed)
    ds = kwargs.pop("data_slide", sid)
    classes = kwargs.pop("classes", "slide")
    aria = kwargs.pop("aria_label", "Slide 1: Test")
    fs = kwargs.pop("font_size", "clamp(1.5rem, 2vw, 2rem)")
    style_extra = kwargs.pop("style_extra", "")
    extra = kwargs.pop("extra", "")
    style = (
        f'section[data-slide="{sid}"] h1 {{ font-size: {fs}; }}\n'
        + style_extra
    )
    return (
        f'<section data-slide="{ds}" aria-label="{aria}" class="{classes}" '
        f'data-brief-hash="{h}">\n'
        f'  <h1>Test</h1>\n'
        f'  {extra}\n'
        f'  <style>\n    {style}\n  </style>\n'
        f'</section>\n'
    )


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

_PASS = 0
_FAIL = 0


def _check(name, findings, *, expect_errors=(), expect_warns=(), expect_clean=False):
    global _PASS, _FAIL
    error_checks = {f.check for f in findings if f.level == "ERROR"}
    warn_checks = {f.check for f in findings if f.level == "WARN"}
    ok = True

    if expect_clean:
        if findings:
            print(f"FAIL  {name}: expected clean but got {len(findings)} finding(s):")
            for f in findings:
                print(f"        {f}")
            ok = False

    for check in expect_errors:
        if check not in error_checks:
            print(f"FAIL  {name}: expected ERROR {check!r} but not found")
            ok = False

    for check in expect_warns:
        if check not in warn_checks:
            print(f"FAIL  {name}: expected WARN {check!r} but not found")
            ok = False

    if ok:
        print(f"pass  {name}")
        _PASS += 1
    else:
        _FAIL += 1


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_clean_deck():
    with tempfile.TemporaryDirectory() as tmp:
        brief_text = _brief("title")
        _make_deck(
            tmp,
            "title: Test Deck\nslides:\n  - title\n",
            slides={"title": brief_text},
            fragments={"title": _hashed_fragment("title", brief_text)},
        )
        _check("clean deck", lint.lint_deck(tmp), expect_clean=True)


def test_no_deck_yml():
    with tempfile.TemporaryDirectory() as tmp:
        _check("no deck.yml", lint.lint_deck(tmp), expect_errors=["no-deck-yml"])


def test_slides_md_deprecated():
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "SLIDES.md"), "w") as f:
            f.write("## title\n")
        _check("SLIDES.md deprecated", lint.lint_deck(tmp),
               expect_warns=["slides-md-deprecated"])


def test_missing_fragment():
    with tempfile.TemporaryDirectory() as tmp:
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={},
        )
        _check("missing fragment", lint.lint_deck(tmp), expect_errors=["missing-fragment"])


def test_data_slide_mismatch():
    with tempfile.TemporaryDirectory() as tmp:
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": _fragment("title", data_slide="wrong-id")},
        )
        _check("data-slide mismatch", lint.lint_deck(tmp),
               expect_errors=["data-slide-mismatch"])


def test_missing_class_slide():
    with tempfile.TemporaryDirectory() as tmp:
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": _fragment("title", classes="")},
        )
        _check("missing class=slide", lint.lint_deck(tmp),
               expect_errors=["missing-class-slide"])


def test_missing_aria_label():
    with tempfile.TemporaryDirectory() as tmp:
        html = (
            '<section data-slide="title" class="slide">\n'
            '  <h1>Test</h1>\n'
            '  <style>section[data-slide="title"] { color: red; }</style>\n'
            '</section>\n'
        )
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": html},
        )
        _check("missing aria-label", lint.lint_deck(tmp),
               expect_errors=["missing-aria-label"])


def test_img_missing_alt():
    with tempfile.TemporaryDirectory() as tmp:
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": _fragment("title", extra='<img src="photo.jpg">')},
        )
        _check("img missing alt", lint.lint_deck(tmp),
               expect_errors=["img-missing-alt"])


def test_img_with_alt_ok():
    with tempfile.TemporaryDirectory() as tmp:
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": _fragment("title", extra='<img src="photo.jpg" alt="A photo">')},
        )
        findings = lint.lint_deck(tmp)
        no_alt = [f for f in findings if f.check == "img-missing-alt"]
        if no_alt:
            _check("img with alt ok", findings, expect_errors=["SHOULD-NOT-BE-HERE"])
        else:
            print("pass  img with alt is fine")
            global _PASS
            _PASS += 1


def test_css_not_scoped():
    with tempfile.TemporaryDirectory() as tmp:
        html = (
            '<section data-slide="title" aria-label="Slide 1" class="slide">\n'
            '  <h1>Test</h1>\n'
            '  <style>\n'
            '    h1 { font-size: clamp(1.5rem, 2vw, 2rem); }\n'
            '  </style>\n'
            '</section>\n'
        )
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": html},
        )
        _check("CSS not scoped", lint.lint_deck(tmp), expect_errors=["css-not-scoped"])


def test_css_scoped_correctly():
    with tempfile.TemporaryDirectory() as tmp:
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": _fragment("title")},
        )
        findings = lint.lint_deck(tmp)
        scoping = [f for f in findings if f.check == "css-not-scoped"]
        if scoping:
            print(f"FAIL  CSS scoped correctly: got unexpected css-not-scoped")
            global _FAIL
            _FAIL += 1
        else:
            print("pass  CSS scoped correctly")
            global _PASS
            _PASS += 1


def test_font_size_too_small_px():
    with tempfile.TemporaryDirectory() as tmp:
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": _fragment("title", font_size="12px")},
        )
        findings = lint.lint_deck(tmp)
        _check("font-size 12px (too small)", findings,
               expect_errors=["font-size-too-small"])


def test_font_size_1rem_body_fails():
    """1rem for body text (non-source selector) should fail."""
    with tempfile.TemporaryDirectory() as tmp:
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": _fragment("title", font_size="1rem")},
        )
        findings = lint.lint_deck(tmp)
        _check("font-size 1rem on body (too small)", findings,
               expect_errors=["font-size-below-minimum"])


def test_font_size_1rem_source_ok():
    """1rem is allowed for source/citation selectors."""
    with tempfile.TemporaryDirectory() as tmp:
        # 1rem in an h1 is not ok, but 1rem in a .source class is fine
        html = (
            '<section data-slide="title" aria-label="S1" class="slide">\n'
            '  <h1>Test</h1>\n'
            '  <style>\n'
            '    section[data-slide="title"] h1 { font-size: clamp(1.5rem, 2.5vw, 2rem); }\n'
            '    section[data-slide="title"] .source { font-size: 1rem; }\n'
            '  </style>\n'
            '</section>\n'
        )
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": _brief("title")},
            fragments={"title": html},
        )
        findings = lint.lint_deck(tmp)
        font_errs = [f for f in findings if f.check in ("font-size-too-small", "font-size-below-minimum")]
        if font_errs:
            print(f"FAIL  1rem source ok: unexpected font-size error")
            global _FAIL
            _FAIL += 1
        else:
            print("pass  1rem in .source is allowed")
            global _PASS
            _PASS += 1


def test_stale_brief():
    with tempfile.TemporaryDirectory() as tmp:
        brief_text = _brief("title")
        html = (
            '<section data-slide="title" aria-label="Slide 1" class="slide" '
            'data-brief-hash="000000000000">\n'
            '  <style>section[data-slide="title"] { color: red; }</style>\n'
            '</section>\n'
        )
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": brief_text},
            fragments={"title": html},
        )
        _check("stale brief", lint.lint_deck(tmp), expect_warns=["stale-brief"])


def test_fresh_brief_no_stale_warn():
    with tempfile.TemporaryDirectory() as tmp:
        brief_text = _brief("title")
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": brief_text},
            fragments={"title": _hashed_fragment("title", brief_text)},
        )
        findings = lint.lint_deck(tmp)
        stale = [f for f in findings if f.check == "stale-brief"]
        if stale:
            print(f"FAIL  fresh brief no stale warn: got unexpected stale-brief warning")
            global _FAIL
            _FAIL += 1
        else:
            print("pass  fresh brief has no stale warning")
            global _PASS
            _PASS += 1


def test_orphan_fragment():
    with tempfile.TemporaryDirectory() as tmp:
        brief_text = _brief("title")
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": brief_text},
            fragments={
                "title": _hashed_fragment("title", brief_text),
                "orphan": _fragment("orphan"),
            },
        )
        _check("orphan fragment", lint.lint_deck(tmp), expect_warns=["orphan-fragment"])


def test_unknown_objective():
    with tempfile.TemporaryDirectory() as tmp:
        brief_text = (
            "---\nid: title\nlayout: key-message\nstatus: draft\nobjective: obj-99\n---\n\n"
            "# Key message\nHello\n"
        )
        _make_deck(
            tmp,
            "title: Test\nobjectives:\n  obj-1: Explain something\nslides:\n  - title\n",
            slides={"title": brief_text},
            fragments={"title": _hashed_fragment("title", brief_text)},
        )
        _check("unknown objective", lint.lint_deck(tmp), expect_errors=["unknown-objective"])


def test_objective_uncovered():
    with tempfile.TemporaryDirectory() as tmp:
        brief_text = _brief("title")
        _make_deck(
            tmp,
            "title: Test\nobjectives:\n  obj-1: Explain something\nslides:\n  - title\n",
            slides={"title": brief_text},
            fragments={"title": _hashed_fragment("title", brief_text)},
        )
        _check("objective uncovered", lint.lint_deck(tmp),
               expect_warns=["objective-uncovered"])


# ---------------------------------------------------------------------------
# Fragment-level unit tests (check_fragment)
# ---------------------------------------------------------------------------

def test_check_fragment_direct():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "title.html")
        with open(path, "w") as f:
            f.write(_fragment("title"))
        findings = lint.check_fragment(path, "title", None)
        errs = [f.check for f in findings if f.level == "ERROR"]
        if errs:
            print(f"FAIL  check_fragment direct: unexpected errors {errs}")
            global _FAIL
            _FAIL += 1
        else:
            print("pass  check_fragment direct returns no errors")
            global _PASS
            _PASS += 1


# ---------------------------------------------------------------------------
# Contrast check tests
# ---------------------------------------------------------------------------

def test_contrast_uw_tokens():
    css_file = os.path.join(
        _PLUGIN_DIR, "design-systems", "uw-brand", "colors_and_type.css"
    )
    if not os.path.isfile(css_file):
        print("skip  contrast UW tokens (file not found)")
        return
    findings = lint.check_contrast(css_file)
    errors = [f for f in findings if f.level == "ERROR"]
    if errors:
        print(f"FAIL  contrast UW tokens: {len(errors)} contrast failure(s):")
        for f in errors:
            print(f"        {f}")
        global _FAIL
        _FAIL += 1
    else:
        print(f"pass  contrast UW tokens ({len(findings)} finding(s), 0 errors)")
        global _PASS
        _PASS += 1


def test_contrast_fail_detected():
    """A contrived CSS with a failing pair should produce an ERROR."""
    with tempfile.TemporaryDirectory() as tmp:
        css_path = os.path.join(tmp, "bad.css")
        # Two very similar colors → contrast ratio ~1:1
        with open(css_path, "w") as f:
            f.write(":root {\n  --uw-spirit-purple: #4b2e83;\n  --uw-white: #4c2f84;\n}\n")
        findings = lint.check_contrast(css_path)
        errors = [f for f in findings if f.level == "ERROR" and f.check == "contrast-fail"]
        if not errors:
            print("FAIL  contrast fail detected: expected at least one contrast ERROR")
            global _FAIL
            _FAIL += 1
        else:
            print("pass  contrast fail is detected correctly")
            global _PASS
            _PASS += 1


# ---------------------------------------------------------------------------
# Status table smoke test
# ---------------------------------------------------------------------------

def test_status_table():
    with tempfile.TemporaryDirectory() as tmp:
        brief_text = _brief("title")
        _make_deck(
            tmp,
            "title: Test\nslides:\n  - title\n",
            slides={"title": brief_text},
            fragments={"title": _hashed_fragment("title", brief_text)},
        )
        table = lint.status_table(tmp)
        if "title" not in table or "ID" not in table:
            print(f"FAIL  status table: output missing expected content\n{table}")
            global _FAIL
            _FAIL += 1
        else:
            print("pass  status table contains expected fields")
            global _PASS
            _PASS += 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_clean_deck()
    test_no_deck_yml()
    test_slides_md_deprecated()
    test_missing_fragment()
    test_data_slide_mismatch()
    test_missing_class_slide()
    test_missing_aria_label()
    test_img_missing_alt()
    test_img_with_alt_ok()
    test_css_not_scoped()
    test_css_scoped_correctly()
    test_font_size_too_small_px()
    test_font_size_1rem_body_fails()
    test_font_size_1rem_source_ok()
    test_stale_brief()
    test_fresh_brief_no_stale_warn()
    test_orphan_fragment()
    test_unknown_objective()
    test_objective_uncovered()
    test_check_fragment_direct()
    test_contrast_uw_tokens()
    test_contrast_fail_detected()
    test_status_table()

    total = _PASS + _FAIL
    print(f"\n{_PASS}/{total} passed", end="")
    if _FAIL:
        print(f", {_FAIL} FAILED")
        sys.exit(1)
    else:
        print()
        sys.exit(0)
