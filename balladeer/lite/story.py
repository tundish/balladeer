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
from collections import namedtuple
from collections.abc import Callable
import uuid
import warnings

from balladeer.lite.director import Director
from balladeer.lite.drama import Drama
from balladeer.lite.loader import Loader
from balladeer.lite.speech import Speech
from balladeer.lite.types import Grouping
from balladeer.lite.world import WorldBuilder


class StoryBuilder:

    Turn = namedtuple(
        "Turn",
        ["scene", "specs", "roles", "speech", "blocks", "notes"],
        defaults=(None, None)
    )

    def __init__(
        self,
        *speech: tuple[Speech],
        config = None,
        assets: Grouping = Grouping(),
        world: WorldBuilder = None, drama: [list | deque] = None,
        **kwargs
    ):
        self.uid = uuid.uuid4()
        self.speech = speech
        self.config = config
        self.assets = assets.copy()
        if not world:
            world_type = next(reversed(WorldBuilder.__subclasses__()), WorldBuilder)
            self.world = world_type(config)
        else:
            self.world = world

        self.drama = drama or deque([])
        self.drama.extend(self.build())

        self.director = Director(**kwargs)

    def build(self):
        drama_classes = Drama.__subclasses__()
        if self.speech or not drama_classes:
            yield Drama(
                *self.speech,
                world=self.world,
                config=self.config
            )
        else:
            yield from (d(world=self.world, config=self.config) for d in drama_classes)

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

    def action(self, text: str, *args, **kwargs):
        drama = self.context
        actions = drama.actions(
            text,
            context=self.director,
            ensemble=drama.ensemble,
            prefix=drama.prefixes[0],
        )
        fn, args, kwargs = drama.pick(actions)
        if not fn:
            return None

        try:
            drama.speech.extend(drama(fn, *args, **kwargs))
        except Exception as e:
            warnings.warn(e)

        return fn, args, kwargs

    def turn(self, *args, **kwargs):
        self.context.interlude(*args, **kwargs)
        return self

    def __enter__(self):
        drama = self.context

        # Director selection
        scripts = drama.scripts(self.assets.get(Loader.Scene, []))
        scene, specs, roles = self.director.selection(scripts, drama.ensemble)
        assert isinstance(scene, Loader.Scene), f"{type(scene)} is not a Scene"

        # TODO: Entity aspects

        # Collect waiting speech
        try:
            speech = [drama.speech.popleft()]
        except AttributeError:
            speech = drama.speech.copy()
            drama.speech.clear()
        except IndexError:
            speech = []

        blocks = list(self.director.rewrite(scene, roles, speech))

        # Directive handlers
        for action, entity, entities in self.direction:
            method = getattr(drama, f"{drama.prefixes[1]}{action}")
            if isinstance(method, Callable):
                try:
                    method(entity, *entities)
                except Exception as e:
                    warnings.warn(e)

        return self.Turn(scene, specs, roles, speech, blocks, self.director.notes.copy())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.director.notes.clear()
        return False
