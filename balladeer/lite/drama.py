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


from collections import deque

from balladeer.lite.entity import Entity
from balladeer.lite.loader import Loader
from balladeer.lite.performance import Performance


class Drama(Performance, Entity):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop("config", None)
        self.world = kwargs.pop("world", None)
        self.speech = deque(args) or list()
        self.prompt = ""
        self.tooltip = "Enter a command, or type 'help' for a list of options."
        self.prefixes = ("do_", "on_")
        super().__init__(**kwargs)

    @property
    def ensemble(self):
        return self.world.entities + [self]

    def scripts(self, assets):
        return [i for i in assets if isinstance(i, Loader.Scene)]

    def media(self, assets):
        return {i.path: i for i in assets if isinstance(i, Loader.Asset)}

    def interlude(self, *args, **kwargs) -> Entity:
        return self
