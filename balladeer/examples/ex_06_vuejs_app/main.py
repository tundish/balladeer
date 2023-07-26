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
from balladeer import Session
from balladeer import quick_start
from balladeer import Drama
from balladeer import Entity
from balladeer import Dialogue
from balladeer import Speech
from balladeer import StoryBuilder
from balladeer import Page
from balladeer import State
from balladeer import WorldBuilder


__doc__ = """
python3 -m balladeer.examples.ex_06_vuejs_app.main

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


class Wall(Drama):
    @property
    def unbroken(self):
        return [i for i in self.ensemble if "Bottle" in i.types and i.state == 1]

    def do_bottle(self, this, text, director, *args, **kwargs):
        """
        bottle
        break | break bottle

        """
        try:
            random.choice(self.unbroken).state = 0
            yield Dialogue("""
                <>  And if one green bottle should *accidentally* fall,
                There'll be...
                """)

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
    title = "Balladeer Example: JS integration"

    def build(self):
        yield Wall(world=self.world, config=self.config)


class Song(Session):
    def compose(
        self, request, page: Page, story: StoryBuilder = None, turn: StoryBuilder.Turn = None
    ) -> Page:
        page.paste(
            '<div id="app"><diorama v-bind:ensemble="ensemble"></diorama></div>',
            zone=page.zone.app
        )
        page = super().compose(request, page, story, turn)
        page.paste(
            '<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>',
            zone=page.zone.link
        )
        return page


if __name__ == "__main__":
    quick_start(balladeer.examples.ex_06_vuejs_app)
