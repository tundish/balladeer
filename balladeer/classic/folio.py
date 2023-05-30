#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2022 D E Haynes

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


"""

Usage::

    python -m balladeer.classic.folio blathnaid/book/ | weasyprint - folio.pdf

"""

import argparse
import datetime
import mimetypes
import pathlib
import re
import sys

from balladeer.classic.drama import Drama
from balladeer.classic.story import Story

from turberfield.dialogue.adapters import ColourAdapter
from turberfield.dialogue.cli import add_common_options
from turberfield.dialogue.cli import add_performance_options
from turberfield.dialogue.main import HTMLHandler
from turberfield.dialogue.model import Model
from turberfield.utils.logger import LogAdapter
from turberfield.utils.logger import LogManager

import textwrap

# TODO
#  Format images
#  Prepend sections from .html files
#  Output is a directory, ?.html + images


class Folio(Story):
    static_style = textwrap.dedent("""
        @page {
            size: 5in 7.75in;
            counter-reset: footnote;
            @bottom-center {
                content: counter(page);
                width: 100%;
                vertical-align: top;
                border-top: 0.5pt solid;
                margin-top: 0.25in;
                margin-bottom: 0.6in;
                padding-top: 0.1in;
            }
            @footnote {
                footnote-display: inline;
                max-height: 2rem;
            }

        }

        @page:first {
            @bottom-center {
                border: 0;
                content: "";
            }
        }

        @page empty {
            @bottom-center {
                border: 0;
                content: "";
            }
            @top-left {
                content: "";
            }
        }

        @page front{
            @bottom-center {
                content: counter(page, lower-roman);
            }
            @top-left {
                content: "";
            }
        }

        @page:left{
            margin: 0.6in 0.75in 0.6in 0.5in;
            @top-left {
                content: var(--balladeer-metadata-project);
                font-size: 0.7rem;
                vertical-align: middle;
                width: 100%;
            }
        }

        @page:right{
            margin: 0.6in 0.5in 0.6in 0.75in;
            @top-right {
                content: var(--balladeer-metadata-version);
                font-size: 0.7rem;
                vertical-align: middle;
                width: 100%;
            }
        }

        @media print {
        .shot h2 {
        display: none;
        }

        .scene {
        page-break-before: right;
        }

        .shot {
        page-break-inside: avoid;
        }

        .shot:first-of-type p {
        text-indent: 0rem;
        }

        h1 {
        font-size: 200%;
        margin-bottom: 18%;
        margin-top: 28%;
        text-transform: capitalize;
        text-align: center;
        }

        blockquote header {
        display: none;
        }

        p {
        font-family: "Libre Baskerville", serif;
        font-size: small;
        margin-bottom: 1.3rem;
        text-align: justify;
        text-indent: 0.5rem;
        }

        .line:last-of-type blockquote::after {
        content: "-";
        display: block;
        margin-bottom: 1rem;
        margin-top: 1rem;
        text-align: center;
        }

        .spoken + .unspoken .line:first-of-type p {
        text-indent: 0rem;
        }

        blockquote {
        font-style: italic;
        }

        dl {
        display: none;
        }

        span.call{
        display: inline;
        }

        span.footnote {
        float: footnote;
        font-family: "Libre Baskerville", serif;
        font-size: 0.7rem;
        }

        ::footnote-call {
        display: inline;
        }

        ::footnote-marker {
        }
        }   /* End of print media */

        @media screen {
        dl {
        align-items: center;
        border-color: gray;
        border-top-style: dotted;
        border-width: thin;
        display: flex;
        flex-direction: row;
        flex-flow: row;
        flex-wrap: wrap;
        font-family: "DejaVu Sans", sans-serif;
        justify-content: space-around;
        letter-spacing: 0.125rem;
        padding-top: 1.6rem;
        margin-left: 1rem;
        }

        dt {
        font-size: 0.7rem;
        font-weight: lighter;
        margin-bottom: 0.4rem;
        margin-right: 0.3rem;
        }

        dt::after {
        content: ":";
        }

        dd {
        font-weight: lighter;
        margin-bottom: 0.9rem;
        margin-right: 1.0rem;
        }

        h1 {
        /* font-family: "Cinzel", "Libre Baskerville", serif; */
        font-size: 1.2rem;
        font-weight: bold;
        letter-spacing: 0.125rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        text-align: center;
        text-transform: uppercase;
        }

        h2 {
        border-color: gray;
        border-left-style: dotted;
        border-width: thin;
        font-family: "DejaVu Sans", sans-serif;
        font-size: 0.7rem;
        padding-left: 0.4rem;
        margin-bottom: 0.6rem;
        margin-left: 24rem;
        }

        section {
        margin-left: auto;
        margin-right: auto;
        margin-top: 6.0rem;
        width: 32rem;
        }

        .scene {
        margin-top: 1.8rem;
        }

        .shot {
        margin-bottom: 1.6rem;
        page-break-inside: avoid;
        }

        p {
        font-family: "IBM Plex Serif", "Junge", "Libre Baskerville", "FreeSerif", serif;
        line-height: 1.6rem;
        padding-bottom: 0.4rem;
        padding-top: 0.4rem;
        word-spacing: 0.3rem;
        }

        .spoken p {
        font-style: italic;
        }

        .spoken .line:first-of-type header {
        display: block;
        font-family: "DejaVu Sans", sans-serif;
        margin-bottom: 0.6rem;
        }

        blockquote header {
        display: none;
        }

        }   /* End of screen media */

        * {
        box-sizing: border-box;
        border: 0;
        font: inherit;
        font-size: 100%;
        line-height: 1.2em;
        list-style-type: none;
        margin: 0;
        outline: 0;
        padding: 0;
        text-decoration: none;
        vertical-align: baseline;
        }

        .catchphrase-banner h1::after{
        content: var(--balladeer-metadata-author);
        display: block;
        font-size: 0.8rem;
        margin-top: 1.2rem;
        }

        em {
        font-style: italic;
        }

        strong {
        font-weight: bold;
        }

        .line:first-of-type blockquote header {
        text-transform: uppercase;
        }

    """)

    @staticmethod
    def single_space(html):
        return (
            re.sub("[ ]+", " ", html.replace("\n", " ").replace("&NewLine;", " "))
            .replace("> <", "><")
            .rstrip()
        )

    def __init__(self, dwell, pause, **kwargs):
        super().__init__(**kwargs)
        self.dwell = dwell
        self.pause = pause
        self.chapters = []
        self.metadata = {"print": datetime.date.today()}
        self.sections = []
        self.seconds = 0
        self.log = LogManager().get_logger("main").clone("folio")

    def animated_line_to_html(self, anim, **kwargs):
        name = getattr(anim.element.persona, "name", anim.element.persona)
        name = "{0.firstname} {0.surname}".format(name) if hasattr(name, "firstname") else name
        delay = self.seconds
        yield (
            f'<div class="line" style="animation-delay: {delay:.2f}s; animation-duration:'
            f' {anim.duration:.2f}s">'
        )
        if name:
            yield "<blockquote>"
            yield f"<header>{name}</header>"
            yield self.single_space(anim.element.html)
            yield "</blockquote>"
        else:
            yield self.single_space(anim.element.html)
        yield "</div>"
        self.seconds += anim.duration

    def render_animated_frame_to_html(self, frame, controls=[], **kwargs):
        witness = next(
            (i.element for v in frame.values() for i in v if hasattr(i, "element")), None
        )
        dialogue = "".join(
            i for l in frame[Model.Line] for i in self.animated_line_to_html(l, **kwargs)
        )
        stills = "\n".join(self.animated_still_to_html(i, **kwargs) for i in frame[Model.Still])
        spoken = any(anim.element.persona for anim in frame[Model.Line])
        chapter = ([i.get("chapter", 0) for i in self.chapters] or [0])[-1]
        if not self.chapters or self.chapters[-1].get("scene") != frame["scene"]:
            if chapter:
                yield "</section>"
            metadata = {"path": witness.path} if witness else {}
            if frame["scene"]:
                metadata.update({"chapter": chapter + 1, "scene": frame["scene"]})
            self.chapters.append(metadata)
            yield from self.render_metadata(**metadata)

            yield f'<section class="scene" style="--chapter: {metadata["chapter"]}">'

            if frame["scene"]:
                yield f"<h1>{frame['scene']}</h1>"

            if spoken:
                yield '<div class="shot spoken">'
            else:
                yield '<div class="shot unspoken">'

            if frame["name"]:
                yield f"<h2>{frame['name']}</h2>"

            if stills.strip():
                yield f"{stills}"
            yield f"{dialogue}"
            yield "</div>"
        else:
            if spoken:
                yield '<div class="shot spoken">'
            else:
                yield '<div class="shot unspoken">'
            yield f"<h2>{frame['name']}</h2>"
            if stills.strip():
                yield f"{stills}"
            yield f"{dialogue}"
            yield "</div>"

        self.log.debug(self.seconds)

    def animate_frame(self, presenter, frame, dwell=None, pause=None):
        dwell = presenter.dwell if dwell is None else dwell
        pause = presenter.pause if pause is None else pause
        animation = presenter.animate(frame, dwell=dwell, pause=pause)
        return "\n".join(self.render_animated_frame_to_html(animation))

    def render_metadata(self, **kwargs):
        yield '<section class="metadata">'
        yield "<dl>"
        metadata = dict(self.metadata, **kwargs)
        for k, v in metadata.items():
            if not v:
                continue

            yield '<div class="field">'
            yield f"<dt>{k}</dt>"
            if isinstance(v, list):
                yield from (f"<dd>{i}</dd>" for i in v)
            else:
                yield f"<dd>{v}</dd>"
            yield "</div>"
        yield "</dl>"
        yield "</section>"

    def read(self, presenter=None, reply=None):
        presenter = self.represent(reply, previous=presenter)
        self.metadata.update(presenter.metadata)

        for frame in presenter.frames:
            section = self.animate_frame(presenter, frame, self.dwell, self.pause)
            if section:
                self.sections.append(section)

        reply = self.context.deliver(cmd="", presenter=presenter)
        return presenter, reply

    def run(self, n=0):
        presenter, reply = None, None
        while self.context.folder:
            presenter, reply = self.read(presenter, reply)

            if not n:
                self.context.folder.pop(0)
            else:
                n -= 1
        else:
            self.sections[-1] += "\n</section>"
            self.log.info("Folder exhausted")

    @property
    def css(self):
        settings = dict(
            {
                f"balladeer-metadata-{k}": next(iter(v if isinstance(v, list) else [v]))
                for k, v in self.metadata.items()
                if v
            },
            **vars(self.settings),
        )

        # Awful hack to avoid errors from weasyprint, which is otherwise awesome
        static_style = self.static_style
        for k, v in settings.items():
            static_style = static_style.replace(f"var(--{k})", f'"{v!s}"')

        return "\n".join(
            (
                self.render_dict_to_css(settings),
                static_style,
            )
        )

    def render_html(self, links=[], style="", sections=[]):
        title = next(
            iter(self.metadata.get("title", [self.__class__.__name__])), self.__class__.__name__
        )
        return self.render_body_html(title=title, base_style="").format(
            "\n".join(links), style, "\n".join(sections)
        )


