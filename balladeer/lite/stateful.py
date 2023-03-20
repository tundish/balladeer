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

from collections import namedtuple
import enum
from numbers import Number
import random
import uuid

from turberfield.utils.assembly import Assembly

Name = namedtuple("Name", ["title", "firstname", "nicknames", "surname"])

class EnumFactory:

    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]


class DataObject:

    def __init__(self, *args, id=None, **kwargs):
        super().__init__(*args)
        self.id = id or uuid.uuid4()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return "<{0}> {1}".format(type(self).__name__, vars(self))


class Stateful:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = {}

    @property
    def state(self):
        return self.get_state()

    @property
    def states(self):
        return self._states.copy()

    @state.setter
    def state(self, value):
        return self.set_state(value)

    def set_state(self, *args):
        for value in args:
            self._states[type(value).__name__] = value
        return self

    def get_state(self, typ=int, default=0):
        return self._states.get(typ.__name__, default)


Assembly.register(type(uuid.uuid4()))
