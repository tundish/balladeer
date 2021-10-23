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

from balladeer import Gesture
from balladeer import Hand
from balladeer import Head
from balladeer import Phrase
from balladeer import Name
from balladeer import Verb


class GestureTests(unittest.TestCase):

    def test_simple(self):
        g = Gesture("simple", head=Head([
            Phrase(Verb("make"), Name("tea")),
            Phrase(Verb("make"), Name("brew")),
        ]))
        self.assertIn("make tea", str(g))
        self.assertIn("\n", str(g))
        self.assertIn("make brew", str(g))
