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

from balladeer.lite.compass import MapBuilder
from balladeer.lite.entity import Entity
from balladeer.lite.types import Grouping
from balladeer.lite.types import State


class WorldBuilder:
    """

    This class is the base for the world of your narrative.

    It is responsible for holding all the entities you need.
    It helps you retrieve them when you need them.

    To populate a new world, override the `build` method of a subclass.
    It is a generator of entity objects.

    .. literalinclude:: ../lite/test/test_world.py
       :pyobject: WorldBuilderTests.test_simple.World
       :dedent: 8

    """
    def __init__(self, map: MapBuilder=None, config: dict=None):
        self.map = map
        self.config = config

        self.entities = list(self.build())
        self.typewise = Grouping.typewise(self.entities)

    @property
    def statewise(self) -> Grouping:
        """
        Returns a :py:class:`~balladeer.lite.types.Grouping`
        whose keys are all of type ``int`` or
        :py:class:`~balladeer.lite.types.State`.

        The corresponding value is a list of entities with that state.

        """
        rv = Grouping(list)
        for entity in self.entities:
            for state in entity.states.values():
                rv[str(state)].append(entity)
        return rv

    def build(self) -> Generator[Entity]:
        """
        Override this method to generate Entities.

        """
        return ()
