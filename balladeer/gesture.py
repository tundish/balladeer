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

from collections import namedtuple

from turberfield.dialogue.types import DataObject
from turberfield.dialogue.types import Stateful


Head = namedtuple(
    "Head",
    ("request", "indefinite"),
    defaults=([], [])
)


class Gesture(DataObject, Stateful):

    # def __init__(
    #     self, request=None, counter=None, promise=None, deliver=None, abandon=None, message=None, **kwargs
    # ):
    def __str__(self):
        return "\n".join("{0.verb.imperative} {0.name.noun}".format(i) for i in self.phrases)

