#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2022 D E Haynes

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
import importlib.resources
import re
import tomllib
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
        """ Return a link Element given an autolink (`<http://example/com>`). """

        def handleMatch(self, m, data):
            el = ET.Element("a")
            href = self.unescape(m.group(1))
            url, role, mode = AutoLinker.parse_url(href)
            if role and mode:
                el.set("data-role", role)
                el.set("data-mode", mode)

            el.set("href", url)
            el.set("class", "autolink")
            el.text = markdown.util.AtomicString(m.group(1))
            return el, m.start(0), m.end(0)

    @staticmethod
    def parse_url(url):
        if "//" in url:
            components = urllib.parse.urlparse(url)
            role, mode = (None, None)
        else:
            components = urllib.parse.urlparse(url)
            role, mode = components.path.split(":")
            url = "dialogue://" + url.replace(":", "/")
        return url, role, mode

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex = r"<([^ :]+:[^ >]+)>"

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.inlinePatterns.register(self.AutolinkInlineProcessor(self.regex, md), "autolink", 120)


class DialogueParser(html.parser.HTMLParser):

    Directive = namedtuple(
        "Directive",
        ["role", "mode", "params", "fragment", "load", "xhtml", "text"],
        defaults=[None, None, None, None, 0, "", ""]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directives = deque()

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            self.directives.append(self.Directive())
        elif tag == "a":
            attribs = dict(attrs)
            role = attribs.get("data-role")
            mode = attribs.get("data-mode")
            d = self.directives.pop()
            self.directives.append(d._replace(role=role, mode=mode))

    def handle_endtag(self, tag):
        line, char = self.getpos()
        print("???", self.rawdata, line, char)
        ordinal = len(self.directives)
        lines = self.rawdata.splitlines(keepends=True)
        pos = 0 if ordinal in (0, 1) else len(self.directives[-2].xhtml)
        if ordinal:
            d = self.directives.pop()
            xhtml = "Nope"
            # xhtml = self.rawdata[pos:self.current_index]
            self.directives.append(d._replace(xhtml=xhtml))

    def handle_data(self, data):
        if self.directives and not self.directives[-1].text:
            d = self.directives.pop()
            self.directives.append(d._replace(text=data))

class Loader:

    Asset = namedtuple("Scene", ["text", "tables", "resource", "path", "error"], defaults=[None, None, None])
    @staticmethod
    def discover(package, resource=".", suffixes=[".dlg.toml"]):
        for path in importlib.resources.files(package).joinpath(resource).iterdir():
            if "".join(path.suffixes) in suffixes:
                with importlib.resources.as_file(path) as f:
                    text = f.read_text(encoding="utf8")
                    yield Loader.read(text)

    @staticmethod
    def read(text: str, resource="", path=None):
        try:
            tables = tomllib.loads(text)
            error = None
        except tomllib.TOMLDecodeError as e:
            tables = None
            error = e
        return Loader.Asset(text, tables, resource, path, error)


class Parser:

    @staticmethod
    def grab_text(el: ET.Element):
        if el.text is not None:
            yield el.text
        if el.tail is not None:
            yield el.tail

    @staticmethod
    def check(asset: Loader.Asset, shot_key):
        report = dict(shots=len(asset.tables.get(shot_key, [])))
        return asset, report

    @staticmethod
    def parse(text: str, ensemble=None):
        autolinker = AutoLinker()
        md = markdown.Markdown(safe_mode=True, output_format="xhtml", extensions=[autolinker])
        document = md.convert(text)

        parser = DialogueParser(convert_charrefs=True)
        #root = ET.fromstring(f"<doc>{document}</doc>")
        parser.feed(document)
        print(vars(parser))

        directions = []

        """
        # https://helpful.knobs-dials.com/index.php/Python_notes_-_XML#Fetching_text_from_this_data_model
        for paragraph in root.findall("p"):
            paragraph.set("class", "markdown")
            link = paragraph.find("a")
            text = " ".join(i.strip() for i in Parser.grab_text(paragraph))
            directions.append(Loader.Direction(
                ET.tostring(paragraph).decode("utf8"),
                len(text),
                link and link.attrib.get("data-mode"),
                link and link.attrib.get("data-role"),
            ))
        """
        report = {}
        return parser.directives, report
