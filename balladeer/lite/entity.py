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


@dataclasses.dataclass(unsafe_hash=True)
class Entity:

    name: dataclasses.InitVar = ""
    names: list = dataclasses.field(default_factory=list, compare=False)
    type: str = None
    states: dict = dataclasses.field(default_factory=dict, compare=False)

    def __post_init__(self, name):
        if name:
            self.names.insert(0, name)

    @property
    def name(self):
        return random.choice(self.names or [self.name])

    @property
    def state(self):
        return self.get_state()

    @state.setter
    def state(self, value):
        return self.set_state(value)

    def set_state(self, *args):
        for arg in args:
            if isinstance(arg, str):
                key, value = arg.rsplit(".")
                self.states[key] = value
            else:
                self.states[type(arg).__name__] = arg
        return self

    def get_state(self, typ: [type | str]=int, default=0):
        if isinstance(typ, str):
            return self.states.get(typ, default)
        else:
            return self.states.get(typ.__name__, default)

    def compare(self, key: str, pattern: [str, re.Pattern]):
        pass

