#!/usr/bin/env python3
#   encoding: UTF-8

from collections import namedtuple
import sys

Arc = namedtuple("Arc", ["exit", "actor", "name", "into"])

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

if __name__ == "__main__":
    assert len(arcs) == 15
    print(arcs)
