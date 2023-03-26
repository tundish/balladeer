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
from types import SimpleNamespace as SN
import unittest

from speechmark import SpeechMark

from balladeer.lite.director import Director


class DirectorTests(unittest.TestCase):

    def test_directive_handling(self):
        """
        <PHONE.announcing@GUEST,STAFF> Ring riiing!
        """

    def test_word_counter(self):
        text = textwrap.dedent("""
        <STAFF.proposing#3> What will you have, sir? The special is fish today.

            1. Order the Beef Wellington
            2. Go for the Shepherd's Pie
            3. Try the Dover Sole
        """).strip()
        sm = SpeechMark()
        html = sm.loads(text)

        director = Director(story=None)
        self.assertEqual(5, len(director.lines(html)))
        self.assertEqual(24, len(director.words(html)))

    def test_rewriter_single_blocks(self):
        text = textwrap.dedent("""
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name}!

        """).strip()
        director = Director(story=None)
        selection = {
            "FIGHTER_1": SN(name="Biffy"),
            "FIGHTER_2": SN(name="Bashy"),
        }

        sm = SpeechMark()
        html = sm.loads(text)
        edit = director.edit(html, selection)
        self.assertIn('data-role="FIGHTER_1"', edit)
        self.assertIn("Bashy!", edit)
        self.assertIn('data-entity="Bashy"', edit)

    def test_rewriter_extended_characters(self):
        text = textwrap.dedent("""
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name}!

        """).strip()
        director = Director(story=None)
        selection = {
            "FIGHTER_1": SN(name="Bîffy"),
            "FIGHTER_2": SN(name="Båshy"),
        }

        sm = SpeechMark()
        html = sm.loads(text)
        edit = director.edit(html, selection)
        self.assertIn('data-role="FIGHTER_1"', edit)
        self.assertIn("B&aring;shy!", edit)
        self.assertIn('data-entity="B&icirc;ffy"', edit)

    def test_rewriter_multiple_blocks(self):
        """
        <WEAPON.attacking@FIGHTER_2:shouts/slapwhack>

            _Whack!_

        <FIGHTER_2>

            Uuurrggh!

        """
