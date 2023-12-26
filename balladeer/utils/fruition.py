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
from collections import namedtuple
import dataclasses
import operator
import sys
import textwrap

from balladeer.lite.types import Page


class Graph:
    arcs = []

    Arc = namedtuple("Arc", ["exit", "actor", "name", "into", "key"], defaults=[None])

    @dataclasses.dataclass
    class Node:
        name: str
        entry: list = dataclasses.field(default_factory=list)
        exits: list = dataclasses.field(default_factory=list)
        width: int = None

    @classmethod
    def build_nodes(cls, arcs: list = None) -> dict:
        arcs = cls.arcs if arcs is None else arcs

        keys = {}
        rv = dict()
        for arc in arcs:
            arc = arc._replace(key=keys.setdefault(arc.actor, len(keys)))
            rv.setdefault(arc.exit, cls.Node(arc.exit)).exits.append(arc)
            rv.setdefault(arc.into, cls.Node(arc.into)).entry.append(arc)
        return list(rv.values())

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


def diagram():
    nodes = Fruition.build_nodes()
    for node in nodes:
        node.width = len(" ".join(Fruition.label(arc) for arc in node.entry + node.exits))
    width = sum(i.width for i in nodes) + len(nodes)

    tracks = [
        [node for node in nodes if not node.exits],
        [node for node in nodes if node.exits],
        [node for node in nodes if not node.exits],
    ]

    n = 0
    sorter = operator.attrgetter("key")
    for track in tracks:
        n += 1
        yield f'<div class="row" id="row-{n:02d}" style="display:flex; flex-direction:row">'
        arcs = sorted((arc for node in track for arc in node.entry), key=sorter)
        yield from (Fruition.label(arc) for arc in arcs)
        yield "</div>"

        n += 1
        yield f'<div class="row" id="row-{n:02d}" style="display:flex; flex-direction:row">'
        arcs = sorted((arc for node in track for arc in node.exits), key=sorter)
        yield from (Fruition.label(arc) for arc in arcs)
        yield "</div>"


def static_page() -> Page:
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
    </style>
    """).strip()
    page.paste(style, zone=page.zone.style)
    page.paste(*diagram(), zone=page.zone.body)
    return page


def parser(usage=__doc__):
    rv = argparse.ArgumentParser(usage)
    return rv


def main(args):
    assert len(Fruition.arcs) == 15
    page = static_page()
    print(page.html)
    return 0


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
