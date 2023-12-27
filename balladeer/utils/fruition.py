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
        size: int = None

    @classmethod
    def build_nodes(cls, arcs: list = None) -> list:
        arcs = cls.arcs if arcs is None else arcs

        keys = {}
        rv = dict()
        for arc in arcs:
            arc.key = keys.setdefault(arc.actor, len(keys))
            rv.setdefault(arc.exit, cls.Node(arc.exit)).exits.append(arc)
            rv.setdefault(arc.into, cls.Node(arc.into)).entry.append(arc)

        return rv

    @staticmethod
    def label(arc: Arc, actor=False, gerund=False):
        prefix = f'<span class="actor">{arc.actor}</span>.' if actor else ""
        if gerund:
            stem = arc.name.rstrip("e")
            return f'{prefix}<span class="directive">{stem}ing</span>'
        else:
            return f'{prefix}<span class="directive">{arc.name}</span>'


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


def diagram(nodes: dict, reflect=False):
    sequence = list(nodes.keys())
    for node in nodes.values():
        arcs = node.entry + node.exits
        node.size = len(" ".join(Fruition.label(arc) for arc in arcs))
        for arc in arcs:
            arc.hops = sequence.index(arc.into) - sequence.index(arc.exit)
            arc.fail = not (bool(nodes[arc.into].exits) or arc.into == sequence[-1])

    width = sum(i.size for i in nodes.values()) + len(nodes)

    spine = [node for node in nodes.values() if node.exits] + [nodes[sequence[-1]]]
    rows = [spine, tuple(node for node in nodes.values() if node not in spine)]
    if reflect:
        rows.insert(0, rows[-1])

    n = 0
    sorter = operator.attrgetter("key")
    yield '<div class="diagram">'

    r = 1
    for n, row in enumerate(rows):
        c = 1
        s = 1

        if row is spine:
            for node in row:
                s = len(node.exits)
                yield f'<div class="node" style="grid-row: {r}; grid-column: {c} / span {s}">{node.name}</div>'

                arcs = sorted((i for i in node.exits), key=sorter)
                for n, arc in enumerate(arcs):
                    if arc.fail:
                        yield (
                            f'<div class="arc" style="grid-row: {r + 1}; grid-column: {c + n}">'
                            f'{Fruition.label(arc)}</div>'
                        )
                    else:
                        yield (
                            f'<div class="arc" style="grid-row: {r}; grid-column: {c + s}">'
                            f'{Fruition.label(arc)}</div>'
                        )
                c += s
            r += 1

        else:
            r += 1
            for node in row:
                s = len(node.entry)
                yield f'<div class="node" style="grid-row: {r}; grid-column: {c} / span {s}">{node.name}</div>'
                c += s

            r += 1
            arcs = sorted((arc for node in row for arc in node.entry), key=sorter)
            for arc in arcs:
                pass
                #yield f'<div class="arc" style="grid-row: {r}">{Fruition.label(arc)}</div>'

    yield "</div>"


def static_page(nodes: dict) -> Page:
    print(len(nodes), file=sys.stderr)
    page = Page()
    style = textwrap.dedent("""
    <style>
    body {
    background-color: silver;
    font-family: sans;
    font-size: 0.8rem;
    margin: 1.2rem;
    margin-left: auto;
    margin-right: auto;
    padding: 1.2rem;
    text-align: center;
    width: 80%;
    }
    div.diagram {
    display: grid;
    grid-template-columns: repeat(15, 1fr);
    }
    </style>
    """).strip()
    page.paste(style, zone=page.zone.style)
    page.paste(*diagram(nodes), zone=page.zone.body)
    return page


def parser(usage=__doc__):
    rv = argparse.ArgumentParser(usage)
    return rv


def main(args):
    assert len(Fruition.arcs) == 15
    nodes = Fruition.build_nodes()
    pprint.pprint(nodes, stream=sys.stderr)
    page = static_page(nodes)
    print(page.html)
    return 0


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
