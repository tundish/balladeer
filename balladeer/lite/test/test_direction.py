import textwrap
import unittest

import markdown

from balladeer.lite.loader import Loader
from balladeer.lite.loader import DialogueParser
from balladeer.lite.loader import Parser


class DirectiveTests(unittest.TestCase):
    # https://python-markdown.github.io/
    # https://spec.commonmark.org/dingus/

    def test_no_directive(self):
        text = """How long, I wonder?"""
        rv = Parser.parse(text)
        self.assertIsInstance(rv, tuple)
        directives, report = rv
        self.assertTrue(directives)
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(text, directives[0].xhtml)
        self.assertEqual(len(text), directives[0].load)

    def test_bad_directive(self):
        line = "How long, I wonder?"
        text = f"MAN_1:says> {line}"
        rv = Parser.parse(text)
        directives, report = rv
        self.assertTrue(directives)
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(line, directives[0].xhtml)
        self.assertEqual(len(text), directives[0].load)

    def test_unspaced_directive(self):
        line = "How long, I wonder?"
        text = f"<MAN_1:says>{line}"
        rv = Parser.parse(text)
        directives, report = rv
        self.assertTrue(directives)
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(line, directives[0].xhtml)
        self.assertEqual(len(line), directives[0].load)

    def test_simple_directive(self):
        line = "How long, I wonder?"
        text = f"<MAN_1:says> {line}"
        rv = Parser.parse(text)
        directives, report = rv
        self.assertTrue(directives)
        self.assertIsInstance(directives[0], DialogueParser.Directive)
        self.assertIn(line, directives[0].xhtml)
        self.assertEqual(len(line), directives[0].load)

    @unittest.skip("not yet")
    def test_multiline_directive(self):
        text = textwrap.dedent("""
        <MAN_1:says>
        How long, I wonder?
        """)
        rv = Parser.parse(text)
        self.assertIsInstance(rv, tuple)
        self.assertEqual(2, len(rv))
        print(rv)
        self.fail(rv)

    @unittest.skip("not yet")
    def test_multipart_directive(self):
        text = textwrap.dedent("""
        <MAN_1:says>

        How long, I wonder?
        """)
        rv = Parser.parse(text)
        self.assertIsInstance(rv, tuple)
        self.assertEqual(2, len(rv))
        print(rv)
        self.fail(rv)
