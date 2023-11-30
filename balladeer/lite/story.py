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
import copy
import operator
import uuid
import warnings

from balladeer.lite.director import Director
from balladeer.lite.drama import Drama
from balladeer.lite.loader import Loader
from balladeer.lite.speech import Speech
from balladeer.lite.types import Detail
from balladeer.lite.types import Turn
from balladeer.lite.types import Grouping
from balladeer.lite.world import WorldBuilder


class StoryBuilder:

    @staticmethod
    def settings(*names, themes={}) -> dict:
        rv = dict()
        for key in ("ink", ):
            rv[key] = dict([(k, v) for name in names for k, v in themes.get(name, {}).get(key, {}).items()])
        return rv

    def __init__(
        self,
        *speech: tuple[Speech],
        config=None,
        assets: Grouping = Grouping(),
        world: WorldBuilder = None,
        **kwargs,
    ):
        self.uid = uuid.uuid4()
        self.speech = deque(speech)
        self.config = config
        self.assets = assets.copy()

        self.world = world or WorldBuilder()

        self.drama = deque([])
        self.director = Director(**kwargs)
        try:
            self.make()
        except Exception:
            pass

    def make(self):
        self.drama = deque(self.build())

    def __deepcopy__(self, memo):
        rv = self.__class__(*self.speech, self.config, self.assets)
        rv.world = copy.deepcopy(self.world, memo)
        for drama in (d for d in rv.drama if hasattr(d, "active")):
            del drama.active  # Will be regenerated on demand

        return rv

    def build(self):
        drama_classes = Drama.__subclasses__()
        if self.speech or not drama_classes:
            yield Drama(*self.speech, world=self.world, config=self.config)
        else:
            yield from (d(world=self.world, config=self.config) for d in drama_classes)

    @property
    def context(self):
        return next((reversed(sorted(self.drama, key=operator.attrgetter("state")))), None)

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

        rv = Turn(scene, specs, roles, speech, blocks, self.director.notes.copy())

        # Directive handlers
        n = 0
        for block, (key, note) in zip(blocks, self.director.notes.items()):
            for m in note.maps:
                for (action, entity, entities) in m.get("directives", []):
                    method = getattr(drama, f"{drama.prefixes[1]}{action}", None)
                    if isinstance(method, Callable):
                        try:
                            method(entity, *entities, identifier=key, **rv._asdict())
                        except Exception as e:
                            warnings.warn(f"Error in directive handler {method}")
                            warnings.warn(str(e))
                    n += 1

        drama.set_state(Detail.none)
        return rv

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.director.notes.clear()
        return False
