#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2022 D E Haynes

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
from collections import namedtuple
import importlib.resources
import inspect
import pprint
import tomllib
import uuid

import markdown

# from turberfield.utils.assembly import Assembly


# turberfield.utils.misc
def group_by_type(items):
    rv = defaultdict(list)
    for i in items:
        rv[type(i)].append(i)
    return rv


# turberfield.dialogue.types
class EnumFactory:

    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]


# turberfield.dialogue.types
class DataObject:

    def __init__(self, *args, id=None, **kwargs):
        super().__init__(*args)
        self.id = id or uuid.uuid4()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return "<{0}> {1}".format(type(self).__name__, vars(self))


# turberfield.dialogue.types
class Stateful:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = {}

    @property
    def state(self):
        return self.get_state()

    @state.setter
    def state(self, value):
        return self.set_state(value)

    def set_state(self, *args):
        for value in args:
            self._states[type(value).__name__] = value
        return self

    def get_state(self, typ=int, default=0):
        return self._states.get(typ.__name__, default)


class Thing(DataObject, Stateful): pass

