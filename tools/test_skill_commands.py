#!/usr/bin/env python3
"""Check that the commands the skills tell Claude to run match the permission rules.

Stdlib only. The skills are prose, and Claude Code asks permission for any
command no allow rule matches, so a command added to a SKILL.md without a rule
(or a rule dropped from tools/deckperms.py) brings the prompts back. This test
reads every command out of skills/*/SKILL.md and requires each one to be either

  - allowed: it matches a rule in deckperms.SHARED_RULES (written into every
    deck), or one of the user-level rules for the plugin's own scripts
    (documented in the README), or
  - on the ASK_FIRST list: commands that are meant to ask, because they delete,
    download, publish or rewrite a slide.

It also requires every command to be a single plain command (no `&&`, `;`,
pipes, `$VAR` or redirects), because Claude Code checks each part of a
compound command and one unmatched part makes the whole command ask.
"""

import glob
import os
import re
import sys
import unittest

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PLUGIN_DIR, "tools"))
import deckperms  # noqa: E402

# Rules a user adds to ~/.claude/settings.json (the README documents them): the
# plugin's own scripts, run from the version-numbered plugin folder.
USER_LEVEL_RULES = [
    "Bash(python3 */tools/new-deck.py *)",
    "Bash(python3 */tools/deckperms.py *)",
]

# Commands a skill may tell Claude to run that are deliberately not allowed.
# Each pairs a pattern (Claude Code rule syntax) with an example the README
# names as one that still asks.
ASK_FIRST = [
    ("python3 tools/resolve-catalog.py eject *", "python3 tools/resolve-catalog.py eject . <id> --catalog=<PLUGIN>/catalog"),
    ("./publish.sh *", "./publish.sh"),
    ("./export.sh *", "./export.sh"),
    ("./setup-reveal.sh *", "./setup-reveal.sh"),
    ("git rm *", "git rm SLIDES.md"),
]

# A code span or line is treated as a command when it starts with one of these.
COMMAND_STARTS = (
    "python3 ", "./", "printenv ", "bash ", "sh ", "cd ", "ls ", "cat ", "echo ", "git ",
    "npx ", "node ", "chmod ", "rm ", "mkdir ", "cp ", "mv ", "test ", "grep ", "find ",
    "sed ", "curl ", "export ",
)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def rule_regex(rule):
    """Regex for a Claude Code Bash rule: `*` is any text, and a trailing ` *`
    also matches the bare command."""
    inner = re.fullmatch(r"Bash\((.*)\)", rule).group(1)
    return pattern_regex(inner)


def pattern_regex(pattern):
    trailing = pattern.endswith(" *")
    core = pattern[:-2] if trailing else pattern
    rx = re.escape(core).replace(r"\*", ".*")
    if trailing:
        rx += r"(?: .*)?"
    return re.compile(rx)


def skill_commands(path):
    """(command, kind) for each command the skill text tells Claude to run.

    Reads fenced code blocks (line by line) and inline `code spans`. A trailing
    `# comment` and a `2>&1` are dropped (Claude Code does not check a
    file-descriptor redirect)."""
    text = _read(path)
    found = []
    for block in re.findall(r"```[a-z]*\n(.*?)```", text, re.S):
        for line in block.splitlines():
            found.append((line.strip(), "block"))
    prose = re.sub(r"```[a-z]*\n.*?```", "", text, flags=re.S)
    for span in re.findall(r"`([^`\n]+)`", prose):
        found.append((span.strip(), "inline"))
    commands = []
    for cmd, kind in found:
        cmd = re.sub(r"\s+#.*$", "", cmd)
        cmd = cmd.replace(" 2>&1", "").strip()
        if cmd.startswith(COMMAND_STARTS):
            commands.append((cmd, kind))
    return commands


def all_skill_commands():
    out = []
    for path in sorted(glob.glob(os.path.join(PLUGIN_DIR, "skills", "*", "SKILL.md"))):
        skill = os.path.basename(os.path.dirname(path))
        for cmd, kind in skill_commands(path):
            out.append((skill, cmd, kind))
    return out


ALLOWED = [rule_regex(r) for r in deckperms.SHARED_RULES + USER_LEVEL_RULES if r.startswith("Bash(")]
ASKS = [pattern_regex(p) for p, _ in ASK_FIRST]


def _is_allowed(cmd):
    return any(rx.fullmatch(cmd) for rx in ALLOWED)


def _is_ask_first(cmd):
    return any(rx.fullmatch(cmd) for rx in ASKS)


