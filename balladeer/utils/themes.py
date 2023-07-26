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

    def test_zero_red(self):
        text = "hsl(0, 100%, 50%)"
        rgba = parse_colour(text)
        self.assertEqual([255, 0, 0, 1], rgba)

    def test_full_red(self):
        text = "hsl(360, 100%, 50%)"
        rgba = parse_colour(text)
        self.assertEqual([255, 0, 0, 1], rgba)

    def test_rgb_to_rgba(self):
        text = "rgb(128, 64, 32)"
        rgba = parse_colour(text)
        self.assertEqual([128, 64, 32, 1], rgba)


# TODO: without commas
# TODO: deg, turn
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
        args = (values[0] / 360.0, values[2], values[1])
        rgb = colorsys.hls_to_rgb(*args)
        return [int(i * 255) for i in rgb] + [values[3] if len(values) > 3 else 1]


def swatch(name, theme):
    yield f"<h3>Theme: {name}</h3>"
    yield "<table><thead><tr>"
    yield "<th>Label</th>"
    yield "<th>Value</th>"
    yield "<th>Swatch</th>"
    yield "<th>R</th>"
    yield "<th>G</th>"
    yield "<th>B</th>"
    yield "<th>A</th>"
    yield "</tr></thead><tbody>"
    for label, value in theme.items():
        rgba = parse_colour(value)
        colour = "rgba({0}, {1}, {2}, {3})".format(*rgba)
        yield "<tr>"
        yield f"<td>{label}</td>"
        yield f'<td style="font-family: monospace;">{value}</td>'
        yield f'<td style="background-color: {value}; width=4rem;"></td>'
        yield f'<td style="border-color: {colour}; border-style: solid; font-family: monospace;">{rgba[0]:03d}</td>'
        yield f'<td style="border-color: {colour}; border-style: solid; font-family: monospace;">{rgba[1]:03d}</td>'
        yield f'<td style="border-color: {colour}; border-style: solid; font-family: monospace;">{rgba[2]:03d}</td>'
        yield f'<td style="border-color: {colour}; border-style: solid; font-family: monospace;">{rgba[3]}</td>'
        yield "</tr>"

    yield "</tbody></table>"


def parser(usage=__doc__):
    rv = argparse.ArgumentParser(usage)
    return rv


def main(args):
    page = Page()
    style = textwrap.dedent("""
    <style>
    body {
    background-color: silver;
    font-family: sans;
    font-size: 0.8rem;
    margin: 1.2rem;
    margin-left: auto;
    margin-right: auto;
    padding: 1.2rem;
    text-align: center;
    width: 80%;
    }
    </style>
    """).strip()
    page.paste(style, zone=page.zone.style)
    for cls in [Page] + Page.__subclasses__():
        page.paste(f"<h2>Class: {cls.__name__}</h2>", zone=page.zone.body)
        for name, theme in cls.themes.items():
            palette = theme.get("ink", {})
            page.paste(*swatch(name, palette), zone=page.zone.body)
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
