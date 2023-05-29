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

import cmath
from collections import defaultdict
import enum

from turberfield.dialogue.types import DataObject
from turberfield.dialogue.types import EnumFactory
from turberfield.dialogue.types import Stateful
from turberfield.utils.homogeneous import vector


class Compass(EnumFactory, enum.Enum):
    N = vector(+0, +1)
    NE = vector(+1, +1)
    E = vector(+1, +0)
    SE = vector(+1, -1)
    S = vector(+0, -1)
    SW = vector(-1, -1)
    W = vector(-1, +0)
    NW = vector(-1, -1)

    @property
    def back(self):
        return {
            "N": Compass.S,
            "NE": Compass.SW,
            "E": Compass.W,
            "SE": Compass.NW,
            "S": Compass.N,
            "SW": Compass.NE,
            "W": Compass.E,
            "NW": Compass.SE,
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


class MapBuilder:
    def __init__(self, spots, config=None):
        self.config = config
        global Into, Home, Spot, Exit
        self.into = Into = enum.Enum("Into", spots, type=State)
        self.home = Home = enum.Enum("Home", spots, type=State)
        self.spot = Spot = enum.Enum("Spot", spots, type=State)
        self.exit = Exit = enum.Enum("Exit", spots, type=State)
        self.transits = list(self.make())

    @property
    def topology(self):
        for t in self.transits:
            d = t.get_state(self.exit)
            a = t.get_state(self.into)
            v = t.get_state(Via)
            c = t.get_state(Compass)
            b = c and c.back
            if v in (Via.bidir, Via.forwd):
                yield d, c, t, a
            if v in (Via.bidir, Via.bckwd):
                yield a, b, t, d

    def options(self, waypoint):
        typ = type(waypoint)
        return {
            (c or n, typ[a.name], t)
            for n, (d, c, t, a) in enumerate(self.topology)
            if d.name == waypoint.name
        }

    def route(self, locn, dest):
        if (locn.name, dest.name) in self.routes:
            return self.routes[(locn.name, dest.name)]

        rvs = set()
        paths = [[locn.name]]

        graph = defaultdict(set)
        for d, _, t, a in self.topology:
            graph[d.name].add(a.name)

        n = len(graph)
        d = 1
        while n >= 0 or not rvs:
            nxt = []
            for p in paths:
                if p[-1] == dest.name:
                    rvs.add(tuple(p))
                else:
                    nodes = graph[p[-1]]
                    d = len(nodes)
                    for i in nodes:
                        if i not in p:
                            nxt.append(p.copy())
                            nxt[-1].append(i)
            paths = nxt
            n = n - d

        rv = [type(locn)[i] for i in sorted(rvs, key=len)[0]] if rvs else []
        self.routes[(locn.name, dest.name)] = rv
        return rv

    def build(self) -> Generator[Transit]:
        return ()

    def make(self):
        yield from self.build()

