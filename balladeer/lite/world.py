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
from balladeer.lite.types import Grouping
from balladeer.lite.types import State



class WorldBuilder:
    def __init__(self, map, config=None):
        self.map = map
        self.config = config

        self.entities = list(self.build())
        self.typewise = Grouping.typewise(self.entities)

    def build(self):
        return ()
