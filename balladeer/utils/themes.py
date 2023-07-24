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

import argparse
import colorsys
from decimal import Decimal
import pathlib
import re
import sys
import textwrap

from balladeer.lite.types import Page


import unittest

class ColourTests(unittest.TestCase):

    def test_hsl_to_rgba(self):
        text = "hsl(293.33, 96.92%, 12.75%)"
        rgba = parse_colour(text)
        self.fail(rgba)

    def test_rgb_to_rgba(self):
        text = "rgb(128, 64, 32)"
        rgba = parse_colour(text)
        self.assertEqual([128, 64, 32, 1], rgba)


def parse_colour(text: str, regex = re.compile("(?P<fn>[^\(]+)\((?P<data>[^\)]*)\)")):
    colour = regex.match(text)
    fn = colour.groupdict()["fn"]
    data = colour.groupdict()["data"]
    values = [float(i.strip(" %")) / (100 if "%" in i else 1) for i in data.split(",")]
    if fn == "rgba":
        return values
    elif fn == "rgb":
        return values + [1]
    elif fn.startswith("hsl"):
        rgb = colorsys.hls_to_rgb(values[0] / 360.0, *values[1:3])
        return [int(i * 256) for i in rgb] + [values[3] if len(values) > 3 else 1]


def swatch(name, theme):
    yield f"<h3>{name}</h3>"
    yield "<ul>"
    for label, value in theme.items():
        colour = parse_colour(value)
        yield "<li>"
        yield f"{label}: {value} {colour}"
        yield "</li>"
    yield "</ul>"


def parser(usage=__doc__):
    rv = argparse.ArgumentParser(usage)
    return rv


def main(args):
    page = Page()
    style = textwrap.dedent("""
    <style>
    body {
    background-color: silver;
    }
    </style>
    """).strip()
    page.paste(page.zone.style, style)
    for cls in [Page] + Page.__subclasses__():
        page.paste(page.zone.body, f"<h2>{cls.__name__}</h2>")
        for name, theme in cls.themes.items():
            page.paste(page.zone.body, *swatch(name, theme))
    print(page.html)
    return 0


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    unittest.main()
    sys.exit(rv)

if __name__ == "__main__":
    run()
