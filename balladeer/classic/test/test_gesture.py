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

from balladeer.classic.gesture import Gesture
from balladeer.classic.gesture import Hand
from balladeer.classic.gesture import Head
from balladeer.classic.speech import Phrase
from balladeer.classic.speech import Name
from balladeer.classic.speech import Verb
from balladeer.classic.types import Fruition


class Brew(Gesture):
    @staticmethod
    def create_mugs(a, b):
        return Gesture(
            "mugs",
            a=a,
            b=b,
            head=Head(
                propose=["Can you get the mugs for me?"],
                confirm=["OK, fine."],
                counter=["Don't worry, I'll do it."],
                abandon=["Oh, never mind."],
                condemn=["There's a crack in that one.", "That needs a wash."],
                declare=["Right then."],
            ),
            # TODO: Add abandon
            hand=Hand(
                decline=["I can't right now."],
                suggest=["I will in a minute."],
                promise=["Sure."],
                disavow=["I though you were doing it."],
                deliver=["There they are."],
            ),
        ).set_state(Fruition.inception)

    @staticmethod
    def strategy(options):
        return random.choice(
            [
                (e, s)
                for e, s in options
                if s not in (Fruition.cancelled, Fruition.defaulted, Fruition.withdrawn)
            ]
        )

    def __init__(self, *args, mugs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.mugs = mugs or self.create_mugs(
            a=getattr(self, "b", None), b=getattr(self, "a", None)
        )

    def __call__(self, strategy=None, **kwargs):
        if self.mugs.failed:
            self.mugs = self.create_mugs(a=getattr(self, "b", None), b=getattr(self, "a", None))

        if self.get_state(Fruition) == Fruition.construction and not self.mugs.passed:
            g, e, s = self.mugs(strategy=self.strategy)
            if e == self.mugs.hand.suggest:
                self.mugs.b = self.mugs.a
            return g, e, s

        return super().__call__(strategy, **kwargs)


class GestureTests(unittest.TestCase):
    @staticmethod
    def create_brew():
        return Brew(
            "brew",
            a="Louise",
            b="Sophie",
            head=Head(
                propose=["Stick the kettle on, would you?"],
                confirm=["Whatever, fine."],
                counter=["I'll have tea, please."],
                abandon=["Actually, forget it; I've got to go."],
                condemn=["You've left the bag in."],
                declare=["Thanks."],
            ),
            hand=Hand(
                decline=["No time now, sorry."],
                suggest=["Coffee?"],
                promise=["OK then."],
                disavow=["I'll be back in a minute. Carry on without me."],
                deliver=["There you go."],
            ),
        ).set_state(Fruition.inception)

    def test_head(self):
        a = Head()
        b = Head()
        self.assertFalse(a.propose)
        self.assertFalse(b.propose)
        self.assertIs(a.propose, b.propose)  # Lest we forget

    def test_simple(self):
        g = Gesture(
            "simple",
            head=Head(
                [
                    Phrase(Verb("make"), Name("tea")),
                    Phrase(Verb("make"), Name("brew")),
                ]
            ),
        )
        self.assertEqual("simple", str(g))
        self.assertEqual("make", g.head.propose[0].verb.imperative)
        self.assertEqual("tea", g.head.propose[0].name.noun)

    def test_simple(self):
        g = Gesture(
            "simple",
            head=Head(
                [
                    Phrase(Verb("make"), Name("tea")),
                    Phrase(Verb("make"), Name("brew")),
                ]
            ),
        )
        g.propose = "Fancy a brew?"
        self.assertEqual("Fancy a brew?", g.propose)
        self.assertEqual("make", g.head.propose[0].verb.imperative)
        self.assertEqual("tea", g.head.propose[0].name.noun)
        g.decline = "I've just had one, thanks"
        self.assertEqual("I've just had one, thanks", g.decline)
        self.assertFalse(g.hand.decline)

    def test_attribute_access(self):
        g = Gesture("blank")
        self.assertRaises(AttributeError, getattr, g, "new_attribute")

        self.assertFalse(g.propose)
        self.assertFalse(g.decline)
        g.new_attribute = True
        self.assertTrue(g.new_attribute)

    def test_brew(self):
        brew = self.create_brew()
        while not (brew.passed or brew.failed):
            gesture, event, state = brew()
            gesture.state = state


if __name__ == "__main__":
    """
    Louise : Stick the kettle on, would you?
    Sophie : Coffee?
    Sophie : OK then.
    Sophie : Can you get the mugs for me?
    Louise : Sure.
    Louise : There they are.
    Sophie : There's a crack in that one.
    Louise : There they are.
    Sophie : Right then.
    Sophie : There you go.
    Louise : You've left the bag in.
    Sophie : I'll be back in a minute. Carry on without me.
    """
    brew = GestureTests.create_brew()

    while not (brew.passed or brew.failed):
        gesture, event, state = brew()
        gesture.state = state

        if event in brew.head:
            actor = brew.a
        elif event in brew.hand:
            actor = brew.b
        elif event in brew.mugs.head:
            actor = brew.mugs.a
        elif event in brew.mugs.hand:
            actor = brew.mugs.b

        print(actor, ":", random.choice(event))
