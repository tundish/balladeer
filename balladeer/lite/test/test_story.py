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

import itertools
import textwrap
import tomllib
import unittest

from balladeer.examples.ex_10_lite_sequence.logic import Story
from balladeer.lite.loader import Loader


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

        scene = Loader.Scene(content, tomllib.loads(content))
        story = Story(config={})
        specs = story.director.specifications(scene.tables)
        self.assertEqual(story.director.rank_constraints(specs["FIGHTER_1"]), 1, specs)
        self.assertEqual(story.director.rank_constraints(specs["FIGHTER_2"]), 2, specs)
        self.assertEqual(story.director.rank_constraints(specs["WEAPON"]), 3, specs)

        for n in range(3):
            with self.subTest(n=n, m=len(story.director.notes[(None, 0)].maps)):
                notes = story.director.notes[(None, 0)]
                actions = list(story.integrate(directives=story.direction))
                if not n:
                    self.assertFalse(story.direction)
                    self.assertFalse(actions)
                else:
                    self.assertTrue(story.direction, notes)
                    self.assertTrue(actions)

                story.director.notes.clear()

                roles = dict(story.director.roles(specs, story.context.ensemble))

                if n == 2:
                    self.assertEqual(2, len(roles), roles)
                    rewriter = story.director.rewrite(scene, roles)
                    self.assertRaises(KeyError, list, rewriter)
                else:
                    self.assertEqual(3, len(roles), roles)
                    html5 = "\n".join(story.director.rewrite(scene, roles))
                    self.assertTrue(html5)

