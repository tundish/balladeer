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

from collections import deque
from collections.abc import Callable
import uuid
import warnings

from balladeer.lite.director import Director
from balladeer.lite.drama import Drama
from balladeer.lite.world import WorldBuilder


class StoryBuilder:
    def __init__(
        self, config, world: WorldBuilder = None, drama: [list | deque] = None, **kwargs
    ):
        self.uid = uuid.uuid4()
        self.config = config
        if not world:
            world_type = next(iter(WorldBuilder.__subclasses__()), WorldBuilder)
            self.world = world_type(config)
        else:
            self.world = world

        self.drama = drama or deque([])
        self.drama.extend(self.build())

        self.director = Director(**kwargs)

    def build(self):
        drama_classes = Drama.__subclasses__()
        if not drama_classes:
            yield Drama(self.world, config=self.config)
        else:
            yield from (d(self.world, config=self.config) for d in drama_classes)

    @property
    def context(self):
        return self.drama[0]

    @property
    def notes(self):
        return list(self.director.notes.values())

    @property
    def direction(self):
        notes = self.notes
        if not notes:
            return []
        else:
            return [t for i in (m.get("directives", []) for m in notes[-1].maps) for t in i]

    def influence(self, text: str, *args, **kwargs):
        performance = self.context
        actions = performance.matches(text)
        fn, args, kwargs = performance.pick(actions)
        # TODO: Handle exceptions
        performance(fn, *args, **kwargs)

    def turn(self, directives: list = [], prefix="on_", **kwargs): # -> Page
        # Call Drama interlude
        speech = self.context.interlude(**kwargs)
        # Director selection
        # Entity aspects
        # Director rewrite
        for action, entity, entities in directives:
            method = getattr(self.context, f"{prefix}{action}")
            if isinstance(method, Callable):
                # TODO: Log errors
                yield method(entity, *entities, **kwargs)

        # TODO:
        # Generate parser options
        # Build page
