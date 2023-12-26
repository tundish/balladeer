#!/usr/bin/env python3
#   encoding: UTF-8

from collections import defaultdict
from collections import namedtuple
import dataclasses
import sys

class Graph:
    arcs = []

    Arc = namedtuple("Arc", ["exit", "actor", "name", "into", "key"], defaults=[None])

    @dataclasses.dataclass
    class Node:
        name: str
        entry: list = dataclasses.field(default_factory=list)
        exits: list = dataclasses.field(default_factory=list)

    @classmethod
    def build_nodes(cls, arcs: list = None) -> dict:
        arcs = cls.arcs if arcs is None else arcs

        keys = {}
        rv = dict()
        for arc in arcs:
            arc = arc._replace(key=keys.setdefault(arc.actor, len(keys)))
            rv.setdefault(arc.exit, cls.Node(arc.exit)).exits.append(arc)
            rv.setdefault(arc.into, cls.Node(arc.into)).entry.append(arc)
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
        Graph.Arc("construction", "hand", "disavow", "defaulted"),
        Graph.Arc("construction", "hand", "deliver", "transition"),
        Graph.Arc("transition", "head", "condemn", "construction"),
        Graph.Arc("transition", "head", "abandon", "cancelled"),
        Graph.Arc("transition", "head", "declare", "completion"),
    ]


if __name__ == "__main__":
    assert len(Fruition.arcs) == 15
    nodes = Fruition.build_nodes()
    print(nodes)
