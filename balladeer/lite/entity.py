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

import dataclasses
import enum
import random
import re
import uuid

from balladeer.lite.speech import Speech
from balladeer.lite.types import State


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class Entity:
    name: dataclasses.InitVar = ""
    names: list = dataclasses.field(default_factory=list, compare=False)

    type: dataclasses.InitVar = ""
    types: set = dataclasses.field(default_factory=set, compare=False)

    states: dict = dataclasses.field(default_factory=dict, compare=False)
    uid: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)

    sketch: Speech = dataclasses.field(default_factory=Speech, compare=False)
    aspect: Speech = dataclasses.field(default_factory=Speech, compare=False)

    def __post_init__(self, name, type):
        if not isinstance(name, property):
            self.names.insert(0, name)
        if type:
            try:
                self.types.add(type.__name__)
            except AttributeError:
                self.types.add(type)

    def __eq__(self, other):
        if not self.names:
            return self.uid == other.uid

        try:
            return set(self.names).union(self.types) == set(other.names).union(other.types)
        except AttributeError:
            return False

    @property
    def name(self):
        return random.choice(self.names or [""])

    @property
    def state(self):
        return self.get_state()

    @state.setter
    def state(self, value):
        return self.set_state(value)

    def set_state(self, *args):
        for arg in args:
            self.states[type(arg).__name__] = arg
        return self

    def get_state(self, typ: State = int):
        try:
            return self.states.get(typ.__name__)
        except AttributeError:
            return self.states.get(typ)
        else:
            return None
