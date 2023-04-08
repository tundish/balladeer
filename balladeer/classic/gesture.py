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

from collections import ChainMap
from collections import namedtuple
import random

from turberfield.dialogue.types import DataObject
from turberfield.dialogue.types import Stateful

from balladeer.classic.types import Fruition


Head = namedtuple(
    "Head",
    ("propose", "confirm", "counter", "abandon", "condemn", "declare"),
    defaults=(tuple(), tuple(), tuple(), tuple(), tuple(), tuple()),
)


Hand = namedtuple(
    "Hand",
    ("decline", "suggest", "promise", "disavow", "deliver"),
    defaults=(tuple(), tuple(), tuple(), tuple(), tuple()),
)


class ChainStore:
    def __init__(self, *args, **kwargs):
        object.__setattr__(self, "_chain", ChainMap(kwargs, *args))

    def __getattr__(self, name):
        try:
            return self._chain[name]
        except KeyError:
            raise AttributeError(f"No mapping in chain has key '{name}'")

    def __setattr__(self, name, value):
        if name in set(Head._fields).union(set(Hand._fields)):
            self._chain[name] = value
        else:
            object.__setattr__(self, name, value)


class Gesture(Stateful, ChainStore):
    def __init__(self, label, head=None, hand=None, **kwargs):
        head = head or Head()
        hand = hand or Hand()
        super().__init__(head._asdict(), hand._asdict(), **kwargs)
        self.label = label

    @property
    def hand(self):
        return Hand(**self._chain.maps[2])

    @property
    def head(self):
        return Head(**self._chain.maps[1])

    @property
    def failed(self):
        return self.get_state(Fruition).value in (7, 8, 9)

    @property
    def passed(self):
        return self.get_state(Fruition) == Fruition.completion

    @property
    def transitions(self):
        if self.get_state(Fruition) == Fruition.inception:
            return [(self.propose, Fruition.elaboration)]
        elif self.get_state(Fruition) == Fruition.elaboration:
            return [
                (self.promise, Fruition.construction),
                (self.suggest, Fruition.discussion),
                (self.decline, Fruition.withdrawn),
                (self.abandon, Fruition.withdrawn),
            ]
        elif self.get_state(Fruition) == Fruition.construction:
            return [
                (self.abandon, Fruition.cancelled),
                (self.deliver, Fruition.transition),
                (self.disavow, Fruition.defaulted),
            ]
        elif self.get_state(Fruition) == Fruition.transition:
            return [
                (self.abandon, Fruition.cancelled),
                (self.condemn, Fruition.construction),
                (self.declare, Fruition.completion),
            ]
        elif self.get_state(Fruition) == Fruition.discussion:
            return [
                (self.promise, Fruition.construction),
                (self.confirm, Fruition.construction),
                (self.counter, Fruition.elaboration),
                (self.abandon, Fruition.withdrawn),
                (self.decline, Fruition.withdrawn),
            ]
        else:
            return []

    def __call__(self, strategy=None, **kwargs):
        strategy = strategy or random.choice
        event, state = strategy(self.transitions)
        return self, event, state

    def __str__(self):
        return self.label
