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

from balladeer.cartography import Compass
from balladeer.cartography import Map
from balladeer.cartography import Transit
from balladeer.cartography import Via
from balladeer.cartography import Waypoint


class CompassTests(unittest.TestCase):

    def test_next_states_single(self):
        assert Compass.N.value + Compass.E.value == Compass.NE.value
        assert Compass.NE.back == Compass.SW
        assert Compass.SW.back == Compass.NE
        assert Compass.N.bearing == 0, Compass.N.bearing 
        assert Compass.N.back.bearing == 180, Compass.N.back.bearing 

class MapTests(unittest.TestCase):

    class SimpleMap(Map):

        spots = {
            "bedroom":  ["bedroom"],
            "hall":  ["hall", "hallway"],
            "kitchen":  ["kitchen"],
            "stairs":  ["stairs", "stairway", "up", "up stairs", "upstairs"],
            "inventory":  None
        }

        Arriving = enum.Enum("Arriving", spots, type=Waypoint)
        Departed = enum.Enum("Departed", spots, type=Waypoint)
        Location = enum.Enum("Location", spots, type=Waypoint)

        def __init__(self, exit=None, into=None, **kwargs):
            super().__init__(exit, into, **kwargs)
            exit = self.exit
            into = self.into
            self.transits = [
                Transit().set_state(exit.bedroom, into.hall, Via.bidir),
                Transit().set_state(exit.hall, Compass.N, into.stairs, Via.bidir),
                Transit().set_state(exit.kitchen, Compass.SW, into.hall, Via.bidir),
            ]

    def test_simple_route(self):
        m = MapTests.SimpleMap()
        print(m.options(m.Location.hall))
        print(m.route(m.Location.kitchen, m.Location.bedroom))
