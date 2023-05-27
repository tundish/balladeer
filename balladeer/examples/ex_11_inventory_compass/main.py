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

import balladeer
from balladeer import quick_start
from balladeer import StoryBuilder
from balladeer import Compass
from balladeer import Drama
from balladeer import Entity
from balladeer import Focus
from balladeer import Prologue
from balladeer import Traffic
from balladeer import Transit
from balladeer import MapBuilder
from balladeer import WorldBuilder

__doc__ = """
python3 -m balladeer.examples.10_animate_media.main

"""


class Map(MapBuilder):

    spots = {
        "foyer": ["foyer", "lobby"],
        "bar": ["bar", "saloon bar"],
        "cloakroom": ["cloakroom", "cloak room", "cloaks"],
        "hook": ["hook", "cloakroom hook"],
        "inventory": ["inventory"],
    }

    def build(self):
        yield from [
            Transit().set_state(self.exit.bar, Compass.N, self.into.foyer, Traffic.flowing),
            Transit().set_state(self.exit.foyer, Compass.W, self.into.cloakroom, Traffic.flowing),
        ]


class World(WorldBuilder):
    def build(self):
        yield from [
            Entity(name="Cloak", type="Clothing").set_state(self.map.spot.cloakroom),
            Entity(name="Hook", type="Fixture").set_state(self.map.home.cloakroom),
            Entity(name="Message", type="Marking").set_state(self.map.home.bar),
        ]


class Adventure(Drama):

    def do_look(self, this, text, director, *args, **kwargs):
        """
        look
        where | where am i

        """
        self.set_state(Focus.info)
        print(self)
        yield Prologue("<> Looking around.")


class Story(StoryBuilder):
    def build(self):
        yield Adventure(world=self.world, config=self.config).set_state(self.world.map.spot.foyer)


if __name__ == "__main__":
    quick_start(balladeer.examples.ex_11_inventory_compass)
