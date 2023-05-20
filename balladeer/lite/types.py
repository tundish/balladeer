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

import enum
from collections import defaultdict


class Page:
    themes = {
        "default": {
            "ballad-ink-gravity": "hsl(293.33, 96.92%, 12.75%)",
            "ballad-ink-shadows": "hsl(202.86, 100%, 4.12%)",
            "ballad-ink-lolight": "hsl(203.39, 96.72%, 11.96%)",
            "ballad-ink-midtone": "hsl(203.39, 96.72%, 11.96%)",
            "ballad-ink-hilight": "hsl(203.06, 97.3%, 56.47%)",
            "ballad-ink-washout": "hsl(50, 0%, 100%, 1.0)",
            "ballad-ink-glamour": "hsl(353.33, 96.92%, 12.75%)",
        },
    }

    @enum.unique
    class Zone(enum.Enum):
        xml = "XML features only"
        doc = "Doctype declaration"
        html = "HTML opening tag"
        head = "Head tag"
        title = "Title tag and attributes"
        rdf = "Dublin Core and semantic links"
        meta = "Meta tags"
        link = "Link tags"
        css = "Links to CSS styles"
        theme = "Dynamic updates to styles"
        body = "Body tag"
        style = "Inline styles"
        banner = "Top content"
        app = "Anchor points for ECMAScript features"
        nav = "Menus and navigation"
        main = "Main focus of content"
        asides = "Ancillary content"
        inputs = "Forms and controls for user input"
        svg = "Inline SVG documents"
        iframe = "Inclusion of external content"
        script = "Late-loading ECMAScript"
        legals = "End content and links"
        end = "Closing tags"

    def __init__(self, zone=Zone):
        self.zone = zone
        self.structure = self.setup(zone)

    def setup(self, zone):
        rv = {z: list() for z in zone}
        rv[zone.doc].append("<!DOCTYPE html>")
        rv[zone.html].append("<html>")
        rv[zone.head].append("<head>")
        rv[zone.body].extend(["</head>", "<body>"])
        # Sort links by type, eg: css, js, font, etc
        # <link
        #   rel="preload"
        #   href="fonts/zantroke-webfont.woff2"
        #   as="font"
        #   type="font/woff2"
        #   crossorigin />

        # NB: Prefetch gets resources for the next page.
        # Stateful Presenter needs lookahead.
        rv[zone.end].extend(["</body>", "</html>"])
        return rv

    def paste(self, zone, *args):
        self.structure[zone].extend(filter(None, args))
        return self

    @property
    def html(self):
        return "\n".join(
            gen if isinstance(gen, str) else "\n".join(gen)
            for seq in self.structure.values()
            for gen in seq
        )


class State:
    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]


class Fruition(State, enum.IntEnum):
    """
    Adapted from 'Understanding Computers and Cognition'
    by Terry Winograd and Fernando Flores,
    fig 5.1: The basic conversation for action.

    """

    inception = 1
    elaboration = 2
    construction = 3
    transition = 4
    completion = 5
    discussion = 6
    defaulted = 7
    withdrawn = 8
    cancelled = 9


class Grouping(defaultdict):
    @classmethod
    def typewise(cls, items):
        rv = cls(list)
        for i in items:
            rv[type(i)].append(i)
            try:
                for t in i.types:
                    rv[t].append(i)
            except AttributeError:
                try:
                    rv[i.type].append(i)
                except AttributeError:
                    pass
        return rv

    @property
    def all(self):
        return [i for s in self.values() for i in s]

    @property
    def each(self):
        return list(set(self.all))
