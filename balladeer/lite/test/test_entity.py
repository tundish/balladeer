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

from balladeer.lite.types import Entity


class TestComparisons(unittest.TestCase):
    def test_identity(self):
        bag = set(
            [
                Entity(),
                Entity(),
                Entity(),
            ]
        )
        self.assertEqual(3, len(bag))

    def test_quality(self):
        a = Entity(name="a")
        b = Entity(name="a")
        self.assertEqual(a, b)

    def test_inequality(self):
        a = Entity(name="a")
        b = Entity(name="b")
        self.assertNotEqual(a, b)


class TestNamesAndTypes(unittest.TestCase):
    class Thing(Entity):
        pass

    def test_string_type(self):
        e = Entity(type="Thing")
        self.assertEqual({"Thing"}, e.types)

    def test_declared_type(self):
        e = Entity(type=TestNamesAndTypes.Thing)
        self.assertEqual({"Thing"}, e.types)


class TestEnumStates(unittest.TestCase):
    class Colour(enum.Enum):
        red = "ff0000"
        green = "00ff00"
        blue = "0000ff"

    def test_state_as_enum(self):
        s = Entity()
        s.set_state(TestEnumStates.Colour.red)
        self.assertEqual(TestEnumStates.Colour.red, s.get_state(TestEnumStates.Colour))
        self.assertEqual({"Colour": TestEnumStates.Colour.red}, s.states)

    def test_state_as_enum_twice(self):
        s = Entity()
        s.set_state(
            TestEnumStates.Colour.red,
            TestEnumStates.Colour.red,
        )
        self.assertEqual(TestEnumStates.Colour.red, s.get_state(TestEnumStates.Colour))
        self.assertEqual({"Colour": TestEnumStates.Colour.red}, s.states)

    def test_state_as_enum_args(self):
        s = Entity()
        s.set_state(
            TestEnumStates.Colour.red,
            TestEnumStates.Colour.green,
        )
        self.assertEqual(
            TestEnumStates.Colour.green, s.get_state(TestEnumStates.Colour)
        )
        self.assertEqual({"Colour": TestEnumStates.Colour.green}, s.states)


class TestStringStates(unittest.TestCase):
    class Colour(enum.Enum):
        red = "ff0000"
        green = "00ff00"
        blue = "0000ff"

    def test_get_state_as_string(self):
        e = Entity()
        e.set_state(TestEnumStates.Colour.green)

        self.assertEqual(TestEnumStates.Colour.green, e.get_state("Colour"))
        self.assertIsNone(e.get_state("Color"))
