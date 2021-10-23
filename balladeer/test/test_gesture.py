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

if __name__ == "__main__":
    a = "Louise"
    b = "Sophie"
    mugs = Gesture(
        "mugs",
        a=a, b=b,
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
            propose=["Stick the kettle on, would you?"],
            confirm=["OK, fine."],
            counter=["I'll have tea, please."],
            abandon=["Actually, don't worry; I've got to go."],
            decline=["You've left the bag in."],
            declare=["Thanks."],
        ),
        hand=Hand(
            decline=["Sorry, not right now."],
            promise=["OK."],
            counter=["Tea or coffee?"],
            deliver=["There you go."],
        ),
    ).set_state(Fruition.inception)

    state = mugs.get_state(Fruition)
    while state.value not in (5, 7, 8, 9):
        event, state = random.choice(mugs.transitions)
        actor = mugs.a if event in mugs.head else mugs.b
        print(actor, ":", random.choice(event))
        mugs.state = state
        if event == mugs.hand.counter:
            mugs.b = mugs.a   # Mugs-specific, not brew
        #TODO: gesture, event, state = brew(policy=random.choice)
        # if gesture.complete:
        #     self.lookup[gesture.label].discard(gesture)
        # else:
        #     self.lookup[gesture.label].add(gesture)
