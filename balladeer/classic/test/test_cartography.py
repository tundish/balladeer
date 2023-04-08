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

from balladeer.classic.cartography import Compass
from balladeer.classic.cartography import Map
from balladeer.classic.cartography import Transit
from balladeer.classic.cartography import Via
from balladeer.classic.cartography import Waypoint


class CompassTests(unittest.TestCase):
    def test_nearing(self):
        self.assertEqual(0, Compass.N.bearing)
        self.assertEqual(180, Compass.S.bearing)

    def test_back(self):
        self.assertEqual(Compass.SW, Compass.NE.back)
        self.assertEqual(Compass.NE, Compass.SW.back)

    def test_vectors(self):
        self.assertEqual(Compass.NE.value, Compass.N.value + Compass.E.value)


class MapTests(unittest.TestCase):
    class SimpleMap(Map):
        spots = {
            "bedroom": ["bedroom"],
            "hall": ["hall", "hallway"],
            "kitchen": ["kitchen"],
            "stairs": ["stairs", "stairway", "up", "up stairs", "upstairs"],
            "inventory": None,
        }

        Into = enum.Enum("Into", spots, type=Waypoint)
        Exit = enum.Enum("Exit", spots, type=Waypoint)
        Spot = enum.Enum("Spot", spots, type=Waypoint)

        def __init__(self, exit=None, into=None, **kwargs):
            super().__init__(exit, into, **kwargs)
            exit = self.exit
            into = self.into
            self.transits = [
                Transit(label="bedroom door").set_state(exit.bedroom, into.hall, Via.bidir),
                Transit().set_state(exit.hall, Compass.N, into.stairs, Via.bidir),
                Transit(label="kitchen door").set_state(
                    exit.kitchen, Compass.SW, into.hall, Via.bidir
                ),
            ]

    def test_simple_options(self):
        m = MapTests.SimpleMap()
        self.assertEqual(3, len(m.options(m.Spot.hall)))

    def test_simple_route(self):
        m = MapTests.SimpleMap()
        r = m.route(m.Spot.kitchen, m.Spot.bedroom)
        self.assertEqual(3, len(r))
        self.assertEqual(3, len(set(r)))
