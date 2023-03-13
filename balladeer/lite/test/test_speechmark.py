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
# cue = persona .directive @ entity, :mode ? parameters # fragment

# Directives: present participles
# Mode: Simple present, third person (singular or plural)

"""
STAFF

GUEST

PHONE


"""

"<GUEST>" == "<GUEST:says>"


# directive: Animation or transition of entity
# mode: mode of speech act

"""
<GUEST.entering:asks?pause=1&dwell=0.2#a>

    a. Hello?
    b. Say nothing

"""

"""
<PHONE:announces@GUEST>

<GUEST>

Your phone's ringing.

<STAFF> How strange I didn't hear it.

<PHONE:announces@GUEST,STAFF>

<STAFF> Oh, now I do!

<PHONE:announces@GUEST,STAFF> RIIING RIIING!

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
    all inline markup must terminate on the same line where it begins.

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


class CommentTests(Syntax):

    @Syntax.example(label="1.0")
    def test_single_comment(self, markup: dict={}, output=""):
        """
        Any line beginning with a "#" is a comment. It is ignored.

        # TOML
        markup."Entire signifier"  =    "# No effect on output"
        output = ""
        """
        return self.check(markup, output)


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
        Significant text is denoted with underscores.

        # TOML
        markup."Entire signifier"  =   "_Warning!_"
        output = '''
        <blockquote>
        <p><strong>Warning!</strong></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="2.2")
    def test_multiple_significance(self, markup: dict={}, output=""):
        """
        There may be multiple snippets of significant text on one line.

        # TOML
        markup."Multiple signifiers" =   "_Warning_ _Warning_!"
        markup."Abutting signifiers" =   "_Warning__Warning_!"
        output = '''
        <blockquote>
        <p><strong>Warning!</strong><strong>Warning!</strong</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)


class CodeTests(Syntax):

    @Syntax.example(label="3.1")
    def test_single_code(self, markup: dict={}, output=""):
        """
        Code snippets are defined between backticks.

        # TOML
        markup."Entire signifier"  =   "`git log`"
        output = '''
        <blockquote>
        <p><code>Hello!</code></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="3.2")
    def test_multiple_code(self, markup: dict={}, output=""):
        """
        There may be multiple code snippets on a line.

        # TOML
        markup."Multiple signifiers" =   "`git` `log`"
        markup."Abutting signifiers" =   "`git``log`"
        output = '''
        <blockquote>
        <p><code>git</code><code>log</code</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_cornercases_code(self):
        expected = textwrap.dedent("""
        <blockquote>
        <p><code>8.8.8.8</code></p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads("`8.8.8.8`")
        self.assertEqual(rv, expected)


class EmphasisTests(Syntax):

    @Syntax.example(label="4.1")
    def test_minimal_emphasis(self, markup: dict={}, output=""):
        """
        Emphasis may be added using pairs of asterisks.

        # TOML
        markup."Entire signifier"  =   "*Definitely!*"
        output = '''
        <blockquote>
        <p><em>Definitely!</em></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="4.2")
    def test_multiple_emphasis(self, markup: dict={}, output=""):
        """
        There may be multiple emphasised phrases on a line.

        # TOML
        markup."Multiple signifiers" =   "*Definitely* *Definitely!*"
        markup."Abutting signifiers" =   "*Definitely**Definitely!*"
        output = '''
        <blockquote>
        <p><em>Definitely</em><em>Definitely!</em></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="4.3")
    def test_multiple_emphasis(self, markup: dict={}, output=""):
        """
        Simple strings are encapsulated in paragraphs.

        # TOML
        markup."Multiple signifiers" =   "*Definitely* *Definitely!*"
        markup."Abutting signifiers" =   "*Definitely**Definitely!*"
        output = '''
        <blockquote>
        <p><em>Hello!</em><em>Hello!</em></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)