class TestSkillCommands(unittest.TestCase):
    def test_commands_are_found(self):
        """Guards the extraction itself: if it finds nothing the other tests pass vacuously."""
        commands = all_skill_commands()
        self.assertGreater(len(commands), 25)
        skills = {s for s, _, _ in commands}
        for expected in ("generate-slides", "update-deck", "new-deck", "plan-deck"):
            self.assertIn(expected, skills)

    def test_every_command_is_allowed_or_asks_first(self):
        problems = []
        for skill, cmd, _ in all_skill_commands():
            if not (_is_allowed(cmd) or _is_ask_first(cmd)):
                problems.append(f"skills/{skill}/SKILL.md: `{cmd}`")
        self.assertFalse(
            problems,
            "no permission rule covers these commands, so Claude Code will ask about each one.\n"
            "Add a rule to deckperms.SHARED_RULES, or list the command in ASK_FIRST here and in the README:\n  "
            + "\n  ".join(problems),
        )

    def test_every_command_is_one_plain_command(self):
        problems = []
        for skill, cmd, _ in all_skill_commands():
            bare = re.sub(r"<[^<>\s]+>", "", cmd)  # placeholders such as <id> and <PLUGIN>
            if re.search(r"&&|\|\||[;|`<>]|\$", bare):
                problems.append(f"skills/{skill}/SKILL.md: `{cmd}`")
        self.assertFalse(
            problems,
            "Claude Code checks every part of a compound command, so these ask even when each part is allowed:\n  "
            + "\n  ".join(problems),
        )

    def test_no_command_is_both_allowed_and_ask_first(self):
        """An ASK_FIRST command that a rule also allows would stop asking without anyone deciding that."""
        for pattern, example in ASK_FIRST:
            with self.subTest(example=example):
                self.assertFalse(_is_allowed(example), f"`{example}` is allowed by a rule")

    def test_every_skill_states_the_command_contract(self):
        for path in sorted(glob.glob(os.path.join(PLUGIN_DIR, "skills", "*", "SKILL.md"))):
            with self.subTest(skill=os.path.basename(os.path.dirname(path))):
                self.assertIn("nothing appended", _read(path))

    def test_readme_documents_what_still_asks(self):
        readme = _read(os.path.join(PLUGIN_DIR, "README.md"))
        start = readme.index("## Permission prompts")
        section = readme[start:readme.index("\n## ", start + 1)]
        for _, example in ASK_FIRST:
            name = example.split()[0] if example.startswith("git ") else re.sub(r"<.*", "", example).strip()
            key = "eject" if "eject" in example else name.removeprefix("python3 ").split()[0]
            with self.subTest(command=example):
                self.assertIn(key, section)
        for rule in USER_LEVEL_RULES:
            with self.subTest(rule=rule):
                self.assertIn(rule, readme)


class TestRuleMatching(unittest.TestCase):
    """The matcher mirrors Claude Code's rule syntax closely enough to be trusted."""

    def test_trailing_star_matches_the_bare_command_and_arguments(self):
        rx = rule_regex("Bash(./build.sh *)")
        for cmd in ("./build.sh", "./build.sh --strict", "./build.sh /path/to/deck"):
            self.assertTrue(rx.fullmatch(cmd), cmd)

    def test_star_needs_a_word_boundary(self):
        self.assertFalse(rule_regex("Bash(./build.sh *)").fullmatch("./build.shx"))
        self.assertFalse(rule_regex("Bash(./build.sh *)").fullmatch("./build-visuals.sh"))

    def test_exact_rule_matches_only_itself(self):
        rx = rule_regex("Bash(printenv UW_SLIDES_HOME)")
        self.assertTrue(rx.fullmatch("printenv UW_SLIDES_HOME"))
        self.assertFalse(rx.fullmatch("printenv UW_SLIDES_HOME; echo $?"))
        self.assertFalse(rx.fullmatch("printenv HOME"))

    def test_resolve_catalog_rule_does_not_cover_eject(self):
        rx = rule_regex("Bash(python3 tools/resolve-catalog.py resolve *)")
        self.assertTrue(rx.fullmatch("python3 tools/resolve-catalog.py resolve . --catalog=/x/catalog"))
        self.assertFalse(rx.fullmatch("python3 tools/resolve-catalog.py eject . id"))

    def test_user_level_rule_matches_a_plugin_placeholder_path(self):
        rx = rule_regex(USER_LEVEL_RULES[0])
        self.assertTrue(rx.fullmatch("python3 <PLUGIN>/tools/new-deck.py my-talk --brand=uw"))

    def test_extraction_drops_comments_and_fd_redirects(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "SKILL.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("```bash\n./outline.sh        # refreshes OUTLINE.md\n"
                         "python3 tools/resolve-catalog.py resolve . 2>&1\n```\n"
                         "Run `printenv UW_SLIDES_HOME` and read `layouts.md`.\n")
            cmds = [c for c, _ in skill_commands(p)]
        self.assertEqual(cmds, ["./outline.sh", "python3 tools/resolve-catalog.py resolve .", "printenv UW_SLIDES_HOME"])

    def test_a_compound_command_is_caught(self):
        bare = re.sub(r"<[^<>\s]+>", "", 'printenv UW_SLIDES_HOME 2>/dev/null; echo "exit: $?"')
        self.assertTrue(re.search(r"&&|\|\||[;|`<>]|\$", bare))


if __name__ == "__main__":
    unittest.main()
