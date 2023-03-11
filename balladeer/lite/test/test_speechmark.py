#!/usr/bin/env python
#   encoding: utf8

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

(
    "Head",
    ("propose", "confirm", "counter", "abandon", "condemn", "declare"),
    defaults=(tuple(), tuple(), tuple(), tuple(), tuple(), tuple())
)


(
    "Hand",
    ("decline", "suggest", "promise", "disavow", "deliver"),
    defaults=(tuple(), tuple(), tuple(), tuple(), tuple())
)


class Syntax(unittest.TestCase):

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
