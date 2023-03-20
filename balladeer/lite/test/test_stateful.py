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

import enum
import unittest

from turberfield.utils.assembly import Assembly

from balladeer.lite.stateful import Stateful


class TestIntegerStates(unittest.TestCase):

    def test_state_as_int(self):
        s = Stateful()
        s.set_state(3)
        self.assertEqual(3, s.get_state())
        self.assertEqual(3, s.state)
        self.assertEqual({"int": 3}, s.states)

    def test_state_as_int_twice(self):
        s = Stateful()
        s.set_state(3).set_state(4)
        self.assertEqual(4, s.get_state())
        self.assertEqual(4, s.state)
        self.assertEqual({"int": 4}, s.states)

    def test_state_as_int_args(self):
        s = Stateful()
        s.set_state(3, 4)
        self.assertEqual(4, s.get_state())
        self.assertEqual(4, s.state)
        self.assertEqual({"int": 4}, s.states)


class TestEnumStates(unittest.TestCase):

    class Colour(enum.Enum):
        red = "ff0000"
        green = "00ff00"
        blue = "0000ff"

    def test_state_as_enum(self):
        s = Stateful()
        s.set_state(TestEnumStates.Colour.red)
        self.assertEqual(
            TestEnumStates.Colour.red,
            s.get_state(TestEnumStates.Colour)
        )
        self.assertEqual(0, s.state)
        self.assertEqual(
            {"Colour": TestEnumStates.Colour.red},
            s.states
        )

    def test_state_as_enum_twice(self):
        s = Stateful()
        s.set_state(
            TestEnumStates.Colour.red,
            TestEnumStates.Colour.red,
        )
        self.assertEqual(
            TestEnumStates.Colour.red,
            s.get_state(TestEnumStates.Colour)
        )
        self.assertEqual(0, s.state)
        self.assertEqual(
            {"Colour": TestEnumStates.Colour.red},
            s.states
        )

    def test_state_as_enum_args(self):
        s = Stateful()
        s.set_state(
            TestEnumStates.Colour.red,
            TestEnumStates.Colour.green,
        )
        self.assertEqual(
            TestEnumStates.Colour.green,
            s.get_state(TestEnumStates.Colour)
        )
        self.assertEqual(0, s.state)
        self.assertEqual(
            {"Colour": TestEnumStates.Colour.green},
            s.states
        )
