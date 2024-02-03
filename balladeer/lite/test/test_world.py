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
from balladeer.lite.world import WorldBuilder


class WorldBuilderTests(unittest.TestCase):
    def test_empty(self):
        class World(WorldBuilder):
            pass

        world = World()
        self.assertIsNone(world.map)
        self.assertIsNone(world.config)
        self.assertFalse(world.entities)
        self.assertFalse(world.typewise)

    def test_simple(self):
        class World(WorldBuilder):
            def build(self):
                yield Entity(names=["Percy Alleline,", "Tinker"], type="Spy")
                yield Entity(names=["Bill Haydon", "Tailor"], type="Spy")
                yield Entity(names=["Roy Bland", "Soldier"], type="Spy")

        world = World()
        self.assertEqual(3, len(world.entities))
        self.assertEqual(len(world.entities), len(world.typewise.each))
        self.assertEqual(set(world.entities), set(world.typewise.each))

    def test_build_to_spec(self):
        world = WorldBuilder()
        for spec  in (
            dict(name="a", type="b"),
            dict(names=["a"], type="b"),
            dict(name="a", types={"b"}),
            dict(names=["a"], types={"b"}),
            dict(name="a", types=["b"]),
            dict(names=["a"], types=["b"]),
        ):
            with self.subTest(spec=spec):
                entity = next(world.build_to_spec([spec]))
                self.assertEqual(entity, Entity(name="a", types={"Spec", "b"}))
