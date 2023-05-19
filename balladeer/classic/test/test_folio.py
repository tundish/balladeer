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

import unittest

from balladeer.classic.speech import Phrase
from balladeer.classic.speech import Name
from balladeer.classic.speech import Verb
from balladeer.classic.types import Named


class NamedTests(unittest.TestCase):
    def test_simple(self):
        mug = Named(names=[Name("Cup"), Name("Mug")])
        self.assertIn("Cup", str(mug))
        self.assertIn("\n", str(mug))
        self.assertIn("Mug", str(mug))


class VerbTests(unittest.TestCase):
    def test_simple(self):
        v = Verb("show")
        self.assertEqual("shows", v.simple)
        self.assertEqual("is showing", v.progressive)
        self.assertEqual("showed", v.perfect)
        self.assertEqual("show", v.imperative)
