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
from collections.abc import Generator
import enum

from balladeer.lite.entity import Entity
from balladeer.lite.types import State


Into = None
Spot = None
Exit = None


class Traffic(State, enum.Enum):
    blocked = enum.auto()
    forward = enum.auto()
    reverse = enum.auto()
    flowing = enum.auto()


class Transit(Entity):
    pass


# TODO: Reconcile with balladeer.cartography.Map
class MapBuilder:
    def __init__(self, spots, config=None):
        self.config = config
        global Into, Spot, Exit
        self.into = Into = enum.Enum("Into", spots, type=State)
        self.exit = Exit = enum.Enum("Exit", spots, type=State)
        self.spot = Spot = enum.Enum("Spot", spots, type=State)
        self.transits = list(self.make())

    def build(self) -> Generator[Transit]:
        return ()

    def make(self):
        yield from self.build()


class WorldBuilder:
    def __init__(self, map, config=None):
        self.map = map
        self.config = config
        # TODO: Grouper by type or name of type?
        self.entities = list(self.build())

    def build(self):
        return ()
