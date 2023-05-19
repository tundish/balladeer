#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2023 D E Haynes

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

from balladeer.lite.entity import Entity
from balladeer.lite.loader import Loader
from balladeer.lite.types import Grouping


class GroupingTests(unittest.TestCase):
    def test_grouping_by_class(self):
        class A:
            pass

        class B:
            pass

        g = Grouping.typewise([A(), B(), A()])
        self.assertIn(A, g)
        self.assertEqual(2, len(g[A]))

        self.assertIn(B, g)
        self.assertEqual(1, len(g[B]))
        self.assertEqual(3, len(g.all))
        self.assertEqual(3, len(g.each))

    def test_grouping_by_type(self):
        types = ("audio/mpeg", "text/css", "text/javascript")
        items = [
            Loader.Asset(unittest, "data/slapwhack.mp4", type=types[0]),
            Loader.Asset(unittest, "styles/style.css", type=types[1]),
            Loader.Asset(unittest, "picker.js", type=types[2]),
        ]
        g = Grouping.typewise(items)

        for t in types:
            with self.subTest(t=t):
                self.assertIn(t, g)
                self.assertEqual(1, len(g[t]))
                self.assertIsInstance(g[t][0], Loader.Asset)

    def test_grouping_via_types(self):
        items = [
            Entity(type="A"),
            Entity(type="B"),
            Entity(type="A"),
        ]

        g = Grouping.typewise(items)

        self.assertIn(Entity, g)
        self.assertEqual(3, len(g[Entity]))

        self.assertIn("A", g)
        self.assertEqual(2, len(g["A"]))

        self.assertIn("B", g)
        self.assertEqual(1, len(g["B"]))

        self.assertEqual(6, len(g.all))
        self.assertEqual(3, len(g.each))

    def test_grouping_by_multiple_type(self):
        items = [
            Entity(type="A"),
            Entity(types={"A", "B"}),
        ]

        g = Grouping.typewise(items)

        self.assertIn(Entity, g)
        self.assertEqual(2, len(g[Entity]))

        self.assertIn("A", g)
        self.assertEqual(2, len(g["A"]))

        self.assertIn("B", g)
        self.assertEqual(1, len(g["B"]))

        self.assertEqual(5, len(g.all), g.all)
        self.assertEqual(2, len(g.each))
