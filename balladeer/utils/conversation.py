#!/usr/bin/env python3
#   encoding: UTF-8

# This is part of the Balladeer library.
# Copyright (C) 2024 D E Haynes

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

A visualization of how the 'Basic Conversation for Action'
(Terry Winograd and Fernando Flores) can be implemented using Fruition states.

You can drive such interactions in Balladeer by making the transitions from SpeechMark directives.

ie: To 'abandon':

    <ACTOR.abandoning@CONVERSATION> You know what, let's just forget this ever happened.

The diagram is generated as HTML on stdout. It seems to print to A4 landscape at a zoom of about 69%.

"""

import argparse
from collections import defaultdict
import dataclasses
import operator
import pprint
import statistics
import sys
import textwrap

from balladeer.lite.app import Home
from balladeer.lite.story import StoryBuilder
from balladeer.lite.types import Fruition
from balladeer.lite.types import Page


class Graph:
    arcs = []

    @dataclasses.dataclass(unsafe_hash=True)
    class Arc:
        exit: str
        actor: str
        name: str
        into: str
        key: int = None
        hops: int = None
        fail: bool = None

    @dataclasses.dataclass
    class Node:
        name: str
        entry: list = dataclasses.field(default_factory=list)
        exits: list = dataclasses.field(default_factory=list)

    @classmethod
    def build_nodes(cls, arcs: list = None) -> tuple[list, dict]:
        arcs = cls.arcs if arcs is None else arcs

        keys = {}
        rv = dict()
        for arc in arcs:
            arc.key = keys.setdefault(arc.actor, len(keys))
            rv.setdefault(arc.exit, cls.Node(arc.exit)).exits.append(arc)
            rv.setdefault(arc.into, cls.Node(arc.into)).entry.append(arc)

        sequence = list(rv.keys())
        for node in rv.values():
            arcs = node.entry + node.exits
            for arc in arcs:
                arc.hops = sequence.index(arc.into) - sequence.index(arc.exit)
                arc.fail = not (bool(rv[arc.into].exits) or arc.into == sequence[-1])

        return rv


class Conversation(Graph):
    arcs = [
        Graph.Arc(Fruition.inception, "head", "propose", Fruition.elaboration),
        Graph.Arc(Fruition.elaboration, "head", "abandon", Fruition.withdrawn),
        Graph.Arc(Fruition.elaboration, "hand", "decline", Fruition.withdrawn),
        Graph.Arc(Fruition.elaboration, "hand", "suggest", Fruition.discussion),
        Graph.Arc(Fruition.elaboration, "hand", "promise", Fruition.construction),
        Graph.Arc(Fruition.discussion, "head", "counter", Fruition.elaboration),
        Graph.Arc(Fruition.discussion, "head", "confirm", Fruition.construction),
        Graph.Arc(Fruition.discussion, "head", "abandon", Fruition.withdrawn),
        Graph.Arc(Fruition.discussion, "hand", "decline", Fruition.withdrawn),
        Graph.Arc(Fruition.construction, "hand", "disavow", Fruition.defaulted),
        Graph.Arc(Fruition.construction, "head", "abandon", Fruition.cancelled),
        Graph.Arc(Fruition.construction, "hand", "deliver", Fruition.evaluation),
        Graph.Arc(Fruition.evaluation, "head", "condemn", Fruition.construction),
        Graph.Arc(Fruition.evaluation, "head", "abandon", Fruition.cancelled),
        Graph.Arc(Fruition.evaluation, "head", "declare", Fruition.completion),
    ]


class Diagram:

    def __init__(self, nodes: dict, grid=None):
        self.nodes = nodes
        self.grid = grid or defaultdict(dict)
        self.spans = defaultdict(list)

    @staticmethod
    def overlaps(nodes: list[Graph.Node]) -> int:
        rv = {}
        n = 0
        for node in nodes:
            n += len([arc for arc in node.exits if not arc.fail and arc.hops > 0])
            n -= len([arc for arc in node.exits if not arc.fail and arc.hops < 0])
            n -= len([arc for arc in node.entry if arc.hops > 0])
            n += len([arc for arc in node.entry if arc.hops < 0])
            rv[node.name] = n
        return rv

    @staticmethod
    def key(arc: Graph.Arc):
        return (arc.hops, arc.key)

    @staticmethod
    def label(arc: Graph.Arc, actor=False, gerund=False):
        prefix = f'<span class="actor">{arc.actor}</span>.' if actor else ""
        if gerund:
            stem = arc.name.rstrip("e")
            return f'{prefix}<span class="directive">{stem}ing</span>'
        else:
            return f'{prefix}<span class="directive">{arc.name}</span>'

    @property
    def spine(self):
        return [node for n, node in enumerate(self.nodes.values()) if node.exits or n + 1 == len(self.nodes)]

    def layout(self, nodes: dict, ranks=2, extend=False):
        height = max(self.overlaps(self.spine).values())
        above = 3 if extend else 0
        below = height + 1 if extend else 0
        end_nodes = tuple(node for node in nodes.values() if node not in self.spine)
        yield '<div class="diagram">'
        if ranks == 2:
            yield from self.draw_spine_nodes(self.spine, r=1, above=0, below=below)
            yield from self.draw_end_nodes(end_nodes, r=1 + height)
        elif ranks == 3:
            yield from self.draw_spine_nodes(self.spine, r=3, above=above, below=below)
            yield from self.draw_end_nodes(end_nodes, r=3, n=-1)
            yield from self.draw_end_nodes(end_nodes, r=3 + height)
        yield "</div>"

    def draw_spine_nodes(self, nodes, r: int, above: int, below: int):
        overlaps = self.overlaps(nodes)
        offset = max(overlaps.values()) // 2
        r += offset

        c = 1
        for n, node in enumerate(nodes):
            s = max(1, len([arc for arc in node.exits if arc.fail]))
            self.spans[node.name].append(slice(c, c + s, s))
            if n in (0, len(nodes) - 1):
                yield f'<div class="node" style="grid-row: {r - above} / span {r + below}; grid-column: {c} / span {s}">{node.name.name}</div>'
            else:
                yield f'<div class="node" style="grid-row: {r}; grid-column: {c} / span {s}">{node.name.name}</div>'
            c += s + 1

        # Decide unique position of each arc label
        for node in nodes:
            c = self.spans[node.name][0].start
            s = self.spans[node.name][0].step
            arcs = sorted((i for i in node.exits if not i.fail), key=self.key, reverse=True)
            n = 0
            for a, arc in enumerate(arcs):
                row = r + n - offset
                col = c + s if arc.hops > 0 else c - 1
                if arc.hops > 0:
                    cols = range(self.spans[arc.exit][0].stop, self.spans[arc.into][0].start, 1)
                else:
                    cols = range(self.spans[arc.exit][0].start - 1, self.spans[arc.into][0].stop -1 , -1)

                while any(self.grid[row].get(col) for col in cols):
                    row += 1
                    n += 1

                # Store span of each arc
                self.grid[row][col] = arc
                self.spans[arc].append(slice(c, c + len(cols), len(cols)))
                for col in cols:
                    self.grid[row][col] = self.grid[row].get(col) or True
                n += 1

        # With each arc in place, spread them vertically if possible
        for node_name, spans in self.spans.items():
            for span in spans:
                arcs = [
                    (r, span.stop, self.grid[r][span.stop])
                    for r in range(r - offset, r + offset)
                    if span.stop in self.grid[r]
                    and isinstance(self.grid[r].get(span.stop), Graph.Arc)
                ]
                if not arcs: continue
                row = arcs[-1][0]
                col = arcs[-1][1]

                if self.grid[row + 1].get(col):
                    continue

                if (len(arcs) == 1 and row == r - offset) or (len(arcs) == 2 and row == r - offset + 1):
                    arc = arcs[-1][2]
                    self.grid[row][col] = None
                    self.grid[row + 1][col] = arc
                    continue

        # Write each arc
        for row, items in self.grid.items():
            for col, item in items.items():
                if isinstance(item, Graph.Arc):
                    s = self.spans[item][-1]
                    if item.hops > 0:
                        yield (
                            f'<div class="arc ltr {item.actor}" style="grid-row: {row}; grid-column: {col} / span {s.step}">'
                            f'{self.label(item)}</div>'
                        )
                    else:
                        yield (
                            f'<div class="arc rtl {item.actor}" style="grid-row: {row}; grid-column: {col} / span {s.step}">'
                            f'{self.label(item)}</div>'
                        )

    def draw_end_nodes(self, nodes, r=1, n=1):
        col = 0
        for node in nodes:
            priors = {self.nodes[arc.exit].name: self.nodes[arc.exit] for arc in node.entry}
            c = max(col + 1, min(self.spans[prior.name][0].start for prior in priors.values()))

            bridges = {i.name: [arc for arc in i.exits if arc in node.entry] for i in self.nodes.values()}
            for node_name, arcs in bridges.items():
                for a, arc in enumerate(arcs):
                    col = max(c, self.spans[node_name][0].start) + a
                    if n < 0:
                        yield (
                            f'<div class="arc {arc.actor} fail upper" style="grid-row: {r + n}; grid-column: {col}">'
                            f'{self.label(arc)}</div>'
                        )
                    else:
                        yield (
                            f'<div class="arc {arc.actor} fail lower" style="grid-row: {r + n}; grid-column: {col}">'
                            f'{self.label(arc)}</div>'
                        )

            s = col - c + 1
            yield f'<div class="node" style="grid-row: {r + 2 * n}; grid-column: {c} / span {s}">{node.name.name}</div>'
            self.spans[node.name].append(slice(c, c + s, s))

    def static_page(self, ranks=2, extend=False) -> Page:
        layout = list(self.layout(self.nodes, ranks=ranks, extend=extend))

        page = Page()
        settings = StoryBuilder.settings("default", themes=page.themes)
        page.paste(*Home.render_css_vars(settings), zone=page.zone.theme)

        n_cols = sum(self.spans[node.name][0].step for node in self.spine) + len(self.spine) - 1
        style = textwrap.dedent(f"""
        <style>
        * {{
        box-sizing: border-box;
        border: 0;
        font: inherit;
        font-size: 1em;
        line-height: 1em;
        margin: 0;
        outline: 0;
        padding: 0;
        text-decoration: none;
        vertical-align: baseline;
        }}
        @page {{
        size: 29.7cm 21cm;
        }}
        @media print {{
        body {{
        background-color: white;
        margin: 0;
        box-shadow: 0;
        }}
        div.arc {{
        font-size: 0.5rem;
        margin-left: 0.2rem;
        margin-right: 0.2rem;
        z-index: -1;
        }}
        div.arc.ltr::after {{
        content: " >";
        }}
        div.arc.rtl::before {{
        content: "< ";
        }}
        }}
        body {{
        background-color: silver;
        margin-top: 6rem;
        text-align: center;
        }}
        div.diagram {{
        align-content: space-around;
        display: grid;
        grid-template-columns: repeat({n_cols}, 1fr);
        grid-gap: 0.1rem;
        justify-content: space-evenly;
        }}
        div.arc {{
        background-color: var(--ballad-ink-glamour, yellow);
        font-family: sans-serif;
        font-weight: lighter;
        font-size: 0.8rem;
        max-height: 1.7rem;
        margin-bottom: 0.2rem;
        margin-top: 0.2rem;
        }}
        div.arc.ltr{{
        border-radius: 0 1.2rem 1.2rem 0;
        }}
        div.arc.rtl{{
        border-radius: 1.2rem 0 0 1.2rem;
        }}
        div.arc.fail {{
        margin-left: 0.3rem;
        margin-right: 0.3rem;
        padding-bottom: 0.4rem;
        padding-top: 0.4rem;
        }}
        div.arc.fail.lower{{
        border-radius: 0 0 1.2rem 1.2rem;
        }}
        div.arc.fail.upper{{
        border-radius: 1.2rem 1.2rem 0 0 ;
        }}
        div.arc.hand {{
        background-color: var(--ballad-ink-glamour, yellow);
        }}
        div.arc.head {{
        background-color: var(--ballad-ink-hilight, blue);
        color: var(--ballad-ink-washout, white);
        }}
        div.node {{
        background-color: var(--ballad-ink-washout, white);
        border: 0.2rem solid black;
        border-radius: 0.1rem;
        font-family: sans-serif;
        font-weight: bolder;
        min-height: 20vh;
        margin-left: 0.3rem;
        margin-right: 0.3rem;
        min-width: 10rem;
        padding-left: 0.6rem;
        padding-top: 0.4rem;
        text-align: left;
        text-transform: capitalize;
        }}
        </style>
        """).strip()
        page.paste(style, zone=page.zone.style)
        page.paste(*layout, zone=page.zone.body)
        return page


def parser(usage=__doc__):
    rv = argparse.ArgumentParser(usage)
    rv.add_argument(
        "--ranks", type=int, default=2,
        help="Number of state ranks. Set to 3 for a big wall display [2]"
    )
    rv.add_argument(
        "--extend", action="store_true", default=False,
        help="Extend terminal states [False]"
    )
    return rv


def main(args):
    nodes = Conversation.build_nodes()
    diagram = Diagram(nodes)
    page = diagram.static_page(ranks=args.ranks, extend=args.extend)
    pprint.pprint(diagram.nodes, stream=sys.stderr)
    print(page.html)
    return 0


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
