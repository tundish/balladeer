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
from collections.abc import Generator
import json
import pathlib
import textwrap
import warnings

import hypercorn
from hypercorn.asyncio import serve

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse
from starlette.responses import JSONResponse
from starlette.responses import PlainTextResponse
from starlette.responses import RedirectResponse
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

import balladeer
from balladeer.lite.entity import Entity
from balladeer.lite.loader import Loader
from balladeer.lite.story import StoryBuilder
from balladeer.lite.types import Grouping
from balladeer.lite.types import Page


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
    meta = textwrap.dedent(
        """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    """
    ).strip()

    body = textwrap.dedent(
        """
    <form role="form" action="/sessions" method="POST" name="ballad-form-start">
    <button action="submit">Begin</button>
    </form>
    """
    ).strip()

    async def get(self, request):
        page = Page()
        page = self.compose(request, page)
        return HTMLResponse(page.html)

    @staticmethod
    def render_css_links(request, assets: Grouping[str, list[Loader.Asset]]) -> Generator[str]:
        for asset in assets["text/css"]:
            yield f'<link rel="stylesheet" href="/static/{asset.path.name}" />'

    @staticmethod
    def render_js_links(request, assets: Grouping[str, list[Loader.Asset]]) -> Generator[str]:
        for asset in assets["application/javascript"]:
            yield f'<script src="/static/{asset.path.name}"></script>'

    def compose(self, request, page: Page, story: StoryBuilder=None, turn: StoryBuilder.Turn=None) -> Page:
        assets = getattr(self, "assets", Grouping())

        page.paste(page.zone.meta, self.meta)
        page.paste(page.zone.css, *[line for line in self.render_css_links(request, assets)])
        page.paste(page.zone.body, self.body)
        return page


class Start(HTTPEndpoint):
    async def post(self, request):
        state = request.app.state
        story = state.builder(state.config, assets=getattr(self, "assets", []))
        state.sessions[story.uid] = story
        return RedirectResponse(
            url=request.url_for("session", session_id=story.uid), status_code=303
        )


class Session(HTTPEndpoint):

    async def get(self, request):
        session_id = request.path_params["session_id"]
        state = request.app.state
        story = state.sessions[session_id]

        page = Page()
        with story.turn() as turn:
            if not turn.blocks:
                warnings.warn(f"Unable to cast {story.context.ensemble}")
                return RedirectResponse(url=request.url_for("home"), status_code=300)

            page = self.compose(request, page, story, turn)

        return HTMLResponse(page.html)

    def render_cues(self, request, story: StoryBuilder=None, turn: StoryBuilder.Turn=None) -> Generator[str]:
        for n, (index, html5) in enumerate(turn.blocks):
            yield '<div class="ballad cue">'
            yield html5
            try:
                notes = turn.notes[(turn.scene.path, index)]
                m = notes.maps[len(turn.blocks) - n]
                mode = m.get("mode", "")
                media = m.get("media", [])
                assets = {i.path.stem: i for i in self.assets[Loader.Asset]}
                delay = m.get("delay", 0) + m.get("pause", 0)
                if media:
                    yield "<details>"
                    if mode:
                        yield f"<summary>{mode}</summary>"
                        # TODO: separate method to resolve file types, paths, etc.
                        for i in media:
                            try:
                                asset = assets[i]
                                if asset.type == "audio/mpeg":
                                    yield f'<audio src="/static/{asset.path.name}"></audio>'
                            except KeyError:
                                pass
                    yield "</details>"
            except (IndexError, KeyError):
                pass
            yield "</div>"

    def render_refresh(self, url, notes: dict = {}) -> str:
        try:
            wait = notes.get("delay", 0) + notes.get("offer", 0)
            return f'<meta http-equiv="refresh" content="{wait:.2f};{url}">'
        except TypeError:
            return ""

    def render_inputs_to_command(self, request, story):
        options = story.context.options(story.context.ensemble)
        url = request.url_for("command", session_id=story.uid)
        return textwrap.dedent(
            f"""
            <form role="form" action="{url}" method="post" name="ballad-control-text">
            <fieldset>
            <label for="input-command-text" id="input-command-text-tip">&gt;</label>

            <input
            name="text"
            placeholder="{story.context.prompt}"
            pattern="[\w ]+"
            autofocus="autofocus"
            type="text"
            title="&gt;"
            />
            <button type="submit">Enter</button>
            </fieldset>
            </form>
        """
        )

    def compose(self, request, page: Page, story: StoryBuilder=None, turn: StoryBuilder.Turn=None) -> Page:
        assets = getattr(self, "assets", Grouping())

        try:
            page.paste(page.zone.title, f"<title>{story.title}</title>")
        except AttributeError:
            page.paste(page.zone.title, "<title>Story</title>")

        page.paste(page.zone.meta, Home.meta)
        page.paste(page.zone.css, *sorted(line for line in Home.render_css_links(request, assets)))
        page.paste(page.zone.script, *sorted(line for line in Home.render_js_links(request, assets)))

        html5 = "\n".join(self.render_cues(request, story, turn))
        page.paste(page.zone.body, html5)

        offer = story.notes and story.notes[-1]["offer"]
        if offer:
            page.paste(page.zone.meta, self.render_refresh(request.url, story.notes[-1]))
        else:
            page.paste(page.zone.inputs, self.render_inputs_to_command(request, story))

        return page