class TypeGetter:
    def __init__(self, paths):
        self.paths = [i for p in paths for i in (p.iterdir() if p.is_dir() else [p])]
        self.log = LogManager().get_logger("main").clone("getter")
        for p, t in zip(self.paths, map(self.guess_type, self.paths)):
            if t[0]:
                self.log.info(f"Recognized {p} as type {t[0]}")
            else:
                self.log.warning(f"Unrecognized file type: {p}")

    @staticmethod
    def guess_type(path):
        if str(path).endswith(".rst"):
            return ("text/x-rst", None)
        else:
            return mimetypes.guess_type(path, strict=False)

    @property
    def css(self):
        return [p for p in self.paths if self.guess_type(p)[0] == "text/css"]

    @property
    def rst(self):
        return sorted(p for p in self.paths if self.guess_type(p)[0] == "text/x-rst")


def main(args):
    log = LogManager().get_logger("main")

    if args.log_path:
        log(args.log_level, ColourAdapter(), sys.stderr)
        log.set_route(log.Level.NOTSET, LogAdapter(), args.log_path)
    else:
        log.set_route(args.log_level, ColourAdapter(), sys.stderr)

    getter = TypeGetter(args.paths)

    drama = Drama()
    drama.folder = getter.rst

    folio = Folio(args.dwell, args.pause, context=drama)

    folio.run(args.repeat)
    if args.tag or "version" not in folio.metadata:
        folio.metadata["version"] = args.tag or "DRAFT"

    if args.css:
        print(folio.css)
    else:
        style = "\n".join([p.read_text() for p in getter.css]) or folio.css
        print(folio.render_html(style=style, sections=folio.sections))

    return 0


def parser():
    rv = add_performance_options(add_common_options(argparse.ArgumentParser()))
    rv.add_argument(
        "--css", default=False, action="store_true", help="Emit internal styles as CSS."
    )
    rv.add_argument("--tag", default=None, help="Supply a version tag for use as metadata.")
    rv.add_argument(
        "paths",
        nargs="*",
        type=pathlib.Path,
        help="Supply one or more paths to dialogue files.",
    )
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
