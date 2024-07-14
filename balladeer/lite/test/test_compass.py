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

import enum
import unittest

from balladeer.lite.compass import Compass
from balladeer.lite.compass import MapBuilder
from balladeer.lite.compass import Traffic
from balladeer.lite.compass import Transit


class CompassTests(unittest.TestCase):
    def test_bearing(self):
        self.assertEqual(0, Compass.bearing(Compass.N))
        self.assertEqual(90, Compass.bearing(Compass.E))
        self.assertEqual(45, Compass.bearing(Compass.N, Compass.E))

    def test_back(self):
        self.assertEqual(Compass.SW, Compass.NE.back)
        self.assertEqual(Compass.NE, Compass.SW.back)

    def test_vectors(self):
        self.assertEqual(Compass.NE.value[-1], Compass.N.value[-1] + Compass.E.value[-1])


class MapTests(unittest.TestCase):
    class Map(MapBuilder):
        spots = {
            "bedroom": ["bedroom"],
            "hall": ["hall", "hallway"],
            "kitchen": ["kitchen"],
            "stairs": ["stairs", "stairway", "up", "up stairs", "upstairs"],
            "inventory": ["inventory"],
        }

        def build(self, **kwargs):
            yield from [
                Transit(name="bedroom door").set_state(
                    self.exit.bedroom, self.into.hall, Traffic.flowing
                ),
                Transit().set_state(
                    self.exit.hall, Compass.N, self.into.stairs, Traffic.flowing
                ),
                Transit(name="kitchen door").set_state(
                    self.exit.kitchen, Compass.SW, self.into.hall, Traffic.flowing
                ),
            ]

    def test_simple_options(self):
        m = MapTests.Map(MapTests.Map.spots)
        self.assertEqual(3, len(m.options(m.spot.hall)))

    def test_simple_route(self):
        m = MapTests.Map(MapTests.Map.spots)
        r = m.route(m.spot.kitchen, m.spot.bedroom)
        self.assertEqual(3, len(r))
        self.assertEqual(3, len(set(r)))
