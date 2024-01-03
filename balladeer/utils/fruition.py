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
from balladeer.lite.types import Page


class Graph:
    arcs = []

    @dataclasses.dataclass
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


class Fruition(Graph):
    arcs = [
        Graph.Arc("inception", "head", "propose", "elaboration"),
        Graph.Arc("elaboration", "head", "abandon", "withdrawn"),
        Graph.Arc("elaboration", "hand", "decline", "withdrawn"),
        Graph.Arc("elaboration", "hand", "suggest", "discussion"),
        Graph.Arc("elaboration", "hand", "promise", "construction"),
        Graph.Arc("discussion", "head", "counter", "elaboration"),
        Graph.Arc("discussion", "head", "confirm", "construction"),
        Graph.Arc("discussion", "head", "abandon", "withdrawn"),
        Graph.Arc("discussion", "hand", "decline", "withdrawn"),
        Graph.Arc("construction", "hand", "disavow", "defaulted"),
        Graph.Arc("construction", "head", "abandon", "cancelled"),
        Graph.Arc("construction", "hand", "deliver", "transition"),
        Graph.Arc("transition", "head", "condemn", "construction"),
        Graph.Arc("transition", "head", "abandon", "cancelled"),
        Graph.Arc("transition", "head", "declare", "completion"),
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

    def layout(self, nodes: dict, ranks=2):
        height = max(self.overlaps(self.spine).values())
        end_nodes = tuple(node for node in nodes.values() if node not in self.spine)
        yield '<div class="diagram">'
        if ranks == 2:
            yield from self.draw_spine_nodes(self.spine, r=1)
            yield from self.draw_end_nodes(end_nodes, r=1 + height)
        elif ranks == 3:
            yield from self.draw_spine_nodes(self.spine, r=3)
            yield from self.draw_end_nodes(end_nodes, r=3, n=-1)
            yield from self.draw_end_nodes(end_nodes, r=3 + height)
        yield "</div>"

    def draw_spine_nodes(self, nodes, r=1):
        overlaps = self.overlaps(nodes)
        offset = max(overlaps.values()) // 2
        r += offset

        c = 1
        for node in nodes:
            s = max(1, len([arc for arc in node.exits if arc.fail]))
            self.spans[node.name].append(slice(c, c + s, s))
            yield f'<div class="node" style="grid-row: {r}; grid-column: {c} / span {s}">{node.name}</div>'
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
                    self.grid[row][col] = None
                    self.grid[row + 1][col] = arcs[-1][2]
                    continue

        # Write each arc
        for row, items in self.grid.items():
            for col, item in items.items():
                if isinstance(item, Graph.Arc):
                    yield (
                        f'<div class="arc" style="grid-row: {row}; grid-column: {col}">'
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
                    yield (
                        f'<div class="arc fail" style="grid-row: {r + n}; grid-column: {col}">'
                        f'{self.label(arc)}</div>'
                    )

            s = col - c + 1
            yield f'<div class="node" style="grid-row: {r + 2 * n}; grid-column: {c} / span {s}">{node.name}</div>'
            self.spans[node.name].append(slice(c, c + s, s))

    def static_page(self, ranks=2) -> Page:
        layout = list(self.layout(self.nodes, ranks=ranks))

        page = Page()
        settings = StoryBuilder.settings("default", themes=page.themes)
        page.paste(*Home.render_css_vars(settings), zone=page.zone.theme)

        n_cols = sum(self.spans[node.name][0].step for node in self.spine) + len(self.spine)
        style = textwrap.dedent(f"""
        <style>
        * {{
        box-sizing: border-box;
        border: 0;
        font: inherit;
        font-size: 0.8em;
        line-height: 1em;
        margin: 0;
        outline: 0;
        padding: 0;
        text-decoration: none;
        vertical-align: baseline;
        }}
        body {{
        background-color: silver;
        text-align: center;
        }}
        div.diagram {{
        align-content: space-around;
        display: grid;
        grid-template-columns: repeat({n_cols}, 1fr);
        justify-content: space-evenly;
        }}
        div.arc {{
        background-color: var(--ballad-ink-washout, white);
        border-top: 1px dashed black;
        padding-bottom: 0.4rem;
        padding-top: 0.4rem;
        }}
        div.fail {{
        background-color: var(--ballad-ink-washout, white);
        border-right: 1px dashed black;
        border-top: none;
        }}
        div.node {{
        background-color: var(--ballad-ink-glamour, yellow);
        border: 1px solid black;
        padding-bottom: 1.4rem;
        padding-top: 1.4rem;
        }}
        </style>
        """).strip()
        page.paste(style, zone=page.zone.style)
        page.paste(*layout, zone=page.zone.body)
        return page


def parser(usage=__doc__):
    rv = argparse.ArgumentParser(usage)
    rv.add_argument("--ranks", type=int, default = 2, help="Number of state ranks")
    return rv


def main(args):
    nodes = Fruition.build_nodes()
    assert len(Fruition.arcs) == 15
    diagram = Diagram(nodes)
    page = diagram.static_page(ranks=args.ranks)
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
