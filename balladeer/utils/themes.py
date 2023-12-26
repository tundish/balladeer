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
import pathlib
import sys
import textwrap

from balladeer.lite.types import Page


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
        rgba = Page.css_rgba(value)
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


def static_page() -> Page:
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
    return page


def parser(usage=__doc__):
    rv = argparse.ArgumentParser(usage)
    return rv


def main(args):
    page = static_page()
    print(page.html)
    return 0


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