class LinkTests(Syntax):

    @Syntax.example(label="5.1")
    def test_single_link(self, markup: dict={}, output=""):
        """
        Hyperlinks are defined by placing link text within square brackets and the link destination
        in parentheses. There must be no space between them.
        See also https://spec.commonmark.org/0.30/#example-482.

        # TOML
        markup."Entire signifier"  =    "[Python](https://python.org)"
        output = '''
        <blockquote>
        <p><a href="https://python.org">Python</a></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="5.2")
    def test_multiple_links(self, markup: dict={}, output=""):
        """
        There may be multiple hyperlinks on a line.

        # TOML
        markup."Multiple signifiers" =  "[Python](https://python.org) [PyPI](https://pypi.org)"
        markup."Abutting signifiers" =  "[Python](https://python.org) [PyPI](https://pypi.org)"
        output = '''
        <blockquote>
        <p><a href="https://python.org">Python</a><a href="https://pypi.org">PyPI</a></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_cornercases_links(self):
        expected = textwrap.dedent("""
        <blockquote>
        <p>[Python] (https://python.org)</p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads("[Python] (https://python.org)")
        self.assertEqual(rv, expected)


class CueTests(Syntax):

    @unittest.skip("Not yet.")
    def test_anonymous_cue(self):
        cue = ""
        line = f"<{cue}> Hello!"
        expected = textwrap.dedent(f"""
        <blockquote cite="{cue}">
        <p>Hello!</p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads(line)
        self.assertEqual(rv, expected)

    @unittest.skip("Not yet.")
    def test_simple_cue(self):
        cue = role = "GUEST"
        line = f"<{cue}> Hello?"
        expected = textwrap.dedent(f"""
        <blockquote cite="{cue}">
        <cite>{role}</cite>
        <p>Hello!</p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads(line)
        self.assertEqual(rv, expected)

    @unittest.skip("Not yet.")
    def test_role_mode_cue(self):
        role = "GUEST"
        mode = "says"
        cue = f"{role}:{mode}"
        line = f"<{cue}> Hello?"
        expected = textwrap.dedent(f"""
        <blockquote cite="{cue}">
        <cite data-mode="{mode}">{role}</cite>
        <p>Hello!</p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads(line)
        self.assertEqual(rv, expected)

    def test_cue_matching_positive(self):
        examples = [
            "<>", "<> Hi!",
            "<role>", "<ROLE>",
            "<role:mode>", "<ROLE:MODE>",
            "<ROLE.d1.d2:mode>",
            "<ROLE:mode?p=0&q=a>",
            "<ROLE:mode#frag>",
            "<ROLE#frag>",
            "<ROLE.d1.d2:mode?p=0&q=a>",
            "<ROLE.d1.d2:mode?p=0&q=a#frag>",
        ]
        sm = SpeechMark()
        for line in examples:
            with self.subTest(line=line):
                rv = sm.cue_matcher.match(line)
                self.assertTrue(rv)
                d = rv.groupdict()
                print(d)
                self.assertEqual(5, len(d))

    def test_cue_matching_negative(self):
        examples = [
            "< >", "< >Hi!",
            "<role >", "< ROLE>"
        ]
        sm = SpeechMark()
        for line in examples:
            with self.subTest(line=line):
                rv = sm.cue_matcher.match(line)
                self.assertFalse(rv)


class UnorderedListTests(Syntax):

    @Syntax.example(label="5.1")
    def test_minimal_list(self, markup: dict={}, output=""):
        """
        A line beginning with a '+' character constitutes an
        item in an unordered list.

        # TOML
        markup."Entire list"  =  '''
        + Hat
        + Gloves
        '''
        output = '''
        <blockquote>
        <ul>
        <li><p>Hat</p></li>
        <li><p>Gloves</p></li>
        </ul>
        </blockquote>
        '''
        """
        return self.check(markup, output)


class OrderedListTests(Syntax):

    @Syntax.example(label="5.1")
    def test_numbered_list(self, markup: dict={}, output=""):
        """
        Ordered lists have lines which begin with one or more digits. Then a dot, and at least one space. 

        # TOML
        markup."Entire list"  =  '''
        1. Hat
        2. Gloves
        '''
        output = '''
        <blockquote>
        <ol>
        <li id="1"><p>Hat</p></li>
        <li id="2"><p>Gloves</p></li>
        </ol>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="5.1")
    def test_zeropadded_list(self, markup: dict={}, output=""):
        """
        Ordered list numbering is exactly as you define. No normalization is performed.

        # TOML
        markup."Entire list"  =  '''
        01. Hat
        02. Gloves
        '''
        output = '''
        <blockquote>
        <ol>
        <li id="01"><p>Hat</p></li>
        <li id="02"><p>Gloves</p></li>
        </ol>
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
