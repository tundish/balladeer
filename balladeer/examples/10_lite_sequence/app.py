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
from balladeer.lite.types import Story

from .logic import World


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


class Presenter:
    pass


class Page:

    @enum.unique
    class Zone(enum.Enum):
        xml     =   2
        doc     =   4
        html    =   6
        head    =   8
        title   =   10
        rdf     =   12
        meta    =   14
        link    =   16
        css     =   18
        theme   =   20
        style   =   22
        body    =   24
        app     =   26
        nav     =   28
        main    =   30
        aside   =   32
        svg     =   34
        iframe  =   36
        script  =   38
        end     =   40

    @staticmethod
    def head_elements(**kwargs):
        yield ""

    @staticmethod
    def body_elements(**kwargs):
        yield ""

    def __init__(self, head=None, body=None, **kwargs):
        self.head = head or self.head_elements(**kwargs)
        self.body = body or self.body_elements(**kwargs)
        self.zones = {z: list() for z in self.Zone}

    def structure(self):
        self.zones[self.Zone.doc].append("<!DOCTYPE html>")
        self.zones[self.Zone.html].append("<html>")
        self.zones[self.Zone.head].append("<head>")
        self.zones[self.Zone.body].extend(["</head>", "<body>"])
        # Sort links by type, eg: css, js, font, etc
        # <link
        #   rel="preload"
        #   href="fonts/zantroke-webfont.woff2"
        #   as="font"
        #   type="font/woff2"
        #   crossorigin />

        # NB: Prefetch gets resources for the next page.
        # Stateful Presenter needs lookahead.
        self.zones[self.Zone.end].extend(["</body>", "</html>", "\n"])
        return self

    def paste(self, zone, *args):
        self.zones[zone].extend(args)
        return self

    @property
    def html(self):
        return "\n".join(
            gen if isinstance(gen, str) else "\n".join(gen)
            for seq in self.zones.values()
            for gen in seq
        )

class About(HTTPEndpoint):
    async def get(self, request):
        return PlainTextResponse("\n".join((
            f"Balladeer {balladeer.__version__}",
            "Example 10",
        )))


class Home(HTTPEndpoint):

    @staticmethod
    def head_elements(**kwargs):
        yield textwrap.dedent("""
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>FIXME</title>
        <link rel="stylesheet" href="/static/styles.css" />
        """).strip()

    @staticmethod
    def body_elements(**kwargs):
        yield textwrap.dedent("""
        <form role="form" action="/sessions" method="POST" name="ballad-form-start">
        <button action="submit">Begin</button>
        </form>
        """).strip()

    async def get(self, request):
        page = Page()
        page.paste(page.Zone.meta, Home.head_elements())
        page.paste(page.Zone.body, Home.body_elements())
        return HTMLResponse(page.html)


class Start(HTTPEndpoint):
    async def post(self, request):
        sessions = request.app.state.sessions
        key , val = await session_factory(request.app.state.config)
        sessions[key] = val
        return RedirectResponse(
            url=request.url_for("session", session_id=key),
            status_code=303
        )


class Session(HTTPEndpoint):

    @staticmethod
    def head_elements(**kwargs):
        yield textwrap.dedent("""
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>FIXME</title>
        <link rel="stylesheet" href="/static/styles.css" />
        """).strip()

    @staticmethod
    def body_elements(text, **kwargs):
        sm = SpeechMark()
        blocks = sm.loads(text)
        yield blocks

    async def get(self, request):
        session_id = request.path_params["session_id"]
        state = request.app.state
        story = state.sessions[session_id]

        ensemble = story.context.ensemble(story.world)
        scripts = story.context.scripts(state.assets)

        director = Director()
        scene, cast = director.selection(scripts, ensemble)
        rewriter = director.rewrite(scene, cast)
        shot = next(i for i in rewriter if director.allows(i))

        text = shot.get(director.dlg_key, "")
        page = Page()
        page.paste(page.Zone.meta, Session.head_elements())
        page.paste(page.Zone.body, Session.body_elements(text))
        return HTMLResponse(page.html)


async def session_factory(config):
    world = World(config)
    story = Story(config, world)
    return story.uid, story


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

    assets = list(
        Loader.discover(balladeer.examples, "10_lite_sequence")
    )
    app = loop.run_until_complete(app_factory(
        static=assets[0].path.parent, loop=loop,
        assets=assets, sessions={}
    ))
    settings = hypercorn.Config.from_mapping(
        {"bind": "localhost:8080", "errorlog": "-"}
    )

    loop.run_until_complete(serve(app, settings))

