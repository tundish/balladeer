#!/usr/bin/env python
# encoding: utf8

# Copyright 2024 D E Haynes

# This file is part of balladeer.
#
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

import balladeer
from balladeer import discover_assets
from balladeer import Drama
from balladeer import Entity
from balladeer import Loader
from balladeer import Resident
from balladeer import WorldBuilder
from busker.stager import Stager


class ResidentTests(unittest.TestCase):

    class TestResident(Resident, Drama):
        pass

    class TestWorld(WorldBuilder):

        def build(self, *args, **kwargs):
            yield Entity().set_state(1)
            yield Entity().set_state(2)

    def test_is_resident(self):
        Colour = enum.Enum("Colour", ["red", "blue", "green", "yellow"])
        Spot = enum.Enum("Spot", {"kitchen": ["kitchen"], "hall": ["hallway"], "cloaks": ["cloakroom", "toilet"]})

        selector = {
            "states": [
                "colour.green",
                "spot.kitchen",
                "spot.cloaks",
            ]
        }

        drama = self.TestResident(selector=selector)
        self.assertIsInstance(drama.selector["states"], set)

        self.assertTrue(drama.is_resident(Colour.green))
        self.assertFalse(drama.is_resident(Colour.red))

        self.assertFalse(drama.is_resident(Colour.red, Spot.kitchen))
        self.assertTrue(drama.is_resident(Colour.green, Spot.kitchen))

    def test_scripts(self):
        selector = {
            "paths": [
                "balladeer/examples/ex_1[01]_*/*.scene.toml"
            ],
        }

        assets = discover_assets(balladeer, "examples")
        scenes = assets.get(Loader.Scene, [])

        drama = self.TestResident(selector=selector)
        scripts = drama.scripts(scenes)

        witness = set(i.path.parts[-3:] for i in scripts)
        self.assertEqual(
            witness,
            set((
                ("examples", "ex_10_animate_media", "argument.scene.toml"),
                ("examples", "ex_11_inventory_compass", "cloakroom.scene.toml"),
                ("examples", "ex_11_inventory_compass", "bar.scene.toml"),
                ("examples", "ex_11_inventory_compass", "foyer.scene.toml"),
            ))
        )

    def test_focus(self):
        world = self.TestWorld()
        drama = self.TestResident(world=world)
