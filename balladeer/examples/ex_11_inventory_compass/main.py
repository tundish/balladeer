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
from balladeer import Compass
from balladeer import Detail
from balladeer import Drama
from balladeer import Entity
from balladeer import Prologue, Dialogue, Epilogue
from balladeer import MapBuilder
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
            ).set_state(self.map.home.cloakroom, self.map.spot.cloakroom, 0),
            Entity(
                name="Message", type="Marking",
                sketch="Someone has written a message in the dust on the floor. It says: {aspect}",
                aspect="You win!",
            ).set_state(self.map.home.bar, 0),
        ]


class Adventure(Drama):

    def do_help(self, this, text, director, *args, **kwargs):
        """
        help | syntax

        """
        commands = [sorted(i, key=lambda x: len(x), reverse=True)[0] for i in self.active.values() if i]
        yield Epilogue(
            "<> Syntax:\n" +
            "\n".join([f"+ {i.upper()}" for i in commands])
        )

    def do_hint(self, this, text, director, *args, **kwargs):
        """
        hint | h

        """
        self.set_state(Detail.hint)

    def do_look(self, this, text, director, *args, **kwargs):
        """
        look
        where | where am i

        """
        self.set_state(Detail.here)
        here = self.get_state(self.world.map.spot)
        entities = [
            i for i in self.world.entities if i.get_state("Spot") == here
        ]
        if entities:
            yield Dialogue("<> You take a look around.")
            yield Dialogue( "<> You see:\n" + "\n".join([f"+ {i.description}" for i in entities]))

        yield Epilogue(
            "<> Exits are:\n" +
            "\n".join([f"+ {dirn.title}" for dirn, dest, transit in self.world.map.options(here)])
        )

    def do_inventory(self, this, text, director, *args, **kwargs):
        """
        inventory | i

        """
        self.set_state(Detail.held)
        here = self.get_state(self.world.map.spot)
        entities = [
            i for i in self.world.entities if i.get_state("Spot") == self.world.map.spot.inventory
        ]
        yield Epilogue(
            "<> You are carrying:\n" +
            "\n".join([f"+ {i.description}" for i in entities])
        )


    def do_move(self, this, text, director, *args, heading: Compass, **kwargs):
        """
        {heading.name} | {heading.label}
        go {heading.name} | go {heading.label}

        """
        here = self.get_state(self.world.map.spot)
        options = {compass: spot for compass, spot, transit in self.world.map.options(here)}
        if heading not in options:
            yield Prologue(f"<> You can't go {heading.title} from here.")
        else:
            self.set_state(options[heading])

    """
    def do_take(self, this, text, director, *args, heading: Compass, **kwargs):
        pass

    def do_drop(self, this, text, director, *args, heading: Compass, **kwargs):
        pass
    """

    def do_hang(
        self, this, text, director, *args,
        clothing: "world.typewise[Clothing]",
        fixture: "world.typewise[Fixture]",
        **kwargs
    ):
        """
        hang {clothing.names[0]} on {fixture.names[0]}

        """
        yield Prologue(f"<> Not yet.")


class Story(StoryBuilder):
    def build(self):
        yield Adventure(world=self.world, config=self.config).set_state(
            self.world.map.spot.foyer, Detail.none
        )


if __name__ == "__main__":
    quick_start(balladeer.examples.ex_11_inventory_compass)
