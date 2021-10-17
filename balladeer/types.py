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
from turberfield.dialogue.types import DataObject


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


class World:

    def __init__(self, *args, **kwargs):
        self.lookup = Grouping(list)
        for item in self.build():
            self.add(item)

    def add(self, item):
        for name in str(item).splitlines():
            self.lookup[name.strip().lower()].append(item)

    def remove(self, item):
        for name in str(item).splitlines():
            try:
                self.lookup[name.strip().lower()].remove(item)
            except ValueError:
                pass
