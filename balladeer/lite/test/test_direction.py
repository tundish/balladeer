import unittest

import markdown

from balladeer.lite.loader import Loader


class DirectionTests(unittest.TestCase):
    # https://python-markdown.github.io/
    # https://spec.commonmark.org/dingus/

    def test_no_direction(self):
        text = """How long, I wonder?"""
        rv = Loader.parse(text)
        self.assertIsInstance(rv, tuple)
        directions, report = rv
        self.assertTrue(directions)
        self.assertIsInstance(directions[0], Loader.Direction)
        self.assertIn(text, directions[0].xml)

    def test_bad_direction(self):
        text = """MAN_1:says> How long, I wonder?"""
        rv = Loader.parse(text)
        self.assertIsInstance(rv, tuple)
        self.assertEqual(2, len(rv))
        print(rv)
        self.fail(rv)

    def test_unspaced_direction(self):
        text = """<MAN_1:says>How long, I wonder?"""
        rv = Loader.parse(text)
        self.assertIsInstance(rv, tuple)
        self.assertEqual(2, len(rv))
        print(rv)
        self.fail(rv)

    def test_simple_direction(self):
        text = """<MAN_1:says> How long, I wonder?"""
        rv = Loader.parse(text)
        self.assertIsInstance(rv, tuple)
        self.assertEqual(2, len(rv))
        print(rv)
        self.fail(rv)