class Command(HTTPEndpoint):
    async def post(self, request):
        session_id = request.path_params["session_id"]
        state = request.app.state
        story = state.sessions[session_id]

        async with request.form() as form:
            command = form["text"]

        story.action(command)

        return RedirectResponse(
            url=request.url_for("session", session_id=story.uid), status_code=303
        )


class Assembly(HTTPEndpoint):

    class EntitySerializer(JSONResponse):
        encoder = Entity.Encoder()

        def render(self, content) -> bytes:
            return self.encoder.encode(content).encode("utf-8")


    async def get(self, request):
        session_id = request.path_params["session_id"]
        state = request.app.state
        story = state.sessions[session_id]
        assembly = dict(ensemble=story.context.ensemble)
        return self.EntitySerializer(assembly)


async def app_factory(
    assets: list = [],
    builder: StoryBuilder = None,
    config: dict = None,
    routes: list = None,
    static: pathlib.Path = None,
    loop=None,
    **kwargs,
):
    endpoints = dict(
        home=next(reversed(Home.__subclasses__()), Home),
        about=next(reversed(About.__subclasses__()), About),
        start=next(reversed(Start.__subclasses__()), Start),
        session=next(reversed(Session.__subclasses__()), Session),
        assembly=next(reversed(Assembly.__subclasses__()), Assembly),
        command=next(reversed(Command.__subclasses__()), Command),
        **kwargs
    )
    for endpt in endpoints.values():
        endpt.assets = assets.copy()

    routes = routes or [
        Route("/", endpoints["home"], name="home"),
        Route("/about", endpoints["about"]),
        Route("/sessions", endpoints["start"], methods=["POST"], name="start"),
        Route("/session/{session_id:uuid}", endpoints["session"], name="session"),
        Route("/session/{session_id:uuid}/assembly", endpoints["assembly"], name="assembly"),
        Route("/session/{session_id:uuid}/command", endpoints["command"], methods=["POST"], name="command"),
    ]
    if static:
        routes.append(Mount("/static", app=StaticFiles(directory=static), name="static"))

    app = Starlette(routes=routes)
    app.state.builder = builder or next(reversed(StoryBuilder.__subclasses__()), StoryBuilder)
    app.state.config = config
    app.state.sessions = {}

    return app


def quick_start(module, resource=""):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    assets = Grouping.typewise(Loader.discover(module, resource))
    app = loop.run_until_complete(
        app_factory(assets=assets, static=assets.all[0].path.parent, loop=loop)
    )
    settings = hypercorn.Config.from_mapping({"bind": "localhost:8080", "errorlog": "-"})

    loop.run_until_complete(serve(app, settings))
