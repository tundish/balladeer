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
import sys


class SpeechMark:

    def __init__(
            self,
            lines=[], maxlen=None,
            noescape="!\"',-;{}~",
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

        self.tag_matcher = re.compile("""
        (?P<tag>[`*_])(?P<text>.*?)(?P=tag) # Non-greedy pair
        """, re.VERBOSE)
        self.tagging = {"`": "code", "_": "strong", "*": "em"}

        self.link_matcher = re.compile("""
        \\[(?P<label>[^\\]]*?)\\]       # Non-greedy, permissive
        \\((?P<link>[^\\)]*?)\\)        # Non-greedy, permissive
        """, re.VERBOSE)

        self.escape_table = str.maketrans({
            v: f"&{k}" for k, v in html.entities.html5.items()
            if k.endswith(";") and len(v) == 1
            and v not in noescape + "#+.`_*[]()@?=:/"
        })
        self.source = deque(lines, maxlen=maxlen)
        self._index = 0

    @property
    def text(self):
        return "\n".join(self.source)

    def cue_element(self, match):
        details = match.groupdict()
        if not details["role"].strip() and not details["parameters"]:
            return ""

        attrs = " ".join(
            f'data-{k}="{html.escape(v, quote=True)}"'
            for k, v in details.items()
            if v.strip()
        )
        return f"<cite{' ' if attrs else ''}{attrs}>{details['role']}</cite>"

    def tag_element(self, match):
        details = match.groupdict()
        tag = self.tagging.get(details.get("tag"), "")
        return f"<{tag}>{details['text'].translate(self.escape_table)}</{tag}>"

    def link_element(self, match):
        details = match.groupdict()
        href = html.escape(details["link"], quote=True)
        return f"""<a href="{href}">{details['label'].translate(self.escape_table)}</a>"""

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
            yield "\n".join(
                i for i in self.parse_block(cue, lines[begin:end], terminate) if isinstance(i, str)
            )

        self._index = end

    def parse_block(self, cue, lines, terminate=False):

        list_items = dict(filter(
            operator.itemgetter(1),
            ((n, self.list_matcher.match(line))
            for n, line in enumerate(lines))
        ))

        list_type = ""
        paragraph = False
        for n, line in enumerate(lines):
            if cue and not paragraph:
                yield '<blockquote cite="{0}">'.format(
                    html.escape(cue.group(), quote=True)
                )
                yield self.cue_element(cue)

            elif not n:
                yield "<blockquote>"

            if line.lstrip().startswith("#"):
                yield f"<!-- {line.translate(self.escape_table)} -->"
                continue

            if n in list_items:
                item = list_items[n]
                yield item
                details = item.groupdict()
                if list_type:
                    yield "</p></li>"
                else:
                    list_type = "ul" if details["ordinal"].strip() == "+" else "ol"
                    if paragraph:
                        yield "</p>"
                    yield f"<{list_type}>"

                if list_type == "ul":
                    yield f"<li><p>"
                else:
                    yield f"""<li id="{details['ordinal'].rstrip('.')}"><p>"""
                line = line[item.end():].lstrip()  # Retain hanging text

            elif not paragraph and n < min(list_items or [sys.maxsize]):
                paragraph = True
                yield f"<p>"
            elif not line:
                yield "</p>"
                yield "<p>"

            # Collect all matches and their substitutions
            subs = dict(
                (m.span(), fn(m))
                for fn, i in (
                    (self.cue_element, self.cue_matcher),
                    (self.link_element, self.link_matcher),
                    (self.tag_element, self.tag_matcher)
                )
                for m in i.finditer(line)
            )

            # Create spans for unmatched chunks of text
            chunks = list(itertools.pairwise(sorted({pos for span in subs for pos in span} | {0, len(line)})))

            # Add default processing for each unmatched span
            for span in chunks:
                if span not in subs:
                    subs[span] = line[span[0]: span[1]].translate(self.escape_table)

            line = "".join("" if cue and cue.span() == span else subs[span] for span in chunks)
            yield line

        if terminate:
            if list_type:
                yield "</p></li>"
                yield f"</{list_type}>"
            elif paragraph:
                yield "</p>"
            yield "</blockquote>"

    def loads(self, text: str, marker: str="\n", **kwargs):
        result = marker.join(i.strip() for i in self.feed(text, terminate=True))
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
