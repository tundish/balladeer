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
from collections import deque
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


class State:
    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]


from balladeer.lite.entity import Entity


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
        self.into = Into = enum.Enum("Into", spots, type=State)
        self.exit = Exit = enum.Enum("Exit", spots, type=State)
        self.spot = Spot = enum.Enum("Spot", spots, type=State)
        self.transits = list(self.build())

    def build(self):
        raise NotImplementedError


class WorldBuilder:
    def __init__(self, config, map=None):
        self.config = config
        self.map = map
        self.entities = list(self.build())

    def build(self):
        return ()


class Drama:
    def __init__(self, config):
        self.config = config

    def ensemble(self, world):
        return world.entities

    def scripts(self, assets):
        return [i for i in assets if isinstance(i, Loader.Scene)]

    def media(self, assets):
        return {i.path: i for i in assets if isinstance(i, Loader.Asset)}


class StoryBuilder:
    def __init__(self, config, world: WorldBuilder = None, drama: [list | deque] = None):
        self.uid = uuid.uuid4()
        self.config = config
        if not world:
            world_type = next(iter(WorldBuilder.__subclasses__()), WorldBuilder)
            self.world = world_type(config)
        else:
            self.world = world

        self.drama = drama or deque([])
        self.drama.extend(self.build())

    def build(self):
        drama_classes = Drama.__subclasses__()
        if not drama_classes:
            yield Drama(self.config)
        else:
            yield from (d(self.config) for d in drama_classes)

    @property
    def context(self):
        return self.drama[0]
