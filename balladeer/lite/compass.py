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
from collections.abc import Generator
import enum
import itertools

from turberfield.utils.homogeneous import vector

from balladeer.lite.entity import Entity
from balladeer.lite.types import State


class Bearing:
    @classmethod
    def bearing(cls, *args) -> float:
        """
        Calculate the angular bearing of the endpoint of
        a route as measured from the beginning.

        >>> Compass.bearing(Compass.E)
        90.0

        >>> Compass.bearing(Compass.N, Compass.E, Compass.E, Compass.SW)
        90.0

        """
        # FIXME sum triggers bug in __add__
        vec = list(itertools.accumulate(i.value[-1] for i in args))[-1]
        phase = 180 * cmath.phase(complex(*vec[:2])) / cmath.pi
        if phase <= 90:
            rv = 90 - phase
        elif phase <= 180:
            rv = 270 + (180 - phase)
        elif phase <= 270:
            rv = 180 + (270 - phase)
        else:
            rv = 90 + 360 - phase
        return rv % 360


class Compass(Bearing, State, enum.Enum):
    """
    A state to represent the eight points of the compass.

    .. literalinclude:: ../lite/compass.py
       :lines: 68-75

    """
    N = ["North", vector(+0, +1)]
    NE = ["Northeast", "North East", vector(+1, +1)]
    E = ["East", vector(+1, +0)]
    SE = ["Southeast", "South East", vector(+1, -1)]
    S = ["South", vector(+0, -1)]
    SW = ["Southwest", "South West", vector(-1, -1)]
    W = ["West", vector(-1, +0)]
    NW = ["Northwest", "North West", vector(-1, -1)]

    @property
    def back(self):
        """
        Return the opposite point:

        >>> Compass.NE.back
        Compass.SW

        """
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


Into = None
Home = None
Spot = None
Exit = None


class Traffic(State, enum.Enum):
    blocked = "No traffic"
    forward = "Traffic flow forward"
    reverse = "Traffic flow reversed"
    flowing = "Traffic flows freely"


class Transit(Entity):
    pass


class MapBuilder:
    """

    This class is the base for the map of your story world.

    It is responsible for routing and navigation.
    It helps your characters find their way around.

    To populate a new map, create a subclass of MapBuilder.
    Give the new class an attribute called ``spots``.
    This must be a dictionary suitable for the constructor of an
    `enum.Enum <https://docs.python.org/3/library/enum.html#module-enum>`_.

    Override the `build` method of your class.
    This method generates :py:class:`~balladeer.lite.compass.Transit` objects.

    Internally the map object will derive four state types from the spot
    data you supplied to it:

    Spot
        This state represents an absolute position, eg: ``map.spot.kitchen``.
    Into
        This state represents motion towards the position, eg: ``map.into.kitchen``.
    Exit
        This state represents motion away from the position, eg: ``map.exit.kitchen``.
    Home
        This state represents an affinity to the position, eg: ``map.home.kitchen``.

    These states are available for use with transits and other entities.

    .. literalinclude:: ../lite/test/test_compass.py
       :pyobject: MapTests.Map
       :dedent: 4

    """
    def __init__(self, spots: dict, config=None):
        self.config = config
        global Into, Home, Spot, Exit
        self.into = Into = enum.Enum("Into", spots, type=State)
        self.home = Home = enum.Enum("Home", spots, type=State)
        self.spot = Spot = enum.Enum("Spot", spots, type=State)
        self.exit = Exit = enum.Enum("Exit", spots, type=State)
        self.transits = list(self.make())
        self.routes = {}

    @property
    def topology(self):
        for t in self.transits:
            d = t.get_state(self.exit)
            a = t.get_state(self.into)
            v = t.get_state(Traffic)
            c = t.get_state(Compass)
            b = c and c.back
            if v in (Traffic.flowing, Traffic.forward):
                yield d, c, t, a
            if v in (Traffic.flowing, Traffic.reverse):
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
