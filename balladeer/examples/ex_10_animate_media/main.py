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
from balladeer import Drama
from balladeer import Entity
from balladeer import WorldBuilder

__doc__ = """
python3 -m balladeer.examples.10_animate_media.main

"""


class World(WorldBuilder):
    def build(self):
        yield from [
            Entity(name="Biffy", type="Animal").set_state(1),
            Entity(name="Bashy", type="Animal").set_state(1),
            Entity(name="Rusty", type="Weapon").set_state(1),
        ]


class Fight(Drama):

    def on_attacking(self, entity: Entity, *args: tuple[Entity], **kwargs):
        for enemy in args:
            enemy.set_state(0)


class Story(StoryBuilder):
    def build(self):
        yield Fight(world=self.world, config=self.config)


if __name__ == "__main__":
    quick_start(balladeer.examples.ex_10_animate_media)
