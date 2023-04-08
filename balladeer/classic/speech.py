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


Article = namedtuple("Article", ("definite", "indefinite"), defaults=("the", "a"))


Pronoun = namedtuple(
    "Pronoun",
    ("subject", "object", "reflexive", "genitive"),
    defaults=("it", "it", "itself", "its"),
)


Name = namedtuple("Name", ("noun", "article", "pronoun"), defaults=("", Article(), Pronoun()))


Tensed = namedtuple("Tensed", ("simple", "progressive", "perfect", "imperative"))


class Verb(Tensed):
    def __new__(
        cls, root, simple="{0}s", progressive="is {0}ing", perfect="{0}ed", imperative="{0}"
    ):
        l = locals()
        return super().__new__(cls, *(l[i].format(root) for i in super()._fields))


Phrase = namedtuple("Phrase", ("verb", "name"))
