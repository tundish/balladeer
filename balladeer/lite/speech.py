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
    processor = SpeechMark()
    tag_matcher = re.compile("<[^>]+?>")

    @functools.cache
    def trim(self) -> str:
        return textwrap.dedent(self).strip()

    @functools.cached_property
    def tags(self) -> str:
        return self.processor.loads(self.trim())

    @functools.cached_property
    def lines(self) -> list[str]:
        text = self.tag_matcher.sub("", self.tags)
        return list(filter(None, (i.strip() for i in text.splitlines())))

    @functools.cached_property
    def words(self) -> list[str]:
        return " ".join(self.lines).split(" ")

class Prologue(Speech):
    "Speech before a scene."

class Dialogue(Speech):
    "Speech during a scene."

class Epilogue(Speech):
    "Speech after a scene."
