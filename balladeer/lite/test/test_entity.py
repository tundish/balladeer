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

import copy
import enum
import json
import unittest

from balladeer.lite.entity import Entity
from balladeer.lite.types import State


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

    def test_copy(self):
        a = Entity(name="a")
        b = copy.deepcopy(a)
        self.assertEqual(a, b)


class TestAttributes(unittest.TestCase):
    def test_aspect(self):
        a = Entity(aspect="whistling")
        b = Entity(aspect="whistling")
        self.assertNotEqual(a, b)

    def test_sketch(self):
        a = Entity(sketch="athletic")
        b = Entity(sketch="athletic")
        self.assertNotEqual(a, b)


class TestNamesAndTypes(unittest.TestCase):
    class Active(State):
        off = 0
        on = 1

    class Thing(Entity):
        pass

    def test_string_type(self):
        e = Entity(type="Thing")
        self.assertEqual({"Thing"}, e.types)

    def test_declared_type(self):
        e = Entity(type=TestNamesAndTypes.Thing)
        self.assertEqual({"Thing"}, e.types)

    def test_dumps_to_json(self):
        e = Entity(type=TestNamesAndTypes.Thing).set_state(3, TestNamesAndTypes.Active.on)
        self.assertEqual({"Thing"}, e.types)

        j = Entity.Encoder().encode(e)
        self.assertTrue(j)

        s = json.loads(j)
        self.assertTrue(s)


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
        j = Entity.Encoder().encode(s)
        self.assertTrue(j)

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
        self.assertEqual(TestEnumStates.Colour.green, s.get_state(TestEnumStates.Colour))
        self.assertEqual({"Colour": TestEnumStates.Colour.green}, s.states)


class TestIntegerStates(unittest.TestCase):
    def test_state_as_int(self):
        s = Entity()
        s.set_state(3)
        self.assertEqual(3, s.get_state(int))
        self.assertEqual(3, s.get_state("int"))
        self.assertEqual(3, s.state)

    def test_state_as_int_twice(self):
        s = Entity()
        s.set_state(3, 3)
        self.assertEqual(3, s.get_state(int))
        self.assertEqual(3, s.get_state("int"))
        self.assertEqual(3, s.state)

    def test_state_as_int_args(self):
        s = Entity()
        s.set_state(3, 4, 5)
        self.assertEqual(5, s.get_state(int))
        self.assertEqual(5, s.get_state("int"))
        self.assertEqual(5, s.state)


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


class TestSerialization(unittest.TestCase):

    def test_default(self):
        entity = Entity()
        s = entity.Encoder().encode(entity)
        data = json.loads(s)
        self.assertTrue(data)

    def test_linked_uids(self):
        entities = [Entity(), Entity()]
        entities[0].links.add(entities[1].uid)
        entities[1].links.add(entities[0].uid)
        s = Entity.Encoder().encode(entities)
        data = json.loads(s)
        self.assertEqual(2, len(data), data)
        data = json.loads(s)
        self.assertTrue(data)
