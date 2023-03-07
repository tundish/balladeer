import textwrap
import unittest

import markdown

from balladeer.lite.loader import Loader
from balladeer.lite.parser import DialogueParser
from balladeer.lite.parser import Parser


class DirectiveTests(unittest.TestCase):
    # https://python-markdown.github.io/
    # https://spec.commonmark.org/dingus/

    def test_no_directive(self):
        text = "How long, I wonder?"
        rv = Parser.parse(text)
        self.assertIsInstance(rv, tuple)
        directives, report = rv
        self.assertTrue(directives)
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(text, directives[0].text)
        self.assertEqual(0, directives[0].enter, directives)
        self.assertEqual(len(directives[0].xhtml), directives[0].exit, directives)

    def test_bad_directive(self):
        line = "How long, I wonder?"
        text = f"MAN_1:says> {line}"
        rv = Parser.parse(text)
        directives, report = rv
        self.assertTrue(directives)
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(line, directives[0].xhtml)
        self.assertEqual(0, directives[0].enter, directives)
        self.assertEqual(len(directives[0].xhtml), directives[0].exit, directives)

    def test_unspaced_directive(self):
        line = "How long, I wonder?"
        text = f"<MAN_1:says>{line}"
        rv = Parser.parse(text)
        directives, report = rv
        self.assertTrue(directives)
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(line, directives[0].text, directives)
        self.assertEqual(0, directives[0].enter, directives)
        self.assertEqual(len(directives[0].xhtml), directives[0].exit, directives)

    def test_simple_directive(self):
        line = "How long, I wonder?"
        text = f"<MAN_1:says> {line}"
        rv = Parser.parse(text)
        directives, report = rv
        self.assertTrue(directives)
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(line, directives[0].xhtml)
        self.assertEqual(0, directives[0].enter, directives)
        self.assertEqual(len(directives[0].xhtml), directives[0].exit, directives)

    def test_multiline_directive(self):
        line = "How long, I wonder?"
        text = textwrap.dedent(f"""
        <MAN_1:says>
        {line}
        """)
        rv = Parser.parse(text)
        directives, report = rv
        self.assertEqual(1, len(directives))
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(line, directives[0].xhtml)
        self.assertEqual(0, directives[0].enter, directives)
        self.assertEqual(len(directives[0].xhtml), directives[0].exit, directives)

    def test_multipart_directives(self):
        line = "How long, I wonder?"
        text = textwrap.dedent(f"""
        <MAN_1:says>

        {line}
        """)
        rv = Parser.parse(text)
        directives, report = rv
        self.assertEqual(2, len(directives))
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(line, directives[0].xhtml)
        self.assertEqual(0, directives[0].enter, directives)
        self.assertEqual(len(directives[1].xhtml), directives[1].exit, directives)

    def test_multiline_substitution(self):
        line = "How long, I wonder, { MAN_2['name'] }?"
        text = textwrap.dedent(f"""
        <MAN_1:says>
        {line}
        """)
        rv = Parser.parse(text)
        directives, report = rv
        self.assertEqual(1, len(directives))
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(line, directives[0].xhtml)
        self.assertIn(line, directives[0].text)

    def test_multipart_substitution(self):
        text = textwrap.dedent("""
        <MAN_1:says>

        How long, I wonder, {MAN_2["name"]}?
        """)
        rv = Parser.parse(text)
        directives, report = rv
        self.assertEqual(2, len(directives))
        self.assertIn('{MAN_2["name"]}', directives[0].xhtml)
        self.assertIn('{MAN_2["name"]}', directives[1].xhtml)
        self.assertNotIn('{MAN_2["name"]}', directives[0].text)
        self.assertIn('{MAN_2["name"]}', directives[1].text)
