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
import re
import sys
import textwrap

from balladeer.lite.types import Page

def swatch(name, theme):
    fn_regex = re.compile("(?P<fn>[^\(]+)\([^\)]*\)")
    yield f"<h3>{name}</h3>"
    yield "<ul>"
    for label, value in theme.items():
        fn = fn_regex.match(value)
        yield "<li>"
        yield f"{label}: {value} {fn.groupdict()}"
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
    sys.exit(rv)

if __name__ == "__main__":
    run()
