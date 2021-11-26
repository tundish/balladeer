#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2021 D E Haynes

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

from turberfield.dialogue.types import EnumFactory
from turberfield.dialogue.types import Stateful
from turberfield.utils.homogeneous import vector


class Compass(EnumFactory, enum.Enum):

    N   = vector(+0, +1)
    NE  = vector(+1, +1)
    E   = vector(+1, +0)
    SE  = vector(+1, -1)
    S   = vector(+0, -1)
    SW  = vector(-1, -1)
    W   = vector(-1, +0)
    NW  = vector(-1, -1)

    @property
    def back(self):
        return {
            "N":  Compass.S,
            "NE": Compass.SW,
            "E":  Compass.W,
            "SE": Compass.NW,
            "S":  Compass.N,
            "SW": Compass.NE,
            "W":  Compass.E,
            "NW": Compass.SE
        }.get(self.name)

    @property
    def bearing(self):
        phase = 180 * cmath.phase(complex(*self.value[:2])) / cmath.pi
        if phase <= 90:
            rv = 90 - phase
        elif phase <= 180:
            rv = 270 + (180 - phase)
        elif phase <= 270:
            rv = 180 + (270 - phase)
        else:
            rv = 90 + 360 - phase
        return rv % 360

