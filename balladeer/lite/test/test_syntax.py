#!/usr/bin/env python
#   encoding: utf8

# Speechmark

from collections import namedtuple
import sys
import textwrap
import warnings

# block = cue + dialogue
# cue = persona / directive/ @ entity, mode ? parameters # fragment


"""
STAFF

GUEST

PHONE


"""

"<GUEST>" == "<GUEST:says>"


# directive: Animation or transition of entity
# mode: mode of speech act

"""
<GUEST/entering:decides?pause=1&dwell=0.2#a>

    a. Hello!
    b. Say nothing

"""

"""
<PHONE:alerts@GUEST>

<GUEST>

Your phone's ringing.

<STAFF> How strange I didn't hear it.

<PHONE:alerts@GUEST,STAFF>

<STAFF> Oh, now I do!

<PHONE/throbbing:alerts@GUEST,STAFF> RIIING RIIING!

"""

Head = namedtuple(
    "Head",
    ("propose", "confirm", "counter", "abandon", "condemn", "declare"),
    defaults=(tuple(), tuple(), tuple(), tuple(), tuple(), tuple())
)


Hand = namedtuple(
    "Hand",
    ("decline", "suggest", "promise", "disavow", "deliver"),
    defaults=(tuple(), tuple(), tuple(), tuple(), tuple())
)

class SpeechMark:

    @staticmethod
    def blocks(text: str):
        trim = textwrap.dedent(text)
        if trim != text:
            warnings.warn(f"Reindentation lost {len(text) - len(trim)} chars")

        lines = text.splitlines(keepends=False)
        enter, exit = 0, 0 # character positions
        start, end = 0, 0  # line numbers
        for n, l in enumerate(lines):
            if not n or l.startswith("<"):
                yield trim, enter, exit, lines, start, end
                start = n
                enter = exit
            else:
                end = n
                exit += len(l)


if __name__ == "__main__":
    text = sys.stdin.read()
    print(text, file=sys.stdout)
    blocks = list(SpeechMark.blocks(text))
    print(*blocks, file=sys.stdout, sep="\n")

