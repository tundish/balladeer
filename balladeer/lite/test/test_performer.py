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
from types import SimpleNamespace
import unittest

from balladeer.lite.entity import Entity
from balladeer.lite.performer import Performer


class PerformerTests(unittest.TestCase):

    class Location(enum.Enum):
        HERE = "here"
        THERE = "there"

    class Liquid(Entity): pass
    class Mass(Entity): pass
    class Space(Entity): pass

    def test_unpack_annotation_single_enum(self):
        rv = list(Performer.unpack_annotation("locn", PerformerTests.Location, ensemble=[]))
        self.assertTrue(rv)
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertEqual(
            len([v for i in PerformerTests.Location for v in ([i.value] if isinstance(i.value, str) else i.value)]),
            len(rv),
            rv
        )

    def test_unpack_annotation_enum_list(self):
        class Season(enum.Enum):
            spring = "Spring"
            summer = "Summer"
            autumn = "Autumn"
            winter = "Winter"

        rv = list(Performer.unpack_annotation("item", [PerformerTests.Location, Season], ensemble=[]))
        self.assertTrue(rv)
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertTrue(all(isinstance(i[0], str) for i in rv), rv)
        self.assertTrue(all(isinstance(i[1], enum.Enum) for i in rv), rv)
        self.assertEqual(
            len([
                v for i in list(PerformerTests.Location) + list(Season)
                for v in ([i.value] if isinstance(i.value, str) else i.value)
            ]),
            len(rv),
            rv
        )

    def test_unpack_annotation_single_class(self):
        ensemble = [PerformerTests.Liquid(), PerformerTests.Mass(), PerformerTests.Space()]
        rv = list(Performer.unpack_annotation("item", PerformerTests.Liquid, ensemble))
        self.assertTrue(rv)
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertEqual(1, len(rv), rv)
        self.assertIsInstance(rv[0][1], PerformerTests.Liquid)

    def test_unpack_annotation_dataobject(self):
        ensemble = [PerformerTests.Liquid(), PerformerTests.Mass(), PerformerTests.Space()]
        rv = list(Performer.unpack_annotation("thing", [PerformerTests.Liquid, PerformerTests.Mass], ensemble))
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertEqual(2, len(rv), rv)
        self.assertIsInstance(rv[0][1], PerformerTests.Liquid)
        self.assertIsInstance(rv[1][1], PerformerTests.Mass)

    def test_unpack_annotation_parent_attribute(self):
        class Season(enum.Enum):
            spring = "Spring"
            summer = "Summer"
            autumn = "Autumn"
            winter = "Winter"

            @property
            def follows(self):
                items = list(Season)
                pos = (items.index(self) - 1) % len(items)
                return items[pos]

        self.assertEqual(Season.summer, Season.autumn.follows)
        s = Season.autumn
        rv = list(Performer.unpack_annotation("item", "follows", ensemble=[], parent=s))
        self.assertTrue(rv)
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertTrue(all(isinstance(i[0], str) for i in rv), rv)
        self.assertTrue(all(isinstance(i[1], enum.Enum) for i in rv), rv)
        self.assertEqual(Season.summer, rv[0][1])

    def test_unpack_annotation_parent_attribute_dotted(self):
        class Season(enum.Enum):
            spring = "Spring"
            summer = "Summer"
            autumn = "Autumn"
            winter = "Winter"

            @property
            def follows(self):
                items = list(Season)
                pos = (items.index(self) - 1) % len(items)
                return items[pos]

        self.assertEqual(Season.summer, Season.autumn.follows)
        obj = SimpleNamespace(s=Season.autumn)
        rv = list(Performer.unpack_annotation("item", "s.follows", ensemble=[], parent=obj))
        self.assertTrue(rv)
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertTrue(all(isinstance(i[0], str) for i in rv), rv)
        self.assertTrue(all(isinstance(i[1], enum.Enum) for i in rv), rv)
        self.assertEqual(Season.summer, rv[0][1])

    def test_unpack_annotation_parent_attribute_mixed(self):
        obj = SimpleNamespace(one=SimpleNamespace(two={"three": 3}))
        rv = list(Performer.unpack_annotation("item", "one.two[three]", ensemble=[], parent=obj))
        self.assertEqual(("item", 3), rv[0])

    def test_expand_commands_no_preserver(self):

        thing = Entity(name="thing")

        def func(obj: Entity):
            """
            pick up a {obj.name}
            """

        rv = dict(Performer.expand_commands(func, ensemble=[thing]))
        self.assertIn("pick up thing", rv)

    def test_expand_commands_sequence_with_preserver(self):

        thing = Entity(names=["thing"])

        def func(obj: Entity):
            """
            pick up a {obj.names[0]}.
            """

        rv = dict(Performer.expand_commands(func, ensemble=[thing]))
        self.assertIn("pick up a thing", rv)

    def test_expand_commands_sequence_no_preserver(self):

        thing = Entity(names=["thing"])

        def func(obj: Entity):
            """
            pick up a {obj.names[0]}
            """

        rv = dict(Performer.expand_commands(func, ensemble=[thing]))
        self.assertIn("pick up thing", rv)

    def test_expand_commands_sequence_synonyms_no_preserver(self):

        thing = Entity(names=["thing", "doobrey"])
        idea = Entity(names=["idea"])

        def func(obj: [object, Entity]):
            """
            pick up a {obj.names[0]} | grab a {obj.names[0]}
            pick up a {obj.names[1]} | grab a {obj.names[1]}
            """

        rv = dict(Performer.expand_commands(func, ensemble=[idea, thing, idea]))
        self.assertIn("pick up thing", rv)
        self.assertIn("pick up doobrey", rv)
        self.assertIn("grab thing", rv)
        self.assertIn("grab doobrey", rv)

    def test_expand_commands_with_preserver(self):

        thing = Entity(name="thing")

        def func(obj: Entity):
            """
            pick up a {obj.name}.
            """

        rv = dict(Performer.expand_commands(func, ensemble=[thing]))
        self.assertIn("pick up a thing", rv)

    def test_expand_commands_discrimminator(self):

        ensemble = [
            Entity(names=["thing"], aspect="blue"),
            Entity(names=["thing"], aspect="red"),
        ]

        def func(obj: Entity):
            """
            pick up a {obj.aspect} {obj.names[0]}
            """

        rv = dict(Performer.expand_commands(func, ensemble=ensemble))
        self.assertIn("pick up blue thing", rv)
        self.assertEqual("blue", rv["pick up blue thing"][1]["obj"].aspect)
        self.assertIn("pick up red thing", rv)
        self.assertEqual("red", rv["pick up red thing"][1]["obj"].aspect)

