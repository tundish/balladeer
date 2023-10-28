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
import copy
import json
import pathlib
import sys
import textwrap
from types import ModuleType
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
        return PlainTextResponse(f"Balladeer {balladeer.__version__}\n")


class Home(HTTPEndpoint):
    meta = textwrap.dedent("""
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    """).strip()

    body = textwrap.dedent("""
    <form role="form" action="/sessions" method="POST" name="ballad-form-start">
    <button action="submit">Begin</button>
    </form>
    """).strip()

    async def get(self, request):
        page = Page()
        page = self.compose(request, page)
        return HTMLResponse(page.html)

    @staticmethod
    def render_css_links(request, assets: Grouping[str, list[Loader.Asset]]) -> Generator[str]:
        static = request.app.state.static
        for asset in assets["text/css"]:
            try:
                path = asset.path.relative_to(static)
            except ValueError:
                continue
            else:
                yield f'<link rel="stylesheet" href="/static/{path}" />'

    @staticmethod
    def render_js_links(request, assets: Grouping[str, list[Loader.Asset]]) -> Generator[str]:
        static = request.app.state.static
        assets = sorted(
            assets["application/javascript"], key=lambda x: len(x.path.suffix), reverse=True
        )
        for asset in assets:
            try:
                path = asset.path.relative_to(static)
            except ValueError:
                continue

            if asset.path.suffix == ".mjs":
                yield f'<script src="/static/{path}" type="module"></script>'
            else:
                yield f'<script src="/static/{path}"></script>'

    @staticmethod
    def render_css_vars(data: dict=None, tag=":root"):
        data = data or {}
        entries = "\n".join(
            "--ballad-{0}-{1}: {2};".format(key, k, v)
            for key in data
            for k, v in (data[key] or {}).items()
        )
        yield '<style type="text/css">'
        yield "{tag} {{\n{entries}\n}}".format(tag=tag, entries=entries)
        yield "</style>"

    def compose(
        self, request, page: Page, story: StoryBuilder = None, turn: StoryBuilder.Turn = None
    ) -> Page:
        assets = getattr(self, "assets", Grouping())

        page.paste(self.meta, zone=page.zone.meta)
        page.paste(*[line for line in self.render_css_links(request, assets)], zone=page.zone.css)
        page.paste(self.body, zone=page.zone.body)
        return page


class Start(HTTPEndpoint):
    async def post(self, request):
        state = request.app.state
        try:
            story = state.builder(state.config, assets=getattr(self, "assets", []))
        except TypeError:
            story = copy.deepcopy(state.builder)

        state.sessions[story.uid] = story
        return RedirectResponse(
            url=request.url_for("session", session_id=story.uid), status_code=303
        )


