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

import sys
import textwrap

from speechmark import SpeechMark

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import PlainTextResponse
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles


import balladeer
from balladeer.lite.loader import Loader

__doc__ = """
~/py3.11-dev/bin/python -m balladeer.examples.10_lite_sequence.logic

"""

"""
        typ = mimetypes.guess_type(rsrc)[0]
        item = None
        try:
            if typ.startswith("audio"):
                item = Model.Audio(pkg, rsrc, offset, duration, loop, self.fP, node.line)
            elif typ.startswith("image"):
                item = Model.Still(pkg, rsrc, offset, duration, loop, label, width, height, self.fP, node.line)
            elif typ.startswith("video"):
                item = Model.Video(
                    pkg, rsrc, offset, duration, loop, label, width, height,
                    *(node["options"].get(i, None) for i in ["poster", "url"]),
                    path=self.fP, line_nr=node.line
                )
        except AttributeError:
            pass
"""

def head_elements():
    yield ""

def body_elements():
    yield ""

def html(**kwargs):
    text = [
        "\n".join(head_elements(**kwargs)),
        "\n".join(body_elements(**kwargs)),
    ]
    return textwrap.dedent(f"""
    <!DOCTYPE html>
    <html>
    <head>
    {text[0]}
    </head>
    <body>
    {text[1]}
    </body>
    </html>
    """).strip()


class About(HTTPEndpoint):
    async def get(self, request):
        return PlainTextResponse(f"Hello, world!")


def app_factory():
    routes = [
        #  Mount("/static", app=StaticFiles(directory="static"), name="static"),
        Mount("/static", app=StaticFiles(directory="."), name="static"),
    ]
    app = Starlette(routes=routes)
    return app


if __name__ == "__main__":
    dialogue = list(
        Loader.discover(balladeer.examples, "10_lite_sequence")
    )
    print(dialogue)
    print(html())

