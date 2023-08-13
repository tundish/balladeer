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


import functools
import re
import textwrap

from speechmark import SpeechMark


class Speech(str):
    """
    This is a lightweight class for objects which
    represent marked-up speech.

    .. code-block:: python

        speech = Speech('''
        <STAFF.proposing#3> What will you have, sir? The special is fish today.
            1. Order the Beef Wellington
            2. Go for the Shepherd's Pie
            3. Try the Dover Sole
        ''')
    """
    processor = SpeechMark()
    tag_matcher = re.compile("<[^>]+?>")

    @functools.cache
    def trim(self) -> str:
        """
        Eliminates indentation and other leading whitespace.
        This method is used internally, so you won't need to call it explicitly.

        """
        return textwrap.dedent(self).strip()

    @functools.cached_property
    def tags(self) -> str:
        """
        Render the markup as HTML5.

        >>> speech.tags

        .. code-block:: html

            <blockquote cite="&lt;STAFF.proposing#3&gt;">
            <cite data-role="STAFF" data-directives=".proposing" data-fragments="#3">STAFF</cite>
            <p>
             What will you have, sir? The special is fish today.
            </p>
            <ol>
            <li id="1"><p>
            Order the Beef Wellington
            </p></li>
            <li id="2"><p>
            Go for the Shepherd's Pie
            </p></li>
            <li id="3"><p>
            Try the Dover Sole
            </p></li>
            </ol>
            </blockquote>

        """
        return self.processor.loads(self.trim())

    @functools.cached_property
    def lines(self) -> list[str]:
        """
        Render the markup into lines of plain text.

        >>> speech.lines
        ['STAFF', 'What will you have, sir? The special is fish today.', 'Order the Beef Wellington',
        "Go for the Shepherd's Pie", 'Try the Dover Sole']

        """
        text = self.tag_matcher.sub("", self.tags)
        return list(filter(None, (i.strip() for i in text.splitlines())))

    @functools.cached_property
    def words(self) -> list[str]:
        """
        Render the markup into constituent words.

        >>> speech.words
        ['STAFF', 'What', 'will', 'you', 'have,', 'sir?', 'The', 'special', 'is', 'fish', 'today.',
        'Order', 'the', 'Beef', 'Wellington', 'Go', 'for', 'the', "Shepherd's", 'Pie',
        'Try', 'the', 'Dover', 'Sole']
        """
        return " ".join(self.lines).split(" ")


class Prologue(Speech):
    "Speech before a scene."


class Dialogue(Speech):
    "Speech during a scene."


class Epilogue(Speech):
    "Speech after a scene."
