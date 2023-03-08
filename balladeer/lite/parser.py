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


from collections import deque
from collections import namedtuple
import html.parser
import re
import urllib.parse
import xml.etree.ElementTree as ET

import markdown
# from markdown.preprocessors import Preprocessor
# from markdown.treeprocessors import Treeprocessor


class AutoLinker(markdown.extensions.Extension):
    """
    https://spec.commonmark.org/0.30/#autolinks

    """

    class AutolinkInlineProcessor(markdown.inlinepatterns.InlineProcessor):

        def handleMatch(self, m, data):
            el = ET.Element("a")
            href = self.unescape(m.group(1))
            components = urllib.parse.urlparse(href)
            try:
                role, mode = components.path.split(":")
            except ValueError:
                role, mode = "", ""
            el.set("data-role", role)
            el.set("data-mode", mode)

            el.set("href", href)
            el.set("class", "autolink")
            el.text = markdown.util.AtomicString(m.group(1))
            return el, m.start(0), m.end(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex = "^<([^ :]+:[^ >]+)>$"

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.inlinePatterns.register(self.AutolinkInlineProcessor(self.regex, md), "autolink", 75)


class DialogueParser(html.parser.HTMLParser):

    Directive = namedtuple(
        "Directive",
        ["role", "mode", "params", "fragment", "xhtml", "enter", "exit", "text"],
        defaults=[None, None, None, None, "", 0, None, ""]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directives = deque()
        self.line_ends = []

    def handle_starttag(self, tag, attrs):
        self.line_ends = self.line_ends or [0] + [len(line) for line in self.rawdata.splitlines(keepends=True)]
        if tag == "p":
            line, char = self.getpos()
            pos = sum(self.line_ends[:line]) + char
            self.directives.append(self.Directive(enter=pos, xhtml=self.rawdata))
        elif tag == "a":
            attribs = dict(attrs)
            role = attribs.get("data-role")
            mode = attribs.get("data-mode")
            d = self.directives.pop()
            self.directives.append(d._replace(role=role, mode=mode))

    def handle_endtag(self, tag):
        if tag == "p":
            line, char = self.getpos()
            pos = sum(self.line_ends[:line]) + char + len("</p>")

            if self.directives:
                d = self.directives.pop()
                self.directives.append(d._replace(exit=pos))

    def handle_data(self, data):
        if self.directives and not self.directives[-1].text:
            d = self.directives.pop()
            self.directives.append(d._replace(text=data))


class Parser:

    @staticmethod
    def parse(text: str, ensemble=None):
        autolinker = AutoLinker()
        md = markdown.Markdown(safe_mode=True, output_format="xhtml", extensions=[autolinker])
        document = md.convert(text)

        parser = DialogueParser(convert_charrefs=True)
        parser.feed(document)

        report = []
        return parser.directives, report

    @staticmethod
    def check(asset, shot_key):
        report = dict(shots=len(asset.tables.get(shot_key, [])))
        return asset, report
