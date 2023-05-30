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

import dataclasses

import balladeer
from balladeer import Compass
from balladeer import Detail
from balladeer import Drama
from balladeer import Entity
from balladeer import Epilogue
from balladeer import MapBuilder
from balladeer import Prologue
from balladeer import StoryBuilder
from balladeer import Traffic
from balladeer import Transit
from balladeer import WorldBuilder
from balladeer import quick_start

__doc__ = """
python3 -m balladeer.examples.11_.inventory_compass.main

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
            Entity(
                name="Cloak", type="Clothing",
                sketch="A {names[0]} so black that its folds and textures cannot be perceived.",
                aspect="It seems to swallow all light.",
            ).set_state(self.map.spot.inventory),
            Entity(
                name="Hook", type="Fixture",
                sketch="A brass hook.",
                aspect="Solid. This is not for decoration.",
            ).set_state(self.map.home.cloakroom),
            Entity(
                name="Message", type="Marking",
                sketch="Someone has written a message in the dust on the floor. It says: {aspect}",
                aspect="You win!",
            ).set_state(self.map.home.bar, 0),
        ]


class Adventure(Drama):

    def do_look(self, this, text, director, *args, **kwargs):
        """
        look
        where | where am i

        """
        self.set_state(Detail.here)
        here = self.get_state(self.world.map.spot)
        entities = [
            i for i in self.world.entities
            if i.get_state("Spot") in (here, self.world.map.spot.inventory)
        ]
        yield Epilogue("<> Looking around, you see:")
        for entity in entities:
            sketch = entity.sketch.format(**dataclasses.asdict(entity))
            yield Epilogue(f"+ {sketch}")

        yield Epilogue("<> Exits are:")
        for dirn, dest, transit in self.world.map.options(here):
            yield Epilogue(f"+ {dirn.title}")

    def do_go(self, this, text, director, *args, heading: Compass, **kwargs):
        """
        {heading.name}
        go {heading.name}

        """
        here = self.get_state(self.world.map.spot)
        print(self.world.map.options(here))
        yield Prologue(f"<> You try to go {heading.title}.")


class Story(StoryBuilder):
    def build(self):
        yield Adventure(world=self.world, config=self.config).set_state(
            self.world.map.spot.foyer, Detail.none
        )


if __name__ == "__main__":
    quick_start(balladeer.examples.ex_11_inventory_compass)
