#!/usr/bin/env python
# encoding: UTF-8

import random
import subprocess
import sys
import textwrap
from xml.dom import minidom

from balladeer import Fruition
from balladeer import Gesture
from balladeer import Hand
from balladeer import Head

def convert(text):
    # 2 May 2015, John F. Raffensperger
    # 1. Read Graphviz.svg. This is output from Graphviz.
    graphvizSVGFile= minidom.parseString(text)

    # 2. For each node, get id and title.
    nodeTitles = {}
    for s in graphvizSVGFile.getElementsByTagName('g'):
        if s.attributes['id'].value[:4] == "node":
            nodeTitles[s.getElementsByTagName('title')[0].firstChild.data] = s.attributes['id'].nodeValue

    # 3. For each arc, parse the title, and match the corresponding ids of the nodes, add the ids to the arc,
    edgeTitles = {}
    for s in graphvizSVGFile.getElementsByTagName('g'):
        if s.attributes['id'].value[:4] == "edge":
            edgeTitle = s.getElementsByTagName('title')[0].firstChild.data
            edgeTitles [s.attributes['id'].nodeValue] = edgeTitle.split("->")
            
    # 4. Add connector elements to Graphviz.svg.
    # For each arc, delete the GraphViz arrow marker,
    for s in graphvizSVGFile.getElementsByTagName('g'):
        if s.attributes['id'].value[:4] == "edge":
            # Remove child "polygon", which is the GraphViz arrow marker.
            for thing in s.childNodes: 
                if thing.nodeType == s.ELEMENT_NODE and thing.tagName == "polygon": 
                    s.removeChild(thing) 
                    break

    # 5. To each edge path, add an Inkscape arrow marker in the attributes.
    for s in graphvizSVGFile.getElementsByTagName('g'):
        if s.attributes['id'].value[:4] == "edge":
            for thing in s.childNodes: 
                if thing.nodeType == s.ELEMENT_NODE and thing.tagName == "path": 
                    thing.setAttribute("inkscape:connector-type", "polyline")
                    thing.setAttribute("inkscape:connector-curvature", "3")
                    nodeID = nodeTitles[edgeTitles[s.attributes['id'].value][0].split(":")[0]]
                    thing.setAttribute("inkscape:connection-start", "#" + nodeID)
                    nodeID = nodeTitles[edgeTitles[s.attributes['id'].value][1].split(":")[0]]
                    thing.setAttribute("inkscape:connection-end", "#" + nodeID)

    # 6. Output should have draggable nodes in Inkscape, after ungrouping as needed.
    return graphvizSVGFile.toxml(encoding="utf-8", standalone=True)


def transitions():
    head = Head(*("head.{0}".format(i) for i in Head._fields))
    hand = Hand(*("hand.{0}".format(i) for i in Hand._fields))
    g = Gesture("witness", head, hand)
    for s in Fruition:
        g.set_state(s)
        for e, t in g.transitions:
            yield s, e, t


def arcs(transitions):
    yield from [i.name.capitalize() for i in Fruition]
    for s, e, t in transitions:
        s = s.name.capitalize()
        t = t.name.capitalize()
        c = "orangered4" if e.startswith("head") else "royalblue4"
        e = e.split(".")[-1]
        hp = "c"
        tp = "c"
        yield f"""
        {s} -> {t} [arrowhead=vee arrowsize=0.6 headport={hp} tailport={tp} xlabel="{e}"
        fontcolor={c} fontname="Ubuntu Condensed"]"""

def template(graph):
    return textwrap.dedent("""
    digraph {{
        graph [center=true nodesep=2 ratio=1 splines=ortho]
        node [fontname="Cabin Sketch" fontsize=16 height=1.0 shape=rectangle]
        {0}
    }}
    """).format("\n".join(graph))

if __name__ == "__main__":
    """
    dot -K neato -Tsvg > output.svg
    """
    graph = arcs(transitions())
    dot = subprocess.run(
        ["dot", "-Tsvg"],
        input=template(graph).encode("utf-8"),
        capture_output=True
    )
    print(dot.stdout.decode("utf-8"))
    svg = convert(dot.stdout.decode("utf-8"))
    #print(svg.decode("utf-8"))
