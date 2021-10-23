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

import random
import unittest

from balladeer import Fruition
from balladeer import Gesture
from balladeer import Hand
from balladeer import Head
from balladeer import Phrase
from balladeer import Name
from balladeer import Verb


class GestureTests(unittest.TestCase):

    def test_head(self):
        a = Head()
        b = Head()
        self.assertFalse(a.propose)
        self.assertFalse(b.propose)
        self.assertIs(a.propose, b.propose)  # Lest we forget

    def test_simple(self):
        g = Gesture("simple", head=Head([
            Phrase(Verb("make"), Name("tea")),
            Phrase(Verb("make"), Name("brew")),
        ]))
        self.assertIn("make tea", str(g))
        self.assertIn("\n", str(g))
        self.assertIn("make brew", str(g))

def transitions(gesture):
    if gesture.get_state(Fruition) == Fruition.inception:
        return [
            (gesture.head.propose, Fruition.elaboration)
        ]
    elif gesture.get_state(Fruition) == Fruition.elaboration:
        return [
            (gesture.hand.promise, Fruition.construction),
            (gesture.hand.counter, Fruition.discussion),
            (gesture.hand.decline, Fruition.withdrawn),
            (gesture.head.abandon, Fruition.withdrawn),
        ]
    else:
        return []

if __name__ == "__main__":
    mugs = Gesture(
        "mugs",
        head=Head(
            propose=["Can you get the mugs for me?"],
            confirm=["OK, fine."],
            counter=["Don't worry, I'll do it."],
            abandon=["Oh, there are some right here."],
            decline=["There's a crack in that one."],
            declare=["Ta."],
        ),
        hand=Hand(
            decline=["I can't right now."],
            promise=["Sure."],
            counter=["I will in a minute."],
            deliver=["There they are."],
        ),
    ).set_state(Fruition.inception)

    brew = Gesture(
        "brew",
        head=Head(
        ),
        hand=Hand(
        ),
    ).set_state(Fruition.inception)

    state = None
    while state not in (Fruition.cancelled,):
        event, state = random.choice(transitions(mugs))
        print(random.choice(event))
        mugs.state = state
