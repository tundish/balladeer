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


import unittest

from balladeer.lite.speech import Speech


class SpeechTests(unittest.TestCase):
    def test_trim(self):
        text = """
            1
            2
            3
        """
        s = Speech(text)
        a = s.trim()
        b = s.trim()
        self.assertIs(a, b)
        self.assertEqual(5, len(a), a)

    def test_tags(self):
        text = """
            <> T

            <>
            1. a
            2. b
            3. c

        """
        s = Speech(text)
        a = s.tags
        b = s.tags
        self.assertIs(a, b)

    def test_line_count(self):
        text = """
        <STAFF.proposing#3> What will you have, sir? The special is fish today.

            1. Order the Beef Wellington
            2. Go for the Shepherd's Pie
            3. Try the Dover Sole
        """
        s = Speech(text)

        a = s.lines
        b = s.lines
        self.assertIs(a, b)
        self.assertEqual(5, len(s.lines))

    def test_word_count(self):
        text = """
        <STAFF.proposing#3> What will you have, sir? The special is fish today.
            1. Order the Beef Wellington
            2. Go for the Shepherd's Pie
            3. Try the Dover Sole
        """
        s = Speech(text)

        a = s.words
        b = s.words
        self.assertIs(a, b)
        self.assertEqual(24, len(s.words))