class Session(HTTPEndpoint):
    async def get(self, request):
        session_id = request.path_params["session_id"]
        state = request.app.state

        try:
            story = state.sessions[session_id]
        except KeyError:
            warnings.warn(f"No such session as {session_id}")
            return RedirectResponse(url=request.url_for("home"), status_code=410)

        page = Page()
        with story.turn() as turn:
            if not turn.blocks:
                warnings.warn(f"Unable to cast {story.context.ensemble}")
                return RedirectResponse(url=request.url_for("home"), status_code=300)

            page = self.compose(request, page, story, turn)

        return HTMLResponse(page.html)

    def render_cues(
        self, request, story: StoryBuilder = None, turn: StoryBuilder.Turn = None
    ) -> Generator[str]:
        for n, (index, html5) in enumerate(turn.blocks):
            yield '<div class="ballad cue">'
            yield html5
            try:
                notes = turn.notes[(turn.scene.path, index)]
                cue = [m for m in reversed(notes.maps) if m.get("type") == "cue"][n]

                mode = cue.get("mode", "")
                media = cue.get("media", [])
                delay = cue.get("delay", 0) + cue.get("pause", 0)
                if media:
                    yield from self.render_detail(
                        request, mode, media, delay, index=index, ordinal=n
                    )
            except (IndexError, KeyError):
                pass
            yield "</div>"

    def render_detail(
        self,
        request,
        mode: str = "",
        media: list[str] = [],
        delay: float = 0,
        duration: float = 1,
        index: int = 0,
        ordinal: int = 0,
    ) -> Generator[str]:
        assets = {i.path.stem: i for i in self.assets[Loader.Asset]}

        yield (
            f'<details tabindex="0" style="animation-delay: {delay:.2f}s; animation-duration:'
            f' {duration:.2f}s">'
        )

        if mode:
            yield f"<summary>{mode}</summary>"

        # TODO: separate method to resolve file types, paths, etc.
        for m in media:
            try:
                asset = assets[m]
                if asset.type == "audio/mpeg":
                    yield (
                        f'<audio id="{index:02d}-{ordinal:02d}" src="/static/{asset.path.name}"'
                        ' controls="controls" preload="auto"></audio>'
                    )
                    yield (
                        '<script type="text/javascript">\n'
                        "  setTimeout(function(){\n"
                        f'   document.getElementById("{index:02d}-{ordinal:02d}").play();\n'
                        f"  }}, {delay * 1000})\n"
                        "</script>"
                    )
            except KeyError:
                pass
        yield "</details>"

    def render_refresh(self, url, notes: dict = {}) -> str:
        try:
            wait = notes.get("delay", 0) + notes.get("offer", 0)
            return f'<meta http-equiv="refresh" content="{wait:.2f};{url}">'
        except TypeError:
            return ""

    def render_inputs_to_command(self, request, story):
        options = story.context.options(story.context.ensemble)
        url = request.url_for("command", session_id=story.uid)
        return textwrap.dedent(f"""
            <form role="form" action="{url}" method="post" name="ballad-command-form">
            <fieldset>
            <label for="ballad-command-form-input-text" id="ballad-command-form-input-text-label">&gt;</label>

            <input
            name="ballad-command-form-input-text"
            placeholder="{story.context.prompt}"
            pattern="[\w ]+"
            autofocus="autofocus"
            type="text"
            title="{story.context.tooltip}"
            />
            <button type="submit">Enter</button>
            </fieldset>
            </form>
        """)

    def compose(
        self, request, page: Page, story: StoryBuilder = None, turn: StoryBuilder.Turn = None
    ) -> Page:
        assets = getattr(self, "assets", Grouping())

        try:
            page.paste(f"<title>{story.title}</title>", zone=page.zone.title)
        except AttributeError:
            page.paste("<title>Story</title>", zone=page.zone.title)

        page.paste(Home.meta, zone=page.zone.meta)

        styles = story.notes and story.notes[-1]["style"] or []
        staged = Loader.stage(assets, *styles)
        page.paste(*sorted(line for line in Home.render_css_links(request, staged)), zone=page.zone.css)

        page.paste(*Home.render_js_links(request, assets), zone=page.zone.script)

        theme_names = ["default"] + (story.notes[-1].get("theme", []) or [] if story.notes else [])
        settings = story.settings(*theme_names, themes=page.themes)
        page.paste(*Home.render_css_vars(settings), zone=page.zone.theme)

        html5 = "\n".join(self.render_cues(request, story, turn))
        page.paste("<main>", html5, "</main>", zone=page.zone.main)

        offer = story.notes and story.notes[-1]["offer"]
        if offer:
            page.paste(self.render_refresh(request.url, story.notes[-1]), zone=page.zone.meta)
        else:
            page.paste(self.render_inputs_to_command(request, story), zone=page.zone.inputs)

        return page


class Command(HTTPEndpoint):
    async def post(self, request):
        session_id = request.path_params["session_id"]
        state = request.app.state
        story = state.sessions[session_id]

        async with request.form() as form:
            command = form["ballad-command-form-input-text"]

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
        ensemble = story.context.ensemble
        assembly = dict(ensemble=ensemble, options=list(story.context.options(ensemble).keys()))
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
        **kwargs,
    )
    for endpt in endpoints.values():
        endpt.assets = assets.copy()

    routes = routes or [
        Route("/", endpoints["home"], name="home"),
        Route("/about", endpoints["about"]),
        Route("/sessions", endpoints["start"], methods=["POST"], name="start"),
        Route("/session/{session_id:uuid}", endpoints["session"], name="session"),
        Route("/session/{session_id:uuid}/assembly", endpoints["assembly"], name="assembly"),
        Route(
            "/session/{session_id:uuid}/command",
            endpoints["command"],
            methods=["POST"],
            name="command",
        ),
    ]
    if static:
        routes.append(Mount("/static", app=StaticFiles(directory=static), name="static"))

    app = Starlette(routes=routes)
    app.state.static = static
    app.state.builder = builder or next(reversed(StoryBuilder.__subclasses__()), StoryBuilder)
    app.state.config = config
    app.state.sessions = {}

    return app


def quick_start(
    module: [str | ModuleType] = "", resource="", builder=None, host="localhost", port=8080
):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if isinstance(module, str):
        module = pathlib.Path(module)
        module = module.parent if module.is_file() else module

    try:
        assets = Grouping.typewise(Loader.discover(module, resource))
    except ValueError:
        assets = Grouping(list)

    locations = set()
    for k, v in assets.items():
        if isinstance(k, str):
            for asset in v:
                locations.add(asset.path.parent)
                print(
                    f"Discovered in {asset.path.parent.name:<24}: {asset.path.name:<36} ({k})",
                    file=sys.stderr,
                )
        elif k is Loader.Scene:
            for scene in v:
                print(
                    (
                        f"Discovered in {scene.path.parent.name:<24}:"
                        f" {scene.path.name:<36} ({k.__name__})"
                    ),
                    file=sys.stderr,
                )

    app = loop.run_until_complete(
        app_factory(
            assets=assets, builder=builder, static=locations and min(locations), loop=loop
        )
    )
    settings = hypercorn.Config.from_mapping({"bind": f"{host}:{port}", "errorlog": "-"})

    loop.run_until_complete(serve(app, settings))
