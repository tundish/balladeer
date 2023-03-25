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

from collections import defaultdict
import dataclasses
import uuid

from balladeer.lite.loader import Loader


# turberfield.utils.misc
def group_by_type(items):
    rv = defaultdict(list)
    for i in items:
        rv[type(i)].append(i)
    return rv


# turberfield.dialogue.types
class State:

    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]


@dataclasses.dataclass(unsafe_hash=True)
class Entity:

    name: str
    type: str = None
    states: dict = dataclasses.field(default_factory=dict, compare=False)


class World:

    def __init__(self, config):
        self.config = config
        self.population = list(self.build())

    @staticmethod
    def build():
        raise NotImplementedError

 
class Drama:

    def __init__(self, config):
        self.config = config

    def ensemble(self, world):
        return world.population

    def scripts(self, assets):
        return [i for i in assets if isinstance(i, Loader.Scene)]


class Story:

    def __init__(self, config=None, world_builder=World):
        self.uid = uuid.uuid4()
        self.config = config
        self.world = world_builder(config)
        self.drama = [
            Drama(config)
        ]

    @property
    def context(self):
        return self.drama[0]


