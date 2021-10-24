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
import random

from turberfield.dialogue.types import DataObject
from turberfield.dialogue.types import Stateful

from balladeer.types import Fruition


Head = namedtuple(
    "Head",
    ("propose", "confirm", "counter", "abandon", "decline", "declare"),
    defaults=(tuple(), tuple(), tuple(), tuple(), tuple(), tuple())
)


Hand = namedtuple(
    "Hand",
    ("decline", "promise", "counter", "deliver"),
    defaults=(tuple(), tuple(), tuple(), tuple())
)


class Gesture(DataObject, Stateful):

    def __init__(self, label, head=None, hand=None, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.head = head or Head()
        self.hand = hand or Hand()

    @property
    def failed(self):
        return self.get_state(Fruition).value in (7, 8, 9)

    @property
    def passed(self):
        return self.get_state(Fruition) == Fruition.completion

    @property
    def transitions(self):
        if self.get_state(Fruition) == Fruition.inception:
            return [
                (self.head.propose, Fruition.elaboration)
            ]
        elif self.get_state(Fruition) == Fruition.elaboration:
            return [
                (self.hand.promise, Fruition.construction),
                (self.hand.counter, Fruition.discussion),
                (self.hand.decline, Fruition.withdrawn),
                (self.head.abandon, Fruition.withdrawn),
            ]
        elif self.get_state(Fruition) == Fruition.construction:
            return [
                (self.head.abandon, Fruition.cancelled),
                (self.hand.deliver, Fruition.transition),
                (self.hand.decline, Fruition.defaulted),
            ]
        elif self.get_state(Fruition) == Fruition.transition:
            return [
                (self.head.abandon, Fruition.cancelled),
                (self.head.decline, Fruition.construction),
                (self.head.declare, Fruition.completion),
            ]
        elif self.get_state(Fruition) == Fruition.discussion:
            return [
                (self.hand.promise, Fruition.construction),
                (self.head.confirm, Fruition.construction),
                (self.head.counter, Fruition.elaboration),
                (self.head.abandon, Fruition.withdrawn),
                (self.hand.decline, Fruition.withdrawn),
            ]
        else:
            return []

    def __call__(self, strategy=None, **kwargs):
        strategy = strategy or random.choice
        event, state = strategy(self.transitions)
        return self, event, state

    def __str__(self):
        return self.label

