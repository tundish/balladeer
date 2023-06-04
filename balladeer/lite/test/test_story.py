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
import copy
import itertools
import textwrap
import tomllib
import unittest

from balladeer.examples.ex_10_animate_media.main import Story as Story_10
from balladeer.lite.loader import Loader
from balladeer.lite.speech import Dialogue
from balladeer.lite.story import StoryBuilder
from balladeer.lite.types import Grouping


class StoryTests(unittest.TestCase):
    def test_simple_turns(self):
        story = StoryBuilder(
            Dialogue("<> Knock, knock."),
            Dialogue("<> Who's there?"),
        )
        self.assertIsInstance(story.context.speech, deque)
        for n in range(3):
            with self.subTest(n=n), story.turn() as turn:
                if n < 2:
                    self.assertTrue(turn.blocks, turn)
                else:
                    self.assertFalse(turn.blocks, turn)

    def test_story_copy(self):
        a = StoryBuilder(
            Dialogue("<> Knock, knock."),
            Dialogue("<> Who's there?"),
        )
        b = copy.deepcopy(a)
        self.assertNotEqual(a.uid, b.uid, vars(a))
        self.assertNotEqual(a.director, b.director, vars(a.director))

        # Side effect: each drama generates its active set
        self.assertTrue([i.options([]) for i in a.drama])
        self.assertTrue([i.options([]) for i in b.drama])

        for drama in a.drama:
            with self.subTest(a=a, b=b, drama=drama):
                self.assertNotIn(drama, b.drama)
                self.assertFalse(
                    any(set(drama.active).intersection(set(i.active)) for i in b.drama)
                )

        for entity in a.world.entities:
            with self.subTest(a=a, b=b, entity=entity):
                self.assertFalse(any(entity.names is i.names for i in b.world.entities))
                self.assertFalse(any(entity.states is i.states for i in b.world.entities))
                self.assertFalse(any(entity.types is i.types for i in b.world.entities))

        for a_d, b_d in zip(a.drama, b.drama):
            with self.subTest(a_d=a_d, b_d=b_d):
                self.assertNotEqual(a_d.uid, b_d.uid)


class ExampleTests(unittest.TestCase):
    def test_cartoon_fight(self):
        content = textwrap.dedent('''
            [FIGHTER_1]
            state = 1

            [FIGHTER_2]
            type = "Animal"
            state = 1

            [WEAPON]
            type = "Weapon"
            roles = ["FIGHTER_1"]
            state = 1

            [[_]]

            s="""
            <FIGHTER_1>

                I don't like the way you use me, {FIGHTER_2.name}!

            <WEAPON.attacking@FIGHTER_2:shouts/slapwhack?offer=1>

                _Whack!_

            <FIGHTER_2?offer=1>

                Uuurrggh!
            """

            ''').strip()

        scene = Loader.read(content)
        story = Story_10(config={}, assets=Grouping.typewise([scene]))
        specs = story.director.specifications(scene.tables)
        self.assertEqual(story.director.rank_constraints(specs["FIGHTER_1"]), 1, specs)
        self.assertEqual(story.director.rank_constraints(specs["FIGHTER_2"]), 2, specs)
        self.assertEqual(story.director.rank_constraints(specs["WEAPON"]), 3, specs)

        for n in range(3):
            with self.subTest(n=n, m=len(story.director.notes[(None, 0)].maps)):
                notes = story.director.notes[(None, 0)]

                with story.turn() as turn:
                    roles = dict(story.director.roles(specs, story.context.ensemble))
                    if not n:
                        self.assertTrue(turn.blocks, notes)
                        self.assertEqual(3, len(roles), roles)
                    elif n == 1:
                        self.assertTrue(turn.blocks, notes)
                        self.assertEqual(2, len(roles), roles)
                        rewriter = story.director.rewrite(scene, roles)
                        self.assertRaises(KeyError, list, rewriter)
                    elif n == 2:
                        self.assertFalse(turn.blocks, notes)
