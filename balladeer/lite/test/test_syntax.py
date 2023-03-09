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
        return lines

if __name__ == "__main__":
    text = sys.stdin.read()
    blocks = SpeechMark.blocks(text)
    print(text, file=sys.stdout)

