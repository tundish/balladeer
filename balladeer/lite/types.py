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
import enum
import random
import uuid

from balladeer.lite.loader import Loader


# turberfield.utils.misc
def group_by_type(items):
    rv = defaultdict(list)
    for i in items:
        rv[type(i)].append(i)
    return rv


Into = None
Spot = None
Exit = None


# turberfield.dialogue.types
class State:

    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]


@dataclasses.dataclass(unsafe_hash=True)
class Entity:

    name: dataclasses.InitVar = ""
    names: list = dataclasses.field(default_factory=list, compare=False)
    type: str = None
    states: dict = dataclasses.field(default_factory=dict, compare=False)

    def __post_init__(self, name):
        if name:
            self.names.insert(0, name)

    @property
    def name(self):
        return random.choice(self.names or [self.name])


class Traffic(State, enum.Enum):
    blocked = enum.auto()
    forward = enum.auto()
    reverse = enum.auto()
    flowing = enum.auto()


class Transit(Entity):
    pass


# TODO: Reconcile with balladeer.cartography.Map
class MapBuilder:

    def __init__(self, spots):
        global Into, Spot, Exit
        self.into = Into = enum.Enum("Into", spots, type=Waypoint)
        self.exit = Exit = enum.Enum("Exit", spots, type=Waypoint)
        self.spot = Spot = enum.Enum("Spot", spots, type=Waypoint)
        self.transits = list(self.build())

    def build(self):
        raise NotImplementedError


class WorldBuilder:

    def __init__(self, config, map=None):
        self.config = config
        self.map = map
        self.entities = list(self.build())

    def build(self):
        raise NotImplementedError

 
class Drama:

    def __init__(self, config):
        self.config = config

    def ensemble(self, world):
        return world.entities

    def scripts(self, assets):
        return [i for i in assets if isinstance(i, Loader.Scene)]


class Story:

    def __init__(self, config=None, world=None, drama=[]):
        self.uid = uuid.uuid4()
        self.config = config
        self.world = world
        self.drama = drama or [Drama(config)]

    @property
    def context(self):
        return self.drama[0]

