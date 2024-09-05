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

import colorsys
import enum
from collections import defaultdict
from collections import namedtuple
import re
import warnings


Turn = namedtuple("Turn", ["scene", "specs", "roles", "speech", "blocks", "notes"], defaults=(None, None))


class Page:
    themes = {
        "default": {
            "ink": {
                "gravity": "hsl(282.86, 100%, 14.12%)",
                "shadows": "hsl(203.33, 96.92%, 8.75%)",
                "lolight": "hsl(203.39, 96.72%, 11.96%)",
                "midtone": "hsl(203.39, 96.72%, 31.96%)",
                "hilight": "hsl(203.06, 97.3%, 56.47%)",
                "washout": "hsl(50.00, 0%, 100%)",
                "glamour": "hsl(66.77, 96.92%, 72.75%)",
            },
        }
    }

    @staticmethod
    def css_rgba(text: str, regex = re.compile("(?P<fn>[^\(]+)\((?P<data>[^\)]*)\)")):
        colour = regex.match(text)
        fn = colour.groupdict()["fn"]
        data = colour.groupdict()["data"]
        values = [float(i.strip("%, ")) / (100 if "%" in i else 1) for i in data.split()]
        if fn == "rgba":
            return values
        elif fn == "rgb":
            return values + [1]
        elif fn.startswith("hsl"):
            args = (values[0] / 360.0, values[2], values[1])
            rgb = colorsys.hls_to_rgb(*args)
            return [int(i * 255) for i in rgb] + [values[3] if len(values) > 3 else 1]

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
        style = "Inline styles"
        body = "Body tag"
        basket = "Topmost tags out-of-flow"
        banner = "Top content"
        app = "Anchor points for ECMAScript features"
        nav = "Menus and navigation"
        main = "Main focus of content"
        asides = "Ancillary content"
        inputs = "Forms and controls for user input"
        svg = "Inline SVG documents"
        iframe = "Inclusion of external content"
        bucket = "Lowermost tags out-of-flow"
        script = "Late-loading ECMAScript"
        legals = "End content and links"
        end = "Closing tags"

    def __init__(self, zone=Zone, divs=("basket", "inputs", "svg", "bucket")):
        self.zone = zone
        self.divs = divs
        self.cursor = next(iter(zone), None)
        self.structure = self.setup(zone)

    def setup(self, zone):
        rv = {z: list() for z in zone}
        rv[zone.doc].append("<!DOCTYPE html>")
        rv[zone.html].append("<html>")
        rv[zone.head].append("<head>")
        rv[zone.body].extend(["</head>", "<body>"])
        rv[zone.end].extend(["</body>", "</html>"])
        self.cursor = zone.body
        return rv

    def paste(self, *args, zone=None):
        zone = zone or self.cursor
        self.structure[zone].extend(filter(None, args))
        return self

    def contents(self, zone: Zone):
        values = self.structure.get(zone, [])
        if any(values) and zone.name in self.divs:
            yield ""
            yield f'<div id="ballad-zone-{zone.name}" class="ballad zone">'

        for seq in values:
            if not seq:
                continue

            if isinstance(seq, str):
                yield seq
            else:
                yield from seq

        if any(values) and zone.name in self.divs:
            yield f"</div>"

    @property
    def html(self):
        return "\n".join(
            filter(None, ("\n".join(self.contents(zone)) for zone in self.structure))
        )


class State:
    """
    A mix-in for Python's standard
    `enum.Enum <https://docs.python.org/3/library/enum.html#module-enum>`_.

    Adds some convenient properties to help
    formatting state values as strings.

    """
    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]

    @property
    def label(self) -> str:
        """
        Gives a consistent string to be used as a label
        even when the class defines multiple synonyms
        for each state value.

        """
        return self.value[0] if self.value and isinstance(self.value, list) else self.value


class Detail(State, enum.Enum):
    none = "Reset"
    hide = "Hidden"
    info = "Information requested"
    goal = "Detail of story goals"
    home = "Detail of home"
    held = "Detail of inventory"
    into = "Detail of entrances"
    spot = "Detail of current position"
    exit = "Detail of exits"
    here = "Detail of location"
    help = "Detail of functions"
    hint = "Detail in context"
    quit = "Story ending"


class Fruition(State, enum.Enum):
    """
    Adapted from 'Understanding Computers and Cognition'
    by Terry Winograd and Fernando Flores,
    fig 5.1: The basic conversation for action.

    """

    inception = 1
    elaboration = 2
    construction = 3
    evaluation = 4
    transition = 4
    completion = 5
    discussion = 6
    defaulted = 7
    withdrawn = 8
    cancelled = 9


class Grouping(defaultdict):
    """
    A subclass of Python's standard
    `defaultdict <https://docs.python.org/3/library/collections.html#collections.defaultdict>`_.

    This data structure is used to return objects
    filtered, sorted, and grouped in a particular
    fashion, eg: by state or type.

    """
    @classmethod
    def typewise(cls, items: list) -> defaultdict:
        """
        Create a Grouping of *items* according to their type.

        >>> pprint.pprint(Grouping.typewise([0, 1, 0.0, 1.0, True, False, None]))
        Grouping(
            <class 'list'>,
            {
                <class 'bool'>: [True, False],
                <class 'float'>: [0.0, 1.0],
                <class 'int'>: [0, 1],
                <class 'NoneType'>: [None]
            }
        )

        Objects will be grouped against their class, as
        well as by any *declared type* (attributes `type` and `types`).

        >>> pprint.pprint(Grouping.typewise([namespace(type='Cat'), namespace(types=['Feline', 'Leopard'])))
        Grouping(
            <class 'list'>,
            {
                'Cat': [namespace(type='Cat')],
                'Feline': [namespace(types=['Feline', 'Leopard'])],
                'Leopard': [namespace(types=['Feline', 'Leopard'])],
                 <class 'types.SimpleNamespace'>: [
                    namespace(type='Cat'),
                    namespace(types=['Feline', 'Leopard'])
                 ]
            }
        )

        """
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
    def all(self) -> list:
        "Returns every entry in the grouping."
        return [i for s in self.values() for i in s]

    @property
    def each(self) -> list:
        "Returns one of each entry in the grouping."
        return list(set(self.all))
