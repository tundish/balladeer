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
import random
import uuid

from turberfield.utils.assembly import Assembly

Name = namedtuple("Name", ["title", "firstname", "nicknames", "surname"])

class EnumFactory:

    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]

@enum.unique
class Ownership(EnumFactory, enum.Enum):
    lost = 0
    acquired = 1

@enum.unique
class Presence(EnumFactory, enum.Enum):
    invisible = 0
    visible = 1
    shine = 2
    fade = 3
    throb = 4

@enum.unique
class Vocabulary(EnumFactory, enum.Enum):
    forgot = 0
    prompted = 1

class DataObject:

    def __init__(self, *args, id=None, **kwargs):
        super().__init__(*args)
        self.id = id or uuid.uuid4()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return "<{0}> {1}".format(type(self).__name__, vars(self))


class Persona(DataObject):

    def __init__(self, *args, **kwargs):
        self._name = kwargs.pop("name", None)
        super().__init__(*args, **kwargs)

        try:
            bits = self._name.split()
            self.name = Name(bits[0], bits[1], bits[2:-1], bits[-1])
        except AttributeError:
            # self._name not a string, assume a Name
            self.name = self._name
        except IndexError:
            self.name = Name("", self._name, [], "")


    @property
    def nickname(self):
        return random.choice(self.name.nicknames)


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

class Player(Persona, Stateful):
    pass

Assembly.register(Name, type(uuid.uuid4()))
