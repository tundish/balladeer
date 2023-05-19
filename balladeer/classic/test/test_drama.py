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

import textwrap
import unittest

from turberfield.catchphrase.presenter import Presenter

from balladeer.classic.drama import Drama


class DramaTests(unittest.TestCase):
    def test_next_states_single(self):
        text = textwrap.dedent("""
        .. entity:: DRAMA
           :types:  balladeer.classic.drama.Drama

        Scene
        =====

        Shot
        ----

        .. condition:: DRAMA.state 0

        Text.
        """)
        drama = Drama()
        presenter = Presenter.build_from_text(text, ensemble=[drama])
        self.assertTrue(presenter.frames, presenter.text)

        drama.valid_states = drama.find_valid_states(presenter)
        self.assertEqual([0], drama.valid_states)

        rv = drama.next_states()
        self.assertEqual((0, 0), rv)

    def test_next_states_gaps(self):
        text = textwrap.dedent("""
        .. entity:: DRAMA
           :types:  balladeer.classic.drama.Drama

        Scene
        =====

        Zero
        ----

        .. condition:: DRAMA.state 0

        Text.

        One
        ---

        .. condition:: DRAMA.state 1

        Text.

        Four
        ----

        .. condition:: DRAMA.state 4

        Text.

        Five
        ----

        .. condition:: DRAMA.state 5

        Text.
        """)
        drama = Drama()
        presenter = Presenter.build_from_text(text, ensemble=[drama])
        self.assertTrue(presenter.frames, presenter.text)

        drama.valid_states = drama.find_valid_states(presenter)
        self.assertEqual([0, 1, 4, 5], drama.valid_states)

        drama.state = 0
        rv = drama.next_states()
        self.assertEqual((0, 1), rv)

        drama.state = 1
        rv = drama.next_states()
        self.assertEqual((0, 4), rv)

        drama.state = 4
        rv = drama.next_states()
        self.assertEqual((1, 5), rv)

        drama.state = 5
        rv = drama.next_states()
        self.assertEqual((4, 5), rv)
