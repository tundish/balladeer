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
import dataclasses
import operator
import pprint
import sys
import textwrap

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

        return arcs, rv


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

    def __init__(self, arcs: list, nodes: dict, grid=None):
        self.arcs = arcs
        self.nodes = nodes
        self.grid = grid or {}

    @staticmethod
    def label(arc: Graph.Arc, actor=False, gerund=False):
        prefix = f'<span class="actor">{arc.actor}</span>.' if actor else ""
        if gerund:
            stem = arc.name.rstrip("e")
            return f'{prefix}<span class="directive">{stem}ing</span>'
        else:
            return f'{prefix}<span class="directive">{arc.name}</span>'

    def layout(self, nodes: dict, reflect=False):
        spine = [node for n, node in enumerate(nodes.values()) if node.exits or n + 1 == len(nodes)]
        rows = [spine, tuple(node for node in nodes.values() if node not in spine)]
        if reflect:
            rows.insert(0, rows[-1])

        n = 0
        sorter = operator.attrgetter("key")
        yield '<div class="diagram">'

        r = 2
        spans = {}
        for n, row in enumerate(rows):
            c = 1

            if row is spine:
                for node in row:
                    s = max(1, len([arc for arc in node.exits if arc.fail]))
                    spans[node.name] = (c, s)
                    yield f'<div class="node" style="grid-row: {r}; grid-column: {c} / span {s}">{node.name}</div>'

                    arcs = sorted((i for i in node.exits if not i.fail), key=sorter)
                    for n, arc in enumerate(arcs):
                        offset = -1 if arc.hops < 0 else 1
                        yield (
                            f'<div class="arc" style="grid-row: {r + offset}; grid-column: {c + s}">'
                            f'{self.label(arc)}</div>'
                        )
                        c += 1
                    c += s
                r += 2

            else:
                # TODO: fail arcs written here.
                r += 1
                for node in row:
                    priors = [nodes[arc.exit] for arc in node.entry]
                    c = min(spans[prior.name][0] for prior in priors) + 1
                    s = len(node.entry)
                    spans[node.name] = (c, s)
                    for n, arc in enumerate(node.entry):
                        yield (
                            f'<div class="arc fail" style="grid-row: {r + 1}; grid-column: {c + n}">'
                            f'{self.label(arc)}</div>'
                        )
                    yield f'<div class="node" style="grid-row: {r + 2}; grid-column: {c} / span {s}">{node.name}</div>'
                    c += s

        yield "</div>"
        print(f"Spans: {spans}", file=sys.stderr)

    def static_page(self) -> Page:
        page = Page()
        n_cols = len(self.arcs) + len(self.nodes)
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
        padding-bottom: 1.4rem;
        padding-top: 1.4rem;
        }}
        div.node {{
        border: 1px solid black;
        padding-bottom: 1.4rem;
        padding-top: 1.4rem;
        }}
        </style>
        """).strip()
        page.paste(style, zone=page.zone.style)
        page.paste(*self.layout(self.nodes), zone=page.zone.body)
        return page


def parser(usage=__doc__):
    rv = argparse.ArgumentParser(usage)
    return rv


def main(args):
    arcs, nodes = Fruition.build_nodes()
    assert len(Fruition.arcs) == 15
    diagram = Diagram(arcs, nodes)
    page = diagram.static_page()
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
