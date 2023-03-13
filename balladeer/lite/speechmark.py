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
        self.cue_matcher = re.compile("""
        ^<(?P<role>[^\.: >]*)       # Role
        (?P<directives>[^\: >]*)    # Directives
        (?P<mode>[^\? >]*)>         # Mode
        """, re.VERBOSE)
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

        # Make a local list of lines to process
        lines = list(itertools.islice(self.source, self._index, None))

        # Match any available cues and store them by line number
        cues = dict(filter(
            operator.itemgetter(1),
            ((n, self.cue_matcher.match(line))
            for n, line in enumerate(lines))
        ))

        # Create a sequence of 2-tuples which demarcate each block
        blocks = list(itertools.pairwise(
            sorted(set(cues.keys()).union({0, len(lines)} if terminate else {0}))
        ))
        for begin, end in blocks:
            cue = cues.get(begin)
            yield from self.parse_block(cue, lines[begin:end])

        self._index = end

    def parse_block(self, cue, lines):
        # TODO:
        #   find paragraph boundaries
        #   list boundaries
        #   then join text
        #   transformations
        l_open, l_close = "", ""
        p_open, p_close = "<p>", ""
        for n, line in enumerate(lines):
            if not n:
                if cue:
                    # TODO: process cue
                    continue
                yield "<blockquote>"
            if not line:
                # TODO: new paragraph
                yield "</p>"
                p_open, p_close = "<p>", ""
                if l_close:
                    l_open, l_close = "", ""
                    yield "</ul>"
                continue
            elif line.startswith("+"):
                l_open, l_close = "<li>", "</li>"
                yield "<ul>"  # TODO also ol

            # Check for list items
            # Everything else is a paragraph with inline markup
            l_open, l_close = "", ""
            content = line.translate(self.escape_table)
            yield f"{l_open}{p_open}{content}{p_close}{l_close}"
            p_open, p_close = "", ""
        else:
            if l_close:
                l_open, l_close = "", ""
                yield "</ul>"
            yield "</blockquote>"

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