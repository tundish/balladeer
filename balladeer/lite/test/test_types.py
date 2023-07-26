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

import enum
import unittest

from balladeer.lite.compass import Traffic
from balladeer.lite.compass import Transit
from balladeer.lite.entity import Entity
from balladeer.lite.loader import Loader
from balladeer.lite.types import Grouping
from balladeer.lite.types import Page
from balladeer.lite.types import State


class GroupingTests(unittest.TestCase):
    def test_grouping_by_class(self):
        class A:
            pass

        class B:
            pass

        g = Grouping.typewise([A(), B(), A()])
        self.assertIn(A, g)
        self.assertEqual(2, len(g[A]))

        self.assertIn(B, g)
        self.assertEqual(1, len(g[B]))
        self.assertEqual(3, len(g.all))
        self.assertEqual(3, len(g.each))

    def test_grouping_by_type(self):
        types = ("audio/mpeg", "text/css", "text/javascript")
        items = [
            Loader.Asset(unittest, "data/slapwhack.mp4", type=types[0]),
            Loader.Asset(unittest, "styles/style.css", type=types[1]),
            Loader.Asset(unittest, "picker.js", type=types[2]),
        ]
        g = Grouping.typewise(items)

        for t in types:
            with self.subTest(t=t):
                self.assertIn(t, g)
                self.assertEqual(1, len(g[t]))
                self.assertIsInstance(g[t][0], Loader.Asset)

    def test_grouping_via_types(self):
        items = [
            Entity(type="A"),
            Entity(type="B"),
            Entity(type="A"),
        ]

        g = Grouping.typewise(items)

        self.assertIn(Entity, g)
        self.assertEqual(3, len(g[Entity]))

        self.assertIn("A", g)
        self.assertEqual(2, len(g["A"]))

        self.assertIn("B", g)
        self.assertEqual(1, len(g["B"]))

        self.assertEqual(6, len(g.all))
        self.assertEqual(3, len(g.each))

    def test_grouping_by_multiple_type(self):
        items = [
            Entity(type="A"),
            Entity(types={"A", "B"}),
        ]

        g = Grouping.typewise(items)

        self.assertIn(Entity, g)
        self.assertEqual(2, len(g[Entity]))

        self.assertIn("A", g)
        self.assertEqual(2, len(g["A"]))

        self.assertIn("B", g)
        self.assertEqual(1, len(g["B"]))

        self.assertEqual(5, len(g.all), g.all)
        self.assertEqual(2, len(g.each))


class StateTests(unittest.TestCase):
    class SingleValue(State, enum.Enum):
        A = "Ah"
        B = "Ba"
        C = "Co"

    class MultiValue(State, enum.Enum):
        A = ["ah", "Ah"]
        B = ["ba", "Ba"]
        C = ["co", "Co"]

    class Politics(State, enum.Enum):
        con = ["Conservative", "Tory"]
        dem = ["Liberal Democrat", "LibDem"]
        grn = ["Green Party", "Green"]
        ind = ["Independent"]
        lab = ["Labour", "New Labour"]
        lib = ["Liberal"]
        ref = ["Reform Party"]
        res = ["Residents' Party"]
        ukp = ["UKIP", "UK Independence Party"]

    def test_labels(self):
        s = StateTests.SingleValue.B
        self.assertEqual("Ba", s.label)

        m = StateTests.MultiValue.B
        self.assertEqual("ba", m.label)

    def test_politics(self):
        s = StateTests.Politics.ukp
        self.assertEqual("UKIP", s.label)


class TransitExample(unittest.TestCase):
    def test_named_transit(self):
        transit = Transit(
            names=["Door", "Wooden Door"],
            type="Door",
            aspect="locked",
            sketch="A {0.name}. It seems to be {aspect}.",
        ).set_state(Traffic.blocked)
        self.assertIn(
            transit.description,
            (
                "A Door. It seems to be locked.",
                "A Wooden Door. It seems to be locked.",
            )
        )

        transit.set_state(Traffic.flowing).aspect, transit.revert = "open", transit.aspect
        self.assertIn(
            transit.description,
            (
                "A Door. It seems to be open.",
                "A Wooden Door. It seems to be open.",
            )
        )
        self.assertEqual("locked", transit.revert)


class PageTests(unittest.TestCase):

    def test_creation(self):
        page = Page()
        self.assertEqual(page.zone.body, page.cursor)

    def test_paste(self):
        page = Page()
        self.assertEqual(2, len(page.structure[page.zone.body]))
        page.paste("<p>One upon a time...</p>")
        self.assertEqual(3, len(page.structure[page.zone.body]))

    def test_paste_zone(self):
        page = Page()
        self.assertFalse(page.structure[page.zone.title])
        page.paste("<title>Zone test</title>", zone=page.zone.title)
        self.assertTrue(page.structure[page.zone.title])


class ColourTests(unittest.TestCase):

    def test_zero_red(self):
        for text in (
            "hsl(0 100% 50%)",
            "hsl(0, 100%, 50%)",
        ):
            with self.subTest(text=text):
                rgba = Page.css_rgba(text)
                self.assertEqual([255, 0, 0, 1], rgba)

    def test_full_red(self):
        for text in (
            "hsl(360 100% 50%)",
            "hsl(360, 100%, 50%)"
        ):
            with self.subTest(text=text):
                rgba = Page.css_rgba(text)
                self.assertEqual([255, 0, 0, 1], rgba)

    def test_rgb_to_rgba(self):
        for text in (
            "rgb(128 64 32)",
            "rgb(128, 64, 32)"
        ):
            with self.subTest(text=text):
                rgba = Page.css_rgba(text)
                self.assertEqual([128, 64, 32, 1], rgba)
