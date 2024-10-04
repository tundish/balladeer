#!/usr/bin/env python
# encoding: utf8

# Copyright 2024 D E Haynes

# This file is part of balladeer.
#
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

import copy
import enum
import operator
import warnings
import sys

from balladeer.lite.compass import Compass
from balladeer.lite.drama import Drama
from balladeer.lite.entity import Entity
from balladeer.lite.types import Fruition
from balladeer.lite.types import Grouping
from balladeer.lite.loader import Loader
from balladeer.lite.compass import MapBuilder
from balladeer.lite.resident import Resident
from balladeer.lite.speech import Speech
from balladeer.lite.storybuilder import StoryBuilder
from balladeer.lite.compass import Transit
from balladeer.lite.compass import Traffic
from balladeer.lite.world import WorldBuilder
from busker.stager import Stager


class StoryStager(StoryBuilder):

    states = [Compass, Fruition, Traffic]
    types = [Drama, Entity, Transit]

    @classmethod
    def item_state(cls, spec: str | int, pool: list[enum.Enum] = [], default=0):
        try:
            name, value = spec.lower().split(".")
        except AttributeError:
            return spec

        lookup = {typ.__name__.lower(): typ for typ in pool + cls.states}

        try:
            cls = lookup[name]
        except KeyError:
            return default

        try:
            return cls[value]
        except KeyError:
            try:
                return cls[value.upper()]
            except KeyError:
                return default

    @classmethod
    def item_type(cls, name: str, default=Entity):
        name = name or ""
        return {
            typ.__name__.lower(): typ for typ in cls.types
        }.get(name.lower(), default)

    def __init__(
        self,
        *speech: tuple[Speech],
        config=None,
        assets: Grouping = Grouping(list),
        **kwargs,
    ):
        staging = [i.data for i in assets[Loader.Staging]]
        self.stager = Stager(staging).prepare()

        spots = self.stager.gather_state()
        m = MapBuilder(spots=spots)
        world = WorldBuilder(map=m, config=config, assets=assets)
        super().__init__(*speech, config=config, assets=assets, world=world, **kwargs)

    def __deepcopy__(self, memo):
        speech = copy.deepcopy(self.speech, memo)
        config = copy.deepcopy(self.config, memo)
        assets = copy.deepcopy(self.assets, memo)
        rv = self.__class__(*speech, config=config, assets=assets)
        return rv

    def make(self, **kwargs):
        self.drama: dict[tuple[str, str], Drama] = {
            (realm, name): self.build(realm, name) for (realm, name) in self.stager.puzzles
        } or {(None, None): Drama(*self.speech, config=self.config, world=self.world)}

    def build(self, realm: str, name: str, **kwargs):
        pool = [self.world.map.home, self.world.map.into, self.world.map.exit, self.world.map.spot]
        puzzle = self.stager.gather_puzzle(realm, name)
        drama_type = self.item_type(puzzle.get("type"), default=Resident)
        states = [self.item_state(f"{k}.{v}", pool=pool) for k, v in puzzle.get("init", {}).items()]
        drama = drama_type(
            *self.speech,
            config=self.config,
            world=self.world,
            name=puzzle.get("name"),
            type=drama_type.__name__,
            links=set(target for transition in puzzle.get("chain", {}).values() for target in transition),
            sketch=puzzle.get("sketch", ""),
            aspect=puzzle.get("aspect", ""),
            revert=puzzle.get("revert", ""),
            selector=puzzle.get("selector", {}),
        ).set_state(0, *states)

        for item in puzzle.get("items"):
            item_names = [i for i in [item.get("name")] + item.get("names", []) if i]
            item_types = list(filter(None, [item.get("type")] + item.get("types", [])))
            item_type = next((self.item_type(i) for i in item_types), Entity)
            states = [self.item_state(i, pool=pool) for i in item.get("states", [])]
            entity = item_type(
                names=item_names,
                types={i for i in item_types if i != item_type.__name__},
                links={puzzle.get("name")},
                sketch=item.get("sketch", ""),
                aspect=item.get("aspect", ""),
                revert=item.get("revert", ""),
            ).set_state(*states)

            if item_type is Transit:
                self.world.map.transits.append(entity)
            else:
                self.world.entities.append(entity)

        self.world.typewise = Grouping.typewise(self.world.entities)
        return drama

    @property
    def context(self):
        active = [self.drama[(realm, name)] for realm, name in self.stager.active]

        drama = sorted(
            [d for d in active if getattr(d, "focus", True)],
            key=operator.attrgetter("state"),
            reverse=True
        )
        drama = drama or active
        return next(iter(drama), None)

    def monitor_context(
        self,
        realm: str,
        name: str,
        drama: Drama,
        terminal={Fruition.withdrawn, Fruition.defaulted, Fruition.cancelled, Fruition.completion}
    ):
        pool = [self.world.map.home, self.world.map.into, self.world.map.exit, self.world.map.spot]
        if (state := drama.get_state(Fruition)) in terminal:
            for event in self.stager.terminate(realm, name, state.name):
                state = self.item_state(event.payload, pool=pool)
                if isinstance(event.target, str):
                    self.drama[event.realm, event.target].set_state(state)
                else:
                    entities = [
                        entity.set_state(state)
                        for entity in drama.ensemble
                        if set(event.target) <= entity.types
                    ]

    def turn(self, *args, **kwargs):
        for realm, name in self.stager.active.copy():
            drama = self.drama[(realm, name)]
            self.monitor_context(realm, name, drama)

        try:
            self.context.interlude(*args, **kwargs)
        except AttributeError:
            warnings.warn("Turn exhausted context")
        return self
