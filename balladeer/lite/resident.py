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

from balladeer import Drama
from balladeer.lite.loader import Loader


class Resident(Drama):

    Move = namedtuple("Move", ["heading", "spot", "via"])

    def __init__(self, *args, selector: dict[str, list] = {}, **kwargs):
        self.selector = selector | {"states": set(selector.get("states", []))}
        self.selector["paths"] = self.selector.get("paths", [])
        super().__init__(*args, **kwargs)

    @property
    def focus(self):
        selected = [i for i in self.world.typewise.get("Focus", []) if self.is_resident(i.get_state("Spot"))]
        return next(reversed(sorted(selected, key=operator.attrgetter("state"))), None)

    @property
    def exits(self):
        spot = self.focus.get_state("Spot")
        return [self.Move(*option) for option in sorted(self.world.map.options(spot), key=str)]

    def is_resident(self, *args: tuple[enum.Enum]):
        states = self.selector["states"]
        return all(str(i).lower() in states for i in args if i or states)

    def scripts(self, assets: list):
        return [
            i for i in assets
            if isinstance(i, Loader.Scene)
            and any(i.path.match(p) for p in self.selector["paths"])
            or not self.selector["paths"]
        ]
