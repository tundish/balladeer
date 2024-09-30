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

import enum

from balladeer.lite.loader import Loader


class Resident:

    def __init__(self, *args, selector: dict[str, list] = {}, **kwargs):
        self.selector = selector | {"states": set(selector.get("states", []))}
        super().__init__(*args, **kwargs)

    @property
    def focus(self):
        return next((i for i in self.world.typewise.get("Focus", []) if self.is_resident(i.get_state("Spot"))), None)

    def is_resident(self, *args: tuple[enum.Enum]):
        return all(str(i).lower() in states for i in args if (states := self.selector["states"]) and i is not None)

    def scripts(self, assets: list):
        return [
            i for i in assets if isinstance(i, Loader.Scene) and any(i.path.match(p) for p in self.selector["paths"])
        ]
