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
import textwrap
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
    SpeechMark is a convention for markup of authored text.
    It is suited for capturing dialogue, attributing speech, and writing screenplay directions.

    SpeechMark takes inspiration from other markup systems already in common use:
    * [Markdown](https://commonmark.org/)
    * [RestructuredText](https://docutils.sourceforge.io/rst.html)

    I tried both these systems prior to creating SpeechMark. I found the first to be underspecified
    to support my particular needs. The second is rather too featureful for my purpose, and
    the document model a little too cumbersome.

    SpeechMark syntax is deliberately constrained to be simple and unambiguous.
    This is to encourage adoption by non-technical users and to permit fast and efficient
    processing of many small pieces of text over an extended period of time.

    SpeechMark does not concern itself with document structure. There are no titles, sections or breaks.
    Rather, the input is expected to be a stream of text fragments.

    The specification intends to be lossless, so that every non-whitespace feature of the original text
    may be retrieved from the output.

    SpeechMark input must be line-based text, and should have UTF-8 encoding.
    The corresponding output must be well-formed HTML5.

    Inline markup consists of emphasis, links, and cues.

    Inline markup must consist of pairs of matching delimiters. There must be no line break within them;
    all inline markup must terminate on the same line it begins.

    Output must be generated in blocks. Each block may begin with a cue element. A block may contain one
    or more paragraphs. A block may contain a list. Every list item must contain a paragraph.

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

    def check(self, markup: dict={}, output=""):
        sm = SpeechMark()
        for n, (tag, text) in enumerate(markup.items()):
            with self.subTest(n=n, tag=tag, text=text):
                rv = sm.loads(text)
                expected = textwrap.dedent(output).strip()
                self.assertEqual(rv, expected)


class ParagraphTests(Syntax):

    @Syntax.example(label="1.1")
    def test_minimal_paragraph(self, markup: dict={}, output=""):
        """
        Simple strings are encapsulated in paragraphs.

        # TOML
        markup."Plain string"  =   "Hello!"
        markup."Anonymous cue" =   "<> Hello!"
        output = '''
        <blockquote>
        <p>Hello!</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_continuing_paragraph(self, markup: dict={}, output=""):
        """
        A paragraph continues until explicitly terminated.

        # TOML
        markup."Continuous string"  =   '''
        Hello!
        Hello!'''
        output = '''
        <blockquote>
        <p>Hello! Hello!</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example()
    def test_multiple_paragraphs(self, markup: dict={}, output=""):
        """
        A paragraph is terminated by a blank line.

        # TOML
        markup."Broken string"  =   '''
        Hello!

        Hello!'''
        output = '''
        <blockquote>
        <p>Hello!</p>
        <p>Hello!</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)


class SignificanceTests(Syntax):

    @Syntax.example(label="2.1")
    def test_minimal_significance(self, markup: dict={}, output=""):
        """
        Simple strings are encapsulated in paragraphs.

        # TOML
        markup."Entire signifier"  =   "_Hello!_"
        output = '''
        <blockquote>
        <p><strong>Hello!</strong></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="2.2")
    def test_multiple_significance(self, markup: dict={}, output=""):
        """
        Simple strings are encapsulated in paragraphs.

        # TOML
        markup."Multiple signifiers" =   "_Hello_ _Hello_!"
        markup."Abutting signifiers" =   "_Hello__Hello_!"
        output = '''
        <blockquote>
        <p><strong>Hello!</strong><strong>Hello!</strong</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)


class BlockTests(Syntax):

    @Syntax.example()
    def test_multiple_paragraphs(self, markup: dict={}, output=""):
        """
        A cue is used as an attribution of speech.

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
