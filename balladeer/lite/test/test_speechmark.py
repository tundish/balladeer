#!/usr/bin/env python
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2023 D E Haynes

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

import re
import tomllib
import unittest

from balladeer.lite.speechmark import SpeechMark

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

# Rendering as blockquote
"""
<blockquote>
<header>Mandelbrot </header>
<p><span class="text">You may choose </span>
<a href="02.html">one</a>
<span class="text">, </span>
<a href="03.html">two</a>
<span class="text"> or </span>
<a href="04.html">three</a>
<span class="text"> coins.</span></p>
</blockquote>
</li>
"""

# Ex 2
"""
<blockquote>
<header>Mandelbrot </header>
<p><span class="text">Look, if you can't make a proper analysis of the situation, why don't you&NewLine;pick at </span>
<a href="https://www.random.org/integers/?num=1&min=1&max=3&col=1&base=10&format=html">random</a>
<span class="text">&quest;</span></p>
</blockquote>
"""

# Plugins must allow for transformation of links, eg:
"""
<nav>
<ul>
<li style="animation-delay: 22.80s; animation-duration: 3.70s">
<form role="form" action="False" method="GET" name="contents">

</form></li>
</ul>
</nav>
"""


# Ordered list marker: '[0-9a-zA-Z].' (remember fragment reference)
# Unordered list marker: '+'
# <em>:  one or more *
# <strong>: _
# <code>:  `
# <a>: [label](url)

Head = ("propose", "confirm", "counter", "abandon", "condemn", "declare")


Hand = ("decline", "suggest", "promise", "disavow", "deliver")


class Syntax(unittest.TestCase):
    """
    SpeechMark is a convention for markup of text documents.
    It is suited for capturing dialogue, attributing speech, and writing screenplays.

    SpeechMark takes inspiration from other markup systems in common use:
    * [Markdown](https://commonmark.org/)
    * [RestructuredText](https://docutils.sourceforge.io/rst.html)

    The syntax is deliberately constrained to be simple and unambiguous.
    This is to encourage adoption by non-technical users and to permit fast and efficient
    processing of many small pieces of text over an extended period of time.

    SpeechMark does not concern itself with document structure. There are no titles, sections or breaks.
    Rather, the input is expected to be a stream of text fragments.

    The specification intends to be lossless, so that every detail in the original text
    may be retrieved from the output.

    SpeechMark input must be line-based text with UTF-8 encoding. The corresponding output is well-formed HTML5.

    Inline markup consists of pairs of matching delimiters. There must be no line break within them;
    all inline markup must terminate on the same line it begins.

    Block boundaries are defined as follows:
    * A cue element terminates the previous block
    * A blank line terminates a paragraph.
    * A line with a list marker becomes an element in a list block

    * Inline emphasis
    * Links
    * Lists
    * Cues

    """
    examples = []

    def example(label=None):
        def wrapper(fn):
            def inner(self, *args, **kwargs):
                return fn(self, **data)
            doc = fn.__doc__ or ""
            text, toml = re.split(r"#\W*TOML\n", doc, maxsplit=1)
            data = tomllib.loads(toml)
            Syntax.examples.append((label, text, data))
            fn.__doc__ = text
            return inner
        return wrapper

    def check(self, markup: list=[], output=""):
        sm = SpeechMark()
        for n, m in enumerate(markup):
            with self.subTest(n=n, m=m):
                rv = sm.process(m)
                self.assertEqual(rv, output.strip())


class SpeechMarkTests(Syntax):

    @Syntax.example(label="1.2")
    def test_minimal_paragraph(self, markup: list=[], output=""):
        """

        # TOML
        markup = ["Hello!"]
        output = '''
        <p>Hello!</p>
        '''
        """
        return self.check(markup, output)

    @Syntax.example()
    def test_minimal_blockquote(self, markup: list=[], output=""):
        """

        # TOML
        markup = ["Hello!"]
        output = '''
        <blockquote cite="GUEST">
        <cite>GUEST</cite>
        <p>Hello!</p>
        </blockquote>
        '''
        """


if __name__ == "__main__":
    print(*Syntax.examples, sep="\n")
