#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2021 D E Haynes

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import textwrap
import unittest

from turberfield.dialogue.model import SceneScript

from balladeer.classic.folio import Folio


class SpacingTests(unittest.TestCase):
    def test_simple(self):
        rv = Folio.single_space("a  b   c")
        self.assertEqual("a b c", rv)

    def test_html_spans(self):
        content = textwrap.dedent("""
        And they lived happily *ever after*.
        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([]))
        model = list(script.run())
        self.assertFalse(any("\n" in Folio.single_space(l.html) for s, l in model), model)
