#!/usr/bin/env python3
#   encoding: UTF-8

from collections import defaultdict
from collections import namedtuple
import dataclasses
import sys

Arc = namedtuple("Arc", ["exit", "actor", "name", "into"])
Node = namedtuple("Node", ["name", "entry", "exits"])

arcs = [
    Arc("inception", "head", "propose", "elaboration"),
    Arc("elaboration", "head", "abandon", "withdrawn"),
    Arc("elaboration", "hand", "decline", "withdrawn"),
    Arc("elaboration", "hand", "suggest", "discussion"),
    Arc("elaboration", "hand", "promise", "construction"),
    Arc("discussion", "head", "counter", "elaboration"),
    Arc("discussion", "head", "confirm", "construction"),
    Arc("discussion", "head", "abandon", "withdrawn"),
    Arc("discussion", "hand", "decline", "withdrawn"),
    Arc("construction", "hand", "disavow", "defaulted"),
    Arc("construction", "hand", "disavow", "defaulted"),
    Arc("construction", "hand", "deliver", "transition"),
    Arc("transition", "head", "condemn", "construction"),
    Arc("transition", "head", "abandon", "cancelled"),
    Arc("transition", "head", "declare", "completion"),
]


@dataclasses.dataclass
class Node:
    name: str
    entry: list = []
    exits: list = []


def build_nodes(arcs: list):
    rv = dict()
    for arc in arcs:
        getattr(rv.setdefault(arc.exit, Node(arc.exit)), arc.actor, []).append(arc)
        yield

if __name__ == "__main__":
    assert len(arcs) == 15
    nodes = list(build_nodes(arcs))
    print(nodes)
