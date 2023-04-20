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
import random
import balladeer
from balladeer.lite.app import quick_start
from balladeer.lite.drama import Drama
from balladeer.lite.entity import Entity
from balladeer.lite.speech import Dialogue
from balladeer.lite.speech import Speech
from balladeer.lite.story import StoryBuilder
from balladeer.lite.types import State
from balladeer.lite.world import WorldBuilder


__doc__ = """
~/py3.11-dev/bin/python -m balladeer.examples.10_lite_sequence.logic

"""


class Green(State, enum.Enum):
    dark = "#005500"
    mint = "#008800"
    lime = "#00BB00"


class World(WorldBuilder):
    def build(self):
        yield from [
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
            Entity(type="Bottle").set_state(random.choice(list(Green)), 1),
        ]


class Song(Drama):
    @property
    def unbroken(self):
        return [i for i in self.ensemble if i.type == "Bottle" and i.state == 1]

    def do_bottle(self, this, text, director, *args, **kwargs):
        """
        bottle
        break

        """
        try:
            random.choice(self.unbroken).state = 0
            yield Dialogue(
                """
                <>  And if one green bottle should *accidentally* fall,
                There'll be...
                """
            )

        except IndexError:
            pass

    def do_look(self, this, text, director, *args, **kwargs):
        """
        look

        """
        yield Dialogue("<> Singing...")

    def interlude(self, *args, **kwargs) -> list[Speech]:
        self.state = len(self.unbroken)
        return self.speech.copy()


class Story(StoryBuilder):
    def build(self):
        yield Song(world=self.world, config=self.config)


if __name__ == "__main__":
    quick_start(balladeer.examples, "ex_06_js_frontend")
