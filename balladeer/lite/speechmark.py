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

    def __init__(
            self,
            lines=[], maxlen=None,
            noescape="!\"#'()*+,-..:;=@{}~`_",
        ):
        self.cue_matcher = re.compile("""
        ^<                              # Opening bracket
        (?P<role>[^\.:\\?# >]*)         # Role
        (?P<directives>[^\:\\?# >]*)    # Directives
        (?P<mode>[^\\?# >]*)            # Mode
        (?P<parameters>[^# >]*)         # Parameters
        (?P<fragments>[^ >]*)           # Fragments
        >                               # Closing bracket
        """, re.VERBOSE)

        self.list_matcher = re.compile("""
        ^\s*                            # Leading space
        (?P<ordinal>\+|\d+\.)           # Digits and a dot
        """, re.VERBOSE)

        self.tone_matcher = re.compile("")
        self.link_matcher = re.compile("")
        self.escape_table = str.maketrans({
            v: f"&{k}" for k, v in html.entities.html5.items()
            if k.endswith(";") and len(v) == 1
            and v not in noescape
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
            yield "\n".join(self.parse_block(
                cue, lines[begin:end], terminate
            ))

        self._index = end

    def parse_block(self, cue, lines, terminate=False):

        list_items = dict(filter(
            operator.itemgetter(1),
            ((n, self.list_matcher.match(line))
            for n, line in enumerate(lines))
        ))

        paragraphs = list(itertools.pairwise(sorted({
            n for n, line in enumerate(lines)
            if not line.strip()
        }.union({0, len(lines)} if terminate else {0}))))

        list_type = ""
        for n, line in enumerate(lines):
            while paragraphs and n < paragraphs[0][0]:
                paragraphs.pop()

            if cue:
                yield '<blockquote cite="{0}">'.format(
                    html.escape(line[:cue.end()], quote=True)
                )

                attrs = " ".join(
                    f'data-{k}="{html.escape(v, quote=True)}"'
                    for k, v in cue.groupdict().items()
                    if v
                )
                yield f"<cite{' ' if attrs else ''}{attrs}>{cue['role']}</cite>"
                line = line[cue.end():].lstrip()  # Retain hanging text
            elif not n:
                yield "<blockquote>"

            if n in list_items:
                item = list_items[n]
                details = item.groupdict()
                if list_type:
                    yield "</p></li>"
                else:
                    list_type = "ul" if details["ordinal"].strip() == "+" else "ol"
                    yield f"<{list_type}>"

                if list_type == "ul":
                    yield f"<li><p>"
                else:
                    yield f"""<li id="{details['ordinal'].rstrip('.')}"><p>"""
                line = line[item.end():].lstrip()  # Retain hanging text

            if paragraphs and n == paragraphs[0][0]:
                # yield "<p>"
                pass

            yield line.translate(self.escape_table)

            if paragraphs and n == paragraphs[0][1]:
                # yield "</p>"
                pass

        if terminate:
            if list_type:
                yield "</p></li>"
                yield f"</{list_type}>"
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
