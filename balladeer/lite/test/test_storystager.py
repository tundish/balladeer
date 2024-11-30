#!/usr/bin/env python
# encoding: utf8

# Copyright 2024 D E Haynes

# This file is part of balladeer.
#
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

import copy
import enum
import textwrap
import unittest

import balladeer
from balladeer import Compass
from balladeer import discover_assets
from balladeer import Detail
from balladeer import Drama
from balladeer import Entity
from balladeer import Fruition
from balladeer import Grouping
from balladeer import Loader
from balladeer import Resident
from balladeer import StoryStager
from balladeer import Stager
from balladeer import Traffic
from balladeer import Transit

import busker
from busker.test.test_stager import StagerTests


class StoryTests(unittest.TestCase):

    class TestStory(StoryStager):
        types = [Drama, Entity, Resident, Transit]

    def setUp(self):
        assets = discover_assets(busker, "test", ignore=[])
        self.assertTrue(assets[Loader.Staging])
        self.story = self.TestStory(assets=assets)

    def test_make(self):
        self.assertIsInstance(getattr(self.story, "stager"), Stager)
        self.assertTrue(self.story.stager.realms)
        self.assertTrue(self.story.stager.active)

        self.assertTrue(issubclass(self.story.world.map.spot, enum.Enum))

        self.assertTrue(self.story.world.map.transits)
        self.assertFalse(
            any(len(i.names) > 1 for i in self.story.world.map.transits),
            self.story.world.map.transits
        )
        self.assertEqual(len([i for i in self.story.world.map.transits if i.get_state(Traffic)]), 9)
        self.assertEqual(len([i for i in self.story.world.map.transits if i.get_state(Compass)]), 8)
        self.assertGreater(len(self.story.world.map.spot), 1, list(self.story.world.map.spot))

        self.assertFalse(
            any(i.get_state(Traffic) for i in self.story.context.ensemble),
            self.story.context.ensemble
        )

    def test_story_copy_drama(self):
        b = copy.deepcopy(self.story)
        self.assertNotEqual(self.story.uid, b.uid, vars(self.story))
        self.assertIsNot(self.story.director, b.director, vars(self.story.director))

        self.assertTrue(self.story.drama)
        self.assertTrue(self.story.context)

        witness = []
        for drama in self.story.drama.values():
            self.assertEqual(sorted(set(drama.names)), sorted(drama.names), drama.names)
            with self.subTest(a=self.story, b=b, drama=drama):
                self.assertNotIn(
                    id(drama), [id(i) for i in b.drama.values()],
                    b.drama
                )
                witness.append(drama)

        self.assertTrue(witness)

    def test_story_copy_map(self):
        a = copy.deepcopy(self.story)
        b = copy.deepcopy(self.story)

        self.assertEqual(list(a.drama), list(b.drama))

        for entity in a.world.entities:
            with self.subTest(a=a, b=b, entity=entity):
                self.assertFalse(any(entity.names is i.names for i in b.world.entities), entity.names)
                self.assertFalse(any(entity.states is i.states for i in b.world.entities))
                self.assertFalse(any(entity.types is i.types for i in b.world.entities))

        self.assertTrue(a.world.map)
        self.assertTrue(b.world.map)

        self.assertIsNot(a.world, b.world)
        self.assertIsNot(a.world.map, b.world.map)

        self.assertGreater(len(a.world.map.spot), 1, list(a.world.map.spot))

        self.assertIsNot(a.world.map.spot, b.world.map.spot)
        self.assertEqual([str(i) for i in a.world.map.spot], [str(i) for i in b.world.map.spot])

        self.assertIsNot(a.world.map.exit, b.world.map.exit)
        self.assertEqual([str(i) for i in a.world.map.exit], [str(i) for i in b.world.map.exit])

        self.assertIsNot(a.world.map.into, b.world.map.into)
        self.assertEqual([str(i) for i in a.world.map.into], [str(i) for i in b.world.map.into])

        self.assertIsNot(a.world.map.home, b.world.map.home)
        self.assertEqual([str(i) for i in a.world.map.home], [str(i) for i in b.world.map.home])

        self.assertTrue(a.world.map.transits)
        self.assertTrue(b.world.map.transits, a.world.map.transits)
        for transit in a.world.map.transits:
            with self.subTest(a=a, b=b, transit=transit):
                self.assertFalse(any(transit.names is i.names for i in b.world.map.transits), transit.names)
                self.assertFalse(any(transit.states is i.states for i in b.world.map.transits))
                self.assertFalse(any(transit.types is i.types for i in b.world.map.transits))

    def test_story_copy_stager(self):
        s = copy.deepcopy(self.story)
        self.assertTrue(s.stager)
        self.assertEqual(len(self.story.stager.strands), len(s.stager.strands))
        for a in self.story.stager.strands.values():
            for b in s.stager.strands.values():
                with self.subTest(a=a, b=b):
                    self.assertIsNot(a, b)

    def test_monitor_context(self):
        text = textwrap.dedent("""
            label = "Events test"
            realm = "test_monitor_context"

            [[puzzles]]
            name = "a"

            [puzzles.init]
            Fruition = "inception"

            [puzzles.state.spot]
            drive = ["Drive"]
            patio = ["Patio"]

            [[puzzles.items]]
            type = "Transit"
            states = ["exit.drive", "into.patio", "Traffic.flowing"]

            [[puzzles.items]]
            names = ["Player", "me"]
            type = "Focus"
            states = ["spot.drive"]

            [puzzles.chain.construction]
            "b" = "Fruition.inception"

            [[puzzles.events]]
            trigger = "Fruition.evaluation"
            targets = ["Deckchair"]
            payload = {state="detail.glow"}
            message = "Hint at use of deckchair: target by name"

            [[puzzles.events]]
            trigger = "Fruition.evaluation"
            targets = ["Furniture"]
            payload = {aspect = "a nice spot to rest"}
            message = "Hint at use of deckchair: target by type"

            [[puzzles]]
            name = "b"

            [[puzzles.items]]
            names = ["Deckchair", "Chair"]
            type = "Furniture"
            states = ["spot.patio", "detail.none"]
            sketch = "a striped deckchair, looks like {aspect}"
            aspect = "it doesn't get much use"

        """)
        data = next(Stager.load(text))
        stage = Loader.Staging(text, data)
        assets = Grouping.typewise([stage])
        story = self.TestStory(assets=assets)
        self.assertIn(("test_monitor_context", "a"), story.drama)
        self.assertIn(("test_monitor_context", "b"), story.drama)
        self.assertIsInstance(story.context, Resident)

        a = story.drama[("test_monitor_context", "a")]
        b = story.drama[("test_monitor_context", "b")]
        c = story.world.typewise["Furniture"][0]

        # First checks on initialization
        self.assertEqual(a.get_state(Fruition), Fruition.inception)
        self.assertEqual(b.get_state(Fruition), None)
        self.assertEqual(c.get_state(Detail), Detail.none)
        self.assertEqual(c.description, "a striped deckchair, looks like it doesn't get much use")

        story.monitor_context("test_monitor_context", "a", story.context)
        self.assertEqual(a.get_state(Fruition), Fruition.inception)
        self.assertEqual(b.get_state(Fruition), None)
        self.assertEqual(c.get_state(Detail), Detail.none)
        self.assertEqual(c.description, "a striped deckchair, looks like it doesn't get much use")

        story.monitor_context("test_monitor_context", "b", story.context)
        self.assertEqual(a.get_state(Fruition), Fruition.inception)
        self.assertEqual(b.get_state(Fruition), None)
        self.assertEqual(c.get_state(Detail), Detail.none)
        self.assertEqual(c.description, "a striped deckchair, looks like it doesn't get much use")

        # Progress puzzle a but no chain yet
        a.set_state(Fruition.elaboration)
        story.monitor_context("test_monitor_context", "a", story.context)

        self.assertEqual(a.get_state(Fruition), Fruition.elaboration)
        self.assertEqual(b.get_state(Fruition), None)
        self.assertEqual(c.get_state(Detail), Detail.none)
        self.assertEqual(c.description, "a striped deckchair, looks like it doesn't get much use")

        story.monitor_context("test_monitor_context", "b", story.context)
        self.assertEqual(a.get_state(Fruition), Fruition.elaboration)
        self.assertEqual(b.get_state(Fruition), None)
        self.assertEqual(c.get_state(Detail), Detail.none)
        self.assertEqual(c.description, "a striped deckchair, looks like it doesn't get much use")

        # Progress puzzle to activate chain
        a.set_state(Fruition.construction)
        story.monitor_context("test_monitor_context", "a", story.context)

        self.assertEqual(a.get_state(Fruition), Fruition.construction)
        self.assertEqual(b.get_state(Fruition), Fruition.inception)
        self.assertEqual(c.get_state(Detail), Detail.none)
        self.assertEqual(c.description, "a striped deckchair, looks like it doesn't get much use")

        story.monitor_context("test_monitor_context", "b", story.context)
        self.assertEqual(a.get_state(Fruition), Fruition.construction)
        self.assertEqual(b.get_state(Fruition), Fruition.inception)
        self.assertEqual(c.get_state(Detail), Detail.none)
        self.assertEqual(c.description, "a striped deckchair, looks like it doesn't get much use")

        # Progress puzzle to generate event
        a.set_state(Fruition.evaluation)
        story.monitor_context("test_monitor_context", "a", story.context)

        self.assertEqual(a.get_state(Fruition), Fruition.evaluation)
        self.assertEqual(b.get_state(Fruition), Fruition.inception)
        self.assertEqual(c.get_state(Detail), Detail.glow, c)
        self.assertEqual(c.description, "a striped deckchair, looks like a nice spot to rest")

        story.monitor_context("test_monitor_context", "b", story.context)
        self.assertEqual(a.get_state(Fruition), Fruition.evaluation)
        self.assertEqual(b.get_state(Fruition), Fruition.inception)
        self.assertEqual(c.get_state(Detail), Detail.glow)
        self.assertEqual(c.description, "a striped deckchair, looks like a nice spot to rest")

    def test_story_turn(self):
        assets = Grouping.typewise([
            stage
            for rule in StagerTests.rules
            if (stage := Loader.Staging(text=rule, data=next(Stager.load(rule)))).data["realm"] == "busker"
        ])
        self.assertEqual(len(assets[Loader.Staging]), 2)
        s = self.TestStory(assets=assets)
        for n, _ in enumerate(set(s.stager.puzzles)):
            d = s.context
            with self.subTest(n=n, d=d):
                if n == 0:
                    self.assertEqual(d.name, "a")
                    self.assertTrue(hasattr(d, "selector"), d)
                    self.assertIsInstance(d.selector, dict)
                    self.assertEqual(set(d.selector), {"states", "paths"})
                    self.assertEqual(d.selector["states"], set(["spot.kitchen", "spot.hall"]))
                    d.set_state(Fruition.completion)
                    s.turn()
                    continue

                self.assertEqual(d.get_state(Fruition), Fruition.inception, d)
                d.set_state(Fruition.completion)
                if n + 1 < len(set(s.stager.puzzles)):
                    s.turn()
