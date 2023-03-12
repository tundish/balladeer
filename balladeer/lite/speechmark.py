#!/usr/bin/env python
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
import html
import itertools
import operator
import re


class SpeechMark:

    @staticmethod
    def blocks(text: str):
        trim = textwrap.dedent(text)
        if trim != text:
            warnings.warn(f"Reindentation lost {len(text) - len(trim)} chars")

        lines = text.splitlines(keepends=False)
        enter, exit = 0, 0 # character positions
        start, end = 0, 0  # line numbers
        for n, l in enumerate(lines):
            if not n or l.startswith("<"):
                yield trim, enter, exit, lines, start, end
                start = n
                enter = exit
            else:
                end = n
                exit += len(l)

    def __init__(self, lines=[], maxlen=None):
        self.cue_matcher = re.compile("^<([^ >]*)>")
        self.tone_matcher = re.compile("")
        self.link_matcher = re.compile("")
        self.escape_table = str.maketrans({
            v: f"&{k}" for k, v in html.entities.html5.items()
            if k.endswith(";") and len(v) == 1
            and v not in "!\"#'()*+,-..:;=@{}~`_"
        })
        self.source = deque(lines, maxlen=maxlen)
        self._index = 0

    @property
    def text(self):
        return "\n".join(self.source)

    def parse_lines(self, terminate: bool):
        # Check for cues
        # Check for list items
        # Everything else is a paragraph with inline markup
        # html escape
        lines = list(itertools.islice(self.source, self._index, None))
        # TODO: Remove cue prior to escaping
        cues = dict(
            (n, self.cue_matcher.match(line))
            for n, line in enumerate(lines)
        )
        print(cues)
        text = "\n".join(lines).translate(self.escape_table)
        self._index = len(self.source)
        yield text

    def loads(self, text: str, marker: str="\n", **kwargs):
        result = marker.join(i for i in self.feed(text, terminate=True) if isinstance(i, str))
        return f"{result}{marker}"

    def feed(self, text: str, terminate=False, **kwargs):
        self.source.extend(text.splitlines(keepends=False))
        yield from self.parse_lines(terminate)

    def reset(self):
        self.source.clear()
        self._index = 0


if __name__ == "__main__":
    sm = SpeechMark()
    print(sm.escape_table)
