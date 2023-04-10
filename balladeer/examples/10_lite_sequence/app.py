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
from collections import defaultdict
import enum
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
from balladeer.lite.director import Director

from .logic import Story


__doc__ = """
~/py3.11-dev/bin/python -m balladeer.examples.10_lite_sequence.logic

"""

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


class Page:
    @enum.unique
    class Zone(enum.Enum):
        xml = enum.auto()
        doc = enum.auto()
        html = enum.auto()
        head = enum.auto()
        title = enum.auto()
        rdf = enum.auto()
        meta = enum.auto()
        link = enum.auto()
        css = enum.auto()
        theme = enum.auto()
        style = enum.auto()
        body = enum.auto()
        app = enum.auto()
        nav = enum.auto()
        main = enum.auto()
        asides = enum.auto()
        inputs = enum.auto()
        svg = enum.auto()
        iframe = enum.auto()
        script = enum.auto()
        end = enum.auto()

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


class About(HTTPEndpoint):
    async def get(self, request):
        return PlainTextResponse(
            "\n".join(
                (
                    f"Balladeer {balladeer.__version__}",
                    "Example 10",
                )
            )
        )


class Home(HTTPEndpoint):
    meta = textwrap.dedent("""
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    """).strip()

    css = """<link rel="stylesheet" href="/static/styles.css" />"""

    body = textwrap.dedent("""
    <form role="form" action="/sessions" method="POST" name="ballad-form-start">
    <button action="submit">Begin</button>
    </form>
    """).strip()

    async def get(self, request):
        page = Page()
        page.paste(page.zone.title, "<title>Example</title>")
        page.paste(page.zone.meta, self.meta)
        page.paste(page.zone.css, self.css)
        page.paste(page.zone.body, self.body)
        return HTMLResponse(page.html)


class Start(HTTPEndpoint):
    async def post(self, request):
        sessions = request.app.state.sessions
        story = Story(request.app.state.config)
        sessions[story.uid] = story
        return RedirectResponse(url=request.url_for("session", session_id=story.uid), status_code=303)


class Session(HTTPEndpoint):
    async def get(self, request):
        session_id = request.path_params["session_id"]
        state = request.app.state
        story = state.sessions[session_id]

        ensemble = story.context.ensemble(story.world)
        scripts = story.context.scripts(state.assets)
        media = story.context.media(state.assets)

        director = Director(story)
        scene, roles = director.selection(scripts, ensemble)
        html5 = director.rewrite(scene, roles)

        page = Page()
        page.paste(page.zone.title, "<title>Example</title>")
        page.paste(page.zone.meta, Home.meta)
        page.paste(page.zone.meta, self.refresh(request.url, director.notes))
        page.paste(page.zone.css, Home.css)
        page.paste(page.zone.body, html5)
        print(director.notes)
        return HTMLResponse(page.html)

    def refresh(self, url, notes: dict = {}) -> str:
        try:
            delay = notes.get("wait", 0) + notes.get("offer", 0)
            return f'<meta http-equiv="refresh" content="{delay:.2f};{url}">'
        except TypeError:
            return ""


async def app_factory(config=None, static=None, loop=None, **kwargs):
    routes = [
        Route("/", Home),
        Route("/about", About),
        Route("/sessions", Start, methods=["POST"], name="start"),
        Route("/session/{session_id:uuid}", Session, name="session"),
    ]
    if static:
        routes.append(Mount("/static", app=StaticFiles(directory=static), name="static"))

    app = Starlette(routes=routes)
    app.state.config = config

    for k, v in kwargs.items():
        setattr(app.state, k, v)

    return app


if __name__ == "__main__":
    print(HTTPEndpoint.__subclasses__())  # Register head, body generators?
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    assets = list(Loader.discover(balladeer.examples, "10_lite_sequence"))
    app = loop.run_until_complete(
        app_factory(static=assets[0].path.parent, loop=loop, assets=assets, sessions={})
    )
    settings = hypercorn.Config.from_mapping({"bind": "localhost:8080", "errorlog": "-"})

    loop.run_until_complete(serve(app, settings))
