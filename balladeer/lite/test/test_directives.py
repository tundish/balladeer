import re
import textwrap
import unittest

import markdown
import markdown.util

from balladeer.lite.loader import Loader
from balladeer.lite.parser import AutoLinker
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


class DirectiveParameterTests(unittest.TestCase):

    def test_numerical_parameters(self):
        import trace
        autolinker = AutoLinker()
        md = markdown.Markdown(safe_mode=True, output_format="xhtml", extensions=[autolinker])
        processor = md.inlinePatterns["autolink"]
        print(processor.compiled_re)

        line = "How long, I wonder?"
        text = f"<MAN1:says?pause=1&dwell=0.2>{line}"
        match = processor.compiled_re.match(text[:-len(line)].strip())
        self.assertTrue(match)
        tracer = trace.Trace(countfuncs=1, countcallers=1, ignoremods=["re"])
        tracer.runfunc(md.convert, text)
        r = tracer.results()
        # r.write_results(coverdir=".")

        rv = Parser.parse(text)
        directives, report = rv
        self.assertEqual(1, len(directives))
        self.assertEqual("MAN1", directives[0].role, directives)
        self.assertEqual("says", directives[0].mode)
        self.assertIsInstance(directives[0].params, dict)

    def test_underscore_with_numerical_parameters(self):
        line = "How long, I wonder?"
        text = f"<MAN_1:says?pause=1&dwell=0.2> {line}"
        rv = Parser.parse(text)
        directives, report = rv
        self.fail(directives)
