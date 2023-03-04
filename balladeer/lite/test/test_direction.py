import unittest

import markdown

from balladeer.lite.loader import Loader


class DirectionTests(unittest.TestCase):
    # https://python-markdown.github.io/

    def test_no_direction(self):
        text = """How long, I wonder?"""
        rv = markdown.markdown(text, output_format="xhtml")
        print(rv)
        self.fail(rv)
