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

from collections import defaultdict
import enum
import random

from turberfield.dialogue.types import DataObject
from turberfield.dialogue.types import EnumFactory
from turberfield.utils.misc import group_by_type

from balladeer.classic.speech import Name


class Fruition(EnumFactory, enum.Enum):
    inception = 1
    elaboration = 2
    construction = 3
    transition = 4
    completion = 5
    discussion = 6
    defaulted = 7
    withdrawn = 8
    cancelled = 9


class Grouping(defaultdict):
    @property
    def all(self):
        return [i for s in self.values() for i in s]

    @property
    def each(self):
        return list(set(self.all))


class Named(DataObject):
    @property
    def name(self):
        name = random.choice(getattr(self, "names", [Name()]))
        article = name.article.definite and f"{name.article.definite} "
        return f"{article}{name.noun}"

    def __str__(self):
        return "\n".join(i.noun for i in self.names)


class Operation(enum.Enum):
    begins = enum.auto()
    frames = enum.auto()
    paused = enum.auto()
    prompt = enum.auto()
    ending = enum.auto()
    finish = enum.auto()


class World:
    def __init__(self, *args, **kwargs):
        self.lookup = Grouping(list)
        for item in self.build():
            self.add(item)

    @staticmethod
    def arrange(items):
        return group_by_type(items)

    def add(self, item):
        for name in str(item).splitlines():
            self.lookup[name.strip().lower()].append(item)

    def remove(self, item):
        for name in str(item).splitlines():
            try:
                self.lookup[name.strip().lower()].remove(item)
            except ValueError:
                pass
