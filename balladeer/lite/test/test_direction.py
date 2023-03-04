import unittest

import markdown

from balladeer.lite.loader import Loader


class DirectionTests(unittest.TestCase):
    # https://python-markdown.github.io/

    def test_no_direction(self):
        text = """How long, I wonder?"""
        rv = Loader.parse(text)
        self.fail(rv)

    def test_bad_direction(self):
        text = """MAN_1:says> How long, I wonder?"""
        rv = Loader.parse(text)
        print(rv)
        self.fail(rv)

    def test_simple_direction(self):
        text = """<MAN_1:says> How long, I wonder?"""
        rv = Loader.parse(text)
        print(rv)
        self.fail(rv)
