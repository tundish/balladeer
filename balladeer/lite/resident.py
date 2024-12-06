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

from collections import namedtuple
import enum
import operator

from balladeer.lite.drama import Drama
from balladeer.lite.entity import Entity
from balladeer.lite.loader import Loader


class Resident(Drama):

    Move = namedtuple("Move", ["heading", "spot", "via"])

    @staticmethod
    def item_state(spec: str | int, pool: list[enum.Enum] = [], default=0):
        try:
            name, value = spec.lower().split(".")
        except AttributeError:
            return spec

        lookup = {typ.__name__.lower(): typ for typ in pool}

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

    @staticmethod
    def item_type(name: str, default=Entity):
        name = name or ""
        return {
            typ.__name__.lower(): typ for typ in cls.types
        }.get(name.lower(), default)

    def __init__(self, *args, selector: dict[str, list] = {}, **kwargs):
        self.selector = selector | {"states": set(selector.get("states", []))}
        self.selector["paths"] = self.selector.get("paths", [])
        super().__init__(*args, **kwargs)

    @property
    def focus(self):
        selected = [
            i for i in self.world.typewise.get("Focus", [])
            if self.is_resident(i.get_state(self.world.map.spot))
        ]
        ordered = sorted(selected, key=operator.attrgetter("state"), reverse=True)
        print(f"{ordered=}")
        return next(iter(ordered), None)

    @property
    def exits(self):
        try:
            spot = self.focus.get_state(self.world.map.spot)
            return [self.Move(*option) for option in sorted(self.world.map.options(spot), key=str)]
        except AttributeError:
            return []

    def is_resident(self, *args: tuple[enum.Enum]):
        states = self.selector["states"]
        return all(str(i).lower() in states for i in args if i is not None) or not states
        rv = all(str(i).lower() in states for i in args if i or states)
        return rv

    def scripts(self, assets: list):
        return [
            i for i in assets
            if isinstance(i, Loader.Scene)
            and any(i.path.match(p) for p in self.selector["paths"])
            or not self.selector["paths"]
        ]
