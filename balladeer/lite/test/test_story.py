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

import textwrap
import tomllib
import unittest

from balladeer.examples.ex_10_lite_sequence.logic import Story
from balladeer.lite.loader import Loader


class ExampleTests(unittest.TestCase):
    def test_cartoon_fight(self):
        content = textwrap.dedent('''
            [FIGHTER_1]
            roles = ["WEAPON"]
            state = 1

            [FIGHTER_2]
            type = "Animal"
            state = 1

            [WEAPON]
            type = "Weapon"
            state = 1

            [[_]]

            s="""
            <FIGHTER_1>

                I don't like the way you use me, {FIGHTER_2.name}!

            <WEAPON.attacking@FIGHTER_2:shouts/slapwhack?offer=1>

                _Whack!_

            """

            [[_]]

            s="""
            <FIGHTER_2>

                Uuurrggh!

            """
            ''').strip()

        scene = Loader.Scene(content, tomllib.loads(content))
        story = Story(config={})
        specs = story.director.specifications(scene.tables)

        for n in range(2):
            with self.subTest(n=n):
                directives = story.director.notes["directives"]
                actions = list(story.action(directives))
                story.director.notes.clear()
                if not n:
                    self.assertFalse(directives)
                    self.assertFalse(actions)
                else:
                    self.assertTrue(directives)
                    self.assertTrue(actions)

                roles = dict(story.director.roles(specs, story.context.ensemble))
                self.assertEqual(3, len(roles), roles)
                html5 = story.director.rewrite(scene, roles)
