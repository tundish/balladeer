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

import asyncio
import sys
import textwrap
import uuid

import hypercorn
from hypercorn.asyncio import serve

from speechmark import SpeechMark

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse
from starlette.responses import PlainTextResponse
from starlette.responses import RedirectResponse
from starlette.routing import Mount
from starlette.routing import Route
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
themes = {
    "default": {
        "ballad-ink-washout": "hsl(50, 0%, 100%, 1.0)",
        "ballad-ink-shadows": "hsl(202.86, 100%, 4.12%)",
        "ballad-ink-lolight": "hsl(203.39, 96.72%, 11.96%)",
        "ballad-ink-midtone": "hsl(203.39, 96.72%, 11.96%)",
        "ballad-ink-hilight": "hsl(203.06, 97.3%, 56.47%)",
        "ballad-ink-glamour": "hsl(353.33, 96.92%, 12.75%)",
        "ballad-ink-gravity": "hsl(293.33, 96.92%, 12.75%)",
    },
}

"""
<form role="form" action="/sessions" method="POST" name="ballad-form-start">
<button action="submit">Begin</button>
</form>
"""

class Page:

    @staticmethod
    def head_elements(**kwargs):
        yield ""

    @staticmethod
    def body_elements(**kwargs):
        yield ""

    def __init__(self, head=None, body=None, **kwargs):
        self.head = head or self.head_elements(**kwargs)
        self.body = body or self.body_elements(**kwargs)

    @property
    def html(self):
        text = ["\n".join(self.head), "\n".join(self.body)]
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
        return PlainTextResponse("\n".join((
            f"Balladeer {balladeer.__version__}",
            "Example 10",
        )))


class Home(HTTPEndpoint):
    async def get(self, request):
        page = Page(self.head_elements(), self.body_elements())
        return HTMLResponse(page.html)


class Start(HTTPEndpoint):
    async def get(self, request):
        sessions = request.app.state.sessions
        key , val = await session_factory()
        sessions[key] = val
        return RedirectResponse(
            url=request.url_for("session", session_id=key)
        )


class Session(HTTPEndpoint):
    async def get(self, request):
        session_id = request.path_params["session_id"]
        session = request.app.state.sessions[session_id]

        print(f"Session: {session_id}")
        page = Page().html
        return HTMLResponse(page)


async def session_factory():
    return uuid.uuid4(), {}

async def app_factory(scripts, loop=None):
    routes = [
        Route("/", Start),
        Route("/about", About),
        Route("/session/{session_id:uuid}", Session, name="session"),
        #  Mount("/static", app=StaticFiles(directory="static"), name="static"),
        Mount("/static", app=StaticFiles(directory="."), name="static"),
    ]
    app = Starlette(routes=routes)
    app.state.scripts = scripts
    app.state.sessions = {}
    return app


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    scripts = list(
        Loader.discover(balladeer.examples, "10_lite_sequence")
    )
    app = loop.run_until_complete(app_factory(scripts, loop=loop))
    settings = hypercorn.Config.from_mapping({"bind": "localhost:8080"})

    loop.run_until_complete(serve(app, settings))

